"""Tests for error handling and recovery.

This is important for sphinx-autobuild where a user might save a file
with a syntax error, then fix it and save again.
"""

from __future__ import annotations

import time

import pytest


def test_syntax_error_in_source(tmp_python_file, directive):
    """Test handling of syntax errors in the source file."""
    file_path = tmp_python_file("""
        def generate(
            # Missing closing paren - syntax error
            return "test"
    """)

    with pytest.raises(SyntaxError):
        directive._execute_function(file_path, "generate")


def test_recovery_after_syntax_error(tmp_python_file, directive):
    """Test that we can recover after a syntax error is fixed."""
    file_path = tmp_python_file("""
        def generate(
            # Syntax error
            return "test"
    """)

    # First call fails
    with pytest.raises(SyntaxError):
        directive._execute_function(file_path, "generate")

    # Fix the file
    time.sleep(0.01)
    file_path.write_text("""
def generate():
    return "Fixed!"
""")

    # Second call should succeed
    result = directive._execute_function(file_path, "generate")
    assert result == "Fixed!"


def test_runtime_error_in_function(tmp_python_file, directive):
    """Test handling of runtime errors in the generator function."""
    file_path = tmp_python_file("""
        def generate():
            raise ValueError("Something went wrong!")
    """)

    with pytest.raises(ValueError, match="Something went wrong!"):
        directive._execute_function(file_path, "generate")


def test_recovery_after_runtime_error(tmp_python_file, directive):
    """Test recovery after a runtime error is fixed."""
    file_path = tmp_python_file("""
        def generate():
            raise RuntimeError("Temporary error")
    """)

    # First call fails
    with pytest.raises(RuntimeError):
        directive._execute_function(file_path, "generate")

    # Fix the file
    time.sleep(0.01)
    file_path.write_text("""
def generate():
    return "Now it works!"
""")

    # Second call should succeed
    result = directive._execute_function(file_path, "generate")
    assert result == "Now it works!"


def test_import_error_in_source(tmp_python_file, directive):
    """Test handling of import errors in the source file."""
    file_path = tmp_python_file("""
        import nonexistent_module_xyz

        def generate():
            return "test"
    """)

    with pytest.raises(ModuleNotFoundError):
        directive._execute_function(file_path, "generate")


def test_recovery_after_import_error(tmp_python_file, directive):
    """Test recovery after an import error is fixed."""
    file_path = tmp_python_file("""
        import nonexistent_module_xyz

        def generate():
            return "test"
    """)

    # First call fails
    with pytest.raises(ModuleNotFoundError):
        directive._execute_function(file_path, "generate")

    # Fix the file by removing the bad import
    time.sleep(0.01)
    file_path.write_text("""
import os  # Valid import

def generate():
    return f"Success! PID: {os.getpid()}"
""")

    # Second call should succeed
    result = directive._execute_function(file_path, "generate")
    assert "Success! PID:" in result


def test_error_in_module_level_code(tmp_python_file, directive):
    """Test handling of errors in module-level code (not in the function)."""
    file_path = tmp_python_file("""
        # This runs at module load time
        result = 1 / 0  # ZeroDivisionError

        def generate():
            return "test"
    """)

    with pytest.raises(ZeroDivisionError):
        directive._execute_function(file_path, "generate")


def test_alternating_error_and_success(tmp_python_file, directive):
    """Test alternating between error and success states."""
    file_path = tmp_python_file("""
        def generate():
            return "success1"
    """)

    # Start with success
    assert directive._execute_function(file_path, "generate") == "success1"

    # Introduce error
    time.sleep(0.01)
    file_path.write_text("""
def generate():
    raise ValueError("error1")
""")
    with pytest.raises(ValueError, match="error1"):
        directive._execute_function(file_path, "generate")

    # Fix
    time.sleep(0.01)
    file_path.write_text("""
def generate():
    return "success2"
""")
    assert directive._execute_function(file_path, "generate") == "success2"

    # Another error
    time.sleep(0.01)
    file_path.write_text("""
def generate():
    raise RuntimeError("error2")
""")
    with pytest.raises(RuntimeError, match="error2"):
        directive._execute_function(file_path, "generate")

    # Final fix
    time.sleep(0.01)
    file_path.write_text("""
def generate():
    return "success3"
""")
    assert directive._execute_function(file_path, "generate") == "success3"
