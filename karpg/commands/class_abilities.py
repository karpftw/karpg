"""
Class Active Ability Commands

One per class — usable only by the matching class. Cooldowns stored in
db.skill_cooldowns with "ability_*" key prefix.

    CmdChallenge  (Warrior)
    CmdSurge      (Mage)
    CmdVanish     (Thief)
    CmdCommune    (Druid)
    CmdConsecrate (Priest)
    CmdDarkPact   (Warlock)
    CmdHex        (Gypsy)
    CmdMeditate   (Mystic)
"""

from evennia import Command

from world.class_abilities import (
    check_cooldown, set_cooldown, cooldown_remaining,
    # Warrior
    apply_challenge, CHALLENGE_CD, CHALLENGE_DURATION,
    # Mage
    can_surge, apply_surge, SURGE_CD,
    # Thief
    vanish_success_chance, VANISH_CD,
    # Druid
    COMMUNE_CD,
    # Priest
    CONSECRATE_CD, CONSECRATE_DURATION,
    # Warlock
    can_dark_pact, apply_dark_pact, DARK_PACT_CD,
    # Gypsy
    hex_save_check, apply_hex_stack, HEX_MAX_STACKS, HEX_CD,
    # Mystic
    begin_meditate, MEDITATE_CD, MEDITATE_TICKS,
)
from world.conditions import apply_condition, has_condition


def _class_only(caller, required_class):
    """Return True if caller is the required class, else send error and return False."""
    char_class = getattr(caller.db, "char_class", None) or ""
    if char_class.lower() != required_class.lower():
        caller.msg(f"|rOnly a {required_class.capitalize()} can use that ability.|n")
        return False
    return True


def _cd_check(caller, key, duration):
    """Check and report cooldown. Returns True if ready."""
    if not check_cooldown(caller, key, duration):
        secs = int(cooldown_remaining(caller, key, duration))
        caller.msg(f"|rAbility on cooldown. ({secs}s remaining)|n")
        return False
    return True


# ---------------------------------------------------------------------------
# Warrior — Challenge
# ---------------------------------------------------------------------------

class CmdChallenge(Command):
    """
    Issue a challenge that forces nearby enemies to attack you.

    Boosts your threat on all NPCs in the room (+50), forcing them to focus
    on you. Applies 'provoked' to yourself (+5 def / -5 acc) for 3 rounds.

    Usage:
      challenge
    """

    key = "challenge"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        if not _class_only(caller, "warrior"):
            return
        if not _cd_check(caller, "ability_challenge", CHALLENGE_CD):
            return

        # Must be in combat or in a room with NPCs
        room_npcs = [
            obj for obj in caller.location.contents
            if obj is not caller
            and hasattr(obj.db, "ai_profile")
            and getattr(obj.db, "ai_profile", None)
            and (obj.db.hp or 0) > 0
        ]

        if not room_npcs:
            caller.msg("There are no enemies here to challenge.")
            return

        apply_challenge(caller, room_npcs)
        apply_condition(caller, "provoked", duration=CHALLENGE_DURATION, source="challenge")

        set_cooldown(caller, "ability_challenge")
        caller.msg(
            f"|YCHALLENGE!|n You roar your defiance — {len(room_npcs)} "
            f"{'enemy focuses' if len(room_npcs) == 1 else 'enemies focus'} on you!\n"
            f"|xProvoked: +5 def / -5 acc for {CHALLENGE_DURATION} rounds.|n"
        )
        caller.location.msg_contents(
            f"|Y{caller.key} issues a thunderous challenge, drawing all eyes!|n",
            exclude=[caller],
        )


# ---------------------------------------------------------------------------
# Mage — Surge
# ---------------------------------------------------------------------------

class CmdSurge(Command):
    """
    Convert HP into mana in a dangerous surge of power.

    Spend 20 HP to gain 10 mana. Requires at least 25 current HP.
    Useful when mana is depleted and the fight is not yet over.

    Usage:
      surge
    """

    key = "surge"
    locks = "cmd:all()"
    help_category = "Magic"

    def func(self):
        caller = self.caller
        if not _class_only(caller, "mage"):
            return
        if not _cd_check(caller, "ability_surge", SURGE_CD):
            return

        ok, reason = can_surge(caller)
        if not ok:
            caller.msg(f"|r{reason}|n")
            return

        hp_spent, mana_gained = apply_surge(caller)
        set_cooldown(caller, "ability_surge")
        caller.msg(
            f"|RSurge!|n You push your life-force into raw magic.\n"
            f"  -{hp_spent} HP  +{mana_gained} Mana\n"
            f"  HP: {caller.db.hp}/{caller.db.hp_max}  "
            f"Mana: {caller.db.mana}/{caller.db.max_mana}"
        )
        caller.location.msg_contents(
            f"|R{caller.key} burns with brief, feverish light!|n",
            exclude=[caller],
        )


