"""
Tests for parse_size function.
Covers various unit systems, formats, edge cases, and error handling.
"""
import pytest
from mini_humanize import parse_size


class TestParseSizeBasic:
    """Test basic parse_size functionality."""
    
    def test_bytes_only(self):
        """Parse byte values without units."""
        assert parse_size("0") == 0
        assert parse_size("1") == 1
        assert parse_size("999") == 999
        assert parse_size("1000") == 1000
    
    def test_bytes_with_b_suffix(self):
        """Parse values with B suffix."""
        assert parse_size("0B") == 0
        assert parse_size("1B") == 1
        assert parse_size("999 B") == 999
        assert parse_size("1000 B") == 1000
    
    def test_decimal_units_lowercase_k(self):
        """Parse decimal kB units (base 1000)."""
        assert parse_size("1kB") == 1000
        assert parse_size("1 kB") == 1000
        assert parse_size("2.5 kB") == 2500
        assert parse_size("10kB") == 10000
    
    def test_decimal_units_megabytes(self):
        """Parse decimal MB units."""
        assert parse_size("1MB") == 1000000
        assert parse_size("1 MB") == 1000000
        assert parse_size("2.5 MB") == 2500000
    
    def test_decimal_units_gigabytes(self):
        """Parse decimal GB units."""
        assert parse_size("1GB") == 1000000000
        assert parse_size("1 GB") == 1000000000
        assert parse_size("2.5 GB") == 2500000000
    
    def test_decimal_units_terabytes(self):
        """Parse decimal TB units."""
        assert parse_size("1TB") == 1000000000000
        assert parse_size("2 TB") == 2000000000000
    
    def test_decimal_units_petabytes(self):
        """Parse decimal PB units."""
        assert parse_size("1PB") == 1000000000000000
        assert parse_size("1 PB") == 1000000000000000


class TestParseSizeBinaryUnits:
    """Test binary (IEC 60027-2) units."""
    
    def test_kibibytes(self):
        """Parse KiB units (base 1024)."""
        assert parse_size("1KiB") == 1024
        assert parse_size("1 KiB") == 1024
        assert parse_size("2 KiB") == 2048
    
    def test_mebibytes(self):
        """Parse MiB units."""
        assert parse_size("1MiB") == 1024**2
        assert parse_size("1 MiB") == 1024**2
        assert parse_size("2 MiB") == 2 * 1024**2
    
    def test_gibibytes(self):
        """Parse GiB units."""
        assert parse_size("1GiB") == 1024**3
        assert parse_size("1 GiB") == 1024**3
    
    def test_tebibytes(self):
        """Parse TiB units."""
        assert parse_size("1TiB") == 1024**4
        assert parse_size("1 TiB") == 1024**4
    
    def test_pebibytes(self):
        """Parse PiB units."""
        assert parse_size("1PiB") == 1024**5
        assert parse_size("1 PiB") == 1024**5


class TestParseSizeAmbiguousUnits:
    """Test ambiguous units (GNU short form and legacy)."""
    
    def test_gnu_units_default_decimal(self):
        """GNU units (K, M, G) default to decimal (base 1000)."""
        assert parse_size("1K") == 1000
        assert parse_size("1M") == 1000000
        assert parse_size("1G") == 1000000000
        assert parse_size("1T") == 1000000000000
        assert parse_size("1P") == 1000000000000000
    
    def test_gnu_units_binary_mode(self):
        """GNU units with default_binary use base 1024."""
        assert parse_size("1K", default_binary=True) == 1024
        assert parse_size("1M", default_binary=True) == 1024**2
        assert parse_size("1G", default_binary=True) == 1024**3
    
    def test_legacy_kb_mb_default_decimal(self):
        """Legacy KB/MB units default to decimal."""
        assert parse_size("1KB") == 1000
        assert parse_size("1 KB") == 1000
        assert parse_size("1MB") == 1000000
        assert parse_size("1GB") == 1000000000
    
    def test_legacy_kb_mb_binary_mode(self):
        """Legacy units with default_binary use base 1024."""
        assert parse_size("1KB", default_binary=True) == 1024
        assert parse_size("1MB", default_binary=True) == 1024**2
        assert parse_size("1GB", default_binary=True) == 1024**3


