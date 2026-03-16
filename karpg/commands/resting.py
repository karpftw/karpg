"""
Resting commands

CmdRest  — sit down and begin HP/mana regeneration
CmdStand — stand up, ending rest
"""

from commands.command import Command


class CmdRest(Command):
    """
    Rest to recover HP and mana.

    Usage:
      rest
      rest stop

    Resting slowly regenerates HP (after 20 seconds) and mana. You cannot
    rest while in combat. Moving or entering combat will interrupt your rest.
    """

    key = "rest"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        args = self.args.strip().lower()

        # rest stop
        if args == "stop":
            scripts = caller.scripts.get("resting")
            if scripts:
                caller.msg("|yYou stop resting and stand up.|n")
                scripts[0].stop()
            else:
                caller.msg("You are not resting.")
            return

        # Already resting
        if caller.db.is_resting:
            caller.msg("You are already resting.")
            return

        # Cannot rest in combat
        if caller.db.in_combat:
            caller.msg("|rYou cannot rest while in combat!|n")
            return

        caller.db.is_resting = True
        caller.location.msg_contents(
            f"{caller.key} sits down to rest.", exclude=[caller]
        )
        caller.msg("|cYou sit down to rest. HP will regenerate after 20 seconds.|n")
        caller.scripts.add("typeclasses.resting_script.RestingScript")


class CmdStand(Command):
    """
    Stand up from resting.

    Usage:
      stand
    """

    key = "stand"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        scripts = caller.scripts.get("resting")
        if scripts:
            caller.msg("|yYou stand up.|n")
            scripts[0].stop()
        else:
            caller.msg("You are already standing.")
