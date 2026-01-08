# mini_humanize

A production-ready Python library for converting between human-readable file sizes and bytes.

## Features

- **naturalsize**: Convert bytes to human-readable format (e.g., "1.5 GB")
- **parse_size**: Parse human-readable sizes back to bytes (e.g., "1.5 GB" → 1500000000)
- Support for both decimal (KB, MB, GB) and binary (KiB, MiB, GiB) units
- GNU-style short suffixes (K, M, G, T, P)
- Scientific notation support (1.5e3 MB)
- Comprehensive error handling and validation
- Command-line interface
- Full round-trip consistency
- Type-annotated for modern Python

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

Convert numeric byte values into human-readable size strings.

```python
from mini_humanize import naturalsize

# Basic usage (decimal units, base 1000)
naturalsize(1000)           # "1.0 kB"
naturalsize(1500000)        # "1.5 MB"
naturalsize(1000000000)     # "1.0 GB"

# Binary units (base 1024)
naturalsize(1024, binary=True)        # "1.0 KiB"
naturalsize(1048576, binary=True)     # "1.0 MiB"

# GNU format (no space, short suffix)
naturalsize(1000, gnu=True)           # "1.0K"
naturalsize(1024, binary=True, gnu=True)  # "1.0K"

# Custom formatting
naturalsize(1500, format="%.2f")      # "1.50 kB"
naturalsize(1000, strip_trailing_zeros=True)  # "1 kB"

# Negative values supported
naturalsize(-1000)                    # "-1.0 kB"
```

#### Parameters

- **value** (`int | float | str`): The size in bytes. Can be int, float, or numeric string.
- **binary** (`bool`, default `False`): If True, use binary units (KiB, MiB) with base 1024. If False, use decimal units (kB, MB) with base 1000.
- **gnu** (`bool`, default `False`): If True, use GNU-style format with short suffixes (K, M, G) and no space between number and unit.
- **format** (`str`, default `"%.1f"`): Printf-style format string for the numeric part.
- **strip_trailing_zeros** (`bool`, default `False`): If True, remove trailing zeros and decimal point when possible.

#### Returns

`str`: Human-readable size string.

#### Units

Decimal (binary=False):
- B (bytes)
- kB (kilobytes, 1000^1)
- MB (megabytes, 1000^2)
- GB (gigabytes, 1000^3)
- TB (terabytes, 1000^4)
- PB (petabytes, 1000^5)

Binary (binary=True):
- B (bytes)
- KiB (kibibytes, 1024^1)
- MiB (mebibytes, 1024^2)
- GiB (gibibytes, 1024^3)
- TiB (tebibytes, 1024^4)
- PiB (pebibytes, 1024^5)

GNU format uses short suffixes: B, K, M, G, T, P

---

### parse_size

Parse human-readable size strings into bytes.

```python
from mini_humanize import parse_size

# Basic usage
parse_size("1 kB")          # 1000
parse_size("1.5 MB")        # 1500000
parse_size("100 B")         # 100
parse_size("100")           # 100 (implicit bytes)

# Binary units (explicit)
parse_size("1 KiB")         # 1024
parse_size("1.5 MiB")       # 1572864
parse_size("2 GiB")         # 2147483648

# Ambiguous units with default_binary flag
parse_size("1 KB")                      # 1000 (decimal by default)
parse_size("1 KB", default_binary=True) # 1024 (binary mode)

# GNU short suffixes
parse_size("1K")                        # 1000 (decimal by default)
parse_size("1K", default_binary=True)   # 1024 (binary mode)
parse_size("1.5M")                      # 1500000

# Scientific notation
parse_size("1.5e3 MB")      # 1500000000
parse_size("2E-1 KB")       # 200

# Thousands separators
parse_size("1,000 B", allow_thousands_separator=True)  # 1000
parse_size("10,000 KB", allow_thousands_separator=True) # 10000000

# Rounding control for fractional bytes
parse_size("1.5 B", rounding="floor")   # 1
parse_size("1.5 B", rounding="nearest") # 2
parse_size("1.5 B", rounding="ceil")    # 2

# Negative sizes
parse_size("-100 B", allow_negative=True)  # -100

# Value bounds
parse_size("100 B", min_value=50, max_value=200)  # 100
parse_size("10 B", min_value=50)  # ValueError: below minimum
```

#### Parameters

- **text** (`str`): Size string to parse (e.g., "1.5 GB", "2048 KiB", "3e6 MB")
- **default_binary** (`bool`, default `False`): Controls interpretation of ambiguous units (KB, MB, GB, K, M, G). If True, treat as binary (base 1024). If False, treat as decimal (base 1000).
- **default_gnu** (`bool`, default `False`): Reserved for future GNU-specific parsing behavior.
- **allow_thousands_separator** (`bool`, default `False`): If True, allow commas (or locale-specific separators) in numbers.
- **rounding** (`Literal["floor", "nearest", "ceil"]`, default `"nearest"`): How to handle fractional bytes.
  - "floor": Round down
  - "nearest": Round to nearest integer
  - "ceil": Round up