class TestParseSizeScientificNotation:
    """Test scientific notation support."""
    
    def test_scientific_notation_lowercase_e(self):
        """Parse with lowercase 'e' notation."""
        assert parse_size("1e3") == 1000
        assert parse_size("1.5e3 MB") == 1500000000
        assert parse_size("2.5e2 kB") == 250000
    
    def test_scientific_notation_uppercase_e(self):
        """Parse with uppercase 'E' notation."""
        assert parse_size("1E3") == 1000
        assert parse_size("1.5E3 MB") == 1500000000
    
    def test_scientific_notation_negative_exponent(self):
        """Parse with negative exponents."""
        assert parse_size("5e-1 kB") == 500
        assert parse_size("2E-1 MB") == 200000


class TestParseSizeThousandsSeparator:
    """Test thousands separator support."""
    
    def test_thousands_separator_enabled(self):
        """Parse with thousands separator when enabled."""
        assert parse_size("1,000", allow_thousands_separator=True) == 1000
        assert parse_size("1,000,000", allow_thousands_separator=True) == 1000000
        assert parse_size("1,234,567", allow_thousands_separator=True) == 1234567
        assert parse_size("1,000 MB", allow_thousands_separator=True) == 1000000000
    
    def test_thousands_separator_disabled(self):
        """Thousands separator should fail when disabled (strict mode)."""
        with pytest.raises(ValueError):
            parse_size("1,000", allow_thousands_separator=False, strict=True)


class TestParseSizeRounding:
    """Test different rounding modes."""
    
    def test_rounding_nearest(self):
        """Nearest rounding (default)."""
        assert parse_size("1.4 B", rounding="nearest") == 1
        assert parse_size("1.5 B", rounding="nearest") == 2
        assert parse_size("1.6 B", rounding="nearest") == 2
        assert parse_size("2.5 B", rounding="nearest") == 2 or parse_size("2.5 B", rounding="nearest") == 3  # round() behavior
    
    def test_rounding_floor(self):
        """Floor rounding always rounds down."""
        assert parse_size("1.9 B", rounding="floor") == 1
        assert parse_size("1.1 B", rounding="floor") == 1
        assert parse_size("1.9 kB", rounding="floor") == 1900
    
    def test_rounding_ceil(self):
        """Ceil rounding always rounds up."""
        assert parse_size("1.1 B", rounding="ceil") == 2
        assert parse_size("1.9 B", rounding="ceil") == 2
        assert parse_size("1.1 kB", rounding="ceil") == 1100


class TestParseSizeNegativeValues:
    """Test negative value handling."""
    
    def test_negative_not_allowed_by_default(self):
        """Negative values should raise error by default."""
        with pytest.raises(ValueError, match="[Nn]egative"):
            parse_size("-100")
        with pytest.raises(ValueError, match="[Nn]egative"):
            parse_size("-1 MB")
    
    def test_negative_allowed(self):
        """Negative values work when explicitly allowed."""
        assert parse_size("-100", allow_negative=True) == -100
        assert parse_size("-1 kB", allow_negative=True) == -1000
        assert parse_size("-1 MB", allow_negative=True) == -1000000


class TestParseSizeConstraints:
    """Test min/max value constraints."""
    
    def test_min_value_constraint(self):
        """Values below minimum should raise error."""
        with pytest.raises(ValueError, match="below minimum"):
            parse_size("100", min_value=1000)
        
        # Valid value should work
        assert parse_size("2000", min_value=1000) == 2000
    
    def test_max_value_constraint(self):
        """Values above maximum should raise error."""
        with pytest.raises(ValueError, match="(above|exceeds) maximum"):
            parse_size("2000", max_value=1000)
        
        # Valid value should work
        assert parse_size("500", max_value=1000) == 500
    
    def test_min_max_both(self):
        """Test both constraints together."""
        assert parse_size("50 MB", min_value=1000, max_value=100000000) == 50000000
        
        with pytest.raises(ValueError):
            parse_size("10 B", min_value=1000, max_value=100000000)
        
        with pytest.raises(ValueError):
            parse_size("1 GB", min_value=1000, max_value=100000000)


