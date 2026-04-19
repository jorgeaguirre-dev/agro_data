"""
Glue Job to run Great Expectations validations
With forced catalog synchronization
"""
import sys
import json
import time
import boto3
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

# Inicialización
args = getResolvedOptions(
    sys.argv,
    ["JOB_NAME", "suite_name", "database_name", "table_name", "results_bucket"],
)
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)


def force_catalog_sync(spark, database, table, max_attempts=10, delay=5):
    """Forces catalog synchronization and retries until the table is available"""

    print("🔄 Forcing catalog synchronization...")

    # Option 1: Refresh the table if it exists
    try:
        spark.sql(f"REFRESH TABLE `{database}`.`{table}`")
        print(f"✅ Table {database}.{table} refreshed")
    except Exception:
        print("⚠️ Could not refresh (table may not exist yet)")

    # Option 2: List available tables in Spark
    for attempt in range(max_attempts):
        try:
            print(
                f"🔍 Attempt {attempt + 1}/{max_attempts} - Checking tables in Spark..."
            )

            # List databases in Spark
            spark.sql("SHOW DATABASES").show(truncate=False)

            # Try to use the database
            spark.sql(f"USE `{database}`")

            # List tables in this database
            tables_df = spark.sql("SHOW TABLES")
            print("📋 Available tables in Spark:")
            tables_df.show(truncate=False)

            # Check if our table is in the list
            tables_list = [row["tableName"] for row in tables_df.collect()]

            if table in tables_list:
                print(f"✅ Table {table} found in Spark!")

                # Try to count records
                count_df = spark.sql(f"SELECT COUNT(*) FROM `{database}`.`{table}`")
                count = count_df.collect()[0][0]
                print(f"📊 Records found: {count}")
                return True
            else:
                print(
                    f"⏳ Table {table} NOT found in Spark. Available tables: {tables_list}"
                )

        except Exception as e:
            print(f"⏳ Error on attempt {attempt + 1}: {str(e)[:100]}")

        if attempt < max_attempts - 1:
            print(f"   Waiting {delay} seconds...")
            time.sleep(delay)

    return False


