import xml.etree.ElementTree
import xml.etree.ElementTree as ET
import re
import json
import copy
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
    5: "Defense Enhancement",
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
    1000001: "Redeployment",
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
    28: "hound",
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
    110211: "Secondary Armament",
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
    110271: "Fork",
    1827: "Electromagnetic Shot",
    4127: "Ionization",
}


@dataclass
class Point:
    x: int
    y: int

    @classmethod
    def from_xml(cls, element: xml.etree.ElementTree.Element) -> "Point":
        return cls(
            x=int(element.find("x").text),
            y=int(element.find("y").text),
        )

    @classmethod
    def default(cls) -> "Point":
        return cls(0, 0)


@dataclass
class Unit:
    unit_name: str
    ident: int
    sell_supply: int
    position: Optional[Point] = field(default_factory=lambda: Point.default())

    def __repr__(self) -> str:
        return f"{self.unit_name}"

    @classmethod
    def from_xml(cls, unit_element: xml.etree.ElementTree.Element) -> "Unit":
        return cls(
            unit_name=UNIT_LOOKUP.get(int(unit_element.find("id").text)),
            ident=int(unit_element.find("id").text),
            sell_supply=int(unit_element.find("SellSupply").text),
            position=Point.from_xml(unit_element.find("Position")),
        )

    @classmethod
    def from_name(cls, name: str) -> "Unit":
        data = UNIT_DATA.get(name)

        return cls(
            unit_name=name,
            ident=data.get("ident"),
            sell_supply=data.get("value"),
            position=Point.default(),
        )

    def set_level(self, level: int) -> "Unit":
        upgrade_cost = self.sell_supply // 2
        base_value = UNIT_DATA.get(self.unit_name).get("value")
        self.sell_supply = base_value + (level - 1) * upgrade_cost
        return self


def _get_special_case_unit_spawning(version: str) -> dict[tuple[int, str], Unit]:
    if int(version) < 1503:
        return {
            (2, "Marksman Specialist"): Unit.from_name("marksmen").set_level(3),
            (2, "Sabertooth Specialist"): Unit.from_name("sabertooth"),
            (2, "Fire Badger Specialist"): Unit.from_name("fire badger"),
            (3, "Typhoon Specialist"): Unit.from_name("typhoon"),
            (3, "Farseer Specialist"): Unit.from_name("farseer"),
            (4, "Rhino Specialist"): Unit.from_name("rhino").set_level(2),
        }
    elif int(version) <= 1527:
        return {
            (2, "Marksman Specialist"): Unit.from_name("marksmen").set_level(3),
            (2, "Sabertooth Specialist"): Unit.from_name("sabertooth"),
            (2, "Fire Badger Specialist"): Unit.from_name("fire badger"),
            (4, "Rhino Specialist"): Unit.from_name("rhino").set_level(2),
            (4, "Typhoon Specialist"): Unit.from_name("typhoon"),
            (4, "Farseer Specialist"): Unit.from_name("farseer"),
        }
    elif int(version) <= 1532:  # new in version 1532
        return {
            (2, "Marksman Specialist"): Unit.from_name("marksmen").set_level(3),
            (1, "Sabertooth Specialist"): Unit.from_name("sabertooth"),
            (1, "Fire Badger Specialist"): Unit.from_name("fire badger"),
            (4, "Rhino Specialist"): Unit.from_name("rhino").set_level(2),
            (4, "Typhoon Specialist"): Unit.from_name("typhoon"),
            (4, "Farseer Specialist"): Unit.from_name("farseer"),
        }
    else:
        return {
            (2, "Marksman Specialist"): Unit.from_name("marksmen").set_level(3),
            (3, "Sabertooth Specialist"): Unit.from_name("sabertooth"),
            (3, "Fire Badger Specialist"): Unit.from_name("fire badger"),
            (4, "Rhino Specialist"): Unit.from_name("rhino").set_level(2),
            (4, "Typhoon Specialist"): Unit.from_name("typhoon"),
            (4, "Farseer Specialist"): Unit.from_name("farseer"),
        }


