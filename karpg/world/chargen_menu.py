"""
Character Creation Menu (chargen)

EvMenu flow:
    node_welcome
        → node_race → node_race_confirm
        → node_class → node_class_confirm
        → node_lore_blurb   (race+class lore + passive bonus preview)
        → node_stats
        → node_appearance_hair_length → node_appearance_hair_color → node_appearance_eye_color
        → node_confirm
        → node_chargen_complete (closes menu; look triggered by cmd_on_exit)
"""

import evennia

from world.classes import get_class, list_classes
from world.races import get_race, list_races
from world.stats import recalc_stats
from world.lore import get_combo_description

STARTING_CP = 30
STAT_CAP_ABOVE_BASE = 10   # max points a player can add above racial base during chargen

_HAIR_LENGTHS = ["short", "medium", "long", "braided", "shaved"]
_HAIR_COLORS  = ["black", "brown", "blonde", "red", "grey", "white", "silver"]
_EYE_COLORS   = ["brown", "blue", "green", "grey", "hazel", "amber", "violet"]


# ─── Entry point ──────────────────────────────────────────────────────────────

def start_chargen(character):
    """Launch the chargen EvMenu for a newly created character."""
    from evennia.utils.evmenu import EvMenu
    EvMenu(
        character,
        "world.chargen_menu",
        startnode="node_welcome",
        persistent=True,
        cmd_on_exit="look",
    )


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _cp_cost_to_raise(current, base):
    """CP cost to raise a stat from current to current+1."""
    points_above = current - base
    if points_above < 10:
        return 1
    return 2


def _cp_refund_to_lower(current, base):
    """CP refunded when lowering a stat from current to current-1.  Returns 0 if at base."""
    points_above = current - base
    if points_above <= 0:
        return 0
    if points_above <= 10:
        return 1
    return 2


def _init_chargen_stats(caller):
    """
    Ensure caller.ndb.chargen_stats is populated from the pending race.
    No-op if already set.
    """
    if caller.ndb.chargen_stats is not None:
        return
    race_name = getattr(caller.ndb, "chargen_pending_race", None) or caller.db.race or "human"
    race = get_race(race_name)
    base_stats = {}
    for stat in ("str", "agi", "int", "wis", "hlt", "chm"):
        mod = race["stat_mods"].get(stat, 0) if race else 0
        base_stats[stat] = 10 + mod
    caller.ndb.chargen_stats = {
        "cp_remaining": STARTING_CP,
        "stats": dict(base_stats),
        "base": dict(base_stats),
    }


def _fmt_mod(v):
    """Return a 4-visible-char stat modifier string with color codes.
    Padding is applied *before* wrapping in color so f-string width
    specifiers are not needed (and don't mis-count invisible color bytes).
    """
    if v > 0:
        return f"|g{f'+{v}':>4}|n"
    if v < 0:
        return f"|r{str(v):>4}|n"
    return "  --"  # 4 visible chars, no color


def _stats_display(caller):
    """Render the CP-allocation stat table."""
    data = caller.ndb.chargen_stats
    cp   = data["cp_remaining"]
    stats = data["stats"]
    base  = data["base"]

    lines = [f"\n|yAllocate your Character Points|n (CP remaining: |w{cp}|n)\n"]
    pairs = [
        (("str", "STR"), ("wis", "WIS")),
        (("agi", "AGI"), ("hlt", "HLT")),
        (("int", "INT"), ("chm", "CHM")),
    ]
    for (lk, ln), (rk, rn) in pairs:
        lv = stats[lk]; rv = stats[rk]
        ld = lv - base[lk]; rd = rv - base[rk]
        ls = f"+{ld}" if ld > 0 else str(ld)
        rs = f"+{rd}" if rd > 0 else str(rd)
        lines.append(f"  {ln}  |w{lv:2d}|n  ({ls:>3})    {rn}  |w{rv:2d}|n  ({rs:>3})")

    lines.append("\n|xCommands:|n  |w+str|n  |w-str|n  |w+agi|n  |w-agi|n  …  |wdone|n to continue")
    lines.append("|xCost: pts 1-10 above racial base = 1 CP each; pts 11+ = 2 CP each|n")
    return "\n".join(lines)


# ─── Node: Welcome ────────────────────────────────────────────────────────────

