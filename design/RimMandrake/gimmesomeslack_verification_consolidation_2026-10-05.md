# GimmeSomeSlack (ex-MessyConduit) — verification consolidation, 2026-10-05

ANALYSIS ONLY. Nothing implemented. Owner, 2026-10-05: *"reduce the number of Northstar verifications and verification
stations for the human review sheet as well. If so, remove them. Then run them."* and *"Yes you should examine the hash
bound ones too. This is a full densification."*

## 1. Inventory (before)

Measured from the latest result JSON of each kind in `src/RimMandrake/GimmeSomeSlack/northstar/` (127 files).
Duration = filename stamp minus `started` (approximate; matrix uses its own `wall_s`).

| # | live run (command) | rows | latest | ~seconds | scene / map |
|---|---|---|---|---|---|
| R1 | `validation.py --live --fresh-map` (core) | 46 | 2026-10-04T144613 42 PASS, 3 UNCOVERED, 1 UNBUILT | 60-100 (390 cold-ish) | fresh quicktest; core room scene + P1b plot |
| R2 | `validation.py --save-load NAME` (M4) | 3 | 144631 3 PASS | 10 | loads a save (replaces map) |
| R3 | `validation.py --removal-check NAME` (M9) | 1 | 20261003 PASS | 6 + **a cold load onto a tier without the mod** | other tier |
| R4 | `validation_aerial.py --live` | 18 | 144729 18 PASS | 20-60 | own site |
| R5 | `validation_aerial.py --save-load` (M16) | 3 | 144749 PASS | 10 | loads save |
| R6 | `validation_aerial.py --removal-check` (M9b) | 1 | 20261002 PASS | 4 + cold load | other tier |
| R7 | `validation_hose.py --live` | 12 | 234747 12 PASS | 15-75 | own site |
| R8 | `validation_hose.py --save-load` (H10) | 3 | 144819 PASS | 10 | loads save |
| R9 | `validation_hose.py --removal-check` (H11) | 1 | 20261002 PASS | 7 + cold load | other tier |
| R10 | `validation_hose.py --maze` | 8 | 235424 7 PASS 1 RECORD | 40 | own site |
| R11 | `validation_hose.py --relay` | 9 | 234910 9 PASS | 20-40 | own site |
| R12 | `validation_hose.py --carry` | 11 | 20261005T001134 10 PASS **1 FAIL (CR7, label case; fixed in harness at dc17f699a, not yet re-run)** | 55-75 | own site + 2 saves |
| R13 | `validation_style.py --live` | 14 | 220407 14 PASS | 20 | own site + 1 save |
| R14 | `validation_style_hose.py --live` | 7 | 234917 6 PASS 1 UNMEASURED | 10-15 | own site + 1 save |
| R15 | `northstar_matrix/run_live.py` | 122 (109 scenes, 19 boards) | 1152: 121 PASS 1 SKIP | 310-610 state-only; ~1580 with shots | absolute 226x100 REGION, map-wide clears |
| — | `validation_styles` (ST1-ST5, 2026-10-02) | 8 | absorbed into R1 as ST1-ST5 | — | dead lane (now rows in R1) |
| — | `validation_merged_laneb` | 62 | a merged report, not a run | — | — |

**Before: 15 live invocations, 259 live rows** (46+3+1+18+3+1+12+3+1+8+9+11+14+7+122), **three cold loads** for the
three removal checks (each a mod-list swap; they share one target tier so they can share ONE cold load), and **~20
save/load cycles** (R2, R5, R8, R12x2, R13, R14 = 7 saves written and reloaded).
Live wall time per full proof, summed from the latest runs: ~1.5 min core + 3x~10 s save-load + ~1 min aerial + ~1 min
hose + 40 s maze + 40 s relay + ~1 min carry + 20 s style + 15 s style-hose + 5-10 min matrix (state-only) or ~26 min
(with shots) = **~13 min state-only / ~30 min with shots**, plus three removal-check cold loads (one if batched), plus
the bridge round-trips of switching scripts (each script re-applies defaults, re-pins weather/clock and builds its
own site: the matrix log shows `site_setup` alone at 8-93 s).

