"""
Conditions

MajorMUD-style conditions that affect combat stats.
No Evennia imports — pure data and lookup functions.

Condition dicts stored on combatant.db.conditions:
    {"name": "poisoned", "duration": 3, "source": "Giant Spider"}

Duration -1 = permanent (until explicitly removed).

Each condition definition has:
    accuracy_modifier   — applied to attacker's accuracy
    defense_modifier    — applied to target's defense (negative = easier to hit)
    attacks_modifier    — added to attacks_per_round
    can_act             — False means the combatant cannot attack/cast
    description         — display text
"""

CONDITIONS = {
    "poisoned": {
        "name": "poisoned",
        "accuracy_modifier": -10,
        "defense_modifier": 0,
        "attacks_modifier": -1,
        "can_act": True,
        "description": "Sickened by poison; accuracy and attack rate reduced.",
    },
    "stunned": {
        "name": "stunned",
        "accuracy_modifier": 0,
        "defense_modifier": -20,
        "attacks_modifier": 0,
        "can_act": False,
        "description": "Stunned; cannot act this round, easier to hit.",
    },
    "paralyzed": {
        "name": "paralyzed",
        "accuracy_modifier": 0,
        "defense_modifier": -30,
        "attacks_modifier": 0,
        "can_act": False,
        "description": "Paralyzed; completely helpless, very easy to hit.",
    },
    "blinded": {
        "name": "blinded",
        "accuracy_modifier": -20,
        "defense_modifier": -10,
        "attacks_modifier": 0,
        "can_act": True,
        "description": "Blinded; greatly reduced accuracy, slightly easier to hit.",
    },
    "slowed": {
        "name": "slowed",
        "accuracy_modifier": 0,
        "defense_modifier": 0,
        "attacks_modifier": -2,
        "can_act": True,
        "description": "Slowed; fewer attacks per round.",
    },
    "hasted": {
        "name": "hasted",
        "accuracy_modifier": 0,
        "defense_modifier": 0,
        "attacks_modifier": 2,
        "can_act": True,
        "description": "Hasted; more attacks per round.",
    },
    "frightened": {
        "name": "frightened",
        "accuracy_modifier": -15,
        "defense_modifier": 0,
        "attacks_modifier": 0,
        "can_act": True,
        "description": "Frightened; reduced accuracy.",
    },
    "weakened": {
        "name": "weakened",
        "accuracy_modifier": -5,
        "defense_modifier": -5,
        "attacks_modifier": 0,
        "can_act": True,
        "description": "Weakened; slightly reduced combat effectiveness.",
    },
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_condition(name):
    """Look up a condition definition by name (case-insensitive). Returns dict or None."""
    return CONDITIONS.get(name.lower())


def apply_condition(combatant, name, duration=-1, source=None):
    """
    Apply a condition to combatant. Identical conditions don't stack
    (duration is refreshed if longer).
    """
    name = name.lower()
    conditions = combatant.db.conditions
    if conditions is None:
        conditions = []
        combatant.db.conditions = conditions

    for cond in conditions:
        if cond.get("name") == name:
            if duration == -1 or (cond.get("duration", -1) != -1
                                  and duration > cond["duration"]):
                cond["duration"] = duration
            return

    conditions.append({"name": name, "duration": duration, "source": source})
    combatant.db.conditions = conditions


def remove_condition(combatant, name):
    """Remove a condition by name from combatant."""
    name = name.lower()
    conditions = combatant.db.conditions or []
    combatant.db.conditions = [c for c in conditions if c.get("name") != name]


def has_condition(combatant, name):
    """Return True if combatant currently has the named condition."""
    name = name.lower()
    for cond in (combatant.db.conditions or []):
        if cond.get("name") == name:
            return True
    return False


def can_act(combatant):
    """Return True if the combatant is able to attack or cast spells."""
    for cond_entry in (combatant.db.conditions or []):
        cond_def = CONDITIONS.get(cond_entry.get("name", ""))
        if cond_def and not cond_def["can_act"]:
            return False
    return True


def tick_conditions(combatant):
    """
    Decrement durations of all conditions. Remove those at 0.
    Duration -1 conditions are permanent.

    Returns list of expired condition name strings.
    """
    conditions = combatant.db.conditions or []
    remaining = []
    expired = []

    for cond in conditions:
        dur = cond.get("duration", -1)
        if dur == -1:
            remaining.append(cond)
            continue
        dur -= 1
        if dur <= 0:
            expired.append(cond["name"])
        else:
            cond["duration"] = dur
            remaining.append(cond)

    combatant.db.conditions = remaining
    return expired


def get_combat_modifiers(attacker, target):
    """
    Return (accuracy_mod, defense_mod) based on conditions.

    accuracy_mod: sum of accuracy modifiers from attacker's conditions.
    defense_mod: sum of defense modifiers from target's conditions
                 (negative values make the target easier to hit).
    """
    acc_mod = 0
    def_mod = 0

    for cond_entry in (attacker.db.conditions or []):
        cond_def = CONDITIONS.get(cond_entry.get("name", ""))
        if cond_def:
            acc_mod += cond_def["accuracy_modifier"]

    for cond_entry in (target.db.conditions or []):
        cond_def = CONDITIONS.get(cond_entry.get("name", ""))
        if cond_def:
            def_mod += cond_def["defense_modifier"]

    return acc_mod, def_mod


def get_attacks_modifier(combatant):
    """Return the total attacks-per-round modifier from all conditions."""
    total = 0
    for cond_entry in (combatant.db.conditions or []):
        cond_def = CONDITIONS.get(cond_entry.get("name", ""))
        if cond_def:
            total += cond_def["attacks_modifier"]
    return total
