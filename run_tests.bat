@echo off
REM run_tests - One-click test runner for mini_humanize
REM This script ensures dependencies are installed and runs the full test suite

setlocal enabledelayedexpansion

echo === mini_humanize Test Runner ===
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.10 or later.
    exit /b 1
)

python --version

REM Check if pytest is installed
python -c "import pytest" >nul 2>&1
if errorlevel 1 (
    echo Checking dependencies...
    echo pytest not found. Installing dependencies...
    python -m pip install --quiet pytest pytest-cov
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        exit /b 1
    )
    echo Dependencies installed
) else (
    echo Checking dependencies...
    echo pytest already installed
)

REM Check if pytest-cov is installed
python -c "import pytest_cov" >nul 2>&1
if errorlevel 1 (
    echo pytest-cov not found. Installing...
    python -m pip install --quiet pytest-cov
    if errorlevel 1 (
        echo Error: Failed to install pytest-cov
        exit /b 1
    )
    echo pytest-cov installed
) else (
    echo pytest-cov already installed
)

REM Run tests
echo.
echo === Running Tests ===
echo.

python -m pytest tests/ -v --cov=mini_humanize --cov-report=term-missing

if errorlevel 1 (
    echo.
    echo === Tests Failed ===
    exit /b 1
) else (
    echo.
    echo === All Tests Passed! ===
    exit /b 0
)
