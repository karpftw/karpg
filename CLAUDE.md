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
| Script | `typeclasses/combat_script.py` | 4-second tick manager + combatant state |
| Engine | `world/combat_engine.py` | Pure math: hit, damage, flee |
| Stats | `world/stats.py` | MajorMUD stat helpers |
| Spells | `world/spells.py` | Mana-based spell registry |
| Conditions | `world/conditions.py` | Condition system |

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
`mana`, `max_mana`, `ac`, `dr`, `level`, `formation_rank`, `conditions`,
`in_combat`, `faction`, `known_spells`, `xp`

**NPCs additionally**: `ai_profile`, `threat_table`, `xp_value`, `loot_table`, `art_key`

---

## Stats — Corrections & Extensions

**Stat scale**: MajorMUD uses a 50-baseline / 100-max scale. This project uses a 10-scale.
Mapping: our 10 ≈ their 50 (baseline); our 20 ≈ their 100 (max).

| Stat | Current impl | MajorMUD target | Status |
|---|---|---|---|
| INT → crit chance | Flat 5% | +1% crit per 10 INT (INT-driven) | Deviation — fix when classes land |
| AGI → AC | `AC + AGI/10` | +2.5 AC per 10 AGI | Close; refine later |
| STR → encumbrance | Not implemented | 480 carry units per 10 STR; exceeding cap penalizes accuracy + damage | Future work |
| HLT → HP milestones | Not implemented | MajorMUD: bonus HP at HLT 60/75/90; our scale: ~12/15/18 | Future work |
| CHM → merchant pricing | Not implemented | Reduces shop markup (see Economy section) | Future work |

---

## Character Classes (design goal — not yet implemented)

Class affects HP per level, available spell schools, weapon/armor restrictions, which stats
matter most, and base combat rating.

| Class | Weapons | Armor | HP/level | Magic | Notes |
|---|---|---|---|---|---|
| Warrior | Any | Any | 6–10 | None | Highest melee DPS, combat rating 4 |
| Mage | Staff/dagger | Robes | 2–4 | Mage (full) | No healing; best nukes |
| Thief | One-handed | Leather or less | 3–6 | None | Stealth, backstab, lockpick, traps |
| Druid | Druidic | Medium | 4–7 | Druid | Heals, resist buffs, nature attacks |
| Priest | Blunt | Any | 4–7 | Priest | Heals, divine attacks, strong vs undead; alignment (good/evil) |
| Warlock | Any melee | Medium | 5–8 | Mage-1 + Mage-2 | Hybrid fighter-mage |
| Gypsy | Light | Light | 3–5 | Mage-1 + Mage-2 | Limited caster |
| Mystic | Unarmed | Robes | 4–7 | Kai (no mana) | Mental powers, unarmed combat forms |

---

## Races (design goal — not yet implemented)

13 races total. Each sets starting stat modifiers (bonus/penalty vs baseline) and provides
racial abilities (nightvision, resistance, stealth, etc.).

Core races to implement first:

| Race | Strengths | Weaknesses | Notes |
|---|---|---|---|
| Human | Balanced | None | Benchmark; all stats at baseline |
| Dwarf | HLT, STR, magic resistance | AGI, CHM | Bonus HP milestones; racial MR bonus |
| Elf | AGI, INT | HLT, STR | Good mage/thief |
| Half-Orc | STR, HLT | INT, CHM | Front-line tank |
| Gnome | INT, WIS | STR, HLT | Best pure caster |
| Halfling | AGI, CHM | STR, HLT | Thief archetype |

Store stat modifiers as `db.race_str_mod`, etc., or as a single `db.race` key looked up
from a registry dict in `world/races.py` (future file).

---

## Skills System (design goal — partially stubbed)

Skills scale with relevant stats. Most are class-restricted. Lives in `world/skills.py`
(future). Each skill has a `check(combatant)` returning success chance based on relevant stats.

| Skill | Primary Stat | Class(es) | Notes |
|---|---|---|---|
| Stealth | AGI | Thief | Prerequisite for Backstab; detected by enemy Perception |
| Backstab | AGI + STR | Thief | Only usable while hidden; single-hit, massive damage |
| Thievery | AGI + INT | Thief | Steal gold/items from characters |
| Lock Picking | AGI + INT | Thief | Open locked doors/chests |
| Traps | INT | Thief | Detect and disarm traps |
| Tracking | INT | Ranger/Druid | Follow character trails |
| Perception | INT | All | Spot hidden things, detect stealthed characters |
| Magic Resistance | WIS + INT | All | Passive damage reduction vs spells |

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
Current `INT*3 + level*2` is a deliberate approximation — note it as a deviation.

