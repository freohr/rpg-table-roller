import tableloader


class OutputTemplate(tableloader.TableLoader):
    def __init__(self, filepath: str):
        super().__init__(filepath)

    def load_table(self, table_path):
        return tableloader.get_table_lines(table_path)

    def get_results(self):
        return self.table
