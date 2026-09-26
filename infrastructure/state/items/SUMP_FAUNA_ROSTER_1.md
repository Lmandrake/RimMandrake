# SUMP_FAUNA_ROSTER_1 — build the 9 invented Sump fauna defs

Source: `design/Jawa/worldbuilding/biomes/sump_fauna_roster_2026-09-24.md` (9
rows, all `RM_` tier, franchise-free — the doc's own collision sweep found 0
hits on any of the new names anywhere in the repo, and this pass independently
re-confirmed 0 hits for existing art on all 9).

## Built this pass

- `src/RimMandrake/TheSump/Defs/ThingDefs_Races/RM_SumpFauna.xml` — 9 new
  race+PawnKindDef pairs: `RM_SumpMouse` (real def, replaces the retired
  `RUT_Placeholder_SumpMouseRace`/`RUT_Placeholder_SumpMouse`), `RM_Gulveth`,
  `RM_Thrummel`, `RM_ThrummelWarden`, `RM_ThrummelBroodmother`, `RM_Brommet`,
  `RM_Dredgel`, `RM_Skarrid`, `RM_Skellarn`.
- `src/RimMandrake/TheSump/Defs/ThingDefs_Items/RM_SumpFaunaItems.xml` —
  harvested goods: `RM_Leather_TarCured` (gulveth), `RM_SkarridHide`,
  `RM_BrommetWool`, `RM_ThrummelChitin`, `RM_DredgelChitin`,
  `RM_SkellarnChitin`, `RM_Seepwax`.
- `RM_TheSump_Biome.xml`: `<wildAnimals>` gains 5 new rows —
  `RM_SumpMouse` 0.8, `RM_Brommet` 0.4, `RM_Dredgel` 0.2, `RM_Skarrid` 0.25,
  `RM_Skellarn` 0.15. The 4 existing donor rows (`AA_TarGuzzler`,
  `AA_Bumbledrone`, `AA_BumbledroneHierophant`, `AA_BumbledroneQueen`) are
  UNCHANGED — see "Eviction scope" below.
- Retired the placeholder mouse: deleted
  `Defs/PawnKindDefs/RUT_Placeholder_SumpMouse.xml` and
  `Defs/ThingDefs_Races/RUT_Placeholder_SumpMouseRace.xml`; updated
  `RUT_ThinkTree_SumpMouseWander.xml`'s header comment to name the real
  `RM_SumpMouse` (the ThinkTreeDef mechanism itself is untouched — it gates
  on `RM_DreadAvoidWanderExtension`'s presence, not on a defName, so no
  functional change was needed).

## Eviction scope — NOT executed this pass

The design doc's own §7 marks replacing today's 4 donor rows with
`RM_Gulveth`/`RM_Thrummel`/`RM_ThrummelWarden`/`RM_ThrummelBroodmother` as
"PROPOSED for this biome's own sitting... executed by nobody here," under the
owner's standing evictions-are-stopped ruling (2026-09-22: "Let's stop
evictions right now... I don't think we should be having rules here. This is
a human review process issue."). All four replacement defs are built in full
and content-complete, but `RM_TheSump_Biome.xml`'s existing donor
`wildAnimals` rows are untouched. Whoever runs the Sump's own biome sitting
rules on evicting them. `RM_SumpMouse` is the one exception — its placeholder
was never wired into wildAnimals at all and was explicitly built as a
mechanism stub awaiting "the roster pass" (its own header), so replacing it
is this item's named job, not an eviction of anything live.

## A pre-existing, related-but-distinct construct found this pass

`src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_Tarred_Solvents.xml`
(built under `SUMP_TAR_NASTINESS_1`, still `doing`) already ships a
`RUT_ThrummelSeepwax` resource, explicitly deferring "the thrummel
creature/hive itself... awaiting its real source, the hive raid" to this
roster. That def lives in the Utinni CAMPAIGN layer, and `RM_TheSump` (the
free RM-tier mod) may not depend on it — the free mod must stand rich alone
(Q11a) and RM tier never depends on RUT tier. So the thrummel family's own
butcherProducts here reference this item's own `RM_Seepwax`/
`RM_ThrummelChitin` instead, a separate def. Reconciling the two economies
(e.g. a campaign-side raid-loot patch that also awards `RUT_ThrummelSeepwax`)
is follow-on work for whoever next picks up `SUMP_TAR_NASTINESS_1` or the
Utinni layer wiring — not this item's scope, and not touched here (that
item's own files were left alone).

