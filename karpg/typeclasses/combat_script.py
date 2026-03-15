"""
Combat Script

Evennia DefaultScript that manages a single MajorMUD-style combat encounter.
One script per room. Fires every 4 seconds (one combat round).

No EvMenu — combat is fully automatic. Player commands (bash, cast, flee, rank)
modify state on the script; at_repeat() consumes that state each tick.

db.active   — bool, True while combat is running
ndb.combatants — runtime dict mapping combatant obj →
    {
        "faction":      "player" | "hostile",
        "target":       obj | None,
        "attack_mode":  "normal" | "bash" | "smash" | "backstab",
        "rank":         "front" | "mid" | "back",
        "pending_spell": str | None,   # spell key queued for next round
        "flee_queued":  bool,
    }
ndb.round  — int, current round number
"""

import random

from evennia import DefaultScript
from evennia.utils.utils import inherits_from

from world.combat_engine import resolve_attack, resolve_spell, roll_flee, hp_colour, hp_bar
from world.spells import get_spell
from world.conditions import can_act, tick_conditions, get_combat_modifiers
from world.stats import get_attacks_per_round, get_mana_regen


# ---------------------------------------------------------------------------
# Verb helpers for attack mode display
# ---------------------------------------------------------------------------

_MODE_VERB = {
    "normal":   ("strike",    "strikes"),
    "bash":     ("BASH",      "BASHES"),
    "smash":    ("SMASH",     "SMASHES"),
    "backstab": ("BACKSTAB",  "BACKSTABS"),
}


def _verb(mode, second_person=True):
    """Return the display verb for an attack mode."""
    verbs = _MODE_VERB.get(mode, ("strike", "strikes"))
    return verbs[0] if second_person else verbs[1]


# ---------------------------------------------------------------------------
# CombatScript
# ---------------------------------------------------------------------------

