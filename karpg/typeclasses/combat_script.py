"""
Combat Script

Evennia DefaultScript that manages a single turn-based combat encounter.
One script per room. Handles initiative, turn order, action resolution,
victory conditions, and all combat display output.

Uses MajorMUD-inspired colour scheme with Evennia markup.
"""

import random

from evennia import DefaultScript
from evennia.utils.utils import inherits_from
from evennia.utils import delay

from world.combat_engine import (
    roll_initiative,
    resolve_attack,
    resolve_spell_attack,
    resolve_spell_save,
    resolve_magic_missile,
    roll_death_save,
    get_mod,
    hp_bar,
    hp_colour,
    parse_dice,
    roll_dice,
    roll_d20,
    ability_mod,
)
from world.conditions import (
    apply_condition,
    remove_condition,
    has_condition,
    tick_conditions,
    get_condition_level,
)
from world.spells import get_spell


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

_SEP = "|x" + "-" * 60 + "|n"
_THICK_SEP = "|x" + "=" * 60 + "|n"


def _name(combatant, faction=None):
    """Return a colour-coded name based on faction."""
    if faction == "hostile":
        return f"|M{combatant.key}|n"
    return f"|W{combatant.key}|n"


def _faction_of(script, combatant):
    """Look up faction from the script's factions dict."""
    factions = script.db.factions or {}
    return factions.get(combatant.id, "unknown")


def _is_pc(combatant):
    """Return True if combatant is a player character."""
    return inherits_from(combatant, "typeclasses.characters.Character")


def _is_npc(combatant):
    """Return True if combatant is an NPC."""
    return inherits_from(combatant, "typeclasses.npcs.NPC")


def _death_save_display(successes, failures):
    """Format death save tracker: filled/empty circles."""
    s_display = "|G●|n" * successes + "|G○|n" * (3 - successes)
    f_display = "|R●|n" * failures + "|R○|n" * (3 - failures)
    return f"  Saves [{s_display}]  Fails [{f_display}]"


# ---------------------------------------------------------------------------
# CombatScript
# ---------------------------------------------------------------------------