def node_welcome(caller, raw_string, **kwargs):
    text = (
        f"\n|y{'=' * 50}|n\n"
        f"  Welcome to Newhaven\n"
        f"|y{'=' * 50}|n\n\n"
        f"Before you enter this world, you must define who you are.\n\n"
        f"Your name is: |w{caller.key}|n\n\n"
        f"This process will guide you through choosing your race,\n"
        f"class, stats, and appearance.\n\n"
        f"|xChoose carefully — race and class cannot be changed after creation.|n"
    )
    options = ({"desc": "Continue", "goto": "node_race"},)
    return text, options


# ─── Node: Race ───────────────────────────────────────────────────────────────

def node_race(caller, raw_string, **kwargs):
    lines = ["\n|yChoose your race.|n\n"]
    lines.append(f"  {'#':<3} {'Race':<12} {'STR':>4} {'AGI':>4} {'INT':>4} {'WIS':>4} {'HLT':>4} {'CHM':>4}  Abilities")
    lines.append("|x" + "-" * 72 + "|n")

    options = []
    for i, (name, race) in enumerate(list_races(), 1):
        mods = race["stat_mods"]
        abilities = ", ".join(race["abilities"]) if race["abilities"] else "—"
        lines.append(
            f"  {i:<3} {name.replace('_',' ').capitalize():<12}"
            f" {_fmt_mod(mods['str'])} {_fmt_mod(mods['agi'])}"
            f" {_fmt_mod(mods['int'])} {_fmt_mod(mods['wis'])}"
            f" {_fmt_mod(mods['hlt'])} {_fmt_mod(mods['chm'])}  {abilities}"
        )
        options.append({
            "key": (str(i), name, name.replace("_", " ")),
            "desc": name.replace("_", " ").capitalize(),
            "goto": (_goto_race_confirm, {"race_name": name}),
        })

    lines.append("\nType a race name or number to select.")
    return "\n".join(lines), tuple(options)


def _goto_race_confirm(caller, raw_string, race_name=None, **kwargs):
    caller.ndb.chargen_pending_race = race_name
    return "node_race_confirm"


def node_race_confirm(caller, raw_string, **kwargs):
    race_name = caller.ndb.chargen_pending_race
    if not race_name:
        return "node_race", {}

    race = get_race(race_name)
    mods = race["stat_mods"]
    abilities = ", ".join(race["abilities"]) if race["abilities"] else "none"
    mr_bonus  = race.get("magic_resistance_bonus", 0)
    two_hand  = "Yes" if race["two_handed_allowed"] else "No"
    mod_str   = "  ".join(
        f"{s.upper()} {'+' if v >= 0 else ''}{v}" for s, v in mods.items() if v != 0
    ) or "none"

    text = (
        f"\n|y{race_name.replace('_', ' ').capitalize()}|n\n\n"
        f"  Stat modifiers: {mod_str}\n"
        f"  Abilities:      {abilities}\n"
        f"  Magic resist:   +{mr_bonus}\n"
        f"  Two-handed:     {two_hand}\n"
    )
    options = (
        {"key": ("1", "yes", "y", "confirm"), "desc": "Confirm — choose this race", "goto": _apply_race},
        {"key": ("2", "no",  "n", "back"),    "desc": "Go back",                    "goto": "node_race"},
    )
    return text, options


def _apply_race(caller, raw_string, **kwargs):
    """Apply the selected race and initialise the CP allocation state."""
    race_name = caller.ndb.chargen_pending_race
    caller.db.race = race_name

    race = get_race(race_name)
    base_stats = {}
    for stat in ("str", "agi", "int", "wis", "hlt", "chm"):
        mod = race["stat_mods"].get(stat, 0) if race else 0
        base_stats[stat] = 10 + mod

    caller.ndb.chargen_stats = {
        "cp_remaining": STARTING_CP,
        "stats": dict(base_stats),
        "base": dict(base_stats),
    }
    return "node_class"


# ─── Node: Class ──────────────────────────────────────────────────────────────