# ---------------------------------------------------------------------------
# Thief — Vanish
# ---------------------------------------------------------------------------

class CmdVanish(Command):
    """
    Vanish from combat, entering stealth mid-fight.

    Requires the Stealth skill. On success, you drop from the current combat
    encounter and become hidden. Failure leaves you visible.

    Usage:
      vanish
    """

    key = "vanish"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        if not _class_only(caller, "thief"):
            return
        if not _cd_check(caller, "ability_vanish", VANISH_CD):
            return

        from world.skills import has_skill
        if not has_skill(caller, "stealth"):
            caller.msg("|rVanish requires the Stealth skill.|n")
            return

        import random
        chance = vanish_success_chance(caller)
        if random.random() < chance:
            # Success: drop from combat and go hidden
            script = caller.db.in_combat
            if script:
                script.remove_combatant(caller)
            caller.db.is_hidden = True
            set_cooldown(caller, "ability_vanish")
            caller.msg(
                f"|G[VANISH]|n You dissolve into the shadows! "
                f"({int(chance * 100)}% chance)"
            )
            caller.location.msg_contents(
                f"|x{caller.key} vanishes from sight!|n",
                exclude=[caller],
            )
        else:
            set_cooldown(caller, "ability_vanish")
            caller.msg(
                f"|rVanish failed!|n You couldn't find cover in time. "
                f"({int(chance * 100)}% chance)"
            )
            caller.location.msg_contents(
                f"|x{caller.key} scrambles for shadows but fails to hide!|n",
                exclude=[caller],
            )


# ---------------------------------------------------------------------------
# Druid — Commune
# ---------------------------------------------------------------------------

class CmdCommune(Command):
    """
    Commune with the natural world to sense hidden presences.

    Reveals all hidden creatures in the current room. Outdoors, also shows
    the direction of a recent track target (if one is active).

    Usage:
      commune
    """

    key = "commune"
    locks = "cmd:all()"
    help_category = "Skills"

    def func(self):
        caller = self.caller
        if not _class_only(caller, "druid"):
            return
        if not _cd_check(caller, "ability_commune", COMMUNE_CD):
            return

        hidden_found = []
        for obj in caller.location.contents:
            if obj is caller:
                continue
            if getattr(obj.db, "is_hidden", False):
                obj.db.is_hidden = False
                hidden_found.append(obj.key)
                obj.msg(f"|y{caller.key}'s commune ability senses your presence!|n")

        set_cooldown(caller, "ability_commune")

        if hidden_found:
            names = ", ".join(hidden_found)
            caller.msg(
                f"|GCommune|n — Your senses extend through the room.\n"
                f"  You sense hidden: |w{names}|n"
            )
        else:
            caller.msg(
                "|GCommune|n — Your senses extend through the room.\n"
                "  No hidden presences detected."
            )

        # Outdoors: hint toward recent track target
        if getattr(caller.location.db, "is_outdoor", False):
            track_target = getattr(caller.ndb, "track_target", None)
            if track_target:
                caller.msg(
                    f"  |xYour connection to the land suggests {track_target} "
                    f"passed through this area recently.|n"
                )


# ---------------------------------------------------------------------------
# Priest — Consecrate
# ---------------------------------------------------------------------------

class CmdConsecrate(Command):
    """
    Consecrate the ground beneath you with holy power.

    For 2 combat rounds: undead in the room take 1d6 holy damage per round,
    and your HP regen (outside combat) doubles while the consecration holds.

    Usage:
      consecrate
    """

    key = "consecrate"
    locks = "cmd:all()"
    help_category = "Magic"

    def func(self):
        caller = self.caller
        if not _class_only(caller, "priest"):
            return
        if not _cd_check(caller, "ability_consecrate", CONSECRATE_CD):
            return

        caller.location.db.consecrated_ticks = CONSECRATE_DURATION
        set_cooldown(caller, "ability_consecrate")
        caller.msg(
            f"|WConsecrate!|n You invoke holy power upon this ground.\n"
            f"  Undead will suffer 1d6 holy damage per round for "
            f"{CONSECRATE_DURATION} rounds."
        )
        caller.location.msg_contents(
            f"|W{caller.key} consecrates the ground with holy light!|n",
            exclude=[caller],
        )