## Deferred — mechanism work, not fauna defs (roster doc's own status column)

Mirrors `SUMP_FLORA_ROSTER_1`'s precedent: each of the following ships as an
ordinary, fully-authored wild animal (or built-but-unwired def) with no
behaviour beyond vanilla defaults; the bespoke mechanism is real follow-on
Sump-mechanics work, not a gap in this item:

- Sump-mouse / skellarn free tar-crossing on landing — one shared
  implementation is owed (small NEW patch or stat trick; UNMEASURED which is
  cheapest, per the roster doc's own note).
- Thrummel mound + defend-radius comp — vanilla `Hive`/`CompSpawnerPawn`
  reskin feasibility is UNMEASURED (engine question, flagged for the
  Desktop).
- Skarrid as a mobile dread-field registration (the dread field itself
  already exists; a moving source is small NEW).
- Dredgel's dig-site attract-mode wander bias (the shipped
  `RM_JobGiver_DreadAvoidWander` is the avoid-mode cousin this needs an
  attract-mode sibling of).
- Skellarn's flying animation flip-book frames (never blocks flight; the
  flight STAT mechanism is fully wired this pass).

Whoever picks up Sump fauna mechanics next should read
`sump_fauna_roster_2026-09-24.md`'s own mechanism roll-up rather than
re-deriving these.

## Wrissen — confirmed excluded

The roster doc's own text records the wrissen (a proposed dormant tar-swarm
row) as **deleted under the owner's typed ruling, 2026-09-24**: "Only truly
ancient machines or assailants. No normal life can survive otherwise." The
doc states "git holds the deleted prose" — it is not present anywhere in the
current doc, this build, or any roster/fact file this pass checked
(`infrastructure/state/facts/rosters/the_sump.json` does not exist; no other
roster file names it). Nothing to remove.

## Flight — RM_Skellarn

Real flight per the standing rule (owner, 2026-09-19) and his own typed
ruling on this creature (2026-09-24: "really long spikey legs so when it
lands it can still move through the tar"): `MaxFlightTime` 10,
`FlightCooldown` 5 (statBases — the actual `Pawn_FlightTracker.CanEverFly`
switch), `flightStartChanceOnJobStart` 0.12, `flightSpeedFactor` 2.2,
`canFlyIntoMap` true, `canLeaveMapFlying` deliberately omitted (it lairs, per
its one-home note). No `flyingAnimationFramePathPrefix`/`-FrameCount` — frames
are owed later and must never block flight. Not live-tested (forbidden
without the owner present, said three times this session) — verified as
correct XML/def construction against the shipped, working `RM_Skerrel`
(Greentide) and `RM_FleetFlier` (TheForge) precedents in this same repo,
which use the identical field set.

## Art

Searched `infrastructure/artpipe/registry.jsonl`/`done/`/`_artsrc/` for all 9
names — 0 hits (sanity-probed against "graniteslug", 30 hits, so the search
itself is live). Queued 27 `fill_queue.py` jobs (9 creatures ×
south/east/north facings, `infrastructure/artpipe/art_lists/sump_fauna.csv`,
`rimflow_item_id SUMP_FAUNA_ROSTER_1`). `RM_SumpFauna.xml` is `DEPLOY_HOLD`'d;
`RM_SumpFaunaItems.xml` needs no hold (every material reuses a
core-guaranteed vanilla icon or a LeatherBase/WoolBase default, zero new
art). Note: an earlier filing pass this same session used non-matching job
ids (`sumpfauna_<name>`) and was deleted before any worker claimed it,
refiled under ids matching each def's own texPath basename
(`RM_<Name>_<facing>`) — `registry.jsonl` (append-only) may still carry a
handful of orphaned `queued` events under the old, abandoned ids; harmless,
but a future search should trust the `RM_<Name>` ids as current.

## Verify

`validate_patch.py` run against the live Mods + Workshop content roots; see
commit for the result at time of close.
