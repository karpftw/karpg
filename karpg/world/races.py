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
        "passive_bonus": {
            "type": "cp_per_level",
            "amount": 2,
            "label": "Adaptable",
            "description": "Gain +2 bonus CP each time you level up.",
        },
    },
    "dwarf": {
        "stat_mods": {"str": 1, "agi": -1, "int": -1, "wis": 1, "hlt": 1, "chm": -1},
        "abilities": ["magic_resistance", "nightvision"],
        "magic_resistance_bonus": 10,
        "xp_modifier": 1.0,
        "two_handed_allowed": True,
        "passive_bonus": {
            "type": "stonecunning",
            "label": "Stonecunning",
            "description": "+10 accuracy and +10 defense in dungeon rooms.",
        },
    },
    "elf": {
        "stat_mods": {"str": -1, "agi": 1, "int": 1, "wis": 0, "hlt": -1, "chm": 1},
        "abilities": ["nightvision", "stealth_bonus"],
        "magic_resistance_bonus": 0,
        "xp_modifier": 1.0,
        "two_handed_allowed": True,
        "passive_bonus": {
            "type": "spell_resist",
            "label": "Spell Resistance",
            "description": "5% chance to resist any incoming condition application.",
        },
    },
    "half_orc": {
        "stat_mods": {"str": 1, "agi": 0, "int": -1, "wis": -1, "hlt": 1, "chm": -2},
        "abilities": ["encumbrance_bonus"],
        "magic_resistance_bonus": 0,
        "xp_modifier": 1.0,
        "two_handed_allowed": True,
        "passive_bonus": {
            "type": "blood_rage",
            "label": "Blood Rage",
            "description": "When HP falls below 25%, gain +5 accuracy.",
        },
    },
    "gnome": {
        "stat_mods": {"str": -1, "agi": 1, "int": 1, "wis": 0, "hlt": 0, "chm": -1},
        "abilities": ["magic_resistance", "lockpick_bonus"],
        "magic_resistance_bonus": 5,
        "xp_modifier": 1.0,
        "two_handed_allowed": True,
        "passive_bonus": {
            "type": "mana_affinity",
            "label": "Mana Affinity",
            "description": "+1 mana per regeneration tick.",
        },
    },
    "halfling": {
        "stat_mods": {"str": -2, "agi": 2, "int": -1, "wis": 0, "hlt": 0, "chm": 0},
        "abilities": ["stealth_bonus"],
        "magic_resistance_bonus": 0,
        "xp_modifier": 1.0,
        "two_handed_allowed": False,
        "passive_bonus": {
            "type": "lucky",
            "label": "Lucky",
            "description": "5% chance to negate any incoming hit.",
        },
    },
    "half_elf": {
        "stat_mods": {"str": -1, "agi": 1, "int": 1, "wis": 0, "hlt": -1, "chm": 1},
        "abilities": ["nightvision", "stealth_bonus"],
        "magic_resistance_bonus": 0,
        "xp_modifier": 1.0,
        "two_handed_allowed": True,
        "passive_bonus": {
            "type": "elven_heritage",
            "label": "Elven Heritage",
            "description": "3% chance to resist any incoming condition application.",
        },
    },
    "dark_elf": {
        "stat_mods": {"str": -1, "agi": 2, "int": 2, "wis": 1, "hlt": -1, "chm": -3},
        "abilities": ["nightvision", "stealth_bonus", "magic_resistance"],
        "magic_resistance_bonus": 5,
        "xp_modifier": 1.0,
        "two_handed_allowed": True,
        "passive_bonus": {
            "type": "shadow_born",
            "label": "Shadow Born",
            "description": "+5 accuracy and +5 defense in dungeon rooms.",
        },
    },
    "lizardman": {
        "stat_mods": {"str": 2, "agi": -1, "int": -2, "wis": -1, "hlt": 2, "chm": -2},
        "abilities": ["natural_armor"],
        "magic_resistance_bonus": 0,
        "xp_modifier": 1.0,
        "two_handed_allowed": True,
        "passive_bonus": {
            "type": "scales",
            "label": "Scales",
            "description": "Natural scales grant +2 permanent AC.",
        },
    },
    "minotaur": {
        "stat_mods": {"str": 3, "agi": -1, "int": -2, "wis": -1, "hlt": 2, "chm": -2},
        "abilities": [],
        "magic_resistance_bonus": 0,
        "xp_modifier": 1.0,
        "two_handed_allowed": True,
        "passive_bonus": {
            "type": "brutal_charge",
            "label": "Brutal Charge",
            "description": "+5 accuracy on the first attack of each combat encounter.",
        },
    },
    "ogre": {
        "stat_mods": {"str": 3, "agi": -2, "int": -2, "wis": -1, "hlt": 3, "chm": -3},
        "abilities": [],
        "magic_resistance_bonus": 0,
        "xp_modifier": 1.0,
        "two_handed_allowed": True,
        "passive_bonus": {
            "type": "thick_hide",
            "label": "Thick Hide",
            "description": "Reduce all incoming physical damage by 1.",
        },
    },
    "troll": {
        "stat_mods": {"str": 2, "agi": -1, "int": -1, "wis": -1, "hlt": 2, "chm": -2},
        "abilities": ["regeneration"],
        "magic_resistance_bonus": 0,
        "xp_modifier": 1.0,
        "two_handed_allowed": True,
        "passive_bonus": {
            "type": "regeneration",
            "label": "Regeneration",
            "description": "Regenerate +1 HP per combat round.",
        },
    },
    "centaur": {
        "stat_mods": {"str": 1, "agi": 2, "int": -1, "wis": 1, "hlt": 1, "chm": -1},
        "abilities": ["outdoor_bonus"],
        "magic_resistance_bonus": 0,
        "xp_modifier": 1.0,
        "two_handed_allowed": True,
        "passive_bonus": {
            "type": "swift_stride",
            "label": "Swift Stride",
            "description": "+10% flee success probability.",
        },
    },
    "vampire": {
        "stat_mods": {"str": 1, "agi": 1, "int": 2, "wis": 1, "hlt": -2, "chm": 1},
        "abilities": ["nightvision", "magic_resistance"],
        "magic_resistance_bonus": 5,
        "xp_modifier": 1.0,
        "two_handed_allowed": True,
        "passive_bonus": {
            "type": "life_drain",
            "label": "Life Drain",
            "description": "Gain +1 HP on every successful melee hit.",
        },
    },
}


def get_race(name):
    """Look up a race by name (case-insensitive, spaces→underscores). Returns dict or None."""
    key = name.lower().strip().replace(" ", "_")
    return RACE_REGISTRY.get(key)


def list_races():
    """Return list of (name, dict) tuples sorted alphabetically."""
    return sorted(RACE_REGISTRY.items())
