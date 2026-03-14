"""
Spells

Spell definitions as plain dicts, parallel to weapon prototypes.
No Evennia imports — pure data and lookup functions.

Spell dict keys:
    key          (str)  - unique identifier / display name
    level        (int)  - 0 = cantrip, 1-9 = spell level
    school       (str)  - spell school (evocation, necromancy, etc.)
    spell_type   (str)  - "attack" | "save" | "utility"
    damage_dice  (str)  - dice notation for damage
    damage_type  (str)  - fire, cold, lightning, etc.
    attack_stat  (str)  - ability used for spell attacks (int/wis/cha)
    save_stat    (str|None) - ability the target saves with
    aoe          (bool) - area-of-effect spell
    range        (str)  - "melee" | "ranged"
    description  (str)  - short flavour text
    special      (str|None) - tag for special-case handling in the engine
    applies_condition (str|None) - condition applied on hit/failed save
"""

# ---------------------------------------------------------------------------
# Cantrips (level 0)
# ---------------------------------------------------------------------------

FIRE_BOLT = {
    "key": "fire bolt",
    "level": 0,
    "school": "evocation",
    "spell_type": "attack",
    "damage_dice": "1d10",
    "damage_type": "fire",
    "attack_stat": "int",
    "save_stat": None,
    "aoe": False,
    "range": "ranged",
    "description": "A mote of flame streaks toward the target.",
    "special": None,
    "applies_condition": None,
}

CHILL_TOUCH = {
    "key": "chill touch",
    "level": 0,
    "school": "necromancy",
    "spell_type": "attack",
    "damage_dice": "1d8",
    "damage_type": "necrotic",
    "attack_stat": "int",
    "save_stat": None,
    "aoe": False,
    "range": "ranged",
    "description": "A ghostly skeletal hand reaches for the target.",
    "special": None,
    "applies_condition": None,
}

SACRED_FLAME = {
    "key": "sacred flame",
    "level": 0,
    "school": "evocation",
    "spell_type": "save",
    "damage_dice": "1d8",
    "damage_type": "radiant",
    "attack_stat": "wis",
    "save_stat": "dex",
    "aoe": False,
    "range": "ranged",
    "description": "Flame-like radiance descends upon the target.",
    "special": None,
    "applies_condition": None,
}

TOLL_THE_DEAD = {
    "key": "toll the dead",
    "level": 0,
    "school": "necromancy",
    "spell_type": "save",
    "damage_dice": "1d8",
    "damage_type": "necrotic",
    "attack_stat": "wis",
    "save_stat": "wis",
    "aoe": False,
    "range": "ranged",
    "description": "A dolorous bell toll causes necrotic energy to wash over "
                   "the target. Deals 1d12 if the target is already wounded.",
    "special": "toll_the_dead",
    "applies_condition": None,
}

# ---------------------------------------------------------------------------
# Level 1
# ---------------------------------------------------------------------------

MAGIC_MISSILE = {
    "key": "magic missile",
    "level": 1,
    "school": "evocation",
    "spell_type": "utility",
    "damage_dice": "1d4",
    "damage_type": "force",
    "attack_stat": "int",
    "save_stat": None,
    "aoe": False,
    "range": "ranged",
    "description": "Three glowing darts of force unerringly strike the target.",
    "special": "magic_missile",
    "applies_condition": None,
}

BURNING_HANDS = {
    "key": "burning hands",
    "level": 1,
    "school": "evocation",
    "spell_type": "save",
    "damage_dice": "3d6",
    "damage_type": "fire",
    "attack_stat": "int",
    "save_stat": "dex",
    "aoe": True,
    "range": "melee",
    "description": "A thin sheet of flames shoots forth from your fingertips.",
    "special": None,
    "applies_condition": None,
}

THUNDERWAVE = {
    "key": "thunderwave",
    "level": 1,
    "school": "evocation",
    "spell_type": "save",
    "damage_dice": "2d8",
    "damage_type": "thunder",
    "attack_stat": "int",
    "save_stat": "con",
    "aoe": True,
    "range": "melee",
    "description": "A wave of thunderous force sweeps out from you.",
    "special": None,
    "applies_condition": None,
}

CURE_WOUNDS = {
    "key": "cure wounds",
    "level": 1,
    "school": "evocation",
    "spell_type": "utility",
    "damage_dice": "2d8",
    "damage_type": "healing",
    "attack_stat": "int",
    "save_stat": None,
    "aoe": False,
    "range": "melee",
    "description": "A creature you touch regains hit points.",
    "special": "cure_wounds",
    "applies_condition": None,
}

# ---------------------------------------------------------------------------
# Level 2
# ---------------------------------------------------------------------------

SCORCHING_RAY = {
    "key": "scorching ray",
    "level": 2,
    "school": "evocation",
    "spell_type": "attack",
    "damage_dice": "2d6",
    "damage_type": "fire",
    "attack_stat": "int",
    "save_stat": None,
    "aoe": False,
    "range": "ranged",
    "description": "You create three rays of fire and hurl them at targets.",
    "special": "scorching_ray",
    "applies_condition": None,
}

