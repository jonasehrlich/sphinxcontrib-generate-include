"""
Sphinx extension: generate-include directive

This directive executes a Python function and includes its output
in the documentation, parsed as Markdown, reStructuredText, or literal text.

Usage in MyST Markdown:
    ```{generate-include} path/to/file.py:function_name
    ```

Usage in reStructuredText:
    .. generate-include:: path/to/file.py:function_name

Options:
    :type: md | rst | literal (default: md)
        - md: Parse output as Markdown using MyST parser
        - rst: Parse output as reStructuredText
        - literal: Include output as preformatted literal block
"""

from __future__ import annotations

import importlib.util
import sys
import traceback
from pathlib import Path
from typing import TYPE_CHECKING, Any

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from sphinx.util.docutils import SphinxDirective

if TYPE_CHECKING:
    from sphinx.application import Sphinx


class GenerateIncludeDirective(SphinxDirective):
    """Directive to execute a Python function and include its output."""

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False

    option_spec = {
        "type": lambda x: directives.choice(x, ("md", "rst", "literal")),
    }

    def run(self) -> list[nodes.Node]:
        """Execute the directive."""
        # Parse the argument: file.py:function_name
        argument = self.arguments[0]

        if ":" not in argument:
            return self._error(
                f"Invalid argument '{argument}'. Expected format: 'path/to/file.py:function_name'"
            )

        file_path_str, function_name = argument.rsplit(":", 1)

        # Get the output type (default: md)
        output_type = self.options.get("type", "md")

        # Resolve the file path relative to the source file
        source_dir = Path(self.env.srcdir)
        doc_dir = Path(self.env.doc2path(self.env.docname)).parent

        # Try relative to the current document first, then relative to source dir
        file_path = doc_dir / file_path_str
        if not file_path.exists():
            file_path = source_dir / file_path_str

        if not file_path.exists():
            return self._error(f"File not found: {file_path_str}")

        # Add the file as a dependency so Sphinx rebuilds when it changes
        self.env.note_dependency(str(file_path))

        # Check if the Python file has been modified since last build
        # and mark the current document for re-reading if needed
        file_mtime = file_path.stat().st_mtime
        dep_key = f"_generate_include_mtime_{file_path}"
        stored_mtime = getattr(self.env, dep_key, None)

        if stored_mtime != file_mtime:
            setattr(self.env, dep_key, file_mtime)

        # Execute the function and get the output
        try:
            output = self._execute_function(file_path, function_name)
        except Exception as exc:
            return self._error(
                f"Error executing {argument}: {exc} \n{traceback.format_exc()}"
            )

        # Process the output based on the type
        if output_type == "literal":
            return self._create_literal_block(output)
        elif output_type == "rst":
            return self._parse_rst(output)
        else:  # md (default)
            return self._parse_markdown(output)

    def _execute_function(self, file_path: Path, function_name: str) -> str:
        """Load a Python file and execute the specified function."""
        # Create a unique module name to avoid conflicts
        module_name = f"_generate_include_{file_path.stem}_{id(self)}"

        # Invalidate any cached bytecode to ensure we get fresh code
        # This is critical for sphinx-autobuild which keeps Python running
        importlib.invalidate_caches()

        # Load the module from the file path
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {file_path}")

        module = importlib.util.module_from_spec(spec)

        # Add the file's directory to sys.path temporarily for relative imports
        file_dir = str(file_path.parent)
        original_path = sys.path.copy()
        if file_dir not in sys.path:
            sys.path.insert(0, file_dir)

        try:
            # Execute the module
            spec.loader.exec_module(module)

            # Get and call the function
            if not hasattr(module, function_name):
                raise AttributeError(
                    f"Function '{function_name}' not found in {file_path}"
                )

            func = getattr(module, function_name)
            if not callable(func):
                raise TypeError(f"'{function_name}' is not callable")

            result = func()

            # Ensure the result is a string
            if result is None:
                return ""
            return str(result)

        finally:
            # Restore the original sys.path
            sys.path[:] = original_path
            # Clean up the module from sys.modules
            if module_name in sys.modules:
                del sys.modules[module_name]

    def _parse_rst(self, content: str) -> list[nodes.Node]:
        """Parse content as reStructuredText."""
        # Create a StringList from the content
        lines = content.split("\n")
        string_list = StringList(lines, source=self.env.docname)

        # Create a container node
        node = nodes.container()
        node.document = self.state.document

        # Parse the RST content
        self.state.nested_parse(string_list, self.content_offset, node)

        return node.children

    def _parse_markdown(self, content: str) -> list[nodes.Node]:
        """Parse content as Markdown using MyST parser."""
        try:
            from myst_parser.parsers.docutils_ import Parser as MystParser
        except ImportError:
            # Fallback: try to parse as RST if MyST is not available
            self._warning("MyST parser not available, falling back to RST parsing")
            return self._parse_rst(content)

        # Use the MyST parser to convert markdown to docutils nodes
        from docutils.frontend import OptionParser
        from docutils.utils import new_document

        # Create a new document for parsing
        parser = MystParser()
        option_parser = OptionParser(components=(MystParser,))
        settings = option_parser.get_default_values()

        # Copy relevant settings from the current document
        settings.env = self.env
        settings.myst_enable_extensions = getattr(
            self.config, "myst_enable_extensions", []
        )

        doc = new_document("<generate-include>", settings=settings)
        parser.parse(content, doc)

        # Return all children except the document node itself
        return list(doc.children)

    def _create_literal_block(self, content: str) -> list[nodes.Node]:
        """Create a literal block node."""
        literal = nodes.literal_block(content, content)
        literal["language"] = "text"
        return [literal]

    def _error(self, message: str) -> list[nodes.Node]:
        """Create an error node."""
        error = self.state.document.reporter.error(
            message,
            nodes.literal_block(self.block_text, self.block_text),
            line=self.lineno,
        )
        return [error]

    def _warning(self, message: str) -> None:
        """Log a warning."""
        self.state.document.reporter.warning(
            message,
            line=self.lineno,
        )


def setup(app: Sphinx) -> dict[str, Any]:
    """Set up the Sphinx extension."""
    app.add_directive("generate-include", GenerateIncludeDirective)

    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
