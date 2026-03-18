"""
Combat Engine

Pure Python MajorMUD-style combat resolution.
No Evennia imports — can be unit-tested without a running server.

Expected combatant db attributes:
    str, agi, int, wis, hlt, chm  — MajorMUD stats (ints)
    ac                             — armor class
    dr                             — damage resistance (flat damage reduction)
    hp, hp_max
    mana, max_mana
    level
    conditions                     — list of condition dicts
    wielded                        — {"main_hand": weapon|None}
    formation_rank                 — "front"|"mid"|"back"

Expected weapon db attributes:
    damage_dice   — e.g. "2d6"
    damage_type   — e.g. "slashing"

Hit formula (MajorMUD): miss_chance = (D² / A²) / 100

Attack mode damage:
    normal:   DR subtracted after multiplier   — (base × 1.0) − DR
    bash:     DR subtracted before multiplier  — (base − DR) × 3.3
    smash:    DR subtracted before multiplier  — (base − DR) × 6.0
    backstab: Like normal but 5× multiplier
    crit:     DR subtracted after multiplier   — (max_weapon_dmg × 2–4) − DR
"""

import random
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Dice helpers
# ---------------------------------------------------------------------------

def roll_die(sides):
    """Roll a single die with the given number of sides."""
    return random.randint(1, sides)


def roll_dice(num, sides):
    """Roll num dice each with sides sides, return list of results."""
    return [roll_die(sides) for _ in range(num)]


def parse_dice(notation):
    """
    Parse a dice notation string such as "2d6", "1d4", or "d8".

    Returns (num, sides) tuple of ints.
    """
    notation = notation.strip().lower()
    if "d" not in notation:
        raise ValueError(f"Invalid dice notation: {notation!r}")
    parts = notation.split("d", 1)
    num = int(parts[0]) if parts[0] else 1
    sides = int(parts[1]) if parts[1] else 1
    return num, sides


def roll_notation(notation):
    """Roll dice from notation string. Returns (total, rolls_list)."""
    num, sides = parse_dice(notation)
    if sides == 0:
        return 0, []
    rolls = roll_dice(num, sides)
    return sum(rolls), rolls


# ---------------------------------------------------------------------------
# Display helpers (Evennia markup, no Evennia imports needed)
# ---------------------------------------------------------------------------

def hp_colour(current, maximum):
    """Return Evennia colour code for a HP value."""
    if maximum <= 0:
        return "|R"
    ratio = current / maximum
    if ratio > 0.6:
        return "|G"
    elif ratio > 0.3:
        return "|Y"
    return "|R"


def hp_bar(current, maximum, width=10):
    """Build a coloured HP bar using Unicode block characters."""
    if maximum <= 0:
        filled = 0
    else:
        filled = max(0, min(width, round(width * current / maximum)))
    empty = width - filled
    colour = hp_colour(current, maximum)
    return f"{colour}{'█' * filled}|x{'░' * empty}|n"


# ---------------------------------------------------------------------------
# Attack modes
# ---------------------------------------------------------------------------

ATTACK_MODES = {
    "normal":    {"multiplier": 1.0,  "accuracy_mod": 1.0,  "attacks": "full"},
    "bash":      {"multiplier": 3.3,  "accuracy_mod": 0.6,  "attacks": "half"},
    "smash":     {"multiplier": 6.0,  "accuracy_mod": 0.4,  "attacks": 1},
    "backstab":  {"multiplier": 5.0,  "accuracy_mod": 1.0,  "attacks": 1},
}


# ---------------------------------------------------------------------------
# Core hit formula
# ---------------------------------------------------------------------------

def calc_miss_chance(total_defense, total_accuracy):
    """
    MajorMUD miss formula: (D² / A²) / 100.

    Returns float in [0.0, 1.0].
    """
    if total_accuracy <= 0:
        return 1.0
    raw = (total_defense ** 2) / (total_accuracy ** 2) / 100
    return min(1.0, max(0.0, raw))


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class AttackResult:
    """Full result of a single weapon attack."""
    attacker_name: str = ""
    target_name: str = ""
    mode: str = "normal"
    hit: bool = False
    critical: bool = False
    miss_chance: float = 0.0
    base_damage: int = 0
    multiplier: float = 1.0
    multiplied_damage: int = 0
    defense_resistance: int = 0
    final_damage: int = 0
    attacker_hp: int = 0
    attacker_max_hp: int = 1
    target_hp: int = 0
    target_max_hp: int = 1
    dodged: bool = False
    parried: bool = False
    blocked: bool = False


@dataclass
class SpellResult:
    """Full result of a single spell cast."""
    caster_name: str = ""
    target_name: str = ""
    spell_key: str = ""
    spell_type: str = "attack"
    hit: bool = False
    damage: int = 0
    heal: int = 0
    mana_cost: int = 0
    mana_spent: int = 0
    condition_applied: str = ""
    caster_hp: int = 0
    caster_max_hp: int = 1
    caster_mana: int = 0
    caster_max_mana: int = 1
    target_hp: int = 0
    target_max_hp: int = 1


