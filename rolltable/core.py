#! python
import sys
import argparse
from pathlib import Path
from randomtable import RandomTable
from chancetable import ChanceTable
from hexflower.hexflower import Hexflower
from inliner import TableInliner
from weightedlisttable import WeightedListTable
from outtemplate import OutputTemplate
import __version__
from enum import Enum


class TableFormat(Enum):
    List = 1
    Chance = 2
    Hexflower = 3
    Weighted_list = 4
    Template = 5


def load_table(table_format: TableFormat, args):
    if table_format == TableFormat.List:
        return RandomTable(
            args.table_filepath,
            args.count,
            args.exclusive,
            args.clamp,
            args.dice_formula,
        )
    elif table_format == TableFormat.Chance:
        return ChanceTable(
            args.table_filepath,
            args.count,
            args.exclusive,
            args.clamp,
            args.dice_formula,
        )
    elif table_format == TableFormat.Weighted_list:
        return WeightedListTable(
            args.table_filepath,
            args.count,
            args.exclusive,
            args.clamp,
            args.dice_formula,
        )
    elif table_format == TableFormat.Hexflower:
        return Hexflower(args.table_filepath, args.count, args.start)
    elif table_format == TableFormat.Template:
        return OutputTemplate(args.table_filepath)

    raise ValueError("Unknown table format")


def main():
    args = get_parameters()
    table = None

    try:
        if args.ext:
            extension = Path(args.table_filepath).suffix[1:]

            if extension == "table" or extension == "list":
                table = load_table(TableFormat.List, args)
            elif extension == "chance":
                table = load_table(TableFormat.Chance, args)
            elif extension == "weighted_list":
                table = load_table(TableFormat.Weighted_list, args)
            elif extension == "hexflower":
                table = load_table(TableFormat.Hexflower, args)
            elif extension == "template":
                table = load_table(TableFormat.Template, args)
        elif args.format == "list":
            table = load_table(TableFormat.List, args)
        elif args.format == "chance":
            table = load_table(TableFormat.Chance, args)
        elif args.format == "hexflower":
            table = load_table(TableFormat.Hexflower, args)
        elif args.format == "weighted-list":
            table = load_table(TableFormat.Weighted_list, args)
        elif args.format == "template":
            table = load_table(TableFormat.Template, args)

        if table is None:
            raise ValueError("Unknown table format")
    except Exception as exc:
        print(exc)
        exit(1)
    else:
        if table:
            base_table_folder = Path(args.table_filepath).parent.resolve()

            recursive_table_inliner = TableInliner()

            raw_results = table.get_results()
            processed_results = process_inline_tables(
                raw_results, recursive_table_inliner, base_table_folder
            )

            open_writing_device(processed_results, args.output, args.append, args.join)
        else:
            exit(1)


def process_inline_tables(results, inliner, base_folder):
    if isinstance(results, str):
        return inliner.roll_inline_tables(results, base_folder)
    else:
        return [
            process_inline_tables(result, inliner, base_folder) for result in results
        ]


def open_writing_device(result_array, output=None, append=False, joiner: str = None):
    write_to = Path(output).open("a" if append else "w") if output else None

    print_results(result_array, joiner, write_to)

    if write_to:
        write_to.close()


def print_results(result_array, joiner: str = None, write_output=None):
    if not result_array:
        print("", file=write_output)
        return

    if isinstance(result_array[0], list):
        for result in result_array:
            print_results(result, joiner, write_output)
        return

    if joiner:
        printed_string = joiner.join(result_array)
        print(printed_string, file=write_output)
    else:
        for result in result_array:
            print(result, file=write_output)


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

    parser.add_argument(
        "-v", "--version", action="version", version=__version__.__version__
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
        - 'hexflower': the table is represented as a hexflower, and result navigation is done step by step. See https://goblinshenchman.wordpress.com/hex-power-flower/ for a detailled explanation\n
        - 'weighted-list': in a TSV list, each item is preceded by a weight indicating the chance to be selected. Does not support custom dice formulae for now\n
        - 'template': the file is not a random table, but should simply be printed to the output with the inline rolls processed. Useful if you want to format rolling on multiple tables at once.
        \n\n
        See the github repo (freohr/rpg-table-roller) for example table files of the supported formats.""",
        default="list",
        choices=["list", "chance", "hexflower", "weighted-list", "template"],
    )

    input_group.add_argument(
        "-x",
        "--ext",
        action="store_true",
        help="Get table format from file extension. See `--format` for the list of accepted formats",
    )

    roll_group = parser.add_argument_group("Roll Options")
    roll_group.add_argument(
        "-c",
        "--count",
        type=str,
        default="1",
        dest="count",
        help="""How many rolled results do you want from the table?
                (defaults to 1 result). Can be a number or a dice formula""",
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
                Keep it simple (XdY±Z). See the python `dice` package for additional notation format""",
    )
    roll_group.add_argument(
        "--clamp",
        help="Force roll result between first and last element. No effect if not using a custom formula.",
        action="store_true",
    )

    hexflower_group = parser.add_argument_group("Hex-flower Options")
    hexflower_group.add_argument(
        "-s",
        "--start",
        type=int,
        help="Change the hex number that navigation starts from",
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
                    file. No effect when printing to STDOUT""",
    )
    output_group.add_argument(
        "-j",
        "--join",
        type=str,
        help="Join the result as a single line string in the output with the provided string. Useful when rolling multiple times on the same chance table, as the results will be aggregated for each set of rolls on the provided table.",
    )

    args = parser.parse_args()
    return args
