"""
Reusable validation functions for Glue jobs
"""
import re
from datetime import datetime
from typing import Optional


def validate_rinde(value: str) -> bool:
    """Validates that yield is between 0 and 20000"""
    try:
        rinde = float(value)
        return 0 <= rinde <= 20000
    except (ValueError, TypeError):
        return False


def validate_temperatura(value: str) -> bool:
    """Validates that temperature is between -20 and 50"""
    try:
        temp = float(value)
        return -20 <= temp <= 50
    except (ValueError, TypeError):
        return False


def validate_precipitacion(value: str) -> bool:
    """Validates that precipitation is between 0 and 500"""
    try:
        precip = float(value)
        return 0 <= precip <= 500
    except (ValueError, TypeError):
        return False


def validate_fecha(value: str, formato: str = "%Y-%m-%d") -> bool:
    """
    Validates that the date has the correct format YYYY-MM-DD
    And also that it is a real date (e.g. 2023-13-45 is invalid)
    """
    if not value or not isinstance(value, str):
        return False

    # First check the pattern
    patron = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(patron, value):
        return False

    # Then verify it is a real date
    try:
        datetime.strptime(value, formato)
        return True
    except ValueError:
        return False


def validate_not_null(value: Optional[str]) -> bool:
    """Validates that a field is not null or empty"""
    return value is not None and str(value).strip() != ""
