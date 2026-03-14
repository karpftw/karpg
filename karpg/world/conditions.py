"""
Conditions

Data-driven 5e conditions system. Each condition is defined as a dict
with boolean flags that the combat engine inspects. No Evennia imports.

Condition dicts stored on ``combatant.db.conditions`` look like::

    {"name": "poisoned", "duration": 3, "source": "Giant Spider"}

Duration ``-1`` means permanent (until explicitly removed).
"""

# ---------------------------------------------------------------------------
# Condition definitions
# ---------------------------------------------------------------------------

CONDITIONS = {
    "blinded": {
        "name": "blinded",
        "description": "Can't see. Auto-fails sight checks. Attack rolls have "
                       "disadvantage; attackers have advantage.",
        "attacker_disadvantage": True,
        "attacker_advantage": False,
        "defender_advantage_for_attacker": True,
        "defender_disadvantage_for_attacker": False,
        "defender_disadvantage_ranged_for_attacker": False,
        "auto_fail_saves": [],
        "no_actions": False,
        "speed_zero": False,
        "auto_crit_melee": False,
        "damage_resistance_all": False,
    },
    "charmed": {
        "name": "charmed",
        "description": "Can't attack the charmer. Charmer has advantage on "
                       "social checks.",
        "attacker_disadvantage": False,
        "attacker_advantage": False,
        "defender_advantage_for_attacker": False,
        "defender_disadvantage_for_attacker": False,
        "defender_disadvantage_ranged_for_attacker": False,
        "auto_fail_saves": [],
        "no_actions": False,
        "speed_zero": False,
        "auto_crit_melee": False,
        "damage_resistance_all": False,
    },
    "deafened": {
        "name": "deafened",
        "description": "Can't hear. Auto-fails hearing checks.",
        "attacker_disadvantage": False,
        "attacker_advantage": False,
        "defender_advantage_for_attacker": False,
        "defender_disadvantage_for_attacker": False,
        "defender_disadvantage_ranged_for_attacker": False,
        "auto_fail_saves": [],
        "no_actions": False,
        "speed_zero": False,
        "auto_crit_melee": False,
        "damage_resistance_all": False,
    },
    "exhaustion": {
        "name": "exhaustion",
        "description": "Multiple levels of exhaustion with escalating effects.",
        "attacker_disadvantage": False,   # set dynamically at level 3+
        "attacker_advantage": False,
        "defender_advantage_for_attacker": False,
        "defender_disadvantage_for_attacker": False,
        "defender_disadvantage_ranged_for_attacker": False,
        "auto_fail_saves": [],
        "no_actions": False,
        "speed_zero": False,              # set dynamically at level 5
        "auto_crit_melee": False,
        "damage_resistance_all": False,
    },
    "frightened": {
        "name": "frightened",
        "description": "Disadvantage on ability checks and attack rolls while "
                       "the source of fear is in sight.",
        "attacker_disadvantage": True,
        "attacker_advantage": False,
        "defender_advantage_for_attacker": False,
        "defender_disadvantage_for_attacker": False,
        "defender_disadvantage_ranged_for_attacker": False,
        "auto_fail_saves": [],
        "no_actions": False,
        "speed_zero": False,
        "auto_crit_melee": False,
        "damage_resistance_all": False,
    },
    "grappled": {
        "name": "grappled",
        "description": "Speed becomes 0.",
        "attacker_disadvantage": False,
        "attacker_advantage": False,
        "defender_advantage_for_attacker": False,
        "defender_disadvantage_for_attacker": False,
        "defender_disadvantage_ranged_for_attacker": False,
        "auto_fail_saves": [],
        "no_actions": False,
        "speed_zero": True,
        "auto_crit_melee": False,
        "damage_resistance_all": False,
    },
    "incapacitated": {
        "name": "incapacitated",
        "description": "Can't take actions or reactions.",
        "attacker_disadvantage": False,
        "attacker_advantage": False,
        "defender_advantage_for_attacker": False,
        "defender_disadvantage_for_attacker": False,
        "defender_disadvantage_ranged_for_attacker": False,
        "auto_fail_saves": [],
        "no_actions": True,
        "speed_zero": False,
        "auto_crit_melee": False,
        "damage_resistance_all": False,
    },
    "invisible": {
        "name": "invisible",
        "description": "Can't be seen. Advantage on attack rolls; attacks "
                       "against have disadvantage.",
        "attacker_disadvantage": False,
        "attacker_advantage": True,
        "defender_advantage_for_attacker": False,
        "defender_disadvantage_for_attacker": True,
        "defender_disadvantage_ranged_for_attacker": False,
        "auto_fail_saves": [],
        "no_actions": False,
        "speed_zero": False,
        "auto_crit_melee": False,
        "damage_resistance_all": False,
    },
    "paralyzed": {
        "name": "paralyzed",
        "description": "Incapacitated, can't move or speak. Auto-fail STR/DEX "
                       "saves. Attacks have advantage; melee hits are crits.",
        "attacker_disadvantage": False,
        "attacker_advantage": False,
        "defender_advantage_for_attacker": True,
        "defender_disadvantage_for_attacker": False,
        "defender_disadvantage_ranged_for_attacker": False,
        "auto_fail_saves": ["str", "dex"],
        "no_actions": True,
        "speed_zero": True,
        "auto_crit_melee": True,
        "damage_resistance_all": False,
    },
    "petrified": {
        "name": "petrified",
        "description": "Turned to stone. Incapacitated, can't move or speak. "
                       "Resistance to all damage. Auto-fail STR/DEX saves.",
        "attacker_disadvantage": False,
        "attacker_advantage": False,
        "defender_advantage_for_attacker": True,
        "defender_disadvantage_for_attacker": False,
        "defender_disadvantage_ranged_for_attacker": False,
        "auto_fail_saves": ["str", "dex"],
        "no_actions": True,
        "speed_zero": True,
        "auto_crit_melee": False,
        "damage_resistance_all": True,
    },
    "poisoned": {
        "name": "poisoned",
        "description": "Disadvantage on attack rolls and ability checks.",
        "attacker_disadvantage": True,
        "attacker_advantage": False,
        "defender_advantage_for_attacker": False,
        "defender_disadvantage_for_attacker": False,
        "defender_disadvantage_ranged_for_attacker": False,
        "auto_fail_saves": [],
        "no_actions": False,
        "speed_zero": False,
        "auto_crit_melee": False,
        "damage_resistance_all": False,
    },
    "prone": {
        "name": "prone",
        "description": "Disadvantage on attack rolls. Melee attacks against "
                       "have advantage; ranged attacks have disadvantage.",
        "attacker_disadvantage": True,
        "attacker_advantage": False,
        "defender_advantage_for_attacker": False,  # melee only, handled in logic
        "defender_disadvantage_for_attacker": False,
        "defender_disadvantage_ranged_for_attacker": True,
        "auto_fail_saves": [],
        "no_actions": False,
        "speed_zero": False,
        "auto_crit_melee": False,
        "damage_resistance_all": False,
    },
    "restrained": {
        "name": "restrained",
        "description": "Speed 0. Attacks have disadvantage. Attacks against "
                       "have advantage. Disadvantage on DEX saves.",
        "attacker_disadvantage": True,
        "attacker_advantage": False,
        "defender_advantage_for_attacker": True,
        "defender_disadvantage_for_attacker": False,
        "defender_disadvantage_ranged_for_attacker": False,
        "auto_fail_saves": [],
        "no_actions": False,
        "speed_zero": True,
        "auto_crit_melee": False,
        "damage_resistance_all": False,
    },
    "stunned": {
        "name": "stunned",
        "description": "Incapacitated, can't move. Auto-fail STR/DEX saves. "
                       "Attacks against have advantage.",
        "attacker_disadvantage": False,
        "attacker_advantage": False,
        "defender_advantage_for_attacker": True,
        "defender_disadvantage_for_attacker": False,
        "defender_disadvantage_ranged_for_attacker": False,
        "auto_fail_saves": ["str", "dex"],
        "no_actions": True,
        "speed_zero": True,
        "auto_crit_melee": False,
        "damage_resistance_all": False,
    },
    "unconscious": {
        "name": "unconscious",
        "description": "Incapacitated, can't move or speak, unaware. Falls "
                       "prone. Auto-fail STR/DEX saves. Attacks have advantage; "
                       "melee hits within 5 ft are crits.",
        "attacker_disadvantage": False,
        "attacker_advantage": False,
        "defender_advantage_for_attacker": True,
        "defender_disadvantage_for_attacker": False,
        "defender_disadvantage_ranged_for_attacker": False,
        "auto_fail_saves": ["str", "dex"],
        "no_actions": True,
        "speed_zero": True,
        "auto_crit_melee": True,
        "damage_resistance_all": False,
    },
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_condition(name):
    """
    Look up a condition definition by name (case-insensitive).

    Returns:
        dict or None
    """
    return CONDITIONS.get(name.lower())


def apply_condition(combatant, name, duration=-1, source=None):
    """
    Apply a condition to *combatant*.

    Conditions are stored as a list of dicts on ``combatant.db.conditions``.
    Identical conditions do not stack (except exhaustion, which increments
    its level).

    Parameters:
        combatant — game object with db.conditions
        name      — condition name string
        duration  — turns remaining (-1 = permanent)
        source    — optional source identifier
    """
    name = name.lower()
    conditions = combatant.db.conditions
    if conditions is None:
        conditions = []
        combatant.db.conditions = conditions

    # Check for existing
    for cond in conditions:
        if cond.get("name") == name:
            if name == "exhaustion":
                cond["level"] = min(6, cond.get("level", 1) + 1)
                return
            # Already has this condition — refresh duration if longer
            if duration == -1 or (cond.get("duration", -1) != -1
                                  and duration > cond["duration"]):
                cond["duration"] = duration
            return

    entry = {"name": name, "duration": duration, "source": source}
    if name == "exhaustion":
        entry["level"] = 1
    conditions.append(entry)
    combatant.db.conditions = conditions


def remove_condition(combatant, name):
    """Remove a condition by name from *combatant*."""
    name = name.lower()
    conditions = combatant.db.conditions or []
    combatant.db.conditions = [c for c in conditions if c.get("name") != name]


def has_condition(combatant, name):
    """Return True if *combatant* currently has the named condition."""
    name = name.lower()
    for cond in (combatant.db.conditions or []):
        if cond.get("name") == name:
            return True
    return False


def get_condition_level(combatant, name):
    """
    Return the level of a condition (used for exhaustion).

    Returns 0 if the condition is not present.
    """
    name = name.lower()
    for cond in (combatant.db.conditions or []):
        if cond.get("name") == name:
            return cond.get("level", 1)
    return 0


def tick_conditions(combatant):
    """
    Decrement durations of all conditions on *combatant*.

    Conditions with duration 0 after decrement are removed.
    Duration -1 (permanent) conditions are never ticked.

    Returns:
        list of expired condition name strings.
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


def get_attack_modifiers(attacker, defender, is_melee=True):
    """
    Aggregate all condition effects on an attack roll.

    Checks conditions on both attacker and defender to determine whether
    the attack is made with advantage, disadvantage, or both.

    Returns:
        (advantage: bool, disadvantage: bool)
    """
    advantage = False
    disadvantage = False

    # --- Attacker's own conditions ---
    for cond_entry in (attacker.db.conditions or []):
        cond_name = cond_entry.get("name", "")
        cond_def = CONDITIONS.get(cond_name)
        if not cond_def:
            continue

        # Attacker has disadvantage from own condition
        if cond_def.get("attacker_disadvantage"):
            # Exhaustion: only level 3+
            if cond_name == "exhaustion":
                if cond_entry.get("level", 1) >= 3:
                    disadvantage = True
            else:
                disadvantage = True

        # Attacker has advantage from own condition (e.g. invisible)
        if cond_def.get("attacker_advantage"):
            advantage = True

    # --- Defender's conditions ---
    for cond_entry in (defender.db.conditions or []):
        cond_name = cond_entry.get("name", "")
        cond_def = CONDITIONS.get(cond_name)
        if not cond_def:
            continue

        # Attacker gains advantage vs this defender
        if cond_def.get("defender_advantage_for_attacker"):
            # Prone: only melee grants advantage
            if cond_name == "prone":
                if is_melee:
                    advantage = True
            else:
                advantage = True

        # Attacker has disadvantage vs this defender
        if cond_def.get("defender_disadvantage_for_attacker"):
            disadvantage = True

        # Ranged attacks have disadvantage vs this defender
        if not is_melee and cond_def.get("defender_disadvantage_ranged_for_attacker"):
            disadvantage = True

    return advantage, disadvantage
