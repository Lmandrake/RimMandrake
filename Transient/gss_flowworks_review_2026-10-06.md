# Gimme Some Slack + FlowWorks — review of 2026-10-06

## 1. The test methods

Window covered: commits from 2026-10-05 18:00 to 2026-10-06 18:31 PDT. Everything below was read from commits and the
docs they wrote; numbers are the docs' own MEASURED figures unless marked otherwise.

**A. In-game scenario runner (FlowWorks).** A small dev-only C# runner inside the JawaBench companion plays whole
player situations on the game's own thread (dig a canal, trap a pawn, light tar, pump, save and reload) and writes
each verdict to a journal file as it finishes; one bridge call starts it. Built at `9366b0193` (3 scenes) and
`7306dd75b` (8 more, incl. a two-half save/reload), driven by `src/RimMandrake/FlowWorks/northstar/playtest_runner.py`.
Cost: the full 11-scene recipe runs in **27-35 s, 14-21 bridge calls, ~1,500-2,600 ticks/s**, against the old
northstar core checkout's 176 s / 861 calls at ~60 ticks/s. Two live rounds (10:40 pilot, 12:01 round 2). Found:
water and tar merging into one body (now fixed and passing every run), a friendly pawn unable to climb out by the
ladder (fixed; passes on a fresh game, still fails in one "dirty" game), and in round 2 four new failures: a reload
lands one tick past the save so the save/reload check can never pass as written (open, C# side); **the natural pond's
stock/capacity is not saved, so a reload resets it** (open, a real mod defect: saved 43/45, loaded 40/40); the sluice
moved nothing past any door in one game (open, cause unread); a dig timed out once (looks like a too-short wait, not
proven). Round 2 cost ~10 live minutes, but **~19 minutes went to making a temporary 6 GB clone first**.

**B. Offline fuzzing (FlowWorks and Gimme Some Slack).** Seeded random action sequences thrown at the pure maths with
no game running, failing cases shrunk to the smallest reproducer. FlowWorks: `a8644d691` (245k sequences in ~1.6 s, 0
failures on shipped code, planted bugs caught), then `0811541df` pulled the per-pulse grid step out into
`RM_FlowKernel` so the game and the fuzz run the same code (matches the Python oracle 3,000/3,000). It reproduced
both source-read findings (water+tar merge; supply order changing after reload), both fixed at `45d720097` on your
rulings. GSS: `0d524b8e0`, four families (cords, hose, carried-hose trail, aerial lines), 9,418 cases in **13-14 s**,
run by the normal selftest on every commit. **One real bug found and fixed**: the cord cache did not notice when a
conduit behind a device stub was removed, so a stale cord look stayed until something else changed it (fixed
`0d524b8e0`, DLL rebuilt `47293418e`). It also tallied five hose gaps it does not fail on (a laid hose slightly
longer than the hose; the hose bending tighter than its minimum right out of the nozzle in 965 of 1,445 cases; three
marginal ones) and one cache trade-off (a wall 4-6 cells from a cord leaves it stale) - all open, design calls.

**C. An agent plays a mission (FlowWorks).** A bounded driver (`fd96b35bf`, `player_missions.py`) gives an agent a
player goal and only player-level actions (designate, order, let time pass), logging timing and every point of
friction. One live run: **canal mission PASS in 130 s, 89 s of it the agent thinking, 40 s bridge**. Found no mod bug;
found bridge friction (`step_game_ticks` stopping early at 601 of 2,000 ticks, `play_for` refusing with "busy").
The pit and chain missions were built but not run; their capture-down step depends on a float-menu choice marked
UNVERIFIED live.

**D. Northstar checkouts (both mods).** The existing long scripted checkout. FlowWorks v2 went GREEN 59/59 three runs
in a row on the current DLL (`8fb5106e8`, `440ddb89f`), the rivers suite 16/16 (`5e7375011`), extensions 16 pass / 1
honest fail (`7dd307cf8`). A finished run stopped going stale on unrelated art edits (`218dde98e`). GSS: `proof_all`
moved under `northstar/` and now saves partial results after every block (`807ba7756`), because this morning's live run
was killed partway with **9 hose FAILs** (bend radius ~0.19 against an expected ~1.14). The last full GSS run is
143 PASS + 1 SKIP in 622 s, and predates last night's hose change. None of today's new bugs was seen by D: it was
59/59 green while water and tar were merging.

**E. Artboard screenshot pre-review (art).** Stage many subjects on a grid, take one capture, cut it into one crop
per subject, run cheap pixel checks (empty, off its cell, spilling over, hole) and one batched image read, so you
only see what is left. Offline half `05ee16921` (selftest 26/26); live half `54d2d1f81` (bridge tools to stage and
capture off-screen, plus a FlowWorks pit-states recipe of 34 subjects) - **compiled but never run live**. One trial on
an old xenotype screenshot: 13 crops in under a second, 3 real staging mistakes caught (pawns placed one cell off by
the staging script), 2 false alarms (skin the colour of the ground), and 5 rows worth your eye from one image read.

**Your four-methods question, from today's tally:** A and B found every real FlowWorks bug today; B found the only
GSS code bug; C found only bridge friction at 2-3 minutes a run; D found nothing new and is the slowest; every GSS
defect you found in rounds 1-7 was visual, which is E's target and E has not yet run in game.

## 2. Per mod

**FlowWorks - changes to the mod itself (game-facing):**
- Different liquids now stay separate bodies; when supply is scarce it is shared by cell position, so a reload no
  longer changes who gets it (`45d720097`, your rulings).
- Pits: a held pawn walks inside the pit to the lowered ladder and climbs out; colonists never path into an open pit,
  only forced arrivals fall (`790fd4e8d`, your card). Key-sheet stop 19 corrected to match.
- The liquid grid step moved into one shared kernel the game calls (`0811541df`) - a refactor of live code; the
  runner's round 2 ran on a DLL containing it.
- Liquid kits: baths, reactions, hot floods and residue, with Mod Settings (`b13f21360`). Load with no errors; **no
  run has exercised any of them**, numbers are first guesses.
- Last night: tar/oil no longer put fire out, a burning level keeps its burn clock as it flows, firefoam and rain
  really extinguish, foam setting gates the foam blast (`84d8bd3f6`, `dbf67fc0e`, `e5f11cb82`, `740672212`); River
  Works merged into FlowWorks (`409d1f57c`); hoses, cargo tank, stills, pipe adapters (`3e473f37c`); universal pump
  (`f3ab74a1b`); canal cuts can turn up minerals (`c858125a8`); bottles fixed and drinkable under Dubs Bad Hygiene
  (`cf1e75d26`, `b22bd59b1`); dug cuts draw walls (`a26e3d875`); visual principles 1-5 - lit wall faces, near lip
  hides sunk pawns, moving liquid surfaces, scorched pits (`157482540`, `d6676a833`).

**Gimme Some Slack - changes to the mod itself:**
- Cord cache fix found by the fuzz (`0d524b8e0`, DLL `47293418e`).
- Last night: hose no longer has rectangles cut across it by wall shadows, leaves the reel through its outlet, the
  joiner reads as one fitting (`0476fadd2`).
- You conditionally accepted it this morning (*"Mark this mod as conditionally accepted. I don't have any evidence
  it's broken. We should move to FlowWorks."*); its north star stays DRAFT.

## 3. For you to review

Every repo file below exists and is committed on origin/main, so the Windows path is the read-only mirror. Saves
were checked on disk at 18:31.

**Start here (in this order):**

1. **The plan you said you wanted to discuss before adopting** -
   `D:\Luke\dev\RimMandrake\design\RimMandrake\flowworks_playtest_automation_2026-10-06.md`. Three GPT runs agreeing on "move the
   playtest into the game", the 15 source findings, the first-week plan and its kill rule, the "stop now" list, and
   the measured time split (66% agent thinking, 4% bridge). Decision it asks: which of it you adopt. It still says
   "no plan adopted", although A, B and C have since been built under your 11:26 direction.
2. **Round 2 of the in-game runner** - `D:\Luke\dev\RimMandrake\Transient\flowworks_playtest\live_round2_2026-10-06.md`. Top table and
   the "New failures" list near the end. Decision: whether the pond-not-saved defect and the one-tick reload offset go
   to the top of the fix list (my read: yes, the first is a real player-facing loss).
3. **Gimme Some Slack fuzz report** - `D:\Luke\dev\RimMandrake\design\RimMandrake\gss_offline_fuzz_B.md`, the "Known gaps" table.
   Decisions it asks: is a hose that bends tighter than its minimum right out of the nozzle (G2, 965 of 1,445 cases)
   acceptable; is a laid hose ~10% longer than the hose (G1) acceptable; is "stale until the next edit" acceptable for
   a cord near a new wall (C1); and should the `sprawlCap` setting actually cap cord length, since today it does not.
4. **Artboard trial** - `D:\Luke\dev\RimMandrake\Transient\artboard_trial_2026-10-06\report.html` (with `owner_board.png` and
   `vision_mosaic.png` beside it), from the old shot `D:\Luke\dev\RimMandrake\Transient\xenotype_review\xeno_grid_v2.png`. Look at
   whether the "only the flagged rows reach you" idea feels right. Decisions: Sophie (near-invisible thin dark
   sprite - a missing body layer?) and Fernandez, Nails, Sayuri, McCann reading grey/white (unset skin or a genuinely
   grey species?).
5. **FlowWorks keeper review map (savegame)** - `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\RM_fw_review_20261006.rws` (14 MB, saved 07:07), with
   `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\northstar\review\map\keysheet.html` as the key and
   `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\northstar\review\README.md` for how to load it (flowworks tier only). **Caveat:**
   it was built before the 11:24 liquids fix and the 11:49 pit-ladder change, so pit stations show the old
   behaviour; the README's own rule says rebuild when code changed. Worth walking for looks, not for pit behaviour.

**Also waiting on you:**

- **Gimme Some Slack keeper map** - `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\RM_gss_review_20261006_prerestart.rws` (33 MB, saved 05:23) with
  `D:\Luke\dev\RimMandrake\src\RimMandrake\GimmeSomeSlack\review\keysheet.html` (rows S, T, U, A-G, M). You conditionally accepted the
  mod; this is the map to walk if you want to turn that into a real validation. It predates the 12:07 cord cache fix,
  which only affects a cord after a conduit is removed, so it is still a fair look.
- **FlowWorks feature sheet** - `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\northstar\review\FlowWorks_review.html` (45
  features, 8 sections) and the printable `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\northstar\review\FlowWorks_status_board.html`.
  Only one decision recorded so far (the ladder drawing, option A). See section 5 on what its "Works in game" means.
- **FlowWorks visual principles before/after sheet** (last night) -
  `D:\Luke\dev\RimMandrake\src\RimMandrake\FlowWorks\art_source\visual_principles_2026-10-05\visual_principles_sheet.html`. Its 11
  rows are all an agent's prefilled "Looks right"; you have not ruled any of them.
- **The three raw GPT answers**, if you want the full options rather than the merge -
  `D:\Luke\dev\RimMandrake\Transient\flowworks_playtest_review_2026-10-06\gpt_answer_A_high.md`, `gpt_answer_B_xhigh.md`,
  `gpt_answer_C_xhigh.md` in the same folder.
- Runner test saves (not keepers, safe to ignore): `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\JBPT_fwpt_20261006T193027_s1.rws` and four others named
  `JBPT_fwpt_20261006T19*`.

## 4. Open items and half-done work

| What | State | NEXT |
|---|---|---|
| Pond stock not saved (FlowWorks) | real defect, seen once live (saved 43/45, loaded 40/40); **not filed as an item** | Save each body's stock, capacity and receded flag in `RM_LiquidStock`, then rerun the runner's save/reload scene |
| Reload lands one tick late | the save/reload scene can never pass as written (`JawaBenchFlowWorksPlaytestScenes.cs:731`) | Accept a 0-1 tick offset there, rebuild the companion, rerun `--recipe save_reload` |
| Sluice doors | shut sluice leaks by design until the two-door build; one game moved nothing past any door | Build the two doors (`FLOWWORKS_SLUICE_TWO_DOORS_1`), rerun the sluice scene on two fresh games |
| Pit ladder fails in one game only | fixed on fresh games, fails 3 of 3 in the dirty game | Rerun `pit` after `destroy_bulk nonColonists` plus a culled map to reproduce |
| Dig timeout | 1 of 4 runs, colonist distracted | Give the dig scene a forced job or a longer budget |
| Artboard live half | compiled, never run in game | Run `python3 -m artboard.live flowworks_pit_states --origin X,Z` on the flowworks tier |
| GSS 9 hose FAILs | untraced since the killed proof_all run | Compare the MX_H bend rows with fuzz gap G2, then rerun `northstar/proof_all.py` |
| GSS hose gaps G1-G5, cache C1, `sprawlCap` | tallied, not failing anything | Put G1, G2, C1 and `sprawlCap` to you as one question card |
| GSS map adapter | not covered offline | One bridge session checking the real-map snapshot |
| Liquid kits | built, load cleanly, never exercised | Add a feature row and run each mechanic live |
| FlowWorks keeper map | predates today's pit and liquid changes | `review_map.py --build --fresh-map`, then save a new keeper |
| Mission driver | canal ran; pit and chain never ran | Verify the float-menu choice live, then run the pit mission |
| GPT findings #3-#6, #8, #10-#15 | confirmed in source, no commit today addresses them | Triage into items or drop, one line each |
| Campaign log | stops at 11:40; round 2 and the GSS fuzz bug are not in its tally | Add those rows |
| Pit temperature softening | built offline (`e60bebedc`) | Live run and your ruling on the numbers |

## 5. Honest judgment

- **The best result of the day is the speed, and it is real.** A full FlowWorks scene pass dropped from ~3-4
  minutes and ~860 calls to ~30 s and ~15 calls, and it found three genuine defects the 59/59-green checkout never
  saw. That checkout being green while water and tar merged is the strongest evidence that D is not a bug-finder.
- **The GSS hose FAILs are probably not mysterious.** The killed live run's 9 FAILs are all "bend radius ~0.19 against
  a minimum ~1.14"; the offline fuzz independently found the hose bending at 0.02-0.4 against 0.6-2.0 right out of
  the nozzle in 965 of 1,445 cases. Neither doc connects the two. That suggests a real hose-shape gap rather than a
  stale expectation (the theory in the acceptance note). Unverified - it is my inference from matching symptoms.
- **"Works in game" on the FlowWorks feature sheet means "a mapped scripted row passed"** - exactly what all three
  GPT runs said to stop calling proof. The sheet has not been changed to reflect that.
- **The keeper FlowWorks save is behind the code** (07:07 save vs 11:24 and 11:49 behaviour changes). Treat its pit
  stations as old behaviour.
- **Claimed but not shown:** the artboard capture (compiled, never run - its own doc lists three ways it may fail);
  the liquid kits ("loaded live" means no load errors, nothing exercised); the pit and chain missions; the GSS
  adapter. The kernel refactor was marked "not yet live-checked" at commit time, but round 2 did run on a DLL that
  contains it, so that one is now partly checked.
- **Contradictions:** the plan doc still says "no plan adopted" though A, B and C were built under your later
  direction; the campaign log's tally is out of date; the round-2 pond defect lives only in a Transient file, which
  is binned in ~14 days, with no item filed. Round 2 ran in a temporary 6 GB clone that cost 19 minutes - that is
  the largest single cost of the round and is not in the timing tally.
- **What I did not check:** I did not re-run any test, open the saves in game, or confirm the 15 GPT findings myself;
  the statuses above are what commits and docs say.
