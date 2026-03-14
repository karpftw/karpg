"""
Combat Engine

Pure Python combat resolution logic for 5e-style turn-based combat.
No Evennia imports — this module can be unit-tested without a running server.

All combatant objects are expected to have a `db` attribute namespace with:
    ability_scores  (dict)  - {"str": int, "dex": int, ...}
    level           (int)
    ac              (int)
    hp              (int)
    hp_max          (int)
    conditions      (list)  - list of condition dicts
    damage_resistances    (list of str)
    damage_vulnerabilities (list of str)
    damage_immunities     (list of str)
    death_saves     (dict)  - {"successes": int, "failures": int}
    wielded         (dict)  - {"main_hand": weapon|None, "off_hand": weapon|None}
    proficiency_bonus (int)

Weapon objects are expected to have a `db` namespace with:
    damage_dice   (str)
    damage_type   (str)
    attack_range  (str)  - "melee" | "ranged"
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
    """Roll *num* dice each with *sides* sides, return list of results."""
    return [roll_die(sides) for _ in range(num)]


def parse_dice(notation):
    """
    Parse a dice notation string such as ``"2d6"``, ``"1d4"``, or ``"d8"``.

    Returns:
        (num, sides) tuple of ints.
    """
    notation = notation.strip().lower()
    if "d" not in notation:
        raise ValueError(f"Invalid dice notation: {notation!r}")
    parts = notation.split("d", 1)
    num = int(parts[0]) if parts[0] else 1
    sides = int(parts[1])
    return num, sides


def roll_notation(notation):
    """
    Roll dice described by *notation* (e.g. ``"2d6"``).

    Returns:
        (total, rolls_list) — the sum and individual die results.
    """
    num, sides = parse_dice(notation)
    rolls = roll_dice(num, sides)
    return sum(rolls), rolls


# ---------------------------------------------------------------------------
# Ability / proficiency helpers
# ---------------------------------------------------------------------------

def ability_mod(score):
    """Return the ability modifier for a given ability score."""
    return (score - 10) // 2


def prof_bonus(level):
    """Return the proficiency bonus for a given character level."""
    return 2 + (level - 1) // 4


def get_mod(combatant, stat):
    """
    Return the ability modifier for *stat* (e.g. ``"str"``, ``"dex"``).

    Reads ``combatant.db.ability_scores``.
    """
    scores = combatant.db.ability_scores or {}
    score = scores.get(stat, 10)
    return ability_mod(score)


# ---------------------------------------------------------------------------
# d20 rolls
# ---------------------------------------------------------------------------

def roll_d20(advantage=False, disadvantage=False):
    """
    Roll a d20, optionally with advantage or disadvantage.

    If both advantage and disadvantage apply they cancel out (straight roll).

    Returns:
        (result, rolls_list) — the effective result and all d20s rolled.
    """
    if advantage and disadvantage:
        # Cancel out
        advantage = disadvantage = False

    if advantage:
        rolls = roll_dice(2, 20)
        return max(rolls), rolls
    elif disadvantage:
        rolls = roll_dice(2, 20)
        return min(rolls), rolls
    else:
        r = roll_die(20)
        return r, [r]


def roll_initiative(combatant):
    """
    Roll initiative for *combatant*: d20 + DEX modifier.

    Returns:
        (total, d20_roll)
    """
    d20 = roll_die(20)
    dex_mod = get_mod(combatant, "dex")
    return d20 + dex_mod, d20


# ---------------------------------------------------------------------------
# Display helpers (Evennia markup, no Evennia imports needed)
# ---------------------------------------------------------------------------

def hp_colour(current, maximum):
    """Return the Evennia colour code for a HP value."""
    if maximum <= 0:
        return "|R"
    ratio = current / maximum
    if ratio > 0.6:
        return "|G"
    elif ratio > 0.3:
        return "|Y"
    else:
        return "|R"


def hp_bar(current, maximum, width=10):
    """
    Build a coloured HP bar using Unicode block characters.

    Uses ``\u2588`` (full block) for filled and ``\u2591`` (light shade) for
    empty portions. Colour follows the hp_colour scheme.
    """
    if maximum <= 0:
        filled = 0
    else:
        filled = max(0, min(width, round(width * current / maximum)))
    empty = width - filled
    colour = hp_colour(current, maximum)
    return f"{colour}{'█' * filled}|x{'░' * empty}|n"


# ---------------------------------------------------------------------------
# Saving throws
# ---------------------------------------------------------------------------

def ability_save(combatant, stat, dc):
    """
    Roll an ability saving throw for *combatant*.

    Returns:
        (d20_roll, total, success)
    """
    d20 = roll_die(20)
    mod = get_mod(combatant, stat)
    total = d20 + mod
    return d20, total, total >= dc


# ---------------------------------------------------------------------------
# Attack modifiers from conditions
# ---------------------------------------------------------------------------

def get_attack_modifiers(attacker, defender, is_melee=True):
    """
    Determine advantage / disadvantage on an attack roll based on conditions
    of both attacker and defender.

    Returns:
        (advantage: bool, disadvantage: bool)
    """
    # Import here to avoid top-level cross-dependency issues; conditions is
    # pure Python so this is fine.
    from .conditions import get_attack_modifiers as _cond_mods
    return _cond_mods(attacker, defender, is_melee=is_melee)


# ---------------------------------------------------------------------------
# Attack result dataclass
# ---------------------------------------------------------------------------

@dataclass
class AttackResult:
    """Encapsulates the full result of a single weapon attack."""
    attacker_name: str = ""
    defender_name: str = ""
    weapon_name: str = "Unarmed"
    d20_rolls: list = field(default_factory=list)
    d20_result: int = 0
    attack_bonus: int = 0
    attack_total: int = 0
    target_ac: int = 10
    is_crit: bool = False
    is_hit: bool = False
    is_miss: bool = False
    damage_rolls: list = field(default_factory=list)
    damage_bonus: int = 0
    damage_total: int = 0
    damage_type: str = "bludgeoning"
    final_damage: int = 0
    resistance_applied: bool = False
    vulnerability_applied: bool = False
    immunity_applied: bool = False


# ---------------------------------------------------------------------------
# resolve_attack
# ---------------------------------------------------------------------------

def resolve_attack(attacker, defender, weapon=None, advantage=False,
                   disadvantage=False):
    """
    Resolve a single weapon attack (melee or ranged).

    Parameters:
        attacker   — combatant object with db attributes
        defender   — combatant object with db attributes
        weapon     — weapon object (or None for unarmed)
        advantage  — True if the attacker has advantage
        disadvantage — True if the attacker has disadvantage

    Returns:
        An :class:`AttackResult` with all resolution details.
    """
    result = AttackResult()
    result.attacker_name = attacker.key
    result.defender_name = defender.key

    # Determine weapon properties
    if weapon is not None:
        result.weapon_name = weapon.key
        dmg_notation = weapon.db.damage_dice or "1d4"
        dmg_type = weapon.db.damage_type or "bludgeoning"
        atk_range = weapon.db.attack_range or "melee"
    else:
        dmg_notation = "1d4"
        dmg_type = "bludgeoning"
        atk_range = "melee"

    result.damage_type = dmg_type
    is_melee = atk_range == "melee"

    # Ability modifier for attack and damage
    if is_melee:
        atk_stat = "str"
    else:
        atk_stat = "dex"
    stat_mod = get_mod(attacker, atk_stat)
    prof = getattr(attacker.db, "proficiency_bonus", None)
    if prof is None:
        prof = prof_bonus(getattr(attacker.db, "level", 1) or 1)

    result.attack_bonus = stat_mod + prof

    # Condition-based advantage/disadvantage
    cond_adv, cond_dis = get_attack_modifiers(attacker, defender,
                                               is_melee=is_melee)
    advantage = advantage or cond_adv
    disadvantage = disadvantage or cond_dis

    # Check defender conditions for auto-crit on melee
    auto_crit = False
    if is_melee:
        defender_conditions = getattr(defender.db, "conditions", None) or []
        for cond in defender_conditions:
            cond_name = cond if isinstance(cond, str) else cond.get("name", "")
            if cond_name in ("paralyzed", "unconscious"):
                auto_crit = True
                break

    # Roll to hit
    d20_result, d20_rolls = roll_d20(advantage=advantage,
                                      disadvantage=disadvantage)
    result.d20_rolls = d20_rolls
    result.d20_result = d20_result
    result.target_ac = defender.db.ac or 10
    result.attack_total = d20_result + result.attack_bonus

    # Natural 1 = auto miss
    if d20_result == 1:
        result.is_miss = True
        result.is_hit = False
        result.is_crit = False
        return result

    # Natural 20 = auto crit
    if d20_result == 20 or auto_crit:
        result.is_crit = True
        result.is_hit = True
    elif result.attack_total >= result.target_ac:
        result.is_hit = True
    else:
        result.is_miss = True
        result.is_hit = False
        return result

    # Roll damage
    num, sides = parse_dice(dmg_notation)
    if result.is_crit:
        num *= 2  # Double the number of damage dice on crit
    rolls = roll_dice(num, sides)
    result.damage_rolls = rolls
    result.damage_bonus = stat_mod
    result.damage_total = max(0, sum(rolls) + stat_mod)

    # Apply resistances / vulnerabilities / immunities
    final = result.damage_total
    resistances = getattr(defender.db, "damage_resistances", None) or []
    vulnerabilities = getattr(defender.db, "damage_vulnerabilities", None) or []
    immunities = getattr(defender.db, "damage_immunities", None) or []

    if dmg_type in immunities:
        final = 0
        result.immunity_applied = True
    elif dmg_type in vulnerabilities:
        final = final * 2
        result.vulnerability_applied = True
    elif dmg_type in resistances:
        final = final // 2
        result.resistance_applied = True

    result.final_damage = max(0, final)
    return result


# ---------------------------------------------------------------------------
# Spell result dataclass
# ---------------------------------------------------------------------------

@dataclass
class SpellResult:
    """Encapsulates the full result of a spell cast."""
    caster_name: str = ""
    spell_name: str = ""
    is_attack: bool = False
    d20_rolls: list = field(default_factory=list)
    d20_result: int = 0
    attack_bonus: int = 0
    attack_total: int = 0
    is_crit: bool = False
    is_hit: bool = False
    save_stat: str = ""
    save_dc: int = 0
    target_results: list = field(default_factory=list)
    slot_level: int = 0


# ---------------------------------------------------------------------------
# Spell attack resolution
# ---------------------------------------------------------------------------

def resolve_spell_attack(caster, target, spell_dict, advantage=False,
                         disadvantage=False):
    """
    Resolve a spell that requires a spell attack roll against a single target.

    Parameters:
        caster       — combatant object
        target       — combatant object
        spell_dict   — spell definition dict (from spells module)
        advantage    — explicit advantage
        disadvantage — explicit disadvantage

    Returns:
        A :class:`SpellResult`.
    """
    result = SpellResult()
    result.caster_name = caster.key
    result.spell_name = spell_dict.get("key", "Unknown Spell")
    result.is_attack = True
    result.slot_level = spell_dict.get("level", 0)

    atk_stat = spell_dict.get("attack_stat", "int")
    stat_mod = get_mod(caster, atk_stat)
    prof = getattr(caster.db, "proficiency_bonus", None)
    if prof is None:
        prof = prof_bonus(getattr(caster.db, "level", 1) or 1)
    result.attack_bonus = stat_mod + prof

    # Condition modifiers
    is_melee = spell_dict.get("range", "ranged") == "melee"
    cond_adv, cond_dis = get_attack_modifiers(caster, target, is_melee=is_melee)
    advantage = advantage or cond_adv
    disadvantage = disadvantage or cond_dis

    d20_result, d20_rolls = roll_d20(advantage=advantage,
                                      disadvantage=disadvantage)
    result.d20_rolls = d20_rolls
    result.d20_result = d20_result
    result.attack_total = d20_result + result.attack_bonus

    target_ac = target.db.ac or 10

    if d20_result == 1:
        result.is_hit = False
        result.is_crit = False
    elif d20_result == 20:
        result.is_hit = True
        result.is_crit = True
    elif result.attack_total >= target_ac:
        result.is_hit = True
    else:
        result.is_hit = False

    # Roll damage if hit
    if result.is_hit:
        dmg_notation = spell_dict.get("damage_dice", "1d6")
        dmg_type = spell_dict.get("damage_type", "magic")
        num, sides = parse_dice(dmg_notation)
        if result.is_crit:
            num *= 2
        rolls = roll_dice(num, sides)
        total_dmg = sum(rolls)

        # Resistances
        resistances = getattr(target.db, "damage_resistances", None) or []
        vulnerabilities = getattr(target.db, "damage_vulnerabilities", None) or []
        immunities = getattr(target.db, "damage_immunities", None) or []

        final = total_dmg
        res_applied = False
        vul_applied = False
        imm_applied = False
        if dmg_type in immunities:
            final = 0
            imm_applied = True
        elif dmg_type in vulnerabilities:
            final *= 2
            vul_applied = True
        elif dmg_type in resistances:
            final //= 2
            res_applied = True

        result.target_results = [{
            "target": target,
            "damage_rolls": rolls,
            "damage": max(0, final),
            "damage_type": dmg_type,
            "resistance_applied": res_applied,
            "vulnerability_applied": vul_applied,
            "immunity_applied": imm_applied,
        }]

    return result


# ---------------------------------------------------------------------------
# Spell save resolution
# ---------------------------------------------------------------------------

def resolve_spell_save(caster, targets_list, spell_dict):
    """
    Resolve a spell that forces saving throws on one or more targets.

    Parameters:
        caster        — combatant object
        targets_list  — list of combatant objects
        spell_dict    — spell definition dict

    Returns:
        A :class:`SpellResult`.
    """
    result = SpellResult()
    result.caster_name = caster.key
    result.spell_name = spell_dict.get("key", "Unknown Spell")
    result.is_attack = False
    result.slot_level = spell_dict.get("level", 0)

    atk_stat = spell_dict.get("attack_stat", "int")
    stat_mod = get_mod(caster, atk_stat)
    prof = getattr(caster.db, "proficiency_bonus", None)
    if prof is None:
        prof = prof_bonus(getattr(caster.db, "level", 1) or 1)

    save_stat = spell_dict.get("save_stat", "dex")
    save_dc = 8 + stat_mod + prof
    result.save_stat = save_stat
    result.save_dc = save_dc

    dmg_notation = spell_dict.get("damage_dice", "0d0")
    dmg_type = spell_dict.get("damage_type", "magic")

    target_results = []
    for target in targets_list:
        save_roll, save_total, saved = ability_save(target, save_stat, save_dc)
        num, sides = parse_dice(dmg_notation)
        rolls = roll_dice(num, sides)
        full_damage = sum(rolls)

        if saved:
            damage = full_damage // 2
        else:
            damage = full_damage

        # Resistances
        resistances = getattr(target.db, "damage_resistances", None) or []
        vulnerabilities = getattr(target.db, "damage_vulnerabilities", None) or []
        immunities = getattr(target.db, "damage_immunities", None) or []

        if dmg_type in immunities:
            damage = 0
        elif dmg_type in vulnerabilities:
            damage *= 2
        elif dmg_type in resistances:
            damage //= 2

        target_results.append({
            "target": target,
            "save_roll": save_roll,
            "save_total": save_total,
            "saved": saved,
            "damage_rolls": rolls,
            "damage": max(0, damage),
            "damage_type": dmg_type,
        })

    result.target_results = target_results
    return result


# ---------------------------------------------------------------------------
# Magic Missile (auto-hit, special handling)
# ---------------------------------------------------------------------------

def resolve_magic_missile(caster, target):
    """
    Resolve *magic missile*: 3 darts, each dealing 1d4+1 force damage.

    Auto-hit, no attack roll.

    Returns:
        dict with damage breakdown per dart and total.
    """
    darts = []
    total_damage = 0
    for _ in range(3):
        roll = roll_die(4)
        dart_dmg = roll + 1
        darts.append({"roll": roll, "damage": dart_dmg})
        total_damage += dart_dmg

    return {
        "caster_name": caster.key,
        "target_name": target.key,
        "spell_name": "magic missile",
        "darts": darts,
        "total_damage": total_damage,
        "damage_type": "force",
    }


# ---------------------------------------------------------------------------
# Death saving throws
# ---------------------------------------------------------------------------

@dataclass
class DeathSaveResult:
    """Encapsulates the result of a single death saving throw."""
    roll: int = 0
    is_nat20: bool = False
    is_nat1: bool = False
    success: bool = False
    successes: int = 0
    failures: int = 0
    stabilized: bool = False
    died: bool = False


def roll_death_save(combatant):
    """
    Roll a death saving throw for *combatant*.

    Reads and writes ``combatant.db.death_saves`` (dict with ``successes``
    and ``failures`` keys).

    Returns:
        A :class:`DeathSaveResult`.
    """
    saves = combatant.db.death_saves
    if saves is None:
        saves = {"successes": 0, "failures": 0}
        combatant.db.death_saves = saves

    d20 = roll_die(20)
    result = DeathSaveResult(roll=d20)

    if d20 == 20:
        # Natural 20: regain 1 HP, clear saves, stabilized
        result.is_nat20 = True
        result.success = True
        result.stabilized = True
        combatant.db.hp = 1
        saves["successes"] = 0
        saves["failures"] = 0
    elif d20 == 1:
        # Natural 1: count as 2 failures
        result.is_nat1 = True
        result.success = False
        saves["failures"] += 2
    elif d20 >= 10:
        result.success = True
        saves["successes"] += 1
    else:
        result.success = False
        saves["failures"] += 1

    # Check thresholds
    if saves["successes"] >= 3:
        result.stabilized = True
        saves["successes"] = 0
        saves["failures"] = 0

    if saves["failures"] >= 3:
        result.died = True

    result.successes = saves["successes"]
    result.failures = saves["failures"]
    combatant.db.death_saves = saves
    return result
