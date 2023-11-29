from pathlib import Path
import re
import types
import dice


class TableLoader:
    def __init__(
        self, filepath: str, count=1, exclusive=False, clamp=False, dice_formula=None
    ):
        self.roll_config = types.SimpleNamespace()
        self.roll_config.count = count
        self.roll_config.exclusive = exclusive

        self.table = self.load_table(filepath or None)

        if not dice_formula:
            self.roll_config.formula = None
            return

        self.roll_config.formula = dice_formula
        self.roll_config.clamp = clamp
        self.check_formula_bounds()

    def table_length(self):
        return len(self.table)

    def check_formula_bounds(self):
        if self.roll_config.clamp:
            return

        roll_max = int(dice.roll_max(self.roll_config.formula))
        roll_min = int(dice.roll_min(self.roll_config.formula))
        if roll_max > self.table_length() or roll_min < 0:
            raise IndexError(
                f"""The supplied dice formula should not roll higher than the number of entries on the table or lower than 0.
Minimum formula value is {roll_min}, maximum formula value is {roll_max}, and table count is {len(self.table)}"""
            )

    def get_results(self):
        pass

    def load_table(self, table_path):
        pass

    def set_flag(self, name, value):
        if name == "exclusive":
            self.roll_config.exclusive = not not value
            return

        if name == "clamp":
            self.roll_config.clamp = not not value
            return

        if name == "formula":
            self.roll_config.formula = value
            if self.roll_config.formula:
                self.check_formula_bounds()
            return

        if name == "count":
            self.roll_config.count = int(value)
            return


def get_table_lines(table_path):
    if not Path(table_path).is_file():
        raise FileNotFoundError(f"Table file '{table_path}' not found.")

    with Path(table_path).open("r") as table_content:
        table_lines = table_content.readlines()
        return table_lines

    return []


def is_line_comment(line):
    return (
        not not re.match("^#", line)
        or not not re.match("^//", line)
        or not not re.match("^;", line)
    )
