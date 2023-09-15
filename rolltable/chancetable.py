import tableloader
from pathlib import Path
import dice


class ChanceTable(tableloader.TableLoader):
    def __init__(self, config):
        super().__init__(config)

    def load_table(self, table_path):
        if not Path(table_path).is_file():
            raise FileNotFoundError(f"File {table_path} does not exists")

        with Path(table_path).open("r") as table_file:
            table_content = table_file.read()

            loaded_table = [split_line(line)
                            for line in table_content.splitlines()]

        return loaded_table

    def get_results(self):
        dice_formula = self.roll_config.formula or "d100"

        results = [
            result
            for entry, chance in self.table
            if (result := roll_occurence(entry, dice_formula, chance))
        ]

        return results


def roll_occurence(name, formula, chance):
    return name if dice.roll(f"{formula}t") <= chance else None


def split_line(line):
    split = line.split("\t")
    return (split[0], int(split[1]))