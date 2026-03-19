"""
Travel commands for inter-area transit.

Currently contains:
  CmdGoSkiff  — board the skiff between Newhaven's Boatman's Dock
                and New Silvermere's Silvermere Pier.
"""

import evennia
from evennia import Command


_DOCK_KEY   = "Boatman's Dock"
_PIER_KEY   = "Silvermere Pier"

_DOCK_TO_PIER_MSG = (
    "The Boatman pushes off from the dock with a single, unhurried stroke. "
    "The dark river slides past as the skiff crosses. After a few quiet "
    "minutes you bump against the Silvermere Pier."
)
_PIER_TO_DOCK_MSG = (
    "The Pier Boatman casts off the mooring line and takes the oars. "
    "The lights of New Silvermere shrink behind you. The Newhaven dock "
    "resolves out of the morning haze and you step ashore."
)


def _find_room(key):
    """Return the first Room matching key, or None."""
    matches = evennia.search_object(key, typeclass="typeclasses.rooms.Room")
    return matches[0] if matches else None


class CmdGoSkiff(Command):
    """
    Board the skiff to travel between Newhaven and New Silvermere.

    Usage:
      go skiff
      skiff
      board skiff

    Must be at Boatman's Dock (Newhaven) or Silvermere Pier (New Silvermere).
    """

    key = "go skiff"
    aliases = ["skiff", "board skiff", "borrow skiff"]
    locks = "cmd:all()"
    help_category = "Travel"

    def func(self):
        caller = self.caller
        location = caller.location

        if location is None:
            caller.msg("You are nowhere.")
            return

        loc_key = location.key

        if loc_key == _DOCK_KEY:
            dest = _find_room(_PIER_KEY)
            msg = _DOCK_TO_PIER_MSG
            others_depart = f"{caller.name} steps into the skiff and is carried across the river."
            others_arrive = f"{caller.name} steps off the skiff onto the pier."
        elif loc_key == _PIER_KEY:
            dest = _find_room(_DOCK_KEY)
            msg = _PIER_TO_DOCK_MSG
            others_depart = f"{caller.name} boards the skiff and disappears across the water."
            others_arrive = f"{caller.name} arrives by skiff from the south."
        else:
            caller.msg("There is no skiff here to board.")
            return

        if dest is None:
            caller.msg("The skiff has nowhere to go right now.")
            return

        location.msg_contents(others_depart, exclude=caller)
        caller.move_to(dest, quiet=True)
        caller.msg(msg)
        dest.msg_contents(others_arrive, exclude=caller)
