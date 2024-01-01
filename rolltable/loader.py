from enum import Enum
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
    elif table_format == TableFormat.NumberedList:
        return NumberedListTable(
            args.table_filepath,
            args.count,
            args.exclusive,
            args.clamp,
            args.dice_formula,
        )

    raise ValueError(f"Unknown table format {table_format}")


def load_table_from_extenstion(extension, args):
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


def load_table_from_format(format, args):
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

    raise ValueError(f"Unknown table format option {format}")
