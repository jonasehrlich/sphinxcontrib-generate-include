"""Tests for edge cases and unusual scenarios."""

from __future__ import annotations

import textwrap
import time

from docutils import nodes

from sphinxcontrib.generate_include.generate_include import GenerateIncludeDirective


def test_unicode_content(tmp_python_file, directive):
    """Test handling of Unicode content."""
    file_path = tmp_python_file("""
        def generate():
            return "Hello, 世界! 🌍 Привет мир"
    """)

    result = directive._execute_function(file_path, "generate")
    assert result == "Hello, 世界! 🌍 Привет мир"


def test_multiline_content(tmp_python_file, directive):
    """Test handling of multiline content."""
    file_path = tmp_python_file('''
        def generate():
            return """# Header

        This is a paragraph.

        - Item 1
        - Item 2
        """
    ''')

    result = directive._execute_function(file_path, "generate")

    assert "# Header" in result
    assert "- Item 1" in result


def test_empty_content(tmp_python_file, directive):
    """Test handling of empty content."""
    file_path = tmp_python_file("""
        def generate():
            return ""
    """)

    result = directive._execute_function(file_path, "generate")
    assert result == ""


def test_argument_parsing_with_colon():
    """Test that colons are handled correctly in the argument parsing."""
    # The argument "file.py:function" should split on the last colon
    argument = "path/to/file.py:generate"
    file_path_str, function_name = argument.rsplit(":", 1)

    assert file_path_str == "path/to/file.py"
    assert function_name == "generate"


def test_file_path_with_special_characters(tmp_path, directive):
    """Test handling of file paths with spaces and special characters."""
    special_dir = tmp_path / "path with spaces"
    special_dir.mkdir()

    file_path = special_dir / "my-generator.py"
    file_path.write_text(
        textwrap.dedent("""
        def generate():
            return "Works!"
    """)
    )

    result = directive._execute_function(file_path, "generate")
    assert result == "Works!"


def test_multiple_functions_in_file(tmp_python_file, directive):
    """Test executing different functions from the same file."""
    file_path = tmp_python_file("""
        def generate_header():
            return "# Title"

        def generate_list():
            return "- Item 1\\n- Item 2"

        def generate_all():
            return generate_header() + "\\n\\n" + generate_list()
    """)

    result1 = directive._execute_function(file_path, "generate_header")
    result2 = directive._execute_function(file_path, "generate_list")
    result3 = directive._execute_function(file_path, "generate_all")

    assert result1 == "# Title"
    assert result2 == "- Item 1\n- Item 2"
    assert "# Title" in result3
    assert "- Item 1" in result3


def test_literal_output_type(directive):
    """Test literal output type creates a literal_block node."""
    result = directive._create_literal_block("Some code here")

    assert len(result) == 1
    assert isinstance(result[0], nodes.literal_block)
    assert result[0].astext() == "Some code here"


def test_relative_import_in_same_directory(tmp_path, directive):
    """Test that relative imports work for files in the same directory."""
    # Create a helper module
    (tmp_path / "helper.py").write_text(
        textwrap.dedent("""
        def get_message():
            return "Hello from helper!"
    """)
    )

    # Create the generator that imports the helper
    generator_file = tmp_path / "generator.py"
    generator_file.write_text(
        textwrap.dedent("""
        from helper import get_message

        def generate():
            return get_message()
    """)
    )

    result = directive._execute_function(generator_file, "generate")

    assert result == "Hello from helper!"


def test_many_rapid_file_changes(tmp_python_file):
    """Test that rapid file changes are all picked up correctly.

    Uses fresh directive instances to simulate separate sphinx build invocations.
    """
    file_path = tmp_python_file("""
        def generate():
            return "v0"
    """)

    for i in range(1, 6):
        time.sleep(0.01)  # Ensure mtime changes
        file_path.write_text(f"""
def generate():
    return "v{i}"
""")
        # Use fresh directive for each iteration
        directive = object.__new__(GenerateIncludeDirective)
        result = directive._execute_function(file_path, "generate")
        assert result == f"v{i}"
