"""
Equipment commands

Commands for wielding/unwielding weapons and viewing equipped items.

  wield <weapon>   - equip a weapon from inventory
  unwield [weapon] - unequip a weapon (or all if no arg)
  equipment / eq   - display an infographic of currently equipped weapons
"""

from evennia import Command
from evennia.utils.utils import display_len, inherits_from


# ── helpers ───────────────────────────────────────────────────────────────────

def _pad(content, width):
    """Pad `content` with spaces until its visual (display) length equals `width`.

    Uses Evennia's display_len which strips colour markup and counts wide
    Unicode characters correctly.
    """
    return content + ' ' * max(0, width - display_len(content))

def _get_wielded(caller):
    """Return the wielded dict, initialising it if absent."""
    if not caller.db.wielded:
        caller.db.wielded = {"main_hand": None, "off_hand": None}
    return caller.db.wielded


def _dmg_colour(damage_type):
    colours = {
        "slashing":    "|r",
        "piercing":    "|y",
        "bludgeoning": "|c",
        "magic":       "|m",
    }
    return colours.get(damage_type, "|w")


def _make_hrule(W):
    return f"|x{'=' * (W + 2)}|n"


def _make_divider(W):
    return f"|x{'-' * (W + 2)}|n"


# ── wield ─────────────────────────────────────────────────────────────────────

