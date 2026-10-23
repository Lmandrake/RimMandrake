# GPT deep-review findings, 2026-10-22 (FOUNDRY helper)

Source replies: `D:\ClaudeWork\gpt_review_2026-10-22\<Mod>\GPT_REPLY.md`. Plan:
`design/RimMandrake/gpt_review_plan_2026-10-22.md`. Every GPT finding is evidence, not a fact.
Each row below was checked against the source at `origin/main` as of the fix commit, not the
package snapshot (built about 15:47). The verdicts are:

- **CONFIRMED**: the current code does what GPT says.
- **FALSE**: it does not.
- **STALE**: true in the snapshot, fixed since.
- **UNVERIFIABLE-OFFLINE**: it needs a running game.

"Fixed" names the commit on `origin/main`.

**Status: seven of eight are processed: GimmeSomeSlack, IshkoDarkLandmarks, FlowWorks, Pyrelands, Graffiti,
Webwork and TheRot.** BiomesComposite's consult started at 17:33 and had not replied by the end of this pass; it needs
the same treatment. The driver is still
running, and each later reply needs the same pass.

## GimmeSomeSlack: 14 findings, 14 CONFIRMED, 0 FALSE, 0 STALE

GPT's headline claim that "11 shared compile inputs are absent" is **FALSE**. All 11 `_Shared`
files the csproj names exist in the repo; the package simply did not copy them.

| # | GPT sev → ours | verdict | where (current) | outcome |
|---|---|---|---|---|
| 1 | HIGH → MED-HIGH | CONFIRMED | `Source/Aerial/ConduitStylePicker.cs` `Patch_TryLink_Bridge` | **Fixed `fae484f5a`.** A pipe link now returns before `QueueLink` (`a.Kind != AerialLineKind.Power`). Before this, `RunOf` seeded on the pole plus the conduit next to it, so linking two pipe poles could repaint a separate electrical run. |
| 2 | HIGH → LOW-MED | CONFIRMED (reproduced in Python) | `Source/Aerial/AerialMath.cs:515,526` | **Open.** The fallen-wire clearance pass samples every 0.25, while the emission pass steps 0.1 then 0.25. GPT's case emits (23.03, 23.98) inside blocked cell (23,23). Fix: test clearance on the exact points pass 2 emits. This changes seeded geometry, so the fuzz fixtures and the digest must be re-baselined in the same change. |
| 3 | HIGH → MED | CONFIRMED (a documented trade-off) | `Source/Core/CordBuilder.cs:198,384`; `Source/SelfTest/GssFuzz.cs:383` | **Owner question Q3.** The C1 gap is accepted in the fuzz test, but the M4 north-star wording says "same polylines after load" with no exception. |
| 4 | HIGH → MED | CONFIRMED | `Source/Aerial/RM_FallenWireShock.cs:36` (`CheckInterval = 20`) | **Fixed `fcf07424c`.** The interval is now 4. A pawn walking at normal speed spends about 13 ticks per cell, so it used to cross a contact between checks. The live phase-shift check is still owed. |
| 5 | MED | CONFIRMED | `Source/SectionLayer_RM_MessyCords.cs:131,149` (`continue` before the LOD block at 171); `validation.py:1346` (B12) | **Open.** A lifted swaying strand has no far-zoom representation. B12 passes on any strand's LOD. Fix: build the LOD ribbon before the two `continue`s, and make B12 count LOD pieces that belong to lifted strands. |
| 6 | HIGH-SUSPECT → LOW | CONFIRMED (a stale contract, not a mod bug) | `northstar/proof_all.py` SL2; `Source/Aerial/RestringJob.cs:103` | **Fixed `fae484f5a`.** SL2 now allow-lists `JobDriver_RestringSpan`, which vanilla saves mid-job by class name, and the false comment is corrected. Whether 1.6 writes that `Class` attribute is UNVERIFIABLE-OFFLINE. |
| 7 | MED → LOW-MED | CONFIRMED | `northstar/proof_all.py` `determinism()`; `northstar_matrix/run_live.py` | **Fixed `fae484f5a`.** D2 now fails on `extra != 0` and on an empty fresh read. New negative controls are in `northstar/selftest_proof_all.py` §10. |
| 8 | MED → LOW | CONFIRMED | `Source/RM_MapComponent_CordGraph.cs:870` | **Fixed `fae484f5a`.** A sway-preference change in a frame that already rebuilt is no longer lost. The flag is set every time, and the existing gate defers it by one frame. |
| 9 | MED → LOW | CONFIRMED | `Source/Aerial/CompPowerTap.cs:148-159` | **Open (design).** The whole 250-tick theft window is charged to the victim current at publish time, and a null victim drops it. Needs per-victim accumulators. |
| 10 | MED | CONFIRMED | `Source/Aerial/RM_MapComponent_Aerial.cs` | **Fixed `fae484f5a`.** There is now a `MapRemoved` override that destroys the span, fallen-wire and local-drop meshes. The live lifecycle count is still owed. |
| 11 | MED | CONFIRMED (perf) | `Source/Core/CordBuilder.cs:265-273,479` | **Fixed `8d5a37b9c`.** The whole-map corridor is hashed once per `Build`. The output is unchanged: SelfTest 753/753, including determinism. |
| 12 | MED → LOW | CONFIRMED (mechanically) | `Source/Aerial/SectionLayer_RM_AerialGround.cs:92` | **Open, low.** The aerial path has no overflow counter. Hitting the limit needs 100 or more full cords of one material in one section, which is practically unreachable. |
| 13 | MED | CONFIRMED (art gap) | `Source/Core/CordBuilder.cs:395` (`DivePlate(Water)` returns null) | **Open, art owed.** The owner said 2026-10-06: *"So we just need the water."* The water entry/exit plate is NONE art, so it qualifies for the art queue. No item exists yet. |
| 14 | LOW | CONFIRMED (reproduced) | `Source/Aerial/CompAerialAnchor.cs:459` | **Fixed `fae484f5a` (text).** The gizmo no longer promises "joins them all". The greedy solver is kept. |

Checkable claims from GPT's C, D and F sections:

- **CONFIRMED:** `review/COVERAGE.md` claimed the live proof covers the gravship flight, but M20d is a setting round trip only. **Fixed `fae484f5a`.**
- **CONFIRMED:** the walk doc said 33 stations; the live count is 31. **Fixed `fae484f5a`**: it now points at the live count.
- **CONFIRMED:** `ConduitStyleProbe.cs:228` makes an observational read force `cg.Rebuild()`. **Open.**
- **CONFIRMED:** `offline_gate()` never ran `selftest_proof_all.py`. **Fixed `fae484f5a`**; the gate is green with it.
- **CONFIRMED:** `P1B_perf_rebuild` passes on `lastRebuildMs > 0`. **Open.** It should be a measurement, not a PASS.
- **CONFIRMED but not wrong:** `CHANGELOG.md:7` names DLL `5e523c88…`, while the current DLL is different. The line itself says "a DLL whose hash differs… repackage", so it marks a repackage as owed (twice over after `fae484f5a`); it is not a false statement.
- **Owner cosmetic call:** fallen pipe ends use the electrical fray art.

