# COLONY_VISIBILITY_BUILD_1

## spec

`design/Jawa/worldbuilding/colony_visibility_stat.md`, specifically
Annex A (BENCH merge, 2026-08-30) and the owner's 2026-08-31 ruling
closing it: "THREAT-SCOPED patching. The global-vs-threat-scoped fork is
closed: the Postfix replaces threat points for HOSTILE events only.
Quest budgets, herd sizing and friendly arrivals stay on vanilla wealth
scaling." Filed as the successor to `COLONY_VISIBILITY_STAT_1` (closed
2026-08-30), which built a safe core + one narrow raid-point call site
and explicitly left the dominant raid path and the mod's home as open
questions.

## What this pass did

**Rehomed** the safe-core `GameComponent_ColonyVisibility` (state vector,
band ladder, `Adjust()`, `ExposeData`) from `mandrake.rut.doctrine` into
its own dedicated mod, `mandrake.rm.visibility`
(`src/RimMandrake/Visibility/`) — the packageId the item's own title
names. `mandrake.jawadoctrine.core`'s bootstrap no longer calls the old
patch; the two superseded files (`ColonyVisibility.cs`,
`ColonyVisibilityRaidPatch.cs`) are deleted from Doctrine, which still
builds clean (0 errors/warnings) without them.

**Replaced the raid-point technique entirely**, per Annex A's simpler
formula (`points ×= VisibilityToThreatCurve(vis)` — a straight
multiplier, superseding STAT_1's more complex "reimplement vanilla's
pawn-power term, replace only the wealth term" approach, which needed no
reimplementation once the formula is multiplicative rather than
substitutive):

- **Verified from scratch, not assumed** (a fresh RimSage research pass):
  `IncidentCategoryDef` carries no hostility flag, and category-based
  filtering is **provably wrong** — `ProblemCauser`
  (`Defs/Royalty/IncidentDefs/Incidents_Map_Misc.xml`) is a quest-giving
  incident tagged `category>ThreatBig`, and `ThrumboPasses`/
  `HerdMigration` (both `category=Misc`) also carry
  `needsParmsPoints=true` despite being named as explicitly out of scope.
  No `incCat` filter at `DefaultParmsNow`/`GenerateParms` separates these
  correctly — confirmed with concrete counterexamples, not left as a
  hedge.
- **The reliable choke point**: a Harmony **Prefix on
  `IncidentWorker.TryExecute(IncidentParms parms)`**
  (`Source/RimWorld/IncidentWorker.cs:183`), gated on the CONCRETE worker
  type (`IncidentWorker_RaidEnemy`, `IncidentWorker_Infestation`,
  `IncidentWorker_AggressiveAnimals` for manhunter packs,
  `IncidentWorker_MechCluster`) rather than any category heuristic.
  `IncidentParms` is a class, so mutating `parms.points` in the Prefix
  changes what the real worker body consumes.
- **This single Prefix also covers `TimedDetectionRaids`** (it
  constructs and fires an `IncidentWorker_RaidEnemy` the same way any
  other raid does), so STAT_1's separate call-site transpiler for that
  one path is no longer needed — one mechanism now covers both the
  dominant storyteller-raid path STAT_1 could never reach AND the one
  path it had already gotten working.
- Ta'Baa's launch-reset Postfix on `GravshipUtility.GenerateGravship`
  carried over unchanged (STAT_1's own work — real, verified, no reason
  to redo it).
- Builds clean (0 warnings, 0 errors) for both `mandrake.rm.visibility`
  and the trimmed `mandrake.rut.doctrine`.

## Deploy state

`mandrake.rm.visibility` deployed clean, added to `ModsConfig.xml` after
`mandrake.rm.ninefold`. `mandrake.rut.doctrine`'s redeploy **failed** —
the game is up this session and has its old DLL locked
(`OSError: [Errno 22] Invalid argument`, not a corruption, just a
Windows file-lock on write). `deploy_custom_mods.py --mod Doctrine
--apply` re-run cleanly redeploys it once the game is down; confirmed
via a dry-run plan (`Drift found`, one file, `~ Assemblies/
JawaDoctrineCore.dll`) that nothing else needs touching.

## Not done — explicitly, not silently

- `VisibilityToThreatCurve`'s five anchor points are Annex A's own
  "first-guess," not tuned — §5's own tuning protocol (throwaway-save
  rig, measure at Visibility ∈ {0,25,50,75,100} × 3 wealth bands, 10
  samples each) has not been run.
- Every OTHER raise/lower hook in the design doc's §2 table (spotted/
  raided at home, challenge broadcasts, Renown, THE SHAMING, Overcurrent,
  melee fighting, flare-lighting, ambush kills, undetected-raid
  survival, concealed construction, darkness, blackout reign, Unseen
  Berth, the Unburdening rite) is still not wired to anything —
  `Adjust()` is ready, nothing calls it yet.
- Sh'kaar's escalation multiplier seam exists (`ShkaarEscalationMultiplier`,
  default 1f) but nothing sets it.
- No live proof this Prefix actually fires and multiplies correctly —
  needs a quicktest with a spawned hostile incident, owed to the next
  restart.

## 2026-09-02 (FOUNDRY) — tile-memory decay built; F17 interface layer partial

