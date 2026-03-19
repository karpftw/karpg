"""
Prototypes

A prototype is a simple way to create individualized instances of a
given typeclass. It is dictionary with specific key names.

For example, you might have a Sword typeclass that implements everything a
Sword would need to do. The only difference between different individual Swords
would be their key, description and some Attributes. The Prototype system
allows to create a range of such Swords with only minor variations. Prototypes
can also inherit and combine together to form entire hierarchies (such as
giving all Sabres and all Broadswords some common properties). Note that bigger
variations, such as custom commands or functionality belong in a hierarchy of
typeclasses instead.

A prototype can either be a dictionary placed into a global variable in a
python module (a 'module-prototype') or stored in the database as a dict on a
special Script (a db-prototype). The former can be created just by adding dicts
to modules Evennia looks at for prototypes, the latter is easiest created
in-game via the `olc` command/menu.

Prototypes are read and used to create new objects with the `spawn` command
or directly via `evennia.spawn` or the full path `evennia.prototypes.spawner.spawn`.

A prototype dictionary have the following keywords:

Possible keywords are:
- `prototype_key` - the name of the prototype. This is required for db-prototypes,
  for module-prototypes, the global variable name of the dict is used instead
- `prototype_parent` - string pointing to parent prototype if any. Prototype inherits
  in a similar way as classes, with children overriding values in their parents.
- `key` - string, the main object identifier.
- `typeclass` - string, if not set, will use `settings.BASE_OBJECT_TYPECLASS`.
- `location` - this should be a valid object or #dbref.
- `home` - valid object or #dbref.
- `destination` - only valid for exits (object or #dbref).
- `permissions` - string or list of permission strings.
- `locks` - a lock-string to use for the spawned object.
- `aliases` - string or list of strings.
- `attrs` - Attributes, expressed as a list of tuples on the form `(attrname, value)`,
  `(attrname, value, category)`, or `(attrname, value, category, locks)`. If using one
   of the shorter forms, defaults are used for the rest.
- `tags` - Tags, as a list of tuples `(tag,)`, `(tag, category)` or `(tag, category, data)`.
-  Any other keywords are interpreted as Attributes with no category or lock.
   These will internally be added to `attrs` (equivalent to `(attrname, value)`.

See the `spawn` command and `evennia.prototypes.spawner.spawn` for more info.

"""

## ── Weapons ──────────────────────────────────────────────────────────────────

RUSTY_DAGGER = {
    "prototype_key": "RUSTY_DAGGER",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "rusty dagger",
    "desc": (
        "A short blade pitted with rust along the fuller. The edge is "
        "notched but still serviceable. Better than empty hands."
    ),
    "attrs": [
        ("damage_dice",  "1d4"),
        ("damage_type",  "piercing"),
        ("weapon_type",  "dagger"),
        ("attack_range", "melee"),
        ("speed",        1.2),
        ("two_handed",   False),
        ("weight",       0.5),
        ("value",        2),
        ("enchantments", []),
        ("art_key",      "rusty_dagger"),
    ],
}

SHORT_SWORD = {
    "prototype_key": "SHORT_SWORD",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "short sword",
    "desc": (
        "A well-balanced one-handed blade, roughly two feet long. "
        "Favoured by scouts and light fighters for its quick draw."
    ),
    "attrs": [
        ("damage_dice",  "1d6"),
        ("damage_type",  "slashing"),
        ("weapon_type",  "sword"),
        ("attack_range", "melee"),
        ("speed",        1.0),
        ("two_handed",   False),
        ("weight",       2.0),
        ("value",        25),
        ("enchantments", []),
        ("art_key",      "short_sword"),
    ],
}

HAND_AXE = {
    "prototype_key": "HAND_AXE",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "hand axe",
    "desc": (
        "A compact axe with a broad iron head and a hickory haft. "
        "Equally useful for splitting kindling and splitting skulls."
    ),
    "attrs": [
        ("damage_dice",  "1d6"),
        ("damage_type",  "slashing"),
        ("weapon_type",  "axe"),
        ("attack_range", "melee"),
        ("speed",        0.9),
        ("two_handed",   False),
        ("weight",       2.5),
        ("value",        20),
        ("enchantments", []),
        ("art_key",      "hand_axe"),
    ],
}