Offline (no bridge): `validation.py` offline tier O1-O5 (mod files, settings defaults, C# SelfTest vs Python oracle +
`--probe` mutation, oracle selftest), `northstar_matrix/selftest.py` (335 lines, fakegame), `selftest_human_review.py`
(layout plan), and the C# SelfTest project (`Source/SelfTest/`, 21 files: Lane A, Hose, HoseCarry, HoseLive, Aerial,
Determinism, LegacyName, ReviewRound1/3/4/5/6/7, StyleStage1/2/3). Offline is cheap (seconds) and is NOT a target for
cuts: the owner's complaint is validation TIME, which is the live tier.
### 1a. Hash-bound north-star bars (owner 2026-10-05: in scope)

**MEASURED: zero.** `design/validation_walks/RimMandrake/GimmeSomeSlack.md` (30 lines) has no `## north star` section,
no `state:` and no `validated-hash:` line; no other walk under `design/validation_walks/` carries one for this mod
(the only other file naming it is `BlueDesert.md`, a mention). So bars before -> after is **0 -> 0**, and nothing here
needs a `modcheck validate` re-sign. The walk's unhashed `## must be true` lines M1-M9 are analysed instead:

| walk line | guards | covered by | proposal |
|---|---|---|---|
| M1 graph + census + cords printed + transparent conduit | core build, adapter, mesh print (Run 2: graph green, layerVerts 0) | R1 M1_* ; matrix floor scenes census every topology | keep |
| M2 no cross-net edge, no unwalkable vertex | planner bug | R1 M2/M2b ; offline O3 on 7 oracle scenes | keep |
| M3 HiddenConduit never drawn | target-def list | offline only (ConduitVisuals list + census `texPaths`) | keep, offline only (already) |
| M4 save/load same polylines | **regression 2026-10-02: no cords on ANY loaded save** (MapDrawer NRE) | R2 | keep, in the ONE merged save/load (SL3) |
| M5 local invalidation | cache bug | R1 M5 | keep |
| M6 overlay connector lines intact | Harmony suppression over-reach | R1 M6 | keep |
| M7 master switch off/on | restore path | R1 M7/M7b, matrix C01 duplicates it | keep M7, cut matrix C01 |
| M8 break: two ends, live/dead, source-off within 250 | end readout | R1 M8/M8b/M8c | keep (M8b folds, see 2) |
| M9 removal | **regression 2026-10-02: MapComponent written into the save** | R3; ALSO already E1 in `## extended`, paused by the owner | delete M9 from `## must be true` (it is E1); keep `M9a` (save holds nothing of ours) in the basic save/load, which is the cheap half that caught that regression's cause |

Walk drift found (facts, not judgement): step X says "15 stations" (there are 47 + M + F); line 1 reads "(was
GimmeSomeSlack)" (the rename's sed hit it; should be "(was MessyConduit)"); and the walk covers only phase 1a: aerial
(M13-M19), hose (H, maze, relay, carry), and style rows have no walk line at all. A densified walk should add ONE line
per subsystem (aerial, hose, carry, style) naming its chain, not one line per row.

## 2. Defect kinds and coverage overlap

A row is cut only when another row (or offline check) FAILS whenever it fails; "consolidated" means N rows become one
row whose detail names the failing part (no detection lost, fewer lines to read).

**Harness/site rows (21 rows: core L0,L1,L2,S0,P1B_plot_built; aerial A0; hose H0,H1; relay RL1; carry CR0; matrix
O0,I0,L0-L6,H0).** They detect harness faults only; each script re-proves the same fresh map / tier / probe channel.
In one session they collapse to 3 preflight rows (P1 fresh map; P2 tier running + startup log clean; P3 probe
channels cord/aerial/hose answer + region pinned + no pawn in region). Scene-built facts move into each site's notes.
Guards kept: the SteamGeyser-in-scene harness lesson stays in P3's region clear.

**Log budget (Z, AZ, HZ, matrix Z: 4 rows)** -> 1 run-end row over the whole session's log; fails whenever any of the four would.

