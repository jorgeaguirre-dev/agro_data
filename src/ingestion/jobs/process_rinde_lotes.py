"""
AWS Glue Job to process plot yield data
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
    print(f"📥 Reading data from: {args['input_path']}")

    # 1. Read CSV
    df = spark.read.option("header", "true").csv(args["input_path"])
    total_inicial = df.count()
    print(f"📊 Records read: {total_inicial}")
    print(f"📋 Columns: {df.columns}")

    # 2. Inline validations
    print("🔍 Validating data...")

    # 2.1 Filter yield out of range (0-20000)
    df = df.withColumn("rinde_num", F.col("rinde").cast("double"))
    df = df.filter(F.col("rinde_num").between(0, 20000))

    # 2.2 Drop nulls in critical columns
    df = df.dropna(subset=["lote_id", "campana"])

    # 2.3 Validate date format (simple)
    df = df.withColumn(
        "fecha_valida",
        F.when(F.col("fecha_cosecha").rlike("^\\d{4}-\\d{2}-\\d{2}$"), True).otherwise(
            False
        ),
    )
    df = df.filter(F.col("fecha_valida"))

    # 3. Transformations
    print("🔄 Applying transformations...")

    # 3.1 Standardize column names
    for col in df.columns:
        df = df.withColumnRenamed(col, col.lower().strip().replace(" ", "_"))

    # 3.2 CREATE lote column from lote_id (for partitioning)
    df = df.withColumn("lote", F.col("lote_id"))

    # 3.3 Clean partition values
    df = df.withColumn(
        "campana", F.regexp_replace(F.col("campana"), "[^a-zA-Z0-9]", "_")
    )
    df = df.withColumn("lote", F.regexp_replace(F.col("lote"), "[^a-zA-Z0-9]", "_"))

    # 3.4 Drop temporary columns
    df = df.drop("rinde_num", "fecha_valida")

    total_final = df.count()
    print(f"📊 Records after validations: {total_final}")
    print(f"   Filtrados: {total_inicial - total_final}")
    print(f"📋 Final columns: {df.columns}")

    # 4. Write as partitioned Parquet
    print(f"📤 Writing to: {args['output_path']}")
    print("📂 Partitioning by: campaign, plot")
    df.write.mode("overwrite").partitionBy("campana", "lote").parquet(
        args["output_path"]
    )

    print("✅ Job completed successfully")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    raise
finally:
    job.commit()
