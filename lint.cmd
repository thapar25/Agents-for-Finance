@echo off
REM Run Ruff format and check with fix on all files in the current directory

echo ============ Linting Process Started ============

ruff format .
ruff check . --fix