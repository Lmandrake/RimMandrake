# Hose port build log — 2026-10-11

Builder: BENCH subagent. Design: `design/RimMandrake/hose_port_to_flowworks_design_FINAL_2026-10-10.md` (f8fee03e4) over v2.
Item: `HOSE_REEL_MIGRATE_TO_FLOWWORKS_AT_LAST`. Step 9 skipped (Q3 needs owner yes).

## Owner rulings
- **Q7 (owner, typed 2026-10-11): "Yes, a tank would pass liquid on to a hose screwed into it, without a pump needed."** Replaces the Q7 default (no). Built at step 6 (tank<->hose coupling): a tank coupled to a laid hose feeds it directly, no pump; pipe runs still never merge through a tank (the BFS still stops at tanks; only the hose link leaves a tank).

## Owner defaults used (Q1-Q7)
- Q4a (art moves byte-for-byte during the pause): YES at step 2 -- 40 hose PNGs moved through the art ledger writer (40 installed, 40 retired, 0 owner-kept), no pixel changed.
- Q4b (reels without a picked look): FlowWorks' own `hose_defaultLook`, seeded once from GSS's global `style` (4-row LookOf table), else Scrapper (step 2).
- Q5 (build tab): RM_HoseReel moved Misc -> Production (step 2).
- Q1 (static liquid hose -> universal pipe): step 4. Q2 (hoses off carry nothing): step 6. Q3: not run (step 9 skipped). Q6 (no flow direction drawn): kept.
- Q7: replaced by the owner's ruling above.

