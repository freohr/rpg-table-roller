from pathlib import Path
import json
import table.baseloader as table_loader
import table.hexflower.parser as Parser


class Hexflower(table_loader.BaseTableLoader):
    def __init__(self, filepath: str, count: str = "1", start=None):
        super().__init__(filepath, count)
        self.roll_config.start = start

    def get_results(self):
        count = self.get_rolled_count()

        if count < 1:
            return []

        start_index = (
            self.roll_config.start
            if self.roll_config.start
            else self.table.navigator.start
        )

        current_hex = self.table.get_hex(start_index)
        results = [str(current_hex)]

        for i in range(count - 1):
            current_hex = self.table.navigate(current_hex)
            results.append(str(current_hex))

        return results

    def load_table(self, table_path):
        if not Path(table_path).is_file():
            raise FileNotFoundError(f"Table file '{table_path}' not found.")

        with Path(table_path).open("r") as table_file:
            json_config = json.load(table_file)
            flower_config = Parser.parse_config(json_config)

            return flower_config
