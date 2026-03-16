"""
Combat Commands

Player-facing commands for MajorMUD-style auto-combat.

Combat is automatic on a 4-second tick. These commands modify queued state
on the CombatScript; the script's at_repeat() consumes the state each round.

Commands:
    attack <target>   — initiate combat or change target
    bash              — switch to bash mode (3.3× damage, half attacks)
    smash             — switch to smash mode (6× damage, 1 attack)
    backstab <target> — backstab (5× damage, requires stealth — placeholder)
    cast <spell>      — queue a spell for next round
    flee              — queue a flee attempt
    rank <front|mid|back> — change formation rank
    spells            — list known spells and mana
"""

from evennia import Command
from evennia.utils.utils import inherits_from

from world.spells import get_spell, list_spells, SPELL_REGISTRY
from world.classes import can_use_weapon, can_use_spell_school


def _get_combat_script(location):
    """Find an active CombatScript in a room. Returns script or None."""
    if not location:
        return None
    for s in location.scripts.all():
        if inherits_from(s, "typeclasses.combat_script.CombatScript"):
            if s.db.active:
                return s
    return None


def _check_weapon_allowed(caller):
    """
    Check that the caller's equipped weapon is allowed by their class and race.

    Returns (allowed: bool, reason: str).
    """
    char_class = getattr(caller.db, "char_class", None)
    if not char_class:
        return True, ""

    wielded = caller.db.wielded or {}
    weapon = wielded.get("main_hand")

    if weapon is None:
        # Unarmed
        weapon_type = None
        two_handed = False
    else:
        weapon_type = getattr(weapon.db, "weapon_type", None)
        two_handed = bool(getattr(weapon.db, "two_handed", False))

    # Race two-handed restriction
    if two_handed and not (caller.db.race_two_handed_allowed if caller.db.race_two_handed_allowed is not None else True):
        return False, "Your race cannot use two-handed weapons."

    return can_use_weapon(char_class, weapon_type, two_handed)


# ---------------------------------------------------------------------------
# CmdAttack
# ---------------------------------------------------------------------------

class CmdAttack(Command):
    """
    Attack a target, initiating combat if not already in one.

    Usage:
        attack <target>
        kill <target>

    If already in combat, changes your current target.
    """

    key = "attack"
    aliases = ["kill", "a"]
    help_category = "Combat"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if not args:
            caller.msg("|rUsage: attack <target>|n")
            return

        target = caller.search(args, location=caller.location)
        if not target:
            return

        if target == caller:
            caller.msg("|rYou can't attack yourself.|n")
            return

        if (caller.db.hp or 0) <= 0:
            caller.msg("|rYou are too injured to fight!|n")
            return

        allowed, reason = _check_weapon_allowed(caller)
        if not allowed:
            caller.msg(f"|r{reason}|n")
            return

        script = _get_combat_script(caller.location)

        if script:
            combatants = script.ndb.combatants or {}
            if caller in combatants:
                # Already in combat — just change target
                script.set_target(caller, target)
                caller.msg(f"|yYou focus your attacks on {target.key}.|n")
                return
            else:
                # Join the existing fight
                faction = getattr(caller.db, "faction", "player") or "player"
                script.add_combatant(caller, target, faction)
                caller.msg(f"|RYou enter the fray targeting {target.key}!|n")
                return

        # Start a new combat encounter
        self._start_combat(target)

    def _start_combat(self, target):
        from typeclasses.combat_script import CombatScript
        import evennia

        caller = self.caller
        room = caller.location

        script = evennia.create_script(
            CombatScript,
            obj=room,
            key="combat",
            persistent=True,
            autostart=False,
        )
        script.begin_combat(caller, [target])


# ---------------------------------------------------------------------------
# CmdBash
# ---------------------------------------------------------------------------

