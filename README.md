mini_humanize
===============

A tiny, dependency-free helper for formatting and parsing human-readable byte sizes.

Features
- naturalsize: format bytes into human-friendly strings (backwards-compatible defaults)
- parse_size: robust, linear-time parser for real-world size strings (scientific notation, thousands separators, multiple unit conventions)
- Small CLI: `python -m mini_humanize` for quick format/parse from the shell

Quick test (one command)

Run the full test suite (installs test dependencies if needed):

    python run_tests


API
---

naturalsize(value, *, binary=False, gnu=False, format="%.1f", strip_trailing_zeros=False) -> str
- Purpose: Convert a numeric byte value to a human-readable string.
- Parameters:
  - value: int, float, or numeric string
  - binary: when True use 1024-based units (KiB, MiB, ...); otherwise 1000-based (kB, MB, ...)
  - gnu: when True use compact GNU-style suffixes (no space and single-letter suffixes like "K"), otherwise use "kB"/"KiB" forms
  - format: printf-style format applied to the scaled number (default "%.1f")
  - strip_trailing_zeros: drop unneeded ".0" from the formatted number

Notes:
- Default behavior is preserved from earlier versions: common calls like `naturalsize(1500)` still return `"1.5 kB"`.
- The function avoids printing "-0"; zero is always rendered as a non-negative zero.


parse_size(text, *,
           default_binary=False,
           default_gnu=False,
           allow_thousands_separator=False,
           rounding="nearest",
           strict=True,
           locale="en_US",
           allow_negative=False,
           min_value=None,
           max_value=None) -> int
- Purpose: Parse a human-friendly size string and return an integer number of bytes.
- Returns: integer byte count (exact, no floating-point truncation)

Supported input forms
- Plain integers: "42"
- Decimal numbers and scientific notation: "1.5e3", "2E10"
- Thousands grouping (locale-aware) when `allow_thousands_separator=True`, e.g. "1,234.56 kB" (en_US) or "1.234,56 kB" (de_DE)
- Units (case-insensitive):
  - Binary/IEC: "KiB", "MiB", "GiB", ... (explicitly 1024-based)
  - Legacy/decimal: "kB", "MB", "GB", ... (1000-based by default)
  - GNU single-letter: "K", "M", "G", ... (allowed when `default_gnu=True` or when `strict=False`)
  - Bare "B" or no suffix means bytes

Ambiguities & design decisions
- Suffixes that explicitly include "iB" are always binary (1024).
- Suffixes that include a trailing "B" ("KB", "kB", "MB") are treated as decimal (1000) unless `default_binary=True` is set.
- Single-letter GNU suffixes ("K", "M") are accepted only when `default_gnu=True` or when `strict=False`. Their base (1000 vs 1024) is controlled by `default_binary`.
- If `strict=True` (the default) unknown or unsupported suffixes raise ValueError. If `strict=False` the parser attempts a best-effort interpretation (e.g., unknown suffixes become bytes, or the leading letter is used as a hint).

Rounding & negative values
- `rounding` controls how fractional bytes are converted to integers:
  - "floor": round toward -infinity
  - "nearest": round halves away from zero (Decimal's ROUND_HALF_UP)
  - "ceil": round toward +infinity
- By default negative sizes are rejected; set `allow_negative=True` to accept negative results.

Limits & errors
- `min_value` and `max_value` (integers) are enforced after rounding; violations raise ValueError with a clear message.
- The parser validates thousands-grouping when `allow_thousands_separator=True` (groups of 3 digits).
- The function raises ValueError for malformed numbers or unsupported units (under `strict=True`).

Precision & performance
- The parser uses Python's Decimal with an increased precision so inputs up to at least 2**70 are handled exactly.
- Parsing complexity is O(n) in the length of the input string.

CLI
---

Usage examples:

- Format 1536 bytes in binary form:

    python -m mini_humanize format 1536 --binary --strip-trailing-zeros

  Output: `1.5 KiB`

- Parse a human size back to bytes:

    python -m mini_humanize parse "1.5 KiB"

  Output: `1536`

Testing
-------

- The repository includes a pytest test suite under `tests/` covering formatting, parsing, edge cases, round-trip consistency, and the module CLI.
- Run the full test suite with the single command:

    python run_tests


License
-------
This tiny library is provided without warranty. Use as you see fit.
