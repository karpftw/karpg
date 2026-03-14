"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    def at_object_creation(self):
        super().at_object_creation()
        # Equipment slots. Two-handed weapons set both slots to the same object.
        self.db.wielded = {
            "main_hand": None,
            "off_hand": None,
        }

        # Combat stats (5e-style)
        self.db.hp              = 10
        self.db.hp_max          = 10
        self.db.ac              = 10
        self.db.level           = 1
        self.db.proficiency_bonus = 2
        self.db.ability_scores  = {
            "str": 10, "dex": 10, "con": 10,
            "int": 10, "wis": 10, "cha": 10,
        }
        self.db.conditions      = []
        self.db.damage_resistances    = []
        self.db.damage_vulnerabilities = []
        self.db.damage_immunities     = []
        self.db.spell_slots     = {}
        self.db.known_spells    = []
        self.db.death_saves     = {"successes": 0, "failures": 0}
        self.db.in_combat       = None
        self.db.faction         = "player"
        self.db.xp              = 0
