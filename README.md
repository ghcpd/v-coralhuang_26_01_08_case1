# mini_humanize

A Python library for converting between byte sizes and human-readable strings. Provides bidirectional conversion with extensive format support and customization options.

## Features

- **Format byte sizes** into human-readable strings (e.g., `1000000` → `"1.0 MB"`)
- **Parse human-readable strings** back to bytes (e.g., `"1.5 GB"` → `1500000000`)
- Support for both **decimal (SI)** and **binary (IEC)** units
- **GNU-style short format** (K, M, G, T, P)
- **Scientific notation** support
- **Locale-aware** decimal separators
- **Multiple rounding modes** for fractional bytes
- **Comprehensive error handling** with strict and permissive modes
- **Round-trip consistency** between format and parse operations

## Installation

```bash
# Install development dependencies
pip install -e ".[dev]"
```

## Python API

### naturalsize

Convert byte values to human-readable strings.

```python
from mini_humanize import naturalsize

# Basic usage (decimal units, base 1000)
naturalsize(1000)           # "1.0 kB"
naturalsize(1000000)        # "1.0 MB"
naturalsize(1500000)        # "1.5 MB"

# Binary units (base 1024)
naturalsize(1024, binary=True)      # "1.0 KiB"
naturalsize(1048576, binary=True)   # "1.0 MiB"

# GNU short format
naturalsize(1000, gnu=True)                  # "1.0K"
naturalsize(1024, gnu=True, binary=True)     # "1.0K"

# Custom formatting
naturalsize(1234567, format="%.2f")          # "1.23 MB"
naturalsize(1000000, strip_trailing_zeros=True)  # "1 MB"
```

#### Parameters

- **value** (`int | float | str`): The byte value to format
- **binary** (`bool`, default `False`): Use binary units (base 1024, KiB/MiB/GiB) instead of decimal (base 1000, kB/MB/GB)
- **gnu** (`bool`, default `False`): Use GNU short format (no space, short suffixes: K/M/G instead of kB/MB/GB)
- **format** (`str`, default `"%.1f"`): Printf-style format string for the number
- **strip_trailing_zeros** (`bool`, default `False`): Remove trailing zeros and decimal point if not needed

#### Returns

`str`: Formatted size string

#### Behavior

**Decimal mode (default):**
- Units: B, kB, MB, GB, TB, PB
- Base: 1000
- Format: `"<number> <unit>"` (with space)

**Binary mode:**
- Units: B, KiB, MiB, GiB, TiB, PiB
- Base: 1024
- Format: `"<number> <unit>"` (with space)

**GNU mode:**
- Units: B, K, M, G, T, P
- Base: 1000 (decimal) or 1024 (binary)
- Format: `"<number><unit>"` (no space)

**Negative values:** Preserved with leading `-` sign

**Default format:** Uses `%.1f` which rounds to one decimal place

### parse_size

Parse human-readable size strings into byte values.

```python
from mini_humanize import parse_size

# Basic usage
parse_size("1 MB")          # 1000000
parse_size("1.5 GB")        # 1500000000
parse_size("100")           # 100 (bytes)

# Binary units
parse_size("1 MiB")         # 1048576
parse_size("1 GiB")         # 1073741824

# Ambiguous units - controlled by defaults
parse_size("1 M")                           # 1000000 (decimal by default)
parse_size("1 M", default_binary=True)      # 1048576 (binary)
parse_size("1 KB")                          # 1000 (decimal by default)
parse_size("1 KB", default_binary=True)     # 1024 (binary)

# Scientific notation
parse_size("1.5e3 MB")      # 1500000000
parse_size("2E-1 kB")       # 200

# Thousands separators
parse_size("1,000 MB", allow_thousands_separator=True)  # 1000000000

# Rounding modes
parse_size("1.5 B", rounding="floor")    # 1
parse_size("1.5 B", rounding="ceil")     # 2
parse_size("1.5 B", rounding="nearest")  # 2 (default)

# Negative values (must be explicitly allowed)
parse_size("-100 MB", allow_negative=True)  # -100000000

# Value constraints
parse_size("50 MB", min_value=1000, max_value=100000000)  # 50000000
```