def node_class(caller, raw_string, **kwargs):
    lines = ["\n|yChoose your class.|n\n"]
    lines.append(f"  {'#':<3} {'Class':<10} {'HP/Lv':<8} {'Magic':<16} Weapons")
    lines.append("|x" + "-" * 65 + "|n")

    options = []
    for i, (name, cls) in enumerate(list_classes(), 1):
        hp_range = f"{cls['hp_per_level_min']}-{cls['hp_per_level_max']}"
        school = cls["magic_school"] or "none"
        ml = cls["magic_level"]
        magic = f"{school} ({ml})" if ml > 0 else "none"
        weapons = cls["weapon_types"]
        if weapons is None:
            wpn_str = "Any"
        else:
            wpn_str = ", ".join(w if w else "Unarmed" for w in weapons)
        lines.append(f"  {i:<3} {name.capitalize():<10} {hp_range:<8} {magic:<16} {wpn_str}")
        options.append({
            "key": (str(i), name),
            "desc": name.capitalize(),
            "goto": (_goto_class_confirm, {"class_name": name}),
        })

    lines.append("\nType a class name or number to select.")
    return "\n".join(lines), tuple(options)


def _goto_class_confirm(caller, raw_string, class_name=None, **kwargs):
    caller.ndb.chargen_pending_class = class_name
    return "node_class_confirm"


def node_class_confirm(caller, raw_string, **kwargs):
    class_name = caller.ndb.chargen_pending_class
    if not class_name:
        return "node_class", {}

    cls = get_class(class_name)
    hp_range  = f"{cls['hp_per_level_min']}-{cls['hp_per_level_max']}"
    school    = cls["magic_school"] or "none"
    ml        = cls["magic_level"]
    magic     = f"{school} (level {ml})" if ml > 0 else "none"
    weapons   = cls["weapon_types"]
    wpn_str   = "Any" if weapons is None else ", ".join(w if w else "Unarmed" for w in weapons)
    armor     = cls["armor_types"]
    armor_str = "Any" if armor is None else ", ".join(armor)
    abilities = ", ".join(cls["abilities"]) if cls["abilities"] else "none"
    two_hand  = "Yes" if cls["two_handed_allowed"] else "No"

    text = (
        f"\n|y{class_name.capitalize()}|n\n\n"
        f"  HP per level:  {hp_range}\n"
        f"  Magic school:  {magic}\n"
        f"  Weapons:       {wpn_str}\n"
        f"  Armor:         {armor_str}\n"
        f"  Abilities:     {abilities}\n"
        f"  Two-handed:    {two_hand}\n"
    )
    options = (
        {"key": ("1", "yes", "y", "confirm"), "desc": "Confirm — choose this class", "goto": _apply_class_and_show_lore},
        {"key": ("2", "no",  "n", "back"),    "desc": "Go back",                     "goto": "node_class"},
    )
    return text, options


def _apply_class_and_show_lore(caller, raw_string, **kwargs):
    """Store the chosen class and proceed to the lore blurb."""
    caller.db.char_class = caller.ndb.chargen_pending_class
    return "node_lore_blurb"


# ─── Node: Lore Blurb ─────────────────────────────────────────────────────────

def node_lore_blurb(caller, raw_string, **kwargs):
    race_name  = getattr(caller.ndb, "chargen_pending_race",  None) or caller.db.race       or "human"
    class_name = getattr(caller.ndb, "chargen_pending_class", None) or caller.db.char_class or "warrior"

    # Passive bonus label
    race = get_race(race_name)
    bonus = race.get("passive_bonus", {}) if race else {}
    bonus_label = bonus.get("label", "")
    bonus_desc  = bonus.get("description", "")

    blurb = get_combo_description(race_name, class_name)
    display_race  = race_name.replace("_", " ").capitalize()
    display_class = class_name.capitalize()

    passive_line = (
        f"\n  |yPassive Bonus:|n |w{bonus_label}|n — {bonus_desc}"
        if bonus_label else ""
    )

    text = (
        f"\n|y{'=' * 50}|n\n"
        f"  {display_race} {display_class}\n"
        f"|y{'=' * 50}|n\n\n"
        f"{blurb}{passive_line}\n"
    )
    options = ({"desc": "Continue to stat allocation", "goto": "node_stats"},)
    return text, options


# ─── Node: Stats ──────────────────────────────────────────────────────────────

def node_stats(caller, raw_string, **kwargs):
    _init_chargen_stats(caller)
    text    = _stats_display(caller)
    options = ({"key": "_default", "goto": _stats_input_handler},)
    return text, options


