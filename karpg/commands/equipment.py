"""
Equipment commands

Commands for wielding/unwielding weapons and viewing equipped items.

  wield <weapon>   - equip a weapon from inventory
  unwield [weapon] - unequip a weapon (or all if no arg)
  equipment / eq   - display an infographic of currently equipped weapons
"""

from evennia import Command
from evennia.utils.utils import display_len, inherits_from

from world.stats import get_carry_capacity, get_carried_weight


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
        caller  = self.caller
        wielded = _get_wielded(caller)
        armor_slots = caller.db.armor_slots or {}

        main = wielded.get("main_hand")
        off  = wielded.get("off_hand")

        W = 56  # visible characters between the | borders

        def line(content):
            return f"|x|||n{_pad(content, W)}|x|||n"

        def weapon_line(slot_label, weapon):
            if not weapon:
                return line(f"  |C{slot_label:<12}|n  |x(empty)|n")
            name        = weapon.get_display_name(caller)
            damage_dice = weapon.db.damage_dice or "—"
            damage_type = weapon.db.damage_type or "—"
            dmg_col     = _dmg_colour(damage_type)
            return line(f"  |C{slot_label:<12}|n  |Y{name}|n  "
                        f"|x[|n{dmg_col}{damage_dice}|n |x{damage_type}]|n")

        def armor_row(left_label, left_slot, right_label, right_slot):
            left_item  = armor_slots.get(left_slot)
            right_item = armor_slots.get(right_slot)

            def item_str(item):
                if not item:
                    return "|x(empty)|n"
                ac = item.db.ac_bonus or 0
                dr = item.db.dr_bonus or 0
                bonus = ""
                if ac:
                    bonus += f" |g+{ac}AC|n"
                if dr:
                    bonus += f" |c+{dr}DR|n"
                return f"|w{item.get_display_name(caller)}|n{bonus}"

            half = W // 2
            left_part  = f"  |C{left_label:<11}|n {item_str(left_item)}"
            right_part = f"  |C{right_label:<11}|n {item_str(right_item)}"
            padded     = left_part + ' ' * max(0, half - display_len(left_part))
            return line(padded + right_part)

        hrule   = _make_hrule(W)
        divider = _make_divider(W)

        # Totals
        base_ac = caller.db.base_ac or 10
        base_dr = caller.db.dr or 0
        armor_ac = sum((a.db.ac_bonus or 0) for a in armor_slots.values() if a)
        armor_dr = sum((a.db.dr_bonus or 0) for a in armor_slots.values() if a)
        total_ac = base_ac + armor_ac
        total_dr = base_dr  # dr on char already includes armor bonuses

        carried  = caller.db.carrying_weight or get_carried_weight(caller)
        cap      = get_carry_capacity(caller)
        carry_col = "|r" if carried > cap else "|g"

        lines = []
        lines.append(hrule)
        lines.append(line(f"  |m*|b~|n |M-- |W EQUIPMENT |M--|n |b~|m*|n"))
        lines.append(hrule)

        # Weapon section
        lines.append(weapon_line("MAIN HAND", main))
        if main and off and main is off:
            lines.append(line(f"  |x(two-handed — occupies both slots)|n"))
        else:
            lines.append(weapon_line("OFF HAND", off))

        lines.append(divider)

        # Armor section
        lines.append(armor_row("Head:",     "head",      "Neck:",       "neck"))
        lines.append(armor_row("Chest:",    "chest",     "Arms:",       "arms"))
        lines.append(armor_row("Hands:",    "hands",     "Waist:",      "waist"))
        lines.append(armor_row("Legs:",     "legs",      "Feet:",       "feet"))
        lines.append(armor_row("Left Ring:","left_ring", "Right Ring:", "right_ring"))

        lines.append(divider)

        # Totals row
        lines.append(line(
            f"  |CTotals|n  "
            f"AC |w{base_ac}|n+|g{armor_ac}|n=|W{total_ac}|n   "
            f"DR |w{total_dr}|n   |  "
            f"Carry: {carry_col}{carried:.1f}|n/|w{cap}|n lbs"
        ))

        lines.append(hrule)
        caller.msg("\n".join(lines))


