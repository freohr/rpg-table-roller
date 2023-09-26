import dice
import re


def insert_inline_dice_roll(string):
    formula_re = re.compile(r"\[\[(?P<formula>([-+*]?\d*d?\d+)+)]]")

    def roll_inline_dice(match):
        formula = match.group("formula")
        return f"{int(dice.roll(formula))}"

    return formula_re.sub(roll_inline_dice, string)