---

## Magic Resistance (design goal — not yet implemented)

DR handles physical damage reduction. Magic resistance is a separate stat for spell damage.

- Range: 0–100 (mapped from MajorMUD's 50–150 scale)
- Store as `db.magic_resistance` on characters and NPCs (default 0)
- **Reduction formula** (our 0-100 scale): `reduction = dmg × (mr / 200)`, capped at 50%
- INT contributes passively: +0.5 MR per INT point above baseline (future)
- Dwarves have racial MR bonus

---

## Leveling & Progression (partially implemented)

- **Level cap**: 75
- **Advancement**: XP accumulates → reaches 100% → player types `train` at a trainer NPC
  → level increments, HP/mana recalculated, CP awarded
- **Character Points (CP)**: Awarded each level to raise stats manually

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

- **Stat training cost**: First 10 points above base = 1 CP each; scales higher after
- **Lives**: Characters start with 9 lives; gain 1 per level (death costs a life)

Key `db` attributes: `xp` (current), `xp_needed` (for next level), `cp` (unspent
character points), `lives` (default 9).

---

## NPC AI Profiles

Profiles stored as `db.ai_profile` but currently ignored. Implement in `combat_script.py`
— `_npc_act()` reads `ai_profile` and dispatches.

| Profile | Target Selection | Attack Mode | Flee Threshold |
|---|---|---|---|
| `tactical` | Highest-threat attacker (threat_table) | normal; bash if target HP < 50% | Never |
| `berserker` | Highest HP enemy | always smash/bash, alternates | Never |
| `cowardly` | Lowest level enemy | normal only | HP < 30% |
| `protective` | Whoever attacked allies | normal | Never |

**MajorMUD rule**: Monsters always get at least 1 attack per round even when stunned or
paralyzed. `can_act = False` should skip extra attacks but always allow 1 normal attack.

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
- Stats: STR/AGI/INT/WIS/HLT/CHM with HP/mana/accuracy/defense formulas
- Mana system: mana costs, WIS-based regen per round
- 11 spells: attack, save, AOE, heal, condition-applying
- 8 conditions: poisoned, stunned, paralyzed, blinded, slowed, hasted, frightened, weakened
- Flee: AGI-based probability, random exit selection (`commands/combat.py` + `combat_script.py:234-262`)
- Death handling: HP-to-zero detection, combatant removal, XP award (`combat_script.py:298-323`)
- Weapon-vs-spell exclusivity: mutually exclusive per round (already enforced in combat script)
- Threat table: NPC target priority by cumulative damage dealt
- 5 NPC prototypes: giant rat, goblin, skeleton, bandit, orc
- 6 weapon prototypes with damage/type/range
- Newhaven starting area: 14 rooms, 7 NPC stubs, arena with giant rats (`world/newhaven.py`)

**Not yet implemented (rough priority order):**
1. NPC AI profile dispatch — `_npc_act()` reads `ai_profile` but does not dispatch on it
2. MajorMUD monster rule: always ≥1 attack even when stunned/paralyzed — `can_act=False` currently blocks all attacks
3. Stealth system (prerequisite for backstab enforcement)
4. INT-based crit chance (currently flat 5%)
5. HP regeneration out of combat
6. Character classes + class restrictions
7. Leveling (TRAIN command, CP system, level-up stat recalc)
8. Races + racial stat modifiers
9. Skills system (stealth, lockpick, traps, tracking, perception)
10. Magic resistance stat
11. Loot drops (loot_table exists, drop logic not written)
12. Ranged combat (weapons have attack_range, no mechanic)
13. CHM → merchant pricing
14. Merchant NPCs + shop commands (stubs exist in Newhaven, no buy/sell logic)
15. Trainer NPCs + TRAIN command (Master Aldric stub exists, no TRAIN logic)
16. Encumbrance (STR-based carry cap affecting accuracy/damage)
17. Bard / Mystic / Kai schools
