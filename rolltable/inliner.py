import dice
import re
from randomtable import RandomTable
from pathlib import Path


def insert_inline_dice_roll(string):
    formula_re = re.compile(r"\[\[(?P<formula>([-+*]?\d*d?\d+)+)]]")

    def roll_inline_dice(match):
        formula = match.group("formula")
        return f"{int(dice.roll(formula))}"

    return formula_re.sub(roll_inline_dice, string)


class InlineTableInfo:
    def __init__(self, path="", exclusive=False, clamp=False, formula="", count=1):
        self.table_path = path
        self.exclusive = exclusive
        self.clamp = clamp
        self.formula = formula
        pass

    def __eq__(self, other):
        return (
            self.table_path == other.table_path
            and self.exclusive == other.exclusive
            and self.clamp == other.clamp
            and self.formula == other.formula
        )

    def __hash__(self):
        return hash((self.table_path, self.formula, self.exclusive, self.clamp))


class TableReferenceCounter:
    def __init__(self):
        self.count = 0
        self.indices = []
        pass

    def add_reference(self, index):
        self.count = self.count + 1
        self.indices.append(index)
        pass


class TableInliner:
    def __init__(self, relative_base_path):
        self.relative_base_path = relative_base_path
        self.loaded_tables = dict()
        pass

    def load_inlined_table(self, table_info: InlineTableInfo, count):
        if table_info.table_path not in self.loaded_tables:
            path = None
            if Path(table_info.table_path).is_absolute():
                path = table_info.table_path
            else:
                path = Path(self.relative_base_path) / table_info.table_path

            self.loaded_tables[table_info.table_path] = RandomTable(path)

        table = self.loaded_tables[table_info.table_path]
        table.set_flag("exclusive", table_info.exclusive)
        table.set_flag("clamp", table_info.clamp)
        table.set_flag("formula", table_info.formula)
        table.set_flag("count", count)
        return table

    def reset_loaded_table(self, table_name):
        table = self.load_inlined_table(table_name)

        table.set_flag("clamp", False)
        table.set_flag("exclusive", False)
        table.set_flag("formula", "")
        table.set_flag("count", 1)

    @staticmethod
    def parse_inline_table_info(extracted_inlined_table):
        table_rolling_info = re.compile(
            r"\[\[(?P<table_path>[^:]+)(((?P<exclusive>:e)|(?P<clamp>:cl)|(?P<count>:c(?P<roll_count>\d+))|(?P<formula>:d(?P<inline_formula>[^:]+)))*)]]"
        )
        parsed_info = table_rolling_info.match(extracted_inlined_table)
        return InlineTableInfo(
            parsed_info.group("table_path"),
            True if parsed_info.group("exclusive") else False,
            True if parsed_info.group("clamp") else False,
            parsed_info.group("inline_formula")
            if parsed_info.group("formula")
            else None,
        )

    def roll_inline_tables(self, rolled_result):
        inline_extractor = re.compile(r"(\[\[[^\[]+]])")

        inlined_elements = inline_extractor.findall(rolled_result)

        if len(inlined_elements) == 0:
            return rolled_result
        else:
            rolled_result = insert_inline_dice_roll(rolled_result)
            inlined_elements = inline_extractor.findall(rolled_result)
            if len(inlined_elements) == 0:
                return rolled_result

        parsed_tables = dict()

        for index, result in enumerate(inlined_elements):
            table_info = self.parse_inline_table_info(result)

            if table_info not in parsed_tables:
                parsed_tables[table_info] = TableReferenceCounter()

            table_ref_count = parsed_tables[table_info]
            table_ref_count.add_reference(index)

        for table_info, ref_count in parsed_tables.items():
            table = self.load_inlined_table(table_info, ref_count.count)
            results = table.get_results()

            for index, result in enumerate(results):
                rolled_result = rolled_result.replace(
                    inlined_elements[ref_count.indices[index]], result, 1
                )

        while (
            replaced_string := self.roll_inline_tables(rolled_result)
        ) != rolled_result:
            rolled_result = replaced_string

        return rolled_result
