"""
Tests with data samples simulating CSV files
"""
import csv
import tempfile
import os
import pytest

from src.ingestion.utils.validators import (
    validate_rinde,
    validate_temperatura,
    validate_precipitacion,
    validate_fecha,
)


@pytest.fixture
def sample_rinde_csv():
    """Creates a temporary CSV file with yield data"""
    content = """lote_id,campana,rinde,fecha_cosecha
L001,2023,8500,2023-05-15
L002,2023,12000,2023-05-20
L003,2023,500,2023-05-18
L004,2023,25000,2023-05-22
L005,2023,,2023-05-25
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(content)
        return f.name


@pytest.fixture
def sample_clima_csv():
    """Creates a temporary CSV file with climate data"""
    content = """lote_id,fecha,temperatura,precipitacion
L001,2023-05-15,25.5,10.2
L002,2023-05-20,30.1,0
L003,2023-05-18,15.3,25.7
L004,2023-05-22,55.0,5.5
L005,2023-05-25,22.0,
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(content)
        return f.name


def test_lectura_rinde_csv(sample_rinde_csv):
    """Tests that we can read the CSV and validate data"""
    import csv

    with open(sample_rinde_csv, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 5

    # Validate each row
    for row in rows:
        if row["rinde"]:  # if it has yield
            assert validate_rinde(row["rinde"]) in [True, False]
        assert validate_fecha(row["fecha_cosecha"]) in [True, False]

    # Clean up
    os.unlink(sample_rinde_csv)


def test_lectura_clima_csv(sample_clima_csv):
    """Tests that we can read the climate CSV and validate data"""
    import csv

    with open(sample_clima_csv, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 5

    # Validate each row
    for row in rows:
        if row["temperatura"]:
            assert validate_temperatura(row["temperatura"]) in [True, False]
        if row["precipitacion"]:
            assert validate_precipitacion(row["precipitacion"]) in [True, False]
        assert validate_fecha(row["fecha"]) in [True, False]

    # Clean up
    os.unlink(sample_clima_csv)


def test_filas_invalidas_rinde(sample_rinde_csv):
    """Identifies invalid rows in the yield CSV"""
    import csv

    with open(sample_rinde_csv, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # The row with rinde=25000 should be invalid
    fila_invalida = [r for r in rows if r["rinde"] == "25000"][0]
    assert validate_rinde(fila_invalida["rinde"]) is False

    # The row without rinde should have invalid yield
    fila_sin_rinde = [r for r in rows if r["rinde"] == ""][0]
    assert validate_rinde(fila_sin_rinde["rinde"]) is False

    os.unlink(sample_rinde_csv)
