import logging
import random
import dice
import types
from pathlib import Path
import re


class TableRoller:
    def __init__(self, config):
        self.roll_config = types.SimpleNamespace()
        self.roll_config.count = config.count
        self.roll_config.exclusive = config.exclusive

        self.table = (
            parse_table_list(
                config.table_filepath) if config.table_filepath else None
        )

        if not config.dice_formula:
            self.roll_config.formula = None
            return
        else:
            self.roll_config.formula = f"{config.dice_formula}t"

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


def is_line_comment(line):
    return (
        not not re.match("^#", line)
        or not not re.match("^//", line)
        or not not re.match("^;", line)
    )


def parse_table_list(table_filepath):
    if not Path(table_filepath).is_file():
        logging.error(f"Table file '{table_filepath}' not found.")
        exit(2)

    with Path(table_filepath).open("r") as table_file:
        table_content = table_file.read()
        table = [
            line for line in table_content.split("\n") if not is_line_comment(line)
        ]
        return table
