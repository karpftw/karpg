"""
Combat Commands

Player-facing commands for the turn-based combat system.
Handles initiating combat, attacking, casting spells, dodging, and fleeing.
"""

from evennia import Command
from evennia.utils.utils import inherits_from

from world.spells import get_spell, SPELL_REGISTRY, list_spells


class CmdAttack(Command):
    """
    Attack a target with your wielded weapon.

    Usage:
        attack <target>
        attack <target> with <weapon>

    Initiates combat if not already in an encounter. If combat is active,
    resolves your attack on your turn.

    Aliases: kill, hit
    """

    key = "attack"
    aliases = ["kill", "hit"]
    help_category = "Combat"
    locks = "cmd:all()"

    def parse(self):
        """Parse target and optional weapon from args."""
        self.target_name = ""
        self.weapon_name = ""

        args = self.args.strip()
        if not args:
            return

        if " with " in args:
            parts = args.split(" with ", 1)
            self.target_name = parts[0].strip()
            self.weapon_name = parts[1].strip()
        else:
            self.target_name = args

    def func(self):
        """Execute the attack command."""
        caller = self.caller

        if not self.target_name:
            caller.msg("|rUsage: attack <target> [with <weapon>]|n")
            return

        # Find target in the room
        target = caller.search(self.target_name, location=caller.location)
        if not target:
            return

        # Don't attack yourself
        if target == caller:
            caller.msg("|rYou can't attack yourself.|n")
            return

        # Find weapon if specified
        weapon = None
        if self.weapon_name:
            weapon = caller.search(self.weapon_name, location=caller)
            if not weapon:
                return
            if not inherits_from(weapon, "typeclasses.weapons.Weapon"):
                caller.msg(f"|r{weapon.key} is not a weapon.|n")
                return
        else:
            # Use main hand weapon
            wielded = caller.db.wielded or {}
            weapon = wielded.get("main_hand")

        # Check for active combat script in the room
        combat_script = self._get_combat_script()

        if combat_script and combat_script.db.active:
            # Combat already active — submit action
            combat_script.receive_action(
                caller, "attack", target=target, weapon=weapon
            )
        else:
            # Initiate new combat
            self._start_combat(target)

    def _get_combat_script(self):
        """Find an active combat script in the caller's location."""
        if not self.caller.location:
            return None
        scripts = self.caller.location.scripts.all()
        for s in scripts:
            if inherits_from(s, "typeclasses.combat_script.CombatScript"):
                if s.db.active:
                    return s
        return None

    def _start_combat(self, target):
        """Create a new combat script and begin the encounter."""
        from typeclasses.combat_script import CombatScript
        import evennia

        caller = self.caller
        room = caller.location

        # Create the combat script on the room
        script = evennia.create_script(
            CombatScript,
            obj=room,
            key="combat",
            persistent=True,
            autostart=False,
        )

        # Gather targets — for now just the single target
        targets = [target]

        # Begin combat
        script.begin_combat(caller, targets)


class CmdCast(Command):
    """
    Cast a spell at a target.

    Usage:
        cast <spell>
        cast <spell> at <target>

    Cantrips do not consume spell slots. Levelled spells require an
    available slot of the appropriate level.

    For AoE spells, the spell hits all enemies if no specific target
    is given.
    """

    key = "cast"
    help_category = "Combat"
    locks = "cmd:all()"

    def parse(self):
        """Parse spell name and optional target."""
        self.spell_name = ""
        self.target_name = ""

        args = self.args.strip()
        if not args:
            return

        if " at " in args:
            parts = args.split(" at ", 1)
            self.spell_name = parts[0].strip()
            self.target_name = parts[1].strip()
        else:
            self.spell_name = args

    def func(self):
        """Execute the cast command."""
        caller = self.caller

        if not self.spell_name:
            caller.msg("|rUsage: cast <spell> [at <target>]|n")
            return

        # Look up the spell
        spell_dict = get_spell(self.spell_name)
        if not spell_dict:
            caller.msg(f"|rUnknown spell: {self.spell_name}|n")
            return

        # Check if the caster knows the spell
        known = caller.db.known_spells or []
        if known and spell_dict["key"] not in known:
            caller.msg(f"|rYou don't know {spell_dict['key']}.|n")
            return

        # Check spell slots (cantrips are free)
        spell_level = spell_dict.get("level", 0)
        if spell_level > 0:
            slots = caller.db.spell_slots or {}
            slot_key = str(spell_level)
            remaining = slots.get(slot_key, 0)
            if remaining <= 0:
                caller.msg(
                    f"|rNo level {spell_level} spell slots remaining!|n"
                )
                return

        # Find combat script
        combat_script = self._get_combat_script()
        if not combat_script or not combat_script.db.active:
            caller.msg("|rYou can only cast combat spells during combat.|n")
            return

        # Determine targets
        targets = []
        if self.target_name:
            target = caller.search(self.target_name,
                                   location=caller.location)
            if not target:
                return
            targets = [target]
        elif spell_dict.get("aoe"):
            # AoE: target all enemies
            factions = combat_script.db.factions or {}
            my_faction = factions.get(caller.id, "player")
            order = combat_script.db.initiative_order or []
            for c, _ in order:
                c_faction = factions.get(c.id, "unknown")
                if c_faction != my_faction:
                    c_hp = c.db.hp if c.db.hp is not None else 0
                    if c_hp > 0:
                        targets.append(c)
            if not targets:
                caller.msg("|rNo valid targets for this spell.|n")
                return

        combat_script.receive_action(
            caller, "cast", spell=spell_dict, targets=targets
        )

    def _get_combat_script(self):
        """Find an active combat script in the caller's location."""
        if not self.caller.location:
            return None
        scripts = self.caller.location.scripts.all()
        for s in scripts:
            if inherits_from(s, "typeclasses.combat_script.CombatScript"):
                if s.db.active:
                    return s
        return None


