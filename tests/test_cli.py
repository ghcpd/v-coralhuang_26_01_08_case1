"""CLI tests using subprocess."""
import subprocess
import sys
import pytest


def run_cli(*args):
    """Helper to run the CLI and return output."""
    result = subprocess.run(
        [sys.executable, "-m", "mini_humanize"] + list(args),
        capture_output=True,
        text=True,
        cwd="c:\\Bug_Bash\\26_01_08\\oswe-mini-secondary"
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


class TestCLIFormat:
    """Test CLI format command."""
    
    def test_format_basic(self):
        """Test basic format command."""
        code, stdout, stderr = run_cli("format", "1000")
        assert code == 0
        assert stdout == "1.0 kB"
    
    def test_format_binary(self):
        """Test format with --binary flag."""
        code, stdout, stderr = run_cli("format", "1024", "--binary")
        assert code == 0
        assert stdout == "1.0 KiB"
    
    def test_format_gnu(self):
        """Test format with --gnu flag."""
        code, stdout, stderr = run_cli("format", "1000", "--gnu")
        assert code == 0
        assert stdout == "1.0K"
    
    def test_format_binary_gnu(self):
        """Test format with both --binary and --gnu."""
        code, stdout, stderr = run_cli("format", "1024", "--binary", "--gnu")
        assert code == 0
        assert stdout == "1.0K"
    
    def test_format_custom_format(self):
        """Test format with custom --format."""
        code, stdout, stderr = run_cli("format", "1500", "--format", "%.2f")
        assert code == 0
        assert stdout == "1.50 kB"
    
    def test_format_strip_zeros(self):
        """Test format with --strip-trailing-zeros."""
        code, stdout, stderr = run_cli("format", "1000", "--strip-trailing-zeros")
        assert code == 0
        assert stdout == "1 kB"
    
    def test_format_large_value(self):
        """Test format with large value."""
        code, stdout, stderr = run_cli("format", "1000000000")
        assert code == 0
        assert stdout == "1.0 GB"
    
    def test_format_string_input(self):
        """Test format with string input."""
        code, stdout, stderr = run_cli("format", "1000000")
        assert code == 0
        assert "MB" in stdout or "GB" in stdout or "kB" in stdout


class TestCLIParse:
    """Test CLI parse command."""
    
    def test_parse_basic(self):
        """Test basic parse command."""
        code, stdout, stderr = run_cli("parse", "1 kB")
        assert code == 0
        assert stdout == "1000"
    
    def test_parse_binary(self):
        """Test parse with binary units."""
        code, stdout, stderr = run_cli("parse", "1 KiB")
        assert code == 0
        assert stdout == "1024"
    
    def test_parse_ambiguous_default_binary(self):
        """Test parse with ambiguous unit and --default-binary."""
        code, stdout, stderr = run_cli("parse", "1 KB", "--default-binary")
        assert code == 0
        assert stdout == "1024"
    
    def test_parse_gnu(self):
        """Test parse with GNU units."""
        code, stdout, stderr = run_cli("parse", "1K")
        assert code == 0
        assert stdout == "1000"
    
    def test_parse_gnu_binary(self):
        """Test parse GNU with --default-binary."""
        code, stdout, stderr = run_cli("parse", "1K", "--default-binary")
        assert code == 0
        assert stdout == "1024"
    
    def test_parse_rounding_floor(self):
        """Test parse with floor rounding."""
        code, stdout, stderr = run_cli("parse", "1.9 B", "--rounding", "floor")
        assert code == 0
        assert stdout == "1"
    
    def test_parse_rounding_ceil(self):
        """Test parse with ceil rounding."""
        code, stdout, stderr = run_cli("parse", "1.1 B", "--rounding", "ceil")
        assert code == 0
        assert stdout == "2"
    
    def test_parse_rounding_nearest(self):
        """Test parse with nearest rounding (default)."""
        code, stdout, stderr = run_cli("parse", "1.5 B", "--rounding", "nearest")
        assert code == 0
        assert stdout == "2"
    
    def test_parse_allow_negative(self):
        """Test parse with negative value."""
        code, stdout, stderr = run_cli("parse", "-100 B", "--allow-negative")
        assert code == 0
        assert stdout == "-100"
    
    def test_parse_min_value(self):
        """Test parse with --min-value."""
        code, stdout, stderr = run_cli("parse", "1000 B", "--min-value", "500")
        assert code == 0
        assert stdout == "1000"
        
        # Should fail if below minimum
        code, stdout, stderr = run_cli("parse", "100 B", "--min-value", "500")
        assert code != 0
    
    def test_parse_max_value(self):
        """Test parse with --max-value."""
        code, stdout, stderr = run_cli("parse", "100 B", "--max-value", "500")
        assert code == 0
        assert stdout == "100"
        
        # Should fail if above maximum
        code, stdout, stderr = run_cli("parse", "1000 B", "--max-value", "500")
        assert code != 0
    
    def test_parse_thousands_separator(self):
        """Test parse with thousands separator."""
        code, stdout, stderr = run_cli("parse", "1,000 B", "--allow-thousands-separator")
        assert code == 0
        assert stdout == "1000"


class TestCLIRoundTrip:
    """Test CLI round-trip conversions."""
    
    def test_format_parse_roundtrip(self):
        """Test format -> parse round trip."""
        # Format 1000 bytes
        code1, formatted, _ = run_cli("format", "1000")
        assert code1 == 0
        
        # Parse back
        code2, parsed, _ = run_cli("parse", formatted)
        assert code2 == 0
        assert parsed == "1000"
    
    def test_format_parse_binary_roundtrip(self):
        """Test binary format -> parse round trip."""
        code1, formatted, _ = run_cli("format", "1024", "--binary")
        assert code1 == 0
        
        code2, parsed, _ = run_cli("parse", formatted)
        assert code2 == 0
        assert parsed == "1024"
    
    def test_format_parse_gnu_roundtrip(self):
        """Test GNU format -> parse round trip."""
        code1, formatted, _ = run_cli("format", "1024", "--binary", "--gnu")
        assert code1 == 0
        
        # Need --default-binary since GNU format is ambiguous
        code2, parsed, _ = run_cli("parse", formatted, "--default-binary")
        assert code2 == 0
        assert parsed == "1024"


class TestCLIErrors:
    """Test CLI error handling."""
    
    def test_format_invalid_value(self):
        """Test format with invalid value."""
        code, stdout, stderr = run_cli("format", "abc")
        assert code != 0
    
    def test_parse_invalid_format(self):
        """Test parse with invalid format."""
        code, stdout, stderr = run_cli("parse", "abc")
        assert code != 0
    
    def test_parse_unknown_unit(self):
        """Test parse with unknown unit (strict mode)."""
        code, stdout, stderr = run_cli("parse", "100 XYZ", "--strict")
        assert code != 0
    
    def test_missing_command(self):
        """Test CLI with no command."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize"],
            capture_output=True,
            text=True,
            cwd="c:\\Bug_Bash\\26_01_08\\oswe-mini-secondary"
        )
        assert result.returncode != 0
    
    def test_format_missing_value(self):
        """Test format command without value."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "format"],
            capture_output=True,
            text=True,
            cwd="c:\\Bug_Bash\\26_01_08\\oswe-mini-secondary"
        )
        assert result.returncode != 0
    
    def test_parse_missing_text(self):
        """Test parse command without text."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "parse"],
            capture_output=True,
            text=True,
            cwd="c:\\Bug_Bash\\26_01_08\\oswe-mini-secondary"
        )
        assert result.returncode != 0


class TestCLIHelpAndUsage:
    """Test CLI help and usage information."""
    
    def test_help(self):
        """Test --help flag."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "--help"],
            capture_output=True,
            text=True,
            cwd="c:\\Bug_Bash\\26_01_08\\oswe-mini-secondary"
        )
        assert result.returncode == 0
        assert "format" in result.stdout
        assert "parse" in result.stdout
    
    def test_format_help(self):
        """Test format --help."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "format", "--help"],
            capture_output=True,
            text=True,
            cwd="c:\\Bug_Bash\\26_01_08\\oswe-mini-secondary"
        )
        assert result.returncode == 0
        assert "binary" in result.stdout
    
    def test_parse_help(self):
        """Test parse --help."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize", "parse", "--help"],
            capture_output=True,
            text=True,
            cwd="c:\\Bug_Bash\\26_01_08\\oswe-mini-secondary"
        )
        assert result.returncode == 0
        assert "rounding" in result.stdout