**Determinism (core D1, matrix D1, D2: 3)** -> 2. Core D1 ("a fresh builder reproduces every edge hash") is the same
predicate as matrix D2 on a superset of boards. **Guards: D2 was RED on every ring board 2026-10-02**; the reduced
floor keeps the ring topology, and `DeterminismChecks.cs` replays every floor scene offline (det_export).

**Save/load (14 rows over 7 save+load cycles: M4a,M9a,M4; M16a,M16b,M16; H10a,H10b,H10; CR4a,CR4b; S7,S9e; R4)** ->
**4 rows over ONE save**, made after every site is built: SL1 only the new .rws appeared (M4a=M16a=H10a, same
predicate); SL2 the save text names no class of ours (M9a ∪ M16b ∪ H10b, the same text scan over one file that holds
all subsystems); SL3 post-load census equals pre-load for cords (geometry hash), aerial links, hose state, style runs
and laid styled hoses (M4, M16, H10, S7, S9e, R4); SL4 carry states survive (CR4a dropped + CR4b carrying; separate
because it guards pawn job/driver state, not geometry). Guards kept: the 2026-10-02 load NRE (SL3) and the
MapComponent-in-save (SL2).

**Removal (M9, M9b, H11)**: already PAUSED by the owner (walk E1). Out of the basic proof. On request: one cold load,
ONE row over the single SL save (it holds cords, masts and hoses, so it fails whenever any of the three would).

**Matrix floor 64 (T16 x S4, F = (t+s)%4).** Detects adapter/core disagreement with the oracle per topology x tangle
stage. The tangle stage (S) only changes core settings; core x setting interactions are proven offline (C# SelfTest
vs oracle, and the floor replay in DeterminismChecks.cs). What only a live board finds is the Verse adapter on a
topology (wall/rock entry, gap, multinet, ring). -> **16 scenes: each T once, S and F each on 4 scenes (Latin
rotation)**. Every T, every S and every F still runs live; lost are only T x S pairs, which are covered offline.
**Owner veto point**: the design (phase-2 design §4.2) asked for T16 x S4 by name.

**Matrix density 16 ({1,10,100,1000} x S4)** detects scale faults (perf, far-zoom LOD, n=1000). S is irrelevant to
scale. -> **4** (one per n, S rotated).

**Matrix aerial 18** = two Latin squares over N{2,3,5} x R{6,12,19} x state{up,cut,fallen}; A00-A08 alone already covers
every pair. -> **9**. (Check before cutting: if A09-A17 differ in a factor the id does not show, e.g. style, rotate it
into A00-A08.)

**Matrix hose 9 (L9)** asserts per scene: state, blend, visible width, width/wire >= 4, bend >= 0.95 x setting, no
self-intersection, no unwalkable point, couplings (`run_live.py` 1011-1020). So `validation_hose` **H3** (width >= 4x
wire), **H4** (bend radius) and **H5** (flat when not flowing) fail only if MX_H00-H08 fail (same predicate, superset of
shapes: straight/corner/water x 6/14/24, flat/plump/filling). Cut H3, H4, H5. Keep H6 (transition timing), H7
(flicker), H8 (collapse), H9 (stiffness setting): time behaviour a static L9 cannot see.

**Matrix controls 2**: C00 empty board (negative control) keep; C01 master off == core M7 -> cut.

**Core**: ST1 x4 (each look's textures load) -> 1 consolidated row. U_motion_look, U_style_missing_art (UNCOVERED /
UNBUILT human-look placeholders) -> move to the human sheet as stations (they are taste, not pass bars; today they also
make `modcheck record` refuse). M4/M9 placeholders inside R1 -> gone (SL3 / extended). **M8b** (no cord across the gap)
is implied by M2 IF M2 is re-evaluated on the post-break census (a one-cell gap splits the PowerNet, so a cord across it
is a cross-net edge) -> cut M8b after that one-line harness change; otherwise keep.

**Aerial**: R2_spans_and_heads_drawn is asserted per MX_A scene (spans + heads drawn) -> cut if MX_A's census row reads
`R2`'s fields (verify). M14_gap_control_without_fix is a negative control: keep. **Guards kept**: M14b dead pole drops
live and dead cords, M15 explosion cut, M19n taps-off control.