class CmdPass(Command):
    """
    Take the Dodge action — skip your attack and gain defensive benefits.

    Usage:
        pass
        dodge
        wait

    Until your next turn, attack rolls against you have disadvantage.
    """

    key = "pass"
    aliases = ["dodge", "wait"]
    help_category = "Combat"
    locks = "cmd:all()"

    def func(self):
        """Execute the pass/dodge command."""
        caller = self.caller

        combat_script = self._get_combat_script()
        if not combat_script or not combat_script.db.active:
            caller.msg("|rYou're not in combat.|n")
            return

        combat_script.receive_action(caller, "pass")

    def _get_combat_script(self):
        """Find an active combat script in the caller's location."""
        if not self.caller.location:
            return None
        scripts = self.caller.location.scripts.all()
        for s in scripts:
            if inherits_from(s, "typeclasses.combat_script.CombatScript"):
                if s.db.active:
                    return s
        return None


class CmdFlee(Command):
    """
    Attempt to flee from combat.

    Usage:
        flee
        run
        escape

    Makes an opposed DEX check against the highest-DEX enemy.
    On failure, you lose your turn and the enemy gets an opportunity attack.
    On success, you are moved to a random exit.
    """

    key = "flee"
    aliases = ["run", "escape"]
    help_category = "Combat"
    locks = "cmd:all()"

    def func(self):
        """Execute the flee command."""
        caller = self.caller

        combat_script = self._get_combat_script()
        if not combat_script or not combat_script.db.active:
            caller.msg("|rYou're not in combat.|n")
            return

        combat_script.receive_action(caller, "flee")

    def _get_combat_script(self):
        """Find an active combat script in the caller's location."""
        if not self.caller.location:
            return None
        scripts = self.caller.location.scripts.all()
        for s in scripts:
            if inherits_from(s, "typeclasses.combat_script.CombatScript"):
                if s.db.active:
                    return s
        return None


class CmdSpells(Command):
    """
    List your known spells and remaining spell slots.

    Usage:
        spells
    """

    key = "spells"
    help_category = "Combat"
    locks = "cmd:all()"

    def func(self):
        """Display known spells and spell slots."""
        caller = self.caller

        known = caller.db.known_spells or []
        slots = caller.db.spell_slots or {}

        if not known:
            caller.msg("|xYou don't know any spells.|n")
            return

        lines = []
        lines.append("")
        lines.append("|y*" + "─" * 40 + "*|n")
        lines.append("|y│|n  |YSpellbook|n" + " " * 29 + "|y│|n")
        lines.append("|y*" + "─" * 40 + "*|n")

        # Spell slots summary
        if slots:
            slot_parts = []
            for lvl in sorted(slots.keys(), key=int):
                remaining = slots[lvl]
                slot_parts.append(f"|wLv{lvl}:|n |c{remaining}|n")
            lines.append(f"  |wSlots:|n {' | '.join(slot_parts)}")
            lines.append("|x" + "-" * 42 + "|n")

        # Group by level
        cantrips = []
        levelled = {}
        for spell_key in known:
            spell = get_spell(spell_key)
            if not spell:
                continue
            if spell["level"] == 0:
                cantrips.append(spell)
            else:
                levelled.setdefault(spell["level"], []).append(spell)

        if cantrips:
            lines.append("  |wCantrips:|n")
            for sp in sorted(cantrips, key=lambda s: s["key"]):
                dmg = sp.get("damage_dice", "-")
                dtype = sp.get("damage_type", "")
                stype = sp.get("spell_type", "")
                lines.append(
                    f"    |c{sp['key']:<20}|n |x{dmg} {dtype} ({stype})|n"
                )

        for lvl in sorted(levelled.keys()):
            remaining = slots.get(str(lvl), 0)
            lines.append(f"\n  |wLevel {lvl}|n |x({remaining} slots):|n")
            for sp in sorted(levelled[lvl], key=lambda s: s["key"]):
                dmg = sp.get("damage_dice", "-")
                dtype = sp.get("damage_type", "")
                stype = sp.get("spell_type", "")
                lines.append(
                    f"    |c{sp['key']:<20}|n |x{dmg} {dtype} ({stype})|n"
                )

        lines.append("")
        caller.msg("\n".join(lines))
