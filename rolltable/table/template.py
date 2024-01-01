import table.baseloader as table_loader


class OutputTemplate(table_loader.BaseTableLoader):
    def __init__(self, table_data):
        super().__init__(table_data)

    def load_table(self, table_path):
        return table_loader.get_table_lines(table_path)

    def get_results(self):
        return self.table
