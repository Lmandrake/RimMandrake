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

**Status: GimmeSomeSlack, IshkoDarkLandmarks, FlowWorks and Pyrelands are processed.** Graffiti,
Webwork, TheRot and BiomesComposite had not replied by the end of this pass. The driver is still
running, and each later reply needs the same pass.

## GimmeSomeSlack: 14 findings, 14 CONFIRMED, 0 FALSE, 0 STALE

GPT's headline claim that "11 shared compile inputs are absent" is **FALSE**. All 11 `_Shared`
files the csproj names exist in the repo; the package simply did not copy them.

| # | GPT sev → ours | verdict | where (current) | outcome |
|---|---|---|---|---|
| 1 | HIGH → MED-HIGH | CONFIRMED | `Source/Aerial/ConduitStylePicker.cs` `Patch_TryLink_Bridge` | **Fixed `fae484f5a`.** A pipe link now returns before `QueueLink` (`a.Kind != AerialLineKind.Power`). Before this, `RunOf` seeded on the pole plus the conduit next to it, so linking two pipe poles could repaint a separate electrical run. |
| 2 | HIGH → LOW-MED | CONFIRMED (reproduced in Python) | `Source/Aerial/AerialMath.cs:515,526` | **Open.** The fallen-wire clearance pass samples every 0.25, while the emission pass steps 0.1 then 0.25. GPT's case emits (23.03, 23.98) inside blocked cell (23,23). Fix: test clearance on the exact points pass 2 emits. This changes seeded geometry, so the fuzz fixtures and the digest must be re-baselined in the same change. |
| 3 | HIGH → MED | CONFIRMED (a documented trade-off) | `Source/Core/CordBuilder.cs:198,384`; `Source/SelfTest/GssFuzz.cs:383` | **Owner question Q3.** The C1 gap is accepted in the fuzz test, but the M4 north-star wording says "same polylines after load" with no exception. |
| 4 | HIGH → MED | CONFIRMED | `Source/Aerial/RM_FallenWireShock.cs:36` (`CheckInterval = 20`) | **Open.** A pawn walking at normal speed spends about 13 ticks per cell, so it can cross a contact cell between two checks. Fix: lower the interval to 5, or shock on cell entry. A live check is still owed. |
| 5 | MED | CONFIRMED | `Source/SectionLayer_RM_MessyCords.cs:131,149` (`continue` before the LOD block at 171); `validation.py:1346` (B12) | **Open.** A lifted swaying strand has no far-zoom representation. B12 passes on any strand's LOD. Fix: build the LOD ribbon before the two `continue`s, and make B12 count LOD pieces that belong to lifted strands. |
| 6 | HIGH-SUSPECT → LOW | CONFIRMED (a stale contract, not a mod bug) | `northstar/proof_all.py` SL2; `Source/Aerial/RestringJob.cs:103` | **Fixed `fae484f5a`.** SL2 now allow-lists `JobDriver_RestringSpan`, which vanilla saves mid-job by class name, and the false comment is corrected. Whether 1.6 writes that `Class` attribute is UNVERIFIABLE-OFFLINE. |
| 7 | MED → LOW-MED | CONFIRMED | `northstar/proof_all.py` `determinism()`; `northstar_matrix/run_live.py` | **Fixed `fae484f5a`.** D2 now fails on `extra != 0` and on an empty fresh read. New negative controls are in `northstar/selftest_proof_all.py` §10. |
| 8 | MED → LOW | CONFIRMED | `Source/RM_MapComponent_CordGraph.cs:870` | **Fixed `fae484f5a`.** A sway-preference change in a frame that already rebuilt is no longer lost. The flag is set every time, and the existing gate defers it by one frame. |
| 9 | MED → LOW | CONFIRMED | `Source/Aerial/CompPowerTap.cs:148-159` | **Open (design).** The whole 250-tick theft window is charged to the victim current at publish time, and a null victim drops it. Needs per-victim accumulators. |
| 10 | MED | CONFIRMED | `Source/Aerial/RM_MapComponent_Aerial.cs` | **Fixed `fae484f5a`.** There is now a `MapRemoved` override that destroys the span, fallen-wire and local-drop meshes. The live lifecycle count is still owed. |
| 11 | MED | CONFIRMED (perf) | `Source/Core/CordBuilder.cs:265-273,479` | **Open.** Each cached diving edge hashes the whole map. Fix: memoise one full-map signature per `Build`. The output does not change, so the determinism selftest covers it. |
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
| 1 | BLOCKER | CONFIRMED | `validation.py:57` (`suite.toggles = []`); no Source/ | **Owner question Q1.** This pure-XML pack has no settings, which goes against *"Every mod ships superb Mod Settings… no exceptions."* |
| 2 | HIGH → MED | CONFIRMED | `Defs/LandmarkDefs_IshkoDark.xml` (Cold Lava Tube had `<LavaCaves>0.4</LavaCaves>`; Odyssey: "Small lava-filled cave networks") | **Fixed `bf28588c1`.** Removed, because the description says "long since gone out… claimed cold". |
| 3 | HIGH → LOW | CONFIRMED | `validation.py` placement cleanup | **Fixed `bf28588c1`.** `_restore()` removes the landmark and every mutator the add introduced, re-adds any it displaced, then reads the tile back. An unverified restore FAILs. The add is now inside the protected block. (Severity is LOW: the quicktest world is disposable.) |
| 4 | HIGH → MED | CONFIRMED | `About/About.xml` (the art mod was only `loadAfter`) | **Fixed `bf28588c1`.** `mandrake.rut.ashkarrlandmarkart` is now a `modDependency`. |
| 5 | MED → LOW | CONFIRMED, by design | `validation.py` placement | **Kept.** This is forced authoring (the owner's hand), not a legality claim. Validity is recorded, and the code now says so. |
| 6 | MED | CONFIRMED | `validation.py` `_candidate_tiles` | **Fixed `bf28588c1`.** Candidate tiles must carry none of the three anchors. Mock tile 2 carries Hollow and is skipped. |
| 7 | MED | CONFIRMED | `validation.py` defs chain | **Fixed `bf28588c1`.** It now asserts anchor chance == 1 and the exact `iconTexturePath` from our XML. |
| 8 | MED | CONFIRMED | `northstar_plan.py` mock (every optional at 0.2) | **Fixed `bf28588c1`.** The mock parses the Defs XML, rolls one optional deterministically so the restore is exercised, and has a new `no_restore` break. |
| 9 | MED-SUSPECT | CONFIRMED that no geometry backs the names | Defs descriptions vs Hollow/Chasm anchors | **Owner question Q2.** |
| 10 | MED → LOW | CONFIRMED | stored run JSON | **Partly fixed.** The new restore and placement records keep before/after state. The running-package identity in the record is still open. |
| 11 | LOW | CONFIRMED | `validation.py` source chain (`return` inside the first `with`) | **Fixed `bf28588c1`.** Both components are now declared under declaration probing. |

Mock after the fixes: GREEN 8/8. Each break is red: `wrong_pkg` 1 FAIL, `no_anchor` 3 FAIL, `shallow` 3 UNMEASURED, `no_restore` 3 FAIL. 🔴 **The 2026-10-07 GREEN is now at an old hash.** Re-running it costs one 22 s minimal-list `ishko` sitting.

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

## Pyrelands

(Written from the verifier's report below. The two FlowWorks loose ends follow it.)

## Loose ends from other helpers

- **`selftest_hose_port.py` P9, 24 vs 22 credit sites: REAL drift, not stale.** `Source/SelfTest/TransferChecks.cs` `CreditTags` gained "credit site: pump overflow spill" and "credit site: gravity overflow" in `1da459a0d` (09:54, overflow stages 2-3). The python mirror `CREDIT_SITES` stayed at 22. Another helper re-synced the mirror in `37f064ef7` (16:36). `selftest_hose_port.py` now passes (0 failing).
- **`carry_tanks` "pump piped to a tank" with no pipe: REAL.** A tank is reached only through a network (`RM_LiquidNet.TanksFor` → `Store(origin)`). The pump at (3,6) and the tank at (8..9,6..7) shared none, so the pump read "no tank". `pump_pour` had the same layout. **Fixed `70ebe9720`**: an `RM_UniversalPipe` run at x 4..7, z 6 on both stations (`selftest_review_map.py` ok, 88 stations). 🔴 Review saves already frozen from the old layout still lack the pipe.

## Validation efficiency advice

These are ranked by the wall-clock time they save per acceptance cycle. The estimates are ours, not measured.

| rank | suggestion (source) | saving | verdict |
|---|---|---|---|
| 1 | **Find fixture bugs offline before taking the bridge.** Check component membership on the exact fixture graph (FW E.1). The 200-rig tank fixture and `carry_tanks` both had no hydraulic path; each would have wasted a live sitting. | a whole sitting (15–60 min) per bad fixture | **Adopt now.** Add a `review_map`/fixture check: every pump station has a network path to its tank (a pure python graph walk over `build=`). |
| 2 | **Never spend a dedicated cold load on a small mod.** Attach Ishko and other XML packs to the next canonical full-list sitting (Ishko E.4, GSS E.3, FW E.4). | ~15 min per mod | **Adopt now.** This is already doctrine (`rimworld-load-round`); state it in each mod's walk. |
| 3 | **One minimal-list load, several maps.** One process with separate dry, river and stress maps, rather than several loads (FW E.2, GSS E.3 `fw_gss_sitting` riders). | 15–30 min | **Adopt now.** The `fw_gss_sitting` tier already exists; batch the GSS riders (pipe-link isolation, LOD membership, re-string save, shock crossings) into it. |
| 4 | **Reuse an offline receipt keyed to the complete input closure** (source + `_Shared` + XML/art + harness + spec hash), and run SelfTest once per fingerprint (GSS E.2, FW E.5). | 2–6 min per run, many runs a day | **Adopt later.** It needs a closure-hash definition. `--skip-offline` must stay a partial run, never a certification shortcut. |
| 5 | **Predicates that can fail.** Every PASS row gets a negative control in the selftest. Perf numbers become measurements, not PASS rows (`P1B`, levelling `msAvg`). B12 counts per strand (GSS D, FW #13). | prevents false GREENs that cost a re-run | **Adopt now, incrementally.** D2 is done (`fae484f5a`). B12, P1B and levelling `msMax` are listed open above. |
| 6 | **Bind evidence to identity:** source hash, DLL sha, running-list fingerprint and tier in every result, with readers rejecting mismatches (GSS E.5, FW #11, Ishko E.6). | prevents certifying on stale evidence | **Adopt later.** The assembly check in the FW core reader is small. The tier rule needs a contract. |
| 7 | **Merge duplicate rows:** B8+B12, D1+D2, and toggle rows as one ON→OFF→ON fixture (GSS E.4, FW E.5). | minutes per run | **Adopt later**, when those rows are next edited. |
| 8 | **Do not re-run green, unchanged scenes** (the theft day/stop scene) (GSS E.3). | 5–10 min | **Adopt now.** This is already the currency rule (fingerprint, not timestamp). |
| 9 | **Use a disposable fixture, discarded or reloaded, instead of inverse cleanup** (Ishko E.2). | small | **Adopted for Ishko** as a verified restore (`bf28588c1`). Discard-and-reload stays the default for map-level work. |
| 10 | **Pre-registered structured result lines** such as `GSS_ACCEPT …` and `FW_ACCEPT row=… source=… dll=… running=…` (all three). | makes a sitting decidable by grep | **Adopt later**, as the shape for new rows. Do not rewrite the existing harnesses for it. |
| — | GPT's wall-clock budgets: GSS 41–54 min automated plus 10–15 owner; Ishko 15–25 (+15 if no shared full load); FW 2.5–4.5 h. | — | Informational; none is measured. |
| — | Ishko: three morphology maps to prove "lightless" or "overhang" geometry. | — | **Reject** unless the owner rules the names are physical promises (Q2). |
| — | Restoring the old 109-scene GSS matrix. | — | **Reject.** GPT agrees: keep the reduced matrix. |
| — | Replacing GREEN-FULL with a compatibility smoke test. | — | **Reject.** GPT also says not to; GREEN-FULL is the owner's bar. |

## Owner questions

**Q1. Ishko's landmarks have no Mod Settings, and the rule is "every mod, no exceptions."**

- (a) Add a small C# settings screen with a switch per landmark. *Buys:* rule compliance. *Costs:* a DLL for a pure-XML pack, and the switches would do almost nothing: players get a frozen world, so a landmark already in the save stays, and turning it "off" cannot remove it safely.
- (b) **Recommended:** rule that a content-only pack whose content lives in the shipped save is exempt. *Buys:* no fake switches. *Costs:* one written exception to a standing rule.
- (c) Put Ishko's switches on the composite's or the art mod's settings screen. *Buys:* one screen. *Costs:* the same near-meaningless switches.

**Q2. Are "Lightless Sink", "Shadowed Overhang" and "Cold" physical promises, or names and lore?**

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

GPT's other FlowWorks questions are left as they are in the reply and not pressed here:

- whether passive levelling should stop when a pump works;
- whether nonwater overflow carries every canal hazard;
- whether overflow appears in the composite walk.

Each is a design call to make when that feature is next touched.
