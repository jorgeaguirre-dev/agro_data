"""
Great Expectations Data Quality Validator
Versión activa en Step Functions
Ejecuta validaciones declarativas usando GE en AWS Glue
Implementa Great Expectations para validaciones más robustas y reportables
"""

# Instalar GE en el job de Glue
!pip install great_expectations

import sys
import json
import time
import boto3
import great_expectations as ge
from great_expectations.core import ExpectationSuite, ExpectationConfiguration
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions


class GExpectationsValidator:
    """Validador de calidad usando Great Expectations"""
    
    def __init__(self, spark, database_name, table_name, results_bucket, suite_name):
        self.spark = spark
        self.database_name = database_name
        self.table_name = table_name
        self.results_bucket = results_bucket
        self.suite_name = suite_name
        self.glue_client = boto3.client('glue', region_name='us-east-1')
    
    def wait_for_table(self, max_attempts=12, delay=10):
        """Espera a que la tabla esté disponible"""
        for attempt in range(max_attempts):
            try:
                tables = self.glue_client.get_tables(DatabaseName=self.database_name)
                table_names = [t['Name'] for t in tables['TableList']]
                if self.table_name in table_names:
                    print(f"✅ Tabla {self.table_name} encontrada")
                    return True
                print(f"⏳ Intento {attempt + 1}/{max_attempts}")
            except Exception as e:
                print(f"⚠️ Error: {str(e)[:100]}")
            if attempt < max_attempts - 1:
                time.sleep(delay)
        raise Exception(f"Tabla {self.table_name} no disponible")
    
    def load_data(self):
        """Carga datos desde Glue Catalog"""
        query = f"SELECT * FROM `{self.database_name}`.`{self.table_name}`"
        print(f"📊 Ejecutando: {query}")
        return self.spark.sql(query)
    
    def create_expectation_suite(self):
        """Crea una suite de expectativas según el tipo de tabla"""
        suite = ExpectationSuite(f"{self.suite_name}_suite")
        
        if 'rinde' in self.table_name:
            # Expectativas para rinde_lotes
            suite.add_expectation(
                ExpectationConfiguration(
                    expectation_type="expect_column_values_to_be_between",
                    kwargs={"column": "rinde", "min_value": 0, "max_value": 20000}
                )
            )
            suite.add_expectation(
                ExpectationConfiguration(
                    expectation_type="expect_column_values_to_not_be_null",
                    kwargs={"column": "lote_id"}
                )
            )
            suite.add_expectation(
                ExpectationConfiguration(
                    expectation_type="expect_column_values_to_not_be_null",
                    kwargs={"column": "campana"}
                )
            )
        else:
            # Expectativas para clima_diario
            suite.add_expectation(
                ExpectationConfiguration(
                    expectation_type="expect_column_values_to_be_between",
                    kwargs={"column": "temperatura", "min_value": -20, "max_value": 50}
                )
            )
            suite.add_expectation(
                ExpectationConfiguration(
                    expectation_type="expect_column_values_to_be_between",
                    kwargs={"column": "precipitacion", "min_value": 0, "max_value": 500}
                )
            )
            suite.add_expectation(
                ExpectationConfiguration(
                    expectation_type="expect_column_values_to_not_be_null",
                    kwargs={"column": "lote_id"}
                )
            )
            suite.add_expectation(
                ExpectationConfiguration(
                    expectation_type="expect_column_values_to_match_regex",
                    kwargs={"column": "fecha", "regex": "^\\d{4}-\\d{2}-\\d{2}$"}
                )
            )
        
        return suite
    
    def run(self):
        """Ejecuta validaciones y guarda resultados"""
        print("=" * 50)
        print("🚀 INICIANDO GREAT EXPECTATIONS VALIDATOR")
        print("=" * 50)
        
        # 1. Esperar tabla
        self.wait_for_table()
        
        # 2. Cargar datos
        df = self.load_data()
        total_rows = df.count()
        print(f"📊 Registros a validar: {total_rows}")
        
        if total_rows == 0:
            print("⚠️ Tabla vacía")
            return
        
        # 3. Crear suite y validar con GE
        suite = self.create_expectation_suite()
        validator = ge.from_spark_df(df, expectation_suite=suite)
        results = validator.validate()
        
        # 4. Guardar resultados
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        key = f"dq_results/ge_{self.table_name}_{self.suite_name}_{timestamp}.json"
        
        s3 = boto3.client('s3')
        s3.put_object(
            Bucket=self.results_bucket,
            Key=key,
            Body=json.dumps(results.to_json_dict(), indent=2, default=str)
        )
        
        # 5. Generar reporte HTML (opcional)
        html_key = f"dq_reports/ge_{self.table_name}_{self.suite_name}_{timestamp}.html"
        html_content = results.to_html()
        s3.put_object(
            Bucket=self.results_bucket,
            Key=html_key,
            Body=html_content,
            ContentType="text/html"
        )
        
        print(f"📈 Resultados: s3://{self.results_bucket}/{key}")
        print(f"📊 Reporte HTML: s3://{self.results_bucket}/{html_key}")
        
        # 6. Evaluar éxito
        success_rate = results.success_percent
        print(f"✅ Tasa de éxito: {success_rate}%")
        
        if success_rate < 100:
            raise Exception(f"Validaciones fallaron: {results.statistics['unexpected_count']} errores")


def main():
    """Función principal para AWS Glue"""
    # Inicialización estándar de Glue
    args = getResolvedOptions(sys.argv, [
        'JOB_NAME', 'suite_name', 'database_name', 'table_name', 'results_bucket'
    ])
    
    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session
    job = Job(glueContext)
    job.init(args['JOB_NAME'], args)
    
    try:
        validator = GExpectationsValidator(
            spark=spark,
            database_name=args['database_name'],
            table_name=args['table_name'],
            results_bucket=args['results_bucket'],
            suite_name=args['suite_name']
        )
        validator.run()
        job.commit()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()