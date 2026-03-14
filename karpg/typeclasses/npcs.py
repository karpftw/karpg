"""
NPCs

Typeclass for non-player characters with full 5e-style combat stats.
NPCs participate in combat as hostiles (or other factions) and are
driven by the AI profiles in the combat script.
"""

from evennia.objects.objects import DefaultObject
from evennia.utils.utils import display_len

from .objects import ObjectParent


# ---------------------------------------------------------------------------
# Display helpers (shared style with weapons.py)
# ---------------------------------------------------------------------------

def _pad(content, width):
    """Pad *content* with spaces until its visual length equals *width*."""
    return content + " " * max(0, width - display_len(content))


def _make_hrule(w):
    return f"|x{'=' * (w + 2)}|n"


def _make_divider(w):
    return f"|x{'-' * (w + 2)}|n"


# ---------------------------------------------------------------------------
# NPC ASCII art
# ---------------------------------------------------------------------------

_NPC_ART = {
    "giant_rat": [
        r"|x        /\/\          /\/\         |n",
        r"|x       /    \        /    \        |n",
        r"|x      | |roo|n|x |       | |roo|n|x |       |n",
        r"|x   ,~~\  __  /~~~~~\  __  /~~,   |n",
        r"|x  /    `----`       `----`    \  |n",
        r"|x  \   .-'  `-.___.-'  `-.   /   |n",
        r"|x   `-'                   `-'    |n",
        r"|y      ~~~~~~~~~~~~~~~~~~        |n",
    ],
    "goblin": [
        r"|g      _____                        |n",
        r"|g    .'     `.    ,^.               |n",
        r"|g   /  |Yo|g   |Yo|g  \  /   \              |n",
        r"|g  |    .-.    | | |Yw|n|g | teeth      |n",
        r"|g  |   (   )   |  \   /              |n",
        r"|g   \   `-'   /    `^'               |n",
        r"|g    `._____.`                       |n",
        r"|g     |     |  <-- crude blade       |n",
        r"|x    /|=====|\                       |n",
    ],
    "skeleton": [
        r"|w       .--~~~--.                    |n",
        r"|w      /  |M(o)|n|w  |M(o)|n|w  \                   |n",
        r"|w     |   .----.   |                 |n",
        r"|w     |  / |x|||n|w  \ |  |                 |n",
        r"|w      \ `------' /                 |n",
        r"|w    ---|========|---               |n",
        r"|x       | |  | |                   |n",
        r"|x       |_|  |_|                   |n",
        r"|x      /         \                 |n",
    ],
    "bandit": [
        r"|w       .-------.                   |n",
        r"|w      / .-. .-. \   <-- scarred    |n",
        r"|w     | (|x-|n|w) (|x-|n|w) ||r /|n|w            |n",
        r"|w     |    ___    |                 |n",
        r"|w      \  '---'  /                 |n",
        r"|x    .============.                |n",
        r"|x    | L E A T H  |               |n",
        r"|x    | E  R  A C  |               |n",
        r"|x    '============'               |n",
    ],
    "orc": [
        r"|g      ,-----------.              |n",
        r"|g     /  |r..|n|g    |r..|n|g  \             |n",
        r"|g    | |r(o)|n|g    |r(o)|n|g   |            |n",
        r"|g    |    \___/    |             |n",
        r"|g    |  |W/V    V\|n|g  |  <-- tusks    |n",
        r"|g     \ `---------'/            |n",
        r"|x      |===========|            |n",
        r"|x      | IRON HIDE |            |n",
        r"|x      |===========|            |n",
    ],
}


# ---------------------------------------------------------------------------
# NPC typeclass
# ---------------------------------------------------------------------------

