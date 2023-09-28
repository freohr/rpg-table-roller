from pathlib import Path
import random
import dice
import tableloader


class RandomTable(tableloader.TableLoader):
    def __init__(
        self, filepath: str, count=1, exclusive=False, clamp=False, dice_formula=None
    ):
        super().__init__(filepath, count, exclusive, clamp, dice_formula)

    def get_results(self):
        if self.roll_config.formula:
            return self.get_formula_result()

        if self.roll_config.exclusive:
            return self.get_exclusive_results()

        return self.get_random_results()

    def get_exclusive_results(self):
        return random.sample(self.table, k=min(self.roll_config.count, len(self.table)))

    def get_random_results(self):
        return random.choices(self.table, k=self.roll_config.count)

    def get_formula_result(self):
        rolled_indices = None

        if self.roll_config.clamp:
            rolled_indices = [
                clamp(
                    int(dice.roll(f"{self.roll_config.formula}")) - 1,
                    0,
                    len(self.table) - 1,
                )
                for i in range(self.roll_config.count)
            ]
            if self.roll_config.exclusive:
                rolled_indices = set(rolled_indices)
        else:
            rolled_indices = [
                int(dice.roll(f"{self.roll_config.formula}")) - 1
                for i in range(self.roll_config.count)
            ]

            if self.roll_config.exclusive:
                rolled_indices = set(rolled_indices)

        results = [self.table[index] for index in rolled_indices]

        return results

    def load_table(self, table_path):
        if not Path(table_path).is_file():
            raise FileNotFoundError(f"Table file '{table_path}' not found.")

        with Path(table_path).open("r") as table_file:
            table_content = table_file.readlines()
            table = [
                line.strip()
                for line in table_content
                if not tableloader.is_line_comment(line) and not line.strip() == ""
            ]
            return table


def clamp(value, min, max):
    return sorted((min, value, max))[1]
