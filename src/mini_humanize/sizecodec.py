from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union

NumberOrString = Union[int, float, str]
RoundingMode = Literal["floor", "nearest", "ceil"]


@dataclass(frozen=True)
class SizeFormatSpec:
    binary: bool = False
    gnu: bool = False
    format: str = "%.1f"
    strip_trailing_zeros: bool = False


def naturalsize(
    value: NumberOrString,
    *,
    binary: bool = False,
    gnu: bool = False,
    format: str = "%.1f",
    strip_trailing_zeros: bool = False,
) -> str:
    """
    Simplified naturalsize, inspired by python-humanize/humanize.

    Baseline behavior:
    - gnu=False:
        decimal units: B, kB, MB, GB, TB, PB
        binary units:  B, KiB, MiB, GiB, TiB, PiB
      Output: "<number> <suffix>"
    - gnu=True:
        decimal units: B, K, M, G, T, P (base 1000)
        binary units:  B, K, M, G, T, P (base 1024)
      Output: "<number><suffix>"

    NOTE: This baseline is intentionally naive for agent evaluation.
    """
    if isinstance(value, str):
        try:
            value_f = float(value)
        except ValueError:
            raise ValueError("value must be a number or numeric string")
    elif isinstance(value, (int, float)):
        value_f = float(value)
    else:
        raise TypeError("value must be int, float, or str")

    sign = "-" if value_f < 0 else ""
    size = abs(value_f)

    if binary:
        base = 1024.0
        units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
        gnu_units = ["B", "K", "M", "G", "T", "P"]
    else:
        base = 1000.0
        units = ["B", "kB", "MB", "GB", "TB", "PB"]
        gnu_units = ["B", "K", "M", "G", "T", "P"]

    idx = 0
    while size >= base and idx < len(units) - 1:
        size /= base
        idx += 1

    suffix = (gnu_units[idx] if gnu else units[idx])

    num = format % size
    if strip_trailing_zeros:
        if "." in num:
            num = num.rstrip("0").rstrip(".")
        # Fix for -0 edge case and empty string after stripping
        if num in ("-0", "", "-"):
            num = "0"

    if gnu:
        return f"{sign}{num}{suffix}"
    return f"{sign}{num} {suffix}"