**Carry/relay/maze/style/style-hose**: distinct behaviours each (job driver, couplings, routing, per-build style
store/merge/tie/split, legacy default). Only their harness and save/load rows fold. **CR7** (no instant gizmos without
dev mode) is FAIL in the latest result from a label-case harness bug fixed at `dc17f699a`; it guards a real rule
(dev gizmos leak to players) and stays.
## 3. Proposed dense set (after)

One live session on one fresh quicktest map (gimmesomeslack tier), every site in a disjoint region, one save/load at the end.

| block | rows before | rows after | what changed |
|---|---|---|---|
| shared preflight + det + log + save/load | (spread over scripts) | 10 | P1-P3, D1, D2, Z, SL1-SL4 |
| matrix | 122 | 39 | harness 11 and Z/D out to shared; floor 64->16, density 16->4, aerial 18->9, hose 9, controls 2->1 |
| core `validation.py --live` | 46 | 31 | harness 5, D1, Z out; ST1 x4->1; U x2 to human sheet; M4/M9 placeholders out; M8b (conditional) |
| aerial | 18 + 3 save/load | 15 | A0, AZ out; R2 (conditional); save/load to SL |
| hose live | 12 + 3 save/load | 6 | H0, H1, HZ out; H3/H4/H5 implied by MX_H |
| maze | 8 | 8 | — |
| relay | 9 | 8 | RL1 to preflight |
| carry | 11 | 8 | CR0 out; CR4a/b -> SL4 |
| style | 14 | 12 | S7, S9e -> SL3 |
| style-hose | 7 | 6 | R4 -> SL3 |
| removal (M9, M9b, H11) | 3 | 0 basic (1 on request) | owner-paused extended E1 |
| **total** | **259** | **143** (+1 extended) | |

Scenes: matrix 109 -> 39; the 8 script sites (core room + P1b plot, aerial, hose, maze, relay, carry, style,
style-hose) stay 8 but share one map, one calm-world setup and one probe-defaults pass.
## 4. Human review sheet stations

Before: 47 stations + M (art board) + F (free area). The style gallery 1-12 (built 2026-10-04 through the real per-build
style machinery) supersedes most of the old default-look rows A/B. Every distinct visual question is kept.

| station(s) | proposal | why (what still shows it) |
|---|---|---|
| 1-6 style rows S | keep | one look per station; 1-4 each already hold battery, 3x3 tangle, run under a steel wall, in-line switch, three plugged devices and a missing cell (live + dead end) |
| 7-10 merge / tie / split / restyle | keep | four distinct rules |
| 11 reels per look, 12 older save | keep | 12 guards the legacy unstyled-default path |
| 13 powered line | **cut** | stations 1-4 |
| 14 unpowered line ("intact cord looks the same unpowered") | **cut — veto point** | weakest distinct question; matrix P=dead scenes cover it in state |
| 15 cut line | cut | 1-4 missing cell: live + dead end |
| 16 tangled pile | cut | 1-4 3x3 tangle; 32 electric room |
| 17 devices + plugs | cut | 1-4 switch + three plugged devices; 31 pole cluster |
| 18 wall + rock entries | keep | the only rock (granite) entry and wall-terminal branch |
| 19 mast chain, 20 lamp masts, 21 wall bracket | cut | 6 has battery > mast > mast > lamp mast > wall bracket in all four looks; 10 has a span |
| 22 cut + fallen span, 23 power tap | keep | distinct states |
| 24 flat, 25 filling, 26 plump, 29 parallel | **merge into ONE "HOSE STATES" station**: three parallel hoses two cells apart, flat / frozen half-filled / plump | neighbours differ in one thing (the layout rule) and 29's question (lanes, one over the other) is the same picture |
| 27 long + bend | cut | 34/35 maze bends, 42 relay length, 45 pond |
| 28 crossing | cut | 30 hose grid has four crossings with the same over/under question |
| 30 hose grid | keep | |
| 31-33, 36-41 showpieces + challenges | keep | each a distinct question (terminal allocation, lived-in room, fog, edge, river, roof, span limit/refusal, hub refusal, nets + blueprint) |
| 34, 35 mazes | keep | before/after pair |
| 42 relay | keep | |
| 43 deploy by hand + 47 wind it in | **merge**: 43's card says "after he lays it, press Retract" | 47 is the same reel and pawn, the reverse action |
| 44 dropped, 45 pond, 46 their tank | keep | three end kinds |
| new: U_motion_look, U_style_missing_art | add as notes on 13->(1) and M | they were UNCOVERED live rows; they are taste |
| M, F | keep | |

