# sphinxcontrib-generate-include

Sphinx extension to allow calling Python functions and including their output as Markdown,
ReStructuredText or literal in the Sphinx document.

## `generate-include` directive

This directive executes a Python function and includes its output in the documentation, parsed as
Markdown, reStructuredText, or literal text.

`````{tab-set-code}
   ````md
      ```{generate-include} path/to/file.py:function_name
      ```
   ````

   ````rst
   .. generate-include:: path/to/file.py:function_name
   ````
`````

Options:

- `type`: `md` | `rst` | `literal` (default: `md`)
  - `md`: Parse output as Markdown using MyST parser
  - `rst`: Parse output as reStructuredText
  - `literal`: Include output as preformatted literal block
