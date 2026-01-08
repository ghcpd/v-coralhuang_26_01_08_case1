"""
Tests for naturalsize function.
Tests backward compatibility and various formatting options.
"""
import pytest
from mini_humanize import naturalsize


class TestNaturalsizeBasic:
    """Test basic naturalsize functionality and backward compatibility."""
    
    def test_bytes_default(self):
        """Small values should show as bytes."""
        assert naturalsize(0) == "0.0 B"
        assert naturalsize(1) == "1.0 B"
        assert naturalsize(999) == "999.0 B"
    
    def test_kilobytes_decimal(self):
        """Decimal kilobytes (base 1000)."""
        assert naturalsize(1000) == "1.0 kB"
        assert naturalsize(1500) == "1.5 kB"
        assert naturalsize(10000) == "10.0 kB"
    
    def test_megabytes_decimal(self):
        """Decimal megabytes."""
        assert naturalsize(1000000) == "1.0 MB"
        assert naturalsize(1500000) == "1.5 MB"
    
    def test_gigabytes_decimal(self):
        """Decimal gigabytes."""
        assert naturalsize(1000000000) == "1.0 GB"
        assert naturalsize(2500000000) == "2.5 GB"
    
    def test_terabytes_decimal(self):
        """Decimal terabytes."""
        assert naturalsize(1000000000000) == "1.0 TB"
    
    def test_petabytes_decimal(self):
        """Decimal petabytes."""
        assert naturalsize(1000000000000000) == "1.0 PB"
    
    def test_binary_mode(self):
        """Binary mode uses 1024 base and IEC units."""
        assert naturalsize(0, binary=True) == "0.0 B"
        assert naturalsize(1024, binary=True) == "1.0 KiB"
        assert naturalsize(1024**2, binary=True) == "1.0 MiB"
        assert naturalsize(1024**3, binary=True) == "1.0 GiB"
        assert naturalsize(1024**4, binary=True) == "1.0 TiB"
        assert naturalsize(1024**5, binary=True) == "1.0 PiB"
    
    def test_gnu_mode_decimal(self):
        """GNU mode with decimal base."""
        assert naturalsize(0, gnu=True) == "0.0B"
        assert naturalsize(1000, gnu=True) == "1.0K"
        assert naturalsize(1000000, gnu=True) == "1.0M"
        assert naturalsize(1000000000, gnu=True) == "1.0G"
    
    def test_gnu_mode_binary(self):
        """GNU mode with binary base."""
        assert naturalsize(1024, gnu=True, binary=True) == "1.0K"
        assert naturalsize(1024**2, gnu=True, binary=True) == "1.0M"
        assert naturalsize(1024**3, gnu=True, binary=True) == "1.0G"
    
    def test_negative_values(self):
        """Negative values should preserve sign."""
        assert naturalsize(-1000) == "-1.0 kB"
        assert naturalsize(-1024, binary=True) == "-1.0 KiB"
        assert naturalsize(-1000, gnu=True) == "-1.0K"


class TestNaturalsizeFormatting:
    """Test various formatting options."""
    
    def test_custom_format_precision(self):
        """Custom format string for different precision."""
        assert naturalsize(1500, format="%.2f") == "1.50 kB"
        assert naturalsize(1500, format="%.0f") == "2 kB"  # rounds to nearest
        assert naturalsize(1234567, format="%.3f") == "1.235 MB"
    
    def test_strip_trailing_zeros(self):
        """Strip trailing zeros from output."""
        assert naturalsize(1000, strip_trailing_zeros=True) == "1 kB"
        assert naturalsize(1500, strip_trailing_zeros=True) == "1.5 kB"
        assert naturalsize(1100, strip_trailing_zeros=True) == "1.1 kB"
    
    def test_strip_trailing_zeros_with_gnu(self):
        """Strip trailing zeros in GNU mode."""
        assert naturalsize(1000, gnu=True, strip_trailing_zeros=True) == "1K"
        assert naturalsize(1500, gnu=True, strip_trailing_zeros=True) == "1.5K"
    
    def test_zero_with_strip_trailing_zeros(self):
        """Zero should format correctly with strip_trailing_zeros."""
        # This tests the bug fix
        assert naturalsize(0, strip_trailing_zeros=True) == "0 B"
        assert naturalsize(0.0, strip_trailing_zeros=True) == "0 B"


class TestNaturalsizeInputTypes:
    """Test different input types."""
    
    def test_integer_input(self):
        """Integer input should work."""
        assert naturalsize(1000) == "1.0 kB"
    
    def test_float_input(self):
        """Float input should work."""
        assert naturalsize(1000.0) == "1.0 kB"
        assert naturalsize(1500.5) == "1.5 kB"
    
    def test_string_input(self):
        """String input should be parsed."""
        assert naturalsize("1000") == "1.0 kB"
        assert naturalsize("1500.5") == "1.5 kB"
    
    def test_invalid_string_input(self):
        """Invalid string input should raise ValueError."""
        with pytest.raises(ValueError, match="must be a number"):
            naturalsize("not a number")
    
    def test_invalid_type(self):
        """Invalid type should raise TypeError."""
        with pytest.raises(TypeError, match="must be int, float, or str"):
            naturalsize([1000])


class TestNaturalsizeLargeNumbers:
    """Test handling of very large numbers."""
    
    def test_large_numbers(self):
        """Handle numbers >= 2^70."""
        large = 2**70
        result = naturalsize(large)
        assert "PB" in result or "EB" in result
        # Should not crash or lose precision significantly
    
    def test_very_large_binary(self):
        """Very large numbers in binary mode."""
        large = 2**70
        result = naturalsize(large, binary=True)
        assert "PiB" in result or "EiB" in result


class TestNaturalsizeBackwardCompatibility:
    """Ensure default behavior hasn't changed."""
    
    def test_default_output_format(self):
        """Default outputs must match expected format."""
        # These test cases ensure backward compatibility
        assert naturalsize(0) == "0.0 B"
        assert naturalsize(1) == "1.0 B"
        assert naturalsize(1000) == "1.0 kB"
        assert naturalsize(1000000) == "1.0 MB"
        assert naturalsize(1500000) == "1.5 MB"
        
    def test_default_uses_decimal(self):
        """Default should use decimal (base 1000), not binary."""
        assert naturalsize(1000) == "1.0 kB"  # not 1.0 KiB
        assert "kB" in naturalsize(10000)
        
    def test_default_format_string(self):
        """Default format string is %.1f."""
        assert naturalsize(1234) == "1.2 kB"
        assert naturalsize(1567) == "1.6 kB"
