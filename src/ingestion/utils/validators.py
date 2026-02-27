"""
Funciones de validación reutilizables para los jobs de Glue
"""
import re
from datetime import datetime
from typing import List, Optional

def validate_rinde(value: str) -> bool:
    """Valida que el rinde esté entre 0 y 20000"""
    try:
        rinde = float(value)
        return 0 <= rinde <= 20000
    except (ValueError, TypeError):
        return False

def validate_temperatura(value: str) -> bool:
    """Valida que la temperatura esté entre -20 y 50"""
    try:
        temp = float(value)
        return -20 <= temp <= 50
    except (ValueError, TypeError):
        return False

def validate_precipitacion(value: str) -> bool:
    """Valida que la precipitación esté entre 0 y 500"""
    try:
        precip = float(value)
        return 0 <= precip <= 500
    except (ValueError, TypeError):
        return False

def validate_fecha(value: str, formato: str = "%Y-%m-%d") -> bool:
    """
    Valida que la fecha tenga el formato correcto YYYY-MM-DD
    Y además que sea una fecha real (ej: 2023-13-45 es inválida)
    """
    if not value or not isinstance(value, str):
        return False
    
    # Primero verificar el patrón
    patron = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(patron, value):
        return False
    
    # Luego verificar que sea una fecha real
    try:
        datetime.strptime(value, formato)
        return True
    except ValueError:
        return False

def validate_not_null(value: Optional[str]) -> bool:
    """Valida que un campo no sea nulo o vacío"""
    return value is not None and str(value).strip() != ""