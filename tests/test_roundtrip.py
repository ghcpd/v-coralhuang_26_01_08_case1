"""Round-trip consistency tests for naturalsize <-> parse_size."""
import pytest
from mini_humanize import naturalsize, parse_size


class TestRoundTripDecimal:
    """Test round-trip consistency with decimal units."""
    
    def test_simple_decimal_roundtrip(self):
        """Test basic decimal round trips."""
        # Exact values that round-trip cleanly
        values = [1000, 1000000, 1000000000, 1000000000000]
        
        for value in values:
            formatted = naturalsize(value)
            parsed = parse_size(formatted)
            assert parsed == value, f"Failed for {value}: {formatted} -> {parsed}"
    
    def test_fractional_decimal_roundtrip(self):
        """Test fractional decimal values."""
        # These should round-trip with some tolerance for formatting
        values = [1500, 1500000, 2300000]
        
        for value in values:
            formatted = naturalsize(value)
            parsed = parse_size(formatted)
            # Allow small rounding error due to .1f format
            assert abs(parsed - value) / value < 0.01, f"Failed for {value}: {formatted} -> {parsed}"
    
    def test_large_decimal_roundtrip(self):
        """Test large decimal values."""
        value = 1234567890123456
        formatted = naturalsize(value)
        parsed = parse_size(formatted)
        # Due to %.1f formatting, we expect some rounding; allow up to 3% relative error for very large values
        assert abs(parsed - value) / value < 0.03


class TestRoundTripBinary:
    """Test round-trip consistency with binary units."""
    
    def test_simple_binary_roundtrip(self):
        """Test basic binary round trips."""
        values = [1024, 1048576, 1073741824, 1099511627776]
        
        for value in values:
            formatted = naturalsize(value, binary=True)
            parsed = parse_size(formatted)
            assert parsed == value, f"Failed for {value}: {formatted} -> {parsed}"
    
    def test_fractional_binary_roundtrip(self):
        """Test fractional binary values."""
        values = [1536, 2048, 1572864]  # 1.5 KiB, 2 KiB, 1.5 MiB
        
        for value in values:
            formatted = naturalsize(value, binary=True)
            parsed = parse_size(formatted)
            assert abs(parsed - value) / value < 0.01, f"Failed for {value}: {formatted} -> {parsed}"


class TestRoundTripGNU:
    """Test round-trip consistency with GNU format."""
    
    def test_gnu_decimal_roundtrip(self):
        """Test GNU decimal round trips."""
        values = [1000, 1000000, 1000000000]
        
        for value in values:
            formatted = naturalsize(value, gnu=True)
            parsed = parse_size(formatted)
            assert parsed == value, f"Failed for {value}: {formatted} -> {parsed}"
    
    def test_gnu_binary_roundtrip(self):
        """Test GNU binary round trips."""
        values = [1024, 1048576, 1073741824]
        
        for value in values:
            formatted = naturalsize(value, binary=True, gnu=True)
            # GNU format is ambiguous, need default_binary flag
            parsed = parse_size(formatted, default_binary=True)
            assert parsed == value, f"Failed for {value}: {formatted} -> {parsed}"


class TestRoundTripEdgeCases:
    """Test round-trip edge cases."""
    
    def test_zero_roundtrip(self):
        """Test zero round trips."""
        formatted = naturalsize(0)
        parsed = parse_size(formatted)
        assert parsed == 0
    
    def test_bytes_roundtrip(self):
        """Test byte values round trip."""
        values = [1, 10, 100, 999]
        
        for value in values:
            formatted = naturalsize(value)
            parsed = parse_size(formatted)
            assert abs(parsed - value) <= 1, f"Failed for {value}: {formatted} -> {parsed}"
    
    def test_negative_roundtrip(self):
        """Test negative values round trip."""
        value = -1000
        formatted = naturalsize(value)
        parsed = parse_size(formatted, allow_negative=True)
        assert parsed == value


class TestRoundTripWithOptions:
    """Test round-trip with various formatting options."""
    
    def test_strip_zeros_roundtrip(self):
        """Test round-trip with strip_trailing_zeros."""
        value = 1000
        formatted = naturalsize(value, strip_trailing_zeros=True)
        parsed = parse_size(formatted)
        assert parsed == value
    
    def test_custom_format_roundtrip(self):
        """Test round-trip with custom format."""
        value = 1234000
        formatted = naturalsize(value, format="%.2f")
        parsed = parse_size(formatted)
        # Allow rounding error
        assert abs(parsed - value) / value < 0.01


class TestRoundTripLargeNumbers:
    """Test round-trip for very large numbers."""
    
    def test_large_binary_roundtrip(self):
        """Test large binary values (>= 2^70)."""
        # 2^70 = 1180591620717411303424
        value = 2**70
        formatted = naturalsize(value, binary=True)
        parsed = parse_size(formatted)
        # Due to formatting precision, allow small relative error
        assert abs(parsed - value) / value < 0.01
    
    def test_petabyte_roundtrip(self):
        """Test petabyte-scale values."""
        value = 1125899906842624  # 1 PiB
        formatted = naturalsize(value, binary=True)
        parsed = parse_size(formatted)
        assert parsed == value
        
        value_dec = 1000000000000000  # 1 PB
        formatted_dec = naturalsize(value_dec)
        parsed_dec = parse_size(formatted_dec)
        assert parsed_dec == value_dec


class TestRoundTripConsistency:
    """Test consistency across multiple conversions."""
    
    def test_multiple_conversions(self):
        """Test that multiple conversions maintain consistency."""
        original = 1234567890
        
        # Convert multiple times
        for _ in range(3):
            formatted = naturalsize(original)
            parsed = parse_size(formatted)
            # Each iteration should yield similar results — allow up to 3% relative error for large numbers
            assert abs(parsed - original) / original < 0.03
            
            # Use parsed value for next iteration
            original = parsed
