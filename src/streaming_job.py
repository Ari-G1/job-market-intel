"""
Kafka -> bronze. Streaming ingestion only.

Reads jobs.raw, parses each message into typed columns, writes Parquet to
data/bronze. No cleaning here: bronze is the raw landing zone. Cleansing
happens in write_silver.py, where the data is bounded.
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType

SCHEMA = StructType([
    StructField("job_id", StringType()),
    StructField("title", StringType()),
    StructField("company_name", StringType()),
    StructField("description", StringType()),
    StructField("location", StringType()),
    StructField("formatted_experience_level", StringType()),
    StructField("formatted_work_type", StringType()),
    StructField("remote_allowed", StringType()),
    StructField("listed_time", StringType()),
])

spark = (SparkSession.builder
         .appName("jobs-bronze")
         .config("spark.jars.packages",
                 "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1")
         .config("spark.sql.shuffle.partitions", "8")
         .getOrCreate())
spark.sparkContext.setLogLevel("WARN")

raw = (spark.readStream.format("kafka")
       .option("kafka.bootstrap.servers", "localhost:9092")
       .option("subscribe", "jobs.raw")
       .option("startingOffsets", "earliest")
       .option("maxOffsetsPerTrigger", 10000)
       .load())

parsed = (raw
          .select(from_json(col("value").cast("string"), SCHEMA).alias("d"))
          .select("d.*"))

query = (parsed.writeStream
         .format("parquet")
         .outputMode("append")
         .option("path", "data/bronze")
         .option("checkpointLocation", "checkpoints/bronze")
         .trigger(availableNow=True)
         .start())

query.awaitTermination()
print("bronze write complete")