"""
Newhaven world builder.

Programmatically creates the starting town of Newhaven and its surroundings.
Called once from server/conf/at_initial_setup.py on first server start.
Guards against double-build by checking for the Village Center room.

Layout:
                    [Training Grounds]
                           |  north
         [Weapon Shop] - [North Road] - [Armor Shop]
              west               |  south from center            east
  [General Store] - [Village Center] - [Spell Shop]
              west               |  south                        east
           [Healer] - [South Road] - [Boatman's Dock]
              west               |  south                        east
                      [River Crossing] -- east --> [Old East Road]

Underground:
  [Village Center] --down--> [Arena Entrance] --east--> [The Arena Floor]
"""

import evennia
from evennia.utils.create import create_object
from evennia.prototypes.spawner import spawn


_DIR_ALIASES = {
    "north": ["n"],
    "south": ["s"],
    "east": ["e"],
    "west": ["w"],
    "up": ["u"],
    "down": ["d"],
    "northeast": ["ne"],
    "northwest": ["nw"],
    "southeast": ["se"],
    "southwest": ["sw"],
}


def _room(key, desc, aliases=None):
    """Create a Newhaven room."""
    room = create_object(
        typeclass="typeclasses.rooms.Room",
        key=key,
        aliases=aliases or [],
    )
    room.db.desc = desc
    room.db.zone = "newhaven"
    return room


def _exit(direction, from_room, to_room):
    """Create a one-way exit."""
    create_object(
        typeclass="typeclasses.exits.Exit",
        key=direction,
        aliases=_DIR_ALIASES.get(direction, []),
        location=from_room,
        destination=to_room,
    )


def _link(from_room, to_room, there, back):
    """Create a two-way exit pair."""
    _exit(there, from_room, to_room)
    _exit(back, to_room, from_room)


def _npc(name, location, desc, aliases=None):
    """Create a stub non-hostile NPC."""
    npc = create_object(
        typeclass="typeclasses.npcs.NPC",
        key=name,
        aliases=aliases or [],
        location=location,
    )
    npc.db.desc = desc
    npc.db.faction = "neutral"
    npc.db.ai_profile = None
    npc.db.level = 0
    npc.db.hp = 100
    npc.db.hp_max = 100
    npc.db.threat_table = {}
    npc.db.in_combat = None
    return npc


# Map from room key → room_type, used by patch_newhaven_room_types()
_ROOM_TYPES = {
    "Village Center of Newhaven": "center",
    "North Road":                 "road",
    "South Road":                 "road",
    "Harden's Weapons":           "shop",
    "Fletcher's Armory":          "shop",
    "The Arcane Shelf":           "shop",
    "Newhaven General Store":     "shop",
    "Healer's Cottage":           "healer",
    "Training Grounds":           "trainer",
    "Boatman's Dock":             "dock",
    "River Crossing":             "wilderness",
    "Old East Road":              "wilderness",
    "Arena Entrance":             "dungeon",
    "The Arena Floor":            "dungeon",
    "Bandit Hideout":             "dungeon",
}

# Rooms that are considered outdoors (for foraging / hp_regen_outdoor)
_OUTDOOR_ROOMS = {
    "Village Center of Newhaven",
    "North Road",
    "South Road",
    "Training Grounds",
    "Boatman's Dock",
    "River Crossing",
    "Old East Road",
}


def patch_newhaven_room_types():
    """
    Backfill db.room_type on any Newhaven room that is missing it.
    Safe to call every server start — skips rooms already tagged.
    """
    for room_key, room_type in _ROOM_TYPES.items():
        matches = evennia.search_object(room_key, typeclass="typeclasses.rooms.Room")
        for room in matches:
            if room.db.zone == "newhaven" and room.db.room_type != room_type:
                room.db.room_type = room_type


def patch_newhaven_outdoors():
    """
    Backfill db.is_outdoor and db.recent_visitors on existing Newhaven rooms.
    Safe to call every server start.
    """
    for room_key in _OUTDOOR_ROOMS:
        matches = evennia.search_object(room_key, typeclass="typeclasses.rooms.Room")
        for room in matches:
            if room.db.zone == "newhaven":
                room.db.is_outdoor = True
                if room.db.recent_visitors is None:
                    room.db.recent_visitors = []
    # Non-outdoor rooms also need recent_visitors initialized
    for room_key in _ROOM_TYPES:
        if room_key not in _OUTDOOR_ROOMS:
            matches = evennia.search_object(room_key, typeclass="typeclasses.rooms.Room")
            for room in matches:
                if room.db.zone == "newhaven" and room.db.recent_visitors is None:
                    room.db.recent_visitors = []