def _stats_input_handler(caller, raw_string, **kwargs):
    """Process a +stat / -stat command or 'done' and stay on node_stats."""
    cmd = (raw_string or "").strip().lower()

    if cmd in ("done", "next", ""):
        return "node_appearance_hair_length"

    data = caller.ndb.chargen_stats
    if not data:
        return "node_stats"

    if len(cmd) >= 2 and cmd[0] in ("+", "-") and cmd[1:] in ("str", "agi", "int", "wis", "hlt", "chm"):
        direction = cmd[0]
        stat      = cmd[1:]
        current   = data["stats"][stat]
        base      = data["base"][stat]

        if direction == "+":
            cap = base + STAT_CAP_ABOVE_BASE
            if current >= cap:
                caller.msg(f"|rCannot raise {stat.upper()} above {cap} (cap: racial base +{STAT_CAP_ABOVE_BASE}).|n")
            else:
                cost = _cp_cost_to_raise(current, base)
                if data["cp_remaining"] < cost:
                    caller.msg(f"|rNot enough CP (need {cost}, have {data['cp_remaining']}).|n")
                else:
                    data["stats"][stat] += 1
                    data["cp_remaining"] -= cost
        else:
            refund = _cp_refund_to_lower(current, base)
            if refund == 0:
                caller.msg(f"|rCannot lower {stat.upper()} below racial base ({base}).|n")
            else:
                data["stats"][stat] -= 1
                data["cp_remaining"] += refund
    else:
        caller.msg("|xUnknown command. Use |w+str|x, |w-str|x, |w+agi|x, etc., or |wdone|x to continue.|n")

    return "node_stats"


# ─── Nodes: Appearance ────────────────────────────────────────────────────────

def node_appearance_hair_length(caller, raw_string, **kwargs):
    text    = "\n|yChoose your hair length.|n\n"
    options = tuple(
        {"key": (str(i), val), "desc": val.capitalize(),
         "goto": (_set_appearance, {"attr": "chargen_hair_length", "value": val, "next_node": "node_appearance_hair_color"})}
        for i, val in enumerate(_HAIR_LENGTHS, 1)
    )
    return text, options


def node_appearance_hair_color(caller, raw_string, **kwargs):
    text    = "\n|yChoose your hair color.|n\n"
    options = tuple(
        {"key": (str(i), val), "desc": val.capitalize(),
         "goto": (_set_appearance, {"attr": "chargen_hair_color", "value": val, "next_node": "node_appearance_eye_color"})}
        for i, val in enumerate(_HAIR_COLORS, 1)
    )
    return text, options


def node_appearance_eye_color(caller, raw_string, **kwargs):
    text    = "\n|yChoose your eye color.|n\n"
    options = tuple(
        {"key": (str(i), val), "desc": val.capitalize(),
         "goto": (_set_appearance, {"attr": "chargen_eye_color", "value": val, "next_node": "node_confirm"})}
        for i, val in enumerate(_EYE_COLORS, 1)
    )
    return text, options


def _set_appearance(caller, raw_string, attr=None, value=None, next_node=None, **kwargs):
    setattr(caller.ndb, attr, value)
    return next_node


# ─── Node: Confirm ────────────────────────────────────────────────────────────

def node_confirm(caller, raw_string, **kwargs):
    data         = caller.ndb.chargen_stats or {}
    stats        = data.get("stats", {})
    cp_remaining = data.get("cp_remaining", 0)

    race_name  = getattr(caller.ndb, "chargen_pending_race",  None) or caller.db.race       or "human"
    class_name = getattr(caller.ndb, "chargen_pending_class", None) or caller.db.char_class or "warrior"
    hair_len   = getattr(caller.ndb, "chargen_hair_length", "medium")
    hair_col   = getattr(caller.ndb, "chargen_hair_color",  "brown")
    eye_col    = getattr(caller.ndb, "chargen_eye_color",   "brown")

    text = (
        f"\n|y{'=' * 40}|n\n"
        f"  Character Summary\n"
        f"|y{'=' * 40}|n\n\n"
        f"  Name:   |w{caller.key}|n\n"
        f"  Race:   |w{race_name.replace('_', ' ').capitalize()}|n\n"
        f"  Class:  |w{class_name.capitalize()}|n\n\n"
        f"  |yStats|n\n"
        f"  STR {stats.get('str', 10):2d}   WIS {stats.get('wis', 10):2d}\n"
        f"  AGI {stats.get('agi', 10):2d}   HLT {stats.get('hlt', 10):2d}\n"
        f"  INT {stats.get('int', 10):2d}   CHM {stats.get('chm', 10):2d}\n"
        f"  CP remaining: {cp_remaining}\n\n"
        f"  |yAppearance|n\n"
        f"  Hair: {hair_len} {hair_col}\n"
        f"  Eyes: {eye_col}\n\n"
        f"  |yStarting gold:|n 50 GP\n"
    )
    options = (
        {"key": ("1", "yes", "y", "confirm"), "desc": "Confirm and enter Newhaven", "goto": "node_chargen_complete"},
        {"key": ("2", "no",  "n", "restart"), "desc": "Start over",                "goto": _restart_chargen},
    )
    return text, options


