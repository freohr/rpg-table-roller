import dice
import re
import loader
from table.numberedlist import NumberedListTable
from table.random import RandomTable
from table.chance import ChanceTable
from table.weightedlist import WeightedListTable
from table.template import OutputTemplate
from pathlib import Path
from natsort import natsorted


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
        format_from_extension=False,
        sort=False,
    ):
        self.table_path = canonical_path

        if format_from_extension:
            ext = canonical_path.suffix[1:].replace("_", "-")
            if ext == "table":
                ext = "list"

            if ext == "num-list":
                ext = "numbered-list"

            self.format = ext
        else:
            self.format = table_format if table_format is not None else "list"

        self.exclusive = exclusive
        self.clamp = clamp
        self.formula = formula if formula is not None else ""
        self.count = int(dice.roll(count)) if count is not None else 1
        self.joiner = joiner if joiner is not None else ", "
        self.sort = sort

    def __eq__(self, other):
        return (
            self.table_path == other.table_path
            and self.format == other.format
            and self.exclusive == other.exclusive
            and self.clamp == other.clamp
            and self.formula == other.formula
        )

    def __hash__(self):
        return hash(
            (self.table_path, self.format, self.formula, self.exclusive, self.clamp)
        )


class TableReferenceCounter:
    def __init__(self):
        self.roll_count = 0
        self.indices = dict()

    def add_reference(self, index, count: int, joiner=None):
        self.roll_count = self.roll_count + count
        self.indices[index] = {
            "count": count,
            "joiner": joiner if joiner is not None else ", ",
        }


def create_table(table_info):
    table_data = loader.read_table_file(table_info.table_path)

    if not table_info.format or table_info.format == "list":
        return RandomTable(table_data)
    elif table_info.format == "chance":
        return ChanceTable(table_data)
    elif table_info.format == "weighted-list":
        return WeightedListTable(table_data)
    elif table_info.format == "template":
        return OutputTemplate(table_data, table_info.count)
    elif table_info.format == "numbered-list":
        return NumberedListTable(table_data)
    else:
        raise ValueError(
            f"Unknown table format {table_info.format}"
            f"for inline table {table_info.table_path}"
        )


class TableInliner:
    inline_element_option_parser = re.compile(
        r"(?P<element>[^:]+)"
        r"("
        r"(?P<count>:c(?P<roll_count>[^:]+))|"
        r"(?P<clamp>:cl)|"
        r"(?P<formula>:d(?P<inline_formula>[^:]+))|"
        r"(?P<exclusive>:e)|"
        r"(?P<format>:f(?P<inline_format>list|chance|weighted-list))|"
        r"(?P<joiner>:j(?P<inline_joiner>[^:]+))|"
        r"(?P<extension>:x)|"
        r"(?P<sort>:s)"
        r")*"
    )

    inline_element_re = re.compile(r"\[\[(?P<element>[^\[\]]+)]]")

    def __init__(self):
        self.loaded_tables = dict()

    def load_inlined_table(self, table_info: InlineTableInfo, count=1):
        if table_info.table_path not in self.loaded_tables:
            self.loaded_tables[table_info.table_path] = create_table(table_info)

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
    def insert_inline_dice_roll(string):
        def roll_inline_dice(match):
            element = match.group("element")
            if element is None:
                return match.group(0)

            formula_options = TableInliner.inline_element_option_parser.match(element)
            if formula_options is None:
                return match.group(0)

            try:
                base_roll = formula_options.group("element")

                count_formula = (
                    formula_options.group("roll_count")
                    if formula_options.group("count")
                    else "1"
                )
                count = int(dice.roll(count_formula))

                joiner = (
                    formula_options.group("inline_joiner")
                    if formula_options.group("joiner")
                    else ", "
                )

                sort = formula_options.group("sort") is not None

                rolls = [f"{int(dice.roll(base_roll))}" for _ in range(count)]

                if sort:
                    rolls = natsorted(rolls)

                return joiner.join(rolls)
            except dice.DiceBaseException:
                return match.group(0)

        new_string = TableInliner.inline_element_re.sub(roll_inline_dice, string)
        return new_string

    @staticmethod
    def parse_inline_table_info(extracted_inlined_table, current_table_folder: Path):
        parsed_info = TableInliner.inline_element_option_parser.match(
            extracted_inlined_table
        )

        if parsed_info is None:
            raise ValueError(
                f"Invalid inline table format: '{extracted_inlined_table}'"
            )

        inline_table_path = loader.get_absolute_file_path(
            parsed_info.group("element"), current_table_folder
        )

        return InlineTableInfo(
            inline_table_path,
            parsed_info.group("inline_format") if parsed_info.group("format") else None,
            parsed_info.group("exclusive") is not None,
            parsed_info.group("clamp") is not None,
            (
                parsed_info.group("inline_formula")
                if parsed_info.group("formula")
                else None
            ),
            parsed_info.group("roll_count") if parsed_info.group("count") else None,
            parsed_info.group("inline_joiner") if parsed_info.group("joiner") else None,
            parsed_info.group("extension") is not None,
            parsed_info.group("sort") is not None,
        )

    def roll_inline_tables(self, rolled_result: str, current_table_folder: Path):
        inlined_elements = TableInliner.inline_element_re.findall(rolled_result)

        # Step 1: replace inline dice rolls
        if len(inlined_elements) == 0:
            return rolled_result

        rolled_result = self.insert_inline_dice_roll(rolled_result)
        inlined_elements = TableInliner.inline_element_re.findall(rolled_result)
        if len(inlined_elements) == 0:
            return rolled_result

        # Step 2: Load inlined tables info
        parsed_tables = dict()

        for index, result in enumerate(inlined_elements):
            table_info = self.parse_inline_table_info(result, current_table_folder)

            if table_info not in parsed_tables:
                parsed_tables[table_info] = TableReferenceCounter()

            table_ref_count = parsed_tables[table_info]
            table_ref_count.add_reference(index, table_info.count, table_info.joiner)

        # Step 3: Replace inlined tables reference with rolled results
        for table_info, ref_counter in parsed_tables.items():
            # Part 1: load the referenced table in cache and roll the needed results
            table = self.load_inlined_table(table_info, ref_counter.roll_count)
            results = table.get_results()

            if table_info.sort:
                results = natsorted(results)

            # Part 2: Replace inline markers with results
            for index, replacer_info in ref_counter.indices.items():
                # Get as many results as needed to replace a single marker
                result_slicer = slice(0, replacer_info["count"])
                replacer_string = replacer_info["joiner"].join(results[result_slicer])

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
