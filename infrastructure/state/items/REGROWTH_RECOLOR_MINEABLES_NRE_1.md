# REGROWTH_RECOLOR_MINEABLES_NRE_1

## Symptom
Every full-modlist save load logs, once:
```
Exception from long event: System.NullReferenceException: Object reference not set to an instance of an object
  at ReGrowthCore.Map_FinalizeInit_Patch+<>c__DisplayClass1_0.<ProcessMap>g__RecolorMineables|4 () [0x00062]
  at ReGrowthCore.Map_FinalizeInit_Patch+<>c__DisplayClass1_0.<ProcessMap>b__0 () [0x00000]
  at Verse.LongEventHandler.UpdateCurrentSynchronousEvent (...)
```
Confirmed real in `Transient/Player.log.geneticrim_ctor_nre_2026-09-25` (L11288-92) and
`Transient/logs_2026-09-24/Player.log.before_bacta_swap` (L14377-81). Release DLL, no PDB
— only 2 frames, no field name in the trace.

## Mechanism (reverse-engineered from ReGrowthCore.dll IL, since RimSage does not index
third-party mod assemblies — only `Defs/`+`Source/` for core RimWorld)

`Map_FinalizeInit_Patch.ProcessMap`:
1. Synchronously flood-fills every `Mineable` Thing with `def.building.isNaturalRock==true`
   into a `lumps: Dictionary<Thing,int>` (skips any defName in
   `ModSettings_PerspectiveOres.skippedMineableDefs`).
2. `AssociateLumps` gives each lump a `Color` borrowed from an adjacent
   `isNaturalRock && !isResourceRock` neighbour's `Thing.DrawColor`.
3. Queues **two independent** long-event actions: `b__0` (wraps `RecolorMineables`) and
   `b__1` (a separate map-refresh call). They are queued separately, so `b__0` throwing
   does NOT stop `b__1` or the rest of map load — `LongEventHandler` catches per-action.
4. `RecolorMineables` iterates `lumps`, and for each Thing with an assigned lump colour
   reads `thing.Graphic.data` (a `GraphicData`) to rebuild a tinted `Graphic` via
   `GraphicDatabase.Get(...)`, then overwrites `thing.graphicInt` directly. The only
   NRE-shaped dereference in the method is `thing.Graphic.data` being null (i.e.
   `Thing.Graphic` returned something not built from a `GraphicData`, e.g. a fallback/error
   graphic) — none of the fields it touches are literally `color`/`stuff` on our def as
   originally guessed when this item was filed; it is specifically `Graphic.data`.

**Blast radius: cosmetic and self-contained.** Only the recolor tint for some mineables is
skipped for that one map load; nothing else in ReGrowth's map init or the game's own load
is affected (`b__1` and the rest of the load run normally — matches the log: 1x/load, no
crash, no cascading errors).

## Investigation against our own defs
Queried the live def dump (`defs.sqlite`, mods=623, captured 2026-09-24) for every ThingDef
matching the IL's exact inclusion gate (`building.isNaturalRock == true`): **174 total across
all 623 active mods, 52 of them ours** (`mandrake.rsw.armoury` KOTOR_* ore/crystal veins,
`mandrake.rut.*` rock/wall/heartwood defs, plus their `GravTide_*` variants). Checked each for
`graphicData` presence, `texPath`/`graphicClass` populated, and `cachedGraphic.data` being a
valid GraphicData self-reference (not null).

**Result: zero anomalies, in ours or in any of the other 571 mods' defs.** Every one of the 52
has complete, healthy graphicData already successfully rendered at least once in the same
captured session.

**Caveat, stated honestly:** the dump is a post-load snapshot. A Graphic that failed once
during `Map_FinalizeInit` but was rebuilt cleanly afterward by the normal render pipeline
would still show healthy here — a static dump cannot rule out a transient bad state that
self-healed before the dump was captured.

## Status: BLOCKED, not closed
No fixable defect found on our side after a genuine, evidenced attempt (real stack trace +
full IL disassembly of the actual crashing method chain + exhaustive def-dump cross-check
against the derived qualifying criterion). Did not guess a fix.

**What would resolve it:** a live Harmony postfix/breakpoint on `RecolorMineables` (or on the
exception handler) on the Windows Desktop machine (where RimSage/live debugging is reachable),
logging the actual `Thing`/`ThingDef` whose `Graphic.data` was null at the moment of the throw.
Not obtainable from `Player.log` or the def dump alone.

## Note on RimSage
This session's `mcp__rimsage__*` tools DID connect (contra the CLAUDE.md claim that RimSage
has never connected off the Windows Desktop) — `search_defs`/`get_def_details` returned real
data. It simply has no index of `ReGrowthCore.dll` or any other 3rd-party mod source, only
`Defs/` and core `Source/`. Worth a CLAUDE.md correction by whoever owns that section next.
