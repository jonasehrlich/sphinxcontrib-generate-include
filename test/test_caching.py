"""Tests for caching and module reloading.

These are critical for sphinx-autobuild which keeps Python running
and needs fresh code on each rebuild.
"""

from __future__ import annotations

import sys
import time

import pytest

from sphinxcontrib.generate_include.generate_include import GenerateIncludeDirective


def test_module_reloading_on_file_change(tmp_python_file):
    """Test that changes to the source file are picked up on subsequent calls.

    Uses fresh directive instances to simulate separate sphinx build invocations.
    """
    file_path = tmp_python_file("""
        def generate():
            return "Version 1"
    """)

    # First call with fresh directive
    directive1 = object.__new__(GenerateIncludeDirective)
    result1 = directive1._execute_function(file_path, "generate")
    assert result1 == "Version 1"

    # Modify the file (ensure mtime changes)
    time.sleep(0.01)
    file_path.write_text("""
def generate():
    return "Version 2"
""")

    # Second call with fresh directive (simulates new sphinx build)
    directive2 = object.__new__(GenerateIncludeDirective)
    result2 = directive2._execute_function(file_path, "generate")
    assert result2 == "Version 2"


def test_module_isolation(tmp_python_file, directive):
    """Test that modules are properly isolated and don't leak between calls."""
    file1 = tmp_python_file(
        """
        GLOBAL_STATE = "file1"
        def generate():
            return GLOBAL_STATE
    """,
        filename="file1.py",
    )

    file2 = tmp_python_file(
        """
        GLOBAL_STATE = "file2"
        def generate():
            return GLOBAL_STATE
    """,
        filename="file2.py",
    )

    result1 = directive._execute_function(file1, "generate")
    result2 = directive._execute_function(file2, "generate")

    assert result1 == "file1"
    assert result2 == "file2"


def test_sys_modules_cleanup(tmp_python_file, directive):
    """Test that temporary modules are cleaned up from sys.modules."""
    file_path = tmp_python_file("""
        def generate():
            return "test"
    """)

    # Count modules before
    modules_before = set(sys.modules.keys())

    directive._execute_function(file_path, "generate")

    # Count modules after
    modules_after = set(sys.modules.keys())

    # No new _generate_include_ modules should remain
    new_modules = modules_after - modules_before
    generate_include_modules = [m for m in new_modules if "_generate_include_" in m]
    assert len(generate_include_modules) == 0


def test_sys_path_restoration(tmp_python_file, directive):
    """Test that sys.path is properly restored after execution."""
    file_path = tmp_python_file("""
        def generate():
            return "test"
    """)

    original_path = sys.path.copy()
    directive._execute_function(file_path, "generate")
    assert sys.path == original_path


def test_sys_path_restoration_on_error(tmp_python_file, directive):
    """Test that sys.path is restored even when execution raises an error."""

    file_path = tmp_python_file("""
        def generate():
            raise RuntimeError("Intentional error")
    """)

    original_path = sys.path.copy()

    with pytest.raises(RuntimeError):
        directive._execute_function(file_path, "generate")

    assert sys.path == original_path


def test_global_state_does_not_persist(tmp_python_file, directive):
    """Test that global state modifications don't persist between calls."""
    file_path = tmp_python_file("""
        counter = 0

        def generate():
            global counter
            counter += 1
            return f"Count: {counter}"
    """)

    result1 = directive._execute_function(file_path, "generate")
    result2 = directive._execute_function(file_path, "generate")

    # Both should return "Count: 1" because module is reloaded each time
    assert result1 == "Count: 1"
    assert result2 == "Count: 1"
