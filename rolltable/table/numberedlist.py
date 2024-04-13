from types import SimpleNamespace
import table.baseloader as table_loader
import random


class NumberedListTable(table_loader.BaseTableLoader):
    def __init__(
        self,
        table_data,
        count: str = "1",
        exclusive=False,
        clamp=False,
        dice_formula=None,
    ):
        super().__init__(table_data, count, exclusive, clamp, dice_formula)

    def load_table(self, table_data):
        results = table_loader.get_table_lines(table_data, strip_lines=True)

        table_items = []
        table_weights = []
        for line in results:
            if not line or table_loader.is_line_comment(line):
                continue

            line_weight, line_item = get_line_weight(line)
            table_weights.append(line_weight)
            table_items.append(line_item)

        table = SimpleNamespace()
        table.weights = table_weights
        table.items = table_items
        return table

    def get_results(self):
        count = self.get_rolled_count()

        if self.roll_config.exclusive:
            return random.sample(
                self.table.items,
                counts=self.table.weights,
                k=min(count, sum(self.table.weight)),
            )
        else:
            return random.choices(
                self.table.items,
                weights=self.table.weights,
                k=count,
            )

    def table_length(self):
        return sum(self.table.weights)


def get_line_weight(line):
    split_line = line.strip().split("\t")

    if len(split_line) != 2:
        raise ValueError(f"Invalid numbered list item '{line}'")

    line_number = split_line[0]
    line_numbers = line_number.split("-")

    if len(line_numbers) == 1:
        return 1, split_line[1]
    else:
        return int(line_numbers[1]) - int(line_numbers[1]) + 1, split_line[1]
