#! python
import sys
import logging
import os.path
import argparse
from pathlib import Path
import random

LOCAL_ARGS = None


class table_roller:
    def __init__(self, table_filepath):
        with Path(table_filepath).open("r") as table_file:
            table_content = table_file.read()
            self.table = [line for line in table_content.split("\n") if line]

    def get_table(self):
        return self.table

    def roll_result(self):
        if LOCAL_ARGS.exclusive:
            return random.sample(self.table, k=min(LOCAL_ARGS.count, len(self.table)))
        else:
            return random.choices(self.table, k=LOCAL_ARGS.count)


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

    parser.add_argument(
        "table_filepath", help="path to random table config file")

    roll_group = parser.add_argument_group("Roll Options")
    roll_group.add_argument(
        "-c",
        "--count",
        type=int,
        default=1,
        dest="count",
        help="How many rolled results do you want from the table? (defaults to 1 result)",
    )
    roll_group.add_argument(
        "-e",
        "--exclusive",
        action="store_true",
        help="Each result can be rolled at most once",
    )

    global LOCAL_ARGS
    LOCAL_ARGS = parser.parse_args()

    if not os.path.isfile(LOCAL_ARGS.table_filepath):
        logging.error(f"File '{LOCAL_ARGS.table_file}' not found.")
        usage()
        exit(2)


def print_results(result_array):
    [print(result) for result in result_array]


if __name__ == "__main__":
    get_parameters()
    table_roller = table_roller(LOCAL_ARGS.table_filepath)
    print_results(table_roller.roll_result())