class CombatScript(DefaultScript):
    """One per room. Fires every 4 seconds."""

    def at_script_creation(self):
        self.key = "combat"
        self.interval = 4
        self.persistent = True
        self.repeats = 0          # run indefinitely
        self.db.active = False

    def at_start(self):
        """Called each time the script starts (including after server restart)."""
        if self.ndb.combatants is None:
            self.ndb.combatants = {}
        if self.ndb.round is None:
            self.ndb.round = 0

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def begin_combat(self, initiator, targets):
        """
        Start a new combat encounter.

        initiator — the player/object initiating combat
        targets   — list of targets (usually NPCs)
        """
        self.ndb.combatants = {}
        self.ndb.round = 0
        self.db.active = True

        # Add the initiator
        faction = getattr(initiator.db, "faction", "player") or "player"
        self.add_combatant(initiator, targets[0] if targets else None, faction)

        # Add each target; NPCs target the initiator
        for t in targets:
            t_faction = getattr(t.db, "faction", "hostile") or "hostile"
            self.add_combatant(t, initiator, t_faction)

        room = self.obj
        _fmt = initiator.key
        room.msg_contents(
            f"\n|R*COMBAT BEGINS*|n — {_fmt} attacks {targets[0].key if targets else '???'}!"
        )

        if not self.is_active:
            self.start()

    # ------------------------------------------------------------------
    # Combatant management
    # ------------------------------------------------------------------

    def add_combatant(self, combatant, target, faction):
        """Add a combatant to the ongoing fight."""
        if self.ndb.combatants is None:
            self.ndb.combatants = {}
        self.ndb.combatants[combatant] = {
            "faction":       faction,
            "target":        target,
            "attack_mode":   "normal",
            "rank":          getattr(combatant.db, "formation_rank", "mid") or "mid",
            "pending_spell": None,
            "flee_queued":   False,
        }
        combatant.db.in_combat = self

    def remove_combatant(self, combatant):
        """Remove a combatant (they fled, died, or left the room)."""
        combatants = self.ndb.combatants or {}
        combatants.pop(combatant, None)
        combatant.db.in_combat = None
        self.ndb.combatants = combatants

    # ------------------------------------------------------------------
    # State setters (called by combat commands)
    # ------------------------------------------------------------------

    def set_target(self, combatant, target):
        state = self._state(combatant)
        if state:
            state["target"] = target

    def set_attack_mode(self, combatant, mode):
        state = self._state(combatant)
        if state:
            state["attack_mode"] = mode
            state["pending_spell"] = None  # modes are mutually exclusive with spells

    def set_rank(self, combatant, rank):
        state = self._state(combatant)
        if state:
            state["rank"] = rank
            combatant.db.formation_rank = rank

    def queue_spell(self, combatant, spell_name):
        state = self._state(combatant)
        if state:
            state["pending_spell"] = spell_name
            state["attack_mode"] = "normal"  # spells override melee modes

    def queue_flee(self, combatant):
        state = self._state(combatant)
        if state:
            state["flee_queued"] = True

    # ------------------------------------------------------------------
    # Main tick
    # ------------------------------------------------------------------

    def at_repeat(self):
        """One combat round — all combatants act simultaneously."""
        combatants = self.ndb.combatants
        if not combatants:
            self.end_combat()
            return

        self.ndb.round = (self.ndb.round or 0) + 1
        self._broadcast(f"\n|x--- Round {self.ndb.round} ---|n")

        # Snapshot so we don't mutate while iterating
        snapshot = list(combatants.items())

        for combatant, state in snapshot:
            if combatant not in (self.ndb.combatants or {}):
                continue  # was removed mid-round (killed)
            if (combatant.db.hp or 0) <= 0:
                continue

            # NPC target selection
            if state["faction"] != "player":
                self._npc_pick_target(combatant, state)

            # Ensure target is alive and present
            target = state.get("target")
            if not target or (target.db.hp or 0) <= 0:
                new_target = self._find_target(combatant, state["faction"])
                if not new_target:
                    continue
                state["target"] = new_target
                target = new_target

            # Resolve action
            if state["flee_queued"]:
                self._resolve_flee(combatant, state)
                state["flee_queued"] = False
            elif state["pending_spell"]:
                self._resolve_spell(combatant, state, target)
                state["pending_spell"] = None
                state["attack_mode"] = "normal"
            else:
                if not can_act(combatant):
                    self._broadcast(
                        f"|x{combatant.key} is unable to act!|n", targets=[combatant]
                    )
                    self._send(combatant, "|xYou are unable to act!|n")
                else:
                    n = get_attacks_per_round(combatant, state["attack_mode"])
                    for _ in range(n):
                        if (target.db.hp or 0) <= 0:
                            break
                        result = resolve_attack(combatant, target, state["attack_mode"])
                        self._broadcast_attack(result, combatant, target)
                        if (target.db.hp or 0) <= 0:
                            self._handle_death(target, combatant)
                            break

        # End-of-round housekeeping
        self._tick_mana_regen()
        self._tick_all_conditions()
        self._broadcast_hp_status()
        self._check_end_conditions()

    # ------------------------------------------------------------------
    # Action resolvers
    # ------------------------------------------------------------------

    def _resolve_flee(self, combatant, state):
        """Attempt to flee combat."""
        success = roll_flee(combatant)
        if success:
            # Find a random exit
            exits = [e for e in (self.obj.exits or []) if e.access(combatant, "traverse")]
            if exits:
                dest = random.choice(exits).destination
                self._send(combatant, "|YYou scramble for the exit... |G[SUCCESS]|n You escape!")
                self._broadcast(
                    f"|Y{combatant.key} scrambles away and escapes!|n",
                    exclude=[combatant]
                )
                self.remove_combatant(combatant)
                combatant.move_to(dest, quiet=False)
            else:
                self._send(combatant, "|YYou scramble for an exit... |R[FAILED]|n No way out!")
        else:
            # Find a name to blame
            enemy = state.get("target")
            blocker = enemy.key if enemy else "your enemies"
            self._send(
                combatant,
                f"|YYou scramble for the exit... |R[FAILED]|n {blocker} blocks your path!"
            )
            self._broadcast(
                f"|Y{combatant.key} tries to flee but is cut off!|n",
                exclude=[combatant]
            )

    def _resolve_spell(self, combatant, state, target):
        """Cast a queued spell."""
        spell_name = state["pending_spell"]
        spell = get_spell(spell_name)
        if not spell:
            self._send(combatant, f"|rYou don't know the spell '{spell_name}'.|n")
            return

        mana = combatant.db.mana or 0
        if mana < spell["mana_cost"]:
            self._send(
                combatant,
                f"|rNot enough mana! ({spell['mana_cost']} needed, {mana} available)|n"
            )
            return

        # AOE spells hit all enemies
        targets = [target]
        if spell.get("aoe"):
            targets = [
                c for c, s in (self.ndb.combatants or {}).items()
                if s["faction"] != state["faction"] and (c.db.hp or 0) > 0
            ]

        for t in targets:
            result = resolve_spell(combatant, t, spell)
            self._broadcast_spell(result, combatant, t, spell)
            if (t.db.hp or 0) <= 0:
                self._handle_death(t, combatant)

    # ------------------------------------------------------------------
    # Death handling
    # ------------------------------------------------------------------

    def _handle_death(self, victim, killer):
        """Handle a combatant reaching 0 HP."""
        self._broadcast(f"\n|R{victim.key} is DEAD!|n")

        # XP grant to killer (if player)
        xp_val = getattr(victim.db, "xp_value", 0) or 0
        if xp_val and killer and hasattr(killer.db, "xp"):
            killer.db.xp = (killer.db.xp or 0) + xp_val
            self._send(killer, f"|YYou gain {xp_val} XP.|n")

        # Call NPC death hook
        if hasattr(victim, "at_death"):
            victim.at_death(killer)

        # Player death — respawn
        if getattr(victim.db, "faction", "hostile") == "player":
            victim.db.hp = victim.db.hp_max or 10
            self._send(victim, "|rYou have been slain!|n |YYou awaken at the starting room.|n")
            # Move to limbo/start room if possible
            start = victim.search("Limbo", global_search=True, quiet=True)
            if start:
                if isinstance(start, list):
                    start = start[0]
                victim.move_to(start, quiet=True)

        self.remove_combatant(victim)

    # ------------------------------------------------------------------
    # Broadcasts
    # ------------------------------------------------------------------

    def _broadcast_attack(self, result, attacker, target):
        """Send personalized attack messages to combatants."""
        mode = result.mode
        if result.hit:
            if result.critical:
                dr_note = f" |x[DR {result.defense_resistance}]|n" if result.defense_resistance else ""
                dmg_colour = "|R"
                atk_msg = (
                    f"{dmg_colour}CRITICAL! You {_verb(mode, True)} "
                    f"{target.key} for {result.final_damage} damage!|n{dr_note}"
                )
                def_msg = (
                    f"{dmg_colour}CRITICAL! {attacker.key} {_verb(mode, False)} "
                    f"you for {result.final_damage} damage!|n{dr_note}"
                )
                obs_msg = (
                    f"{dmg_colour}CRITICAL! {attacker.key} {_verb(mode, False)} "
                    f"{target.key} for {result.final_damage} damage!|n{dr_note}"
                )
            else:
                dr_note = (
                    f" |x[DR {result.defense_resistance} → {result.final_damage} final]|n"
                    if result.defense_resistance else ""
                )
                dmg_colour = "|Y" if mode == "normal" else "|M"
                atk_msg = (
                    f"You {_verb(mode, True)} {target.key} "
                    f"for {dmg_colour}{result.final_damage}|n damage!{dr_note}"
                )
                def_msg = (
                    f"{attacker.key} {_verb(mode, False)} you "
                    f"for {dmg_colour}{result.final_damage}|n damage!{dr_note}"
                )
                obs_msg = (
                    f"{attacker.key} {_verb(mode, False)} {target.key} "
                    f"for {dmg_colour}{result.final_damage}|n damage!{dr_note}"
                )
        else:
            atk_msg = f"You swing at {target.key} and |xMISS!|n"
            def_msg = f"{attacker.key} swings at you and |xMISSES!|n"
            obs_msg = f"{attacker.key} swings at {target.key} and misses."

        self._send(attacker, atk_msg)
        self._send(target, def_msg)
        self._broadcast(obs_msg, exclude=[attacker, target])

    def _broadcast_spell(self, result, caster, target, spell):
        """Send spell result messages."""
        spell_name = spell["key"].title()
        spell_type = result.spell_type

        if spell_type == "heal":
            msg = f"|G{spell_name}|n heals you for |G{result.heal}|n HP."
            self._send(caster, msg)
            self._broadcast(
                f"|G{caster.key} casts {spell_name} and heals!|n",
                exclude=[caster]
            )
        elif result.hit:
            dmg_colour = "|C"
            atk_msg = (
                f"You cast |W{spell_name}|n at {target.key} "
                f"for {dmg_colour}{result.damage}|n damage!"
            )
            def_msg = (
                f"{caster.key} casts |W{spell_name}|n at you "
                f"for {dmg_colour}{result.damage}|n damage!"
            )
            obs_msg = f"{caster.key} casts {spell_name} at {target.key} for {result.damage} damage."
            if result.condition_applied:
                cond_note = f" |y[{result.condition_applied.upper()}]|n"
                atk_msg += cond_note
                def_msg += cond_note
            self._send(caster, atk_msg)
            self._send(target, def_msg)
            self._broadcast(obs_msg, exclude=[caster, target])
            self._send(caster, f"|xMana: {result.caster_mana}/{result.caster_max_mana}|n")
        else:
            self._send(caster, f"Your |W{spell_name}|n fizzles against {target.key}!")
            self._send(target, f"{caster.key}'s |W{spell_name}|n fizzles!")

    def _broadcast_hp_status(self):
        """Send end-of-round HP status to each combatant."""
        combatants = self.ndb.combatants or {}
        if len(combatants) < 2:
            return

        players = [c for c, s in combatants.items() if s["faction"] == "player"]
        hostiles = [c for c, s in combatants.items() if s["faction"] == "hostile"]

        for player in players:
            parts = []
            # Player's own HP
            php = player.db.hp or 0
            phpm = player.db.hp_max or 1
            col = hp_colour(php, phpm)
            parts.append(f"|w{player.key}:|n {col}{php}/{phpm} HP|n")
            # Their current target's HP
            state = combatants.get(player, {})
            enemy = state.get("target")
            if enemy and enemy in combatants:
                ehp = enemy.db.hp or 0
                ehpm = enemy.db.hp_max or 1
                ecol = hp_colour(ehp, ehpm)
                parts.append(f"|w{enemy.key}:|n {ecol}{ehp}/{ehpm} HP|n")
            self._send(player, "  " + "  |x||n  ".join(parts))

    def _broadcast(self, msg, exclude=None, targets=None):
        """
        Send a message to combatants in this fight.

        If targets is given, only send to those. Otherwise send to all except exclude list.
        """
        exclude = exclude or []
        combatants = self.ndb.combatants or {}
        if targets is not None:
            for c in targets:
                if hasattr(c, "msg"):
                    c.msg(msg)
        else:
            for c in combatants:
                if c not in exclude and hasattr(c, "msg"):
                    c.msg(msg)

    def _send(self, combatant, msg):
        """Send a message to one specific combatant."""
        if hasattr(combatant, "msg"):
            combatant.msg(msg)

    # ------------------------------------------------------------------
    # End-of-round housekeeping
    # ------------------------------------------------------------------

    def _tick_mana_regen(self):
        """Regenerate mana for all combatants."""
        for combatant in (self.ndb.combatants or {}):
            regen = get_mana_regen(combatant)
            max_mana = combatant.db.max_mana or 0
            if max_mana > 0:
                combatant.db.mana = min(
                    max_mana,
                    (combatant.db.mana or 0) + regen
                )

    def _tick_all_conditions(self):
        """Tick condition durations for all combatants."""
        for combatant in (self.ndb.combatants or {}):
            expired = tick_conditions(combatant)
            for cond_name in expired:
                self._send(combatant, f"|xYour {cond_name} condition has worn off.|n")

    # ------------------------------------------------------------------
    # End-condition check
    # ------------------------------------------------------------------

    def _check_end_conditions(self):
        """Check if the fight is over and end combat if so."""
        combatants = self.ndb.combatants or {}
        if not combatants:
            self.end_combat()
            return

        factions = set(s["faction"] for s in combatants.values())
        if len(factions) <= 1:
            # Only one faction left — or everyone is gone
            self.end_combat()

    def end_combat(self):
        """Clean up and stop the script."""
        self.db.active = False
        combatants = list((self.ndb.combatants or {}).keys())
        for c in combatants:
            c.db.in_combat = None
            if (c.db.hp or 0) > 0:
                self._send(c, "|gCombat has ended.|n")
        self.ndb.combatants = {}
        self.stop()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _state(self, combatant):
        """Return the state dict for a combatant, or None if not in combat."""
        return (self.ndb.combatants or {}).get(combatant)

    def _npc_pick_target(self, npc, state):
        """Pick the best target for an NPC based on threat table or random."""
        combatants = self.ndb.combatants or {}
        enemies = [
            c for c, s in combatants.items()
            if s["faction"] == "player" and (c.db.hp or 0) > 0
        ]
        if not enemies:
            state["target"] = None
            return
        threat = getattr(npc.db, "threat_table", None) or {}
        if threat:
            state["target"] = max(enemies, key=lambda c: threat.get(c.id, 0))
        else:
            state["target"] = random.choice(enemies)

    def _find_target(self, combatant, faction):
        """Find a live enemy-faction combatant for combatant to attack."""
        combatants = self.ndb.combatants or {}
        enemies = [
            c for c, s in combatants.items()
            if s["faction"] != faction and (c.db.hp or 0) > 0
        ]
        return random.choice(enemies) if enemies else None
