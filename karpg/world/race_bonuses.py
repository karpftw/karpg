"""
Race Passive Bonuses

Pure-Python helpers for the per-race passive bonus system.
No Evennia imports.

Each race has one unique passive bonus that fires automatically in combat,
leveling, or stat calculations.

| Race     | Bonus Name   | Effect                                              |
|----------|--------------|-----------------------------------------------------|
| Human    | Adaptable    | +2 CP on every level-up                            |
| Dwarf    | Stonecunning | +10 acc / +10 def in dungeon rooms (is_dungeon=True)|
| Elf      | Spell Resist | 5% chance to resist any incoming condition         |
| Half-Orc | Blood Rage   | HP < 25% max → +5 accuracy/damage                  |
| Gnome    | Mana Affinity| +1 mana per regen tick                             |
| Halfling | Lucky        | 5% proc to negate any incoming hit                 |
"""

import random


def get_passive_bonus(race_key):
    """Return the passive_bonus dict for the given race key, or None."""
    from world.races import get_race
    race = get_race(race_key)
    if race is None:
        return None
    return race.get("passive_bonus")


def halfling_lucky_proc():
    """Return True with 5% probability (Halfling Lucky)."""
    return random.random() < 0.05


def elf_condition_resist_check():
    """Return True with 5% probability (Elf Spell Resistance)."""
    return random.random() < 0.05


def half_orc_blood_rage_bonus(char):
    """Return +5 accuracy bonus if Half-Orc is below 25% HP, else 0."""
    hp = getattr(char.db, "hp", 0) or 0
    hp_max = getattr(char.db, "hp_max", 1) or 1
    if hp_max > 0 and hp / hp_max < 0.25:
        return 5
    return 0


def stonecunning_bonus(char):
    """
    Return (acc_bonus, def_bonus) for Dwarf Stonecunning.
    +10 accuracy and +10 defense when in a dungeon room (is_dungeon=True).
    """
    location = getattr(char, "location", None)
    if location and getattr(location.db, "is_dungeon", False):
        return (10, 10)
    return (0, 0)


def gnome_mana_regen_bonus(char):
    """Return +1 mana regen bonus if char is a Gnome, else 0."""
    race = getattr(char.db, "race", None)
    if race == "gnome":
        return 1
    return 0


HUMAN_CP_BONUS = 2  # Extra CP Humans gain per level-up
