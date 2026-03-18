# KARPG — Claude Development Guide

## Project Layout

```
karpg/          ← Evennia game directory (run commands from here)
  commands/     ← Player-facing commands
  typeclasses/  ← Evennia typeclasses (characters, NPCs, scripts, etc.)
  world/        ← Pure Python game logic (no Evennia imports)
  server/conf/  ← Evennia settings
  karp/         ← Python virtualenv (nested inside karpg/, NOT the game dir)
mise.toml       ← Sets Python 3.11
```

## Running Evennia

The virtualenv is `karpg/karp/`. The `evennia` binary is at `karpg/karp/bin/evennia` and
requires `twistd` to be on PATH. Always run from the `karpg/karpg/` game directory:

```bash
cd /home/ryan/code/karpg/karpg
PATH="/home/ryan/code/karpg/karp/bin:$PATH" /home/ryan/code/karpg/karp/bin/evennia start
PATH="/home/ryan/code/karpg/karp/bin:$PATH" /home/ryan/code/karpg/karp/bin/evennia stop
PATH="/home/ryan/code/karpg/karp/bin:$PATH" /home/ryan/code/karpg/karp/bin/evennia reload
```

Connect via telnet on port 4000 or webclient at http://localhost:4001.

## Architecture

Strict separation of concerns — keep Evennia imports out of `world/`:

| Layer | Path | Role |
|---|---|---|
| Commands | `commands/combat.py` | Player-facing combat commands |
| Commands | `commands/chargen.py` | `chargen`, `setclass`, `setrace` |
| Commands | `commands/equipment.py` | `wield`, `unwield`, `equipment` |
| Commands | `commands/wearing.py` | `wear`, `remove` |
| Commands | `commands/resting.py` | `rest`, `stand` |
| Commands | `commands/map.py` | `map` |
| Commands | `commands/xp.py` | `xp` — windowed XP table |
| Commands | `commands/train.py` | `train` — level-up at trainer NPC |
| Commands | `commands/stealth.py` | `hide` — enter stealth (Thief/Elf/Halfling) |
| Engine | `world/stealth.py` | Stealth math: score, hide/noise/detection checks |
| Engine | `world/skills.py` | Skill registry + all skill math (perception, combat mastery, dodge, parry, etc.) |
| Commands | `commands/skills.py` | `skills`, `learn`, `pick`, `steal`, `track`, `bandage`, `turn`, `intimidate`, `forage`, `identify`, `search`, `disarm`, `settrap`, `battlecry`, `form` |
| Commands | `commands/economy.py` | `gold`, `balance`, `deposit`, `withdraw`, `list`, `buy`, `sell`, `drink` |
| Engine | `world/economy.py` | Pricing math, gold weight, format helpers |
| Typeclass | `typeclasses/merchants.py` | Merchant NPC typeclass with shop inventory |
| Script | `typeclasses/interest_script.py` | Global daily bank interest (1%/day, cap 50k GP) |
| Script | `typeclasses/combat_script.py` | 4-second tick manager + combatant state |
| Script | `typeclasses/resting_script.py` | Out-of-combat HP regen tick |
| Typeclasses | `typeclasses/characters.py` | Player character typeclass |
| Typeclasses | `typeclasses/npcs.py` | NPC typeclass |
| Typeclasses | `typeclasses/weapons.py` | Weapon typeclass |
| Typeclasses | `typeclasses/armor.py` | Armor typeclass |
| Engine | `world/combat_engine.py` | Pure math: hit, damage, flee |
| Stats | `world/stats.py` | MajorMUD stat helpers + `recalc_stats()` |
| Chargen | `world/chargen_menu.py` | EvMenu character creation flow |
| Classes | `world/classes.py` | Class registry + weapon/armor restriction helpers |
| Races | `world/races.py` | Race registry + stat mod data |
| Spells | `world/spells.py` | Mana-based spell registry |
| Conditions | `world/conditions.py` | Condition system |
| Area | `world/newhaven.py` | Newhaven starting area builder |
| Prototypes | `world/prototypes.py` | NPC + weapon spawn prototypes |
| Prototypes | `world/armor_prototypes.py` | Armor spawn prototypes |

## Combat System (MajorMUD style)

- **Auto-combat**: `CombatScript` fires every 4 seconds (one round). No EvMenu.
- **Commands modify state**; `at_repeat()` consumes it. State lives in `ndb.combatants`.
- **Hit formula**: `miss_chance = (D² / A²) / 100`
- **Stats**: STR, AGI, INT, WIS, HLT, CHM (not D&D scores)
- **Mana** replaces spell slots. Regens each round via WIS.
- **Formation ranks**: front (+15 acc / -10 def), mid (0/0), back (-10 acc / +15 def)

