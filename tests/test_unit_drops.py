import pytest

from mechabellum_replay_parser import UnitDrop


@pytest.mark.parametrize(
    "round_number,drop_identifier,expected",
    [
        (4, 1042216, UnitDrop(2, 2, "phoenix", 4)),        # - 2 lvl 2 phoenix
        (6, 106124, UnitDrop(1, 2, "melting point", 6)),   # - 1 lvl 2 melter
        (6, 106227, UnitDrop(2, 2, "mustang", 6)),         # - 2 lvl 2 mustang
        (9, 109262, UnitDrop(2, 6, "marksmen", 9)),        # - 2 lvl 6 marksmen
        (9, 1093220, UnitDrop(3, 2, "fire badger", 9)),    # - 3 lvl 2 fire badgers
        (4, 1042213, UnitDrop(2, 2, "sledgehammer", 4)),   # - 2 lvl 2 sledgehammers
        (4, 104225, UnitDrop(2, 2, "rhino", 4)),           # - 2 lvl 2 rhinos
        (7, 1071223, UnitDrop(1, 2, "sandworm", 7)),       # - 1 lvl 2 sandworm
        (10, 1102218, UnitDrop(2, 2, "wraith", 10)),       # - 2 lvl 2 wraith
        (10, 1103216, UnitDrop(3, 2, "phoenix", 10)),      # - 3 lvl 2 phoenix
    ])
def test_unit_drops(round_number: int, drop_identifier: int, expected: UnitDrop):
    actual = UnitDrop.from_round_number_and_identifier(round_number, drop_identifier)
    assert actual == expected