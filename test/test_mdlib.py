from sphinxcontrib.generate_include import mdlib
from pytest_subtests import SubTests


def test_table(subtests: SubTests):
    # Data always stays the same for these tests because formatting does not depend on it
    table_rows = [
        ["Alice", "30", "New York"],
        ["Bob", "25", "Los Angeles"],
        ["Charlie", "35", "Chicago"],
    ]

    for headers, expected_headers in [
        (
            ["Name", "Age", "City"],
            (
                "| Name | Age | City |",
                "| :--- | :-: | ---: |",
            ),
        ),
        (
            ["a", "b", "c"],
            (
                "| a | b | c |",
                "| :- | :-: | -: |",
            ),
        ),
    ]:
        with subtests.test(headers=headers):
            expected = (
                f"\n"
                f"{'\n'.join(expected_headers)}\n"
                f"| Alice | 30 | New York |\n"
                f"| Bob | 25 | Los Angeles |\n"
                f"| Charlie | 35 | Chicago |\n"
            )
            result = mdlib.table(headers, table_rows, alignment=["l", "c", "r"])
            assert result == expected


def test_ordered_list():
    items = [
        "Item 1",
        [
            "Subitem 1.1",
            "Subitem 1.2",
            [
                "Subsubitem 1.2.1",
                "Subsubitem 1.2.2",
            ],
        ],
        "Item 2",
    ]
    expected = (
        "1. Item 1\n"
        "   1. Subitem 1.1\n"
        "   1. Subitem 1.2\n"
        "      1. Subsubitem 1.2.1\n"
        "      1. Subsubitem 1.2.2\n"
        "1. Item 2"
    )
    result = mdlib.ordered_list(items)
    assert result == expected


def test_unordered_list():
    items = [
        "Item 1",
        [
            "Subitem 1.1",
            "Subitem 1.2",
            [
                "Subsubitem 1.2.1",
                "Subsubitem 1.2.2",
            ],
        ],
        "Item 2",
    ]
    expected = (
        "- Item 1\n"
        "  - Subitem 1.1\n"
        "  - Subitem 1.2\n"
        "    - Subsubitem 1.2.1\n"
        "    - Subsubitem 1.2.2\n"
        "- Item 2"
    )
    result = mdlib.unordered_list(
        items,
    )
    assert result == expected


def test_header():
    assert mdlib.header("Title") == "# Title"
    assert mdlib.header("Subtitle", level=2) == "## Subtitle"
    assert mdlib.header("Subsubtitle", level=3) == "### Subsubtitle"
    assert mdlib.header("Title", -1) == "# Title"
