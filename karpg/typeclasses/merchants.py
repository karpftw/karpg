"""
Merchants

Merchant NPC typeclass with shop inventory support.

Extends NPC. Shop commands (list, buy, sell) check for this typeclass.
"""

from typeclasses.npcs import NPC


class Merchant(NPC):
    """
    A Merchant NPC that can sell items to and buy items from players.

    Key db attributes (in addition to NPC attributes):
        shop_inventory  — list of dicts: {"prototype_key": str, "stock": int|-1, "price_override": int|None}
                          stock=-1 means unlimited; price_override overrides the calculated price
        shop_type       — "general" | "weapons" | "armor" | "magic" | "healer" | "bank"
        no_negotiate    — bool: True = fixed pricing, CHM/negotiate has no effect
        buys_items      — bool: True if this merchant will buy items from players
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.shop_inventory = []
        self.db.shop_type = "general"
        self.db.no_negotiate = False
        self.db.buys_items = True

    def get_shop_listing(self, char):
        """
        Return a formatted shop inventory listing for display to char.

        Shows item name, buy price (adjusted for char's CHM/negotiate), and stock.
        """
        from evennia.prototypes import prototypes as proto_utils
        from world.economy import proto_value, buy_price_from_proto, format_gold

        inventory = self.db.shop_inventory or []
        if not inventory:
            return f"{self.key} has nothing for sale."

        W = 50
        hrule   = f"|x{'=' * (W + 4)}|n"
        divider = f"|x{'-' * (W + 4)}|n"

        lines = [hrule]
        lines.append(f"|x|||n  |C{'Item':<28}|n {'Price':>10}  {'Stock':>6}  |x|||n")
        lines.append(divider)

        no_neg = self.db.no_negotiate or False

        for entry in inventory:
            if isinstance(entry, str):
                proto_key     = entry
                stock         = -1
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

            if price_override is not None:
                price = price_override
            else:
                price = buy_price_from_proto(proto, char, no_negotiate=no_neg)

            stock_str = "|x(unlimited)|n" if stock == -1 else f"|w{stock}|n"
            lines.append(
                f"|x|||n  |w{item_name:<28}|n {format_gold(price):>10}  {stock_str:>10}  |x|||n"
            )

        lines.append(hrule)
        return "\n".join(lines)