IRON_STAFF = {
    "prototype_key": "IRON_STAFF",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "iron staff",
    "desc": (
        "A six-foot pole capped at both ends with iron rings. "
        "Heavy and unforgiving, it demands both hands and room to swing."
    ),
    "attrs": [
        ("damage_dice",  "1d6"),
        ("damage_type",  "bludgeoning"),
        ("weapon_type",  "staff"),
        ("attack_range", "melee"),
        ("speed",        0.8),
        ("two_handed",   True),
        ("weight",       4.0),
        ("value",        15),
        ("enchantments", []),
        ("art_key",      "iron_staff"),
    ],
}

LONGBOW = {
    "prototype_key": "LONGBOW",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "longbow",
    "desc": (
        "A tall yew bow strung with waxed linen. It demands considerable "
        "draw strength and two hands, but can place an arrow at great distance."
    ),
    "attrs": [
        ("damage_dice",  "1d8"),
        ("damage_type",  "piercing"),
        ("weapon_type",  "bow"),
        ("attack_range", "ranged"),
        ("speed",        0.7),
        ("two_handed",   True),
        ("weight",       2.0),
        ("value",        50),
        ("enchantments", []),
        ("art_key",      "longbow"),
    ],
}

BROADSWORD = {
    "prototype_key": "BROADSWORD",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "broadsword",
    "desc": (
        "A heavy double-edged blade that runs nearly four feet from pommel "
        "to tip. It strikes with bone-breaking force but asks both hands in return."
    ),
    "attrs": [
        ("damage_dice",  "2d4"),
        ("damage_type",  "slashing"),
        ("weapon_type",  "sword"),
        ("attack_range", "melee"),
        ("speed",        0.75),
        ("two_handed",   True),
        ("weight",       6.0),
        ("value",        75),
        ("enchantments", []),
        ("art_key",      "broadsword"),
    ],
}

## ── New Silvermere Weapons ────────────────────────────────────────────────────

STILETTO = {
    "prototype_key": "STILETTO",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "stiletto",
    "desc": (
        "A slender, needle-pointed dagger with a diamond-section blade. "
        "Its fine tip finds gaps in armour that broader blades cannot."
    ),
    "attrs": [
        ("damage_dice",  "1d6"),
        ("damage_type",  "piercing"),
        ("weapon_type",  "dagger"),
        ("attack_range", "melee"),
        ("speed",        1.1),
        ("two_handed",   False),
        ("weight",       0.4),
        ("value",        35),
        ("enchantments", []),
        ("art_key",      "stiletto"),
    ],
}

FALCHION = {
    "prototype_key": "FALCHION",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "falchion",
    "desc": (
        "A single-edged curved sword with a wide, clipped tip. Heavy at "
        "the point, it delivers devastating chopping blows."
    ),
    "attrs": [
        ("damage_dice",  "1d8"),
        ("damage_type",  "slashing"),
        ("weapon_type",  "sword"),
        ("attack_range", "melee"),
        ("speed",        0.9),
        ("two_handed",   False),
        ("weight",       3.0),
        ("value",        60),
        ("enchantments", []),
        ("art_key",      "falchion"),
    ],
}

SCIMITAR = {
    "prototype_key": "SCIMITAR",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "scimitar",
    "desc": (
        "A curved single-edged blade of southern make, balanced for "
        "swift slashing arcs. The blade sings when it cuts the air."
    ),
    "attrs": [
        ("damage_dice",  "1d8"),
        ("damage_type",  "slashing"),
        ("weapon_type",  "sword"),
        ("attack_range", "melee"),
        ("speed",        1.0),
        ("two_handed",   False),
        ("weight",       2.5),
        ("value",        65),
        ("enchantments", []),
        ("art_key",      "scimitar"),
    ],
}

GREATSWORD = {
    "prototype_key": "GREATSWORD",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "greatsword",
    "desc": (
        "A massive two-handed sword taller than most men. Its broad "
        "double-edged blade cleaves through armour and bone alike."
    ),
    "attrs": [
        ("damage_dice",  "2d6"),
        ("damage_type",  "slashing"),
        ("weapon_type",  "sword"),
        ("attack_range", "melee"),
        ("speed",        0.7),
        ("two_handed",   True),
        ("weight",       8.0),
        ("value",        120),
        ("enchantments", []),
        ("art_key",      "greatsword"),
    ],
}

