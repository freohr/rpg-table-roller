from pathlib import Path
import table.baseloader as table_loader
import dice


class OutputTemplate(table_loader.BaseTableLoader):
    def __init__(self, table_data, count="1"):
        super().__init__(table_data, count)

    def load_table(self, table_path):
        with Path(table_path).open("r") as table:
            return [table.read()]

    def get_results(self):
        print_count = int(dice.roll(self.roll_config.count))

        return [line for line in self.table for _ in range(print_count)]
