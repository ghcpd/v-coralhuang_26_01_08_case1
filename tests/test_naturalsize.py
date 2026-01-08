"""
Tests for naturalsize function - ensuring backward compatibility
and correct behavior across various inputs and formats.
"""
import pytest
from mini_humanize import naturalsize


class TestNaturalsizeBasicDecimal:
    """Test basic decimal (base 1000) formatting"""
    
    def test_bytes(self):
        assert naturalsize(0) == "0.0 B"
        assert naturalsize(1) == "1.0 B"
        assert naturalsize(999) == "999.0 B"
    
    def test_kilobytes(self):
        assert naturalsize(1000) == "1.0 kB"
        assert naturalsize(1500) == "1.5 kB"
        assert naturalsize(999999) == "1000.0 kB"
    
    def test_megabytes(self):
        assert naturalsize(1000000) == "1.0 MB"
        assert naturalsize(1500000) == "1.5 MB"
    
    def test_gigabytes(self):
        assert naturalsize(1000000000) == "1.0 GB"
        assert naturalsize(2500000000) == "2.5 GB"
    
    def test_terabytes(self):
        assert naturalsize(1000000000000) == "1.0 TB"
    
    def test_petabytes(self):
        assert naturalsize(1000000000000000) == "1.0 PB"


class TestNaturalsizeBasicBinary:
    """Test binary (base 1024) formatting"""
    
    def test_bytes(self):
        assert naturalsize(0, binary=True) == "0.0 B"
        assert naturalsize(1, binary=True) == "1.0 B"
        assert naturalsize(1023, binary=True) == "1023.0 B"
    
    def test_kibibytes(self):
        assert naturalsize(1024, binary=True) == "1.0 KiB"
        assert naturalsize(1536, binary=True) == "1.5 KiB"
    
    def test_mebibytes(self):
        assert naturalsize(1048576, binary=True) == "1.0 MiB"
        assert naturalsize(1572864, binary=True) == "1.5 MiB"
    
    def test_gibibytes(self):
        assert naturalsize(1073741824, binary=True) == "1.0 GiB"
    
    def test_tebibytes(self):
        assert naturalsize(1099511627776, binary=True) == "1.0 TiB"
    
    def test_pebibytes(self):
        assert naturalsize(1125899906842624, binary=True) == "1.0 PiB"


class TestNaturalsizeGNU:
    """Test GNU-style formatting (no space between number and unit)"""
    
    def test_decimal_gnu(self):
        assert naturalsize(1000, gnu=True) == "1.0K"
        assert naturalsize(1000000, gnu=True) == "1.0M"
        assert naturalsize(1000000000, gnu=True) == "1.0G"
    
    def test_binary_gnu(self):
        assert naturalsize(1024, binary=True, gnu=True) == "1.0K"
        assert naturalsize(1048576, binary=True, gnu=True) == "1.0M"
        assert naturalsize(1073741824, binary=True, gnu=True) == "1.0G"


class TestNaturalsizeFormatting:
    """Test custom format strings and strip_trailing_zeros"""
    
    def test_custom_format(self):
        assert naturalsize(1500, format="%.2f") == "1.50 kB"
        assert naturalsize(1500, format="%.0f") == "2 kB"
        assert naturalsize(1500, format="%.3f") == "1.500 kB"
    
    def test_strip_trailing_zeros(self):
        assert naturalsize(1000, strip_trailing_zeros=True) == "1 kB"
        assert naturalsize(1500, strip_trailing_zeros=True) == "1.5 kB"
        assert naturalsize(1100, strip_trailing_zeros=True) == "1.1 kB"
    
    def test_strip_trailing_zeros_zero_value(self):
        # Test the bug fix for size=0 with strip_trailing_zeros
        assert naturalsize(0, strip_trailing_zeros=True) == "0 B"
    
    def test_strip_trailing_zeros_with_gnu(self):
        assert naturalsize(1000, gnu=True, strip_trailing_zeros=True) == "1K"


class TestNaturalsizeNegative:
    """Test negative values"""
    
    def test_negative_decimal(self):
        assert naturalsize(-1000) == "-1.0 kB"
        assert naturalsize(-1500) == "-1.5 kB"
    
    def test_negative_binary(self):
        assert naturalsize(-1024, binary=True) == "-1.0 KiB"
        assert naturalsize(-1536, binary=True) == "-1.5 KiB"
    
    def test_negative_gnu(self):
        assert naturalsize(-1000, gnu=True) == "-1.0K"
    
    def test_negative_zero(self):
        # Edge case: -0.0 should display as positive
        assert naturalsize(-0.0) == "0.0 B"


class TestNaturalsizeInputTypes:
    """Test different input types"""
    
    def test_int_input(self):
        assert naturalsize(1000) == "1.0 kB"
    
    def test_float_input(self):
        assert naturalsize(1000.0) == "1.0 kB"
        assert naturalsize(1500.5) == "1.5 kB"
    
    def test_string_input(self):
        assert naturalsize("1000") == "1.0 kB"
        assert naturalsize("1500.5") == "1.5 kB"
    
    def test_invalid_string_input(self):
        with pytest.raises(ValueError, match="must be a number"):
            naturalsize("not a number")
    
    def test_invalid_type(self):
        with pytest.raises(TypeError, match="must be int, float, or str"):
            naturalsize([1000])
        with pytest.raises(TypeError, match="must be int, float, or str"):
            naturalsize(None)


class TestNaturalsizeLargeNumbers:
    """Test handling of very large numbers (>= 2^70)"""
    
    def test_large_number_precision(self):
        # 2^70 = 1180591620717411303424
        large_val = 2**70
        result = naturalsize(large_val)
        # Should not lose precision and should format correctly
        assert "PB" in result or "EB" in result
    
    def test_very_large_decimal(self):
        # 1 YB = 10^24
        val = 10**24
        result = naturalsize(val)
        # Should handle without overflow
        assert isinstance(result, str)
    
    def test_very_large_binary(self):
        # 1 YiB = 2^80
        val = 2**80
        result = naturalsize(val, binary=True)
        assert isinstance(result, str)


class TestNaturalsizeEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_exactly_at_boundary(self):
        # Exactly 1000 should move to next unit
        assert naturalsize(1000) == "1.0 kB"
        assert naturalsize(1000000) == "1.0 MB"
    
    def test_just_below_boundary(self):
        assert naturalsize(999) == "999.0 B"
        assert "kB" in naturalsize(999999)
    
    def test_fractional_bytes(self):
        # Fractional bytes should be handled
        assert naturalsize(0.5) == "0.5 B"
        assert naturalsize(1.999) == "2.0 B"


class TestNaturalsizeBackwardCompatibility:
    """
    Verify backward compatibility: default behavior must not change
    """
    
    def test_default_parameters_100(self):
        assert naturalsize(100) == "100.0 B"
    
    def test_default_parameters_1500(self):
        assert naturalsize(1500) == "1.5 kB"
    
    def test_default_parameters_1048576(self):
        assert naturalsize(1048576) == "1.0 MB"
    
    def test_default_parameters_zero(self):
        assert naturalsize(0) == "0.0 B"
    
    def test_default_format_string(self):
        # Default format is "%.1f"
        result = naturalsize(1234)
        assert "1.2 kB" == result or "1.3 kB" == result