MACE = {
    "prototype_key": "MACE",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "mace",
    "desc": (
        "A stout iron-headed club with flanged ridges that concentrate "
        "impact force. Favoured by those who prefer to break rather than cut."
    ),
    "attrs": [
        ("damage_dice",  "1d8"),
        ("damage_type",  "bludgeoning"),
        ("weapon_type",  "blunt"),
        ("attack_range", "melee"),
        ("speed",        0.9),
        ("two_handed",   False),
        ("weight",       3.5),
        ("value",        50),
        ("enchantments", []),
        ("art_key",      "mace"),
    ],
}

FLAIL = {
    "prototype_key": "FLAIL",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "flail",
    "desc": (
        "A wooden haft connected by a short chain to a spiked iron ball. "
        "Its unpredictable arc defeats shields and parries."
    ),
    "attrs": [
        ("damage_dice",  "1d8"),
        ("damage_type",  "bludgeoning"),
        ("weapon_type",  "blunt"),
        ("attack_range", "melee"),
        ("speed",        0.85),
        ("two_handed",   False),
        ("weight",       3.0),
        ("value",        55),
        ("enchantments", []),
        ("art_key",      "flail"),
    ],
}

MORNING_STAR = {
    "prototype_key": "MORNING_STAR",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "morning star",
    "desc": (
        "A heavy shaft topped with a spiked metal ball. It combines the "
        "crushing weight of a mace with the piercing menace of a spike."
    ),
    "attrs": [
        ("damage_dice",  "1d8+1"),
        ("damage_type",  "bludgeoning"),
        ("weapon_type",  "blunt"),
        ("attack_range", "melee"),
        ("speed",        0.85),
        ("two_handed",   False),
        ("weight",       4.0),
        ("value",        65),
        ("enchantments", []),
        ("art_key",      "morning_star"),
    ],
}

MAUL = {
    "prototype_key": "MAUL",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "maul",
    "desc": (
        "A massive two-handed war hammer with an iron head the size of a "
        "man's fist. It does not cut — it obliterates."
    ),
    "attrs": [
        ("damage_dice",  "2d6"),
        ("damage_type",  "bludgeoning"),
        ("weapon_type",  "blunt"),
        ("attack_range", "melee"),
        ("speed",        0.65),
        ("two_handed",   True),
        ("weight",       9.0),
        ("value",        100),
        ("enchantments", []),
        ("art_key",      "maul"),
    ],
}

SICKLE = {
    "prototype_key": "SICKLE",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "sickle",
    "desc": (
        "A curved iron blade on a short wooden haft. Originally a harvest "
        "tool, Druids have long found it suited to ritual and combat alike."
    ),
    "attrs": [
        ("damage_dice",  "1d6"),
        ("damage_type",  "slashing"),
        ("weapon_type",  "blunt"),
        ("attack_range", "melee"),
        ("speed",        1.0),
        ("two_handed",   False),
        ("weight",       1.5),
        ("value",        25),
        ("enchantments", []),
        ("art_key",      "sickle"),
    ],
}

BATTLE_AXE = {
    "prototype_key": "BATTLE_AXE",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "battle axe",
    "desc": (
        "A broad double-bitted axe head on a reinforced haft. Heavier than "
        "a hand axe but fearsomely powerful in practiced hands."
    ),
    "attrs": [
        ("damage_dice",  "1d10"),
        ("damage_type",  "slashing"),
        ("weapon_type",  "axe"),
        ("attack_range", "melee"),
        ("speed",        0.85),
        ("two_handed",   False),
        ("weight",       5.0),
        ("value",        80),
        ("enchantments", []),
        ("art_key",      "battle_axe"),
    ],
}

HALBERD = {
    "prototype_key": "HALBERD",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "halberd",
    "desc": (
        "A long polearm combining an axe blade with a spear point and a "
        "back spike. It keeps enemies at distance while delivering powerful blows."
    ),
    "attrs": [
        ("damage_dice",  "2d6"),
        ("damage_type",  "slashing"),
        ("weapon_type",  "axe"),
        ("attack_range", "melee"),
        ("speed",        0.7),
        ("two_handed",   True),
        ("weight",       7.0),
        ("value",        110),
        ("enchantments", []),
        ("art_key",      "halberd"),
    ],
}