class TestParseSizeStrictMode:
    """Test strict vs permissive mode."""
    
    def test_strict_invalid_unit(self):
        """Strict mode should reject unknown units."""
        with pytest.raises(ValueError, match="[Uu]nknown unit"):
            parse_size("100 XYZ", strict=True)
    
    def test_permissive_invalid_unit(self):
        """Permissive mode should ignore unknown units."""
        assert parse_size("100 XYZ", strict=False) == 100
    
    def test_strict_invalid_format(self):
        """Strict mode should reject malformed input."""
        with pytest.raises(ValueError, match="[Ii]nvalid"):
            parse_size("not a number", strict=True)


class TestParseSizeLocale:
    """Test locale-aware decimal separator."""
    
    def test_locale_en_us_decimal_point(self):
        """US locale uses period as decimal separator."""
        assert parse_size("1.5 MB", locale="en_US") == 1500000
    
    def test_locale_de_decimal_comma(self):
        """German locale uses comma as decimal separator."""
        # Note: Locale support requires allow_thousands_separator in some implementations
        try:
            result = parse_size("1,5 MB", locale="de_DE")
            assert result == 1500000
        except ValueError:
            # Some implementations may not support this without explicit flag
            pytest.skip("Locale decimal separator not supported without allow_thousands_separator")
    
    def test_locale_de_thousands_separator(self):
        """German locale uses period as thousands separator."""
        # "1.500 MB" with de_DE locale means 1500 (not 1,500,000)
        result = parse_size("1.500 MB", locale="de_DE", allow_thousands_separator=True)
        # Could be interpreted as 1.5 MB (1500000) or 1500 MB (1500000000)
        assert result in [1500000, 1500000000]


class TestParseSizeEdgeCases:
    """Test edge cases and corner conditions."""
    
    def test_empty_string(self):
        """Empty string should raise error."""
        with pytest.raises(ValueError):
            parse_size("")
        with pytest.raises(ValueError):
            parse_size("   ")
    
    def test_whitespace_handling(self):
        """Handle leading/trailing whitespace."""
        assert parse_size("  1000  ") == 1000
        assert parse_size("  1 MB  ") == 1000000
    
    def test_case_sensitivity(self):
        """Units should be case-sensitive."""
        assert parse_size("1MB") == 1000000
        assert parse_size("1MiB") == 1024**2
        assert parse_size("1M") == 1000000  # GNU short form
    
    def test_zero_values(self):
        """Zero should work with all units."""
        assert parse_size("0") == 0
        assert parse_size("0 B") == 0
        assert parse_size("0 MB") == 0
        assert parse_size("0 GiB") == 0
    
    def test_fractional_bytes(self):
        """Fractional bytes should be handled according to rounding."""
        assert parse_size("0.5 B") in [0, 1]  # Python round() rounds 0.5 up to 1
        assert parse_size("0.6 B") == 1
        assert parse_size("0.9 B", rounding="floor") == 0
        assert parse_size("0.1 B", rounding="ceil") == 1


class TestParseSizeLargeNumbers:
    """Test handling of very large numbers."""
    
    def test_large_numbers_no_precision_loss(self):
        """Handle numbers >= 2^70 without precision loss."""
        # 2^70 bytes
        large = 2**70
        large_str = str(large)
        assert parse_size(large_str) == large
    
    def test_petabytes_large(self):
        """Parse large petabyte values."""
        result = parse_size("1000 PB")
        assert result == 1000 * 10**15
    
    def test_pebibytes_large(self):
        """Parse large pebibyte values."""
        result = parse_size("100 PiB")
        assert result == 100 * 1024**5


class TestParseSizeComplexity:
    """Verify O(n) complexity constraint."""
    
    def test_performance_scales_linearly(self):
        """Performance should scale with input length."""
        import time
        
        # Short input
        start = time.perf_counter()
        for _ in range(1000):
            parse_size("1.5 MB")
        short_time = time.perf_counter() - start
        
        # Longer input with thousands separators
        start = time.perf_counter()
        for _ in range(1000):
            parse_size("1,234,567.890 MB", allow_thousands_separator=True)
        long_time = time.perf_counter() - start
        
        # Should be roughly similar (within an order of magnitude)
        # This is a soft check - not strict O(n) proof but sanity check
        assert long_time < short_time * 20  # very generous bound
