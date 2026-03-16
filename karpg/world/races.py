"""
Races

MajorMUD-style race definitions. No Evennia imports — pure data.

Each race entry:
    stat_mods             — dict of stat deltas vs baseline (10)
    abilities             — list of string ability tags
    magic_resistance_bonus — flat MR added on top of base
    xp_modifier           — XP gain multiplier (reserved, all 1.0 for now)
    two_handed_allowed    — whether the race can use two-handed weapons
"""

RACE_REGISTRY = {
    "human": {
        "stat_mods": {"str": 0, "agi": 0, "int": 0, "wis": 0, "hlt": 0, "chm": 0},
        "abilities": [],
        "magic_resistance_bonus": 0,
        "xp_modifier": 1.0,
        "two_handed_allowed": True,
    },
    "dwarf": {
        "stat_mods": {"str": 1, "agi": -1, "int": -1, "wis": 1, "hlt": 1, "chm": -1},
        "abilities": ["magic_resistance", "nightvision"],
        "magic_resistance_bonus": 10,
        "xp_modifier": 1.0,
        "two_handed_allowed": True,
    },
    "elf": {
        "stat_mods": {"str": -1, "agi": 1, "int": 1, "wis": 0, "hlt": -1, "chm": 1},
        "abilities": ["nightvision", "stealth_bonus"],
        "magic_resistance_bonus": 0,
        "xp_modifier": 1.0,
        "two_handed_allowed": True,
    },
    "half_orc": {
        "stat_mods": {"str": 1, "agi": 0, "int": -1, "wis": -1, "hlt": 1, "chm": -2},
        "abilities": ["encumbrance_bonus"],
        "magic_resistance_bonus": 0,
        "xp_modifier": 1.0,
        "two_handed_allowed": True,
    },
    "gnome": {
        "stat_mods": {"str": -1, "agi": 1, "int": 1, "wis": 0, "hlt": 0, "chm": -1},
        "abilities": ["magic_resistance", "lockpick_bonus"],
        "magic_resistance_bonus": 5,
        "xp_modifier": 1.0,
        "two_handed_allowed": True,
    },
    "halfling": {
        "stat_mods": {"str": -2, "agi": 2, "int": -1, "wis": 0, "hlt": 0, "chm": 0},
        "abilities": ["stealth_bonus"],
        "magic_resistance_bonus": 0,
        "xp_modifier": 1.0,
        "two_handed_allowed": False,
    },
}


def get_race(name):
    """Look up a race by name (case-insensitive, spaces→underscores). Returns dict or None."""
    key = name.lower().strip().replace(" ", "_")
    return RACE_REGISTRY.get(key)


def list_races():
    """Return list of (name, dict) tuples sorted alphabetically."""
    return sorted(RACE_REGISTRY.items())
