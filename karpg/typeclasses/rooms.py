"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """

    def return_appearance(self, looker, **kwargs):
        """Filter hidden characters from room contents for non-self lookers."""
        # Temporarily block view access for hidden non-looker characters
        hidden_chars = [
            obj for obj in self.contents
            if obj is not looker and getattr(obj.db, "is_hidden", False)
        ]
        for obj in hidden_chars:
            obj.locks.add("view:false()")
        try:
            result = super().return_appearance(looker, **kwargs)
        finally:
            for obj in hidden_chars:
                obj.locks.remove("view")
        return result