@dataclass
class UnitCollection:
    units: Dict[int, Unit] = field(default_factory=dict)
    next_index: int = 0

    @classmethod
    def from_xml(cls, round_element: xml.etree.ElementTree.Element) -> "UnitCollection":
        units_element = round_element.find("playerData/units")
        units = cls()
        for unit_element in units_element.findall("NewUnitData"):
            unit = Unit.from_xml(unit_element)
            units.add_unit(unit, int(unit_element.find("Index").text))
        units.next_index = int(round_element.find("playerData/unitIndex").text)
        return units

    def add_unit(self, unit: Unit, index: Optional[int] = None) -> int:
        if index is None:
            index = self.next_index
        self.units[index] = unit
        self.next_index += 1
        return index

    def delete_unit(self, index: int) -> None:
        if index in self.units:
            del self.units[index]

    def get_unit(self, index: int) -> Optional[Unit]:
        return self.units.get(index)

    def __contains__(self, index: int) -> bool:
        return index in self.units

    def copy(self) -> "UnitCollection":
        return copy.deepcopy(self)


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
        return cls(
            device=CONTRAPTION_LOOKUP.get(
                int(action_element.find("ContraptionID").text)
            )
        )


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
    unit: Unit

    def __repr__(self) -> str:
        return f"Upgrade {self.unit}"

    @classmethod
    def from_xml(
        cls, action_element: xml.etree.ElementTree.Element, units: UnitCollection
    ):
        # TODO: Bug here: sometimes the upgraded unit is not in the list for some reason.
        # typically its out of bounds by 1 past the last unit. Buying and selling may shift
        # the unit data and I am not accounting for that. Upgrades done at the beginning of a turn
        # seem to always be correct.
        unit_index = int(action_element.find("UIDX").text)
        if unit_index not in units:
            return None
        return cls(
            unit=units.get_unit(unit_index),
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
    def from_round_number_and_identifier(
        cls, round_number: int, identifier: int
    ) -> "UnitDrop":
        unit_drop_data = str(identifier)
        unit_drop_regex = re.compile(
            r"1{:02d}(?P<count>\d)(?P<level>\d)(?P<unit>\d+)".format(round_number)
        )
        match = unit_drop_regex.match(unit_drop_data)
        data = {k: int(v) for (k, v) in match.groupdict().items()}
        data["unit"] = UNIT_LOOKUP.get(data["unit"])
        data["round"] = round_number
        return cls(**data)

    @classmethod
    def from_xml(cls, round_number: int, action_element: xml.etree.ElementTree.Element):
        return cls.from_round_number_and_identifier(
            round_number, int(action_element.find("ID").text)
        )


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
    target_unit_index: Optional[int] = None

    def __str__(self) -> str:
        return f"Use Skill: {self.skill_name}"

    @classmethod
    def from_xml(
        cls, action_element: xml.etree.ElementTree.Element, skills: "SkillCollection"
    ):
        # The game supposedly uses the <id> field to track which skill is being used. However, in practice
        # a lot of times this field is simply set to 0 for unknown reasons. Instead of relying on this field
        # we can use the <SkillIndex> field to determine the index in the player's skill list of the skill.
        # This is more work since we manually need to track this using the SkillCollection class, but is required
        # for consistency.
        skill_index = int(action_element.find("SkillIndex").text)
        skill_name = skills.get_skill(skill_index)
        unit_index = action_element.find("UnitIndex")
        return cls(
            skill_name=skill_name,
            target_unit_index=int(unit_index.text) if unit_index is not None else None,
        )


@dataclass
class MoveUnitAction:
    unit_index: int
    rotate: bool
    position: Point

    @classmethod
    def from_xml(
        cls, action_element: xml.etree.ElementTree.Element
    ) -> "MoveUnitAction":
        move_element = action_element.find("moveUnitDatas/MoveUnitData")
        return cls(
            unit_index=int(move_element.find("unitIndex").text),
            rotate=move_element.find("isRotate").text == "true",
            position=Point.from_xml(move_element.find("position")),
        )


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
    MoveUnitAction,
]


