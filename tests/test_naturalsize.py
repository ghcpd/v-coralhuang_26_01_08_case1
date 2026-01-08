"""Tests for naturalsize function - backward compatibility and edge cases."""
import pytest
from mini_humanize import naturalsize


class TestNaturalsizeBasic:
    """Test basic naturalsize functionality."""
    
    def test_bytes(self):
        """Test byte values."""
        assert naturalsize(0) == "0.0 B"
        assert naturalsize(1) == "1.0 B"
        assert naturalsize(999) == "999.0 B"
    
    def test_kilobytes_decimal(self):
        """Test kilobyte values (decimal, base 1000)."""
        assert naturalsize(1000) == "1.0 kB"
        assert naturalsize(1500) == "1.5 kB"
        assert naturalsize(999999) == "1000.0 kB"
    
    def test_megabytes_decimal(self):
        """Test megabyte values (decimal)."""
        assert naturalsize(1000000) == "1.0 MB"
        assert naturalsize(1500000) == "1.5 MB"
    
    def test_gigabytes_decimal(self):
        """Test gigabyte values (decimal)."""
        assert naturalsize(1000000000) == "1.0 GB"
        assert naturalsize(1500000000) == "1.5 GB"
    
    def test_terabytes_decimal(self):
        """Test terabyte values (decimal)."""
        assert naturalsize(1000000000000) == "1.0 TB"
    
    def test_petabytes_decimal(self):
        """Test petabyte values (decimal)."""
        assert naturalsize(1000000000000000) == "1.0 PB"


class TestNaturalsizeBinary:
    """Test binary mode (base 1024)."""
    
    def test_kibibytes(self):
        """Test KiB values."""
        assert naturalsize(1024, binary=True) == "1.0 KiB"
        assert naturalsize(1536, binary=True) == "1.5 KiB"
    
    def test_mebibytes(self):
        """Test MiB values."""
        assert naturalsize(1048576, binary=True) == "1.0 MiB"
        assert naturalsize(1572864, binary=True) == "1.5 MiB"
    
    def test_gibibytes(self):
        """Test GiB values."""
        assert naturalsize(1073741824, binary=True) == "1.0 GiB"
    
    def test_tebibytes(self):
        """Test TiB values."""
        assert naturalsize(1099511627776, binary=True) == "1.0 TiB"
    
    def test_pebibytes(self):
        """Test PiB values."""
        assert naturalsize(1125899906842624, binary=True) == "1.0 PiB"


class TestNaturalsizeGNU:
    """Test GNU mode (no space, short suffixes)."""
    
    def test_gnu_decimal(self):
        """Test GNU mode with decimal (base 1000)."""
        assert naturalsize(0, gnu=True) == "0.0B"
        assert naturalsize(1000, gnu=True) == "1.0K"
        assert naturalsize(1000000, gnu=True) == "1.0M"
        assert naturalsize(1000000000, gnu=True) == "1.0G"
    
    def test_gnu_binary(self):
        """Test GNU mode with binary (base 1024)."""
        assert naturalsize(1024, binary=True, gnu=True) == "1.0K"
        assert naturalsize(1048576, binary=True, gnu=True) == "1.0M"
        assert naturalsize(1073741824, binary=True, gnu=True) == "1.0G"


class TestNaturalsizeFormatting:
    """Test formatting options."""
    
    def test_custom_format(self):
        """Test custom format strings."""
        assert naturalsize(1500, format="%.2f") == "1.50 kB"
        assert naturalsize(1500, format="%.0f") == "2 kB"
        assert naturalsize(1234, format="%.3f") == "1.234 kB"
    
    def test_strip_trailing_zeros(self):
        """Test stripping trailing zeros."""
        assert naturalsize(1000, strip_trailing_zeros=True) == "1 kB"
        assert naturalsize(1500, strip_trailing_zeros=True) == "1.5 kB"
        assert naturalsize(1100, strip_trailing_zeros=True, format="%.2f") == "1.1 kB"
    
    def test_strip_trailing_zeros_bytes(self):
        """Test stripping trailing zeros for byte values."""
        assert naturalsize(0, strip_trailing_zeros=True) == "0 B"
        assert naturalsize(100, strip_trailing_zeros=True) == "100 B"


class TestNaturalsizeEdgeCases:
    """Test edge cases and special values."""
    
    def test_negative_values(self):
        """Test negative sizes."""
        assert naturalsize(-1000) == "-1.0 kB"
        assert naturalsize(-1024, binary=True) == "-1.0 KiB"
        assert naturalsize(-1000, gnu=True) == "-1.0K"
    
    def test_zero(self):
        """Test zero value."""
        assert naturalsize(0) == "0.0 B"
        assert naturalsize(0, binary=True) == "0.0 B"
        assert naturalsize(0, gnu=True) == "0.0B"
    
    def test_large_values(self):
        """Test very large values (>= 2^70)."""
        # 2^70 = 1180591620717411303424
        large = 2**70
        result = naturalsize(large, binary=True)
        # Should be in PiB range
        assert "PiB" in result
        
        # Test decimal too
        result_dec = naturalsize(large)
        assert "PB" in result_dec
    
    def test_float_input(self):
        """Test float input values."""
        assert naturalsize(1000.5) == "1.0 kB"
        assert naturalsize(1500.7, binary=True) == "1.5 KiB"
    
    def test_string_input(self):
        """Test string input (numeric)."""
        assert naturalsize("1000") == "1.0 kB"
        assert naturalsize("1024", binary=True) == "1.0 KiB"
    
    def test_string_input_invalid(self):
        """Test invalid string input."""
        with pytest.raises(ValueError, match="must be a number"):
            naturalsize("abc")
    
    def test_invalid_type(self):
        """Test invalid input type."""
        with pytest.raises(TypeError, match="must be int, float, or str"):
            naturalsize([1000])


class TestBackwardCompatibility:
    """Verify backward compatibility - default outputs must not change."""
    
    def test_default_outputs(self):
        """Test that default parameter outputs match baseline behavior."""
        # These test cases ensure backward compatibility
        test_cases = [
            (0, "0.0 B"),
            (1, "1.0 B"),
            (999, "999.0 B"),
            (1000, "1.0 kB"),
            (1000000, "1.0 MB"),
            (1000000000, "1.0 GB"),
            (1500, "1.5 kB"),
            (1500000, "1.5 MB"),
        ]
        
        for value, expected in test_cases:
            assert naturalsize(value) == expected, f"Failed for {value}"
    
    def test_binary_default_outputs(self):
        """Test binary mode default outputs."""
        test_cases = [
            (1024, "1.0 KiB"),
            (1048576, "1.0 MiB"),
            (1073741824, "1.0 GiB"),
        ]
        
        for value, expected in test_cases:
            assert naturalsize(value, binary=True) == expected
    
    def test_gnu_default_outputs(self):
        """Test GNU mode default outputs."""
        test_cases = [
            (1000, "1.0K"),
            (1000000, "1.0M"),
            (1000000000, "1.0G"),
        ]
        
        for value, expected in test_cases:
            assert naturalsize(value, gnu=True) == expected
