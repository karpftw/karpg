"""
Armor

Typeclass for all wearable armor in the game. Armor occupies one gear slot
and provides AC/DR bonuses when worn.

Attributes set on db:
    slot         (str)   - gear slot: "head" | "neck" | "chest" | "arms" | "hands"
                                       "waist" | "legs" | "feet" | "left_ring" | "right_ring"
    ac_bonus     (int)   - armor class bonus when equipped
    dr_bonus     (int)   - damage resistance bonus when equipped
    armor_type   (str)   - "cloth" | "leather" | "medium" | "heavy"
    weight       (float) - weight in lbs
    value        (int)   - base gold value
    enchantments (list)  - list of enchantment dicts
"""

from evennia.objects.objects import DefaultObject
from evennia.utils.utils import display_len

from .objects import ObjectParent


def _pad(content, width):
    """Pad `content` with spaces until its visual (display) length equals `width`."""
    return content + ' ' * max(0, width - display_len(content))


def _make_hrule(W):
    return f"|x{'=' * (W + 2)}|n"


def _make_divider(W):
    return f"|x{'-' * (W + 2)}|n"


_ARMOR_TYPE_COLOURS = {
    "cloth":   "|w",
    "leather": "|y",
    "medium":  "|c",
    "heavy":   "|W",
}


class Armor(ObjectParent, DefaultObject):
    """
    A piece of wearable armor.

    All stat data lives in db attributes so it can be inspected and
    modified by enchantments.
    """

    def at_object_creation(self):
        self.db.slot         = "chest"
        self.db.ac_bonus     = 0
        self.db.dr_bonus     = 0
        self.db.armor_type   = "cloth"
        self.db.weight       = 1.0
        self.db.value        = 0
        self.db.enchantments = []

    def return_appearance(self, looker, **kwargs):
        """Infographic-style armor detail panel."""
        W = 52

        name = self.get_display_name(looker)
        desc = self.db.desc or "No description."

        slot       = self.db.slot       or "chest"
        ac_bonus   = self.db.ac_bonus   or 0
        dr_bonus   = self.db.dr_bonus   or 0
        armor_type = self.db.armor_type or "cloth"
        weight     = self.db.weight     if self.db.weight is not None else 0.0
        value      = self.db.value      if self.db.value  is not None else 0
        enchants   = self.db.enchantments or []

        type_col    = _ARMOR_TYPE_COLOURS.get(armor_type, "|w")
        enchant_str = (
            ", ".join(e.get("name", str(e)) for e in enchants)
            if enchants else "|x(none)|n"
        )

        ac_str = f"|g+{ac_bonus} AC|n" if ac_bonus else "|x+0 AC|n"
        dr_str = f"|c+{dr_bonus} DR|n" if dr_bonus else "|x+0 DR|n"

        def line(content):
            return f"|x|||n{_pad(content, W)}|x|||n"

        def stat(label, val):
            return line(f"  |C{label:<16}|n{val}")

        hrule   = _make_hrule(W)
        divider = _make_divider(W)

        lines = []
        lines.append(hrule)
        lines.append(line(f"  |m*|b~|n |M-- |W ARMOR |M--|n |b~|m*|n"))
        lines.append(hrule)
        lines.append(line(f"  |Y{name}|n"))

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
        lines.append(stat("Slot",      f"|w{slot.replace('_', ' ').title()}|n"))
        lines.append(stat("Type",      f"{type_col}{armor_type.capitalize()}|n"))
        lines.append(stat("AC Bonus",  ac_str))
        lines.append(stat("DR Bonus",  dr_str))
        lines.append(stat("Weight",    f"|w{weight:.1f} lbs|n"))
        lines.append(stat("Value",     f"|y{value} gp|n"))
        lines.append(divider)
        lines.append(line(f"  |m*|b~|n |MEnchantments|n"))
        lines.append(line(f"    {enchant_str}"))
        lines.append(hrule)

        return "\n".join(lines)
