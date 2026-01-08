import subprocess
import sys
import pytest
from mini_humanize import naturalsize, parse_size


class TestCLI:
    def run_cli(self, args):
        """Run the CLI and return stdout."""
        result = subprocess.run(
            [sys.executable, "-m", "mini_humanize"] + args,
            capture_output=True,
            text=True,
            cwd="c:\\Bug_Bash\\26_01_08\\grok-fast"
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()

    def test_format_basic(self):
        code, out, err = self.run_cli(["format", "1000"])
        assert code == 0
        assert out == naturalsize(1000)

    def test_format_options(self):
        code, out, err = self.run_cli(["format", "1024", "--binary", "--gnu"])
        assert code == 0
        assert out == naturalsize(1024, binary=True, gnu=True)

    def test_parse_basic(self):
        code, out, err = self.run_cli(["parse", "1 MB"])
        assert code == 0
        assert out == str(parse_size("1 MB"))

    def test_parse_options(self):
        code, out, err = self.run_cli(["parse", "1K", "--default-binary"])
        assert code == 0
        assert out == str(parse_size("1K", default_binary=True))

    def test_invalid_command(self):
        code, out, err = self.run_cli(["invalid"])
        assert code == 2

    def test_parse_error(self):
        code, out, err = self.run_cli(["parse", "invalid"])
        assert code != 0