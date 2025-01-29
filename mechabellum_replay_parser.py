import xml.etree.ElementTree
import xml.etree.ElementTree as ET
import re
import json
import argparse
from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any
from prettytable import PrettyTable, ALL
from pathlib import Path


HERE = Path(__file__)
DATA_DIR = HERE.parent / "data"


def _load_data_file(name: str) -> dict[str, Any]:
    with open(DATA_DIR / name) as filepath:
        return json.load(filepath)


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
    401: "Attack Enhancement II",
    501: "Defense Enhancement II",
}


OFFICER_LOOKUP = {
    # Starting Specialists
    10002: "Supply Specialist",
    10010: "Quick Supply Specialist",
    10011: "Missile Specialist",
    10013: "Amplify Specialist",
    10014: "Training Specialist",
    20005: "Giant Specialist",
    20021: "Aerial Specialist",
    20024: "Speed Specialist",
    20029: "Marksman Specialist",
    20032: "Elite Specialist",
    20036: "Sabertooth Specialist",
    20037: "Farseer Specialist",
    20033: "Rhino Specialist",
    20034: "Cost Control Specialist",
    20035: "Heavy Armor Specialist",
    20036: "Sabertooth Specialist",
    20038: "Fire Badger Specialist",
    20039: "Typhoon Specialist",

    # Other "officers" which are a combination of
    # unit upgrade cards and what used to be specialists.
    10001: "Quick Cooldown",
    10003: "Super Supply Enhancement",
    10004: "Additional Deployment Slot",
    10007: "Advanced Shield Device",
    10008: "Advanced Missile Device",
    10009: "Quick Teleport",
    20001: "Advanced Defense Tactics",
    20002: "Advanced Offensive Tactics",
    20003: "Efficient Tech Research",
    20004: "Advanced Power System",
    20006: "Advanced Targeting System",
    20007: "Supply Enhancement",
    20022: "Efficient Giant Manufacturing",
    20023: "Efficient Light Manufacturing",
    30101: "Mass Produced Fortress",
    30102: "Assault Fortress",
    30104: "Improved Fortress",
    30105: "Extended Range Fortress",
    30201: "Extended Range Marksman",
    30202: "Smart Marksman",
    30203: "Subsidized Marksman",
    30204: "Elite Marksman",
    30301: "Extended Range Vulcan",
    30302: "Assault Vulcan",
    30401: "Assault Melting Point",
    30402: "Improved Melting Point",
    30403: "Mass Produced Melting Point",
    30501: "Mass Produced Rhino",
    30502: "Berserk Rhino",
    30503: "Elite Rhino",
    30601: "Mass Produced Wasp",
    30602: "Improved Wasp",
    30604: "Elite Wasp",
    30701: "Subsidized Mustang",
    30702: "Fortified Mustang",
    30703: "Elite Mustang",
    30801: "Subsidized Steel Ball",
    30803: "Improved Steel Ball",
    30804: "Elite Steel Ball",
    30901: "Elite Fang",
    30902: "Assault Fang",
    31001: "Subsidized Crawler",
    31002: "Elite Crawler",
    31101: "Fortified Overlord",
    31102: "Mass Produced Overlord",
    31104: "Improved Overlord",
    31201: "Assault Stormcaller",
    31202: "Extended Range Stormcaller",
    31203: "Subsidized Stormcaller",
    31301: "Mass Produced Sledgehammer",
    31302: "Extended Range Sledgehammer",
    31304: "Improved Sledgehammer",
    31305: "Elite Sledgehammer",
    31402: "Fortified Hacker",
    31403: "Elite Hacker",
    31501: "Subsidized Arclight",
    31502: "Smart Arclight",
    31503: "Fortified Arclight",
    31504: "Extended Range Arclight",
    31601: "Mass Produced Phoenix",
    31602: "Extended Range Phoenix",
    31603: "Improved Phoenix",
    31604: "Elite Phoenix",
    31701: "Extended Range War Factory",
    31702: "Improved War Factory",
    31801: "Mass Produced Wraith",
    31802: "Improved Wraith",
    31901: "Assault Scorpion",
    31902: "Mass Produced Scorpion",
    31903: "Improved Scorpion",
    32301: "Improved Sandworm",
    32302: "Mass Produced Sandworm",
    32401: "Improved Tarantula",
    32402: "Elite Tarantula",
    32501: "Extended Range Phantom Ray",
}


