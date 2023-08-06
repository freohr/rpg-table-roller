#! python
import sys
import logging
import os.path


def usage():
    print(f"Usage: {sys.argv[0]} <table-file>")
    print("This script loads the random table from the file")
    print("then roll a result from this table and prints it")


def get_parameters():
    if len(sys.argv) < 2:
        logging.warning("Missing the expected the table file as argument.")
        usage()
        exit(1)

    table_name = sys.argv[1]
    if not os.path.isfile(table_name):
        logging.error(f"File '{table_name}' not found.")
        usage()
        exit(2)

    return table_name


if __name__ == "__main__":
    table_name = get_parameters()
    print(f"Found table from file '{table_name}'")