SPEAR = {
    "prototype_key": "SPEAR",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "spear",
    "desc": (
        "A seven-foot ash shaft tipped with a leaf-bladed iron head. "
        "Light, quick, and reach-extending — the soldier's oldest weapon."
    ),
    "attrs": [
        ("damage_dice",  "1d8"),
        ("damage_type",  "piercing"),
        ("weapon_type",  "axe"),
        ("attack_range", "melee"),
        ("speed",        0.85),
        ("two_handed",   False),
        ("weight",       4.0),
        ("value",        45),
        ("enchantments", []),
        ("art_key",      "spear"),
    ],
}

TRIDENT = {
    "prototype_key": "TRIDENT",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "trident",
    "desc": (
        "A three-pronged iron trident on a reinforced haft. The multiple "
        "tines make parrying it difficult and catching weapons easier."
    ),
    "attrs": [
        ("damage_dice",  "1d8"),
        ("damage_type",  "piercing"),
        ("weapon_type",  "axe"),
        ("attack_range", "melee"),
        ("speed",        0.8),
        ("two_handed",   False),
        ("weight",       4.5),
        ("value",        55),
        ("enchantments", []),
        ("art_key",      "trident"),
    ],
}

CROSSBOW = {
    "prototype_key": "CROSSBOW",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "crossbow",
    "desc": (
        "A heavy steel-bowed crossbow with a cranked windlass mechanism. "
        "Slow to reload but devastating — it requires no great strength to use."
    ),
    "attrs": [
        ("damage_dice",  "1d8"),
        ("damage_type",  "piercing"),
        ("weapon_type",  "bow"),
        ("attack_range", "ranged"),
        ("speed",        0.6),
        ("two_handed",   True),
        ("weight",       3.0),
        ("value",        75),
        ("enchantments", []),
        ("art_key",      "crossbow"),
    ],
}

SILVERY_MACE = {
    "prototype_key": "SILVERY_MACE",
    "typeclass": "typeclasses.weapons.Weapon",
    "key": "silvery mace",
    "desc": (
        "A ceremonial mace with a head cast from silver-alloyed iron and "
        "etched with holy glyphs. It carries a divine resonance that "
        "unsettles the undead. Sold only at the Temple."
    ),
    "attrs": [
        ("damage_dice",  "1d8+2"),
        ("damage_type",  "bludgeoning"),
        ("weapon_type",  "blunt"),
        ("attack_range", "melee"),
        ("speed",        0.9),
        ("two_handed",   False),
        ("weight",       4.0),
        ("value",        150),
        ("dr_bonus",     2),
        ("enchantments", ["holy"]),
        ("art_key",      "silvery_mace"),
    ],
}

## ── Consumables / General Goods ──────────────────────────────────────────────

TORCH = {
    "prototype_key": "TORCH",
    "typeclass": "typeclasses.objects.Object",
    "key": "torch",
    "desc": "A pitch-soaked pine torch. Burns for about an hour.",
    "attrs": [
        ("weight",    0.3),
        ("value",     1),
        ("item_type", "misc"),
    ],
}

IRON_RATION = {
    "prototype_key": "IRON_RATION",
    "typeclass": "typeclasses.objects.Object",
    "key": "iron ration",
    "desc": "Hard tack, dried meat, and a pinch of salt wrapped in oilcloth. Keeps indefinitely.",
    "attrs": [
        ("weight",    0.5),
        ("value",     3),
        ("item_type", "misc"),
    ],
}

## ── Consumables ──────────────────────────────────────────────────────────────

HEALING_POTION = {
    "prototype_key": "HEALING_POTION",
    "typeclass": "typeclasses.objects.Object",
    "key": "healing potion",
    "desc": "A small vial of shimmering red liquid. Drinking it mends wounds.",
    "attrs": [
        ("weight",      0.2),
        ("value",       25),
        ("item_type",   "consumable"),
        ("heal_amount", 20),
    ],
}

## ── NPC Prototypes ───────────────────────────────────────────────────────────

