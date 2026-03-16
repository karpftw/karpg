"""
Chargen Commands

Admin (Builder-permission) commands for setting class and race on characters.
Used for testing; full player character-creation is deferred.

Commands:
    setclass [list | <class> | <target>=<class>]
    setrace  [list | <race>  | <target>=<race>]
"""

from evennia import Command

from world.classes import get_class, list_classes
from world.races import get_race, list_races
from world.stats import recalc_stats


class CmdSetClass(Command):
    """
    Set a character's class.

    Usage:
        setclass list
        setclass <class>
        setclass <target>=<class>

    Requires Builder permission. Clears known_spells and recalculates stats.
    HP/mana/kai are restored to full after a class change.
    """

    key = "setclass"
    locks = "cmd:perm(Builder)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if not args or args.lower() == "list":
            self._show_list()
            return

        # Parse optional "target=class" syntax
        if "=" in args:
            target_name, _, class_name = args.partition("=")
            target_name = target_name.strip()
            class_name = class_name.strip().lower()
            target = caller.search(target_name)
            if not target:
                return
        else:
            target = caller
            class_name = args.lower()

        cls = get_class(class_name)
        if not cls:
            valid = ", ".join(name for name, _ in list_classes())
            caller.msg(f"|rUnknown class '{class_name}'. Valid: {valid}|n")
            return

        old_class = getattr(target.db, "char_class", None)
        target.db.char_class = class_name
        target.db.known_spells = []

        recalc_stats(target)
        # Restore to full after class change
        target.db.hp   = target.db.hp_max
        target.db.mana = target.db.max_mana
        target.db.kai  = target.db.max_kai

        school = cls["magic_school"] or "none"
        hp_range = f"{cls['hp_per_level_min']}-{cls['hp_per_level_max']}"
        caller.msg(
            f"|gSet {target.key}'s class to |w{class_name}|g "
            f"(HP/lvl: {hp_range}, school: {school}).|n"
        )
        if target != caller:
            target.msg(f"|gYour class has been set to |w{class_name}|g by {caller.key}.|n")

    def _show_list(self):
        lines = ["", "|y Classes |n", "|x" + "-" * 52 + "|n"]
        lines.append(f"  {'Name':<12} {'HP/lvl':<8} {'School':<10} {'Combat'}")
        lines.append("|x" + "-" * 52 + "|n")
        for name, cls in list_classes():
            hp_range = f"{cls['hp_per_level_min']}-{cls['hp_per_level_max']}"
            school = cls["magic_school"] or "none"
            rating = cls["combat_rating"]
            lines.append(f"  |w{name:<12}|n {hp_range:<8} {school:<10} {rating}")
        lines.append("")
        self.caller.msg("\n".join(lines))


class CmdSetRace(Command):
    """
    Set a character's race.

    Usage:
        setrace list
        setrace <race>
        setrace <target>=<race>

    Requires Builder permission. Applies racial stat modifiers.
    HP/mana/kai are clamped to new maximums (not restored to full).
    """

    key = "setrace"
    locks = "cmd:perm(Builder)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if not args or args.lower() == "list":
            self._show_list()
            return

        # Parse optional "target=race" syntax
        if "=" in args:
            target_name, _, race_name = args.partition("=")
            target_name = target_name.strip()
            race_name = race_name.strip().lower().replace(" ", "_")
            target = caller.search(target_name)
            if not target:
                return
        else:
            target = caller
            race_name = args.lower().replace(" ", "_")

        race = get_race(race_name)
        if not race:
            valid = ", ".join(name for name, _ in list_races())
            caller.msg(f"|rUnknown race '{race_name}'. Valid: {valid}|n")
            return

        target.db.race = race_name
        recalc_stats(target)
        # Do NOT restore to full — clamp only (recalc_stats already does this)

        mods = race["stat_mods"]
        mod_str = "  ".join(
            f"{s.upper()}{'+' if v >= 0 else ''}{v}"
            for s, v in mods.items()
            if v != 0
        ) or "none"
        caller.msg(f"|gSet {target.key}'s race to |w{race_name}|g (mods: {mod_str}).|n")
        if target != caller:
            target.msg(f"|gYour race has been set to |w{race_name}|g by {caller.key}.|n")

    def _show_list(self):
        lines = ["", "|y Races |n", "|x" + "-" * 60 + "|n"]
        lines.append(f"  {'Name':<12} {'Stat modifiers':<30} {'Abilities'}")
        lines.append("|x" + "-" * 60 + "|n")
        for name, race in list_races():
            mods = race["stat_mods"]
            mod_str = " ".join(
                f"{s.upper()}{'+' if v >= 0 else ''}{v}"
                for s, v in mods.items()
                if v != 0
            ) or "balanced"
            abilities = ", ".join(race["abilities"]) or "none"
            lines.append(f"  |w{name:<12}|n {mod_str:<30} {abilities}")
        lines.append("")
        self.caller.msg("\n".join(lines))
