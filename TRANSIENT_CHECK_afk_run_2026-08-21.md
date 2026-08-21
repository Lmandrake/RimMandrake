# CHECK's AFK run, 2026-08-21 03:36 → dawn

Written for the owner waking up. One page. Detail is in the items and the commits.

## 🔴 The one thing that changed everything

**The load blocker is the MOD SET, not the saves — settled, third save, third abort.**

`WORLDMAP_gen`, written by this mod set last night with **no map in it**, aborts with the
identical signature that killed `rt_probe` and `WORLDMAP_gen_sub7b`:

    Exception in FinalizeLoading(): Collection was modified
      at FactionControl.CrossRefHandler_ResolveAllCrossReferences.Postfix ()

Read back after: `status: no_game`, `programState: Entry`. Bailed to the main menu.
`LOADS_ARE_BLOCKED_NEEDS_YOU_1` is answered. `LOAD_ABORT_IS_FACTIONCONTROL_1` carries it.

⚠️ **AND YOUR MOD LIST IS MODIFIED RIGHT NOW.** `thereallemon.factioncontrol` is disabled
(579 → 578) to test whether it is the cause. Your untouched list is snapshotted at
`infrastructure/state/modlists/ModsConfig.BEFORE_FACTIONCONTROL_TEST.xml` — restore from it
if the removal is not justified. Nothing declares FactionControl as a dependency (swept all
1,254 installed workshop mods); what it provides is worldgen configurability for faction
counts, not content.

## 🔴 The canary was lying, and everything trusted it

`ErrorWhileLoadingGame` read **0** on that abort. Every tool gating on that string — including
`w9_run.py`'s `canary()` — would have called the dead game healthy and worked on the corpse.

The handler fires on **map** init; a save with no map dies in `FinalizeLoading` with nothing
to write the line. Fixed: the canary now checks `Exception in FinalizeLoading` too, and
`reload_check.py` reads `programState` back as a third instrument.

## Four new bridge tools, built and deployed

119 `jawa/` tools now, from 115. Each exists because a question cost you a night:

| tool | answers |
|---|---|
| `jawa/tile_settleable` | "why can't I click these tiles" — the ENGINE's own refusal text |
| `jawa/tile_cache_audit` | the mountain question, as a number. Reads the cache **by reflection** so the read does not populate it |
| `jawa/biome_art_audit` | which biome draws magenta |
| `jawa/faction_leader_get` | effective leader title beside the def's and the ideo's |

⭐ **And the offline arithmetic already answers your tile question:** **2,232 tiles (10.2%)
are unsettleable by the engine's own rule** — 1,780 water, **504 because our own 72
settlements block themselves and every neighbour**, 39 impassable. Not a cache bug. The
engine working correctly on the world we painted.

## Map fixes that landed

- **Three settlements stood on Impassable** and their own lore said otherwise — Oxalate
  Watch is *"the one breach in the Spine"*. Fixed the terrain, not the placement, so every
  named place stays where the design put it. Impassable 42 → 39.
- **The magenta is not ours.** ReGrowth 2 owns `WorldMaterials/BiomesKit` and ships **no**
  `_VerySnowy`/`_FullySnowy` for **any** biome — a healthy biome ships the same six files as
  ExtremeDesert. And our desert runs 19–64 °C with zero tiles below freezing.
- **The Scald is not water to the engine.** `SurfaceTile.WaterCovered => elevation <= 0f`,
  and the Scald is a crater lake at +1411 m. I enumerated every call site rather than
  guessing: the real bill is one broken `RiverDelta`, a road drawn where a boat should be,
  and a statistic 1.4 points low — **not** what it first looked like. Three options written
  up; ⛔ do not just drop 312 elevations, it re-rolls the relief.
- **Tribal Furniture's "dead art" was false** — 140 PNGs and its resolver DLL are both
  present. `jawa/texture_audit` was judging a mod's own `graphicClass` by vanilla rules; 39
  of 53 rows were noise. Fixed: such defs now go to an `unjudged` bucket, never `missing`.
  The false item is dropped with the measurement.

## ✅ THE EXPERIMENT WORKED — v1's load blocker was one mod entry

**`WORLDMAP_gen` loads clean with FactionControl disabled.** `programState: Playing`,
`hasCurrentGame: true`, `mapCount: 0`, and BOTH canary strings at zero. The same save
aborted three times with that mod active.

Then, in the same window, the world was completed and saved:

    rainfall re-push   21,872 applied, 0 unknown biomes
    river re-push      238 rivers, 837 roads, 0 unknown defs
    volcanic read-back 40 mm on all three (was 1668)
    saved over WORLDMAP_gen, and backed up into the repo

⭐ **The new save no longer records FactionControl, so it loads with no override**, and its
`<maps />` is still empty — the state the paint requires.

⚠️ **The catch you need to know:** disabling a mod makes every save that RECORDED it refuse
to load until `ignoreModCompatibility: true` is passed. That is a one-time cost — the new
save is clean.

### Every decision string, read back

| | |
|---|---|
| canary | ErrorWhileLoadingGame **0**, Exception in FinalizeLoading **0** |
| world | Ash'karr, seed grasshopper, **21,872 tiles**, maps 0 |
| spot-check | **7 of 7** tiles match the CSV on biome and temperature |
| landmarks / features | **16** / **23**, largest label 24.3 tiles — the resize scribed |
| `tile_cache_audit` | **UNEXPLAINED STALE = 0** — your mountain hypothesis was right, and it is a number now |
| `biome_art_audit` | 24 biomes, **0 missing**. BiomesKit misses this run: **0** |
| `tile_settleable` | 2,236 refused vs my offline 2,232 — 1,468 Ocean, 345 settlement-adjacent, 312 Lake, 24 impassable |

### 🔴 And the new tools found a real bug on their first run

`faction_leader_get`: **the ideoligion overrode the def on 15 of 17 factions.**
Empire reads **"leader"** where its def says **"Emperor"**. Pirate reads **"Ethical Dog"**
where its def says **"Captain"**. `Faction.LeaderTitle` (Faction.cs:142) prefers
`PrimaryIdeo.leaderTitleMale` and only falls back to the def — so an authored title can never
win, and every offline check still reads correct. **B40, B41, B42, B52 fail their title half.**
Same root cause as the faiths. `IDEO_TITLE_BEATS_DEF_TITLE_1`, filed for DECIDE.

## Where it stands

The game is **UP, paused, world loaded, no map** — exactly the state the paint requires, and
the save on disk matches. `python.exe src/RimMandrake/Utils/reload_check.py` re-reads every
string in one command; `infrastructure/state/RELOAD_CHECK.md` says what each should say.

### 🔴 Three things want your call

1. **Does FactionControl stay out?** It is what made v1 loadable. What it costs is the
   worldgen faction-count spinners — which is exactly the page we still need for the slate
   work. Snapshot to restore from is named above.
2. **The ideoligion mode.** It is now responsible for TWO failures, not one: the eleven
   faiths never generated, and 15 of 17 faction leader titles are overridden. Both are
   decided by one irreversible click on the world-creation page.
3. **The Scald** — accept it as brine over ground, drop 312 elevations, or just move the two
   `RiverDelta` mutators. `THE_SCALD_LOST_ITS_WATER_1` has the whole cost.

### And one correction on my own method

I spent an hour diagnosing "the load will not dispatch" from `Player.log` not growing, while
`load_game` had been returning `success: false, code: save.missing_mods` naming the mod the
whole time. **I never read the return value.** The project's one law, applied to every write
I made tonight and not once to a call I expected to succeed. Recorded on the item rather than
quietly fixed.
