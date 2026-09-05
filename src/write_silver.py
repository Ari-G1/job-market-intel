"""
Bronze -> silver. Batch cleansing.

Deliberately batch, not streaming: deduplication in Structured Streaming
requires bounded state, which requires a watermark on a real event-time
column. Our source is a replayed file with no meaningful arrival time, so
cleansing happens here where the data is bounded and dropDuplicates is exact.
"""
import os

# Must be set BEFORE the JVM starts, i.e. before SparkSession is created.
# In local mode the driver IS the executor, so the default 1g heap has to
# hold the Parquet read buffers, the dedupe shuffle, and everything else.
os.environ["PYSPARK_SUBMIT_ARGS"] = "--driver-memory 4g pyspark-shell"

from pyspark.sql import SparkSession
from pyspark.sql.functions import (col, regexp_replace, trim, length, lower,
                                   when, count, sum as spark_sum,
                                   countDistinct)

STOPWORDS = ["the", "and", "for", "with", "you", "our", "are", "will", "have",
             "this", "that", "your", "from", "work", "team", "role",
             "experience", "skills", "who", "all"]
MIN_STOPWORDS = 5
MIN_CHARS = 200

spark = (SparkSession.builder
         .appName("bronze-to-silver")
         .config("spark.sql.shuffle.partitions", "8")
         # 4096-row batches of a 3.7KB average string column need ~15MB
         # contiguous. 512 keeps each allocation small.
         .config("spark.sql.parquet.columnarReaderBatchSize", "512")
         .getOrCreate())
spark.sparkContext.setLogLevel("WARN")

# ---------------------------------------------------------------- derive
df = spark.read.parquet("data/bronze")

# Strip HTML tags, then collapse whitespace. Order matters: removing tags
# first leaves double spaces that the second pass cleans up.
df = df.withColumn(
    "description_clean",
    trim(regexp_replace(
        regexp_replace(col("description"), r"<[^>]+>", " "),
        r"\s+", " ")))

# Count distinct stopword hits. Builds one Column expression by summing 20
# conditionals, so it compiles to a single pass rather than 20.
lc = lower(col("description_clean"))
hits = sum(when(lc.rlike(r"\b" + w + r"\b"), 1).otherwise(0) for w in STOPWORDS)
df = df.withColumn("stopword_hits", hits)
df = df.withColumn("clean_len", length(col("description_clean")))

has_desc = col("description").isNotNull() & (trim(col("description")) != "")
is_english = col("stopword_hits") >= MIN_STOPWORDS
long_enough = col("clean_len") >= MIN_CHARS

# ------------------------------------------------------- pass 1: counts
stats = df.agg(
    count("*").alias("bronze"),
    spark_sum(when(has_desc, 1).otherwise(0)).alias("has_desc"),
    countDistinct(when(has_desc, col("job_id"))).alias("distinct_ids"),
    spark_sum(when(has_desc & ~is_english, 1).otherwise(0)).alias("not_english"),
    spark_sum(when(has_desc & is_english & ~long_enough, 1).otherwise(0)).alias("too_short"),
    spark_sum(when(has_desc & is_english & long_enough, 1).otherwise(0)).alias("silver"),
).collect()[0]

(df.filter(has_desc & is_english & long_enough)
   .select("job_id", "title", "company_name", "description_clean",
           "location", "formatted_experience_level", "formatted_work_type",
           "remote_allowed", "listed_time")
   .write.mode("overwrite").parquet("data/silver"))
print("silver written")

# ------------------------------------------------------- funnel report
# stats was computed above in the single agg pass; emit it so docs/funnel.txt
# is reproducible from this script (it used to come from a separate one-off).
blank = stats["bronze"] - stats["has_desc"]
dup   = stats["has_desc"] - stats["distinct_ids"]
loss  = stats["bronze"] - stats["silver"]
funnel = (
    f"bronze rows           : {stats['bronze']:,}\n"
    f"blank description     : -{blank:,}\n"
    f"duplicate job_id      : -{dup:,}\n"
    f"language filter       : -{stats['not_english']:,}\n"
    f"shorter than 200 chars: -{stats['too_short']:,}\n"
    f"silver rows           : {stats['silver']:,}\n"
    f"total loss            : {loss:,} ({loss / stats['bronze']:.2%})\n"
)
print(funnel)
os.makedirs("docs", exist_ok=True)
with open("docs/funnel.txt", "w", encoding="utf-8") as f:
    f.write(funnel)
print("wrote docs/funnel.txt")