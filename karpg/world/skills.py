"""
Skills

Central skill registry and all skill math. No Evennia imports — pure Python.

Each skill entry:
    name           — display name
    type           — "passive" | "active"
    stats          — primary stats used in skill_score()
    class_abilities — [] = all classes; non-empty = must be in char class abilities
    race_abilities  — [] = all races; non-empty = must be in char race abilities
    race_bonus      — {"elf": 3} adds flat bonus to score
    cp_learn        — CP cost to learn (0 = auto-granted)
    cp_per_level    — CP cost to level up
    max_level       — maximum skill level (1-5)
    auto_grant      — True = granted at chargen (racial passives)
    cooldown        — seconds (active skills only)
    description     — help text
"""

import time
import random

SKILL_REGISTRY = {
    # ── Perception (passive, all classes) ───────────────────────────────────
    "perception": {
        "name": "Perception",
        "type": "passive",
        "stats": ["int"],
        "class_abilities": [],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 5,
        "cp_per_level": 3,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 0,
        "description": (
            "Heightens your senses, allowing you to spot hidden characters "
            "on room entry and each combat round."
        ),
    },

    # ── Combat Mastery (passive, Warrior) ────────────────────────────────────
    "combat_mastery": {
        "name": "Combat Mastery",
        "type": "passive",
        "stats": ["str", "agi"],
        "class_abilities": ["combat_mastery"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 8,
        "cp_per_level": 5,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 0,
        "description": (
            "Deep expertise with all weapons. Grants +2 accuracy and +1 damage per level."
        ),
    },

    # ── Dodge (passive, Thief/Mystic or Elf/Halfling) ────────────────────────
    "dodge": {
        "name": "Dodge",
        "type": "passive",
        "stats": ["agi"],
        "class_abilities": ["dodge"],
        "race_abilities": [],
        "race_bonus": {"elf": 2, "halfling": 2, "centaur": 2},
        "cp_learn": 8,
        "cp_per_level": 5,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 0,
        "description": (
            "Training in evasion. AGI×2 + level×3 = % chance to fully avoid a melee hit (cap 30%)."
        ),
    },

    # ── Dual Wield (passive, Warriors/Thieves/Warlocks/Gypsies) ─────────────
    "dual_wield": {
        "name": "Dual Wield",
        "type": "passive",
        "stats": ["agi"],
        "class_abilities": ["dual_wield"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 10,
        "cp_per_level": 5,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 0,
        "description": (
            "Mastery of fighting with two weapons. Off-hand weapon grants "
            "1 extra attack per 2 skill levels."
        ),
    },

    # ── Parry (passive, Warrior/Warlock) ─────────────────────────────────────
    "parry": {
        "name": "Parry",
        "type": "passive",
        "stats": ["str"],
        "class_abilities": ["parry"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 8,
        "cp_per_level": 5,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 0,
        "description": (
            "Deflect incoming melee attacks. STR×2 + level×3 = % chance to halve damage (cap 25%)."
        ),
    },

    # ── Shield Block (passive, Warrior/Priest) ────────────────────────────────
    "shield_block": {
        "name": "Shield Block",
        "type": "passive",
        "stats": ["str"],
        "class_abilities": ["shield_block"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 8,
        "cp_per_level": 5,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 0,
        "description": (
            "Use a shield to negate incoming hits. STR + level×3 = % chance (cap 20%). "
            "Requires a shield in the off-hand."
        ),
    },

    # ── Encumbrance Bonus (auto-granted, Half-Orc racial) ────────────────────
    "encumbrance_bonus": {
        "name": "Encumbrance Bonus",
        "type": "passive",
        "stats": [],
        "class_abilities": [],
        "race_abilities": ["encumbrance_bonus"],
        "race_bonus": {},
        "cp_learn": 0,
        "cp_per_level": 0,
        "max_level": 1,
        "auto_grant": True,
        "cooldown": 0,
        "description": "Half-Orc's natural strength grants ×1.2 carry capacity.",
    },

    # ── Nightvision (auto-granted, Dwarf/Elf racial) ─────────────────────────
    "nightvision": {
        "name": "Nightvision",
        "type": "passive",
        "stats": [],
        "class_abilities": [],
        "race_abilities": ["nightvision"],
        "race_bonus": {},
        "cp_learn": 0,
        "cp_per_level": 0,
        "max_level": 1,
        "auto_grant": True,
        "cooldown": 0,
        "description": "Can see clearly in dark rooms.",
    },

    # ── Stealth (Thief/Elf/Halfling — handled by can_hide(), registry entry for display) ──
    "stealth": {
        "name": "Stealth",
        "type": "passive",
        "stats": ["agi"],
        "class_abilities": ["stealth"],
        "race_abilities": ["stealth_bonus"],
        "race_bonus": {"elf": 2, "halfling": 2, "dark_elf": 3, "half_elf": 1},
        "cp_learn": 0,
        "cp_per_level": 0,
        "max_level": 1,
        "auto_grant": False,
        "cooldown": 0,
        "description": "Move unseen. Prerequisite for Backstab. Use the 'hide' command.",
    },

    # ── Backstab (Thief — handled by CmdBackstab, registry entry for display) ──
    "backstab": {
        "name": "Backstab",
        "type": "active",
        "stats": ["agi", "str"],
        "class_abilities": ["backstab"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 0,
        "cp_per_level": 0,
        "max_level": 1,
        "auto_grant": False,
        "cooldown": 0,
        "description": "Devastating strike from stealth. 5× damage multiplier. Use 'backstab <target>'.",
    },

    # ── HP Regen Outdoor (passive, Druid) ─────────────────────────────────────
    "hp_regen_outdoor": {
        "name": "Outdoor Regen",
        "type": "passive",
        "stats": ["hlt"],
        "class_abilities": ["hp_regen_outdoor"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 5,
        "cp_per_level": 3,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 0,
        "description": "+1 HP/tick per level when resting in outdoor rooms.",
    },

    # ── Negotiate (passive, Gypsy) ────────────────────────────────────────────
    "negotiate": {
        "name": "Negotiate",
        "type": "passive",
        "stats": ["chm"],
        "class_abilities": ["negotiate"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 5,
        "cp_per_level": 3,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 0,
        "description": "Charm and haggling skill. Reduces shop prices by CHM + level×3 %, capped at 15%.",
    },

    # ── Unarmed Forms (passive, Mystic) ──────────────────────────────────────
    "unarmed_forms": {
        "name": "Unarmed Forms",
        "type": "passive",
        "stats": ["str", "agi"],
        "class_abilities": ["unarmed_forms"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 8,
        "cp_per_level": 5,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 0,
        "description": (
            "Mastery of tiger, crane, and serpent stances. Each form scales "
            "unarmed damage dice. Use 'form <tiger|crane|serpent|none>'."
        ),
    },

    # ── Lockpick (active, Thief / Gnome racial bonus) ────────────────────────
    "lockpick": {
        "name": "Lockpick",
        "type": "active",
        "stats": ["agi", "int"],
        "class_abilities": ["lockpick"],
        "race_abilities": [],
        "race_bonus": {"gnome": 3},
        "cp_learn": 8,
        "cp_per_level": 4,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 30,
        "description": "Open locked doors and containers. AGI+INT+level×3 vs lock_difficulty.",
    },

    # ── Thievery (active, Thief/Gypsy) ───────────────────────────────────────
    "thievery": {
        "name": "Thievery",
        "type": "active",
        "stats": ["agi", "int"],
        "class_abilities": ["thievery"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 8,
        "cp_per_level": 4,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 60,
        "description": "Pick pockets and steal items. AGI+INT+level×3 vs target_level×5.",
    },

    # ── Track (active, Druid) ─────────────────────────────────────────────────
    "track": {
        "name": "Track",
        "type": "active",
        "stats": ["int"],
        "class_abilities": ["track"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 8,
        "cp_per_level": 4,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 20,
        "description": "Follow trails. INT+level×3 check; reveals direction target last moved.",
    },

    # ── First Aid (active, Warrior/Druid/Priest) ──────────────────────────────
    "first_aid": {
        "name": "First Aid",
        "type": "active",
        "stats": ["wis"],
        "class_abilities": ["first_aid"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 5,
        "cp_per_level": 3,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 60,
        "description": "Bandage wounds. Heals HLT+(level×2) HP. 60s cooldown.",
    },

    # ── Turn Undead (active, Priest) ─────────────────────────────────────────
    "turn_undead": {
        "name": "Turn Undead",
        "type": "active",
        "stats": ["wis", "int"],
        "class_abilities": ["turn_undead"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 8,
        "cp_per_level": 5,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 30,
        "description": "Channel divine power. WIS+INT+level×3 vs undead_level×4; cause flight or damage.",
    },

    # ── Intimidate (active, Warrior/Warlock) ──────────────────────────────────
    "intimidate": {
        "name": "Intimidate",
        "type": "active",
        "stats": ["str", "chm"],
        "class_abilities": ["intimidate"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 8,
        "cp_per_level": 4,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 30,
        "description": "Strike fear. STR+CHM+level×3 vs target_wis×3; applies frightened for 3 rounds.",
    },

    # ── Battle Cry (active, Warrior) ──────────────────────────────────────────
    "battle_cry": {
        "name": "Battle Cry",
        "type": "active",
        "stats": ["str", "chm"],
        "class_abilities": ["battle_cry"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 10,
        "cp_per_level": 5,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 60,
        "description": "+5 accuracy to all allies for 3 rounds per level. Requires allies in room.",
    },

    # ── Disarm (active, Warrior) ──────────────────────────────────────────────
    "disarm": {
        "name": "Disarm",
        "type": "active",
        "stats": ["str", "agi"],
        "class_abilities": ["disarm"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 8,
        "cp_per_level": 4,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 20,
        "description": "Knock weapon from target's hand. STR+AGI+level×3 vs target_str×3.",
    },

    # ── Traps (active, Thief) ─────────────────────────────────────────────────
    "traps": {
        "name": "Traps",
        "type": "active",
        "stats": ["int", "agi"],
        "class_abilities": ["traps"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 8,
        "cp_per_level": 4,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 0,
        "description": "'search' detects, 'disarm trap' disables, 'settrap' places. INT+AGI+level×3 vs difficulty.",
    },

    # ── Forage (active, Druid) ────────────────────────────────────────────────
    "forage": {
        "name": "Forage",
        "type": "active",
        "stats": ["int", "wis"],
        "class_abilities": ["forage"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 5,
        "cp_per_level": 3,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 120,
        "description": "Gather herbs/food in outdoor rooms. INT+WIS+level×3 check.",
    },

    # ── Identify (active, Mage/Druid) ─────────────────────────────────────────
    "identify": {
        "name": "Identify",
        "type": "active",
        "stats": ["int"],
        "class_abilities": ["identify"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 5,
        "cp_per_level": 3,
        "max_level": 5,
        "auto_grant": False,
        "cooldown": 30,
        "description": "Reveal hidden item stats. INT+level×3 check.",
    },

    # ── Performance (passive, Bard — auto-granted) ────────────────────────────
    "performance": {
        "name": "Performance",
        "type": "passive",
        "stats": ["chm"],
        "class_abilities": ["performance"],
        "race_abilities": [],
        "race_bonus": {},
        "cp_learn": 0,
        "cp_per_level": 4,
        "max_level": 5,
        "auto_grant": True,
        "cooldown": 0,
        "description": "Extends the duration of Bard songs by 1 round per level.",
    },
}


# ---------------------------------------------------------------------------
# Proficiency level names
# ---------------------------------------------------------------------------

_LEVEL_NAMES = {
    0: "Not Learned",
    1: "Novice",
    2: "Apprentice",
    3: "Journeyman",
    4: "Expert",
    5: "Master",
}

_LEVEL_UP_USES = {1: 0, 2: 50, 3: 100, 4: 200, 5: 400}


def level_name(level):
    """Return the display name for a skill level."""
    return _LEVEL_NAMES.get(level, "Unknown")


# ---------------------------------------------------------------------------
# Registry access
# ---------------------------------------------------------------------------

def get_skill(key):
    """Look up a skill by key. Returns dict or None."""
    return SKILL_REGISTRY.get(key)


def list_skills():
    """Return list of (key, dict) tuples sorted by name."""
    return sorted(SKILL_REGISTRY.items(), key=lambda x: x[1]["name"])


# ---------------------------------------------------------------------------
# Eligibility
# ---------------------------------------------------------------------------

def can_learn_skill(char, skill_key):
    """
    Check if a character can learn/buy a skill.

    Returns (bool, reason_str).
    """
    skill = get_skill(skill_key)
    if skill is None:
        return False, "That skill does not exist."

    if skill["auto_grant"]:
        return False, "That skill is automatically granted — it cannot be purchased."

    if skill["cp_learn"] == 0 and not skill["class_abilities"] and not skill["race_abilities"]:
        # Already-handled skills like stealth/backstab
        return False, "That skill is granted through your class or race, not purchased."

    char_class = getattr(char.db, "char_class", None) or "warrior"
    char_race = getattr(char.db, "race", None) or "human"

    from world.classes import get_class
    from world.races import get_race

    cls = get_class(char_class)
    race = get_race(char_race)

    cls_abilities = (cls.get("abilities") or []) if cls else []
    race_abilities = (race.get("abilities") or []) if race else []

    # Class restriction check
    if skill["class_abilities"]:
        if not any(ab in cls_abilities for ab in skill["class_abilities"]):
            return False, f"Your class ({char_class}) cannot learn {skill['name']}."

    # Race restriction check
    if skill["race_abilities"]:
        if not any(ab in race_abilities for ab in skill["race_abilities"]):
            return False, f"Your race ({char_race}) cannot learn {skill['name']}."

    return True, ""


def has_skill(char, skill_key):
    """Return True if character has the skill at any level > 0."""
    known = getattr(char.db, "known_skills", None) or {}
    entry = known.get(skill_key)
    if entry is None:
        return False
    return entry.get("level", 0) > 0


def skill_level(char, skill_key):
    """Return the skill level (0 if unknown)."""
    known = getattr(char.db, "known_skills", None) or {}
    entry = known.get(skill_key)
    if entry is None:
        return 0
    return entry.get("level", 0)


def auto_grant_racial_skills(char):
    """
    Grant racial auto-grant skills based on the character's race abilities.
    Called at chargen and recalc_stats.
    """
    from world.races import get_race
    char_race = getattr(char.db, "race", None) or "human"
    race = get_race(char_race)
    if not race:
        return

    race_abilities = race.get("abilities") or []
    known = dict(getattr(char.db, "known_skills", None) or {})

    for key, skill in SKILL_REGISTRY.items():
        if not skill["auto_grant"]:
            continue
        # Grant if race has matching ability
        if skill["race_abilities"] and any(ab in race_abilities for ab in skill["race_abilities"]):
            if key not in known or known[key].get("level", 0) == 0:
                known[key] = {"level": 1, "uses": 0}

    char.db.known_skills = known


# ---------------------------------------------------------------------------
# Economy
# ---------------------------------------------------------------------------

def learn_skill_cost(char, skill_key):
    """
    Return the CP cost to learn (or advance) a skill.
    Returns 0 if the skill is free/auto-granted, -1 if maxed or ineligible.
    """
    skill = get_skill(skill_key)
    if skill is None:
        return -1

    current_level = skill_level(char, skill_key)
    max_level = skill.get("max_level", 5)

    if current_level >= max_level:
        return -1  # already maxed

    if current_level == 0:
        return skill["cp_learn"]
    else:
        return skill["cp_per_level"]


def learn_skill(char, skill_key):
    """
    Spend CP to learn or advance a skill.

    Returns (bool, message_str).
    """
    skill = get_skill(skill_key)
    if skill is None:
        return False, "That skill does not exist."

    eligible, reason = can_learn_skill(char, skill_key)
    if not eligible:
        return False, reason

    current_level = skill_level(char, skill_key)
    max_level = skill.get("max_level", 5)

    if current_level >= max_level:
        return False, f"{skill['name']} is already at maximum level."

    cost = learn_skill_cost(char, skill_key)
    cp = getattr(char.db, "cp", 0) or 0

    if cp < cost:
        return False, f"You need {cost} CP to learn {skill['name']} (you have {cp})."

    # Deduct CP and update skill
    char.db.cp = cp - cost

    known = dict(getattr(char.db, "known_skills", None) or {})
    if skill_key not in known:
        known[skill_key] = {"level": 1, "uses": 0}
    else:
        known[skill_key]["level"] = current_level + 1

    char.db.known_skills = known

    new_level = known[skill_key]["level"]
    return True, (
        f"You have learned |W{skill['name']}|n ({level_name(new_level)}) "
        f"for {cost} CP. ({cp - cost} CP remaining)"
    )


# ---------------------------------------------------------------------------
# Core check engine
# ---------------------------------------------------------------------------

def skill_score(char, skill_key):
    """
    Compute the base skill score: sum of relevant stats + level×3 + racial bonus.
    """
    skill = get_skill(skill_key)
    if skill is None:
        return 0

    total = 0
    for stat_name in skill.get("stats", []):
        val = getattr(char.db, stat_name, None)
        total += int(val) if val is not None else 10

    level = skill_level(char, skill_key)
    total += level * 3

    # Racial bonus
    race = getattr(char.db, "race", "human") or "human"
    total += skill.get("race_bonus", {}).get(race, 0)

    return total


def skill_check(char, skill_key, difficulty=0, multiplier=3):
    """
    Roll a skill check: success_chance = min(95, max(5, score×multiplier - difficulty)).

    Returns True on success.
    """
    score = skill_score(char, skill_key)
    chance = min(95, max(5, score * multiplier - difficulty))
    return random.randint(1, 100) <= chance


def tick_skill_use(char, skill_key):
    """
    Increment the use counter for a skill. Auto-levels if threshold reached.
    """
    known = dict(getattr(char.db, "known_skills", None) or {})
    if skill_key not in known:
        return

    entry = dict(known[skill_key])
    entry["uses"] = entry.get("uses", 0) + 1

    current_level = entry.get("level", 1)
    max_level = get_skill(skill_key).get("max_level", 5)
    next_uses = _LEVEL_UP_USES.get(current_level + 1, 999999)

    if current_level < max_level and entry["uses"] >= next_uses:
        entry["level"] = current_level + 1
        entry["uses"] = 0
        known[skill_key] = entry
        char.db.known_skills = known
        skill_name = get_skill(skill_key)["name"]
        char.msg(
            f"|G[SKILL]|n Your {skill_name} has improved to "
            f"|W{level_name(entry['level'])}|n!"
        )
        return

    known[skill_key] = entry
    char.db.known_skills = known


# ---------------------------------------------------------------------------
# Cooldown
# ---------------------------------------------------------------------------

def check_cooldown(char, skill_key):
    """
    Return True if skill is ready (not on cooldown), False if still cooling down.
    Also returns remaining seconds as second value.
    """
    skill = get_skill(skill_key)
    if skill is None or skill["cooldown"] == 0:
        return True, 0

    cooldowns = getattr(char.db, "skill_cooldowns", None) or {}
    last_used = cooldowns.get(skill_key, 0)
    elapsed = time.time() - last_used
    cd = skill["cooldown"]

    if elapsed >= cd:
        return True, 0
    return False, int(cd - elapsed)


def set_cooldown(char, skill_key):
    """Stamp the current time as last-used for this skill."""
    cooldowns = dict(getattr(char.db, "skill_cooldowns", None) or {})
    cooldowns[skill_key] = time.time()
    char.db.skill_cooldowns = cooldowns


# ---------------------------------------------------------------------------
# Per-skill math helpers
# ---------------------------------------------------------------------------

def perception_check(perceiver, hidden):
    """
    Check if perceiver spots the hidden character.

    Returns True if spotted.
    """
    from world.stealth import stealth_score
    # Stealth score of the hidden character
    hide_score = stealth_score(hidden)

    # Perceiver's detection power: INT + level (NPCs always get their raw INT)
    perceiver_int = int(getattr(perceiver.db, "int", 10) or 10)
    perceiver_level = int(getattr(perceiver.db, "level", 1) or 1)

    # Skill bonus for players with perception
    p_skill_level = skill_level(perceiver, "perception")
    skill_bonus = p_skill_level * 3

    detection_score = perceiver_int + perceiver_level + skill_bonus
    chance = min(80, max(5, detection_score - hide_score))
    return random.randint(1, 100) <= chance


def combat_mastery_bonus(char):
    """Return (accuracy_bonus, damage_bonus) from combat mastery."""
    level = skill_level(char, "combat_mastery")
    if level == 0:
        return 0, 0
    return level * 2, level * 1


def dodge_check(defender):
    """Return True if dodge triggers (full avoidance of melee hit)."""
    agi = int(getattr(defender.db, "agi", 10) or 10)
    level = skill_level(defender, "dodge")
    race = getattr(defender.db, "race", "human") or "human"
    race_bonus = SKILL_REGISTRY["dodge"].get("race_bonus", {}).get(race, 0)
    chance = min(30, agi * 2 + level * 3 + race_bonus)
    result = random.randint(1, 100) <= chance
    return result


def parry_check(defender):
    """Return True if parry triggers (damage halved)."""
    str_val = int(getattr(defender.db, "str", 10) or 10)
    level = skill_level(defender, "parry")
    chance = min(25, str_val * 2 + level * 3)
    return random.randint(1, 100) <= chance


def shield_block_check(defender):
    """Return True if shield block triggers (hit negated)."""
    str_val = int(getattr(defender.db, "str", 10) or 10)
    level = skill_level(defender, "shield_block")
    chance = min(20, str_val + level * 3)
    return random.randint(1, 100) <= chance


def dual_wield_extra_attacks(char):
    """Return number of extra off-hand attacks granted by dual wield."""
    level = skill_level(char, "dual_wield")
    if level == 0:
        return 0
    return level // 2  # 1 extra at level 2, 2 at level 4


def encumbrance_bonus_multiplier(char):
    """Return carry capacity multiplier (1.0 normally, 1.2 for Half-Orc with skill)."""
    if has_skill(char, "encumbrance_bonus"):
        return 1.2
    return 1.0


def hp_regen_outdoor_bonus(char):
    """Return bonus HP per resting tick for Druids in outdoor rooms."""
    level = skill_level(char, "hp_regen_outdoor")
    return level  # +1 HP/tick per level


def lockpick_check(char, difficulty):
    """
    Roll lockpick check against a door/container difficulty.

    Returns True on success.
    """
    return skill_check(char, "lockpick", difficulty=difficulty, multiplier=1)


def thievery_check(char, target):
    """
    Roll thievery (pick-pocket) check against a target.

    Returns True on success.
    """
    target_level = int(getattr(target.db, "level", 1) or 1)
    difficulty = target_level * 5
    return skill_check(char, "thievery", difficulty=difficulty, multiplier=1)


def track_check(char):
    """Roll tracking check. Returns True if trail found."""
    return skill_check(char, "track", difficulty=5, multiplier=1)


def first_aid_heal(char):
    """Return amount healed by first_aid."""
    hlt = int(getattr(char.db, "hlt", 10) or 10)
    level = skill_level(char, "first_aid")
    return hlt + level * 2


def turn_undead_check(char, undead):
    """
    Check turn undead outcome.

    Returns "flee" | "damage" | "fail".
    """
    wis = int(getattr(char.db, "wis", 10) or 10)
    int_ = int(getattr(char.db, "int", 10) or 10)
    level = skill_level(char, "turn_undead")
    score = wis + int_ + level * 3

    undead_level = int(getattr(undead.db, "level", 1) or 1)
    difficulty = undead_level * 4

    roll = random.randint(1, 100)
    if roll <= max(5, score - difficulty):
        # Strong success: undead flees; weak success: damage
        if roll <= max(5, (score - difficulty) // 2):
            return "flee"
        return "damage"
    return "fail"


def turn_undead_damage(char):
    """Return divine damage dealt by a successful turn."""
    wis = int(getattr(char.db, "wis", 10) or 10)
    level = skill_level(char, "turn_undead")
    import random as _r
    return _r.randint(1, wis) + level * 2


def intimidate_check(char, target):
    """Return True if intimidation succeeds."""
    str_val = int(getattr(char.db, "str", 10) or 10)
    chm = int(getattr(char.db, "chm", 10) or 10)
    level = skill_level(char, "intimidate")
    score = str_val + chm + level * 3

    target_wis = int(getattr(target.db, "wis", 10) or 10)
    difficulty = target_wis * 3

    return random.randint(1, 100) <= max(5, score - difficulty)


def battle_cry_bonus(char):
    """Return accuracy bonus per round from battle cry."""
    level = skill_level(char, "battle_cry")
    return level * 5


def disarm_check(char, target):
    """Return True if disarm succeeds."""
    str_val = int(getattr(char.db, "str", 10) or 10)
    agi = int(getattr(char.db, "agi", 10) or 10)
    level = skill_level(char, "disarm")
    score = str_val + agi + level * 3

    target_str = int(getattr(target.db, "str", 10) or 10)
    difficulty = target_str * 3

    return random.randint(1, 100) <= max(5, score - difficulty)


def trap_check(char, difficulty):
    """Roll trap-related check. Returns True on success."""
    return skill_check(char, "traps", difficulty=difficulty, multiplier=1)


def forage_check(char):
    """Return True if foraging succeeds."""
    return skill_check(char, "forage", difficulty=10, multiplier=1)


def identify_check(char):
    """Return True if identification succeeds."""
    return skill_check(char, "identify", difficulty=10, multiplier=1)


def negotiate_discount(char):
    """
    Return shop discount as a float multiplier (e.g., 0.92 = 8% off).
    """
    if not has_skill(char, "negotiate"):
        return 1.0
    chm = int(getattr(char.db, "chm", 10) or 10)
    level = skill_level(char, "negotiate")
    discount_pct = min(15, chm + level * 3) / 100.0
    return 1.0 - discount_pct


def unarmed_damage_dice(char):
    """
    Return damage dice string for unarmed Mystic based on active form and level.

    tiger  — damage-focused: 1d8 / 2d4 / 2d6
    crane  — balanced:       1d6 / 1d8 / 2d4
    serpent— accuracy-focused: 1d4 / 1d6 / 1d8
    none   — base unarmed:  1d4
    """
    level = skill_level(char, "unarmed_forms")
    if level == 0:
        return "1d4"

    form = getattr(char.db, "active_form", None) or "none"

    # Tier by level: 1-2, 3-4, 5
    if level <= 2:
        tier = 0
    elif level <= 4:
        tier = 1
    else:
        tier = 2

    form_dice = {
        "tiger":   ["1d8", "2d4", "2d6"],
        "crane":   ["1d6", "1d8", "2d4"],
        "serpent": ["1d4", "1d6", "1d8"],
        "none":    ["1d4", "1d6", "1d8"],
    }
    return form_dice.get(form, form_dice["none"])[tier]


def performance_duration_bonus(char):
    """Return extra rounds added to buff/debuff song duration. 0 for non-Bards."""
    level = skill_level(char, "performance")
    return level if level > 0 else 0
