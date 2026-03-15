"""
Spells

Mana-based spell definitions. No Evennia imports — pure data and lookup.

Spell dict keys:
    key          (str)  - unique identifier / display name
    school       (str)  - evocation, necromancy, etc.
    spell_type   (str)  - "attack" | "save" | "heal" | "utility"
    mana_cost    (int)  - mana consumed when cast
    damage_dice  (str)  - dice notation for damage or healing
    damage_type  (str)  - fire, cold, lightning, healing, etc.
    attack_stat  (str)  - caster stat used for accuracy (int/wis)
    save_stat    (str|None) - stat the target saves with (agi/wis/str)
    accuracy_mod (float) - multiplier on caster accuracy (default 1.0)
    aoe          (bool) - area-of-effect (hits all enemies in room)
    description  (str)  - short flavour text
"""

# ---------------------------------------------------------------------------
# Attack spells
# ---------------------------------------------------------------------------

FIRE_BOLT = {
    "key": "fire bolt",
    "school": "evocation",
    "spell_type": "attack",
    "mana_cost": 4,
    "damage_dice": "1d10",
    "damage_type": "fire",
    "attack_stat": "int",
    "save_stat": None,
    "accuracy_mod": 1.0,
    "aoe": False,
    "description": "A mote of flame streaks toward the target.",
}

CHILL_TOUCH = {
    "key": "chill touch",
    "school": "necromancy",
    "spell_type": "attack",
    "mana_cost": 4,
    "damage_dice": "1d8",
    "damage_type": "necrotic",
    "attack_stat": "int",
    "save_stat": None,
    "accuracy_mod": 1.0,
    "aoe": False,
    "description": "A ghostly skeletal hand reaches for the target.",
}

SCORCHING_RAY = {
    "key": "scorching ray",
    "school": "evocation",
    "spell_type": "attack",
    "mana_cost": 10,
    "damage_dice": "3d6",
    "damage_type": "fire",
    "attack_stat": "int",
    "save_stat": None,
    "accuracy_mod": 1.0,
    "aoe": False,
    "description": "Three rays of searing fire streak toward the target.",
}

LIGHTNING_BOLT = {
    "key": "lightning bolt",
    "school": "evocation",
    "spell_type": "attack",
    "mana_cost": 15,
    "damage_dice": "6d6",
    "damage_type": "lightning",
    "attack_stat": "int",
    "save_stat": None,
    "accuracy_mod": 1.2,
    "aoe": False,
    "description": "A stroke of crackling lightning blasts toward the target.",
}

# ---------------------------------------------------------------------------
# Save spells
# ---------------------------------------------------------------------------

SACRED_FLAME = {
    "key": "sacred flame",
    "school": "evocation",
    "spell_type": "save",
    "mana_cost": 4,
    "damage_dice": "1d8",
    "damage_type": "radiant",
    "attack_stat": "wis",
    "save_stat": "agi",
    "accuracy_mod": 1.0,
    "aoe": False,
    "description": "Flame-like radiance descends on the target; AGI save halves.",
}

BURNING_HANDS = {
    "key": "burning hands",
    "school": "evocation",
    "spell_type": "save",
    "mana_cost": 8,
    "damage_dice": "3d6",
    "damage_type": "fire",
    "attack_stat": "int",
    "save_stat": "agi",
    "accuracy_mod": 1.0,
    "aoe": True,
    "description": "Sheets of flame erupt from your hands, hitting all enemies; AGI save halves.",
}

FIREBALL = {
    "key": "fireball",
    "school": "evocation",
    "spell_type": "save",
    "mana_cost": 15,
    "damage_dice": "8d6",
    "damage_type": "fire",
    "attack_stat": "int",
    "save_stat": "agi",
    "accuracy_mod": 1.0,
    "aoe": True,
    "description": "A roaring explosion of flame engulfs all enemies; AGI save halves.",
}

HOLD_PERSON = {
    "key": "hold person",
    "school": "enchantment",
    "spell_type": "save",
    "mana_cost": 10,
    "damage_dice": "0d0",
    "damage_type": "none",
    "attack_stat": "int",
    "save_stat": "wis",
    "accuracy_mod": 1.0,
    "aoe": False,
    "applies_condition": "paralyzed",
    "condition_duration": 3,
    "description": "The target must succeed on a WIS save or be paralyzed for 3 rounds.",
}

THUNDERWAVE = {
    "key": "thunderwave",
    "school": "evocation",
    "spell_type": "save",
    "mana_cost": 8,
    "damage_dice": "2d8",
    "damage_type": "thunder",
    "attack_stat": "int",
    "save_stat": "str",
    "accuracy_mod": 1.0,
    "aoe": True,
    "description": "A wave of thunderous force hits all enemies; STR save halves.",
}

# ---------------------------------------------------------------------------
# Heal spells
# ---------------------------------------------------------------------------

CURE_WOUNDS = {
    "key": "cure wounds",
    "school": "evocation",
    "spell_type": "heal",
    "mana_cost": 8,
    "damage_dice": "2d8",
    "damage_type": "healing",
    "attack_stat": "wis",
    "save_stat": None,
    "accuracy_mod": 1.0,
    "aoe": False,
    "description": "Healing energy flows into you, restoring hit points.",
}

HEAL = {
    "key": "heal",
    "school": "evocation",
    "spell_type": "heal",
    "mana_cost": 20,
    "damage_dice": "6d8",
    "damage_type": "healing",
    "attack_stat": "wis",
    "save_stat": None,
    "accuracy_mod": 1.0,
    "aoe": False,
    "description": "Powerful restorative magic floods your body.",
}

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_ALL_SPELLS = [
    # Attack
    FIRE_BOLT, CHILL_TOUCH, SCORCHING_RAY, LIGHTNING_BOLT,
    # Save
    SACRED_FLAME, BURNING_HANDS, FIREBALL, HOLD_PERSON, THUNDERWAVE,
    # Heal
    CURE_WOUNDS, HEAL,
]

SPELL_REGISTRY = {spell["key"]: spell for spell in _ALL_SPELLS}


def get_spell(name):
    """Look up a spell by name (case-insensitive). Returns dict or None."""
    return SPELL_REGISTRY.get(name.lower().strip())


def list_spells(spell_type=None):
    """Return list of spell dicts, optionally filtered by spell_type."""
    spells = _ALL_SPELLS if spell_type is None else [
        s for s in _ALL_SPELLS if s["spell_type"] == spell_type
    ]
    return sorted(spells, key=lambda s: (s["mana_cost"], s["key"]))
