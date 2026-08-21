# CHECK — handoff, 2026-08-21 10:06

Written for a CHECK with none of this in context. One page. Detail is in the items.

## 🟢 STATE RIGHT NOW

- **Game is UP.** World `Ash'karr` loaded, **1 map**, ticks 361, ~**304 pawns** on it.
- 🔴 **~300 of those are MY TEST LITTER** — hostile spawns from the arming sweep and the
  xenotype re-tests. They are disposable. The map is disposable. Nothing on it is kept.
- Bridge **released**. `MODE` is **interactive**. The owner is at the desk.
- `WORLDMAP_gen.rws` is the **complete painted world** — rain clamped, rivers re-graded,
  labels small, 16 landmarks, mutators, 72 settlements, 23 regions — and it loads **with no
  compatibility override**. Backed up at `world/WORLDMAP_gen.rws`.

## 🔴 THE RULING THAT CHANGES EVERYTHING ELSE

**Faction Control is OUT of v1.** Owner, 09:56 — *"I was wrong. We should remove the Faction
Control mod."*

With `thereallemon.factioncontrol` active, **three separate saves aborted** at
`FactionControl.CrossRefHandler_ResolveAllCrossReferences.Postfix`. Without it the same save
loads clean and a map save round-trips. `LOADS_ARE_BLOCKED_NEEDS_YOU_1`, open since
2026-08-20, is **cleared**.

Propagated, not just noted: live `ModsConfig` 578 · `ModsConfig.FULL.LATEST.xml`
**regenerated** (it is what `modlist_swap --restore` reads and it still carried the entry) ·
`canon.yml` has an `excluded_by_ruling` block.
⚠️ The count is still 578 **by coincidence** — a custom mod was added the same night.
⚠️ Cost: the faction-count spinners at world creation are gone, making
`FACTION_SLATE_ZEROES_KEEPS_1` the only remaining lever over which factions generate.

## 🔴 READ THIS BEFORE YOU TRUST A MEASUREMENT

`skills/rimbridge/references/traps.md`, bottom. **Three parameter names produced three fake
catastrophes in one session.** Each returned `success: true` and answered a different question:

- `jawa/pawn_get` takes **`pawn`**, not `pawnId` → read as *0 of 270 pawns armed*
- `jawa/spawn_pawn`'s `faction` decides the **species** (all 67 kinds use
  `useFactionXenotypes`) → `"hostile"` read as *49 of 55 kinds spawn Baseliners*
- `rimworld/load_game` was returning `save.missing_mods` **while I diagnosed from the log for
  an hour**

🔑 **A dramatic result makes the CALLER the first suspect.** Re-run it a second way before
writing it down.

⚠️ `ErrorWhileLoadingGame` alone is NOT a load canary. On a save with no map the engine throws
in `FinalizeLoading` and bails while that string reads **0**. Check both, and read
`programState` back. `w9_run.py` and `reload_check.py` do this now.

## Settled, with verdicts

| item | verdict |
|---|---|
| `LOADS_ARE_BLOCKED_NEEDS_YOU_1`, `RT_PROBE_LOAD_ABORTS_ON_578_1` | ✅ answered — FactionControl |
| `HILLINESS_CACHE_NOT_READABLE_1` | ✅ `unexplainedStale = 0` after reload — the owner's hypothesis was right |
| `BIOMESKIT_SNOWY_DESERT_TEXTURES_1` | ✅ 0 misses; the magenta belonged to the broken session |
| `ASH_STORM_OVER_PYRELANDS_1`, `IKEE_READS_AS_OURS_1`, `B63` | ✅ off the fresh dump |
| `FACTION_RELATION_MATRIX_1` | ✅ — but found **0 allies** planet-wide and **14 asymmetric** pairs |
| `ROLE_KINDS_ARMED_5_OF_5_1` + `sixteen-authored-…` | ❌ **23 of 54 kinds field a bare pawn in 5** |
| `B40 B41 B42 B52` | ❌ leader titles — the ideo overrides the def on 15 of 17 factions |
| `B54` | ❌ only **2 ideoligions exist**; none of the eleven faiths generated |
| `C40` | ❌ — but (a) and (b) are **retracted**, below |
| `CAST_ROSTER_269_LOAD_1` | ⚠️ partial — 269 load, but `Spawn authored character` **does not exist** in the debug tree |
| `SETTLEMENTS_OFF_IMPASSABLE_1`, `worldbuilder-preset-…` | ✅ closed |

## ⚠️ Two of my own findings are RETRACTED — do not act on them

1. **"49 of 55 kinds spawn Baseliners"** — false, my spawn parameter. The roster is fine:
   Geonosians 4/4, Jawa 5/5, Blackstar returns a five-species mercenary company.
   **Exactly one faction is wrong**: `Jawa_Droid_Grunt` → `Jawa_FreeDroidEnclaves` gives
   `Baseliner` 4/4. `DROID_ENCLAVES_FIELD_HUMANS_1`.
2. **Drinks as melee weapons** — owner ruled it **not a defect and not even a check**.
   ⚠️ BUILD shipped a fix 20 min *before* the ruling (`3c915e3`) permanently excluding
   ingestibles from weapon tags. It contradicts the ruling and is BUILD's to revert.
   `DRINK_WEAPON_CHECK_IS_RETIRED_1`.

## Owner decisions standing

- **Ideoligion mode**: fix at worldgen, do NOT accept Classic. At the top of
  `WORLDGEN_RUN.md`. It causes BOTH the missing faiths and the wrong leader titles.
- **The Scald**: sunk to −30 m. It was a lake perched **1,300 m above its own shoreline** —
  32 "cliffs" were that absurdity. Water now 8.14%.

## Pick up with

`rimflow next --seat CHECK`. The game is up with a disposable map, so anything needing pawns
is cheap right now. ⛔ `INHABITED_POOL_ROUND_TRIP_1` is NOT cheap — it wants a quit-to-desktop
and a two-settlement raid sequence.
