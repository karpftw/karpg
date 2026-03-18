"""
Economy Commands

balance   — show carried gold + bank balance
gold      — quick carried gold display
deposit   — deposit gold at a bank NPC
withdraw  — withdraw gold from a bank NPC
list      — view merchant shop inventory + prices
buy       — buy an item from a merchant
sell      — sell an item to a merchant
drink     — drink a consumable (potion)
"""

from evennia import Command
from world.economy import (
    can_afford, transfer_gold, format_gold,
    sell_price, buy_price_from_proto,
)


# ── Room-search helpers ────────────────────────────────────────────────────────

def _find_bank(location):
    """Find an NPC tagged 'bank' in location. Returns NPC or None."""
    for obj in location.contents:
        if obj.tags.get("bank", category="npc_role"):
            return obj
    return None


def _find_merchant(location):
    """Find a Merchant typeclass NPC in location. Returns NPC or None."""
    from typeclasses.merchants import Merchant
    for obj in location.contents:
        if isinstance(obj, Merchant):
            return obj
    return None


# ── Commands ──────────────────────────────────────────────────────────────────

class CmdGold(Command):
    """
    Show how much gold you are carrying.

    Usage:
      gold
    """

    key = "gold"
    aliases = ["gp"]
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        gold = self.caller.db.gold or 0
        self.caller.msg(f"You are carrying |y{gold:,} GP|n.")


class CmdBalance(Command):
    """
    Show your carried gold and bank balance.

    Usage:
      balance
    """

    key = "balance"
    aliases = ["bal"]
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller
        gold = caller.db.gold or 0
        bank = caller.db.bank_balance or 0
        caller.msg(
            f"|yGold on hand:|n  {gold:,} GP\n"
            f"|yBank balance:|n  {bank:,} GP\n"
            f"|yTotal:|n         {gold + bank:,} GP"
        )


class CmdDeposit(Command):
    """
    Deposit gold at the bank.

    Must be in the same room as a bank NPC (tagged 'bank').

    Usage:
      deposit <amount>
      deposit all
    """

    key = "deposit"
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Usage: deposit <amount> or deposit all")
            return

        bank = _find_bank(caller.location)
        if not bank:
            caller.msg("You must be at a bank to deposit gold.")
            return

        gold = caller.db.gold or 0
        arg = self.args.strip().lower()

        if arg == "all":
            amount = gold
        else:
            try:
                amount = int(arg)
            except ValueError:
                caller.msg("Usage: deposit <amount> or deposit all")
                return

        if amount <= 0:
            caller.msg("You must deposit a positive amount.")
            return
        if amount > gold:
            caller.msg(f"You only have {gold:,} GP on hand.")
            return

        caller.db.gold = gold - amount
        caller.db.bank_balance = (caller.db.bank_balance or 0) + amount
        caller.msg(
            f"You deposit {format_gold(amount)} with {bank.key}. "
            f"New balance: {format_gold(caller.db.bank_balance)}."
        )


class CmdWithdraw(Command):
    """
    Withdraw gold from the bank.

    Must be in the same room as a bank NPC (tagged 'bank').

    Usage:
      withdraw <amount>
      withdraw all
    """

    key = "withdraw"
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Usage: withdraw <amount> or withdraw all")
            return

        bank = _find_bank(caller.location)
        if not bank:
            caller.msg("You must be at a bank to withdraw gold.")
            return

        bank_bal = caller.db.bank_balance or 0
        arg = self.args.strip().lower()

        if arg == "all":
            amount = bank_bal
        else:
            try:
                amount = int(arg)
            except ValueError:
                caller.msg("Usage: withdraw <amount> or withdraw all")
                return

        if amount <= 0:
            caller.msg("You must withdraw a positive amount.")
            return
        if amount > bank_bal:
            caller.msg(f"Your bank balance is only {bank_bal:,} GP.")
            return

        caller.db.bank_balance = bank_bal - amount
        caller.db.gold = (caller.db.gold or 0) + amount
        caller.msg(
            f"You withdraw {format_gold(amount)} from {bank.key}. "
            f"Remaining balance: {format_gold(caller.db.bank_balance)}."
        )


class CmdList(Command):
    """
    View a merchant's shop inventory and prices.

    Must be in the same room as a merchant NPC.

    Usage:
      list
    """

    key = "list"
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        merchant = _find_merchant(self.caller.location)
        if not merchant:
            self.caller.msg("There is no merchant here.")
            return
        self.caller.msg(merchant.get_shop_listing(self.caller))


