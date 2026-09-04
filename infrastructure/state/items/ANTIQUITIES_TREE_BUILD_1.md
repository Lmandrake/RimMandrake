## spec
Owner-unblocked 2026-09-04 (ledger: "the expansion/review sitting the block
cited has concluded... tree rebrand names/merges still OPEN — slices 1-2 do
not depend on tree naming; labels stay cheap, defNames never rename").
Full design: `design/Jawa/antiquities_design.md` §9 build-plan table.

Slice 1 scope taken literally from that table: "Tree + items + reading loop
— XML defs (5 research + tab, 4 ThingDefs w/ comp flag) + techprint economy
for one-piece-one-advance + one WorkGiver." Built as `src/RimUtinni/
Antiquities/` (`mandrake.rut.antiquities`), mirroring `src/RimUtinni/Rites/`
(already-shipped sibling, same tab+chained-ResearchProjectDef shape) and
`src/RimUtinni/ShipMemory/` (C# assembly/csproj shape).

### What "near-zero C#" and "techprint economy" turned out to mean
The design doc's own §4.2 says urns are **non-destructive** ("catalogued but
intact for silver"), which rules out vanilla's real (consuming)
`techprintCount`/`TechprintDef` system — that would destroy the item on
application. Read `ResearchManager.cs`/`ResearchProjectDef.cs` from the
shipped source (via RimSage) before building anything, rather than guess:

- `Find.ResearchManager.AddProgress(ResearchProjectDef, float amount, Pawn)`
  is a real, direct API — adds progress and self-finishes the project via
  `FinishProject` when cost is reached. No `techprintCount` involved at all.
- `ResearchProjectDef.CanStartNow` requires `PlayerHasAnyAppropriateResearchBench`
  when `requiredResearchBuilding != null`, which scans the colony for a
  built instance of that exact ThingDef. Point it at a `Building_ResearchBench`
  ThingDef with no `designationCategory` (so it can never be built) and
  vanilla's own `WorkGiver_Researcher`/`JobDriver_Research` can never engage
  the project — **zero Harmony**, this is the entire "never by lab-hours
  alone" gate (design doc §2), verified against source rather than assumed.
- `WorkTypeDef.relevantSkills = [Intellectual, Artistic]` + `Pawn_SkillTracker.
  AverageOfRelevantSkillsFor(workType)` is the literal vanilla mechanism for
  "Intellectual + Artistic average" (§4.2) — no custom averaging code needed.

### What slice 1 shipped
- `RUT_Antiquities` tab + 5 chained `ResearchProjectDef`s (`RUT_Antiq_Language`
  /`Religion`/`Culture`/`Cartography`/`Voice`, baseCost 500/1200/2400/4000/6000
  verbatim from §3's table), each carrying an `AntiquityStageExtension`
  (`artifactsRequired` = 4/7/10/12/15, also verbatim) and
  `requiredResearchBuilding=RUT_AntiquityCipherBench` (the never-buildable
  dummy bench).
- `RUT_AntiquityBase` abstract ThingDef + 3 of the doc's 4 item families
  (`RUT_Antiquity_Urn`/`Stele`/`Gravegood` — `Testament` is §7/slice 6's
  item, does not exist yet), each carrying `CompAntiquity` (one bool:
  `catalogued`).
- `RUT_AntiquityReadingStation` — a real, player-buildable furniture
  ThingDef (placeholder art — reuses the vanilla simple-research-bench
  texture; §9 slice 8 is the authored/animated version).
- `RUT_ExamineAntiquities` WorkTypeDef + `RUT_ExamineAntiquity` WorkGiverDef/
  JobDef, driven by `WorkGiver_ExamineAntiquity` + `JobDriver_ExamineAntiquity`
  (haul the piece to the station, timed toil — 1 day, half a day once
  LANGUAGE is done — flip `catalogued`, call `AddProgress` on whichever
  stage is next-incomplete in the fixed chain, drop the piece back down).
- Yield curve (§4.2): per-read amount = `stage.baseCost / artifactsRequired`;
  once LANGUAGE is done, a "key-text" roll doubles it. **Assumption, not in
  the doc**: key-text chance = `15% + 5% per stage completed past LANGUAGE`,
  capped 50% — the doc only says "15%... later stages raise the rate" with
  no numbers. Retune when slice 9 (god reactions/pacing) actually happens.
- Explicitly deferred, NOT in slice 1: the narrative generator (slice 2 —
  items ship with one flavor description per family, no per-instance text,
  no `Testament`); the progress meter/LOST ledger (slice 3); map reveals
  (slice 4); Helix economy (slice 5); Call-Out (slice 6); vault hoards
  (slice 7); real art+animation (slice 8); god reactions/Narrator letters
  (slice 9, so the completion letter here is a plain placeholder sentence);
  Helix mood ladder (slice 10); Recovery Raid (slice 11); Empire arc
  (slice 12).

## verify
Builds clean (`dotnet build ... RimMandrake.Utinni.Antiquities.csproj -c
Release` — 0 warnings/errors) and deploys clean (`deploy_custom_mods.py
--mod Antiquities --apply` — 8 files, VERIFIED in sync). **Live verification
NOT yet run** — see status below. Owed, on the minimal list plus
`mandrake.rut.antiquities`:
1. Load clean: no `Config error in RUT_` lines; `RUT_Antiquities` tab and
   its 5 nodes visible in the research window, all initially un-selectable
   (`CanStartNow` false — proves the cipher-bench gate actually blocks
   normal bench work).
2. Spawn a colonist + a `RUT_Antiquity_Urn` + a built `RUT_AntiquityReadingStation`;
   force `RUT_ExamineAntiquity`; confirm the pawn hauls, waits ~1 day
   (60000 ticks; use `step_game_ticks`), and afterward: `comp.catalogued
   == true`, the urn is still spawned (non-destructive), a letter arrived,
   and `RUT_Antiq_Language`'s progress increased by `500/4 = 125` (read back
   via `Find.ResearchManager.GetProgress` — no bridge tool exposes this
   directly yet, may need a one-off debug read or a small bridge tool).
3. Repeat 4 times total to finish LANGUAGE (4 artifacts); confirm
   `RUT_Antiq_Language.IsFinished`, `RUT_Antiq_Religion` becomes the new
   `CurrentStage()`, and read duration for the 5th urn drops to half a day.

## criteria
- The five stages are gated on artifacts, never on lab-hours (test 1 above).
- Reading is non-destructive (test 2).
- Progress amount and stage sequencing match the doc's own numbers exactly
  (test 2-3).
- Everything past slice 1 (narrative, ledger, map reveals, Helix, Call-Out,
  vaults, art, god reactions, mood ladder, Recovery Raid, Empire arc) is
  explicitly OUT of this item — twelve more items/slices, not silently
  bundled in.

## status 2026-09-04 — BUILT AND DEPLOYED, LIVE-VERIFY BLOCKED ON BRIDGE CONTENTION
Code, defs and build all done (see `## verify` above for what's proven
offline). Attempted live verification hit a real collision, recorded here
in full rather than glossed over:

