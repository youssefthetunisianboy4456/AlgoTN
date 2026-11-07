import sys

# This list holds the most recently exported tables.
all_tabs = []


def process_tables(tables):
    # Update the list when gui.py sends the saved tables.
    all_tabs[:] = tables

    # Print each table in the Python console.
    for tab in all_tabs:
        print(f"Table: {tab['name']}", file=sys.__stdout__)
        print(tab["data"], file=sys.__stdout__)