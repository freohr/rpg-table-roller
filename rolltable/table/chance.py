import dice
import table.baseloader as table_loader


class ChanceTable(table_loader.BaseTableLoader):
    def __init__(
        self, table_data, count=1, exclusive=False, clamp=False, dice_formula=None
    ):
        super().__init__(table_data, count, exclusive, clamp, dice_formula)

    def load_table(self, table_data: str):
        lines = table_loader.get_table_lines(table_data, strip_lines=True)

        entries = []

        for line in lines:
            if not line or table_loader.is_line_comment(line):
                continue

            entries.append(get_line_chance(line))

        return entries

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


def get_line_chance(line):
    split = line.split("\t")

    if len(split) != 2:
        raise ValueError(f"Invalid chance format for item '{line}'")

    return split[0], int(split[1])
