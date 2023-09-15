from pathlib import Path
import random
import dice
import tableloader


class RandomTable(tableloader.TableLoader):
    def __init__(self, config):
        super().__init__(config)

    def get_default_result(self):
        if self.roll_config.exclusive:
            return random.sample(
                self.table, k=min(self.roll_config.count, len(self.table))
            )
        else:
            return random.choices(self.table, k=self.roll_config.count)

    def get_formula_result(self):
        results = [
            self.table[
                clamp(dice.roll(f"{self.roll_config.formula}t"),
                      0, len(self.table) - 2)
                if self.roll_config.clamp
                else dice.roll(f"{self.roll_config.formula}t") - 1
            ]
            for _ in range(self.roll_config.count)
        ]

        return results

    def get_results(self):
        if self.roll_config.formula:
            return self.get_formula_result()
        else:
            return self.get_default_result()

    def load_table(self, table_path):
        if not Path(table_path).is_file():
            raise FileNotFoundError(f"Table file '{table_path}' not found.")

        with Path(table_path).open("r") as table_file:
            table_content = table_file.read()
            table = [
                line
                for line in table_content.split("\n")
                if not tableloader.is_line_comment(line) and not line == ""
            ]
            return table


def clamp(value, min, max):
    return sorted((min, value, max))[1]
