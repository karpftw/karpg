"""
Stats

MajorMUD-style stat system helpers. No Evennia imports — pure math.

Stats:
    STR  — melee damage + accuracy
    AGI  — accuracy, defense, attacks per round
    INT  — mana pool size, spell power
    WIS  — mana regeneration
    HLT  — max HP, HP regeneration
    CHM  — merchant prices, social (non-combat for now)

Combatants are expected to have db.str, db.agi, db.int, db.wis, db.hlt, db.chm,
db.ac, db.dr, db.level, and db.formation_rank attributes.
"""

STAT_NAMES = ("str", "agi", "int", "wis", "hlt", "chm")

# Formation rank modifiers: (accuracy_bonus, defense_bonus)
_RANK_MODS = {
    "front": (+15, -10),
    "mid":   (0,   0),
    "back":  (-10, +15),
}


def _stat(combatant, name, default=10):
    val = getattr(combatant.db, name, None)
    return int(val) if val is not None else default


def get_accuracy(combatant):
    """Total accuracy: STR + AGI + level bonus."""
    level = _stat(combatant, "level", 1)
    return _stat(combatant, "str") + _stat(combatant, "agi") + level * 2


def get_defense(combatant):
    """Total defense: AC + AGI/10 secondary dodge bonus."""
    ac = _stat(combatant, "ac", 10)
    agi = _stat(combatant, "agi")
    return ac + agi // 10


def get_max_hp(combatant):
    """HLT-based max HP: 10 + HLT*2 + level*5."""
    hlt = _stat(combatant, "hlt")
    level = _stat(combatant, "level", 1)
    return 10 + hlt * 2 + level * 5


def get_max_mana(combatant):
    """INT-based max mana: INT*3 + level*2."""
    int_ = _stat(combatant, "int")
    level = _stat(combatant, "level", 1)
    return int_ * 3 + level * 2


def get_mana_regen(combatant):
    """WIS-based mana per round: WIS//5 + 1."""
    wis = _stat(combatant, "wis")
    return wis // 5 + 1


def get_attacks_per_round(combatant, attack_mode="normal"):
    """
    AGI + level based attacks per round, capped at 5.

    bash/smash modes halve the attack count (minimum 1).
    """
    agi = _stat(combatant, "agi")
    level = _stat(combatant, "level", 1)
    base = 1 + agi // 15 + level // 5
    base = min(5, max(1, base))

    if attack_mode in ("bash", "smash"):
        return max(1, base // 2)
    return base


def apply_formation_modifier(accuracy, defense, rank):
    """
    Apply front/mid/back formation modifiers.

    Returns (modified_accuracy, modified_defense).
    """
    acc_mod, def_mod = _RANK_MODS.get(rank, (0, 0))
    return accuracy + acc_mod, defense + def_mod
