# Lightspeed: the no-LLM test lane (design, 2026-11-06)

Owner, 2026-11-06: *"For the One test lane with no LLM in it, that's awesome! We should call this Lightspeed. I wonder
how much we could write up to be tested this way? How much of Northstar could be wired with no LLM in the mix? Write
this up with GSS as the test case and Expedite it."*

Inputs: `design/RimMandrake/fast_testing_2026-11-05/scored.md` (item 1, "One no-LLM lane", scored 4.70). Related items
filed 2026-11-05: STAGING_REWIRE_PYTHON_NOT_AN_LLM, PACING_PRUNE_LLMS_SLOW_ENOUGH_ALONE,
PROOFLINT_WIRE_AT_FILING_NOT_AT_RUN, UNMEASURED_ROUTES_WIRE_NO_SIX_HOUR_NAPS. Measured at HEAD `fbeecfac7f`.

## 1. What Lightspeed is

Lightspeed is **one queue, one warm game, and scripts that decide every verdict**. A commit goes in; a dated row
(PASS / FAIL / UNMEASURED, with the sha it ran on) comes out; no language model reads, stages or judges anything in
between.

- **The queue is testq** (`src/RimMandrake/Utils/testq/testq.py`). Its worker (`infrastructure/stevedesktop/worker.py`)
  already does deploy -> load -> run -> result with no LLM, on SteveDesktop (and on Archmagi under
  `archmagi_switch.py`'s rules). It has two job shapes today: a `modcheck run <Mod>` job, and an exact-tier job
  (`profile tier:<name>`, selector `{"proofs": [...]}`) that loads a `modset_builder.py` tier as the whole list and
  runs an item's `live-proof` lines from `infrastructure/state/live_proofs/<ID>.txt` at `source_sha`, exit 0 PASS,
  1 FAIL, else UNMEASURED (`worker.py run_proofs`).
- **The game stays warm.** A job does not cold-load unless its mod list changed; the dispatcher groups jobs of one
  host+profile into a train.
- **Scripts decide.** A verdict is a script's exit code or a row in its results JSON. Nobody reads a log to decide.
- **Where an LLM still enters**, and only there:
  1. an *unhandled failure*: a job ends INVALID or FAIL with a cause no rule routes (scored.md "coded UNMEASURED
     routes": not deployed -> deploy and retry; changed since built -> rebuild; not in the running load -> park for
     that list; exit 2 -> harness fixer with stderr). Anything else wakes a fixer, with the job's logs as input;
  2. *judgement no script can make*: a north-star `must show` bar on a frame, an art look, an owner look, a walk.
     Lightspeed still stages and shoots those frames; the verdict waits for `northstar_driver/judge_cli.py` or the
     owner, and the script half of the same row is not held back by it.
  3. Flyer flight is never in Lightspeed (standing ruling: never live-test a flyer's flight). It is owner-present only.
- **Relentless keeps building**; it stops *testing* through an LLM-staged live round
  (`src/RimMandrake/rimflow/relentless_live_round.py`) and becomes a testq client: its criteria get their verdicts
  from Lightspeed rows (section 3, step 5).

## 2. Census: how much of Northstar could run with no LLM

**Unit.** One runnable unit is one of: a modcheck row (a `t.component` a chain emits), a standalone proof script
(not reached by any chain), one `live-proof` line, one north-star `must show`/`cannot show` bar, or one
owner-present walk line. Units of different kinds are not the same size (a script is many rows); the totals say how
many *things* need a verdict.

**Classes.** (A) deterministic, PASS/FAIL rows, runnable by testq today. (B) deterministic but needs a route (a
script testq does not call, a mod list SteveDesktop lacks, or a script still owed). (C) needs judgement. (D) flyer
flight, owner-present only.

### Totals (HEAD fbeecfac7f, 2026-11-05)

| class | units | made of |
|---|---:|---|
| A | **4,108** | 1,140 modcheck rows in the 6 wired mods; 2,966 modcheck rows in 112 more *selectable* mods testq can run but its filler never queues; 2 `live-proof` lines already sent to testq as exact-tier jobs |
| B | **736** | 313 `live-proof` lines run only by the LLM-staged round; 302 modcheck rows on mods whose dependencies are not on SteveDesktop's MINIMAL list (290) or that GSS measures only in `proof_all.py` (13 `proof_all_only_rows`, UNMEASURED by design); 77 standalone proof scripts (65 drive the bridge); 42 stub rows that raise "UNMEASURED: live check owed" (script owed); 2 mods with no `suite` (DeepDrill, TileFeatures) |
| C | **378** | 374 north-star bars across 95 walk files (6 VALIDATED by hash); 4 stub rows that say "judged by eye" |
| D | **3** | TheRot `dustveil.flip_book_frames_cycle`; LeaningScrub shirrel Gale glide; LeaningScrub runway-bloom dustflutter burst |

**93% of units (4,844 of 5,225) need no LLM at all; 79% (A) need no new code, only queueing.** Only C (7%) and D
(3 units) need a judge or the owner.

Outside the table, because it is not a runnable unit yet: **882 Relentless live criteria on 498 built items have no
`live-proof` line at all** (`relentless_live_round.py eligible` -> `skipped["no proof"]`; my replay of `candidates()`
gives the same 882). No lane, LLM or not, can ever run them until a line is written (PROOFLINT_WIRE_AT_FILING_NOT_AT_RUN).

### Per mod (top of the table; every mod is in the evidence file)

| mod | A | B | C | D | | mod | A | B | C | D |
|---|--:|--:|--:|--:|-|---|--:|--:|--:|--:|
| FlowWorks | 600 | 59 | 87 | 0 | | Cauldron | 97 | 0 | 9 | 0 |
| Wastes | 186 | 0 | 0 | 0 | | HugeThings | 96 | 0 | 0 | 0 |
| EnvironmentalHazards | 139 | 1 | 0 | 0 | | TerminalBiomes | 93 | 1 | 0 | 0 |
| Stillsand | 118 | 9 | 0 | 0 | | Contagion | 84 | 0 | 10 | 0 |
| RustCathedral | 116 | 1 | 0 | 0 | | Pyrelands | 44 | 2 | 21 | 0 |
| TheForge | 112 | 1 | 0 | 0 | | AtmosphericBase | 23 | 1 | 28 | 0 |
| CreatureBehaviors | 110 | 2 | 0 | 0 | | **GimmeSomeSlack** | **30** | **18** | **11** | 0 |
| FeverWood | 106 | 0 | 0 | 0 | | LeaningScrub | 0 | 112 | 10 | 2 |
| TheRot | 102 | 0 | 0 | 1 | | WeepingStones | 0 | 71 | 0 | 0 |

The 299 `live-proof` lines that do not call `modcheck run <Mod>` are counted against their item, not a mod.
B for GimmeSomeSlack understates it: its 5 scripts include `proof_all.py`, which is **119 rows** (2026-10-16 result:
37 core, 30 matrix, 26 aerial, 17 style, 9 preflight/session/save-load).

### How it was measured (offline; no game, no bridge, no ledger write)

Scripts and outputs: `D:\ClaudeWork\rimmandrake\scratch\lightspeed_census_2026-11-06\` (per-mod table `permod.tsv`).

1. `python3 src/RimMandrake/Utils/testq/coverage.py measure --json` -> 130 harnessed mods: 118 selectable,
   9 steve_missing, 2 load (no `suite`), 1 refused (StarWarsPatches, preview unreadable); 4,456 planned rows.
2. `census_rows.py`: `testq.preview(mod, {"chains": [c]})` for each of the 1,352 chains -> row ids per chain (4,454).
3. `stubs.py`: AST walk of each `validation.py` + `northstar/*.py` for a `with t.component(...)` whose body only
   raises `"UNMEASURED: ..."` (46 stubs in 8 mods); "by eye / look owed / judged / owner" text -> C, else B.
4. `lp.py`: every `^live-proof <clause>:` line (315 in 169 files); those in a file with `live-tier` -> A.
5. `scripts.py`: `proof_*.py`, `prove_*.py`, `*live_proof*.py`, `validation_<x>.py`, `northstar/`, `live_probes/` in
   each mod folder, selftests excluded -> 77 scripts in 30 mods.
6. `walks.py`: `modcheck/northstar.py parse()` over the 95 walk files holding `## north star` -> 374 bars.
7. D: read by hand. A regex over the bars (`fly|flight|airborne`) gave 4 hits, 3 false (an ion bolt "flies", a
   pit jump, a downed span); the walk lines marked "JOINT SESSION ONLY" / "judged only WITH the owner" give the 3.

Sanity probes (every count was checked against an independent route before it was believed):
- harnessed 130 = `ls src/*/*/validation.py | wc -l` (130).
- per-chain rows 4,454 vs coverage's 4,456 (2 rows planned only under the all-chains selection).
- the stub walker finds the known stub `FlowWorks/plot_B_fill_tiers/climbing_gear_look` (True).
- live-proof lines 315 = `grep -c '^live-proof [A-Za-z0-9_]*:'` over the folder (315).
- A from live-proofs = 2: the only files with a `live-tier` line are GIZKA_STOWAWAY_UNMEASURED_ROWS_1 and
  VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL (grep), matching `eligible`'s "exact tier: SteveDesktop runs it" = 2.
- C over live-proof lines read **45 then 0**: my first regex matched `claude` inside every `D:/ClaudeWork` path.
  Fixed; C for live-proof lines is 0 by command text. Not proven: a line that calls `northstar_driver/cli.py run` on a
  plan with `shows=` bars exits non-zero until `judge_cli.py` writes a verdict, so a few of the 313 B lines may hide a
  C half. They are counted B.
- Known undercount in C: rows whose visual half is a `shows=` bar are counted once as A (state) and once per bar in
  C only when the bar is in a walk file; `shows=` lists outside walks (4 files) are not added.

## 3. GSS as the test case

GimmeSomeSlack is the right first case: its whole proof is one script (`northstar/proof_all.py --live`, 119 rows,
420 s on 2026-10-16), the last full result is 70 GSS commits old (`git log --since=2026-10-16T19:25 --
src/RimMandrake/GimmeSomeSlack`), and its modcheck suite cannot prove it (13 rows read UNMEASURED by design,
"measured only by proof_all.py --live").

**Step 1. Wire it.** Add `GimmeSomeSlack` to `src/RimMandrake/Utils/testq/wired_mods.json` (`mods` + a dated `wired`
line); `coverage.py check` must still exit 0 (its probe already reads selectable: 3 chains, 43 rows). This alone gets
the 30 A rows (offline O1-O8, live_battery) onto every gap fill.

**Step 2. A job type for the real proof.** Use the exact-tier route that exists (`profile tier:gimmesomeslack`,
selector `proofs`), not a new worker mode. Write `infrastructure/state/live_proofs/GSS_LIGHTSPEED_PROOF_ALL.txt`:
`live-tier: gimmesomeslack` and one line running
`python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live --no-shots --out <attempt dir>` then
`modcheck/cli.py record GimmeSomeSlack --result <that json> --tier gimmesomeslack`. Three changes make it a
Lightspeed job:
- **Row mapping.** `run_proofs` today makes one row per clause from the exit code. Add: when the line prints
  `ROWS_JSON <path>`, the worker reads that file and emits each row (`chain` = the proof_all block, `row` = its id,
  `verdict` = its status). proof_all writes `rows` already; it gains one print. The clause row stays as the summary.
- **Exit codes.** proof_all returns 1 for FAIL *and* UNMEASURED (`main()`: `bad = FAIL or UNMEASURED`), so the
  2026-10-16 result (118 PASS, 1 UNMEASURED) would read FAIL. Return 2 when nothing FAILed.
- **S12d.** The one standing UNMEASURED row (`S12d_D4_pending_queue_save`, "measured by validation_style.py --live
  --save") gets its own clause on the same file, so the job is green-able.
The job carries the sha: the worker runs at the pinned clone's `source_sha`, so the dated result is per commit.

**Step 3. The mod list.** The tier is `modset_builder.py` `gimmesomeslack` (BRIDGE + `mandrake.rm.gimmesomeslack`,
its closure, all five DLC; refuses Invisible Conduit Continued). The 2026-10-16 run held third-party
`vfe.insectoid2`, absent from Steve's MINIMAL list; that dependency was retired on 2026-10-18 and today's probe shows
no missing dependency, so the expectation is "nothing to copy". Proven only when `tier_load.py check --tier
gimmesomeslack` on SteveDesktop reads exact. P1 loads the clean saved site `calm` (`RM_TestSite_calm_v1`,
`modcheck/test_site_saves.py`): that save must exist on SteveDesktop, and the offline gate calls `wsl.exe python3`
(numpy, the C# SelfTest), so Steve's WSL must hold numpy. Both are first-run checks, not assumptions.

**Step 4. SteveDesktop, not Archmagi.** Exact-tier jobs run only on SteveDesktop (schema rule, owner by card
2026-11-05). Archmagi keeps the owner's list and its bridge for agents; `archmagi_switch.py` S3 already refuses
filler on it. A 7-minute GSS job is one train stop.

**Step 5. Relentless criteria get verdicts from Lightspeed rows.** A Relentless criterion that a proof_all row
decides names it on its proof line, e.g. `live-proof A1: lightspeed GimmeSomeSlack proof_all B6_tangle_lit_strips`:
"the newest Lightspeed row with that id, on a sha at or after the item's built sha, PASS". The round reads testq
results instead of staging a game; no row on a new enough sha -> it submits the GSS job and waits. The 10 GSS items
that run `proof_all.py --only` or `validation_aerial.py` themselves today (GSS_WATER_STUB_FIX_PASSED_LAST_WEEK,
GSS_SWITCHES_PROVE_LAST_FOUR_STANDING, ...) move to this form where a proof_all row covers them; the rest stay
exact-tier lines of their own.

**Step 6. Generate the missing live_proofs for built GSS items.** By id prefix (GSS/MESSY/SLACK/CORD), 7 built items
owe 11 live criteria with no proof line: MESSY_CONDUIT_MOD_1 (A1, A2), MESSYCONDUIT_CABLE_PILE_LOOK_1 (A2, A3),
MESSYCONDUIT_REVIEW_ROUND1_1 (A1, A2), CORD_GRAPH_TOPOLOGY_REVISION_1 (A2), SLACK_LOOP_REDRAW_STANDS_UP_IN_PROFILE
(A1, A2), GSS_RESTRING_FIX_STYLES_UNRECONCILED (A1), GSS_CORD_SWAY_TAME_PER_FRAME_ALLOC (A2). For each: map the
criterion text to proof_all row ids (a script: criterion prose vs the row table in
`design/RimMandrake/gimmesomeslack_verification_consolidation_2026-10-05.md` section 3, a human-checkable list), write
a `lightspeed` line; a criterion that is a look (CABLE_PILE_LOOK) gets an owner-look line, not a fake proof.

**Acceptance.**
1. A dated GSS proof_all result on the current sha from a testq job, no LLM in the path (the job's attempt dir holds
   `result.json` with 119 mapped rows plus `source_sha`).
2. Then one per GSS commit: testq's filler queues the GSS job when `git log -1 -- src/RimMandrake/GimmeSomeSlack`
   is newer than the newest result. Measured as "GSS commits without a Lightspeed result within 2 h" = 0 over a week.
3. Every GSS Relentless criterion with a `lightspeed` line closes or fails from a row, never from a staged round.

## 4. Rollout after GSS (rows unlocked per day of work)

| # | unit | rows / units unlocked | work | per day |
|---|---|---:|---|---:|
| 1 | Queue the 112 selectable-but-unwired mods (A not being run): extend `wired_mods.json` in `coverage.py rank` order, ~15 mods a batch, `coverage.py check` + one filler cycle between batches | 2,966 rows | 1 day (config; watch INVALID share) | ~3,000 |
| 2 | Make the Relentless round a testq client for every `live-proof` line, not only `live-tier` ones: infer a tier per file from `live-mods`, submit `tier:` jobs | 313 lines | 2-3 days (relentless_game.steve_sync already does it for 2) | ~120 |
| 3 | Steve's missing mods: per-mod tiers carrying `sarg.alphaanimals` + `mlie.starwarsanimalcollection` (LeaningScrub 111, WeepingStones 70), `vanillaexpanded.vfefactory` (WreckedMachines 31), the Armoury pair (33), `sarg.alphavehiclesneolithic` (25); copy by `sync_test_mods.py` | 290 rows | 2 days | ~145 |
| 4 | The `ROWS_JSON` contract for the other 72 standalone scripts (FlowWorks 26 incl. `proof_hose.py`; Stillsand 8; BlueDesert 5; LongShade 4): one print each plus a proof file | 72 scripts (rows: hundreds; uncounted) | 3 days | ~25 scripts |
| 5 | Proof lines for the 882 owed criteria: generate from the mod's suite where a row id matches the criterion, lint at filing | 882 criteria | 4-5 days | ~180 |
| 6 | Write the 42 "live check owed" stubs (FlowWorks 28) and a `suite` for DeepDrill and TileFeatures | 44 | 5+ days | ~8 |

Order is rows per day, except that #5's yield is an estimate (how many criteria a suite row matches is unmeasured)
and #1 must go in batches: testq's own UNMEASURED share (~30%, scored.md) rides along with every mod it wires.

## What this doc does not do

It changes no code, queue, ledger or game. Owed filings from it (for the next seat; this brief forbade ledger writes):
the proof_all exit-code conflation (step 2), the `ROWS_JSON` worker change, the GSS Lightspeed proof file, and the
112-mod wiring batches.