class CmdBash(Command):
    """
    Switch to BASH attack mode for the next round.

    Usage:
        bash

    Bash deals 3.3× weapon damage but reduces your accuracy by 40% and
    cuts your attacks per round in half.
    """

    key = "bash"
    aliases = ["aa"]
    help_category = "Combat"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        script = _get_combat_script(caller.location)
        if not script or caller not in (script.ndb.combatants or {}):
            caller.msg("|rYou are not in combat.|n")
            return
        allowed, reason = _check_weapon_allowed(caller)
        if not allowed:
            caller.msg(f"|r{reason}|n")
            return
        script.set_attack_mode(caller, "bash")
        caller.msg("|MYou wind up for a BASH!|n")


# ---------------------------------------------------------------------------
# CmdSmash
# ---------------------------------------------------------------------------

class CmdSmash(Command):
    """
    Switch to SMASH attack mode for the next round.

    Usage:
        smash

    Smash deals 6× weapon damage but greatly reduces accuracy and you only
    get one attack per round.
    """

    key = "smash"
    help_category = "Combat"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        script = _get_combat_script(caller.location)
        if not script or caller not in (script.ndb.combatants or {}):
            caller.msg("|rYou are not in combat.|n")
            return
        allowed, reason = _check_weapon_allowed(caller)
        if not allowed:
            caller.msg(f"|r{reason}|n")
            return
        script.set_attack_mode(caller, "smash")
        caller.msg("|RYou ready yourself for a massive SMASH!|n")


# ---------------------------------------------------------------------------
# CmdBackstab
# ---------------------------------------------------------------------------

class CmdBackstab(Command):
    """
    Backstab a target for massive damage (requires hiding).

    Usage:
        backstab <target>
        bs <target>

    Deals 5× weapon damage on a single hit. You must be hiding (future
    feature — currently always available but telegraphed to the target).
    """

    key = "backstab"
    aliases = ["bs"]
    help_category = "Combat"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if getattr(caller.db, "char_class", None) not in ("thief", None):
            caller.msg("|rOnly Thieves can backstab.|n")
            return

        script = _get_combat_script(caller.location)

        if script and caller in (script.ndb.combatants or {}):
            # Already in combat — switch mode
            if args:
                target = caller.search(args, location=caller.location)
                if not target:
                    return
                script.set_target(caller, target)
            script.set_attack_mode(caller, "backstab")
            caller.msg("|xYou move into position for a BACKSTAB...|n")
            return

        if not args:
            caller.msg("|rUsage: backstab <target>|n")
            return

        target = caller.search(args, location=caller.location)
        if not target:
            return
        if target == caller:
            caller.msg("|rYou can't backstab yourself.|n")
            return

        # Start combat in backstab mode
        from typeclasses.combat_script import CombatScript
        import evennia

        new_script = evennia.create_script(
            CombatScript,
            obj=caller.location,
            key="combat",
            persistent=True,
            autostart=False,
        )
        new_script.begin_combat(caller, [target])
        # Set mode after begin_combat registers us
        new_script.set_attack_mode(caller, "backstab")
        caller.msg("|xYou slip into the shadows to backstab...|n")


# ---------------------------------------------------------------------------
# CmdCast
# ---------------------------------------------------------------------------

class CmdCast(Command):
    """
    Cast a spell at your current target.

    Usage:
        cast <spell name>
        c <spell name>

    The spell fires on the next combat round. Requires sufficient mana.
    Use 'spells' to see available spells and your mana pool.
    """

    key = "cast"
    aliases = ["c"]
    help_category = "Combat"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if not args:
            caller.msg("|rUsage: cast <spell name>|n")
            return

        spell = get_spell(args)
        if not spell:
            # Try partial match
            matches = [s for k, s in SPELL_REGISTRY.items() if args.lower() in k]
            if len(matches) == 1:
                spell = matches[0]
            elif len(matches) > 1:
                names = ", ".join(s["key"] for s in matches)
                caller.msg(f"|rAmbiguous spell name. Did you mean: {names}?|n")
                return
            else:
                caller.msg(f"|rUnknown spell: '{args}'. Type 'spells' to see your spellbook.|n")
                return

        known = caller.db.known_spells or []
        if spell["key"] not in known:
            caller.msg(f"|rYou don't know '{spell['key']}'.|n")
            return

        spell_class_school = spell.get("class_school")
        char_class = getattr(caller.db, "char_class", None)
        if char_class and spell_class_school:
            if not can_use_spell_school(char_class, spell_class_school):
                caller.msg(f"|rYour class cannot cast {spell_class_school}-school spells.|n")
                return

        mana = caller.db.mana or 0
        cost = spell["mana_cost"]
        if mana < cost:
            caller.msg(f"|rNot enough mana! (need {cost}, have {mana})|n")
            return

        script = _get_combat_script(caller.location)
        if not script or caller not in (script.ndb.combatants or {}):
            caller.msg("|rYou are not in combat. Use 'attack' to initiate combat first.|n")
            return

        script.queue_spell(caller, spell["key"])
        caller.msg(f"|CYou prepare to cast |W{spell['key'].title()}|C...|n |x({cost} mana)|n")


