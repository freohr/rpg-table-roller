#! python
import sys
import logging
import os.path
import argparse
from pathlib import Path


class table_roller:
    def __init__(self, table_filepath):
        with table_filepath.open("r") as table_file:
            table_content = table_file.read()
            self.table = [line for line in table_content.split("\n") if line]

    def get_table(self):
        return self.table


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


if __name__ == "__main__":
    table_filepath = get_parameters()
    table_roller = table_roller(table_filepath)
    print(table_roller.get_table())
