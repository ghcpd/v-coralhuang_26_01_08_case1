"""
Tests for parse_size function - comprehensive coverage of
parsing human-readable size strings into bytes.
"""
import pytest
from mini_humanize import parse_size


class TestParseSizeBasicBinary:
    """Test parsing binary units (KiB, MiB, GiB, etc.)"""
    
    def test_bytes(self):
        assert parse_size("0 B") == 0
        assert parse_size("1 B") == 1
        assert parse_size("100 B") == 100
        assert parse_size("1000B") == 1000
    
    def test_kibibytes(self):
        assert parse_size("1 KiB") == 1024
        assert parse_size("2 KiB") == 2048
        assert parse_size("1.5 KiB") == 1536
        assert parse_size("10KiB") == 10240
    
    def test_mebibytes(self):
        assert parse_size("1 MiB") == 1048576
        assert parse_size("2.5 MiB") == 2621440
        assert parse_size("10MiB") == 10485760
    
    def test_gibibytes(self):
        assert parse_size("1 GiB") == 1073741824
        assert parse_size("5 GiB") == 5368709120
    
    def test_tebibytes(self):
        assert parse_size("1 TiB") == 1099511627776
        assert parse_size("2 TiB") == 2199023255552
    
    def test_pebibytes(self):
        assert parse_size("1 PiB") == 1125899906842624


class TestParseSizeBasicDecimal:
    """Test parsing decimal units (kB, MB, GB, etc.)"""
    
    def test_kilobytes(self):
        assert parse_size("1 kB") == 1000
        assert parse_size("1.5 kB") == 1500
        assert parse_size("10kB") == 10000
    
    def test_megabytes(self):
        assert parse_size("1 MB") == 1000000
        assert parse_size("2.5 MB") == 2500000
        assert parse_size("10MB") == 10000000
    
    def test_gigabytes(self):
        assert parse_size("1 GB") == 1000000000
        assert parse_size("5 GB") == 5000000000
    
    def test_terabytes(self):
        assert parse_size("1 TB") == 1000000000000
        assert parse_size("2 TB") == 2000000000000
    
    def test_petabytes(self):
        assert parse_size("1 PB") == 1000000000000000


class TestParseSizeGNUStyle:
    """Test parsing GNU-style short suffixes (K, M, G, T, P)"""
    
    def test_gnu_decimal_default(self):
        # By default, short suffixes use decimal (base 1000)
        assert parse_size("1K") == 1000
        assert parse_size("1M") == 1000000
        assert parse_size("1G") == 1000000000
        assert parse_size("1T") == 1000000000000
        assert parse_size("1P") == 1000000000000000
    
    def test_gnu_binary_with_flag(self):
        # With default_binary=True, short suffixes use binary (base 1024)
        assert parse_size("1K", default_binary=True) == 1024
        assert parse_size("1M", default_binary=True) == 1048576
        assert parse_size("1G", default_binary=True) == 1073741824
        assert parse_size("1T", default_binary=True) == 1099511627776
    
    def test_gnu_with_decimals(self):
        assert parse_size("1.5K") == 1500
        assert parse_size("2.5M", default_binary=True) == 2621440


class TestParseSizeLegacyUnits:
    """Test ambiguous legacy units (KB, MB, GB) with default_binary flag"""
    
    def test_legacy_decimal_default(self):
        # By default, KB/MB/GB use decimal (base 1000)
        assert parse_size("1 KB") == 1000
        assert parse_size("1 MB") == 1000000
        assert parse_size("1 GB") == 1000000000
    
    def test_legacy_binary_with_flag(self):
        # With default_binary=True, KB/MB/GB use binary (base 1024)
        assert parse_size("1 KB", default_binary=True) == 1024
        assert parse_size("1 MB", default_binary=True) == 1048576
        assert parse_size("1 GB", default_binary=True) == 1073741824


