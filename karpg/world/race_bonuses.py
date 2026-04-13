"""
Race Passive Bonuses

Pure-Python helpers for the per-race passive bonus system.
No Evennia imports.

Each race has one unique passive bonus that fires automatically in combat,
leveling, or stat calculations.

| Race      | Bonus Name     | Effect                                              |
|-----------|----------------|-----------------------------------------------------|
| Human     | Adaptable      | +2 CP on every level-up                            |
| Dwarf     | Stonecunning   | +10 acc / +10 def in dungeon rooms (is_dungeon=True)|
| Elf       | Spell Resist   | 5% chance to resist any incoming condition         |
| Half-Orc  | Blood Rage     | HP < 25% max → +5 accuracy                         |
| Gnome     | Mana Affinity  | +1 mana per regen tick                             |
| Halfling  | Lucky          | 5% proc to negate any incoming hit                 |
| Half-Elf  | Elven Heritage | 3% chance to resist any incoming condition         |
| Dark Elf  | Shadow Born    | +5 acc / +5 def in dungeon rooms                   |
| Lizardman | Scales         | +2 permanent AC from natural armor                 |
| Minotaur  | Brutal Charge  | +5 acc on first attack of each combat              |
| Ogre      | Thick Hide     | Reduce incoming physical damage by 1               |
| Troll     | Regeneration   | +1 HP per combat round                             |
| Centaur   | Swift Stride   | +10% flee success probability                      |
| Vampire   | Life Drain     | +1 HP on every successful melee hit                |
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


def half_elf_condition_resist_check():
    """Return True with 3% probability (Half-Elf Elven Heritage)."""
    return random.random() < 0.03


def dark_elf_shadow_born_bonus(char):
    """
    Return (acc_bonus, def_bonus) for Dark Elf Shadow Born.
    +5 accuracy and +5 defense when in a dungeon room (is_dungeon=True).
    """
    location = getattr(char, "location", None)
    if location and getattr(location.db, "is_dungeon", False):
        return (5, 5)
    return (0, 0)


def lizardman_natural_armor_bonus():
    """Return the flat AC bonus granted by Lizardman natural scales: +2."""
    return 2


def minotaur_brutal_charge_bonus(char):
    """Return +5 accuracy bonus if this is the Minotaur's first combat round, else 0."""
    if getattr(char.ndb, "first_combat_round", False):
        return 5
    return 0


def ogre_thick_hide_dr():
    """Return the flat DR bonus from Ogre Thick Hide: 1."""
    return 1


def troll_combat_regen():
    """Return the HP regenerated per combat round for a Troll: 1."""
    return 1


def centaur_flee_bonus():
    """Return the flee probability bonus for Centaur Swift Stride: 0.10."""
    return 0.10


def vampire_life_drain_heal():
    """Return the HP healed on each successful melee hit for a Vampire: 1."""
    return 1