class NPC(ObjectParent, DefaultObject):
    """
    A non-player character with combat stats, AI profile, and threat tracking.

    Key db attributes:
        hp, hp_max, ac, level, proficiency_bonus
        ability_scores   - {"str": 10, "dex": 10, ...}
        conditions       - list of condition dicts
        damage_resistances, damage_vulnerabilities, damage_immunities
        faction          - "hostile" by default
        ai_profile       - "tactical" | "berserker" | "cowardly" | "protective"
        threat_table     - {attacker_id: cumulative_damage}
        xp_value         - XP awarded on defeat
        loot_table       - list of loot dicts (future)
        wielded          - {"main_hand": obj|None, "off_hand": obj|None}
    """

    def at_object_creation(self):
        """Set default combat stats for a new NPC."""
        super().at_object_creation()

        # Core combat stats
        self.db.hp = 10
        self.db.hp_max = 10
        self.db.ac = 10
        self.db.level = 1
        self.db.proficiency_bonus = 2

        # Ability scores
        self.db.ability_scores = {
            "str": 10, "dex": 10, "con": 10,
            "int": 10, "wis": 10, "cha": 10,
        }

        # Status
        self.db.conditions = []
        self.db.spell_slots = {}
        self.db.death_saves = {"successes": 0, "failures": 0}
        self.db.in_combat = None

        # Faction and AI
        self.db.faction = "hostile"
        self.db.ai_profile = "tactical"

        # Damage modifiers
        self.db.damage_resistances = []
        self.db.damage_vulnerabilities = []
        self.db.damage_immunities = []

        # Rewards
        self.db.xp_value = 50
        self.db.loot_table = []

        # Combat tracking
        self.db.threat_table = {}

        # Equipment
        self.db.wielded = {
            "main_hand": None,
            "off_hand": None,
        }

    # ------------------------------------------------------------------
    # Combat hooks
    # ------------------------------------------------------------------

    def at_attacked_by(self, attacker, damage):
        """
        Called when this NPC takes damage from an attacker.

        Updates the threat table so the AI can prioritise targets.
        """
        threat = self.db.threat_table or {}
        atk_id = attacker.id
        threat[atk_id] = threat.get(atk_id, 0) + damage
        self.db.threat_table = threat

    def at_death(self, killer):
        """
        Called when this NPC is killed.

        Handles loot drops (future hook) and logs the death.
        """
        # Future: iterate self.db.loot_table and drop items
        self.db.hp = 0
        self.db.in_combat = None

    # ------------------------------------------------------------------
    # Appearance
    # ------------------------------------------------------------------

    def return_appearance(self, looker, **kwargs):
        """Infographic-style NPC detail panel with combat stats."""
        W = 52  # visible width between borders

        name = self.get_display_name(looker)
        desc = self.db.desc or "A non-descript creature."

        hp = self.db.hp if self.db.hp is not None else 0
        hp_max = self.db.hp_max if self.db.hp_max is not None else 1
        ac = self.db.ac if self.db.ac is not None else 10
        level = self.db.level if self.db.level is not None else 1
        faction = self.db.faction or "hostile"
        ai_profile = self.db.ai_profile or "tactical"
        scores = self.db.ability_scores or {}

        # HP colour
        if hp_max > 0:
            ratio = hp / hp_max
        else:
            ratio = 0
        if ratio > 0.6:
            hp_col = "|G"
        elif ratio > 0.3:
            hp_col = "|Y"
        else:
            hp_col = "|R"

        def line(content):
            return f"|x|||n{_pad(content, W)}|x|||n"

        def stat(label, val):
            return line(f"  |C{label:<16}|n{val}")

        hrule = _make_hrule(W)
        divider = _make_divider(W)

        lines = []
        lines.append(hrule)
        lines.append(line(f"  |m*|b~|n |M-- |W NPC |M--|n |b~|m*|n"))
        lines.append(hrule)
        lines.append(line(f"  |M{name}|n"))

        # Description
        desc_words = desc.split()
        desc_line = ""
        desc_lines = []
        for word in desc_words:
            if len(desc_line) + len(word) + 1 > W - 4:
                desc_lines.append(desc_line)
                desc_line = word
            else:
                desc_line = f"{desc_line} {word}".strip()
        if desc_line:
            desc_lines.append(desc_line)
        for dl in desc_lines:
            lines.append(line(f"  |x{dl}|n"))

        lines.append(divider)
        lines.append(stat("Level", f"|w{level}|n"))
        lines.append(stat("HP",
                          f"{hp_col}{hp}/{hp_max}|n"))
        lines.append(stat("AC", f"|w{ac}|n"))
        lines.append(stat("Faction", f"|M{faction}|n"))
        lines.append(stat("AI", f"|w{ai_profile}|n"))
        lines.append(divider)

        # Ability scores in a compact row
        score_parts = []
        for s in ("str", "dex", "con", "int", "wis", "cha"):
            val = scores.get(s, 10)
            mod = (val - 10) // 2
            sign = "+" if mod >= 0 else ""
            score_parts.append(f"|C{s.upper()}|n |w{val}|n|x({sign}{mod})|n")
        score_line = "  " + "  ".join(score_parts[:3])
        lines.append(line(score_line))
        score_line2 = "  " + "  ".join(score_parts[3:])
        lines.append(line(score_line2))

        # Resistances / vulnerabilities / immunities
        res = self.db.damage_resistances or []
        vul = self.db.damage_vulnerabilities or []
        imm = self.db.damage_immunities or []
        if res or vul or imm:
            lines.append(divider)
            if res:
                lines.append(line(f"  |GResist:|n {', '.join(res)}"))
            if vul:
                lines.append(line(f"  |RVuln:|n  {', '.join(vul)}"))
            if imm:
                lines.append(line(f"  |xImmune:|n {', '.join(imm)}"))

        # Conditions
        conditions = self.db.conditions or []
        if conditions:
            lines.append(divider)
            cond_names = [c.get("name", str(c)) for c in conditions]
            lines.append(line(f"  |yConditions:|n {', '.join(cond_names)}"))

        # ASCII art
        art_key = self.db.art_key or ""
        art = _NPC_ART.get(art_key, [])
        if art:
            lines.append(divider)
            for art_line in art:
                lines.append(line(art_line))

        lines.append(hrule)
        return "\n".join(lines)