# ---------------------------------------------------------------------------
# resolve_attack
# ---------------------------------------------------------------------------

def resolve_attack(attacker, target, mode="normal"):
    """
    Resolve a single weapon attack.

    Applies damage directly to target.db.hp. Returns AttackResult.
    """
    from .stats import get_accuracy, get_defense, apply_formation_modifier, get_crit_chance
    from .conditions import get_combat_modifiers

    result = AttackResult()
    result.attacker_name = attacker.key
    result.target_name = target.key
    result.mode = mode

    mode_def = ATTACK_MODES.get(mode, ATTACK_MODES["normal"])
    acc_scale = mode_def["accuracy_mod"]
    multiplier = mode_def["multiplier"]
    result.multiplier = multiplier

    # Build accuracy and defense totals
    accuracy = get_accuracy(attacker) * acc_scale
    defense = get_defense(target)

    # Formation rank adjustments
    atk_rank = (getattr(attacker.db, "formation_rank", None) or "mid")
    def_rank = (getattr(target.db, "formation_rank", None) or "mid")
    accuracy, _ = apply_formation_modifier(accuracy, 0, atk_rank)
    _, defense = apply_formation_modifier(0, defense, def_rank)

    # Condition modifiers
    cond_acc, cond_def = get_combat_modifiers(attacker, target)
    accuracy = max(1, accuracy + cond_acc)
    defense = max(0, defense + cond_def)

    miss_chance = calc_miss_chance(defense, accuracy)
    result.miss_chance = miss_chance

    roll = random.random()
    result.hit = (roll >= miss_chance)

    if not result.hit:
        result.attacker_hp = attacker.db.hp or 0
        result.attacker_max_hp = attacker.db.hp_max or 1
        result.target_hp = target.db.hp or 0
        result.target_max_hp = target.db.hp_max or 1
        return result

    # Passive defenses: shield block first, then dodge
    from .skills import shield_block_check, dodge_check, skill_level, tick_skill_use
    wielded_t = getattr(target.db, "wielded", None) or {}
    off_hand = wielded_t.get("off_hand")
    off_is_shield = off_hand and getattr(off_hand.db, "item_type", "") == "shield"
    if off_is_shield and skill_level(target, "shield_block") > 0:
        if shield_block_check(target):
            result.hit = False
            result.blocked = True
            tick_skill_use(target, "shield_block")
    if result.hit and skill_level(target, "dodge") > 0:
        if dodge_check(target):
            result.hit = False
            result.dodged = True
            tick_skill_use(target, "dodge")

    if not result.hit:
        result.attacker_hp = attacker.db.hp or 0
        result.attacker_max_hp = attacker.db.hp_max or 1
        result.target_hp = target.db.hp or 0
        result.target_max_hp = target.db.hp_max or 1
        return result

    # Critical: INT-driven — baseline INT 10 → 10%, capped 25%
    crit_chance = get_crit_chance(attacker)
    result.critical = (roll >= (1.0 - crit_chance))

    # Weapon base damage
    wielded = getattr(attacker.db, "wielded", None) or {}
    weapon = wielded.get("main_hand")
    weapon_notation = "1d4"
    weapon_sides = 4
    if weapon and getattr(weapon.db, "damage_dice", None):
        weapon_notation = weapon.db.damage_dice
        try:
            _, weapon_sides = parse_dice(weapon_notation)
        except ValueError:
            pass
    # Unarmed: check Mystic unarmed form
    if not weapon:
        from .skills import unarmed_damage_dice, skill_level as _sl
        if _sl(attacker, "unarmed_forms") > 0:
            weapon_notation = unarmed_damage_dice(attacker)
            try:
                _, weapon_sides = parse_dice(weapon_notation)
            except ValueError:
                pass

    base_dmg, _ = roll_notation(weapon_notation)

    # Combat mastery damage bonus
    from .skills import combat_mastery_bonus
    if skill_level(attacker, "combat_mastery") > 0:
        _, dmg_bonus = combat_mastery_bonus(attacker)
        base_dmg = max(1, base_dmg + dmg_bonus)

    result.base_damage = base_dmg

    dr = _get_dr(target)
    result.defense_resistance = dr

    if result.critical:
        # Crit: 2–4× of max weapon damage, then subtract DR
        crit_mult = random.uniform(2.0, 4.0)
        raw = int(weapon_sides * crit_mult)
        result.multiplied_damage = raw
        result.final_damage = max(0, raw - dr)
    elif mode in ("bash", "smash"):
        # DR before multiplier
        after_dr = max(0, base_dmg - dr)
        result.multiplied_damage = int(after_dr * multiplier)
        result.final_damage = result.multiplied_damage
    else:
        # normal/backstab: DR after multiplier
        result.multiplied_damage = int(base_dmg * multiplier)
        result.final_damage = max(0, result.multiplied_damage - dr)

    # Parry: halve damage for normal-mode attacks
    from .skills import parry_check
    if result.hit and skill_level(target, "parry") > 0 and mode == "normal":
        if parry_check(target):
            result.final_damage = max(1, result.final_damage // 2)
            result.parried = True
            tick_skill_use(target, "parry")

    # Apply damage
    target.db.hp = max(0, (target.db.hp or 0) - result.final_damage)

    # Update threat table if target is an NPC with one
    _update_threat(target, attacker, result.final_damage)

    result.attacker_hp = attacker.db.hp or 0
    result.attacker_max_hp = attacker.db.hp_max or 1
    result.target_hp = target.db.hp
    result.target_max_hp = target.db.hp_max or 1
    return result


def _get_dr(target):
    """Get the flat damage resistance value from target."""
    return getattr(target.db, "dr", 0) or 0


def _update_threat(target, attacker, damage):
    """Update the threat table on an NPC target if it has one."""
    threat = getattr(target.db, "threat_table", None)
    if threat is None:
        return
    aid = attacker.id
    threat[aid] = threat.get(aid, 0) + damage
    target.db.threat_table = threat


# ---------------------------------------------------------------------------
# resolve_spell
# ---------------------------------------------------------------------------

def resolve_spell(caster, target, spell):
    """
    Resolve a mana-based spell cast.

    Applies damage/healing directly to target.db.hp and deducts mana from
    caster.db.mana. Returns SpellResult.
    """
    from .stats import get_accuracy, get_defense
    from .conditions import apply_condition

    result = SpellResult()
    result.caster_name = caster.key
    result.target_name = target.key
    result.spell_key = spell["key"]
    result.spell_type = spell.get("spell_type", "attack")
    result.mana_cost = spell.get("mana_cost", 0)

    # Deduct mana (clamped to 0)
    current_mana = caster.db.mana or 0
    spent = min(current_mana, result.mana_cost)
    caster.db.mana = max(0, current_mana - result.mana_cost)
    result.mana_spent = spent

    spell_type = result.spell_type

    if spell_type == "heal":
        notation = spell.get("damage_dice", "1d6")
        heal, _ = roll_notation(notation)
        hp_max = target.db.hp_max or 1
        target.db.hp = min(hp_max, (target.db.hp or 0) + heal)
        result.heal = heal
        result.hit = True

    elif spell_type == "attack":
        acc = get_accuracy(caster) * spell.get("accuracy_mod", 1.0)
        defense = get_defense(target)
        miss_chance = calc_miss_chance(max(0, defense), max(1, acc))
        result.hit = (random.random() >= miss_chance)
        if result.hit:
            notation = spell.get("damage_dice", "1d6")
            dmg, _ = roll_notation(notation)
            target.db.hp = max(0, (target.db.hp or 0) - dmg)
            result.damage = dmg
            _update_threat(target, caster, dmg)

    elif spell_type == "save":
        # Target rolls their save_stat + d20 vs caster INT-based DC
        notation = spell.get("damage_dice", "1d6")
        dmg, _ = roll_notation(notation)
        save_stat = spell.get("save_stat", "agi")
        target_stat_val = getattr(target.db, save_stat, 10) or 10
        caster_int = getattr(caster.db, "int", 10) or 10
        spell_dc = 10 + caster_int // 3
        save_roll = roll_die(20) + target_stat_val // 3
        if save_roll >= spell_dc:
            dmg = dmg // 2  # half damage on successful save
        target.db.hp = max(0, (target.db.hp or 0) - dmg)
        result.damage = dmg
        result.hit = True
        _update_threat(target, caster, dmg)

        # Apply condition if the spell has one and the save failed
        applies = spell.get("applies_condition")
        if applies and save_roll < spell_dc:
            dur = spell.get("condition_duration", -1)
            apply_condition(target, applies, duration=dur, source=caster.key)
            result.condition_applied = applies

    result.caster_hp = caster.db.hp or 0
    result.caster_max_hp = caster.db.hp_max or 1
    result.caster_mana = caster.db.mana or 0
    result.caster_max_mana = caster.db.max_mana or 1
    result.target_hp = target.db.hp or 0
    result.target_max_hp = target.db.hp_max or 1
    return result


# ---------------------------------------------------------------------------
# roll_flee
# ---------------------------------------------------------------------------

def roll_flee(combatant):
    """
    AGI-based flee success check.

    Base 20% + 1% per AGI point, capped at 90%.
    Returns True on success.
    """
    agi = getattr(combatant.db, "agi", 10) or 10
    chance = min(0.9, 0.20 + agi / 100.0)
    return random.random() < chance
