#! python
import sys
import logging
import os.path
import argparse


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
    table_name = args.filename
    if not os.path.isfile(table_name):
        logging.error(f"File '{table_name}' not found.")
        usage()
        exit(2)

    return table_name


if __name__ == "__main__":
    table_name = get_parameters()
    print(f"Found table from file '{table_name}'")