class TestParseSizeScientificNotation:
    """Test scientific notation in numbers"""
    
    def test_basic_scientific(self):
        assert parse_size("1e3 B") == 1000
        assert parse_size("1.5e3 B") == 1500
        assert parse_size("2e6 B") == 2000000
    
    def test_scientific_with_units(self):
        assert parse_size("1e3 KB") == 1000000
        assert parse_size("1.5e2 MB") == 150000000
    
    def test_negative_exponent(self):
        assert parse_size("5e-1 KiB") == 512
        assert parse_size("1e-1 MB") == 100000
    
    def test_uppercase_e(self):
        assert parse_size("1E3 B") == 1000
        assert parse_size("1.5E6 B") == 1500000


class TestParseSizeThousandsSeparator:
    """Test thousands separator handling"""
    
    def test_comma_separator(self):
        assert parse_size("1,000 B", allow_thousands_separator=True) == 1000
        assert parse_size("1,000,000 B", allow_thousands_separator=True) == 1000000
        assert parse_size("10,500 KB", allow_thousands_separator=True) == 10500000
    
    def test_comma_not_allowed_by_default(self):
        # Without flag, comma should cause parse error
        with pytest.raises(ValueError):
            parse_size("1,000 B")
    
    def test_space_separator(self):
        assert parse_size("1 000 B", allow_thousands_separator=True) == 1000


class TestParseSizeRounding:
    """Test rounding modes for fractional bytes"""
    
    def test_floor_rounding(self):
        assert parse_size("1.9 B", rounding="floor") == 1
        assert parse_size("2.1 B", rounding="floor") == 2
        assert parse_size("1.5 KiB", rounding="floor") == 1536
    
    def test_ceil_rounding(self):
        assert parse_size("1.1 B", rounding="ceil") == 2
        assert parse_size("1.9 B", rounding="ceil") == 2
        assert parse_size("1.5 KiB", rounding="ceil") == 1536
    
    def test_nearest_rounding(self):
        assert parse_size("1.4 B", rounding="nearest") == 1
        assert parse_size("1.5 B", rounding="nearest") == 2
        assert parse_size("1.6 B", rounding="nearest") == 2
    
    def test_default_rounding_is_nearest(self):
        assert parse_size("1.5 B") == 2


class TestParseSizeNegativeValues:
    """Test negative value handling"""
    
    def test_negative_not_allowed_by_default(self):
        with pytest.raises(ValueError, match="[Nn]egative"):
            parse_size("-100 B")
        with pytest.raises(ValueError, match="[Nn]egative"):
            parse_size("-1 KB")
    
    def test_negative_with_flag(self):
        assert parse_size("-100 B", allow_negative=True) == -100
        assert parse_size("-1 KB", allow_negative=True) == -1000
        assert parse_size("-1.5 MiB", allow_negative=True) == -1572864
    
    def test_explicit_positive_sign(self):
        assert parse_size("+100 B") == 100
        assert parse_size("+1 KB") == 1000


class TestParseSizeConstraints:
    """Test min_value and max_value constraints"""
    
    def test_min_value_constraint(self):
        assert parse_size("100 B", min_value=50) == 100
        with pytest.raises(ValueError, match="below minimum"):
            parse_size("10 B", min_value=50)
    
    def test_max_value_constraint(self):
        assert parse_size("100 B", max_value=200) == 100
        with pytest.raises(ValueError, match="exceeds maximum"):
            parse_size("500 B", max_value=200)
    
    def test_both_constraints(self):
        assert parse_size("100 B", min_value=50, max_value=200) == 100
        with pytest.raises(ValueError):
            parse_size("10 B", min_value=50, max_value=200)
        with pytest.raises(ValueError):
            parse_size("500 B", min_value=50, max_value=200)


class TestParseSizeStrictMode:
    """Test strict vs permissive mode"""
    
    def test_invalid_unit_strict(self):
        with pytest.raises(ValueError, match="Unknown unit"):
            parse_size("100 XB", strict=True)
    
    def test_invalid_unit_permissive(self):
        # Permissive mode: treat unknown unit as bytes
        assert parse_size("100 XB", strict=False) == 100


