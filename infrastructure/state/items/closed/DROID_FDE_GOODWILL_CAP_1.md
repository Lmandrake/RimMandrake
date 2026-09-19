## spec
Implement `design/Jawa/worldbuilding/restraining_bolt_technical.md`'s "Build note"
verdict exactly: one `GoodwillSituationDef` + one `GoodwillSituationWorker` subclass,
no Harmony, no stored state. Caps the player's goodwill ceiling with the Free Droid
Enclaves (`Jawa_FreeDroidEnclaves`) by how many currently-owned pawns carry Droid
Depot's `OuterRim_RestraintBolt` hediff right now: `maxGoodwill = 100 - 2.5*N`,
floored at -70. Degrades quietly (returns the vanilla 100) if Droid Depot or the
Enclaves faction is not active.

## the doc was stale — corrected in the same commit
The design doc (a retired seat, 2026-08-13) marked this whole feature `[v2]`,
blocked on "the Free Droid Enclaves `FactionDef` is unbuilt". That FactionDef is
now built and live on the frozen world (confirmed today via
`DROID_FACTIONS_IN_FROZEN_SAVE_1`'s census, cb0f7506) — BENCH had already promoted
this item to `target: v1` on 2026-09-06 accordingly, but the doc's own `[v2]`
markers were never updated. Both struck through and superseded in place, per the
project's "superseding a doc means writing into the doc" rule.

## what was built
`src/RimUtinni/RestrainingBolts/` — new small mod, `mandrake.rut.restrainingbolts`:
- `Defs/GoodwillSituationDefs/Jawa_RestrainingBolts.xml` — the def, worker class
  named, no `baseMaxGoodwill` (confirmed by the design doc's own decompiled-IL
  trap note: that field is read by nothing, only the ctor stores it).
- `Source/GoodwillSituationWorker_RestrainingBolts.cs` — implements the doc's exact
  formula; early-outs to vanilla 100 before touching `PawnsFinder` for any faction
  that isn't the Enclaves (load-bearing for perf, not tidiness — Recalculate runs
  every worker for every goodwill-capable faction every recache); lazily resolves
  the bolt `HediffDef` via `GetNamedSilentFail` (never throws if Droid Depot is
  absent) instead of trusting a `[DefOf]` for a donor-mod def.
- `Source/DefOfs.cs` — `FactionDefOf_RestrainingBolts.Jawa_FreeDroidEnclaves`.

Builds clean (0 warnings, 0 errors) against the live RimWorld assemblies —
confirms `PawnsFinder.AllMapsCaravansAndTravellingTransporters_Alive_OfPlayerFaction`,
`GoodwillSituationWorker`, `Faction`, `HediffDef` all resolve exactly as the design
doc's decompiled-IL evidence said they would. Deployed to the live Mods folder
(`deploy_custom_mods.py --apply`); NOT added to any active ModsConfig yet — the
mod sits present-but-inactive until a game-up session enables and tests it.
`run_selftests.py`: 43/43 still pass.

## verify
```
PROVE   bolt N droids, read the Enclaves' goodwill cap via the Factions tab or
        Faction.GoodwillWith(Jawa_FreeDroidEnclaves) before/after; unbolt one and
        confirm the cap rises within ~1000 ticks with NO removal hook firing
EXPECT  cap == Max(-70, 100 - round(2.5*N)) at every N tested (2, 12, 40 per the
        doc's own worked table); the faction-card explanation line names
        "restraining bolts" once N>0
LIES    testing on a save with zero droids ever bolted -- the situation never
        activates, so "it didn't break anything" is not "it works". Need at
        least one real bolted droid to observe a cap below 100.
```

**Not done tonight (2026-09-07)**: the live verify above (needs a game-up session
with the mod enabled and at least one droid + bolt on hand) and enabling the mod
in any active ModsConfig — left for a session that can also watch the Factions
tab. Offline authoring, compile-verification and the doc correction are complete;
leaving `doing` rather than closing, per this project's own "a live check is owed
to a mechanism never once observed running" rule.

## re-verified offline, 2026-09-09 (game mid-cold-load, bridge unavailable)
Re-read the doc's Build note and every source file against it line by line — no
gap found; the shipped code matches the verdict exactly (early-out on the wrong
faction FIRST, `GetNamedSilentFail` on the donor hediff, no `baseMaxGoodwill`,
`Mathf.Max(-70, 100 - Mathf.RoundToInt(2.5f*N))`). Nothing to author.

- **Rebuilt clean** from source (`dotnet build … -c Release`): 0 warnings, 0
  errors. The rebuilt DLL was byte-different only in embedded build
  metadata (no source changed), so the rebuild was discarded rather than
  recommitted — nothing to `git add`.
- **`validate_patch.py`** against the live 586-mod set: `OK - 0 errors, 0
  warnings` on `Jawa_RestrainingBolts.xml`.
- **`run_selftests.py`**: 43/46 pass; the 3 failures
  (`selftest_one_path_seam.py`, `bridgetools/selftest_tool_metadata.py`,
  `rimflow/selftest_render.py`) are all in unrelated subsystems with zero
  mention of RestrainingBolts/GoodwillSituation in their output — not this
  item's regression, not investigated further here.
- **Bridge check**: `rimflow bridge who` — held by FOUNDRY for an unrelated
  item (`BIOME_ENRICHMENT_POISON_FOREST_1`), and the game itself was
  mid-cold-load per this session's briefing. No live call attempted.

**Closing this item.** Per this session's explicit close criteria (fully built
+ offline-verified closes; the live-observed test is noted as owed, not a
blocker): the mod is fully built, matches the spec exactly, and re-verifies
clean by every offline instrument available (build, `validate_patch.py`,
selftest suite). **Still genuinely owed, and NOT done here:** the
live-observed test in the verify block above (bolt N droids, watch the
Enclaves cap move in the Factions tab) — nobody has ever watched this
mechanism run. Whoever next has bridge access to a game with Droid Depot +
Free Droid Enclaves active and an actual bolted droid on hand should run it
and file a fresh item if it fails.
