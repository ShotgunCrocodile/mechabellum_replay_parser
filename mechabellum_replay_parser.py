import xml.etree.ElementTree
import xml.etree.ElementTree as ET
import argparse
from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict
from prettytable import PrettyTable, ALL


COMMAND_TOWER_SKILLS = {
    1: "Loan",
    3: "Mass Recruit",
    4: "Elite Recruit",
    5: "Enhanced Range",
    6: "High Mobility",
}


RESEARCH_TOWER_SKILLS = {
    1: "Oil Bomb",
    2: "Field Recovery",
    3: "Mobile Beacon",
    4: "Attack Enhancement",
    5: "Defence Enhancement",
}


OFFICER_LOOKUP = {
    10014: "Training Specialist",
    20032: "Elite Specialist",
    10002: "Supply Specialist",
    20029: "Marksman Specialist",
    20039: "Typhoon Specialist",
    10013: "Amplify Specialist",
    20036: "Sabertooth Specialist",
    20037: "Farseer Specialist",
    20021: "Aerial Specialist",
}


CONTRAPTION_LOOKUP = {
    30001: "Missile Interceptor",
    20001: "Sentry Missile",
    10001: "Shield Generator",
}


UNIT_LOOKUP = {
    1: "fortress",
    2: "marksmen",
    3: "vulcan",
    4: "melting point",
    5: "rhino",
    6: "wasp",
    7: "mustang",
    8: "steel ball",
    9: "fang",
    10: "crawler",
    11: "overlord",
    12: "stormcaller",
    13: "sledgehammer",
    14: "hacker",
    15: "arclight",
    16: "phoenix",
    17: "warfactory",
    18: "wraith",
    19: "scorpion",
    20: "fire badger",
    21: "sabertooth",
    22: "typhoon",
    23: "sandworm",
    24: "tarantula",
    25: "phantom ray",
    26: "farseer",
    27: "raiden",
}


TECH_LOOKUP = {
    # Wasp
    10206: "Range",
    406: "High Explosive Ammo",
    3206: "Aerial Specialization",
    206: "Energy Shield",
    506: "Ground Specialization",

    # Arclight
    10215: "Range",
    10915: "Charged shot",
    3115: "Anti-Aircraft Ammunition",

    # Scorpion
    10219: "Range",

    # Overlord
    180311: "Photon Emission",

    # Rhino
    3005: "Armor",

    # Fortress
    1105: "Anti Air Barrage",
    1001: "Barrier",

    # Mustang
    10207: "Range",
    3207: "Aerial Specialization",
    3307: "Missile Interceptor",

    # Steel ball
    1308: "Mechanical Division",

    # Sabertooth
    3321: "Missile interceptor",

    # Marksmen
    10202: "Range",

    # Melting Point
    10204: "Range",
    1107: "Energy Diffraction",

    # Stormcaller
    10212: "Range",
    812: "Incendiary Bomb",
    1812: "Electromagnetic Explosion",

    # Crawler
    10710: "Impact Drill",
    10510: "Mechanical Rage",
    2610: "Subterranean Blitz",

    # Fang
    10209: "Range",
    10509: "Mechanical Rage",

    # Tarantula
    924: "Field Maintenance",
    11024: "Spider Mines",
    10224: "Range",

    # Typhoon
    1022: "Barrier",

    # Farseer
    180526: "Scanning Radar",
    1826: "Electromagnetic Explosion",

    # Raiden
    10227: "Range",
    4027: "Chain",
}


@dataclass
class BuyAction:
    unit: str

    def __repr__(self) -> str:
        return f"Buy {self.unit}"

    @classmethod
    def from_xml(cls, action_element: xml.etree.ElementTree.Element):
        return cls(unit=UNIT_LOOKUP.get(int(action_element.find("UID").text)))


@dataclass
class UnlockAction:
    unit: str

    def __repr__(self) -> str:
        return f"Unlock {self.unit}"

    @classmethod
    def from_xml(cls, action_element: xml.etree.ElementTree.Element):
        return cls(unit=UNIT_LOOKUP.get(int(action_element.find("UID").text)))


