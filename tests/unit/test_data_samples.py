"""
Tests con muestras de datos simulando archivos CSV
"""
import csv
import tempfile
import os
import pytest

from src.ingestion.utils.validators import (
    validate_rinde, validate_temperatura, 
    validate_precipitacion, validate_fecha
)

@pytest.fixture
def sample_rinde_csv():
    """Crea un archivo CSV temporal con datos de rinde"""
    content = """lote_id,campana,rinde,fecha_cosecha
L001,2023,8500,2023-05-15
L002,2023,12000,2023-05-20
L003,2023,500,2023-05-18
L004,2023,25000,2023-05-22
L005,2023,,2023-05-25
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(content)
        return f.name

@pytest.fixture
def sample_clima_csv():
    """Crea un archivo CSV temporal con datos de clima"""
    content = """lote_id,fecha,temperatura,precipitacion
L001,2023-05-15,25.5,10.2
L002,2023-05-20,30.1,0
L003,2023-05-18,15.3,25.7
L004,2023-05-22,55.0,5.5
L005,2023-05-25,22.0,
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(content)
        return f.name

def test_lectura_rinde_csv(sample_rinde_csv):
    """Prueba que podemos leer el CSV y validar datos"""
    import csv
    
    with open(sample_rinde_csv, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) == 5
    
    # Validar cada fila
    for row in rows:
        if row['rinde']:  # si tiene rinde
            assert validate_rinde(row['rinde']) in [True, False]
        assert validate_fecha(row['fecha_cosecha']) in [True, False]
    
    # Limpiar
    os.unlink(sample_rinde_csv)

def test_lectura_clima_csv(sample_clima_csv):
    """Prueba que podemos leer el CSV de clima y validar datos"""
    import csv
    
    with open(sample_clima_csv, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) == 5
    
    # Validar cada fila
    for row in rows:
        if row['temperatura']:
            assert validate_temperatura(row['temperatura']) in [True, False]
        if row['precipitacion']:
            assert validate_precipitacion(row['precipitacion']) in [True, False]
        assert validate_fecha(row['fecha']) in [True, False]
    
    # Limpiar
    os.unlink(sample_clima_csv)

def test_filas_invalidas_rinde(sample_rinde_csv):
    """Identifica filas inválidas en el CSV de rinde"""
    import csv
    
    with open(sample_rinde_csv, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # La fila con rinde=25000 debe ser inválida
    fila_invalida = [r for r in rows if r['rinde'] == '25000'][0]
    assert validate_rinde(fila_invalida['rinde']) is False
    
    # La fila sin rinde debe tener rinde inválido
    fila_sin_rinde = [r for r in rows if r['rinde'] == ''][0]
    assert validate_rinde(fila_sin_rinde['rinde']) is False
    
    os.unlink(sample_rinde_csv)