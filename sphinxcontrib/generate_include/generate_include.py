from __future__ import annotations

import importlib.util
import sys
import traceback
from pathlib import Path
from typing import ClassVar

from docutils import nodes
from docutils.frontend import OptionParser
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from docutils.utils import new_document
from myst_parser.parsers.docutils_ import Parser as MystParser
from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import OptionSpec


class GenerateIncludeDirective(SphinxDirective):
    """Directive to execute a Python function and include its output."""

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False

    option_spec: ClassVar[OptionSpec] = {
        "type": lambda x: directives.choice(x, ("md", "rst", "literal")),
    }

    def run(self) -> list[nodes.Node]:  # pyrefly: ignore[bad-override]
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
            return self._error(f"Error executing {argument}: {exc} \n{traceback.format_exc()}")

        # Process the output based on the type
        if output_type == "literal":
            return self._create_literal_block(output)
        elif output_type == "rst":
            return self._parse_rst(output)
        else:  # md (default)
            return self._parse_markdown(output)

    def _execute_function(self, file_path: Path, function_name: str) -> str:
        """Load a Python file and execute the specified function.

        Uses importlib with proper cache invalidation to ensure fresh code
        is loaded on each execution. This is critical for sphinx-autobuild
        scenarios where files change while the Python process is running.
        """

        # Create a unique module name using timestamp to ensure fresh load
        # This bypasses Python's module caching by using a new name each time
        module_name = f"_generate_include_{file_path.stem}_{id(self)}"

        # Invalidate any cached bytecode
        importlib.invalidate_caches()

        # Load the module from the file path
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {file_path}")

        # Set submodule search locations for relative imports
        spec.submodule_search_locations = [str(file_path.parent)]
        module = importlib.util.module_from_spec(spec)

        # Add the file's directory to sys.path temporarily for relative imports
        file_dir = str(file_path.parent)
        original_path = sys.path.copy()
        if file_dir not in sys.path:
            sys.path.insert(0, file_dir)

        try:
            # Add module to sys.modules before loading for relative imports
            sys.modules[module_name] = module

            # Execute the module using the loader
            spec.loader.exec_module(module)

            # Get and call the function
            if not hasattr(module, function_name):
                raise AttributeError(f"Function '{function_name}' not found in {file_path}")

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

        # Create a new document for parsing
        parser = MystParser()
        option_parser = OptionParser(components=(MystParser,))
        settings = option_parser.get_default_values()

        # Copy relevant settings from the current document
        settings.env = self.env
        settings.myst_enable_extensions = getattr(self.config, "myst_enable_extensions", [])

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
