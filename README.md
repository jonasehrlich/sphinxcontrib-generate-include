# sphinxcontrib-generate-include

## `generate-include` directive

This directive executes a Python function and includes its output in the documentation, parsed as
Markdown, reStructuredText, or literal text.

During execution of the

Usage in MyST Markdown:

````md
    ```{generate-include} path/to/file.py:function_name
    ```
````

Usage in reStructuredText:

```rst
.. generate-include:: path/to/file.py:function_name
```

Options:

- `type`: `md` | `rst` | `literal` (default: `md`)
  - `md`: Parse output as Markdown using MyST parser
  - `rst`: Parse output as reStructuredText
  - `literal`: Include output as preformatted literal block

## Markdown Generation

The module `sphinxcontrib.generate_include.mdlib` provides helpers for generating Markdown content
programmatically:

### Markdown Utility Functions

- `table(headers, rows, alignment="l")` Generates a Markdown table from headers, rows, and optional
  column alignment (left, right, center).

- `header(text, level=1)` Returns a Markdown header string of the specified level.

- `ordered_list(items)` Creates an ordered (numbered) Markdown list from a (possibly nested) list of
  strings.

- `unordered_list(items)` Creates an unordered (bulleted) Markdown list from a (possibly nested)
  list of strings.

- `link(url, text=None)` Returns a Markdown link. If `text` is not provided, the URL is used as the
  link text.

These functions simplify Markdown generation for documentation and content automation.
