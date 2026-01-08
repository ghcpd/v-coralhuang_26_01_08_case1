"""Tests for parse_size function - comprehensive format and edge case coverage."""
import pytest
from mini_humanize import parse_size


class TestParseSizeBasic:
    """Test basic parse_size functionality."""
    
    def test_bytes_explicit(self):
        """Test explicit byte values."""
        assert parse_size("100 B") == 100
        assert parse_size("100B") == 100
        assert parse_size("0 B") == 0
        assert parse_size("1 B") == 1
    
    def test_bytes_implicit(self):
        """Test implicit bytes (number only)."""
        assert parse_size("100") == 100
        assert parse_size("0") == 0
        assert parse_size("1234567") == 1234567


class TestParseSizeBinaryUnits:
    """Test binary units (KiB, MiB, etc.) - explicit base 1024."""
    
    def test_kibibytes(self):
        """Test KiB parsing."""
        assert parse_size("1 KiB") == 1024
        assert parse_size("1KiB") == 1024
        assert parse_size("1.5 KiB") == 1536
        assert parse_size("2 kib") == 2048  # case insensitive
    
    def test_mebibytes(self):
        """Test MiB parsing."""
        assert parse_size("1 MiB") == 1048576
        assert parse_size("1.5 MiB") == 1572864
        assert parse_size("10 MiB") == 10485760
    
    def test_gibibytes(self):
        """Test GiB parsing."""
        assert parse_size("1 GiB") == 1073741824
        assert parse_size("2 GiB") == 2147483648
    
    def test_tebibytes(self):
        """Test TiB parsing."""
        assert parse_size("1 TiB") == 1099511627776
        assert parse_size("2 TiB") == 2199023255552
    
    def test_pebibytes(self):
        """Test PiB parsing."""
        assert parse_size("1 PiB") == 1125899906842624
    
    def test_larger_binary_units(self):
        """Test EiB, ZiB, YiB."""
        assert parse_size("1 EiB") == 1152921504606846976
        assert parse_size("1 ZiB") == 1180591620717411303424
        assert parse_size("1 YiB") == 1208925819614629174706176


class TestParseSizeDecimalUnits:
    """Test decimal units (kB, MB, etc.) - explicit base 1000."""
    
    def test_kilobytes(self):
        """Test kB parsing."""
        assert parse_size("1 kB") == 1000
        assert parse_size("1kB") == 1000
        assert parse_size("1.5 kB") == 1500
        assert parse_size("2 KB") == 2000  # case variations
    
    def test_megabytes(self):
        """Test MB parsing."""
        assert parse_size("1 MB") == 1000000
        assert parse_size("1.5 MB") == 1500000
        assert parse_size("10 MB") == 10000000
    
    def test_gigabytes(self):
        """Test GB parsing."""
        assert parse_size("1 GB") == 1000000000
        assert parse_size("2 GB") == 2000000000
    
    def test_terabytes(self):
        """Test TB parsing."""
        assert parse_size("1 TB") == 1000000000000
    
    def test_petabytes(self):
        """Test PB parsing."""
        assert parse_size("1 PB") == 1000000000000000
    
    def test_larger_decimal_units(self):
        """Test EB, ZB, YB."""
        assert parse_size("1 EB") == 1000000000000000000
        assert parse_size("1 ZB") == 1000000000000000000000
        assert parse_size("1 YB") == 1000000000000000000000000


class TestParseSizeGNUUnits:
    """Test GNU-style single-letter units (K, M, G, etc.)."""
    
    def test_gnu_decimal_default(self):
        """Test GNU units default to decimal (base 1000)."""
        assert parse_size("1K") == 1000
        assert parse_size("1M") == 1000000
        assert parse_size("1G") == 1000000000
        assert parse_size("1T") == 1000000000000
        assert parse_size("1P") == 1000000000000000
    
    def test_gnu_binary_mode(self):
        """Test GNU units with default_binary=True."""
        assert parse_size("1K", default_binary=True) == 1024
        assert parse_size("1M", default_binary=True) == 1048576
        assert parse_size("1G", default_binary=True) == 1073741824
        assert parse_size("1T", default_binary=True) == 1099511627776
    
    def test_gnu_with_spaces(self):
        """Test GNU units with spaces."""
        assert parse_size("1 K") == 1000
        assert parse_size("1.5 M") == 1500000


