#! python
import os
import sys
import argparse
from pathlib import Path
from tablehandler import TableRoller


def main():
    args = get_parameters()
    try:
        table_roller = TableRoller(args)
    except Exception as exc:
        print(exc)
        exit(1)
    else:
        print_results(table_roller.get_result(), args.output, args.append)


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
        prog="rolltable",
        description="""This program loads the random table from
                    a configuration file and rolls a random result from it""",
    )

    input_group = parser.add_argument_group("Input Options")
    input_group.add_argument(
        "table_filepath", help="path to random table config file")
    input_group.add_argument(
        "-f",
        "--format",
        help="""Format for the table file content.
        Options are:
        - 'list' [default] (contains each item as a straight simple list with comments)\n
        \n\n
        See the github repo (freohr/rpg-table-roller) for example table files of the supported formats.""",
        default="list",
        choices=["list"],
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
        "-d",
        "--dice-formula",
        help="""Custom dice formula to roll on the table.
                Keep it simple (XdY±Z)""",
    )
    roll_group.add_argument(
        "--clamp",
        help="Force roll result between first and last element. No effect if not using a custom formula.",
        action="store_true",
    )

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

    args = parser.parse_args()
    return args