@dataclass
class DeviceAction:
    device: str

    def __repr__(self) -> str:
        return f"Device {self.device}"

    @classmethod
    def from_xml(cls, action_element: xml.etree.ElementTree.Element):
        return cls(device=CONTRAPTION_LOOKUP.get(int(action_element.find("ContraptionID").text)))


@dataclass
class TechAction:
    unit: str
    tech: str

    def __repr__(self) -> str:
        return f"Tech {self.unit} {self.tech}"

    @classmethod
    def from_xml(cls, action_element: xml.etree.ElementTree.Element):
        tech_id = int(action_element.find("TechID").text)
        tech_name = TECH_LOOKUP.get(tech_id, tech_id)
        return cls(
            unit=UNIT_LOOKUP.get(int(action_element.find("UID").text)),
            tech=tech_name,
        )


@dataclass
class UpgradeAction:
    unit: str

    def __repr__(self) -> str:
        return f"Upgrade {self.unit}"

    @classmethod
    def from_xml(cls, action_element: xml.etree.ElementTree.Element, units: dict[int, str]):
        # TODO: Bug here: sometimes the upgraded unit is not in the list for some reason.
        # typically its out of bounds by 1 past the last unit. Buying and selling may shift
        # the unit data and I am not accounting for that. Upgrades done at the beginning of a turn
        # seem to always be correct.
        # This might not be entirely simulatable since we don't know what unit drops contained without
        # looking ahead to the next round.
        unit_id = int(action_element.find("UIDX").text)
        return cls(
            unit=units.get(unit_id, unit_id),
        )


@dataclass
class CommandCenterTowerAction:
    skill_name: str

    def __repr__(self) -> str:
        return f"Command Tower {self.skill_name}"

    @classmethod
    def from_xml(cls, action_element: xml.etree.ElementTree.Element):
        skill_id = int(action_element.find("SkillID").text)
        skill_name = COMMAND_TOWER_SKILLS.get(skill_id, skill_id)
        return cls(
            skill_name=skill_name,
        )


@dataclass
class ResearchCenterTowerAction:
    skill_name: str

    def __repr__(self) -> str:
        return f"Research Tower {self.skill_name}"

    @classmethod
    def from_xml(cls, action_element: xml.etree.ElementTree.Element):
        skill_id = int(action_element.find("ID").text)
        skill_name = RESEARCH_TOWER_SKILLS.get(skill_id, skill_id)
        return cls(
            skill_name=skill_name,
        )


PlayerAction = Union[
    BuyAction,
    UnlockAction,
    DeviceAction,
    TechAction,
    UpgradeAction,
    ResearchCenterTowerAction,
    CommandCenterTowerAction,
]


def create_action_from_xml_element(
    action_element: xml.etree.ElementTree.Element,
    units: Dict[int, str],
) -> Optional[PlayerAction]:
    action_type = action_element.get("{http://www.w3.org/2001/XMLSchema-instance}type")
    if action_type == "PAD_BuyUnit":
        return BuyAction.from_xml(action_element)
    elif action_type == "PAD_UnlockUnit":
        return UnlockAction.from_xml(action_element)
    elif action_type == "PAD_ReleaseContraption":
        return DeviceAction.from_xml(action_element)
    elif action_type == "PAD_UpgradeTechnology":
        return TechAction.from_xml(action_element)
    elif action_type == "PAD_UpgradeUnit":
        return UpgradeAction.from_xml(action_element, units)
    elif action_type == "PAD_ActiveEnergyTowerSkill":
        return CommandCenterTowerAction.from_xml(action_element)
    elif action_type == "PAD_ActiveBlueprint":
        return ResearchCenterTowerAction.from_xml(action_element)

    return None


@dataclass
class PlayerRoundRecord:
    round: int
    actions: List[PlayerAction] = field(default_factory=list)


@dataclass
class PlayerRecord:
    id: str
    name: str
    round_records: List[PlayerRoundRecord] = field(default_factory=list)
    starting_officer: Optional[str] = None
    starting_units: List[int] = field(default_factory=list)

@dataclass
class BattleRecord:
    player_records: List[PlayerRecord]


def extract_xml(file_path) -> str:
    """Extracts the XML portion from a file containing a binary blob with XML content."""
    with open(file_path, 'rb') as file:
        content = file.read()

    # Locate the XML start and end tags
    start = content.find(b'<?xml')
    end = content.rfind(b'>') + 1
    if start == -1 or end == -1:
        raise ValueError("No XML content found in the file.")

    return content[start:end].decode('utf-8')


