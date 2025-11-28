from sphinxcontrib.generate_include import mdlib


def data_table():
    return mdlib.table(
        ["Name", "Age", "City"],
        [
            ["Alice", "30", "New York"],
            ["Bob", "25", "Los Angeles"],
            ["Charlie", "35", "Chicago"],
        ],
        alignment=["l", "r", "c"],
    )
