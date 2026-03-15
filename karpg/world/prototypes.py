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
        ("faction",     "hostile"),
        ("ai_profile",  "cowardly"),
        ("xp_value",    25),
        ("loot_table",  []),
        ("threat_table", {}),
        ("art_key",     "giant_rat"),
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
        ("faction",     "hostile"),
        ("ai_profile",  "cowardly"),
        ("xp_value",    50),
        ("loot_table",  []),
        ("threat_table", {}),
        ("art_key",     "goblin"),
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
        ("faction",     "hostile"),
        ("ai_profile",  "tactical"),
        ("xp_value",    50),
        ("loot_table",  []),
        ("threat_table", {}),
        ("art_key",     "skeleton"),
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
        ("faction",     "hostile"),
        ("ai_profile",  "tactical"),
        ("xp_value",    75),
        ("loot_table",  []),
        ("threat_table", {}),
        ("art_key",     "bandit"),
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
        ("faction",     "hostile"),
        ("ai_profile",  "berserker"),
        ("xp_value",    100),
        ("loot_table",  []),
        ("threat_table", {}),
        ("art_key",     "orc"),
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
