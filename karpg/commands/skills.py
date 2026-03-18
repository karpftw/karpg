"""
Skill Commands

All player-facing skill commands in one module.

CmdSkills    — skills          — formatted table of known skills
CmdLearn     — learn <skill>   — buy/advance at trainer NPC
CmdPick      — pick <target>   — lockpick door or container
CmdSteal     — steal <target>  — thievery / pick pocket
CmdTrack     — track <name>    — follow a character's trail
CmdBandage   — bandage [target]— first aid heal
CmdTurn      — turn            — turn undead (all undead in room)
CmdIntimidate— intimidate <t>  — frighten a target
CmdForage    — forage          — gather herbs/food outdoors
CmdIdentify  — identify <item> — reveal item stats
CmdSearch    — search          — detect traps in room
CmdDisarmTrap— disarm trap     — disable a discovered trap
CmdSetTrap   — settrap <type>  — place a trap (snare/alarm/spike)
CmdBattleCry — battlecry       — party accuracy buff
CmdDisarm    — disarm <target> — knock weapon from target's hand
CmdForm      — form <stance>   — Mystic unarmed stance
"""

from evennia import Command

from world.skills import (
    SKILL_REGISTRY, get_skill, has_skill, skill_level, level_name,
    learn_skill, learn_skill_cost, can_learn_skill,
    check_cooldown, set_cooldown, tick_skill_use,
    lockpick_check, thievery_check, track_check, first_aid_heal,
    turn_undead_check, turn_undead_damage, intimidate_check,
    battle_cry_bonus, disarm_check, trap_check, forage_check, identify_check,
)


# ---------------------------------------------------------------------------
# CmdSkills — view known skills
# ---------------------------------------------------------------------------

class CmdSkills(Command):
    """
    Display your known skills and their levels.

    Usage:
      skills
    """

    key = "skills"
    aliases = []
    locks = "cmd:all()"
    help_category = "Skills"

    def func(self):
        char = self.caller
        known = getattr(char.db, "known_skills", None) or {}

        W = 52
        hrule = f"|x{'=' * (W + 2)}|n"
        divider = f"|x{'-' * (W + 2)}|n"

        lines = [hrule, f" |WKnown Skills|n", divider]

        if not known:
            lines.append("  |xYou have no skills yet. Visit a trainer to learn some.|n")
        else:
            for key in sorted(known.keys()):
                skill = get_skill(key)
                if not skill:
                    continue
                level = known[key].get("level", 0)
                uses = known[key].get("uses", 0)
                lvl_name = level_name(level)
                max_level = skill.get("max_level", 5)
                skill_type = skill["type"].capitalize()
                line = (
                    f"  |W{skill['name']:<20}|n "
                    f"|y{lvl_name:<12}|n "
                    f"|x({skill_type}, Lv {level}/{max_level})|n"
                )
                lines.append(line)

        # Show learnable skills (not known, eligible)
        learnable = []
        for key, skill in sorted(SKILL_REGISTRY.items(), key=lambda x: x[1]["name"]):
            if has_skill(char, key):
                continue
            if skill["auto_grant"]:
                continue
            if skill["cp_learn"] == 0:
                continue
            eligible, _ = can_learn_skill(char, key)
            if eligible:
                cost = learn_skill_cost(char, key)
                learnable.append((skill["name"], cost))

        if learnable:
            lines.append(divider)
            lines.append(f"  |xAvailable to learn (at trainer):|n")
            for name, cost in learnable:
                lines.append(f"  |c{name:<24}|n |x{cost} CP|n")

        cp = getattr(char.db, "cp", 0) or 0
        lines.append(divider)
        lines.append(f"  |xUnspent CP: |W{cp}|n")
        lines.append(hrule)

        self.caller.msg("\n".join(lines))


# ---------------------------------------------------------------------------
# CmdLearn — buy skill at trainer
# ---------------------------------------------------------------------------

