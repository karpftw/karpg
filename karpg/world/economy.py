"""
Economy

Pure Python pricing math for MajorMUD-style shops and banking.
No Evennia imports — called from commands/economy.py and typeclasses/merchants.py.

Constants:
    SHOP_MARKUP    = 2.0   (shops sell to players at 200% of base value)
    SHOP_BUY_RATE  = 0.5   (shops buy from players at 50% of base value)
    GOLD_WEIGHT    = 0.01  (lbs per gold piece)
    INTEREST_RATE  = 0.01  (1% per day compound bank interest)
    INTEREST_CAP   = 50000 (max bank balance that accrues interest)
"""

SHOP_MARKUP   = 2.0
SHOP_BUY_RATE = 0.5
GOLD_WEIGHT   = 0.01
INTEREST_RATE = 0.01
INTEREST_CAP  = 50_000


def proto_value(proto: dict) -> int:
    """
    Extract base value from a prototype dict.

    Handles two formats:
      - Weapon/NPC style: attrs = [("value", 25), ...]
      - Armor style:      "db.value": 25  (top-level key)
    """
    if "db.value" in proto:
        return max(1, int(proto["db.value"] or 1))
    for attr in proto.get("attrs", []):
        if isinstance(attr, (list, tuple)) and len(attr) >= 2 and attr[0] == "value":
            return max(1, int(attr[1] or 1))
    return 1


def get_item_value(item) -> int:
    """Read db.value from an in-world item object, defaulting to 1."""
    val = getattr(item.db, "value", None)
    return max(1, int(val)) if val is not None else 1


def buy_price_from_proto(proto: dict, char, no_negotiate: bool = False) -> int:
    """
    Calculate shop sell-to-player price from a prototype dict.

    price = base_value * SHOP_MARKUP * negotiate_discount(char)
    """
    from world.skills import negotiate_discount
    base = proto_value(proto)
    discount = 1.0 if no_negotiate else negotiate_discount(char)
    return max(1, int(base * SHOP_MARKUP * discount))


def buy_price(item, char, no_negotiate: bool = False) -> int:
    """Shop sell-to-player price for an in-world item object."""
    from world.skills import negotiate_discount
    base = get_item_value(item)
    discount = 1.0 if no_negotiate else negotiate_discount(char)
    return max(1, int(base * SHOP_MARKUP * discount))


def sell_price(item) -> int:
    """
    Shop buy-from-player price: base_value * BUY_RATE, minimum 1 GP.

    Rounds up (0.5 bias) so fractional values don't round to zero.
    """
    base = get_item_value(item)
    return max(1, int(base * SHOP_BUY_RATE + 0.5))


def gold_weight(char) -> float:
    """Weight contribution of carried gold: db.gold * GOLD_WEIGHT lbs."""
    gold = getattr(char.db, "gold", 0) or 0
    return gold * GOLD_WEIGHT


def can_afford(char, amount: int) -> bool:
    """Return True if char has at least amount GP on hand."""
    return (getattr(char.db, "gold", 0) or 0) >= amount


def transfer_gold(src, dst, amount: int):
    """
    Move amount GP from src to dst. Does NOT validate affordability.
    Pass dst=None to destroy gold (e.g. taxes, fees).
    """
    src.db.gold = (getattr(src.db, "gold", 0) or 0) - amount
    if dst is not None:
        dst.db.gold = (getattr(dst.db, "gold", 0) or 0) + amount


def format_gold(amount: int) -> str:
    """Format a gold amount as '1,234 GP'."""
    return f"{amount:,} GP"