SKILL_LOOKUP = {
    100001: "Redeployment",
    100002: "Incendiary Bomb",
    200001: "Electromagnetic Impact",
    200002: "Electromagnetic Blast",
    200003: "Photon Emission",
    300001: "Missile Strike",
    300003: "Orbital Bombardment",
    300004: "Nuke",
    300005: "Lightning Storm",
    300006: "Ion Blast",
    300007: "Orbital Javelin",
    400002: "Sticky Oil Bomb Tower",
    400003: "Sticky Oil Bomb Spell",
    500002: "Acid Blast",
    600002: "Smoke Bomb",
    800001: "Shield Airdrop",
    900001: "Field Recovery",
    1100001: "Intensive Training",
    1200001: "Underground Threat",
    1200002: "Rhino Assault",
    1200003: "Wasp Swarm",
    1200004: "Mobilize Battleship",
    1200005: "Vulcan's Descent",
    1500001: "Mobile Beacon Tower",
    1500002: "Mobile Beacon Spell",
}


ITEM_LOOKUP = {
    1305003: "Photon Coating",
    1306001: "Tank Production Line",
    1306002: "Mustang Production Line",
    1306003: "Steel Ball Production Line",
    1307001: "Barrier",
    1308001: "Anti Interference Module",
    1309001: "Absorption Module",
    13010001: "Portable Shield",
    13020001: "Nano Repair Kit",
    13030001: "Laser Sights",
    13030002: "Heavy Armor",
    13030003: "Improved Firepower Control System",
    13030004: "Enhancement Module",
    13030005: "Haste Module",
    13030006: "Super Heavy Armor",
    13030007: "Amplifying Core",
    13040001: "Deployment Module",
}