### Attack modes and DR timing

| Mode | Multiplier | DR applied |
|---|---|---|
| normal | 1× | after multiply |
| bash | 3.3× | before multiply |
| smash | 6× | before multiply |
| backstab | 5× | after multiply |
| crit | 2–4× of max | after multiply |

## Key db Attributes

**Characters / NPCs**: `str`, `agi`, `int`, `wis`, `hlt`, `chm`, `hp`, `hp_max`,
`mana`, `max_mana`, `kai`, `max_kai`, `ac`, `base_ac`, `dr`, `level`, `formation_rank`,
`conditions`, `in_combat`, `faction`, `known_spells`, `xp`, `lives`,
`magic_resistance`, `base_magic_resistance`

**Characters additionally**: `base_str`, `base_agi`, `base_int`, `base_wis`, `base_hlt`,
`base_chm` (pre-racial values used by `recalc_stats`), `char_class`, `race`, `cp`,
`bonus_hp`, `is_resting`, `is_hidden`, `chargen_complete`,
`hair_length`, `hair_color`, `eye_color`,
`wielded` (`{"main_hand": obj|None, "off_hand": obj|None}`),
`armor_slots` (`{"head", "neck", "chest", "arms", "hands", "waist", "legs", "feet",
"left_ring", "right_ring"}`),
`carrying_weight`, `race_two_handed_allowed`

**NPCs additionally**: `ai_profile`, `threat_table`, `xp_value`, `loot_table`, `art_key`

---

## Stats — Corrections & Extensions

**Stat scale**: MajorMUD uses a 50-baseline / 100-max scale. This project uses a 10-scale.
Mapping: our 10 ≈ their 50 (baseline); our 20 ≈ their 100 (max).

| Stat | Current impl | MajorMUD target | Status |
|---|---|---|---|
| INT → crit chance | INT-driven: 1% per INT pt, 10–20% typical, cap 25% | Done |
| AGI → AC | `AC + AGI/10` | +2.5 AC per 10 AGI | Close; refine later |
| STR → encumbrance | Carry cap enforced; accuracy/damage penalty active | 480 carry units per 10 STR | Done |
| HLT → HP milestones | Not implemented | MajorMUD: bonus HP at HLT 60/75/90; our scale: ~12/15/18 | Future work |
| CHM → merchant pricing | Not implemented | Reduces shop markup (see Economy section) | Future work |

---

## Character Classes

8 classes fully implemented in `world/classes.py`. Each entry defines:
`hp_per_level_min/max/avg`, `magic_school`, `magic_level`, `weapon_types`,
`two_handed_allowed`, `combat_rating`, `abilities`, `armor_types`.

| Class | Weapons | Armor | HP/level | Magic | Notes |
|---|---|---|---|---|---|
| Warrior | Any | Any | 6–10 | None | Highest melee DPS, combat rating 4 |
| Mage | Staff/dagger | Cloth | 2–4 | Mage (3) | No healing; best nukes |
| Thief | Dagger/sword/axe | Cloth/leather | 3–6 | None | Backstab, stealth, lockpick |
| Druid | Blunt/staff/sickle | Cloth/leather/medium | 4–7 | Druid (3) | Heals, nature attacks |
| Priest | Blunt/staff | Any | 4–7 | Priest (3) | Heals, divine attacks, turn undead |
| Warlock | Any | Cloth/leather/medium | 5–8 | Mage (2) | Hybrid fighter-mage |
| Gypsy | Dagger/sword | Cloth/leather | 3–5 | Mage (2) | Limited caster, thievery |
| Mystic | Unarmed/staff | Cloth | 4–7 | Kai (3) | Mental powers, unarmed forms, no mana |

Helper functions: `get_class(name)`, `can_use_weapon()`, `can_wear_armor()`,
`can_use_spell_school()`.

---

## Races

6 races implemented in `world/races.py`. Each entry defines:
`stat_mods`, `abilities`, `magic_resistance_bonus`, `xp_modifier`, `two_handed_allowed`.

`recalc_stats()` in `world/stats.py` applies racial `stat_mods` on top of `base_*` attrs
and stores the racial MR bonus.

