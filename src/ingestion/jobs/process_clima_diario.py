"""
AWS Glue Job to process climate data
"""
import sys
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

# Inicialización
args = getResolvedOptions(sys.argv, ["JOB_NAME", "input_path", "output_path"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

try:
    print(f"📥 Reading climate data from: {args['input_path']}")

    # 1. Read CSV
    df = spark.read.option("header", "true").csv(args["input_path"])
    total_inicial = df.count()
    print(f"📊 Climate records: {total_inicial}")
    print(f"📋 Columns: {df.columns}")

    # 2. Inline validations
    print("🔍 Validating climate data...")

    # 2.1 Cast to numeric
    df = df.withColumn("temp_num", F.col("temperatura").cast("double"))
    df = df.withColumn("precip_num", F.col("precipitacion").cast("double"))

    # 2.2 Validate ranges
    df = df.filter(F.col("temp_num").between(-20, 50))
    df = df.filter(F.col("precip_num").between(0, 500))

    # 2.3 Drop nulls in key columns
    df = df.dropna(subset=["lote_id", "fecha"])

    # 2.4 Validate date format
    df = df.withColumn(
        "fecha_valida",
        F.when(F.col("fecha").rlike("^\\d{4}-\\d{2}-\\d{2}$"), True).otherwise(False),
    )
    df = df.filter(F.col("fecha_valida"))

    # 3. Transformations
    print("🔄 Applying transformations...")

    # 3.1 Standardize column names
    for col in df.columns:
        df = df.withColumnRenamed(col, col.lower().strip().replace(" ", "_"))

    # 3.2 EXTRACT campaign from date (assuming YYYY-MM-DD format)
    df = df.withColumn("campana", F.substring(F.col("fecha"), 1, 4))

    # 3.3 CREATE lote column from lote_id
    df = df.withColumn("lote", F.col("lote_id"))

    # 3.4 Clean partition values
    df = df.withColumn(
        "campana", F.regexp_replace(F.col("campana"), "[^a-zA-Z0-9]", "_")
    )
    df = df.withColumn("lote", F.regexp_replace(F.col("lote"), "[^a-zA-Z0-9]", "_"))

    # 3.5 Drop temporary columns
    df = df.drop("temp_num", "precip_num", "fecha_valida")

    total_final = df.count()
    print(f"📊 Records after validations: {total_final}")
    print(f"   Filtrados: {total_inicial - total_final}")
    print(f"📋 Final columns: {df.columns}")

    # 4. Write
    print(f"📤 Writing to: {args['output_path']}")
    print("📂 Partitioning by: campaign, plot")
    df.write.mode("overwrite").partitionBy("campana", "lote").parquet(
        args["output_path"]
    )

    print("✅ Climate job completed")
    job.commit()
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    raise