class CmdLearn(Command):
    """
    Learn or advance a skill at a trainer NPC.

    Usage:
      learn <skill name>

    You must be in a room with a skill trainer NPC.
    """

    key = "learn"
    locks = "cmd:all()"
    help_category = "Skills"

    def func(self):
        char = self.caller
        if not self.args:
            char.msg("Learn what? Usage: learn <skill name>")
            return

        # Check for trainer in room
        trainer = None
        for obj in char.location.contents:
            if obj is char:
                continue
            if hasattr(obj, "tags") and obj.tags.get("skill_trainer", category="npc_role"):
                trainer = obj
                break
        if not trainer:
            char.msg("|rThere is no skill trainer here.|n")
            return

        skill_arg = self.args.strip().lower()

        # Match skill by name or key
        matched_key = None
        for key, skill in SKILL_REGISTRY.items():
            if key == skill_arg or skill["name"].lower() == skill_arg:
                matched_key = key
                break

        if not matched_key:
            char.msg(f"|rNo skill named '{self.args.strip()}' found.|n")
            return

        success, msg = learn_skill(char, matched_key)
        char.msg(msg)


# ---------------------------------------------------------------------------
# CmdPick — lockpick
# ---------------------------------------------------------------------------

class CmdPick(Command):
    """
    Use lockpicking skill to open a locked door or container.

    Usage:
      pick <exit/door>

    Requires the Lockpick skill.
    """

    key = "pick"
    aliases = ["lockpick"]
    locks = "cmd:all()"
    help_category = "Skills"

    def func(self):
        char = self.caller
        if not has_skill(char, "lockpick"):
            char.msg("|rYou don't have the Lockpick skill.|n")
            return

        ready, remaining = check_cooldown(char, "lockpick")
        if not ready:
            char.msg(f"|rYour hands are still shaking. Wait {remaining}s.|n")
            return

        if not self.args:
            char.msg("Pick what? Usage: pick <door/exit>")
            return

        target_name = self.args.strip().lower()
        target = None
        for obj in char.location.contents:
            if obj.key.lower() == target_name or target_name in [a.lower() for a in obj.aliases.all()]:
                target = obj
                break

        if not target:
            char.msg(f"|rYou don't see '{self.args.strip()}' here.|n")
            return

        if not getattr(target.db, "is_locked", False):
            char.msg(f"|r{target.key} isn't locked.|n")
            return

        difficulty = getattr(target.db, "lock_difficulty", 10)
        set_cooldown(char, "lockpick")

        if lockpick_check(char, difficulty):
            target.db.is_locked = False
            target.locks.remove("traverse")
            tick_skill_use(char, "lockpick")
            char.msg(f"|gYou skillfully pick the lock on {target.key}.|n")
            char.location.msg_contents(
                f"|y{char.key} picks the lock on {target.key}.|n",
                exclude=[char],
            )
        else:
            char.msg(f"|rYour picks slip — {target.key} resists your attempts.|n")


# ---------------------------------------------------------------------------
# CmdSteal — thievery / pick pocket
# ---------------------------------------------------------------------------

