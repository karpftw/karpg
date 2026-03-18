"""
TRAIN command — advance to the next level at a trainer NPC.
"""

from evennia import Command
from world.xp_tables import xp_for_level, xp_to_next_level, cp_for_level
from world.stats import recalc_stats


class CmdTrain(Command):
    """
    Advance to the next level.

    Must be in the same room as a trainer NPC (tagged "trainer").
    Requires enough XP and must not be at the level cap.

    Usage:
      train
    """

    key = "train"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller

        # Level cap check
        current_level = caller.db.level or 1
        if current_level >= 75:
            caller.msg("You have reached the maximum level. There is nothing more to train.")
            return

        # Trainer presence check
        trainer = None
        for obj in caller.location.contents:
            if obj.tags.get("trainer", category="npc_role"):
                trainer = obj
                break

        if not trainer:
            caller.msg("You must be in the presence of a trainer to advance.")
            return

        # XP check
        char_class = caller.db.char_class or "warrior"
        race = caller.db.race or "human"
        current_xp = caller.db.xp or 0
        xp_needed = xp_for_level(current_level + 1, char_class, race)

        if current_xp < xp_needed:
            xp_remain = xp_needed - current_xp
            caller.msg(
                f"You do not have enough experience to advance. "
                f"You need {xp_remain:,} more XP."
            )
            return

        # ── Level up ──────────────────────────────────────────────────────────

        old_hp_max  = caller.db.hp_max  or 0
        old_mana    = caller.db.max_mana or 0
        old_kai     = caller.db.max_kai  or 0

        new_level = current_level + 1
        caller.db.level = new_level

        # Award CP and lives
        cp_gained = cp_for_level(new_level)
        caller.db.cp    = (caller.db.cp or 0) + cp_gained
        caller.db.lives = (caller.db.lives or 9) + 1

        # Recalculate HP/mana/kai maxima (recalc_stats uses db.level)
        recalc_stats(caller)

        new_hp_max = caller.db.hp_max  or 0
        new_mana   = caller.db.max_mana or 0
        new_kai    = caller.db.max_kai  or 0

        # Restore to full
        caller.db.hp   = new_hp_max
        caller.db.mana = new_mana
        caller.db.kai  = new_kai

        # ── Output ────────────────────────────────────────────────────────────

        msg_lines = [
            f"\n|Y*** You have advanced to level {new_level}! ***|n",
            f"  |wHP:|n    {old_hp_max} -> {new_hp_max}",
        ]

        if new_mana > 0 or old_mana > 0:
            msg_lines.append(f"  |wMana:|n  {old_mana} -> {new_mana}")
        if new_kai > 0 or old_kai > 0:
            msg_lines.append(f"  |wKai:|n   {old_kai} -> {new_kai}")

        msg_lines.append(
            f"  |wCP awarded:|n {cp_gained}  "
            f"(Total unspent: {caller.db.cp})"
        )
        msg_lines.append(f"  |wLives:|n {caller.db.lives}")
        msg_lines.append(
            f"\n{trainer.key} nods. \"Well earned, {caller.key}.\""
        )

        # Show XP progress for the new level
        xp_next = xp_to_next_level(new_level, char_class, race)
        if xp_next > 0:
            msg_lines.append(
                f"\n  XP to next level: {xp_next:,}"
            )

        caller.msg("\n".join(msg_lines))
        caller.msg(caller.get_prompt(), options={"send_prompt": True})