def build_newhaven():
    """
    Build the town of Newhaven. Returns the Village Center room on success,
    or None if it already exists.
    """
    if evennia.search_object("Village Center of Newhaven"):
        return None

    # ── Rooms ──────────────────────────────────────────────────────────────────

    center = _room(
        "Village Center of Newhaven",
        aliases=["newhaven_entrance"],
        desc=(
            "The heart of Newhaven, where the roads from the four compass points "
            "converge at a worn cobblestone plaza. A weathered signpost stands at "
            "the center, its arrows smoothed by years of travelers' hands. The "
            "smell of cookfire and tallow drifts from the surrounding buildings. "
            "A stone staircase descends into the earth nearby."
        ),
    )
    center.db.is_start_room = True
    center.db.room_type = "center"
    center.db.is_outdoor = True
    center.db.recent_visitors = []

    north_road = _room(
        "North Road",
        desc=(
            "A dirt track lit by sputtering torches. Harden's weapon shop "
            "faces the road to the west; Fletcher's armory rises to the east. "
            "The training grounds lie further north, and Newhaven's center "
            "is a short walk south."
        ),
    )
    north_road.db.room_type = "road"
    north_road.db.is_outdoor = True
    north_road.db.recent_visitors = []

    south_road = _room(
        "South Road",
        desc=(
            "The road narrows toward the river. The healer's cottage sits "
            "quietly to the west. The boatman's dock extends eastward over "
            "dark water. The river crossing lies to the south, and the "
            "village center is back to the north."
        ),
    )
    south_road.db.room_type = "road"
    south_road.db.is_outdoor = True
    south_road.db.recent_visitors = []

    weapon_shop = _room(
        "Harden's Weapons",
        desc=(
            "Racks of blades, hafts, and bows line the walls. The smell of "
            "oil and iron is thick. Harden stands behind a heavy counter, "
            "appraising each visitor with a merchant's flat eye."
        ),
    )
    weapon_shop.db.room_type = "shop"
    weapon_shop.db.recent_visitors = []

    armor_shop = _room(
        "Fletcher's Armory",
        desc=(
            "Suits of leather and chainmail hang from iron pegs along the "
            "walls. Shield bosses catch the lamplight. Fletcher looks up "
            "from a helm she is polishing."
        ),
    )
    armor_shop.db.room_type = "shop"
    armor_shop.db.recent_visitors = []

    spell_shop = _room(
        "The Arcane Shelf",
        desc=(
            "Floor-to-ceiling shelves crowd with scroll cases, inkpots, and "
            "arcane components. A faint smell of ozone lingers. Mira moves "
            "silently between the stacks, cataloguing her wares."
        ),
    )
    spell_shop.db.room_type = "shop"
    spell_shop.db.recent_visitors = []

    general_store = _room(
        "Newhaven General Store",
        desc=(
            "Barrels, crates, and hanging dried goods fill every corner. "
            "Old Bern leans against the counter, pipe in hand, watching "
            "customers with half-lidded eyes."
        ),
    )
    general_store.db.room_type = "shop"
    general_store.db.recent_visitors = []

    healer = _room(
        "Healer's Cottage",
        desc=(
            "A modest room smelling of dried herbs and clean linen. Bundles "
            "of feverfew and comfrey hang from the rafters. Sister Elara "
            "looks up from her pestle with a gentle, weary smile."
        ),
    )
    healer.db.room_type = "healer"
    healer.db.recent_visitors = []

    training_grounds = _room(
        "Training Grounds",
        desc=(
            "A wide courtyard of packed earth, scarred by years of practice "
            "blows. Weapon racks line one wall. Master Aldric stands with "
            "arms crossed, watching for those ready to advance."
        ),
    )
    training_grounds.db.room_type = "trainer"
    training_grounds.db.is_outdoor = True
    training_grounds.db.recent_visitors = []

    boatman_dock = _room(
        "Boatman's Dock",
        desc=(
            "Planks creak underfoot over dark, slow water. A skiff sits "
            "lashed to the dock pilings. The Boatman regards you from "
            "beneath a wide-brimmed hat, waiting without expectation."
        ),
    )
    boatman_dock.db.room_type = "dock"
    boatman_dock.db.is_outdoor = True
    boatman_dock.db.recent_visitors = []

    river_crossing = _room(
        "River Crossing",
        desc=(
            "A low stone bridge spans a slow river. Across it, the Old "
            "East Road stretches toward distant hills. Newhaven lies "
            "north behind you. The road east leads into the wilderness."
        ),
    )
    river_crossing.db.room_type = "wilderness"
    river_crossing.db.is_outdoor = True
    river_crossing.db.recent_visitors = []

    road_east = _room(
        "Old East Road",
        desc=(
            "A rutted track winds east through sparse woodland. The road "
            "fades further on, swallowed by overgrowth. Whatever lies "
            "beyond has not been travelled in some time."
        ),
    )
    road_east.db.room_type = "wilderness"
    road_east.db.is_outdoor = True
    road_east.db.recent_visitors = []

    arena_entrance = _room(
        "Arena Entrance",
        desc=(
            "Stone steps lead down to a vaulted antechamber lit by iron "
            "sconces. Scrawled carvings mark the walls — tallies of past "
            "combats, names of the fallen. The sounds of scrabbling and "
            "hissing echo from deeper within. A narrow passage seems to "
            "lead east toward a heavy iron door."
        ),
    )
    arena_entrance.db.room_type = "dungeon"
    arena_entrance.db.recent_visitors = []
    arena_entrance.db.has_trap = True
    arena_entrance.db.trap_difficulty = 12
    arena_entrance.db.trap_damage = "1d6"
    arena_entrance.db.trap_type = "spike"
    arena_entrance.db.trap_discovered = False

    arena_floor = _room(
        "The Arena Floor",
        aliases=["newhaven_arena"],
        desc=(
            "A circular chamber of packed earth and old bloodstains. Stone "
            "seating rings the walls above, empty and dark. Several large "
            "rats move in the shadows — they own this place now."
        ),
    )
    arena_floor.db.room_type = "dungeon"
    arena_floor.db.recent_visitors = []

    bandit_hideout = _room(
        "Bandit Hideout",
        desc=(
            "A dank chamber carved from living rock. Bedrolls, empty bottles, "
            "and stolen goods litter the floor. The bandits have made themselves "
            "quite at home here."
        ),
    )
    bandit_hideout.db.room_type = "dungeon"
    bandit_hideout.db.recent_visitors = []

    # ── Exits ──────────────────────────────────────────────────────────────────

    _link(center,       north_road,       "north", "south")
    _link(center,       south_road,       "south", "north")
    _link(center,       spell_shop,       "east",  "west")
    _link(center,       general_store,    "west",  "east")
    _link(center,       arena_entrance,   "down",  "up")

    _link(north_road,   training_grounds, "north", "south")
    _link(north_road,   weapon_shop,      "west",  "east")
    _link(north_road,   armor_shop,       "east",  "west")

    _link(south_road,   healer,           "west",  "east")
    _link(south_road,   boatman_dock,     "east",  "west")
    _link(south_road,   river_crossing,   "south", "north")

    _link(river_crossing, road_east,      "east",  "west")

    _link(arena_entrance, arena_floor,    "east",  "west")

    # Locked bandit hideout east of South Road (requires lockpick)
    bandit_door = create_object(
        typeclass="typeclasses.exits.Exit",
        key="heavy door",
        aliases=["east", "e", "door"],
        location=south_road,
        destination=bandit_hideout,
    )
    bandit_door.db.lock_difficulty = 15
    bandit_door.db.is_locked = True
    bandit_door.db.desc = "A heavy iron-banded door, firmly locked."
    bandit_door.locks.add("traverse:false()")
    # Return exit from hideout (unlocked from inside)
    _exit("west", bandit_hideout, south_road)

    # ── NPC stubs (non-hostile, no economy yet) ────────────────────────────────

    aldric = _npc(
        "Master Aldric",
        training_grounds,
        "A veteran fighter with close-cropped grey hair and calm eyes. "
        "His bearing speaks of long years at arms. He is available to "
        "train those who have earned their next level.",
        aliases=["aldric", "trainer"],
    )
    aldric.tags.add("trainer", category="npc_role")
    aldric.tags.add("skill_trainer", category="npc_role")

    _npc(
        "Harden",
        weapon_shop,
        "A broad-shouldered man with forge-scarred forearms and a "
        "measuring eye. He knows every blade in the shop by weight.",
        aliases=["harden", "weaponsmith"],
    )

    _npc(
        "Fletcher",
        armor_shop,
        "A wiry, methodical woman with ink-stained fingers and a "
        "habit of humming while she works.",
        aliases=["fletcher", "armorer"],
    )

    _npc(
        "Mira",
        spell_shop,
        "A slight woman in grey robes, her eyes carrying the calm "
        "focus of someone who reads very small text in very dim light.",
        aliases=["mira", "spellseller"],
    )

    _npc(
        "Old Bern",
        general_store,
        "A heavyset man who looks as permanent as the store itself. "
        "He has sold goods here since before the current signpost.",
        aliases=["bern", "storekeeper"],
    )

    _npc(
        "Sister Elara",
        healer,
        "A serene woman in simple robes who tends her herbs with "
        "quiet efficiency. She will patch the wounded without judgment.",
        aliases=["elara", "healer_npc"],
    )

    _npc(
        "The Boatman",
        boatman_dock,
        "A weathered figure whose face you cannot quite place. He "
        "offers passage across the river to those who ask.",
        aliases=["boatman"],
    )

    # ── Arena monsters ─────────────────────────────────────────────────────────

    for _ in range(3):
        rats = spawn({"prototype_parent": "GIANT_RAT", "location": arena_floor})
        if rats:
            # Ensure the rat is placed correctly
            rats[0].location = arena_floor

    return center