#### Parameters

- **text** (`str`): Size string to parse (e.g., "10 MB", "5.5GiB", "1.5e3 kB")
- **default_binary** (`bool`, default `False`): When ambiguous units (K/M/G/T/P or KB/MB/GB) are used, interpret as base 1024 instead of base 1000
- **default_gnu** (`bool`, default `False`): Alternative flag for GNU format ambiguity resolution (same as default_binary for GNU short units)
- **allow_thousands_separator** (`bool`, default `False`): Allow comma or period as thousands separator (locale-dependent)
- **rounding** (`"floor" | "nearest" | "ceil"`, default `"nearest"`): How to handle fractional bytes
  - `"floor"`: Always round down
  - `"nearest"`: Round to nearest integer (banker's rounding)
  - `"ceil"`: Always round up
- **strict** (`bool`, default `True`): Reject invalid/malformed input; when `False`, attempts permissive parsing
- **locale** (`str`, default `"en_US"`): Locale for decimal separator
  - `"en_US"`: Uses `.` for decimal, `,` for thousands
  - `"de_DE"`, `"fr_FR"`, etc.: Uses `,` for decimal, `.` for thousands
- **allow_negative** (`bool`, default `False`): Whether to accept negative values
- **min_value** (`int | None`, default `None`): Minimum allowed value (inclusive), raises ValueError if below
- **max_value** (`int | None`, default `None`): Maximum allowed value (inclusive), raises ValueError if above

#### Returns

`int`: Number of bytes

#### Raises

- **ValueError**: Invalid format, out of range, or negative when not allowed
- **ValueError**: Empty or whitespace-only input
- **ValueError**: Unknown unit (in strict mode)

#### Supported Formats

**Unambiguous binary units (IEC 60027-2):**
- KiB, MiB, GiB, TiB, PiB, EiB, ZiB, YiB
- Always base 1024

**Unambiguous decimal units (SI):**
- kB, MB, GB, TB, PB, EB, ZB, YB
- Always base 1000

**Ambiguous GNU short units:**
- K, M, G, T, P, E, Z, Y
- Interpretation controlled by `default_binary` flag
- Default: base 1000

**Ambiguous legacy units:**
- KB, MB, GB, TB, PB, EB, ZB, YB
- Interpretation controlled by `default_binary` flag
- Default: base 1000

**Scientific notation:**
- `1.5e3 MB` (1500 MB)
- `2E-1 kB` (0.2 kB = 200 bytes)

**Spacing:**
- With space: `"10 MB"`, `"1.5 GiB"`
- Without space: `"10MB"`, `"1.5GiB"`

**Thousands separators** (when `allow_thousands_separator=True`):
- `"1,000 MB"` (en_US locale)
- `"1.000 MB"` (de_DE locale)

## CLI Usage

The library provides a command-line interface with two subcommands: `format` and `parse`.

### Format Command

Convert bytes to human-readable format.

```bash
# Basic usage
python -m mini_humanize format 1000000
# Output: 1.0 MB

# Binary mode
python -m mini_humanize format 1048576 --binary
# Output: 1.0 MiB

# GNU format
python -m mini_humanize format 1000000 --gnu
# Output: 1.0M

# Custom precision
python -m mini_humanize format 1234567 --format "%.2f"
# Output: 1.23 MB

# Strip trailing zeros
python -m mini_humanize format 1000000 --strip-trailing-zeros
# Output: 1 MB

# Combine options
python -m mini_humanize format 1048576 --binary --gnu --strip-trailing-zeros
# Output: 1M
```

#### Format Options

- `--binary`: Use binary units (KiB, MiB, GiB) with base 1024
- `--gnu`: Use GNU short format (K, M, G without space)
- `--format FORMAT`: Custom printf-style format string (default: `"%.1f"`)
- `--strip-trailing-zeros`: Remove trailing zeros from decimal part

### Parse Command

Convert human-readable size to bytes.

```bash
# Basic usage
python -m mini_humanize parse "1 MB"
# Output: 1000000

# Binary unit
python -m mini_humanize parse "1 MiB"
# Output: 1048576

# Ambiguous unit with binary interpretation
python -m mini_humanize parse "1 M" --default-binary
# Output: 1048576

# Thousands separator
python -m mini_humanize parse "1,000 MB" --allow-thousands-separator
# Output: 1000000000

# Rounding modes
python -m mini_humanize parse "1.9 B" --rounding floor
# Output: 1

python -m mini_humanize parse "1.1 B" --rounding ceil
# Output: 2

# Negative values
python -m mini_humanize parse "-100 MB" --allow-negative
# Output: -100000000

# Value constraints
python -m mini_humanize parse "50 MB" --min-value 1000 --max-value 100000000
# Output: 50000000
```

#### Parse Options

- `--default-binary`: Interpret ambiguous units (K/M/G/KB/MB/GB) as base 1024
- `--default-gnu`: Alternative flag for GNU format (same as --default-binary)
- `--allow-thousands-separator`: Allow comma/period as thousands separator
- `--rounding {floor,nearest,ceil}`: Rounding mode for fractional bytes (default: nearest)
- `--strict` / `--permissive`: Strict parsing (reject invalid) vs permissive (default: strict)
- `--locale LOCALE`: Locale for decimal separator (default: en_US)
- `--allow-negative`: Accept negative values
- `--min-value N`: Minimum allowed value (inclusive)
- `--max-value N`: Maximum allowed value (inclusive)

## Design Decisions

### Ambiguity Resolution

**Problem:** Some size units are ambiguous in real-world usage:
- **K, M, G, T, P**: Could mean 1000 or 1024-based
- **KB, MB, GB**: Historically used for both decimal (SI) and binary (IEC) contexts

**Solution:**
- **Unambiguous units preferred**: Use `kB` (decimal) or `KiB` (binary) for clarity
- **Ambiguous units default to decimal**: `parse_size("1 KB")` → 1000 bytes (base 1000)
- **Override with `default_binary=True`**: `parse_size("1 KB", default_binary=True)` → 1024 bytes
- **This matches modern SI standards** where KB = 1000 bytes, and KiB = 1024 bytes

### Rounding Behavior

**Problem:** Size strings often represent fractional bytes (e.g., "1.5 B"), but byte counts must be integers.

**Solution:**
- **Default: "nearest"** - Uses Python's `round()` (banker's rounding)
- **"floor"** - Always rounds down (conservative)
- **"ceil"** - Always rounds up (ensures capacity)
- **Rounding happens after unit conversion**, so "1.5 kB" becomes 1500 bytes (not rounded)

