"""Tests for basic directive functionality."""

from __future__ import annotations

import pytest


def test_execute_simple_function(tmp_python_file, directive):
    """Test executing a simple function that returns a string."""
    file_path = tmp_python_file("""
        def generate():
            return "Hello, World!"
    """)

    result = directive._execute_function(file_path, "generate")
    assert result == "Hello, World!"


def test_execute_function_returning_none(tmp_python_file, directive):
    """Test executing a function that returns None."""
    file_path = tmp_python_file("""
        def generate():
            return None
    """)

    result = directive._execute_function(file_path, "generate")
    assert result == ""


def test_execute_function_returning_non_string(tmp_python_file, directive):
    """Test executing a function that returns a non-string (should be converted)."""
    file_path = tmp_python_file("""
        def generate():
            return 42
    """)

    result = directive._execute_function(file_path, "generate")
    assert result == "42"


def test_function_not_found(tmp_python_file, directive):
    """Test error when function doesn't exist."""
    file_path = tmp_python_file("""
        def other_function():
            return "test"
    """)

    with pytest.raises(AttributeError, match="Function 'generate' not found"):
        directive._execute_function(file_path, "generate")


def test_not_callable(tmp_python_file, directive):
    """Test error when the attribute is not callable."""
    file_path = tmp_python_file("""
        generate = "not a function"
    """)

    with pytest.raises(TypeError, match="'generate' is not callable"):
        directive._execute_function(file_path, "generate")
