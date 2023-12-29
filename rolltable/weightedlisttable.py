import tableloader
import random
from types import SimpleNamespace


class WeightedListTable(tableloader.TableLoader):
    def __init__(
        self, filepath: str, count=1, exclusive=False, clamp=False, dice_formula=None
    ):
        super().__init__(filepath, count, exclusive, clamp, dice_formula)

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
        table_content = tableloader.get_table_lines(table_path)

        table_items = []
        table_weight = []
        for index, line in enumerate(table_content):
            split_line = line.strip().split("\t")

            if len(split_line) == 0 or not split_line[0]:
                continue

            potential_weight = split_line[0]

            if len(split_line) == 1:
                if potential_weight.isdecimal():
                    table_weight.append(int(potential_weight))
                    table_items.append('')
                else:
                    table_items.append(split_line[0])
                    table_weight.append(1)
            elif split_line[0].isdecimal():
                table_weight.append(int(split_line[0]))
                table_items.append(" ".join(split_line[1:]))

        table = SimpleNamespace()
        table.weights = table_weight
        table.items = table_items
        return table
