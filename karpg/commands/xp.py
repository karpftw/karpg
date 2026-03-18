"""
XP table command — shows a windowed view of the XP progression table
anchored to the player's current level.

Box total visible width: 46 chars
Columns (content width including 1 leading + 1 trailing space):
  Lvl=6, XP Required=16, Bracket=11, CP=8  (inner total = 44, +2 outer ║ = 46)
Cell widths (col_width - 2 padding spaces): 4, 14, 9, 6
Footer inner = 44: "  " prefix + 42-char text
"""

from evennia import Command
from world.xp_tables import xp_for_level, xp_to_next_level, xp_in_bracket, cp_for_level

_TOP = "|x╔══════╦════════════════╦═══════════╦════════╗|n"
_HDR = "|x╠══════╬════════════════╬═══════════╬════════╣|n"
_SEP = "|x╠══════╩════════════════╩═══════════╩════════╣|n"
_BOT = "|x╚════════════════════════════════════════════╝|n"


class CmdXP(Command):
    """
    Display your XP progression table.

    Usage:
      xp

    Shows a 15-row window of XP requirements centered on your current
    level, including the XP bracket for each level and CP awarded.
    """

    key = "xp"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        level = caller.db.level or 1
        current_xp = caller.db.xp or 0
        char_class = caller.db.char_class or "warrior"
        race = caller.db.race or "human"

        window_start = max(1, level - 5)
        window_end = min(75, window_start + 14)

        title = f"XP Table \u2014 {race.capitalize()} {char_class.capitalize()}"

        lines = [_TOP]
        # Title: ║ + " " + title(43) + ║ = 46 visible
        lines.append(f"|x║|n |C{title:<43}|x║|n")
        lines.append(_HDR)
        # Headers: cell widths 4, 14, 9, 6 (padded to fill their columns)
        lines.append(
            f"|x║|n |C{'Lvl':<4}|n "
            f"|x║|n |C{'XP Required':>14}|n "
            f"|x║|n |C{'Bracket':>9}|n "
            f"|x║|n |C{'CP':>6}|n "
            f"|x║|n"
        )
        lines.append(_HDR)

        for lvl in range(window_start, window_end + 1):
            xp_req = xp_for_level(lvl, char_class, race)
            xp_str = f"{xp_req:>14,}"

            if lvl < 75:
                bracket = xp_to_next_level(lvl, char_class, race)
                br_str = f"{bracket:>9,}"
            else:
                br_str = f"{'—':>9}"

            cp_str = f"{cp_for_level(lvl):>6}"

            if lvl == level:
                lvl_str = f"\u25b6 {lvl:<2}"  # ▶ + space + level, 4 chars
                lines.append(
                    f"|x║|n |Y{lvl_str}|n "
                    f"|x║|n |Y{xp_str}|n "
                    f"|x║|n |Y{br_str}|n "
                    f"|x║|n |Y{cp_str}|n "
                    f"|x║|n"
                )
            else:
                lvl_str = f"  {lvl:<2}"  # 4 chars
                lines.append(
                    f"|x║|n {lvl_str} "
                    f"|x║|n {xp_str} "
                    f"|x║|n {br_str} "
                    f"|x║|n {cp_str} "
                    f"|x║|n"
                )

        lines.append(_SEP)

        # Footer: ║ + "  " + text(42) + ║ = 46 visible
        in_bracket = xp_in_bracket(current_xp, level, char_class, race)
        bracket_size = xp_to_next_level(level, char_class, race)
        if bracket_size > 0:
            pct = int(in_bracket * 100 / bracket_size)
            footer = f"Progress: {in_bracket:,} / {bracket_size:,} XP  ({pct}%)"
        else:
            footer = "Level cap reached"

        lines.append(f"|x║|n  {footer:<42}|x║|n")
        lines.append(_BOT)

        caller.msg("\n".join(lines))
