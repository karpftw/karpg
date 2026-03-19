"""
Class Ability Helpers

Pure-Python math and logic for the per-class active abilities.
No Evennia imports.

One active ability per class:
    Warrior  — challenge  (boost threat, apply provoked)
    Mage     — surge      (spend HP for mana, 2:1)
    Thief    — vanish     (mid-combat stealth, drop from combat)
    Druid    — commune    (sense hidden creatures; reveal track direction outdoors)
    Priest   — consecrate (consecrate room; holy damage to undead; double HP regen)
    Warlock  — dark_pact  (spend HP for mana, 3:2 ratio — more efficient than Surge)
    Gypsy    — hex        (apply stacking -5 acc curse, max 3 stacks, WIS save)
    Mystic   — meditate   (can_act=False, +10 def, Kai regen ×2 for 3 ticks)
"""

import random


# ---------------------------------------------------------------------------
# Shared cooldown helpers (work with db.skill_cooldowns dict)
# ---------------------------------------------------------------------------

import time as _time


def check_cooldown(char, key, duration):
    """Return True if the ability is off cooldown."""
    cd = dict(char.db.skill_cooldowns or {})
    return _time.time() - cd.get(key, 0) >= duration


def set_cooldown(char, key):
    """Record current time as the last-used timestamp for this ability key."""
    cd = dict(char.db.skill_cooldowns or {})
    cd[key] = _time.time()
    char.db.skill_cooldowns = cd


def cooldown_remaining(char, key, duration):
    """Return seconds remaining on a cooldown (0 if off cooldown)."""
    cd = dict(char.db.skill_cooldowns or {})
    elapsed = _time.time() - cd.get(key, 0)
    return max(0.0, duration - elapsed)


# ---------------------------------------------------------------------------
# Warrior — Challenge
# ---------------------------------------------------------------------------

CHALLENGE_THREAT_BOOST = 50
CHALLENGE_DURATION = 3   # rounds
CHALLENGE_CD = 30        # seconds


def apply_challenge(warrior, room_npcs):
    """
    Boost warrior's threat on all NPCs in room by CHALLENGE_THREAT_BOOST.
    Returns list of NPCs that were affected.
    """
    affected = []
    for npc in room_npcs:
        threat = dict(getattr(npc.db, "threat_table", None) or {})
        wid = warrior.id
        threat[wid] = threat.get(wid, 0) + CHALLENGE_THREAT_BOOST
        npc.db.threat_table = threat
        affected.append(npc)
    return affected


# ---------------------------------------------------------------------------
# Mage — Surge
# ---------------------------------------------------------------------------

SURGE_HP_COST = 20
SURGE_MANA_GAIN = 10
SURGE_MIN_HP = 25
SURGE_CD = 45


def can_surge(mage):
    """Return (ok, reason). ok=True if mage has enough HP to surge."""
    hp = getattr(mage.db, "hp", 0) or 0
    if hp < SURGE_MIN_HP:
        return False, f"You need at least {SURGE_MIN_HP} HP to surge. (You have {hp})"
    return True, ""


def apply_surge(mage):
    """Deduct HP and add mana. Returns (hp_spent, mana_gained)."""
    mage.db.hp = max(1, (mage.db.hp or 1) - SURGE_HP_COST)
    max_mana = mage.db.max_mana or 0
    current_mana = mage.db.mana or 0
    gained = min(SURGE_MANA_GAIN, max_mana - current_mana)
    mage.db.mana = current_mana + gained
    return SURGE_HP_COST, gained


# ---------------------------------------------------------------------------
# Thief — Vanish
# ---------------------------------------------------------------------------

VANISH_CD = 90


# The Vanish command requires the stealth skill and drops the thief from combat.
# Mechanical logic lives in the command (needs Evennia objects); only the
# skill check threshold lives here.

def vanish_success_chance(thief):
    """AGI-based success chance: 50% base + 3% per AGI point above 10."""
    agi = getattr(thief.db, "agi", 10) or 10
    return min(0.95, 0.50 + max(0, agi - 10) * 0.03)


# ---------------------------------------------------------------------------
# Druid — Commune
# ---------------------------------------------------------------------------

COMMUNE_CD = 60


def commune_hidden_check(druid, target):
    """Always reveals hidden creatures (commune bypasses normal detection)."""
    return True


# ---------------------------------------------------------------------------
# Priest — Consecrate
# ---------------------------------------------------------------------------

CONSECRATE_CD = 90
CONSECRATE_DURATION = 2     # combat rounds
CONSECRATE_HOLY_DICE = "1d6"


def consecrate_damage():
    """Roll 1d6 holy damage for undead in a consecrated room."""
    return random.randint(1, 6)


# ---------------------------------------------------------------------------
# Warlock — Dark Pact
# ---------------------------------------------------------------------------

DARK_PACT_HP_COST = 15
DARK_PACT_MANA_GAIN = 10
DARK_PACT_MIN_HP = 20
DARK_PACT_CD = 30


def can_dark_pact(warlock):
    """Return (ok, reason)."""
    hp = getattr(warlock.db, "hp", 0) or 0
    if hp < DARK_PACT_MIN_HP:
        return False, f"You need at least {DARK_PACT_MIN_HP} HP to invoke the pact. (You have {hp})"
    return True, ""


def apply_dark_pact(warlock):
    """Deduct HP and add mana. Returns (hp_spent, mana_gained)."""
    warlock.db.hp = max(1, (warlock.db.hp or 1) - DARK_PACT_HP_COST)
    max_mana = warlock.db.max_mana or 0
    current_mana = warlock.db.mana or 0
    gained = min(DARK_PACT_MANA_GAIN, max_mana - current_mana)
    warlock.db.mana = current_mana + gained
    return DARK_PACT_HP_COST, gained


# ---------------------------------------------------------------------------
# Gypsy — Hex
# ---------------------------------------------------------------------------

HEX_MAX_STACKS = 3
HEX_CD = 45
HEX_DC = 12        # WIS save DC


def hex_save_check(target):
    """
    Target rolls d20 + WIS//3 vs DC 12.
    Returns True if target SAVES (hex fails), False if hex lands.
    """
    wis = getattr(target.db, "wis", 10) or 10
    roll = random.randint(1, 20) + wis // 3
    return roll >= HEX_DC


def apply_hex_stack(target):
    """
    Increment hex_stacks on target (max HEX_MAX_STACKS).
    Returns new stack count, or None if already at max.
    """
    stacks = getattr(target.db, "hex_stacks", 0) or 0
    if stacks >= HEX_MAX_STACKS:
        return None
    target.db.hex_stacks = stacks + 1
    return target.db.hex_stacks


def clear_hex(target):
    """Remove all hex stacks from target."""
    target.db.hex_stacks = 0


def hex_accuracy_penalty(target):
    """Return the total accuracy penalty from hex stacks."""
    stacks = getattr(target.db, "hex_stacks", 0) or 0
    return stacks * -5


# ---------------------------------------------------------------------------
# Mystic — Meditate
# ---------------------------------------------------------------------------

MEDITATE_CD = 60
MEDITATE_TICKS = 3
MEDITATE_DEF_BONUS = 10
MEDITATE_KAI_MULT = 2


def begin_meditate(mystic):
    """Set meditate state on mystic. Returns True."""
    from world.conditions import apply_condition
    apply_condition(mystic, "meditating", duration=MEDITATE_TICKS)
    mystic.db.meditate_ticks = MEDITATE_TICKS
    return True
