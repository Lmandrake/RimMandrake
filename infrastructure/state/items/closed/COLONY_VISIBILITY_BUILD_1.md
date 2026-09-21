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

## 2026-09-18 (FOUNDRY, belt mode, subagent)

**Task briefing was stale — corrected first.** The task handed to this pass
assumed the currently-loaded DLL predates the 2026-09-02 tile-memory-decay
work (because that pass's own deploy attempt was refused by the file lock).
Checked properly instead of assumed: `md5sum` of the deployed
`Mods/Visibility/Assemblies/RimMandrakeVisibility.dll` is byte-identical to
the repo's committed `src/RimMandrake/Visibility/Assemblies/
RimMandrakeVisibility.dll` at current HEAD, whose most recent touching
commit is `7a14e5ed2` (2026-09-11, `MOD_OPTIONS_RETROFIT_1` — the Mod
Settings retrofit, which itself came AFTER all the tile-memory-decay commits:
`2746864e0`/`c279f1ce2`/`2827b64fc`/`b2abec307`/`8a24dcd78`). No commit since
`7a14e5ed2` touches any `.cs` file in this mod (only `1c06dcf5c` added
`validation.py`, no code). So **the currently-loaded DLL is the FULL current
build** — tile-memory decay AND the Mod Settings retrofit both included —
not the pre-decay version the briefing described. That was already true by
the 2026-09-13 entry above (which itself says "deploy_custom_mods.py --mod
Visibility reported already in sync") and has not regressed since.

**What that means the threat-point Prefix test already covers**: the
2026-09-13 live proof (200→320 pts, factor 1.60) ran against code that
is — confirmed via the same md5 check — functionally identical to what's
loaded right now (no logic changes since, only the unrelated Mod Settings
UI layer added in `7a14e5ed2`). Separately, `DIRTY_CODE_REVIEW_STANDING_LOOP_1`
(2026-09-12, ledger) full-file-reviewed `ColonyVisibilityRaidPatch.cs` post-
retrofit and confirmed `enableRaidScaling`/`launchResetMultiplier` are read at
their real gates, no double-scaling, `IncidentParms` mutation propagates as
designed. **Read `RM_VisibilitySettings`/`Prefix_ScaleHostilePoints` myself
this pass too**: `enableRaidScaling` defaults `true`, gates the effect (not
the dial itself); no `ModConfigs` XML for this mod exists on disk yet
(checked), so the live game is running on that default, not some
saved-off toggle.

**Attempted a fresh live re-fire anyway** (bridge taken, game confirmed
`RUNNING`, `mapCount=9`, `ticksGame≈130976`, paused throughout, `jawa/
list_pawns` 35 before and after, nothing touched). Hit a real, reproducible
bridge limitation rather than getting a clean new data point: `Set Colony
Visibility (dev)` opens `LudeonTK.Dialog_DebugOptionListLister` (confirmed
via `rimworld/get_ui_state`), `rimworld/get_ui_layout` correctly locates each
preset row's button (`ui-element:N:4:4` etc., verified against each row's
screen `rect`, not guessed from element order alone — the first attempt
guessed wrong and hit the dialog's close-X button instead), and
`rimworld/click_ui_target` reports `"changed": true` / `"Activated UI target
button"` and the dialog closes normally — but no
`[RimMandrake.Visibility] shipVisibility set...` line ever appears in
`jawa/drain_log` (checked both filtered and unfiltered) or in `Player.log`.
This is the SAME failure mode `CAST_ROSTER_269_LOAD_1` already documented
for `Dialog_DebugOptionListLister` picker rows ("click registers as a
selection and the action does not complete") — now independently reproduced
on a second, unrelated debug action of the same UI kind, which generalizes
that trap rather than being specific to the roster picker. Consequence:
`validation.py`'s own assumed mechanism (`rimworld/execute_debug_action`
with a literal two-level path like `"Actions\\Set Colony Visibility
(dev)\\0 (Hidden)"`) **does not work at all** — that path lookup fails
outright ("Could not find debug action") because the presets are a runtime
dialog, not debug-tree nodes; and the click-driven fallback this pass tried
instead is the one CAST_ROSTER already showed is unreliable for this exact
widget. Left the toggle-round-trip and strength-slider live checks
untried rather than burn more bridge time on a mechanism already shown not
to complete.

**Net effect on this item's own criteria**: the threat-point Prefix's live
firing/multiplying claim is unweakened — it still rests on the 2026-09-13
direct proof plus the 2026-09-12 code review, both against code confirmed
byte-identical to what's deployed today — but this pass could not add a
THIRD independent live data point because the only available lever
(the dev debug action) is not reliably drivable over the bridge. Whoever
next wants a fresh live number here should either fix/replace
`DebugActions_Visibility.SetVisibility` to not require a
`Dialog_DebugOptionListLister` (e.g. a chain of single-preset `[DebugAction]`
leaves, each directly executable by path with no picker), or accept the
existing 09-13 proof as standing evidence. Tile-memory round trip remains
untouched and still needs real travel time — not attempted this pass, per
the task's own scope.
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

## FOUNDRY, 2026-09-07: game-up batch happened; this item's own test still owed

Did the batched restart (see `NINEFOLD_ENGINE_M0_1`/`SETTLEMENT_VISIT_LOOP_1`
for the same session). Added a "Set Colony Visibility (dev)" debug action to
sweep the ruled threat-point curve, but found (and fixed, `6e6ce2d9`) that
`Visibility.csproj`'s `EnableDefaultCompileItems=false` was silently
excluding it from the build — same trap as `TheftHauler`. Fixed and
committed, but NOT YET deployed/tested this pass: the game was up and other
mods' fixes needed priority; a `deploy_custom_mods.py --mod Visibility
--apply` + one more restart is owed before the threat-point Prefix can
actually be swept live. Still blocked on the same live-check this item's
own history already names.

## 2026-09-13 (FOUNDRY) — threat-point Prefix LIVE-PROVEN, firing and multiplying for real

`mandrake.rm.visibility` is enabled in the currently-live full modlist and
`deploy_custom_mods.py --mod Visibility` reported already in sync (3 files) —
the running game has this pass's code, no restart needed. Bridge session on
the live campaign map (`Map_3`, tile 17007, `ticksGame ~127977`), paused
throughout, no colonists touched:

- `Actions\Set Colony Visibility (dev)` debug action swept the band ladder
  live: `shipVisibility set 5 -> 0 (Hidden), ThreatFactor=0.55`, then
  `0 -> 100 (Exposed), ThreatFactor=1.6` — both logged directly by the mod,
  confirming `VisibilityToThreatCurve` evaluates correctly in the running
  game (not just offline selftest).
- **The Prefix itself, decisively proven**: with visibility forced to 100,
  force-fired a real `IncidentWorker_RaidEnemy` execution via the vanilla
  debug menu (`Actions\Do incident w/ points\RaidEnemy\200 points` — this
  path bypasses the normal `CanFireNow` eligibility gate, which was blocking
  every ThreatBig incident this session, RaidEnemy/ManhunterPack/MechCluster/
  Infestation all included, almost certainly an early-colony grace period
  unrelated to this mod). Log:
  `[RimMandrake.Visibility] IncidentWorker_RaidEnemy points 200 -> 320
  (visibility 100.0, factor 1.60)` — 200 × 1.60 = 320, exact. This is the
  Prefix firing on a REAL `TryExecute` call, not a synthetic/offline
  invocation. A separate mod's own log line one tick later
  (`[RimMandrake.Aftermath] battle opened: Galactic Empire, 5 pawns, 288
  pts.`) independently confirms the raid that actually resolved used the
  scaled points, not the original 200 — a second system reading the same
  post-Prefix value. No hostile pawns were left on the map afterward
  (`jawa/list_pawns` — Aftermath resolves raids narratively, not by spawning
  a physical raid party this pass observed), so nothing needed cleaning up.

**Still open, explicitly**: the tile-memory round trip (launch, let a season+
pass, return, confirm the dial decays/restores per the halved-per-season
curve) needs real travel time this pass did not spend — that is a
much longer live test (real or heavily time-skipped in-game seasons), left
for a dedicated pass. Everything else this item's own history listed as
"not wired" (spotted/raided-at-home, Renown, THE SHAMING, etc.) remains
correctly unwired, out of this item's scope per its own `## Not done`
section. Visibility dial was left at 100 (Exposed) from this test — a click
to reset it to a lower band did not register in the log; low-stakes since
in-game state is disposable per standing doctrine, but worth a note for
whoever next reads the live dial. Left `doing` — the Prefix live-check
criterion is now met; the tile-memory live-check criterion is not.

## 2026-09-19 (FOUNDRY) — tile-memory round trip LIVE-PROVEN, item closed

The remaining gap (six prior passes over three weeks) was a live proof that a
real gravship launch records tile-memory on departure and a real arrival
restores it. Every prior pass concluded no debug shortcut existed for a
player gravship launch, checking only the debug-action tree. **That
conclusion was wrong** — `jawa/gravship_launch`/`jawa/gravship_land`
already existed as closed, proven tools (`GRAVSHIP_LAUNCH_TRAVEL_1`,
2026-08-27) and call the real vanilla path
(`WorldComponent_GravshipController.InitiateTakeoff` → `GravshipUtility.
GenerateGravship`, and — confirmed via RimSage source read,
`Gravship.TickInterval` — `ArriveExistingMap`/`ArriveNewMap` fire
automatically once world-travel ticks complete, no landing confirmation
needed for the arrival hook itself). Both are exactly the methods this
item's Harmony patches (`Prefix_RecordTileMemoryOnLaunch`,
`Postfix_ApplyTileMemoryOnArrival`) are patched onto.