**Tile-memory decay, built for real** (`GameComponent_ColonyVisibility.cs`):
`Dictionary<int, TileVisibilityMemory>` keyed by `PlanetTile.tileId`, Scribe'd
(`LookMode.Value, LookMode.Deep`). `RecordTileDeparture(tileId)` snapshots the
dial + `Find.TickManager.TicksGame` at the moment the ship leaves — wired into
`Postfix_ResetVisibilityOnLaunch` (reads `shipVisibility` BEFORE
`ResetOnLaunch()` clamps it; combined into one postfix method rather than a
second Harmony registration on the same target, since cross-registration
postfix ordering on one method isn't guaranteed). `ApplyTileMemoryOnArrival(tileId)`
decays by `Mathf.Pow(0.5f, seasonsAway)` where `seasonsAway = ticksAway /
GenDate.TicksPerSeason` (900,000, the real vanilla constant, not guessed) —
matches the owner's own "halved per season" wording exactly. If the decayed
value exceeds the CURRENT dial, restores the difference via `Adjust()`; if not,
does nothing (a tile the desert remembers less than your current notoriety
shouldn't drag it down). Wired to both gravship-landing choke points
(`ArriveExistingMap`/`ArriveNewMap` — a trip can end either way), reading the
destination tile off `Gravship.destinationTile.tileId` (set by
`GravshipUtility.TravelTo` before either runs). Overwrites rather than
accumulates history — only the most recent departure from a tile decays
forward.

**F17's interface layer, inspect-tag piece only** — a `Command_Action` gizmo
postfixed onto `Building_GravEngine.GetGizmos()` showing the current band name
and numeric dial (plain strings, not `.Translate()` keys — no Languages/
English XML exists for this mod, out of scope this pass). Reused vanilla
`TexCommand.Attack` icon rather than authoring new art.

**F17's other two pieces — deliberately NOT built, not silently skipped**: the
reign-calendar date-line clause and band-crossing letters (design doc §3.1/
§3.2) both depend on Ninefold's own signed-letter/god-attribution
infrastructure, which `NINEFOLD_ENGINE_M0_1` itself records as unbuilt
("event hooks... corpus letters... NOT built... reserved for the owner's
voice redline pass" — confirmed absent from the codebase this pass, no
`reign`/`ReignCalendar` hits anywhere in `src/`). Firing an unsigned letter
here would violate F9's own "no unsigned crossings" rule that the design doc
itself cites. Left a named, documented, currently-inert trigger point
(`Notify_BandCrossed_NotYetWired`, `ColonyVisibilityRaidPatch.cs`) for
whoever builds that layer to call from `Adjust()`, rather than fabricating
placeholder flavor text against established doctrine.

`dotnet build`: 0 warnings/0 errors. No XML changed (pure C#), so
`validate_patch.py` isn't the relevant check here. **Deploy attempted,
correctly refused**: the game is up this session (mod already active,
`mandrake.rm.visibility` in `ModsConfig.xml`) — `deploy_custom_mods.py --mod
Visibility --apply` hit the same Windows file-lock this item's own history
already documents for the Doctrine mod (`OSError: [Errno 22] Invalid
argument`, DLL memory-mapped by the running game, not corruption). Compiled,
not deployed — redeploy once the game is down, then this item still needs a
live quicktest for the ORIGINAL Prefix (threat-point multiplier, never
live-proven) AND the new tile-memory round trip (launch from a tile, let a
season+ pass, return, confirm the dial bumps per the decay curve above).

Left `doing`.

## 2026-09-02 (FOUNDRY, background fanout) — decay math extracted and selftested

Extracted `SeasonsAway()`/`DecayedTileVisibility()` as pure static methods
out of `ApplyTileMemoryOnArrival` (no behavior change — the live path calls
the same two functions now instead of inlining the formula), so the
tile-memory decay math ("halved per season away") is testable without a
running game, matching `selftest_stun_scaling.py`'s extraction pattern.
Added 9 offline test cases. Verified independently:
`python3 src/RimMandrake/Utils/selftest_colony_visibility.py` → 28/28
passed (up from 19/19). Rebuilt the DLL, 0 warnings/0 errors.

Remaining offline gap: `VisibilityToThreatCurve` in
`ColonyVisibilityRaidPatch.cs` still isn't selftested — it lives in a file
pulling in HarmonyLib/`RimWorld.Planet` types the SelfTest project doesn't
reference, so extracting it cleanly is a separate ~30-60 min increment
(add references or pull the curve into a dependency-free helper). Everything
else remaining is live-quicktest-gated (per the note above) or blocked on
unbuilt Ninefold infrastructure — not boundable offline work this pass.

## FOUNDRY, 2026-09-06: re-checked — nothing new to build offline, still live-gated

Re-verified rather than re-doing: `code_review_status.py check` on all four
Visibility source files (`ColonyVisibilityRaidPatch.cs`,
`GameComponent_ColonyVisibility.cs`, `VisibilityModInit.cs`,
`SelfTest/Program.cs`) — all four CLEAN. The
`VisibilityToThreatCurve`-not-selftested gap noted 2026-09-02 is closed: the
curve now lives on `GameComponent_ColonyVisibility` (no HarmonyLib
dependency), selftestable, per that file's own header comment.
`deploy_custom_mods.py --mod Visibility` (dry run): already in sync, 2
files — no redeploy owed.

Everything genuinely left is gated on a live game session (the threat-point
Prefix and tile-memory round trip have never been observed firing) or on
Ninefold's still-unbuilt Sh'kaar-meter/corpus-letter infrastructure (same
block as `NINEFOLD_ENGINE_M0_1`). Not triggering a solo restart for this one item — batching game-up work
across the queue first. Blocking rather than leaving `doing` so the next
pass can tell at a glance this isn't mid-edit.
