"""
New Silvermere world builder.

The second major town, targeted at levels 5-15. Connected to Newhaven via
a skiff from Boatman's Dock. Modelled faithfully on MajorMUD's Silvermere.

Layout:
                     [Adventurer's Guild]
                            |  north
  [Helfgrim's Blades] -- [Crown Street] -- [Colin's Maces]
         west                  |  south              east
  [Sentara's Clothing] -- [Town Square] -- [Aiken's Magic Shoppe]
         west          nw/    |  south  \\se              east
             [Silvermere Bank]  [Temple Road] --east-- [Temple Chapel]
                                   |  south (via Market Lane chain)
    [Wailing Hound] -- [Market Lane] -- [Giovanni's General Store]
         west                |  south              east
   [Thuluk's Axes] -- [Riverside Walk] -- [Skali's Fine Armour]
         west                |  south              east
   [Jael's Missile] -- [Silvermere Pier] -- [Curio Store - Meia]
         west                                         east

Underground (down from Town Square via manhole):
  [Town Square] --down--> [Sewer Entrance] --east--> [Sewer Tunnel] --east--> [Sewer Chamber]
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
    """Create a New Silvermere room."""
    room = create_object(
        typeclass="typeclasses.rooms.Room",
        key=key,
        aliases=aliases or [],
    )
    room.db.desc = desc
    room.db.zone = "newsilvermere"
    room.db.recent_visitors = []
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


def _merchant(name, location, desc, shop_type, shop_inventory,
               aliases=None, no_negotiate=False, buys_items=True):
    """Create a Merchant NPC with shop inventory."""
    merchant = create_object(
        typeclass="typeclasses.merchants.Merchant",
        key=name,
        aliases=aliases or [],
        location=location,
    )
    merchant.db.desc = desc
    merchant.db.faction = "neutral"
    merchant.db.ai_profile = None
    merchant.db.level = 0
    merchant.db.hp = 100
    merchant.db.hp_max = 100
    merchant.db.threat_table = {}
    merchant.db.in_combat = None
    merchant.db.shop_type = shop_type
    merchant.db.shop_inventory = shop_inventory
    merchant.db.no_negotiate = no_negotiate
    merchant.db.buys_items = buys_items
    return merchant


# Map from room key → room_type, used by patch_newsilvermere_room_types()
_ROOM_TYPES = {
    "Town Square of New Silvermere": "center",
    "Crown Street":                  "road",
    "Market Lane":                   "road",
    "Temple Road":                   "road",
    "Riverside Walk":                "road",
    "Silvermere Pier":               "dock",
    "Adventurer's Guild":            "trainer",
    "Helfgrim's Blades":             "shop",
    "Colin's Maces":                 "shop",
    "Thuluk's Axes":                 "shop",
    "Jael's Missile Weapons":        "shop",
    "Skali's Fine Armour":           "shop",
    "Sentara's Clothing":            "shop",
    "Aiken's Magic Shoppe":          "shop",
    "Giovanni's General Store":      "shop",
    "The Wailing Hound":             "shop",
    "Curio Store":                   "shop",
    "Temple Chapel":                 "healer",
    "Silvermere Bank":               "bank",
    "Sewer Entrance":                "dungeon",
    "Sewer Tunnel":                  "dungeon",
    "Sewer Chamber":                 "dungeon",
}

# Rooms considered outdoors (foraging / hp_regen_outdoor)
_OUTDOOR_ROOMS = {
    "Town Square of New Silvermere",
    "Crown Street",
    "Market Lane",
    "Temple Road",
    "Riverside Walk",
    "Silvermere Pier",
}


def patch_newsilvermere_room_types():
    """
    Backfill db.room_type on any New Silvermere room that is missing it.
    Safe to call every server start.
    """
    for room_key, room_type in _ROOM_TYPES.items():
        matches = evennia.search_object(room_key, typeclass="typeclasses.rooms.Room")
        for room in matches:
            if room.db.zone == "newsilvermere" and room.db.room_type != room_type:
                room.db.room_type = room_type


def patch_newsilvermere_outdoors():
    """
    Backfill db.is_outdoor and db.recent_visitors on New Silvermere rooms.
    Safe to call every server start.
    """
    for room_key in _OUTDOOR_ROOMS:
        matches = evennia.search_object(room_key, typeclass="typeclasses.rooms.Room")
        for room in matches:
            if room.db.zone == "newsilvermere":
                room.db.is_outdoor = True
                if room.db.recent_visitors is None:
                    room.db.recent_visitors = []
    for room_key in _ROOM_TYPES:
        if room_key not in _OUTDOOR_ROOMS:
            matches = evennia.search_object(room_key, typeclass="typeclasses.rooms.Room")
            for room in matches:
                if room.db.zone == "newsilvermere" and room.db.recent_visitors is None:
                    room.db.recent_visitors = []


def build_newsilvermere():
    """
    Build the town of New Silvermere. Returns the Town Square on success,
    or None if it already exists.
    """
    if evennia.search_object("Town Square of New Silvermere"):
        return None

    # ── Rooms ──────────────────────────────────────────────────────────────────

    square = _room(
        "Town Square of New Silvermere",
        aliases=["newsilvermere_center"],
        desc=(
            "The broad central plaza of New Silvermere. Cobblestones worn "
            "smooth by years of commerce radiate outward from a stone "
            "fountain at the centre, its basin crusted with moss. The "
            "smells of bread, leather, and horse manure mingle in the "
            "salt-tinged breeze off the river. Streets branch in every "
            "direction. A heavy iron manhole cover sits flush with the "
            "stones near the fountain's base."
        ),
    )
    square.db.room_type = "center"
    square.db.is_outdoor = True

    crown = _room(
        "Crown Street",
        desc=(
            "A wide, well-maintained street running north past the "
            "Adventurer's Guild. Shops line both sides: a blade-smith "
            "to the west and a mace-wright to the east. The town square "
            "lies to the south."
        ),
    )
    crown.db.room_type = "road"
    crown.db.is_outdoor = True

    market = _room(
        "Market Lane",
        desc=(
            "A narrower street than Crown, but lively with haggling. "
            "The Wailing Hound tavern spills lamplight from the west; "
            "Giovanni's general store faces it from the east. The "
            "town square is a short walk north, and the docks lie south."
        ),
    )
    market.db.room_type = "road"
    market.db.is_outdoor = True

    temple_road = _room(
        "Temple Road",
        desc=(
            "A quiet, straight road paved with fitted stone, leading "
            "east toward the temple's arched entrance. The noise of "
            "the town square fades behind you. Incense drifts on the "
            "breeze from the chapel ahead."
        ),
    )
    temple_road.db.room_type = "road"
    temple_road.db.is_outdoor = True

    riverside = _room(
        "Riverside Walk",
        desc=(
            "A stone-paved promenade along the riverbank. The smell of "
            "mud and fish is sharp here. Thuluk's axe shop occupies a "
            "long shed to the west; Skali's armour workshop rises to "
            "the east. The pier extends southward over dark water."
        ),
    )
    riverside.db.room_type = "road"
    riverside.db.is_outdoor = True

    pier = _room(
        "Silvermere Pier",
        aliases=["newsilvermere_pier"],
        desc=(
            "Planks of salt-bleached timber stretch out over the slow "
            "river. A skiff is lashed to the mooring post, its oars "
            "shipped and ready. The Pier Boatman stands at the end, "
            "watching the far bank with unhurried patience. The "
            "missile weapons shop occupies a low shed to the west; "
            "Meia's curio store is tucked in the east."
        ),
    )
    pier.db.room_type = "dock"
    pier.db.is_outdoor = True

    # ── Indoor rooms ────────────────────────────────────────────────────────────

    guild = _room(
        "Adventurer's Guild",
        desc=(
            "A long hall of rough-hewn beams hung with old trophies and "
            "faded adventure notices. The Universal Trainer holds court "
            "near a well-used sparring dummy, ready to help seasoned "
            "adventurers reach their next level. A board near the door "
            "lists current bounties."
        ),
    )
    guild.db.room_type = "trainer"

    helfgrims = _room(
        "Helfgrim's Blades",
        desc=(
            "Sword racks crowd every wall, each blade tagged with neat "
            "handwriting. The air smells of honing oil. Helfgrim moves "
            "between the racks with the unhurried confidence of a man "
            "who knows the value of every piece in his shop."
        ),
    )
    helfgrims.db.room_type = "shop"

    colins = _room(
        "Colin's Maces",
        desc=(
            "Rows of maces, flails, and staves line the walls on padded "
            "pegs. A massive maul hangs from the ceiling on display. "
            "Colin watches from behind his counter with a cheerful, "
            "gap-toothed grin."
        ),
    )
    colins.db.room_type = "shop"

    sentara = _room(
        "Sentara's Clothing",
        desc=(
            "Bolts of fabric in every weight fill the back shelves. "
            "Ready-made cloaks and robes hang from iron rails near the "
            "door. Lady Sentara greets you with cool professionalism — "
            "she has dressed warriors and nobles alike."
        ),
    )
    sentara.db.room_type = "shop"

    aiken = _room(
        "Aiken's Magic Shoppe",
        desc=(
            "Glass cases and locked cabinets hold components, curios, "
            "and implements of uncertain purpose. Aiken stands behind "
            "the counter in ink-stained robes, peering over his "
            "spectacles with restrained enthusiasm."
        ),
    )
    aiken.db.room_type = "shop"

    bank = _room(
        "Silvermere Bank",
        desc=(
            "Thick stone walls and iron-barred windows give this room "
            "an atmosphere of impregnability. Teller Halvard stands at "
            "a polished counter behind reinforced glass, ready to manage "
            "deposits and withdrawals for trusted customers."
        ),
    )
    bank.db.room_type = "bank"

    temple_chapel = _room(
        "Temple Chapel",
        desc=(
            "High vaulted ceilings draw the eye upward to painted "
            "scenes of divine intervention. Candles burn in tiered "
            "holders along the nave. Sister Margery tends the altar "
            "with quiet devotion, pausing to offer aid to the wounded "
            "and weary."
        ),
    )
    temple_chapel.db.room_type = "healer"

    wailing = _room(
        "The Wailing Hound",
        desc=(
            "A low-ceilinged tavern thick with pipe smoke and the smell "
            "of spilled ale. A stuffed hound of dubious provenance "
            "regards the room from above the bar. Barkeep Nessa wipes "
            "down the counter, eyeing each customer in the mirror."
        ),
    )
    wailing.db.room_type = "shop"

    giovanni = _room(
        "Giovanni's General Store",
        desc=(
            "Shelves crammed with provisions, cordage, lamp oil, and "
            "the sundry necessities of adventuring life. Giovanni "
            "stands at the counter with the easy warmth of a man who "
            "has seen everything come through his door."
        ),
    )
    giovanni.db.room_type = "shop"

    thuluk = _room(
        "Thuluk's Axes",
        desc=(
            "The walls are hung with axes of every size, from small "
            "hatchets to enormous pole-arms. Shavings of iron on the "
            "floor speak to recent grinding. Thuluk, a broad Half-Orc, "
            "eyes you from behind a cluttered workbench."
        ),
    )
    thuluk.db.room_type = "shop"

    skali = _room(
        "Skali's Fine Armour",
        desc=(
            "Complete suits of armour stand on wooden mannequins "
            "throughout the workshop. Scale, chain, and plate gleam "
            "under oil lamps. Skali moves between them, testing "
            "joints with methodical satisfaction."
        ),
    )
    skali.db.room_type = "shop"

    jael = _room(
        "Jael's Missile Weapons",
        desc=(
            "Longbows and crossbows hang from pegged boards, each "
            "strung and labelled. Quivers of fletched bolts and arrows "
            "fill the racks below. Jael sits in the corner stringing "
            "a new bow, working by feel without looking up."
        ),
    )
    jael.db.room_type = "shop"

    curio = _room(
        "Curio Store",
        desc=(
            "Shelves of odd objects, strange stones, and nameless "
            "trinkets crowd every surface. Meia drifts among them "
            "like a ghost, rearranging things only she understands. "
            "Some items here may be worth more than they appear."
        ),
    )
    curio.db.room_type = "shop"

    # ── Sewers ──────────────────────────────────────────────────────────────────

    sewer_entrance = _room(
        "Sewer Entrance",
        desc=(
            "Iron rungs descend from the manhole into a low-ceilinged "
            "tunnel of mortared stone. The air is damp and fetid. Water "
            "trickles along a central channel. Faint scraping sounds "
            "echo from further in. A passage continues east."
        ),
    )
    sewer_entrance.db.room_type = "dungeon"
    sewer_entrance.db.is_dungeon = True

    sewer_tunnel = _room(
        "Sewer Tunnel",
        desc=(
            "The tunnel widens here, the ceiling arching higher. Old "
            "iron brackets once held torches; now they hold nothing "
            "but rust. Slick green growth covers the lower walls. "
            "Something moves in the water ahead. The tunnel continues east."
        ),
    )
    sewer_tunnel.db.room_type = "dungeon"
    sewer_tunnel.db.is_dungeon = True

    sewer_chamber = _room(
        "Sewer Chamber",
        desc=(
            "A vaulted chamber where three drainage channels converge. "
            "The floor is perpetually wet. Thick, pale worms have made "
            "their home in the dark beyond the water's edge — enormous "
            "things that fill the tunnel when they move. There is nowhere "
            "to go but back."
        ),
    )
    sewer_chamber.db.room_type = "dungeon"
    sewer_chamber.db.is_dungeon = True

    # ── Exits ──────────────────────────────────────────────────────────────────

    # Main north-south spine
    _link(pier,     riverside, "north", "south")
    _link(riverside, market,   "north", "south")
    _link(market,   square,    "north", "south")
    _link(square,   crown,     "north", "south")
    _link(crown,    guild,     "north", "south")

    # Crown Street east-west shops
    _link(crown, helfgrims, "west", "east")
    _link(crown, colins,    "east", "west")

    # Town Square east-west shops + bank + temple road
    _link(square, sentara,     "west",      "east")
    _link(square, aiken,       "east",      "west")
    _link(square, bank,        "northwest", "southeast")
    _link(square, temple_road, "southeast", "northwest")

    # Temple Road
    _link(temple_road, temple_chapel, "east", "west")

    # Market Lane east-west shops
    _link(market, wailing,  "west", "east")
    _link(market, giovanni, "east", "west")

    # Riverside Walk east-west shops
    _link(riverside, thuluk, "west", "east")
    _link(riverside, skali,  "east", "west")

    # Pier east-west shops
    _link(pier, jael,  "west", "east")
    _link(pier, curio, "east", "west")

    # Sewers (down from Town Square)
    _link(square,         sewer_entrance, "down",  "up")
    _link(sewer_entrance, sewer_tunnel,   "east",  "west")
    _link(sewer_tunnel,   sewer_chamber,  "east",  "west")

    # ── NPCs ───────────────────────────────────────────────────────────────────

    # Adventurer's Guild trainer
    trainer = _npc(
        "Universal Trainer",
        guild,
        "A weathered veteran whose calm eyes have seen adventurers of every "
        "stripe come and go. He trains any willing student who has earned "
        "their next level, regardless of class or creed.",
        aliases=["trainer", "universal trainer"],
    )
    trainer.tags.add("trainer", category="npc_role")
    trainer.tags.add("skill_trainer", category="npc_role")

    # Pier Boatman (flavor)
    _npc(
        "Pier Boatman",
        pier,
        "A sun-browned man with calloused hands who watches the far bank "
        "as if expecting someone. He nods at you without particular interest.",
        aliases=["pier boatman", "boatman"],
    )

    # Bank Teller
    halvard = _npc(
        "Teller Halvard",
        bank,
        "A compact, precise man with close-cropped hair and the careful "
        "manners of someone who handles other people's money for a living. "
        "His ledger is always open.",
        aliases=["halvard", "teller"],
    )
    halvard.tags.add("bank", category="npc_role")

    # ── Merchants ──────────────────────────────────────────────────────────────

    _merchant(
        "Helfgrim",
        helfgrims,
        "A compact, sharp-eyed man with a forge-scarred right hand and the "
        "measured speech of someone who weighs each word like blade steel.",
        shop_type="weapons",
        shop_inventory=[
            {"prototype_key": "RUSTY_DAGGER",  "stock": -1, "price_override": None},
            {"prototype_key": "SHORT_SWORD",   "stock": -1, "price_override": None},
            {"prototype_key": "STILETTO",      "stock": -1, "price_override": None},
            {"prototype_key": "BROADSWORD",    "stock": -1, "price_override": None},
            {"prototype_key": "FALCHION",      "stock": -1, "price_override": None},
            {"prototype_key": "SCIMITAR",      "stock": -1, "price_override": None},
            {"prototype_key": "GREATSWORD",    "stock": -1, "price_override": None},
        ],
        aliases=["helfgrim", "bladeseller"],
    )

    _merchant(
        "Colin",
        colins,
        "A broad-shouldered man who handles even the heaviest maul with "
        "one hand and never loses his cheerful disposition.",
        shop_type="weapons",
        shop_inventory=[
            {"prototype_key": "IRON_STAFF",   "stock": -1, "price_override": None},
            {"prototype_key": "MACE",         "stock": -1, "price_override": None},
            {"prototype_key": "FLAIL",        "stock": -1, "price_override": None},
            {"prototype_key": "MORNING_STAR", "stock": -1, "price_override": None},
            {"prototype_key": "MAUL",         "stock": -1, "price_override": None},
            {"prototype_key": "SICKLE",       "stock": -1, "price_override": None},
        ],
        aliases=["colin", "macewright"],
    )

    _merchant(
        "Thuluk",
        thuluk,
        "A barrel-chested Half-Orc with iron filings permanently ground "
        "into his knuckles. He speaks in short sentences and favours action "
        "over words — much like his merchandise.",
        shop_type="weapons",
        shop_inventory=[
            {"prototype_key": "HAND_AXE",   "stock": -1, "price_override": None},
            {"prototype_key": "BATTLE_AXE", "stock": -1, "price_override": None},
            {"prototype_key": "HALBERD",    "stock": -1, "price_override": None},
            {"prototype_key": "SPEAR",      "stock": -1, "price_override": None},
            {"prototype_key": "TRIDENT",    "stock": -1, "price_override": None},
        ],
        aliases=["thuluk", "axesmith"],
    )

    _merchant(
        "Jael",
        jael,
        "A lean, quiet woman who moves with the unhurried precision of "
        "a practiced archer. She says little and knows everything about "
        "the equipment she sells.",
        shop_type="weapons",
        shop_inventory=[
            {"prototype_key": "LONGBOW",  "stock": -1, "price_override": None},
            {"prototype_key": "CROSSBOW", "stock": -1, "price_override": None},
        ],
        aliases=["jael", "bowyer"],
    )

    _merchant(
        "Skali",
        skali,
        "A compact craftsman with the unhurried manner of someone who has "
        "never made a piece of armour he was not proud of. He inspects "
        "your current gear with professional curiosity.",
        shop_type="armor",
        shop_inventory=[
            {"prototype_key": "CHAIN_COIF",      "stock": -1, "price_override": None},
            {"prototype_key": "CHAIN_MAIL",      "stock": -1, "price_override": None},
            {"prototype_key": "CHAIN_VAMBRACES", "stock": -1, "price_override": None},
            {"prototype_key": "CHAIN_LEGGINGS",  "stock": -1, "price_override": None},
            {"prototype_key": "IRON_BOOTS",      "stock": -1, "price_override": None},
            {"prototype_key": "IRON_HELM",       "stock": -1, "price_override": None},
            {"prototype_key": "PLATE_MAIL",      "stock": -1, "price_override": None},
            {"prototype_key": "IRON_VAMBRACES",  "stock": -1, "price_override": None},
            {"prototype_key": "IRON_GAUNTLETS",  "stock": -1, "price_override": None},
            {"prototype_key": "PLATE_LEGGINGS",  "stock": -1, "price_override": None},
            {"prototype_key": "IRON_SABATONS",   "stock": -1, "price_override": None},
            {"prototype_key": "SCALE_MAIL",      "stock": -1, "price_override": None},
            {"prototype_key": "TOWER_SHIELD",    "stock": -1, "price_override": None},
        ],
        aliases=["skali", "armourer"],
    )

    _merchant(
        "Lady Sentara",
        sentara,
        "A tall, elegant woman with impeccable posture and an eye for "
        "fabric weight. She has dressed everyone from peasants to "
        "minor nobility without altering her tone.",
        shop_type="armor",
        shop_inventory=[
            {"prototype_key": "PLAIN_ROBES",      "stock": -1, "price_override": None},
            {"prototype_key": "CLOTH_CAP",        "stock": -1, "price_override": None},
            {"prototype_key": "LEATHER_CAP",      "stock": -1, "price_override": None},
            {"prototype_key": "LEATHER_JERKIN",   "stock": -1, "price_override": None},
            {"prototype_key": "LEATHER_BRACERS",  "stock": -1, "price_override": None},
            {"prototype_key": "LEATHER_GLOVES",   "stock": -1, "price_override": None},
            {"prototype_key": "LEATHER_BELT",     "stock": -1, "price_override": None},
            {"prototype_key": "LEATHER_LEGGINGS", "stock": -1, "price_override": None},
            {"prototype_key": "LEATHER_BOOTS",    "stock": -1, "price_override": None},
            {"prototype_key": "GREATCLOAK",       "stock": -1, "price_override": None},
        ],
        aliases=["sentara", "lady sentara", "clothier"],
    )

    _merchant(
        "Aiken",
        aiken,
        "A middle-aged mage in ink-stained robes who peers at customers "
        "over half-moon spectacles. He sells components and curiosities; "
        "spell scrolls are future work.",
        shop_type="magic",
        shop_inventory=[],   # spell scrolls: future work
        aliases=["aiken", "magician"],
    )

    _merchant(
        "Giovanni",
        giovanni,
        "A broad, cheerful man with a thick accent and an encyclopedic "
        "knowledge of what every traveller needs before setting out. "
        "His shelves are always stocked.",
        shop_type="general",
        shop_inventory=[
            {"prototype_key": "HEALING_POTION", "stock": -1, "price_override": None},
            {"prototype_key": "TORCH",          "stock": -1, "price_override": None},
            {"prototype_key": "IRON_RATION",    "stock": -1, "price_override": None},
        ],
        aliases=["giovanni", "storekeeper"],
    )

    _merchant(
        "Sister Margery",
        temple_chapel,
        "A serene woman in white robes who tends both the altar and the "
        "wounded with equal dedication. She sells healing supplies and, "
        "for those of the faith, a blessed weapon.",
        shop_type="healer",
        shop_inventory=[
            {"prototype_key": "HEALING_POTION", "stock": -1, "price_override": None},
            {"prototype_key": "SILVERY_MACE",   "stock": -1, "price_override": 150},
        ],
        aliases=["margery", "sister margery", "healer"],
    )

    _merchant(
        "Barkeep Nessa",
        wailing,
        "A sturdy woman with thick forearms and a sharp wit, who keeps "
        "order in the Wailing Hound through force of personality alone. "
        "She stocks the basics for travelling adventurers.",
        shop_type="general",
        shop_inventory=[
            {"prototype_key": "HEALING_POTION", "stock": -1, "price_override": None},
        ],
        aliases=["nessa", "barkeep"],
    )

    _merchant(
        "Meia",
        curio,
        "A slight, ageless woman who drifts among her curios as if she "
        "has all the time in the world. Her stock is eclectic; her prices "
        "are her own business.",
        shop_type="general",
        shop_inventory=[],   # curios and gems: future work
        aliases=["meia", "curio seller"],
    )

    # ── Sewer monsters ─────────────────────────────────────────────────────────

    for _ in range(2):
        result = spawn({"prototype_parent": "SEWER_RAT", "location": sewer_entrance})
        if result:
            result[0].location = sewer_entrance

    for _ in range(2):
        result = spawn({"prototype_parent": "WHITE_JELLY", "location": sewer_tunnel})
        if result:
            result[0].location = sewer_tunnel

    for _ in range(3):
        result = spawn({"prototype_parent": "CAVE_WORM", "location": sewer_chamber})
        if result:
            result[0].location = sewer_chamber

    return square