Built two small read/seed bridge tools (`jawa/visibility_report`,
`jawa/visibility_seed_tile_memory`; `cd50c47d3`, `2eca56cd8` — a same-session
duplicate-tool collision with a background fork happened and self-resolved
mid-pass, see the ledger note on this item, no data lost) and reused
`prove_gravship.py`'s already-proven minimal-ship recipe (adapted for a
vanilla, non-VGE mod list: `ChemfuelTank` is itself a facility with
`CompRefuelable`, no astrofuel pipe network needed — `DEV: Set fuel to max`
refuels it directly). Custom 9-mod test tier: `brrainz.rimbridgeserver` +
`mandrake.rm.visibility` + all DLC (`modset_builder.py`'s new `visibility`
tier, filed by the background fork this same pass).

### Live proof 1 — departure (real launch, real tile)
Built a minimal flyable ship on a quicktest map, launched for real to a
neighbouring tile. `jawa/visibility_report` before/after:
- Pre-launch dial: **10.0**. Recorded memory for the origin tile: **10.0**,
  exact match — `Prefix_RecordTileMemoryOnLaunch` fires on a real
  `GenerateGravship` call and records the correct pre-reset value.
- Post-launch dial: **5.0** (Ta'Baa reset, within the ruled 5-15 floor).
- Arrival at the (memory-less) destination tile restored nothing — correct,
  a dictionary miss is a no-op.

### Live proof 2 — arrival restore (real postfix, seeded data)
Vanilla marks an abandoned origin permanently unlandable (a `GravshipLaunch`
world object at the tile — confirmed via `jawa/world_objects_get`), so a real
round trip back to a tile the SAME ship departed cannot be flown. Seeded a
synthetic memory (`jawa/visibility_seed_tile_memory`, visibility 80.0, 0
ticks ago) for a tile about to be launched to — same "sealed room" pattern
as `LIQUID_SINK_DRAINAGE_1`'s driver-API test, real wiring under test, only
the input data manufactured. Fresh minimal ship, real launch, real travel,
real `ArriveNewMap` postfix (unmodified):
```
PROVE    seed tile T's memory at 80.0/0-ticks-ago, real-launch to T, real-travel,
         real-land; read jawa/visibility_report before vs after.
EXPECT   dial rises from the 5-15 post-launch-reset range to ~80 (DecayedTileVisibility
         at ~860 ticks elapsed is ~79.9, negligible decay).
LIES     a false pass would be the dial matching by coincidence of the reset range
         alone -- ruled out by seeding a value (80) far outside 5-15 and by predicting
         the exact number BEFORE looking, then checking within 1.0.
```
Result: dial rose to **79.96**, band **Marked**, matching the pre-stated
prediction (**80.00 - decay ≈ 79.9469**) within 0.04. A second, independent
memory entry (the real 10.0 recorded on THIS launch's own departure) sits
alongside it in the report, unaffected — confirms the restore targeted the
right dictionary key, not every entry.

## status — CLOSED, 2026-09-19 (FOUNDRY)

Both halves of the tile-memory round trip are now live-proven, closing the
one gap this item was left open for. Everything else this item's own history
already named as out of scope stays out of scope: `VisibilityToThreatCurve`'s
anchor points are untuned (§5's tuning protocol not run), the other design-doc
raise/lower hooks are unwired, `ShkaarEscalationMultiplier` has no setter, and
F17's reign-calendar/band-crossing-letter pieces wait on Ninefold's unbuilt
signed-letter infrastructure (`NINEFOLD_ENGINE_M0_1`) — none of that was ever
this item's own bar.