Offline gate after the fixes: validation 9/9, matrix 58/58, selftest_proof_all ALL PASS, C# SelfTest 753/753 plus aerial 112/112.

## IshkoDarkLandmarks: 11 findings, 10 CONFIRMED, 1 CONFIRMED-but-by-design, 0 FALSE

| # | GPT sev → ours | verdict | where | outcome |
|---|---|---|---|---|
| 1 | BLOCKER | CONFIRMED | `validation.py:57` (`suite.toggles = []`); no Source/ | **Answered (Q1), and done:** a concept of the religion of the Nine, not a mod of its own. The three landmarks now live in Salvation Rites; see "Ishko: folded into Salvation Rites" below. |
| 2 | HIGH → MED | CONFIRMED | `Defs/LandmarkDefs_IshkoDark.xml` (Cold Lava Tube had `<LavaCaves>0.4</LavaCaves>`; Odyssey: "Small lava-filled cave networks") | **Fixed `bf28588c1`.** Removed, because the description says "long since gone out… claimed cold". |
| 3 | HIGH → LOW | CONFIRMED | `validation.py` placement cleanup | **Fixed `bf28588c1`.** `_restore()` removes the landmark and every mutator the add introduced, re-adds any it displaced, then reads the tile back. An unverified restore FAILs. The add is now inside the protected block. (Severity is LOW: the quicktest world is disposable.) |
| 4 | HIGH → MED | CONFIRMED | `About/About.xml` (the art mod was only `loadAfter`) | **Fixed `bf28588c1`.** `mandrake.rut.ashkarrlandmarkart` is now a `modDependency`. |
| 5 | MED → LOW | CONFIRMED, by design | `validation.py` placement | **Kept.** This is forced authoring (the owner's hand), not a legality claim. Validity is recorded, and the code now says so. |
| 6 | MED | CONFIRMED | `validation.py` `_candidate_tiles` | **Fixed `bf28588c1`.** Candidate tiles must carry none of the three anchors. Mock tile 2 carries Hollow and is skipped. |
| 7 | MED | CONFIRMED | `validation.py` defs chain | **Fixed `bf28588c1`.** It now asserts anchor chance == 1 and the exact `iconTexturePath` from our XML. |
| 8 | MED | CONFIRMED | `northstar_plan.py` mock (every optional at 0.2) | **Fixed `bf28588c1`.** The mock parses the Defs XML, rolls one optional deterministically so the restore is exercised, and has a new `no_restore` break. |
| 9 | MED-SUSPECT | CONFIRMED that no geometry backs the names | Defs descriptions vs Hollow/Chasm anchors | **Fixed (Q2 answered: principles).** The three descriptions now say what Ishko is drawn toward or away from, and claim no shade, roof or cold. |
| 10 | MED → LOW | CONFIRMED | stored run JSON | **Partly fixed.** The new restore and placement records keep before/after state. The running-package identity in the record is still open. |
| 11 | LOW | CONFIRMED | `validation.py` source chain (`return` inside the first `with`) | **Fixed `bf28588c1`.** Both components are now declared under declaration probing. |

Mock after the fixes: GREEN 8/8. Each break is red: `wrong_pkg` 1 FAIL, `no_anchor` 3 FAIL, `shallow` 3 UNMEASURED, `no_restore` 3 FAIL. 🔴 **The 2026-10-07 GREEN was at an old hash, and its package is now retired.** The checks now run inside Salvation Rites' suite, which needs one fresh minimal-list `rites` sitting (about 22 s).

## FlowWorks: 16 findings, 14 CONFIRMED, 1 STALE, 1 CONFIRMED-premise/UNVERIFIABLE

| # | GPT sev → ours | verdict | where (current) | outcome |
|---|---|---|---|---|
| 1 | BLOCKER | CONFIRMED (process gate) | `design/validation_walks/RimMandrake/FlowWorks.md` `state: DRAFT`, step 4 | **Owner revalidation** after the acceptance campaign. No code fix. |
| 2 | HIGH | CONFIRMED | `Source/Machinery/RM_Levelling.cs:132` (`OrderBy(id).Take(16)`), `:286` (`walked >= 60000`), `:322-326` (BFS runs before the `keyIndex` check) | **Open (design).** The 17th and later ends never get a link, and repeated ends each pay for a full walk. Fix: rotate the `Take` window and the component start by `st.cursor`, and memoise cell→body per cycle. This needs an adapter-boundary test (none exists). |
| 3 | HIGH | CONFIRMED | `Source/Sheet/RM_SheetFire.cs` Detonation branch | **Fixed `c963216c2`.** Past the blast cap the puddle is no longer consumed; it stays lit and explodes on a later check. |
| 4 | HIGH | CONFIRMED | `Source/RM_MapComponent_Excavation.cs:2681` (engine-off return) | **Owner question Q5.** With the depth engine off, existing sheets freeze. |
| 5 | HIGH → MED | CONFIRMED | `Source/RM_MapComponent_Excavation.cs` (`if (excavatedCells.Count > 0)`) | **Fixed `c963216c2`.** It also runs while any sheet is wet (interval test first). |
| 6 | MED | CONFIRMED | `Source/Sheet/RM_MapComponent_Sheet.cs` pawn loop | **Fixed `c963216c2`.** The mood guard now covers the SoakingWet thought only, so animals take toxins from poisoned spills. |
| 7 | MED → MED-LOW | CONFIRMED | `Source/Sheet/RM_MapComponent_Sheet.cs` `Classify` | **Fixed `c963216c2`.** A kind change calls `RM_SheetMath.WakeAround`. No kernel test: the wake lives in the component. |
| 8 | MED | CONFIRMED | `Source/Sheet/RM_MapComponent_Sheet.cs` `EnginePulse` early return | **Fixed `c963216c2`.** On a dry map, the last-dried cells get their mesh dirtied and path cost recalculated. A live path-cost read is still owed. |
| 9 | MED | CONFIRMED | `Source/LiquidTypes/Building_LiquidPump.cs:375` (`CanSupply`/`TryDebit` whole notch) | **Owner question Q6.** |
| 10 | MED → LOW-MED | CONFIRMED | `Source/RM_SheetMath.cs` sweep and `ReturnAndAbsorb` | **Fixed `c963216c2`.** A 0% door is sealed on both paths. New SelfTest case `Sheet_a_zero_percent_door_is_sealed`. |
| 11 | HIGH → MED | CONFIRMED | `validation.py:170-181`, `:934-949` | **Open.** The core reader ignores `env.assembly_sha256`, and neither reader checks `env.running_sha256`. The assembly check is small; the tier/list rule needs the per-tier contract. |
| 12 | HIGH | **STALE** | `northstar/pipe_levelling_perf_proof.py` | Fixed in `e94e48c89` after the snapshot. Rigs now join on an `RM_UniversalPipe` run. |
| 13 | MED → LOW-MED | CONFIRMED | `pipe_levelling_perf_proof.py:93` (`msMax` ignored); `SheetWaterChecks.cs:584` (the alloc test measures an asleep puddle) | **Open.** Add `msMax` and minimum-`moves` clauses, and an awake-puddle byte budget. |
| 14 | MED → LOW-MED | CONFIRMED | `northstar/extensions.py:1244` (`_dig_run` → `flowworks_excavation_drive`) | **Open, live.** "All off still digs" proves the engine path, not a colonist's designation→job. |
| 15 | MED-SUSPECT | premise CONFIRMED; consequence UNVERIFIABLE-OFFLINE | `RM_MapComponent_Excavation.cs:3369` (`driverInputs` not saved) | Needs a live save/replay comparison. |
| 16 | LOW | CONFIRMED | `About/About.xml` | **Fixed `c963216c2`.** It no longer says four depths, propane "like a fuse", or headwater river gradient. |

Checkable claims from C, D and F:

- **CONFIRMED:** `TransferChecks` exercises fake legs plus a source regex, not `Building_LiquidPump`.
- **CONFIRMED:** `sheet_overflow_proof.py:623` watches the wet count, not the per-cell volume.
- **CONFIRMED:** the sheet overflow picture is a placeholder (`BaseContent.WhiteTex`).
- **CONFIRMED and conserving:** a hose can hold more than its nominal capacity (`RM_LiquidNet.FillRoutes`).
- **CONFIRMED:** sheet fire has no rain dousing (a NOT-built note).
- **STALE:** the pipe-pole "hostage to wires" item.

SelfTest after the fixes: sheet 37/37, stock 831/831, hose 158/158 and 375/375. The FlowWorks python selftests are 62/63 in the parallel sweep. The one red was `selftest_flowworks_stock.py` failing to BUILD under parallel build contention; it passes alone.

## Pyrelands: 20 findings, 19 CONFIRMED, 1 FALSE, 0 STALE

The only Pyrelands commit since noon, `533d21006` (15:26), predates the snapshot.

| # | GPT sev → ours | verdict | where (current) | outcome |
|---|---|---|---|---|
| 1 | BLOCKER → owed | CONFIRMED | `Defs/BiomeDefs/Pyrelands.xml:97-104` (`RM_SunHeatExtension` overhead +10 °C) | **Already planned.** `unified_direct_sun_heat_2026-10-19.md` lists Pyrelands for "drop all heat". It belongs to the shared migration, not a local fix. |
| 2 | MED-HIGH | CONFIRMED (latch sub-claim FALSE: the world is frozen) | `Source/PyrelandsTuning.cs` `DeepDesertBiomeDefNames` | **Fixed `f41f2eb9e`.** Added `RM_LongShade` and `RM_Stillsand`, the ruled successors (`biome_mod_architecture.md`), per the list's own "every plausible name" rule. |
| 3 | HIGH | CONFIRMED | `Source/MapComponent_BurnLine.cs` (`Measure()` ran only under `burnLineEnabled`) | **Fixed `f41f2eb9e`.** Burrowing and the furnace thermal cycle read `AnyBurn` under their own switches; with the burn line off they never saw a fire. |
| 4 | LOW-MED | CONFIRMED | `Source/Kernel/RM_FireEcoKernel.cs:318` | **Open (design).** A fruit can land on bare soil that never burned. The fix needs a "burned" test (`PyrelandsAshField.StampBurn`). |
| 5 | MED | CONFIRMED | `Source/Kernel/RM_BurnKernel.cs:198-216`; walk bar `Pyrelands.md:92-94` | **Owner question Q7.** |
| 6 | HIGH (journey) | CONFIRMED | `Defs/ThingDefs_Buildings/RM_StruckGlassRing.xml` (no CompStudiable); rite discovery "unbuilt" | **Owner question Q8.** |
| 7 | HIGH-MED | CONFIRMED | `northstar_site.py` fixture build | **Fixed `f41f2eb9e`.** The dict comprehension called `reload_fixture` (a `load_game`, budget 420 s) once per key: five loads where one was needed. **This is the biggest single wall-clock saving in this round.** |
| 8 | — | **FALSE** as stated | `validation.py:1629` | Vanilla's text is "Unrefrigerated, spoils in…", so `'rot'` does not match a fresh stack. The weaker residual is real: a vanished stack is not attributed to rot. LOW. |
| 9 | MED | CONFIRMED | `validation.py:1664-1682` | **Open.** The fire-hawk row passes without a NEW fire after the drop. Fix: wait for job end and require fire count above baseline, or a Fire instigated by the hawk. |
| 10 | MED | CONFIRMED | `validation.py:2109`; `debug_process.md` | **Open (harness).** modcheck has no INFERRED verdict, so the accepted inference policy cannot be expressed. |
| 11 | LOW | CONFIRMED | ember-drop and burrow job drivers | **Open, low.** A running job ignores its setting being switched off. |
| 12, 13 | LOW | CONFIRMED (12 self-disclosed) | `validation.py:1008`, `:1534` | **Open, low.** |
| 14 | MED | CONFIRMED (documented) | `preflight_pyrelands.py:438` fixture fingerprint = def names only | **Open.** Add the DLL sha and an XML hash (about 5 lines). |
| 15 | MED → LOW | CONFIRMED but deliberate | `preflight_pyrelands.py` gate C ("left in place") | **Kept.** Making a new `Mod_*.xml` FAIL would turn every first run of a newly loaded mod red. |
| 16 | MED | CONFIRMED | `preflight_pyrelands.py` `scan_log` | **Fixed `f41f2eb9e`.** Our own "patch FAILED" and "NOT FOUND" errors now refuse. |
| 17 | LOW-MED | CONFIRMED | `validation.py:1432` (`windSpeedFactor` alone can make cinderfall "differ") | **Open.** |
| 18 | LOW | CONFIRMED | `Source/RM_JobDriver_Burrow.cs:83` | **Open (perf).** `FireIsNear` runs every tick per burrower. |
| 19 | MED | CONFIRMED | `Source/PyrelandsFireFront.cs:107` | **Open.** Fire-front cadence is not in settings ("superb settings" rule); it is design work for the settings retrofit. |
| 20 | LOW | CONFIRMED | `Source/RM_StruckGlass.cs:79,99` | **Open.** Thin natural roofs pass the filter, and the last fallback ignores it. |

Checkable claims from C, D and F:

- **CONFIRMED:** there are 9 RM_ kinds inline. EmberGrass `FertilitySensitivity` is 0.15 and Quickgrass is 0.1.
- **CONFIRMED:** the trial plan's `shows=` coverage is 0/19, and it has 13 vanilla placeholders.
- **CONFIRMED (art hygiene, no action without the owner):** QuickgrassA and `_b` are byte-identical, and the root stage PNGs duplicate `Half/` and `Sprout/`. `FireHawk_Flying__east.png` is an orphan.
- **FALSE:** "trial plan budgets ash-ladder work" (line 150 says it is retired).
- **PARTIAL:** "requires retired Alpha Biomes" (line 260 only notes it cannot be excluded).

Selftests after the fixes: 5/5 (site, fruit_clear, review_map, fuzz, lint).

## Graffiti: 17 findings, 15 CONFIRMED, 1 partly FALSE, 1 partly STALE

No Graffiti finding was fixed by the two commits since noon. Those commits touched only comments and the csproj.

| # | GPT sev → ours | verdict | where (current) | outcome |
|---|---|---|---|---|
| 1 | BLOCKER | CONFIRMED | `Source/GraffitiJobUtility.cs:32`; `Source/Filth_Mark.cs:147` | **Owner question Q9.** Marks are filth on the floor cell beside the wall, and sigils print at `DrawPos`. Nothing puts them ON the wall. |
| 2 | HIGH | CONFIRMED (by engine read) | `Source/RaidExitTagger.cs:34` | **Open (design).** The prefix is on `ExitMapAndJoinOrCreateCaravan`, which a fleeing hostile raider does not reach. Fix: hook `Pawn.ExitMap` with a hostile check. The fuzz covers only the policy boolean. |
| 3 | HIGH | CONFIRMED | `Source/WorkGiver_PaintGraffitiDesignated.cs` | **Fixed `407de35f8`.** `ignoreJoyTimeAssignment = true`. Before this, `JoyTickCheckEnd` interrupted ordered marks during work hours. |
| 4 | MED | CONFIRMED, by design | Graffiti ships no ThoughtDefs ("mechanism only") | The content is in SacredGraffiti. GPT's G5 asks how broad Graffiti's own reactions must be (see Q9 notes). |
| 5 | MED | CONFIRMED | `Source/Designator_PaintGraffitiMark.cs` | **Fixed `407de35f8`.** The clicked cell itself must be standable against a cardinal wall; a wall merely "within radius" no longer counts. |
| 6 | MED | CONFIRMED | `Source/Filth_Mark.cs` `MakeMark`; driver | **Fixed `407de35f8`.** Rivals are destroyed only after the new mark exists. A null mark keeps the order and ends the job Incompletable. |
| 7 | MED | CONFIRMED | `validation.py:285,314` | **Open.** Variant coverage is random (`_REPEAT=3`). Pin variants with `Thing.overrideGraphicIndex` (GPT: `Graphic_Random.SubGraphicFor` honours it). |
| 8 | MED | CONFIRMED | `Source/JobDriver_PaintGraffiti.cs` | **Fixed `407de35f8`.** A work-giver job (`workGiverDef`, which is saved) whose order was cancelled paints nothing. |
| 9 | LOW-MED | CONFIRMED | `Defs/MentalStateDefs_Graffiti.xml:6` | **Open.** The spree break fires with painting off; it needs a settings-aware worker. |
| 10 | LOW-MED | CONFIRMED | `Source/BreachBiasHook.cs:104` | **Open.** The breach lure ignores the BreachGrid domain, and the "same gates" comment overstates. |
| 11 | LOW | CONFIRMED | `Source/GraffitiPool.cs:90`; SacredGraffiti Ishko mark has no `form` | **Open.** Small, in SacredGraffiti: `<form>Sigil</form>` or `poolWeight` 0, so a sacred mark is not a spree pick. |
| 12 | LOW | CONFIRMED, design | same-cell repaint every interval | Left as is. |
| 13 | LOW | CONFIRMED | `validation.py:95` (`.get("success", True)`) | **Open**, small. |
| 14 | LOW | CONFIRMED, but GPT's "demonstrably false docstring" is **FALSE** (no shipped def carries `breachLure`) | `validation.py:388` `_flip` has no `finally` | **Open**, small. |
| 15 | LOW | CONFIRMED | only the sigil is tinted by faction | **Open (design).** |
| 16 | LOW | CONFIRMED | `sigil_coverage.py` | **Fixed `407de35f8`.** Our own Defs failing to parse now fails the run. The game Data scan still skips unparseable vanilla files. |
| 17 | LOW | CONFIRMED (About has no Harmony dependency; the description is stale); 45-def count not re-checked | `About/About.xml` | **Open**, metadata. |

GPT's efficiency estimate: one minimal sitting (about 11 subtests, one save and reload, the gallery as the keeper save) plus one shared full-list load: 55–75 min in total. It would drop the Core-only launch and the stale expected failures.

## Webwork: 16 findings, 14 CONFIRMED, 2 UNVERIFIABLE-OFFLINE, 0 STALE

The three commits since the snapshot touched only `northstar_plan.py` and `validation.py`.

| # | GPT sev → ours | verdict | where (current) | outcome |
|---|---|---|---|---|
| 1 | HIGH → MED | CONFIRMED (def level) | `Defs/ThingDefs_Races/RM_Ollathrix.xml` (`AnimalFighter` trade tag; Core orbital and caravan traders stock it) | **Fixed `32d1d8caf`.** It is now `tradeability None`, like the other biome giants. |
| 2 | HIGH | CONFIRMED | `RM_Webwork_Gutter` is placed by no Source code, yet the junction and lance research depend on it | **Owner question Q10.** |
| 3 | MED | CONFIRMED (a known gap, `WEBWORK_MECHANICS_1`) | web-sense convergence unbuilt | Tracked; no new item. |
| 4 | — | CONFIRMED, owed | `Defs/BiomeDefs/RM_Webwork_Biome.xml:39-43` heat fields; `validation.py:314` asserts them | Part of the Direct Sun migration. Delete the assertion in the same change. |
| 5 | MED | CONFIRMED | `Source/RM_WebworkSiege.cs:188,414` (the fallbacks drop the `!ExposedAt` filter) | **Open.** It hangs on GPT's G1: is the light-moat a hard boundary? That is a design call to make at the siege's next sitting. |
| 6 | MED | CONFIRMED | `Source/RM_UrravethRemains.cs:147` (destroyed bones complete the site with chapters unread) | **Open (design).** GPT G2: what should happen when an unread bone is destroyed? |
| 7 | MED | CONFIRMED | Cable `killedLeavings` Hyperweave vs kit spec "beetle-destroyed web drops nothing" | **Open.** Two rulings disagree (force-break yields vs the kit spec). Confirm which one wins before deleting. |
| 8 | HIGH | CONFIRMED (GPT's line numbers off) | `validation.py` ProofSlick/ProofDoor/ProofBreak passed `""` = zero params (lesson 20261021T213508Z) | **Fixed `32d1d8caf`.** They now pass `"-"`. These three rows could never have reached their C# before. |
| 9 | LOW-MED | CONFIRMED | spin, cocoon and wrap `Wait` toils | **Fixed `32d1d8caf`.** Each wait now carries `FailOnCannotTouch(A, Touch)`. |
| 10 | MED | CONFIRMED (def) | Kollavane, Tavrosk and Brimlock lack `forceIsTree`; the siege tests `IsTree` | **Open.** Which species are canopy is a design call; the precedent is FeverWood and LeaningScrub. |
| 11 | LOW | CONFIRMED | `allowRivers` true vs "no surface water" | **Open.** It touches the world paint, so it waits for the paint-once pass. |
| 12 | LOW | CONFIRMED (negligible odds) | nest GenStep 160 random tries | Left as is. |
| 13 | MED | CONFIRMED | no `nestEnabled` switch for the egg-clutch relay | **Open.** The settings rule requires one; it is about 6 lines plus the screen. |
| 14 | LOW | CONFIRMED | `TakeYield` spends the cap before placement | **Comment corrected `32d1d8caf`.** The loss only happens on a failed Near-placement. |
| 15, 16 | LOW | UNVERIFIABLE-OFFLINE | map-local siege ledger; `CanPhysicallyPass` | Live only. |

- **Art (CONFIRMED):** there are three different `AB_Gomphoeria.png` copies (UtinniPatches, Webwork and Webwork StandIn). The egg clutch is `RockFlecked_Atlas` (placeholder), and the cocoon reuses limb-pile art. No action without the owner.
- **Mock run:** `--mock --mock-skip-site` gives 1 PASS / 11 FAIL / 75 UNMEASURED, identical to the 23:00Z run before these edits. The mock is red on its own and needs a pass; that is not caused here.
- **GPT's budget:** 65–100 min. It has two minimal starts (shipped defaults, then all-off at 4–7 min) and one shared full-list load batched with Sump, CreatureBehaviors and GravshipLanding.

## TheRot: 17 findings, 14 CONFIRMED, 2 CONFIRMED-by-design, 1 UNVERIFIABLE-OFFLINE

The `AA_AnimaColossus` removal (`1b82da72f`) staled no finding.

| # | GPT sev → ours | verdict | where (current) | outcome |
|---|---|---|---|---|
| 1 | MED-HIGH | CONFIRMED | `Source/RM_HwelgrueSwallow.cs` (holder `removeContentsIfDestroyed:false`; the cap's `Vanish` never reaches Downed or Killed) | **Fixed `292c84956`.** `PostDestroy` releases the passenger where the hwelgrue stood. |
| 2 | MED | CONFIRMED (partly) | retaliation ungated; digestion runs with the mod off | **Retaliation gated `292c84956`.** What all-off does to an existing passenger is GPT's question; our recommendation is to release them, to settle at the next Rot sitting. |
| 3 | MED | CONFIRMED, by design | `RM_LivingMatRoot.cs:111` (grown cells reset on respawn; the header says why) | Left as is. |
| 4 | MED-LOW | CONFIRMED | `RM_SwallowedCore.cs:95-122` (`claimChecked` set once; the fuzz invariant says the carrier never changes) | **Owner question Q11.** |
| 5 | — | CONFIRMED | `RM_LivingMatRoot` is dev-spawn only | GPT G1: how is the root earned? Design. |
| 6 | — | CONFIRMED | Rot generates on other players' worlds | Already tracked: `webworks_open_questions_2026-10-22.md:33`. |
| 7 | MED | CONFIRMED | draft bar 4: "36,000 ticks (1.5 days)" | **Fixed `292c84956`.** 1.5 days is 90,000 ticks, and the cost line is corrected. The draft is not yet hash-bound. |
| 8 | LOW | CONFIRMED (overstated: it doubles the warming rate; the ceiling holds) | `RM_LivingMatRoot.cs` room dedupe `at == now` | **Fixed `292c84956`.** One push per room per sweep interval. |
| 9 | — | UNVERIFIABLE-OFFLINE | lethal ship-weapon hit may skip the integrity change | Check the callback order with RimSage. |
| 10 | MED-HIGH | CONFIRMED | `RM_RegenerantVeil` alarm: no Rot race carries `RM_AlarmResponderExtension` | **Open (design).** The veil's defence answers no one: which species respond? |
| 11 | MED | CONFIRMED | `Swallowable` had no stockpile check (`Edible` did) | **Fixed `292c84956`.** It now matches draft bar 2. |
| 12 | LOW | CONFIRMED, by design | spore cloud slider governs nothing off the Rot | Cross-biome is unsupported by ruling. |
| 13 | LOW | CONFIRMED | Sheenblood unjoining yields 2 husks | **Open (small design).** |
| 14 | MED | CONFIRMED (recomputed: 48.5% small fauna) | `RM_TheRot_Biome.xml` roster | It goes on the Rot's review sheet; evictions are stopped. |
| 15 | LOW-MED | CONFIRMED | amber weeper ("poison dart") and tumrata ("keeps longer") descriptions vs a `RawFungus` yield | **Open.** Small text corrections. |
| 16 | MED | CONFIRMED | `validation.py:780` `or "spent True"`; `ProofRange` is tautological (`without = with / RangeFactor`) | **Open.** `spent True` may be a legitimate "already claimed" state, so it was not cut blind. `ProofRange` needs a stat read before and after unlinking. |
| 17 | MED (art) | CONFIRMED | Nogtyl A painted vs B flat cartoon in one random pool | Cosmetic change: the owner first. |

- **CONFIRMED:** a failed reveal in the Nav log still consumes an entry (`RM_NavigatorLog.cs:~62`).
- **CONFIRMED:** six byte-identical texture pairs share random pools.
- **CONFIRMED:** agaripods are comfortable down to -15 °C and Shambles to 0 °C. The Rot's cold ecology needs a design read.
- **GPT's budget:** 77–106 min, on two maps (R and a cold control) plus one shared full-list load.

## Loose ends from other helpers

- **`selftest_hose_port.py` P9, 24 vs 22 credit sites: REAL drift, not stale.** `Source/SelfTest/TransferChecks.cs` `CreditTags` gained "credit site: pump overflow spill" and "credit site: gravity overflow" in `1da459a0d` (09:54, overflow stages 2-3). The python mirror `CREDIT_SITES` stayed at 22. Another helper re-synced the mirror in `37f064ef7` (16:36). `selftest_hose_port.py` now passes (0 failing).
- **`carry_tanks` "pump piped to a tank" with no pipe: REAL.** A tank is reached only through a network (`RM_LiquidNet.TanksFor` → `Store(origin)`). The pump at (3,6) and the tank at (8..9,6..7) shared none, so the pump read "no tank". `pump_pour` had the same layout. **Fixed `70ebe9720`**: an `RM_UniversalPipe` run at x 4..7, z 6 on both stations (`selftest_review_map.py` ok, 88 stations). 🔴 Review saves already frozen from the old layout still lack the pipe.

## Validation efficiency advice

These are ranked by the wall-clock time they save per acceptance cycle. The estimates are ours, not measured.

| rank | suggestion (source) | saving | verdict |
|---|---|---|---|
| 0 | **Audit the harness for repeated expensive calls.** Pyrelands rebuilt every fixture with FIVE `load_game` calls where one was needed (#7); one grep for a bridge call inside a comprehension or loop found it. | up to 4 × (load + settle) per fixture, minutes each | **Adopt now. Done for Pyrelands (`f41f2eb9e`).** A one-line comprehension grep over `src/**/*.py` (2026-10-22) found no other instance. |
| 1 | **Find fixture bugs offline before taking the bridge.** Check component membership on the exact fixture graph (FW E.1). The 200-rig tank fixture and `carry_tanks` both had no hydraulic path; each would have wasted a live sitting. | a whole sitting (15–60 min) per bad fixture | **Adopt now.** Add a `review_map`/fixture check: every pump station has a network path to its tank (a pure python graph walk over `build=`). |
| 2 | **Never spend a dedicated cold load on a small mod.** Attach Ishko and other XML packs to the next canonical full-list sitting (Ishko E.4, GSS E.3, FW E.4). | ~15 min per mod | **Adopt now.** This is already doctrine (`rimworld-load-round`); state it in each mod's walk. |
| 3 | **One minimal-list load, several maps.** One process with separate dry, river and stress maps, rather than several loads (FW E.2, GSS E.3 `fw_gss_sitting` riders). | 15–30 min | **Adopt now.** The `fw_gss_sitting` tier already exists; batch the GSS riders (pipe-link isolation, LOD membership, re-string save, shock crossings) into it. |
| 4 | **Reuse an offline receipt keyed to the complete input closure** (source + `_Shared` + XML/art + harness + spec hash), and run SelfTest once per fingerprint (GSS E.2, FW E.5). | 2–6 min per run, many runs a day | **Adopt later.** It needs a closure-hash definition. `--skip-offline` must stay a partial run, never a certification shortcut. |
| 5 | **Predicates that can fail.** Every PASS row gets a negative control in the selftest. Perf numbers become measurements, not PASS rows (`P1B`, levelling `msAvg`). B12 counts per strand (GSS D, FW #13). | prevents false GREENs that cost a re-run | **Adopt now, incrementally.** D2 is done (`fae484f5a`). B12, P1B and levelling `msMax` are listed open above. |
| 6 | **Bind evidence to identity:** source hash, DLL sha, running-list fingerprint and tier in every result, with readers rejecting mismatches (GSS E.5, FW #11, Ishko E.6). | prevents certifying on stale evidence | **Adopt later.** The assembly check in the FW core reader is small. The tier rule needs a contract. |
| 7 | **Merge duplicate rows:** B8+B12, D1+D2, and toggle rows as one ON→OFF→ON fixture (GSS E.4, FW E.5). | minutes per run | **Adopt later**, when those rows are next edited. |
| 8 | **Do not re-run green, unchanged scenes** (the theft day/stop scene) (GSS E.3). | 5–10 min | **Adopt now.** This is already the currency rule (fingerprint, not timestamp). |
| 9 | **Use a disposable fixture, discarded or reloaded, instead of inverse cleanup** (Ishko E.2). | small | **Adopted for Ishko** as a verified restore (`bf28588c1`). Discard-and-reload stays the default for map-level work. |
| 9b | **Shorten clocks, don't wait them out** (Pyrelands E.11-13). Test the reseed, fresh-burn and spoil waits (120k, 102k and 270k ticks) on a shortened clock plus a read-back of the shipped constant, and record the shipped duration as INFERRED. | 30–75 min per long wait | **Adopt later.** It needs the INFERRED verdict in modcheck (Pyrelands #10); the policy already allows it (`debug_process.md`). |
| 10 | **Pre-registered structured result lines** such as `GSS_ACCEPT …` and `FW_ACCEPT row=… source=… dll=… running=…` (all three). | makes a sitting decidable by grep | **Adopt later**, as the shape for new rows. Do not rewrite the existing harnesses for it. |
| — | GPT's wall-clock budgets: GSS 41–54 min automated plus 10–15 owner; Ishko 15–25 (+15 if no shared full load); FW 2.5–4.5 h; Pyrelands 60–85 min. | — | Informational; none is measured. |
| — | Ishko: three morphology maps to prove "lightless" or "overhang" geometry. | — | **Rejected.** The owner ruled the names are principles (Q2). |
| — | Restoring the old 109-scene GSS matrix. | — | **Reject.** GPT agrees: keep the reduced matrix. |
| — | Replacing GREEN-FULL with a compatibility smoke test. | — | **Reject.** GPT also says not to; GREEN-FULL is the owner's bar. |

## Owner questions

**Q1. Ishko's landmarks have no Mod Settings, and the rule is "every mod, no exceptions."** ANSWERED 2026-10-22: *"Likely fold this mod into the religion mod of the 9. It's a concept, not a mod."* Then: *"I think the Nine Gods belong in Salvation Rites. They are NOT a general reuse mod."* Done: see "Ishko: folded into Salvation Rites" below.

- (a) Add a small C# settings screen with a switch per landmark. *Buys:* rule compliance. *Costs:* a DLL for a pure-XML pack, and the switches would do almost nothing: players get a frozen world, so a landmark already in the save stays, and turning it "off" cannot remove it safely.
- (b) **Recommended:** rule that a content-only pack whose content lives in the shipped save is exempt. *Buys:* no fake switches. *Costs:* one written exception to a standing rule.
- (c) Put Ishko's switches on the composite's or the art mod's settings screen. *Buys:* one screen. *Costs:* the same near-meaningless switches.

**Q2. Are "Lightless Sink", "Shadowed Overhang" and "Cold" physical promises, or names and lore?** ANSWERED 2026-10-22: *"I believe it's referring to principles that guide what he is drawn toward or away from."* The descriptions are reworded to match.

- (a) **Recommended:** names and lore over vanilla Hollow, Chasm and Cavern terrain. *Buys:* nothing to build; the lava contradiction is already removed. *Costs:* the names promise a little more than the map shows.
- (b) Physical promises: build shade or roof geometry and prove it. *Buys:* places that match their names. *Costs:* new generation code, three live maps, and a Direct Sun interaction.

**Q3. GSS determinism.** The M4 north-star bar says "same polylines after load". The code accepts a known gap (C1): an edit outside a cord's cached corridor can leave geometry that a fresh rebuild draws differently.

- (a) **Recommended:** reword M4 to "same polylines after load, except a strand re-planned after an edit outside its corridor". *Buys:* an honest bar at no code cost. *Costs:* your re-validation of the bar.
- (b) Widen the corridor margin to 7. *Buys:* the gap closes. *Costs:* the "unrelated edit re-plans only the touched edge" check fails, and that check would have to be relaxed.

**Q4. GSS water entry/exit art.** Diving into water has no plate art (*"So we just need the water."*). It is NONE art, so it can go to the art queue.

- **Recommended:** queue it. Say if you want a particular look first.

**Q5. FlowWorks: when the depth engine is switched off, existing surface spills freeze in place** (no soak, evaporation or run-back). New spills are already refused.

- (a) **Recommended:** keep the spills draining with the engine off, on their own timer. *Buys:* matches "existing spills keep draining (D7)". *Costs:* a small code change plus a live check.
- (b) Freeze them, and say so in the setting's tooltip. *Buys:* nothing runs while off. *Costs:* standing water that never goes away while off.

**Q6. FlowWorks: a natural pond's last <1,000 L cannot be pumped.** A dug channel can be pumped to the last decilitre.

- (a) **Recommended:** make ponds pump to the last decilitre too (the exact-dL routines already exist). *Buys:* one rule everywhere. *Costs:* small; one TransferChecks case.
- (b) Keep a wet, unpumpable remainder in natural ponds. *Buys:* a pond never quite empties. *Costs:* it differs from the channel route, unexplained.

**Q7. Pyrelands: the walk bar says a fresh map shows an active burn line with a scorched trail,** but the first front is armed 2–4 days in.

- (a) **Recommended:** start every fresh Pyrelands map with one small smouldering front. *Buys:* the bar is true at arrival, which is what you will see on a walk. *Costs:* a small code change and one live read.
- (b) Reword the bar to "within a few days". *Buys:* no code. *Costs:* your re-validation of the bar, and a first visit with nothing burning.

**Q8. Pyrelands: the Struck Glass ring can be fuelled, but nothing lets a colony discover or learn its rite** (no study comp; rite discovery is "unbuilt for every found rite").

- (a) **Recommended:** build rite discovery once, for every found rite. *Buys:* every found rite becomes reachable. *Costs:* a shared design item, not a Pyrelands fix.
- (b) Give the ring its own study comp now. *Buys:* this rite works sooner. *Costs:* one-off code that the shared system would replace.

**Q9. Graffiti: marks are painted on the floor cell beside a wall, not on the wall.** The north-star bar says "on walls".

- (a) **Recommended:** keep the mark on the floor cell, but record which side the wall is on and draw it offset and facing onto the wall face. *Buys:* it reads as wall art, with no new thing class. *Costs:* a render change plus your look in game.
- (b) Make marks a wall-attached thing. *Buys:* truly on the wall. *Costs:* a rewrite of placement, cleaning and going-over.

**Q10. Webwork: nothing places the Gutter any more,** but the gutter junction and the lance research both need one (the header says "Nothing places these three any more").

- (a) **Recommended:** have the web GenStep place one or two gutters on every Webwork map. *Buys:* the research and the junction become reachable again. *Costs:* small GenStep code plus one map read.
- (b) Retire the gutter and re-point the junction and the research at something that is placed. *Buys:* less content. *Costs:* a research-tree edit and losing the gutter's role.

**Q11. The Rot: when the navigator-core carrier leaves the world** (shipped off, killed off-map, or its ID goes stale), may another hwelgrue inherit the one core?

- (a) **Recommended:** yes. A stale carrier is released and the next hwelgrue that checks may claim it, so the unique item is never lost forever. *Costs:* the fuzz test's "the carrier never changes" invariant is rewritten.
- (b) No. That animal keeps it for good. *Buys:* a simpler rule. *Costs:* a world where the core can vanish with no sign (against "no animal or pawn ever vanishes without a readable sign").

GPT's Graffiti questions on content, left in the reply for the design sitting:

- whether F6 needs a literal bill window;
- whether the punk register is met;
- which provisional subjects are kept;
- how broad the base reactions must be.

GPT's other FlowWorks questions are left as they are in the reply and not pressed here:

- whether passive levelling should stop when a pump works;
- whether nonwater overflow carries every canal hazard;
- whether overflow appears in the composite walk.

Each is a design call to make when that feature is next touched.

## Ishko: folded into Salvation Rites (done 2026-10-22)

The owner said: *"Likely fold this mod into the religion mod of the 9. It's a concept, not a mod."* Then, by
question card: *"I think the Nine Gods belong in Salvation Rites. They are NOT a general reuse mod."*

What was done:

- The three LandmarkDefs now live in Salvation Rites (`mandrake.rut.rites`), in
  `src/RimUtinni/Rites/Defs/RUT_IshkoLandmarks.xml`. Both mods are RimUtinni, so the `RUT_` defNames stay as
  they are. No canonical Ash'karr save names any of the three; the 13, 14 and 19 old test saves that do still find
  them. (Measured 2026-10-22 with an exact `<def>NAME</def>` search of the Saves folder; the canonical saves do
  show `<def>Hollow</def>` and `<def>RUT_` entries, so the search can see them.) No save was edited.
- Salvation Rites now needs Odyssey and `mandrake.rut.ashkarrlandmarkart` (`modDependencies` and `loadAfter`).
- `mandrake.rut.ishkolandmarks` is retired. It is gone from the six maintained mod lists (the five
  `RULED_2026-10-20` lists and `FULL.LATEST`), and it is recorded as `RETIRED-MERGED` in the mod archive. The PAINT
  list did not carry Salvation Rites, so it now does, which keeps the landmarks available while painting.
- Its 8 checks are now the `ishko_source`, `ishko_defs` and `ishko_placement` chains in
  `src/RimUtinni/Rites/validation.py`, and the walk is a section of `design/validation_walks/RimUtinni/Rites.md`. The
  north-star plan is now `src/RimUtinni/Rites/northstar_plan.py`, and its mock covers the whole Rites suite: GREEN
  12/12, and each Ishko break still reads red. The `ishko` test tier is replaced by `rites`. The registry entry for
  the retired mod was removed (`forget_key`), so no GREEN is claimed for it.
- 🔴 **Not live-proven.** The 2026-10-07 GREEN was at the retired package and an old hash. The merged suite needs
  one fresh minimal-list `rites` sitting.
- **Mod Settings:** Salvation Rites has no settings screen (`suite.toggles = []`). Folding the landmarks in did not
  add one. Q1's gap is now a Rites question, and it closes if Ninefold moves in (option (a) below).
- The game's copy of `Mods\IshkoDarkLandmarks` still has to be removed at the next deploy. Only a dry run was made.

## Ninefold home (owner question, open)

His words also say *"the Nine Gods belong in Salvation Rites. They are NOT a general reuse mod."* The Nine Gods'
engine is Ninefold. Nothing about Ninefold has been moved: moving it is a bigger change and crosses a naming tier.

Facts, measured 2026-10-22:

- **What Ninefold is:** `mandrake.rm.ninefold` (`src/RimMandrake/Ninefold`), a RimMandrake (free tier) mod.
  It is the nine-god favour engine: 32 C# files in namespace `RimMandrake.Ninefold`, Harmony patches on colony
  events, a settings screen, and a self-test. `God.cs` hard-codes the Nine by name (Ishko … Ozzik).
  `Defs/RM_GodFavourTilts.xml` holds 20 `RM_Tilt_<God>_*` defs. Its only dependency is Harmony.
- **Who leans on it:**
  - **Salvation Rites already does.** `RUT_NineFaults.xml` guards its defs with
    `MayRequire="mandrake.rm.ninefold,…"`, and its worker classes are in Ninefold's DLL.
  - **Aftermath** (RimMandrake) reads it softly, by type name (`RimMandrake.Ninefold.GameComponent_Ninefold`),
    and lists it in `loadAfter` only.
  - **LuminousPigment** (RimMandrake) and **AftermathRites** (RimUtinni) list it in `loadAfter` only.
  - **Graffiti** (RimMandrake) carries a hook string that a RimUtinni pack reads.
  - It is in the DEV, TEST, AUTHORING and SHIP lists, but not PAINT.
- **Saves:** 18 of the 34 `CANONICAL_ASHKARR_START_*` saves contain
  `<li Class="RimMandrake.Ninefold.GameComponent_Ninefold">`, and 88 of the 420 saves name "Ninefold". No canonical
  save names an `RM_Tilt_` def. If the class's namespace or name changes, those saves need a type alias (C#
  back-compatibility). Otherwise they lose the Nine's favour state when loaded. No save may be edited.
- **The tier rule:** `design/NAMING_SCHEME_PLAN.md` asks of a RimUtinni mod: *"Does it name … the Nine?"* Ninefold
  does, in C# and in XML, so a RimMandrake packageId on it is a straddle. The 2026-09-08 card ruled "RM engine + RUT
  Salvation pack" (§7 item 1), but that split was never built. His new words, "NOT a general reuse mod", point the
  other way: one RimUtinni home. The consolidation plan (`design/MOD_CONSOLIDATION_PLAN.md`, R2 and R8) also keeps
  Ninefold as a RimMandrake engine, beside a planned RimUtinni `mandrake.rut.salvation` that would hold the nine mark
  styles, Ishko's landmarks and Rites.

Options:

- (a) **Recommended: fold Ninefold into Salvation Rites.** The Nine's engine and its content become one RimUtinni
  mod, `mandrake.rut.rites`. *Buys:* exactly his words. It ends the straddle, and Rites' `MayRequire` guards on
  Ninefold go away. Rites also gets Ninefold's settings screen, which closes Q1 for the landmarks too. One fewer
  packageId. *Costs:* the biggest move, about half a day plus one minimal-list sitting. Rites gains a DLL and a
  Harmony dependency. The namespace becomes `RimMandrake.Utinni.Rites`, with a type alias so the 18 canonical saves
  keep their favour state. The 20 `RM_Tilt_` defs become `RUT_` (no canonical save names them). Aftermath's
  type-name strings change. Three free-tier mods then point softly at a campaign mod, which is allowed through
  `loadAfter` only.
- (b) Make Ninefold its own RimUtinni mod (`mandrake.rut.ninefold`) beside Salvation Rites. *Buys:* an honest tier
  with the code kept apart. *Costs:* the same namespace, type-alias and save work as (a), but the Nine still live in
  two mods. That is not what "belong in Salvation Rites" says.
- (c) Build the 2026-09-08 split: keep a RimMandrake engine with no god names in it (gods read from data), and move
  the Nine into Rites as data. *Buys:* an engine another scenario could reuse. *Costs:* it contradicts "NOT a
  general reuse mod", and it is the largest C# rewrite, because the `God` enum runs through every patch.
- (d) Leave Ninefold where it is. *Buys:* nothing moves and nothing breaks. *Costs:* a free-tier mod keeps naming
  the Nine, against the tier rule and his words.

## Owner answers, 2026-10-22 evening (by question card; owner's words verbatim where quoted)

- Q1 Ishko settings: *"Likely fold this mod into the religion mod of the 9. It's a concept, not a mod."* Later: *"I think the Nine Gods belong in Salvation Rites. They are NOT a general reuse mod."* -> Ishko landmarks moved into Salvation Rites (done; live proof owed). Ninefold's own home is an OPEN owner question: see "Ninefold home".
- Q2 landmark names: *"I believe it's referring to principles that guide what he is drawn toward or away from."* -> lore only (descriptions already rewritten, 08fd00768).
- Q3 GSS M4: *"I don't value that the polylines are identical after load. Strike that."* -> done d8b98ae78.
- Q5 depth engine off: *"...have the depth engine change apply only upon reload ... We shouldn't be supporting live changes to the physics."* -> done d8b98ae78.
- Q6 ponds: pump to the last decilitre (card: option a). BUILD OWED.
- Q7 Pyrelands burn line: start every fresh map with a small smouldering front (option a). BUILD OWED.
- Q8 Struck Glass ring rite: *"We need to re-examine the rites and special items within each map. Many of them are somewhat fluff"* -> no rite-discovery build; see special-mechanics review.
- Q9 Graffiti: floor cell, drawn offset facing the wall (option a). BUILD OWED (needs his look in game).
- Q10 Webwork gutter: *"We need to review all of these special mechanics."* -> no placement build; see special-mechanics review.
- Q11 Rot core carrier: yes, the next hwelgrue may claim it (option a). BUILD OWED (rewrite the fuzz invariant).
