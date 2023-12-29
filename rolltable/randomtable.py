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
        count = self.get_rolled_count()

        if self.roll_config.formula:
            return self.get_formula_result(count)

        if self.roll_config.exclusive:
            return self.get_exclusive_results(count)

        return self.get_random_results(count)

    def get_exclusive_results(self, count: int):
        return random.sample(self.table, k=min(count, len(self.table)))

    def get_random_results(self, count: int):
        return random.choices(self.table, k=count)

    def get_formula_result(self, count: int):
        if self.roll_config.clamp:
            rolled_indices = [
                clamp(
                    int(dice.roll(f"{self.roll_config.formula}")) - 1,
                    0,
                    len(self.table) - 1,
                )
                for _ in range(count)
            ]
            if self.roll_config.exclusive:
                rolled_indices = set(rolled_indices)
        else:
            rolled_indices = [
                int(dice.roll(f"{self.roll_config.formula}")) - 1
                for _ in range(count)
            ]

            if self.roll_config.exclusive:
                rolled_indices = set(rolled_indices)

        results = [self.table[index] for index in rolled_indices]

        return results

    def load_table(self, table_path):
        table_content = tableloader.get_table_lines(table_path)
        table = [
            line.strip()
            for line in table_content
            if not tableloader.is_line_comment(line) and not line.strip() == ""
        ]
        return table


def clamp(value, min, max):
    return sorted((min, value, max))[1]
