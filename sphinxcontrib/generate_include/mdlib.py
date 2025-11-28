import collections.abc
from typing import Literal, cast

import jinja2

MDTABLE_TEMPLATE = jinja2.Template("""
| {{ headers | join(" | ")}} |
| {{ header_aligns | join(" | ")}} |
{%- for row in rows %}
| {{ row | join(" | ")}} |
{%- endfor %}

""")


type Alignment = Literal["l", "r", "c"]
Row = collections.abc.Sequence[str]


def _table_column_alignment_specifier(align: Alignment, header: str) -> str:
    """Create the alignment specifier for a column in a markdown table.

    :param align: Alignment specifier ("l", "r", "c")
    :param header: Header text (used to determine length)
    :raises ValueError: If an invalid alignment specifier is provided
    :return: Alignment line for the markdown table
    """
    if align == "l":
        return ":" + "-" * max(len(header) - 1, 1)
    elif align == "r":
        return "-" * max(len(header) - 1, 1) + ":"
    elif align == "c":
        return ":" + "-" * max(len(header) - 2, 1) + ":"
    else:
        raise ValueError(f"Invalid alignment specifier: {align}")


def table(
    headers: Row,
    rows: collections.abc.Iterable[Row],
    alignment: Alignment | collections.abc.Sequence[Alignment] = "l",
) -> str:
    """
    Generates a Markdown table from the given headers, rows, and alignment specifications.

    :param headers: A sequence representing the table headers
    :param rows: An iterable of rows, where each row is a sequence of cell values
    :param alignment: Specifies column alignment. Can be a single alignment value applied to all
                      columns, or a sequence of alignment values per column. Defaults to "l"
                      (left alignment).
    :return: The rendered Markdown table as a string.
    """
    alignment_line: list[str] = []
    alignment_per_header: list[Alignment] = (
        cast(list[Alignment], [alignment] * len(headers))
        if isinstance(alignment, str)
        else list(alignment)
    )

    alignment_line = [
        _table_column_alignment_specifier(cast(Alignment, col_align), header)
        for header, col_align in zip(headers, alignment_per_header, strict=True)
    ]

    return MDTABLE_TEMPLATE.render(headers=headers, rows=rows, header_aligns=alignment_line)


def header(text: str, level: int = 1) -> str:
    """Create a Markdown header.

    :param text: Header text
    :param level: Header level, defaults to 1
    :return: Markdown header string
    """
    level = max(1, level)
    return f"{'#' * level} {text}"


type NestedList[T] = T | list[NestedList[T]]


def _mdlist(
    items: NestedList[str],
    ordered: bool,
    level: int = 0,
) -> list[str]:
    """Create a Markdown list.

    :param items: List of items (strings or nested lists)
    :param ordered: Whether the list is ordered, defaults to False
    :return: Markdown list string
    """
    md_list = []
    prefix = "1. " if ordered else "- "
    indent = " " * (level * len(prefix))

    for item in items:
        if isinstance(item, str):
            md_list.append(f"{indent}{prefix}{item}")
        else:
            md_list.extend(_mdlist(items=item, ordered=ordered, level=level + 1))
    return md_list


def ordered_list(items: NestedList[str]) -> str:
    """Create an ordered Markdown list.

    :param items: List of items (strings or nested lists)
    :return: Markdown ordered list string
    """
    return "\n".join(_mdlist(items, ordered=True))


def unordered_list(items: NestedList[str]) -> str:
    """Create an unordered Markdown list.

    :param items: List of items (strings or nested lists)
    :return: Markdown unordered list string
    """
    return "\n".join(_mdlist(items, ordered=False))


def link(url: str, text: str | None = None) -> str:
    """Create a Markdown link.

    :param url: URL for the link
    :param text: Link text, defaults to None (uses URL as text)
    :return: Markdown link string
    """
    if text is None:
        text = url
    return f"[{text}]({url})"
