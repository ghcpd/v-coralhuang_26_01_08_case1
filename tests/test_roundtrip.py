"""
Round-trip consistency tests.
Ensures parse_size and naturalsize are inverse operations where appropriate.
"""
import pytest
from mini_humanize import naturalsize, parse_size


class TestRoundTripDecimal:
    """Test round-trip conversion with decimal units."""
    
    def test_round_trip_simple_decimal(self):
        """Simple decimal units should round-trip."""
        values = [1000, 1000000, 1000000000, 1000000000000]
        for val in values:
            formatted = naturalsize(val)
            parsed = parse_size(formatted)
            assert parsed == val, f"{val} -> {formatted} -> {parsed}"
    
    def test_round_trip_decimal_with_fractions(self):
        """Decimal values with fractions."""
        # These may not round-trip exactly due to rounding
        val = 1500000  # 1.5 MB
        formatted = naturalsize(val)  # "1.5 MB"
        parsed = parse_size(formatted)
        assert parsed == val
    
    def test_round_trip_all_decimal_units(self):
        """Test all decimal unit magnitudes."""
        test_cases = [
            (1000, "1.0 kB"),
            (1000000, "1.0 MB"),
            (1000000000, "1.0 GB"),
            (1000000000000, "1.0 TB"),
            (1000000000000000, "1.0 PB"),
        ]
        for val, expected_format in test_cases:
            formatted = naturalsize(val)
            assert formatted == expected_format
            parsed = parse_size(formatted)
            assert parsed == val


class TestRoundTripBinary:
    """Test round-trip conversion with binary units."""
    
    def test_round_trip_simple_binary(self):
        """Simple binary units should round-trip."""
        values = [1024, 1024**2, 1024**3, 1024**4, 1024**5]
        for val in values:
            formatted = naturalsize(val, binary=True)
            parsed = parse_size(formatted)
            assert parsed == val, f"{val} -> {formatted} -> {parsed}"
    
    def test_round_trip_binary_with_fractions(self):
        """Binary values with fractions."""
        val = 1536  # 1.5 KiB
        formatted = naturalsize(val, binary=True)
        parsed = parse_size(formatted)
        assert parsed == val


class TestRoundTripGNU:
    """Test round-trip with GNU format."""
    
    def test_round_trip_gnu_decimal(self):
        """GNU format with decimal base."""
        val = 1000000
        formatted = naturalsize(val, gnu=True)  # "1.0M"
        # Parse needs to know it's decimal (default) or binary
        parsed = parse_size(formatted, default_binary=False)
        assert parsed == val
    
    def test_round_trip_gnu_binary(self):
        """GNU format with binary base."""
        val = 1024**2
        formatted = naturalsize(val, gnu=True, binary=True)  # "1.0M"
        parsed = parse_size(formatted, default_binary=True)
        assert parsed == val


class TestRoundTripPrecision:
    """Test precision handling in round trips."""
    
    def test_round_trip_with_custom_format(self):
        """Custom format precision."""
        val = 1234567
        # Default format is %.1f, so we get "1.2 MB"
        formatted = naturalsize(val)
        parsed = parse_size(formatted)
        # Due to rounding, parsed won't exactly match
        # 1.2 MB = 1,200,000 bytes
        assert parsed == 1200000
    
    def test_round_trip_strip_zeros(self):
        """Round trip with strip_trailing_zeros."""
        val = 1000000
        formatted = naturalsize(val, strip_trailing_zeros=True)  # "1 MB"
        parsed = parse_size(formatted)
        assert parsed == val


class TestRoundTripNegative:
    """Test round-trip with negative values."""
    
    def test_round_trip_negative(self):
        """Negative values should round-trip."""
        val = -1000000
        formatted = naturalsize(val)  # "-1.0 MB"
        parsed = parse_size(formatted, allow_negative=True)
        assert parsed == val


class TestRoundTripEdgeCases:
    """Test round-trip edge cases."""
    
    def test_round_trip_zero(self):
        """Zero should round-trip."""
        val = 0
        formatted = naturalsize(val)  # "0.0 B"
        parsed = parse_size(formatted)
        assert parsed == val
    
    def test_round_trip_bytes(self):
        """Small byte values."""
        for val in [1, 10, 100, 999]:
            formatted = naturalsize(val)
            parsed = parse_size(formatted)
            # Due to "1.0 B" format, parsing gives exact value
            assert parsed == val
    
    def test_round_trip_large_values(self):
        """Large values in petabytes."""
        val = 10 * 10**15  # 10 PB
        formatted = naturalsize(val)
        parsed = parse_size(formatted)
        assert parsed == val


class TestRoundTripConsistency:
    """Test consistency across multiple round trips."""
    
    def test_multiple_round_trips(self):
        """Multiple round trips should be stable."""
        val = 1000000
        
        # First round trip
        formatted1 = naturalsize(val)
        parsed1 = parse_size(formatted1)
        
        # Second round trip
        formatted2 = naturalsize(parsed1)
        parsed2 = parse_size(formatted2)
        
        # Should stabilize
        assert formatted1 == formatted2
        assert parsed1 == parsed2
    
    def test_idempotence(self):
        """parse_size(naturalsize(x)) should stabilize."""
        values = [1000, 1000000, 1000000000, 1024, 1024**2, 1024**3]
        
        for val in values:
            formatted = naturalsize(val)
            parsed = parse_size(formatted)
            
            # Format the parsed value again
            formatted2 = naturalsize(parsed)
            
            # Should be the same
            assert formatted == formatted2
