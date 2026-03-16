"""
Resting Script

Attached to a resting Character. Ticks every 4 seconds.
- Mana regens at the same rate as combat (MajorMUD authentic).
- HP regen activates after 5 ticks (20 seconds).
- Auto-stops when fully recovered or when combat starts.
"""

from evennia import DefaultScript
from world.stats import get_mana_regen, get_hp_regen


class RestingScript(DefaultScript):
    """Attached to the resting Character. Ticks every 4 seconds."""

    def at_script_creation(self):
        self.key = "resting"
        self.interval = 4
        self.persistent = False
        self.repeats = 0
        self.db.ticks = 0  # HP regen starts at tick 5 (20s)

    def at_repeat(self):
        char = self.obj

        # Abort if they entered combat
        if char.db.in_combat:
            self._stop_rest(char, "")
            return

        self.db.ticks = (self.db.ticks or 0) + 1
        hp       = char.db.hp or 0
        hp_max   = char.db.hp_max or 1
        mana     = char.db.mana or 0
        max_mana = char.db.max_mana or 1

        # Mana regen — same rate as combat (MajorMUD authentic)
        mana_gain = get_mana_regen(char)
        char.db.mana = min(max_mana, mana + mana_gain)

        # HP regen — only after 5 ticks (20 seconds), MajorMUD authentic
        hp_gain = 0
        if self.db.ticks >= 5:
            hp_gain = get_hp_regen(char)
            char.db.hp = min(hp_max, hp + hp_gain)

        # Push updated status line — \r overwrites the previous line in-place
        if hasattr(char, "get_prompt"):
            char.msg("\r" + char.get_prompt(), options={"send_prompt": True})

        # Auto-stop when fully recovered
        if char.db.hp >= hp_max and char.db.mana >= max_mana:
            char.msg("|gYou feel fully restored. You stand up.|n")
            self._stop_rest(char, None)

    def at_stop(self):
        char = self.obj
        char.db.is_resting = False

    def _stop_rest(self, char, msg):
        if msg:
            char.msg(msg)
        self.stop()
