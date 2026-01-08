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
        # Fix: handle both "-0" and "0" after stripping
        if num == "-0" or num == "":
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
        text: Size string to parse (e.g., "10 MB", "5.5GiB", "1.5e3 KB")
        default_binary: When ambiguous (K/M/G/T/P), use base 1024 (default: False = base 1000)
        default_gnu: When GNU format detected, use base 1024 (default: False = base 1000)
        allow_thousands_separator: Allow comma/space as thousands separator based on locale
        rounding: How to handle fractional bytes - "floor", "nearest", or "ceil"
        strict: Reject invalid/malformed input (False = permissive mode)
        locale: Locale for decimal point ('en_US' uses '.', 'de_DE' uses ',')
        allow_negative: Whether to accept negative values
        min_value: Minimum allowed value (inclusive), None = no minimum
        max_value: Maximum allowed value (inclusive), None = no maximum

    Returns:
        Integer number of bytes

    Raises:
        ValueError: Invalid format, out of range, or negative when not allowed
        
    Supported formats:
        - Binary IEC 60027-2: KiB, MiB, GiB, TiB, PiB, EiB, ZiB, YiB (base 1024)
        - Decimal SI: kB, MB, GB, TB, PB, EB, ZB, YB (base 1000)
        - GNU short: K, M, G, T, P, E, Z, Y (ambiguous, controlled by default_binary)
        - Legacy: KB, MB, GB, TB, PB (ambiguous, controlled by default_binary)
        - Scientific notation: 1.5e3 MB, 2E-1 KB
        - With/without spaces: "10MB" or "10 MB"
        - Thousands separators: "1,000 MB" (if allow_thousands_separator=True)
    """
    import math
    import re
    
    if not text or not isinstance(text, str):
        raise ValueError("text must be a non-empty string")
    
    text = text.strip()
    if not text:
        raise ValueError("text must be a non-empty string")
    
    # Define unit mappings
    # Binary units (IEC 60027-2): unambiguous base 1024
    binary_units = {
        'KiB': 1024,
        'MiB': 1024**2,
        'GiB': 1024**3,
        'TiB': 1024**4,
        'PiB': 1024**5,
        'EiB': 1024**6,
        'ZiB': 1024**7,
        'YiB': 1024**8,
    }
    
    # Decimal SI units: unambiguous base 1000
    decimal_units = {
        'kB': 1000,
        'MB': 1000**2,
        'GB': 1000**3,
        'TB': 1000**4,
        'PB': 1000**5,
        'EB': 1000**6,
        'ZB': 1000**7,
        'YB': 1000**8,
    }
    
    # GNU/Legacy ambiguous units - interpretation depends on defaults
    ambiguous_units = ['K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
    legacy_units = ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    
    # Determine decimal separator and thousands separator based on locale
    if locale.startswith('de_') or locale.startswith('fr_') or locale.startswith('es_'):
        decimal_sep = ','
        thousands_sep = '.' if allow_thousands_separator else None
    else:  # en_US and most others
        decimal_sep = '.'
        thousands_sep = ',' if allow_thousands_separator else None
    
    # Parse the input: number + optional unit
    # Pattern: optional sign, number (with optional scientific notation), optional whitespace, optional unit
    # Build regex pattern for number part
    num_pattern_parts = [r'([+-]?)']  # optional sign
    
    if thousands_sep:
        # Allow thousands separator in integer part
        if thousands_sep == ',':
            num_pattern_parts.append(r'(\d{1,3}(?:,\d{3})*|\d+)')
        else:  # '.'
            num_pattern_parts.append(r'(\d{1,3}(?:\.\d{3})*|\d+)')
    else:
        num_pattern_parts.append(r'(\d+)')
    
    # Decimal part
    if decimal_sep == ',':
        num_pattern_parts.append(r'(?:,(\d+))?')
    else:
        num_pattern_parts.append(r'(?:\.(\d+))?')
    
    # Scientific notation
    num_pattern_parts.append(r'(?:[eE]([+-]?\d+))?')
    
    # Unit part (optional whitespace + optional unit)
    num_pattern_parts.append(r'\s*')
    num_pattern_parts.append(r'([A-Za-z]*)')
    num_pattern_parts.append(r'$')
    
    pattern = ''.join(num_pattern_parts)
    match = re.match(pattern, text)
    
    if not match:
        if strict:
            raise ValueError(f"Invalid size format: '{text}'")
        else:
            # Permissive: try to extract any number
            try:
                return int(float(text))
            except:
                raise ValueError(f"Invalid size format: '{text}'")
    
    sign_str, int_part, dec_part, exp_part, unit = match.groups()
    
    # Remove thousands separators
    if thousands_sep:
        int_part = int_part.replace(thousands_sep, '')
    
    # Build the number
    try:
        if dec_part:
            num_str = f"{int_part}.{dec_part}"
        else:
            num_str = int_part
        
        number = float(num_str)
        
        # Apply scientific notation
        if exp_part:
            number *= 10 ** int(exp_part)
        
        # Apply sign
        if sign_str == '-':
            number = -number
    except (ValueError, OverflowError) as e:
        raise ValueError(f"Invalid number in size string: '{text}'") from e
    
    # Check negative handling
    if number < 0 and not allow_negative:
        raise ValueError(f"Negative values not allowed: '{text}'")
    
    # Determine multiplier based on unit
    unit = unit.strip()
    
    if not unit or unit.upper() == 'B':
        # No unit or just 'B' = bytes
        multiplier = 1
    elif unit in binary_units:
        # Unambiguous binary unit
        multiplier = binary_units[unit]
    elif unit in decimal_units:
        # Unambiguous decimal unit
        multiplier = decimal_units[unit]
    elif unit in ambiguous_units:
        # GNU short form - use default_binary to resolve
        idx = ambiguous_units.index(unit)
        base = 1024 if (default_binary or default_gnu) else 1000
        multiplier = base ** (idx + 1)
    elif unit in legacy_units:
        # Legacy units like KB, MB - use default_binary to resolve
        idx = legacy_units.index(unit)
        base = 1024 if default_binary else 1000
        multiplier = base ** (idx + 1)
    else:
        if strict:
            raise ValueError(f"Unknown unit: '{unit}'")
        else:
            # Permissive: treat as bytes
            multiplier = 1
    
    # Calculate final value
    result_float = number * multiplier
    
    # Check for overflow
    if abs(result_float) > 2**70:
        # Still allow it but ensure we can handle it
        pass
    
    # Apply rounding
    if rounding == "floor":
        result = math.floor(result_float)
    elif rounding == "ceil":
        result = math.ceil(result_float)
    else:  # "nearest"
        result = round(result_float)
    
    # Check constraints
    if min_value is not None and result < min_value:
        raise ValueError(f"Value {result} is below minimum {min_value}")
    if max_value is not None and result > max_value:
        raise ValueError(f"Value {result} is above maximum {max_value}")
    
    return result
