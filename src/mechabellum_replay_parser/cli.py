import argparse
from pathlib import Path

from prettytable import PrettyTable

from . import parse_battle_record
from . import battle_record_to_string


def show_battle_record(args):
    battle_record = parse_battle_record(Path(args.file).absolute())
    table = battle_record_to_string(battle_record)
    print(table)


def show_tech(args):
    battle_record = parse_battle_record(Path(args.file).absolute())
    for player in battle_record.player_records:
        print(player.name)
        table = PrettyTable()
        table.align = "l"
        table.field_names = ["Unit", "Techs"]
        for unit, techs in player.tech_choices.items():
            table.add_row([unit, "\n".join(techs)])
            table.add_divider()
        print(table)
        print()


def main():
    parser = argparse.ArgumentParser(description="Mechabellum replay file parser")
    subparsers = parser.add_subparsers(dest="command")

    battle_parser = subparsers.add_parser(
        "battle", help="Parse a Mechabellum replay file (.grbr)"
    )
    battle_parser.add_argument(
        "file", help="Path to the Mechabellum replay file (.grbr)"
    )
    battle_parser.set_defaults(func=show_battle_record)

    tech_parser = subparsers.add_parser(
        "tech", help="Show tech information of both players in a replay file."
    )
    tech_parser.add_argument("file", help="Path to the Mechabellum replay file (.grbr)")
    tech_parser.set_defaults(func=show_tech)

    args = parser.parse_args()

    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