def parse_battle_record(file_path) -> BattleRecord:
    """Parses the BattleRecord XML file to extract player records and their details."""
    # Extract XML content from the binary file
    xml_content = extract_xml(file_path)

    # Parse the XML content
    root = ET.fromstring(xml_content)

    # Navigate to player records
    player_records_element = root.find("playerRecords")
    if player_records_element is None:
        raise Exception("No player records found.")

    player_records = []
    for player_element in player_records_element.findall("PlayerRecord"):
        player_id = player_element.find("id").text
        player_name = player_element.find("name").text

        # Parse round records
        round_records_element = player_element.find("playerRoundRecords")
        round_records = []
        starting_units = []
        starting_officer = None
        if round_records_element is not None:
            for round_element in round_records_element.findall("PlayerRoundRecord"):
                round_number = int(round_element.find("round").text)

                # The information about your starting pack is entirely determined by the seed
                # and the index of which option you picked and is simulated in-game. So
                # there is no way to reverse engineer that in a way that will be durable to game
                # changes. Instead, just look at what units were pre-placed on round 1 and which
                # officer the player has as those will be what were in the starting pack.
                if round_number == 1:
                    starting_units = _parse_round_units(round_element)
                    starting_officer = _parse_round_officers(round_element)[0]

                action_records = _parse_actions(round_element)
                round_records.append(PlayerRoundRecord(round=round_number, actions=action_records))

        player_records.append(PlayerRecord(
            id=player_id,
            name=player_name,
            round_records=round_records,
            starting_units=starting_units,
            starting_officer=starting_officer,
        ))

    return BattleRecord(player_records=player_records)


def _parse_actions(round_element: xml.etree.ElementTree.Element):
    action_records = []
    units = _parse_round_units(round_element)

    for action_element in round_element.findall("actionRecords/MatchActionData"):

        action = create_action_from_xml_element(action_element, units)
        if action is not None:
            action_records.append(action)

    return action_records


def _parse_round_units(round_element: xml.etree.ElementTree.Element) -> Dict[int, str]:
    units_element = round_element.find("playerData/units")
    return {
        int(unit_element.find("Index").text): UNIT_LOOKUP.get(int(unit_element.find("id").text))
        for unit_element in units_element.findall("NewUnitData")
    }


def _parse_round_officers(round_element: xml.etree.ElementTree.Element) -> List[str]:
    officer_elements = round_element.find("playerData/officers")
    return [
        OFFICER_LOOKUP.get(int(officer_element.text), officer_element.text)
        for officer_element in officer_elements.findall("int")
    ]


def _setup_pretty_table_with_players(players: List[PlayerRecord]):
    pretty_table = PrettyTable()
    pretty_table.hrules = ALL
    pretty_table.align = "l"
    pretty_table.left_padding_width = 1
    pretty_table.right_padding_width = 0
    pretty_table.field_names = ["Round"] + [f"{player.name}" for player in players]
    return pretty_table


def _player_start_to_string(player: PlayerRecord) -> str:
    return "\n".join([player.starting_officer] + list(player.starting_units.values()))


def _battle_record_to_string(battle_record: BattleRecord) -> str:
    """Displays the battle record in a tabular format."""
    max_rounds = max(len(player.round_records) for player in battle_record.player_records)
    table = _setup_pretty_table_with_players(battle_record.player_records)

    table.add_row(["0"] + [_player_start_to_string(player) for player in battle_record.player_records])

    for i, round_idx in enumerate(range(max_rounds)[1:]):
        players_actions = []
        for player in battle_record.player_records:
            player_actions = []
            if round_idx < len(player.round_records):
                for action in player.round_records[round_idx].actions:
                    player_actions.append(str(action))

            players_actions.append("\n".join(player_actions))

        table.add_row([f"{i+1}"] + [actions for actions in players_actions])

    return table


if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Parse a Mechabellum replay file (.grbr).")
    parser.add_argument("file", help="Path to the Mechabellum replay file (.grbr).")
    args = parser.parse_args()

    battle_record = parse_battle_record(args.file)
    table = _battle_record_to_string(battle_record)
    print(table)