| Race | STR | AGI | INT | WIS | HLT | CHM | Abilities |
|---|---|---|---|---|---|---|---|
| Human | 0 | 0 | 0 | 0 | 0 | 0 | — |
| Dwarf | +1 | -1 | -1 | +1 | +1 | -1 | magic_resistance (+10 MR), nightvision |
| Elf | -1 | +1 | +1 | 0 | -1 | +1 | nightvision, stealth_bonus |
| Half-Orc | +1 | 0 | -1 | -1 | +1 | -2 | encumbrance_bonus |
| Gnome | -1 | +1 | +1 | 0 | 0 | -1 | magic_resistance (+5 MR), lockpick_bonus |
| Halfling | -2 | +2 | -1 | 0 | 0 | 0 | stealth_bonus (no two-handed weapons) |

---

## Character Creation (Chargen)

EvMenu flow in `world/chargen_menu.py`. Triggered automatically on first login
(`at_post_puppet` checks `db.chargen_complete is False`). Re-enterable via `chargen` command.

**Flow**: Race → Race confirm → Class → Class confirm → CP stat allocation → Hair length →
Hair color → Eye color → Summary confirm → Enter Newhaven

**CP allocation**: 30 starting CP. Cost 1 CP/pt for first 10 above racial base; 2 CP/pt
for 11+. Hard cap: racial base + 10 per stat. Leftover CP stored in `db.cp`.

On confirm: `recalc_stats()` is called, HP/mana/kai restored to full, character teleported
to Village Center of Newhaven, `chargen_complete` set to `True`.

Admin commands (`setclass`, `setrace`) in `commands/chargen.py` remain for testing.

---

## Skills System

Implemented in `world/skills.py` (registry + math) and `commands/skills.py` (commands).
Each skill has proficiency levels 1–5 (Novice → Master). CP to learn/advance at trainer NPC.
Auto-use advancement: successful uses auto-level the skill (50/100/200/400 thresholds).

| Skill | Type | Primary Stats | Eligible Classes/Races | Notes |
|---|---|---|---|---|
| Perception | passive | INT | All | Spot hidden chars on room entry + combat round |
| Combat Mastery | passive | STR, AGI | Warrior | +2 acc +1 dmg per level |
| Dodge | passive | AGI | Thief, Mystic / Elf, Halfling | % chance to avoid hit; cap 30% |
| Dual Wield | passive | AGI | Warrior, Thief, Warlock, Gypsy | Extra off-hand attacks |
| Parry | passive | STR | Warrior, Warlock | % chance to halve damage; cap 25% |
| Shield Block | passive | STR | Warrior, Priest | % chance to negate hit (with shield); cap 20% |
| Encumbrance Bonus | passive | — | Half-Orc racial | ×1.2 carry cap; auto-granted |
| Nightvision | passive | — | Dwarf, Elf racial | See in dark rooms; auto-granted |
| Stealth | passive | AGI | Thief / Elf, Halfling | `hide` command; prerequisite for Backstab |
| Backstab | active | AGI, STR | Thief | 5× damage from stealth; `backstab <target>` |
| Outdoor Regen | passive | HLT | Druid | +1 HP/resting tick per level outdoors |
| Negotiate | passive | CHM | Gypsy | Shop discount (stub, future) |
| Unarmed Forms | passive | STR, AGI | Mystic | Tiger/crane/serpent stances; `form <stance>` |
| Lockpick | active | AGI, INT | Thief / Gnome (+3 bonus) | `pick <door>`; unlocks locked exits |
| Thievery | active | AGI, INT | Thief, Gypsy | `steal <target>`; gold or item |
| Track | active | INT | Druid | `track <name>`; reads footprint trail |
| First Aid | active | WIS | Warrior, Druid, Priest | `bandage [target]`; HLT+level×2 HP; 60s CD |
| Turn Undead | active | WIS, INT | Priest | `turn`; flee or damage undead; 30s CD |
| Intimidate | active | STR, CHM | Warrior, Warlock | `intimidate <t>`; frightened condition |
| Battle Cry | active | STR, CHM | Warrior | `battlecry`; +5 acc/level to allies for 3 rounds |
| Disarm | active | STR, AGI | Warrior | `disarm <target>`; knock weapon to floor |
| Traps | active | INT, AGI | Thief | `search`/`disarm trap`/`settrap <type>` |
| Forage | active | INT, WIS | Druid | `forage`; outdoor rooms; spawns herbs |
| Identify | active | INT | Mage, Druid | `identify <item>`; reveal hidden stats |

---

## Spell Schools