def _restart_chargen(caller, raw_string, **kwargs):
    """Clear all chargen ndb state and return to the welcome node."""
    caller.ndb.chargen_stats          = None
    caller.ndb.chargen_pending_race   = None
    caller.ndb.chargen_pending_class  = None
    caller.ndb.chargen_hair_length    = None
    caller.ndb.chargen_hair_color     = None
    caller.ndb.chargen_eye_color      = None
    return "node_welcome"


# ─── Node: Chargen Complete ───────────────────────────────────────────────────

def node_chargen_complete(caller, raw_string, **kwargs):
    """
    Terminal node: apply all choices, move to Newhaven, close the menu.
    Returning (None, None) signals EvMenu to close.
    """
    data         = caller.ndb.chargen_stats or {}
    stats        = data.get("stats", {})
    cp_remaining = data.get("cp_remaining", 0)

    race_name  = getattr(caller.ndb, "chargen_pending_race",  None) or "human"
    class_name = getattr(caller.ndb, "chargen_pending_class", None) or "warrior"
    hair_len   = getattr(caller.ndb, "chargen_hair_length", "medium")
    hair_col   = getattr(caller.ndb, "chargen_hair_color",  "brown")
    eye_col    = getattr(caller.ndb, "chargen_eye_color",   "brown")

    # 1. Compute pure base stats (remove racial mods — recalc_stats will re-add them)
    race = get_race(race_name)
    for stat in ("str", "agi", "int", "wis", "hlt", "chm"):
        allocated = stats.get(stat, 10)
        race_mod  = race["stat_mods"].get(stat, 0) if race else 0
        setattr(caller.db, f"base_{stat}", allocated - race_mod)

    # 2. Apply race and class
    caller.db.race       = race_name
    caller.db.char_class = class_name
    caller.db.known_spells = []

    # Class-specific starting spells
    if class_name == "bard":
        caller.db.known_spells = ["battle hymn", "taunt", "lullaby"]
        # Auto-grant performance skill
        _known_skills = dict(getattr(caller.db, "known_skills", None) or {})
        _known_skills["performance"] = {"level": 1, "uses": 0}
        caller.db.known_skills = _known_skills

    # 3. Recalculate all derived stats, restore HP/mana/kai to full
    recalc_stats(caller)
    caller.db.hp   = caller.db.hp_max
    caller.db.mana = caller.db.max_mana
    caller.db.kai  = caller.db.max_kai

    # 4. Store leftover CP and lives
    caller.db.cp = cp_remaining

    # 5. Store appearance
    caller.db.hair_length = hair_len
    caller.db.hair_color  = hair_col
    caller.db.eye_color   = eye_col

    # 6. Award starting gold and mark chargen complete
    caller.db.gold = 50
    caller.db.chargen_complete = True

    # 7. Move to Village Center of Newhaven
    destinations = evennia.search_object("Village Center of Newhaven")
    if destinations:
        caller.move_to(destinations[0], quiet=True, move_type="teleport")
    else:
        caller.msg("|rWarning: Could not find 'Village Center of Newhaven'.|n")

    # 8. Welcome message + status prompt
    caller.msg(f"\n|gWelcome to Newhaven, {caller.key}! Your adventure begins.|n\n")
    caller.msg(caller.get_prompt(), options={"send_prompt": True})

    # 9. Clean up ndb
    caller.ndb.chargen_stats          = None
    caller.ndb.chargen_pending_race   = None
    caller.ndb.chargen_pending_class  = None
    caller.ndb.chargen_hair_length    = None
    caller.ndb.chargen_hair_color     = None
    caller.ndb.chargen_eye_color      = None

    # Returning (None, None) closes the EvMenu
    return None, None