def parse_size(
    text: str,
    *,
    default_binary: bool = False,
    default_gnu: bool = False,
    allow_thousands_separator: bool = False,
    rounding: RoundingMode = "nearest",
    strict: bool = True,
    locale: str = "en_US",
    allow_negative: bool = False,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    """
    Parse human-readable size string into bytes.

    Args:
        text: Human-readable size string (e.g., "1.5 GB", "2048KiB", "10K")
        default_binary: If True, ambiguous units (K, M, G, T, P, KB, MB...) default to binary (base 1024)
        default_gnu: If True, treat short suffixes as GNU-style (K, M, G, T, P)
        allow_thousands_separator: If True, allow comma/space as thousands separator
        rounding: How to round fractional bytes: "floor", "nearest", or "ceil"
        strict: If True, reject invalid/ambiguous inputs; if False, be more permissive
        locale: Locale for number parsing (affects decimal point)
        allow_negative: If True, allow negative sizes
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)

    Returns:
        Size in bytes as integer

    Raises:
        ValueError: If input is invalid or out of range
        
    Supported units (case-insensitive):
        - Binary (base 1024): B, KiB, MiB, GiB, TiB, PiB, EiB, ZiB, YiB
        - Decimal (base 1000): B, kB, MB, GB, TB, PB, EB, ZB, YB
        - GNU-style (short): K, M, G, T, P, E, Z, Y (base depends on default_binary)
        - Legacy (ambiguous): KB, MB, GB, TB, PB (base depends on default_binary)
        
    Number formats:
        - Integer: 100, -50
        - Decimal: 1.5, 2.3e3
        - Scientific: 1e3, 2.5E-1
        - With separators: 1,000 (if allow_thousands_separator=True)
    """
    import re
    import math
    
    if not text or not isinstance(text, str):
        raise ValueError("Input must be a non-empty string")
    
    original_text = text
    text = text.strip()
    
    if not text:
        raise ValueError("Input must be a non-empty string")
    
    # Define unit mappings
    # Binary units (base 1024)
    binary_units = {
        "kib": 1024,
        "mib": 1024**2,
        "gib": 1024**3,
        "tib": 1024**4,
        "pib": 1024**5,
        "eib": 1024**6,
        "zib": 1024**7,
        "yib": 1024**8,
    }
    
    # GNU-style short suffixes
    gnu_suffixes = {
        "k": 1,
        "m": 2,
        "g": 3,
        "t": 4,
        "p": 5,
        "e": 6,
        "z": 7,
        "y": 8,
    }
    
    # Parse number and unit
    # Pattern: optional sign, number (with optional separators), optional whitespace, optional unit
    if allow_thousands_separator:
        # Allow comma or space as thousands separator
        number_pattern = r'^([+-]?)\s*(\d[\d,\s]*\.?\d*(?:[eE][+-]?\d+)?)\s*([a-zA-Z]*)$'
    else:
        number_pattern = r'^([+-]?)\s*(\d+\.?\d*(?:[eE][+-]?\d+)?)\s*([a-zA-Z]*)$'
    
    match = re.match(number_pattern, text)
    if not match:
        raise ValueError(f"Invalid size format: {original_text}")
    
    sign_str, number_str, unit_str = match.groups()
    
    # Handle sign
    if sign_str == '-':
        if not allow_negative:
            raise ValueError(f"Negative values not allowed: {original_text}")
        is_negative = True
    else:
        is_negative = False
    
    # Parse number
    # Remove thousands separators if allowed
    if allow_thousands_separator:
        # Remove commas and spaces from number
        number_str = number_str.replace(',', '').replace(' ', '')
    
    # Handle locale-specific decimal point
    if locale.startswith('de') or locale.startswith('fr') or locale.startswith('es'):
        # European locales use comma as decimal separator
        number_str = number_str.replace(',', '.')
    
    try:
        number = float(number_str)
    except ValueError:
        raise ValueError(f"Invalid number format: {number_str} in {original_text}")
    
    if math.isnan(number) or math.isinf(number):
        raise ValueError(f"Invalid number value: {original_text}")
    
    # Parse unit
    unit_lower = unit_str.lower() if unit_str else ''
    
    if not unit_lower or unit_lower == 'b':
        # No unit or just 'B' means bytes
        multiplier = 1
    elif unit_lower in binary_units:
        # Explicit binary unit (KiB, MiB, etc.)
        multiplier = binary_units[unit_lower]
    elif unit_lower in ['kb', 'mb', 'gb', 'tb', 'pb', 'eb', 'zb', 'yb']:
        # Ambiguous legacy units - depends on default_binary flag
        exponent = {'kb': 1, 'mb': 2, 'gb': 3, 'tb': 4, 'pb': 5, 'eb': 6, 'zb': 7, 'yb': 8}[unit_lower]
        if default_binary:
            multiplier = 1024 ** exponent
        else:
            multiplier = 1000 ** exponent
    elif unit_lower in gnu_suffixes:
        # GNU-style short suffix (K, M, G, T, P, E, Z, Y)
        exponent = gnu_suffixes[unit_lower]
        base = 1024 if default_binary else 1000
        multiplier = base ** exponent
    else:
        if strict:
            raise ValueError(f"Unknown unit: {unit_str} in {original_text}")
        else:
            # Permissive mode: treat as bytes
            multiplier = 1
    
    # Calculate result
    result_float = abs(number) * multiplier
    
    # Apply rounding
    if rounding == "floor":
        result = int(math.floor(result_float))
    elif rounding == "ceil":
        result = int(math.ceil(result_float))
    else:  # nearest
        result = int(round(result_float))
    
    # Apply sign
    if is_negative:
        result = -result
    
    # Check constraints
    if min_value is not None and result < min_value:
        raise ValueError(f"Value {result} is below minimum {min_value}")
    if max_value is not None and result > max_value:
        raise ValueError(f"Value {result} exceeds maximum {max_value}")
    
    return result
