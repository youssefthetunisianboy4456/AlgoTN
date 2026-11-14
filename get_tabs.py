import sys

all_tabs = []


def process_tables(tables):
    all_tabs[:] = tables

    for tab in all_tabs:
        print(f"Table: {tab['name']}", file=sys.__stdout__)
        print(tab["data"], file=sys.__stdout__)