After: **33 stations + M + F** (cut 13,14,15,16,17,19,20,21,24,25,26,27,28,29,47 = 15; add 1 HOSE STATES). Removing
stations shrinks REGION and the north gallery; `--plan` must re-pass (spacing R=5, masts 20 from F).
## 5. Before -> after numbers

| measure | before | after |
|---|---|---|
| live invocations for a full proof | 15 (13 basic + 3 removal, minus the dead `validation_styles` lane) | **1** (`proof_all.py`), +1 removal on request |
| fresh maps / site setups | ~10 (each script) | 1 |
| saves written + loaded | 7 | 1 |
| cold loads | 1-3 (removal) | 0 basic |
| live rows | 259 | **143** |
| matrix scenes | 109 | **39** |
| hash-bound north-star bars | 0 (measured) | 0 |
| walk `## must be true` lines | 9 (phase 1a only) | 8 + 4 subsystem lines (M9 lives in E1 only) |
| live minutes, state-only | ~13 (matrix 5-10 of it) + switching | **~7** (matrix ~3: scene_probes+build+ticks scale with 39/109; mod_settings_field polling, 3168 calls / 212 s, falls with it) |
| live minutes, with screenshots | ~30 (matrix ~26) | ~12 |
| human stations | 47 + M + F | **33 + M + F** |
## 6. One-shot full proof (proof_all.py)

Write `src/RimMandrake/GimmeSomeSlack/proof_all.py` (excluded from `mod_hash` like `validation.py`/`human_review.py`).
It imports the existing scripts' functions; it does not reimplement checks. One results JSON in `northstar/`
(`proof_all_<stamp>.json`), every row once, plus per-phase timing.

Ordered command list it runs (and what an agent types today, until it exists):

1. Offline, refuse to go live if any red: `python3 validation.py` (O1-O5 incl. C# SelfTest + `--probe` mutation),
   `python3 northstar_matrix/selftest.py`, `python3 northstar_matrix/det_export.py` + SelfTest determinism replay,
   `python3 human_review.py --plan` (and `selftest_human_review.py`).
2. `modset_builder.py --tier gimmesomeslack --apply` only if the live list is not already that tier; launch via Steam;
   `rimflow bridge take`.
3. Live, one map: preflight P1-P3 -> matrix reduced boards (FIRST: it clears map-wide and destroys non-colonists) ->
   core site (`live_battery`) -> aerial -> hose live -> maze -> relay -> carry -> style -> style-hose -> D1/D2 ->
   log budget Z.
4. One save (Saves folder stat'd before/after), one load, SL1-SL4.
5. `--extended removal` only when asked: one cold load onto `--tier flowworks`, one removal row on that save.
6. Then (not a proof) `human_review.py --build --fresh-map` for the owner, and `rimflow bridge release`.

Implementation notes: the scripts each set probe defaults and pin weather/clock; hoist that into `proof_all` and pass a
`shared=True` that skips each script's own setup and log-budget rows. Matrix must accept `--scenes reduced` (a
`design_spec` subset flag), keeping full T16xS4 behind `--full` for a design review. Each site needs a region that does
not overlap the matrix REGION (226x100) or another site (cord reach 5, mast link 20).
## 7. Cuts needing owner veto

1. Matrix floor 64 -> 16 (the phase-2 design named T16 x S4; the lost T x S pairs stay proven offline only).
2. Human station 14 "unpowered line" (its one question: an intact cord looks the same unpowered).
3. U_motion_look / U_style_missing_art leave the live rows for the human sheet (changes what `modcheck record` waits on).
4. M9 removed from the walk's `## must be true` (it is already E1, paused by him).
Everything else is a strict implication or a consolidation and needs no ruling.
