"""
Weapons

Typeclass for all wieldable weapons in the game. Weapons are physical
objects with combat attributes and an optional enchantment list.

Attributes set on db:
    damage_dice  (str)   - dice notation, e.g. "2d6"
    damage_type  (str)   - "slashing" | "piercing" | "bludgeoning" | "magic"
    weapon_type  (str)   - "sword" | "dagger" | "axe" | "staff" | "bow"
    attack_range (str)   - "melee" | "ranged"
    speed        (float) - attack speed modifier (1.0 = normal)
    two_handed   (bool)  - True if weapon requires both hands
    weight       (float) - weight in lbs
    value        (int)   - base gold value
    enchantments (list)  - list of enchantment dicts; empty until enchantment system is built
"""

from evennia.objects.objects import DefaultObject
from evennia.utils.utils import display_len

from .objects import ObjectParent

# ── display helpers ───────────────────────────────────────────────────────────

def _pad(content, width):
    """Pad `content` with spaces until its visual (display) length equals `width`."""
    return content + ' ' * max(0, width - display_len(content))

# ── colour helpers ────────────────────────────────────────────────────────────
_DAMAGE_COLOURS = {
    "slashing":    "|r",
    "piercing":    "|y",
    "bludgeoning": "|c",
    "magic":       "|m",
}

_RANGE_ICONS = {
    "melee":  "[M]",
    "ranged": "[R]",
}

# ── per-weapon ASCII profile art ─────────────────────────────────────────────
# Each value is a list of Evennia-markup strings rendered inside the stat box.
# Visible width of each line must be <= W (52).  Use || for a literal |.
_WEAPON_ART = {
    # ── Rusty Dagger: small, simple, muted rust tones ────────────────────────
    "rusty_dagger": [
        "|r            .|n",
        "|x  {o}|n|r---|n|y~~~~|n|r.>|n   |x<- corroded blade|n",
        "|r            '|n",
        "|x    pommel   grip   edge|n",
    ],
    # ── Short Sword: clean silver one-hander ─────────────────────────────────
    "short_sword": [
        "|W              .|n",
        "|x  (*)|n|w====|n|c[+]|n|W===========>|n",
        "|W              '|n",
        "|x   pommel guard    blade      tip|n",
    ],
    # ── Hand Axe: compact iron head, schematic side view ─────────────────────
    "hand_axe": [
        "|x              .---.|n",
        "|x  {o}|n|r========|n|x/    |||n",
        "|x             \\    |||n",
        "|x              '---'|n",
        "|x       haft    head|n",
    ],
    # ── Iron Staff: long pole with iron end-caps, full-width shaft ────────────
    "iron_staff": [
        "|x  [|n|c==|n|x]|n|c==========================================|n|x[|n|c==|n|x]|n",
        "|x    cap                   shaft                   cap|n",
    ],
    # ── Longbow: tall curved yew bow, arrow nocked ────────────────────────────
    "longbow": [
        "|y    (|n",
        "|y   (|n",
        "|y  (|n|x---------------------------------|n|y=>|n  |x<- arrow|n",
        "|y   (|n",
        "|y    (|n",
        "|x   yew bow        string          arrow|n",
    ],
    # ── Broadsword: massive ornate two-hander, full colour ───────────────────
    "broadsword": [
        "|W              .|n",
        "|m           ___|n|W/|n",
        "|y   {*}|n|C======|n|m[+]|n|W=========================>|n",
        "|m           ---|n|W\\|n",
        "|W              '|n",
        "|x  pommel   guard          broad blade           tip|n",
    ],
}


def _dmg_colour(damage_type):
    return _DAMAGE_COLOURS.get(damage_type, "|w")


def _make_hrule(W):
    return f"|x{'=' * (W + 2)}|n"


def _make_divider(W):
    return f"|x{'-' * (W + 2)}|n"


class Weapon(ObjectParent, DefaultObject):
    """
    A wieldable weapon.

    All combat-relevant data lives in db attributes so it can be inspected,
    modified by enchantments, and eventually read by the combat system.
    """

    def at_object_creation(self):
        self.db.damage_dice = "1d4"
        self.db.damage_type = "slashing"
        self.db.weapon_type = "sword"
        self.db.attack_range = "melee"
        self.db.speed = 1.0
        self.db.two_handed = False
        self.db.weight = 1.0
        self.db.value = 1
        self.db.enchantments = []

    # ── appearance ────────────────────────────────────────────────────────────

    def return_appearance(self, looker, **kwargs):
        """Infographic-style weapon detail panel."""
        W = 52  # visible characters between the ║ borders

        name = self.get_display_name(looker)
        desc = self.db.desc or "No description."

        damage_dice  = self.db.damage_dice  or "—"
        damage_type  = self.db.damage_type  or "—"
        weapon_type  = self.db.weapon_type  or "—"
        attack_range = self.db.attack_range or "—"
        speed        = self.db.speed        if self.db.speed   is not None else 1.0
        two_handed   = self.db.two_handed   or False
        weight       = self.db.weight       if self.db.weight  is not None else 0.0
        value        = self.db.value        if self.db.value   is not None else 0
        enchantments = self.db.enchantments or []

        dmg_col     = _dmg_colour(damage_type)
        range_icon  = _RANGE_ICONS.get(attack_range, "?")
        handed_str  = "|rTWO-HANDED|n" if two_handed else "|gone-handed|n"
        enchant_str = (
            ", ".join(e.get("name", str(e)) for e in enchantments)
            if enchantments else "|x(none)|n"
        )

        def line(content):
            return f"|x|||n{_pad(content, W)}|x|||n"

        def stat(label, val):
            return line(f"  |C{label:<16}|n{val}")

        hrule   = _make_hrule(W)
        divider = _make_divider(W)

        lines = []
        lines.append(hrule)
        lines.append(line(f"  |m*|b~|n |M-- |W WEAPON |M--|n |b~|m*|n"))
        lines.append(hrule)
        lines.append(line(f"  |Y{name}|n"))

        # Description wrapped to fit within the box
        desc_words = desc.split()
        desc_line, desc_lines = "", []
        for word in desc_words:
            if len(desc_line) + len(word) + 1 > W - 4:
                desc_lines.append(desc_line)
                desc_line = word
            else:
                desc_line = f"{desc_line} {word}".strip()
        if desc_line:
            desc_lines.append(desc_line)
        for dl in desc_lines:
            lines.append(line(f"  |x{dl}|n"))

        lines.append(divider)
        lines.append(stat("Type",    f"|w{weapon_type.capitalize()}|n  {range_icon}  |x{attack_range}|n"))
        lines.append(stat("Damage",  f"{dmg_col}{damage_dice}|n  {dmg_col}[{damage_type}]|n"))
        lines.append(stat("Hands",   handed_str))
        lines.append(stat("Speed",   f"|w{speed:.1f}x|n"))
        lines.append(stat("Weight",  f"|w{weight:.1f} lbs|n"))
        lines.append(stat("Value",   f"|y{value} gp|n"))
        lines.append(divider)
        lines.append(line(f"  |m*|b~|n |MEnchantments|n"))
        lines.append(line(f"    {enchant_str}"))

        art = _WEAPON_ART.get(self.db.art_key or "", [])
        if art:
            lines.append(divider)
            lines.append(line(f"  |m*|b~|n |M-- PROFILE --|n"))
            lines.append(divider)
            for art_line in art:
                lines.append(line(art_line))

        lines.append(hrule)

        return "\n".join(lines)
