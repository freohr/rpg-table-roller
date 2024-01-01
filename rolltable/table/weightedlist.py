import random
from types import SimpleNamespace
import table.baseloader as table_loader


class WeightedListTable(table_loader.BaseTableLoader):
    def __init__(
        self, table_data, count=1, exclusive=False, clamp=False, dice_formula=None
    ):
        super().__init__(table_data, count, exclusive, clamp, dice_formula)

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

    def load_table(self, table_path):
        table_content = table_loader.get_table_lines(table_path)

        table_items = []
        table_weights = []
        for line in table_content:
            split_line = line.strip().split("\t")

            if len(split_line) == 0 or not split_line[0]:
                continue

            potential_weight = split_line[0]

            if len(split_line) == 1:
                if potential_weight.isdecimal():
                    table_weights.append(int(potential_weight))
                    table_items.append("")
                else:
                    table_items.append(split_line[0])
                    table_weights.append(1)
            elif split_line[0].isdecimal():
                table_weights.append(int(split_line[0]))
                table_items.append(" ".join(split_line[1:]))

        table = SimpleNamespace()
        table.weights = table_weights
        table.items = table_items
        return table
