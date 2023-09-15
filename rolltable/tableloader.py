import re
import types
import dice


class TableLoader:
    def __init__(self, config):
        self.roll_config = types.SimpleNamespace()
        self.roll_config.count = config.count
        self.roll_config.exclusive = config.exclusive

        self.table = self.load_table(config.table_filepath or None)

        if not config.dice_formula:
            self.roll_config.formula = None
            return
        else:
            self.roll_config.formula = config.dice_formula

        self.roll_config.clamp = config.clamp

        if not self.roll_config.clamp:
            roll_max = dice.roll_max(self.roll_config.formula)
            roll_min = dice.roll_min(self.roll_config.formula)
            if roll_max > len(self.table) or roll_min < 0:
                raise IndexError(
                    f"""The supplied dice formula should not roll higher than the number of entries on the table or lower than 0.
Formula min is {roll_min}, formula max is {roll_max}, and table count is {len(self.table)}"""
                )
        pass

    def get_results(self):
        pass

    def load_table(self, able_path):
        pass


def is_line_comment(line):
    return (
        not not re.match("^#", line)
        or not not re.match("^//", line)
        or not not re.match("^;", line)
    )
