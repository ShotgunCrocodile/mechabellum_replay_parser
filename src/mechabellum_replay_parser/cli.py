import argparse

from . import parse_battle_record
from . import battle_record_to_string


def main():
    parser = argparse.ArgumentParser(description="Parse a Mechabellum replay file (.grbr).")
    parser.add_argument("file", help="Path to the Mechabellum replay file (.grbr).")
    args = parser.parse_args()

    battle_record = parse_battle_record(args.file)
    table = battle_record_to_string(battle_record)
    print(table)


if __name__ == "__main__":
    main()
