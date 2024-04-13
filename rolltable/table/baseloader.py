from pathlib import Path
import re
import types
import dice


class BaseTableLoader:
    def __init__(
        self,
        table_data,
        count: str = "1",
        exclusive=False,
        clamp=False,
        dice_formula=None,
    ):
        self.roll_config = types.SimpleNamespace()
        self.roll_config.count = count
        self.roll_config.exclusive = exclusive
        self.table = self.load_table(table_data)

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
                f"""The supplied dice formula should not roll higher than the number of entries on the table or lower 
                than 0. Minimum formula value is {roll_min}, maximum formula value is {roll_max}, and table count is 
                {len(self.table)}"""
            )

    def get_rolled_count(self):
        return int(dice.roll(self.roll_config.count))

    def get_results(self):
        return []

    def load_table(self, table_data: str):
        return []

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
            self.roll_config.count = f"{value}"
            return


def get_table_lines(table_data: str, strip_lines: bool = True):
    return [line.strip() if strip_lines else line for line in table_data.split("\n")]


def is_line_comment(line):
    return (
        not not re.match("^#", line)
        or not not re.match("^//", line)
        or not not re.match("^;", line)
    )
