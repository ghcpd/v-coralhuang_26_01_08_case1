"""
CLI tests using subprocess to test the command-line interface
"""
import subprocess
import sys
import pytest


def run_cli(*args):
    """Helper to run the CLI and capture output"""
    result = subprocess.run(
        [sys.executable, "-m", "mini_humanize"] + list(args),
        capture_output=True,
        text=True,
    )
    return result


class TestCLIFormat:
    """Test the format subcommand"""
    
    def test_basic_format(self):
        result = run_cli("format", "1000")
        assert result.returncode == 0
        assert "kB" in result.stdout
    
    def test_format_binary(self):
        result = run_cli("format", "1024", "--binary")
        assert result.returncode == 0
        assert "KiB" in result.stdout
    
    def test_format_gnu(self):
        result = run_cli("format", "1000", "--gnu")
        assert result.returncode == 0
        assert "K" in result.stdout
        # GNU format has no space
        assert " " not in result.stdout.strip()
    
    def test_format_custom_format(self):
        result = run_cli("format", "1500", "--format", "%.2f")
        assert result.returncode == 0
        output = result.stdout.strip()
        # Should have 2 decimal places
        assert ".5" in output or "1.50" in output
    
    def test_format_strip_trailing_zeros(self):
        result = run_cli("format", "1000", "--strip-trailing-zeros")
        assert result.returncode == 0
        # Should not have .0
        assert ".0" not in result.stdout
    
    def test_format_invalid_value(self):
        result = run_cli("format", "not_a_number")
        assert result.returncode == 1
        assert "Error" in result.stderr


class TestCLIParse:
    """Test the parse subcommand"""
    
    def test_basic_parse(self):
        result = run_cli("parse", "1 KB")
        assert result.returncode == 0
        assert "1000" in result.stdout
    
    def test_parse_binary(self):
        result = run_cli("parse", "1 KiB")
        assert result.returncode == 0
        assert "1024" in result.stdout
    
    def test_parse_default_binary(self):
        result = run_cli("parse", "1 K", "--default-binary")
        assert result.returncode == 0
        assert "1024" in result.stdout
    
    def test_parse_gnu_decimal(self):
        result = run_cli("parse", "1K")
        assert result.returncode == 0
        assert "1000" in result.stdout
    
    def test_parse_gnu_binary(self):
        result = run_cli("parse", "1K", "--default-binary")
        assert result.returncode == 0
        assert "1024" in result.stdout
    
    def test_parse_with_thousands_separator(self):
        result = run_cli("parse", "1,000 B", "--allow-thousands-separator")
        assert result.returncode == 0
        assert "1000" in result.stdout
    
    def test_parse_rounding_floor(self):
        result = run_cli("parse", "1.9 B", "--rounding", "floor")
        assert result.returncode == 0
        assert "1" in result.stdout.strip()
    
    def test_parse_rounding_ceil(self):
        result = run_cli("parse", "1.1 B", "--rounding", "ceil")
        assert result.returncode == 0
        assert "2" in result.stdout.strip()
    
    def test_parse_allow_negative(self):
        result = run_cli("parse", "-100 B", "--allow-negative")
        assert result.returncode == 0
        assert "-100" in result.stdout
    
    def test_parse_negative_without_flag(self):
        result = run_cli("parse", "-100 B")
        assert result.returncode == 1
        assert "Error" in result.stderr
    
    def test_parse_min_value(self):
        result = run_cli("parse", "100 B", "--min-value", "50")
        assert result.returncode == 0
        assert "100" in result.stdout
    
    def test_parse_min_value_violation(self):
        result = run_cli("parse", "10 B", "--min-value", "50")
        assert result.returncode == 1
        assert "Error" in result.stderr
    
    def test_parse_max_value(self):
        result = run_cli("parse", "100 B", "--max-value", "200")
        assert result.returncode == 0
        assert "100" in result.stdout
    
    def test_parse_max_value_violation(self):
        result = run_cli("parse", "500 B", "--max-value", "200")
        assert result.returncode == 1
        assert "Error" in result.stderr
    
    def test_parse_invalid_input(self):
        result = run_cli("parse", "invalid")
        assert result.returncode == 1
        assert "Error" in result.stderr


class TestCLIHelp:
    """Test help messages"""
    
    def test_main_help(self):
        result = run_cli("--help")
        assert result.returncode == 0
        assert "format" in result.stdout
        assert "parse" in result.stdout
    
    def test_format_help(self):
        result = run_cli("format", "--help")
        assert result.returncode == 0
        assert "binary" in result.stdout
        assert "gnu" in result.stdout
    
    def test_parse_help(self):
        result = run_cli("parse", "--help")
        assert result.returncode == 0
        assert "default-binary" in result.stdout
        assert "rounding" in result.stdout


class TestCLIEdgeCases:
    """Test CLI edge cases"""
    
    def test_no_arguments(self):
        result = run_cli()
        assert result.returncode == 2
    
    def test_zero_value(self):
        result = run_cli("format", "0")
        assert result.returncode == 0
        assert "B" in result.stdout
    
    def test_large_value(self):
        result = run_cli("format", str(2**70))
        assert result.returncode == 0
        # Should handle without error
        assert result.stdout.strip()


class TestCLIRoundTrip:
    """Test that CLI format and parse are inverses"""
    
    def test_format_then_parse(self):
        # Format a value
        format_result = run_cli("format", "1234567")
        assert format_result.returncode == 0
        formatted = format_result.stdout.strip()
        
        # Parse it back
        parse_result = run_cli("parse", formatted)
        assert parse_result.returncode == 0
        parsed = int(parse_result.stdout.strip())
        
        # Should be close to original
        assert abs(parsed - 1234567) / 1234567 < 0.1
    
    def test_format_binary_then_parse(self):
        format_result = run_cli("format", "1048576", "--binary")
        assert format_result.returncode == 0
        formatted = format_result.stdout.strip()
        
        parse_result = run_cli("parse", formatted)
        assert parse_result.returncode == 0
        parsed = int(parse_result.stdout.strip())
        
        assert abs(parsed - 1048576) / 1048576 < 0.1