GIANT_RAT = {
    "prototype_key": "GIANT_RAT",
    "typeclass": "typeclasses.npcs.NPC",
    "key": "giant rat",
    "desc": (
        "A rat the size of a large dog, with matted grey fur, yellowed teeth, "
        "and beady red eyes. It moves in quick, jerky bursts."
    ),
    "attrs": [
        ("hp",          10),
        ("hp_max",      10),
        ("ac",          11),
        ("dr",          0),
        ("level",       1),
        ("str",         7),
        ("agi",         14),
        ("int",         2),
        ("wis",         8),
        ("hlt",         8),
        ("chm",         3),
        ("faction",        "hostile"),
        ("ai_profile",     "cowardly"),
        ("xp_value",       25),
        ("loot_table",     []),
        ("threat_table",   {}),
        ("art_key",        "giant_rat"),
        ("prototype_key",  "GIANT_RAT"),
        ("respawn_delay",  120),
    ],
}

GOBLIN = {
    "prototype_key": "GOBLIN",
    "typeclass": "typeclasses.npcs.NPC",
    "key": "goblin",
    "desc": (
        "A scrawny, green-skinned creature with oversized ears and a wide, "
        "toothy grin. It clutches a crude blade and looks for an opening."
    ),
    "attrs": [
        ("hp",          18),
        ("hp_max",      18),
        ("ac",          12),
        ("dr",          0),
        ("level",       1),
        ("str",         8),
        ("agi",         13),
        ("int",         8),
        ("wis",         8),
        ("hlt",         9),
        ("chm",         5),
        ("faction",        "hostile"),
        ("ai_profile",     "cowardly"),
        ("xp_value",       50),
        ("loot_table",     []),
        ("threat_table",   {}),
        ("art_key",        "goblin"),
        ("prototype_key",  "GOBLIN"),
        ("respawn_delay",  180),
    ],
}

SKELETON = {
    "prototype_key": "SKELETON",
    "typeclass": "typeclasses.npcs.NPC",
    "key": "skeleton",
    "desc": (
        "A reanimated human skeleton, its bones yellowed and cracked. Empty "
        "eye sockets glow with a faint violet light. It moves with unsettling purpose."
    ),
    "attrs": [
        ("hp",          22),
        ("hp_max",      22),
        ("ac",          13),
        ("dr",          1),
        ("level",       2),
        ("str",         10),
        ("agi",         12),
        ("int",         5),
        ("wis",         6),
        ("hlt",         12),
        ("chm",         3),
        ("faction",        "hostile"),
        ("faction_type",   "undead"),
        ("ai_profile",     "tactical"),
        ("xp_value",       50),
        ("loot_table",     []),
        ("threat_table",   {}),
        ("art_key",        "skeleton"),
        ("prototype_key",  "SKELETON"),
        ("respawn_delay",  300),
    ],
}

BANDIT = {
    "prototype_key": "BANDIT",
    "typeclass": "typeclasses.npcs.NPC",
    "key": "bandit",
    "desc": (
        "A road-worn human with a scarred face and hard eyes. Leather armour "
        "and a short blade mark them as trouble. They size you up coolly."
    ),
    "attrs": [
        ("hp",          30),
        ("hp_max",      30),
        ("ac",          12),
        ("dr",          1),
        ("level",       2),
        ("str",         11),
        ("agi",         11),
        ("int",         10),
        ("wis",         10),
        ("hlt",         11),
        ("chm",         8),
        ("faction",        "hostile"),
        ("ai_profile",     "tactical"),
        ("xp_value",       75),
        ("loot_table",     []),
        ("threat_table",   {}),
        ("art_key",        "bandit"),
        ("prototype_key",  "BANDIT"),
        ("respawn_delay",  300),
    ],
}

ORC = {
    "prototype_key": "ORC",
    "typeclass": "typeclasses.npcs.NPC",
    "key": "orc",
    "desc": (
        "A hulking creature with grey-green skin, a jutting underbite, and small "
        "black eyes burning with aggression. It rolls its shoulders and charges."
    ),
    "attrs": [
        ("hp",          40),
        ("hp_max",      40),
        ("ac",          13),
        ("dr",          2),
        ("level",       3),
        ("str",         15),
        ("agi",         10),
        ("int",         7),
        ("wis",         9),
        ("hlt",         14),
        ("chm",         6),
        ("faction",        "hostile"),
        ("ai_profile",     "berserker"),
        ("xp_value",       100),
        ("loot_table",     []),
        ("threat_table",   {}),
        ("art_key",        "orc"),
        ("prototype_key",  "ORC"),
        ("respawn_delay",  600),
    ],
}

## ── New Silvermere Monsters ───────────────────────────────────────────────────

