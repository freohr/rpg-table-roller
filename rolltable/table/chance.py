import dice
import table.baseloader as table_loader


class ChanceTable(table_loader.BaseTableLoader):
    def __init__(
        self, filepath: str, count=1, exclusive=False, clamp=False, dice_formula=None
    ):
        super().__init__(filepath, count, exclusive, clamp, dice_formula)

    def load_table(self, table_path):
        return table_loader.get_table_lines(table_path)

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


def roll_occurrence(name, formula, chance):
    return name if dice.roll(f"{formula}t") <= chance else None


def split_line(line):
    split = line.split("\t")
    return split[0], int(split[1])
