"""
Tests for CLI functionality.
Tests both format and parse subcommands via subprocess.
"""
import subprocess
import sys
import pytest


class TestCLIFormat:
    """Test the 'format' subcommand."""
    
    def test_format_basic(self):
        """Basic format command."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "format", "1000000"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "1.0 MB" in result.stdout
    
    def test_format_binary(self):
        """Format with binary flag."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "format", "1048576", "--binary"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "1.0 MiB" in result.stdout
    
    def test_format_gnu(self):
        """Format with GNU flag."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "format", "1000000", "--gnu"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "1.0M" in result.stdout
    
    def test_format_custom_format(self):
        """Format with custom format string."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "format", "1500000", "--format", "%.2f"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "1.50 MB" in result.stdout
    
    def test_format_strip_trailing_zeros(self):
        """Format with strip trailing zeros."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "format", "1000000", "--strip-trailing-zeros"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "1 MB" in result.stdout


class TestCLIParse:
    """Test the 'parse' subcommand."""
    
    def test_parse_basic(self):
        """Basic parse command."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "parse", "1 MB"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "1000000" in result.stdout
    
    def test_parse_binary_unit(self):
        """Parse binary unit."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "parse", "1 MiB"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "1048576" in result.stdout
    
    def test_parse_default_binary(self):
        """Parse with default-binary flag."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "parse", "1M", "--default-binary"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "1048576" in result.stdout
    
    def test_parse_thousands_separator(self):
        """Parse with thousands separator."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "parse", "1,000", "--allow-thousands-separator"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "1000" in result.stdout
    
    def test_parse_rounding_floor(self):
        """Parse with floor rounding."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "parse", "1.9", "--rounding", "floor"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "1" in result.stdout
    
    def test_parse_rounding_ceil(self):
        """Parse with ceil rounding."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "parse", "1.1", "--rounding", "ceil"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "2" in result.stdout
    
    def test_parse_allow_negative(self):
        """Parse with allow-negative flag."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "parse", "-100", "--allow-negative"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "-100" in result.stdout


class TestCLIErrors:
    """Test CLI error handling."""
    
    def test_no_subcommand(self):
        """No subcommand should show error."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
    
    def test_invalid_subcommand(self):
        """Invalid subcommand should show error."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "invalid"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
    
    def test_parse_negative_without_flag(self):
        """Parsing negative without allow-negative should fail."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "parse", "-100"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0


class TestCLIRoundTrip:
    """Test round-trip through CLI."""
    
    def test_cli_round_trip_decimal(self):
        """Format then parse should give original value."""
        # Format
        format_result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "format", "1000000"],
            capture_output=True,
            text=True,
        )
        formatted = format_result.stdout.strip()
        
        # Parse
        parse_result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "parse", formatted],
            capture_output=True,
            text=True,
        )
        parsed = parse_result.stdout.strip()
        
        assert parsed == "1000000"
    
    def test_cli_round_trip_binary(self):
        """Format binary then parse should work."""
        # Format
        format_result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "format", "1048576", "--binary"],
            capture_output=True,
            text=True,
        )
        formatted = format_result.stdout.strip()
        
        # Parse
        parse_result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "parse", formatted],
            capture_output=True,
            text=True,
        )
        parsed = parse_result.stdout.strip()
        
        assert parsed == "1048576"
