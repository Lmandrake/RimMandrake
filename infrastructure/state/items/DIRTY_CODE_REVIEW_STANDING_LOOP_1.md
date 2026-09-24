## the loop

Standing FOUNDRY full-file code-review loop, self-continuing. Pick a reachable file
not yet recorded CLEAN in `infrastructure/state/CODE_REVIEW_STATUS.json`, full-file
review it (never diff-scoped until it's CLEAN once), fix real bugs found, mark-clean
files with nothing significant found. Protocol: CLAUDE.md's "Code isn't clean until
a review says so" section.

🔴 **Always survey with `code_review_status.py list --show-untracked`, never bare
`list`.** Bare `list` silently omits every file that has never been given a status
entry at all — this is documented behavior (see the tool's own help text and
`LESSONS_INBOX.md`'s 2026-09-13 entry) but waves 1-43 of this exact loop didn't apply
it, so "0 DIRTY" was reported as a milestone multiple times while 346 never-entered
files sat invisible. Wave 44 (2026-09-24) rediscovered this the hard way. A future
curation pass should fold this into a skill; until then, this line is the fix.

## PAUSED — owner, 2026-09-20

Verbatim: **"Stop all clean/dirty code review until Wednesday 3pm token reset please."**

⛔ **Do not spawn or resume this loop — no mark-clean pass, no full-file review pass,
no bug-fix-under-this-item pass — before 2026-09-23 15:00.** This applies across a
reboot/new session; it is not scoped to one window's lifetime.

Progress so far today before the pause: two waves, 6 files marked CLEAN
(`RM_CompGrappler.cs`, `RM_CompProperties_Grappler.cs`, `RM_Hediff_Grappled.cs`,
`RM_MapComponent_LivingProduce.cs`), 2 real bugs found and fixed (`RM_LiquidTankUtility.cs`
closure-variable bug, `PyrelandsFireFront.cs` off-by-one on even fire-front widths — both
commits already pushed, see ledger). A third wave was launched and killed mid-start on
the owner's word — zero commits from it, nothing to clean up.

Resume normally after 2026-09-23 15:00 — this note is the only gate; no other ruling
changed.

## Wave 3 — 2026-09-24, first wave after the gate

Reviewed 4 files, full-file, none previously recorded in
`CODE_REVIEW_STATUS.json`: `RM_LiquidTankUtility.cs` and
`PyrelandsFireFront.cs` (the two files whose bugs were fixed in wave 2, but
which had never been mark-clean'd — re-reviewed to confirm the fixes hold
and nothing else was wrong), plus `RM_JobDriver_FilterFeedTerrain.cs` and
`CompContactVenom.cs` (first-time review). All four confirmed reachable via
their `.csproj` `<Compile Include>` entries. No new bugs found; no fixes
needed this wave. All 4 marked CLEAN, commit `7eb44027e`, pushed.

Next wave: pick from the remaining ~175 reachable `.cs`/`.py` files never
entered in `CODE_REVIEW_STATUS.json` — candidates surveyed but not yet
reviewed this pass include `RM_CompDungSeeder.cs`, the `SeaShores/Source/`
cluster, `GizkaStowaway/Source/` cluster, and the `modcheck/` Python tools
(`doctor.py`, `judge.py`, `northstar.py`, `walklint.py`). The many
`validation.py` files across mod folders were left unreviewed this wave —
they are likely near-identical boilerplate per mod and worth a quick
sampling pass rather than one-by-one full review.

## Wave 4 — 2026-09-24

Reviewed 4 files, full-file, none previously recorded in
`CODE_REVIEW_STATUS.json`: `RM_CompDungSeeder.cs` (desert megafauna dung/seed
mechanic), `RM_SeaShoreExtension.cs` + `RM_SeaShoreUtility.cs` (SeaShores
mod's DefModExtension and its sea/terrain/fishing-band resolution logic),
and `HediffComp_GizkaFecundity.cs` (GizkaStowaway's per-pawn breeding hediff).
All four confirmed reachable via their `.csproj` `<Compile Include>` entries
(`RM_CreatureBehaviors.csproj`, `RM_SeaShores.csproj`,
`RimMandrakeGizkaStowaway.csproj`). Traced `RM_SeaShoreUtility`'s ambiguous-
terrain dedup logic (a terrain claimed by two seas gets added to an
`ambiguous` set and stripped from `terrainToSea` only after the full
registration pass, so partial removal mid-loop was checked and is not a bug)
and its tie-break in `PrimarySeaFor` (defName-ordinal tie break, verified the
`best == null` first-candidate path is unreachable with count 0 since a
biome always counts itself as its own neighbour). No bugs found in any of
the 4; no fixes needed this wave. All 4 marked CLEAN, commit `04cb87e13`,
pushed.

Next wave: the `SeaShores/Source/` (`RM_SeaShoresHarmony.cs`,
`RM_SeaShoresMod.cs`, `RM_SeaShoresSettings.cs`,
`RM_TileMutatorWorker_SeaCoast.cs`, `RM_WorldComponent_SeaShoreHealer.cs`)
and `GizkaStowaway/Source/` (`MapComponent_GizkaInfestation.cs`,
`RSW_GizkaHarmonyPatches.cs`, `RSW_GizkaPopulation.cs`,
`RSW_GizkaSettings.cs`, `RSW_GizkaStowawayManager.cs`) clusters both still
have files remaining; the `modcheck/` Python tools and the `validation.py`
sampling pass are both still untouched.

## Wave 5 — 2026-09-24

Reviewed 5 files, full-file, none previously recorded in
`CODE_REVIEW_STATUS.json`: the remaining `SeaShores/Source/` cluster —
`RM_SeaShoresHarmony.cs` (the Harmony patch set: `CoastDirectionAt`
postfix, `WorldGenStep_Mutators.TryAddMutator` prefix reached via
`AccessTools.Method` since it's private static, `WaterBody.SetFishTypes`
postfix, and a `FishingUtility.GetCatchesFor` transpiler), `RM_SeaShoresMod.cs`,
`RM_SeaShoresSettings.cs`, `RM_TileMutatorWorker_SeaCoast.cs`, and
`RM_WorldComponent_SeaShoreHealer.cs`. This completes the whole
`SeaShores/Source/` cluster (`RM_SeaShoreExtension.cs` and
`RM_SeaShoreUtility.cs` were already marked clean in wave 4). All 5
confirmed reachable via `RM_SeaShores.csproj` `<Compile Include>` entries.

Traced the transpiler's IL rewrite closely since it's the highest-risk code
in the cluster: it replaces the `callvirt Map.get_Biome()` instruction
in-place with `ldarg.1` (leaving the already-pushed `Map` reference on the
stack instead of consuming it) then appends a `call` to
`RM_SeaShoreUtility.FishBiomeFor(Map, IntVec3)` — stack ends up
`[Map, cell]` matching the static method's signature, which is correct and
is why the rewrite is done in-place rather than as an insert (preserves
labels/exception-block targets on that instruction). Also checked the
`SetFishTypes` postfix's early-return ordering (`ext == null || ...`
short-circuits before `sea.fishTypes` is dereferenced when `sea` itself is
null) and the `WorldComponent`'s heal pass for idempotency (skips any tile
already wearing a `Coast`-category mutator). No bugs found in any of the 5;
no fixes needed this wave. All 5 marked CLEAN, commit `477c30d53`, pushed.

Next wave: `GizkaStowaway/Source/` cluster (`MapComponent_GizkaInfestation.cs`,
`RSW_GizkaHarmonyPatches.cs`, `RSW_GizkaPopulation.cs`,
`RSW_GizkaSettings.cs`, `RSW_GizkaStowawayManager.cs` —
`HediffComp_GizkaFecundity.cs` was already marked clean in wave 4), the
`modcheck/` Python tools (`doctor.py`, `judge.py`, `northstar.py`,
`walklint.py` all confirmed DIRTY/never-entered this wave; `status.py` is
already CLEAN; `cli.py` is DIRTY again — content changed since its
2026-09-20 clean mark, so it needs a fresh full-file review, not a diff
review), and the `validation.py` sampling pass, all still untouched.

## Wave 6 — 2026-09-24

Reviewed 3 files, full-file, none previously recorded in
`CODE_REVIEW_STATUS.json`: `judge.py` (grades run screenshots against a
mod's must-show/cannot-show checklist via `claude -p`, one narrow
yes/no/unjudgeable question per line — verified `passes()`'s polarity logic,
that UNJUDGEABLE never counts as a pass, and that `visual_all_green([])`
returning `True` is the documented "no visual floor for this mod" case, not
a bug), `northstar.py` (parses a walk's `## north star` section, distinguishes
`### must show` from `### cannot show` checklists, and computes the
content-hash that gates VALIDATED vs DRAFT — traced `_checklists`'s
continuation-line handling, `_canonical`'s header-stripping, and confirmed
`parse`/`record_validation` hash the same line set so the two never
disagree; also confirmed this file already returns dict access (`ns["must_show"]`)
throughout, not `getattr`, so it does not carry the confident-wrong-zero bug
CLAUDE.md warns about elsewhere), and `walklint.py` (checks every identifier
a validation walk names still exists — traced the `walklint-ok` escape
hatch's off-by-one-looking `{i, i+1}` math against its own docstring and
confirmed it's correct: a marker on line `i` suppresses a finding on `i`
itself (inline use) or `i+1` (marker-on-the-line-above use)). Confirmed
reachable: `judge.py`/`northstar.py` imported by `runner.py` and `cli.py`
(`northstar.find_walk`/`parse`/`record_validation`, `judge.judge_run`/
`visual_all_green`), `walklint.py` imported by `cli.py`, `doctor.py` and
`floor.py`. No bugs found in any of the 3; no fixes needed this wave. All 3
marked CLEAN, commit `c504d3c64`, pushed.

Next wave: `GizkaStowaway/Source/` cluster (5 files, unchanged from wave 5's
note), `doctor.py` (500 lines, never-entered) and `cli.py` (323 lines,
re-dirtied since its 2026-09-20 clean mark — needs a fresh full-file pass,
not diff-scoped) in `modcheck/`, and the `validation.py` sampling pass — all
still untouched.

## Wave 7 — 2026-09-24

Reviewed 4 files, full-file: `cli.py` (323 lines, the modcheck CLI entry
point — re-dirtied since its 2026-09-20 clean mark at `9ff1457ee`, so this
was a fresh full-file pass, not diff-scoped; confirmed the previously-fixed
"stored field" bug (wave notes / CLAUDE.md) is still fixed — `status` prints
re-derive each row via `northstar.find_walk`/`status.check_or_orphaned`
rather than trusting `entry["status"]`), `doctor.py` (500 lines, never
entered — the five-registry cross-check tool; traced `check_walks`'s
subject-collision logic against `_duplicate_features`/`_is_real_collision`
and confirmed the FAIL/WARN split and the "raise loudly on empty read" guard
in `run()` match CLAUDE.md's own traps this module documents itself as built
against), and two of the `GizkaStowaway/Source/` cluster —
`RSW_GizkaPopulation.cs` (the stowaway-lineage lookup/spawn helper — donor
defName fallback via `GetNamedSilentFail`, `CountOnMap`/`ListOnMap` counting
lineage via the fecundity hediff rather than species) and `RSW_GizkaSettings.cs`
(Mod Settings + `RSW_GizkaDonorTuning`, which captures the post-patch donor
baseline once and always rescales from that capture so repeated `Apply()`
calls don't compound). Confirmed reachable: `cli.py` is the modcheck CLI
entry point itself (`if __name__ == "__main__"`); `doctor.py` imported by
`cli.py`'s `doctor` subcommand and by `selftest_doctor.py`; both `.cs` files
listed in `RimMandrakeGizkaStowaway.csproj`'s `<Compile Include>`. No bugs
found in any of the 4; no fixes needed this wave. All 4 marked CLEAN, commit
pending below, pushed.

Next wave: `GizkaStowaway/Source/` cluster has 3 files left
(`MapComponent_GizkaInfestation.cs`, `RSW_GizkaHarmonyPatches.cs`,
`RSW_GizkaStowawayManager.cs`), and the `validation.py` sampling pass across
mod folders is still untouched.

## Wave 8 — 2026-09-24

Reviewed 4 files, full-file: two of the three remaining
`GizkaStowaway/Source/` files — `MapComponent_GizkaInfestation.cs` (the
stage-escalation MapComponent: verified `StageFor`'s threshold ordering
holds for any `cap >= 4` — the `Max(const, round(cap*fraction))` floors keep
Plague > Infestation > Underfoot monotonic at every cap, including the
`cap < 4` clamp case; verified the chewing mechanism's
`Rand.MTBEventOccurs(ChewMtbTicksPerGizka / here, 1f, CheckIntervalTicks)`
call uses the `mtbUnit=1f` pattern correctly since the constant is already
expressed in raw ticks; verified stage step-down is silent-by-design,
matching the class docstring's "steps down so the warning can be
re-earned") and `RSW_GizkaHarmonyPatches.cs` (all 5 Harmony hooks — traced
every `GameComponent_GizkaStowaway.Notify_*` and
`RSW_GizkaPopulation.IsStowawayGizka` call target to its real method in
`RSW_GizkaStowawayManager.cs`/`RSW_GizkaPopulation.cs`, confirmed the
cull-guilt patch is correctly a Prefix rather than Postfix per its own
docstring reasoning — `Pawn.Kill` despawns before Postfix would run, so
Prefix is the only point `victim.Position` is still valid).

Plus a first pass at the **validation.py sampling question wave 3 raised**:
read `Pyrelands/validation.py` (257 lines) and `SWBestiary/validation.py`
(241 lines) whole, and separately confirmed all 55 `validation.py` files
across the repo have **distinct** content (a full MD5 pass found zero
duplicate files — the illusion of duplication in `code_review_status.py
list`'s output is the informational `sha` field, which is the **commit**
they were bulk mark-clean'd in, not a content hash; `list`'s displayed
`(hash, date)` pair genuinely reads as a per-file content hash at a glance
and isn't one — worth being careful reading that output). Line counts range
87–595 across the 55 files. **Verdict: the "likely near-identical
boilerplate" theory is REFUTED.** All `validation.py` files share the same
`modcheck.Suite`/`ExpectationFailed` import and `@suite.chain`/
`t.component`/toggle scaffolding, but the actual content inside each is
bespoke per mod — mod-specific defNames, tick-count budgets grounded in
that mod's own prior live runs, per-mod docstrings tracing which item
closed what and why, and explicit "what this suite cannot prove and why"
sections. Both files reviewed found no bugs (Pyrelands' `_live()` gate and
SWBestiary's `t._guard()` calls are two different but both-correct ways of
implementing the same offline-probe-safety pattern the framework requires).
⇒ **The remaining 34 DIRTY `validation.py` files need one-by-one full-file
review, same as everything else in this loop — no sampling shortcut.** (21
of 55 were already marked CLEAN in a 2026-09-17 bulk pass, confirmed by
`code_review_status.py list`; this wave's 2 samples bring the total to 23
CLEAN / 32 DIRTY.)

All 4 confirmed reachable: the two `.cs` files via
`RimMandrakeGizkaStowaway.csproj`'s `<Compile Include>`; both `validation.py`
files via `modcheck/runner.py`'s `load_suite()`, which dynamically imports
`<mod_dir>/validation.py` for `modcheck/cli.py run <Mod>`. No bugs found in
any of the 4; no fixes needed this wave. All 4 marked CLEAN, commit
`e220673d9`, pushed.

Next wave: `GizkaStowaway/Source/` cluster has exactly 1 file left
(`RSW_GizkaStowawayManager.cs`) — finishing it closes out the whole
cluster. The `validation.py` sampling question is now answered (see above):
32 files remain DIRTY and need individual full-file review like any other
file in this loop, no shortcut. No other named clusters remain from earlier
waves' notes — a future wave should re-survey
`code_review_status.py list --show-untracked` for what's left reachable and
never-entered, since the GizkaStowaway/SeaShores/modcheck clusters named in
waves 3–7 are now exhausted or down to their last file.

## Wave 9 — 2026-09-24

Closed out the `GizkaStowaway/Source/` cluster: reviewed
`RSW_GizkaStowawayManager.cs` (the four discovery hooks —
`Notify_GravshipLanded`/`Notify_SalvageDeconstructed`/`Notify_TradeCompleted`/
`Notify_QuestCompleted` — plus `Discover`/`FindAnchorCell`). **Found and
fixed a real bug**: all four hooks called `Ready(RSW_GizkaStowawayMod.Settings.triggerX)`
— a hard dereference of `Settings` passed as the argument — while `Ready`'s
own body checks `s == null` internally, too late to matter: a null `Settings`
would throw an NRE at the call site before `Ready`'s guard ever ran. `Roll()`
in the same file already used the null-safe `Settings?.discoveryFrequency ?? 1f`
pattern, so the four hooks were the outliers. Fixed all four to
`Settings?.triggerX ?? false`, commit `3e547d539`, pushed. Confirmed
reachable via `RimMandrakeGizkaStowaway.csproj`'s `<Compile Include>`, and
cross-checked `RSW_GizkaPopulation.SpawnStowaway`'s signature matches the
call site. Marked CLEAN after the fix.

Also reviewed 3 of the 32 DIRTY `validation.py` files, full-file each, no
sampling shortcut per wave 8's finding: `SeaShores/validation.py` (135
lines — verified its API usage against `modcheck/suite.py`'s actual
`component`/`bridge_call`/`_guard`/`screenshot` signatures), `WreckedMachines/
validation.py` (189 lines — verified `t.spawn`'s returned `(x, z)` cells feed
correctly into the `rect="x,z,20,20"` format `jawa/list_things` expects, matching
`clear_area`'s own rect convention), and `Aftermath/validation.py` (153
lines — traced the suite's core assumption, that killing every raider outright
classifies as `"-> Repelled"`, against `BattleOutcomeClassifier.Classify`'s
actual priority order in `BattleOutcomeClassifier.cs` [`fraction >= 0.6f` checked
first, before LOST/ROUTED/STALEMATE] and confirmed both DevMode-gated
`Log.Message` lines the suite greps for — "battle opened"/"battle closed ->
Repelled" in `MapComponent_BattleRecorder.cs` — match the suite's exact
substrings and that the suite correctly sets `devMode=True` before firing).
No bugs found in any of the 3. All 3 marked CLEAN, commit `270bf9bc2`, pushed.

Next wave: 29 `validation.py` files remain DIRTY (32 minus this wave's 3;
re-derive the live list with `comm -23` between a fresh `find . -name
validation.py` sweep and `code_review_status.py list`'s CLEAN rows, since
`list` only shows entries that have ever been recorded — a file never
entered doesn't appear as DIRTY, it just doesn't appear). No other named
clusters remain outstanding from earlier waves.

## Wave 10 — 2026-09-24

Re-derived the DIRTY `validation.py` list per wave 9's recipe: a fresh
`find . -name validation.py` sweep (55 total) minus `code_review_status.py
list`'s CLEAN rows (27) gave 28 DIRTY (not 29 — the prior wave's count was
off by one, not worth chasing). Reviewed the 5 smallest of those, full-file
each, no sampling shortcut: `SacredGraffiti/validation.py` (108 lines —
confirmed its one outcome-effect def is genuinely unreachable by any bridge
path, per its own docstring, and both settings-toggle components correctly
get write+read-back only), `IshkoDarkLandmarks/validation.py` (135 lines —
pure-XML landmark mod; verified the `mutatorChances` substring-check pattern
and the "not yet placed on planet" negative-assertion chain), `Rites/
validation.py` (145 lines — pure-data research-tree gating; verified its
correction of the walk doc's own wrong claim about `jawa/research_
availability`'s `unfinishedPrerequisites` field, which walks ordinary
`prerequisites` only and has no hidden-prerequisite field at all, by reading
`JawaBenchResearchTimeTools.cs` directly), `BirthHatchDemo/validation.py`
(166 lines — reproduction-chain demo; verified the baseline-pawn-IDs-before-
spawn pattern that guards against `CompHatcher`'s `forceGenerateNewPawn:
false` handing back a recycled world pawn instead of a genuine new one), and
`StructureInjectionsSW/validation.py` (167 lines — 7 GenStepDef/
TileMutatorDef pairs; verified the `jawa/get_defs` replacement for the walk
doc's own wrong-tool (`jawa/get_def`) prescription by reading `JawaBenchTerrainTools.cs`,
and confirmed the `ChunkSlagSteel` cross-template-collision dodge — checking
`Filth_AnimalFilth` for Mynock Roost instead — is real, since that defName
also appears in the earlier-run Podracer Wreck template). Cross-checked
`jawa/list_things`' and `jawa/get_defs`' actual C# result shapes
(`JawaBenchTerrainTools.cs`) against both files' parsing to confirm field
names and the 200-item default `limit` don't silently truncate any of
StructureInjectionsSW's expected counts (max 62, BanthaHorn/MynockRoost).
No bugs found in any of the 5; no fixes needed this wave. All 5 marked
CLEAN, commit `510b4c29f`, pushed.

Next wave: 23 `validation.py` files remain DIRTY (28 minus this wave's 5) —
re-derive with the same `comm -23` recipe rather than trusting this count,
since it has drifted by one before. No other named clusters remain
outstanding from earlier waves.

## Wave 11 — 2026-09-24

Re-derived the DIRTY `validation.py` list per wave 9/10's recipe (fresh `find
. -name validation.py` sweep, 55 total, minus `code_review_status.py list`'s
CLEAN rows, 32) — confirmed exactly 23 DIRTY, matching wave 10's count for
once. Reviewed the 5 smallest, full-file each: `RestrainingBolts/
validation.py` (175 lines), `PawnFlavor/validation.py` (197), `AshkarrFlora/
validation.py` (201), `UtinniPatches/validation.py` (208), `JawaVoice/
validation.py` (221).

**Found and fixed a real, high-confidence bug in `AshkarrFlora/
validation.py`**: `sweetline_thingdef_readback` called `jawa/get_def` and read
`row.get("resolved") or row.get("fields")` — neither key exists on that
tool's actual response (cross-checked against `JawaBenchTerrainTools.cs`'s
`GetDef`: the real top-level keys are `statBases`/`comps`/`extra`/
`extraModelled`, and `extra` never carries `plant.*` or `parentName` for a
ThingDef). `resolved` was therefore always `{}`, so the chain raised
`ExpectationFailed` on **every** live run regardless of whether the def was
correct — a guaranteed false failure that had never been caught because this
suite had apparently never been run against a live bridge since it was
written. Fixed by splitting into two components against tools that actually
expose the data: `jawa/get_def`'s own `statBases` dict (already flat,
purpose-built) for the four `statBases.*` checks, and
`jawa/get_defs(fields="plant", deep=True)` — named as the documented escape
hatch in `GetDef`'s own `extraNote` string — for the plant sub-fields.
Dropped `parentName` from the expectations entirely (it is consumed by the
XML loader at parse time and is not a field retained on the resolved runtime
ThingDef — unreadable by any bridge tool, so it was never a checkable claim)
and downgraded `plant.visualSizeRange` to a presence-only check rather than
an exact-value one (its `FloatRange` struct's serialized field names were
never confirmed against a live call, and this repo's own rule is not to
assert an unmeasured engine-internal shape).

Also corrected the same file's module docstring: it asserted
`Textures/` does not exist on disk at all for `RUT_SweetlineTree` — true when
the suite was first written (`f145b6587`, 2026-09-17) but stale since
`0d9116326` landed 14 accepted PNG variants the very next day (2026-09-18).
The suite itself was never re-run/re-read after that commit, which is
directly why it sat DIRTY this whole time. `art_folder_exists_and_has_art`
now correctly passes and is kept as a standing regression guard.

The other 4 files (`RestrainingBolts`, `PawnFlavor`, `UtinniPatches`,
`JawaVoice`) were cross-checked line-by-line against their actual C#/bridge-
tool dependencies (`GoodwillSituationWorker_RestrainingBolts.cs`,
`RestrainingBoltsMod.cs`, `DefOfs.cs`; `jawa/faction_goodwill_situations`,
`jawa/list_factions`, `jawa/get_defs`, `jawa/get_def`, `jawa/world_info_get`,
`jawa/list_things`, `jawa/drain_log`, `jawa/set_pawn_xenotype` in
`JawaBenchStoryTools.cs`/`JawaBenchTerrainTools.cs`/`JawaBenchWorldTools.cs`)
and every field name, response shape and quoted XML/Jawaese string checked
out exactly as each suite's own docstring claimed — including JawaVoice's
205-count of `PatchOperationConditional` blocks across 11 files (spot-counted
fresh, matches exactly) and its `StuckIndoors` line (byte-for-byte match
against the live XML). No bugs found in those 4. All 5 marked CLEAN, commits
`8257db565` (the AshkarrFlora fix) and `030894504` (the mark-clean batch),
pushed.

Next wave: 18 `validation.py` files remain DIRTY (23 minus this wave's 5) —
re-derive with the same recipe rather than trusting this count. No other
named clusters remain outstanding from earlier waves.

## Wave 12 — 2026-09-24

Re-derived the DIRTY `validation.py` list per the standing recipe: a fresh
`find . -name validation.py` sweep (55 total) minus `code_review_status.py
list`'s CLEAN rows (37) gave exactly 18 DIRTY, matching wave 11's count.
Reviewed the 5 smallest, full-file each: `MSEDroidFix/validation.py` (228
lines), `WeatherSuite/validation.py` (235), `AshkarrLandmarkArt/
validation.py` (235), `RimDefDump/validation.py` (241),
`AshkarrInhabited/validation.py` (241).

**Found and fixed FIVE real, high-confidence bugs across 4 of the 5
files** — every one the same class as wave 11's `AshkarrFlora` bug, and
every one confirmed by reading the actual C# in
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs` rather than
trusting the suite's own claim:

- **AshkarrLandmarkArt** (`sample_defs_readback`): called `jawa/get_def`
  (singular) with `defType="LandmarkDef"` and read
  `row.get("resolved") or row.get("fields")` — neither key exists on that
  tool's response for any type; `GetDef`'s `extra` block is hand-modelled
  for exactly ThingDef/PawnKindDef/BiomeDef, so a LandmarkDef always came
  back with `extra=null`. The guard (`not resolved and not fields`) was
  therefore unconditionally true on every call, success or failure, so this
  component silently never once compared `iconTexturePath` to anything —
  a permanent no-op, the mirror image of AshkarrFlora's always-fails bug.
  Switched to `jawa/get_defs` (plural), the tool built exactly for
  reflective field reads on any def type, whose real per-entry shape
  (`found`, `fields`) does carry `iconTexturePath`.
- **AshkarrInhabited** (`settlement_manifests_readback`): read `districts`
  via `jawa/get_defs` without `deep=True`. `districts` is
  `List<DistrictSlot>` and `DistrictSlot` is a plain non-Def class — per
  `Scalars()`'s own documented behaviour, a list of non-scalar/non-Def
  items at `deep=false` serialises each item as its bare TYPE NAME string
  (`"DistrictSlot"`), never a dict with `label`. The fallback substring
  check (`district0_label not in str(districts)`) was therefore comparing
  against a stringified list of type-name strings — guaranteed to fail on
  every live run regardless of the real label. `castSlots`' own check only
  needed `len()`, which survives either shape, so that half was never
  actually broken. Fixed by passing `deep=True` on this one call.
- **RimDefDump** (`bridge_tool_mode_validation`): read `r.get("error")`,
  but `RimDefDumpRun` is declared in the SAME partial class as
  `JawaBenchTerrainTools.cs` and its `Fail()` calls resolve to that file's
  shared helper (`{success=false, message, details}`) — there is no
  `error` key anywhere in the file. `err` was always `""`, so the check
  raised `ExpectationFailed` on every live run regardless of whether the
  bridge tool actually refused for the right reason. Fixed to read
  `message`.
- **WeatherSuite** — two bugs in one file:
  1. `terminator_front_registers_permanently_bypassing_geometry` read
     `r.get("active")`, but `GameConditionTool`'s return statement names
     the outer key `activeConditions` (`active` is only the local variable
     it was built from) — guaranteed false failure on every live run.
  2. `dark_aurora_incident_is_correctly_gated_by_geometry` read
     `r.get("canFire")`, but `StorytellerFire`'s dry-run response names the
     field `canFireNow` — a silent no-op: the component could never have
     raised even if the incident genuinely could fire, so it was never
     actually testing the geometry gate it claims to test.

`MSEDroidFix/validation.py` (the fifth file) was reviewed line-by-line
against `jawa/get_defs` (blob-`str()`-search pattern, robust to key names),
`jawa/texture_audit` (`missing[]` shape confirmed, also `str()`-searched),
`jawa/drain_log` and `jawa/set_pawn_rotation` (both confirmed correct) — no
bugs found, no fixes needed.

All 5 confirmed reachable via `modcheck/runner.py`'s `load_suite()`
(dynamic per-mod-dir import). Fixes committed at `db60da8bc`, pushed. All 5
marked CLEAN, same commit.

Next wave: 13 `validation.py` files remain DIRTY (18 minus this wave's 5) —
re-derive with the same recipe rather than trusting this count. No other
named clusters remain outstanding from earlier waves. 🔑 Given this wave
found 5 bugs in 4 of 5 files reviewed (all key-mismatch against a bridge
tool's real C# response shape), a future wave should keep cross-checking
every `t.bridge_call(...)` against its actual `[Tool]` implementation
rather than treating the pattern as exhausted after wave 11's single find.

## Wave 13 — 2026-09-24

Re-derived the DIRTY `validation.py` list per the standing recipe: a fresh
`find . -name validation.py` sweep (55 total) minus `code_review_status.py
list`'s CLEAN rows (42) gave exactly 13 DIRTY, matching wave 12's count.
Reviewed the 5 smallest, full-file each, every `t.bridge_call(...)`
cross-checked against its actual `[Tool]` implementation in
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/*.cs`:
`EmpirePursuit/validation.py` (248 lines), `AshkarrWeatherSuite/
validation.py` (249), `StructureInjectionsRUT/validation.py` (259),
`PlantGrowth/validation.py` (264), `StarWarsPatches/validation.py` (266).

**Found and fixed 3 more real, high-confidence bugs, same family as waves
11-12, in 2 of the 5 files:**

- **EmpirePursuit** (`scenario_part_lifecycle`'s `part_readback_matches`):
  read `part.get("defName")` and flat `part.get("firstRaidDelayHours")`/
  `part.get("canDoNormalRaid")` off `jawa/scenario_parts_get`'s rows, but
  `DescribePart` (`JawaBenchScenarioTools.cs`) shapes each part as
  `{className, def, summary}` -- the ScenPartDef name is under `def`, never
  `defName`, and every field value is nested under `summary`, not flat.
  `part` was therefore always `None` and the component raised
  `ExpectationFailed` on every live run regardless of the real readback.
- **EmpirePursuit** (`normal_raid_pool_gate_flips_both_ways`, both
  directions): read `f.get("defName", f)` off `jawa/raid_preview`'s
  `hostileFactions[]`, but `RaidPreview` (`JawaBenchEventTools.cs`) shapes
  each entry as `{def, name, canStageAttacks}` -- no `defName` key, so the
  fallback always returned the whole dict. `"Mechanoid" not in names`
  (dicts, never the string) was therefore always true regardless of real
  exclusion, and the mirror `"Mechanoid" in names` check in the second half
  was therefore always false -- one direction silently never tested
  anything, the other always failed.
- **AshkarrWeatherSuite** (`planet_geometry_readback`): called `jawa/get_def`
  (singular) and read `row.get("resolved") or row.get("fields")` -- `GetDef`
  (`JawaBenchTerrainTools.cs`) only hand-models `extra` for ThingDef/
  PawnKindDef/BiomeDef; for a custom Def subclass like `PlanetGeometryDef`
  it returns `extra=null`, `extraModelled=false`, and there is no
  `resolved`/`fields` key on its response at all -- the check raised
  unconditionally on every live run. Fixed by switching to `jawa/get_defs`
  (plural)'s documented `fields=` escape hatch, same fix shape as wave 11's
  AshkarrFlora bug.
- **AshkarrWeatherSuite** (`weather_pathway_healthy`'s smoke check): guarded
  on `"error" in row`, but `jawa/weather_get`'s failure path returns the
  shared `Fail()` helper's shape (`{success=false, message, details}`,
  `JawaBenchTerrainTools.cs`) -- there is no `error` key anywhere in this
  bridge's response family (same finding as wave 12's RimDefDump bug), so
  the guard could never fire on a genuine failure. Fixed to check
  `success` directly.

The other 3 files (`StructureInjectionsRUT`, `PlantGrowth`,
`StarWarsPatches`) were cross-checked line-by-line against their actual
bridge-tool dependencies (`jawa/map_info`, `jawa/list_things`,
`jawa/run_genstep`, `jawa/drain_log` for StructureInjectionsRUT;
`jawa/inspect_string`, `jawa/set_plants`, `jawa/get_defs` for PlantGrowth --
its own docstring flagged the `things` key on `jawa/inspect_string` as an
unverified guess, and it turned out correct; `jawa/list_things`,
`jawa/pawn_get`/`PawnSnapshot` for StarWarsPatches, including confirming
`apparel[]`/`equipment[]` carry both `def` and `defName` as deliberate
aliases per that file's own comment) and every field name and response
shape checked out exactly as each suite assumed. No bugs found in those 3.

All 5 confirmed reachable via `modcheck/runner.py`'s `load_suite()`
(dynamic per-mod-dir import). Fixes committed at `1fc63ee14`, pushed. All 5
marked CLEAN, same commit.

Next wave: 8 `validation.py` files remain DIRTY (13 minus this wave's 5) --
re-derive with the same recipe rather than trusting this count. No other
named clusters remain outstanding from earlier waves. The key-mismatch
pattern is still productive (3 more bugs this wave, 11 total across waves
11-13) -- keep cross-checking every `t.bridge_call(...)` against its real
`[Tool]` implementation.

## Wave 14 — 2026-09-24, the `validation.py` tail is FINISHED

Re-derived the DIRTY `validation.py` list per the standing recipe: a fresh
`find . -name validation.py` sweep (55 total) minus `code_review_status.py
list`'s CLEAN rows (47) gave exactly 8 DIRTY, matching wave 13's count.
Reviewed all 8, full-file each (the whole remaining tail, per this wave's
own brief to finish it since it's small) -- `src/RimStarWars/
KotORBandolierNorthFix/validation.py` (276 lines), `src/RimMandrake/
MandrakePatches/validation.py` (284, plus a docstring CORRECTION already
recorded in-file from a prior pass), `src/RimStarWars/JawaRules/
validation.py` (290), `src/RimStarWars/DesertVehicleReskin/validation.py`
(303), `src/RimUtinni/LongHunger/validation.py` (310), `src/RimUtinni/
LanternDeeps/validation.py` (324), `src/RimStarWars/Cuisine/validation.py`
(332), `src/RimStarWars/Armoury/validation.py` (369) -- 2488 lines total.
Every `t.bridge_call(...)` in all 8 cross-checked against its actual
`[Tool]` implementation in `src/RimMandrake/bridgetools/JawaBench.
BridgeTools/*.cs` (`GetDefs`, `DrainLog`, `FireIncident`, `ListThings`,
`MapInfo`, `PawnGenes`, `PawnRelations`, `OrderedJob`, `PawnThoughts`,
`PawnNeed`, `HarmonyPatches`, `Damage`, `ListPawns` all read directly).

**Found and fixed 3 more real, high-confidence bugs, same family as waves
11-13, in 3 of the 8 files:**

- **JawaRules** (`droid_relations_smoke`): checked `"error" not in (r or
  {})` after `jawa/pawn_relations`, but `PawnRelations`' failure path is
  the shared `Fail()` helper (`{success=false, message, details}`,
  `JawaBenchTerrainTools.cs`) -- there is no `"error"` key anywhere in this
  response family (same finding as wave 12's RimDefDump and wave 13's
  AshkarrWeatherSuite bugs). The check was therefore unconditionally True
  on any non-exception response, success or failure -- only an actual
  thrown exception could ever fail this component. Fixed to check
  `r.get("success") is True`.
- **LanternDeeps** (`biome_gate_on_current_map`): read `jawa/map_info`'s
  non-existent top-level `"biome"` key. `MapInfo` (`JawaBenchMapInfoTools.cs`)
  reports the tile's biome at `tileInfo.biome` and the MAP's own resolved
  biome at the separate top-level `mapBiome` (deliberately both, per the
  tool's own doc comment on why they can diverge after a live
  `world_tile_set`) -- neither is a bare `biome` key. `biome` was therefore
  always `None`, so `biome in QUALIFYING_BIOMES` could never take the
  positive-scatter branch this suite's own docstring describes as one of
  its two intended outcomes; the suite always asserted the negative-gate
  half regardless of the actual map. Fixed to read `mapBiome`.
- **Armoury** (`_harmony_owner_present`'s instrument-blind guard): checked
  a top-level `(r or {}).get("harmonyError")`, but `HarmonyPatches`'
  failure path passes `harmonyError` as the `extra` argument to the same
  shared `Fail()` helper, which nests it under `details` -- there is no
  top-level `harmonyError` key. A genuinely blind instrument (HarmonyLib
  introspection itself throwing) therefore fell through this guard and hit
  the generic "no Harmony patch owned by ... found" raise below instead of
  the intended "THIS INSTRUMENT IS BLIND, not proof the patch is missing"
  message -- same failing test, but a misleading diagnostic that would
  send a first live-run reader looking for a missing patch that was never
  actually checked. Fixed to read `details.harmonyError`.

The other 5 files (`KotORBandolierNorthFix`, `MandrakePatches`,
`DesertVehicleReskin`, `LongHunger`, `Cuisine`) were cross-checked
line-by-line against their actual bridge-tool dependencies and every field
name/response shape checked out exactly as each suite assumed --
including `GetDefs`' `defs`/`fields`/`notFound`/`success` shape (both the
`str(r)` blob-search pattern several of these files use, robust to key
names by construction, and the direct `row["fields"][...]` pattern
MandrakePatches uses), `ListThings`' `things[]` rows (`hitPoints`,
`def`, `id`), `FireIncident`'s top-level `canFireNow`, `OrderedJob`'s
top-level `accepted`, `PawnThoughts`' `thoughts[].def`, `PawnGenes`'
top-level `xenotype`, and `Damage`'s `targets`/`results` dual-key alias
(the exact pattern the tool's own comment says was added after a prior
seat's `targets`-only miss). No bugs found in those 5.

Fixes committed at `5ae0191cc`, pushed. All 8 marked CLEAN, commit
`7ade1065a`, pushed. **This closes out every `validation.py` file in the
repo — all 55 are now CLEAN, 0 remain DIRTY or never-entered.** 14 real
bugs found across waves 9/11-14 (1 GizkaStowaway null-guard + 13
bridge-response key-mismatches), every one caught only by reading the
actual C# rather than trusting a suite's own assumption about a tool's
response shape.

### Post-tail survey: what the loop should pick up next

Per this item's own "standing, self-continuing" doctrine, ran a fresh
`code_review_status.py list` and a repo-wide reachable-file survey now
that the validation.py tail is closed, so the next wave has real
candidates instead of restarting from a cold search:

- **284 previously-CLEAN entries are now DIRTY again** (content changed
  since their clean mark) — this is a SEPARATE backlog from
  "never-entered," and per this file's own protocol a re-dirtied file
  needs a fresh full-file review, not a diff review, same as `cli.py` in
  wave 6/7. Two are this loop's own hooks (`.claude/hooks/queue_lint.py`,
  `.claude/hooks/selftest_queue_lint.py`, both re-dirtied since
  2026-09-20), several are `design/Jawa/mods/*.py` and
  `design/Jawa/worldbuilding/biomes/rosters/_validate.py`, and the bulk
  are `src/RimMandrake/**` `.cs`/`.xml`/`.md` files re-touched since their
  last clean mark (`CreatureBehaviors`, `EnvironmentalHazards`, `FlowWorks`
  and others recur). Full list: `code_review_status.py list | grep
  '^DIRTY'` (284 rows this pass — re-derive, do not trust this count next
  wave).
- **95 reachable `.cs` files have NEVER been entered at all** (present in
  a `.csproj`'s `<Compile Include>` or its default-compile-items glob, per
  a fresh survey of every `src/**/*.csproj`, absent from
  `CODE_REVIEW_STATUS.json` in any state). By folder: 20
  `CreatureBehaviors`, 12 `SWBestiary`, 9 `FlowWorks`, 8
  `EnvironmentalHazards`, 5 `PyrelandsMechanics`, 4 `bridgetools`, 3 each
  `StructureInjectionsRUT`/`Doctrine`/`TrophyCraft`/`DesertVehicleReskin`/
  `Ninefold`/`GelatinousSlime`, 2 each `LanternDeeps`/`JawaIonWeapons`/
  `Droidworks`/`Visibility`/`Pyrelands`/`Oracle`/`Inhabited`, 1 each
  `UtinniPatches`/`WreckedMachines`/`TitanicCreatures`/`SeaShores`/
  `Aftermath`. Full list saved this pass in the wave's own working notes
  (not committed — regenerate via the recipe in the next bullet).
- **13 never-entered Python tools under `src/RimMandrake/Utils/`**:
  `apply_blanket_ruling.py`, `artpipe/build_flora_legibility_sheet.py`,
  `artpipe/facing_set_audit.py`, `artpipe/requeue_quota_failures.py`,
  `build_landmark_density_sheet.py`, `canon_census.py`,
  `check_pseudo_sw_name.py`, `ecosystem_pyramid_check.py`,
  `label_collision_check.py`, `modcheck/readline_registry.py`,
  `sheet_to_artifact.py`, `stage_review.py`, `stage_xenotype_grid.py`.
  Reachability (importer/CLI entry point) was NOT independently confirmed
  for each of these 13 this pass — that check is owed before reviewing
  any of them, per this item's own "check it is still reachable" rule
  (CLAUDE.md's code-review section) and the DEAD-FILE-candidate protocol.
- Recipe used, re-derive rather than trust: `find . -name '*.csproj'`,
  regex `<Compile Include="...">` per project plus a default-glob fallback
  when a project has no `EnableDefaultCompileItems=false`, diffed via
  `comm -23` against the path column of `code_review_status.py list`
  (any status, not just CLEAN — a DIRTY or ORPHANED row still means
  "recorded", only an absent row means "never entered").

Next wave: pick from either the 284-row re-dirtied backlog (prioritize
this loop's own hooks and the `design/Jawa/mods/*.py` cluster, since a
stale review on this loop's own enforcement code is the worst kind of
self-inflicted gap) or the 95 never-entered `.cs` files (largest cluster:
`CreatureBehaviors`, already partly reviewed in earlier waves —
`RM_CompDungSeeder.cs` etc. — so the other 20 files there are a natural
next full-file batch). Confirm reachability on the 13 Utils Python tools
before spending a review on any of them.

## Wave 15 — 2026-09-24: the 284 re-dirty finding, diagnosed

**Part 1 — re-derived the 284 count independently** (`code_review_status.py
list | grep -c '^DIRTY'` gave exactly 284 again, same instrument the
post-tail survey used, so no drift this time). Verdict: **real, not a bug —
ordinary organic development touching reviewed files, no hashing defect, no
git-base artifact.**

- Broke the 284 down by extension: **161 `.png`, 74 `.xml`, 32 `.py`, 14
  `.cs`, 2 `.txt`, 1 `.csproj`.** The PNG majority is one identifiable
  event: `git log --oneline <clean-sha>..HEAD -- <file>` on a sample of the
  re-dirtied `*ArtOverride/Textures/**.png` files all point to the same
  commit, `1135036ce` ("art: zero the sub-visible export halo across 241 of
  our facing sprites") — a genuine bulk pixel-level art fix that touched
  hundreds of previously-clean-marked texture files across `RimStarWars`/
  `RimUtinni` `*ArtOverride` mods weeks after they were marked clean. Byte
  size differs (209509 → 188379 on the sampled file) confirming real content
  change, not a re-save no-op.
- Grouped by clean-mark date: **165 of 284 trace to clean-marks made on
  2026-09-17** (mostly three bulk mark-clean commits from *before* the
  2026-09-20 pause: `38ce6b1fa` "mark-clean 7 small RimMandrake dev-tool
  mods", `9aaf55cec` wave 41, `7d6efe921` an MLIE_FAUNA_ABSORPTION_1 note —
  these are `code_review_status.py list`'s informational `sha` field, i.e.
  the mark-clean commit, exactly the "not a per-file content hash" trap
  wave 8 already flagged). The remaining dates spread from 2026-09-02
  through 2026-09-20 — a long tail of ordinary re-touches, not a single
  event.
- Spot-checked non-PNG samples for legitimacy: `.claude/hooks/queue_lint.py`
  (+80/-30 lines since its clean-mark, one real commit
  `1135036ce`'s sibling history shows unrelated hook work), `RM_Environmental
  HazardsMod.cs` (+93/-1, two feature-build commits:
  `VENOMVINE_FORTRESS_PASSABILITY_1`, `DESERT_LEACHMOSS_BUILD_1`),
  `design/Jawa/mods/biome_flora.py` (+263/-57, roster expansion). Every
  sample is a substantive, real content change — no whitespace-only diffs,
  no timestamp-only diffs, no case where `git diff --stat` came back empty.
- **Conclusion: the 284 figure is exactly what `code_review_status.py` is
  designed to report — files reviewed once, then legitimately edited again
  by ~3 weeks of active feature work (biome rosters, new mechanics, hook
  fixes) plus one large bulk art-correction commit that alone accounts for
  ~57% of the backlog.** Nothing to fix in the tool; this is the review
  debt the standing loop exists to work down, not a defect to chase. One
  scope question this surfaces but does NOT answer here (out of scope for
  this wave, flagging for whoever picks the PNG portion up): binary PNG
  texture files make up 161 of these 284 "DIRTY" entries and 161/latent of
  the reachable-file universe generally — whether `code_review_status.py`
  tracking binary art assets at all (rather than just source/XML/py) is
  intentional scope or accidental scope-creep from an earlier over-broad
  `mark-clean` glob is undecided; either way "review" of a PNG can only ever
  mean "confirm it's the art we mean to ship," not a bug hunt, so those 161
  rows should probably be handled by the art pipeline's own review-sheet
  tooling rather than this loop's full-file-read protocol. Not resolved
  this wave — noted for a future wave or the owner.

**Part 2 — one normal review wave**, 3 files from the `CreatureBehaviors`
never-entered cluster (re-derived the 20-file list fresh via the item's own
`<Compile Include>` recipe, matches the post-tail survey's count):
`RM_CompProperties_ProximityPsychicStun.cs` (87 lines),
`RM_CompProximityPsychicStun.cs` (115 lines, the Soulchime proximity-stun
ThingComp — DEEPS_FAUNA_MECHANICS_1), `RM_FilterFeedExtension.cs` (69
lines, DefModExtension for DESERT_SHADE_WHALE_FILTERFEED_1's terrain-grazing
mechanic). Traced the stun comp's cooldown/faction/line-of-sight/damage-
trigger logic in full and cross-checked its two external references —
`RM_CreatureBehaviorsSettings.soulchimePsychicStunEnabled` (real static at
`RM_CreatureBehaviorsMod.cs:189`, inside the `RM_CreatureBehaviorsSettings`
class which spans lines 163–414) and `RM_CompPlantAlarm.TriggerAlarm()`
(real public method) — both resolve correctly. No bugs found in any of the
3. Confirmed reachable via `RM_CreatureBehaviors.csproj`'s `<Compile
Include>`. All 3 marked CLEAN, commit pending below, pushed.

Next wave: 17 `CreatureBehaviors` never-entered files remain (20 minus this
wave's 3) — re-derive rather than trust this count. The 284-row re-dirtied
backlog is now diagnosed (see above) but untouched for actual re-review;
the binary-art-tracking scope question above is still open.

## Wave 16 — 2026-09-24

Re-derived the `CreatureBehaviors` never-entered list fresh: `<Compile
Include>` entries in `RM_CreatureBehaviors.csproj` (75) minus every basename
recorded in `CODE_REVIEW_STATUS.json` in any state, CLEAN or DIRTY (58 — 56
CLEAN + 2 re-dirtied: `RM_CreatureBehaviorsMod.cs`, `RM_JobDefOf.cs`, both
already flagged in the 284-row backlog, not touched this wave) gave exactly
17, matching wave 15's count.

Reviewed 5 of those 17, full-file each, one coherent cluster — the shade-grid
keystone's remaining consumers (`RM_MapComponent_ShadeGrid.cs` itself was
still never-entered despite being the keystone three other files already
reference): `RM_MapComponent_ShadeGrid.cs` (151 lines, the per-cell shade
scan — `DESERT_SHADE_GRID_KEYSTONE_1`), `RM_HediffCompProperties_
ShadeDrivenSeverity.cs` (23) + `RM_HediffComp_ShadeDrivenSeverity.cs` (50,
the burst-predator's shade-driven severity decay), and
`RM_HediffCompProperties_ShadeStagger.cs` (64) + `RM_HediffComp_
ShadeStagger.cs` (237, `DESERT_STAGGERSEED_BUILD_1`'s stagger-toward-shade-
then-germinate life cycle).

Traced `ShadeGrid.Recompute`/`ComputeShadeAt`/`CastsShade` (roofed cells
return 1f directly; otherwise a radius-2 falloff score against the nearest
Building/Plant thing clearing its own fill-percent/visual-size threshold);
`ShadeDrivenSeverity.SeverityChangePerDay`'s `Mathf.Lerp` between the two
Props rates gated on both `shadeGridEnabled` and `heatDrivenBurstEnabled`;
and `ShadeStagger`'s two halves in full — the `CompPostTickInterval` steer
loop (`FindShadeCell`'s strict-improvement-only update over
`GenRadial.RadialCellsAround`, confirmed it converges on the best-shaded
reachable cell within `staggerRadius` with the nearest cell winning ties,
since only a strictly greater shade value triggers an update) and the
`Notify_PawnDied` germinate step (confirmed against the engine's own `Pawn.
Kill` phase ordering already cited in the file's header comment — the corpse
is spawned and positioned before `Notify_PawnDied` fires, so reading
`base.Pawn?.Corpse` is safe and `Pawn.Position`/`Pawn.Map` correctly aren't
touched). Cross-checked every `RM_CreatureBehaviorsSettings.*` field these
five files read (`shadeGridEnabled`, `heatDrivenBurstEnabled`,
`heatDrivenBurstDecayMultiplier`, `shadeStaggerEnabled`,
`shadeStaggerGerminationMultiplier`) against `RM_CreatureBehaviorsMod.cs`'s
actual static fields and Scribe/settings-UI wiring — all five exist and are
wired, confirming these files compile against real settings despite that mod
file itself sitting DIRTY in the 284-row backlog. Also confirmed the
`pawn.jobs.StartJob(job, JobCondition.InterruptForced, resumeCurJobAfterwards:
false, cancelBusyStances: true)` call and the `pawn.IsHashIntervalTick(n,
delta)` two-arg interval pattern both match the exact idiom four other
already-CLEAN files in this assembly use, so neither is a one-off risk.

No bugs found in any of the 5; no fixes needed this wave. All 5 confirmed
reachable via `RM_CreatureBehaviors.csproj`'s `<Compile Include>`. All 5
marked CLEAN, commit pending below, pushed.

Next wave: 12 `CreatureBehaviors` never-entered files remain (17 minus this
wave's 5) — re-derive rather than trust this count. Candidates visible in
this pass's diff: `RM_CompProperties_DungSeeder.cs`,
`RM_CompProperties_PlantAlarm.cs`, `RM_HediffDef_Grapple.cs`,
`RM_Hediff_Drained.cs`, `RM_HydrocarbonBloodExtension.cs`,
`RM_JobGiver_FilterFeedTerrain.cs`, `RM_JobGiver_WanderInShadeGrid.cs` (the
shade grid's third consumer — natural next pick, same cluster as this
wave), `RM_MapComponent_ProximitySoundscape.cs`,
`RM_ProximitySoundscapeExtension.cs`, `RM_ShadeSeekingWanderExtension.cs`,
`RM_WoundLinkExtension.cs`, `RUT_Plant_FalseFruit.cs`. The 284-row
re-dirtied backlog (including this assembly's own
`RM_CreatureBehaviorsMod.cs` and `RM_JobDefOf.cs`) is still untouched for
actual re-review; the binary-art-tracking scope question from wave 15 is
still open.

## Wave 17 — 2026-09-24

Reviewed 5 of the 12 remaining `CreatureBehaviors` never-entered files,
full-file each: `RM_JobGiver_WanderInShadeGrid.cs` (65 lines, the shade
grid's third consumer — closes out that cluster), `RM_ShadeSeekingWander
Extension.cs` (22, its paired DefModExtension), `RM_CompProperties_
DungSeeder.cs` (82, the Comp already marked clean in wave 3 but whose own
Properties file was still never-entered), `RM_CompProperties_PlantAlarm.cs`
(50, same shape — pairs with wave-3-clean `RM_CompPlantAlarm.cs`), and
`RM_HediffDef_Grapple.cs` (77, pairs with wave-1-clean `RM_Hediff_
Grappled.cs`).

Cross-checked every field each Properties/Def file declares against its
paired already-CLEAN consumer's actual `Props.*`/`Def.*` reads
(`RM_CompDungSeeder.cs`, `RM_CompPlantAlarm.cs`, `RM_Hediff_Grappled.cs`) —
every field name and type matches exactly, no orphaned or missing fields
either direction. For `RM_JobGiver_WanderInShadeGrid.cs` (a `JobGiver_
Wander` subclass, a vanilla base class none of this repo's other source
files had been checked against RimSage for — unavailable on this machine
per CLAUDE.md's Mac/WSL note), corroborated its `wanderDestValidator`
signature and constructor-field pattern against `RM_JobGiver_
DreadAvoidWander.cs` (`EnvironmentalHazards/Source/`, already CLEAN since
2026-09-14), whose own header records reading `Verse.AI/JobGiver_Wander.cs`
in a live 1.6 decompile and confirms the exact same `Func<Pawn, IntVec3,
IntVec3, bool> wanderDestValidator` shape — a real, reviewed, compiling
precedent in this repo, so the shade-grid file's use of the same shape
needed no fresh decompile to trust. Also confirmed `RM_CreatureBehaviors
Settings.shadeGridEnabled`/`shadeSeekingWanderEnabled` are real wired
statics (declared, Scribed, and exposed via `CheckboxLabeled` in
`RM_CreatureBehaviorsMod.cs`) despite that file itself sitting in the
284-row re-dirtied backlog.

No bugs found in any of the 5; no fixes needed this wave. All 5 confirmed
reachable via `RM_CreatureBehaviors.csproj`'s `<Compile Include>`. All 5
marked CLEAN, commit pending below, pushed.

Next wave: 7 `CreatureBehaviors` never-entered files remain (12 minus this
wave's 5): `RM_Hediff_Drained.cs`, `RM_HydrocarbonBloodExtension.cs`,
`RM_JobGiver_FilterFeedTerrain.cs`, `RM_MapComponent_
ProximitySoundscape.cs`, `RM_ProximitySoundscapeExtension.cs`,
`RM_WoundLinkExtension.cs`, `RUT_Plant_FalseFruit.cs` — re-derive rather
than trust this count. The 284-row re-dirtied backlog and the
binary-art-tracking scope question from wave 15 are both still untouched.

## Wave 18 — 2026-09-24: `CreatureBehaviors` never-entered cluster CLOSED

Reviewed the final 7 `CreatureBehaviors` never-entered files, full-file each,
closing out the whole cluster this loop has been working since wave 3:
`RM_Hediff_Drained.cs` (31 lines, the DEEPS_FAUNA_MECHANICS_1 drain-marker
hediff), `RM_HydrocarbonBloodExtension.cs` (22, the paired DefModExtension —
cross-checked `RM_Hediff_Drained.PostAdd`'s
`attacker.TryGetComp<RM_CompFluidSacs>()?.Notify_Fed(pawn, Severity)` call
against `RM_CompFluidSacs.Notify_Fed(Pawn victim, float severity)`'s real
signature, matches), `RM_JobGiver_FilterFeedTerrain.cs` (89, DESERT_SHADE_
WHALE_FILTERFEED_1's terrain-grazing job giver — cross-checked every
`RM_FilterFeedExtension` field read and `RM_CreatureBehaviorsSettings.
filterFeedingEnabled`/`RM_JobDefOf.RM_FilterFeedTerrain` against their real
declarations), `RM_MapComponent_ProximitySoundscape.cs` (304,
GREENTIDE_HUMMING_GROVE_1's proximity-mix MapComponent — traced the scan/
apply/hysteresis/pop-mitigation pipeline and the isolated, already-MEASURED
`CameraDriver.MapPosition` read; noted but did not change one imprecise
comment, "wind it down through the same hysteresis path", where the actual
code for a group with zero nearby Things cuts sustainers directly via
`SyncSustainers(..., null, 0)` rather than routing through `Apply`'s
hysteresis — functionally reasonable as an immediate silence-when-nothing-
present policy, not treated as a bug), `RM_ProximitySoundscapeExtension.cs`
(138, its paired DefModExtension with full `ConfigErrors` validation),
`RM_WoundLinkExtension.cs` (51, ROT_HEALTH_SHARING_1's kin-tag extension),
and `RUT_Plant_FalseFruit.cs` (67, ROT_GUARDIAN_GROVES_1's mimic-lure Plant
subclass — cross-checked `RM_CreatureBehaviorsSettings.guardianAlarmEnabled`
and `RM_CompPlantAlarm.TriggerAlarm()` against their real declarations). No
bugs found in any of the 7; no fixes needed. All 7 confirmed reachable via
`RM_CreatureBehaviors.csproj`'s `<Compile Include>`. All 7 marked CLEAN,
commit `4ac66bfeb`, pushed. **This closes the entire `CreatureBehaviors`
never-entered cluster (75 `<Compile Include>` files, all now recorded).**

With time remaining, surveyed the next-largest never-entered cluster from
wave 14's list, `SWBestiary` (three separate `.csproj`s under `SWBestiary/
Source/`: `BeastMechanics`, `JawaIkee`, `Livestock`). Re-derived fresh
rather than trusting wave 14's "12" figure: `JawaIkee` (`EnableDefaultCompile
Items=true`, glob) and `Livestock` (`<Compile Include>` explicit) were
**already fully recorded** — `code_review_status.py list` shows all 6 of
their `.cs` files CLEAN already, so wave 14's per-folder count included
files that were never actually never-entered (or have since been reviewed
elsewhere). `BeastMechanics` (`EnableDefaultCompileItems=false`, 11
`<Compile Include>` entries) had **all 11** absent from
`CODE_REVIEW_STATUS.json` — the real never-entered set is these 11, not 12,
and it's entirely in one folder, not spread across three.

Reviewed 3 of the 11 `BeastMechanics` files, full-file each, one coherent
cluster (the ferroclaw's steel-eating mechanic, PORTED_BEAST_MECHANICS_
REBUILD_1, rebuilt from Vanilla Expanded Framework's `CompEatWeirdFood`/
`JobGiver_GetWeirdFood`/`JobDriver_IngestWeird` per this file's own header):
`CompMetalEater.cs` (82 lines, the marker comp + its Props), `JobGiver_
EatMetal.cs` (129, priority/job-giving with the dig-when-map-empty fallback),
`JobDriver_EatMetal.cs` (141, the bespoke chew-then-consume toils, since
steel has no ordinary ingestible properties for `JobDriver_Ingest` to use).
Cross-checked `RSW_BeastMechanicsDefOf.RSW_EatMetal` and `RSW_
BeastMechanicsSettings.metalEatingEnabled` against their real declarations —
both exist and are wired. No bugs found in any of the 3; no fixes needed.
All 3 confirmed reachable via `RimMandrakeBeastMechanicsRSW.csproj`'s
`<Compile Include>`. All 3 marked CLEAN, commit pending below, pushed.

Next wave: 8 `BeastMechanics` never-entered files remain (11 minus this
wave's 3): `Patch_JobGiver_GetFood.cs`, `CompScrapHoarder.cs`, `JobGiver_
HoardScrap.cs`, `JobDriver_HoardScrap.cs`, `CompInnateAbility.cs`,
`CompAbilityEffect_FuelSpew.cs`, `RSW_BeastMechanicsDefOf.cs`, `RSW_
BeastMechanicsSettings.cs` — re-derive rather than trust this count (recipe:
`<Compile Include>` in each `src/**/*.csproj` minus every basename recorded
in `CODE_REVIEW_STATUS.json` in any state). The other never-entered clusters
from wave 14's survey (`FlowWorks` 9 files, `EnvironmentalHazards` 8,
`PyrelandsMechanics` 5, and the smaller ones) are still untouched and, per
this wave's SWBestiary finding, their counts should be re-verified rather
than trusted — wave 14's per-cluster tally may be stale the same way
SWBestiary's was. The 284-row re-dirtied backlog and the binary-art-tracking
scope question from wave 15 are both still untouched.

## Wave 19 — 2026-09-24: `BeastMechanics` never-entered cluster CLOSED

Reviewed the final 8 `BeastMechanics` never-entered files, full-file each,
closing out the whole SWBestiary `BeastMechanics` cluster (11/11 recorded):
`CompScrapHoarder.cs`/`JobGiver_HoardScrap.cs`/`JobDriver_HoardScrap.cs`
(SHRUBLAND_SCRAPNEST_BIRDS_1's scrap-hoarding bird mechanic — a marker comp,
a `ThinkNode_JobGiver` inserted at `Animal_PreMain`, and a haul job built
almost entirely from vanilla `Toils_Haul`), `CompInnateAbility.cs` (grants a
donor-comp-replacement AbilityDef once, Scribed so it isn't re-granted),
`CompAbilityEffect_FuelSpew.cs` (the cindermite's chemfuel spew — confirmed
against both the vanilla `CompAbilityEffect_FireSpew` and the VFE Insectoids
donor source that this is deliberately Blunt/no-ignition, not vanilla's
Flame, matching the file's own header claim), and `RSW_
BeastMechanicsDefOf.cs`/`RSW_BeastMechanicsSettings.cs`/`Patch_JobGiver_
GetFood.cs` (JobDef/settings/Harmony-prefix scaffolding). Cross-checked every
field and DefOf reference against its consumer or its paired XML
(`RSW_ScrapNest.xml`'s `CompProperties_ScrapHoarder`/`RSW_HoardScrap` JobDef/
`RSW_ScrapHoarderInsert` ThinkTreeDef all match the C# exactly) and
`CompMetalEater.cs`'s `blockNormalFood` field the Harmony prefix reads. No
bugs found in any of the 8. All 8 confirmed reachable via `RimMandrakeBeast
MechanicsRSW.csproj`'s `<Compile Include>`. All 8 marked CLEAN, commit
`91bf261fb`, pushed.

With time remaining, re-derived every never-entered cluster fresh from
scratch (fresh `<Compile Include>`/default-glob parse of every
`src/**/*.csproj`, diffed against `CODE_REVIEW_STATUS.json`'s full key set —
not just CLEAN rows, any recorded status) rather than trusting wave 14's
tallies, which wave 18 already found stale once (SWBestiary's true 11 vs its
claimed 12). **Current total: 43 never-entered `.cs` files**, far below wave
14's original 95 — most of that gap is prior waves' own work already having
closed out `CreatureBehaviors` (75) and `BeastMechanics` (11) entirely, plus
some folders wave 14 counted (`JawaIkee`, `Livestock`) turning out to already
be fully recorded. Fresh per-folder breakdown: `EnvironmentalHazards/Source`
8, `FlowWorks/Source/LiquidTypes` 7, `PyrelandsMechanics/Source` 5,
`GelatinousSlime/Source` 3, `TrophyCraft/Source` 3,
`StructureInjectionsRUT/Source/Ashfall` 3, `bridgetools/JawaBench.
BridgeTools` 2, `FlowWorks/Source` 2, `Pyrelands/Source` 2, `LanternDeeps/
Source` 2, and 1 each in `Aftermath/Source`, `FlowWorks/Source/SelfTest`,
`Ninefold/Source`, `SeaShores/Source/SelfTest`, `WreckedMachines/Source`,
`UtinniPatches/Source`.

Reviewed 3 of `EnvironmentalHazards/Source`'s 8, full-file each:
`RM_TreasureConscienceDef.cs` + `RM_Patch_TreasureSaleConscience.cs`
(ROT_LIVE_PREPARATIONS_1 card 6's "selling the Rot's treasure gives a guilt
memory" mechanic — verified the Harmony prefix/postfix split against the
`TradeDeal.TryExecute` source RimSage cited in the file's own header, since
`ResolveTrade()`+`Reset()` clear the deal before a postfix could read it),
and `RM_HaulVictimAIUtility.cs` (FEVER_WOOD_MECHANICS_1's generalized
kidnap-victim finder — diffed field-for-field against the real
`RimWorld/KidnapAIUtility.TryFindGoodKidnapVictim` in
`/mnt/d/Luke/dev/reference/rimworld-decompiled/RimWorld/KidnapAIUtility.cs`:
identical validator shape with `RaceProps.Humanlike` correctly generalized
to a caller-supplied predicate; the one omission — vanilla's Anomaly-DLC
`IsSubhuman` exclusion — is not a bug, the file's own header names this a
SPIKE that doesn't yet build the calling LordJob). Confirmed both
`TryFindGoodHaulVictim` (called from `RUT_HaulPawnAndExit.cs`) and
`treasureConscienceEnabled` (declared and read in `RM_EnvironmentalHazards
Mod.cs`) are real, wired, non-dead code. No bugs found in any of the 3. All
3 marked CLEAN, commit pending below, pushed.

Next wave: 5 `EnvironmentalHazards/Source` never-entered files remain:
`RM_LivingProduceExtension.cs`, `RUT_IncidentWorker_SporeCloud.cs`, `RUT_
HediffComp_SheenExposure.cs`, `ContactVenomImmunity.cs`, `MapComponent_
ContactVenom.cs` — re-derive rather than trust this count. `FlowWorks/Source/
LiquidTypes` (7) is the next-largest cluster after this one closes. The
284-row re-dirtied backlog and the binary-art-tracking scope question from
wave 15 are both still untouched.

## Wave 20 — 2026-09-24: `EnvironmentalHazards/Source` never-entered cluster CLOSED

Re-confirmed the final 5 `EnvironmentalHazards/Source` never-entered files
against `RM_EnvironmentalHazards.csproj`'s `<Compile Include>` list before
touching anything (all 5 still present, all 5 still DIRTY/never-entered per
`code_review_status.py check`) — wave 19's list held exactly. Reviewed all 5,
full-file each: `RM_LivingProduceExtension.cs` (51 lines, ROT_DECAY_HARVEST_1's
calibrated heat-per-unit DefModExtension), `RUT_IncidentWorker_SporeCloud.cs`
(27, a one-line mod-option gate on `IncidentWorker_MakeGameCondition`, same
shape as the already-CLEAN `RUT_IncidentWorker_Breaklight.cs`),
`RUT_HediffComp_SheenExposure.cs` (50, same gate shape wrapping
`RM_HediffComp_EnvironmentalExposure`), `ContactVenomImmunity.cs` (34, a
deliberately-empty marker DefModExtension — confirmed no current consumer in
the repo, matching its own header's claim that this is expected, not a
missing wiring step), and `MapComponent_ContactVenom.cs` (369, the map-side
contact-venom scan/scratch/prune loop — the meaty one). Traced
`MapComponent_ContactVenom`'s sample/prune cadence in full: `Sample`'s
per-pawn first-contact-vs-lingering-contact branch, `Prune`'s staleness
threshold (`now - lastContactTicks[i] > contactIntervals[i]`), the
save/load row-alignment repair in `ExposeData` (drops any row left
misaligned by a null Pawn reference rather than trying to repair it), and
`ApplyLethalityOption`'s clamp-at-0.99x-of-lethalSeverity approach (matches
`Hediff.Severity`'s own clamp-at-assignment semantics). Cross-checked every
field/method these 5 files read against its real declaration:
`RM_EnvironmentalHazardsSettings.sporeCloudEnabled`/`sheenExposureEnabled`/
`contactVenomEnabled`/`contactVenomLethal`/`contactVenomScratchMultiplier`/
`hazardDamageMultiplier` (`RM_EnvironmentalHazardsMod.cs`, all real statics,
Scribed and UI-wired), `RM_HediffComp_EnvironmentalExposure.SeverityChangePerDay`
(virtual, correctly overridden), and `CompProperties_ContactVenom`'s
`damageDef`/`damageAmount`/`armorPenetration`/`contactIntervalTicks`/
`bodyHeight` fields (`CompContactVenom.cs`, already CLEAN since wave 6). No
bugs found in any of the 5; no fixes needed. All 5 marked CLEAN, commit
`354f10fbb`, pushed. **This closes the entire `EnvironmentalHazards/Source`
never-entered cluster (8/8 recorded, matching wave 19's fresh tally).**

Moved to `FlowWorks/Source/LiquidTypes` per this item's own brief. Re-derived
the file list fresh from `RimMandrake_FlowWorks.csproj`'s `<Compile Include>`
entries (20 total under `LiquidTypes\`, not a separate `.csproj` — it's a
subfolder of the main `RimMandrake_FlowWorks.csproj`) and checked all 20
against `CODE_REVIEW_STATUS.json`: **13 were already CLEAN** (mostly from a
2026-09-17/18 pass plus `RM_LiquidTankUtility.cs`'s wave-2 bugfix mark),
leaving exactly **7 never-entered**, matching wave 19's tally for this
cluster by coincidence — `WorkGiver_EmptyBottleIntoTank.cs`,
`JobDriver_EmptyBottleIntoTank.cs`, `WorkGiver_FillBottleFromTank.cs`,
`JobDriver_FillBottleFromTank.cs`, `RM_LiquidBodyDef.cs`,
`RM_WorldComponent_LiquidTags.cs`, `RM_GenStep_LiquidShores.cs`.

With time remaining, reviewed 3 of the 7, full-file each, one coherent
cluster (the tank-pour-in half of LIQUID_BOTTLE_LOOP_1, mirroring the
already-CLEAN terrain-edge `WorkGiver_FillBottle.cs`/`JobDriver_FillBottle.cs`
pair): `WorkGiver_EmptyBottleIntoTank.cs` (59 lines), `JobDriver_
EmptyBottleIntoTank.cs` (77), `WorkGiver_FillBottleFromTank.cs` (58).
Cross-checked every call against its real target: `RM_LiquidTankUtility.
TryFindTankToFill`/`TryFindTankToDrain` (`RM_LiquidTankUtility.cs`, already
CLEAN — confirmed the wave-2 closure-variable bugfix noted in that file's own
comment is still in place, deriving `liquid` from the chosen `tank` after the
search rather than from the predicate closure), `Building_LiquidTank.
CanAccept`/`CanProvide`/`TryAddLiquid`/`Empty`/`storedLiquid` (`Building_
LiquidTank.cs`, already CLEAN), `RM_BottledLiquidExtension.IsEmpty`/`size`/
`liquid` and `LiquidDef.UnitsFor`/`bottled.FilledDefFor`
(`RM_BottledLiquidExtension.cs`/`LiquidDef.cs`, already CLEAN),
`RM_LiquidBottleUtility.EmptyDefFor`, and `RimMandrakeFlowWorks_DefOf.
RM_EmptyIntoTankJob`/`RM_FillFromTankJob` (both real, declared `JobDef`
statics). No bugs found in any of the 3; no fixes needed. All 3 marked
CLEAN, commit pending below, pushed.

Next wave: 4 `FlowWorks/Source/LiquidTypes` never-entered files remain
(7 minus this wave's 3): `JobDriver_FillBottleFromTank.cs` (natural next
pick — closes out the tank-loop pair with this wave's 3),
`RM_LiquidBodyDef.cs`, `RM_WorldComponent_LiquidTags.cs`,
`RM_GenStep_LiquidShores.cs` — re-derive rather than trust this count. The
284-row re-dirtied backlog and the binary-art-tracking scope question from
wave 15 are both still untouched.

## Wave 21 — 2026-09-24: `FlowWorks/Source/LiquidTypes` CLOSED, plus `PyrelandsMechanics`

Re-confirmed the final 4 `FlowWorks/Source/LiquidTypes` never-entered files
against `RimMandrake_FlowWorks.csproj`'s `<Compile Include>` list (20 entries
under `LiquidTypes\`, `EnableDefaultCompileItems=false` confirmed explicit)
before touching anything — wave 20's list held exactly. Reviewed all 4,
full-file each: `JobDriver_FillBottleFromTank.cs` (69 lines, the tank-draw
half mirroring the already-CLEAN `JobDriver_EmptyBottleIntoTank.cs` — traced
the `tank.Empty`/`filledDef == null`/`TryRemoveLiquid` short-circuit chain to
confirm no side effect fires on a stale WorkGiver scan), `RM_LiquidBodyDef.cs`
(90, the per-body-of-water authoring Def — `liquid`/`biomes`/`tiles` plus its
own ConfigErrors), `RM_WorldComponent_LiquidTags.cs` (177, the per-tile/
per-biome lookup cache with no `ExposeData` by design), and
`RM_GenStep_LiquidShores.cs` (147, the landing-repaint GenStep). Cross-checked
every engine call these four make against the real decompiled source at
`/mnt/d/Luke/dev/reference/rimworld-decompiled`: `PlanetTile.Tile` (indexer
into `Layer`), `Tile.PrimaryBiome`, `Map.Tile`/`Map.Biome`,
`BiomeDef.waterDeepTerrain`/`waterShallowTerrain`/`oceanDeepTerrain`/
`oceanShallowTerrain`, `TerrainDefOf.WaterDeep`/`WaterShallow`/
`WaterOceanDeep`/`WaterOceanShallow`, `TerrainGrid.SetTerrain`/`TerrainAt` —
all real, all matching usage. Also read the three companion XML files
(`RM_GenStep_LiquidShores.xml`'s GenStepDef + order-245 placement,
`RM_LiquidShores_MapGenPatch.xml`'s `PatchOperationAdd` onto
`MapCommonBase`, `RM_LiquidBodyRegistry.xml`'s four Ash'karr body rows) and
confirmed `RimMandrakeFlowWorksSettings.typedLiquidShoresEnabled` is a real
Scribed static the GenStep reads correctly (it lives in the `...Settings`
class, not `...Mod`, despite the class boundary falling mid-file — checked
line ranges to be sure). No bugs found in any of the 4; no fixes needed. All
4 marked CLEAN, commit pending below, pushed. **This closes the entire
`FlowWorks/Source/LiquidTypes` never-entered cluster (20/20 recorded).**

Re-surveyed every `src/RimMandrake|RimStarWars|RimUtinni/**/*.csproj`'s
`<Compile Include>` entries against `code_review_status.py list` (any
status) fresh, restricted to our three owned tiers (excludes vendored/donor
source under `1.6/`, `VanillaExpandedFramework-main/`,
`BiomesFramework_src/`, etc., which are not ours to review): **38
never-entered files remain**, down from wave 14's ~95 (waves 15-20 closed
`CreatureBehaviors` and `EnvironmentalHazards`). Largest cluster:
`RimUtinni/PyrelandsMechanics` (6 files). With time remaining, reviewed 3 of
those 6, full-file each: `PyrelandsTuning.cs` (265 lines, the kit's single
tuning-constants file — content-only, no logic to break, spot-checked that
every `[INVENTED]`-tagged constant does trace to a ruling or an anchor cited
in its own comment), `Patch_FurnaceBeastHeatImmunity.cs` (123, the Harmony
prefix absorbing Heat-category damage on `RUT_FurnaceBeast` — verified the
`ref bool absorbed` prefix parameter correctly mirrors `Pawn.PreApplyDamage`'s
real `out bool absorbed` signature per Harmony's documented out-param
convention, confirmed `DamageDef.armorCategory`/`DamageInfo.Def` are real
fields, and confirmed the file's own cited engine fact —
`FireUtility.CanEverAttachFire` returning false on `!t.FlammableNow` — reads
byte-for-byte as claimed against the decompiled source), and
`JobGiver_RUT_HarvestScorchFruit.cs` (108, the Deep Tribes' pick-up-then-
harvest duty — verified `ThingOwner.TotalStackCountOfDef`,
`GenClosest.ClosestThingReachable`'s signature, and `FireUtility.IsBurning`
all match their real declarations, and confirmed both
`furnaceHeatImmunityEnabled` and `fireRiteCarryPerPawn` are real Scribed
statics in `PyrelandsMechanicsMod.cs`). No bugs found in any of the 3. All 3
marked CLEAN, commit pending below, pushed.

Next wave: 3 `PyrelandsMechanics` never-entered files remain
(`JobGiver_RUT_FurnaceThermalCycle.cs`, `LordJob_RUT_FireRite.cs`,
`PyrelandsFireRite.cs`) — re-derive via the recipe above rather than trust
this count. 35 never-entered files remain across our three tiers overall
(38 minus this wave's 3); next-largest after PyrelandsMechanics closes:
`RimMandrake/Pyrelands` (4), `RimMandrake/FlowWorks` (3, non-LiquidTypes:
`RM_StockMath.cs`, `Source/ManyWaters/RiverSteamHook.cs`,
`Source/SelfTest/Program.cs` — confirm each is reachable, not just listed,
since a `SelfTest/Program.cs` may be a standalone entry point rather than
part of the main assembly), `RimMandrake/GelatinousSlime` (3),
`RimStarWars/TrophyCraft` (3), `RimUtinni/StructureInjectionsRUT` (3). The
284-row re-dirtied backlog and the binary-art-tracking scope question from
wave 15 are both still untouched.

## Wave 22 — 2026-09-24: `PyrelandsMechanics` never-entered cluster CLOSED

Re-confirmed the final 3 `PyrelandsMechanics` never-entered files against
`RimMandrake.Utinni.PyrelandsMechanics.csproj`'s `<Compile Include>` list
before touching anything — wave 21's list held exactly. Reviewed all 3,
full-file each: `PyrelandsFireRite.cs` (183 lines, spawns and dispatches the
Deep Tribes' rite party), `LordJob_RUT_FireRite.cs` (205, the rite's state
graph — travel/rite-harvest/exit), `JobGiver_RUT_FurnaceThermalCycle.cs`
(211, the furnace-beast's map-leg heat-seeking + thornvine diet). Cross-
checked every engine call against the real decompiled source at
`/mnt/d/Luke/dev/reference/rimworld-decompiled`: `RCellFinder.
TryFindRandomPawnEntryCell`, `CellFinder.RandomClosewalkCellNear`,
`LordMaker.MakeNewLord`, `StateGraph.AttachSubgraph`/`StartingToil`,
`Transition`/`AddSources`, `Trigger_Memo`/`Trigger_TicksPassed`/
`Trigger_BecamePlayerEnemy`, `GenClosest.ClosestThingReachable`,
`ThingDef.IsNutritionGivingIngestible` — all real, all matching usage.

**Found and fixed one false engineering claim** (comment-only, no behaviour
change) in `LordJob_RUT_FireRite.cs`: the `ignited` field's comment claimed
"a load re-enters the current toil", implying `LordToil.Init()` re-fires on
reload and the guard exists to stop a second ignition from that. Traced
`Verse.AI.Group.Lord.ExposeData_StateGraph`/`Lord.SetJob` in the decompiled
engine: on load, `SetJob(loading: true)` rebuilds the graph via
`CreateGraph()` and then restores `curLordToil` by **direct index
assignment** (`curLordToil = graph.lordToils[tmpCurLordToilIdx]`), bypassing
`GotoToil()` — and therefore `Init()` — entirely. A reload can never
re-ignite this toil either way, and in a live session only the `arrived`
transition ever targets `rite`, so `Init()` runs at most once regardless.
The guard is harmless (kept as cheap insurance against a future transition
change) but its stated justification was flatly wrong. Corrected the
comment in place, commit `16a03960e`, pushed.

Also traced `LordToil_Travel.LordToilTick`'s `lord.ReceiveMemo
("TravelArrived")` call (fires when every pawn is within 10 tiles of the
destination and can reach it) to confirm the `Trigger_Memo("TravelArrived")`
this file listens for is real and correctly named, and cross-checked every
`PyrelandsMechanicsSettings.*`/`PyrelandsTuning.*` field/constant these 3
files read against their real declarations in `PyrelandsMechanicsMod.cs`/
`PyrelandsTuning.cs` — all exist, all correctly typed. No functional bugs
found. All 3 confirmed reachable via `RimMandrake.Utinni.
PyrelandsMechanics.csproj`'s `<Compile Include>`. All 3 marked CLEAN, commit
`23259a0a9`, pushed. **This closes the entire `PyrelandsMechanics`
never-entered cluster.**

With time remaining, re-derived the never-entered survey fresh rather than
trust wave 21's "35 remain" tally — that tally turned out to be inflated by
a script bug (Windows-style backslash separators inside some `<Compile
Include>` paths, e.g. `LiquidTypes\Building_LiquidTank.cs`, joined wrong on
Linux and produced ~167 phantom "never-entered" entries for files that were
actually already CLEAN). Fixed the join (normalize backslashes before
joining) and re-ran across every `src/RimMandrake|RimStarWars|RimUtinni/**/
*.csproj`: **22 never-entered files genuinely remain**, all real files
confirmed present on disk. By folder: `GelatinousSlime/Source` (3),
`RimStarWars/TrophyCraft/Source` (3), `StructureInjectionsRUT/Source/
Ashfall` (3), `RimMandrake/Pyrelands/Source` (2), `bridgetools/JawaBench.
BridgeTools` (2), `LanternDeeps/Source` (2), and 1 each in `Aftermath/
Source`, `FlowWorks/Source` (`RM_StockMath.cs`), `FlowWorks/Source/SelfTest`
(`Program.cs` — still unconfirmed as part of the main assembly vs. a
standalone entry point, per wave 21's own caution), `Ninefold/Source`,
`SeaShores/Source/SelfTest` (`Program.cs`, same caution), `WreckedMachines/
Source`, `UtinniPatches/Source`.

Reviewed the `RimStarWars/TrophyCraft/Source` cluster (3/3, its whole
`<Compile Include>` list, confirmed via `RSW_TrophyCraft.csproj`):
`RSW_FactionApparelThoughtExtension.cs` (17 lines, the DefModExtension
carrying which apparel + which factions), `RSW_ThoughtWorker_
ObserverFactionApparel.cs` (66, the ThoughtWorker plus `RSW_Thought_
ObserverBraveFang`'s opinion-multiplier override), `RSW_
TrophyCraftSettings.cs` (65, Mod Settings). Traced the whole mechanism
end to end: `RSW_TrophyCraft_Thoughts.xml`'s `ThoughtDef` sets
`thoughtClass`/`workerClass` to these exact two classes and ships
`factionDefNames` empty by design; `WyyyschokkFangPendantFactions.xml`
(RimUtinni Patches) fills it via `PatchOperationConditional`+
`PatchOperationAdd` with the 3 real faction defNames; `apparelDefName`
(`RSW_Apparel_FangPendant`) is a real ThingDef in `RSW_TrophyCraft_
Items.xml`; the XML's `baseOpinionOffset` of 8 matches the settings UI's
"(base +8 opinion)" label exactly. Cross-checked `ThoughtWorker.def`
(real field), `ThoughtWorker.CurrentSocialStateInternal(Pawn p, Pawn
otherPawn)` (real virtual signature, `p`=observer/`otherPawn`=wearer per
the file's own cross-check against vanilla's `ThoughtWorker_Precept_
GroinUncovered_Social`), and `Thought_SituationalSocial.OpinionOffset()`
(real virtual, correctly overridden) against the decompiled engine. No
bugs found. All 3 confirmed reachable via `RSW_TrophyCraft.csproj`'s
`<Compile Include>`. All 3 marked CLEAN, commit `23259a0a9`, pushed.
**This closes the entire `TrophyCraft` never-entered cluster.**

Next wave: 16 never-entered files remain (22 minus this wave's 3) —
re-derive with the fixed backslash-safe recipe above rather than trust this
count. Largest remaining clusters: `GelatinousSlime/Source` (3),
`StructureInjectionsRUT/Source/Ashfall` (3, the Rakatan command-codes
mechanic), `RimMandrake/Pyrelands/Source` (2), `bridgetools/JawaBench.
BridgeTools` (2, `JawaBenchAbilityTools.cs`/`JawaBenchInhabitedTools.cs`),
`LanternDeeps/Source` (2). Confirm the two `SelfTest/Program.cs` files'
reachability (standalone entry point vs. main-assembly member) before
reviewing either. The 284-row re-dirtied backlog and the binary-art-tracking
scope question from wave 15 are both still untouched.

## Wave 23 — 2026-09-24: `GelatinousSlime` + `bridgetools` never-entered clusters CLOSED

Re-derived the never-entered list fresh with the backslash-safe join wave
22's fix already carries (normalize `\` to `/` before joining, verified
still correct — no phantom entries this pass): **19 genuinely never-entered
files remain**, all confirmed present on disk against every
`src/RimMandrake|RimStarWars|RimUtinni/**/*.csproj`'s `<Compile Include>`
list (down from wave 22's 22 — 3 closed by `TrophyCraft` that same wave).

**Resolved the `SelfTest/Program.cs` reachability question first**, per
this wave's own brief: both `FlowWorks/Source/SelfTest/Program.cs` and
`SeaShores/Source/SelfTest/Program.cs` sit in their own standalone
`net8.0`/`net472` `.csproj` (`RimMandrakeFlowWorks.SelfTest.csproj`,
`RimMandrakeSeaShores.SelfTest.csproj` — `OutputType=Exe`, compiling the
REAL production `.cs` files in directly rather than reimplementing them,
per each project's own header comment), each with a documented run path
(`python3 src/RimMandrake/Utils/selftest_flowworks_stock.py` /
`selftest_seashores.py`). Confirmed both wrapper scripts exist and are
picked up by `run_selftests.py`'s `selftest*.py` glob over `SEARCH_ROOTS`
(the file's own header explains the broadened-from-`selftest_*.py` glob
fix) — so both `Program.cs` files are genuinely reachable, buildable,
runnable entry points in the standing pre-commit selftest suite, not
orphaned test scaffolding. They remain queued for review (not reviewed
this wave — this pass answered reachability, not content) since this
wave's time went to the two clusters below.

Reviewed 5 of the 19, full-file each, two clusters closed:

**`GelatinousSlime/Source` (3/3)**: `GeneConditions.cs` (135 lines,
`Gene_ForcesHediff`/`Gene_TheReek` — cross-checked `GasUtility.AddGas`'s
signature and `GasType.RotStink` against the vanilla `CompRottable`
precedent cited in the file's own header), `Titanoslime.cs` (1195,
`RM_CompEngulfer`'s full growth/swallow/digest/shed lifecycle — traced
`StageFor`'s hysteresis climb/fall, `ApplyStage`'s life-stage lock via
`Pawn_AgeTracker.LockCurrentLifeStageIndex`, and `TitanoslimeSpawnTuning`'s
reflection-based commonality slider; both `wildAnimals`
[private `List<BiomeAnimalRecord>`] and `cachedAnimalCommonalities`
[private `Dictionary<PawnKindDef, float>`] field names confirmed byte-exact
against the decompiled `RimWorld/BiomeDef.cs`, and `BiomeAnimalRecord`
confirmed a class so the `baseCommonality` dictionary's reference-identity
keying is sound. Noted one harmless dead branch in `ApplyStage` — an
`else if (CurLifeStageIndex != target)` that can never be true since
`current` was captured from that same property moments earlier and nothing
mutates it in between — not a functional bug, left as-is), and
`TitanoslimeVerb.cs` (45, `RM_Verb_MeleeEngulf` — a thin `Verb_
MeleeAttackDamage` override, matches the file's own cited seam against
`Verb_MeleeAttackDamage.ApplyMeleeDamageToTarget`). All settings fields
(`titanoslimeMaxStage`/`Grows`/`Reversible`/`Engulfs`/`Sheds`/
`SpawnFactor`) and all `SlimeDefs`/`SlimeUtility` statics these files read
confirmed real and wired in `SlimeMod.cs`/`Slimification.cs`.

**`bridgetools/JawaBench.BridgeTools` (2/2)**: `JawaBenchAbilityTools.cs`
(1137, `jawa/select_things` + `jawa/pawn_use_ability` + `jawa/pawn_use_verb`
— the non-colonist pawn driving tools) and `JawaBenchInhabitedTools.cs`
(161, `jawa/inhabited_settlement_create`, `SETTLEMENT_VISIT_LOOP_1`'s
non-interactive settlement producer). Cross-checked every one of the six
"engine facts" `JawaBenchAbilityTools.cs`'s own header cites against the
decompiled source: `Ability.CanApplyOn` reading the private `effectComps`
field rather than the `EffectComps` property (confirmed,
`RimWorld/Ability.cs:362-368`), `Ability.Activate` applying `EffectComps`
only with no verb fired (confirmed), `Verb.TryStartCastOn`'s
Bursting/`CanHitTarget` refusal (confirmed, `Verse/Verb.cs:324-335`), and
`HediffSet.GetHediffsVerbs()` returning the shared `tmpHediffVerbs` buffer
a next call clears (confirmed, `Verse/HediffSet.cs:761-776`) — all four
read exactly as claimed. For `JawaBenchInhabitedTools.cs`, confirmed
`DebugActions_Inhabited.CreateAndEnterSettlement`/`TryEnterSettlementMap`'s
real signatures match the call site exactly
(`src/RimMandrake/Inhabited/Source/DebugActions_Inhabited.cs:150,192`), and
`SettlementCasing`'s `everVisited`/`visitCount`/`knownDistrictLabels`
fields this tool's `casing` result block reads are all real and Scribed.
One precision nuance, not fixed: the file's description string says
`MapParent.PostRemove` "unconditionally calls `DeinitAndRemoveMap`" — the
decompiled source gates it on `if (HasMap)`
(`RimWorld.Planet/MapParent.cs:110-116`), so it is conditional in the
literal code, but every MapParent this tool actually encounters (an
already-generated tile) always `HasMap`, so the claim holds in every case
this tool matters for. Left as-is, same call as wave 16's imprecise-but-
harmless comment.

No bugs found in any of the 5. Fixes: none this wave — a clean pass. All 5
marked CLEAN, commit `b21473703`, pushed. **This closes both the
`GelatinousSlime/Source` and `bridgetools/JawaBench.BridgeTools`
never-entered clusters.**

Next wave: 14 never-entered files remain (19 minus this wave's 5) —
re-derive rather than trust this count. Remaining clusters:
`StructureInjectionsRUT/Source/Ashfall` (3, the Rakatan command-codes
mechanic), `RimMandrake/Pyrelands/Source` (2, `PlantGrowthStages.cs`/
`RM_PyrelandsDensityEnforcer.cs`), `LanternDeeps/Source` (2,
`GenStep_LanternstoneRock.cs`/`GenStep_ScatterLanternstone.cs`), and 1 each
in `Aftermath/Source` (`Patch_PayloadLanded.cs`), `FlowWorks/Source`
(`RM_StockMath.cs`), `FlowWorks/Source/SelfTest` (`Program.cs`, reachability
now CONFIRMED above — ready to review), `Ninefold/Source`
(`Patch_GravshipLanded.cs`), `SeaShores/Source/SelfTest` (`Program.cs`,
reachability now CONFIRMED above — ready to review), `WreckedMachines/
Source` (`WreckedMachinesMod.cs`), `UtinniPatches/Source`
(`BlueDesertLife.cs`). **This is small enough (14 files) that a future wave
should be able to close out the entire never-entered `.cs` backlog in one or
two more waves.** After that, the loop's only remaining backlogs are the
284-row re-dirtied set (diagnosed wave 15, not yet re-reviewed) and the
never-independently-confirmed 13 `Utils/` Python tools from the post-tail
survey (wave 14) — the binary-art-tracking scope question (wave 15) is
still open and unresolved.

## Wave 24 — 2026-09-24: the never-entered `.cs` backlog is CLOSED

Re-confirmed wave 23's 14-file list against `code_review_status.py check`
(all 14 DIRTY/"never marked clean") and against each owning `.csproj`'s
`<Compile Include>` (or, for `Ninefold.csproj`, its documented default-glob
compile — the csproj's own comment records that a hand-maintained
`<Compile Include>` list once silently dropped 10 `Patch_*.cs` files
including both `Pawn.Kill` hooks, which is why it now compiles every `.cs`
under `Source/` by default) before touching anything. All 14 confirmed
reachable. Reviewed all 14, full-file each — this closes the entire
never-entered `.cs` backlog in one wave, as wave 23 predicted:

- **`StructureInjectionsRUT/Source/Ashfall`** (3/3): `AshfallCommandCodesFlag.cs`
  (51 lines, static flag + `Seize()`), `CompRedeemRakatanCommandCodes.cs` (41,
  the redeem gizmo), `GameComponent_AshfallCommandCodes.cs` (28, Scribed
  persistence). Confirmed `StructureInjectionsRUTSettings.ashfallCommandCodesEnabled`
  is a real, correctly-wired static.
- **`RimMandrake/Pyrelands/Source`** (2/2): `PlantGrowthStages.cs` (269, the
  three-stage plant growth art `DefModExtension` + `Plant_GrowthStaged`
  subclass) and `RM_PyrelandsDensityEnforcer.cs` (71, the post-load
  plantDensity re-assertion GameComponent). Cross-checked
  `Plant.Graphic`'s exact rung order (Sowing → polluted → leaflessImmature →
  leafless → immature) and the `CurrentlyCultivated()` mesh-dirty gate
  against the decompiled `RimWorld/Plant.cs` (lines 474-492, 827) — both
  match byte-for-byte as the file's own comments claim.
- **`LanternDeeps/Source`** (2/2): `GenStep_LanternstoneRock.cs` (66, appends
  a `RockNoises.RockNoise` entry so a pocket map's lanternstone rock rides
  the engine's own rock-noise mechanism) and `GenStep_ScatterLanternstone.cs`
  (76, the settings-gated crystal scatter). Cross-checked `RockNoises.Init`/
  `RockNoise.rockDef`/`.noise` and `GenStep_Scatterer.countPer10kCellsRange`
  against the decompiled `Verse/RockNoises.cs` and `Verse/GenStep_Scatterer.cs`
  — field names and the Perlin constructor's parameters match exactly.
- **`Aftermath/Source`**: `Patch_PayloadLanded.cs` (30, a Harmony postfix on
  `IncidentWorker.TryExecute` — confirmed that is the single funnel every
  incident category's successful fire passes through, decompiled
  `RimWorld/IncidentWorker.cs:183`).
- **`FlowWorks/Source`**: `RM_StockMath.cs` (316, the whole §5 source-stock
  arithmetic — Verse-free by design so `Source/SelfTest/` can compile it in
  directly). Cross-checked every one of its 15 public members against its
  real call sites in `RM_LiquidStock.cs`/`RM_LiquidBody.cs`/
  `RM_MapComponent_Excavation.cs`: argument order and units match at every
  call.
- **`FlowWorks/Source/SelfTest/Program.cs`** and **`SeaShores/Source/SelfTest/
  Program.cs`** (both reachability-confirmed in wave 23, reviewed for content
  this wave): hand-traced a sample of each suite's assertions against the
  production formulas/logic they exercise (`RM_StockMath`'s budget/refill/
  recession/displacement arithmetic; `RM_SeaShoreUtility.DeepTerrainOf`/
  `ShallowTerrainOf`/`BandFor`'s resolution-order and salt/fresh-fallback
  logic) — every assertion's expected value matches what the real code
  actually computes.
- **`Ninefold/Source`**: `Patch_GravshipLanded.cs` (38, a Harmony postfix on
  `GenStep_GravshipMarker.Generate` calling `GameComponent_Ninefold.
  ReckonFrontAtLanding()`). Checked this against `GameComponent_Ninefold.
  FinalizeInit`, which also calls `ReckonFrontAtLanding()` as a baseline —
  confirmed this is the documented dual-call design (baseline at
  `FinalizeInit`, overwritten at every real landing), not a double-fire bug.
- **`WreckedMachines/Source`**: `WreckedMachinesMod.cs` (240, Mod Settings +
  a `[StaticConstructorOnStartup]` patcher that captures shipped baselines
  once and rescales from them on every `Apply()`, same non-compounding
  pattern wave 7 verified in `RSW_GizkaSettings.cs`). Cross-checked
  `ThingDefCountClass`'s constructor and `Scribe_Values.Look`'s 4-arg
  overload against the decompiled `Verse/ThingDefCountClass.cs` and
  `Verse/Scribe_Values.cs` — both match.
- **`UtinniPatches/Source`**: `BlueDesertLife.cs` (243, the Blue Desert's
  hydrocarbon fauna/flora mechanics — explosion-on-part-destroyed, flora
  warm-detonation chain, cold-wax temperature-ruin wiring, the Burner's
  conditional halo VFX, and the natives' toxin exemption). Cross-checked
  `HediffComp.Notify_PawnPostApplyDamage`'s signature, `CompTemperatureRuinable.
  RuinedSignal`'s literal value, `CompEffecter.ShouldShowEffecter`'s
  protected-virtual signature, `IngestionOutcomeDoer_GiveHediff.
  DoIngestionOutcomeSpecial`'s signature, and `GenExplosion.DoExplosion`'s
  full named-parameter list against the decompiled engine — all match. Every
  `UtinniPatchesSettings.*` field it reads is a real, correctly-wired static.

No bugs found in any of the 14; no fixes needed this wave — a clean pass.
All 14 marked CLEAN, commit pending below, pushed.

**🔴 THE NEVER-ENTERED `.cs` BACKLOG IS NOW CLOSED.** Every reachable `.cs`
file across `src/RimMandrake|RimStarWars|RimUtinni/**/*.csproj` (backslash-
safe join, per wave 22's fix) that was never once recorded in
`CODE_REVIEW_STATUS.json` has now been full-file reviewed and marked CLEAN.
Waves 3 through 24 covered this ground; the loop's remaining work is the two
backlogs wave 23 already named and neither is touched this wave:

1. **The 284-row RE-DIRTIED backlog** (files previously marked CLEAN, then
   changed and gone DIRTY again) — diagnosed wave 15 as real organic drift,
   not an instrument bug. Needs individual full-file re-review, file by
   file, same discipline as this loop's never-entered pass. Re-derive the
   live count with `code_review_status.py list` rather than trusting "284"
   — it will have moved.
2. **The scope question**: does binary PNG art belong in this tool's
   tracking at all? Flagged wave 15. Needs owner input — do not decide it
   yourself, and do not let either backlog block on it; they are
   independent.

Whoever picks up wave 25: start the re-dirtied backlog, smallest files
first per this loop's established recipe, and re-derive every count fresh
before reporting it.

## Wave 39 — 2026-09-24: two stale wave-38 claims corrected; 5 of the 13 never-entered Utils Python tools CLOSED

First action, per this wave's own brief: wave 38's "Next wave" paragraph
carried two stale claims and was corrected in place (commit `ff8b3a821`,
separate from the review commit below) — (1) it called the PNG
binary-art-tracking scope question "still open" when the orchestrating
window had already resolved it with the owner earlier this same session
(deterministic bulk probe, 161/161 PNGs CLEAN, permanently out of scope —
see the FOUNDRY 2026-09-24 note above); (2) it listed "95 never-entered `.cs`
files" as a wave-39 candidate when wave 24 (above) already closed that whole
backlog in full. Neither claim is re-litigated here; both are now correct at
the source.

Then ran `code_review_status.py list` fresh (`/mnt/d/Luke/dev/Rimworld/src/RimMandrake/Utils/code_review_status.py list`,
from repo root): **41 DIRTY rows total, all non-`.png`, all "content changed
since clean mark" (re-dirtied, not never-entered)** — the 284-row backlog
wave 25 started has been worked down to 41 by waves 25-38's diff-scoped
passes. None of those 41 were touched this wave (see "next wave" below).

Per the brief, checked the one candidate class never independently verified
either way: the **13 never-entered Utils Python tools flagged in wave 15**.
Confirmed reachability first for all 13 via `code_review_status.py check`
(all still DIRTY "never marked clean" — genuinely untouched) and a repo-wide
grep for each filename: every one is named in a live item doc, a handoff, a
skill's usage doc, or has a sibling `selftest_*.py` — none is a dead-file
candidate. Full-file reviewed the 5 smallest: `apply_blanket_ruling.py` (99
lines, blanket-ruling stamper with `--over-sitting` refusal on a real
sitting), `artpipe/requeue_quota_failures.py` (62, quota-failure requeue
daemon — verified its `parents[4]` root-path arithmetic resolves to the repo
root from its actual location), `check_pseudo_sw_name.py` (132, pseudo-SW
name shape/collision heuristic), `label_collision_check.py` (209, CAST-animal
label-collision checker — verified its `dump_db`/`DUMP_ROOT` imports and its
None-means-UNMEASURED contract match `dump_manifest.py`'s real API), and
`sheet_to_artifact.py` (163, review-sheet-to-artifact-db backend patcher —
verified its spliced `frozen = false` JS assignment targets the page-level
`let frozen` the template already declares, same pattern `ServerBackend`/
`FileBackend` use, not an accidental implicit global). No bugs found in any
of the 5. All 5 marked CLEAN, commit `1a838c529`, pushed.

**8 of the 13 never-entered Utils Python tools remain**:
`artpipe/build_flora_legibility_sheet.py` (335), `artpipe/facing_set_audit.py`
(248), `build_landmark_density_sheet.py` (315), `canon_census.py` (230),
`ecosystem_pyramid_check.py` (339), `modcheck/readline_registry.py` (215),
`stage_review.py` (409), `stage_xenotype_grid.py` (310) — all confirmed
reachable (same grep sweep as above), none reviewed yet.

Next wave: either continue this cluster (8 left, largest first or smallest
first per taste — none is blocked on another) or resume the 41-row re-dirtied
backlog (`code_review_status.py list | grep '^DIRTY'` from repo root,
re-derive the count fresh, do not trust "41" next wave). The item file itself
is now past 2500 lines and getting unwieldy for a human or agent to read in
full each wave — flagging for a future archiving/summarizing pass, not doing
it this wave.

## Wave 25 — 2026-09-24: re-dirtied backlog started, non-PNG only

Re-derived the DIRTY count fresh: `code_review_status.py list | grep -c
'^DIRTY'` gave **283** (284 minus one, ordinary drift since wave 15/24 — no
tooling bug). Broke it down by extension: **161 `.png`, 74 `.xml`, 32 `.py`,
13 `.cs`, 2 `.txt`, 1 `.csproj`** — **122 non-PNG**. Per this wave's brief,
PNGs stay untouched this pass (wave 15's open scope question — does
`code_review_status.py` even belong tracking binary art — is still
unresolved and still not this loop's call).

Reviewed 5 of the 122 non-PNG DIRTY files, diff-scoped against each file's
own clean-mark sha (all were CLEAN once, so full-file re-review was not
required — CLAUDE.md's own rule):

- **`.claude/hooks/queue_lint.py`** (+80/-30 since `91c3f95e8`) and
  **`.claude/hooks/selftest_queue_lint.py`** (+19 since the same sha) —
  prioritized per wave 14's own note that this loop's enforcement code is
  the worst kind of self-inflicted gap. Both diffs are the ledger-sharding
  retrofit (`EVENTS_JSONL_SHARDING_1`, 2026-09-23): `queue_lint.py` adds
  `is_ledger_file()` and `_ledger_events()` (merges the frozen head +
  per-seat shards, ts-sorted) and rewires `owners()`/`LEDGER_PATH_RE`/
  `main()`'s Write-guard onto them; `selftest_queue_lint.py` adds matching
  DENY/ALLOW cases for shard writes, shard commits, and a decoy non-ledger
  `.jsonl` beside the shard dir. Traced the merge-sort's "frozen history
  always precedes shards" claim (holds because frozen events carry earlier
  timestamps, and ties resolve by list order since `LEDGER` is first in
  `paths`) and ran the suite directly: `python3 .claude/hooks/
  selftest_queue_lint.py` → **55/55 passed**. No bugs found.
- **`RM_JobDefOf.cs`** (+2 since `3bcf80ccf`), **`RM_ThinkTree_
  VerminBehaviors.xml`** (+12/-1 since `99a9e5cbc`), **`RM_JobDefs.xml`**
  (+12 since `0aa131589`) — all three are one coherent change,
  `DESERT_SHADE_WHALE_FILTERFEED_1` wiring in a new `RM_FilterFeedTerrain`
  JobDef. Cross-checked the two classes it names
  (`RM_JobDriver_FilterFeedTerrain`, `RM_JobGiver_FilterFeedTerrain`) exist
  on disk, and verified the ThinkTree comment's ordering claim ("tried
  before vanilla hunger handling, sits last in the priority list on
  purpose") against the JobGiver's own docstring and the actual
  `insertTag`/`subNodes` order — both agree. No bugs found.

All 5 had zero uncommitted changes (`git status --porcelain` empty before
marking), so no fix-then-verify step was needed. All 5 marked CLEAN, commit
`5e0d7edad`, pushed.

Next wave: 117 non-PNG DIRTY files remain (122 minus this wave's 5: 2 `.py`
hooks + 3 `.cs`/`.xml` closed this wave, out of the pre-wave 74 `.xml` / 32
`.py` / 13 `.cs` / 2 `.txt` / 1 `.csproj` breakdown) — re-derive with
`code_review_status.py list | grep '^DIRTY'` filtered for non-`.png` rather
than trusting this arithmetic. The PNG binary-art-tracking scope question
(wave 15) is still open and still not this loop's to decide.

## Wave 26 — 2026-09-24

Re-derived fresh: `code_review_status.py list | grep -c '^DIRTY'` gave 278
(284→283→278, ordinary drift — no tooling bug); filtered for non-`.png` gave
exactly **117**, matching wave 25's prediction. Reviewed 5, diff-scoped
against each file's own clean-mark sha (all were CLEAN once):

- **`design/Jawa/mods/biome_flora.py`** (+263/-57 since `51867f432`) — the
  emitter change from `BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1` (2026-09-21): a
  new `owned_flora()` parses the BiomeDefs we author ourselves and `main()`
  now skips emitting a `wildPlants`/`plantDensity` patch operation for any
  biome we own (its own def is the shipping truth), while `check()` gained a
  cross-check that fails the build if an owned def's `wildPlants` disagrees
  with its roster. Traced the skip logic (family-level `all(b in ours ...)`
  short-circuit plus the per-biome `if b in ours: continue` inside the loop)
  and confirmed it's redundant-but-correct, not a double-skip bug. Ran
  `python3 design/Jawa/mods/biome_flora.py --check`: the live def dump is
  stale/UNMEASURED for the current capture (expected, per CLAUDE.md's
  def-dump-currency doctrine — not exercised further, this file's own logic
  was traced by hand instead). No bugs found.
- **`design/Jawa/mods/plant_tolerances.py`** (+75/-4 since `3ea1ca20`) — two
  already-fixed bugs from the same day
  (`PLANT_TOLERANCE_VERIFY_STALE_CLIMATE_KEYS_1` /
  `_REGEN_AFTER_KEY_FIX_1`): climate-median lookup now resolves through
  `rosters/*.json`'s own `defNames` list instead of a frozen, since-renamed
  `biome_climate.json` key, and `compute()`'s "already survives its whole
  home, leave alone" skip is now gated `p in donors` so a plant whose `cur`
  fell back to the live dump (this patch's own prior output) re-affirms its
  widened band instead of silently dropping it on regen. Both fixes traced
  against their own surrounding code and confirmed internally consistent.
  No bugs found.
- **`design/Jawa/worldbuilding/biomes/rosters/_validate.py`** (+41/-16 since
  `bb73b6bd`) — `PAINTED_DEFS` is now derived from
  `world/ASHKARR_WORLDMAP_tiles.csv` instead of a hand-maintained literal
  that had drifted 19/19 false after the world was repainted onto `RUT_*`
  defs; confirmed `RUT_BlueDesert` (previously a hardcoded "pending-switch"
  exception) is genuinely present in the live CSV so dropping that carve-out
  does not regress it. Also fixed `cross_check()` to check a target roster's
  `flora` list as well as `fauna` (a flora eviction move was previously
  always reported as a false positive). Ran `python3 _validate.py` from
  `design/Jawa/worldbuilding/biomes/rosters/`: exits clean, only the
  expected "typo, or already gone?" eviction warnings, no errors. No bugs
  found.
- **`src/RimMandrake/Utils/repair_torn_ledger.py`** (+19/-2 since
  `113ad7131`) — adds `--seat <SEAT>` to target a per-seat ledger shard
  (`ledger/events/<SEAT>.jsonl`) post-`EVENTS_JSONL_SHARDING_1`, and fixes
  the backup filename to use `path.name` instead of a hardcoded
  `events.jsonl` (would have silently mislabeled a shard's backup). No bugs
  found.
- **`src/RimUtinni/UtinniPatches/Source/UtinniPatchesSettings.cs`** (+45/-0
  since `18e1ab1b6`) — adds 6 Mod Settings fields for
  `BLUE_DESERT_LIFE_AUTHORING_1`. Cross-checked all 6 field names
  (`nativeDetonationsEnabled`, `floraChainReactionsEnabled`,
  `coldWaxWarmReactiveEnabled`, `butaneGutEnabled`, `burnerHaloEnabled`,
  `warmDetonationThresholdC`) against their read sites in
  `BlueDesertLife.cs` — every one matches exactly. No bugs found.

All 5 had zero uncommitted changes before marking. All 5 marked CLEAN,
commit pending below, pushed.

Next wave: 112 non-PNG DIRTY files remain (117 minus this wave's 5) —
re-derive with `code_review_status.py list | grep '^DIRTY'` filtered for
non-`.png` rather than trusting this arithmetic. The PNG binary-art-tracking
scope question (wave 15) is still open and still not this loop's to decide.

## Wave 27 — 2026-09-24

Re-derived fresh: `code_review_status.py list | grep -c '^DIRTY'` gave 273
(278→273, ordinary drift, no orphaned/missing rows — all 273 paths exist on
disk); filtered for non-`.png` gave exactly **112**, matching wave 26's
prediction. Reviewed the 5 smallest, diff-scoped against each file's own
clean-mark sha (all were CLEAN once):

- **`src/RimStarWars/Armoury/Defs/Absorbed_KotorWeapons/
  Absorbed_KotorWeapons_BLOCKED_manifest.txt`** (1 line changed since
  `0fc737f9d`) — a bare item-ID typo fix in a comment,
  `ARMOUR_MW2_CUT_1` → `ARMOURY_MW2_CUT_1`. No bug; the corrected ID is the
  real item name.
- **`src/RimUtinni/PlantGrowth/Defs/JawaPlantGrowthSettings.xml`** (+7 since
  `ff35f27f`) — adds `RM_Palefloss`/`RM_Glassfern`/`RM_Chimeglobe` to
  `<exemptPlants>` for `BLUE_DESERT_LIFE_AUTHORING_1`, with a comment
  explaining why (their growDays already assume vanilla rate; a x4 growth
  multiplier would erase the "less efficient without polar water" point of
  those numbers). Comment's claim checked against the three plants' own
  `growDays` values — consistent. No bug.
- **`src/RimUtinni/LanternDeeps/Patches/RUT_LanternDeepEvictCrystalFauna.xml`**
  (2-line comment correction since `bb73b6bd`) — fixes a stale claim that
  this mod declares `BMT_CrystalCaverns` a hard `modDependency`; checked
  `LanternDeeps/About/About.xml` directly — it lists only Harmony as a
  dependency, confirming the corrected comment (not the original) is true.
  A real prior inaccuracy, now fixed — no further action needed.
- **`src/RimUtinni/RotSporeKit/Defs/ThingDefs_Items/
  RUT_RotSporeKit_FurnaceCap.xml`** and **`.../ThingDefs_Plants/
  RUT_RotSporeKit_FurnaceCap.xml`** (both since `d4559b984`, `ROT_ART_WAVE_1`/
  `ROT_FLORA_FAUNA_VERDICTS_1`) — both retarget `texPath` off shared
  placeholder art (`MortalMorel`/`CrimsonCap`) onto newly authored own-folder
  art (`LivingFurnaceCap`, `FurnaceCapPlant`) and update the "ART OWED"
  docstring comments accordingly. Per CLAUDE.md's texPath-binds-by-texPath
  warning, verified the art actually exists at the new paths rather than
  trusting the comment: `Textures/RotSporeKit/Things/Item/Crops/
  LivingFurnaceCap/LivingFurnaceCap_A.png` and `Textures/RotSporeKit/Things/
  Plant/FurnaceCapPlant/FurnaceCapPlant_A.png` both present on disk,
  `_A` suffix matching `Graphic_StackCount`/`Graphic_Random`'s expected
  single-variant naming. No bug.

All 5 had zero uncommitted changes before marking (`git status --porcelain`
empty). All 5 marked CLEAN, commit pending below, pushed.

Next wave: 107 non-PNG DIRTY files remain (112 minus this wave's 5) —
re-derive with `code_review_status.py list | grep '^DIRTY'` filtered for
non-`.png` rather than trusting this arithmetic. The PNG binary-art-tracking
scope question (wave 15) is still open and still not this loop's to decide.

## Wave 28 — 2026-09-24

Re-derived fresh: `code_review_status.py list | grep -c '^DIRTY'` gave 268
(273→268, ordinary drift); filtered for non-`.png` gave exactly **107**,
matching wave 27's prediction. Picked 5 for breadth across areas this
backlog hadn't touched yet (Utils tooling, FlowWorks def XML, LanternDeeps
patch XML, Pyrelands terrain XML, an Armoury absorption generator script),
diff-scoped against each file's own clean-mark sha (all were CLEAN once):

- **`src/RimMandrake/Utils/broadcast.py`** (1 line since `0a8d8761`) — the
  ledger-sharding retrofit's follow-on: `seats_waiting_on_the_game()` now
  calls `model.read()` with no argument instead of `model.read(model.
  EVENTS)`. Verified against `model.py`'s own `read()` docstring, which
  states plainly that a bare `model.EVENTS` argument now means "the history,
  without today" post-sharding and that every production caller was
  converted 2026-09-23 — this was exactly that conversion, correctly done.
  No bug.
- **`src/RimMandrake/FlowWorks/Defs/ManyWaters/ThingDefs/
  RM_ColoredWaterBottles.xml`** (1 line since `d0b0d6b7b`) — a comment's
  cross-reference path corrected from `src/RimStarWars/UtinniPatches/...`
  to `src/RimUtinni/UtinniPatches/...` (the NAMING_SCHEME_EXECUTION_1
  tier move). Confirmed the RimStarWars path no longer exists and the
  RimUtinni path does. A real prior inaccuracy, now fixed. No bug.
- **`src/RimUtinni/LanternDeeps/Patches/
  RUT_LanternDeepGateKotorStygium.xml`** (2 lines since `1dc7382d`) — a
  doc-comment correction recording that `guy762.mm.kotorcore` (the donor
  whose live GenStepDef this patch used to describe as active) is now
  ABSENT from the live ModsConfig as of 2026-09-23, so the op it documents
  matches nothing today — consistent with CLAUDE.md's "a patch that matches
  nothing logs nothing" doctrine, not a defect. No bug.
- **`src/RimMandrake/Pyrelands/Defs/TerrainDefs/AshLadder.xml`** (+4/-1
  since `90940c68`) — moves `texturePath` off the shared abstract
  `RM_FE_AshBase` and onto each of the four concrete ash-depth terrains
  individually (`RM_FE_Ash_Trace/_Light/_Heavy/_Deep`). Verified all four
  referenced textures (`RM_FE_Ash_Trace.png` etc.) actually exist on disk
  under `Pyrelands/Textures/Terrain/Surfaces/` — a real per-terrain art
  differentiation, not a placeholder-path guess. No bug.
- **`src/RimStarWars/Armoury/Source/gen_sovsith_absorption.py`** (+17 since
  `ee0b3ad6`) — adds a body-type-suffixed texture search
  (`<path>_<BodyType>_<rotation>.ext`) to `find_and_copy_texture` and adds
  `wornGraphicPath` to the set of collected texture-path attributes, per
  the added comment's correct account of `ApparelGraphicRecordGetter`'s
  real naming scheme and of `wornGraphicPath` being a genuine third texture
  root distinct from `texPath`/`iconPath`. Traced the nested-loop `rot`
  variable reuse (inner loop redefines `rot` after the outer rotation loop
  already finished) — shadowing, not a bug, since the outer loop's `rot`
  is not read again after the inner loop starts. No bug.

All 5 had zero uncommitted changes before marking (`git status --porcelain`
empty). All 5 marked CLEAN, commit `5952f0306`, pushed.

Next wave: 102 non-PNG DIRTY files remain (107 minus this wave's 5) —
re-derive with `code_review_status.py list | grep '^DIRTY'` filtered for
non-`.png` rather than trusting this arithmetic. Candidates not yet touched
in this backlog include the 27-file `RUT_*` BiomeDef cluster under
`UtinniPatches/Defs/BiomeDefs/`, the `~15`-file `RSW_*ThingDefs_Races`
cluster under `SWBestiary/Defs/ThingDefs_Races/`, the bridgetools `.cs`
files (`JawaBenchPawnKitTools.cs`, `JawaBenchRenderTools.cs`,
`JawaBenchTerrainTools.cs` — safety-critical, use full-file context per
this item's own protocol), and the `rimflow`/`Utils` Python tooling
(`selftest_concurrency.py`, `codebase_health.py`, `handoff.py`,
`modset_builder.py`, `run_selftests.py`, several `artpipe/*.py`). The PNG
binary-art-tracking scope question (wave 15) is still open and still not
this loop's to decide.

## Wave 29 — 2026-09-24: bridge-tools priority, 2 of 3 cleared

Per the owner's explicit brief for this wave: prioritized the three
bridge-tools files named in wave 28's note (`JawaBenchPawnKitTools.cs`,
`JawaBenchRenderTools.cs`, `JawaBenchTerrainTools.cs`) over the rest of the
102-file non-PNG backlog, at a HIGHER bar than this loop's normal diff-scoped
re-review: full-file review of all three even though each was previously
CLEAN, with every `[Tool]` method's engine-API usage cross-checked line by
line against `/mnt/d/Luke/dev/reference/rimworld-decompiled` rather than
trusting the file's own inline claims about engine behavior (several of
which cite specific method signatures and silent-failure modes from prior
review passes).

Re-confirmed DIRTY (all three re-dirtied since their original 2026-09-03/
2026-09-18 clean marks — ordinary drift, ~9155 combined lines, `git status`
showed no in-flight edits from another window before starting):
`JawaBenchPawnKitTools.cs` (961 lines, clean-marked 2026-09-03),
`JawaBenchRenderTools.cs` (1184 lines, clean-marked 2026-09-03),
`JawaBenchTerrainTools.cs` (7010 lines, clean-marked 2026-09-18).

**Reviewed and cleared 2 of 3 this wave** (the 7010-line `JawaBenchTerrainTools.cs`
is roughly 3x the combined size of the other two and was not started this
wave — thoroughness over count, per this wave's own brief):

- **`JawaBenchPawnKitTools.cs`** (Group E: skills/relations/abilities/
  inspiration/psychic/genes/apparel-locking/inventory-and-stack tools).
  Cross-checked against the decompiled engine: `Pawn_SkillTracker.Learn`/
  `SkillRecord.Learn`/`SkillRecord.TotallyDisabled` (the mutant `CanGainXP`
  gate the tool re-checks separately is EXACTLY what `Pawn_SkillTracker.Learn`
  itself gates on — `ModsConfig.AnomalyActive && pawn.IsMutant &&
  !pawn.mutant.Def.canGainXP` — confirmed identical), `Pawn_AbilityTracker.
  GainAbility`/`GetAbility`, `InspirationHandler.TryStartInspiration`/
  `BlockedByHediff` (confirmed the tool's pre-check of `CurStage.
  blocksInspirations` reproduces the engine's own private gate exactly, so
  the "should not be reachable" claim after a forced `EndInspiration` holds),
  `GeneUtility.OffsetHemogen`/`SatisfyChemicalGenes`, `Gene_Resource.Value`/
  `Max`, `Pawn_GeneTracker.GetFirstGeneOfType<T>`/`ClearXenogenes`,
  `Pawn_ApparelTracker.Lock`/`Unlock`/`LockAll`/`UnlockAll`/`IsLocked`,
  `Pawn_InventoryTracker.RemoveCount` (confirmed it touches at most ONE
  matching stack per call via its `break` after the first match, exactly as
  the tool's own comment claims — justifying the tool's own loop-until-gone
  retry logic), `Thing.SplitOff` (confirmed the `count >= stackCount` branch
  DeSpawns and returns the ORIGINAL thing rather than a copy — the tool
  correctly refuses that case strictly before calling, so it never hits that
  branch), `GenPlace.TryPlaceThing`, `Thing.TryAbsorbStack`. Every signature
  and every behavioral claim in the file's own extensive comments (many
  citing specific prior 2026-09-02/09-03 code-review fixes) matched the
  engine exactly. No bugs found.
- **`JawaBenchRenderTools.cs`** (Group K: buildings/construction, Anomaly,
  save/load side artifacts, rendering/camera/screenshots, terrain/roof/heat,
  stat-explanation). Cross-checked: `GenConstruct.CanPlaceBlueprintAt`/
  `PlaceBlueprintForBuild` (both full parameter lists match positionally),
  `Frame.CompleteConstruction`, `GameComponent_Anomaly.SetLevel`/`Level`/
  `LevelDef`, `PortraitsCache.Get` (confirmed `supersample=false,
  compensateForUIScale=false` are the correct positional args to get exactly
  width×height out, matching the tool's own comment about why), `CompHolding
  PlatformTarget`'s `CompStudiable`/`HeldPlatform`/`CanBeCaptured`/`CanStudy`/
  `StudiedAtHoldingPlatform`/`CurrentlyHeldOnPlatform`/`isEscaping`/
  `extractBioferrite`/`containmentMode` fields, `CompStudiable.SetStudyEnabled`/
  `Study(Pawn, float, float)`/`studyPoints`/`anomalyKnowledgeGained`/
  `ProgressPercent`/`Completed`/`TicksTilNextStudy`/`KnowledgeCategory`,
  `GameDataSaveLoader`'s all 6 Save*/TryLoad* signatures (and confirmed
  `SaveScenario` et al. genuinely swallow their own exceptions via a
  try/catch-and-log, which is exactly why the tool reads the result back via
  `File.Exists` + size rather than trusting the call returning), `Global
  TextureAtlasManager.TryMarkPawnFrameSetDirty`/`DumpPawnAtlases`,
  `GenTemperature.PushHeat`, `Room.Temperature` (confirmed it has a real
  setter, not just a getter), `PowerNet`'s `hasPowerSource`/`connectors`/
  `transmitters`/`powerComps`/`batteryComps` fields, `StatRequest.For(Thing)`,
  `StatWorker.GetExplanationFull`/`ValueToString`. Every signature and claim
  matched. No bugs found.

`Current.Game.DeinitAndRemoveMap` (jawa/map_drop) and its documented
serialization-loop trap (`BRIDGE_MAP_DROP_SERIALIZATION_LOOP_1` — a
`PlanetTile.Tile` circular reference) were read for consistency with the
tool's own primitives-only response shape but not re-derived against the
engine independently this pass — the tool's defensive design (project every
field to a primitive BEFORE the deinit) is sound regardless of the exact
shape of that trap.

Both files had zero uncommitted changes before marking (`git status
--porcelain` empty). Both marked CLEAN, commit pending below, pushed.

**`JawaBenchTerrainTools.cs` (7010 lines) remains for the next wave** —
explicitly not started this wave, per this wave's own brief to favor
thoroughness over finishing all three. It is the single largest file in the
bridge-tools set and by a wide margin (all four `[Tool]`-bearing files this
loop has cross-checked bridge-response shapes against across waves 9-14 —
`GetDef`, `GetDefs`, `ListThings`, `MapInfo`, etc. — live in this file), so
a future wave should expect to spend real time on it and may need more than
one wave itself.

Next wave: finish `JawaBenchTerrainTools.cs` first (bridge-tools priority
still stands until it's done), then return to the 102-file non-PNG backlog
(now effectively 100, two down). Re-derive counts fresh rather than trusting
this arithmetic — it has drifted before.

## Wave 30 — 2026-09-24: `JawaBenchTerrainTools.cs` cleared, bridge-tools priority DONE

Per the owner's brief for this wave: finished the one bridge-tools file wave
29 left, `JawaBenchTerrainTools.cs` (7010 lines, clean-marked 2026-09-18,
re-dirtied since — the file this whole loop's waves 9-14 cross-checked
their validation.py bug hunt against, since it holds most of the
bridge-response shapes those 14 bugs turned out to be CALLER-side
misreadings of).

**Reviewed lines 1-7010 of 7010 — the entire file, full-file, in one
sitting.** Read it in ~15 overlapping sections of 200-430 lines each,
covering every one of its 29 `[Tool]`-attributed public methods
(`SetTerrain`, `SetTerrainBatch`, `GetTerrainBatch`, `SpawnBatch`,
`DestroyBatch`, `ListPawns`, `SetPlants`, `Damage`, `GetDef`, `DrainLog`,
`RefreshRectTool`, `SpawnPawn`, `SetPawnStyle`, `SetPawnRotation`,
`SetPawnXenotype`, `OrderPawn`, `WorldStats`, `WorldTileExport`, `GetDefs`,
`FireQuest`, `FireIncident`, `SendLetter` [both `#if JAWA_GM_TOOLS`],
`SetRoofBatch`, `GetRoofBatch`, `ListFactions`, `ClearUi`, `ListThings`,
`IdeoOf`, `BiomeProbe`, `InspectString`, `SetFactionRelation`,
`WorldNeighbors`) plus every private helper (`Scalars`,
`DeepSerializeValue`, `CompScalars`, `TryParseOps`, `RunLengthEncode`,
`ResolvePawns`, the terrain/roof layer helpers, the CSV/JSON tile-export
writers, the Vehicle Framework reflection shim).

Prioritized per this wave's brief: `GetDef` (line 1669), `GetDefs` (3965)
and `ListThings` (5422) first, cross-checked line by line against the
exact key-mismatch bugs waves 9-14 found in validation.py CALLERS
(`resolved`/`fields` on `GetDef`, `extra`-modelled-only-for-three-types,
`fields` on `GetDefs`, `things[]` with `hitPoints`/`def`/`id` on
`ListThings`) — every one of those response shapes in the actual C# matches
what the corrected validation.py callers now expect. The bugs waves 9-14
fixed were genuinely all on the calling side; the tool implementations
were already correct.

**No new bugs found anywhere in the file.** It already carries extensive
prior hardening directly visible in the comments — a `COMPANION_HARDENING_
AUDIT_2026-09-09` pass (findings #30/#31: bare try/catch-and-skip on pawn
capacities and reflection fields replaced with reported errors), an "opus
code review 2026-09-02" pass (at least 9 distinct fixed defects cited
inline: missing cell caps, `outOfBounds`/`thingsShort` not entering
verdicts, unconditional `success=true` on several batch tools, the
`RemoveEmptyEntries` ops-parsing shift bug, split terrain/roof perimeter
definitions, the `MaxFlightTime`-adjacent main-thread-livelock caps, the
`order_pawn` speed-restore-on-cancellation `finally` block), and a
`MASS_VALIDATION_LADDER_1` pass (2026-09-18, the `System.Type` field
serializing to `{}` fix in `DeepSerializeValue`). Spot-verified several of
these fix claims directly against the code rather than trusting the
comment (e.g. `RoofGrid.SetRoof`'s self-dirtying claim, the `GenSpawn.Spawn`
never-merges-stacks claim, the `TryTakeOrderedJob` accept-is-not-arrival
claim) and all held.

Zero uncommitted changes before marking (`git status --porcelain` empty).
Marked CLEAN, commit `e0f3787f4`, pushed.

**This closes the bridge-tools priority wave 29 opened.** All three files
named in wave 28's note (`JawaBenchPawnKitTools.cs`, `JawaBenchRenderTools.cs`,
`JawaBenchTerrainTools.cs`) are now CLEAN. Next wave: return to the non-PNG
backlog (was 102 at wave 28, minus wave 29's implicit 0 — those two files
were bridge-tools priority pickups, not backlog draws — re-derive fresh with
`code_review_status.py list | grep '^DIRTY'` filtered for non-`.png`). The
PNG binary-art-tracking scope question (wave 15) is still open and still
not this loop's to decide.

## Wave 31 — 2026-09-24: SWBestiary RSW_* race ThingDefs cluster closed

Resumed the general non-PNG re-dirtied backlog (bridge-tools priority is
done as of wave 30). Re-derived fresh: `code_review_status.py list | grep -c
'^DIRTY'` gave 260 total, 99 non-`.png`. Of the two named clusters wave 28
flagged, both were still present: the 25-file `RUT_*` BiomeDef cluster under
`UtinniPatches/Defs/BiomeDefs/` (untouched this wave) and the 13-file `RSW_*`
`ThingDefs_Races` cluster under `SWBestiary/Defs/ThingDefs_Races/` (all 13,
not just wave 28's estimated ~15 — the real count). Took the smaller,
fully-present cluster to close it out in one wave.

Reviewed all 13, diff-scoped against each file's own clean-mark sha (all
were CLEAN once): `RSW_Anooba.xml`, `RSW_Bantha.xml`, `RSW_Bolotaur.xml`,
`RSW_Cannok.xml`, `RSW_Clodhopper.xml`, `RSW_Convor.xml`,
`RSW_Corinathoth.xml`, `RSW_Eopie.xml`, `RSW_Iriaz.xml`, `RSW_Mudhorn.xml`,
`RSW_Nuna.xml`, `RSW_Porg.xml`, `RSW_Vulptex.xml`. Every diff is the same
shape — a `<Desert>`/`<AridShrubland>` commonality entry added to
`<wildBiomes>` (a biome-wiring pass, 1-2 lines each). Verified programmatically
for all 13: no duplicate `wildBiomes` keys introduced, and every file still
parses as valid XML (`xml.etree.ElementTree.parse`). `RSW_Nuna.xml` also
carries a docstring rewrite recording the owner's 2026-09-23
`DUPLICATE_CANON_DEFNAME_PAIRS_1` ruling (the vanilla-Core-Nuna assumption
behind the original "keep both" call was wrong — MEASURED on the Desktop,
no Core/DLC Nuna exists, the bare `"Nuna"` is Mlie's own def — so the pair
now collapses onto `RSW_Nuna`); the new docstring text is internally
consistent and correctly dated/attributed, not re-verified independently
(engine dump is UNMEASURABLE from this laptop per CLAUDE.md). Noted but NOT
acted on, out of this review's scope: `AnimalBiomeDuplicates_Generated.xml`,
`AnimalTolerances_Ashkarr.xml` and `BiomeCastEvictions_WildBiomes.xml`
still target the bare `defName="Nuna"` in several `PatchOperation`s — these
are generated/curated patch artifacts (not hand-edited per
`patch-a-curated-artifact-never-reallocate`), and whether they're owed a
regen onto `RSW_Nuna` is `DUPLICATE_CANON_DEFNAME_PAIRS_1`'s call, not a
code-review bug in `RSW_Nuna.xml` itself.

No bugs found in any of the 13. All had zero uncommitted changes before
marking (`git status --porcelain` empty). All 13 marked CLEAN, commit
`52bc5448d`, pushed.

**This closes the whole `SWBestiary/Defs/ThingDefs_Races/` `RSW_*` cluster.**
Next wave: 86 non-PNG DIRTY files remain (99 minus this wave's 13) —
re-derive with `code_review_status.py list | grep '^DIRTY'` filtered for
non-`.png` rather than trusting this arithmetic. The other named cluster
from wave 28, the 25-file `RUT_*` BiomeDef cluster under
`UtinniPatches/Defs/BiomeDefs/`, is still untouched and is a natural next
pick (all 25 confirmed still present in the DIRTY list this wave). The PNG
binary-art-tracking scope question (wave 15) is still open and still not
this loop's to decide.

## Wave 32 — 2026-09-24: `RUT_*` BiomeDef cluster, 8 of 26 cleared

Re-derived the cluster fresh rather than trusting wave 31's "25": a real
`find` under `UtinniPatches/Defs/BiomeDefs/` gave **26** `RUT_*` files, of
which `code_review_status.py check` showed **25 DIRTY** and **1 already
CLEAN** (`RUT_Sump.xml`, clean since 2026-09-13) — so 25 was correct as a
DIRTY count, not a file count; wave 31's phrasing conflated the two. One
file, `RUT_FuelSnows.xml`, has never been marked clean and needs a full-file
review rather than diff-scoped, so it was left for a future wave per this
item's own protocol (diff-scoped review is only valid once a file has been
CLEAN once).

Reviewed 8 of the 24 diff-eligible DIRTY files, diff-scoped against each
file's own clean-mark sha, prioritizing roster/commonality correctness over
XML validity per this wave's brief: `RUT_Contagion.xml` (+7/-1),
`RUT_Slime.xml` (+6/-1), `RUT_FeverWood.xml` (+2/-2), `RUT_Miasma.xml`
(+7/-5), `RUT_CrackedLands.xml` (+8/-3), `RUT_WeepingStones.xml` (+9/-2),
`RUT_Webwork.xml` (+8/-1), `RUT_Scarlands.xml` (+5/-2) — the 8 smallest
diffs in the cluster.

Every diff traced to a real, well-documented ruling, cross-checked against
its cited commit/item rather than taken on the comment's word alone:

- **RUT_Contagion / RUT_Miasma / RUT_Slime**: `SHEET_ORPHAN_CONSUMPTION_1`
  (owner review 2026-09-20) plant moves/cuts, transplanted from the retired
  `BiomeFlora_Ashkarr.xml` replace-patch onto the base defs directly by
  `BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1` (`921c04e1c`). Read the full commit
  chain on `RUT_Miasma.xml` (`8725fb338` → `921c04e1c` → `429446d0d`) since
  its diff removed 4 plant rows and added only 1, which looked at first
  glance like a bulk-drop: confirmed via commit message that the 4 removed
  rows (`BMT_Plant_TreeTanglerootMangrove`/`SewerReed`/`RainbowTongue`/
  `Snaketails`) were a deliberate 2026-09-18 cut (mangal family already
  carried 92% of that roster's weight), unrelated to the 1 added row
  (`RUT_Nogtyl`, a separate 2026-09-20 move-in) — two different rulings
  landing in the same diff, not one bug.
- **RUT_FeverWood / RUT_Miasma / RUT_Webwork**: `DUPLICATE_CANON_DEFNAME_PAIRS_1`
  (owner-ruled merge 2026-09-23) repointing bare donor defNames (`Nuna`,
  `Kreetle`) onto their `RSW_` ports.
  `RUT_Webwork`'s `Kreetle`→`RSW_Kreetle` also carries an independent
  commonality boost (0.2→0.8) under `ECOSYSTEM_PYRAMID_LAW_1` — verified
  the file's own comment against its cited frozen roster
  (`the_webwork.json`) rather than trusting the math: the roster's two
  unwired candidates (`AA_Feralisk`/`GR_Chickenspider`) are genuinely
  bodySize 1.0/1.1 (LARGE), so raising an already-wired small species was
  correctly the only pyramid-safe move.
- **RUT_CrackedLands**: two independent changes in one diff — a `BMT_`→`RUT_`
  defName sync (`RUT_TwistingThorngrass`/`Thornweed`/`Thornwood`,
  `8725fb338`/`61c6a9233`) and a `FloodedCanyon` freeze-header comment
  (`962ee9a80`, closed item `FLOODEDCANYON_RM_MOD_BUILD_1`) declaring this
  `RUT_` def frozen — content now lives in `mandrake.rm.floodedcanyon`,
  this def only "carries the world until the terminal paint." Checked commit
  order to confirm the freeze comment landed AFTER the plant-name sync, not
  a content edit smuggled in after the freeze.
- **RUT_WeepingStones / RUT_Webwork / RUT_Scarlands**: `ECOSYSTEM_PYRAMID_LAW_1`
  commonality raises on already-wired small fauna (no megafauna cuts, no new
  wiring beyond what each biome's own frozen roster already names) plus,
  on Scarlands, a label change (`"the Scarlands"` → `"Warscar"`) and three
  newly-wired `RSW_` species from the round2 move mapping — each carries an
  inline bodySize-grounded commonality rationale (`RSW_CrystalFairyMole`
  0.86, `RSW_MegaphoridLarva` 0.32 both small so wired high;
  `RSW_Korrum` 4.00 large so deliberately wired at 0.05, not the roster's
  placeholder 0.5).

Verified independently for all 8: every added/renamed defName
(`RUT_RustPuff`, `RUT_Nogtyl`, `RSW_Nuna`, `RUT_GiantLeaf`, `RSW_Kreetle`,
`RSW_PodWorm`, `RUT_TwistingThorngrass`/`Thornweed`/`Thornwood`,
`RUT_Dewshrooms`, `RUT_ScorchedStars`, `RSW_CrystalFairyMole`,
`RSW_MegaphoridLarva`, `RSW_Korrum`) resolves to a real `defName` element on
disk, and every `MayRequire` packageId resolves to a real `About.xml`. All 8
files parse as valid XML with no duplicate `wildAnimals`/`wildPlants` keys
introduced (checked programmatically, not by eye). No bugs found; no fixes
needed this wave. All 8 had zero uncommitted changes before marking
(`git status --porcelain` empty). All 8 marked CLEAN, commit pending below,
pushed.

Next wave: 16 `RUT_*` BiomeDef files remain in the cluster (24 diff-eligible
minus this wave's 8), plus `RUT_FuelSnows.xml` still needs its first
full-file review (never marked clean) — re-derive both counts fresh with
`code_review_status.py check` rather than trusting this arithmetic. The
`~15`-file `RSW_*ThingDefs_Races` cluster is already closed (wave 31); the
bridgetools `.cs` files and `rimflow`/`Utils` Python tooling named in wave
28's note are still untouched; the PNG binary-art-tracking scope question
(wave 15) is still open and still not this loop's to decide.

## Wave 33 — 2026-09-24: `RUT_*` BiomeDef cluster, `RUT_FuelSnows` first review + 7 more diff-scoped

Re-derived the cluster fresh rather than trusting wave 32's arithmetic: a
real `find` under `UtinniPatches/Defs/BiomeDefs/` now gives **27** `RUT_*`
files (one more than wave 32's 26 — `RUT_Umbra.xml` was restored as a
live-continuity duplicate by `UMBRA_IS_A_REGION_NOT_A_BIOME_1`'s addendum,
2026-09-21, unrelated to this loop). `code_review_status.py check` showed
**19 DIRTY**: 18 diff-eligible (already CLEAN once) plus `RUT_FuelSnows.xml`,
still never marked clean.

`RUT_FuelSnows.xml` full-file review (first ever): the successor to the
retired `RUT_Umbra` defName (`UMBRA_IS_A_REGION_NOT_A_BIOME_1`), its whole
mechanics body carried forward verbatim per its own header. Verified
independently rather than trusting the header's word: all four
`wildAnimals` rows (`AA_Frostmite`/`AA_FrostboundBehemoth`/`AA_Terramorph`/
`AA_Slurrypede`) and all four `wildPlants` rows (`AB_CrystalHorn`/
`AB_FrostLeaf`/`AB_RimeNodules`/`PoisonShrub`) match their commonalities
exactly against `design/Jawa/worldbuilding/biomes/rosters/
the_propane_lakes.json`'s `fauna`/`flora` arrays; `workerClass`
(`AlphaBiomes.BiomeWorker_PropaneLakes`) and both `terrainsByFertility`
defNames (`AB_PackedSnow`/`AB_PackedIce`) confirmed against the vendored
`vendor/mod_sources/AlphaBiomes_src`; `sarg.alphaanimals` packageId confirmed
referenced as a real dependency elsewhere (no vendored source for Alpha
Animals itself, consistent with every other AA_-prefixed reference in this
cluster). No duplicate `wildAnimals`/`wildPlants` keys; XML parses. No bugs.

Diff-scoped the 7 smallest remaining diffs by `git diff --shortstat`:
`RUT_TwilightSea.xml` (+10), `RUT_RustCathedral.xml` (+12),
`RUT_PoisonForest.xml` (+13/-4), `RUT_NightsideIce.xml` (+21),
`RUT_ForsakenCrags.xml` (+18/-2), `RUT_TheForge.xml` (+18/-6),
`RUT_Greentide.xml` (+31/-5). Every change traced to its cited item/ruling
and verified on disk, not taken on the comment's word:

- **RUT_TwilightSea**: `SEA_FLOOR_AND_CATCH_PASS_1`'s `RM_SeaShoreExtension`
  modExtension — class confirmed at
  `src/RimMandrake/SeaShores/Source/RM_SeaShoreExtension.cs` (namespace
  `RimMandrake.SeaShores` matches the XML `Class=`), `mandrake.rm.seashores`
  packageId confirmed at `src/RimMandrake/SeaShores/About/About.xml`, and
  UtinniPatches' own `About.xml` `loadAfter` carries a matching comment
  naming this exact file.
- **RUT_RustCathedral**: `ECOSYSTEM_PYRAMID_LAW_1` wiring in two
  never-before-wired roster rows (`RUT_CathedralRoach` 0.12,
  `GR_Mecharat` 0.5) — both defNames confirmed on disk (`RUT_CathedralRoach`
  in `RustCathedralRoaches/`, `GR_Mecharat` in the vendored
  `VanillaGeneticsExpanded_src`), both commonalities match
  `rosters/the_rust_cathedral.json` exactly, and the comment's claim that
  `GR_Mechachicken` stays cut is correct — it is NOT in the file, and the
  roster confirms `CUT` disposition.
- **RUT_PoisonForest**: `RSW_Screecher` multi-homing annotation under
  `BIOME_SPECIFIC_FAUNA_LAW_1` — confirmed the item exists and the
  screecher's own def (`RSW_BiomesTeamPort_Races.xml`) really carries
  `MaxFlightTime 35`, backing the "real flier that migrates" carve-out.
  Plus a `BMT_`→`RUT_` defName sync (`RUT_TwistingThornwood`/
  `RUT_TreeMartyr`, both confirmed at `RUT_PollutedFlora.xml`) and a
  `SHEET_ORPHAN_CONSUMPTION_1` plant swap (`AB_CrystalHorn` out,
  `AB_GiantToxicFlower` 0.08 in) matching `rosters/poison_forest.json`.
- **RUT_NightsideIce**: `ECOSYSTEM_PYRAMID_LAW_1` wiring of
  `AA_ShockGoat` (0.03) and `RSW_CaveLemming` (0.03) — both match
  `rosters/nightside_ice.json` exactly, including the roster's own note that
  the cave lemming deliberately WORSENS the small-fauna ratio on the
  owner's explicit ruling (not a defect to fix).
- **RUT_ForsakenCrags / RUT_TheForge**: a matched pair — `AG_Gamma` (0.5)
  and `AG_Septimum` (0.25) moved OUT of `RUT_TheForge` and INTO
  `RUT_ForsakenCrags` at the same commonalities under
  `SHEET_ORPHAN_CONSUMPTION_1` (checked both diffs against each other, not
  just each file's own comment) plus independent `ECOSYSTEM_PYRAMID_LAW_1`
  small-fauna boosts (`AA_DuskRat`/`AA_Murkling` raises on Crags,
  `AA_CrescendoAnole` 0.5 new-wire on the Forge) and a `BMT_`→`RUT_`
  defName sync on the Forge's plants (`RUT_FireLavender`/`RUT_Sagecrust`/
  `RUT_HeatsinkFungus`, all confirmed on disk). All commonalities match
  their respective roster JSONs.
- **RUT_Greentide**: the biggest diff, four independent changes verified
  separately. (1) A new `FROZEN` header under `GREENTIDE_RM_MOD_BUILD_1` —
  confirmed `RM_Greentide` exists (`RM_Greentide_Biome.xml`), confirmed
  `RM_BiomeWorker_Greentide.cs:44` really reads `RM_GreentideBiomeRanges`
  exactly as the header claims, confirmed `WildAnimals_Greentide.xml`
  exists. (2) Three `DUPLICATE_CANON_DEFNAME_PAIRS_1` repoints
  (`Gizka`→`RSW_Gizka`, `Worrt`→`RSW_Worrt`, `Nuna`→`RSW_Nuna`), all three
  defNames confirmed on disk, item confirmed closed/ruled. (3) The Dianoga
  row removed outright — cross-checked the removal comment's verbatim owner
  quote against `rosters/the_greentide.json`'s `evictions` array and it
  matches word-for-word, and confirmed no live `Dianoga`/`RSW_Dianoga` row
  survives in either this file or `WildAnimals_Greentide.xml` (only
  explanatory comments do). (4) A `BMT_GiantLeaf`→`RUT_GiantLeaf` defName
  sync, confirmed on disk.

No bugs found in any of the 8 files reviewed this wave (1 full-file + 7
diff-scoped). All had zero uncommitted changes before marking
(`git status --porcelain` empty). All 8 marked CLEAN, commit `8270c8245`,
pushed.

Next wave: **10** `RUT_*` BiomeDef files remain DIRTY, all diff-eligible
(already CLEAN once) — re-derive fresh with `code_review_status.py check`
rather than trusting this list: `RUT_AridShrubland.xml`, `RUT_BlueDesert.xml`,
`RUT_Desert.xml`, `RUT_ExtremeDesert.xml`, `RUT_GreySea.xml`,
`RUT_PropaneLake.xml`, `RUT_TheRot.xml`, `RUT_TheScald.xml`,
`RUT_Umbra.xml`, `RUT_Wasteland.xml`. This closes out the cluster in the
next wave or two. The `~15`-file `RSW_*ThingDefs_Races` cluster is already
closed (wave 31); the bridgetools `.cs` files and `rimflow`/`Utils` Python
tooling named in wave 28's note are still untouched; the PNG
binary-art-tracking scope question (wave 15) is still open and still not
this loop's to decide.

## Wave 34 — 2026-09-24: `RUT_*` BiomeDef cluster CLOSED

Diff-scoped all 10 remaining files, full rigor, same as waves 32-33:
`RUT_AridShrubland.xml`, `RUT_BlueDesert.xml`, `RUT_Desert.xml`,
`RUT_ExtremeDesert.xml`, `RUT_GreySea.xml`, `RUT_PropaneLake.xml`,
`RUT_TheRot.xml`, `RUT_TheScald.xml`, `RUT_Umbra.xml`,
`RUT_Wasteland.xml`. **This closes the whole `RUT_*` BiomeDef
never-clean/re-dirtied cluster that waves 32-34 worked through.**

Every added/renamed defName and every `MayRequire` packageId verified on
disk (RimSage's live def dump was available this session — used to confirm
`Plant_GrayGrass`/`Plant_Toxipotato`/`Plant_TreePolux` are real vanilla
Biotech pollution flora in `RUT_Wasteland.xml`'s newly-populated
`wildPlants`, after grep-only checks against `src/`/`vendor/` came back
empty for them — the standing "not vendored ≠ not real" caveat this cluster
has hit before, now cross-checked against the live game itself, not just
plausibility). Every commonality cross-checked against its cited roster
JSON (`the_scald`, `the_propane_lakes`, `wasteland`, `the_rot`, `desert`,
`dune_sea_deep_desert`, `the_grey_sea`, `the_blue_desert`) or
`cast_assignment.csv` row. `RUT_Desert.xml` (the largest diff, +179/-71) is
a full mass-rename of ~50 bare-canon fauna/flora rows to their `RSW_`/`RM_`/
`RUT_` ports plus several newly-wired round-2 import rows — every single
renamed/new defName resolves, confirmed by two batched greps (the first
timed out mid-run at 120s and was let finish in the background rather than
half-trusted). No duplicate `wildAnimals`/`wildPlants` keys anywhere
(checked programmatically via `xml.etree`, all 10 files, not by eye); all
10 parse as valid XML. All 10 had zero uncommitted changes before marking
(`git status --porcelain` empty).

Two apparent bugs chased down and both resolved as NOT bugs, worth
recording so a future wave doesn't re-chase them:

- **`RUT_TheRot.xml` wires `AA_AnimaColossus`, but
  `design/Jawa/worldbuilding/biomes/rosters/the_rot.json`'s own
  `evictions` array still carries a *different*, unretracted entry for the
  same defName** ("ban 2: anima (psychic-tree) creature, not fungal; the
  pale tree owns that register alone (§7)", `homeless-reserve`) —
  contradicting the `fauna` array's `import`/`commonality 0.5` row the XML
  actually implements. Traced this to the closed item
  `ROT_ROSTER_DEAD_DONOR_NAMES_1` (closed 2026-09-21), which explicitly
  ruled `AA_AnimaColossus | wire as-is` without addressing the older ban-2
  eviction on record. **The XML is correct — it implements the later,
  closed-item ruling** — but the roster JSON's `evictions` row is now
  stale/contradictory and nobody has reconciled it. This is a content
  question (does the later ruling knowingly override ban 2, or was the
  eviction simply missed?), not a code defect, so left unfixed and
  unfiled — flagging here for whoever next touches Rot roster hygiene.
- **`RUT_ExtremeDesert.xml` silently drops `AA_BoulderMit`, which
  `design/Jawa/worldbuilding/biomes/rosters/dune_sea_deep_desert.json`'s
  `fauna` array still lists as `"action": "keep"` at commonality 0.025, with
  no eviction record.** Initially read as an undocumented content-loss bug
  (every other removal in that same diff cites a reason). Resolved: the
  diff's own header comment already covers it under a different name —
  `AA_BoulderMit` is the donor def behind `RSW_Stoneback`/`RSW_Korrum` (the
  "korrum"/"bokka" `STONEBACK_DEFNAME_COLLISION_1` /
  `BIOME_SPECIFIC_FAUNA_LAW_1` "one arid home" ruling the diff cites by its
  ported name, not its donor name). The `dune_sea_deep_desert.json` `fauna`
  row is the stale artifact here (same class of staleness as the Rot
  finding above, in a different roster) — again a roster-hygiene question,
  not a code defect, left unfixed.

Both findings are roster-JSON staleness, not BiomeDef-XML defects, and both
are outside this loop's scope to resolve (content/provenance judgment calls
per this session's brief) — recorded here rather than silently dropped, per
`nothing-learned-is-dropped-for-space`.

All 10 marked CLEAN, commit `772109351`, pushed.

**Re-derived the full non-PNG re-dirtied list fresh** (`code_review_status.py
list`, TALLY line): **61 DIRTY** (well under the earlier "~78" figure — most
of the shrinkage is the just-closed `RUT_*` cluster). Grouped by directory,
the two largest surviving clusters are tied at 9 files each:

- `src/RimUtinni/UtinniPatches/Patches/` — `AnimalTolerances_Ashkarr.xml`,
  `AshStorms_Pyrelands.xml`, `BiomeDescriptions_Ashkarr.xml`,
  `BiomeFlora_Ashkarr.xml`, `FishTypesStrip_NoFishBiomes.xml`,
  `ManyWaters_RiverSteam_Ashkarr.xml`, `PlantTolerances_Ashkarr.xml`,
  `SandFishing_CrackedLands.xml`, `WildAnimals_Pyrelands.xml` — all
  diff-eligible (already CLEAN once per the list output).
- `src/RimMandrake/Utils/` (top-level scripts, not the `artpipe/` or
  `rimflow/` subdirectories, which are their own smaller clusters at 2 and
  6 files respectively) — `ashkarr_paint.py`, `ashkarr_settle.py`,
  `codebase_health.py`, `codebase_health_publish.py`, `handoff.py`,
  `modset_builder.py`, `project_maturity_dashboard.py`,
  `run_selftests.py`, `structure_roster_lint.py`.

`src/RimStarWars/Armoury/Source/` (5 `gen_*_absorption.py` files) and
`src/RimMandrake/rimflow/` (6 files) are the next-largest after those two.
Not started — left for whoever picks this up next, per this wave's brief.

## FOUNDRY, 2026-09-24 (orchestrating window): PNG scope question RESOLVED — binary art gets a deterministic bulk probe, not per-file LLM review

**Owner ruling, verbatim: "PNG's and other binary content for dirty clean health could just do a quick probe that they are a well formed image file (or whatever they are). This should be done in bulk and swiftly using deterministic tools."**

This closes the open scope question waves 15/28 flagged and declined to decide. Built
`src/RimMandrake/Utils/probe_png_wellformed.py` — pure-stdlib PNG structure validator
(signature bytes, chunk length/type/CRC32 for every chunk, IHDR first, IEND last,
non-zero width/height). It proves a file is not truncated, not corrupted, and not a
renamed non-PNG; it says nothing about whether the ART is right — that stays a human
call (or the artpipe validator's own job for a fresh generation), same division of
labour as everywhere else in this repo (CLAUDE.md's art review doctrine).

Self-tested against corrupt/truncated/non-PNG fixtures before trusting it on real
files (confidently-wrong-numbers discipline) — all three failure modes correctly
detected with the right diagnosis, exit code 1.

Ran `--dirty-from-status --mark-clean` for real: **161/161 DIRTY PNGs passed and are
now CLEAN.** Also found and pruned (via `code_review_status.py prune --apply`) 9
CODE_REVIEW_STATUS.json entries — 1 PNG (`RM_FE_Pyrelands.png`, an orphan of the
Pyrelands wrong-biome-def rename) and 8 non-PNG — pointing at files that no longer
exist on disk at all.

**Standing convention going forward**: any newly-DIRTY PNG (or other binary art) should
be cleared with `probe_png_wellformed.py --dirty-from-status --mark-clean`, in bulk,
not queued into a per-file review wave. The non-PNG backlog (waves 25-33's re-dirtied
sweep) is unaffected and continues under the normal diff-scoped review protocol.

Commit: `28df62974`.

## Wave 35 — 2026-09-24: `src/RimMandrake/rimflow/` cluster CLOSED, all 6 files reviewed clean

Re-derived the non-PNG DIRTY list fresh (`code_review_status.py list | grep '^DIRTY'`
filtered non-`.png`): exactly **61**, matching wave 34's count. Per the standing brief
to prioritize the ledger/queue engine itself as high-leverage (same reasoning as
prioritizing the bridge-tools files in waves 29-30), took the `src/RimMandrake/rimflow/`
cluster — all 6 files, all diff-eligible (already CLEAN once): `cli.py` (2418 lines,
+56/-5 since `9ff1457ee`), `model.py` (1664 lines, +159/-10 since `23513b419`),
`render.py` (756 lines, +28/-7 since `f203d6f3`), `selftest_cli.py` (1110 lines,
+116/-43 since `13b71380a`), `selftest_model.py` (1357 lines, +149/-6 since
`1a7a75d09`), `selftest_concurrency.py` (232 lines, +115/-1 since `43f96b1b`).

Every diff is one coherent piece of work: the `EVENTS_JSONL_SHARDING_1` retrofit
(2026-09-23, CLAUDE.md's own ledger section) landing across the whole module —
`model.py` gains `SHARD_DIR`/`shard_dir()`/`shard_path()`/`ledger_files()` and
`read()`/`append()` are rewritten so a bare call merges the frozen `events.jsonl`
with every `events/<SEAT>.jsonl` shard (read) or routes by `ev["seat"]` (append);
`cli.py` converts every `model.read(model.EVENTS)` call site to `model.read()` (the
"NO PATH" comments explain why — the old form now means "history only, blind to
everything since the cutover") and adds `_move_prose_to_closed()` (the
`LIVE_ITEM_GLOB_DRIFT_1` fix: `close`/`drop`/`supersede` now actually move an item's
prose to `items/closed/` instead of leaving it a manual `git mv` every closing seat
had to remember); `render.py` follows suit (`build(events_path=None)` no longer
resolves the constant, `_ledger_label()` names the ledger correctly in a truncation
refusal); the three selftest files gain the coverage for all of it.

Traced the load-bearing correctness properties by hand rather than trusting the
comments:
- **`append()`'s ordering** — `validate(ev)` (which calls `_check_seat`, refusing any
  seat not in `SEATS`) runs BEFORE `path = path or shard_path(ev["seat"])`, so
  `ev["seat"]` is guaranteed present and bounded before it is ever used to build a
  filename — confirmed by reading `validate()`'s call order and `_check_seat`
  directly, not just the inline comment claiming it.
- **`read()`'s merge tie-break** — `(ts, source rank, within-file order)` via
  `merged.sort(key=lambda t: (t[0], t[1]))`: the sort key deliberately excludes the
  event dict itself (avoids a TypeError from comparing two dicts on a tie) and Python's
  stable sort preserves `extend()`'s file-order for same-`(ts, rank)` entries — verified
  this is exactly what `t_read_merges_frozen_history_with_every_shard_in_ts_order`
  exercises and its expected tie order (`BUILD, FOUNDRY, FOUNDRY` for three same-second
  events across head + one shard) matches the sort's actual behavior.
- **`cli.py`'s `_move_prose_to_closed`** — confirmed `args.id` for `supersede` is the
  OLD/superseded item (not `--by`, the new one), so moving `args.id`'s prose to
  `items/closed/` on `drop`/`supersede`/`close` is correct: the terminal item's prose
  moves, matching CHARTER's "on close/drop/supersede the prose moves to
  items/closed/<ID>.md".
- **No stale `model.read(model.EVENTS)` / `.read(EVENTS)` call sites survived the
  conversion** anywhere in `src/` outside selftests and comments (grepped fresh) — wave
  26's `broadcast.py` fix was the only production caller elsewhere and it already
  converted correctly.

**Ran all three selftest suites for real rather than reading them and trusting they'd
pass** (this cluster earns it — it is the ledger/queue engine itself):
`selftest_model.py` **71/71 passed**, `selftest_cli.py` **43/43 passed**,
`selftest_concurrency.py --writers 4 --each 50` **both arms passed** (200/200 events,
zero torn, zero lost on the one-file arm; 200/200 across BENCH.jsonl/FOUNDRY.jsonl with
`events.jsonl` correctly left untouched on the sharded arm). No bugs found in any of
the 6 files.

All 6 had zero uncommitted changes before marking (`git status --porcelain` empty —
confirmed no collision with the concurrent BACTA_REVIVAL_MECHANIC_1 build agent, which
does not touch this cluster). All 6 marked CLEAN, commit pending below, pushed.
`infrastructure/state/queue/BENCH.md`/`FOUNDRY.md` also showed as modified after the
mark-clean pass (queue views re-render on every `rimflow`-adjacent write per CHARTER)
but that drift traces to the concurrent build agent's own ledger activity, not to this
wave's `mark-clean` calls — left uncommitted, not this wave's to claim.

**This closes the whole `src/RimMandrake/rimflow/` cluster.** Next wave: 55 non-PNG
DIRTY files remain (61 minus this wave's 6) — re-derive with `code_review_status.py
list | grep '^DIRTY'` filtered for non-`.png` rather than trusting this arithmetic. The
two other named clusters from wave 34's note are still untouched:
`src/RimUtinni/UtinniPatches/Patches/` (9 files: `AnimalTolerances_Ashkarr.xml`,
`AshStorms_Pyrelands.xml`, `BiomeDescriptions_Ashkarr.xml`, `BiomeFlora_Ashkarr.xml`,
`FishTypesStrip_NoFishBiomes.xml`, `ManyWaters_RiverSteam_Ashkarr.xml`,
`PlantTolerances_Ashkarr.xml`, `SandFishing_CrackedLands.xml`,
`WildAnimals_Pyrelands.xml`) and `src/RimMandrake/Utils/` top-level scripts (9 files:
`ashkarr_paint.py`, `ashkarr_settle.py`, `codebase_health.py`,
`codebase_health_publish.py`, `handoff.py`, `modset_builder.py`,
`project_maturity_dashboard.py`, `run_selftests.py`, `structure_roster_lint.py`), plus
`src/RimStarWars/Armoury/Source/` (5 `gen_*_absorption.py` files) and the rest of the
never-entered `.cs`/Python backlogs surveyed in wave 15. The PNG binary-art-tracking
scope question (wave 15) is still open, resolved separately (see the FOUNDRY note
above) and still not this loop's to decide.

## Wave 36 — 2026-09-24: `src/RimUtinni/UtinniPatches/Patches/` cluster CLOSED

Re-derived the non-PNG DIRTY list fresh (`code_review_status.py list | grep '^DIRTY'`
filtered non-`.png`): exactly **61**, matching wave 35's count. Took the named
`src/RimUtinni/UtinniPatches/Patches/` cluster — all 9 files, all diff-eligible
(already CLEAN once): `AnimalTolerances_Ashkarr.xml` (19,260 lines, generated,
+5944/-5584 since `14aaf1757`), `PlantTolerances_Ashkarr.xml` (6,770 lines, generated,
+1506/-2262 since `3ea1ca20`), `BiomeFlora_Ashkarr.xml` (99 lines, +51/-377 since
`5ab0e549a`), `ManyWaters_RiverSteam_Ashkarr.xml` (+32/-21 since `504ead829`),
`BiomeDescriptions_Ashkarr.xml` (+17/-7 since `7c80850cb`), `AshStorms_Pyrelands.xml`
(+17/-2 since `d92f5459`), `WildAnimals_Pyrelands.xml` (+7/-7 since `204a30ed7`),
`SandFishing_CrackedLands.xml` (+33/-0 since `48b321e95`), `FishTypesStrip_NoFishBiomes.xml`
(+4/-2 since `429d1760`).

Every diff traced to a named ruling/item already in the record: the `RM_FE_Pyrelands` →
`RM_Pyrelands` rename (owner ruling 2026-09-21, commit `84d42c63b`), `PYRELANDS_WRONG_BIOME_DEF_1`
(repoints content onto our own def rather than the donor, with an honest unreconciled
CSV-vs-live caveat left in `ManyWaters_RiverSteam_Ashkarr.xml`'s own comment — correctly
NOT resolved by this wave, since CLAUDE.md's own rule is never to settle a live-vs-CSV
disagreement from the CSV, and the file's dual-target patch already hedges by patching
both defNames rather than picking one), `UMBRA_IS_A_REGION_NOT_A_BIOME_1` (RUT_Umbra →
RUT_FuelSnows, with the live-continuity duplicate file explained), `BIOMEFLORA_PATCH_WIPES_WILDPLANTS_1`
(closed item — removed 19 `PatchOperationReplace` ops for BiomeDefs that now own their
`wildPlants` directly, verified RUT_Desert's def now carries its own list and only the
`ZBiome_Grasslands` op remains in the patch file), and `FLOODEDCANYON_RM_MOD_BUILD_1`
(new `RM_FloodedCanyon` fishTypes op, verified byte-for-byte copy of `RUT_CrackedLands.xml`'s
own inline block).

Verified every defName and packageId cited resolves on disk: `RM_Pyrelands`
(`src/RimMandrake/Pyrelands/Defs/BiomeDefs/Pyrelands.xml`), `RM_FloodedCanyon`
(`src/RimMandrake/FloodedCanyon/Defs/BiomeDefs/RM_FloodedCanyon_Biome.xml`, confirmed
no pre-existing `fishTypes`/`maxFishPopulation` so the `PatchOperationAdd` cannot
double up), `mandrake.rsw.swbestiary` (`src/RimStarWars/SWBestiary/About/About.xml`),
and the two generated tolerance files' referenced defNames spot-checked (125 unique in
`PlantTolerances_Ashkarr.xml`, 481 in `AnimalTolerances_Ashkarr.xml` — the latter count
matches its own regen commit message exactly, `683211335`, including the single
surviving `BMT_LandOctopus` donor-mod exception). Both generated files parse as
well-formed XML; both their generating commits (`46ef96ae9` for plants, `683211335`
for animals) already carry `validate_patch.py --live: 0 errors` / a live deploy
confirmation, so this wave did not re-run that check, only verified the checked-in
XML matches what those commits claim to have produced (spot-checked `RUT_FireLavender`'s
26.9°C re-affirmed band, the specific self-reference regression `46ef96ae9` fixed).

**Found and fixed one real defect, a stale comment (not a patch-behavior bug):**
`FishTypesStrip_NoFishBiomes.xml`'s own docstring claimed "the Scald ships 5
`fishTypes` on its def and the Twilight Sea 8 via patch" — recounting both files
directly gives 8 (Scald) and 10 (Twilight Sea). Corrected in place; the patch's actual
XML operations don't touch either biome so nothing else was affected. Commit `17c7dab1a`,
pushed.

No xpath-matches-nothing risk found in any of the 9 — every xpath's target defName was
independently confirmed present on disk this wave (not inferred from `validate_patch.py`'s
static syntax check alone, which cannot see match/no-match at all).

All 9 marked CLEAN, commit `17c7dab1a`, pushed. Confirmed no collision with the
concurrent `BACTA_REVIVAL_MECHANIC_1` build agent (that work doesn't touch this
cluster; no bridge access was used or needed — pure offline review).

**This closes the whole `src/RimUtinni/UtinniPatches/Patches/` cluster.** Next wave:
52 non-PNG DIRTY files remain (61 minus this wave's 9) — re-derive with
`code_review_status.py list | grep '^DIRTY'` filtered non-`.png` rather than trusting
this arithmetic. The two other named clusters from wave 34/35's notes are still
untouched: `src/RimMandrake/Utils/` top-level scripts (9 files: `ashkarr_paint.py`,
`ashkarr_settle.py`, `codebase_health.py`, `codebase_health_publish.py`, `handoff.py`,
`modset_builder.py`, `project_maturity_dashboard.py`, `run_selftests.py`,
`structure_roster_lint.py`) and `src/RimStarWars/Armoury/Source/` (5
`gen_*_absorption.py` files), plus the rest of the never-entered `.cs`/Python backlogs
surveyed in wave 15. The PNG binary-art-tracking scope question (wave 15) is still
open and still not this loop's to decide.

## Wave 37 — 2026-09-24: `src/RimMandrake/Utils/` top-level scripts cluster CLOSED (8 of 9)

Re-derived the non-PNG DIRTY list fresh (`code_review_status.py list | grep '^DIRTY'`
filtered non-`.png`): exactly **52**, matching wave 36's count. Took the named
`src/RimMandrake/Utils/` top-level scripts cluster — all 9 files, all diff-eligible
(already CLEAN once): `ashkarr_paint.py` (1219 lines, +21/-21 since `3ea1ca20`),
`ashkarr_settle.py` (556 lines, +96/-9 since `e82a4ea05`), `codebase_health.py` (1188
lines, +14/-2 since `7d1a18fc1`), `codebase_health_publish.py` (333 lines, +27 since
`9e5089f22`), `handoff.py` (768 lines, +30/-11 since `6ecce8a3d`), `modset_builder.py`
(586 lines, +146 since `23513b419`), `project_maturity_dashboard.py` (1174 lines, +1/-1
since `5e99ea13e`), `run_selftests.py` (192 lines, +17/-2 since `d946c8522`),
`structure_roster_lint.py` (287 lines, +1/-1 since `cd7a57e06`). Reachability confirmed
for all 9 by grep — every one is cited live in CLAUDE.md, another script, a handoff, or
an item doc; none is a dead-file candidate. This is hand-run/safety-critical tooling
(deploy/bridge/game-state adjacent) so full context was read around every diff hunk, not
just the patch text.

Traced the load-bearing pieces by hand rather than trusting comments:
- **`ashkarr_settle.py`'s new `validate_barren_regions()`/`live_feature_names()`**
  (BARREN_REGIONS_NAME_NOTHING_1's fix: region-name literals used to silently
  un-protect ground when a rename drifted): live-ran it against the real canonical
  save (`CANONICAL_ASHKARR_START_2026-09-12.rws`, reachable at
  `/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon
  Studios/Saves/`) rather than reading the nested `<world><features><features><li>`
  parse and trusting it — all 22 `BARREN_REGIONS` + 7 `HELIX_BARREN_OK` literals
  resolve against the live 71-name feature set, zero missing. `ashkarr_paint.py`'s
  sibling diff (dropping "The " prefixes from ridge/basin/region names) does not
  itself define every name the settle guard checks (e.g. `Fuelmere` doesn't appear
  in paint.py at all) — not a bug, since paint.py isn't the sole source of feature
  names and the settle-time live guard is the actual safety net either way.
- **`codebase_health.py` and `handoff.py`'s matching ledger-sharding fixes**
  (`EVENTS_JSONL_SHARDING_1` retrofit, same shape as wave 35's `rimflow/` cluster):
  both now read `events.jsonl` plus every `ledger/events/<SEAT>.jsonl` shard instead
  of the frozen head alone; `handoff.py`'s added `out.sort(key=lambda e: str(e.get("ts")
  or ""))` is a correct stable string-sort on an ISO8601 `ts` field, same tie-break
  shape `rimflow/model.py`'s own merge uses.
- **`codebase_health_publish.py`'s new `rebase_or_merge_in_progress()` guard** matches
  CLAUDE.md's own "stuck rebase" section exactly (checks `rebase-merge`/`rebase-apply`/
  `MERGE_HEAD` in the real git-dir, resolved via `git rev-parse --git-dir` rather than
  assuming `.git/` — correct for a worktree too) — refuses even with `--force`, which is
  the documented intent, not an oversight.
- **`modset_builder.py`'s new stdout/stderr `reconfigure(encoding="utf-8")`** fixes a
  real prior incident (FOUNDRY, 2026-09-21: emoji in a tier's `why` string raised
  `UnicodeEncodeError` on Windows cp1252 stdout, aborting `--apply` before
  `ModsConfig.xml` was written, so a swap silently didn't happen) — correctly wrapped in
  try/except so it no-ops if `.reconfigure` is unavailable; all-new tier dicts are data,
  all carry `"dlc": True` per the standing "all test lists include all 5 expansions"
  ruling.
- **`run_selftests.py`'s new per-file `# selftest-timeout: N` tag** — regex
  `^#\s*selftest-timeout:\s*(\d+)` with `re.M` correctly anchors per-line across the
  joined first-40-lines string; both the actual `subprocess.run(timeout=...)` call and
  the `TIMEOUT` message's reported duration were updated together, no stale
  `PER_TEST_TIMEOUT_S` reference left in either path.
- **`structure_roster_lint.py`'s one-line diff** is a legitimate data-status update (The
  Sarlacc: `gap-design` → `done`, citing the `GenStep_RimplacePlan` `anchorThingDef`
  fix) inside a Python list literal, not a code change to review as logic.

No bugs found in any of the 9. **8 of 9 marked CLEAN**, commit `e55a9b3fd`, pushed.
`modset_builder.py` left DIRTY: `git status --porcelain` showed it with uncommitted
changes (a new `"bacta"` tier, `BACTA_REVIVAL_MECHANIC_1`) from the concurrent build
agent working `BACTA_SIDE_ITEMS_1` — not this review's file to commit or mark clean;
`code_review_status.py mark-clean` correctly refused with "has uncommitted changes."

**This closes 8/9 of the `src/RimMandrake/Utils/` top-level scripts cluster** —
`modset_builder.py` remains, pending the build agent's own commit. Next wave: 44
non-PNG DIRTY files remain (52 minus this wave's 8) — re-derive with
`code_review_status.py list | grep '^DIRTY'` filtered non-`.png` rather than trusting
this arithmetic. The one other named cluster from wave 34/35/36's notes is still
untouched: `src/RimStarWars/Armoury/Source/` (5 `gen_*_absorption.py` files), plus the
rest of the never-entered `.cs`/Python backlogs surveyed in wave 15 (95 never-entered
`.cs` files, 13 never-entered Utils Python tools whose reachability still needs
confirming per-file). The PNG binary-art-tracking scope question (wave 15) is resolved
separately (see the FOUNDRY note above) and still not this loop's to decide.

## Wave 38 — 2026-09-24: `modset_builder.py` closes the Utils cluster; `Armoury/Source` gen_*_absorption.py cluster CLOSED

Picked up `modset_builder.py` first: the concurrent build agent's uncommitted
`"bacta"` tier (wave 37's blocker) landed committed at `7f5f81262`
("Add a minimal 'bacta' tier for live-testing BACTA_TANK_CORE_1"), so
`git status --porcelain` on the file was clean and it was reviewable.
Diffed since its last clean mark (`23513b419`); wave 37 had already traced
everything in that range except the new 10-line `"bacta"` tier itself
(utf-8 stdout/stderr reconfigure, slime/xenotypes/beastmechanics/warlab
tiers were wave 37's job and are not re-litigated here). Verified the
`"bacta"` tier's claim ("No hard `<modDependencies>` beyond Core") directly
against `src/RimStarWars/Bacta/About/About.xml`: `<modDependencies>` lists
only `Ludeon.RimWorld`, `mandrake.rm.flowworks` is `<loadAfter>`-only —
matches exactly. No bugs found. Marked CLEAN, commit `8c754d292`, pushed.
**This closes the `src/RimMandrake/Utils/` top-level scripts cluster in
full (9/9).**

Then took the named `src/RimStarWars/Armoury/Source/` `gen_*_absorption.py`
cluster (5 files, all diff-eligible): `gen_additionalmods_absorption.py`,
`gen_jds_armory_absorption.py`, `gen_kotorcore_absorption.py`,
`gen_kotorweapons_absorption.py`, `gen_theforcelightsaber_kyber_absorption.py`.
Confirmed reachability first per this item's own rule — these are one-shot,
hand-run donor-absorption generators (no importer expected), and all 5 are
named in closed items (`WEAPONS_DONOR_RETIREMENT_1`, `WEAPONS_ABSORPTION_WAVE_1`,
`DROIDWORKS_MODULE_ABSORB_1`, etc.) as having actually been run — including
`gen_theforcelightsaber_kyber_absorption.py`, whose only in-repo citation is
its own docstring (`CRYSTAL_INGEST_EXECUTION_1` item 2) plus one closed item
listing it alongside the others; not a dead-file candidate.

Diffed each since its own last clean mark (25-44 lines each). **All 5 diffs
are the same deliberate fix, applied consistently across the whole
cluster**: `collect_texpaths`/`collect_paths` now also collects
`wornGraphicPath` (a third texture-root tag, alongside `texPath`/`iconPath`/
`uiIconPath`), and `find_and_copy_texture` in all 5 now additionally tries
`<path>_<BodyType>_<rotation>.<ext>` for BodyType in
Male/Female/Thin/Fat/Hulk and rotation in south/north/east/west — matching
`ApparelGraphicRecordGetter`'s real naming convention for worn-apparel
graphics, which the old rotation-only ladder missed entirely (copying only
the inventory icon, marking the texture "found", and silently leaving every
worn-graphic frame behind — a magenta-render defect on 123 absorbed apparel
defs per `gen_kotorcore_absorption.py`'s own comment). Traced the new nested
loop's scope/indentation in each file (all correctly nested inside the
existing per-`ext` loop, none accidentally unconditional or mis-scoped) and
confirmed `gen_kotorweapons_absorption.py`'s one-line comment typo fix
(`ARMOUR_MW2_CUT_1` -> `ARMOURY_MW2_CUT_1`) matches the real item ID at
`infrastructure/state/items/closed/ARMOURY_MW2_CUT_1.md` (already reviewed
correct back in wave 26 per this item's own line 1554 — re-confirmed, not
re-fixed). No bugs found in any of the 5. All 5 marked CLEAN, commit
`8c754d292`, pushed. **This closes the `src/RimStarWars/Armoury/Source/`
`gen_*_absorption.py` cluster in full.**

Next wave: re-derive the non-PNG DIRTY list fresh
(`code_review_status.py list | grep '^DIRTY'` filtered non-`.png`) rather
than trusting any count carried forward — both named clusters from waves
34-37 are now closed, so the next wave has no standing cluster pointer and
should re-survey. The never-entered `.cs` backlog is NOT a candidate here —
wave 24 closed it in full (see that wave's heading), so do not re-open it as
untouched. The one candidate class never actually verified either way is the
13 never-entered Utils Python tools flagged in wave 15 — check reachability
per-file before reviewing any of them. The PNG binary-art-tracking scope
question is RESOLVED, not open — see the FOUNDRY 2026-09-24 (orchestrating
window) note above: owner ruled binary art gets a deterministic bulk probe
(`src/RimMandrake/Utils/probe_png_wellformed.py`), 161/161 PNGs already
passed and are CLEAN, and PNGs are permanently out of this loop's per-file
scope.

## Wave 40 — 2026-09-24: last 8 never-entered Utils Python tools CLOSED; 3 re-dirtied files marked CLEAN

Note on file structure: wave 39's heading sits mid-file (line 1428, before wave
25 at line 1482) rather than at the true tail — an artifact of some earlier
merge, not a defect introduced this wave. Flagging it, not fixing it: an
append-only rule and a 2500+-line file are a bad combination for reordering by
hand, and wave 39's own "flagging for a future archiving/summarizing pass" note
already covers this.

Re-derived the DIRTY list fresh (`code_review_status.py list | grep '^DIRTY'`
from repo root): **41 non-PNG DIRTY rows**, matching wave 39's count exactly —
no drift in this window.

Took the 8 never-entered Utils Python tools wave 39 left standing. Reachability
re-confirmed for all 8 (grep hits in a live item doc, a handoff, or a skill's
usage doc; `canon_census.py` and `modcheck/readline_registry.py` also carry
live sibling selftests — ran both, all green including the live-repo checks).
Full-file reviewed each:

- **`artpipe/build_flora_legibility_sheet.py`** (335) — FLORA_LEGIBILITY_BAR_1
  sheet builder. Traced `job_art_info`/`resolve_stem`'s suffix-stripping loop,
  `find_flora_jobs`'s transparent+flora filter, and the weakest-first sort
  feeding `contested` on the bottom 15. No bugs.
- **`artpipe/facing_set_audit.py`** (248) — cross-facing sprite metric audit.
  Verified the canvas-transposition gate (`{(w,h) sorted}` set, not raw
  equality — correctly permits vanilla's own north/south vs east/west
  transposition) and that `viewpoint_south()`'s LLM judge is wired as
  ADVISORY-only, never returned as a FLAG except on UNMEASURED. No bugs.
- **`build_landmark_density_sheet.py`** (315) — BIOME_LANDMARK_REFINEMENT_1
  sheet builder. Checked `landmark_effects()` reads mutatorChances from the
  live def dump (not donor XML) and raises on any missing LandmarkDef rather
  than silently zeroing it; `measured_rows()`'s water/drift classification
  against the frozen tiles CSV. No bugs.
- **`canon_census.py`** (230) — the C8 ruled/unruled/non-conforming classifier.
  Traced `_BOILERPLATE_RE`'s bounded-gap shape match and the deliberate gizka
  non-conforming classification (documented, reasoned, not a bug). Ran
  `selftest_canon_census.py`: **ok** (all 7 boilerplate wordings + gizka/zeer
  shapes). No bugs.
- **`ecosystem_pyramid_check.py`** (339) — ECOSYSTEM_PYRAMID_LAW_1 checker.
  Verified the shortfall-commonality algebra (`t/(1-t) * large_c`, reduces to
  `large_c - small_c` at t=0.5 exactly as the comment claims) and that EMPTY
  rosters fail rather than silently pass/skip, per the owner's no-exemption
  ruling. No bugs.
- **`modcheck/readline_registry.py`** (215) — shared read-line registry lint.
  Ran `modcheck/selftest_readline_registry.py`: **ok**, including the live-repo
  check (78 walks, 0 dangling citations). One unused private helper noted,
  not fixed: `_read_sections()` is defined but never called anywhere in the
  file (grepped the whole repo) — dead code, not a behavioural bug, since
  nothing invokes it.
- **`stage_review.py`** (409) — live bridge staging tool for review
  screenshots. **Found and fixed one real bug**: `cell_open()`'s terrain check
  computed `"Water" in terr or "Rock" in terr or (not terr.endswith("_Rough")
  and "Marble" in terr)` inside an `if ...: pass` that discarded the result —
  only `water = "Water" in terr` actually gated the return, so any non-water
  Rock terrain silently read as open. That is exactly "the #1 review-shot
  defect" the function's own docstring says it exists to catch (a subject
  spawned inside rock). Fixed to actually gate on the computed condition.
  Commit `f2ffed68d`, pushed, verified with `py_compile` before marking clean.
- **`stage_xenotype_grid.py`** (310) — the companion xenotype-grid staging
  tool. Compared its `open_cells()`/`grid_cells()` against `stage_review.py`'s
  broken version above: this one uses the engine's own `walkable` flag from
  `rimworld/get_cells_info` directly, plus an explicit things-based block list
  including `"Rock"`/`"Mineable"` — no equivalent dead-code gap. No bugs.

All 8 had zero uncommitted changes except `stage_review.py` (the fix above,
committed separately from the mark-clean commit). **All 8 marked CLEAN**,
commit `8b65a2173`, pushed. **This closes the wave-15 never-entered Utils
Python tools backlog in full (13/13 across waves 39-40).**

With time remaining, picked 3 of the re-dirtied backlog, diff-scoped against
each file's own clean-mark sha (all confirmed zero uncommitted changes first):
`artpipe/artpiped.py` (+6/-2 since `74e9d4953` — owner ruling 2026-09-23
raising the weekly/5h Claude-budget thresholds toward the account ceiling,
hard_stop unchanged), `bridgetools/build.py` (+9 since `3ea1ca20` — new
`INHABITED_MOD_DIR` env override, same pattern as the existing
`ORACLE_MOD_DIR` one), `FlowWorks/Tools/generate_liquid_suite.py` (+1/-1 since
`51867f432` — Propane Lake's `waterBodyType` `None` -> `Saltwater` per owner
card `SEA_FLOOR_AND_CATCH_PASS_1`, matches the enum value every other
Saltwater row in the file already uses). All three are data/config changes
with clear provenance; no bugs found. All 3 marked CLEAN, commit `b5e8a9245`,
pushed. Deliberately left the `RimStarWars/Bacta/*` cluster (8 files, all
sharing clean-mark `d79860270`) and `EnvironmentalHazards`/`Inhabited`-adjacent
files untouched this wave — they sit close to the concurrent
`BACTA_SIDE_ITEMS_1` build agent's live work and a stale index.lock was hit
once mid-wave (transient, cleared on retry, not this agent's own process).

Re-derived the final count: **38 non-PNG DIRTY files remain** (41 minus this
wave's 3) — re-derive fresh next wave rather than trusting this arithmetic.
Next wave: no standing named cluster — the two remaining backlogs from wave
38/39's notes (the 13 never-entered tools, and the PNG scope question) are
both now closed/resolved. Resume the re-dirtied backlog fresh:
`code_review_status.py list | grep '^DIRTY'` filtered non-`.png`. The
`RimStarWars/Bacta/*` 8-file cluster is a reasonable next target once
`BACTA_SIDE_ITEMS_1` looks settled (check `git status --porcelain` on it
first — wave 37 hit exactly this collision with `modset_builder.py` and had
to skip it for a wave).

## Wave 41 — 2026-09-24: `RimStarWars/Bacta/*` cluster CLOSED (18 files, this wave's priority)

`BACTA_SIDE_ITEMS_1` (the concurrent build agent wave 40 stood clear of) finished
and pushed at `93f810a38` before this wave started — confirmed
`git status --porcelain -- src/RimStarWars/Bacta/` clean, nothing in flight.
Full-file reviewed (multiple same-day pieces — BACTA_TANK_CORE_1,
BACTA_REVIVAL_MECHANIC_1, BACTA_SIDE_ITEMS_1 — never cross-checked against
each other before now), reading all three items' prose first for the ruled
mechanics before judging the code.

Re-derived the cluster fresh via `code_review_status.py check` on every file
under `src/RimStarWars/Bacta/`, not just the 9-row DIRTY count carried
forward from wave 39/40: the cluster had grown to **22 reviewable files**
since its last clean mark (`d79860270`, 2026-09-17) — 18 DIRTY (About.xml,
`RSW_BactaJobDefs.xml`, `RSW_BactaTank.xml`, `RSW_MedicalDroid.xml`,
`RSW_BactaFieldItems.xml`, `RSW_BactaWorkGivers.xml`, `RSW_Bacta.xml`
(Languages), `RSW_Bacta_RecipeWiring.xml`, `RSW_Bacta_TraderStock.xml`,
`BactaDefOf.cs`, `BactaHealingUtility.cs`, `BactaMod.cs`, `BactaTuning.cs`,
`Building_BactaTank.cs`, `CompBactaImmersion.cs`, `CompUseEffect_BactaHeal.cs`,
`JobDriver_CarryCorpseToBactaTank.cs`, the `.csproj`,
`WorkGiver_CarryCorpseToBactaTank.cs`) and 4 already CLEAN from an earlier
pass (`RSW_BactaResearch.xml`, the item `RSW_Bacta.xml` fluid/container def,
`CompBactaShell.cs`, `WorkGiver_CarryToBactaTank.cs`), left untouched.

**Specifically checked, per this wave's brief:**
- **Corpse-vs-living-pawn admission race** (`Building_BactaTank.cs`,
  `CanAcceptPawn`/`TryAcceptPawn` vs `CanAcceptCorpse`/`TryAcceptCorpse`,
  `JobDriver_CarryCorpseToBactaTank.cs`): the corpse job's
  `TryMakePreToilReservations` reserves only the Corpse, never the tank —
  looked like a missing reservation at first read. Compared directly against
  the decompiled vanilla `RimWorld/JobDriver_CarryToBuilding.cs` (the base
  the living-pawn path's `WorkGiver_CarryToBactaTank` extends): vanilla does
  the **identical** thing — reserves only the Takee, never the Building. Both
  admission paths gate re-entry via a cheap `selectedPawn`/
  `innerContainer.Count` check re-evaluated every tick (`FailOn`), the same
  self-correcting shape vanilla ships for Growth Vats/Gene Extractors. Not a
  bug — a faithfully copied vanilla pattern, not a new race this mod
  introduced.
- **`CompUseEffect_BactaHeal` reusing `BactaHealingUtility.ApplyHealingDose`**:
  confirmed zero duplicated healing logic — `DoEffect` calls the shared
  static method with item-scaled amounts (`FieldProps.* *
  BactaSettings.fieldItemPotency`), same guarded law (skip
  `Hediff_MissingPart`, skip anything on `ConsciousnessSource`) as the tank's
  own call site in `CompBactaImmersion.TryHealPawn`. The static `tmpHediffs`
  scratch list is shared between both call sites but not reentrant (RimWorld
  is single-threaded, no nested calls), so no aliasing risk.
- **Medical droid multiplier consistency across all three healing paths**:
  `CompBactaImmersion.DroidAssisting` reads the facility link and multiplies
  the TANK's own wound/scar/immunity rates only — by design, not oversight:
  the droid is a `CompFacility` linked to the tank specifically
  (`RSW_BactaTank.xml`'s `CompProperties_AffectedByFacilities`), field items
  have no facility link to read and are a self-contained burst dose, and
  revival goes through the same tank/`CompBactaImmersion` loop once the pawn
  is alive, so it inherits the droid bonus automatically post-revival with no
  separate wiring needed. All three paths correctly obey the same two laws
  (never regrow, never touch the brain) via the one shared
  `ApplyHealingDose`; only the *rate* differs by path, which is the intended
  shape, not an inconsistency.
- Cross-checked `RSW_Bacta_RecipeWiring.xml`'s `[@Name="AnimalThingBase"]`
  xpath fix (BACTA_SIDE_ITEMS_1's own noted catch) against the decompiled
  `Races_Animal_Base.xml` — confirmed correct, not re-broken.
- XML well-formedness: all 9 touched/new XML files parse clean
  (`xml.etree.ElementTree`). `.csproj` wiring: both new files
  (`BactaHealingUtility.cs`, `CompUseEffect_BactaHeal.cs`, plus the revival
  item's `WorkGiver_CarryCorpseToBactaTank.cs`/
  `JobDriver_CarryCorpseToBactaTank.cs`) are all explicitly in
  `<Compile Include>` — no dead-compile trap.

**No bugs found.** All 18 DIRTY files marked CLEAN, commit `3cd8b692f`,
pushed. **This closes the `src/RimStarWars/Bacta/*` cluster in full (22/22
reviewable files CLEAN — 18 this wave, 4 already clean).**

Re-derived the final count after this cluster:
`code_review_status.py list | grep '^DIRTY'` filtered non-`.png` — **20
non-PNG DIRTY files remain** (38 minus this wave's 18). Next wave: no
standing named cluster; re-derive fresh from that command rather than
trusting this arithmetic, same standing instruction as every prior wave.

## Wave 42 — 2026-09-24

Re-derived fresh: the DIRTY non-PNG count had grown to **29** (not 20 — files
keep re-dirtying between waves from other agents' commits, expected). No
5+-file cluster existed in one directory; picked two small same-mod trios
instead, both confirmed `git status --porcelain` clean (no concurrent build
agent in flight) and both away from the live `JAWA_MESS_IMMUNITY_1` build
agent's work (traced its likely touch surface — Jawa xenotype/gene defs under
`RimStarWars/StarWarsRaces` and `RimUtinni/PawnFlavor` — and picked clusters
with zero overlap):

- **`EnvironmentalHazards` trio** — `BiomeGlowPatches.cs` (+44/-2: two new
  Harmony patches for `VENOMVINE_FORTRESS_PASSABILITY_1`, wiring
  `RM_BodySizeBarrierPatches.CreateRequest_Prefix`/
  `GetPawnCellBaseCostOverride_Postfix` via the existing generic `Apply`
  helper with a new `asPrefix` param, default `false`, backward compatible);
  `RM_EnvironmentalHazards.csproj` (+16: 6 new `<Compile Include>` for the
  contact-venom/body-size-barrier files — confirmed all 6 exist on disk, no
  dead-compile trap — plus a new `Unity.Collections` engine reference,
  ships with the game); `RM_EnvironmentalHazardsMod.cs` (+93/-1: new
  `bodySizeBarrierEnabled`/`bodySizeBarrierThreadCostMultiplier` mod-setting
  pair, full checkbox+slider+ExposeData+doc-comment wiring, and the fixed
  scroll-view height correctly raised 3400f→3880f per its own "raise this or
  the block is invisible" instruction). Cross-read `RM_BodySizeBarrierPatches.cs`
  and confirmed its two hook methods (already CLEAN from an earlier wave, not
  re-reviewed) are what's being wired in. **Found and fixed one stale
  comment**: the settings-window header said "35 checkboxes... three labeled
  sliders" — actually 36/6 (grepped `CheckboxLabeled`/`list.Slider(` counts);
  stale from before this wave already. No behavioural bugs.
- **`Pyrelands` trio** — `Pyrelands.xml`, `FireEcologyHook.cs`,
  `WildPlantAllowlist.cs`, all three a clean, consistent
  `RM_FE_Pyrelands` → `RM_Pyrelands` rename (`PYRELANDS_DEFNAME_RENAME_1`,
  closed 2026-09-21). Verified zero remaining `RM_FE_Pyrelands` in `src/`
  (criterion met) and that the plant defNames (`RM_FE_Plant_*`) were
  correctly left alone — only the biome defName was in scope for that
  rename. **Found and fixed one stale reference outside my DIRTY set**:
  `design/validation_walks/RimMandrake/Pyrelands.md` — a live north-star
  validation walk — still cited the dead `RM_FE_Pyrelands` defName 7 times in
  its `## must be true`/`## the walk` prose (a walk step literally instructs
  generating "a fresh RM_FE_Pyrelands map", which no longer resolves).
  Corrected all 7 to `RM_Pyrelands`; left the hashed `## north star` section
  (state: VALIDATED, `validated-hash: 90a286aa...`) untouched per the
  standing rule that touching it reverts validation — none of the 7 were
  inside it anyway.

Both fixes (the stale checkbox-count comment and the stale walk-defName
references) committed together at `4a023191b`, pushed, before marking any
file clean. All 6 files marked CLEAN, commit `ee027a88d`, pushed.

Re-derived the final count: **23 non-PNG DIRTY files remain** (29 minus this
wave's 6). Next wave: no standing named cluster — re-derive fresh via
`code_review_status.py list | grep '^DIRTY'` filtered non-`.png`, same
standing instruction as every prior wave. Two other small same-clean-mark-sha
trios are visible in that list and worth checking for cluster continuity:
`RimStarWars/StarWarsRaces` (`SW_Genes.xml`, `RimMandrakePawnKinds.xml`,
`RimMandrakeXenotypes.xml`, all at clean-mark `7e8587cea`) and
`RimStarWars/SWBestiary` (4 files) — but the StarWarsRaces one is exactly the
Jawa gene/xenotype territory this wave routed around for
`JAWA_MESS_IMMUNITY_1`; re-check `git status --porcelain` on it before
touching, it may still be live.

## Wave 43 — 2026-09-24: both flagged trios CLOSED (7 files)

`JAWA_MESS_IMMUNITY_1` finished and pushed (`a9aef1bc1`) before this wave
started; checked its actual diff (`git show --stat`) rather than trusting the
"likely touch surface" guess from wave 42 — it only ever touched two new
files under `src/RimUtinni/UtinniPatches/` (`Defs/GeneDefs/Jawa_MessImmunity.xml`,
`Patches/JawaMessImmunity.xml`), zero overlap with `StarWarsRaces` either way.
`git status --porcelain` confirmed clean on both target directories.

Reviewed all 7 files diff-scoped against each one's own clean-mark sha:
`RimStarWars/StarWarsRaces` trio (`SW_Genes.xml`, `RimMandrakePawnKinds.xml`,
`RimMandrakeXenotypes.xml`) + `RimStarWars/SWBestiary` 4-file cluster
(`About.xml`, `RSW_BiomesTeamPort_Items.xml`, `RSW_BiomesTeamPort_Races.xml`,
`RSW_Mynock.xml`).

**StarWarsRaces trio**: mostly `species_skin_rulings.json`-driven gene edits
(new `RSW_Skin_GreyBlue` GeneDef for the ruled Umbaran grey-blue skin — traced
to the right XenotypeDef, `RSW_RimMandrakeUmbaran`, not the Tuskens the
nearby comment block belongs to) plus the `XENOTYPE_CANON_CORRECTION_1`
rename `RSW_RimMandrakeSithKissaiPureblood(_Kind)` →
`RSW_RimMandrakeSithKissai(_Kind)`, consistently applied across the
PawnKindDef and XenotypeDef. Checked every added/changed gene reference
against `mcp__rimsage__get_def_details`/`search_defs` (RimSage answered —
this session is not the disconnected Mac laptop): `Hair_DarkBlack`,
`Hair_Gray`, `RSW_WaterBreathing`, `RSW_Skin_MidGray` all confirmed real
defs; `AptitudeStrong_Intellectual`/`AptitudeStrong_Artistic` correctly come
back "not found" because Aptitude genes are procedurally generated from the
`AptitudeStrong` `GeneTemplateDef` + a `SkillDef` suffix at runtime, not
static defs — confirmed by checking the pre-existing, already-shipping
`AptitudeStrong_Mining` resolves identically (also "not found," same
mechanism). No bugs.

**One finding, not a code bug, not fixed here**: `f894fe574` (2026-09-20)
renamed the Sith Kissai defName in this repo, but the ledger's
`FULL_LOAD_RESIDUE_TRIAGE_1` note from a **2026-09-24** Player.log harvest
still lists `RSW_RimMandrakeSithKissaiPureblood` as an untriaged crossref —
the live deployed mod still holds the old defName 4 days after the repo
rename. Deploy-path staleness (`rimworld-deploy`), not a review-scope fix;
flagging for whoever next touches `FULL_LOAD_RESIDUE_TRIAGE_1` or runs
`deploy_custom_mods.py` for `mandrake.rsw.starwarsraces`.

**SWBestiary cluster**: `About.xml`'s dependency-list changes (Harmony and
`OskarPotocki.VFE.Insectoid2` promoted to hard `modDependencies`, with
inline comments explaining exactly why — missing-comp-type def-discard and
texPath-binding failures respectively) are self-documenting and correct;
`brrainz.harmony` was added to `loadAfter` too, `Insectoid2` correctly
wasn't (texture lookups aren't load-order-sensitive). The `RSW_Stoneback` →
"bokka" and `RSW_EggStoneback*` → "bokka egg" changes are label-only
(defNames untouched) and consistent with each other. Verified the two new
`BIOME_SPECIFIC_FAUNA_LAW_1` hydrocarbon-lifeform defs (`RSW_Gembug`,
`RSW_GlowSlug`) both reference `RimMandrake.CreatureBehaviors.RM_HydrocarbonBloodExtension`,
which exists on disk and is in `RM_CreatureBehaviors.csproj`'s `<Compile
Include>` list — no dead-compile trap, the exact failure class CLAUDE.md
names for this assembly. `RSW_Mynock`'s flight-stat retrofit
(`MaxFlightTime`/`FlightCooldown`/`flightStartChanceOnJobStart`/
`flightSpeedFactor`/`canFlyIntoMap`) matches this repo's house convention
across other bestiary flyers, and its claimed generated art
(`RimStarWars/SWBestiary/ShipVermin/Mynock/Mynock.png`) is confirmed present
on disk. All 7 files parse clean (`xml.etree.ElementTree`). No bugs.

All 7 files marked CLEAN, commit `7b33bb90d`, pushed (one transient
`index.lock` retry mid-wave, cleared on its own — a concurrent agent's git
process, not this agent's).

Re-derived the final count: **17 non-PNG DIRTY files remain** (not the
arithmetic-expected 16 — files keep re-dirtying between waves from other
agents' commits, expected, same as every prior wave). Next wave: no standing
named cluster surfaced this pass; re-derive fresh via `code_review_status.py
list | grep '^DIRTY'` filtered non-`.png`.

## Wave 44 — 2026-09-24: recorded DIRTY backlog reached 0, but the full
## picture is NOT "every file is CLEAN" — 346 files were NEVER ENTERED

Reviewed all 17 non-PNG DIRTY files from wave 43's re-derived list, diff-scoped
against each file's own clean-mark sha (`git status --porcelain` confirmed
nothing was mid-edit by the concurrent FEVERWOOD_BOUGH_SOIL_TERRAIN_1 build
agent before touching `RUT_FeverWood.xml`): `src/DEPLOY_HOLD.txt`,
`CreatureBehaviors/About/About.xml` + `Source/RM_CreatureBehaviorsMod.cs`,
`FloodedCanyon/Defs/BiomeDefs/RM_FloodedCanyon_Biome.xml`, `FlowWorks/Defs/
LiquidTypes/TerrainDefs/RM_Propane.xml` + `Source/ManyWaters/RiverSteamHook.cs`,
`Inhabited/Source/DebugActions_Inhabited.cs`, `StructureInjections/Source/
GenStep_RimplacePlan.cs`, `Utils/artpipe/selftest_artpipe.py`,
`RimStarWars/StarWarsPatches/Defs/PawnKindDefs/AlienSpawnEnablers.xml`,
`RimUtinni/AshkarrFlora/About/About.xml` + `Defs/ThingDefs_Plants/
RUT_AshkarrFlora_Plants.xml`, `RimUtinni/PawnFlavor/Patches/
PawnFlavorPhase2_Xenotype.xml`, `RimUtinni/RotSporeKit/Defs/ThingDefs_Plants/
RUT_PaleTree.xml`, `RimUtinni/UtinniPatches/About/About.xml` +
`Defs/BiomeDefs/RUT_FeverWood.xml` + `Defs/FactionDefs/JawaAscendantHelix.xml`.

Verified cross-references rather than trusting prose: `RM_Propane.xml`'s
`waterBodyType: None→Saltwater` change traced to the generator's own
`LIQUID_ROWS` table in `generate_liquid_suite.py` (an owner-carded
`native_overrides`, not a hand-edit of generated output); the
`RSW_RimMandrakeSithKissaiPureblood→RSW_RimMandrakeSithKissai` rename in
`AlienSpawnEnablers.xml` and `JawaAscendantHelix.xml` confirmed against the
already-renamed `XenotypeDef`; `RUT_SweetlineWool`, `RUT_BoughSoil`,
`mandrake.rm.seashores`/`mandrake.rm.flowworks` packageIds, and the
`PaleTree`/`PaleMoss` texPaths all confirmed to resolve to real defs/files on
disk; `selftest_artpipe.py`'s hardcoded-threshold→named-constant rewrite
re-run (`python3 selftest_artpipe.py`) and passes in full.

**One real bug found and fixed**, not code but a doc-correctness defect inside
a reviewed file: `RM_CreatureBehaviorsMod.cs`'s 27-entry mod-settings header
comment had inserted the new `proximitySoundscapeEnabled` entry as "`9.`"
directly ahead of the pre-existing "`8. senseWebEnabled`" without renumbering
anything after it, leaving TWO entries both claiming "`9.`"
(`proximitySoundscapeEnabled` and `chewAnchorsBehaviorEnabled`) and the list
running 1,2,3,4,5,6,7,9,8,9,10,... Renumbered the whole 1..28 sequence in file
order, no functional change. Commit `e05f7e0f8`, pushed. Verified the file's
braces still balance and every `//  N.` marker now reads 1..28 with no
duplicates/gaps.

All 17 files marked CLEAN, commit `1a45ed672`, pushed.

🔴 **Re-derived the count and it is genuinely 0** —
`code_review_status.py list | grep '^DIRTY' | grep -v '\.png'` returns nothing.
**But this is NOT the milestone it looks like.** `list --show-untracked` (the
flag wave 9's own note, 35 waves ago, said a future wave should re-run and no
wave since appears to have) reports:

```
TALLY  CLEAN 3093  DIRTY 0  ORPHANED 0  NEVER ENTERED 346
```

**346 `.py`/`.cs`/`.xml` files under `src/` have never been given a
`code_review_status.py` entry at all** — the exact trap the tool's own
`find_untracked()` docstring names by history (485 of 1402 files invisible to
a "0 DIRTY" claim on 2026-09-05): a path with no entry doesn't appear in plain
`list`, but CLAUDE.md's own rule is explicit — "no entry ... is DIRTY" — so
these 346 are review debt too, just invisible to the report every prior wave
(including this one, until this check) has been deriving its count from.
⛔ **Do not report "every tracked file in the repo is CLEAN" off a bare `list`
count — it was never true, and this wave nearly repeated the exact mistake
CLAUDE.md's own "confident wrong numbers" doctrine warns about.** The real
backlog going into wave 45 is **346 NEVER ENTERED files**, not 0; the 17-file
recorded backlog closing out is real progress, but it was the smaller of two
backlogs and the loop has been counting only that one for at least 35 waves.

Next wave: run `code_review_status.py list --show-untracked` (not the plain
`list | grep DIRTY` every prior wave used) to get the real backlog, and start
working the 346 NEVER ENTERED files — full-file review (never diff-scoped,
per the loop's own protocol for a file with no prior clean mark) since none of
them have ever been reviewed once.

## Wave 45 — 2026-09-24: first wave against the real 346-file NEVER ENTERED
## backlog; sanity-checked it first, then reviewed 6

Re-ran `code_review_status.py list --show-untracked` fresh rather than
trusting wave 44's "346" verbatim — it read **346** again (no drift in the
few minutes between waves this time). Breakdown by extension: **306 `.xml`**,
**39 `.py`**, **1 `.cs`**. By directory, dominated by two live def/patch
trees: `src/RimStarWars/SWBestiary` (99), `src/RimUtinni/UtinniPatches` (83),
then `src/RimUtinni/LanternDeeps` (18), `src/RimMandrake/Utils` (18),
`src/RimUtinni/StructureInjectionsRUT` (17), `src/RimMandrake/CreatureBehaviors`
(14), `src/RimMandrake/GelatinousSlime` (12), `src/RimMandrake/FlowWorks` (12),
smaller tails elsewhere.

**Sanity check on `list --show-untracked` itself, per the brief's instruction
to verify before diving in blind:** sampled 8 files at random from the 346 —
all 8 were `git ls-files`-TRACKED, real committed source. Checked the whole
list for build-artifact contamination (`/obj/`, `/bin/`, `__pycache__`) and
test-fixture noise — **zero hits on either**. So the tool is not pulling in
untracked build output; the 346 are genuinely never-reviewed tracked source,
exactly as wave 44 concluded. No tool bug to flag this time.

Picked 6 files spanning C#/Python and covering a spread of subsystems, all
confirmed reachable before reviewing (csproj `<Compile Include>` for the .cs,
`if __name__ == "__main__"` CLI entry + sibling-convention checks for the
`.py` files — none were orphaned one-offs):

- `src/RimMandrake/EnvironmentalHazards/Source/RM_Patch_LeachmossWildSpawnGate.cs`
  — Harmony postfix gating `RM_Leachmoss` out of wild-plant spawn rolls behind
  a Mod Settings bool. Confirmed in `RM_EnvironmentalHazards.csproj`'s Compile
  list; `RM_EnvironmentalHazardsSettings.leachmossEnabled` resolves to a real
  field in `RM_EnvironmentalHazardsMod.cs`. No bugs.
- `src/RimMandrake/Utils/probe_png_wellformed.py` — bulk PNG structural
  validator (signature/chunk/CRC32/IHDR-first/IEND-last). Traced its
  `DIRTY  {rel}  ({detail})` parser against `code_review_status.py`'s actual
  `cmd_check` format line-by-line — matches exactly. No bugs.
- `src/RimMandrake/rimflow/citations_lint.py` — the stale-gate/state-lie doc
  linter. Ran its selftest: **11/11 passed**, including the one case that
  proves the 3-line gate/closure window (which reads one line *after* the
  citation as well as before — looked like a possible off-by-one until the
  selftest confirmed it's deliberate and covered). No bugs.
- `src/RimMandrake/rimflow/live_proof_lint.py` — detects a close whose commit
  body names live-proof/deploy debt with no spawned successor anywhere in the
  ledger. Ran the paired hook's selftest (`selftest_warn_close_live_proof_owed.py`):
  **7/7 passed**. Ran `live_proof_lint.py sweep` live against the real ledger:
  executes clean, reports 5 pre-existing unspawned closes (process debt,
  not a code defect — out of this wave's scope). No bugs.
- `src/RimMandrake/bridgetools/prove_river_water.py` — bridge repro/verify
  script for the missing-water-terrain bug. Static full-file review only (no
  bridge access this wave); its hardcoded `D:\Luke\dev\Rimworld\...` sys.path
  insert matches the same line in both sibling `prove_*.py` scripts, so not a
  one-off mistake. No bugs.
- `src/RimUtinni/StructureInjectionsRUT/Source/Ashfall/gen_ashfall_layout.py`
  — KCSG StructureLayoutDef generator for the Ashfall Spire dungeon. Ran it:
  reachability BFS proof passes, and the regenerated
  `StructureLayoutDefs_Ashfall.xml` + `SymbolDefs_Ashfall.xml` came out
  **byte-identical** to the committed files (`git status` clean after the
  run) — strongest possible confirmation this generator is still correct.
  No bugs.

**No bugs found this wave** — all 6 marked CLEAN with nothing significant,
commit `cf1d9cc76`, pushed.

Re-measured after: `TALLY  CLEAN 3095  DIRTY 4  ORPHANED 0  NEVER ENTERED 340`
— 340 matches 346 − 6 exactly; the 4 DIRTY are new re-dirties from a
concurrent build agent's commits mid-wave (same expected churn every prior
wave has noted, not this wave's doing). **340 NEVER ENTERED files remain**,
still dominated by `SWBestiary` and `UtinniPatches` XML. Next wave: keep
working this backlog with `list --show-untracked`, not plain `list`.

## Wave 46 — 2026-09-24: SWBestiary cluster, 7 files

Re-ran `list --show-untracked` fresh: **340 NEVER ENTERED**, same tally wave
45 left. Confirmed `src/RimStarWars/SWBestiary` (packageId
`mandrake.rsw.swbestiary`, real About.xml) is a reachable live mod, then
picked 7 files from its 99-file NEVER-ENTERED share, spanning a spread of
subsystems rather than one folder: `Defs/ThingDefs_Races/
RSW_GreaterKraytDragon.xml`, `Defs/BiomesTeamPort/ThingDefs_Races/
RSW_Maguana.xml`, `Defs/DesertPort/RSW_Ultracactus.xml` (+ its raw-food
item), `Defs/ScrapNest/RSW_ScrapNest.xml`, `Defs/ThingDefs_Races/
RSW_GreatDevourer.xml`, `Defs/ThingDefs_Items/RSW_GreatDevourerEggs.xml`,
`Defs/DesertPort/RSW_DesertPortMechanics.xml`.

Full-file review (all 7 had no prior clean mark). Cross-checked the C#
surface the mechanics file leans on — `RSW_DesertPortMechanics.xml` invokes
`RimMandrake.StarWars.SWBestiary.JobDriver_EatMetal`,
`JobGiver_EatMetal`, `JobGiver_HoardScrap` (via `RSW_ScrapNest.xml`'s
`ThinkTreeDef`) and `CompProperties_AbilityFuelSpew` — grepped
`Source/BeastMechanics/*.cs` for namespace + class declarations, all four
resolve exactly. Checked defName cross-refs: `RSW_GreatDevourer`'s
`<body>RSW_WormWithArmor</body>` resolves in `RSW_AADesertPort_Bodies.xml`.
No bugs found in any of the 7 — all marked CLEAN, commit `0ff446642`, pushed.

Hit a transient `.git/index.lock` from the concurrent build agent mid-commit
(brief warned this could happen); waited and retried, succeeded on the third
attempt with no data loss.

Re-measured after: `TALLY  CLEAN 3102  DIRTY 4  ORPHANED 0  NEVER ENTERED 333`
— 333 matches 340 − 7 exactly. **333 NEVER ENTERED files remain**, still
dominated by `SWBestiary` (92 left) and `UtinniPatches` (83). Next wave: keep
working this backlog with `list --show-untracked`.

## Wave 47 — 2026-09-24: SWBestiary DesertPort/Zakkro cluster, 9 files, 1 bug fixed

Re-ran `list --show-untracked` fresh: **333 NEVER ENTERED**, matching wave
46's close exactly (`CLEAN 3101 DIRTY 5`, 4→5 DIRTY is the same concurrent
build-agent churn every wave notes). `SWBestiary` still the biggest single
cluster at 92 files.

Picked 9 files (7 planned, +1 mid-wave, +1 to round out the spread) from
`SWBestiary`'s `DesertPort`/`ThingDefs_Items`/`ThingDefs_Misc`/`Bodies`/`art`
subtrees — none had a prior clean mark:

- `Defs/BiomesTeamPort/ThingDefs_Items/RSW_Maguana_Items.xml` — **found and
  fixed a real bug**: `RSW_EggMaguanaUnfertilized`'s `<label>` read
  "**magmuana** egg (unfert.)" — a copy-paste typo off the fertilized egg's
  label two defs above it ("maguana egg (fert.)"). Player-facing text error,
  high confidence, fixed to "maguana egg (unfert.)". Commit `7775fe8ba`,
  pushed.
- `Defs/Bodies/RSW_AADesertPort_Bodies.xml` — Alpha Animals body/body-part
  port (`RSW_WormWithArmor`, `RSW_TentacledQuadrupedEyeless`), defName-only
  rename, pure data. No bugs.
- `Defs/DesertPort/RSW_DesertPortB_Plants.xml` — 4 SWAC flora ports
  (chak-root, nysillin, hubba gourd, bloddle) with raw-food closures. No bugs.
- `Defs/DesertPort/RSW_ExtremeDesertSignatureFlora.xml` — Extreme Desert's
  own signature flora (light-pipe nub, ollim, ollim wood), heavily
  cross-referenced against live engine config-error fixes from 2026-09-21.
  No bugs.
- `Defs/DesertPort/RSW_Zakkro.xml` + `Defs/ThingDefs_Items/RSW_ZakkroEgg.xml`
  — the cavern-beast pair (`EXTREME_DESERT_CAVERN_BEAST_1`), deliberately
  unwired pending cavern map-gen. No bugs.
- `Defs/ThingDefs_Misc/RSW_Filth_WhaleDung.xml` — fixes a shipped no-op
  (Filth placementMask vs NaturalTerrainBase's filthAcceptanceMask). Verified
  the claimed real texture actually exists on disk:
  `Textures/Things/Filth/RSW_WhaleDung.png` — present. No bugs.
- `art/ScrapNest/gen_scrapnest_placeholder.py` — 3-variant procedural
  placeholder-nest generator, explicitly self-documented as throwaway. No
  bugs.
- `Defs/DesertPort/RSW_DesertPortMisc_Items.xml` — leather/meat/egg closure
  for the misc DesertPort fauna. Checked the `RSW_Sandstrider`/`RSW_Tuskcoil`
  defName vs "ossik"/"ulgga" label mismatch that looked suspicious at first
  glance — cross-checked both race defs in `RSW_DesertPortMisc_Races.xml`:
  same defName/label split there too, so it's the repo's deliberate
  bare-defName-vs-renamed-label convention, not a bug.

All 9 marked CLEAN (one after its typo fix was committed first, since
`mark-clean` refuses on uncommitted changes). Commits `7775fe8ba` (the fix)
and `3d90e4806` (status file), both pushed. No `.git/index.lock` contention
this wave.

Re-measured after: `TALLY  CLEAN 3110  DIRTY 5  ORPHANED 0  NEVER ENTERED 324`
— 324 matches 333 − 9 exactly. **324 NEVER ENTERED files remain**, `SWBestiary`
now at 83 left, `UtinniPatches` still 83. Next wave: keep working
`SWBestiary` (still the larger single cluster once it drops below
`UtinniPatches`, switch to that) with `list --show-untracked`.

## Wave 48 — 2026-09-24: SWBestiary ThingDefs_Races, 8 files, 6 files fixed

Re-ran `list --show-untracked` fresh: **324 NEVER ENTERED**, matching wave
47's close exactly, `SWBestiary` (83) and `UtinniPatches` (83) tied. Picked
`SWBestiary` over `UtinniPatches`: its 81 remaining files are almost all one
folder/one def-type (`Defs/ThingDefs_Races/RSW_*.xml`, one creature per
file, same template every prior SWBestiary wave has calibrated against),
the more coherent sub-cluster versus `UtinniPatches`'s mixed
GenStepDefs/HediffDefs/TerrainDefs/Patches spread.

Picked 8 alphabetically-first files from `ThingDefs_Races`, none had a
prior clean mark: `RSW_Drazzik.xml`, `RSW_Falumpaset.xml`,
`RSW_Fambaa.xml`, `RSW_Fanback.xml`, `RSW_FeralGrazer.xml`,
`RSW_FeralNerf.xml`, `RSW_FrilledGorg.xml`, `RSW_Gelagrub.xml`.

Full-file review of all 8, cross-checking C# and cross-def references
rather than reading each file in isolation: `RSW_Drazzik`'s
`RM_CompProperties_DrumLure` and its two hediffs
(`RM_DrumLureLured`/`RM_DrumLureSubmersion`) resolve in
`src/RimMandrake/CreatureBehaviors/Source/RM_CompDrumLure.cs` +
`RM_DrumLure_Hediffs.xml`; its egg's `hatcherPawn` (`RSW_Nizzek`) resolves
in `RSW_Nizzek.xml`. `RSW_Fambaa`'s body repoints to the already-ported
`RSW_Dewback` (confirmed present). No bugs in the mechanics/wiring of any
of the 8.

**Found and fixed a real bug, high confidence**: `RSW_Fambaa.xml`'s and
`RSW_Gelagrub.xml`'s `<race><willNeverEat>` blocks both carried
`MayRequire="Ludeon.RimWorld.Odysse"` (missing the trailing "y") on the
`Plant_TreeArchean` entry — a copy-paste typo, since the other 4 entries
in the same block (Royalty/Ideology/Biotech/Anomaly sacred trees) are all
correctly spelled. A misspelled `MayRequire` packageId never matches an
active mod, so that `<li>` silently drops on every load regardless of
whether Odyssey is active — these animals would eat the Odyssey sacred
archotree even with the DLC on, unlike vanilla's intent for the other 4.
Grepped the whole repo for the same string rather than fixing just the 2
files in this wave's pick: found **6** total occurrences (also
`RSW_Horax.xml`, `RSW_Ronto.xml`, `RSW_Skalder.xml`, `RSW_Zeer.xml` — none
otherwise reviewed this wave), fixed all 6 in one commit per
"correctness outranks seat ownership." Commit `41ce89ca8`, pushed.

All 8 picked files marked CLEAN (Fambaa/Gelagrub after their fix was
committed, since `mark-clean` refuses on uncommitted changes). Commit
`b1d7bd744` (status file), pushed. Hit a transient `.git/index.lock` from
the concurrent build agent on the status-file commit; waited 5s and
retried, succeeded with no data loss.

Re-measured after: `TALLY  CLEAN 3118  DIRTY 5  ORPHANED 0  NEVER ENTERED 320`.
320 = 324 − 8 (cleaned) + 4 (new files the concurrent build agent added
mid-wave, not this wave's doing) — reconciles exactly, not a discrepancy.
**320 NEVER ENTERED files remain**: `SWBestiary` now at **75**,
`UtinniPatches` at **85** (UtinniPatches grew by 2, also the concurrent
build agent). `SWBestiary` has now dropped below `UtinniPatches` — next
wave: switch to `UtinniPatches` with `list --show-untracked`, per wave
47's own rule. The 4 fixed-but-unreviewed SWBestiary files above
(Horax/Ronto/Skalder/Zeer) still need a full-file review of their own
before they can be marked CLEAN — the typo fix alone doesn't cover it.

## Wave 49 — 2026-09-24: SWBestiary Odyssey-typo cleanup + UtinniPatches Patches/, 10 files, 12 fixed

Ran `list --show-untracked` fresh: **320 NEVER ENTERED**, matching wave 48's
close exactly. Full-file reviewed the 4 SWBestiary files wave 48 left
fixed-but-unreviewed (`RSW_Horax.xml`, `RSW_Ronto.xml`, `RSW_Skalder.xml`,
`RSW_Zeer.xml`) — verified the `Odyssey` typo fix in each is correct and
cross-checked every def/resource/body/ability reference the files make
(leather, meat, eggs, bodies, abilities, trophies) all resolve.

**Found and fixed a real bug in `RSW_Zeer.xml`, high confidence**: its
`lifeStageAges`' adult-stage `soundWounded/Death/Call/Angry` referenced
bare `Pawn_Zeer_Wounded` etc., but the actually-ported SoundDef (per its own
header comment) is `RSW_Pawn_Zeer_Wounded` — the mod's RSW_ tier rename
applied the prefix to the SoundDef but never updated this ThingDef's own
reference to it, so the bare name resolves to nothing and no combat/death
sound plays for adult Zeer. Wrote a small script to check every
`sound{Wounded,Death,Call,Angry}` value in
`Defs/ThingDefs_Races/*.xml` against the SoundDefs actually defined in
`SoundDefs_SWBestiary.xml`, flagging any bare reference whose RSW_-prefixed
twin exists but whose bare form doesn't (excluding the many deliberate
reuses of genuinely vanilla/DLC sound families — Boomrat, Elk, Rhinoceros,
Cat, Muffalo, Dromedary, Rodent, Chick, Wildboar, Monkey, Thrumbo,
BigInsect, Spelopede, Megascarab, Iguana — all confirmed present with no
RSW_ twin, i.e. genuine cross-references, not renamed ports). Found the
same bug in **11 more files**: `RSW_Uvak.xml`, `RSW_Varactyl.xml`,
`RSW_Voorpak.xml`, `RSW_WarWyrm.xml`, `RSW_Whisperbird.xml` (adult stage),
`RSW_Woolamander.xml` (adult stage), `RSW_Wyyyschokk.xml`,
`RSW_Yobshrimp.xml`, `RSW_Lylek.xml` (both baby and adult stages),
`RSW_ScrapNestBird.xml` (adult stage, cross-references Whisperbird's
sounds), `RSW_Pufferpig.xml` (soundDeath only, cross-references Gullipud's)
— all fixed to the RSW_-prefixed defName that actually exists. Left
`RSW_Zakkeg.xml`'s own `Pawn_Boma_*` mismatch alone: already flagged in its
own header comment as a separate pre-existing donor bug (wrong species
entirely, not just a missing prefix) and explicitly left as-is by a prior
pass — not the same defect class. Commit `609daf5ad`, pushed. All 4 picked
files marked CLEAN (Zeer after its fix was committed). No bugs in
Horax/Ronto/Skalder beyond the already-fixed Odyssey typo.

Switched to `UtinniPatches` (biggest cluster this wave, 85 files) per wave
48's rule. Its `Patches/` subfolder (18 files) is the largest coherent
sub-cluster there — picked 6 alphabetically-first: `AnoobaDrawSize_Fix.xml`,
`BiomeFishTypes_TwilightDeep.xml`, `DesertWrapsApparelWiring.xml`,
`FlowWorks_SubsurfaceLiquid_Ashkarr.xml`, `JawaMessImmunity.xml`,
`RUT_FeverWood_ScatterPoolsGenStep_Register.xml`. Full-file reviewed all 6,
cross-checking every xpath target, MayRequire packageId, and referenced
defName against the actual def files (fish species, liquid defs, gene defs,
xenotype defs, pawnkind defs, GenStepDef, the `RM_SubsurfaceLiquidBiomeExtension`
C# class) — all resolve correctly, all patches well-gated
(`PatchOperationFindMod`/`PatchOperationConditional` used correctly, no
double-add risk). No bugs found in any of the 6. All marked CLEAN.

Commit `b8690768e` (status file + this entry), pushed. No `.git/index.lock`
contention this wave.

Re-measured after: `TALLY  CLEAN 3128  DIRTY 5  ORPHANED 0  NEVER ENTERED 310`
— 310 = 320 − 10 exactly, no concurrent-agent noise this wave. **310 NEVER
ENTERED files remain**: `UtinniPatches` now at **79**, `SWBestiary` at
**71**. `UtinniPatches` is still the larger cluster — next wave: keep
working it (`Patches/` has 12 files left, or move to
`Defs/ThingDefs_Items`, its next-biggest subfolder at 11) with
`list --show-untracked`.

## Wave 50 — 2026-09-24: UtinniPatches Patches/, 8 files picked, 7 fixed clean

Ran `list --show-untracked` fresh: **310 NEVER ENTERED**, matching wave 49's
close exactly (`UtinniPatches` 79, `SWBestiary` 71 — confirmed, no drift).
Continued `UtinniPatches/Patches/` per wave 49's own next-step note, picking
the 8 alphabetically-first of its 12 remaining files:
`RUT_Greentide_LivingBolesGenStep_Register.xml`,
`RUT_Greentide_RootCausewaysGenStep_Register.xml`,
`RUT_Miasma_CrecheScatterer_Register.xml`, `RUT_TarShallow_GeneratedFilth.xml`,
`RotDecayHarvest_LivingProduce.xml`, `RotGuardianGroves_WildSpawn.xml`,
`RotPaleTree_WildSpawn.xml`, `RotSpecies_NamesAndSizes.xml`.

Full-file reviewed all 8, cross-checking every `xpath` target, `MayRequire`
gate/`PatchOperationFindMod` mod name and referenced defName/C# class against
the actual live defs rather than reading each patch in isolation: the three
GenStep-register patches' target GenStepDefs (`RUT_GenStep_LivingBoles`,
`RUT_GenStep_RootCauseways`, `RUT_GenStep_CrecheScatterer`) all exist with
matching defNames; `RUT_TarShallow_GeneratedFilth.xml`'s `RM_TarShallow`
TerrainDef and `RM_Filth_Tar` ThingDef both resolve; `RotDecayHarvest_
LivingProduce.xml`'s two RotSporeKit flora targets
(`RUT_Glimmerslime`/`RUT_RawDulcis`) exist with no pre-existing
`<modExtensions>` (confirming its own nomatch-branch comment still holds),
its `RM_LivingProduceExtension` class exists with `heatPerUnit = 3.5f`
matching the comment's stated Campfire calibration exactly; `RotGuardianGroves_
WildSpawn.xml`'s four plant defNames and `RotPaleTree_WildSpawn.xml`'s
`RUT_PaleTree` (confirmed genuinely `MayRequire="Ludeon.RimWorld.Royalty"`-gated
on its own ThingDef, matching the patch's own claim) all exist and none
already appear in `RUT_TheRot.xml`'s base `<wildPlants>` list, so both
Add-only patches append with no key collision; `RotSpecies_NamesAndSizes.xml`'s
~20 `texPath` overrides were checked against `Textures/RotSpecies/` on disk —
every referenced path has matching art. No bugs found in any of the 8.

Per the brief, re-ran wave 49's own sound-prefix check (`sound{Wounded,Death,
Call,Angry}` bare name vs RSW_/RUT_-prefixed SoundDef) as a repo-wide sweep
across both `UtinniPatches/Defs/ThingDefs_Races/*.xml` and
`SWBestiary/Defs/ThingDefs_Races/*.xml`, since this is a known recurring
pattern: the only hits were `RSW_Zakkeg.xml`'s 4 `Pawn_Boma_*` references —
already identified in wave 49 as the pre-existing donor-species mismatch, not
this bug class, and deliberately left alone. No new instances anywhere in the
repo; wave 49's fix was complete.

`RUT_TarShallow_GeneratedFilth.xml` reviewed clean (no bugs) but **not**
marked CLEAN: `mark-clean` refused it as having uncommitted changes — its
working-tree copy carries an in-flight edit from the concurrent
`SUMP_TAR_NASTINESS_1` build agent (its own header notes a same-day
`DEPLOY_HOLD LIFTED` edit). Left it alone rather than touching another
agent's uncommitted work; it stays NEVER ENTERED for a future wave once that
edit lands.

Commit `148261324` (status file + this entry), pushed. No `.git/index.lock`
contention this wave.

Re-measured after: `TALLY  CLEAN 3134  DIRTY 6  ORPHANED 0  NEVER ENTERED 303`
— 303 = 310 − 7 exactly, no concurrent-agent noise on the NEVER ENTERED count
this wave (DIRTY ticked 5→6, unrelated to this wave's picks). **303 NEVER
ENTERED files remain**: `UtinniPatches` now at **72**, `SWBestiary` at **71**
— nearly tied. `UtinniPatches/Patches/` has **5** files left
(`RUT_TarShallow_GeneratedFilth.xml` plus `VQEQuestText_AreForsaken.xml`,
`WildAnimals_CrackedLands.xml`, `WildAnimals_Greentide.xml`,
`WyyyschokkFangPendantFactions.xml`) — next wave: finish it, or switch to
`SWBestiary/Defs/ThingDefs_Items` (11) since the two clusters are now
essentially tied, with `list --show-untracked`.

## Wave 51 — 2026-09-24: UtinniPatches Patches/ finished, SWBestiary races started

Ran `list --show-untracked` fresh: **303 NEVER ENTERED**, matching wave 50's
close exactly (`UtinniPatches` 72, `SWBestiary` 71 — confirmed, no drift).

First checked `git status --porcelain` on `RUT_TarShallow_GeneratedFilth.xml`
per the brief: still `M` (uncommitted), same in-flight edit from the
concurrent `SUMP_TAR_NASTINESS_1` build agent noted in wave 50 — not
settled, left alone again. That leaves only **4** reviewable files in
`UtinniPatches/Patches/`, so picked all 4
(`VQEQuestText_AreForsaken.xml`, `WildAnimals_CrackedLands.xml`,
`WildAnimals_Greentide.xml`, `WyyyschokkFangPendantFactions.xml`) plus 4
alphabetically-first from `SWBestiary/Defs/ThingDefs_Races` (the next
biggest live subfolder there — `Defs/ThingDefs_Items` from wave 50's own
"next wave" note turned out to already be **fully CLEAN**, nothing left to
pick; that stale pointer is now corrected by this entry):
`RSW_Gizka.xml`, `RSW_Gorg.xml`, `RSW_Gornt.xml`, `RSW_GraniteSlug.xml`.

Full-file reviewed all 8. `VQEQuestText_AreForsaken.xml` patches an
external donor mod's (VQE - Ancients) quest text — its internal xpath/
index structure and PatchOperationFindMod/Sequence mechanism check out
and it parses clean, but the donor's own defs aren't in this repo so the
xpath targets themselves are unverifiable offline; same shape as the
already-CLEAN `AncientsAreRakata.xml` it says it copies. The two
`WildAnimals_*` files were checked by diffing their content against the
live source biome defs they claim to mirror: `WildAnimals_CrackedLands.xml`
matches `RUT_CrackedLands.xml`'s own frozen wildAnimals/wildPlants/
baseWeatherCommonalities/terrainsByFertility verbatim (the one deliberate
addition, `RSW_SandPillar`, is documented and correctly not yet in the
frozen twin). `WildAnimals_Greentide.xml`'s row count and weight sum were
recomputed by hand against its own claimed 26 rows / 9.168 total — correct
— but its Op2 comment still said "all 23" from before the 2026-09-23
dianoga removal; the block actually carries 22 RSW_ rows. **Fixed**
(23->22, commit `8b0b715b5`). Every RSW_/AA_/VFEI2_ defName referenced by
both files was checked to resolve (AA_/VFEI2_ entries are donor-mod
defNames, correctly absent from this repo — that's expected, not a bug).
`WyyyschokkFangPendantFactions.xml`'s xpath and target packageId
(`mandrake.rsw.trophycraft`) were checked directly against
`RSW_TrophyCraft_Thoughts.xml`'s own `modExtensions/li/factionDefNames`
node — matches exactly, and `RUT_Jawa_WildsteamClan` resolves to the
live FactionDef.

The 4 `SWBestiary` race files (Gizka/Gorg/Gornt/GraniteSlug) got the
wave 49-50 sound-prefix check plus a defName resolution pass on every
cross-reference (`leatherDef`, `specificMeatDef`, egg comp defs,
`canCrossBreedWith` targets, `BodyDef`): all `sound{Wounded,Death,Call,
Angry}` fields are correctly RSW_-prefixed, and every referenced def
(`RSW_Leather_Saurian`, `RSW_Saurian_Meat`, `RSW_EggGizka*`,
`RSW_Gorg_Meat`, `RSW_EggGorg*`, `RSW_FrilledGorg`, `RSW_LongtailGorg`,
`RSW_Leather_Reptomammal`, `RSW_Gornt_Meat`, `RSW_Silica_Meat`) exists.
No bugs found beyond the one comment fix above.

Commit `8b0b715b5` (the fix), then status file + this entry in a second
commit, both pushed. No `.git/index.lock` contention this wave.

Re-measured after: `TALLY  CLEAN 3142  DIRTY 6  ORPHANED 0  NEVER ENTERED 295`
— 295 = 303 - 8 exactly, no concurrent-agent noise this wave. **295 NEVER
ENTERED files remain**: `UtinniPatches` now at **68** (its `Patches/`
subfolder is exhausted except the blocked TarShallow file), `SWBestiary`
at **67**. Nearly tied again — next wave: `SWBestiary/Defs/ThingDefs_Races`
has ~65 files left (the next-biggest live cluster in either mod now that
`Patches/` and `ThingDefs_Items` are both spent), or survey `UtinniPatches`
for its next-biggest subfolder, with `list --show-untracked`.

## Wave 52 — 2026-09-24: SWBestiary races continued, UtinniPatches Patches/ fully closed

Ran `list --show-untracked` fresh: **306 NEVER ENTERED** (up from wave 51's
295 — 11 new files appeared from a concurrent build agent's own work, e.g.
`RUT_TarredSurgery_RecipeUsers.xml`, `build_desert_review_sheet.py`, several
new `ThingDefs_Items` catch/resource files — normal cross-agent noise, not
this loop's doing).

First re-checked `git status --porcelain` on `RUT_TarShallow_GeneratedFilth.xml`
(correct repo-relative path this time — wave 51's check used a wrong path
that happened to also return empty, so its "still M" reading was actually
mis-diagnosed; re-verified from scratch): clean, no uncommitted changes —
the concurrent `SUMP_TAR_NASTINESS_1` build agent's edit has landed and
committed. Reviewed it: `PatchOperationAdd` wires `<generatedFilth>RM_Filth_Tar
</generatedFilth>` onto `TerrainDef[defName="RM_TarShallow"]`; both
`RM_TarShallow` (`FlowWorks/Defs/LiquidTypes/TerrainDefs/RM_Tar.xml`) and
`RM_Filth_Tar` (`FlowWorks/Defs/LiquidTypes/ThingDefs/RM_Filth_Tar.xml`)
resolve, and the sibling `filthAcceptanceMask` file it depends on exists.
No bugs. **Marked CLEAN — `UtinniPatches/Patches/` is now fully exhausted.**

Picked the next 7 alphabetically-first files from
`SWBestiary/Defs/ThingDefs_Races/`: `RSW_Grank.xml`, `RSW_Groundrunner.xml`,
`RSW_Gutkurr.xml`, `RSW_Hawkbat.xml`, `RSW_Hrumph.xml`, `RSW_Hssiss.xml`,
`RSW_Igitz.xml`. Full-file reviewed all 7, each got the wave 49-51
sound-prefix check (`sound{Wounded,Death,Call,Angry}`): six carry
correctly RSW_-prefixed sounds, all 4 fields present and all 4 resolve in
`SoundDefs_SWBestiary.xml` for each; `RSW_Groundrunner.xml` deliberately
uses bare vanilla `Pawn_Muffalo_*` (its own header says so explicitly —
correct, not this bug class). Every cross-referenced def (bodies:
`RSW_CorellianHound`, `RSW_Gutkurr`, `RSW_Hssiss`, `RSW_Igitz`; leather/meat:
`RSW_Reptomammal_Meat`, `RSW_Leather_Insectile`/`RSW_Insectile_Meat`,
`RSW_Leather_Reptavian`/`RSW_Reptavian_Meat`, `RSW_Leather_Dark`/
`RSW_Saurian_Meat`, `RSW_Pachydermoid_Meat`, `RSW_Gorg_Meat`; eggs:
`RSW_EggGutkurr*`, `RSW_EggHawkbat*`, `RSW_EggHssiss*`, `RSW_EggIgitz*`;
body-part groups: `RSW_SWClaws`, `RSW_SWTailAttackTool`,
`RSW_SWToxicAppendage`) was confirmed to resolve to a real defName in the
repo. `RSW_Hawkbat.xml` already carries full native flight
(`MaxFlightTime`/`FlightCooldown`/`canFlyIntoMap`/`canLeaveMapFlying` plus a
real `flyingAnimationFramePathPrefix` flip-book, 4 frames) — already
compliant with the "if it flies in the fiction" rule, nothing to fix. No
bugs found in any of the 7.

Commit `22125e2f1` (status file), pushed. No `.git/index.lock` contention
this wave.

Re-measured after: `TALLY  CLEAN 3150  DIRTY 6  ORPHANED 0  NEVER ENTERED 298`
— 298 = 306 − 8 exactly, no further concurrent-agent noise mid-wave.
**298 NEVER ENTERED files remain**: `UtinniPatches` at **73** (its own
`Patches/` subfolder is now fully spent — the 1 remaining `Patches/` file,
`RUT_TarredSurgery_RecipeUsers.xml`, is new since wave 51 and unreviewed;
`Defs/` carries 68, `Languages/` 3), `SWBestiary` at **60**
(`Defs/ThingDefs_Races` has **58** left). Next wave: continue
`SWBestiary/Defs/ThingDefs_Races` (still the single biggest live cluster),
with `list --show-untracked`.

## Wave 53 — 2026-09-24: SWBestiary races continued (I-K)

Ran `list --show-untracked` fresh: **298 NEVER ENTERED**, matching wave 52's
ending tally exactly — no concurrent-agent noise this wave.

Picked the next 8 alphabetically-first files from
`SWBestiary/Defs/ThingDefs_Races/`: `RSW_IridonianReek.xml`,
`RSW_Jakobeast.xml`, `RSW_Jamel.xml`, `RSW_Jimvu.xml`, `RSW_Kinrath.xml`,
`RSW_Klorslug.xml`, `RSW_KowakianMonkeyLizard.xml`, `RSW_KraytDragon.xml`.
Full-file reviewed all 8, each got the wave 49-52 sound-prefix check
(`sound{Wounded,Death,Call,Angry}`): all 8 carry correctly RSW_-prefixed
sounds (`RSW_Pawn_Reek_*`/`RSW_Pawn_ReekBaby_*` for IridonianReek — a
deliberate donor-documented reuse of plain Reek's clips, not this bug
class — plus `RSW_Pawn_{Jakobeast,Jamel,Jimvu,Kinrath,Klorslug,
KowakianMonkeyLizard,KraytDragon}_*` for the rest), all 4 fields present
and all 4 confirmed to resolve in `SoundDefs_SWBestiary.xml`. Every
cross-referenced def was swept and confirmed to resolve: bodies
(`RSW_Reek`, `RSW_Jakobeast`, `RSW_Jimvu`, `RSW_Kinrath`, `RSW_Klorslug`,
`RSW_KowakianMonkeyLizard`, `RSW_KraytDragon`), body-part groups
(`RSW_SWHornAttackTool`, `RSW_SWToxicAppendage`,
`RSW_SWLeftLegClawAttackTool`/`RSW_SWRightLegClawAttackTool`,
`RSW_SWTailAttackTool`, `RSW_SW_DexterousTail`, `RSW_SW_Spikes`), leather/
meat (`RSW_Leather_Tough`/`RSW_Tough_Meat`, `RSW_Leather_Bright`/
`RSW_Felinoid_Meat`, `RSW_Leather_Reptomammal`/`RSW_Reptomammal_Meat`,
`RSW_Leather_Insectine`, `RSW_Leather_Insectile`/`RSW_Insectile_Meat`,
`RSW_Leather_Mammavian`/`RSW_Anthropoid_Meat`,
`RSW_Leather_KraytDragon`/`RSW_Krayt_Meat`), eggs (`RSW_EggKinrath*`,
`RSW_EggKlorslug*`, `RSW_EggKraytDragon*`), trophies
(`RSW_JakobeastHorn`, `RSW_KraytDragonSkull`), and abilities
(`RSW_SW_WebShot`/`RSW_SW_Webbed`/`RSW_SW_WebShotprojectile`,
`RSW_SW_Calamity`). `RSW_KraytDragon.xml`'s own header claims it already
fixed `RSW_GreaterKraytDragon.xml`'s `canCrossBreedWith` to point at
`RSW_KraytDragon` instead of the bare donor name in an earlier pass — spot-
checked directly against that file, confirmed true. `TuskAttackTool`
(Jakobeast's tusks) correctly stays bare/unresolvable in this repo — it's
Alpha Animals' (`sarg.alphaanimals`) own group, per the file's own header,
same "leave bare, no MayRequire" pattern as other cross-mod group reuse.

🔴 **One real bug found and fixed**: `RSW_Jimvu.xml`'s `race` block carried
`<lifeExpectancy>` twice — `22` then, 20 lines later after the
`litterSizeCurve` block, `30`. XML last-node-wins means `30` was already
the live value, but the dead `22` line is exactly the kind of duplicate
that gets "corrected" back to the wrong number by a future edit. Fixed:
removed the dead first occurrence, `30` stands. Commit `50a5f7f57`.

Commits `50a5f7f57` (the fix) and `73a1b0b33` (status file), both pushed.
No `.git/index.lock` contention this wave.

Re-measured after: `TALLY  CLEAN 3158  DIRTY 6  ORPHANED 0  NEVER ENTERED 290`
— 290 = 298 − 8 exactly, no concurrent-agent noise this wave either.
**290 NEVER ENTERED files remain**: `UtinniPatches` still at **73** (its
`Patches/` subfolder holds only the 1 unreviewed
`RUT_TarredSurgery_RecipeUsers.xml`), `SWBestiary` at **52**
(`Defs/ThingDefs_Races` has **50** left — still the single biggest live
cluster in either mod). Next wave: continue `SWBestiary/Defs/
ThingDefs_Races` alphabetically from `RSW_Kreetle.xml`, with
`list --show-untracked`.

## Wave 54 — 2026-09-24: SWBestiary races K-L, UtinniPatches/Patches/ closed out

Ran `list --show-untracked` fresh: **290 NEVER ENTERED**, matching wave 53's
ending tally exactly — no concurrent-agent noise this wave.

Picked the next 8 alphabetically-first files from
`SWBestiary/Defs/ThingDefs_Races/`: `RSW_Kreetle.xml`, `RSW_Krykna.xml`,
`RSW_Kwi.xml`, `RSW_Kybuck.xml`, `RSW_LavaFlea.xml`, `RSW_LongtailGorg.xml`,
`RSW_Lothcat.xml`, `RSW_Lylek.xml`, plus the last unreviewed
`UtinniPatches/Patches/` file, `RUT_TarredSurgery_RecipeUsers.xml`. Full-file
reviewed all 9, each race got the wave 49-53 sound-prefix check
(`sound{Wounded,Death,Call,Angry}`): 6 of 8 carry correctly RSW_-prefixed
sounds and resolve in `SoundDefs_SWBestiary.xml`; `RSW_Kybuck.xml` and
`RSW_Lothcat.xml` deliberately reuse bare vanilla `Pawn_Elk_*`/`Pawn_Cat_*`
clips per their own header comments — correct, not this bug class. Every
cross-referenced defName (bodies, body-part groups, leather/meat pairs,
eggs, abilities, a PawnRenderTreeDef for `RSW_Lylek`'s tentacle-spasm
animation, `canCrossBreedWith` targets `RSW_FrilledGorg`/`RSW_Gorg`) was
grepped and confirmed to resolve to a real def in the repo — 32 distinct
names checked, all present. Also ran an XML-tree duplicate-element scan
(the general form of wave 53's duplicate-`lifeExpectancy` bug class) across
all 8 race files — zero duplicate non-`<li>` elements found in any block.
`RUT_TarredSurgery_RecipeUsers.xml` matches its named sibling
(`BrainWormSurgery_RecipeUsers.xml`) shape exactly, and its
`RUT_ScrubTarred` target resolves in `RUT_Tarred_Surgery.xml` — no bugs.
**`UtinniPatches/Patches/` is now fully exhausted** (0 remaining, confirmed
in the wave's re-measurement below).

🔴 **One real bug found and fixed**: `RSW_LavaFlea.xml`'s PawnKindDef
`<abilities>` block wrapped `RSW_SW_Leap` in an outer
`MayRequire="Ludeon.RimWorld.Odyssey"`, while the inner `<li>` — and the
ThingDef's own `specialTrainables` entry for the same ability — both
correctly gate it on `Ludeon.RimWorld.Biotech` only (the file's own header
documents this explicitly: "Biotech-gated, NOT Odyssey"). An outer
`MayRequire` skips the whole node if unmet, so with Biotech active but not
Odyssey the ability would never wire into the PawnKindDef at all, silently
contradicting the ThingDef half of the same def pair. Fixed: removed the
outer `MayRequire`, leaving only the correct inner Biotech gate. Commit
`0c0282d70`.

Commits `0c0282d70` (the fix) and `487168757` (status file), both pushed.
Two transient `.git/index.lock` collisions with the concurrent
`SUMP_GASLIGHT_1` build agent, both cleared within 5-10s on retry per the
item's own protocol.

Re-measured after: `TALLY  CLEAN 3167  DIRTY 6  ORPHANED 0  NEVER ENTERED 281`
— 281 = 290 − 9 exactly, no concurrent-agent noise this wave either.
**281 NEVER ENTERED files remain**: `UtinniPatches` at **72**, all in
`Defs/`/`Languages/` (`Patches/` fully spent), `SWBestiary` at **44**
(`Defs/ThingDefs_Races` has **42** left — still the single biggest live
cluster). Next wave: continue `SWBestiary/Defs/ThingDefs_Races`
alphabetically from `RSW_Massiff.xml`, with `list --show-untracked`.

## Wave 55 — 2026-09-24: SWBestiary races M-O

Ran `list --show-untracked` fresh: **289 NEVER ENTERED**, 8 more than wave
54's ending 281 — concurrent-agent noise (other build work adding new
`UtinniPatches`/`SWBestiary` files mid-loop), not a regression in this loop.

Picked the next 8 alphabetically-first files from
`SWBestiary/Defs/ThingDefs_Races/`: `RSW_Massiff.xml`,
`RSW_MatureFleshbeast.xml`, `RSW_Mott.xml`, `RSW_Neebray.xml`,
`RSW_Nerf.xml`, `RSW_Nizzek.xml`, `RSW_Ollopom.xml`, `RSW_Orray.xml`.
Full-file reviewed all 8. Every cross-referenced defName was grepped and
confirmed to resolve to a real def in the repo: bodies (`RSW_Massiff`
bare-vanilla-parts, `RSW_TentacledQuadrupedEyeless`, `RSW_Neebray` reusing
Wave B's `RSW_SW_LeftWing`/`RSW_SW_RightWing`, `QuadrupedAnimalWithPaws`
and `QuadrupedAnimalWithHoovesAndHorn` vanilla Core, `RSW_Ollopom`,
`RSW_Orray`, vanilla `Bird` for `RSW_Nizzek`), leather/meat
(`RSW_Leather_Saurian`/`RSW_Saurian_Meat`, `RSW_Tender_Meat`,
`RSW_Silica_Meat`, `RSW_Leather_Nerf`/`RSW_Nerf_Meat`,
`RSW_Rodentia_Meat`, `RSW_Leather_Tough`/`RSW_Reptomammal_Meat`, plus
`RSW_Nizzek`'s deliberate vanilla `Leather_Panthera`/`useMeatFrom Cougar`),
new resources (`RSW_WoolNerf`, `RSW_NerfHorn`), abilities/trainables
(`RSW_SW_Spur`), `canCrossBreedWith` targets (`RSW_FeralNerf`,
`RSW_FeralGrazer`), and `RSW_Nizzek`'s own hatch wiring (confirmed
`RSW_Drazzik.xml`'s `CompHatcher` names `<hatcherPawn>RSW_Nizzek</hatcherPawn>`
correctly). Each race got the wave 49-54 sound-prefix check
(`sound{Wounded,Death,Call,Angry}`): `RSW_Massiff`, `RSW_Mott`,
`RSW_Neebray`, `RSW_Nerf` (repoints to `RSW_Pawn_FeralNerf_*`, matching its
own donor's verbatim reuse), and `RSW_Orray` all carry correctly
RSW_-prefixed sounds, all 4 fields present and all 4 confirmed to resolve
in `SoundDefs_SWBestiary.xml`; `RSW_Ollopom` deliberately reuses vanilla
Core `Pawn_Rodent_*` per its own header (not this bug class);
`RSW_MatureFleshbeast` deliberately keeps donor `AA_TarGuzzler_*` clips
live since Alpha Animals stays an active hard dependency for this batch
(same pattern, not this bug class); `RSW_Nizzek` carries no life-stage
sound fields at all (single-lifeStage hatchling, consistent with its
sibling `RSW_BrainWormKind`). Also ran the wave 54 XML-tree duplicate-
element scan across all 8 files (the general form of wave 53's duplicate-
`lifeExpectancy` bug class) — zero duplicate non-`<li>` elements found in
any block. No bugs found in any of the 8.

All 8 marked CLEAN, commit `8c44f08cc`, pushed. No `.git/index.lock`
contention this wave.

Re-measured after: `TALLY  CLEAN 3175  DIRTY 6  ORPHANED 0  NEVER ENTERED 281`
— 281 = 289 − 8 exactly, no further concurrent-agent noise mid-wave.
**281 NEVER ENTERED files remain**: `UtinniPatches` at **77** (up 5 from
wave 54's 72 — concurrent build-agent noise, all in `Defs/`/`Languages/`,
`Patches/` still fully spent), `SWBestiary` at **36** (`Defs/
ThingDefs_Races` has **34** left — exactly wave 54's 42 minus the 8
reviewed this wave, so `ThingDefs_Races` itself saw no concurrent-agent
noise; the 8-file gap between the wave-start tally (289) and wave 54's
ending tally (281) landed entirely in `UtinniPatches` and elsewhere in
`SWBestiary`, not in this cluster). Next wave: continue `SWBestiary/Defs/
ThingDefs_Races` alphabetically from `RSW_PekoPeko.xml`, with
`list --show-untracked`.

## Wave 56 — 2026-09-24: SWBestiary races P-S

Ran `list --show-untracked` fresh: **282 NEVER ENTERED** (1 more than wave
55's ending 281 — minor concurrent-agent noise, not a regression).

Picked the next 8 alphabetically-first files from
`SWBestiary/Defs/ThingDefs_Races/`: `RSW_PekoPeko.xml`, `RSW_Pikobis.xml`,
`RSW_Pufferpig.xml`, `RSW_Qormot.xml`, `RSW_Runyip.xml`, `RSW_SandLion.xml`,
`RSW_Scavrat.xml`, `RSW_ScrapNestBird.xml`. Full-file reviewed all 8. Every
cross-referenced defName was grepped and confirmed to resolve to a real def
in the repo: bodies (`RSW_FlyingAvian` for PekoPeko/ScrapNestBird,
`RSW_Pikobis`, `RSW_Qormot`, vanilla Core `QuadrupedAnimalWithHoovesAndTusks`/
`QuadrupedAnimalWithHoovesAndHorn`/`QuadrupedAnimalWithPawsAndTail` for
Pufferpig/Runyip/SandLion, `RSW_Scavrat`), leather/meat
(`RSW_Leather_Reptavian`/`RSW_Reptavian_Meat`, `RSW_Tender_Meat`,
`RSW_Leather_Reptomammal`/`RSW_Reptomammal_Meat`, vanilla `Leather_Light`,
`RSW_Pachydermoid_Meat`, vanilla `Leather_Panthera`/`Cougar`,
`RSW_Leather_SoftFur`/`RSW_Rodentia_Meat`, vanilla `Leather_Bird`), eggs
(`RSW_EggReptavianUnfertilized`/`RSW_EggPekopekoFertilized`,
`RSW_EggPikobisUnFertilized`/`RSW_EggPikobisFertilized`,
`RSW_EggScrapNestBirdFertilized`/`RSW_EggScrapNestBirdUnFertilized`, both
defined in the reviewed file itself and matching the comp's field names
exactly), body-part groups (`RSW_SWClaws`, `RSW_SWHornAttackTool`),
abilities/trainables (`RSW_SW_GoldForage`, `RSW_SW_Spur`, vanilla Odyssey
`Forage`), a C# comp (`RimMandrake.StarWars.SWBestiary.
CompProperties_ScrapHoarder`, confirmed live in
`Source/BeastMechanics/CompScrapHoarder.cs` alongside its
`JobGiver_HoardScrap.cs`/`JobDriver_HoardScrap.cs`), and the `RSW_ScrapNest`
nestDef target. Each race got the wave 49-55 sound-prefix check
(`sound{Wounded,Death,Call,Angry}`): `RSW_PekoPeko`, `RSW_Pikobis`,
`RSW_Qormot`, `RSW_Runyip` all carry correctly RSW_-prefixed sounds, all 4
fields present and confirmed to resolve in `SoundDefs_SWBestiary.xml`;
`RSW_Pufferpig` deliberately reuses vanilla Core `Pawn_Wildboar_*` plus one
already-ported `RSW_Pawn_Gullipud_Death` per its own header (not this bug
class, confirmed off the donor's own race block); `RSW_Scavrat` deliberately
reuses vanilla Core `Pawn_Rodent_*` per its own header; `RSW_SandLion`
carries no lifeStage sound fields at all (header documents this as
deliberate — unported donor sound defs, matching its sibling ports); and
`RSW_ScrapNestBird` deliberately reuses the already-ported
`RSW_Pawn_Whisperbird_*` set (a documented body/art/sound reskin of an
existing "ours" species, not a new absorption). Also ran the wave 54-55
XML-tree duplicate-element scan across all 8 files — zero duplicate
non-`<li>` elements found in any block.

🔴 **One real bug found and fixed, same class as wave 55's `RSW_LavaFlea`
fix**: `RSW_Pufferpig.xml`'s PawnKindDef `<abilities>` wrapper carried an
extra outer `MayRequire="Ludeon.RimWorld.Odyssey"` around the inner
`<li MayRequire="Ludeon.RimWorld.Royalty">RSW_SW_GoldForage</li>`.
`RSW_SW_GoldForage`'s own AbilityDef/TrainableDef pair (confirmed in
`RSW_MlieWaveC_Abilities.xml`) and the ThingDef's own `specialTrainables`
entry are both Royalty-gated only — so the outer Odyssey wrapper silently
dropped the whole `<abilities>` element, and the ability with it, for a
Royalty-only player with no Odyssey, contradicting the rest of the same def
pair's own gating. The file's own header comment had explicitly documented
this as "the donor's own gating quirk … preserved verbatim, not corrected" —
a deliberate choice by an earlier porting pass, not an oversight, but still
the identical functional bug wave 55 fixed elsewhere. Fixed: removed the
outer `MayRequire`, leaving only the correct inner Royalty gate. Also
corrected the matching stale comment in `RSW_MlieWaveC_Abilities.xml` (which
asserted the quirk was intentionally left uncorrected) so it no longer
describes a now-false state, per CLAUDE.md's "correctness outranks seat
ownership." Commit `cc3c45709`.

All 8 marked CLEAN, commit `35f451401`, pushed. No `.git/index.lock`
contention this wave.

⚠️ Editing `RSW_MlieWaveC_Abilities.xml`'s stale comment (it was CLEAN since
2026-09-18) put it back to DIRTY per the tool's own by-design behavior — a
single edit after `mark-clean` always does. Left DIRTY rather than folded
into this wave's mark-clean batch, since only a two-line comment correction
was reviewed there, not the whole file; it is now normal review debt for a
future wave alongside the pre-existing 6 DIRTY files (now 7).

Re-measured after: `TALLY  CLEAN 3182  DIRTY 7  ORPHANED 0  NEVER ENTERED 274`
— 274 = 282 − 8 exactly, no concurrent-agent noise this wave.
**274 NEVER ENTERED files remain**: `UtinniPatches` at **75**, `SWBestiary`
at **28** (`Defs/ThingDefs_Races` has **26** left). Next wave: continue
`SWBestiary/Defs/ThingDefs_Races` alphabetically from `RSW_Scurrier.xml`,
with `list --show-untracked`.

## Wave 57 — 2026-09-24: SWBestiary races Sc-Sk

Ran `list --show-untracked` fresh: matched wave 56's ending 274 (no
concurrent-agent noise at wave start). Confirmed `RSW_Scurrier.xml` still
the alphabetically-first NEVER ENTERED file in `SWBestiary/Defs/
ThingDefs_Races/` (26 files there, unchanged) — wave 56's pointer held.

Picked the next 8 alphabetically-first files: `RSW_Scurrier.xml`,
`RSW_Shaak.xml`, `RSW_ShadeWhale.xml`, `RSW_Shiro.xml`,
`RSW_ShiroTrap.xml`, `RSW_ShrublandGiant.xml`, `RSW_Shyrack.xml`,
`RSW_Sketto.xml`. Full-file reviewed all 8. Every cross-referenced defName
was grepped and confirmed to resolve to a real def in the repo: bodies
(`RSW_Scurrier`/`RSW_Shaak`/`RSW_ShiroTrap`/`RSW_Shyrack` new this wave in
`RSW_MlieWaveC_Bodies.xml`; `RSW_ShadeWhale` reuses already-ported
`RSW_Horax`; `RSW_Shiro` uses vanilla Core `TurtleLike`; `RSW_ShrublandGiant`
reuses `RSW_Dewback` — cross-checked against `RSW_Fambaa.xml`'s own header,
which documents Fambaa itself repointing to Dewback's body plan, so
ShrublandGiant's header claim "same body as Fambaa" and its literal
`<body>RSW_Dewback</body>` are consistent, not a mismatch; `RSW_Sketto`
reuses already-ported `RSW_Bogwing`), leather/meat (`Leather_Light`/
`RSW_Rodentia_Meat`, `Leather_Plain`/`RSW_Pachydermoid_Meat`,
`RSW_Leather_Horax`/`RSW_Saurian_Meat`, `RSW_Leather_Testudine`/
`RSW_Saurian_Meat` shared by Shiro+ShiroTrap, `RSW_Leather_Fambaa`/
`RSW_Gorg_Meat`, `RSW_Leather_Dark`/`RSW_Insectile_Meat`, vanilla
`Leather_Lizard`/`RSW_Reptavian_Meat`), eggs (`RSW_EggShiro{,Un}Fertilized`
shared by Shiro+ShiroTrap per both files' own header claim of shared
symbiote eggs, `RSW_EggShyrack{,Un}Fertilized`), `canCrossBreedWith`
(`RSW_Shiro`<->`RSW_ShiroTrap`, both directions confirmed), an ability/
trainable pair (`RSW_SW_SwarmCall`, both `Shyrack`'s ThingDef
`specialTrainables` and PawnKindDef `abilities` correctly single-level
`MayRequire="Ludeon.RimWorld.Odyssey"` — matches the AbilityDef/TrainableDef's
own gating in `RSW_MlieWaveC_Abilities.xml`, NOT the wave 55/56 double-
MayRequire bug class), and 4 CreatureBehaviors C# extension/comp classes new
to this wave's review (`RM_ShadeSeekingWanderExtension`,
`RM_FilterFeedExtension`, `RM_CompProperties_DungSeeder` on `RSW_ShadeWhale`;
`RM_ParentalEnrageExtension`/`RM_CompProperties_ParentalEnrage` on
`RSW_ShrublandGiant`) — read each class's actual C# field declarations and
confirmed every XML field name used (`intervalTicksRange`, `minShadeToSeed`,
`dungFilthDef`, `seedPlants`, `feedTerrainDefNames`, `beginBelowFoodPercent`,
`triggerRadius`, `guardianSearchRadius`, etc.) matches exactly, no
key-mismatch bugs. Each race got the wave 49-56 sound-prefix check
(`sound{Wounded,Death,Call,Angry}`): all 6 sound-bearing races
(`Scurrier`/`Shaak`/`Shiro`/`Shyrack`/`Sketto` plus `ShadeWhale`'s reused
`Horax` set) carry correctly RSW_-prefixed sounds, all 4 fields present and
confirmed to resolve in `SoundDefs_SWBestiary.xml` (`Sketto`'s own header
flags all 4 fields deliberately pointing at the same `RSW_Pawn_Sketto_Call`
clip — verified true off the donor's own race block, not a typo).
`RSW_ShiroTrap`'s own header flags a deliberately-unfixed dangling
cross-reference (`butcherBodyPart.thing` = bare donor `RawTookeTrapRoot`,
out of scope per the item's own "not-yet-ported dependency" tolerance) —
confirmed the flag is accurate and left it, not this wave's job. Also ran
the wave 54-56 XML-tree duplicate-element scan (Python, non-`<li>` elements
per parent) across all 8 files — zero duplicates found in any block. No
bugs found in any of the 8.

All 8 marked CLEAN, commit `1f0ffd7ca`, pushed. One transient
`.git/index.lock` collision with a concurrent agent, cleared on retry
within seconds per the item's own protocol.

Re-measured after: `TALLY  CLEAN 3184  DIRTY 13  ORPHANED 0  NEVER ENTERED 266`
— 266 = 274 − 8 exactly, no concurrent-agent noise mid-wave (DIRTY rose
274→7→13 between wave 56's end and this wave's start/end from unrelated
concurrent build work, not this loop's doing). **18 `SWBestiary/Defs/
ThingDefs_Races` files remain**: `RSW_Strill.xml`, `RSW_TeeMuss.xml`,
`RSW_TunnelSnake.xml`, `RSW_Urusai.xml`, `RSW_Uvak.xml`, `RSW_Varactyl.xml`,
`RSW_Voorpak.xml`, `RSW_Vornskyr.xml`, `RSW_WarWyrm.xml`,
`RSW_Whisperbird.xml`, `RSW_WompRat.xml`, `RSW_Woolamander.xml`,
`RSW_Worrt.xml`, `RSW_Wraid.xml`, `RSW_WraidAlpha.xml`, `RSW_Wyyyschokk.xml`,
`RSW_Yobshrimp.xml`, `RSW_Zakkeg.xml`. Next wave: continue
`SWBestiary/Defs/ThingDefs_Races` alphabetically from `RSW_Strill.xml`,
with `list --show-untracked` (re-derive the 266 count fresh, do not trust
it — this wave's own start count already showed the standard drift from
concurrent build agents).

## Wave 58 — 2026-09-24: SWBestiary races St-Vo

Ran `list --show-untracked` fresh: matched wave 57's ending 266 (no
concurrent-agent noise at wave start). Confirmed `RSW_Strill.xml` still the
alphabetically-first NEVER ENTERED file in `SWBestiary/Defs/
ThingDefs_Races/` (18 files there, unchanged) — wave 57's pointer held.

Picked the next 8 alphabetically-first files: `RSW_Strill.xml`,
`RSW_TeeMuss.xml`, `RSW_TunnelSnake.xml`, `RSW_Urusai.xml`, `RSW_Uvak.xml`,
`RSW_Varactyl.xml`, `RSW_Voorpak.xml`, `RSW_Vornskyr.xml`. Full-file
reviewed all 8.

**Found and fixed one real, high-confidence bug**: `RSW_TeeMuss.xml`'s
`CompProperties_Shearable` read `<woolDef>WoolCoarse</woolDef>` — bare
`WoolCoarse` is not a defName that exists anywhere in the repo (confirmed by
grep and by `infrastructure/state/facts/
mlie_creature_defname_map_wave_c.json`, whose own resources map records
`"WoolCoarse": "RSW_WoolCoarse"`); only `RSW_WoolCoarse`
(`RSW_MlieWaveC_Resources.xml`, ported Pass 6 for Mudhorn) exists. The
file's own header comment even says the resource was "already-ported
(RSW_WoolCoarse, Pass 6 Mudhorn) — left/renamed accordingly," so the intent
was clearly to use the renamed defName; the XML just didn't follow its own
comment. `RSW_Mudhorn.xml` (same resource, same wave) correctly uses
`RSW_WoolCoarse`, confirming TeeMuss was the outlier, not the convention.
Silent-failure class: `CompProperties_Shearable.woolDef` would resolve to
null at load with no error — a shearable animal that silently produces no
wool. Fixed to `RSW_WoolCoarse`, commit `1ef66c91c`, pushed.

Every other cross-referenced defName across all 8 files was grepped and
confirmed to resolve: bodies (`RSW_Strill`/`RSW_FlyingAvian` (Urusai)/
`RSW_Bogwing` (Uvak)/`RSW_Varactyl`/`RSW_Voorpak`/`RSW_Vornskyr` all new
this wave in `RSW_MlieWaveC_Bodies.xml`; `RSW_TunnelSnake` reuses
already-ported `RSW_Klorslug` — its two art-reuse claws
`RSW_SWLeftLegClawAttackTool`/`RSW_SWRightLegClawAttackTool` and its tail
`RSW_SWToxicAppendage` all confirmed present as `<groups>` entries on the
Klorslug BodyDef; `RSW_TeeMuss` uses vanilla Core
`QuadrupedAnimalWithHoovesAndHump`, bare per its own header), leather/meat
(`RSW_Leather_Mammavian`/`RSW_Mammavian_Meat` (Strill), vanilla
`Leather_Plain`/new `RSW_Cameloid_Meat` (TeeMuss), `RSW_Leather_Insectile`/
`RSW_Insectile_Meat` (TunnelSnake, reused from Klorslug's own resources),
`RSW_Leather_Reptavian`/`RSW_Reptavian_Meat` (Urusai/Uvak/Varactyl, Wave B),
`RSW_Leather_SoftFur`/`RSW_Felinoid_Meat` (Voorpak), vanilla `Leather_Wolf`/
`RSW_Tough_Meat` (Vornskyr)), eggs (`RSW_EggUrusai{,Un}Fertilized`,
`RSW_EggUvak{,Un}Fertilized`, `RSW_EggVaractyl{,Un}Fertilized`, all
confirmed present in `RSW_MlieWaveC_Resources.xml`), and the new
`RSW_SW_ForceFocus` AbilityDef+HediffDef+TrainableDef trio wired off
Vornskyr (`RSW_MlieWaveC_Abilities.xml`) — traced all three top-level Defs
and confirmed each carries a correct **single-level**
`MayRequire="Ludeon.RimWorld.Odyssey"` on the Def element itself (not the
double-nested bug class waves 55/56 found), matching the equally
single-level `<li MayRequire="Ludeon.RimWorld.Odyssey">RSW_SW_ForceFocus</li>`
wiring in both `RSW_Vornskyr.xml`'s PawnKindDef `<abilities>` and ThingDef
`<race><specialTrainables>`. Ran the sound-prefix check (wave 49+): all 7
sound-bearing races (`Strill`/`Urusai`/`Uvak`/`Varactyl`/`Voorpak`/
`Vornskyr`/`TunnelSnake`'s reused `Klorslug` set) plus the ForceFocus
ability's two sounds (`RSW_Ability_Force`/`RSW_Ability_ForceFocus_Warmup`)
all confirmed present in `SoundDefs_SWBestiary.xml`; `TeeMuss` deliberately
keeps vanilla `Pawn_Dromedary_*` per its own header, confirmed unchanged
from the donor. Also ran the wave 54+ XML-tree duplicate-element scan
(Python, non-`<li>` elements per parent) across all 8 files — zero
duplicates found in any block.

All 8 marked CLEAN, commit `d07130272`, pushed. One transient
`.git/index.lock` collision with a concurrent agent during the mark-clean
commit, cleared on retry within seconds per the item's own protocol.

Re-measured after: `TALLY  CLEAN 3192  DIRTY 13  ORPHANED 0  NEVER ENTERED 258`
— 258 = 266 − 8 exactly, no concurrent-agent noise this wave. **10
`SWBestiary/Defs/ThingDefs_Races` files remain**: `RSW_WarWyrm.xml`,
`RSW_Whisperbird.xml`, `RSW_WompRat.xml`, `RSW_Woolamander.xml`,
`RSW_Worrt.xml`, `RSW_Wraid.xml`, `RSW_WraidAlpha.xml`,
`RSW_Wyyyschokk.xml`, `RSW_Yobshrimp.xml`, `RSW_Zakkeg.xml`. Next wave:
finish `SWBestiary/Defs/ThingDefs_Races` (10 files, under one wave's usual
8-file batch plus 2 — either do all 10 in one wave or split 8+2) with
`list --show-untracked` (re-derive the 258 count fresh, do not trust it).
After that cluster closes, no other named cluster remains outstanding from
recent waves — re-survey `code_review_status.py list --show-untracked` for
the next NEVER ENTERED candidates (the 95-file `.cs` never-entered survey
from wave 14's post-tail note, largest cluster `CreatureBehaviors`, is
likely stale by now and should be re-derived, not trusted).

## Wave 59 — 2026-09-24: `SWBestiary/Defs/ThingDefs_Races` FINISHED

Ran `list --show-untracked` fresh: matched wave 58's ending 258 (no
concurrent-agent noise at wave start). Confirmed the 10 remaining files in
`SWBestiary/Defs/ThingDefs_Races/` were exactly `RSW_WarWyrm.xml` through
`RSW_Zakkeg.xml` alphabetically, unchanged from wave 58's pointer. Reviewed
all 10 in one wave (finishing the cluster outright, per wave 58's own
either/or note): `RSW_WarWyrm.xml`, `RSW_Whisperbird.xml`,
`RSW_WompRat.xml`, `RSW_Woolamander.xml`, `RSW_Worrt.xml`, `RSW_Wraid.xml`,
`RSW_WraidAlpha.xml`, `RSW_Wyyyschokk.xml`, `RSW_Yobshrimp.xml`,
`RSW_Zakkeg.xml`.

**Found and fixed 3 real defects across 3 of the 10 files:**

- **RSW_Zakkeg.xml** (silent-failure class, same shape as wave 58's
  TeeMuss bug): the adult lifeStage's `soundWounded`/`soundDeath`/
  `soundCall`/`soundAngry` all named bare `Pawn_Boma_*` — confirmed byte-
  identical to the donor's own XML (`vendor/mod_sources/
  StarWarsAnimalCollection_src`), where it resolved fine because the
  donor's own Boma sounds are also bare/unprefixed. But this repo's own
  absorption pass renamed those SoundDefs to `RSW_Pawn_Boma_*`
  (`SoundDefs_SWBestiary.xml`) without updating Zakkeg's cross-reference,
  so all four fields resolved to nothing at load — a silent null SoundDef,
  no error logged (confirmed the bare form doesn't exist anywhere in the
  repo). A prior pass's header comment had called this "ported byte-
  identical, pre-existing donor mismatch, not introduced here" — true of
  the wrong-species CHOICE, false of the resolution failure, which the
  port itself caused. Fixed to `RSW_Pawn_Boma_*` (all 4 confirmed to
  exist); left the wrong-species sound choice itself alone, since that part
  really is the donor's and not this loop's call to invent new
  Zakkeg-specific sounds. Corrected the header comment to say so.
- **RSW_WarWyrm.xml**: `statBases` carried a duplicate
  `ToxicResistance`/`ToxicEnvironmentResistance` pair (identical values
  both times, `1`/`1.0` — a copy-paste artifact, not a value conflict;
  caught by the standing wave 54+ XML-tree duplicate-element scan, the
  first real hit that scan has produced across waves 54-59). Removed the
  redundant second pair.
- **RSW_Wraid.xml**: `tradeTags` carried `AnimalUnommon` — confirmed the
  exact typo in the donor's own source (`vendor/mod_sources/
  StarWarsAnimalCollection_src`, faithfully ported) and the only
  occurrence of that string anywhere in the repo, against 35 files' worth
  of correctly-spelled `AnimalUncommon`. tradeTags don't need to resolve
  to a def (they're plain strings a `ThingSetMaker` filter matches against),
  so this doesn't break loading, but it does mean this creature silently
  never matched the "uncommon animal" trade category. Fixed to
  `AnimalUncommon`.

Every other cross-referenced defName across all 10 files was grepped and
confirmed to resolve: bodies (6 new BodyDefs in `RSW_MlieWaveC_Bodies.xml`
for `WarWyrm`/`Worrt`/`Wyyyschokk`/`Zakkeg`/`YobshrimpLand` plus reused
`RSW_FlyingAvian` (Whisperbird), `QuadrupedAnimalWithPaws`/`Monkey` vanilla
Core (WompRat/Woolamander), and `RSW_Dewback` reused by both Wraid and
WraidAlpha per the donor's own def), leather/meat (`RSW_Leather_Dark`/
`RSW_Silica_Meat` (WarWyrm), vanilla `Leather_Bird`/`RSW_Reptavian_Meat`
(Whisperbird), vanilla `Leather_Light`/`RSW_Rodentia_Meat` (WompRat),
vanilla `Leather_Bluefur`/`RSW_Anthropoid_Meat` (Woolamander),
`RSW_Leather_Insectile`/`RSW_Gorg_Meat` (Worrt) and
`RSW_Leather_Insectile` again/no specificMeatDef (Wyyyschokk, vanilla
`useMeatFrom>Megaspider`), `RSW_Leather_Wraid`/`RSW_Saurian_Meat` (Wraid +
WraidAlpha, shared), `RSW_Leather_Crustapod`/`RSW_Crustapod_Meat`
(YobshrimpLand), `RSW_Leather_Zakkeg`/`RSW_Saurian_Meat` (Zakkeg)), eggs
(`RSW_EggWorrtFertilized`/`UnFertilized`, `RSW_EggWraidFertilized`/
`UnFertilized`, `RSW_EggWraidAlphaFertilized`/`UnFertilized` (new this
file, self-contained ThingDefs), `RSW_EggWyyyschokkFertilized`/
`UnFertilized`, `RSW_EggYobshrimpFertilized`/`UnFertilized`, all confirmed
present in `RSW_MlieWaveC_Resources.xml`), a wool resource
(`RSW_WoolWyyyschokk`), abilities (`RSW_SW_Calamity` on WarWyrm,
`RSW_SW_SootheSong` on Whisperbird, `RSW_SW_WebShot` on Wyyyschokk — all
three confirmed single-level `MayRequire="Ludeon.RimWorld.Odyssey"`, not
the wave 55/56 double-nesting bug class), and sound-prefix checks (wave
49+) for all sound-bearing races. `RSW_WraidAlpha.xml`'s
`RM_CompProperties_HeatBurstPredator` (DESERT_BURST_PREDATOR_FLAGSHIP_1)
was cross-checked field-by-field against
`RM_CompProperties_HeatBurstPredator.cs`/`RM_CompHeatBurstPredator.cs` —
every XML field (`hediffDef`, `burstTriggerRangeCells`,
`heatFatigueSeverityThreshold`, `retreatShadeThreshold`,
`retreatSearchRadiusCells`, `checkIntervalTicks`) matches the C# exactly,
`RM_HeatDrivenBurst` hediff exists, and `RM_CreatureBehaviorsSettings.
heatDrivenBurstEnabled` resolves (two classes in one file,
`RM_CreatureBehaviorsMod.cs` — not a typo). `RSW_Whisperbird.xml` is a
flyer (`MaxFlightTime`/`FlightCooldown` stats,
`flyingAnimationFramePathPrefix`/`FrameCount`/`TicksPerFrame`,
`canFlyIntoMap`/`canLeaveMapFlying`) — confirmed correctly built per "if it
flies in the fiction, it flies in the game," not a finding. `RSW_Worrt.xml`
worrtling lifeStage's `swimmingGraphicData` points at the ADULT
`Worrt_Swimming` texture rather than the extracted `Worrt_j_Swimming` one —
checked against the donor's own XML and confirmed byte-identical to the
donor (not a porting bug, a faithful donor art-wiring quirk, left alone).
`RSW_Yobshrimp.xml`'s documented `YOBSHRIMP_DEFNAME_COLLISION_1` rename
(`RSW_Yobshrimp` -> `RSW_YobshrimpLand`, freeing the bare name for the
aquatic `SeaBeasts_Swarm.xml` pair) was independently re-verified: `RSW_
Yobshrimp` now resolves only inside `SeaBeasts_*` files, no lingering
reference to the land creature under the old name. Ran the wave 54+
XML-tree duplicate-element scan (Python, non-`<li>` elements per parent)
across all 10 files — only WarWyrm's hit above; WraidAlpha's 3 `ThingDef`
children under `<Defs>` are the expected shape (1 creature + 2 egg
ThingDefs, not a duplicate).

Fixes committed at `936acd7f7`, pushed. All 10 marked CLEAN, commit
`d7ed4ce2f`, pushed.

**This closes out every file in `SWBestiary/Defs/ThingDefs_Races/` — 0
remain DIRTY or NEVER ENTERED in that folder.**

Re-measured after: `TALLY  CLEAN 3202  DIRTY 13  ORPHANED 0  NEVER ENTERED 248`
— 248 = 258 − 10 exactly, no concurrent-agent noise this wave.

Next wave: no named cluster remains outstanding from recent waves — re-
survey `code_review_status.py list --show-untracked` for the next NEVER
ENTERED candidates. The 95-file `.cs` never-entered survey from wave 14's
post-tail note (largest cluster `CreatureBehaviors`, then `SWBestiary`,
`FlowWorks`, `EnvironmentalHazards`, `PyrelandsMechanics`, and smaller
clusters) is now roughly 10 waves stale and should be re-derived fresh via
that wave's own recipe (`<Compile Include>`/default-glob per `.csproj`,
`comm -23` against `list`'s path column), not trusted. The 13 never-entered
Python tools under `src/RimMandrake/Utils/` named in wave 14's post-tail
note also still need a reachability check before any of them are spent on
a review.