class CmdBuy(Command):
    """
    Buy an item from a nearby merchant.

    Prices are affected by your CHM stat and Negotiate skill level.

    Usage:
      buy <item name>
    """

    key = "buy"
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Usage: buy <item name>")
            return

        merchant = _find_merchant(caller.location)
        if not merchant:
            caller.msg("There is no merchant here.")
            return

        from evennia.prototypes import prototypes as proto_utils

        query = self.args.strip().lower()
        inventory = merchant.db.shop_inventory or []
        no_neg = merchant.db.no_negotiate or False

        matched_entry  = None
        matched_proto  = None

        for entry in inventory:
            if isinstance(entry, str):
                proto_key      = entry
                stock          = -1
                price_override = None
            else:
                proto_key      = entry.get("prototype_key", "")
                stock          = entry.get("stock", -1)
                price_override = entry.get("price_override", None)

            protos = proto_utils.search_prototype(proto_key)
            if not protos:
                continue
            proto = protos[0] if isinstance(protos, list) else protos

            item_name = proto.get("key", proto_key.lower().replace("_", " "))
            if query in item_name.lower():
                matched_entry = (
                    entry if not isinstance(entry, str)
                    else {"prototype_key": entry, "stock": -1, "price_override": None}
                )
                matched_proto = proto
                break

        if not matched_proto:
            caller.msg(f"No item matching '{self.args.strip()}' is sold here.")
            return

        stock          = matched_entry.get("stock", -1)
        price_override = matched_entry.get("price_override", None)

        if stock == 0:
            caller.msg("That item is out of stock.")
            return

        price = (
            price_override
            if price_override is not None
            else buy_price_from_proto(matched_proto, caller, no_negotiate=no_neg)
        )

        gold = caller.db.gold or 0
        if gold < price:
            caller.msg(
                f"You need {format_gold(price)} but only have {format_gold(gold)}."
            )
            return

        # Spawn the item into the caller's inventory
        from evennia.prototypes.spawner import spawn
        proto_key  = matched_entry.get("prototype_key", "")
        new_items  = spawn({"prototype_parent": proto_key})
        if not new_items:
            caller.msg("|rError spawning item. Please report this.|n")
            return

        item          = new_items[0]
        item.location = caller

        caller.db.gold = gold - price

        # Decrement finite stock
        if stock > 0:
            matched_entry["stock"] = stock - 1

        caller.msg(
            f"You buy |w{item.key}|n from {merchant.key} for {format_gold(price)}. "
            f"You have {format_gold(caller.db.gold)} remaining."
        )


class CmdSell(Command):
    """
    Sell an item to a nearby merchant.

    Shops pay 50% of an item's base value. You cannot sell wielded
    or worn items without removing them first.

    Usage:
      sell <item name>
    """

    key = "sell"
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Usage: sell <item name>")
            return

        merchant = _find_merchant(caller.location)
        if not merchant:
            caller.msg("There is no merchant here.")
            return

        if not (merchant.db.buys_items or False):
            caller.msg(f"{merchant.key} doesn't buy items.")
            return

        item = caller.search(self.args.strip(), location=caller)
        if not item:
            return   # search() already printed an error

        # Guard: can't sell currently-equipped items
        wielded = caller.db.wielded or {}
        worn    = caller.db.armor_slots or {}
        if item in wielded.values() or item in worn.values():
            caller.msg("You must remove or unwield that item before selling it.")
            return

        price     = sell_price(item)
        item_name = item.key
        item.delete()

        caller.db.gold = (caller.db.gold or 0) + price
        caller.msg(
            f"You sell |w{item_name}|n to {merchant.key} for {format_gold(price)}. "
            f"You now have {format_gold(caller.db.gold)}."
        )


class CmdDrink(Command):
    """
    Drink a potion or consumable from your inventory.

    Usage:
      drink <item>
    """

    key = "drink"
    aliases = ["quaff"]
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller
        if not self.args.strip():
            caller.msg("Usage: drink <item>")
            return

        item = caller.search(self.args.strip(), location=caller)
        if not item:
            return

        item_type = getattr(item.db, "item_type", None)
        if item_type != "consumable":
            caller.msg(f"You can't drink {item.key}.")
            return

        heal_amount = getattr(item.db, "heal_amount", 0) or 0
        if heal_amount:
            old_hp  = caller.db.hp or 0
            max_hp  = caller.db.hp_max or 1
            new_hp  = min(max_hp, old_hp + heal_amount)
            healed  = new_hp - old_hp
            caller.db.hp = new_hp
            caller.msg(
                f"You drink the {item.key}. |gYou recover {healed} HP.|n "
                f"({new_hp}/{max_hp})"
            )
        else:
            caller.msg(f"You drink the {item.key}, but feel no effect.")

        item.delete()
        caller.msg(caller.get_prompt(), options={"send_prompt": True})
