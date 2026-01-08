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

    # Produce the formatted number using the user format string.
    num = format % size

    # Robustly strip trailing zeros while preserving a single "0" for exact zeros
    # and avoiding a negative zero sign.
    if strip_trailing_zeros and "." in num:
        num = num.rstrip("0").rstrip(".")
        if num in ("", "-0"):
            num = "0"

    # Only show the negative sign for non-zero results (avoid "-0 B").
    if sign and num == "0":
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

    Intentionally left incomplete. Agent must implement:
    - decimal + binary units, with and without spaces
    - KiB/MiB... vs kB/MB...
    - GNU suffixes K/M/G/T/P with ambiguity controlled by defaults
    - IEC 60027-2 legacy units (KB/MB/GB)
    - scientific notation (1.5e3 MB, 2E-1 KB)
    - optional thousands separators (locale-aware decimal point)
    - negative handling policy + strict vs permissive behavior
    - rounding behavior for fractional bytes
    - min/max value constraints with clear error messages
    """
    # Basic locale settings (decimal point, thousands separator).
    LOCALES: dict[str, tuple[str, str]] = {
        "en_US": (".", ","),
        "C": (".", ","),
        "POSIX": (".", ","),
        "de_DE": (",", "."),
    }

    if not text or not isinstance(text, str):
        raise ValueError("text must be a non-empty string")

    decimal_point, thousands_sep = LOCALES.get(locale, LOCALES["en_US"])

    s = text.strip()
    if not s:
        raise ValueError("text must be a non-empty string")

    # Extract optional sign
    sign_char = ""
    if s[0] in "+-":
        sign_char = s[0]
        s = s[1:].lstrip()

    # Find where the unit starts while treating scientific notation correctly
    unit_start = None
    i = 0
    n = len(s)
    seen_decimal = False
    seen_exponent = False
    while i < n:
        ch = s[i]
        if ch.isdigit():
            i += 1
            continue
        if ch == decimal_point and not seen_decimal and not seen_exponent:
            seen_decimal = True
            i += 1
            continue
        if allow_thousands_separator and ch == thousands_sep and not seen_exponent:
            # treat thousands separator as part of the number for now
            i += 1
            continue
        # Handle exponent markers 'e' or 'E' and their sign
        if (ch == "e" or ch == "E") and not seen_exponent:
            # look ahead to ensure this is a valid exponent
            j = i + 1
            if j < n and s[j] in "+-":
                j += 1
            if j < n and s[j].isdigit():
                seen_exponent = True
                i = j
                # consume remaining exponent digits
                while i < n and s[i].isdigit():
                    i += 1
                continue
            # otherwise fall through and treat 'e' as unit start
        if ch.isalpha():
            unit_start = i
            break
        # any other character signals unit start or invalid input
        unit_start = i
        break

    if unit_start is None:
        number_part = s
        unit_part = ""
    else:
        number_part = s[:unit_start].rstrip()
        unit_part = s[unit_start:].strip()
    if not number_part:
        raise ValueError(f"no numeric value found in {text!r}")

    # Handle thousands separator if requested.
    if allow_thousands_separator:
        # Validate thousands grouping: groups of 3 digits from the right in integer part.
        if thousands_sep in number_part:
            int_part, _, frac_part = number_part.partition(decimal_point)
            groups = int_part.split(thousands_sep)
            if len(groups) < 1:
                raise ValueError(f"invalid thousands grouping in {text!r}")
            # First group can be shorter than 3, others must be exactly 3 digits.
            if any((i != 0 and len(g) != 3) for i, g in enumerate(groups)):
                raise ValueError(f"invalid thousands grouping in {text!r}")
            # Rebuild number with '.' as decimal point for Decimal parsing
            number_part = "".join(groups)
            if frac_part:
                number_part += "." + frac_part
    else:
        # If thousands separators are present but not allowed -> error
        if thousands_sep in number_part:
            raise ValueError(
                "thousands separator found in number but allow_thousands_separator is False"
            )

    # Normalize decimal point to '.' for Decimal
    if decimal_point != ".":
        if decimal_point in number_part:
            number_part = number_part.replace(decimal_point, ".")

    # At this point number_part should be a valid numeric literal (allow sci notation)
    try:
        from decimal import Decimal, getcontext, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_UP


        getcontext().prec = max(28, 100)
        dec = Decimal(number_part)
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError(f"invalid numeric value {number_part!r}: {exc}")

    # Normalize unit part
    u = unit_part.lower()
    if u.endswith("s"):
        u = u[:-1]

    # Map unit prefixes to powers
    powers = {"k": 1, "m": 2, "g": 3, "t": 4, "p": 5, "e": 6}

    if u == "" or u == "b" or u == "byte":
        multiplier = 1
    else:
        # Recognize KiB/MiB style (explicit binary)
        if u.endswith("ib"):
            prefix = u[:-2]
            if prefix not in powers:
                raise ValueError(f"unknown unit {unit_part!r}")
            multiplier = 1024 ** powers[prefix]
        # Legacy/ambiguous forms that end with 'b' (KB, kB, MB ...)
        elif u.endswith("b"):
            prefix = u[:-1]
            if prefix not in powers:
                raise ValueError(f"unknown unit {unit_part!r}")
            base = 1024 if default_binary else 1000
            multiplier = base ** powers[prefix]
        # Single-letter GNU-style (K, M, ...)
        elif len(u) == 1 and u in powers:
            if not default_gnu and strict:
                raise ValueError(
                    "single-letter suffix (e.g. 'K') is ambiguous; set default_gnu or use a B/iB suffix"
                )
            base = 1024 if default_binary else 1000
            multiplier = base ** powers[u]
        else:
            # Be permissive when strict is False: try to match leading letter
            if not strict:
                if u and u[0] in powers:
                    base = 1024 if default_binary else 1000
                    multiplier = base ** powers[u[0]]
                else:
                    # Unknown suffix -> interpret as bytes in permissive mode
                    multiplier = 1
            else:
                raise ValueError(f"unknown or unsupported unit {unit_part!r}")

    # Apply sign
    if sign_char == "-":
        dec = -dec

    # Convert to bytes (Decimal * multiplier) and round according to policy
    bytes_dec = dec * Decimal(multiplier)

    rounding_map = {"floor": ROUND_FLOOR, "nearest": ROUND_HALF_UP, "ceil": ROUND_CEILING}
    if rounding not in rounding_map:
        raise ValueError("invalid rounding mode")

    rounded = int(bytes_dec.to_integral_value(rounding=rounding_map[rounding]))

    # Negative value policy
    if rounded < 0 and not allow_negative:
        raise ValueError("negative sizes are not allowed")

    # Min / Max checks
    if min_value is not None and rounded < min_value:
        raise ValueError(f"value {rounded} is less than minimum allowed {min_value}")
    if max_value is not None and rounded > max_value:
        raise ValueError(f"value {rounded} is greater than maximum allowed {max_value}")

    return rounded
