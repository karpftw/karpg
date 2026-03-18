"""
Loot typeclass layer

GoldCoins  — a physical object that auto-consumes on pickup
execute_loot_drop(npc, room) — rolls and spawns all loot after an NPC death
_decay_loot_item(obj_dbid)   — module-level picklable callback for evdelay()
"""

from evennia.objects.objects import DefaultObject

from .objects import ObjectParent


# ---------------------------------------------------------------------------
# Decay helper (module-level so delay() can pickle it)
# ---------------------------------------------------------------------------

def _decay_loot_item(obj_dbid):
    """Delayed callback: delete a loot item still sitting on a room floor."""
    import evennia
    from evennia.objects.objects import DefaultRoom

    results = evennia.search_object(f"#{obj_dbid}")
    if not results:
        return
    obj = results[0]
    # Only decay items still on the room floor — not in a player's inventory
    if obj.location and isinstance(obj.location, DefaultRoom):
        obj.location.msg_contents(f"|x{obj.key} crumbles to dust.|n")
        obj.delete()


# ---------------------------------------------------------------------------
# GoldCoins typeclass
# ---------------------------------------------------------------------------

class GoldCoins(ObjectParent, DefaultObject):
    """
    A physical pile of gold coins in a room. Auto-consumed on pickup —
    the gold amount is added directly to the getter's db.gold.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.gold_amount = 0
        self.db.item_type = "gold_coins"

    def get_display_name(self, looker=None, **kwargs):
        amount = self.db.gold_amount or 0
        if amount == 1:
            return "1 gold coin"
        return f"{amount:,} gold coins"

    def return_appearance(self, looker, **kwargs):
        amount = self.db.gold_amount or 0
        return f"|YA pile of {amount:,} gold coins glitters on the ground.|n"

    def at_get(self, getter):
        """Called after the object has been moved to getter's inventory."""
        amount = self.db.gold_amount or 0
        if amount > 0:
            getter.db.gold = (getattr(getter.db, "gold", 0) or 0) + amount
            from world.economy import format_gold
            getter.msg(f"|YYou pocket {format_gold(amount)}.|n")
        # Delete immediately — gold should never sit in a player's inventory
        self.delete()


# ---------------------------------------------------------------------------
# Loot drop executor
# ---------------------------------------------------------------------------

def execute_loot_drop(npc, room):
    """Roll loot for a dying NPC and spawn results in the room."""
    if not room:
        return

    from world.loot import roll_loot
    drops = roll_loot(npc)
    if not drops:
        return

    from evennia.utils.utils import delay as evdelay
    from evennia.prototypes.spawner import spawn
    import evennia
    from world.economy import format_gold

    for drop in drops:
        if drop["type"] == "gold":
            amount = drop["amount"]
            gold_obj = evennia.create_object(
                "typeclasses.loot.GoldCoins",
                key=f"{amount} gold coins",
                location=room,
            )
            gold_obj.db.gold_amount = amount
            room.msg_contents(f"|Y{npc.key} dropped {format_gold(amount)}!|n")
            evdelay(300, _decay_loot_item, gold_obj.dbid)   # 5-min decay

        elif drop["type"] == "item":
            spawned = spawn({"prototype_parent": drop["prototype_key"], "location": room})
            if spawned:
                item = spawned[0]
                room.msg_contents(f"|Y{npc.key} dropped {item.key}!|n")
                evdelay(600, _decay_loot_item, item.dbid)   # 10-min decay
