#! python
import sys
import argparse
from pathlib import Path
from randomtable import RandomTable
from chancetable import ChanceTable
from inliner import TableInliner


def main():
    args = get_parameters()
    table = None

    try:
        if args.format == "list":
            table = RandomTable(
                args.table_filepath,
                args.count,
                args.exclusive,
                args.clamp,
                args.dice_formula,
            )
        elif args.format == "chance":
            table = ChanceTable(
                args.table_filepath,
                args.count,
                args.exclusive,
                args.clamp,
                args.dice_formula,
            )
    except Exception as exc:
        print(exc)
        exit(1)
    else:
        if table:
            base_table_folder = Path(args.table_filepath).parent

            recursive_table_inliner = TableInliner(base_table_folder)

            processed_results = [
                recursive_table_inliner.roll_inline_tables(result)
                for result in table.get_results()
            ]

            print_results(processed_results, args.output, args.append)
        else:
            exit(1)


def print_results(result_array, output=None, append=False):
    write_to = Path(output).open("a" if append else "w") if output else None

    for result in result_array:
        print(result, file=write_to)

    if write_to:
        write_to.close()


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
    input_group.add_argument("table_filepath", help="path to random table config file")
    input_group.add_argument(
        "-f",
        "--format",
        help="""Format for the table file content.
        Options are:
        - 'list' [default]: contains each item as a straight simple list with comments\n
        - 'chance':  each item has a chance to appears in the results, usually as a percentage\n
        \n\n
        See the github repo (freohr/rpg-table-roller) for example table files of the supported formats.""",
        default="list",
        choices=["list", "chance"],
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