class CmdWield(Command):
    """
    Wield a weapon from your inventory.

    Usage:
      wield <weapon>

    Equips the named weapon into your main hand. Two-handed weapons
    will occupy both hands, unequipping anything currently held.
    """

    key = "wield"
    aliases = ["equip"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Wield what?")
            return

        weapon = caller.search(self.args.strip(), location=caller)
        if not weapon:
            return

        if not inherits_from(weapon, "typeclasses.weapons.Weapon"):
            caller.msg(f"|r{weapon.get_display_name(caller)}|n is not a weapon.")
            return

        wielded = _get_wielded(caller)
        two_handed = weapon.db.two_handed

        # Unequip anything currently in the way
        displaced = set()
        if two_handed:
            for slot in ("main_hand", "off_hand"):
                if wielded[slot] and wielded[slot] != weapon:
                    displaced.add(wielded[slot])
            wielded["main_hand"] = weapon
            wielded["off_hand"] = weapon
        else:
            if wielded["main_hand"] == wielded["off_hand"] and wielded["main_hand"]:
                # Currently holding a two-hander — clear both
                displaced.add(wielded["main_hand"])
                wielded["main_hand"] = None
                wielded["off_hand"] = None
            if wielded["main_hand"] and wielded["main_hand"] != weapon:
                displaced.add(wielded["main_hand"])
            wielded["main_hand"] = weapon

        caller.db.wielded = wielded

        for old in displaced:
            caller.msg(f"You sheathe |w{old.get_display_name(caller)}|n.")

        hand_str = "both hands" if two_handed else "your main hand"
        caller.msg(
            f"You wield |Y{weapon.get_display_name(caller)}|n "
            f"|x[{weapon.db.weapon_type}]|n in {hand_str}."
        )
        caller.location.msg_contents(
            f"|w{caller.name}|n wields |Y{weapon.get_display_name(caller)}|n.",
            exclude=caller,
        )


# ── unwield ───────────────────────────────────────────────────────────────────

class CmdUnwield(Command):
    """
    Unequip a wielded weapon.

    Usage:
      unwield [weapon]

    Without an argument, unequips everything. With an argument,
    unequips the named weapon from whichever slot it occupies.
    """

    key = "unwield"
    aliases = ["unequip", "sheathe"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        wielded = _get_wielded(caller)

        equipped = {w for w in wielded.values() if w}
        if not equipped:
            caller.msg("You are not wielding anything.")
            return

        if not self.args:
            # Unequip everything
            for w in equipped:
                caller.msg(f"You sheathe |w{w.get_display_name(caller)}|n.")
                caller.location.msg_contents(
                    f"|w{caller.name}|n sheathes |w{w.get_display_name(caller)}|n.",
                    exclude=caller,
                )
            caller.db.wielded = {"main_hand": None, "off_hand": None}
            return

        weapon = caller.search(self.args.strip(), location=caller)
        if not weapon:
            return

        if weapon not in equipped:
            caller.msg(f"You are not wielding |w{weapon.get_display_name(caller)}|n.")
            return

        # Clear every slot that holds this weapon (handles two-handers)
        for slot in ("main_hand", "off_hand"):
            if wielded[slot] == weapon:
                wielded[slot] = None
        caller.db.wielded = wielded

        caller.msg(f"You sheathe |w{weapon.get_display_name(caller)}|n.")
        caller.location.msg_contents(
            f"|w{caller.name}|n sheathes |w{weapon.get_display_name(caller)}|n.",
            exclude=caller,
        )


# ── equipment ─────────────────────────────────────────────────────────────────

class CmdEquipment(Command):
    """
    View your currently equipped weapons.

    Usage:
      equipment
      eq
    """

    key = "equipment"
    aliases = ["eq"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        wielded = _get_wielded(caller)

        main = wielded.get("main_hand")
        off  = wielded.get("off_hand")

        W = 54  # visible characters between the | borders

        def line(content):
            return f"|x|||n{_pad(content, W)}|x|||n"

        def weapon_block(weapon, slot_label):
            rows = []

            if not weapon:
                rows.append(line(f"  |C{slot_label:<12}|n  |x(empty)|n"))
                return rows

            name         = weapon.get_display_name(caller)
            damage_dice  = weapon.db.damage_dice  or "—"
            damage_type  = weapon.db.damage_type  or "—"
            weapon_type  = weapon.db.weapon_type  or "—"
            attack_range = weapon.db.attack_range or "—"
            speed        = weapon.db.speed        if weapon.db.speed  is not None else 1.0
            two_handed   = weapon.db.two_handed   or False
            weight       = weapon.db.weight       if weapon.db.weight is not None else 0.0
            value        = weapon.db.value        if weapon.db.value  is not None else 0
            enchants     = weapon.db.enchantments or []

            dmg_col     = _dmg_colour(damage_type)
            handed_str  = "|rTWO-HANDED|n" if two_handed else "|gone-handed|n"
            enchant_str = (
                ", ".join(e.get("name", str(e)) for e in enchants)
                if enchants else "|x(none)|n"
            )

            # Column layout: 2 margin + 12 slot + 2 gap + 12 label + 2 gap + value
            indent = f"  {' ' * 12}  "

            rows.append(line(f"  |C{slot_label:<12}|n  |Y{name}|n"))
            rows.append(line(f"{indent}|C{'Type':<12}|n  "
                             f"|w{weapon_type.capitalize()}|n  |x[{attack_range}]|n"))
            rows.append(line(f"{indent}|C{'Damage':<12}|n  "
                             f"{dmg_col}{damage_dice}|n  {dmg_col}[{damage_type}]|n"))
            rows.append(line(f"{indent}|C{'Hands':<12}|n  {handed_str}"))
            rows.append(line(f"{indent}|C{'Speed':<12}|n  |w{speed:.1f}x|n"))
            rows.append(line(f"{indent}|C{'Weight':<12}|n  |w{weight:.1f} lbs|n"))
            rows.append(line(f"{indent}|C{'Value':<12}|n  |y{value} gp|n"))
            rows.append(line(f"{indent}|C{'Enchantments':<12}|n  {enchant_str}"))
            return rows

        hrule   = _make_hrule(W)
        divider = _make_divider(W)

        lines = []
        lines.append(hrule)
        lines.append(line(f"  |m*|b~|n |M-- |W EQUIPPED WEAPONS |M--|n |b~|m*|n"))
        lines.append(hrule)

        for row in weapon_block(main, "MAIN HAND"):
            lines.append(row)

        if main and off and main is off:
            lines.append(line(f"  |b~|m*|n |x(two-handed -- occupies both slots)|n"))
        else:
            lines.append(divider)
            for row in weapon_block(off, "OFF HAND"):
                lines.append(row)

        lines.append(hrule)
        caller.msg("\n".join(lines))