@dataclass
class SkillCollection:
    skills: Dict[int, str] = field(default_factory=dict)
    next_index: int = 0

    @classmethod
    def from_xml(
        cls, round_element: xml.etree.ElementTree.Element
    ) -> "SkillCollection":
        commander_skills_element = round_element.find("playerData/commanderSkills")
        collection = cls()
        for skill_element in commander_skills_element.findall("CommanderSkillData"):
            index = int(skill_element.find("index").text)
            skill_id = int(skill_element.find("id").text)
            skill_name = SKILL_LOOKUP.get(skill_id, skill_id)
            collection.add_skill(skill_name, index)
        return collection

    def add_skill(self, skill_name: str, index: Optional[int] = None) -> None:
        if index is None:
            index = self.next_index
        self.skills[index] = skill_name
        self.next_index += 1

    def add_skill_from_action(self, action: PlayerAction) -> None:
        # Not worth attaching metadata to the various actions yet to determine their type, just to avoid a
        # special case here. It eventually may be worth it though if the metadata was used elsewhere.
        if isinstance(action, ResearchCenterTowerAction):
            if action.skill_name in ("Oil Bomb", "Field Recovery", "Mobile Beacon"):
                self.add_skill(action.skill_name)
        elif isinstance(action, ReinforcementSelection):
            if action.card_name in SKILL_LOOKUP.values():
                self.add_skill(action.card_name)

    def get_skill(self, skill_index: int) -> str:
        return self.skills.get(
            skill_index, f"unknown skill (invalid index {skill_index}"
        )


