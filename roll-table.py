#! python
import sys
import logging
import os.path
import argparse
from pathlib import Path
import random
import dice
import types


class TableRoller:
    def __init__(self, config):
        with Path(config.table_filepath).open("r") as table_file:
            table_content = table_file.read()
            self.table = [line for line in table_content.split("\n") if line]

            self.roll_config = types.SimpleNamespace()
            self.roll_config.count = config.count
            self.roll_config.exclusive = config.exclusive

            if not config.formula:
                self.roll_config.formula = None
                return
            else:
                self.roll_config.formula = f"{config.formula}t"

            if (
                dice.roll_max(self.roll_config.formula) > len(self.table)
                or dice.roll_min(self.roll_config.formula) < 0
            ):
                raise IndexError(
                    """The supplied dice formula should not roll higher than the number of entries on the table or lower than 0"""
                )

    def get_default_result(self):
        if self.roll_config.exclusive:
            return random.sample(
                self.table, k=min(self.roll_config.count, len(self.table))
            )
        else:
            return random.choices(self.table, k=self.roll_config.count)

    def get_formula_result(self):
        results = [
            self.table[dice.roll(self.roll_config.formula) - 1]
            for _ in range(self.roll_config.count)
        ]
        return results

    def get_result(self):
        if self.roll_config.formula:
            return self.get_formula_result()
        else:
            return self.get_default_result()


def print_results(result_array, output, append):
    if output:
        output_action = "a" if append else "w"
        with Path(output).open(output_action) as output:
            [print(result, file=output) for result in result_array]
    else:
        [print(result) for result in result_array]


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

    parser.add_argument("table_filepath", help="path to random table config file")

    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "-o",
        "--output",
        help="""Text file to output the rolled results.
                Note: Contents will be overwritten.""",
    )
    output_group.add_argument(
        "-a",
        "--append",
        action="store_true",
        help="""Append the rolled results to the output
                file. No effect when printing to STD""",
    )

    roll_group = parser.add_argument_group("Roll Options")
    roll_group.add_argument(
        "-c",
        "--count",
        type=int,
        default=1,
        dest="count",
        help="""How many rolled results do you want from the table?
                (defaults to 1 result)""",
    )
    roll_group.add_argument(
        "-e",
        "--exclusive",
        action="store_true",
        help="Each result can be rolled at most once",
    )
    roll_group.add_argument(
        "-f",
        "--formula",
        help="""Custom dice formula to roll on the table.
                Keep it simple for now (XdY±Z)""",
    )

    args = parser.parse_args()

    if not os.path.isfile(args.table_filepath):
        logging.error(f"File '{args.table_filepath}' not found.")
        usage()
        exit(2)

    return args


if __name__ == "__main__":
    args = get_parameters()
    table_roller = TableRoller(args)
    print_results(table_roller.get_result(), args.output, args.append)