- **strict** (`bool`, default `True`): If True, reject malformed input with ValueError. If False, attempt best-effort parsing.
- **locale** (`str`, default `"en_US"`): Locale for decimal point parsing (e.g., "de_DE" uses comma as decimal separator).
- **allow_negative** (`bool`, default `False`): If True, allow negative size values.
- **min_value** (`int | None`, default `None`): If set, reject values below this threshold.
- **max_value** (`int | None`, default `None`): If set, reject values above this threshold.

#### Returns

`int`: Size in bytes.

#### Raises

- **TypeError**: If input is not a string.
- **ValueError**: If input is invalid, malformed, or violates constraints (min/max values, negative policy).

#### Supported Formats

**Explicit Binary Units** (always base 1024):
- KiB, MiB, GiB, TiB, PiB, EiB, ZiB, YiB

**Explicit Decimal Units** (always base 1000):
- kB, MB, GB, TB, PB, EB, ZB, YB

**Ambiguous Legacy Units** (controlled by `default_binary`):
- KB, MB, GB, TB, PB, EB, ZB, YB
- Interpreted as decimal (base 1000) by default
- Interpreted as binary (base 1024) when `default_binary=True`

**GNU Single-Letter Units** (controlled by `default_binary`):
- K, M, G, T, P, E, Z, Y
- Interpreted as decimal (base 1000) by default
- Interpreted as binary (base 1024) when `default_binary=True`

**Number Formats**:
- Integers: `1000`, `2048`
- Decimals: `1.5`, `0.5`, `.5`
- Scientific notation: `1e3`, `1.5e6`, `2E-1`
- Thousands separators: `1,000`, `10,000` (when `allow_thousands_separator=True`)

**Unit Spacing**:
- With space: `"1.5 GB"`, `"1 KiB"`
- Without space: `"1.5GB"`, `"1KiB"`
- Case-insensitive: `"1 kb"`, `"1 KB"`, `"1 Kb"`

## Command-Line Interface

### format

Convert bytes to human-readable format.

```bash
# Basic usage
python -m mini_humanize format 1000
# Output: 1.0 kB

# Binary units
python -m mini_humanize format 1024 --binary
# Output: 1.0 KiB

# GNU format
python -m mini_humanize format 1000 --gnu
# Output: 1.0K

# Combined options
python -m mini_humanize format 1024 --binary --gnu
# Output: 1.0K

# Custom format
python -m mini_humanize format 1500 --format "%.2f"
# Output: 1.50 kB

# Strip trailing zeros
python -m mini_humanize format 1000 --strip-trailing-zeros
# Output: 1 kB
```

#### Options

- `value`: Numeric value in bytes (required)
- `--binary`: Use binary units (KiB, MiB, etc.)
- `--gnu`: Use GNU format (short suffixes, no space)
- `--format FORMAT`: Custom printf-style format (default: `%.1f`)
- `--strip-trailing-zeros`: Remove trailing zeros from output

### parse

Parse human-readable size to bytes.

```bash
# Basic usage
python -m mini_humanize parse "1 kB"
# Output: 1000

# Binary units
python -m mini_humanize parse "1 KiB"
# Output: 1024

# Ambiguous units with default-binary
python -m mini_humanize parse "1 KB" --default-binary
# Output: 1024

# GNU units
python -m mini_humanize parse "1K"
# Output: 1000

python -m mini_humanize parse "1K" --default-binary
# Output: 1024

# Rounding modes
python -m mini_humanize parse "1.9 B" --rounding floor
# Output: 1

python -m mini_humanize parse "1.1 B" --rounding ceil
# Output: 2

# Thousands separator
python -m mini_humanize parse "1,000 B" --allow-thousands-separator
# Output: 1000

# Negative values
python -m mini_humanize parse "-100 B" --allow-negative
# Output: -100

# Value bounds
python -m mini_humanize parse "100 B" --min-value 50 --max-value 200
# Output: 100
```

#### Options

- `text`: Size string to parse (required)
- `--default-binary`: Treat ambiguous units (KB, K) as binary (base 1024)
- `--default-gnu`: Reserved for GNU-specific behavior
- `--allow-thousands-separator`: Allow commas in numbers
- `--rounding {floor,nearest,ceil}`: Rounding mode for fractional bytes (default: nearest)
- `--strict`: Reject malformed input (default: True)
- `--permissive`: Allow malformed input (opposite of --strict)
- `--locale LOCALE`: Locale for decimal parsing (default: en_US)
- `--allow-negative`: Allow negative size values
- `--min-value N`: Reject values below N
- `--max-value N`: Reject values above N

## Design Decisions

### Ambiguous Unit Resolution

The library distinguishes between explicit and ambiguous units:

1. **Explicit binary units** (KiB, MiB, GiB, etc.) always use base 1024
2. **Explicit decimal units** (kB, MB, GB, etc.) always use base 1000
3. **Ambiguous units** (KB, MB, GB and K, M, G) are controlled by the `default_binary` parameter:
   - `default_binary=False` (default): base 1000 (decimal)
   - `default_binary=True`: base 1024 (binary)

