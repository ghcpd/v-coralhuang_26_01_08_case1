from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union
import re
import decimal

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

    # Note: This implementation has a subtle bug when size is exactly 0
    # and strip_trailing_zeros=True. Agent should identify and fix.
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
            if num == "-0":
                num = "0"
    if num == "0":
        sign = ""

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

    Supports:
    - Decimal and binary units: B, kB/KB, MB, ..., KiB, MiB, ...
    - GNU suffixes: K, M, G, T, P (base depends on default_binary)
    - Scientific notation: 1.5e3 MB
    - Thousands separators: 1,000 MB (if allow_thousands_separator)
    - Negative values (if allow_negative)
    - Rounding modes for fractional bytes

    Ambiguous units (K/M/G/T/P) use base 1024 if default_binary else 1000.
    default_gnu is ignored for parsing.

    Raises ValueError on invalid input if strict=True.
    """
    decimal.getcontext().prec = 100  # High precision for large numbers

    text = text.strip()
    if not text:
        raise ValueError("Empty input string")

    # Handle sign
    sign = 1
    if text.startswith(('+', '-')):
        if text[0] == '-':
            if not allow_negative:
                raise ValueError("Negative values not allowed")
            sign = -1
        text = text[1:].strip()

    # Regex to match number and optional unit
    # Number: digits, optional comma thousands, optional decimal, optional scientific
    pattern = r'^(\d+(?:,\d{3})*(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*([a-zA-Z]+)?$'
    match = re.match(pattern, text)
    if not match:
        raise ValueError(f"Invalid format: {text!r}")

    number_str, unit_str = match.groups()

    # Remove thousands separators if allowed
    if allow_thousands_separator:
        number_str = number_str.replace(',', '')
    elif ',' in number_str:
        raise ValueError("Thousands separators not allowed")

    # Parse number
    try:
        number = decimal.Decimal(number_str)
    except decimal.InvalidOperation:
        raise ValueError(f"Invalid number: {number_str!r}")

    # Get multiplier
    multiplier = 1
    if unit_str:
        multiplier = get_multiplier(unit_str, default_binary)

    # Compute result
    result = number * multiplier * sign

    # Round to integer
    if rounding == "floor":
        rounded = result.to_integral_value(decimal.ROUND_FLOOR)
    elif rounding == "ceil":
        rounded = result.to_integral_value(decimal.ROUND_CEILING)
    elif rounding == "nearest":
        rounded = result.to_integral_value(decimal.ROUND_HALF_UP)
    else:
        raise ValueError(f"Invalid rounding mode: {rounding!r}")

    value = int(rounded)

    # Check constraints
    if min_value is not None and value < min_value:
        raise ValueError(f"Value {value} is below minimum {min_value}")
    if max_value is not None and value > max_value:
        raise ValueError(f"Value {value} is above maximum {max_value}")

    return value


def get_multiplier(unit: str, default_binary: bool) -> int:
    """Get the multiplier for a unit."""
    unit = unit.lower()
    base = 1024 if default_binary else 1000

    multipliers = {
        'b': 1,
        'k': base,
        'm': base ** 2,
        'g': base ** 3,
        't': base ** 4,
        'p': base ** 5,
        'kb': 1000,
        'mb': 1000 ** 2,
        'gb': 1000 ** 3,
        'tb': 1000 ** 4,
        'pb': 1000 ** 5,
        'kib': 1024,
        'mib': 1024 ** 2,
        'gib': 1024 ** 3,
        'tib': 1024 ** 4,
        'pib': 1024 ** 5,
    }

    if unit not in multipliers:
        raise ValueError(f"Unknown unit: {unit!r}")

    return multipliers[unit]
