"""
Round-trip tests: verify that naturalsize and parse_size are inverses
"""
import pytest
from mini_humanize import naturalsize, parse_size


class TestRoundTripDecimal:
    """Test round-trip conversion with decimal units"""
    
    def test_basic_sizes(self):
        sizes = [0, 1, 100, 1000, 1500, 10000, 100000, 1000000]
        for size in sizes:
            formatted = naturalsize(size)
            parsed = parse_size(formatted)
            # Allow small rounding errors
            assert abs(parsed - size) <= 1, f"Failed for {size}: {formatted} -> {parsed}"
    
    def test_large_sizes(self):
        sizes = [
            1000000000,       # 1 GB
            5000000000,       # 5 GB
            1000000000000,    # 1 TB
            1000000000000000, # 1 PB
        ]
        for size in sizes:
            formatted = naturalsize(size)
            parsed = parse_size(formatted)
            # For large numbers, allow proportional error
            error = abs(parsed - size) / size
            assert error < 0.01, f"Failed for {size}: {formatted} -> {parsed}"


class TestRoundTripBinary:
    """Test round-trip conversion with binary units"""
    
    def test_basic_sizes(self):
        sizes = [0, 1, 1024, 2048, 1536, 10240, 1048576]
        for size in sizes:
            formatted = naturalsize(size, binary=True)
            parsed = parse_size(formatted)
            assert abs(parsed - size) <= 1, f"Failed for {size}: {formatted} -> {parsed}"
    
    def test_powers_of_1024(self):
        sizes = [
            1024**1,  # 1 KiB
            1024**2,  # 1 MiB
            1024**3,  # 1 GiB
            1024**4,  # 1 TiB
        ]
        for size in sizes:
            formatted = naturalsize(size, binary=True)
            parsed = parse_size(formatted)
            assert parsed == size, f"Failed for {size}: {formatted} -> {parsed}"


class TestRoundTripGNU:
    """Test round-trip conversion with GNU-style formatting"""
    
    def test_gnu_decimal(self):
        sizes = [1000, 1000000, 1000000000]
        for size in sizes:
            formatted = naturalsize(size, gnu=True)
            parsed = parse_size(formatted)
            assert abs(parsed - size) <= 1
    
    def test_gnu_binary(self):
        sizes = [1024, 1048576, 1073741824]
        for size in sizes:
            formatted = naturalsize(size, binary=True, gnu=True)
            # Need to tell parser this is binary
            parsed = parse_size(formatted, default_binary=True)
            assert abs(parsed - size) <= 1


class TestRoundTripWithOptions:
    """Test round-trip with various formatting options"""
    
    def test_with_strip_trailing_zeros(self):
        sizes = [1000, 2500, 10000]
        for size in sizes:
            formatted = naturalsize(size, strip_trailing_zeros=True)
            parsed = parse_size(formatted)
            assert abs(parsed - size) <= 1
    
    def test_different_formats(self):
        sizes = [1234, 5678]
        for size in sizes:
            # %.2f format
            formatted = naturalsize(size, format="%.2f")
            parsed = parse_size(formatted)
            # Allow rounding error from format
            assert abs(parsed - size) / size < 0.1


class TestRoundTripEdgeCases:
    """Test round-trip for edge cases"""
    
    def test_zero(self):
        formatted = naturalsize(0)
        parsed = parse_size(formatted)
        assert parsed == 0
    
    def test_very_small(self):
        formatted = naturalsize(1)
        parsed = parse_size(formatted)
        assert parsed == 1
    
    def test_very_large(self):
        # Test with 2^70
        size = 2**70
        formatted = naturalsize(size, binary=True)
        parsed = parse_size(formatted)
        # Allow small relative error for very large numbers
        error = abs(parsed - size) / size
        assert error < 0.01


class TestRoundTripNegative:
    """Test round-trip with negative values"""
    
    def test_negative_values(self):
        sizes = [-1000, -1500, -1000000]
        for size in sizes:
            formatted = naturalsize(size)
            parsed = parse_size(formatted, allow_negative=True)
            assert abs(parsed - size) <= 1


class TestRoundTripConsistency:
    """Test that parse_size can handle all naturalsize outputs"""
    
    def test_all_unit_levels(self):
        # Test at each unit boundary
        bases_decimal = [1, 1000, 1000**2, 1000**3, 1000**4, 1000**5]
        for base in bases_decimal:
            formatted = naturalsize(base)
            parsed = parse_size(formatted)
            error = abs(parsed - base) / max(base, 1)
            assert error < 0.01
    
    def test_all_unit_levels_binary(self):
        bases_binary = [1, 1024, 1024**2, 1024**3, 1024**4, 1024**5]
        for base in bases_binary:
            formatted = naturalsize(base, binary=True)
            parsed = parse_size(formatted)
            error = abs(parsed - base) / max(base, 1)
            assert error < 0.01
