#!/usr/bin/env python
"""
run_tests - One-click test runner for mini_humanize
This script ensures dependencies are installed and runs the full test suite.
"""
import sys
import subprocess
import os

def run_command(cmd, description=""):
    """Run a command and return the exit code"""
    if description:
        print(description)
    result = subprocess.run(cmd, shell=True)
    return result.returncode

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"✗ Python 3.10 or later required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install test dependencies if needed"""
    print("\nChecking dependencies...")
    
    # Check pytest
    try:
        import pytest
        print("✓ pytest already installed")
    except ImportError:
        print("✗ pytest not found. Installing dependencies...")
        if run_command(f"{sys.executable} -m pip install --quiet pytest pytest-cov") != 0:
            print("✗ Failed to install dependencies")
            return False
        print("✓ Dependencies installed")
    
    # Check pytest-cov
    try:
        import pytest_cov
        print("✓ pytest-cov already installed")
    except ImportError:
        print("✗ pytest-cov not found. Installing...")
        if run_command(f"{sys.executable} -m pip install --quiet pytest-cov") != 0:
            print("✗ Failed to install pytest-cov")
            return False
        print("✓ pytest-cov installed")
    
    return True

def main():
    """Main entry point"""
    print("=== mini_humanize Test Runner ===\n")
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Run tests
    print("\n=== Running Tests ===\n")
    test_cmd = f"{sys.executable} -m pytest tests/ -v --cov=mini_humanize --cov-report=term-missing"
    exit_code = run_command(test_cmd)
    
    print()
    if exit_code == 0:
        print("=== All Tests Passed! ===")
    else:
        print("=== Tests Failed ===")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
