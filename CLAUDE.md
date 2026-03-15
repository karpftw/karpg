# KARPG — Claude Development Guide

## Project Layout

```
karpg/          ← Evennia game directory (run commands from here)
  commands/     ← Player-facing commands
  typeclasses/  ← Evennia typeclasses (characters, NPCs, scripts, etc.)
  world/        ← Pure Python game logic (no Evennia imports)
  server/conf/  ← Evennia settings
karp/           ← Python virtualenv (NOT the game directory)
mise.toml       ← Sets Python 3.11
```

## Running Evennia

The virtualenv is `karp/`. The `evennia` binary is at `karp/bin/evennia` and
requires `twistd` to be on PATH. Always run from the `karpg/` game directory:

```bash
cd karpg
PATH="/home/ryan/code/karpg/karp/bin:$PATH" ../karp/bin/evennia start
PATH="/home/ryan/code/karpg/karp/bin:$PATH" ../karp/bin/evennia stop
PATH="/home/ryan/code/karpg/karp/bin:$PATH" ../karp/bin/evennia reload
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