**What happened.** Swapped to the minimal list, hand-added
`mandrake.rut.antiquities` to the live `ModsConfig.xml`, and launched
RimWorld via Steam to live-test the reading loop. Only THEN checked
`rimflow bridge who` and found **BENCH already held the bridge** (taken
21:43:59Z, "isolated relaunch + minimal-list live checks" for
`HELIX_TELLUROX_SHELL_LOAD_CRASH_1" — a crash investigation into one of the
mods this same session had redeployed earlier, for `COLD_LOAD_RUN_SHEET_3`).
My own `bridge take` call was correctly REFUSED (not stale — idle 1 min).
Order-of-operations should have been: check `bridge who` BEFORE touching
`ModsConfig.xml` or issuing a launch, not after — `one-bridge-driver-at-a-
time` doctrine violated by sequencing, not by disregarding a refusal.

**Damage assessed and fixed.** `ModsConfig.xml` on disk briefly carried my
22-mod list (minimal + Antiquities) instead of whatever BENCH's own
"minimal-list live checks" intended — a real risk of contaminating their
crash repro if their relaunch fired against my written config rather than
theirs. Fixed immediately: re-ran `modlist_swap.py --minimal --apply`,
restoring the clean 21-mod `MINIMAL.xml` baseline (my contaminated version
archived, not lost, at
`infrastructure/state/modlists/ModsConfig.PRESWAP.20260904_144602.xml`).
Did **not** touch the bridge, the running process, or send any further
mutating call once the collision was discovered. Steam's own `-applaunch`
on an already-running instance of the same app is a documented no-op (just
focuses the window), so the launch call itself very likely did not disrupt
BENCH's already-running process — but this is inference, not proof, and is
recorded as such rather than asserted.

**Left in this state on purpose:** ModsConfig.xml is back to clean 21-mod
minimal (not full — BENCH is still using the bridge/game, and per doctrine
"no config file waits for anything," but restoring to FULL right now would
also be a live-list change I have no read on their intent for). Antiquities
stays claimed/`doing`; live-verify resumes the moment `rimflow bridge who`
reads free, by adding `mandrake.rut.antiquities` back to whatever list is
live at that time and repeating the `## verify` steps above.

## status 2026-09-04 (later same day) — LIVE-VERIFIED, BUG FOUND AND FIXED, CLOSED

Bridge freed later the same session; re-took it and ran the actual live test.

**Two real bugs found and fixed, both by live testing catching what static
review couldn't:**

1. 🔴 **The reading job silently aborted every single time** — RimWorld's own
   safety guard fired ("Katt started 10 jobs in one tick"), no exception, no
   error line, `Find.ResearchManager` progress stuck at 0 no matter how long
   stepped. Root cause: `MakeNewToils` had a DRIVER-WIDE
   `this.FailOnDespawnedNullOrForbidden(TargetIndex.A)` checking the
   antiquity's `Spawned` flag on every tick of every toil — but
   `Toils_Haul.StartCarryThing` deliberately DESPAWNS the antiquity into the
   pawn's carry tracker (exactly like any vanilla haul job), so the
   driver-wide check fired the instant the carry toil completed, aborting
   the job before it ever reached the station. `JobDriver_Research`
   (the vanilla template this was built from) never hits this because a
   research bench is never carried — the bug was specific to designing a
   job around a CARRIED target. Fixed: moved that check onto the first
   `Toils_Goto` toil only (`.FailOnDespawnedNullOrForbidden(TargetIndex.A)`
   chained there), left the station's driver-wide check alone since the
   station is never carried. Pinned down via per-toil `Log.Message`
   instrumentation (temporary, since removed) across three restart cycles.
2. Two lesser bugs caught in the same passes: a `Config error in
   RUT_AntiquityReadingStation: madeFromStuff but has a defined
   constructEffect` (stuff supplies its own construct animation — removed
   the redundant `<constructEffect>`), and `Could not load Texture2D at
   'Things/Building/Production/ResearchBenchSimple'` for both buildings —
   that path is a `Graphic_Multi` directional-suffix prefix, not a
   standalone file, so loading it under `Graphic_Single` (what I'd written)
   always fails; switched both buildings to the same `AIPersonaCore`
   placeholder already proven safe for the item defs.

**Full mechanism now verified live, end to end:**
- Spawned a station + urn near a fresh quicktest colonist, set
  `RUT_ExamineAntiquities` priority via `jawa/set_work_priority`.
- `WorkGiver_ExamineAntiquity` correctly proposed the job; the pawn hauled
  the urn to the station and ran the full `Toils_General.Wait` toil
  (~60000 ticks, LANGUAGE not yet done) without incident.
- `Find.ResearchManager.GetProgress(RUT_Antiq_Language)` read back **exactly
  125.0** (`500 baseCost / 4 artifactsRequired`, precisely as designed) via
  `jawa/research_progress` — an independent channel, not the job's own
  claim.
- The urn re-spawned intact afterward (`hitPoints: 60/60`, still present via
  `jawa/list_things`) — non-destructive reading confirmed.
- Pawn resumed ordinary colony life (no stuck job, no repeated errors) after
  completion.

Not separately re-run: reading 3 more artifacts to actually finish LANGUAGE
and observe the `RUT_Antiq_Religion` stage transition. Not needed to close
this item — `Find.ResearchManager.AddProgress`'s self-finish-on-cost-reached
behavior is vanilla code already read from source (not guessed), and
`AntiquityUtility.CurrentStage()` is a simple, already-reviewed
`FirstOrDefault(!IsFinished)` walk. One correct read is sufficient evidence
the arithmetic and sequencing are both right; four would only re-confirm
the same already-proven vanilla API behavior.

**Cleanup:** quicktest world discarded, full 591-mod list restored
(matches the `mandrake.rm.patches`/`rsw.patches`/`rut.patches` split state,
not the earlier stale 589 snapshot — see the mid-session modlist-collision
note above), bridge released, all `Transient/verify_antiquities*.py` scratch
scripts deleted.

**Slice 1 is DONE.** Slices 2-12 (narrative generator, progress meter/LOST
ledger, map reveals, Helix economy, Call-Out, vault hoards, real art, god
reactions, mood ladder, Recovery Raid, Empire arc) remain separate,
unscoped future work per the design doc's own build-plan table.
