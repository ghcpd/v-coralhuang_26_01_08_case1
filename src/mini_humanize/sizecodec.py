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
    if strip_trailing_zeros and "." in num:
        num = num.rstrip("0").rstrip(".")

    # Ensure we never return a negative zero (e.g. "-0") — normalize to "0"
    try:
        # Use Decimal to accurately detect a zero value even for formatted strings
        from decimal import Decimal

        if Decimal(num) == 0:
            sign = ""
    except Exception:
        # Be conservative: if Decimal isn't usable, keep existing sign behavior
        pass

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
    Parse a human-readable size string into an integer number of bytes.

    Rules / behavior (summary):
    - Accepts integer, decimal and scientific notation numbers (eg. 1, 1.5, 1e3).
    - Units are case-insensitive. Supported unit forms:
        - IEC binary: KiB, MiB, GiB, TiB, PiB => base 1024
        - SI decimal: kB, MB, GB, TB, PB => base 1000
        - Short GNU: K, M, G, T, P => base determined by `default_binary`
        - Legacy: KB/MB/GB are treated as decimal by default (1000) but honored by
          `default_binary` when set to True.
        - Bytes: B or no suffix => bytes
    - Whitespace between number and unit is optional.
    - If `allow_thousands_separator` is True, the function will accept the common
      thousands separator for the given `locale` (only basic support: en uses
      ',' and '.'; de uses '.' and ',').
    - `rounding` determines how fractional bytes are converted:
        - 'floor' -> truncate toward -inf
        - 'nearest' -> round half up
        - 'ceil' -> ceil toward +inf
    - If `strict` is True, unknown units or unparsable input raise ValueError.
      If False (permissive), unknown trailing text is ignored when possible.
    - `allow_negative` controls whether negative values are permitted.
    - `min_value` and `max_value` are inclusive constraints applied after rounding.

    Implementation notes:
    - Uses `decimal.Decimal` with adjusted precision to avoid float precision loss
      and to support very large numbers (>= 2**70).
    - Complexity is O(n) in the input length.
    """
    import re
    from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_HALF_UP, ROUND_CEILING, InvalidOperation

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    s = text.strip()
    if not s:
        raise ValueError("empty size string")

    # Locale-aware separators (simple heuristic)
    if locale and locale.lower().startswith("de"):
        dec_point = ","
        thou_sep = "."
    else:
        # default to en_US style
        dec_point = "."
        thou_sep = ","

    # Normalize locale specifics into a working text for regex parsing.
    working = s

    # Preprocess thousands separator and decimal point
    if allow_thousands_separator and thou_sep and thou_sep != dec_point:
        working = working.replace(thou_sep, "")
    if dec_point != ".":
        working = working.replace(dec_point, ".")

    # Accept underscores in numeric literals
    working = working.replace("_", "")

    # Use regex to extract the leading numeric part (allow exponent 'e'/'E')
    # If strict, require full-string match (number + optional unit). If permissive,
    # allow trailing junk after the unit.
    num_unit_pattern = r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)(?:\s*([a-zA-Z]+))?\s*$"
    m = re.match(num_unit_pattern, working) if strict else re.match(r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)(?:\s*([a-zA-Z]+))?", working)

    if not m:
        # permissive: try to extract leading numeric part
        if not strict:
            num_match = re.match(r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)", working)
            if not num_match:
                raise ValueError(f"invalid format: {original_text}")
            num_str = num_match.group(1)
            unit_part = working[num_match.end():].strip()
        else:
            raise ValueError(f"invalid format: {original_text}")
    else:
        num_str = m.group(1)
        unit_part = (m.group(2) or "").strip()

    # Validate numeric part as Decimal using a conservative precision
    try:
        digits = len(re.sub(r"[^0-9]", "", num_str))
        prec = max(50, digits + 10)
        with localcontext() as ctx:
            ctx.prec = prec
            number = Decimal(num_str)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid numeric value: {num_str!r}") from exc

    # Determine multiplier from unit_part
    u = unit_part.strip().lower()

    # Accept synonyms
    if u.endswith("bytes"):
        u = u[:-5].strip()
    if u == "b":
        u = ""

    multipliers: dict[str, int] = {}
    # binary (KiB etc.)
    prefixes = ["k", "m", "g", "t", "p"]
    for idx, pfx in enumerate(prefixes, 1):
        multipliers[f"{pfx}i"] = 1024 ** idx  # ki, mi, ...
        multipliers[f"{pfx}ib"] = 1024 ** idx
        multipliers[f"{pfx}b"] = 1000 ** idx  # kB, MB -> decimal by default
        multipliers[f"{pfx}"] = (1024 ** idx) if default_binary else (1000 ** idx)

    multipliers[""] = 1

    # Legacy uppercase KB/MB variants are accepted via lowercasing above

    # Resolve unit
    mult = None
    if u in multipliers:
        mult = multipliers[u]
    else:
        # Try patterns like kib, mib, kb with optional 'b'
        u_stripped = u.rstrip("b")
        if u_stripped in prefixes:
            # single letter
            mult = (1024 ** (prefixes.index(u_stripped) + 1)) if default_binary else (1000 ** (prefixes.index(u_stripped) + 1))
        else:
            if strict:
                raise ValueError(f"unknown unit: {unit_part!r}")
            # permissive: ignore unknown unit
            mult = 1

    # Compute bytes precisely
    with localcontext() as ctx:
        # ensure enough precision
        ctx.prec = max(50, number.as_tuple().digits and len(number.as_tuple().digits) + 10)
        total = number * Decimal(mult)

        # Apply rounding
        if rounding == "floor":
            rounded = total.to_integral_value(rounding=ROUND_FLOOR)
        elif rounding == "ceil":
            rounded = total.to_integral_value(rounding=ROUND_CEILING)
        else:
            # nearest: tie-breaking away from zero (ROUND_HALF_UP)
            rounded = total.to_integral_value(rounding=ROUND_HALF_UP)

    try:
        result = int(rounded)
    except (OverflowError, InvalidOperation) as exc:
        raise ValueError("value out of range") from exc

    if result < 0 and not allow_negative:
        raise ValueError("negative values are not allowed")

    if min_value is not None and result < min_value:
        raise ValueError(f"value {result} is less than minimum allowed {min_value}")
    if max_value is not None and result > max_value:
        raise ValueError(f"value {result} is greater than maximum allowed {max_value}")

    return result
