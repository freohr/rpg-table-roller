import sys
import argparse
import __version__
import dice.exceptions
import loader
from pathlib import Path
from inliner.inliner import TableInliner
from natsort.natsort import natsorted


def main():
    try:
        args = get_parameters()

        if args.ext:
            extension = loader.get_absolute_file_path(args.table_filepath).suffix[1:]
            table = loader.load_table_from_extension(extension, args)
        else:
            table = loader.load_table_from_format(args.format, args)

        if args.table_filepath == "-":
            base_table_folder = Path().cwd()
        else:
            base_table_folder = loader.get_absolute_file_path(
                args.table_filepath
            ).parent

        recursive_table_inliner = TableInliner()

        raw_results = table.get_results()
        processed_results = process_inline_tables(
            raw_results, recursive_table_inliner, base_table_folder
        )

        if args.sort and isinstance(processed_results, list):
            processed_results = natsorted(processed_results)

        open_writing_device(processed_results, args.output, args.append, args.join)

    except dice.exceptions.DiceException as exc:
        print(f"Invalid dice formula: {str(exc)}")
        sys.exit(2)
    except Exception as exc:
        print(f"Error when processing arguments: {str(exc)}")
        sys.exit(1)


def process_inline_tables(results, inliner, base_folder):
    if isinstance(results, str):
        return inliner.roll_inline_tables(results, base_folder)
    else:
        return [
            process_inline_tables(result, inliner, base_folder) for result in results
        ]


def open_writing_device(result_array, output=None, append=False, joiner: str = ""):
    write_to = Path(output).open("a" if append else "w") if output else None

    print_results(result_array, joiner, write_to)

    if write_to:
        write_to.close()


def print_results(result_array, joiner: str, write_output=None):
    if not result_array:
        print("", file=write_output)
        return

    if type(result_array[0]) is list:
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
    input_group.add_argument(
        "table_filepath",
        help="Path to random table config file. Can be set to '-' to read the random table content from STDIN.",
    )
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
        - 'numbered-list': in a TSV list, each item is preceded by the values to roll to select this item, usually indicated by two numbers separated by a dash (e.g. '3-6	Potion of Healing')
        \n\n
        See the github repo (freohr/rpg-table-roller) for example table files of the supported formats.""",
        default="list",
        choices=[
            "list",
            "chance",
            "hexflower",
            "weighted-list",
            "template",
            "numbered-list",
        ],
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
    output_group.add_argument(
        "-s",
        "--sort",
        action="store_true",
        help="Sort the results lexicographically (for strings) and based on expected order (for numbers). No effect when only rolling a single result. See the python package `natsort` for details",
    )

    args = parser.parse_args()
    return args