SEWER_RAT = {
    "prototype_key": "SEWER_RAT",
    "typeclass": "typeclasses.npcs.NPC",
    "key": "sewer rat",
    "desc": (
        "A rat bloated by years in the sewers, its grey fur slick with "
        "filth. Larger than a normal rat but not yet truly fearsome — "
        "a hazard for the careless, not a test for the experienced."
    ),
    "attrs": [
        ("hp",          20),
        ("hp_max",      20),
        ("ac",          12),
        ("dr",          0),
        ("level",       4),
        ("str",         8),
        ("agi",         13),
        ("int",         2),
        ("wis",         8),
        ("hlt",         9),
        ("chm",         3),
        ("faction",        "hostile"),
        ("ai_profile",     "cowardly"),
        ("xp_value",       45),
        ("loot_table",     []),
        ("threat_table",   {}),
        ("art_key",        "sewer_rat"),
        ("prototype_key",  "SEWER_RAT"),
        ("respawn_delay",  120),
    ],
}

WHITE_JELLY = {
    "prototype_key": "WHITE_JELLY",
    "typeclass": "typeclasses.npcs.NPC",
    "key": "white jelly",
    "desc": (
        "A translucent, amorphous mass that slides across the stone floor "
        "with a faint hiss. Contact with its surface burns like acid. "
        "It has no eyes, no mind — only hunger."
    ),
    "attrs": [
        ("hp",          35),
        ("hp_max",      35),
        ("ac",          10),
        ("dr",          1),
        ("level",       5),
        ("str",         10),
        ("agi",         7),
        ("int",         1),
        ("wis",         5),
        ("hlt",         13),
        ("chm",         1),
        ("faction",        "hostile"),
        ("ai_profile",     "cowardly"),
        ("xp_value",       75),
        ("loot_table",     []),
        ("threat_table",   {}),
        ("art_key",        "white_jelly"),
        ("prototype_key",  "WHITE_JELLY"),
        ("respawn_delay",  180),
    ],
}

CAVE_WORM = {
    "prototype_key": "CAVE_WORM",
    "typeclass": "typeclasses.npcs.NPC",
    "key": "cave worm",
    "desc": (
        "A segmented grey worm as thick as a man's torso, propelled by "
        "rows of bristled legs. Its mandibles can shear through chain "
        "mail. The wet rasping of its movement fills the chamber."
    ),
    "attrs": [
        ("hp",          60),
        ("hp_max",      60),
        ("ac",          13),
        ("dr",          2),
        ("level",       7),
        ("str",         15),
        ("agi",         8),
        ("int",         4),
        ("wis",         8),
        ("hlt",         16),
        ("chm",         2),
        ("faction",        "hostile"),
        ("ai_profile",     "tactical"),
        ("xp_value",       150),
        ("loot_table",     []),
        ("threat_table",   {}),
        ("art_key",        "cave_worm"),
        ("prototype_key",  "CAVE_WORM"),
        ("respawn_delay",  600),
    ],
}

## ── Example NPC prototypes (commented out) ───────────────────────────────────
## example of module-based prototypes using
## the variable name as `prototype_key` and
## simple Attributes

# from random import randint
#
# GOBLIN = {
# "key": "goblin grunt",
# "health": lambda: randint(20,30),
# "resists": ["cold", "poison"],
# "attacks": ["fists"],
# "weaknesses": ["fire", "light"],
# "tags": = [("greenskin", "monster"), ("humanoid", "monster")]
# }
#
# GOBLIN_WIZARD = {
# "prototype_parent": "GOBLIN",
# "key": "goblin wizard",
# "spells": ["fire ball", "lighting bolt"]
# }
#
# GOBLIN_ARCHER = {
# "prototype_parent": "GOBLIN",
# "key": "goblin archer",
# "attacks": ["short bow"]
# }
#
# This is an example of a prototype without a prototype
# (nor key) of its own, so it should normally only be
# used as a mix-in, as in the example of the goblin
# archwizard below.
# ARCHWIZARD_MIXIN = {
# "attacks": ["archwizard staff"],
# "spells": ["greater fire ball", "greater lighting"]
# }
#
# GOBLIN_ARCHWIZARD = {
# "key": "goblin archwizard",
# "prototype_parent" : ("GOBLIN_WIZARD", "ARCHWIZARD_MIXIN")
# }
