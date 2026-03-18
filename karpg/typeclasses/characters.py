"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.
"""

from evennia.objects.objects import DefaultCharacter
from evennia.utils.utils import display_len

from .objects import ObjectParent
from world.combat_engine import hp_colour
from world.stats import recalc_stats, get_carry_capacity, get_carried_weight
from world.xp_tables import xp_in_bracket, xp_to_next_level


class Character(ObjectParent, DefaultCharacter):
    """
    The Character re-implements some Object hooks to represent a player-
    controlled entity in-game.

    MajorMUD stats:
        str  — melee damage + accuracy
        agi  — accuracy, defense, attacks per round
        int  — mana pool, spell power
        wis  — mana regeneration
        hlt  — max HP
        chm  — merchant prices, social effects

    Combat attributes:
        hp, hp_max       — current and max hit points
        mana, max_mana   — current and max mana
        ac               — armor class (base defense)
        dr               — damage resistance (flat damage reduction)
        level
        formation_rank   — "front" | "mid" | "back"
        in_combat        — reference to active CombatScript, or None
        known_spells     — list of spell key strings
        xp               — total experience points
        faction          — "player"
    """

    def at_object_creation(self):
        super().at_object_creation()

        # Weapon slots
        self.db.wielded = {
            "main_hand": None,
            "off_hand": None,
        }

        # Armor slots
        self.db.armor_slots = {
            "head": None, "neck": None, "chest": None, "arms": None,
            "hands": None, "waist": None, "legs": None, "feet": None,
            "left_ring": None, "right_ring": None,
        }
        self.db.base_ac = 10
        self.db.carrying_weight = 0.0

        # Class and race
        self.db.char_class = "warrior"
        self.db.race       = "human"

        # MajorMUD base stats (before racial modifiers)
        self.db.base_str = 10
        self.db.base_agi = 10
        self.db.base_int = 10
        self.db.base_wis = 10
        self.db.base_hlt = 10
        self.db.base_chm = 10

        # Derived stats (set by recalc_stats)
        self.db.str = 10
        self.db.agi = 10
        self.db.int = 10
        self.db.wis = 10
        self.db.hlt = 10
        self.db.chm = 10

        # Combat stats
        self.db.hp      = 1   # placeholder; recalc_stats sets hp_max and clamps
        self.db.hp_max  = 1
        self.db.mana    = 0
        self.db.max_mana = 0
        self.db.kai     = 0
        self.db.max_kai = 0
        self.db.ac      = 10
        self.db.dr      = 0
        self.db.level   = 1
        self.db.bonus_hp = 0

        # Magic resistance
        self.db.base_magic_resistance = 0
        self.db.magic_resistance = 0

        # Race-derived flags
        self.db.race_two_handed_allowed = True

        # Formation
        self.db.formation_rank = "mid"

        # Status
        self.db.conditions = []
        self.db.in_combat  = None
        self.db.faction    = "player"

        # Spells and progression
        self.db.known_spells = []
        self.db.xp           = 0
        self.db.lives        = 9   # MajorMUD: start with 9 lives; gain 1 per level

        # Resting
        self.db.is_resting = False

        # Stealth
        self.db.is_hidden = False

        # Chargen flag — False triggers the chargen menu on first puppet
        self.db.chargen_complete = False
        self.db.cp = 0

        # Appearance (set during chargen)
        self.db.hair_length = "medium"
        self.db.hair_color  = "brown"
        self.db.eye_color   = "brown"

        # Calculate derived values and set hp/mana/kai to full
        recalc_stats(self)
        self.db.hp   = self.db.hp_max
        self.db.mana = self.db.max_mana
        self.db.kai  = self.db.max_kai

    def at_post_puppet(self, **kwargs):
        """Send the status line immediately when a player connects/puppets.
        For newly created characters (chargen_complete is exactly False),
        launch the chargen menu instead.
        """
        super().at_post_puppet(**kwargs)
        if self.db.chargen_complete is False:
            from world.chargen_menu import start_chargen
            start_chargen(self)
        else:
            self.msg(self.get_prompt(), options={"send_prompt": True})

    def at_after_move(self, source_location, move_type="move", **kwargs):
        """Interrupt rest, break stealth, and exit combat if the character moves."""
        # Stealth movement checks
        if self.db.is_hidden:
            from world.stealth import noise_check, detection_check
            if not noise_check(self):
                self.db.is_hidden = False
                self.msg("|yYou stumble and break stealth!|n")
            else:
                # Moved silently — check NPC detection in new room
                for obj in self.location.contents:
                    if obj is self:
                        continue
                    if not hasattr(obj, "db") or not getattr(obj.db, "ai_profile", None):
                        continue
                    if detection_check(self, obj):
                        self.db.is_hidden = False
                        self.msg(f"|rThe {obj.key} spots you!|n")
                        self.location.msg_contents(
                            f"|r{self.key} emerges from the shadows!|n",
                            exclude=[self],
                        )
                        break

        if self.db.is_resting:
            scripts = self.scripts.get("resting")
            if scripts:
                self.msg("|yYour rest is interrupted as you move.|n")
                scripts[0].stop()

        script = self.db.in_combat
        if script:
            script.remove_combatant(self)
            self.msg("|yYou retreat from the fight!|n")

    def get_prompt(self):
        """Return a MajorMUD-style status line string."""
        hp     = self.db.hp or 0
        hp_max = self.db.hp_max or 1
        level = self.db.level or 1
        xp    = self.db.xp or 0

        col = hp_colour(hp, hp_max)
        hidden_tag = "|x[HIDDEN]|n " if self.db.is_hidden else ""
        rest_tag = "|c[REST]|n " if self.db.is_resting else ""
        hp_part = f"[|wHP|n: {col}{hp}/{hp_max}|n]"

        char_class = self.db.char_class or "warrior"
        race = self.db.race or "human"
        if level >= 75:
            xp_display = "MAX"
        else:
            xp_bracket = xp_in_bracket(xp, level, char_class, race)
            xp_next = xp_to_next_level(level, char_class, race)
            xp_display = f"{xp_bracket:,}/{xp_next:,}"
        lv_part = f"[|wLv {level}|n | |yXP: {xp_display}|n]>"

        max_kai  = self.db.max_kai or 0
        max_mana = self.db.max_mana or 0

        if max_kai > 0:
            kai = self.db.kai or 0
            energy_part = f" [|mKai|n: |M{kai}/{max_kai}|n]"
        elif max_mana > 0:
            mana = self.db.mana or 0
            energy_part = f" [|cMana|n: |C{mana}/{max_mana}|n]"
        else:
            energy_part = ""

        return f"{hidden_tag}{rest_tag}{hp_part}{energy_part} {lv_part}"

    # ── appearance ────────────────────────────────────────────────────────────

    def _generate_description(self):
        """Generate a deterministic 1-2 sentence description from stats and race."""
        str_val = self.db.str or 10
        hlt_val = self.db.hlt or 10
        agi_val = self.db.agi or 10
        int_val = self.db.int or 10
        wis_val = self.db.wis or 10
        race    = (self.db.race or "human").lower()

        build_avg = (str_val + hlt_val) / 2
        mind_avg  = (int_val + wis_val) / 2

        # Race prefix modifies build descriptor
        race_prefix = {
            "dwarf":    "stocky",
            "elf":      "lithe",
            "half_orc": "broad and brutish",
            "gnome":    "small-framed",
            "halfling": "diminutive",
        }.get(race, "")

        if build_avg >= 16:
            build = "powerfully-built figure with the broad shoulders of a seasoned fighter"
        elif build_avg >= 12:
            build = "broad-shouldered figure with a sturdy frame"
        elif build_avg >= 8:
            build = "figure of average build"
        else:
            build = "slight, almost frail figure"

        if race_prefix:
            build = f"{race_prefix}, {build}"

        if agi_val >= 16:
            movement = "Fluid, almost supernatural movements suggest extraordinary agility."
        elif agi_val >= 12:
            movement = "Practiced, easy movements carry a quiet confidence."
        else:
            movement = "Measured, deliberate movements suggest steady composure."

        if mind_avg >= 14:
            eyes = "sharp, calculating eyes that miss little"
        elif mind_avg >= 10:
            eyes = "an attentive, watchful gaze"
        else:
            eyes = "a distant, unfocused gaze"

        hair_length = self.db.hair_length or "medium"
        hair_color  = self.db.hair_color  or "brown"
        eye_color   = self.db.eye_color   or "brown"

        appearance_clause = f"with {hair_length} {hair_color} hair and {eye_color} eyes"

        return (
            f"A {build} {appearance_clause}. "
            f"{movement} {eyes.capitalize()} completes the picture."
        )

    def return_appearance(self, looker, **kwargs):
        """Override default look: show procedural description + full gear panel."""
        W = 52

        def _pad(content, width):
            return content + ' ' * max(0, width - display_len(content))

        def line(content):
            return f"|x|||n{_pad(content, W)}|x|||n"

        hrule   = f"|x{'=' * (W + 2)}|n"
        divider = f"|x{'-' * (W + 2)}|n"

        name       = self.get_display_name(looker)
        char_class = (self.db.char_class or "adventurer").capitalize()
        race       = (self.db.race or "human").replace("_", "-").capitalize()
        desc_text  = self.db.desc or self._generate_description()

        lines = []
        lines.append(hrule)
        lines.append(line(f"  |Y{name}|n  |x[{race} {char_class}]|n"))
        lines.append(divider)

        # Wrap description
        desc_words = desc_text.split()
        desc_line, desc_lines = "", []
        for word in desc_words:
            if len(desc_line) + len(word) + 1 > W - 4:
                desc_lines.append(desc_line)
                desc_line = word
            else:
                desc_line = f"{desc_line} {word}".strip()
        if desc_line:
            desc_lines.append(desc_line)
        for dl in desc_lines:
            lines.append(line(f"  {dl}"))

        lines.append(divider)

        # Gear panel — armor slots in two columns
        armor_slots = self.db.armor_slots or {}
        wielded     = self.db.wielded or {}

        def slot_str(slot):
            item = armor_slots.get(slot)
            if item:
                return f"|w{item.get_display_name(looker)}|n"
            return "|x(empty)|n"

        def weapon_str(slot):
            item = wielded.get(slot)
            if item:
                return f"|w{item.get_display_name(looker)}|n"
            return "|x(empty)|n"

        def gear_row(left_label, left_slot, right_label, right_slot, is_weapon=False):
            lval = weapon_str(left_slot)  if is_weapon else slot_str(left_slot)
            rval = weapon_str(right_slot) if is_weapon else slot_str(right_slot)
            left_label_padded  = f"|C{left_label:<11}|n"
            right_label_padded = f"|C{right_label:<11}|n"
            left_part  = f"  {left_label_padded} {lval}"
            right_part = f"  {right_label_padded} {rval}"
            # pad left half to half-width
            half = W // 2
            left_part_padded = left_part + ' ' * max(0, half - display_len(left_part))
            full = left_part_padded + right_part
            return line(full)

        lines.append(gear_row("Head:",     "head",      "Neck:",        "neck"))
        lines.append(gear_row("Chest:",    "chest",     "Arms:",        "arms"))
        lines.append(gear_row("Hands:",    "hands",     "Waist:",       "waist"))
        lines.append(gear_row("Legs:",     "legs",      "Feet:",        "feet"))
        lines.append(gear_row("Left Ring:","left_ring", "Right Ring:",  "right_ring"))
        lines.append(gear_row("Main Hand:","main_hand", "Off Hand:",    "off_hand", is_weapon=True))

        lines.append(hrule)

        return "\n".join(lines)