class CmdSteal(Command):
    """
    Attempt to steal from a target.

    Usage:
      steal <target>

    Requires the Thievery skill. Failure may trigger combat.
    """

    key = "steal"
    aliases = ["pickpocket"]
    locks = "cmd:all()"
    help_category = "Skills"

    def func(self):
        char = self.caller
        if not has_skill(char, "thievery"):
            char.msg("|rYou don't have the Thievery skill.|n")
            return

        ready, remaining = check_cooldown(char, "thievery")
        if not ready:
            char.msg(f"|rYou need to lay low for {remaining}s before trying again.|n")
            return

        if not self.args:
            char.msg("Steal from whom? Usage: steal <target>")
            return

        target = char.search(self.args.strip(), location=char.location)
        if not target:
            return
        if target is char:
            char.msg("You can't steal from yourself.")
            return

        set_cooldown(char, "thievery")

        if thievery_check(char, target):
            # Try to steal gold first, then an item
            gold = getattr(target.db, "gold", 0) or 0
            if gold > 0:
                stolen = max(1, gold // 4)
                target.db.gold = gold - stolen
                char_gold = getattr(char.db, "gold", 0) or 0
                char.db.gold = char_gold + stolen
                tick_skill_use(char, "thievery")
                char.msg(f"|gYou deftly lift {stolen} gold from {target.key}.|n")
            else:
                items = [obj for obj in target.contents if not obj.destination]
                if items:
                    import random
                    item = random.choice(items)
                    item.move_to(char, quiet=True)
                    tick_skill_use(char, "thievery")
                    char.msg(f"|gYou slip {item.key} from {target.key}'s belongings.|n")
                else:
                    char.msg(f"|y{target.key} has nothing worth taking.|n")
        else:
            char.msg(f"|r{target.key} notices your attempt!|n")
            char.location.msg_contents(
                f"|r{target.key} shouts: 'Thief!'|n",
                exclude=[char],
            )
            # Trigger combat if NPC
            if getattr(target.db, "ai_profile", None):
                from typeclasses.combat_script import CombatScript
                from evennia.utils.utils import inherits_from
                from evennia.utils.create import create_script
                script = None
                for s in char.location.scripts.all():
                    if inherits_from(s, "typeclasses.combat_script.CombatScript"):
                        script = s
                        break
                if script and script.db.active:
                    target_faction = getattr(target.db, "faction", "hostile") or "hostile"
                    script.add_combatant(target, char, target_faction)
                else:
                    new_script = create_script(
                        CombatScript,
                        obj=char.location,
                        autostart=False,
                    )
                    new_script.begin_combat(target, [char])


# ---------------------------------------------------------------------------
# CmdTrack — track a character
# ---------------------------------------------------------------------------

class CmdTrack(Command):
    """
    Follow the trail of another character.

    Usage:
      track <name>

    Requires the Track skill. Reads footprints left in this room.
    """

    key = "track"
    locks = "cmd:all()"
    help_category = "Skills"

    def func(self):
        char = self.caller
        if not has_skill(char, "track"):
            char.msg("|rYou don't have the Track skill.|n")
            return

        ready, remaining = check_cooldown(char, "track")
        if not ready:
            char.msg(f"|rYou need {remaining}s before tracking again.|n")
            return

        if not self.args:
            char.msg("Track whom? Usage: track <name>")
            return

        target_name = self.args.strip().lower()
        import time as _time

        visitors = list(getattr(char.location.db, "recent_visitors", None) or [])
        # Find most recent entry matching the name (skip stale > 5 minutes)
        now = _time.time()
        matches = [
            v for v in reversed(visitors)
            if v["name"].lower() == target_name and now - v.get("time", 0) < 300
        ]

        set_cooldown(char, "track")

        if not matches:
            char.msg(f"|rYou find no recent tracks from {self.args.strip()} here.|n")
            return

        if not track_check(char):
            char.msg("|rYou find signs of passage, but can't make sense of the trail.|n")
            return

        tick_skill_use(char, "track")
        entry = matches[0]
        age = int(now - entry.get("time", now))
        age_str = f"{age}s ago" if age < 60 else f"{age // 60}m ago"
        char.msg(
            f"|g{entry['name']} passed through here recently ({age_str}).|n"
        )


# ---------------------------------------------------------------------------
# CmdBandage — first aid
# ---------------------------------------------------------------------------

class CmdBandage(Command):
    """
    Apply first aid to yourself or another character.

    Usage:
      bandage [target]

    Requires the First Aid skill. 60-second cooldown.
    Cannot be used in combat.
    """

    key = "bandage"
    aliases = ["firstaid"]
    locks = "cmd:all()"
    help_category = "Skills"

    def func(self):
        char = self.caller
        if not has_skill(char, "first_aid"):
            char.msg("|rYou don't have the First Aid skill.|n")
            return

        if char.db.in_combat:
            char.msg("|rYou can't bandage wounds in the middle of combat!|n")
            return

        ready, remaining = check_cooldown(char, "first_aid")
        if not ready:
            char.msg(f"|rYou need {remaining}s before treating wounds again.|n")
            return

        if self.args:
            target = char.search(self.args.strip(), location=char.location)
            if not target:
                return
        else:
            target = char

        hp = getattr(target.db, "hp", 0) or 0
        hp_max = getattr(target.db, "hp_max", 1) or 1

        if hp >= hp_max:
            char.msg(
                f"|y{target.key} is|n" if target is not char else "|yYou are|n"
                + " already at full health.|n"
            )
            return

        heal = first_aid_heal(char)
        target.db.hp = min(hp_max, hp + heal)
        set_cooldown(char, "first_aid")
        tick_skill_use(char, "first_aid")

        if target is char:
            char.msg(f"|gYou bandage your wounds, recovering {heal} HP.|n")
        else:
            char.msg(f"|gYou bandage {target.key}'s wounds, restoring {heal} HP.|n")
            target.msg(f"|g{char.key} tends your wounds, restoring {heal} HP.|n")


# ---------------------------------------------------------------------------
# CmdTurn — turn undead
# ---------------------------------------------------------------------------

class CmdTurn(Command):
    """
    Channel divine power to turn undead in the room.

    Usage:
      turn

    Requires the Turn Undead skill. Targets all undead faction_type NPCs present.
    """

    key = "turn"
    aliases = ["turn undead"]
    locks = "cmd:all()"
    help_category = "Skills"

    def func(self):
        char = self.caller
        if not has_skill(char, "turn_undead"):
            char.msg("|rYou don't have the Turn Undead skill.|n")
            return

        ready, remaining = check_cooldown(char, "turn_undead")
        if not ready:
            char.msg(f"|rYou need {remaining}s to channel divine power again.|n")
            return

        undead_targets = [
            obj for obj in char.location.contents
            if obj is not char
            and getattr(obj.db, "faction_type", "") == "undead"
            and (getattr(obj.db, "hp", 0) or 0) > 0
        ]

        if not undead_targets:
            char.msg("|rThere are no undead here to turn.|n")
            return

        char.msg("|WSolden light bursts from your outstretched hand!|n")
        char.location.msg_contents(
            f"|W{char.key} channels divine energy against the undead!|n",
            exclude=[char],
        )
        set_cooldown(char, "turn_undead")
        tick_skill_use(char, "turn_undead")

        for undead in undead_targets:
            outcome = turn_undead_check(char, undead)
            if outcome == "flee":
                undead_level = getattr(undead.db, "level", 1) or 1
                char.msg(f"|G{undead.key} recoils and flees from your holy power!|n")
                undead.location.msg_contents(
                    f"|G{undead.key} flees in terror!|n", exclude=[char]
                )
                # Remove from combat if in combat
                script = getattr(undead.db, "in_combat", None)
                if script:
                    script.remove_combatant(undead)
                    import random
                    exits = [e for e in char.location.exits if e.access(undead, "traverse")]
                    if exits:
                        undead.move_to(random.choice(exits).destination, quiet=True)
            elif outcome == "damage":
                dmg = turn_undead_damage(char)
                undead.db.hp = max(0, (undead.db.hp or 0) - dmg)
                char.msg(f"|Y{undead.key} takes {dmg} divine damage!|n")
                char.location.msg_contents(
                    f"|Y{undead.key} writhes under the holy light!|n", exclude=[char]
                )
                if (undead.db.hp or 0) <= 0:
                    script = getattr(undead.db, "in_combat", None)
                    if script:
                        script._handle_death(undead, char)
            else:
                char.msg(f"|r{undead.key} resists your turning attempt!|n")


# ---------------------------------------------------------------------------
# CmdIntimidate — frighten a target
# ---------------------------------------------------------------------------

class CmdIntimidate(Command):
    """
    Intimidate a target to apply the frightened condition.

    Usage:
      intimidate <target>

    Requires the Intimidate skill. Must be in combat.
    """

    key = "intimidate"
    locks = "cmd:all()"
    help_category = "Skills"

    def func(self):
        char = self.caller
        if not has_skill(char, "intimidate"):
            char.msg("|rYou don't have the Intimidate skill.|n")
            return

        if not char.db.in_combat:
            char.msg("|rYou can only intimidate in combat.|n")
            return

        ready, remaining = check_cooldown(char, "intimidate")
        if not ready:
            char.msg(f"|rWait {remaining}s before intimidating again.|n")
            return

        if not self.args:
            char.msg("Intimidate whom? Usage: intimidate <target>")
            return

        target = char.search(self.args.strip(), location=char.location)
        if not target:
            return
        if target is char:
            char.msg("You can't intimidate yourself.")
            return

        set_cooldown(char, "intimidate")

        if intimidate_check(char, target):
            from world.conditions import apply_condition
            apply_condition(target, "frightened", duration=3, source=char.key)
            tick_skill_use(char, "intimidate")
            char.msg(f"|G{target.key} blanches with fear!|n")
            target.msg(f"|r{char.key} stares you down — fear grips your heart!|n")
            char.location.msg_contents(
                f"|Y{char.key} intimidates {target.key}!|n",
                exclude=[char, target],
            )
        else:
            char.msg(f"|r{target.key} stands their ground, unmoved.|n")
            target.msg(f"|x{char.key} tries to intimidate you, but you shrug it off.|n")


# ---------------------------------------------------------------------------
# CmdForage — gather herbs outdoors
# ---------------------------------------------------------------------------

class CmdForage(Command):
    """
    Gather herbs or food from the surrounding area.

    Usage:
      forage

    Requires the Forage skill. Only works in outdoor rooms.
    """

    key = "forage"
    locks = "cmd:all()"
    help_category = "Skills"

    def func(self):
        char = self.caller
        if not has_skill(char, "forage"):
            char.msg("|rYou don't have the Forage skill.|n")
            return

        if not getattr(char.location.db, "is_outdoor", False):
            char.msg("|rThere's nothing to forage here — you need to be outdoors.|n")
            return

        ready, remaining = check_cooldown(char, "forage")
        if not ready:
            char.msg(f"|rWait {remaining}s before foraging again.|n")
            return

        if char.db.in_combat:
            char.msg("|rYou can't forage while fighting!|n")
            return

        char.msg("|xYou search the area for edible plants and herbs...|n")
        set_cooldown(char, "forage")

        if forage_check(char):
            import random
            herbs = [
                ("Nightshade Herb", "A dark-leaved herb with a sharp, bitter smell."),
                ("Wild Berries", "A small cluster of tart red berries."),
                ("Feverfew", "Pale yellow flowers said to reduce fever and headache."),
                ("Comfrey Root", "A thick root used to speed healing."),
            ]
            name, desc = random.choice(herbs)
            from evennia.utils.create import create_object
            herb = create_object(
                typeclass="typeclasses.objects.Object",
                key=name,
                location=char,
            )
            herb.db.desc = desc
            herb.db.weight = 0.1
            herb.db.value = 2
            tick_skill_use(char, "forage")
            char.msg(f"|gYou find some {name}!|n")
        else:
            char.msg("|rYou search carefully but find nothing useful.|n")


# ---------------------------------------------------------------------------
# CmdIdentify — reveal item stats
# ---------------------------------------------------------------------------

class CmdIdentify(Command):
    """
    Magically identify an item to reveal its hidden properties.

    Usage:
      identify <item>

    Requires the Identify skill.
    """

    key = "identify"
    locks = "cmd:all()"
    help_category = "Skills"

    def func(self):
        char = self.caller
        if not has_skill(char, "identify"):
            char.msg("|rYou don't have the Identify skill.|n")
            return

        ready, remaining = check_cooldown(char, "identify")
        if not ready:
            char.msg(f"|rWait {remaining}s before identifying again.|n")
            return

        if not self.args:
            char.msg("Identify what? Usage: identify <item>")
            return

        item = char.search(self.args.strip())
        if not item:
            return

        set_cooldown(char, "identify")

        if not identify_check(char):
            char.msg(f"|rYour reading of {item.key} is unclear — you can't discern its properties.|n")
            return

        tick_skill_use(char, "identify")

        lines = [f"|WIdentifying: {item.key}|n"]
        attrs_to_show = [
            ("damage_dice",   "Damage"),
            ("damage_type",   "Damage Type"),
            ("weapon_type",   "Weapon Type"),
            ("armor_type",    "Armor Type"),
            ("ac_bonus",      "AC Bonus"),
            ("dr_bonus",      "DR Bonus"),
            ("weight",        "Weight"),
            ("value",         "Value"),
            ("two_handed",    "Two-Handed"),
            ("speed",         "Speed"),
            ("enchantments",  "Enchantments"),
        ]
        found_any = False
        for attr, label in attrs_to_show:
            val = getattr(item.db, attr, None)
            if val is not None and val != [] and val != "":
                lines.append(f"  |C{label}:|n {val}")
                found_any = True

        if not found_any:
            lines.append("  |xThis item has no special properties.|n")

        char.msg("\n".join(lines))


# ---------------------------------------------------------------------------
# CmdSearch — detect traps
# ---------------------------------------------------------------------------

class CmdSearch(Command):
    """
    Search the room for hidden traps.

    Usage:
      search

    Requires the Traps skill.
    """

    key = "search"
    locks = "cmd:all()"
    help_category = "Skills"

    def func(self):
        char = self.caller
        if not has_skill(char, "traps"):
            char.msg("|rYou don't have the Traps skill.|n")
            return

        char.msg("|xYou carefully examine the area for hidden dangers...|n")

        if not getattr(char.location.db, "has_trap", False):
            char.msg("|xYou find no traps here.|n")
            return

        if getattr(char.location.db, "trap_discovered", False):
            char.msg("|yYou already know about the trap here.|n")
            return

        difficulty = getattr(char.location.db, "trap_difficulty", 10)
        if trap_check(char, difficulty):
            tick_skill_use(char, "traps")
            char.location.db.trap_discovered = True
            trap_type = getattr(char.location.db, "trap_type", "unknown")
            char.msg(f"|G[TRAP FOUND]|n You spot a hidden {trap_type} trap! Use 'disarm trap' to disable it.")
        else:
            char.msg("|rYou search carefully but find nothing... (the trap may still be there.)|n")


# ---------------------------------------------------------------------------
# CmdDisarm — disarm trap OR disarm weapon from target
# ---------------------------------------------------------------------------

class CmdDisarm(Command):
    """
    Disarm a trap or knock a weapon from a target's hand.

    Usage:
      disarm trap          — disable a discovered trap in this room
      disarm <target>      — knock target's weapon to the floor (in combat)

    'disarm trap' requires the Traps skill.
    'disarm <target>' requires the Disarm skill.
    """

    key = "disarm"
    locks = "cmd:all()"
    help_category = "Skills"

    def func(self):
        arg = self.args.strip().lower() if self.args else ""

        if arg == "trap":
            self._disarm_trap()
        elif arg:
            self._disarm_weapon(self.args.strip())
        else:
            self.caller.msg("Usage: disarm trap  OR  disarm <target>")

    def _disarm_trap(self):
        char = self.caller
        if not has_skill(char, "traps"):
            char.msg("|rYou don't have the Traps skill.|n")
            return

        if not getattr(char.location.db, "has_trap", False):
            char.msg("|rThere is no trap here.|n")
            return

        if not getattr(char.location.db, "trap_discovered", False):
            char.msg("|rYou haven't found any trap to disarm. Try 'search' first.|n")
            return

        difficulty = getattr(char.location.db, "trap_difficulty", 10)
        if trap_check(char, difficulty):
            char.location.db.has_trap = False
            char.location.db.trap_discovered = False
            tick_skill_use(char, "traps")
            char.msg("|gYou carefully disarm the trap.|n")
            char.location.msg_contents(
                f"|y{char.key} disarms a hidden trap.|n", exclude=[char]
            )
        else:
            char.msg("|rYour hands slip — the trap is still armed.|n")

    def _disarm_weapon(self, target_name):
        char = self.caller
        if not has_skill(char, "disarm"):
            char.msg("|rYou don't have the Disarm skill.|n")
            return

        if not char.db.in_combat:
            char.msg("|rYou can only disarm in combat.|n")
            return

        ready, remaining = check_cooldown(char, "disarm")
        if not ready:
            char.msg(f"|rWait {remaining}s before attempting to disarm again.|n")
            return

        target = char.search(target_name, location=char.location)
        if not target:
            return
        if target is char:
            char.msg("You can't disarm yourself.")
            return

        wielded = getattr(target.db, "wielded", None) or {}
        weapon = wielded.get("main_hand")
        if not weapon:
            char.msg(f"|r{target.key} isn't wielding anything to disarm.|n")
            return

        set_cooldown(char, "disarm")

        if disarm_check(char, target):
            wielded["main_hand"] = None
            target.db.wielded = wielded
            weapon.move_to(char.location, quiet=True)
            tick_skill_use(char, "disarm")
            char.msg(f"|G{target.key}'s {weapon.key} clatters to the floor!|n")
            target.msg(f"|r{char.key} knocks {weapon.key} from your hand!|n")
            char.location.msg_contents(
                f"|Y{char.key} disarms {target.key}!|n", exclude=[char, target]
            )
        else:
            char.msg(f"|r{target.key} maintains their grip.|n")
            target.msg(f"|x{char.key} attempts to disarm you but fails.|n")


# ---------------------------------------------------------------------------
# CmdSetTrap — place a trap
# ---------------------------------------------------------------------------

class CmdSetTrap(Command):
    """
    Set a trap in the current room.

    Usage:
      settrap <snare|alarm|spike>

    Requires the Traps skill.
    """

    key = "settrap"
    locks = "cmd:all()"
    help_category = "Skills"

    _TRAP_TYPES = {
        "snare": {"difficulty": 10, "damage": "0", "desc": "slows movement"},
        "alarm": {"difficulty": 8, "damage": "0", "desc": "alerts nearby NPCs"},
        "spike": {"difficulty": 12, "damage": "1d6", "desc": "deals piercing damage"},
    }

    def func(self):
        char = self.caller
        if not has_skill(char, "traps"):
            char.msg("|rYou don't have the Traps skill.|n")
            return

        if char.db.in_combat:
            char.msg("|rYou can't set traps while fighting!|n")
            return

        if not self.args:
            char.msg("Usage: settrap <snare|alarm|spike>")
            return

        trap_type = self.args.strip().lower()
        if trap_type not in self._TRAP_TYPES:
            char.msg(f"|rUnknown trap type. Choose: {', '.join(self._TRAP_TYPES.keys())}|n")
            return

        if getattr(char.location.db, "has_trap", False):
            char.msg("|rThere is already a trap here.|n")
            return

        trap_info = self._TRAP_TYPES[trap_type]
        if not trap_check(char, trap_info["difficulty"] - 5):
            char.msg("|rYou fumble with the trap components and fail to set it.|n")
            return

        char.location.db.has_trap = True
        char.location.db.trap_type = trap_type
        char.location.db.trap_difficulty = trap_info["difficulty"]
        char.location.db.trap_damage = trap_info["damage"]
        char.location.db.trap_discovered = False
        tick_skill_use(char, "traps")
        char.msg(f"|gYou set a {trap_type} trap. ({trap_info['desc']})|n")


# ---------------------------------------------------------------------------
# CmdBattleCry — warrior party buff
# ---------------------------------------------------------------------------

class CmdBattleCry(Command):
    """
    Let out a battle cry that fills your allies with fighting spirit.

    Usage:
      battlecry

    Requires the Battle Cry skill. Must have allies in the room.
    Grants +5 accuracy per skill level to all allies for 3 rounds.
    """

    key = "battlecry"
    aliases = ["battle cry", "warcry"]
    locks = "cmd:all()"
    help_category = "Skills"

    def func(self):
        char = self.caller
        if not has_skill(char, "battle_cry"):
            char.msg("|rYou don't have the Battle Cry skill.|n")
            return

        if not char.db.in_combat:
            char.msg("|rYou can only use battle cry in combat.|n")
            return

        ready, remaining = check_cooldown(char, "battle_cry")
        if not ready:
            char.msg(f"|rWait {remaining}s before using battle cry again.|n")
            return

        # Find allies (same faction) in combat
        script = char.db.in_combat
        combatants = getattr(script, "ndb", None)
        comb_dict = getattr(combatants, "combatants", None) or {} if combatants else {}
        my_faction = getattr(char.db, "faction", "player")
        allies = [c for c, s in comb_dict.items() if s["faction"] == my_faction and c is not char]

        if not allies:
            char.msg("|rThere are no allies in this fight to inspire.|n")
            return

        bonus = battle_cry_bonus(char)
        set_cooldown(char, "battle_cry")
        tick_skill_use(char, "battle_cry")

        char.msg(f"|RYOUR BATTLE CRY ECHOES THROUGH THE ROOM!|n")
        char.location.msg_contents(
            f"|R{char.key} lets out a thunderous battle cry!|n", exclude=[char]
        )
        for ally in allies:
            ally.db.battlecry_bonus = (getattr(ally.db, "battlecry_bonus", 0) or 0) + 3
            ally.msg(f"|Y{char.key}'s battle cry fills you with courage! (+{bonus} accuracy for 3 rounds)|n")


# ---------------------------------------------------------------------------
# CmdForm — Mystic unarmed stance
# ---------------------------------------------------------------------------

class CmdForm(Command):
    """
    Adopt a Mystic unarmed combat stance.

    Usage:
      form tiger     — damage-focused stance
      form crane     — balanced stance
      form serpent   — accuracy-focused stance
      form none      — leave all stances

    Requires the Unarmed Forms skill.
    """

    key = "form"
    locks = "cmd:all()"
    help_category = "Skills"

    _FORMS = {"tiger", "crane", "serpent", "none"}
    _FORM_DESC = {
        "tiger":   "You settle into the |RTiger stance|n — aggressive and powerful.",
        "crane":   "You adopt the |WCrane stance|n — balanced and watchful.",
        "serpent": "You flow into the |GSerpent stance|n — fluid and precise.",
        "none":    "You relax from your combat stance.",
    }

    def func(self):
        char = self.caller
        if not has_skill(char, "unarmed_forms"):
            char.msg("|rYou don't have the Unarmed Forms skill.|n")
            return

        if not self.args:
            current = char.db.active_form or "none"
            char.msg(f"Current stance: |W{current}|n. Usage: form <tiger|crane|serpent|none>")
            return

        form = self.args.strip().lower()
        if form not in self._FORMS:
            char.msg(f"|rUnknown stance. Choose: {', '.join(sorted(self._FORMS))}|n")
            return

        char.db.active_form = None if form == "none" else form
        char.msg(self._FORM_DESC[form])
        char.location.msg_contents(
            f"|x{char.key} shifts into a new combat stance.|n", exclude=[char]
        )
