"""Shared fixtures for generate-include tests."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from sphinxcontrib.generate_include.generate_include import GenerateIncludeDirective


@pytest.fixture
def tmp_python_file(tmp_path: Path):
    """Create a temporary Python file with a generator function."""

    def _create_file(content: str, filename: str = "generator.py") -> Path:
        file_path = tmp_path / filename
        file_path.write_text(textwrap.dedent(content))
        return file_path

    return _create_file


@pytest.fixture
def directive():
    """Create a GenerateIncludeDirective instance for testing _execute_function."""
    # Create a minimal instance - _execute_function doesn't use most directive attributes
    return object.__new__(GenerateIncludeDirective)