## Increments
| # | status | sha | files | offline test |
|---|---|---|---|---|
| 0 | done | (see below) | FlowWorks/validation.py, FlowWorks/northstar/selftest_extensions.py | selftest_extensions PASS (+P12 adapter case; sanity: reverting the fix FAILs it) |
| 1 | done | (below) | _Shared/SlackGeometry/* (5 git mv + CordSig), _Shared/StylePicker/StylePickerCore.cs, GSS usings/csprojs/StylePicker/CordMaterials, 169 member decls public->internal | GSS SelfTest 871/871, hose 130/130, aerial 96/96 (identical to step 0); top-level-type gate PASS (23 decls); slice 20/20 GREEN |
| 2 | done | (below) | GSS Source/Hose/** + 3 defs + 40 PNGs (art ledger) + 4 whole selftest files + hose parts of 5 mixed ones -> FlowWorks; RM_HoseSettings section + import; HoseLook; RM_HoseLegacy(+Math) essentials/alias/import/old-GSS; HoseStyleProbe; Utils/validation_core.py; validation_hose*.py moved; validation_hose_offline.py; selftest_hose_port.py; walks; JawaBench playtest | FW SelfTest 140/140 + hose 278/278 (257 moved + 21 new); GSS SelfTest 614/614 (871 - 257 = 614, nothing lost); GSS proof_all --offline-gate red []; selftest_hose_port 18/18; selftest_extensions PASS; slice 24/25 (the 1 = pre-existing GSS#Cables screen check) |
| 3 | pending | | | |
| 4 | pending | | | |
| 5 | pending | | | |
| 6 | pending | | | |
| 7 | pending | | | |
| 8 | pending | | | |

## Deviations from design
- Step 2: the GSS human review map (GimmeSomeSlack/human_review.py) KEEPS its hose stations for now as cross-mod stations
  (they drive FlowWorks' HoseProbe, so the map is built on the flowworks tier, which carries both mods); its art board reads
  the hose art from FlowWorks' folder. Moving those stations into FlowWorks' own review tooling is step 8 harness work.
- Step 2: GSS AerialProbe census now reports its overhead queues; RL9 (FlowWorks) reads them by name, cross-mod, UNMEASURED
  when GSS is absent (design M3).
- Step 2: StyleStage3's clause "the reel is not in AerialStyles.StyledDefs" was dropped from the moved check (FlowWorks cannot
  see GSS); the same fact is enforced by selftest_hose_port P2 (no hose code left in GSS at all).
- Step 2 (not in the design, found on the way): bridgetools/JawaBenchGssPlaytest.cs compiled against GSS's hose and core
  types. It now references RimMandrakeFlowWorks.dll under extern alias `flowworks`, and both mods grant it
  InternalsVisibleTo (the shared geometry is internal). Compile-checked against the repo DLLs (build.py, no --apply);
  NOT deployed. build.py's dry stage used the wrong stage name (the -p:GssModDir override never resolved): fixed.
  ExplosiveKnockback's by-name hose hook repointed to FlowWorks' type names (flag renamed `Hoses`).
- Step 2: the GSS GPT-read shape "B7 hose corridor hash has route cost" was already red after step 1 (CordBuilder.CellSig ->
  CordSig.CellSig) -- step 1 ran the slice but not proof_all --offline-gate. Moved to HO7 with the new fragment; green.
- **Full `run_selftests.py` cannot finish inside one 600 s foreground call** (391 tests; several take 150-240 s; it also
  waits on FOUNDRY's suite lock). Each increment runs the relevant slice instead (`--only`: every selftest under
  GimmeSomeSlack/, FlowWorks/, _Shared/, plus selftest_gimmesomeslack/flowworks_stock); the full suite is owed after the port.
- Step 1: the internal cascade was fixed at MEMBER level (169 declarations public->internal), not by making whole GSS
  types internal, so XML-referenced classes (comps, map components, probes) stay public.

## FlowWorks pre-existing bugs fixed in-port
- (pending)

## Bugs filed (not fixed)
- (pending)

## Moved tests (step 2) -- every one still runs
- C# SelfTest, GSS -> FlowWorks (run by `selftest_flowworks_stock.py`, "hose:" block, per-suite counts printed): HoseSelfTest 130,
  HoseCarryChecks 33, HoseLiveChecks 21, StyleStage3Checks 10 (whole files); split out of mixed files into HoseReviewChecks.cs:
  HoseReview6 26 (ReviewRound6 Draw/Length/Relay), HoseReview7 7 (ReviewRound7 EndsOnEdge/LaysIntoEverySide/Station42/WireWidth;
  the GSS file was left empty and deleted), HosePileLook 6 (PileLook rule 3), HoseGptFix 20 (GptReadFix B4/B10/B11/B13/B5/B2-B3);
  HoseFuzz 4 (GssFuzz hose + trail families, same seeds, same 2798/1500 cases and known-gap tallies). Total 257 moved; GSS 871 -> 614.
  NEW: HoseLegacyChecks 21 (alias table, import fixtures x3 folder families, look import).
- Stayed in GSS on purpose: LaneAChecks.HoseChecks (it tests GSS's CordBuilder with the hose LayParams, not the reel);
  LegacyNameChecks (GSS's own MessyConduit rename table, whose FireHosesMod handle still feeds the FlowWorks import).
- Python: validation_hose.py, validation_style_hose.py -> FlowWorks (on Utils/validation_core.py); GSS validation O5 hose art,
  O6 B8/B22, O6 B20 (hose files), O7 hose shapes -> FlowWorks/validation_hose_offline.py HO5-HO8 (registered as FW chain
  `hose_offline`); GSS ROW_SHOWS hose rows + the UNBUILT pump row -> FW `HOSE_ROW_SHOWS` / chain `hose_live_rows`;
  GSS proof_all hose/maze/relay/carry/style_hose blocks + SL4 + the 9 matrix hose scenes -> FlowWorks/northstar/proof_hose.py
  (step 8; until then each is runnable standalone through validation_hose.py --live/--maze/--relay/--carry and
  validation_style_hose.py --live; the matrix scenes through reduced.hose_spec()).

## Lessons
- Step 1: run each mod's own offline gate (proof_all --offline-gate), not only run_selftests: a source-shape row (O7) went red
  on a pure rename and only the gate reads it.

## Step 0 census (bench HEAD b525ecca8, 2026-10-11)
- GSS SelfTest: **871/871** total; `hose:` suite (HoseSelfTest) **130/130** — the design's sanity probe said 129; one check was
  added since (drift, not a fault). Aerial 96/96.
- Mod/ModSettings classes: FlowWorks `RimMandrakeFlowWorksSettings`/`RimMandrakeFlowWorksMod`, `RiverSteamSettings`/`RiverSteamMod`;
  GSS `GimmeSomeSlackSettings`/`GimmeSomeSlackMod`, `AerialSettings`/`AerialLinesMod`, `HoseSettings`/`FireHosesMod` (moves).
- Hose settings: 17 Scribe keys (`HoseSettings.cs:54-75`); 15 survive (useFlowWorksPumps, defaultFluid die at step 6).
- `GimmeSomeSlack` strings in moved files: 21 files (16 C#, 3 defs + styles) — all rewritten at step 2.
- 11 credit sites verified at the FINAL doc's lines: pump 152/169/231, converter 219/223, adapter 135/153, reactor 184/185/191, bath 148.
- Live hose rows declared in GSS proof_all DECLARED_ROWS: hose 6, maze 8, relay 8, carry 8, style_hose 6, SL4 1 = **37**;
  matrix hose scenes H00-H08 = **9** (reduced.py HOSE_PREFIX). human_review.py: 192 hose/reel mentions (stations moved at step 2/8).

## Pre-existing failures seen, not mine
- `Utils/selftest_settings_screens.py` GimmeSomeSlack#Cables: "6 groups found, expected 5" (the GSS cable screen gained a
  "Which conduits become cords" group; the HEAD version of the selftest fails identically). Left to the GSS owner.
