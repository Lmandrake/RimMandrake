# LanternDeeps offline validation, 2026-10-07 (FOUNDRY, uncommitted, no bridge)

## 1. Survey (4.5k lines, 15 files)
Chosen kernels, and why:
1. **Deep collapse warning machine** (RM_MapComponent_DeepCollapse in RM_AuroraCollapse.cs): three sets (`due` windows, `released`, `forced`) bridging vanilla's
   roof buffer and a Harmony prefix, with Scribed state, a setting that can switch it off mid-game, map-gen pass-through, galuush blasts that force falls, and a design
   promise (a propped roof holds; nothing falls without its warning). Pure bookkeeping once the engine calls are lifted out.
2. **Sipper glow-radius ledger** (RM_MapComponent_Sippers.Pass): a two-writer float accounting problem (the sippers dim a glower, the aurora's Apply rewrites it) that must
   give back exactly what it took and only if nobody else wrote since. Tolerance-gated writes make this the kind of arithmetic that drifts.
Rejected as kernels:
- RM_MapComponent_Creep / RM_CompCleave / RM_CompTapper / RM_CompPooler / RM_CompHush / RM_CompKnocker: each tick is a scan of map pawns/things and a placement or job start; the
  arithmetic left (caps 160/14, a cooldown, charge give/take) is a handful of lines and would be tested against a mock of the grid. Tapper charge (`min(capacity, charge+...)`, `give = min(charge, canAccept)`) is the closest and is two lines.
- RM_OrunGhal (tier thresholds, daily standing, lore at session N): small and linear; the thresholds are XML-driven.
- RM_WorkingDead, GenStep_* (scatter, flora gate, lanternstone rock), MapComponent_LanternDeepDarkness, DeepFloraRegrowth, DeepFloraPlanter, RM_HydrocarbonFauna/Wave2: map generation, light-grid and spawn calls.
- LanternDeepsMod (518 lines): settings UI.

## 2. Kernels + fuzz
Extracted (behaviour preserving except where noted below; call sites call the kernels, Scribe names unchanged; Verse-free so the net8 selftest compiles the production files):
- `src/RimMandrake/LanternDeeps/Source/RM_DeepCollapseKernel.cs`: `DeepCollapseState<T>` {due, released, forced; Window, Filter, Ripe, Resolve, EndRelease, PassThrough, DueAll, EnsureNotNull}.
  RM_MapComponent_DeepCollapse owns one (cells are IntVec3), Scribes `due`/`forced` as before, and plays the returned falls into the roof buffer; Patch_DeepCollapseWarning calls PassThrough.
- `src/RimMandrake/LanternDeeps/Source/RM_SipperLedgerKernel.cs`: `SipperLedger<G>` {Pass, AuroraWant}. RM_MapComponent_Sippers.Pass and RM_GameCondition_DeepAurora.Apply call it.
- Both added as `<Compile Include>` lines in `RM_LanternDeeps.csproj` (it turns default compile items off).
Real defects found by the extraction + fuzz, all FIXED in the kernels (each was reproduced by the fuzz first, shrunk to 3-6 actions):
1. **Sipper ratchet** (player-reachable): the "glow lost per sipper" slider goes down to 0.02. When the reduction was under the 0.05 change tolerance nothing was written, but the ledger
   still recorded the reduction, so when the sippers left the restore HANDED BACK light that was never taken: the radius ratcheted upward on every visit (def 5.0 -> 5.02 -> ..., and above the aurora's x1.75 ceiling). Now the reduction recorded is the difference actually left on the glower.
2. **Sipper entry dropped on despawn**: a glower that was dimmed and then unspawned (minified, carried) lost its ledger entry in the restore pass WITHOUT being restored, so it stayed dimmed (12.9 -> 11.4) when put down again. The radius is now restored whether or not it is spawned (it is only re-registered when spawned and lit).
3. **Stale `released` set**: after a fall the component re-runs vanilla's resolver and the prefix consumes `released`. When the prefix is skipped (collapse warnings switched off, map generation) the entries stayed forever and later waved an unrelated re-marking of that cell through with no warning. `EndRelease()` now clears leftovers after the resolver run.
4. **Stale `forced` marks** (Scribed, so they live in the save): a galuush blast marks cells forced and marks them to collapse; with warnings off (or in the save/load gap, the roof buffer is not saved) the filter never took them, so the forced mark stayed, grew with every blast, and made a later collapse of a rebuilt roof at that cell ignore its supports. Fixed two ways: Patch_DeepCollapseWarning's pass-through path calls `PassThrough(marked)` (drops forced and pending for cells vanilla collapses unwarned), and `EnsureNotNull()` (PostLoadInit) drops forced marks that are not pending.
Cleanup, not behaviour: `Patch_GateLanternstoneDeep.IsLanternstone` also tested defName `RUT_Lanternstone`, which exists nowhere under src/; the dead branch is removed (found by the lint).
Fuzz: `src/RimMandrake/LanternDeeps/Source/SelfTest/{LanternDeepsFuzz.cs,Program.cs,RimMandrakeLanternDeeps.SelfTest.csproj}`, wrapper `src/RimMandrake/Utils/selftest_lanterndeeps_fuzz.py`
(families collapse | sipper | units; knobs --fuzz-scale/--fuzz-seed/--fuzz-only).
Invariants:
- collapse (model: roofs, supports, vanilla's buffer and resolver with the prefix on/off): pending cells == model's, each with the deadline it was first given (re-marking never extends or shortens it);
  ripe == exactly the cells whose deadline passed; a ripe cell leaves `due` and `forced`; it falls iff roofed and (forced or unsupported), else is held; fell+held == ripe; with the prefix active NO cell collapses unless a Resolve released it
  (no unwarned collapse); `released` is empty outside a resolver run; every forced cell is pending or still awaiting the filter (never stale), and only after a blast; warnings off => DueAll then resolve; save/load keeps `due`+`forced` and drops the transient state.
- sipper (model: glowers with def radius, aurora toggles and Apply, resets, despawn/unlight, setting toggle, varying cells-per-sipper): radius stays within [0.25 x def, def x 1.75] and positive; a repeated pass over unchanged inputs changes nothing (no oscillation);
  a glower with sippers and no foreign write reads def minus the clamped reduction; after every sipper leaves, a glower only the ledger ever touched reads its def radius within 1e-3.
- units: knocker window (x1/x2/x1), re-mark keeps the deadline, aurora write rule.
Seeds: default 12,001 cases / 983k steps in 1.4 s; `--fuzz-scale 40`: 480,001 cases / 39.4M steps in 27 s, all green; replayed --fuzz-seed 7, 4242, 99991 green.
Mutations (each planted, caught, reverted; md5 of both kernels verified identical afterwards):
- M1 EndRelease does nothing (defect 3): collapse FAIL "released leftovers ... wave a later marking through unwarned" (4 seeds, 4 actions).
- M2 PassThrough keeps forced (defect 4): collapse FAIL "stale forced mark on cell 4" (3 actions).
- M3 reduction recorded as `red` (defect 1): sipper FAIL "glow radius 8.78 above the aurora's 8.75" and "5.02 vs def 5".
- M4 restore skips unspawned glowers (defect 2): sipper FAIL "reads 11.4, its def radius is 12.9" (6 actions).
- M5 re-mark moves the deadline: collapse FAIL "cell 5 deadline 5300 != 5900 (extended or shortened)".
- M6 forced no longer overrides support: collapse FAIL "(roofed, supported, forced) was held, expected fall".
- M7 held cell stays pending: collapse FAIL "resolved cell 6 is still pending".
- M8 ripe uses `<` not `<=`: collapse FAIL "ripe  != cells whose deadline passed".
- M9 Floor removed: sipper FAIL "glow radius -5.5" / "below the floor".
- M10 reload no longer drops stranded forced marks: collapse FAIL "stale forced mark on cell 6" after Blast+Reload.
Trap hit again: M10 first ran right after M9's restore and read M9's staged copy; sleep after the RESTORE as well as after the mutation (re-run alone it was caught).

## 3. Lint
`src/RimMandrake/Utils/selftest_lanterndeeps_lint.py` (selftest*.py, so run_selftests.py runs it): 31 XML class refs resolve; 84 field children are public fields of their class or a listed vanilla base (GenStep_ScatterGroup,
CompProperties, DeathActionProperties, ThinkNode_JobGiver tables; an unlisted vanilla base is counted as unverifiable and is 0 today); 20 .cs files == csproj Compile list; 64 RM_/RUT_/RSW_ literals resolve to a defName, tag, key,
class name (GetType().Name comparisons) or computed-key prefix; 14 Translate() keys exist in Keyed; DeepCollapseState's saved fields (`due`, `forced`) are Scribed under their own names and `released` stays transient; 60 Scribe calls with no
duplicated name per class; both kernels in the mod csproj + selftest csproj and free of Verse/RimWorld/UnityEngine/Harmony usings. Count 0 on any check fails the run.
Lint findings on the original tree: the dead `RUT_Lanternstone` defName (fixed by deleting the branch); 5 false positives of my own fixed in the lint (vanilla-base children, class-name and key-prefix literals).
Mutations (each caught, file restored): misspelled `<hearRadius>`; deleted the `forced` Scribe line; removed the kernel `<Compile>` from the mod csproj; `using Verse;` in the ledger kernel; renamed Keyed `RM_DeepCollapseWarning`;
broke a `<minSpacing>` tag (caught as an XML parse error).

## 4. Build
`python3 src/RimMandrake/Utils/winbuild.py src/RimMandrake/LanternDeeps/Source/RM_LanternDeeps.csproj`: 0 warnings, 0 errors, two `<Compile Include>` lines added. DLL + .srchash rewritten in the working tree, NOT committed (source stamp +dirty).
Not run in game; the live chains in validation.py (aurora_collapse, hydrocarbon_wave2/3) are the place to confirm the unchanged behaviour.

## Run
- `python3 src/RimMandrake/Utils/selftest_lanterndeeps_fuzz.py [--fuzz-scale 40] [--fuzz-seed N] [--fuzz-only collapse|sipper|units]`
- `python3 src/RimMandrake/Utils/selftest_lanterndeeps_lint.py`
