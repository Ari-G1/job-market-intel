"""
Applies the gazetteer across all silver postings as a Spark UDF.

Runs distributed rather than as a plain Python loop: this is what makes
Spark a real transformation stage rather than a file-format converter, and
it uses the UDF feature covered in lecture 3.

Output is COMPUTED. No LLM is involved at any point in this file.
"""
import os
os.environ["PYSPARK_SUBMIT_ARGS"] = "--driver-memory 3g pyspark-shell"

import sys
sys.path.insert(0, "src")

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, size
from pyspark.sql.types import ArrayType, StringType

from gazetteer import extract_skills

spark = (SparkSession.builder
         .appName("gazetteer")
         .config("spark.sql.shuffle.partitions", "8")
         .config("spark.sql.parquet.columnarReaderBatchSize", "512")
         .getOrCreate())
spark.sparkContext.setLogLevel("WARN")

# The UDF runs in a separate Python worker process with a fresh interpreter
# and no knowledge of the driver's sys.path. addPyFile ships the module to
# every worker so the pickled function can resolve its import.
spark.sparkContext.addPyFile("src/gazetteer.py")

extract_udf = udf(extract_skills, ArrayType(StringType()))

df = spark.read.parquet("data/silver")
df = df.withColumn("skills_gazetteer", extract_udf(col("description_clean")))
df = df.withColumn("n_skills", size(col("skills_gazetteer")))

df.write.mode("overwrite").parquet("data/silver_gazetteer")
print("written to data/silver_gazetteer")