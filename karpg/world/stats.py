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

from world.classes import get_class
from world.races import get_race

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


def get_carry_capacity(combatant):
    """STR-based carry cap: STR * 48 lbs (baseline STR 10 → 480 lbs)."""
    from world.skills import encumbrance_bonus_multiplier
    return int(_stat(combatant, "str") * 48 * encumbrance_bonus_multiplier(combatant))


def get_carried_weight(char):
    """Sum of db.weight for every item in char.contents, plus gold weight (0.01 lbs/GP)."""
    from world.economy import gold_weight
    item_weight = sum((getattr(item.db, "weight", 0) or 0) for item in char.contents)
    return item_weight + gold_weight(char)


def get_accuracy(combatant):
    """Total accuracy: STR + AGI + level bonus, minus encumbrance penalty."""
    level = _stat(combatant, "level", 1)
    acc = _stat(combatant, "str") + _stat(combatant, "agi") + level * 2

    carried = getattr(combatant.db, "carrying_weight", 0) or 0
    cap = get_carry_capacity(combatant)
    if carried > cap:
        over    = carried - cap
        penalty = int(min(20, (over / max(cap, 1)) * 20))
        acc    -= penalty

    # Combat mastery accuracy bonus
    from world.skills import combat_mastery_bonus, skill_level
    if skill_level(combatant, "combat_mastery") > 0:
        acc_bonus, _ = combat_mastery_bonus(combatant)
        acc += acc_bonus

    # Battle cry buff (tracked in db.battlecry_bonus)
    acc += getattr(combatant.db, "battlecry_bonus", 0) * 5

    return acc


def get_defense(combatant):
    """Total defense: AC + AGI/10 secondary dodge bonus."""
    ac = _stat(combatant, "ac", 10)
    agi = _stat(combatant, "agi")
    return ac + agi // 10


def get_max_hp(combatant):
    """Class + HLT based max HP: 10 + HLT*2 + hp_per_level_avg * (level-1)."""
    hlt = _stat(combatant, "hlt")
    level = _stat(combatant, "level", 1)
    char_class = getattr(combatant.db, "char_class", None)
    cls = get_class(char_class) if char_class else None
    hp_per_level = cls["hp_per_level_avg"] if cls else 5
    bonus_hp = getattr(combatant.db, "bonus_hp", 0) or 0
    return 10 + hlt * 2 + hp_per_level * (level - 1) + bonus_hp


def get_max_mana(combatant):
    """MajorMUD authentic mana: 6 + 2 * magic_level * level. Returns 0 for non-casters and Mystics."""
    char_class = getattr(combatant.db, "char_class", None)
    cls = get_class(char_class) if char_class else None
    if cls is None:
        # Default fallback for characters without a class set
        int_ = _stat(combatant, "int")
        level = _stat(combatant, "level", 1)
        return int_ * 3 + level * 2
    magic_level = cls["magic_level"]
    if magic_level == 0 or cls["magic_school"] == "kai":
        return 0
    level = _stat(combatant, "level", 1)
    return 6 + 2 * magic_level * level


def get_max_kai(combatant):
    """Kai energy for Mystics: 6 + 2*3*level + wis. Returns 0 for non-Mystics."""
    char_class = getattr(combatant.db, "char_class", None)
    cls = get_class(char_class) if char_class else None
    if cls is None or cls.get("magic_school") != "kai":
        return 0
    level = _stat(combatant, "level", 1)
    wis = _stat(combatant, "wis")
    return 6 + 2 * 3 * level + wis


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


def get_hp_regen(combatant):
    """HLT-based HP regen per rest tick: HLT//5 + 1.
    Baseline HLT 10 → 3 HP/tick (12 HP/min). Max HLT 20 → 5 HP/tick.
    """
    hlt = _stat(combatant, "hlt")
    return hlt // 5 + 1


def get_crit_chance(combatant) -> float:
    """INT-based crit chance: 1% per INT point, capped at 25%.
    Baseline INT 10 → 10%, max INT 20 → 20%.
    """
    int_ = _stat(combatant, "int")
    return min(0.25, int_ * 0.01)


def apply_formation_modifier(accuracy, defense, rank):
    """
    Apply front/mid/back formation modifiers.

    Returns (modified_accuracy, modified_defense).
    """
    acc_mod, def_mod = _RANK_MODS.get(rank, (0, 0))
    return accuracy + acc_mod, defense + def_mod


def recalc_stats(char):
    """
    Recompute racial stats, hp_max, max_mana, and max_kai after a class or race change.

    Safe to call on existing characters: bootstraps base_* from db.* if not yet set.
    Does NOT restore current hp/mana/kai to full — callers do that explicitly when desired.
    """
    # 1. Bootstrap base stats from current db values if not yet set (migration path)
    for stat in STAT_NAMES:
        base_key = f"base_{stat}"
        if getattr(char.db, base_key, None) is None:
            setattr(char.db, base_key, getattr(char.db, stat, None) or 10)

    # 2. Apply racial stat mods
    race_key = getattr(char.db, "race", "human") or "human"
    race = get_race(race_key)
    if race:
        for stat in STAT_NAMES:
            base = getattr(char.db, f"base_{stat}", 10) or 10
            mod = race["stat_mods"].get(stat, 0)
            setattr(char.db, stat, base + mod)
        # 3. Apply racial magic resistance bonus
        base_mr = getattr(char.db, "base_magic_resistance", 0) or 0
        char.db.magic_resistance = base_mr + race.get("magic_resistance_bonus", 0)
        # 4. Store racial two-handed restriction
        char.db.race_two_handed_allowed = race["two_handed_allowed"]

    # 5–7. Recalculate derived maximums
    char.db.hp_max  = get_max_hp(char)
    char.db.max_mana = get_max_mana(char)
    char.db.max_kai  = get_max_kai(char)

    # 8. Clamp current values to new maximums (don't restore to full)
    char.db.hp   = min(char.db.hp or 1, char.db.hp_max)
    char.db.mana = min(char.db.mana or 0, char.db.max_mana)
    char.db.kai  = min(char.db.kai or 0, char.db.max_kai)

    # 9. Reapply racial auto-grant skills (safe to call repeatedly)
    from world.skills import auto_grant_racial_skills
    auto_grant_racial_skills(char)
