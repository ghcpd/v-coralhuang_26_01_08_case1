import pytest
from mini_humanize import naturalsize


class TestNaturalSize:
    def test_basic_decimal(self):
        assert naturalsize(0) == "0.0 B"
        assert naturalsize(1) == "1.0 B"
        assert naturalsize(1000) == "1.0 kB"
        assert naturalsize(1000000) == "1.0 MB"

    def test_basic_binary(self):
        assert naturalsize(0, binary=True) == "0.0 B"
        assert naturalsize(1024, binary=True) == "1.0 KiB"
        assert naturalsize(1024**2, binary=True) == "1.0 MiB"

    def test_gnu_format(self):
        assert naturalsize(1000, gnu=True) == "1.0K"
        assert naturalsize(1024, binary=True, gnu=True) == "1.0K"

    def test_strip_trailing_zeros(self):
        assert naturalsize(0, strip_trailing_zeros=True) == "0 B"
        assert naturalsize(1000, strip_trailing_zeros=True) == "1 kB"
        assert naturalsize(1000, gnu=True, strip_trailing_zeros=True) == "1K"

    def test_negative_zero_bug_fix(self):
        # Test the bug fix for negative zero
        assert naturalsize(-0.0, strip_trailing_zeros=True) == "0 B"
        assert naturalsize(-0, strip_trailing_zeros=True) == "0 B"

    def test_string_input(self):
        assert naturalsize("1000") == "1.0 kB"
        assert naturalsize("-1000") == "-1.0 kB"

    def test_custom_format(self):
        assert naturalsize(1000, format="%.0f") == "1 kB"
        assert naturalsize(1500, format="%.2f") == "1.50 kB"

    def test_large_numbers(self):
        large = 2**70
        assert naturalsize(large) == "1180591.6 PB"  # Approximate

    def test_backward_compatibility(self):
        # Ensure default behavior unchanged
        test_cases = [
            (0, "0.0 B"),
            (1, "1.0 B"),
            (1024, "1.0 KiB" if False else "1.0 kB"),
            (1024, {"binary": True}, "1.0 KiB"),
            (1000, {"gnu": True}, "1.0K"),
            (1000, {"strip_trailing_zeros": True}, "1 kB"),
        ]
        for args in test_cases:
            if len(args) == 2:
                value, expected = args
                kwargs = {}
            else:
                value, kwargs, expected = args
            assert naturalsize(value, **kwargs) == expected