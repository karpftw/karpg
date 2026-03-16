"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.
"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent
from world.combat_engine import hp_colour


class Character(ObjectParent, DefaultCharacter):
    """
    The Character re-implements some Object hooks to represent a player-
    controlled entity in-game.

    MajorMUD stats:
        str  — melee damage + accuracy
        agi  — accuracy, defense, attacks per round
        int  — mana pool, spell power
        wis  — mana regeneration
        hlt  — max HP
        chm  — merchant prices, social effects

    Combat attributes:
        hp, hp_max       — current and max hit points
        mana, max_mana   — current and max mana
        ac               — armor class (base defense)
        dr               — damage resistance (flat damage reduction)
        level
        formation_rank   — "front" | "mid" | "back"
        in_combat        — reference to active CombatScript, or None
        known_spells     — list of spell key strings
        xp               — total experience points
        faction          — "player"
    """

    def at_object_creation(self):
        super().at_object_creation()

        # Equipment slots
        self.db.wielded = {
            "main_hand": None,
            "off_hand": None,
        }

        # MajorMUD stats
        self.db.str = 10
        self.db.agi = 10
        self.db.int = 10
        self.db.wis = 10
        self.db.hlt = 10
        self.db.chm = 10

        # Combat stats
        self.db.hp      = 40   # 10 + HLT*2(10*2=20) + level*5(1*5=5) → 35 base, round to 40
        self.db.hp_max  = 40
        self.db.mana    = 32   # INT*3(10*3=30) + level*2(1*2=2) → 32
        self.db.max_mana = 32
        self.db.ac      = 10
        self.db.dr      = 0
        self.db.level   = 1

        # Formation
        self.db.formation_rank = "mid"

        # Status
        self.db.conditions = []
        self.db.in_combat  = None
        self.db.faction    = "player"

        # Spells and progression
        self.db.known_spells = []
        self.db.xp           = 0

    def get_prompt(self):
        """Return a MajorMUD-style status line string."""
        hp     = self.db.hp or 0
        hp_max = self.db.hp_max or 1
        mana     = self.db.mana or 0
        max_mana = self.db.max_mana or 1
        level = self.db.level or 1
        xp    = self.db.xp or 0

        col = hp_colour(hp, hp_max)
        return (
            f"[|wHP|n: {col}{hp}/{hp_max}|n] "
            f"[|cMana|n: |C{mana}/{max_mana}|n] "
            f"[|wLv {level}|n | |yXP: {xp}|n]>"
        )
