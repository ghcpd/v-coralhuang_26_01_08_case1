# mini_humanize

A Python library for human-readable size formatting and parsing.

## APIs

### `naturalsize(value, *, binary=False, gnu=False, format="%.1f", strip_trailing_zeros=False) -> str`

Formats a number of bytes into a human-readable string.

**Parameters:**
- `value`: Number of bytes (int, float, or str)
- `binary`: Use binary units (1024 base) instead of decimal (1000 base)
- `gnu`: Use GNU format (no space between number and unit, short unit names)
- `format`: Printf-style format string for the number part
- `strip_trailing_zeros`: Remove trailing zeros and decimal point if applicable

**Examples:**
```python
naturalsize(1000)  # "1.0 kB"
naturalsize(1024, binary=True)  # "1.0 KiB"
naturalsize(1000, gnu=True)  # "1.0K"
naturalsize(1000, strip_trailing_zeros=True)  # "1 kB"
```

### `parse_size(text, *, default_binary=False, default_gnu=False, allow_thousands_separator=False, rounding="nearest", strict=True, locale="en_US", allow_negative=False, min_value=None, max_value=None) -> int`

Parses a human-readable size string into bytes.

**Parameters:**
- `text`: The size string to parse
- `default_binary`: For ambiguous units (K/M/G/T/P), use 1024 base instead of 1000
- `default_gnu`: Ignored (for compatibility)
- `allow_thousands_separator`: Allow commas as thousands separators
- `rounding`: Rounding mode for fractional bytes ("floor", "nearest", "ceil")
- `strict`: Raise errors on invalid input
- `locale`: Locale for number formatting (currently only "en_US" supported)
- `allow_negative`: Allow negative sizes
- `min_value`, `max_value`: Value constraints

**Supported formats:**
- Units: B, kB/KB, MB, GB, TB, PB, KiB, MiB, GiB, TiB, PiB, K, M, G, T, P
- Scientific notation: 1.5e3 MB
- Thousands separators: 1,000 MB (if allowed)
- Case insensitive

**Examples:**
```python
parse_size("1 MB")  # 1000000
parse_size("1 KiB")  # 1024
parse_size("1K", default_binary=True)  # 1024
parse_size("1.5 MB")  # 1500000
```

**Error handling:**
- Raises `ValueError` for invalid input, unknown units, constraint violations
- Ambiguous inputs are resolved based on `default_binary`

**Rounding rules:**
- Fractional bytes are rounded to the nearest integer using the specified mode
- For example, "1.3 KiB" (1331.2 bytes) rounds to 1331 (floor), 1332 (ceil), 1331 (nearest)

## CLI Usage

### Format command
```bash
python -m mini_humanize format <value> [--binary] [--gnu] [--format FORMAT] [--strip-trailing-zeros]
```

Examples:
```bash
python -m mini_humanize format 1000
# Output: 1.0 kB

python -m mini_humanize format 1024 --binary --gnu
# Output: 1.0K
```

### Parse command
```bash
python -m mini_humanize parse <text> [--default-binary] [--allow-thousands-separator] [--rounding {floor,nearest,ceil}] [--allow-negative] [--min-value INT] [--max-value INT]
```

Examples:
```bash
python -m mini_humanize parse "1 MB"
# Output: 1000000

python -m mini_humanize parse "1K" --default-binary
# Output: 1024
```

## Running Tests

To run the full test suite:

```bash
python run_tests
```

This script will install required dependencies (pytest, pytest-cov) if not present and run all tests.