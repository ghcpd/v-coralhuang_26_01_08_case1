import pytest
from mini_humanize import naturalsize


class TestBackwardCompatibility:
    # Test that default behavior of naturalsize is unchanged
    def test_default_behavior(self):
        # These should match the original implementation
        assert naturalsize(0) == "0.0 B"
        assert naturalsize(1) == "1.0 B"
        assert naturalsize(1000) == "1.0 kB"
        assert naturalsize(1024) == "1.0 kB"  # Not binary by default
        assert naturalsize(1000000) == "1.0 MB"
        assert naturalsize(-1000) == "-1.0 kB"
        assert naturalsize("1000") == "1.0 kB"

    def test_binary_flag(self):
        assert naturalsize(1024, binary=True) == "1.0 KiB"

    def test_gnu_flag(self):
        assert naturalsize(1000, gnu=True) == "1.0K"

    def test_strip_zeros(self):
        assert naturalsize(1000, strip_trailing_zeros=True) == "1 kB"

    def test_custom_format(self):
        assert naturalsize(1000, format="%.0f") == "1 kB"