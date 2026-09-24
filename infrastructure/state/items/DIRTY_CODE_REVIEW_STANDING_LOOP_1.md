## the loop

Standing FOUNDRY full-file code-review loop, self-continuing. Pick a reachable file
not yet recorded CLEAN in `infrastructure/state/CODE_REVIEW_STATUS.json`, full-file
review it (never diff-scoped until it's CLEAN once), fix real bugs found, mark-clean
files with nothing significant found. Protocol: CLAUDE.md's "Code isn't clean until
a review says so" section.

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
