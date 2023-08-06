#! python
import sys
import logging
import os.path
import argparse
from pathlib import Path


def usage():
    print(f"Usage: {sys.argv[0]} <table-file>")
    print("This script loads the random table from the file")
    print("then roll a result from this table and prints it")


def get_parameters():
    parser = argparse.ArgumentParser(
        prog="RPG Random Table roller",
        description="""This program loads the random table from
                    a configuration file and rolls a random result from it""",
    )

    parser.add_argument("filename", help="path to random table config file")

    args = parser.parse_args()
    table_name = Path(args.filename)
    if not os.path.isfile(table_name):
        logging.error(f"File '{table_name}' not found.")
        usage()
        exit(2)

    return table_name


def load_table(table_filepath):
    with table_filepath.open("r") as table_file:
        table_content = table_file.read()
        return table_content


if __name__ == "__main__":
    table_name = get_parameters()
    table_content = load_table(table_name)
    print(table_content)