# ---------------------------------------------------------------------------
# Warlock — Dark Pact
# ---------------------------------------------------------------------------

class CmdDarkPact(Command):
    """
    Invoke your dark patron to convert HP into mana.

    Spend 15 HP to gain 10 mana (better ratio than Mage Surge).
    Requires at least 20 current HP.

    Usage:
      dark_pact
    """

    key = "dark_pact"
    aliases = ["darkpact", "pact"]
    locks = "cmd:all()"
    help_category = "Magic"

    def func(self):
        caller = self.caller
        if not _class_only(caller, "warlock"):
            return
        if not _cd_check(caller, "ability_dark_pact", DARK_PACT_CD):
            return

        ok, reason = can_dark_pact(caller)
        if not ok:
            caller.msg(f"|r{reason}|n")
            return

        hp_spent, mana_gained = apply_dark_pact(caller)
        set_cooldown(caller, "ability_dark_pact")
        caller.msg(
            f"|MDark Pact!|n Your patron extracts its price.\n"
            f"  -{hp_spent} HP  +{mana_gained} Mana\n"
            f"  HP: {caller.db.hp}/{caller.db.hp_max}  "
            f"Mana: {caller.db.mana}/{caller.db.max_mana}"
        )
        caller.location.msg_contents(
            f"|M{caller.key} communes with a dark presence!|n",
            exclude=[caller],
        )


# ---------------------------------------------------------------------------
# Gypsy — Hex
# ---------------------------------------------------------------------------

class CmdHex(Command):
    """
    Lay a hex on your target, reducing their accuracy.

    Each application reduces the target's accuracy by 5. Stacks up to 3
    times. Target rolls WIS save (d20 + WIS vs DC 12) to resist.

    Usage:
      hex <target>
    """

    key = "hex"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        if not _class_only(caller, "gypsy"):
            return
        if not _cd_check(caller, "ability_hex", HEX_CD):
            return

        if not self.args.strip():
            caller.msg("Usage: hex <target>")
            return

        target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return

        if target is caller:
            caller.msg("You cannot hex yourself.")
            return

        # WIS save check
        if hex_save_check(target):
            set_cooldown(caller, "ability_hex")
            caller.msg(f"|r{target.key} resists your hex!|n")
            try:
                target.msg(f"|GYou resist {caller.key}'s hex!|n")
            except Exception:
                pass
            return

        new_stacks = apply_hex_stack(target)
        set_cooldown(caller, "ability_hex")

        if new_stacks is None:
            caller.msg(f"|y{target.key} is already fully hexed (max {HEX_MAX_STACKS} stacks).|n")
            return

        penalty = new_stacks * 5
        caller.msg(
            f"|yHex!|n A curse settles on {target.key}. "
            f"({new_stacks}/{HEX_MAX_STACKS} stacks, -{penalty} acc)"
        )
        try:
            target.msg(
                f"|y{caller.key} lays a hex upon you!|n "
                f"({new_stacks}/{HEX_MAX_STACKS} stacks, -{penalty} acc)"
            )
        except Exception:
            pass
        caller.location.msg_contents(
            f"|y{caller.key} hexes {target.key}!|n",
            exclude=[caller, target],
        )


# ---------------------------------------------------------------------------
# Mystic — Meditate
# ---------------------------------------------------------------------------

class CmdMeditate(Command):
    """
    Enter a meditative trance to rapidly restore Kai energy.

    While meditating you cannot act, but gain +10 defense and Kai regenerates
    at double speed. Lasts 3 combat ticks (12 seconds). Auto-clears after.

    Usage:
      meditate
    """

    key = "meditate"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        if not _class_only(caller, "mystic"):
            return
        if not _cd_check(caller, "ability_meditate", MEDITATE_CD):
            return

        if has_condition(caller, "meditating"):
            caller.msg("You are already meditating.")
            return

        begin_meditate(caller)
        set_cooldown(caller, "ability_meditate")
        caller.msg(
            f"|mMeditate|n — You sink into deep focus.\n"
            f"  +10 defense, double Kai regen, cannot act for {MEDITATE_TICKS} rounds."
        )
        caller.location.msg_contents(
            f"|m{caller.key} closes their eyes and enters deep meditation.|n",
            exclude=[caller],
        )
