import os
import time
import json

os.environ["PYSPARK_PYTHON"] = r"C:\Program Files\Python310\python.exe"
os.environ["PYSPARK_DRIVER_PYTHON"] = r"C:\Program Files\Python310\python.exe"
os.environ["HADOOP_HOME"] = r"C:\BigData\hadoop"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from kafka import KafkaConsumer

# Create Spark Session
spark = (
    SparkSession.builder
    .appName("AMLRealtimeSimulation")
    .master("local[*]")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

print("✅ Spark Session Created")

# Kafka Consumer
consumer = KafkaConsumer(
    "transactions",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="latest",
    enable_auto_commit=True
)

print("✅ Connected to Kafka")
print("✅ Streaming Started")

# Schema
schema = StructType([
    StructField("sender_id", StringType(), True),
    StructField("receiver_id", StringType(), True),
    StructField("amount", DoubleType(), True)
])

batch = []

while True:

    messages = consumer.poll(timeout_ms=2000)

    for tp, records in messages.items():

        for record in records:

            batch.append(record.value)

    if len(batch) > 0:

        df = spark.createDataFrame(batch, schema=schema)

        suspicious_df = df.filter(col("amount") > 50000)

        print("\n🚨 Suspicious Transactions:\n")

        suspicious_df.show(truncate=False)

        batch = []

    time.sleep(2)