### Error Handling

**Strict mode (default):**
- Rejects unknown units
- Rejects malformed input
- Rejects negative values (unless `allow_negative=True`)
- Enforces min/max constraints
- **Use when:** Input comes from untrusted sources or exact validation is required

**Permissive mode (`strict=False`):**
- Ignores unknown units (treats as bytes)
- Attempts to extract any number from input
- **Use when:** Parsing legacy data or user input where flexibility is needed

### Locale Support

**Decimal separators vary by locale:**
- **en_US**: `1.5 MB` (period for decimal)
- **de_DE**: `1,5 MB` (comma for decimal)

**Thousands separators:**
- **en_US**: `1,000 MB` (comma for thousands)
- **de_DE**: `1.000 MB` (period for thousands)

Set `locale` parameter to match your input format.

### Large Number Support

**Requirement:** Must handle numbers >= 2^70 bytes without precision loss.

**Implementation:**
- Uses Python's arbitrary-precision integers
- Parse complexity is O(n) where n = input string length
- Tested up to 2^70 bytes (1,180,591 TiB / 1.07 EiB)

### Backward Compatibility

**naturalsize function:**
- Default behavior unchanged from baseline
- Default outputs: `"1.0 kB"`, `"1.5 MB"`, etc.
- Existing code continues to work without modification

## Testing

### Running Tests

