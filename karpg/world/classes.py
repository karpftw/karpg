"""
Classes

MajorMUD-style character class definitions. No Evennia imports — pure data.

Each class entry:
    hp_per_level_min  — minimum HP gained per level (for future random rolls)
    hp_per_level_max  — maximum HP gained per level
    hp_per_level_avg  — average used for get_max_hp() calculation
    magic_school      — "mage" | "druid" | "priest" | "kai" | None
    magic_level       — 0–3 (used in mana formula: 6 + 2*magic_level*level)
    weapon_types      — list of allowed weapon type strings, or None (= any)
                        None in the list means unarmed/fist is allowed
    two_handed_allowed — whether two-handed weapons are allowed by class
    combat_rating     — 1–4 (reserved for future combat bonuses)
    abilities         — list of ability tag strings
    armor_types       — list of allowed armor type strings, or None (= any)
"""

# Sentinel meaning "any weapon type is allowed" at the class level.
_ANY = None

CLASS_REGISTRY = {
    "warrior": {
        "hp_per_level_min": 6,
        "hp_per_level_max": 10,
        "hp_per_level_avg": 8,
        "magic_school": None,
        "magic_level": 0,
        "weapon_types": _ANY,      # no restriction
        "two_handed_allowed": True,
        "combat_rating": 4,
        "abilities": ["combat_mastery"],
        "armor_types": _ANY,       # no restriction
    },
    "mage": {
        "hp_per_level_min": 2,
        "hp_per_level_max": 4,
        "hp_per_level_avg": 3,
        "magic_school": "mage",
        "magic_level": 3,
        "weapon_types": ["staff", "dagger"],
        "two_handed_allowed": True,
        "combat_rating": 1,
        "abilities": [],
        "armor_types": ["cloth"],
    },
    "thief": {
        "hp_per_level_min": 3,
        "hp_per_level_max": 6,
        "hp_per_level_avg": 4,
        "magic_school": None,
        "magic_level": 0,
        "weapon_types": ["dagger", "sword", "blade", "axe"],
        "two_handed_allowed": False,
        "combat_rating": 2,
        "abilities": ["backstab", "stealth", "lockpick"],
        "armor_types": ["cloth", "leather"],
    },
    "druid": {
        "hp_per_level_min": 4,
        "hp_per_level_max": 7,
        "hp_per_level_avg": 5,
        "magic_school": "druid",
        "magic_level": 3,
        "weapon_types": ["blunt", "staff", "sickle"],
        "two_handed_allowed": True,
        "combat_rating": 2,
        "abilities": ["hp_regen_outdoor"],
        "armor_types": ["cloth", "leather", "medium"],
    },
    "priest": {
        "hp_per_level_min": 4,
        "hp_per_level_max": 7,
        "hp_per_level_avg": 5,
        "magic_school": "priest",
        "magic_level": 3,
        "weapon_types": ["blunt", "staff"],
        "two_handed_allowed": True,
        "combat_rating": 2,
        "abilities": ["turn_undead"],
        "armor_types": _ANY,       # no restriction
    },
    "warlock": {
        "hp_per_level_min": 5,
        "hp_per_level_max": 8,
        "hp_per_level_avg": 6,
        "magic_school": "mage",
        "magic_level": 2,
        "weapon_types": _ANY,      # no restriction
        "two_handed_allowed": True,
        "combat_rating": 3,
        "abilities": [],
        "armor_types": ["cloth", "leather", "medium"],
    },
    "gypsy": {
        "hp_per_level_min": 3,
        "hp_per_level_max": 5,
        "hp_per_level_avg": 4,
        "magic_school": "mage",
        "magic_level": 2,
        "weapon_types": ["dagger", "sword", "blade"],
        "two_handed_allowed": False,
        "combat_rating": 2,
        "abilities": ["thievery"],
        "armor_types": ["cloth", "leather"],
    },
    "mystic": {
        "hp_per_level_min": 4,
        "hp_per_level_max": 7,
        "hp_per_level_avg": 5,
        "magic_school": "kai",
        "magic_level": 3,
        # None in list means unarmed/fist; "staff" is also allowed
        "weapon_types": [None, "staff"],
        "two_handed_allowed": True,
        "combat_rating": 3,
        "abilities": ["unarmed_forms", "kai_energy"],
        "armor_types": ["cloth"],
    },
}


def get_class(name):
    """Look up a class by name (case-insensitive). Returns dict or None."""
    return CLASS_REGISTRY.get(name.lower().strip())


def list_classes():
    """Return list of (name, dict) tuples sorted alphabetically."""
    return sorted(CLASS_REGISTRY.items())


def can_use_weapon(char_class_key, weapon_type, weapon_two_handed=False):
    """
    Check whether a class can use a weapon.

    weapon_type        — string from db.weapon_type on the weapon, or None for unarmed
    weapon_two_handed  — bool, True if the weapon requires two hands

    Returns (allowed: bool, reason: str).
    """
    cls = get_class(char_class_key)
    if cls is None:
        return True, ""  # unknown class → no restriction

    allowed_types = cls["weapon_types"]

    # No class restriction on weapon types
    if allowed_types is _ANY:
        type_ok = True
    elif weapon_type is None:
        # Unarmed attack — only allowed if None is in the weapon_types list
        type_ok = None in allowed_types
    else:
        type_ok = weapon_type in allowed_types

    if not type_ok:
        return False, f"Your class cannot use {weapon_type or 'unarmed'} weapons."

    if weapon_two_handed and not cls["two_handed_allowed"]:
        return False, "Your class cannot use two-handed weapons."

    return True, ""


def can_wear_armor(char_class_key, armor_type) -> tuple:
    """
    Check whether a class can wear a given armor type.

    Returns (allowed: bool, reason: str).
    """
    cls = get_class(char_class_key)
    if cls is None:
        return True, ""
    allowed = cls.get("armor_types", _ANY)
    if allowed is _ANY:
        return True, ""
    if armor_type in allowed:
        return True, ""
    return False, f"Your class cannot wear {armor_type} armor."


def can_use_spell_school(char_class_key, spell_class_school):
    """
    Return True if the class has access to the given spell school.

    spell_class_school — "mage" | "druid" | "priest" | "kai"
    """
    cls = get_class(char_class_key)
    if cls is None:
        return True  # unknown class → no restriction
    return cls["magic_school"] == spell_class_school
