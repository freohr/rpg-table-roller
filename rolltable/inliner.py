import dice
import re
from randomtable import RandomTable
from chancetable import ChanceTable
from weightedlisttable import WeightedListTable
from pathlib import Path


class InlineTableInfo:
    def __init__(
        self,
        canonical_path: Path,
        table_format=None,
        exclusive=False,
        clamp=False,
        formula=None,
        count=None,
        joiner=None,
    ):
        self.table_path = canonical_path
        self.format = table_format if table_format is not None else "list"
        self.exclusive = exclusive
        self.clamp = clamp
        self.formula = formula if formula is not None else ""
        self.count = int(count) if count is not None else 1
        self.joiner = joiner if joiner is not None else ", "

    def __eq__(self, other):
        return (
            self.table_path == other.table_path
            and self.format == other.format
            and self.exclusive == other.exclusive
            and self.clamp == other.clamp
            and self.formula == other.formula
        )

    def __hash__(self):
        return hash((self.table_path, self.formula, self.exclusive, self.clamp))


class TableReferenceCounter:
    def __init__(self):
        self.roll_count = 0
        self.indices = dict()

    def add_reference(self, index, count, joiner: str = None):
        self.roll_count = self.roll_count + count
        self.indices[index] = {
            "count": count,
            "joiner": joiner if joiner is not None else ", ",
        }


def create_table(table_info):
    if not table_info.format or table_info.format == "list":
        return RandomTable(table_info.table_path)
    elif table_info.format == "chance":
        return ChanceTable(table_info.table_path)
    elif table_info.format == "weighted-list":
        return WeightedListTable(table_info.table_path)
    else:
        raise ValueError(
            f"Unknown table format {table_info.format}"
            f"for inline table {table_info.table_path}"
        )


class TableInliner:
    def __init__(self):
        self.loaded_tables = dict()
        self.inline_element_re = re.compile(r"\[\[(?P<element>[^\[\]]+)]]")
        self.table_rolling_info_parser = re.compile(
            r"(?P<table_path>[^:]+)"
            r"("
            r"(?P<count>:c(?P<roll_count>\d+))|"
            r"(?P<clamp>:cl)|"
            r"(?P<formula>:d(?P<inline_formula>[^:]+))|"
            r"(?P<exclusive>:e)|"
            r"(?P<format>:f(?P<inline_format>list|chance|weighted))|"
            r"(?P<joiner>:j(?P<inline_joiner>[^:]+))"
            r")*"
        )
        pass

    def load_inlined_table(self, table_info: InlineTableInfo, count):
        if table_info.table_path not in self.loaded_tables:
            self.loaded_tables[table_info.table_path] = create_table(
                table_info)

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

    def insert_inline_dice_roll(self, string):
        def roll_inline_dice(match):
            formula = match.group("element")
            try:
                return f"{int(dice.roll(formula))}"
            except dice.DiceBaseException:
                return match.group(0)

        new_string = self.inline_element_re.sub(roll_inline_dice, string)
        return new_string

    def parse_inline_table_info(
        self, extracted_inlined_table, current_table_folder: Path
    ):
        parsed_info = self.table_rolling_info_parser.match(
            extracted_inlined_table)

        inline_table_path = (
            current_table_folder / parsed_info.group("table_path")
        ).resolve()

        return InlineTableInfo(
            inline_table_path,
            parsed_info.group("inline_format") if parsed_info.group(
                "format") else None,
            True if parsed_info.group("exclusive") else False,
            True if parsed_info.group("clamp") else False,
            parsed_info.group("inline_formula")
            if parsed_info.group("formula")
            else None,
            parsed_info.group("roll_count") if parsed_info.group(
                "count") else None,
            parsed_info.group("inline_joiner") if parsed_info.group(
                "joiner") else None,
        )

    def roll_inline_tables(self, rolled_result: str, current_table_folder: Path):
        inlined_elements = self.inline_element_re.findall(rolled_result)

        # Step 1: replace inline dice rolls
        if len(inlined_elements) == 0:
            return rolled_result
        else:
            rolled_result = self.insert_inline_dice_roll(rolled_result)
            inlined_elements = self.inline_element_re.findall(rolled_result)
            if len(inlined_elements) == 0:
                return rolled_result

        # Step 2: Load inlined tables info
        parsed_tables = dict()

        for index, result in enumerate(inlined_elements):
            table_info = self.parse_inline_table_info(
                result, current_table_folder)

            if table_info not in parsed_tables:
                parsed_tables[table_info] = TableReferenceCounter()

            table_ref_count = parsed_tables[table_info]
            table_ref_count.add_reference(
                index, table_info.count, table_info.joiner)

        # Step 3: Replace inlined tables reference with rolled results
        for table_info, ref_counter in parsed_tables.items():
            # Part 1: load the referenced table in cache and roll the needed results
            table = self.load_inlined_table(table_info, ref_counter.roll_count)
            results = table.get_results()

            # Part 2: Replace inline markers with results
            for index, replacer_info in ref_counter.indices.items():
                # Get as much results as needed to replace a single marker
                result_slicer = slice(0, replacer_info["count"])
                replacer_string = replacer_info["joiner"].join(
                    results[result_slicer])

                del results[result_slicer]

                # Recursively replace inlined tables
                while (
                    replaced_result := self.roll_inline_tables(
                        replacer_string, table_info.table_path.parent
                    )
                ) != replacer_string:
                    replacer_string = replaced_result

                # Replace the targeted marker with the new string
                rolled_result = rolled_result.replace(
                    f"[[{inlined_elements[index]}]]", replacer_string, 1
                )

        return rolled_result