# Pool of all reinforcement card selections a player can make not including unit reinforcements.
CARD_LOOKUP = {
    0: "Skip",
    **ITEM_LOOKUP,
    **SKILL_LOOKUP,
    **OFFICER_LOOKUP,
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


UNIT_DATA = _load_data_file("unit_data.json")


TECH_LOOKUP = {
    # Crawler techs
    10510: "Mechanical rage",
    180110: "Replicate",
    2610: "Subterranean blitz",
    2710: "Acidic explosion",
    10710: "Impact drill",
    3510: "Loose formation",

    # Fang techs
    180209: "Ignite",
    10209: "Range enhancement",
    10509: "Mechanical rage",
    209: "Portable shield",
    10609: "Armor piercing bullets",

    # Fortress techs
    1001: "Barrier",
    10201: "Range enhancement",
    1105: "Anti air barrage",
    1201: "Fang production",
    10301: "Launcher overload",
    10801: "Elite marksman",
    701: "Doubleshot",
    3001: "Armor enhancement",
    110201: "Rocket punch",

    # Marksman techs
    702: "Doubleshot",
    10202: "Range enhancement",
    10402: "Quick reload",
    1802: "Electromagnetic shot",
    10802: "Elite marksman",
    1202: "Shooting squad",
    10102: "Assault mode",
    3202: "Aerial specialisation",

    # Vulcan techs
    180203: "Ignite",
    10203: "Range enhancement",
    1103: "Incendiary bomb",
    10603: "Scorching fire",
    1203: "Best partner",
    11010: "Sticky oil bomb",
    3003: "Armor enhancement",

    # Melting point techs
    304: "Energy absorption",
    10204: "Range enhancement",
    1107: "Energy diffraction",
    1106: "Electromagnetic barrage",
    1204: "Crawler production",
    3004: "Armor enhancement",

    # Rhino techs
    1109: "Whirlwind",
    180305: "Photon coating",
    905: "Field maintenance",
    2805: "Final blitz",
    10505: "Mechanical rage",
    2305: "Wreckage recycling",
    2505: "Power armor",
    3005: "Armor enhancement",

    # Wasp techs
    206: "Energy shield",
    10206: "Range enhancement",
    1606: "Jump drive",
    506: "Ground specialization",
    10806: "Elite marksman",
    180206: "Ignite",
    1806: "Electromagnetic shot",
    406: "High explosive ammo",
    10606: "Armor piercing bullets",
    3206: "Aerial specialization",

    # Mustang techs
    3307: "Missile interceptor",
    10207: "Range enhancement",
    407: "High explosive ammo",
    3207: "Aerial specialization",
    10607: "Armor piercing bullets",

    # Steel ball techs
    308: "Energy absorption",
    608: "Damage sharing",
    10208: "Range enhancement",
    1308: "Mechanical division",
    3008: "Armor enhancement",
    2408: "Fortified target lock",

    # Overlord techs
    1108: "Overlord artillery",
    10311: "Launcher overload",
    1211: "Mothership",
    1611: "Jump drive",
    180311: "Photon emission",
    10211: "Range enhancement",
    3011: "Armor enhancement",
    911: "Field maintenance",
    411: "High explosive ammo",

    # Stormcaller techs
    812: "Incendiary bomb",
    10212: "Range enhancement",
    10312: "Launcher overload",
    412: "High explosive ammo",
    1812: "Electromagnetic explosion",
    10912: "High explosive anti tank shells",

    # Sledgehammer techs
    913: "Field maintenance",
    613: "Damage sharing",
    10513: "Mechanical rage",
    10213: "Range enhancement",
    1813: "Electromagnetic shot",
    10613: "Armor piercing bullets",
    3013: "Armor enhancement",

    # Hacker techs
    11014: "Multi control",
    1014: "Barrier",
    10214: "Range enhancement",
    1714: "Enhanced control",
    1814: "Electromagnetic interference",

    # Arclight techs
    10215: "Range enhancement",
    1815: "Electromagnetic shot",
    10915: "Charged shot",
    3015: "Armor enhancement",
    3115: "Anti aircraft ammunition",
    10815: "Elite marksman",

    # Phoenix techs
    2916: "Quantum reassembly",
    10216: "Range enhancement",
    10316: "Launcher overload",
    216: "Energy shield",
    1616: "Jump drive",
    1816: "Electromagnetic shot",
    10816: "Elite marksman",
    10916: "Charged shot",

    # War factory techs
    10217: "Range enhancement",
    3417: "Efficient maintenance",
    12017: "Phoenix production",
    12117: "Steel ball production",
    12217: "Sledgehammer production",
    3317: "Missile interceptor",
    10317: "Launcher overload",
    180317: "Photon coating",
    3017: "Armor enhancement",
    417: "High explosive ammo",

    # Wraith techs
    110181: "Floating artillery array",
    10218: "Range enhancement",
    3018: "Armor enhancement",
    180418: "Degeneration beam",
    918: "Field maintenance",
    418: "High explosive ammo",

    # Scorpion techs
    180519: "Acid attack",
    10019: "Siege mode",
    10219: "Range enhancement",
    719: "Doubleshot",
    919: "Field maintenance",
    3019: "Armor enhancement",

    # Fire badger techs
    10220: "Range enhancement",
    820: "Napalm",
    180220: "Ignite",
    920: "Field maintenance",
    10620: "Scorching fire",

    # Sabertooth techs
    10221: "Range enhancement",
    10321: "Field maintenance",
    3321: "Missile interceptor",
    721: "Doubleshot",

    # Typhoon techs
    3022: "Mechanical rage",
    3222: "Aerial specialisation",
    1022: "Barrier",
    11022: "Homing missile",

    # Sandworm techs
    10523: "Mechanical rage",
    3023: "Armor enhancement",
    13023: "Mechanical division",
    3123: "Anti aerial",
    923: "Burrow maintenance",
    3623: "Replicate",
    3723: "Sandstorm",
    3823: "Strike",

    # Tarantula techs
    11024: "Spider mine",
    10224: "Range enhancement",
    10524: "Mechanical rage",
    10624: "Armor piercing bullets",
    924: "Field maintenance",
    3024: "Armor enhancement",
    3124: "Anti aircraft ammunition",
    424: "High explosive ammo",

    # Farseer techs
    180326: "Photon emission",
    180526: "Scanning radar",
    3326: "Missile interceptor",
    1826: "Electromagnetic explosion",
    10226: "Range enhancement",

    # Phantom ray techs
    725: "Burst mode",
    10225: "Range enhancement",
    3025: "Armor enhancement",
    11025: "Sticky oil bomb",
    3925: "Stealth cloak",
    425: "High explosive ammo",
    225: "Energy shield",

    # Raiden techs
    10227: "Range enhancement",
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


@dataclass
class UnitDrop:
    count: int
    level: int
    unit: str
    round: int

    def __repr__(self) -> str:
        return f"Unit Drop: {self.count} level {self.level} {self.unit}"
    @classmethod
    def from_round_number_and_identifier(cls, round_number: int, identifier: int) -> 'UnitDrop':
        unit_drop_data = str(identifier)
        unit_drop_regex = re.compile('1{:02d}(?P<count>\d)(?P<level>\d)(?P<unit>\d+)'.format(round_number))
        match = unit_drop_regex.match(unit_drop_data)
        data = {
            k: int(v)
            for (k, v) in match.groupdict().items()
        }
        data['unit'] = UNIT_LOOKUP.get(data['unit'])
        data['round'] = round_number
        return cls(**data)

    @classmethod
    def from_xml(cls, round_number: int, action_element: xml.etree.ElementTree.Element):
        return cls.from_round_number_and_identifier(round_number, int(action_element.find("ID").text))


@dataclass
class ReinforcementSelection:
    card_name: str

    def __str__(self) -> str:
        return f"Select Card: {self.card_name}"

    @classmethod
    def from_xml(cls, action_element: xml.etree.ElementTree.Element):
        ident = int(action_element.find("ID").text)
        card_name = CARD_LOOKUP.get(ident, ident)
        return cls(card_name=card_name)


@dataclass
class SkillAction:
    skill_name: str

    def __str__(self) -> str:
        return f"Use Skill: {self.skill_name}"

    @classmethod
    def from_xml(cls, action_element: xml.etree.ElementTree.Element):
        ident = int(action_element.find("ID").text)
        skill_name = SKILL_LOOKUP.get(ident, ident)
        return cls(skill_name=skill_name)


PlayerAction = Union[
    BuyAction,
    UnlockAction,
    DeviceAction,
    TechAction,
    UpgradeAction,
    ResearchCenterTowerAction,
    CommandCenterTowerAction,
    UnitDrop,
    ReinforcementSelection,
    SkillAction,
]


def create_action_from_xml_element(
    action_element: xml.etree.ElementTree.Element,
    units: Dict[int, str],
    round_number: int,
    reinforce_rounds: List[int],
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
    elif action_type == "PAD_ChooseReinforceItem" and round_number in reinforce_rounds:
        return UnitDrop.from_xml(round_number, action_element)
    elif action_type == "PAD_ChooseReinforceItem":
        return ReinforcementSelection.from_xml(action_element)
    elif action_type == "PAD_ReleaseCommanderSkill":
        return SkillAction.from_xml(action_element)

    return None


@dataclass
class PlayerRoundRecord:
    round: int
    player_hp: int
    actions: List[PlayerAction] = field(default_factory=list)


@dataclass
class DeploymentTracker:
    count: List[int] = field(default_factory=list)
    # Value here encompasses the unit purchase cost only. Upgrades and tech not included yet.
    # TODO add tech tracker
    # TODO add upgrade cost tracking
    value: List[int] = field(default_factory=list)

    @classmethod
    def from_record_list(cls, records: List[PlayerRoundRecord]) -> 'DeploymentTracker':
        tracker = cls(count=[5], value=[700])
        for round_number, record in enumerate(records):
            for action in record.actions:
                if isinstance(action, BuyAction):
                    tracker.buy(round_number, action)
                elif isinstance(action, SkillAction) and action == SkillAction("Field Recovery"):
                    tracker.sell(round_number, action)
                elif isinstance(action, UnitDrop):
                    tracker.process_unit_drop(round_number, action)
        return tracker

    def _ensure_round_number(self, round_number: int):
        if round_number >= len(self.count):
            self.count.append(self.count[round_number - 1])
            self.value.append(self.value[round_number - 1])

    def buy(self, round_number: int, buy: BuyAction):
        self._ensure_round_number(round_number)

        self.count[round_number] += 1
        self.value[round_number] += UNIT_DATA.get(buy.unit).get("value")

    def sell(self, round_number: int, sell: SkillAction):
        self._ensure_round_number(round_number)

        self.count[round_number] += 1
        # TODO figure out how to get the unit being sold's value here (upgrades etc)

    def process_unit_drop(self, round_number: int, drop: UnitDrop):
        self._ensure_round_number(round_number)

        self.count[round_number] += drop.count
        self.value[round_number] += drop.count * UNIT_DATA.get(drop.unit).get("value")


@dataclass
class PlayerRecord:
    id: str
    name: str
    round_records: List[PlayerRoundRecord] = field(default_factory=list)
    starting_officer: Optional[str] = None
    starting_units: List[int] = field(default_factory=list)
    deployments: Optional[DeploymentTracker] = None

    def __post_init__(self):
        if self.deployments is None:
            self.deployments = DeploymentTracker.from_record_list(self.round_records)


@dataclass
class BattleRecord:
    player_records: List[PlayerRecord]


def extract_xml(file_path) -> str:
    """Extracts the XML portion from a file containing a binary blob with XML content."""
    with open(file_path, 'rb') as file:
        content = file.read()

    # Locate the XML start and end of the XML embedded in the binary file.
    start = content.find(b'<?xml')
    # The name of the players appears in the footer of the file in binary. If we just search for > a player name with
    # > in it will be found and give us incorrect xml boundaries. We search for BattleRecord> instead to give a more
    # unique sentinel value to look for. If a player has that in their name they deserve to have their
    # replays be un-parsable.
    end = content.rfind(b'BattleRecord>') + 13
    if start == -1 or end == -1:
        raise ValueError("No XML content found in the file.")

    return content[start:end].decode('utf-8')


def parse_battle_record(file_path) -> BattleRecord:
    """Parses the BattleRecord XML file to extract player records and their details."""
    # Extract XML content from the binary file
    xml_content = extract_xml(file_path)

    # Parse the XML content
    root = ET.fromstring(xml_content)

    # Find the unit drop rounds
    reinforce_rounds = [
        int(node.text) for node in
        root.find("matchDatas/MatchSnapshotData/unitReinforceRounds").findall("int")
    ]

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
                player_hp = int(round_element.find("playerData/reactorCore").text)

                # The information about your starting pack is entirely determined by the seed
                # and the index of which option you picked and is simulated in-game. So
                # there is no way to reverse engineer that in a way that will be durable to game
                # changes. Instead, just look at what units were pre-placed on round 1 and which
                # officer the player has as those will be what were in the starting pack.
                if round_number == 1:
                    starting_units = _parse_round_units(round_element)
                    starting_officer = _parse_round_officers(round_element)[0]

                action_records = _parse_actions(round_element, round_number, reinforce_rounds)
                round_records.append(PlayerRoundRecord(
                    round=round_number,
                    player_hp=player_hp,
                    actions=action_records,
                ))

        player_records.append(PlayerRecord(
            id=player_id,
            name=player_name,
            round_records=round_records,
            starting_units=starting_units,
            starting_officer=starting_officer,
        ))

    return BattleRecord(player_records=player_records)


def _parse_actions(round_element: xml.etree.ElementTree.Element, round_number: int, reinforce_rounds: List[int]):
    action_records = []
    units = _parse_round_units(round_element)

    for action_element in round_element.findall("actionRecords/MatchActionData"):

        action = create_action_from_xml_element(action_element, units, round_number, reinforce_rounds)
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

                # Grab the player HP and put it at the top of the list of actions for the round.
                player_hp = str(player.round_records[round_idx].player_hp)
                player_hp_line = f"HP: {player_hp}"
                player_actions.append(player_hp_line)

                # Collect all the remaining player actions
                for action in player.round_records[round_idx].actions:
                    player_actions.append(str(action))

                # Grab the deployment count and put it at the bottom of the list of actions.
                deployments = str(player.deployments.count[round_idx])
                deployments_line = f"Deployment Total: {deployments}"
                player_actions.append(deployments_line)

                # Get the value of units on board total for each turn
                value_on_board = str(player.deployments.value[round_idx])
                player_actions.append(f"Value on board: {value_on_board}")

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