try:
    print("=" * 50)
    print("🚀 STARTING DATA QUALITY JOB")
    print("=" * 50)
    print("📋 Configuration:")
    print(f"   - Database: {args['database_name']}")
    print(f"   - Table: {args['table_name']}")
    print(f"   - Suite: {args['suite_name']}")
    print(f"   - Results bucket: {args['results_bucket']}")

    # Option 3: Use Glue Client directly for debug
    glue_client = boto3.client("glue", region_name="us-east-1")
    try:
        tables_response = glue_client.get_tables(DatabaseName=args["database_name"])
        print(
            f"📋 Tables in Glue Catalog: {[t['Name'] for t in tables_response['TableList']]}"
        )
    except Exception as e:
        print(f"⚠️ Error getting tables from Glue: {e}")

    # WAIT until the table is available in Spark
    if not force_catalog_sync(spark, args["database_name"], args["table_name"]):
        # Last resort: try with the S3 path directly
        print("⚠️ Trying to access via S3 path as fallback...")
        s3_path = f"s3://{args['results_bucket'].replace('-curated', '')}/{args['table_name']}"

        # Determine the correct path
        if "rinde" in args["table_name"]:
            s3_path = "s3://agro-data-pipeline-dev-curated/rinde_lotes"
        else:
            s3_path = "s3://agro-data-pipeline-dev-curated/clima_diario"

        print(f"📂 Reading directly from: {s3_path}")

        try:
            df = spark.read.parquet(s3_path)
            total_rows = df.count()
            print(f"✅ Direct read successful! {total_rows} records")

            # Create temporary view to use SQL
            df.createOrReplaceTempView(args["table_name"])

        except Exception as e2:
            raise Exception(
                f"Could not access data via catalog or S3: {e2}"
            )
    else:
        # Read the table normally
        df = spark.sql(
            f"SELECT * FROM `{args['database_name']}`.`{args['table_name']}`"
        )
        total_rows = df.count()

    print(f"📊 Total records: {total_rows}")

    if total_rows == 0:
        print("⚠️ Empty table - validations cannot be performed")
        results = {
            "suite_name": args["suite_name"],
            "table": args["table_name"],
            "database": args["database_name"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_rows": 0,
            "status": "EMPTY_TABLE",
            "validations": [],
        }
    else:
        # Show schema and data
        print("📋 Schema:")
        df.printSchema()
        print("📋 First 3 rows:")
        df.show(3, truncate=False)

        # Validations
        results = {
            "suite_name": args["suite_name"],
            "table": args["table_name"],
            "database": args["database_name"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_rows": total_rows,
            "validations": [],
        }

        # Available columns
        columns = df.columns
        print(f"📋 Available columns: {columns}")

        # Validation 1: No nulls in lote_id (if exists)
        if "lote_id" in columns:
            null_count = df.filter("`lote_id` IS NULL").count()
            results["validations"].append(
                {
                    "expectation": "not_null_lote_id",
                    "column": "lote_id",
                    "success": null_count == 0,
                    "null_count": null_count,
                    "null_percentage": round(null_count / total_rows * 100, 2),
                }
            )
            print(f"   lote_id nulls: {null_count}")

        # Table-specific validations
        if "rinde" in args["table_name"]:
            if "rinde" in columns:
                out_of_range = df.filter(
                    "CAST(`rinde` AS double) < 0 OR CAST(`rinde` AS double) > 20000"
                ).count()
                results["validations"].append(
                    {
                        "expectation": "range_rinde_0_20000",
                        "column": "rinde",
                        "success": out_of_range == 0,
                        "out_of_range": out_of_range,
                    }
                )
                print(f"   rinde out of range: {out_of_range}")

            if "campana" in columns:
                null_campana = df.filter("`campana` IS NULL").count()
                results["validations"].append(
                    {
                        "expectation": "not_null_campana",
                        "column": "campana",
                        "success": null_campana == 0,
                        "null_count": null_campana,
                    }
                )

        elif "clima" in args["table_name"]:
            if "temperatura" in columns:
                temp_out = df.filter(
                    "CAST(`temperatura` AS double) < -20 OR CAST(`temperatura` AS double) > 50"
                ).count()
                results["validations"].append(
                    {
                        "expectation": "range_temperatura_-20_50",
                        "column": "temperatura",
                        "success": temp_out == 0,
                        "out_of_range": temp_out,
                    }
                )
                print(f"   temperatura out of range: {temp_out}")

            if "precipitacion" in columns:
                precip_out = df.filter(
                    "CAST(`precipitacion` AS double) < 0 OR CAST(`precipitacion` AS double) > 500"
                ).count()
                results["validations"].append(
                    {
                        "expectation": "range_precipitacion_0_500",
                        "column": "precipitacion",
                        "success": precip_out == 0,
                        "out_of_range": precip_out,
                    }
                )
                print(f"   precipitacion out of range: {precip_out}")

    # Save results
    s3 = boto3.client("s3")
    key = f"dq_results/{args['table_name']}_{args['suite_name']}_{time.strftime('%Y%m%d_%H%M%S')}.json"

    s3.put_object(
        Bucket=args["results_bucket"],
        Key=key,
        Body=json.dumps(results, indent=2, default=str),
    )

    print(f"📈 Results saved to s3://{args['results_bucket']}/{key}")

    if total_rows > 0:
        all_success = all(v.get("success", False) for v in results["validations"])
        print(f"✅ Successful validations: {all_success}")

        if not all_success:
            print("⚠️ Some validations failed - check results")
    else:
        print("⚠️ Empty table - validations not applied")

    print("=" * 50)
    print("✅ JOB COMPLETED")
    print("=" * 50)

except Exception as e:
    print(f"❌ Fatal error: {str(e)}")
    import traceback

    traceback.print_exc()
    raise
finally:
    job.commit()
