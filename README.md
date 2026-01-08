# mini_humanize

A production-ready Python library for converting between bytes and human-readable size strings.

## Features

- **naturalsize**: Convert bytes to human-readable format (e.g., `1000` → `"1.0 kB"`)
- **parse_size**: Parse human-readable size strings back to bytes (e.g., `"1.5 GB"` → `1500000000`)
- **CLI interface**: Command-line tools for both operations
- **Multiple unit systems**: Binary (KiB, MiB) and decimal (kB, MB) units
- **GNU-style formatting**: Short suffixes (K, M, G, T, P)
- **Flexible parsing**: Scientific notation, thousands separators, case-insensitive
- **High precision**: Handles numbers up to 2^80 bytes without precision loss

## Installation

```bash
pip install -e .
```

For development with testing:

```bash
pip install -e ".[dev]"
```

## Python API

### naturalsize

Convert numeric byte values to human-readable strings.

```python
from mini_humanize import naturalsize

# Basic usage (decimal, base 1000)
naturalsize(1000)        # "1.0 kB"
naturalsize(1500000)     # "1.5 MB"
naturalsize(2500000000)  # "2.5 GB"

# Binary units (base 1024)
naturalsize(1024, binary=True)       # "1.0 KiB"
naturalsize(1048576, binary=True)    # "1.0 MiB"

# GNU-style (no space between number and unit)
naturalsize(1000, gnu=True)                    # "1.0K"
naturalsize(1024, binary=True, gnu=True)       # "1.0K"

# Custom formatting
naturalsize(1234, format="%.2f")               # "1.23 kB"
naturalsize(1000, strip_trailing_zeros=True)   # "1 kB"

# Negative values
naturalsize(-1500)       # "-1.5 kB"
```

**Parameters:**
- `value` (int, float, or str): The byte value to format
- `binary` (bool, default=False): Use binary units (KiB, MiB) with base 1024
- `gnu` (bool, default=False): Use GNU-style short suffixes (K, M, G) without space
- `format` (str, default="%.1f"): Printf-style format string for the number
- `strip_trailing_zeros` (bool, default=False): Remove trailing zeros and decimal point

**Returns:** Human-readable size string

**Units:**
- Decimal (binary=False): B, kB, MB, GB, TB, PB
- Binary (binary=True): B, KiB, MiB, GiB, TiB, PiB
- GNU-style (gnu=True): B, K, M, G, T, P

### parse_size

Parse human-readable size strings into bytes.

```python
from mini_humanize import parse_size

# Basic usage - explicit binary units
parse_size("1 KiB")      # 1024
parse_size("1.5 MiB")    # 1572864
parse_size("2 GiB")      # 2147483648

# Decimal units (base 1000)
parse_size("1 kB")       # 1000
parse_size("1.5 MB")     # 1500000
parse_size("2 GB")       # 2000000000

# GNU-style short suffixes
parse_size("1K")                          # 1000 (decimal by default)
parse_size("1K", default_binary=True)     # 1024 (binary with flag)
parse_size("1.5M")                        # 1500000
parse_size("1.5M", default_binary=True)   # 1572864

# Ambiguous legacy units (KB, MB, GB)
parse_size("1 KB")                        # 1000 (decimal by default)
parse_size("1 KB", default_binary=True)   # 1024 (binary with flag)

# Scientific notation
parse_size("1.5e3 MB")   # 1500000000
parse_size("2E6 B")      # 2000000

# Thousands separators
parse_size("1,000 B", allow_thousands_separator=True)  # 1000

# Rounding modes for fractional bytes
parse_size("1.9 B", rounding="floor")    # 1
parse_size("1.9 B", rounding="ceil")     # 2
parse_size("1.5 B", rounding="nearest")  # 2 (default)

# Negative values
parse_size("-100 B", allow_negative=True)  # -100

# Constraints
parse_size("100 B", min_value=50, max_value=200)  # 100
```

**Parameters:**
- `text` (str): Human-readable size string to parse
- `default_binary` (bool, default=False): Treat ambiguous units (K, M, KB, MB, etc.) as binary (base 1024)
- `default_gnu` (bool, default=False): Treat short suffixes as GNU-style
- `allow_thousands_separator` (bool, default=False): Allow comma/space as thousands separator
- `rounding` (str, default="nearest"): How to round fractional bytes ("floor", "nearest", "ceil")
- `strict` (bool, default=True): Reject unknown units; if False, treat as bytes
- `locale` (str, default="en_US"): Locale for number parsing (affects decimal point)
- `allow_negative` (bool, default=False): Allow negative sizes
- `min_value` (int | None, default=None): Minimum allowed value (inclusive)
- `max_value` (int | None, default=None): Maximum allowed value (inclusive)

**Returns:** Size in bytes as integer

**Raises:** `ValueError` if input is invalid or out of range

**Supported Units:**
- Binary (base 1024): B, KiB, MiB, GiB, TiB, PiB, EiB, ZiB, YiB
- Decimal (base 1000): B, kB, MB, GB, TB, PB, EB, ZB, YB
- GNU-style short: K, M, G, T, P, E, Z, Y (base depends on `default_binary`)
- Legacy ambiguous: KB, MB, GB, TB, PB (base depends on `default_binary`)

**Number Formats:**
- Integer: `100`, `-50`
- Decimal: `1.5`, `2.3`
- Scientific: `1e3`, `2.5E-1`
- With separators: `1,000` (if `allow_thousands_separator=True`)

## CLI Usage

The library provides a command-line interface with two subcommands: `format` and `parse`.

### Format Command

Convert bytes to human-readable format:

