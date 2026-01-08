from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from mini_humanize.sizecodec import naturalsize, parse_size


def test_naturalsize_defaults_preserved() -> None:
    assert naturalsize(0) == "0.0 B"
    assert naturalsize(0, strip_trailing_zeros=True) == "0 B"
    assert naturalsize(1024, binary=True) == "1.0 KiB"
    assert naturalsize(1500) == "1.5 kB"
    assert naturalsize(1500, gnu=True) == "1.5K"


def test_parse_simple_numbers() -> None:
    assert parse_size("42") == 42
    assert parse_size("  42  ") == 42


def test_parse_suffixes_and_bases() -> None:
    assert parse_size("1KiB") == 1024
    assert parse_size("1 KiB") == 1024
    assert parse_size("1kB") == 1000
    assert parse_size("1KB") == 1000
    assert parse_size("1K", default_gnu=True) == 1000
    assert parse_size("1K", default_gnu=True, default_binary=True) == 1024


def test_scientific_and_thousands() -> None:
    assert parse_size("1.5e3 B") == 1500
    assert parse_size("1,234.56 kB", allow_thousands_separator=True) == 1234560
    assert (
        parse_size("1.234,56 kB", locale="de_DE", allow_thousands_separator=True) == 1234560
    )


def test_rounding_modes() -> None:
    assert parse_size("1.5 B", rounding="nearest") == 2
    assert parse_size("1.5 B", rounding="floor") == 1
    assert parse_size("1.5 B", rounding="ceil") == 2


def test_negative_and_limits() -> None:
    try:
        parse_size("-1 KB")
        raise AssertionError("expected ValueError for negative without allow_negative")
    except ValueError:
        pass

    assert parse_size("-1 KB", allow_negative=True) < 0

    try:
        parse_size("1K", min_value=2000)
        raise AssertionError("expected ValueError for value below min_value")
    except ValueError:
        pass

    try:
        parse_size("3K", max_value=2000)
        raise AssertionError("expected ValueError for value above max_value")
    except ValueError:
        pass


def test_large_numbers_and_precision() -> None:
    big = 2 ** 70
    assert parse_size(str(big)) == big
    # also test a large multiplier
    assert parse_size("1PiB") == 1024 ** 5


def test_round_trip_consistency() -> None:
    # Round-trip for binary formatting (use matching parse flags)
    values_bin = [0, 1, 512, 1024, 1536, 2 ** 70]
    for v in values_bin:
        s = naturalsize(v, binary=True)
        assert parse_size(s, default_binary=True) == v

    # Round-trip for decimal formatting on values that are exact when scaled
    values_dec = [0, 1, 1500, 10 ** 6]
    for v in values_dec:
        s = naturalsize(v, binary=False)
        assert parse_size(s, default_binary=False) == v


def test_cli_module_format_and_parse() -> None:
    # format
    p = subprocess.run(
        [sys.executable, "-m", "mini_humanize", "format", "1536", "--binary", "--strip-trailing-zeros"],
        capture_output=True,
        check=True,
        text=True,
    )
    assert p.stdout == "1.5 KiB\n"

    # parse
    p2 = subprocess.run(
        [sys.executable, "-m", "mini_humanize", "parse", "1.5 KiB"],
        capture_output=True,
        check=True,
        text=True,
    )
    assert p2.stdout.strip() == "1536"


def test_permissive_mode_handles_unknown_suffix() -> None:
    # strict mode rejects single-letter GNU suffix
    try:
        parse_size("1K")
        raise AssertionError("expected ValueError for ambiguous 'K' when strict")
    except ValueError:
        pass

    # permissive (strict=False) accepts a best-effort interpretation
    assert parse_size("1X", strict=False) == 1


def test_invalid_number_formats() -> None:
    try:
        parse_size("abc")
        raise AssertionError("expected ValueError for non-numeric input")
    except ValueError:
        pass

    try:
        parse_size("1,234.56")
        raise AssertionError("expected ValueError when thousands separator present but not allowed")
    except ValueError:
        pass


def test_run_tests_script_exists() -> None:
    root = Path(__file__).resolve().parents[1]
    script = root / "run_tests"
    assert script.exists()
    assert script.read_text().strip().startswith("#!")
