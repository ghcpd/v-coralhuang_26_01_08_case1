import pytest
from mini_humanize import naturalsize, parse_size


class TestRoundTrip:
    def test_round_trip_decimal(self):
        test_values = [0, 1, 1000, 1000**2, 1000**3, 1000**4]
        for value in test_values:
            formatted = naturalsize(value)
            parsed = parse_size(formatted)
            assert parsed == value, f"Failed for {value}: {formatted} -> {parsed}"

    def test_round_trip_binary(self):
        test_values = [0, 1, 1024, 1024**2, 1024**3, 1024**4]
        for value in test_values:
            formatted = naturalsize(value, binary=True)
            parsed = parse_size(formatted, default_binary=True)
            assert parsed == value, f"Failed for {value}: {formatted} -> {parsed}"

    def test_round_trip_gnu(self):
        test_values = [1000, 1000**2]
        for value in test_values:
            formatted = naturalsize(value, gnu=True)
            parsed = parse_size(formatted)
            assert parsed == value, f"Failed for {value}: {formatted} -> {parsed}"

    def test_round_trip_with_strip(self):
        test_values = [1000, 1000**2]
        for value in test_values:
            formatted = naturalsize(value, strip_trailing_zeros=True)
            parsed = parse_size(formatted)
            assert parsed == value, f"Failed for {value}: {formatted} -> {parsed}"