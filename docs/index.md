# sphinxcontrib-generate-include

Sphinx extension to allow calling Python functions and including their output as Markdown,
ReStructuredText or literal in the Sphinx document.

## `generate-include` directive

This directive executes a Python function from a file and includes its output in the documentation,
parsed as Markdown, reStructuredText, or literal text.

`````{tab-set-code}
   ````md
      ```{generate-include} path/to/file.py:function_name
      ```
   ````

   ````rst
   .. generate-include:: path/to/file.py:function_name
   ````
`````

### Options

- `type`: `md` | `rst` | `literal` (default: `md`)
  - `md`: Parse output as Markdown using MyST parser
  - `rst`: Parse output as reStructuredText
  - `literal`: Include output as preformatted literal block

### Example

Assuming the following *estimation.py* file:

```{literalinclude} ./estimation.py
---
linenos:
---
```

As mentioned above it can be included like this:

`````{tab-set-code}
   ````md
      ```{generate-include} estimation.py:data_table
      ```
   ````

   ````rst
   .. generate-include:: estimation.py:data_table
   ````
`````

And it will then create a table like this:

```{generate-include} estimation.py:data_table
```