class TestParseSizeAmbiguousUnits:
    """Test ambiguous units (KB, MB, etc.) with default_binary flag."""
    
    def test_ambiguous_decimal_default(self):
        """Test KB/MB/GB default to decimal."""
        assert parse_size("1 KB") == 1000
        assert parse_size("1 MB") == 1000000
        assert parse_size("1 GB") == 1000000000
    
    def test_ambiguous_binary_mode(self):
        """Test KB/MB/GB with default_binary=True."""
        assert parse_size("1 KB", default_binary=True) == 1024
        assert parse_size("1 MB", default_binary=True) == 1048576
        assert parse_size("1 GB", default_binary=True) == 1073741824


class TestParseSizeScientificNotation:
    """Test scientific notation support."""
    
    def test_scientific_basic(self):
        """Test basic scientific notation."""
        assert parse_size("1e3 B") == 1000
        assert parse_size("1E3 B") == 1000
        assert parse_size("1.5e3 B") == 1500
    
    def test_scientific_with_units(self):
        """Test scientific notation with units."""
        assert parse_size("1.5e3 MB") == 1500000000
        assert parse_size("2E-1 KB") == 200
        assert parse_size("1e6 B") == 1000000
    
    def test_scientific_negative_exponent(self):
        """Test negative exponents."""
        assert parse_size("5e-1 KB") == 500
        assert parse_size("1e-3 MB") == 1000


class TestParseSizeThousandsSeparator:
    """Test thousands separator support."""
    
    def test_thousands_separator_allowed(self):
        """Test comma as thousands separator."""
        assert parse_size("1,000 B", allow_thousands_separator=True) == 1000
        assert parse_size("1,000,000 B", allow_thousands_separator=True) == 1000000
        assert parse_size("10,000 KB", allow_thousands_separator=True) == 10000000
    
    def test_thousands_separator_not_allowed(self):
        """Test comma rejected when not allowed."""
        with pytest.raises(ValueError):
            parse_size("1,000 B", allow_thousands_separator=False, strict=True)


class TestParseSizeRounding:
    """Test rounding behavior for fractional bytes."""
    
    def test_rounding_nearest(self):
        """Test nearest rounding (default)."""
        assert parse_size("1.4 B", rounding="nearest") == 1
        assert parse_size("1.5 B", rounding="nearest") == 2
        assert parse_size("1.6 B", rounding="nearest") == 2
    
    def test_rounding_floor(self):
        """Test floor rounding."""
        assert parse_size("1.1 B", rounding="floor") == 1
        assert parse_size("1.9 B", rounding="floor") == 1
        assert parse_size("2.0 B", rounding="floor") == 2
    
    def test_rounding_ceil(self):
        """Test ceiling rounding."""
        assert parse_size("1.1 B", rounding="ceil") == 2
        assert parse_size("1.9 B", rounding="ceil") == 2
        assert parse_size("1.0 B", rounding="ceil") == 1
    
    def test_rounding_with_units(self):
        """Test rounding with different units."""
        # 1.5 KB = 1500 bytes (no rounding needed)
        assert parse_size("1.5 KB", rounding="floor") == 1500
        
        # Fractional result: 1.5 KiB = 1536 bytes
        # 1.1 KiB = 1126.4 bytes
        assert parse_size("1.1 KiB", rounding="floor") == 1126
        assert parse_size("1.1 KiB", rounding="nearest") == 1126
        assert parse_size("1.1 KiB", rounding="ceil") == 1127


class TestParseSizeNegative:
    """Test negative value handling."""
    
    def test_negative_not_allowed_default(self):
        """Test negative values rejected by default."""
        with pytest.raises(ValueError, match="Negative size not allowed"):
            parse_size("-100 B")
        
        with pytest.raises(ValueError, match="Negative size not allowed"):
            parse_size("-1 KB")
    
    def test_negative_allowed(self):
        """Test negative values when allowed."""
        assert parse_size("-100 B", allow_negative=True) == -100
        assert parse_size("-1 KB", allow_negative=True) == -1000
        assert parse_size("-1.5 MB", allow_negative=True) == -1500000


