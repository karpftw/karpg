"""
Wearing commands

Commands for equipping/removing armor.

  wear <armor>   - put on armor from inventory
  remove <armor> - take off armor (slot name or item name)
"""

from evennia import Command
from evennia.utils.utils import inherits_from

from world.classes import can_wear_armor
from world.stats import get_carry_capacity, get_carried_weight


_ARMOR_SLOTS = (
    "head", "neck", "chest", "arms", "hands",
    "waist", "legs", "feet", "left_ring", "right_ring",
)


def _get_armor_slots(caller):
    """Return the armor_slots dict, initialising it if absent."""
    if not caller.db.armor_slots:
        caller.db.armor_slots = {slot: None for slot in _ARMOR_SLOTS}
    return caller.db.armor_slots


def _update_carrying_weight(caller):
    """Recalculate and store total carried weight from all contents."""
    caller.db.carrying_weight = get_carried_weight(caller)


class CmdWear(Command):
    """
    Put on a piece of armor from your inventory.

    Usage:
      wear <armor>

    Equips the named armor into its appropriate gear slot. The slot must
    be empty before you can wear the item.
    """

    key = "wear"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Wear what?")
            return

        item = caller.search(self.args.strip(), candidates=caller.contents)
        if not item:
            return

        if not inherits_from(item, "typeclasses.armor.Armor"):
            caller.msg(f"|r{item.get_display_name(caller)}|n is not armor.")
            return

        slot       = item.db.slot or "chest"
        armor_type = item.db.armor_type or "cloth"
        ac_bonus   = item.db.ac_bonus or 0
        dr_bonus   = item.db.dr_bonus or 0

        # Class restriction check
        char_class = getattr(caller.db, "char_class", None) or "warrior"
        ok, reason = can_wear_armor(char_class, armor_type)
        if not ok:
            caller.msg(f"|r{reason}|n")
            return

        armor_slots = _get_armor_slots(caller)

        if slot not in armor_slots:
            caller.msg(f"|rUnknown slot: {slot}|n")
            return

        if armor_slots[slot] is not None:
            current = armor_slots[slot]
            caller.msg(
                f"You are already wearing |w{current.get_display_name(caller)}|n "
                f"on your {slot.replace('_', ' ')}. Remove it first."
            )
            return

        # Equip
        armor_slots[slot] = item
        caller.db.armor_slots = armor_slots
        caller.db.ac = (caller.db.ac or 10) + ac_bonus
        caller.db.dr = (caller.db.dr or 0) + dr_bonus
        _update_carrying_weight(caller)

        bonus_parts = []
        if ac_bonus:
            bonus_parts.append(f"+{ac_bonus} AC")
        if dr_bonus:
            bonus_parts.append(f"+{dr_bonus} DR")
        bonus_str = f" |g({', '.join(bonus_parts)})|n" if bonus_parts else ""

        caller.msg(
            f"You put on |Y{item.get_display_name(caller)}|n"
            f" on your {slot.replace('_', ' ')}.{bonus_str}"
        )
        caller.location.msg_contents(
            f"|w{caller.name}|n puts on |w{item.get_display_name(caller)}|n.",
            exclude=caller,
        )


class CmdRemove(Command):
    """
    Remove a piece of worn armor.

    Usage:
      remove <armor>
      remove <slot>

    You can specify the item name or the slot name (e.g. "remove head",
    "remove iron helm").
    """

    key = "remove"
    aliases = ["takeoff"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Remove what?")
            return

        armor_slots = _get_armor_slots(caller)
        arg = self.args.strip().lower()

        # Try to match by slot name first
        item = None
        matched_slot = None

        # Check if arg directly matches a slot
        if arg in armor_slots:
            matched_slot = arg
            item = armor_slots[arg]
            if item is None:
                caller.msg(f"You are not wearing anything on your {arg.replace('_', ' ')}.")
                return
        else:
            # Search equipped items by name
            for slot, equipped in armor_slots.items():
                if equipped and arg in equipped.get_display_name(caller).lower():
                    matched_slot = slot
                    item = equipped
                    break

            if item is None:
                # Try caller's inventory search as fallback to get better error msgs
                candidate = caller.search(arg, candidates=caller.contents, quiet=True)
                if candidate:
                    candidate = candidate[0] if isinstance(candidate, list) else candidate
                    caller.msg(
                        f"You are not wearing |w{candidate.get_display_name(caller)}|n."
                    )
                else:
                    caller.msg(f"You are not wearing anything called '{self.args.strip()}'.")
                return

        ac_bonus = item.db.ac_bonus or 0
        dr_bonus = item.db.dr_bonus or 0

        # Unequip
        armor_slots[matched_slot] = None
        caller.db.armor_slots = armor_slots
        caller.db.ac = max(0, (caller.db.ac or 10) - ac_bonus)
        caller.db.dr = max(0, (caller.db.dr or 0) - dr_bonus)
        _update_carrying_weight(caller)

        bonus_parts = []
        if ac_bonus:
            bonus_parts.append(f"-{ac_bonus} AC")
        if dr_bonus:
            bonus_parts.append(f"-{dr_bonus} DR")
        bonus_str = f" |r({', '.join(bonus_parts)})|n" if bonus_parts else ""

        caller.msg(
            f"You remove |Y{item.get_display_name(caller)}|n.{bonus_str}"
        )
        caller.location.msg_contents(
            f"|w{caller.name}|n removes |w{item.get_display_name(caller)}|n.",
            exclude=caller,
        )
