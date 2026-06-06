"""
Great Expectations Data Quality Validator
Versión activa en Step Functions

Implementa Great Expectations para validaciones más robustas y reportables
"""
import sys
import json
import time
import boto3
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

# Instalar GE en el job de Glue
!pip install great_expectations

# Implementación de validación usando Great Expectations
import great_expectations as ge
from great_expectations.core import ExpectationSuite, ExpectationConfiguration

# Crear suite
suite = ExpectationSuite("agro_quality_suite")

# Agregar expectativas
suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={"column": "rinde", "min_value": 0, "max_value": 20000}
    )
)

# Validar
validator = ge.from_spark_df(df, expectation_suite=suite)
results = validator.validate()

# Generar reporte HTML
results.to_html("dq_report.html")