# ── inventory ─────────────────────────────────────────────────────────────────

class CmdInventory(Command):
    """
    View items in your pack (carried but not equipped), gold, and carry weight.

    Usage:
      inventory
      inv
      i
    """

    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        W = 56

        def line(content):
            return f"|x|||n{_pad(content, W)}|x|||n"

        hrule   = _make_hrule(W)
        divider = _make_divider(W)

        # Build set of equipped objects to exclude
        wielded = _get_wielded(caller)
        equipped = set(v for v in wielded.values() if v)
        armor_slots = caller.db.armor_slots or {}
        equipped.update(v for v in armor_slots.values() if v)

        # Pack = everything in inventory minus equipped
        pack = [obj for obj in caller.contents if obj not in equipped]

        def item_line(obj):
            if inherits_from(obj, "typeclasses.weapons.Weapon"):
                tag   = "|c[W]|n"
                dice  = obj.db.damage_dice or "—"
                dtype = obj.db.damage_type or "—"
                col   = _dmg_colour(dtype)
                stats = f"{col}{dice} {dtype}|n"
                wt    = obj.db.weight or 0
                val   = obj.db.value or 0
                name  = f"|Y{obj.get_display_name(caller)}|n"
            elif inherits_from(obj, "typeclasses.armor.Armor"):
                tag   = "|y[A]|n"
                slot  = obj.db.slot or "?"
                ac    = obj.db.ac_bonus or 0
                atype = obj.db.armor_type or ""
                stats = f"|w{slot}|n |g+{ac}AC|n {atype}"
                wt    = obj.db.weight or 0
                val   = obj.db.value or 0
                name  = f"|w{obj.get_display_name(caller)}|n"
            elif getattr(obj.db, "item_type", None) == "consumable":
                tag   = "|m[!]|n"
                heal  = obj.db.heal_amount
                stats = f"|Mheals {heal} hp|n" if heal else "|mconsumable|n"
                wt    = obj.db.weight or 0
                val   = obj.db.value or 0
                name  = f"|m{obj.get_display_name(caller)}|n"
            else:
                tag   = "|x[?]|n"
                stats = ""
                wt    = getattr(obj.db, "weight", 0) or 0
                val   = getattr(obj.db, "value",  0) or 0
                name  = obj.get_display_name(caller)

            right   = f"{wt:.1f} lb  {val} gp"
            content = f" {tag} {_pad(name, 24)} {_pad(stats, 20)} {right}"
            return line(content)

        lines = []
        lines.append(hrule)
        lines.append(line(f"  |m*|b~|n |M-- |W INVENTORY |M--|n |b~|m*|n"))
        lines.append(hrule)

        if pack:
            for obj in pack:
                lines.append(item_line(obj))
        else:
            lines.append(line("  |x(nothing in pack)|n"))

        lines.append(divider)

        # Gold row
        gold     = caller.db.gold or 0
        gold_wt  = gold * 0.01
        lines.append(line(f"  Gold carried:  |Y{gold} gp|n  ({gold_wt:.1f} lbs)"))

        lines.append(divider)

        # Carry bar
        carried = caller.db.carrying_weight or get_carried_weight(caller)
        cap     = get_carry_capacity(caller)
        pct     = min(1.0, carried / cap) if cap else 0
        filled  = int(pct * 20)
        if pct < 0.75:
            bar_col = "|g"
        elif pct < 1.0:
            bar_col = "|y"
        else:
            bar_col = "|r"
        bar = bar_col + "█" * filled + "|x" + "░" * (20 - filled) + "|n"
        pct_str = f"{int(pct * 100)}%"
        lines.append(line(
            f"  Carry: {bar_col}{carried:.1f}|n / |w{cap}|n lbs"
            f"    [{bar}]  {pct_str}"
        ))

        lines.append(hrule)
        caller.msg("\n".join(lines))
