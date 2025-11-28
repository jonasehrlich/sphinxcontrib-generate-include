"""Tests for the setup function and directive registration."""

from __future__ import annotations

from unittest import mock

from sphinxcontrib import generate_include


class MockSphinx:
    def __init__(self):
        self.registered_directives = {}

    def add_directive(self, name, directive_class):
        self.registered_directives[name] = directive_class

    def require_sphinx(self, version):
        pass


def test_setup_returns_metadata():
    """Test that setup returns proper extension metadata."""

    app = mock.Mock()
    result = generate_include.setup(app)

    assert isinstance(result, dict)
    assert "version" in result
    assert "parallel_read_safe" in result
    assert "parallel_write_safe" in result


def test_setup_registers_directive():
    """Test that setup registers the generate-include directive."""

    app = mock.Mock()
    generate_include.setup(app)

    app.add_directive.assert_called_once_with(
        "generate-include",
        generate_include.GenerateIncludeDirective,
    )


def test_setup_version_is_string():
    """Test that the version is a valid string."""

    app = mock.Mock()
    result = generate_include.setup(app)

    assert result.get("version") == generate_include.__version__


def test_parallel_safety_flags():
    """Test that parallel safety flags are set correctly."""

    app = mock.Mock()
    result = generate_include.setup(app)

    # The directive should be safe for parallel reading and writing
    # since each invocation uses a unique module name
    assert isinstance(result.get("parallel_read_safe"), bool)
    assert isinstance(result.get("parallel_write_safe"), bool)