SHATTER = {
    "key": "shatter",
    "level": 2,
    "school": "evocation",
    "spell_type": "save",
    "damage_dice": "3d8",
    "damage_type": "thunder",
    "attack_stat": "int",
    "save_stat": "con",
    "aoe": True,
    "range": "ranged",
    "description": "A sudden loud noise painfully intense erupts.",
    "special": None,
    "applies_condition": None,
}

HOLD_PERSON = {
    "key": "hold person",
    "level": 2,
    "school": "enchantment",
    "spell_type": "save",
    "damage_dice": "0d0",
    "damage_type": "none",
    "attack_stat": "int",
    "save_stat": "wis",
    "aoe": False,
    "range": "ranged",
    "description": "The target must succeed on a WIS save or be paralyzed.",
    "special": "hold_person",
    "applies_condition": "paralyzed",
}

# ---------------------------------------------------------------------------
# Level 3
# ---------------------------------------------------------------------------

FIREBALL = {
    "key": "fireball",
    "level": 3,
    "school": "evocation",
    "spell_type": "save",
    "damage_dice": "8d6",
    "damage_type": "fire",
    "attack_stat": "int",
    "save_stat": "dex",
    "aoe": True,
    "range": "ranged",
    "description": "A bright streak flashes to a point and blossoms into a "
                   "roaring explosion of flame.",
    "special": None,
    "applies_condition": None,
}

LIGHTNING_BOLT = {
    "key": "lightning bolt",
    "level": 3,
    "school": "evocation",
    "spell_type": "save",
    "damage_dice": "8d6",
    "damage_type": "lightning",
    "attack_stat": "int",
    "save_stat": "dex",
    "aoe": True,
    "range": "ranged",
    "description": "A stroke of lightning forming a line blasts out from you.",
    "special": None,
    "applies_condition": None,
}

COUNTERSPELL = {
    "key": "counterspell",
    "level": 3,
    "school": "abjuration",
    "spell_type": "utility",
    "damage_dice": "0d0",
    "damage_type": "none",
    "attack_stat": "int",
    "save_stat": None,
    "aoe": False,
    "range": "ranged",
    "description": "You attempt to interrupt a creature casting a spell.",
    "special": "counterspell",
    "applies_condition": None,
}

# ---------------------------------------------------------------------------
# Level 4
# ---------------------------------------------------------------------------

ICE_STORM = {
    "key": "ice storm",
    "level": 4,
    "school": "evocation",
    "spell_type": "save",
    "damage_dice": "2d8",
    "damage_type": "bludgeoning",
    "attack_stat": "int",
    "save_stat": "dex",
    "aoe": True,
    "range": "ranged",
    "description": "Hail stones pound the area, dealing bludgeoning and cold "
                   "damage.",
    "special": "ice_storm",
    "applies_condition": None,
    "secondary_damage_dice": "4d6",
    "secondary_damage_type": "cold",
}

# ---------------------------------------------------------------------------
# Level 5
# ---------------------------------------------------------------------------

CONE_OF_COLD = {
    "key": "cone of cold",
    "level": 5,
    "school": "evocation",
    "spell_type": "save",
    "damage_dice": "8d8",
    "damage_type": "cold",
    "attack_stat": "int",
    "save_stat": "con",
    "aoe": True,
    "range": "melee",
    "description": "A blast of cold air erupts from your hands.",
    "special": None,
    "applies_condition": None,
}

HOLD_MONSTER = {
    "key": "hold monster",
    "level": 5,
    "school": "enchantment",
    "spell_type": "save",
    "damage_dice": "0d0",
    "damage_type": "none",
    "attack_stat": "wis",
    "save_stat": "wis",
    "aoe": False,
    "range": "ranged",
    "description": "The target must succeed on a WIS save or be paralyzed.",
    "special": "hold_person",
    "applies_condition": "paralyzed",
}

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_ALL_SPELLS = [
    # Cantrips
    FIRE_BOLT, CHILL_TOUCH, SACRED_FLAME, TOLL_THE_DEAD,
    # Level 1
    MAGIC_MISSILE, BURNING_HANDS, THUNDERWAVE, CURE_WOUNDS,
    # Level 2
    SCORCHING_RAY, SHATTER, HOLD_PERSON,
    # Level 3
    FIREBALL, LIGHTNING_BOLT, COUNTERSPELL,
    # Level 4
    ICE_STORM,
    # Level 5
    CONE_OF_COLD, HOLD_MONSTER,
]

SPELL_REGISTRY = {spell["key"]: spell for spell in _ALL_SPELLS}


def get_spell(name):
    """
    Look up a spell by name (case-insensitive).

    Returns:
        dict or None
    """
    return SPELL_REGISTRY.get(name.lower())


def list_spells(level=None):
    """
    Return a list of spell dicts, optionally filtered by level.

    Results are sorted by ``(level, key)``.
    """
    spells = _ALL_SPELLS if level is None else [
        s for s in _ALL_SPELLS if s["level"] == level
    ]
    return sorted(spells, key=lambda s: (s["level"], s["key"]))
