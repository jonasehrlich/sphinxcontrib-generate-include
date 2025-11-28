import importlib.metadata

from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata

from .generate_include import GenerateIncludeDirective

__version__ = importlib.metadata.version(__name__)


def setup(app: Sphinx) -> ExtensionMetadata:
    """Set up the Sphinx extension."""
    app.require_sphinx("7.0")

    app.add_directive("generate-include", GenerateIncludeDirective)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
