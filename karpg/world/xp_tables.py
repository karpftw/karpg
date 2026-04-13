"""
XP tables for MajorMUD-style leveling.

Pure Python — no Evennia imports.
"""

# ── Base XP curve ──────────────────────────────────────────────────────────────
# _BASE_XP[n] = cumulative XP required to reach level n.
# Level 1 requires 0 XP (starting level).
# Formula: base_xp(k) = 250*k^2 + 50*k^3  where k = level - 1

def _build_base_xp(max_level: int = 75) -> tuple:
    values = [0]  # level 1 requires 0 XP
    for level in range(2, max_level + 1):
        k = level - 1
        values.append(250 * k**2 + 50 * k**3)
    return tuple(values)


_BASE_XP: tuple = _build_base_xp(75)


# ── Class XP multipliers ───────────────────────────────────────────────────────

CLASS_XP_MULTIPLIERS: dict = {
    "warrior": 1.00,
    "thief":   1.05,
    "druid":   1.10,
    "priest":  1.10,
    "gypsy":   1.10,
    "warlock": 1.15,
    "mystic":  1.15,
    "mage":    1.25,
}

# Race XP modifiers live on race data in world/races.py.
# They are passed in as a float multiplier (e.g. 1.0 = no modifier).
# Default import helper below reads from races module.

def _race_xp_modifier(race: str) -> float:
    try:
        from world.races import RACE_REGISTRY as RACES
        data = RACES.get((race or "human").lower(), {})
        return data.get("xp_modifier", 1.0)
    except Exception:
        return 1.0


# ── Public API ─────────────────────────────────────────────────────────────────

def xp_for_level(level: int, char_class: str = None, race: str = None) -> int:
    """
    Cumulative XP needed to *be at* the given level (i.e. to have just reached it).

    xp_for_level(1) == 0
    xp_for_level(2) == 300  (for a Warrior)
    """
    level = max(1, min(75, level))
    base = _BASE_XP[level - 1]
    multiplier = CLASS_XP_MULTIPLIERS.get((char_class or "warrior").lower(), 1.0)
    multiplier *= _race_xp_modifier(race)
    return int(base * multiplier)


def xp_to_next_level(current_level: int, char_class: str = None, race: str = None) -> int:
    """
    XP needed to advance from current_level to current_level+1.
    Returns 0 if already at level cap.
    """
    if current_level >= 75:
        return 0
    return xp_for_level(current_level + 1, char_class, race) - xp_for_level(current_level, char_class, race)


def xp_in_bracket(current_xp: int, current_level: int, char_class: str = None, race: str = None) -> int:
    """
    XP earned within the current level bracket (for status display).

    e.g. if level 3 starts at 1,800 and player has 2,500 XP, returns 700.
    """
    level_floor = xp_for_level(current_level, char_class, race)
    return max(0, current_xp - level_floor)


def cp_for_level(level: int) -> int:
    """CP awarded when reaching the given level."""
    if level <= 10:
        return 10
    elif level <= 20:
        return 15
    elif level <= 30:
        return 20
    elif level <= 40:
        return 25
    elif level <= 50:
        return 30
    elif level <= 60:
        return 35
    elif level <= 70:
        return 40
    else:
        return 45
