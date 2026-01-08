# mini_humanize

mini_humanize is a tiny, dependency-free library for formatting and parsing human-readable file sizes.

## API

### naturalsize(value: int|float|str, *, binary: bool = False, gnu: bool = False, format: str = "%.1f", strip_trailing_zeros: bool = False) -> str

- Purpose: Format a numeric byte quantity into a human-friendly string.
- Parameters:
  - value: numeric value (int, float, or numeric string)
  - binary: if True, use binary base (1024) and `KiB`/`MiB` suffixes; otherwise decimal (1000)
  - gnu: if True, use GNU style suffixes without a space and one-letter suffixes (K/M/...) when possible
  - format: a printf-style format for the numeric part (default `"%.1f"`)
  - strip_trailing_zeros: when True remove trailing zeros and the decimal point if unnecessary
- Notes:
  - Backward-compatible defaults are preserved (default outputs unchanged in normal cases).
  - `naturalsize(0, strip_trailing_zeros=True)` returns `"0 B"` (no negative zero).

Example:

```
from mini_humanize import naturalsize

naturalsize(1536, binary=True)  # -> '1.5 KiB'
```

### parse_size(text: str, *, default_binary: bool = False, default_gnu: bool = False, allow_thousands_separator: bool = False, rounding: Literal['floor','nearest','ceil'] = 'nearest', strict: bool = True, locale: str = 'en_US', allow_negative: bool = False, min_value: int|None = None, max_value: int|None = None) -> int

- Purpose: Parse a human-friendly size string into an integer number of bytes.
- Behavior highlights:
  - Accepts integer, decimal and scientific notation numbers (e.g. `1`, `1.5`, `1e3`).
  - Recognizes units (case-insensitive):
    - IEC binary: `KiB`, `MiB`, `GiB`, ... => base 1024
    - SI decimal: `kB`, `MB`, `GB`, ... => base 1000
    - Short GNU: `K`, `M`, `G`, ... => base determined by `default_binary` (False => 1000, True => 1024)
    - Legacy `KB/MB/...` are treated as decimal (1000) by default; set `default_binary=True` to treat them as binary.
    - `B` or no suffix means bytes.
  - Thousands separators: set `allow_thousands_separator=True` to accept separators for the provided `locale` (basic support: `en_*` uses `,` for thousands and `.` for decimal; `de_*` uses `.` and `,`).
  - Rounding: fractional bytes are converted using the `rounding` parameter:
    - `floor` truncates toward -∞
    - `nearest` rounds half up
    - `ceil` rounds toward +∞
  - `strict=True` (default): unknown units or malformed input raise `ValueError`.
    `strict=False` (permissive) will attempt to ignore trailing unknown text.
  - `allow_negative` controls negative values.
  - `min_value` and `max_value` are inclusive bounds applied after rounding.

Examples:

```
from mini_humanize import parse_size

parse_size("1.5 KiB", default_binary=True)  # -> 1536
parse_size("1,234.56 kB", allow_thousands_separator=True, locale="en_US")  # -> 1234560
```

## CLI

Install the package and run as a module:

- Format: python -m mini_humanize format <value> [--binary] [--gnu] [--format FORMAT] [--strip-trailing-zeros]
- Parse:  python -m mini_humanize parse <text> [--default-binary] [--default-gnu] [--allow-thousands-separator] [--rounding floor|nearest|ceil] [--strict] [--permissive] [--locale LOCALE] [--allow-negative] [--min-value N] [--max-value N]

Examples:

```
python -m mini_humanize format 1536 --binary
# prints: 1.5 KiB

python -m mini_humanize parse "1.5 KiB" --default-binary
# prints: 1536
```

## Ambiguities and Design Decisions

- Short suffixes like `K`, `M` are ambiguous between 1000 and 1024. We use `default_binary` to resolve ambiguity; if `default_binary=False` short suffixes are decimal (1000).
- Legacy uppercase `KB/MB/GB` are treated as decimal (1000) by default to follow SI.
- `strict=True` will raise `ValueError` on unknown units or malformed numeric text. In permissive mode the parser will try to ignore unrecognized trailing text.
- Locale handling is intentionally minimal (supports `en_*` and `de_*` styles).

## Rounding rules

- Rounding is applied after multiplying the parsed numeric value by the unit multiplier.
- `nearest` uses half-up rounding to be consistent and predictable.

## Testing

Run the full test suite with exactly this command:

```
python run_tests
```

(That single command will install test dependencies if missing and run pytest with coverage.)