# ---------------------------------------------------------------------------
# CmdFlee
# ---------------------------------------------------------------------------

class CmdFlee(Command):
    """
    Attempt to flee from combat.

    Usage:
        flee
        break
        fl

    Success depends on your Agility. On success you move to a random exit.
    """

    key = "flee"
    aliases = ["break", "fl"]
    help_category = "Combat"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        script = _get_combat_script(caller.location)
        if not script or caller not in (script.ndb.combatants or {}):
            caller.msg("|rYou are not in combat.|n")
            return
        script.queue_flee(caller)
        caller.msg("|YYou look for an opening to escape...|n")


# ---------------------------------------------------------------------------
# CmdRank
# ---------------------------------------------------------------------------

class CmdRank(Command):
    """
    Change your formation rank.

    Usage:
        rank <front|mid|back>

    front — +15 accuracy, -10 defense
    mid   — no modifier (default)
    back  — -10 accuracy, +15 defense
    """

    key = "rank"
    help_category = "Combat"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        args = self.args.strip().lower()

        if args not in ("front", "mid", "back"):
            caller.msg("|rUsage: rank <front|mid|back>|n")
            return

        script = _get_combat_script(caller.location)
        if script and caller in (script.ndb.combatants or {}):
            script.set_rank(caller, args)
        else:
            # Out of combat — still set formation preference
            caller.db.formation_rank = args

        msgs = {
            "front": "|YYou push to the FRONT rank! (+15 acc / -10 def)|n",
            "mid":   "|wYou settle into the MID rank.|n",
            "back":  "|CYou fall back to the BACK rank. (-10 acc / +15 def)|n",
        }
        caller.msg(msgs[args])


# ---------------------------------------------------------------------------
# CmdSpells
# ---------------------------------------------------------------------------

class CmdSpells(Command):
    """
    List your known spells and current mana pool.

    Usage:
        spells
    """

    key = "spells"
    help_category = "Combat"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        known = caller.db.known_spells or []
        mana = caller.db.mana or 0
        max_mana = caller.db.max_mana or 0

        if not known:
            caller.msg("|xYou don't know any spells.|n")
            return

        lines = [""]
        lines.append("|y*" + "─" * 44 + "*|n")
        lines.append("|y│|n  |YSpellbook|n" + " " * 33 + "|y│|n")
        lines.append("|y*" + "─" * 44 + "*|n")
        mana_bar = _mana_bar(mana, max_mana)
        lines.append(f"  |CMana:|n {mana_bar} |c{mana}/{max_mana}|n")
        lines.append("|x" + "-" * 46 + "|n")

        for spell_key in sorted(known):
            spell = get_spell(spell_key)
            if not spell:
                continue
            cost = spell["mana_cost"]
            stype = spell["spell_type"]
            dmg = spell.get("damage_dice", "-")
            affordable = "|n" if mana >= cost else "|x"
            lines.append(
                f"  {affordable}|c{spell['key']:<22}|n "
                f"|w{cost:>3}mp|n  |x{dmg} {stype}|n"
            )

        lines.append("")
        caller.msg("\n".join(lines))


def _mana_bar(current, maximum, width=10):
    """Blue mana bar."""
    if maximum <= 0:
        filled = 0
    else:
        filled = max(0, min(width, round(width * current / maximum)))
    empty = width - filled
    return f"|B{'█' * filled}|x{'░' * empty}|n"