This design provides clarity while maintaining flexibility for different conventions.

### Rounding Behavior

When parsing results in fractional bytes, the `rounding` parameter controls behavior:

- **"floor"**: Always round down (conservative for storage allocation)
- **"nearest"** (default): Round to nearest integer (balanced approach)
- **"ceil"**: Always round up (conservative for capacity requirements)

### Error Handling

By default, `strict=True` mode rejects invalid input with descriptive error messages. For legacy or malformed input, use `strict=False` for best-effort parsing.

### Backward Compatibility

The `naturalsize` function maintains strict backward compatibility:
- Default parameters produce unchanged output
- Existing code continues to work without modification
- New features are opt-in via explicit parameters

### Performance

The `parse_size` implementation maintains O(n) complexity where n is input string length:
- Single-pass parsing for number and unit separation
- No regular expressions (constant-time unit lookups via dictionaries)
- Efficient for both small and large inputs

### Large Number Support

Both functions support values up to and beyond 2^70 bytes without precision loss:
- Uses Python's arbitrary-precision integers
- Supports units up to YiB (yobibytes, 2^80) and YB (yottabytes, 10^24)
- Maintains precision through conversions

## Testing

### Run Full Test Suite

Execute all tests with coverage:

```bash
./run_tests
```

Or using pytest directly:

```bash
python -m pytest tests/ -v --cov=src/mini_humanize --cov-report=term-missing
```

### Test Structure

The test suite includes:

- **test_naturalsize.py**: Tests for naturalsize function
  - Basic formatting (decimal, binary, GNU)
  - Custom format strings and trailing zeros
  - Edge cases (zero, negative, large values)
  - Backward compatibility verification
  
- **test_parse_size.py**: Tests for parse_size function
  - Binary, decimal, and GNU units
  - Scientific notation
  - Thousands separators
  - Rounding modes
  - Negative handling
  - Min/max bounds
  - Error conditions
  - Large number support (>= 2^70)
  
- **test_roundtrip.py**: Round-trip consistency tests
  - Decimal format round trips
  - Binary format round trips
  - GNU format round trips
  - Edge cases and large numbers
  
- **test_cli.py**: Command-line interface tests
  - format command with all options
  - parse command with all options
  - Round-trip via CLI
  - Error handling
  - Help and usage

### Coverage Goals

The test suite aims for:
- 100% line coverage of core functions
- Comprehensive edge case coverage
- Real-world usage patterns
- Error condition validation

## Examples

### Round-Trip Conversions

```python
from mini_humanize import naturalsize, parse_size

# Decimal round trip
size_bytes = 1500000
formatted = naturalsize(size_bytes)        # "1.5 MB"
parsed = parse_size(formatted)             # 1500000
assert parsed == size_bytes

# Binary round trip
size_bytes = 1572864
formatted = naturalsize(size_bytes, binary=True)  # "1.5 MiB"
parsed = parse_size(formatted)                    # 1572864
assert parsed == size_bytes

# GNU round trip (requires default_binary flag)
size_bytes = 1048576
formatted = naturalsize(size_bytes, binary=True, gnu=True)  # "1.0M"
parsed = parse_size(formatted, default_binary=True)        # 1048576
assert parsed == size_bytes
```

### Validation and Bounds

```python
from mini_humanize import parse_size

# Validate file size is within acceptable range
def validate_upload_size(size_str: str) -> int:
    """Validate uploaded file size is between 1KB and 100MB."""
    try:
        size_bytes = parse_size(
            size_str,
            min_value=1000,      # 1 KB minimum
            max_value=100000000, # 100 MB maximum
            allow_negative=False
        )
        return size_bytes
    except ValueError as e:
        print(f"Invalid size: {e}")
        raise

# Valid
validate_upload_size("5 MB")      # 5000000

# Invalid - too small
validate_upload_size("500 B")     # ValueError: below minimum

# Invalid - too large
validate_upload_size("500 MB")    # ValueError: exceeds maximum
```

### Parsing User Input

```python
from mini_humanize import parse_size

def parse_user_quota(input_str: str) -> int:
    """Parse user quota with flexible input handling."""
    return parse_size(
        input_str,
        default_binary=True,  # Treat KB/MB as binary
        allow_thousands_separator=True,
        strict=False,  # Tolerate minor formatting issues
        min_value=0
    )

# Flexible parsing
parse_user_quota("10 GB")          # 10737418240 (binary interpretation)
parse_user_quota("1,024 MB")       # 1073741824 (with separator)
parse_user_quota("2048M")          # 2147483648 (GNU format)
```

## Dependencies

- **Runtime**: Python 3.10+, no external dependencies
- **Development**: pytest >= 8.0.0, pytest-cov >= 5.0.0

## License

This is an evaluation project for agent-based development.

## Contributing

This library is designed for production use with comprehensive testing and documentation. Contributions should maintain:
- Type annotations for all public APIs
- Comprehensive test coverage
- Clear documentation of design decisions
- Backward compatibility for existing functionality
