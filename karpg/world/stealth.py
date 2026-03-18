"""
Stealth System — Pure Math

All stealth probability calculations. No Evennia imports.
Reveal logic (which needs .msg() calls) is inlined at each call site.
"""

import random


def stealth_score(char) -> int:
    """AGI + racial bonus (Elf/Halfling +3)."""
    agi = char.db.agi or 10
    race = (char.db.race or "").lower()
    bonus = 3 if race in ("elf", "halfling") else 0
    return agi + bonus


def can_hide(char) -> bool:
    """Thief class, or Elf/Halfling of any class."""
    char_class = (char.db.char_class or "").lower()
    race = (char.db.race or "").lower()
    return char_class == "thief" or race in ("elf", "halfling")


def hide_check(char) -> bool:
    """True = successfully entered stealth. AGI 10 = 50%, AGI 20 = 95% cap."""
    score = stealth_score(char)
    return random.randint(1, 100) <= min(95, score * 5)


def noise_check(char) -> bool:
    """True = moved quietly (stealth maintained). AGI 10 = 70%, AGI 20 = 95% cap."""
    score = stealth_score(char)
    return random.randint(1, 100) <= min(95, 30 + score * 4)


def detection_check(char, npc) -> bool:
    """True = NPC detects the hidden character."""
    npc_int = npc.db.int or 10
    score = stealth_score(char)
    chance = max(5, npc_int * 5 - score * 3)
    return random.randint(1, 100) < chance
