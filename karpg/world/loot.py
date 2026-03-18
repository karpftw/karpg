"""
Loot

Pure Python loot registry and roll math. No Evennia imports.

LOOT_TABLES keys match NPC prototype_key values. Each entry has:
  gold  — None (no gold) or {"chance": float, "min": int, "max": int}
  items — list of {"chance": float, "prototype_key": str}

roll_loot(npc) -> list[dict]  where each dict is one of:
  {"type": "gold", "amount": int}
  {"type": "item",  "prototype_key": str}
"""

import random

# ---------------------------------------------------------------------------
# Loot table registry
# ---------------------------------------------------------------------------

LOOT_TABLES = {
    "GIANT_RAT": {
        "gold": None,   # animal — carries nothing
        "items": [],
    },
    "GOBLIN": {
        "gold": {"chance": 0.85, "min": 2, "max": 12},
        "items": [
            {"chance": 0.08, "prototype_key": "RUSTY_DAGGER"},
        ],
    },
    "SKELETON": {
        "gold": None,   # undead — no money
        "items": [
            {"chance": 0.10, "prototype_key": "SHORT_SWORD"},
        ],
    },
    "BANDIT": {
        "gold": {"chance": 0.90, "min": 8, "max": 30},
        "items": [
            {"chance": 0.08, "prototype_key": "SHORT_SWORD"},
            {"chance": 0.05, "prototype_key": "LEATHER_JERKIN"},
            {"chance": 0.05, "prototype_key": "RUSTY_DAGGER"},
        ],
    },
    "ORC": {
        "gold": {"chance": 0.80, "min": 15, "max": 50},
        "items": [
            {"chance": 0.10, "prototype_key": "HAND_AXE"},
            {"chance": 0.05, "prototype_key": "LEATHER_CAP"},
            {"chance": 0.03, "prototype_key": "CHAIN_COIF"},
        ],
    },
}


# ---------------------------------------------------------------------------
# Roll logic
# ---------------------------------------------------------------------------

def roll_loot(npc):
    """
    Roll loot for a dying NPC. Returns a list of drop dicts.

    Priority:
    1. Boss override: npc.db.loot_table is a non-empty list of explicit entries.
    2. Registry lookup by npc.db.prototype_key.
    3. Procedural fallback via npc.db.faction_type and npc.db.level.
    """
    drops = []

    # ── 1. Boss override ──────────────────────────────────────────────────
    explicit = getattr(npc.db, "loot_table", None)
    if explicit:  # non-empty list
        table = {"gold": None, "items": []}
        for entry in explicit:
            if entry.get("type") == "gold":
                table["gold"] = {
                    "chance": entry.get("chance", 1.0),
                    "min": entry.get("min", 0),
                    "max": entry.get("max", 0),
                }
            elif entry.get("type") == "item":
                table["items"].append({
                    "chance": entry.get("chance", 1.0),
                    "prototype_key": entry["prototype_key"],
                })
        return _execute_rolls(table)

    # ── 2. Registry lookup ────────────────────────────────────────────────
    proto_key = getattr(npc.db, "prototype_key", None)
    if proto_key and proto_key in LOOT_TABLES:
        return _execute_rolls(LOOT_TABLES[proto_key])

    # ── 3. Procedural fallback ────────────────────────────────────────────
    faction_type = getattr(npc.db, "faction_type", None) or ""
    level = getattr(npc.db, "level", 1) or 1

    if faction_type == "animal" or level == 0:
        return []  # no loot

    table = {"gold": None, "items": []}

    if faction_type == "undead":
        table["items"] = [{"chance": 0.05, "prototype_key": "RUSTY_DAGGER"}]
    else:
        # Default humanoid
        table["gold"] = {
            "chance": 0.80,
            "min": level * 4,
            "max": level * 15,
        }
        table["items"] = [{"chance": 0.05, "prototype_key": "RUSTY_DAGGER"}]

    return _execute_rolls(table)


def _execute_rolls(table):
    """Roll each entry in a loot table dict and return resulting drops."""
    drops = []

    gold_entry = table.get("gold")
    if gold_entry and random.random() < gold_entry["chance"]:
        amount = random.randint(gold_entry["min"], gold_entry["max"])
        if amount > 0:
            drops.append({"type": "gold", "amount": amount})

    for item_entry in table.get("items", []):
        if random.random() < item_entry["chance"]:
            drops.append({"type": "item", "prototype_key": item_entry["prototype_key"]})

    return drops