def create_action_from_xml_element(
    action_element: xml.etree.ElementTree.Element,
    units: Dict[int, str],
    round_number: int,
    reinforce_rounds: List[
        int
    ],  # If the number of extra arguments grows past reinforce_rounds
    skills: SkillCollection,  # and skills, then they should be wrapped in a CreateActionContext class.
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
        return SkillAction.from_xml(action_element, skills)
    elif action_type == "PAD_MoveUnit":
        return MoveUnitAction.from_xml(action_element)
    return None


@dataclass
class PlayerRoundRecord:
    round: int
    player_hp: int
    starting_units: List[Unit] = field(default_factory=list)
    actions: List[PlayerAction] = field(default_factory=list)


@dataclass
class DeploymentTracker:
    count: List[int] = field(default_factory=list)
    # Value here encompasses the unit purchase cost only. Upgrades and tech not included yet.
    # TODO add tech tracker
    value: List[int] = field(default_factory=list)
    units: List[UnitCollection] = field(default_factory=list)

    @classmethod
    def from_record_list(
        cls, version: str, officer: str, records: List[PlayerRoundRecord]
    ) -> "DeploymentTracker":
        tracker = cls(count=[5], value=[700])
        # This is a little confusing since record_number and record.round seem to be used
        # interchangeably. record.round is the actual in game round, even in the event that
        # the replay was missing some starting rounds. record_number is just the number of
        # the record in our list. For example if you started observing a game on round 3
        # your replay would data for round 0, 3, 4, 5 etc... record_number would still be
        # 0, 1, 2, 3. That means for things that trigger on a round number like spawning a
        # farseer for farseer spec we need to use the record.round number. But for internal
        # bookkeeping we use record_number.
        for record_number, record in enumerate(records):
            units = record.starting_units.copy()
            tracker.ensure_round_number(record_number)
            cls._pre_action_unit_setup(version, record.round, officer, units)
            for action in record.actions:
                if isinstance(action, BuyAction):
                    tracker.buy(record_number, action, units)
                elif isinstance(action, UpgradeAction):
                    tracker.upgrade(record_number, action)
                elif (
                    isinstance(action, SkillAction)
                    and action.skill_name == "Field Recovery"
                ):
                    tracker.sell(record_number, action, units)
                elif isinstance(action, UnitDrop):
                    tracker.process_unit_drop(record_number, action, units)
                elif isinstance(action, MoveUnitAction):
                    tracker.move(action, units)
            tracker.units.append(units)
        return tracker

    @classmethod
    def _pre_action_unit_setup(
        cls, version: str, round_number: int, officer: str, units: UnitCollection
    ):
        # There are some special cases to take care of before we process user actions
        cases = _get_special_case_unit_spawning(version)

        key = (round_number, officer)
        unit = cases.get(key)

        if unit is not None:
            units.add_unit(unit)

    def ensure_round_number(self, round_number: int):
        if round_number >= len(self.count):
            self.count.append(self.count[round_number - 1])
            self.value.append(self.value[round_number - 1])

    def move(self, move: MoveUnitAction, units: UnitCollection):
        unit = units.get_unit(move.unit_index)
        unit.position = move.position

    def buy(self, round_number: int, buy: BuyAction, units: UnitCollection):
        self.count[round_number] += 1
        self.value[round_number] += UNIT_DATA.get(buy.unit).get("value")
        units.add_unit(Unit.from_name(buy.unit))

    def upgrade(self, round_number: int, upgrade: UpgradeAction):
        self.value[round_number] += (
            UNIT_DATA.get(upgrade.unit.unit_name, {}).get("value", 0) // 2
        )
        # TODO: Potentially better here to update the UnitCollection and then
        # at the end of a turn we can total the units' SellSupply values. This will
        # keep everything consistent and have a single source of truth.

    def sell(self, round_number: int, sell: SkillAction, units: UnitCollection):
        sold_unit = units.get_unit(sell.target_unit_index)
        self.count[round_number] -= 1
        self.value[round_number] -= sold_unit.sell_supply
        units.delete_unit(sell.target_unit_index)

    def process_unit_drop(
        self, round_number: int, drop: UnitDrop, units: UnitCollection
    ):
        self.count[round_number] += drop.count
        for i in range(drop.count):
            new_unit = Unit.from_name(drop.unit).set_level(drop.level)

            units.add_unit(new_unit)
            self.value[round_number] += new_unit.sell_supply


@dataclass
class PlayerRecord:
    version: str
    id: str
    name: str
    round_records: List[PlayerRoundRecord] = field(default_factory=list)
    starting_officer: Optional[str] = None
    starting_units: List[int] = field(default_factory=list)
    deployments: Optional[DeploymentTracker] = None
    tech_choices: Optional[Dict[str, List[str]]] = None

    def __post_init__(self):
        if self.deployments is None:
            self.deployments = DeploymentTracker.from_record_list(
                self.version,
                self.starting_officer,
                self.round_records,
            )


@dataclass
class BattleRecord:
    version: str
    player_records: List[PlayerRecord]


def extract_xml(file_path: Path) -> str:
    """Extracts the XML portion from a file containing a binary blob with XML content."""
    with open(file_path, "rb") as file:
        content = file.read()

    # Locate the XML start and end of the XML embedded in the binary file.
    start = content.find(b"<?xml")
    # The name of the players appears in the footer of the file in binary. If we just search for > a player name with
    # > in it will be found and give us incorrect xml boundaries. We search for BattleRecord> instead to give a more
    # unique sentinel value to look for. If a player has that in their name they deserve to have their
    # replays be un-parsable.
    end = content.rfind(b"BattleRecord>") + 13
    if start == -1 or end == -1:
        raise ValueError("No XML content found in the file.")

    return content[start:end].decode("utf-8")


def parse_battle_record(file_path: Path) -> BattleRecord:
    """Parses the BattleRecord XML file to extract player records and their details."""
    # Extract XML content from the binary file
    xml_content = extract_xml(file_path)

    # Parse the XML content
    root = ET.fromstring(xml_content)

    # Find the unit drop rounds
    reinforce_rounds = []

    # Iterate through all MatchSnapshotData elements
    for snapshot in root.findall("matchDatas/MatchSnapshotData"):
        # Extract reinforcement rounds from the current snapshot
        rounds = [
            int(node.text) for node in snapshot.findall("unitReinforceRounds/int")
        ]

        # If we found values, store them and stop searching
        # Sometimes these are empty for some reason in round 0, so we can't just assume
        # it will always be in a particular round. I assume it will always be in at
        # the very least the first round the drops arrive.
        if rounds:
            reinforce_rounds = rounds
            break

    # Navigate to player records
    player_records_element = root.find("playerRecords")
    if player_records_element is None:
        raise Exception("No player records found.")

    player_records = []
    for player_element in player_records_element.findall("PlayerRecord"):
        player_id = player_element.find("id").text
        player_name = player_element.find("name").text

        # Parse their tech choices
        unit_datas_element = player_element.find("data/unitDatas")
        unit_data = {
            UNIT_LOOKUP.get(
                int(data_element.find("id").text), data_element.find("id").text
            ): [
                TECH_LOOKUP.get(int(tech_element.get("data")), tech_element.get("data"))
                for tech_element in data_element.find("techs").findall("tech")
            ]
            for data_element in unit_datas_element.findall("unitData")
            if data_element.find("id").text
            != "2001"  # For now a special case for death knell to just keep it out.
        }

        # Parse round records
        round_records_element = player_element.find("playerRoundRecords")
        round_records = []
        starting_units = []
        starting_officer = None
        if round_records_element is not None:
            extracted_starting_units_and_officer = False
            for round_element in round_records_element.findall("PlayerRoundRecord"):
                round_number = int(round_element.find("round").text)
                player_hp = int(round_element.find("playerData/reactorCore").text)
                units = UnitCollection.from_xml(round_element)

                # The information about your starting pack is entirely determined by the seed
                # and the index of which option you picked and is simulated in-game. So
                # there is no way to reverse engineer that in a way that will be durable to game
                # changes. Instead, just look at what units were pre-placed on round 1 and which
                # officer the player has as those will be what were in the starting pack.
                # Addendum:
                # When you join a game to observe late you only have the rounds you observed. That
                # means in a common case round 1 can be missing, we cannot extract the officer and
                # starting units from it reliably. Instead, we look at the lowest non-zero round
                # and get the 0th officer, and the units labeled with indexes 1-5 as those do not
                # change. In the event that they were sold they will simply be missing from the
                # report as I do not want to guess.
                if round_number > 0 and extracted_starting_units_and_officer is False:
                    starting_units = units.copy()
                    starting_officer = _parse_round_officers(round_element)[0]
                    extracted_starting_units_and_officer = True

                action_records = _parse_actions(
                    round_element, round_number, reinforce_rounds
                )
                round_records.append(
                    PlayerRoundRecord(
                        round=round_number,
                        player_hp=player_hp,
                        starting_units=units,
                        actions=action_records,
                    )
                )

        player_records.append(
            PlayerRecord(
                version=root.find("Version").text,
                id=player_id,
                name=player_name,
                round_records=round_records,
                starting_units=starting_units,
                starting_officer=starting_officer,
                tech_choices=unit_data,
            )
        )

    return BattleRecord(
        version=root.find("Version").text,
        player_records=player_records,
    )


def _parse_actions(
    round_element: xml.etree.ElementTree.Element,
    round_number: int,
    reinforce_rounds: List[int],
):
    action_records = []
    units = UnitCollection.from_xml(round_element)
    skills = SkillCollection.from_xml(round_element)

    for action_element in round_element.findall("actionRecords/MatchActionData"):
        action = create_action_from_xml_element(
            action_element, units, round_number, reinforce_rounds, skills
        )
        skills.add_skill_from_action(action)
        if action is not None:
            action_records.append(action)

    return action_records


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
    return "\n".join(
        [player.starting_officer]
        + [unit.unit_name for unit in player.starting_units.units.values()]
    )


def battle_record_to_string(battle_record: BattleRecord) -> str:
    """Displays the battle record in a tabular format."""
    max_rounds = max(
        len(player.round_records) for player in battle_record.player_records
    )
    table = _setup_pretty_table_with_players(battle_record.player_records)

    table.add_row(
        ["0"]
        + [_player_start_to_string(player) for player in battle_record.player_records]
    )

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
                    # TODO implement custom filtering here rather than hardcode
                    # that we are ignoring move actions.
                    if isinstance(action, MoveUnitAction):
                        continue
                    player_actions.append(str(action))

                # Grab the deployment count and put it at the bottom of the list of actions.
                deployments = str(player.deployments.count[round_idx])
                deployments_line = f"Deployment Total: {deployments}"
                player_actions.append(deployments_line)

                # Get the value of units on board total for each turn
                value_on_board = str(player.deployments.value[round_idx])
                player_actions.append(f"Value on board: {value_on_board}")

            players_actions.append("\n".join(player_actions))

        table.add_row([f"{i + 1}"] + [actions for actions in players_actions])

    return table
