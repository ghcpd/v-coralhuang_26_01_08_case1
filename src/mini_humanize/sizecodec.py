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
        text: Size string to parse (e.g., "1.5 GB", "2048 KiB", "3e6 MB")
        default_binary: If True, ambiguous units (K/M/G/T/P) use base 1024, else base 1000
        default_gnu: If True, ambiguous single-letter units are treated as GNU-style
        allow_thousands_separator: If True, allows comma/locale-specific separators in numbers
        rounding: How to handle fractional bytes ("floor", "nearest", "ceil")
        strict: If True, reject malformed input; if False, attempt best-effort parsing
        locale: Locale for decimal point (e.g., "en_US" uses '.', "de_DE" uses ',')
        allow_negative: If True, allows negative sizes
        min_value: If set, reject values below this threshold
        max_value: If set, reject values above this threshold

    Returns:
        Size in bytes as an integer

    Raises:
        ValueError: If input is invalid or out of bounds

    Supported formats:
        - Explicit binary: KiB, MiB, GiB, TiB, PiB, EiB, ZiB, YiB
        - Explicit decimal: kB, MB, GB, TB, PB, EB, ZB, YB
        - Legacy IEC: KB, MB, GB, TB, PB, EB, ZB, YB (ambiguous, controlled by default_binary)
        - GNU single-letter: K, M, G, T, P, E, Z, Y (ambiguous, controlled by default_binary/gnu)
        - Scientific notation: 1.5e3, 2E-1
        - With/without spaces: "1.5 GB" or "1.5GB"
        - Case-insensitive suffixes
    """
    import re
    import decimal

    if not isinstance(text, str):
        raise TypeError(f"Expected string, got {type(text).__name__}")

    original_text = text
    text = text.strip()

    if not text:
        raise ValueError("Empty string cannot be parsed as size")

    # Handle explicit sign at the start
    if text.startswith("+") or text.startswith("-"):
        # Keep sign as part of the number; allow negative only if allow_negative is set
        if text.startswith("-") and not allow_negative:
            raise ValueError(f"Negative size not allowed: {original_text}")

    # Unit mappings
    binary_units = {
        "KIB": 1024,
        "MIB": 1024**2,
        "GIB": 1024**3,
        "TIB": 1024**4,
        "PIB": 1024**5,
        "EIB": 1024**6,
        "ZIB": 1024**7,
        "YIB": 1024**8,
    }

    decimal_units = {
        "KB": 1000,
        "MB": 1000**2,
        "GB": 1000**3,
        "TB": 1000**4,
        "PB": 1000**5,
        "EB": 1000**6,
        "ZB": 1000**7,
        "YB": 1000**8,
    }

    gnu_units = {
        "K": 1024 if default_binary else 1000,
        "M": (1024**2) if default_binary else (1000**2),
        "G": (1024**3) if default_binary else (1000**3),
        "T": (1024**4) if default_binary else (1000**4),
        "P": (1024**5) if default_binary else (1000**5),
        "E": (1024**6) if default_binary else (1000**6),
        "Z": (1024**7) if default_binary else (1000**7),
        "Y": (1024**8) if default_binary else (1000**8),
    }

    # Preprocess thousands separator for en locales
    if allow_thousands_separator and locale.startswith("en"):
        text = text.replace(",", "")

    # Regex to extract number and optional unit
    pattern = r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)(?:\s*([a-zA-Z]+))?\s*$"
    m = re.match(pattern, text)
    if not m:
        # Unit-only (e.g., "KB")
        if re.fullmatch(r"\s*[a-zA-Z]+\s*", text):
            raise ValueError(f"No number found in: {original_text}")
        if strict:
            raise ValueError(f"Invalid format: {original_text}")
        # permissive: try to extract leading numeric
        m = re.match(r"^\s*([+-]?\d+(?:\.\d*)?)", text)
        if not m:
            raise ValueError(f"Invalid format: {original_text}")

    number_str = m.group(1)
    unit_str = (m.group(2) or "").strip().upper()

    # Locale-specific handling (de/fr/es)
    if allow_thousands_separator and (locale.startswith("de") or locale.startswith("fr") or locale.startswith("es")):
        if "," in number_str and "." in number_str:
            parts = number_str.rsplit(",", 1)
            number_str = parts[0].replace(".", "") + "." + parts[1]
        elif "," in number_str and "." not in number_str:
            number_str = number_str.replace(",", ".")

    # Parse number using Decimal for precision
    decimal.getcontext().prec = 200
    try:
        number = decimal.Decimal(number_str)
    except decimal.InvalidOperation:
        raise ValueError(f"Invalid number format: {number_str} in {original_text}")

    # Determine multiplier
    if not unit_str or unit_str == "B" or unit_str == "BYTES":
        multiplier = 1
    elif unit_str in binary_units:
        multiplier = binary_units[unit_str]
    elif unit_str in gnu_units:
        multiplier = gnu_units[unit_str]
    elif unit_str in decimal_units:
        if default_binary:
            unit_map = {"KB": "KIB", "MB": "MIB", "GB": "GIB", "TB": "TIB", "PB": "PIB", "EB": "EIB", "ZB": "ZIB", "YB": "YIB"}
            multiplier = binary_units[unit_map.get(unit_str, unit_str)]
        else:
            multiplier = decimal_units[unit_str]
    else:
        if strict:
            raise ValueError(f"Unknown unit: {unit_str} in {original_text}")
        multiplier = 1

    total = number * decimal.Decimal(multiplier)

    # Negative handling
    if total < 0 and not allow_negative:
        raise ValueError(f"Negative size not allowed: {original_text}")

    # Rounding
    if rounding == "floor":
        rounded = total.to_integral_value(rounding=decimal.ROUND_FLOOR)
    elif rounding == "ceil":
        rounded = total.to_integral_value(rounding=decimal.ROUND_CEILING)
    elif rounding == "nearest":
        rounded = total.to_integral_value(rounding=decimal.ROUND_HALF_UP)
    else:
        raise ValueError(f"Invalid rounding mode: {rounding!r}")

    result = int(rounded)

    # Bounds
    if min_value is not None and result < min_value:
        raise ValueError(f"Value {result} is below minimum {min_value}")
    if max_value is not None and result > max_value:
        raise ValueError(f"Value {result} exceeds maximum {max_value}")

    return result
