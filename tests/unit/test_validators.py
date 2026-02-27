"""
Tests unitarios para funciones de validación
"""
import sys
import os
import pytest

# Agregar src al path para poder importar
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from ingestion.utils.validators import (
    validate_rinde,
    validate_temperatura,
    validate_precipitacion,
    validate_fecha,
    validate_not_null
)

class TestRindeValidator:
    """Tests para validación de rinde"""
    
    def test_rinde_valido(self):
        assert validate_rinde("5000") is True
        assert validate_rinde("0") is True
        assert validate_rinde("20000") is True
        assert validate_rinde("15000.5") is True
    
    def test_rinde_invalido(self):
        assert validate_rinde("-10") is False
        assert validate_rinde("25000") is False
        assert validate_rinde("") is False
        assert validate_rinde("abc") is False
        assert validate_rinde(None) is False
    
    def test_rinde_limites(self):
        assert validate_rinde("0") is True
        assert validate_rinde("20000") is True
        assert validate_rinde("-0.1") is False
        assert validate_rinde("20000.1") is False

class TestTemperaturaValidator:
    """Tests para validación de temperatura"""
    
    def test_temperatura_valida(self):
        assert validate_temperatura("25") is True
        assert validate_temperatura("-20") is True
        assert validate_temperatura("50") is True
        assert validate_temperatura("0") is True
    
    def test_temperatura_invalida(self):
        assert validate_temperatura("-21") is False
        assert validate_temperatura("51") is False
        assert validate_temperatura("") is False
        assert validate_temperatura("frio") is False

class TestPrecipitacionValidator:
    """Tests para validación de precipitación"""
    
    def test_precipitacion_valida(self):
        assert validate_precipitacion("0") is True
        assert validate_precipitacion("250") is True
        assert validate_precipitacion("500") is True
    
    def test_precipitacion_invalida(self):
        assert validate_precipitacion("-1") is False
        assert validate_precipitacion("501") is False
        assert validate_precipitacion("lluvia") is False

class TestFechaValidator:
    """Tests para validación de fechas"""
    
    def test_fecha_valida(self):
        assert validate_fecha("2023-05-15") is True
        assert validate_fecha("2024-12-31") is True
    
    def test_fecha_invalida(self):
        assert validate_fecha("15-05-2023") is False
        assert validate_fecha("2023/05/15") is False
        assert validate_fecha("") is False
        assert validate_fecha(None) is False
        assert validate_fecha("2023-13-45") is False

class TestNotNullValidator:
    """Tests para validación de nulos"""
    
    def test_not_null_valido(self):
        assert validate_not_null("dato") is True
        assert validate_not_null("123") is True
        assert validate_not_null(" ") is False
    
    def test_not_null_invalido(self):
        assert validate_not_null("") is False
        assert validate_not_null(None) is False