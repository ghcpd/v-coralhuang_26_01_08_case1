import subprocess
import sys


def run_cmd(args):
    p = subprocess.run([sys.executable, "-m", "mini_humanize"] + args, capture_output=True, text=True)
    return p


def test_cli_format():
    p = run_cmd(["format", "1536", "--binary"]) 
    assert p.returncode == 0
    assert p.stdout.strip() == "1.5 KiB"


def test_cli_parse():
    p = run_cmd(["parse", "1.5 KiB", "--default-binary"]) 
    assert p.returncode == 0
    assert p.stdout.strip() == "1536"


def test_cli_parse_with_flags():
    p = run_cmd(["parse", "1,234.56 kB", "--allow-thousands-separator", "--locale", "en_US"]) 
    assert p.returncode == 0
    assert p.stdout.strip() == "1234560"
