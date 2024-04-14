import sys
from enum import Enum
from pathlib import Path
from table.numberedlist import NumberedListTable
from table.chance import ChanceTable
from table.random import RandomTable
from table.template import OutputTemplate
from table.hexflower.hexflower import Hexflower
from table.weightedlist import WeightedListTable


class TableFormat(Enum):
    List = 1
    Chance = 2
    Hexflower = 3
    Weighted_list = 4
    Template = 5
    NumberedList = 6


def load_table(table_format: TableFormat, args):
    table_data = read_table_file(args.table_filepath)

    if table_format == TableFormat.List:
        return RandomTable(
            table_data,
            args.count,
            args.exclusive,
            args.clamp,
            args.dice_formula,
        )
    elif table_format == TableFormat.Chance:
        return ChanceTable(
            table_data,
            args.count,
            args.exclusive,
            args.clamp,
            args.dice_formula,
        )
    elif table_format == TableFormat.Weighted_list:
        return WeightedListTable(
            table_data,
            args.count,
            args.exclusive,
            args.clamp,
            args.dice_formula,
        )
    elif table_format == TableFormat.Hexflower:
        return Hexflower(table_data, args.count, args.start)
    elif table_format == TableFormat.Template:
        return OutputTemplate(table_data, args.count)
    elif table_format == TableFormat.NumberedList:
        return NumberedListTable(
            table_data,
            args.count,
            args.exclusive,
            args.clamp,
            args.dice_formula,
        )

    raise ValueError(f"Unknown table format {table_format}")


def read_table_file(table_path):
    if table_path == "-":
        return "\n".join([line.rstrip("\n") for line in sys.stdin.readlines()])

    if type(table_path) is str:
        table_file = get_absolute_file_path(table_path)
    else:
        table_file = table_path

    if not table_file.is_file():
        raise FileNotFoundError(f"Table file '{table_path}' not found.")

    with table_file.open("r") as table_content:
        table_lines = table_content.readlines()
        return "".join(table_lines)


def get_absolute_file_path(path_str: str, relative_to: Path = None):
    if path_str.find("~") == 0:
        return Path(path_str).expanduser()
    elif path_str.find("/") == 0:
        return Path(path_str).resolve()
    elif relative_to:
        return (relative_to / path_str).resolve()
    else:
        return Path(path_str).resolve()


def load_table_from_extension(extension, args):
    if extension == "table" or extension == "list":
        return load_table(TableFormat.List, args)
    elif extension == "chance":
        return load_table(TableFormat.Chance, args)
    elif extension == "weighted_list":
        return load_table(TableFormat.Weighted_list, args)
    elif extension == "hexflower":
        return load_table(TableFormat.Hexflower, args)
    elif extension == "template":
        return load_table(TableFormat.Template, args)
    elif extension == "num_list":
        return load_table(TableFormat.NumberedList, args)

    raise ValueError(f"Unknown table file extension {extension}")


def load_table_from_format(table_format, args):
    if args.format == "list":
        return load_table(TableFormat.List, args)
    elif args.format == "chance":
        return load_table(TableFormat.Chance, args)
    elif args.format == "hexflower":
        return load_table(TableFormat.Hexflower, args)
    elif args.format == "weighted-list":
        return load_table(TableFormat.Weighted_list, args)
    elif args.format == "template":
        return load_table(TableFormat.Template, args)
    elif args.format == "numbered-list":
        return load_table(TableFormat.NumberedList, args)

    raise ValueError(f"Unknown table format option {table_format}")


def load_table_from_stdin(table_format, table_data, args):
    if args.format == "list":
        return load_table(TableFormat.List, args)
    elif args.format == "chance":
        return load_table(TableFormat.Chance, args)
    elif args.format == "hexflower":
        return load_table(TableFormat.Hexflower, args)
    elif args.format == "weighted-list":
        return load_table(TableFormat.Weighted_list, args)
    elif args.format == "template":
        return load_table(TableFormat.Template, args)
    elif args.format == "numbered-list":
        return load_table(TableFormat.NumberedList, args)

    raise ValueError(f"Unknown table format option {table_format}")