class TestParseSizeBounds:
    """Test min/max value constraints."""
    
    def test_min_value(self):
        """Test minimum value constraint."""
        assert parse_size("100 B", min_value=0) == 100
        assert parse_size("100 B", min_value=50) == 100
        
        with pytest.raises(ValueError, match="below minimum"):
            parse_size("100 B", min_value=200)
    
    def test_max_value(self):
        """Test maximum value constraint."""
        assert parse_size("100 B", max_value=200) == 100
        assert parse_size("100 B", max_value=100) == 100
        
        with pytest.raises(ValueError, match="exceeds maximum"):
            parse_size("100 B", max_value=50)
    
    def test_both_bounds(self):
        """Test both min and max constraints."""
        assert parse_size("100 B", min_value=50, max_value=200) == 100
        
        with pytest.raises(ValueError, match="below minimum"):
            parse_size("100 B", min_value=200, max_value=300)
        
        with pytest.raises(ValueError, match="exceeds maximum"):
            parse_size("100 B", min_value=0, max_value=50)


class TestParseSizeStrictMode:
    """Test strict vs permissive parsing."""
    
    def test_strict_rejects_invalid_unit(self):
        """Test strict mode rejects unknown units."""
        with pytest.raises(ValueError, match="Unknown unit"):
            parse_size("100 XB", strict=True)
    
    def test_permissive_handles_invalid_unit(self):
        """Test permissive mode treats unknown units as bytes."""
        assert parse_size("100 XB", strict=False) == 100
    
    def test_strict_rejects_malformed(self):
        """Test strict mode rejects malformed input."""
        with pytest.raises(ValueError):
            parse_size("abc KB", strict=True)


class TestParseSizeEdgeCases:
    """Test edge cases and special inputs."""
    
    def test_whitespace_handling(self):
        """Test various whitespace scenarios."""
        assert parse_size("  100 B  ") == 100
        assert parse_size("100  B") == 100
        assert parse_size("100\tB") == 100
    
    def test_empty_string(self):
        """Test empty string."""
        with pytest.raises(ValueError, match="Empty string"):
            parse_size("")
        
        with pytest.raises(ValueError, match="Empty string"):
            parse_size("   ")
    
    def test_zero_values(self):
        """Test zero in various formats."""
        assert parse_size("0") == 0
        assert parse_size("0 B") == 0
        assert parse_size("0 KB") == 0
        assert parse_size("0.0 MB") == 0
    
    def test_large_values(self):
        """Test very large values (>= 2^70)."""
        # 2^70 bytes
        large_bytes = 2**70
        
        # Test parsing large number directly
        result = parse_size(f"{large_bytes} B")
        assert result == large_bytes
        
        # Test parsing in larger units
        # 1 ZiB = 2^70 bytes
        result = parse_size("1 ZiB")
        assert result == 1180591620717411303424
        
        # Verify we can handle even larger
        result = parse_size("1 YiB")
        assert result == 1208925819614629174706176
    
    def test_precision_preservation(self):
        """Test that large values maintain precision."""
        # Parse a large value and verify exact result
        value = "1234567890123456789"
        result = parse_size(f"{value} B")
        assert result == int(value)
    
    def test_case_insensitivity(self):
        """Test case-insensitive parsing."""
        assert parse_size("1 kb") == 1000
        assert parse_size("1 Kb") == 1000
        assert parse_size("1 KB") == 1000
        assert parse_size("1 kB") == 1000
        
        assert parse_size("1 mib") == 1048576
        assert parse_size("1 MiB") == 1048576
        assert parse_size("1 MIB") == 1048576
    
    def test_decimal_variations(self):
        """Test various decimal formats."""
        assert parse_size("1.0 KB") == 1000
        assert parse_size("1.00 KB") == 1000
        assert parse_size(".5 KB") == 500
        assert parse_size("0.5 KB") == 500


class TestParseSizeInvalidInput:
    """Test invalid input handling."""
    
    def test_non_string_input(self):
        """Test non-string input."""
        with pytest.raises(TypeError, match="Expected string"):
            parse_size(1000)
        
        with pytest.raises(TypeError, match="Expected string"):
            parse_size(None)
        
        with pytest.raises(TypeError, match="Expected string"):
            parse_size(["1 KB"])
    
    def test_invalid_number_format(self):
        """Test invalid number formats."""
        with pytest.raises(ValueError):
            parse_size("abc KB")
        
        with pytest.raises(ValueError):
            parse_size("1.2.3 KB")
    
    def test_unit_only(self):
        """Test unit without number."""
        with pytest.raises(ValueError, match="No number found"):
            parse_size("KB")
        
        with pytest.raises(ValueError, match="No number found"):
            parse_size("MiB")
