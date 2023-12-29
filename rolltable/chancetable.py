import tableloader
from pathlib import Path
import dice


class ChanceTable(tableloader.TableLoader):
    def __init__(
        self, filepath: str, count=1, exclusive=False, clamp=False, dice_formula=None
    ):
        super().__init__(filepath, count, exclusive, clamp, dice_formula)

    def load_table(self, table_path):
        if not Path(table_path).is_file():
            raise FileNotFoundError(f"File {table_path} does not exists")

        with Path(table_path).open("r") as table_file:
            table_content = table_file.read()

            loaded_table = [split_line(line) for line in table_content.splitlines()]

        return loaded_table

    def get_results(self):
        dice_formula = self.roll_config.formula or "d100"
        count = self.get_rolled_count()

        results = [
            [
                result
                for entry, chance in self.table
                if (result := roll_occurrence(entry, dice_formula, chance))
            ]
            for _ in range(count)
        ]

        return results


def roll_occurence(name, formula, chance):
    return name if dice.roll(f"{formula}t") <= chance else None


def split_line(line):
    split = line.split("\t")
    return (split[0], int(split[1]))
