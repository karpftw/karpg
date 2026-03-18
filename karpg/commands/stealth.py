"""
Stealth Commands

CmdHide — enter stealth (Thief, Elf, Halfling only)
"""

from evennia import Command
from world.stealth import can_hide, hide_check


class CmdHide(Command):
    """
    Attempt to hide in the shadows.

    Usage:
        hide

    Only Thieves, Elves, and Halflings can hide. Success depends on your
    Agility. While hidden you cannot be targeted by NPCs and backstab becomes
    available. Most actions (attacking, casting, moving noisily) will break
    your stealth.
    """

    key = "hide"
    help_category = "General"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller

        if not can_hide(caller):
            caller.msg("|rOnly Thieves, Elves, and Halflings can hide.|n")
            return

        if caller.db.is_hidden:
            caller.msg("|xYou are already concealed.|n")
            return

        if caller.db.in_combat:
            caller.msg("|rYou can't hide while fighting!|n")
            return

        if hide_check(caller):
            caller.db.is_hidden = True
            caller.msg("|xYou slip into the shadows.|n")
        else:
            caller.msg("|rYou fail to find cover.|n")

        caller.msg(caller.get_prompt(), options={"send_prompt": True})
