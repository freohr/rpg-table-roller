from table.hexflower.direction import Direction
from table.hexflower.navigator import Navigator
from table.hexflower.hexagon import Hexagon
from typing import Dict


class Flower:
    def __init__(self, nav: Navigator, hex_list: Dict[int, Hexagon], desc: str):
        self.navigator = nav
        self.hex_list = hex_list
        self.description = desc
        pass

    def get_hex(self, hex_number: int) -> Hexagon:
        return self.hex_list[hex_number]

    def navigate(self, current_hex: Hexagon) -> Hexagon:
        next_direction = self.navigator.next_direction()
        return self.get_hex(current_hex.get_neighbour(next_direction))


def parse_navigator(dct: dict):
    json_formula = dct["formula"]
    json_start = dct["start"]
    json_navigation = dct["navigation"]
    navigation = {}
    for k, v in json_navigation.items():
        navigation[int(k)] = Direction[v]

    navigator = Navigator(json_formula, int(json_start), navigation)
    return navigator


def parse_hexagon(dct: dict):
    json_id = dct["id"]
    json_content = dct["content"]

    json_neighbours = dct["neighbours"]
    neighbours = {}
    for k, v in json_neighbours.items():
        neighbours[Direction[k]] = int(v)

    hexagon = Hexagon(int(json_id), json_content, neighbours)

    return hexagon


def parse_config(dct: dict):
    parsed_navigator = parse_navigator(dct["navigator"])

    # Parse hexes
    parsed_hexes = {}
    for parsed_hex in [parse_hexagon(hexa) for hexa in dct["hex-list"]]:
        parsed_hexes[parsed_hex.id] = parsed_hex

    extra_desc = f'{dct["comment"]["description"]}'
    description = f'{extra_desc}\n\nSource: {dct["comment"]["source"]}'
    hex_flower = Flower(parsed_navigator, parsed_hexes, description)

    return hex_flower
