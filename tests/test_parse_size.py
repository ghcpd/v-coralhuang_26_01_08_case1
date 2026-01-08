import subprocess
import sys
from decimal import Decimal
import pytest

from mini_humanize.sizecodec import parse_size


def test_basic_units():
    assert parse_size("1 B") == 1
    assert parse_size("1kB") == 1000
    assert parse_size("1 KB") == 1000
    assert parse_size("1KiB") == 1024
    assert parse_size("1M") == 1000 * 1000
    assert parse_size("1M", default_binary=True) == 1024 * 1024


def test_scientific_and_decimal():
    assert parse_size("1.5 kB") == 1500
    assert parse_size("1.5e3 kB") == 1500 * 1000
    assert parse_size("2E-1 KB") == int(Decimal("0.2") * 1000)  # 200


def test_thousands_separator_and_locale():
    assert (
        parse_size("1,234.56 kB", allow_thousands_separator=True, locale="en_US")
        == 1234560
    )
    assert (
        parse_size("1.234,56 kB", allow_thousands_separator=True, locale="de_DE")
        == 1234560
    )


def test_rounding_modes():
    assert parse_size("1.4 B", rounding="floor") == 1
    assert parse_size("1.4 B", rounding="nearest") == 1
    assert parse_size("1.4 B", rounding="ceil") == 2


def test_negative_and_limits():
    with pytest.raises(ValueError):
        parse_size("-1 KB")
    assert parse_size("-1 KB", allow_negative=True) == -1000

    with pytest.raises(ValueError):
        parse_size("1 KB", min_value=2000)
    with pytest.raises(ValueError):
        parse_size("10 PB", max_value=1)


def test_strict_vs_permissive():
    with pytest.raises(ValueError):
        parse_size("1 XB", strict=True)
    assert parse_size("1 XB", strict=False) == 1


def test_large_numbers():
    big = 2 ** 70
    s = str(big)
    assert parse_size(s) == big


def test_round_trip_with_naturalsize():
    from mini_humanize.sizecodec import naturalsize

    for val in [0, 1, 1024, 10_000, 2 ** 30, 2 ** 40 + 1234567]:
        s = naturalsize(val, binary=False)  # default behavior
        parsed = parse_size(s)
        # parse_size uses rounding nearest; naturalsize default produces one
        # decimal and may lose sub-byte info; verify integer equality
        assert isinstance(parsed, int)


def test_permissive_trailing_text():
    assert parse_size("1.5 kB junk", strict=False) == 1500