```bash
# Basic usage
python -m mini_humanize format 1000
# Output: 1.0 kB

# Binary units
python -m mini_humanize format 1024 --binary
# Output: 1.0 KiB

# GNU-style
python -m mini_humanize format 1000 --gnu
# Output: 1.0K

# Custom format
python -m mini_humanize format 1234 --format "%.2f"
# Output: 1.23 kB

# Strip trailing zeros
python -m mini_humanize format 1000 --strip-trailing-zeros
# Output: 1 kB

# Combine options
python -m mini_humanize format 1048576 --binary --gnu --strip-trailing-zeros
# Output: 1M
```

**Format Options:**
- `value`: The byte value to format (required)
- `--binary`: Use binary units (KiB, MiB, base 1024)
- `--gnu`: Use GNU-style short suffixes
- `--format FORMAT`: Printf-style format string (default: "%.1f")
- `--strip-trailing-zeros`: Remove trailing zeros

### Parse Command

Parse human-readable size strings to bytes:

```bash
# Basic usage
python -m mini_humanize parse "1.5 MB"
# Output: 1500000

# Binary units
python -m mini_humanize parse "1.5 MiB"
# Output: 1572864

# Ambiguous units - default to binary
python -m mini_humanize parse "1 KB" --default-binary
# Output: 1024

# GNU short suffix with binary
python -m mini_humanize parse "1K" --default-binary
# Output: 1024

# With thousands separator
python -m mini_humanize parse "1,000 B" --allow-thousands-separator
# Output: 1000

# Rounding modes
python -m mini_humanize parse "1.9 B" --rounding floor
# Output: 1

python -m mini_humanize parse "1.9 B" --rounding ceil
# Output: 2

# Negative values
python -m mini_humanize parse "-100 B" --allow-negative
# Output: -100

# With constraints
python -m mini_humanize parse "100 B" --min-value 50 --max-value 200
# Output: 100
```

**Parse Options:**
- `text`: The size string to parse (required)
- `--default-binary`: Treat ambiguous units as binary (base 1024)
- `--default-gnu`: Treat short suffixes as GNU-style
- `--allow-thousands-separator`: Allow comma/space as thousands separator
- `--rounding {floor,nearest,ceil}`: Rounding mode for fractional bytes (default: nearest)
- `--strict`: Reject unknown units (default: true)
- `--permissive`: Allow unknown units (treat as bytes)
- `--locale LOCALE`: Locale for number parsing (default: en_US)
- `--allow-negative`: Allow negative sizes
- `--min-value N`: Minimum allowed value
- `--max-value N`: Maximum allowed value

## Design Decisions

### Ambiguity Resolution

The library handles several ambiguous size notations:

1. **Short GNU suffixes (K, M, G, T, P)**: By default, these use decimal (base 1000). Use `default_binary=True` to interpret as binary (base 1024).

2. **Legacy units (KB, MB, GB)**: Historically ambiguous - different systems use different bases. By default, we use decimal (base 1000) for consistency with SI prefixes. Use `default_binary=True` for binary interpretation.

3. **Case insensitivity**: All unit parsing is case-insensitive for user convenience.

4. **Whitespace**: Optional whitespace between number and unit for flexibility.

### Error Handling

- **Strict mode (default)**: Unknown units raise `ValueError`
- **Permissive mode**: Unknown units treated as bytes
- **Negative values**: Rejected by default, allowed with `allow_negative=True`
- **Range constraints**: `min_value` and `max_value` provide bounds checking
- **Invalid input**: Clear error messages for malformed input

### Rounding

When parsing results in fractional bytes:
- **floor**: Always round down (e.g., 1.9 → 1)
- **ceil**: Always round up (e.g., 1.1 → 2)
- **nearest**: Round to nearest integer (e.g., 1.5 → 2, Python 3 banker's rounding)

### Backward Compatibility

The `naturalsize` function preserves backward compatibility:
- Default parameters produce the same output as before
- All existing test cases pass without modification
- Bug fixes (e.g., `-0` handling) improve behavior without breaking changes

### Performance

- **O(n) complexity**: `parse_size` parses input in linear time relative to string length
- **No regex overhead**: Efficient parsing without heavy regex operations (one simple match)
- **Integer arithmetic**: Uses integer arithmetic where possible for precision

### Precision

- Handles numbers up to 2^80 (1 YiB) without precision loss
- Uses `int` for final byte values to avoid floating-point errors
- Preserves full precision during multiplication and rounding

## Testing

Run the full test suite:

```bash
pytest tests/ -v --cov=mini_humanize --cov-report=term-missing
```

Or use the provided test script:

```bash
./run_tests
```

The test suite includes:
- **Unit tests**: 150+ tests covering all functions and edge cases
- **Round-trip tests**: Verify naturalsize ↔ parse_size consistency
- **CLI tests**: Subprocess tests for command-line interface
- **Backward compatibility tests**: Ensure default behavior unchanged
- **Large number tests**: Verify precision for values >= 2^70 bytes
- **Error handling tests**: Comprehensive coverage of error conditions

### Test Organization

- `tests/test_naturalsize.py`: Tests for `naturalsize` function
- `tests/test_parse_size.py`: Tests for `parse_size` function
- `tests/test_roundtrip.py`: Round-trip conversion tests
- `tests/test_cli.py`: Command-line interface tests

### Coverage Goals

- Line coverage: > 95%
- Branch coverage: > 90%
- All public API functions fully tested
- Edge cases and error conditions covered

## Requirements

- Python >= 3.10
- No runtime dependencies
- Development dependencies: pytest, pytest-cov

## License

This project is provided as-is for evaluation purposes.