Each class has access to a specific school. Only spells from their school(s) can be learned.
Spells in `world/spells.py` must have a `"school"` field. The `known_spells` list on
characters is constrained by class + school at the character creation / trainer level.

| School | Classes | Focus |
|---|---|---|
| Mage | Mage, Warlock, Gypsy | High single-target damage, room-sweeping AoE, protective buffs, combat boosts. **No healing.** |
| Druid | Druid | Nature attacks, healing, cure poison, resistance buffs (fire/cold/lightning), nature AoE |
| Priest | Priest | Healing, buffs, divine attacks (bonus vs undead), alignment spells (good/evil variants) |
| Bard | Bard | Song-based: ally buffs, enemy debuffs, crowd control |
| Kai | Mystic | Mental powers. **No mana** — uses a separate Kai energy pool. Unarmed combat forms. |

**Mana formula (MajorMUD authentic)**:
`mana = 6 + 2 × magic_level × character_level`
where `magic_level` = 1 (Mage-1), 2 (Mage-2), 3 (full school access).
Mystics use Kai energy instead: `kai = 6 + 2*3*level + WIS`.

---

## Magic Resistance

Implemented. `db.magic_resistance` and `db.base_magic_resistance` on all characters and NPCs.
`recalc_stats()` applies racial MR bonus on top of `base_magic_resistance`.