class CombatScript(DefaultScript):
    """
    Manages a single combat encounter in a room.

    Created dynamically when combat starts. Persists across server reloads.
    Removed when combat ends.
    """

    def at_script_creation(self):
        """Set default db attributes."""
        self.key = "combat"
        self.desc = "Turn-based combat encounter"
        self.persistent = True
        self.interval = 0  # no repeating tick — turn-based, not ticker-based

        self.db.combatants = []
        self.db.initiative_order = []
        self.db.round = 1
        self.db.current_turn_idx = 0
        self.db.turn_log = []
        self.db.active = False
        self.db.factions = {}

    # ------------------------------------------------------------------
    # Room broadcast
    # ------------------------------------------------------------------

    def _broadcast(self, msg, exclude=None):
        """Send a message to the room this script is attached to."""
        room = self.obj
        if room:
            room.msg_contents(msg, exclude=exclude or [])

    def _msg_combatant(self, combatant, msg):
        """Send a message to a single combatant."""
        combatant.msg(msg)

    # ------------------------------------------------------------------
    # Combat lifecycle
    # ------------------------------------------------------------------

    def begin_combat(self, initiator, targets):
        """
        Start a new combat encounter.

        Parameters:
            initiator — the Character/NPC who started combat
            targets   — list of Character/NPC objects being attacked
        """
        self.db.active = True
        self.db.round = 1
        self.db.turn_log = []
        self.db.combatants = []
        self.db.initiative_order = []
        self.db.factions = {}

        # Determine factions
        initiator_faction = getattr(initiator.db, "faction", "player")

        # Add initiator side
        all_combatants = [initiator]
        self.db.factions[initiator.id] = initiator_faction

        # Add targets
        for t in targets:
            if t not in all_combatants:
                all_combatants.append(t)
                t_faction = getattr(t.db, "faction", "hostile")
                self.db.factions[t.id] = t_faction

        self.db.combatants = list(all_combatants)

        # Roll initiative for everyone
        init_results = []
        for c in all_combatants:
            total, d20 = roll_initiative(c)
            dex_score = (c.db.ability_scores or {}).get("dex", 10)
            init_results.append((c, total, d20, dex_score))

        # Sort: descending total, then by DEX score, then random tiebreak
        init_results.sort(key=lambda x: (x[1], x[2], random.random()),
                          reverse=True)

        self.db.initiative_order = [(c, total) for c, total, _, _ in init_results]

        # Mark all combatants as in combat
        for c in all_combatants:
            c.db.in_combat = self.id

        # Broadcast initiative banner
        self._broadcast_initiative_banner(init_results)

        # Start first turn
        self.start_turn(0)

    def _broadcast_initiative_banner(self, init_results):
        """Display the initiative roll results."""
        lines = []
        lines.append("")
        lines.append("|y*" + "─" * 58 + "*|n")
        lines.append("|y│|n" + "  |Y⚔  COMBAT BEGINS  ⚔|n".center(68) + "|y│|n")
        lines.append("|y*" + "─" * 58 + "*|n")
        lines.append("")
        lines.append("  |wInitiative Order:|n")

        for i, (c, total, d20, dex_score) in enumerate(init_results):
            faction = _faction_of(self, c)
            name = _name(c, faction)
            marker = " |Y►|n " if i == 0 else "   "
            lines.append(
                f"{marker}{name} |x(d20={d20} + DEX {ability_mod(dex_score):+d}"
                f" = |w{total}|x)|n"
            )

        lines.append("")
        lines.append(_SEP)
        self._broadcast("\n".join(lines))

    # ------------------------------------------------------------------
    # Combatant management
    # ------------------------------------------------------------------

    def add_combatant(self, combatant, faction):
        """Add a new combatant mid-combat."""
        if combatant in (self.db.combatants or []):
            return

        self.db.combatants.append(combatant)
        self.db.factions[combatant.id] = faction
        combatant.db.in_combat = self.id

        total, d20 = roll_initiative(combatant)

        # Insert into initiative order at the correct position
        order = self.db.initiative_order or []
        inserted = False
        for i, (c, t) in enumerate(order):
            if total > t:
                order.insert(i, (combatant, total))
                inserted = True
                break
        if not inserted:
            order.append((combatant, total))
        self.db.initiative_order = order

        name = _name(combatant, faction)
        self._broadcast(
            f"\n|w{name} |whas joined the battle!|n |x(initiative {total})|n"
        )

    def remove_combatant(self, combatant):
        """Remove a combatant from the encounter."""
        combatants = self.db.combatants or []
        if combatant in combatants:
            combatants.remove(combatant)
            self.db.combatants = combatants

        order = self.db.initiative_order or []
        current_idx = self.db.current_turn_idx or 0
        removed_idx = None

        new_order = []
        for i, (c, t) in enumerate(order):
            if c.id == combatant.id:
                removed_idx = i
            else:
                new_order.append((c, t))
        self.db.initiative_order = new_order

        self.db.factions.pop(combatant.id, None)
        combatant.db.in_combat = None

        # If it was their turn, advance
        if removed_idx is not None and removed_idx == current_idx:
            # Adjust index since we removed an entry
            if current_idx >= len(new_order):
                self.end_round()
            else:
                self.start_turn(current_idx)
        elif removed_idx is not None and removed_idx < current_idx:
            self.db.current_turn_idx = max(0, current_idx - 1)

        # Check win condition
        if self.db.active:
            self.check_victory()

    # ------------------------------------------------------------------
    # Turn management
    # ------------------------------------------------------------------

    def start_turn(self, idx):
        """Begin a combatant's turn."""
        order = self.db.initiative_order or []
        if not order:
            self.end_combat([])
            return

        if idx >= len(order):
            self.end_round()
            return

        self.db.current_turn_idx = idx
        self.db.turn_log = []
        combatant, _ = order[idx]

        # Display turn banner
        self._display_turn_banner(combatant)

        # Start-of-turn condition ticks (e.g. ongoing damage)
        # (Conditions tick at end of turn in 5e, but we check for
        #  incapacitating effects at start)

        # Check unconscious → death save
        if has_condition(combatant, "unconscious"):
            self._handle_death_save(combatant)
            return

        # Check incapacitated / stunned / paralyzed
        if self._is_incapacitated(combatant):
            faction = _faction_of(self, combatant)
            name = _name(combatant, faction)
            self._broadcast(f"\n  {name} |yis incapacitated and loses their turn!|n")
            self.end_turn()
            return

        # NPC AI
        if _is_npc(combatant):
            delay(0.5, self.ai_act, combatant)
            return

        # Player prompt
        self._msg_combatant(
            combatant,
            "\n|Y► Your turn!|n Use: |wattack <target>|n, "
            "|wcast <spell> [at <target>]|n, |wpass|n, or |wflee|n"
        )

    def _display_turn_banner(self, active_combatant):
        """Show round info, whose turn it is, and HP roster."""
        order = self.db.initiative_order or []
        rnd = self.db.round or 1

        lines = []
        lines.append("")
        lines.append(_SEP)
        faction = _faction_of(self, active_combatant)
        active_name = _name(active_combatant, faction)
        lines.append(f"  |y Round {rnd}|n  —  {active_name}|w's turn|n")
        lines.append(_SEP)

        for c, init_total in order:
            c_faction = _faction_of(self, c)
            c_name = _name(c, c_faction)
            hp = c.db.hp if c.db.hp is not None else 0
            hp_max = c.db.hp_max if c.db.hp_max is not None else 1
            bar = hp_bar(hp, hp_max)
            colour = hp_colour(hp, hp_max)

            marker = " |Y►|n" if c.id == active_combatant.id else "  "
            cond_str = ""
            conditions = c.db.conditions or []
            if conditions:
                cond_names = [cd.get("name", "") for cd in conditions]
                cond_str = " |y[" + ", ".join(cond_names) + "]|n"

            lines.append(
                f"{marker} {c_name}  {bar} "
                f"{colour}{hp}/{hp_max}|n{cond_str}"
            )

        lines.append(_SEP)
        self._broadcast("\n".join(lines))

    def _is_incapacitated(self, combatant):
        """Return True if combatant cannot take actions."""
        for cond in (combatant.db.conditions or []):
            cond_name = cond.get("name", "")
            if cond_name in ("incapacitated", "stunned", "paralyzed",
                              "petrified"):
                return True
            if cond_name == "exhaustion" and cond.get("level", 1) >= 6:
                return True
        return False

    def _handle_death_save(self, combatant):
        """Process a death saving throw for an unconscious PC."""
        faction = _faction_of(self, combatant)
        name = _name(combatant, faction)
        result = roll_death_save(combatant)

        lines = []
        lines.append(f"\n  |Y{combatant.key} makes a death saving throw...|n")

        if result.is_nat20:
            lines.append(
                f"  |Y★ Natural 20! ★|n {name} |Gregains consciousness "
                f"with 1 HP!|n"
            )
            remove_condition(combatant, "unconscious")
            remove_condition(combatant, "prone")
        elif result.is_nat1:
            lines.append(
                f"  |R★ Natural 1! ★|n Two failures!"
            )
            lines.append(_death_save_display(result.successes, result.failures))
        elif result.success:
            lines.append(
                f"  |Gd20 = {result.roll}|n — |GSuccess|n"
            )
            lines.append(_death_save_display(result.successes, result.failures))
        else:
            lines.append(
                f"  |Rd20 = {result.roll}|n — |RFailure|n"
            )
            lines.append(_death_save_display(result.successes, result.failures))

        if result.stabilized and not result.is_nat20:
            lines.append(f"\n  |G{combatant.key} has stabilized!|n")

        if result.died:
            lines.append(f"\n  |R══ {combatant.key} has died. ══|n")
            self._handle_pc_death(combatant)

        self._broadcast("\n".join(lines))
        self.end_turn()

    def _handle_pc_death(self, combatant):
        """Handle a player character dying."""
        remove_condition(combatant, "unconscious")
        self.remove_combatant(combatant)

    # ------------------------------------------------------------------
    # Action processing
    # ------------------------------------------------------------------

    def receive_action(self, combatant, action_type, **kwargs):
        """
        Process a combat action from a combatant.

        Parameters:
            combatant   — the acting combatant
            action_type — "attack", "offhand_attack", "cast", "pass", "flee"
            **kwargs    — action-specific arguments
        """
        order = self.db.initiative_order or []
        idx = self.db.current_turn_idx or 0

        if idx >= len(order):
            self._msg_combatant(combatant, "|rCombat error: invalid turn index.|n")
            return

        current, _ = order[idx]
        if current.id != combatant.id:
            self._msg_combatant(combatant, "|rIt's not your turn!|n")
            return

        if self._is_incapacitated(combatant):
            self._msg_combatant(combatant, "|rYou are incapacitated!|n")
            return

        if action_type == "attack":
            self._action_attack(combatant, **kwargs)
        elif action_type == "offhand_attack":
            self._action_offhand_attack(combatant, **kwargs)
        elif action_type == "cast":
            self._action_cast(combatant, **kwargs)
        elif action_type == "pass":
            self._action_pass(combatant)
        elif action_type == "flee":
            self.attempt_flee(combatant)
            return  # flee handles its own end_turn
        else:
            self._msg_combatant(combatant,
                                f"|rUnknown action: {action_type}|n")
            return

        if action_type != "flee":
            self.end_turn()

    # --- Attack ---

    def _action_attack(self, combatant, target=None, weapon=None, **kwargs):
        """Resolve a main-hand weapon attack."""
        if target is None:
            self._msg_combatant(combatant, "|rYou must specify a target.|n")
            return

        # Determine weapon
        if weapon is None:
            wielded = combatant.db.wielded or {}
            weapon = wielded.get("main_hand")

        # Check dodge advantage/disadvantage
        advantage = kwargs.get("advantage", False)
        disadvantage = kwargs.get("disadvantage", False)

        # Check if target is dodging
        if getattr(target.ndb, "dodging", False):
            disadvantage = True

        result = resolve_attack(combatant, target, weapon=weapon,
                                advantage=advantage,
                                disadvantage=disadvantage)

        self._display_attack_result(result, combatant, target)

        if result.is_hit:
            died = self.apply_damage(target, result.final_damage,
                                     result.damage_type, combatant)
            self.db.turn_log.append(
                f"{combatant.key} hit {target.key} for {result.final_damage} "
                f"{result.damage_type} damage"
            )
        else:
            self.db.turn_log.append(
                f"{combatant.key} missed {target.key}"
            )

    def _action_offhand_attack(self, combatant, target=None, **kwargs):
        """Resolve an off-hand bonus action attack (no ability mod to damage)."""
        if target is None:
            self._msg_combatant(combatant, "|rYou must specify a target.|n")
            return

        wielded = combatant.db.wielded or {}
        off_weapon = wielded.get("off_hand")
        if off_weapon is None:
            self._msg_combatant(
                combatant, "|rYou have nothing in your off hand.|n"
            )
            return

        # Off-hand attacks don't add ability modifier to damage
        disadvantage = getattr(target.ndb, "dodging", False)
        result = resolve_attack(combatant, target, weapon=off_weapon,
                                disadvantage=disadvantage)

        # Zero out the ability modifier from damage
        result.damage_total = max(0, result.damage_total - result.damage_bonus)
        result.damage_bonus = 0
        result.final_damage = max(0, result.final_damage - result.damage_bonus)
        # Recalculate final with resistances
        final = result.damage_total
        if result.immunity_applied:
            final = 0
        elif result.vulnerability_applied:
            final = final * 2
        elif result.resistance_applied:
            final = final // 2
        result.final_damage = max(0, final)

        self._broadcast(f"\n  |y— Bonus Action: Off-hand Attack —|n")
        self._display_attack_result(result, combatant, target)

        if result.is_hit:
            self.apply_damage(target, result.final_damage,
                              result.damage_type, combatant)
            self.db.turn_log.append(
                f"{combatant.key} off-hand hit {target.key} for "
                f"{result.final_damage} {result.damage_type} damage"
            )

    def _display_attack_result(self, result, attacker, defender):
        """Format and broadcast an attack result with MajorMUD colours."""
        a_faction = _faction_of(self, attacker)
        d_faction = _faction_of(self, defender)
        a_name = _name(attacker, a_faction)
        d_name = _name(defender, d_faction)

        lines = []

        # Swing line
        lines.append(
            f"\n  |c{attacker.key} swings {result.weapon_name} at "
            f"{defender.key}!|n"
        )

        # Roll breakdown
        rolls_str = ", ".join(str(r) for r in result.d20_rolls)
        lines.append(
            f"  |x[d20: {rolls_str}] + {result.attack_bonus} = "
            f"{result.attack_total} vs AC {result.target_ac}|n"
        )

        if result.is_miss:
            lines.append(f"  |x— Miss —|n")
        elif result.is_crit:
            lines.append(f"  |R★ CRITICAL HIT! ★|n")
            dmg_rolls_str = ", ".join(str(r) for r in result.damage_rolls)
            lines.append(
                f"  |RDamage: [{dmg_rolls_str}] + {result.damage_bonus} = "
                f"{result.final_damage} {result.damage_type}|n"
            )
        else:
            lines.append(f"  |G— Hit! —|n")
            dmg_rolls_str = ", ".join(str(r) for r in result.damage_rolls)
            lines.append(
                f"  |RDamage: [{dmg_rolls_str}] + {result.damage_bonus} = "
                f"{result.final_damage} {result.damage_type}|n"
            )

        if result.resistance_applied:
            lines.append(f"  |x(Resistance: damage halved)|n")
        if result.vulnerability_applied:
            lines.append(f"  |R(Vulnerability: damage doubled!)|n")
        if result.immunity_applied:
            lines.append(f"  |x(Immune to {result.damage_type}!)|n")

        self._broadcast("\n".join(lines))

    # --- Cast ---

    def _action_cast(self, combatant, spell=None, targets=None, **kwargs):
        """Resolve a spell cast."""
        if spell is None:
            self._msg_combatant(combatant, "|rYou must specify a spell.|n")
            return

        spell_name = spell.get("key", "unknown")
        spell_level = spell.get("level", 0)
        spell_type = spell.get("spell_type", "utility")
        special = spell.get("special")

        # Check and consume spell slot (cantrips are free)
        if spell_level > 0:
            slots = combatant.db.spell_slots or {}
            slot_key = str(spell_level)
            remaining = slots.get(slot_key, 0)
            if remaining <= 0:
                self._msg_combatant(
                    combatant,
                    f"|rNo level {spell_level} spell slots remaining!|n"
                )
                return
            slots[slot_key] = remaining - 1
            combatant.db.spell_slots = slots

        a_faction = _faction_of(self, combatant)
        a_name = _name(combatant, a_faction)

        # --- Special: magic missile ---
        if special == "magic_missile":
            if not targets:
                self._msg_combatant(combatant, "|rYou must specify a target.|n")
                return
            target = targets[0]
            mm_result = resolve_magic_missile(combatant, target)
            d_faction = _faction_of(self, target)
            d_name = _name(target, d_faction)

            lines = []
            lines.append(
                f"\n  |c{combatant.key} casts Magic Missile at "
                f"{target.key}!|n"
            )
            for i, dart in enumerate(mm_result["darts"], 1):
                lines.append(
                    f"  |R  Dart {i}: d4={dart['roll']} + 1 = "
                    f"{dart['damage']} force|n"
                )
            lines.append(
                f"  |RTotal damage: {mm_result['total_damage']} force|n"
            )
            self._broadcast("\n".join(lines))
            self.apply_damage(target, mm_result["total_damage"], "force",
                              combatant)
            self.db.turn_log.append(
                f"{combatant.key} cast magic missile on {target.key} for "
                f"{mm_result['total_damage']} force damage"
            )
            return

        # --- Special: cure wounds ---
        if special == "cure_wounds":
            if not targets:
                targets = [combatant]  # self-heal by default
            target = targets[0]
            heal_dice = spell.get("damage_dice", "2d8")
            num, sides = parse_dice(heal_dice)
            rolls = roll_dice(num, sides)
            spell_mod = get_mod(combatant, spell.get("attack_stat", "int"))
            healing = sum(rolls) + spell_mod

            old_hp = target.db.hp or 0
            hp_max = target.db.hp_max or 1
            target.db.hp = min(hp_max, old_hp + healing)
            new_hp = target.db.hp

            d_faction = _faction_of(self, target)
            d_name = _name(target, d_faction)
            rolls_str = ", ".join(str(r) for r in rolls)

            self._broadcast(
                f"\n  |c{combatant.key} casts Cure Wounds on {target.key}!|n\n"
                f"  |G  Healing: [{rolls_str}] + {spell_mod} = {healing}|n\n"
                f"  |G  {target.key}: {old_hp} → {new_hp} HP|n"
            )

            # Remove unconscious if healed above 0
            if old_hp <= 0 and new_hp > 0:
                remove_condition(target, "unconscious")
                remove_condition(target, "prone")
                target.db.death_saves = {"successes": 0, "failures": 0}
                self._broadcast(
                    f"  |G{target.key} regains consciousness!|n"
                )

            self.db.turn_log.append(
                f"{combatant.key} healed {target.key} for {healing} HP"
            )
            return

        # --- Spell attack ---
        if spell_type == "attack":
            if not targets:
                self._msg_combatant(combatant, "|rYou must specify a target.|n")
                return

            # Scorching ray: 3 separate attack rolls
            if special == "scorching_ray":
                self._broadcast(
                    f"\n  |c{combatant.key} casts Scorching Ray!|n"
                )
                for i in range(3):
                    target = targets[i] if i < len(targets) else targets[0]
                    sr = resolve_spell_attack(combatant, target, spell)
                    d_faction = _faction_of(self, target)
                    d_name = _name(target, d_faction)

                    rolls_str = ", ".join(str(r) for r in sr.d20_rolls)
                    self._broadcast(
                        f"  |c  Ray {i+1} → {target.key}|n "
                        f"|x[d20: {rolls_str}] + {sr.attack_bonus} = "
                        f"{sr.attack_total}|n"
                    )
                    if sr.is_hit and sr.target_results:
                        tr = sr.target_results[0]
                        dr = ", ".join(str(r) for r in tr["damage_rolls"])
                        self._broadcast(
                            f"  |G  Hit!|n |R[{dr}] = "
                            f"{tr['damage']} {tr['damage_type']}|n"
                        )
                        self.apply_damage(target, tr["damage"],
                                          tr["damage_type"], combatant)
                    else:
                        self._broadcast(f"  |x  Miss|n")
                return

            target = targets[0]
            sr = resolve_spell_attack(combatant, target, spell)
            self._display_spell_attack_result(sr, combatant, target)

            if sr.is_hit and sr.target_results:
                tr = sr.target_results[0]
                self.apply_damage(target, tr["damage"], tr["damage_type"],
                                  combatant)
                self.db.turn_log.append(
                    f"{combatant.key} hit {target.key} with {spell_name} "
                    f"for {tr['damage']} {tr['damage_type']} damage"
                )
            else:
                self.db.turn_log.append(
                    f"{combatant.key} missed {target.key} with {spell_name}"
                )

            # Apply condition on hit if applicable
            if sr.is_hit and spell.get("applies_condition"):
                apply_condition(target, spell["applies_condition"],
                                duration=10)
                self._broadcast(
                    f"  |y{target.key} is now {spell['applies_condition']}!|n"
                )
            return

        # --- Spell save ---
        if spell_type == "save":
            if not targets:
                self._msg_combatant(combatant, "|rYou must specify a target.|n")
                return

            # Handle toll the dead special: 1d12 if target is wounded
            if special == "toll_the_dead" and targets:
                target = targets[0]
                hp = target.db.hp or 0
                hp_max = target.db.hp_max or 1
                if hp < hp_max:
                    spell = dict(spell)  # copy to avoid mutating registry
                    spell["damage_dice"] = "1d12"

            sr = resolve_spell_save(combatant, targets, spell)
            self._display_spell_save_result(sr, combatant)

            for tr in sr.target_results:
                target = tr["target"]
                if tr["damage"] > 0:
                    self.apply_damage(target, tr["damage"],
                                      tr["damage_type"], combatant)

                # Apply condition on failed save
                if not tr["saved"] and spell.get("applies_condition"):
                    apply_condition(target, spell["applies_condition"],
                                    duration=10)
                    d_faction = _faction_of(self, target)
                    d_name = _name(target, d_faction)
                    self._broadcast(
                        f"  |y{target.key} is now "
                        f"{spell['applies_condition']}!|n"
                    )

            log_parts = []
            for tr in sr.target_results:
                saved = "saved" if tr["saved"] else "failed"
                log_parts.append(
                    f"{tr['target'].key} ({saved}, {tr['damage']} dmg)"
                )
            self.db.turn_log.append(
                f"{combatant.key} cast {spell_name}: " + ", ".join(log_parts)
            )
            return

        # --- Utility (counterspell, etc.) ---
        self._broadcast(
            f"\n  |c{combatant.key} casts {spell_name}.|n"
        )
        self.db.turn_log.append(f"{combatant.key} cast {spell_name}")

    def _display_spell_attack_result(self, sr, caster, target):
        """Format and broadcast a spell attack result."""
        a_faction = _faction_of(self, caster)
        d_faction = _faction_of(self, target)

        lines = []
        lines.append(
            f"\n  |c{caster.key} casts {sr.spell_name} at {target.key}!|n"
        )

        rolls_str = ", ".join(str(r) for r in sr.d20_rolls)
        target_ac = target.db.ac or 10
        lines.append(
            f"  |x[d20: {rolls_str}] + {sr.attack_bonus} = "
            f"{sr.attack_total} vs AC {target_ac}|n"
        )

        if not sr.is_hit:
            lines.append(f"  |x— Miss —|n")
        elif sr.is_crit:
            lines.append(f"  |R★ CRITICAL HIT! ★|n")
            if sr.target_results:
                tr = sr.target_results[0]
                dr = ", ".join(str(r) for r in tr["damage_rolls"])
                lines.append(
                    f"  |RDamage: [{dr}] = {tr['damage']} "
                    f"{tr['damage_type']}|n"
                )
        else:
            lines.append(f"  |G— Hit! —|n")
            if sr.target_results:
                tr = sr.target_results[0]
                dr = ", ".join(str(r) for r in tr["damage_rolls"])
                lines.append(
                    f"  |RDamage: [{dr}] = {tr['damage']} "
                    f"{tr['damage_type']}|n"
                )

        self._broadcast("\n".join(lines))

    def _display_spell_save_result(self, sr, caster):
        """Format and broadcast a spell save result."""
        a_faction = _faction_of(self, caster)
        a_name = _name(caster, a_faction)

        lines = []
        target_names = ", ".join(
            tr["target"].key for tr in sr.target_results
        )
        lines.append(
            f"\n  |c{caster.key} casts {sr.spell_name}!|n  "
            f"|x(DC {sr.save_dc} {sr.save_stat.upper()} save)|n"
        )

        for tr in sr.target_results:
            t = tr["target"]
            d_faction = _faction_of(self, t)
            d_name = _name(t, d_faction)
            saved_str = "|GSaved|n" if tr["saved"] else "|RFailed|n"
            dr = ", ".join(str(r) for r in tr["damage_rolls"])
            lines.append(
                f"  {d_name}: |xd20={tr['save_roll']} "
                f"(total {tr['save_total']})|n → {saved_str}"
                f"  |R{tr['damage']} {tr['damage_type']}|n"
            )

        self._broadcast("\n".join(lines))

    # --- Pass (Dodge) ---

    def _action_pass(self, combatant):
        """Take the Dodge action — attackers have disadvantage until next turn."""
        combatant.ndb.dodging = True
        faction = _faction_of(self, combatant)
        name = _name(combatant, faction)
        self._broadcast(
            f"\n  {name} |ytakes the Dodge action.|n "
            f"|x(Attacks against them have disadvantage this round)|n"
        )
        self.db.turn_log.append(f"{combatant.key} took the Dodge action")

    # ------------------------------------------------------------------
    # End of turn / round
    # ------------------------------------------------------------------

    def end_turn(self):
        """Finish the current combatant's turn and advance."""
        order = self.db.initiative_order or []
        idx = self.db.current_turn_idx or 0

        if idx < len(order):
            combatant, _ = order[idx]
            # End-of-turn condition ticks
            expired = tick_conditions(combatant)
            if expired:
                faction = _faction_of(self, combatant)
                name = _name(combatant, faction)
                for cond_name in expired:
                    self._broadcast(
                        f"  |w{combatant.key} is no longer {cond_name}.|n"
                    )

        # Check victory before advancing
        if self.check_victory():
            return

        # Advance to next alive, active combatant
        next_idx = (idx + 1)
        if next_idx >= len(order):
            self.end_round()
        else:
            self.start_turn(next_idx)

    def end_round(self):
        """Wrap up the current round and start the next one."""
        self.db.round = (self.db.round or 1) + 1

        # Display round summary with HP roster
        self._display_round_summary()

        # Clear dodge flags
        for c in (self.db.combatants or []):
            if hasattr(c, "ndb"):
                c.ndb.dodging = False

        # Check exhaustion level 6 deaths
        for c in list(self.db.combatants or []):
            if get_condition_level(c, "exhaustion") >= 6:
                faction = _faction_of(self, c)
                name = _name(c, faction)
                self._broadcast(
                    f"\n  |R══ {c.key} succumbs to exhaustion and dies. ══|n"
                )
                c.db.hp = 0
                if _is_npc(c):
                    self.remove_combatant(c)
                else:
                    self._handle_pc_death(c)

        if self.check_victory():
            return

        # Start new round
        self.start_turn(0)

    def _display_round_summary(self):
        """Show end-of-round HP bar roster for all combatants."""
        lines = []
        lines.append("")
        lines.append(_THICK_SEP)
        lines.append(f"  |w End of Round {(self.db.round or 2) - 1}|n")
        lines.append(_THICK_SEP)

        for c in (self.db.combatants or []):
            faction = _faction_of(self, c)
            c_name = _name(c, faction)
            hp = c.db.hp if c.db.hp is not None else 0
            hp_max = c.db.hp_max if c.db.hp_max is not None else 1
            bar = hp_bar(hp, hp_max)
            colour = hp_colour(hp, hp_max)

            cond_str = ""
            conditions = c.db.conditions or []
            if conditions:
                cond_names = [cd.get("name", "") for cd in conditions]
                cond_str = " |y[" + ", ".join(cond_names) + "]|n"

            lines.append(
                f"   {c_name}  {bar}  "
                f"{colour}{hp}/{hp_max}|n{cond_str}"
            )

        lines.append(_THICK_SEP)
        lines.append("")
        self._broadcast("\n".join(lines))

    # ------------------------------------------------------------------
    # Victory & end
    # ------------------------------------------------------------------

    def check_victory(self):
        """
        Check if combat should end.

        Returns True if combat has ended.
        """
        if not self.db.active:
            return True

        factions = self.db.factions or {}
        order = self.db.initiative_order or []

        # Gather alive factions
        alive_factions = set()
        for c, _ in order:
            hp = c.db.hp if c.db.hp is not None else 0
            if hp > 0 and not has_condition(c, "unconscious"):
                alive_factions.add(factions.get(c.id, "unknown"))

        if len(alive_factions) <= 1:
            # Determine winners
            winners = []
            for c, _ in order:
                hp = c.db.hp if c.db.hp is not None else 0
                if hp > 0:
                    winners.append(c)
            self.end_combat(winners)
            return True

        return False

    def end_combat(self, winners):
        """
        End the combat encounter. Award XP, clean up.

        Parameters:
            winners — list of surviving combatants
        """
        self.db.active = False
        factions = self.db.factions or {}

        lines = []
        lines.append("")
        lines.append("|y*" + "─" * 58 + "*|n")
        lines.append("|y│|n" + "  |Y⚔  COMBAT ENDS  ⚔|n".center(68) + "|y│|n")
        lines.append("|y*" + "─" * 58 + "*|n")

        if winners:
            winner_faction = factions.get(winners[0].id, "unknown")
            winner_names = ", ".join(w.key for w in winners)
            lines.append(f"\n  |wVictors: {winner_names}|n")

            # Calculate XP from defeated enemies
            total_xp = 0
            for c in (self.db.combatants or []):
                c_faction = factions.get(c.id, "unknown")
                if c_faction != winner_faction:
                    xp_val = getattr(c.db, "xp_value", 0) or 0
                    total_xp += xp_val

            if total_xp > 0:
                # Split XP among winning players
                player_winners = [w for w in winners if _is_pc(w)]
                if player_winners:
                    xp_each = total_xp // len(player_winners)
                    for pw in player_winners:
                        pw.db.xp = (pw.db.xp or 0) + xp_each
                        lines.append(
                            f"  |w{pw.key} gains {xp_each} XP.|n"
                        )
        else:
            lines.append(f"\n  |wNo victors.|n")

        lines.append("")
        self._broadcast("\n".join(lines))

        # Clean up all combatants
        for c in (self.db.combatants or []):
            c.db.in_combat = None
            if hasattr(c, "ndb"):
                c.ndb.dodging = False

        # Remove the script
        self.stop()

    # ------------------------------------------------------------------
    # Damage application
    # ------------------------------------------------------------------

    def apply_damage(self, target, amount, damage_type, source):
        """
        Apply damage to a target. Handle dropping to 0 HP.

        Returns True if the target dropped to 0 or below.
        """
        if amount <= 0:
            return False

        old_hp = target.db.hp if target.db.hp is not None else 0
        hp_max = target.db.hp_max if target.db.hp_max is not None else 1

        new_hp = old_hp - amount
        target.db.hp = max(0, new_hp) if _is_pc(target) else new_hp

        faction = _faction_of(self, target)
        t_name = _name(target, faction)
        old_colour = hp_colour(old_hp, hp_max)
        new_colour = hp_colour(max(0, new_hp), hp_max)

        self._broadcast(
            f"  {t_name}: {old_colour}{old_hp}|n → "
            f"{new_colour}{max(0, new_hp) if _is_pc(target) else new_hp}|n HP"
        )

        # Update threat table for NPCs
        if _is_npc(target) and hasattr(target, "at_attacked_by"):
            target.at_attacked_by(source, amount)

        if new_hp <= 0:
            if _is_npc(target):
                # NPC dies
                self._broadcast(
                    f"\n  |R══ {target.key} has died. ══|n"
                )
                if hasattr(target, "at_death"):
                    target.at_death(source)
                self.remove_combatant(target)
                return True
            else:
                # PC falls unconscious
                target.db.hp = 0
                target.db.death_saves = {"successes": 0, "failures": 0}
                apply_condition(target, "unconscious", duration=-1)
                apply_condition(target, "prone", duration=-1)
                self._broadcast(
                    f"\n  |Y{target.key} falls unconscious!|n"
                )
                return True

        return False

    # ------------------------------------------------------------------
    # NPC AI
    # ------------------------------------------------------------------

    def ai_act(self, npc):
        """
        Execute an NPC's turn based on its AI profile.

        Called after a short delay for natural pacing.
        """
        if not self.db.active:
            return

        order = self.db.initiative_order or []
        idx = self.db.current_turn_idx or 0
        if idx >= len(order):
            return
        current, _ = order[idx]
        if current.id != npc.id:
            return  # No longer this NPC's turn

        factions = self.db.factions or {}
        npc_faction = factions.get(npc.id, "hostile")
        ai_profile = getattr(npc.db, "ai_profile", "tactical") or "tactical"

        # Get living enemies
        enemies = []
        for c, _ in order:
            c_faction = factions.get(c.id, "unknown")
            if c_faction != npc_faction:
                c_hp = c.db.hp if c.db.hp is not None else 0
                if c_hp > 0 and not has_condition(c, "unconscious"):
                    enemies.append(c)

        if not enemies:
            self._action_pass(npc)
            self.end_turn()
            return

        # Check flee conditions first
        npc_hp = npc.db.hp if npc.db.hp is not None else 0
        npc_hp_max = npc.db.hp_max if npc.db.hp_max is not None else 1
        hp_ratio = npc_hp / npc_hp_max if npc_hp_max > 0 else 0

        if ai_profile == "cowardly" and hp_ratio < 0.5:
            self.attempt_flee(npc)
            return
        if ai_profile == "tactical" and hp_ratio < 0.25:
            int_mod = get_mod(npc, "int")
            if int_mod > -1:
                self.attempt_flee(npc)
                return

        # Select target
        target = self._ai_select_target(npc, enemies, ai_profile)

        # Determine weapon
        wielded = npc.db.wielded or {}
        weapon = wielded.get("main_hand")

        # Attack
        self.receive_action(npc, "attack", target=target, weapon=weapon)

        # Check for dual-wield bonus action (receive_action calls end_turn,
        # so we handle offhand before that by overriding the flow)
        # Actually, receive_action already calls end_turn. For dual-wield
        # NPCs we need to handle this differently. We'll check after main
        # attack but before end_turn by not calling receive_action for the
        # offhand — instead we call the method directly.

    def _ai_act_with_offhand(self, npc, target):
        """Check and execute off-hand attack for dual-wielding NPCs."""
        wielded = npc.db.wielded or {}
        off_weapon = wielded.get("off_hand")
        main_weapon = wielded.get("main_hand")

        # Only if dual wielding (off_hand is a different weapon from main)
        if (off_weapon is not None and main_weapon is not None
                and off_weapon != main_weapon):
            self._action_offhand_attack(npc, target=target)

    def _ai_select_target(self, npc, enemies, ai_profile):
        """Select a target based on AI profile."""
        if not enemies:
            return None

        if ai_profile == "berserker":
            # Attack highest HP target
            return max(enemies, key=lambda e: e.db.hp or 0)

        if ai_profile in ("tactical", "cowardly"):
            # Attack lowest HP target
            return min(enemies, key=lambda e: e.db.hp or 0)

        if ai_profile == "protective":
            # Target whoever attacked an ally last round
            threat_tables = {}
            factions = self.db.factions or {}
            npc_faction = factions.get(npc.id, "hostile")

            for c in (self.db.combatants or []):
                c_faction = factions.get(c.id, "unknown")
                if c_faction == npc_faction and _is_npc(c):
                    tt = getattr(c.db, "threat_table", None) or {}
                    for atk_id, dmg in tt.items():
                        threat_tables[atk_id] = (
                            threat_tables.get(atk_id, 0) + dmg
                        )
            if threat_tables:
                # Find the enemy with highest combined threat
                for e in sorted(enemies,
                                key=lambda e: threat_tables.get(e.id, 0),
                                reverse=True):
                    return e

            # Fallback: lowest HP
            return min(enemies, key=lambda e: e.db.hp or 0)

        # Default: use threat table if available, else random
        threat_table = getattr(npc.db, "threat_table", None) or {}
        if threat_table:
            # Highest threat among living enemies
            enemy_threats = [
                (e, threat_table.get(e.id, 0)) for e in enemies
            ]
            enemy_threats.sort(key=lambda x: x[1], reverse=True)
            return enemy_threats[0][0]

        return random.choice(enemies)

    # ------------------------------------------------------------------
    # Flee
    # ------------------------------------------------------------------

    def attempt_flee(self, combatant):
        """
        Attempt to flee combat with an opposed DEX check.

        Success: remove from combat, move to random exit.
        Failure: lose turn, enemy gets opportunity attack.
        """
        factions = self.db.factions or {}
        c_faction = factions.get(combatant.id, "unknown")
        order = self.db.initiative_order or []

        # Find highest DEX enemy
        best_enemy = None
        best_dex = -999
        for c, _ in order:
            e_faction = factions.get(c.id, "unknown")
            if e_faction != c_faction:
                c_hp = c.db.hp if c.db.hp is not None else 0
                if c_hp > 0:
                    e_dex = get_mod(c, "dex")
                    if e_dex > best_dex:
                        best_dex = e_dex
                        best_enemy = c

        if best_enemy is None:
            # No enemies, just leave
            self._flee_success(combatant)
            return

        # Opposed DEX checks
        flee_roll, _ = roll_d20()
        flee_total = flee_roll + get_mod(combatant, "dex")
        enemy_roll, _ = roll_d20()
        enemy_total = enemy_roll + get_mod(best_enemy, "dex")

        faction = _faction_of(self, combatant)
        name = _name(combatant, faction)
        e_faction = _faction_of(self, best_enemy)
        e_name = _name(best_enemy, e_faction)

        self._broadcast(
            f"\n  {name} |yattempts to flee!|n\n"
            f"  |x{combatant.key}: d20={flee_roll} + DEX = {flee_total} vs "
            f"{best_enemy.key}: d20={enemy_roll} + DEX = {enemy_total}|n"
        )

        if flee_total >= enemy_total:
            self._flee_success(combatant)
        else:
            self._broadcast(f"  |R{combatant.key} fails to escape!|n")

            # Opportunity attack from the blocking enemy
            e_wielded = best_enemy.db.wielded or {}
            e_weapon = e_wielded.get("main_hand")
            opp_result = resolve_attack(best_enemy, combatant, weapon=e_weapon)

            self._broadcast(f"\n  |y— Opportunity Attack —|n")
            self._display_attack_result(opp_result, best_enemy, combatant)

            if opp_result.is_hit:
                self.apply_damage(combatant, opp_result.final_damage,
                                  opp_result.damage_type, best_enemy)

            self.db.turn_log.append(
                f"{combatant.key} failed to flee. {best_enemy.key} "
                f"got an opportunity attack."
            )
            self.end_turn()

    def _flee_success(self, combatant):
        """Handle successful flee — remove combatant and move them."""
        faction = _faction_of(self, combatant)
        name = _name(combatant, faction)
        self._broadcast(f"  |G{combatant.key} escapes from combat!|n")

        self.db.turn_log.append(f"{combatant.key} fled from combat")

        # Try to move to a random exit
        room = self.obj
        if room and room.exits:
            exit_obj = random.choice(room.exits)
            combatant.move_to(exit_obj.destination, quiet=True)
            combatant.msg(
                f"|wYou flee through {exit_obj.key}!|n"
            )

        self.remove_combatant(combatant)
