"""
Map command — BFS ASCII map of nearby rooms.
"""

from collections import deque

from evennia import Command

DIRS = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}

# Colored symbol for each room type
SYMBOLS = {
    "center":     "|Y@|n",
    "road":       "|x.|n",
    "shop":       "|y$|n",
    "healer":     "|GH|n",
    "trainer":    "|WT|n",
    "dock":       "|C~|n",
    "dungeon":    "|R!|n",
    "wilderness": "|g*|n",
}

# Legend: (raw char, type label, color code for display)
LEGEND_ENTRIES = [
    ("@", "center",     "|Y"),
    (".", "road",       "|x"),
    ("$", "shop",       "|y"),
    ("H", "healer",     "|G"),
    ("T", "trainer",    "|W"),
    ("~", "dock",       "|C"),
    ("!", "dungeon",    "|R"),
    ("*", "wilderness", "|g"),
]


def _build_grid(start, max_depth=3):
    grid = {(0, 0): start}
    pos = {start: (0, 0)}
    queue = deque([(start, 0)])
    while queue:
        room, depth = queue.popleft()
        if depth >= max_depth:
            continue
        x, y = pos[room]
        for ex in room.exits:
            if ex.key not in DIRS:
                continue
            dx, dy = DIRS[ex.key]
            nx, ny = x + dx, y + dy
            dest = ex.destination
            if dest not in pos and (nx, ny) not in grid:
                grid[(nx, ny)] = dest
                pos[dest] = (nx, ny)
                queue.append((dest, depth + 1))
    return grid, pos


def _get_symbol(room, is_current):
    sym = SYMBOLS.get(room.db.room_type, "|x?|n")
    if is_current:
        return f"|M[|n{sym}|M]|n"
    return f"|x[|n{sym}|x]|n"


def _has_exit(room, direction):
    return any(ex.key == direction for ex in room.exits)


def _render_map(grid, current, pos):
    if not grid:
        return "No map available."

    xs = [x for x, y in grid]
    ys = [y for x, y in grid]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    lines = []
    for y in range(min_y, max_y + 1):
        # Room row: [X]---[X]---[X]
        room_row = ""
        for x in range(min_x, max_x + 1):
            room = grid.get((x, y))
            if room:
                room_row += _get_symbol(room, room is current)
            else:
                room_row += "   "  # 3 display chars for empty cell
            # East connector (3 display chars)
            if x < max_x:
                room_here = grid.get((x, y))
                if room_here and _has_exit(room_here, "east") and grid.get((x + 1, y)):
                    room_row += "|x---|n"
                else:
                    room_row += "   "
        lines.append(room_row)

        # Vertical connector row — skip after last row
        if y < max_y:
            # Display width: each column is 6 chars wide ([X]---), last is 3 ([X])
            col_count = max_x - min_x + 1
            row_width = col_count * 6 - 3 if col_count > 1 else 3
            # Track which display positions get a south connector
            pipe_positions = set()
            for xi, x in enumerate(range(min_x, max_x + 1)):
                room_here = grid.get((x, y))
                room_below = grid.get((x, y + 1))
                if room_here and room_below and _has_exit(room_here, "south"):
                    col_pos = xi * 6 + 1
                    if col_pos < row_width:
                        pipe_positions.add(col_pos)
            # Build connector string, inserting || (Evennia escape for literal |)
            connector = []
            for i in range(row_width):
                connector.append("||" if i in pipe_positions else " ")
            lines.append("".join(connector))

    # Legend — two entries per line
    legend_lines = []
    row_entries = []
    for ch, label, color in LEGEND_ENTRIES:
        row_entries.append(f"{color}[{ch}]|n {label}")
        if len(row_entries) == 4:
            legend_lines.append("  ".join(row_entries))
            row_entries = []
    if row_entries:
        legend_lines.append("  ".join(row_entries))

    lines.append("")
    lines.extend(legend_lines)
    lines.append(f"|M[|n you |M]|n = current location  |wYou are at:|n {current.key}")

    return "\n".join(lines)


class CmdMap(Command):
    """
    Display an ASCII map of nearby rooms.

    Usage:
      map

    Shows a 2D map of rooms reachable within 3 exits from your
    current location, following cardinal directions only.
    Your current room is highlighted with bright white brackets.
    """

    key = "map"
    aliases = ["m"]
    help_category = "General"

    def func(self):
        room = self.caller.location
        if not room:
            self.caller.msg("You are nowhere.")
            return
        grid, pos = _build_grid(room, max_depth=3)
        output = _render_map(grid, room, pos)
        self.caller.msg(output)
