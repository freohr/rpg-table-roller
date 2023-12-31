from table.hexflower.direction import Direction
import dice


class Navigator:
    formula = "2d6l"
    start = 0
    navigation = {
        0: Direction.self,
        1: Direction.bottom,
        2: Direction.bottom_left,
        3: Direction.bottom_right,
        4: Direction.top_left,
        5: Direction.top_right,
        6: Direction.top,
    }

    def __init__(self, formula: str, start: int, navigation: dict) -> None:
        self.formula = formula
        self.start = start
        self.navigation = navigation
        pass

    def next_direction(self) -> Direction:
        result = int(dice.roll(self.formula))
        direction = self.navigation.get(result)

        return direction if direction is not None else Direction.self
