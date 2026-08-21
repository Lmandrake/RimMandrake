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

## Where it stands

The game is relaunching without FactionControl. `reload_check.py` runs every decision string
in one command; `infrastructure/state/RELOAD_CHECK.md` holds them and what each should say.

**If the load comes back clean, v1's biggest blocker was one mod entry.**

⚠️ Two things still want your call: whether FactionControl stays out, and the Scald.
