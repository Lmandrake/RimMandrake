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