```bash
# Run all tests (one-click command)
./run_tests

# Or with pytest directly (after installing dependencies)
pytest

# With coverage
pytest --cov=mini_humanize --cov-report=term-missing

# Run specific test file
pytest tests/test_parse_size.py

# Run specific test class
pytest tests/test_parse_size.py::TestParseSizeBasic

# Run specific test
pytest tests/test_parse_size.py::TestParseSizeBasic::test_bytes_only
```

### Test Structure

```
tests/
├── __init__.py
├── test_naturalsize.py      # Format function tests
├── test_parse_size.py        # Parse function tests  
├── test_roundtrip.py         # Bidirectional consistency
└── test_cli.py               # Command-line interface tests
```

### Test Coverage

The test suite covers:

**Unit Systems:**
- Decimal (SI) units: kB, MB, GB, TB, PB
- Binary (IEC) units: KiB, MiB, GiB, TiB, PiB
- GNU short form: K, M, G, T, P
- Legacy ambiguous: KB, MB, GB

**Number Formats:**
- Integers and floats
- Scientific notation (e.g., `1.5e3 MB`)
- Thousands separators
- Locale-specific decimal separators

**Edge Cases:**
- Zero values
- Negative values
- Very large numbers (>= 2^70)
- Fractional bytes with different rounding modes
- Empty/whitespace input
- Invalid formats and units

**Functional Tests:**
- Round-trip consistency (parse ↔ format)
- CLI subprocess invocation
- Backward compatibility verification
- Error handling (strict vs permissive)
- Value constraints (min/max)

**Performance:**
- O(n) parse complexity verification

### One-Click Test Script

The `run_tests` script provides a zero-configuration test runner:

1. **Checks for pytest** - Installs if missing
2. **Runs full test suite** with coverage reporting
3. **Works in clean environments** - No manual setup required
4. **Repeatable** - Can be run multiple times safely

```bash
# On Unix/Linux/Mac
./run_tests

# On Windows (PowerShell)
.\run_tests
```

## Examples

### Basic Formatting

```python
from mini_humanize import naturalsize

# Storage device sizes
naturalsize(512_000_000_000)              # "512.0 GB" (500 GB HDD)
naturalsize(512_000_000_000, binary=True) # "476.8 GiB"

# Memory sizes (typically binary)
naturalsize(16 * 1024**3, binary=True)    # "16.0 GiB" (16 GB RAM)
naturalsize(8 * 1024**3, binary=True, gnu=True)  # "8.0G"

# File sizes
naturalsize(1_234_567)                     # "1.2 MB"
naturalsize(1_234_567, format="%.3f")      # "1.235 MB"
```

### Basic Parsing

```python
from mini_humanize import parse_size

# User input
user_input = "500 GB"
bytes_needed = parse_size(user_input)  # 500000000000

# Configuration files
max_upload = parse_size("100 MB")      # 100000000
cache_size = parse_size("2 GiB")       # 2147483648

# With validation
try:
    size = parse_size("10 TB", max_value=5_000_000_000_000)
except ValueError as e:
    print(f"Size too large: {e}")
```

### Round-Trip Conversion

```python
from mini_humanize import naturalsize, parse_size

# Format then parse back
original = 1_500_000_000
formatted = naturalsize(original)          # "1.5 GB"
parsed = parse_size(formatted)             # 1500000000
assert parsed == original

# Binary round-trip
original = 1024**3
formatted = naturalsize(original, binary=True)  # "1.0 GiB"
parsed = parse_size(formatted)                  # 1073741824
assert parsed == original
```

### Error Handling

```python
from mini_humanize import parse_size

# Strict mode (default) - validation
try:
    parse_size("100 INVALID")
except ValueError as e:
    print(f"Error: {e}")  # "Unknown unit: 'INVALID'"

# Permissive mode - best effort
result = parse_size("100 INVALID", strict=False)  # 100 (ignores unit)

# Constraints
try:
    parse_size("10 GB", max_value=1_000_000_000)  # 10 billion > 1 billion
except ValueError as e:
    print(f"Error: {e}")  # "Value ... is above maximum ..."
```

## License

This is an evaluation project for agent assessment.

## Contributing

This library is designed for evaluation purposes. For production use, consider [humanize](https://github.com/python-humanize/humanize) or similar established libraries.
