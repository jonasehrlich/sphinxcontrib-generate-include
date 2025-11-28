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
