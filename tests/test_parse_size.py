import pytest
from mini_humanize import parse_size


class TestParseSize:
    def test_basic_bytes(self):
        assert parse_size("0") == 0
        assert parse_size("1") == 1
        assert parse_size("1 B") == 1
        assert parse_size("1b") == 1

    def test_decimal_units(self):
        assert parse_size("1 kB") == 1000
        assert parse_size("1 MB") == 1000**2
        assert parse_size("1 GB") == 1000**3
        assert parse_size("1 KB") == 1000  # IEC legacy

    def test_binary_units(self):
        assert parse_size("1 KiB") == 1024
        assert parse_size("1 MiB") == 1024**2
        assert parse_size("1 GiB") == 1024**3

    def test_gnu_units(self):
        assert parse_size("1K") == 1000
        assert parse_size("1M") == 1000**2
        assert parse_size("1K", default_binary=True) == 1024
        assert parse_size("1M", default_binary=True) == 1024**2

    def test_scientific_notation(self):
        assert parse_size("1.5e3 MB") == int(1.5e3 * 1000**2)
        assert parse_size("2E-1 KB") == int(0.2 * 1000)

    def test_thousands_separator(self):
        assert parse_size("1,000 MB", allow_thousands_separator=True) == 1000 * 1000**2
        with pytest.raises(ValueError):
            parse_size("1,000 MB")  # Not allowed by default

    def test_negative(self):
        with pytest.raises(ValueError):
            parse_size("-1 MB")  # Not allowed by default
        assert parse_size("-1 MB", allow_negative=True) == -1000**2

    def test_rounding(self):
        # 1.3 KiB = 1.3 * 1024 ≈ 1331.2
        assert parse_size("1.3 KiB", rounding="floor") == 1331
        assert parse_size("1.3 KiB", rounding="ceil") == 1332
        assert parse_size("1.3 KiB", rounding="nearest") == 1331  # 0.2 < 0.5

        # 1.7 KiB ≈ 1740.8
        assert parse_size("1.7 KiB", rounding="nearest") == 1741

    def test_constraints(self):
        with pytest.raises(ValueError):
            parse_size("1 MB", min_value=2000000)
        with pytest.raises(ValueError):
            parse_size("1 MB", max_value=500000)
        assert parse_size("1 MB", min_value=1000000, max_value=1000000) == 1000000

    def test_invalid_input(self):
        invalid_cases = [
            "",
            "abc",
            "1 XB",
            "1.2.3 MB",
            "1 MB extra",
        ]
        for case in invalid_cases:
            with pytest.raises(ValueError):
                parse_size(case)

    def test_case_insensitive(self):
        assert parse_size("1 mb") == 1000**2
        assert parse_size("1 MIB") == 1024**2

    def test_large_numbers(self):
        large = 2**70
        assert parse_size(f"{large} B") == large

    def test_fractional(self):
        assert parse_size("0.5 MB") == 500000