- Range: 0–100 (mapped from MajorMUD's 50–150 scale)
- **Reduction formula**: `reduction = dmg × (mr / 200)`, capped at 50%
- INT passive contribution (+0.5 MR per INT above baseline) — future work

---

## Leveling & Progression (partially implemented)

- **Level cap**: 75
- **Advancement**: XP accumulates → reaches 100% → player types `train` at a trainer NPC
  → level increments, HP/mana recalculated, CP awarded
- **Character Points (CP)**: 30 awarded at chargen; further CP awarded each level

| Level range | CP per level |
|---|---|
| 1–10 | 10 |
| 11–20 | 15 |
| 21–30 | 20 |
| 31–40 | 25 |
| 41–50 | 30 |
| 51–60 | 35 |
| 61–70 | 40 |
| 71–75 | 45 |

- **Stat training cost**: First 10 points above base = 1 CP each; 2 CP each after
- **Lives**: Characters start with 9 lives; gain 1 per level (death costs a life)

Key `db` attributes: `xp`, `cp` (unspent character points), `lives` (default 9).

`world/xp_tables.py`: `xp_for_level()`, `xp_to_next_level()`, `xp_in_bracket()`, `cp_for_level()`.
TRAIN command (`commands/train.py`): checks trainer NPC in room, validates XP threshold, increments
level, awards CP, recalculates stats. `xp` command (`commands/xp.py`): 15-row windowed table
anchored to current level with XP required, bracket size, and CP columns.

---

## NPC AI Profiles

Implemented in `combat_script.py` — `_npc_act()` reads `db.ai_profile` and dispatches.
MajorMUD min-attack rule enforced: NPCs always get ≥1 attack per round even when stunned
or paralyzed (`can_act=False` skips extra attacks but not the base attack).

| Profile | Target Selection | Attack Mode | Flee Threshold |
|---|---|---|---|
| `tactical` | Highest-threat attacker (threat_table) | normal; bash if target HP < 50% | Never |
| `berserker` | Highest HP enemy | always smash/bash, alternates | Never |
| `cowardly` | Lowest level enemy | normal only | HP < 30% |
| `protective` | Whoever attacked allies | normal | Never |

---

## Economy & CHM (design goal — not yet implemented)

- **CHM effect**: `price = base × (1 - (chm - baseline) / 200)`. A character with CHM 20
  (our scale) pays ~10% less than baseline.
- **Ganghouse shops**: Fixed 200% markup; CHM has no effect.
- **Shop commands**: `list` (view inventory + prices), `buy <item>`, `sell <item>`
- **Merchant NPC**: New typeclass `typeclasses/merchants.py` (future)

---

## Implementation Status

**Done:**
- Core combat: MajorMUD hit formula, bash/smash/backstab/crit, DR, formation ranks
- NPC AI profile dispatch (tactical/berserker/cowardly/protective) + min-attack rule
- Stats: STR/AGI/INT/WIS/HLT/CHM with HP/mana/accuracy/defense formulas
- Mana system: mana costs, WIS-based regen per round
- Kai energy system for Mystics
- `recalc_stats()`: applies racial mods, recomputes HP/mana/kai/MR from base attrs
- 8 character classes with weapon/armor restrictions (`world/classes.py`)
- 6 races with stat mods and abilities (`world/races.py`)
- Full chargen EvMenu flow: race → class → CP allocation → appearance → Newhaven (`world/chargen_menu.py`)
- Appearance attributes: `hair_length`, `hair_color`, `eye_color` (set during chargen, shown in `look`)
- Magic resistance: `db.magic_resistance` + racial bonus via `recalc_stats()`
- 11 spells: attack, save, AOE, heal, condition-applying
- 8 conditions: poisoned, stunned, paralyzed, blinded, slowed, hasted, frightened, weakened
- Flee: AGI-based probability, random exit selection
- Death handling: HP-to-zero detection, combatant removal, XP award, lives decrement
- Weapon-vs-spell exclusivity: mutually exclusive per round
- Threat table: NPC target priority by cumulative damage dealt
- Gear slots: 10 armor slots + main/off-hand weapon slots; `wear`/`remove`/`wield`/`unwield`
- Encumbrance: STR-based carry cap; overweight penalises accuracy
- HP regen out of combat: `rest` command + `RrestingScript` tick (HLT-based)
- Status prompt (HP/mana/kai/level/XP) after every command
- ASCII map command with BFS grid and room type system
- 5 NPC prototypes: giant rat, goblin, skeleton, bandit, orc
- 6 weapon prototypes + armor prototypes
- Newhaven starting area: 14 rooms, 7 NPC stubs, arena with giant rats
- Login system: multi-step prompted `connect`/`create`, telnet echo suppression during
  password entry, password confirmation on account creation, styled ASCII connection screen
  (`commands/unloggedin.py`). Webclient password masking deferred (needs JS plugin).
- Leveling: `world/xp_tables.py` (XP curves, class/race multipliers, CP-per-level table),
  TRAIN command (trainer NPC presence check, XP threshold, level-up stat recalc, CP award),
  `xp` command (15-row windowed XP table with bracket progress footer)
- Stealth system: `hide` command (Thief/Elf/Halfling), AGI-based hide/noise/detection checks,
  room visibility filtering, NPC target exclusion, backstab requires stealth, reveal on
  attack/cast, `[HIDDEN]` prompt tag (`world/stealth.py`, `commands/stealth.py`)
- INT-based crit chance: `get_crit_chance()` in `world/stats.py`, 1% per INT point (cap 25%)
- Skills system: `world/skills.py` (central registry), `commands/skills.py` (16 skill commands)
  - Passive combat skills: combat_mastery, dodge, parry, shield_block, dual_wield, unarmed_forms
  - Racial auto-grants: encumbrance_bonus (Half-Orc), nightvision (Dwarf/Elf)
  - Active skills: lockpick, thievery, track, first_aid, turn_undead, intimidate, battle_cry, disarm, traps, forage, identify
  - Outdoor system: `db.is_outdoor` on Newhaven rooms; Druid hp_regen_outdoor; forage
  - Locked bandit hideout exit on South Road (difficulty 15); spike trap in Arena Entrance
  - Footprint trails: `db.recent_visitors` on all rooms, updated on every player move
  - `faction_type: undead` on skeleton prototype for turn_undead targeting
  - CP-based learn/advance economy at trainer NPC (tagged `skill_trainer`)
  - Proficiency levels: Novice → Master (auto-advance on use count)
  - `[FORM]` tag in status prompt when Mystic has active stance

- Economy system: gold (db.gold, db.bank_balance), gold encumbrance (0.01 lbs/GP),
  50 GP starting gold at chargen, daily bank interest script (1%/day, cap 50k GP),
  Merchant typeclass with shop inventory, buy/sell/deposit/withdraw/balance/drink commands,
  First Newhaven Bank room + Teller Oswyn, all 5 shop NPCs wired (Harden, Fletcher,
  Mira, Old Bern, Sister Elara), HEALING_POTION prototype (heals 20 HP, 25 GP base)

**Not yet implemented (rough priority order):**
1. HLT milestone bonus HP (at HLT 12/15/18 on our scale)
2. Loot drops (loot_table exists, drop logic not written)
3. Ranged combat (weapons have attack_range, no mechanic)
4. CHM direct merchant pricing (negotiate_discount() used by buy_price(); CHM-only effect not yet added)
5. Trainer NPCs wired into Newhaven (Master Aldric stub exists; TRAIN logic done but NPC not tagged)
6. Bard class / Bard spell school
7. Alignment system (Priest good/evil variants)
8. Additional races (7 more to reach MajorMUD's 13)