class TestParseSizeCaseInsensitive:
    """Test that unit parsing is case-insensitive"""
    
    def test_uppercase(self):
        assert parse_size("1 KIB") == 1024
        assert parse_size("1 MB") == 1000000
        assert parse_size("1 GB") == 1000000000
    
    def test_lowercase(self):
        assert parse_size("1 kib") == 1024
        assert parse_size("1 mb") == 1000000
        assert parse_size("1 gb") == 1000000000
    
    def test_mixed_case(self):
        assert parse_size("1 KiB") == 1024
        assert parse_size("1 mB") == 1000000


class TestParseSizeWhitespace:
    """Test whitespace handling"""
    
    def test_leading_trailing_whitespace(self):
        assert parse_size("  100 B  ") == 100
        assert parse_size("\t1 KB\n") == 1000
    
    def test_no_space_between_number_and_unit(self):
        assert parse_size("100B") == 100
        assert parse_size("1KB") == 1000
        assert parse_size("1.5MiB") == 1572864
    
    def test_multiple_spaces(self):
        assert parse_size("100   B") == 100
        assert parse_size("1    KB") == 1000


class TestParseSizeErrorHandling:
    """Test error conditions and edge cases"""
    
    def test_empty_string(self):
        with pytest.raises(ValueError, match="non-empty"):
            parse_size("")
        with pytest.raises(ValueError, match="non-empty"):
            parse_size("   ")
    
    def test_invalid_number(self):
        with pytest.raises(ValueError, match="Invalid"):
            parse_size("abc KB")
        with pytest.raises(ValueError, match="Invalid"):
            parse_size("-- 100 B")
    
    def test_non_string_input(self):
        with pytest.raises(ValueError, match="must be.*string"):
            parse_size(123)
        with pytest.raises(ValueError, match="must be.*string"):
            parse_size(None)
    
    def test_nan_infinity(self):
        with pytest.raises(ValueError, match="Invalid"):
            parse_size("inf B")
        with pytest.raises(ValueError, match="Invalid"):
            parse_size("nan B")


class TestParseSizeLargeNumbers:
    """Test handling of very large numbers (>= 2^70)"""
    
    def test_large_number_2_70(self):
        # 2^70 bytes = 1048576 PiB = 1 EiB
        result = parse_size("1048576 PiB")
        assert result == 2**70
    
    def test_large_number_precision(self):
        # Ensure no precision loss for large numbers
        val = 2**70
        result = parse_size(f"{val} B")
        assert result == val
    
    def test_very_large_exponent(self):
        # 1 YiB = 2^80
        result = parse_size("1 YiB")
        assert result == 2**80


class TestParseSizeEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_zero(self):
        assert parse_size("0") == 0
        assert parse_size("0 B") == 0
        assert parse_size("0 KB") == 0
        assert parse_size("0.0 MB") == 0
    
    def test_fractional_bytes_various_rounding(self):
        assert parse_size("0.5 B", rounding="floor") == 0
        assert parse_size("0.5 B", rounding="ceil") == 1
        assert parse_size("0.5 B", rounding="nearest") == 0
    
    def test_no_unit_means_bytes(self):
        assert parse_size("100") == 100
        assert parse_size("1234") == 1234
    
    def test_just_b_unit(self):
        assert parse_size("100 b") == 100
        assert parse_size("100 B") == 100


class TestParseSizeComplexFormats:
    """Test complex real-world formats"""
    
    def test_mixed_formats(self):
        assert parse_size("1.5e3KB") == 1500000
        assert parse_size("2.5E-1 MiB") == 262144
    
    def test_very_precise_decimals(self):
        assert parse_size("1.123456789 KB") == 1123
        assert parse_size("1.999999 KB") == 2000
    
    def test_leading_zeros(self):
        assert parse_size("0001 KB") == 1000
        assert parse_size("00.5 MB") == 500000
