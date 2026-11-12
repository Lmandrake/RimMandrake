# RimMandrake verification and validation: every scheme, 2026-11-12

Item: RIMMANDRAKE_INVENTORY_VALIDATION_SCHEMES_BEFORE_ANY_LADDER (inventory first, ladder argued with Mandrake afterwards).
Written by a detached BENCH helper, 2026-11-12 10:22 to about 11:00 PST. Read-only: no game, bridge, SteveDesktop queue
or ModsConfig was touched.

**How to read the tags.** `[measured: <source>]` means I read the number from that file or command today.
`[measured there: <doc>]` means an earlier report measured it and I did not re-measure. `[guess ~N%]` is my
confidence. `UNMEASURED` means no record was found. A code commit date is never used as a "last ran" date.
Where a run record lives only in one clone or on SteveDesktop, the row says so.

Paths: the repo is `D:\Luke\dev\RimMandrake` (read-only mirror; my clone is the same tree); agent storage is
`D:\ClaudeWork\rimmandrake`. Inside the table, `Utils\` means `D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\` and
`rimflow\` means `D:\Luke\dev\RimMandrake\src\RimMandrake\rimflow\`.

---

## 0. The short version

1. **55 schemes in six stages** (design, code, offline algorithm tests, in-game acceptance, look, owner), counted
   one row each in section 1 `[measured: this table]`. By status: 39 LIVE, 11 DORMANT, 3 STOPPED with Relentless,
   1 DEAD in practice, 1 designed and never built. Of the 39 LIVE, 7 run only when an agent remembers or exist only as
   a rule or text, and 2 are switched on in code but do nothing in effect (the known-red list and the self-test cache).
2. **Two different ladders share the word GREEN.** RimFlow's seven levels (`L0, L1, L2, GREEN-MIN, GREEN-FULL,
   L3, L4`, in `rimflow\model.py` line 327) and the north-star rungs (`DRAFT, VALIDATED, WIRED, GREEN minimal,
   GREEN full, SHIPPED`, in `design\RimMandrake\debug_process.md` §6a). A third, `infrastructure\VALIDATION_LADDER.md`,
   has only L0 to L4 with no GREEN rungs. See section 2.
3. **The nightly self-test sweep has been RED on every one of the 29 nights in its log** `[measured:
   Transient\selftests_nightly.log in the bench clone]`. Last night: 1,531 of 1,586 passed, 41 failed, 3 crashed,
   48 minutes wall. The known-red list meant to make a new red stand out applied to 0 tests last night.
4. **Most live rows still come back UNMEASURED.** Over the last 7 days, the proof-cost ledger counts 191 live rows:
   25 PASS, 9 FAIL, 157 UNMEASURED `[measured: rimflow\proof_cost.py throughput --hours 168]`.
5. **The cheap offline algorithm tests are the healthiest thing in the system.** 61 mods have a C# `Kernel`
   folder; 72 fuzz/kernel tests ran in last night's sweep and 71 passed. FlowWorks has a separate offline C# test
   program with 1,287 checks, all passing. This is where "test the geometry" lives.

---

## 1. The table, one row per scheme

Columns: **Stage** · **Needs** (no game / game minimal list / game full list; machine) · **LLM** (none / to run /
to judge) · **Cost** per run · **Trigger** · **Entry point** · **Last evidence it ran** · **Reach** (how many mods or
items) · **Status** (LIVE / DORMANT / DEAD / DESIGNED-NEVER-BUILT / STOPPED = stopped with Relentless on 2026-11-06).

### 1A. Design stage: deciding what "right" means before code

| Scheme (aliases) | What a pass proves | Needs | LLM | Cost | Trigger | Entry point | Last evidence | Reach | Status |
|---|---|---|---|---|---|---|---|---|---|
| **North-star checklist** ("north star", "bars", the walk's `## north star`) | Nothing by itself: it is the list of what the player must and must never see, that later proofs are scored against. VALIDATED means Mandrake signed that exact text (hash-bound) | no game | to draft (agent); owner or a judge agent to validate | owner minutes per mod | Designer or builder writes; owner validates (`modcheck validate`), or `--delegated` judge binds new bars | `design\validation_walks\<tier>\*.md`; `Utils\modcheck\cli.py validate` | walks committed through 2026-11 `UNMEASURED per file` | 94 walks `[measured: grep '^## north star', 97 files less 1 template and 2 items]`: 86 DRAFT, 8 VALIDATED `[measured: same]` | LIVE |
| **Designer concept tree + coverage judge** ("tree", "leaves", "stage 5") | A fresh Opus that did not make the tree agrees the tree, sheet and scenes cover the concept | no game | to judge | one Opus run `UNMEASURED $` | Designer stage 5 | `rimflow\coverage_judge.py`, `rimflow\designer_stage.py` | `UNMEASURED` (no run log found) | 5 trees, 116 leaves; 2 verdicts, both "not covered" `[measured there: production_system_map_2026-11-12.md §4]` | DORMANT `[guess ~70%]` |
| **Artisan bars** | The owner would accept the mod's quality | judged only by the owner's look | none to run; owner judges | owner time | Artisan loop | `design\RimMandrake\...` per mod (Pyrelands 22, GSS 11, Graffiti 22, FlowWorks 30 bars `[measured there: production map §4]`) | `UNMEASURED` | 4 mods | LIVE as text; nothing automatic reads it |
| **Relentless acceptance exam** (Setter / exam / VALIDATE) | Before the build, a Setter who is not the builder writes checks that must go RED on the base sha (or green on base and red under a planted break); the supervisor checks this mechanically | no game (box) | to write (Opus Setter); mechanical validate | `UNMEASURED` | Relentless, per item | `rimflow\relentless_exam.py` | last exam written 2026-11-06 18:20 `[measured: \home\mandrake\rm\relentless\store\exams, 102 files]` | 102 items | STOPPED |
| **Extended concerns** (`## extended`, mod-mod compatibility, removal from a save) | Only on request: what ordinary Utinni play never meets | game | none | `UNMEASURED` | on request | the walk's own flags (e.g. `validation.py --removal-check`) | none | per-walk flags only | flags per walk `UNMEASURED`; the never-built `modcheck run --extended` design DELETED 2026-11-12 (owner pick 13) |
| **Player-truth sweep** | A list of player-obvious truths (ladders face the wall they lean on, a pit prisoner can walk around) checked offline | no game | to write the truths | `UNMEASURED` | one pilot | `design\RimMandrake\player_truth_testing_pilot_2026-10-26.md` | 2026-10-26: 19 truths, 1 violation class filed `[measured there]` | 1 pilot | DORMANT |

### 1B. Code stage: checks on code and XML, no game

| Scheme (aliases) | What a pass proves | Needs | LLM | Cost | Trigger | Entry point | Last evidence | Reach | Status |
|---|---|---|---|---|---|---|---|---|---|
| **Targeted self-tests before a commit** (`--only`) | The tests for what you changed still pass | no game; any clone | none | seconds to minutes | agent habit (CLAUDE.md "before a commit") | `Utils\run_selftests.py --only <tests>` | `UNMEASURED` (no central record of `--only` runs) | all | LIVE as habit |
| **Nightly full self-test sweep** (L0 sweep) | Every `selftest_*.py` in the repo still passes | no game; Archmagi, `rm-harness.slice`, 6 workers | none | 2,913 s wall last night `[measured: Transient\selftests_nightly.last]` | timer `rm-selftests-nightly` 03:00 + catch-up timer | same, `--nightly` | 2026-11-12 03:00 to 03:48: PASS 1,531 / FAIL 41 / UNMEASURED 8 / CRASH 3 / SKIPPED 3 of 1,586 `[measured]` | 1,586 test files repo-wide | LIVE, RED 29 of 29 logged nights `[measured: grep RESULT in selftests_nightly.log]` |
| **Known-red list** | A red on the list is old news; any other red is news | no game | none | inside the nightly sweep | inside the nightly sweep | `Utils\known_reds.py`, `rimflow\selftest_known_reds.json` | last night: "0 known red" `[measured: selftests_nightly.last]` | 0 tests applied | LIVE in code, empty in effect |
| **Skip-when-unchanged evidence** (suite cache) | A test may be skipped only if its last fully traced run passed and every input is byte-identical | no game | none | saves time when used | inside the nightly sweep | `Utils\suite_evidence.py`, `Utils\known_results.py`, `Utils\suite_trace\` | last night: "0/1583 answered from the ledger" `[measured]` | 0 | LIVE in code, unused in effect |
| **Def and patch linters** (`lint_<mod>_defs.py`, `moddefs_lint`, `effective_def_lint`, `check_config_errors`, `no_duplicate_defs`, `lint_harmony_targets`, `naming_lint` ...) | XML is well-formed and refers to things that exist; mod-specific rules hold | no game (def dump) | none | 61 lint rows, 1,119 s total last night `[measured: selftests_nightly.last]` | inside the nightly sweep; agent habit | `Utils\lint_*.py` (62 files `[measured]`) | 2026-11-12 nightly | 62 linters | LIVE |
| **Patch validation against defs** (`validate_patch.py --live --defs`, `measure`, RimSage) | A patch's xpath matches real defs in the frozen or live dump | no game; dump must match the live mod set | none | seconds | agent habit at deploy (rimworld-deploy skill) | `skills\rimworld-modding\scripts\validate_patch.py`; `measure count <DefType>` | `UNMEASURED` (no run log) | any mod with patches | LIVE as habit |
| **Code review to CLEAN** (CLEAN / DIRTY / ORPHANED) | A full-file review found nothing since the file's content last changed | no game | to review (agent reads the file) | one review read per file `UNMEASURED tokens` | rule "code isn't clean until a review says so"; nightly review waves | `Utils\code_review_status.py check|mark-clean|list` | 14,673 review events, newest 2026-11-12 08:58 `[measured: infrastructure\state\code_review\*.jsonl]` | tally CLEAN 5,188 / DIRTY 1,561 / ORPHANED 174 `[measured: code_review_status.py list]` | LIVE |
| **GPT adversarial review** (chatgpt-consult, "GPT round", "second opinion") | An independent model found no defect in a design or diff | no game | to run and to judge (GPT via Codex) | `UNMEASURED $`; one call logged 11,245 tokens | agent habit; the skill says on any evidence-machinery change | `Utils\gpt_consult.py`, `Utils\gpt_consult_rounds.py` | call log `D:\ClaudeWork\rimmandrake\arena\gpt_calls.jsonl` holds 65 calls, newest 2026-11-01 `[measured]`; dozens of `*gpt*` review docs exist, so the log is incomplete `[guess ~80%]` | many designs | LIVE, instrument incomplete |
| **Hooks that refuse forged or blind evidence** (`block_forged_validation`, `block_blind_scan`, ledger lint, DLL source mismatch ...) | An agent did not hand-write the owner's validation, scan a large artifact blind, or commit a DLL without its source | no game | none | milliseconds | every tool call | `.claude\hooks\block_*.py` (both registered `[measured: 2 matches in .claude\settings.json]`) | `UNMEASURED` (refusals not tallied here) | all agents | LIVE |
| **Hand-planted mutant self-tests** (`*_mut.py`, `*_mutants.py`, the mutate-your-checker skill) | A checker goes red when a fault is planted and stays green on good input | no game | none | 18 rows, 1,156 s last night `[measured]` | inside the nightly sweep | e.g. `Utils\selftest_close_evidence_mut.py`, `rimflow\selftest_validator_mutants.py` | 2026-11-12 nightly | 18 checkers | LIVE |
| **mutmut mutation testing** | The tests for decision and evidence machinery kill at least 85% of automatic mutants (full runs only) | no game; SteveDesktop idle CPU | none | 32.3 CPU-hours for 12 module runs, 2026-10-27..28 `[measured there: testing_policy_2026-10-28.md §1]` | `run_mutation.py nightly` (no timer found on Archmagi `[measured: systemctl --user list-timers]`); gated by `testing_policy.json` (3 stable days, review CLEAN) | `Utils\mutation\run_mutation.py` | newest record on `D:\ClaudeWork\rimmandrake\mutation\steve` is 2026-10-28 09:44 `[measured]`; SteveDesktop's own disk not checked | 5 risk classes (dispatcher, close_evidence, account_plan, gates, graders) | DORMANT since 2026-10-28 `[guess ~75%]` |
| **Validator replay bank** | The real supervisor transitions classify and route known good and bad cases correctly | no game | none | inside the nightly sweep | inside the nightly sweep | `rimflow\validator_replay.py`, `rimflow\selftest_validator_replay.py` | 2026-11-12 nightly | Relentless supervisor | LIVE as a test of a STOPPED system |
| **Process simulations** (testing-investment Monte Carlo, Test Pilot sim, RimFlow v3 sim, fan-out sim) | A proposed process change pays off in a model of the pipeline (not the game) | no game | none | seconds | owner request | `Utils\sim\*.py` | 2026-10-27 testing-investment report `[measured there]` | process only | DORMANT (one-off studies) |

### 1C. Algorithms tested outside the game

| Scheme (aliases) | What a pass proves | Needs | LLM | Cost | Trigger | Entry point | Last evidence | Reach | Status |
|---|---|---|---|---|---|---|---|---|---|
| **C# kernels with seeded fuzz** ("test the geometry", "kernel", "Approach B fuzz", DLL-side tests) | The shipped pure-logic C# (the same `.cs` files the DLL compiles) holds stated invariants over thousands of seeded cases; a failing case is shrunk and replayable | no game; `dotnet.exe` on Windows via `winbuild.stage_build` | none | 72 fuzz/kernel rows, 2,572 s total last night; 0.1 s to 173 s each `[measured]` | inside the nightly sweep; per kernel change | `Utils\selftest_<mod>_fuzz.py` (66 files `[measured]`), `<Mod>\Source\Kernel\*.cs`, `<Mod>\Source\SelfTest\Fuzz\` | 2026-11-12 nightly: 81 PASS, 1 UNMEASURED among matching rows `[measured]` | 61 Kernel folders `[measured: find -name Kernel]` | LIVE |
| **FlowWorks offline C# test program** (in-assembly "SelfTest", HoseTickAllocChecks ...) | Engine-side FlowWorks rules (stock model, hoses, pits, heat budget, gates) hold, compiled outside the game | no game; dotnet | none | 711.7 s last night `[measured]` | inside the nightly sweep | `src\RimMandrake\FlowWorks\Source\SelfTest\` (156 check files `[measured]`), wrapper `Utils\selftest_flowworks_stock.py` | 2026-11-12: "1287/1287 passed" but the harness filed it UNMEASURED because the output also prints the unmeasured phrase `[measured: selftests_nightly.last line 2801]` | FlowWorks (and GSS hose suites moved into it) | LIVE, mislabelled |
| **Other per-mod C# SelfTest projects** | Mod logic in a console program | no game; dotnet | none | `UNMEASURED` per project | via each mod's Python selftest wrapper | 94 `SelfTest` folders in 79 mods `[measured: find -iname '*selftest*' -type d]`; 104 test or kernel `.csproj` | 2026-11-12 nightly, via wrappers | 79 mods | LIVE |
| **Shared geometry libraries with their own tests** (GSS cord geometry, A* cord planner) | Cord routing, sag and draw order behave | no game | none | 0.1 s (internal) `[measured]` | inside the nightly sweep | `src\RimMandrake\_Shared\SlackGeometry\selftest_*.py` | 2026-11-12 nightly PASS | GSS, FlowWorks hoses | LIVE |
| **Planted-bug checks for the fuzzers** (`mutate_<mod>_fuzz.py`, `mutations_*.json`) | The fuzz test goes red when a known bug is planted in the kernel, and the kernel is restored byte-identical | no game; dotnet | none | about 4 s wait plus one fuzz run per mutation | by hand only: nothing calls them `[measured: no reference outside the scripts themselves]` | `Utils\mutate_*_fuzz.py` (49) and `Utils\mutations_*.json` (11) `[measured]` | `UNMEASURED` | 49 mods | LIVE as habit, unrecorded |
| **C# ↔ Python parity vectors** | A rule coded twice (C# in game, Python in the harness) gives the same answers on fixed vectors | no game | none | inside the nightly sweep | inside the nightly sweep | `Utils\conds_vectors.json`, `Utils\selftest_conds_vectors.py`, `rimflow\selftest_fakeworld_parity.py` | 2026-11-12 nightly | condition DSL, fake world | LIVE |
| **Offline world, art and map models** (worldview, rimbench map painter, art zoom sim, patch sim, tree-shade estimate) | A world, map or art rule looks right or computes right before the game sees it | no game | sometimes to judge a picture | seconds | agent habit | `Utils\worldview.py`, `Utils\rimbench\`, `Utils\art_zoom_sim.py`, `Utils\patch_sim.py`, `design\RimMandrake\tree_shade_model_2026-10-19_estimate.py` | `UNMEASURED` | world, art | LIVE as habit |
| **Shipped-settings fuzz matrix** ("V&V pilot 1") | FlowWorks and EmpirePursuit property families at the shipped settings, with honest failure rates | no game | none | `UNMEASURED` | one pilot | `Utils\vv_shipped_matrix.py`; report `design\RimMandrake\vv_methods\pilot1_shipped_matrix_2026-10-16.md` | 2026-10-16 `[measured there]` | 2 mods | DORMANT |

### 1D. In the game: load, behaviour, north star (L1, L2, GREEN-MIN, GREEN-FULL)

| Scheme (aliases) | What a pass proves | Needs | LLM | Cost | Trigger | Entry point | Last evidence | Reach | Status |
|---|---|---|---|---|---|---|---|---|---|
| **Load checks** (L1 "resolved-live", Player.log first exception, load sweep) | The mod list loads; defs resolve in the real engine | game minimal or full list | none | 22 s (13-mod list, Archmagi), 54 s (SteveDesktop), 15 to 25 min full list `[measured there: live_test_speed_assessment §2D]` | before every live proof; biome load proofs | `Utils\check_load.py`, `Utils\live_log_check.py`, `Utils\loadsweep\biome_load_proof.sh`, `Utils\game_health_check.py` | `UNMEASURED` centrally; each testq job loads | all mods | LIVE |
| **L1 expectations manifests** ("one manifest format, one runner") | Every def an item promised exists live, read by `jawa/get_defs` | game minimal list; Windows Python | none | one bridge call per criterion | build items under MASS_VALIDATION_LADDER_1 (mass-built content checks) | `Utils\expectations_manifest.py`, `Utils\run_expectations.py`, `Utils\l1_live_runner.py` | `UNMEASURED` run; 4 manifests, last changed 2026-11-02 `[measured: git log]` | 4 items | DELETED 2026-11-12 (owner pick 6; runner, batch generator and the 4 manifests gone; `expectations_l2.py` kept, art_fold_live drives it) |
| **A mod's functional script** (`validation.py`, "the mod's script", chains and components) | Each basic function of the mod works once, row by row, PASS / FAIL / UNMEASURED | game, the mod's small tier (all five DLCs); bridge; Windows Python | none to run | minutes per mod `UNMEASURED` per mod | builder habit; modcheck run; testq job | `src\<tier>\<Mod>\validation.py` | per mod; see the modcheck row for the record | 137 files in 131 mod folders `[measured]` | LIVE |
| **modcheck run / record / status** (mod GREEN or RED) | The mod's script passed every row on the declared tier at this mod hash | game | none | as a mod script; `modcheck run` also rewrites the live ModsConfig | builder or Conductor; testq `modcheck` jobs | `Utils\modcheck\cli.py`, `infrastructure\state\modcheck_status.json` | newest record 2026-11-06 (Contagion, RED) `[measured]` | 71 mods: 62 RED, 6 GREEN (all six dated 2026-10-05..07), 3 DRAFT-CHECKLIST `[measured]` | LIVE but stale |
| **Validity floor** (`modcheck floor`, WIRED rung) | Every must-show and cannot-show line of the north star is claimed by a component's `shows=`; nothing orphaned | no game | none | seconds | before a north-star run | `Utils\modcheck\floor.py` | `UNMEASURED` | 3 of 110 `validation.py` carried `shows=` on 2026-10-03 `[measured there: debug_process.md §6a]` (few) | LIVE, thin |
| **Per-mod north-star suites** (`<Mod>\northstar\`, `proof_all.py`, `proof_hose.py`, `validation_v2.py`, `hose_replay.py`) | Dense row-by-row proofs of the mod's bars in the live game | game small tier; FlowWorks often on SteveDesktop | none to run | GSS `proof_all`: 670.6 s / 146 rows (139 PASS) before, 686.8 s / 145 rows after, today on SteveDesktop `[measured: speed_20261112\results.md]`; FlowWorks pit exposure 465 to 529 s `[measured there]` | builder; testq; Conductor helpers | e.g. `src\RimMandrake\FlowWorks\northstar\` (448 files), `src\RimMandrake\GimmeSomeSlack\northstar\proof_all.py` | 2026-11-12 (GSS, FlowWorks pit, on SteveDesktop) `[measured]` | 7 mods have a `northstar\` folder: Cauldron, DivingInteraction, FlowWorks, GelatinousSlime, GimmeSomeSlack, HugeThings, LeaningScrub `[measured]` | LIVE |
| **Generic north-star driver** (GREEN-MIN / GREEN-FULL; preflight; judge for frames) | Every expected bar PASS on the minimal (or full) list; UNMEASURED is not green | game minimal or full list | none to run; to judge must-show frames (`judge_cli.py`) | minutes per mod `UNMEASURED` | builder or acceptance sitting | `Utils\northstar_driver\cli.py`, `...\judge_cli.py` | newest results file 2026-10-19 (Cauldron) `[measured: bench clone Transient\northstar\, 11 files]` | `UNMEASURED` | DORMANT `[guess ~70%]` (code still edited 2026-11-12) |
| **Per-item live-proof lines** | One item names the exact command that would prove each live criterion; exit 0 PASS, 1 FAIL, else UNMEASURED | game, tier per line | none | per line | written at build; linted at filing | `infrastructure\state\live_proofs\<ID>.txt`, `rimflow\lightspeed_wire.py lint`, `Utils\northstar_bar_proof.py` | newest commit 2026-11-12 `[measured: git log]` | 409 items `[measured: ls]` | LIVE |
| **Test queue = Lightspeed lane** ("testq", "the no-LLM lane", RUNNER verify events) | A committed script ran against the live game at a named sha, with no language model staging or judging; rows land as verify events | game, SteveDesktop (Archmagi under `archmagi_switch.py` rules) | none | median 71 s run plus about 140 s fixed cost per job (copy 89 s, fingerprint 51 s) `[measured there: live_test_speed_assessment §2C]` | timers `testq-tick` (about every 90 s; service shows "failed" today), `testq-steward-watch`, `testq-sweep` 01:30 (FlowWorks only by default) `[measured: systemctl]` | `Utils\testq\testq.py`, worker `infrastructure\stevedesktop\worker.py` | 853 jobs done 2026-10-26..2026-11-12, newest J20261112T153603Z `[measured: D:\ClaudeWork\rimmandrake\testq\done]`: 736 DONE, 106 INVALID, 6 REFUSED, 5 INTERRUPTED; 815 "targeted", 4 full-list | 30 mods, but FlowWorks is 733 of 853 jobs (86%) `[measured]` | LIVE |
| **Relentless live round** (game_prove lane, "acceptance sweep for every mod") | Every built item with a written proof for an owed live criterion gets its proof run, several per sitting | game; bridge as RELENTLESS | to stage and route (agents in the loop) | `UNMEASURED` | Relentless | `rimflow\relentless_live_round.py`, `rimflow\relentless_live.py` | `live_round.json` last written 2026-11-06 18:05 `[measured]` | `UNMEASURED` | STOPPED |
| **Relentless Marker blind check** (box run; proof_weak, proof_rework, blind_fail) | A Marker who did not build the work runs the proof in a walled box and judges whether it measures the clause | no game for box runs; game for live clauses | to judge | `UNMEASURED` | Relentless, per close | `rimflow\relentless.py`, `rimflow\relentless_boxrun.py`, `rimflow\relentless_wall.py` | 3 box runs, all on 2026-11-06 `[measured: store\boxrun.jsonl]` | `UNMEASURED` | STOPPED |
| **Close gates on the ledger** (close evidence, evidence gate in SHADOW, live promise, dead-man) | A close has machine evidence at this exact sha; an operational fix is still running | no game | none | milliseconds | every `rimflow close`; `rm-deadman` timer | `Utils\close_evidence.py`, `rimflow\evidence_gate.py`, `rimflow\live_line.py`, `Utils\deadman_check.py` | evidence gate: 231 shadow records, newest 2026-11-12 17:01 UTC `[measured: store\evidence_shadow.jsonl]`; dead-man ran 2026-11-12 10:18 `[measured: systemctl]` | every item | LIVE (evidence gate in shadow only) |
| **In-game C# proof classes and scenes** (`RM_*Proof`, scenelib, scenarios) | A scene staged, ticked and judged inside the game, in one call | game; rebuild per change | none | Knockback scene 31 s, of which 0.5 s in C# `[measured there]` | builder | 108 `.cs` files with `class RM_*Proof` `[measured]`; `Utils\scenes\scenelib.py`, `scenarios.py`; 15 `*_scene*.py` | `UNMEASURED` centrally | about 108 classes | LIVE, no shared shape |
| **Tick-speed equality** (tickbench, tickburst) | The fast many-ticks-per-frame advance gives the same verdicts as one-tick-per-frame stepping | game | none | today: pit exposure 457 s slow vs 63.8 s fast, all four verdict rows equal `[measured: speed_20261112\results.md]` | speed work | `Utils\tickburst_bench.py`, `Utils\tickburst_step.py` | 2026-11-12 on SteveDesktop (pit only); `tickburst_bench --arms` never run live `[measured there]` | 1 proof so far | LIVE, one data point |
| **Proof cost ledger** | How many live rows we actually measure per hour, and what they cost | no game (reads records) | none | seconds | on request | `rimflow\proof_cost.py throughput` | last 7 days: 191 rows, 25 PASS, 9 FAIL, 157 UNMEASURED; bridge driven 13% of 166.6 held minutes; 349,809 tokens per measured row `[measured: proof_cost.py throughput --hours 168]` | all live work | LIVE |

### 1E. Look: an agent judges how it looks (L3)

| Scheme (aliases) | What a pass proves | Needs | LLM | Cost | Trigger | Entry point | Last evidence | Reach | Status |
|---|---|---|---|---|---|---|---|---|---|
| **Art evaluation pipeline** (art-eval, auto-judge: Opus first, GPT second look, regenerate up to 3 rounds) | A sprite is good enough to show Mandrake | no game (renders) | to judge (Opus, GPT) | `UNMEASURED $` per subject | timer `rm-arteval-autojudge` every 2 h `[measured: unit file]`; per render | `Utils\art_eval\auto_judge.py`, `Utils\art_eval\runner.py` | 332 run folders; newest 2026-11-12 03:07 `[measured: D:\ClaudeWork\rimmandrake\art_eval\runs]`; today's 08:25 pass refused ("gate closed: BENCH already runs 4 helpers") `[measured: arteval_autojudge\status.json]`; 86 follow-ups and 3 installs owed | creature, plant, machine art | LIVE, often gated shut |
| **Offline art checks** (`check_sprite`, `art_checks`, `art_size_audit`, `facing_art_census`, `probe_png_wellformed`, `art_legibility`) | Canvas, alpha, size, facings and legibility rules hold before a judge sees it | no game | none | seconds | builder; partly inside the nightly sweep | `Utils\check_sprite.py`, `Utils\art_checks.py`, ... | 2026-11-12 nightly (the selftest wrappers) | all art | LIVE |
| **Prereview record** | A naive judge read a review sheet before it reaches Mandrake | no game | to judge | one Opus or GPT read | sheet tools refuse without it | `Utils\art\prereview.py`, `<stem>.prereview.json` | `UNMEASURED` | 16 prereview files vs 363 `.decisions.json` sheets `[measured: find]` | LIVE, thin |
| **North-star frame judge** (must-show bar on a screenshot) | A frame shows what the bar says the player sees | game for the shot; judge offline | to judge | `UNMEASURED` | north-star run | `Utils\northstar_driver\judge_cli.py` | "no FlowWorks bar has a judge verdict" `[measured there: production map §7]` | `UNMEASURED` | DORMANT |
| **Naive judge / blind evaluation** ("nothing reaches the owner unread") | A fresh Opus that did not make the thing finds it not obviously broken | depends | to judge | one Opus run | before anything reaches Mandrake | skills `blind-evaluation`, `evaluation-independence`; folders `D:\ClaudeWork\rimmandrake\judge_*` | `judge_levelling_20261112` exists `[measured]` | any deliverable | LIVE as habit |
| **Findings judge** (daily judging, Friday memory sweep) | Filed findings are real, not duplicates, not contradicted | no game | to judge (Opus) | about $1 a run `[measured: findings_judge\history.jsonl]` | timer `rm-findings-judge` 07:20, re-enabled 2026-11-12 (it had been stopped with the pipeline on the owner's order of 2026-11-07, PIPELINE_RETHINK_OWNER_STOPPED_BURN) | `Utils\findings_judge.sh` | run 2026-11-12 23:07-23:16 UTC, rc 0, $2.13 `[measured: findings_judge\last.json]` | the ledger | RUNNING (owner pick 8, 2026-11-12) |
| **Test Pilot** (rm-testpilot, surprise book) | One live debugging sitting on an item that failed 3 times in a row: experiments instead of code-and-retest; the surprise book records what is "boring" where | game; bridge | to run and to judge | one Opus sitting `UNMEASURED $` | `rimflow pilot` route after 3 non-pass runs or a live-only defect | `rimflow\testpilot_route.py`, `.claude\agents\rm-testpilot.md`, `rimflow\surprise_book.py` | newest sitting folder 2026-11-05 11:34; surprise book 2026-11-04 `[measured]` | a handful of items | DORMANT since 2026-11-05 `[guess ~70%]` |

### 1F. The owner (L4)

| Scheme (aliases) | What a pass proves | Needs | LLM | Cost | Trigger | Entry point | Last evidence | Reach | Status |
|---|---|---|---|---|---|---|---|---|---|
| **Owner sittings with setup scripts** ("sitting", showing, staged scene, keeper savegame, "options ship as a savegame") | Mandrake looked and said it is right | game (with the advanced-zoom mod) | none to stage; owner judges | his time; e.g. wall art scene about 247 s of staging, 242 s of it Python waiting `[measured there]` | owner request; Relentless "showings" | `src\RimMandrake\FlowWorks\northstar\wall_art_scene.py`, `Utils\stage_review.py`, `Utils\stage_beast_grid.py`, `Utils\scald_showcase.py`, `rimflow\relentless_showing.py`; standard `design\RimMandrake\biome_review_save_standard.md` | `D:\ClaudeWork\rimmandrake\owner_water_pit_20261112` (before/after files, today) `[measured]` | `UNMEASURED` | LIVE |
| **Review sheets** (keep / cut / rank pages) | His decisions recorded as data | no game | none; prereview before | his time | art and roster reviews | `Utils\art\art_sheet.py`, `serve_gated.py`, `art.py enact` | 363 `.decisions.json` files `[measured]` | art, rosters | LIVE |
| **Owner validates a north star** (`modcheck validate --owner-said`) | He signed that exact checklist text | no game | none | his minutes | sitting | `Utils\modcheck\cli.py validate` | 8 VALIDATED walks `[measured]` | 8 mods | LIVE, rare |
| **Owner reviews a run sheet before first GREEN** (`modcheck review`) | He read a run's sheet with his own eyes | no game | none | his minutes | before a mod's first GREEN | `Utils\modcheck\cli.py review` | `owner_review` empty for all 71 mods `[measured: modcheck_status.json]` | 0 | DEAD in practice (yet 6 mods read GREEN) |
| **Human review map** (labelled staged map he can play in; no verdict) | Nothing recorded; he explores | game | none | his time | sitting | `design\RimMandrake\northstar_human_review.md` (Messy Conduit draft, 2026-10-04) | 2026-10-04 `[measured there]` | 1 mod | DORMANT, draft rules never generalised |
| **Flyer flight with the owner present** | Flight looks right in motion | game; joint session | none | his time | joint session only | none (by rule) | `UNMEASURED` | flyers | LIVE as a rule |

---

## 2. The words: levels and verdicts, where each is defined, and where they disagree

| Word | Defined in | Meaning there | Disagreement |
|---|---|---|---|
| L0 to L4, GREEN-MIN, GREEN-FULL | `rimflow\model.py` line 327 (`LEVELS`), with `LEVEL_NEEDS` beside it | Seven levels in this order: L0 offline · L1 resolved-live, minimal list · L2 behaviour gauntlet · GREEN-MIN · GREEN-FULL · L3 Opus evaluation · L4 human. The cheapest one still owed decides what an item waits for | `infrastructure\VALIDATION_LADDER.md` has only L0 to L4, no GREEN rungs. `model.py` says L3 needs only `bridge`; the addendum says bridge plus an Opus evaluator |
| Same levels | `design\RimMandrake\rimflow_validation_levels_addendum_2026-10-07.md` | As above; adds that FOUNDRY owns acceptance sittings and BENCH only L4 | FOUNDRY is retired (owner, by card, 2026-11-02); the addendum still assigns it acceptance |
| GREEN minimal / GREEN full | `design\RimMandrake\debug_process.md` §6a, the north-star ladder | Rungs DRAFT → VALIDATED → WIRED → GREEN minimal → GREEN full → SHIPPED. SHIPPED needs deploy == repo, Mod Settings, art, and code review CLEAN | A second, different ladder sharing the GREEN words. Here GREEN needs `northstar_driver` results; in RimFlow it is any criterion tagged GREEN-MIN |
| GREEN / RED / DRAFT-CHECKLIST / STALE / ORPHANED | `Utils\modcheck\status.py`, `infrastructure\state\modcheck_status.json` | A mod's last recorded run, tied to the mod hash | Six mods read GREEN with no owner review recorded, although the spec requires one before the first GREEN |
| PASS / FAIL / UNMEASURED per row | proof scripts, testq worker (exit 0 / 1 / else) | UNMEASURED = could not ask the question; never a soft pass | Consistent across code I read. The nightly harness also files a test UNMEASURED when its output merely contains the phrase (the FlowWorks 1,287-check program) |
| INVALID / REFUSED / INTERRUPTED / DONE | testq job results | A whole job outcome, not a row | INVALID is often read as a row verdict in prose; it is not |
| CRASH / SKIPPED | `Utils\run_selftests.py` | Reached no verdict / skipped on unchanged evidence | Nightly calls RED "FAIL 0 and CRASH 0"; UNMEASURED does not make it red |
| PROVEN / WEAK PROOF / NO PROOF | `D:\ClaudeWork\rimmandrake\conductor\proofs_20261112\BRIEF.md` | Per acceptance line: a real start assertion, result and control exist, or not | Each of the four inventories used a slightly different rule `[measured there: production map §4]` |
| proof_weak, proof_rework, proof_unchanged, blind_fail | `rimflow\relentless.py` line 239 | Marker outcomes that send work back to strengthen the proof | Relentless only; stopped |
| built / validated / done / proven / accepted | `rimflow\model.py` states; prose | built = code published, proof owed; validated = at least one live proof passed | "validated" also names an owner-signed north star and a script result `[measured there: production map §7 point 2]` |
| CLEAN / DIRTY / ORPHANED / NEVER ENTERED | `Utils\code_review_status.py` | Reviewed since the content last changed | Consistent |
| Basic checkout / extended | `debug_process.md` §6b (owner, 2026-10-04) | Basic runs every time; extended only on request | Extended runs through each walk's own flags (the verb's design was deleted 2026-11-12) |
| Lightspeed | `design\RimMandrake\lightspeed_2026-11-06.md` | The test queue plus scripts that decide every verdict, no LLM | Not a separate system: it is the name for testq used that way |

---

## 3. Special sections

### (a) Flyers: what can and cannot be tested, and how

- **Rule (owner, said three times, 2026-09-25):** never live-test a flyer's flight without him present, and never
  try to capture images of flight. Encoded in `skills\rimworld-modding\references\flight.md`, in
  `testing_policy.json` (`live.flyer_flight_without_owner` false), and in the bridge gate: `--flyer` or flight
  wording refuses a take `[measured: rimflow\selftest_no_owner_presence.py lines 48 to 125]`. Lightspeed excludes
  flight entirely.
- **Offline, any time, no game:** the def says it can fly (`MaxFlightTime` > 0, cooldowns, no flight on job
  start). Examples: `Utils\selftest_leaftail_flight.py`, `src\RimMandrake\LeaningScrub\selftest_leaningscrub_shirrel_glide.py`
  (each row checked on the real tree and then broken in memory to prove it can fail). Glide logic has a C# kernel:
  `src\RimMandrake\LeaningScrub\Source\Kernel\RM_GlideKernel.cs`. Flip-book frames are checked as art (art evaluation and offline art checks;
  `Utils\art_eval\selftest_flyer_master_record.py`, `Utils\art\selftest_flyer_gate.py`).
- **Live, a state read only:** `jawa/pawn_flight` reads `Pawn_FlightTracker` (`canEverFly`, `maxFlightTimeStat`) on a
  spawned pawn with the game paused and no ticks. Example: `Utils\art\flyer_tier_three_state_read.py` (six flyers).
- **Contradiction found:** that state-read script says it is "live only in a joint session: the Relentless game gate
  holds every flyer for him". So the rule "verify flight by a state read instead" and the gate "hold every flyer
  for the owner" disagree, and today even the paused, no-flight read waits for Mandrake `[measured: its docstring]`.
- **Cannot be tested without him:** flight in motion, take-off and landing behaviour, how it looks in the air.

### (b) Algorithms tested outside the game, and candidates

**Today** (all in the nightly sweep unless noted):

- 61 mods compile their pure C# kernels outside the game and fuzz them (the C# kernel fuzz row). Example: Pyrelands burn line, fire-front
  clock, furnace thermal charge, ash rates: `src\RimMandrake\Pyrelands\Source\Kernel\`, run by
  `Utils\selftest_pyrelands_fuzz.py`, which reads the shipped tuning file so the fuzz cannot drift.
- FlowWorks' 1,287-check offline program (the FlowWorks offline program row): stock model, hoses, pits (`PitAccessChecks.cs`, `PitDeckChecks.cs`),
  heat budget (`HeatBudgetChecks.cs`), a flow-kernel fuzz (`FlowKernelFuzz.cs`).
- GSS cord geometry and A* planner (the cord geometry row). Sun heat and tree crowns: `Utils\selftest_sun_heat.py`,
  `Utils\selftest_tree_crowns_measured.py`. Landform geometry: `Utils\selftest_tilefeatures_landform_geometry.py`.

**Candidates** (live today, could move offline; each `[guess]`):

- **FlowWorks pit exposure heat** (`src\RimMandrake\FlowWorks\northstar\pit_exposure_live.py`, 465 to 529 s a run).
   Today's fast-vs-slow run showed cell temperatures differing by about 0.4 °C with pawn wander RNG and door openings
   `[measured: speed_20261112\results.md]`. The heat exchange per cell is arithmetic and could be a kernel with one
   live row pinning it `[guess ~65%]`.
- **GSS failing geometric rows** in `proof_all.py`: `M2c_no_sharp_bends`, `SC_no_two_cords_alike`,
   `D2_fresh_builder_same` (FAIL today). These read cord shapes the planner produced; the planner is already offline
   (the cord geometry row), so the same assertions could run against `CordPlanner.cs` on fixed layouts in seconds `[guess ~70%]`.
- **Direct Sun and tree shade** (`design\RimMandrake\tree_shade_model_2026-10-19_estimate.py` exists as an estimate):
   a pure function of geometry by the owner's ruling, so ideal for a kernel `[guess ~75%]`.
- **Explosive Knockback push** (`src\RimMandrake\ExplosiveKnockback\proof\storeroom_pit_proof.py`): a fuzz exists
   (`Utils\selftest_explosiveknockback_fuzz.py`); the live scene's 36 tick calls test the same push table
   `[guess ~55% that most of it is redundant with the fuzz]`.
- **Not candidates:** pawn pathing and job choice (pit capture, wander), load-order and patch effects, art in the
   world. These need the engine.

### (c) Live tests: fully scripted versus needing an LLM

| Fully scripted (no LLM to run or judge) | Needs an LLM | Why the LLM is there |
|---|---|---|
| testq / Lightspeed jobs (testq), per-item live-proof lines (live-proof lines), mod scripts and north-star suites when run by testq (mod scripts, north-star suites), load checks (load checks), state reads of flyers, tick equality (tick equality) | Relentless live round (live round): agents stage and route | Staging and routing were done by agents; the 2026-11-06 Lightspeed design moves them to scripts |
| | Marker blind check (Marker) | Judging whether a proof measures its clause |
| | Test Pilot (Test Pilot) | Experimenting on a live defect no script reproduces yet |
| | North-star frame judge (the frame judge), art eval (art evaluation), naive judge (the naive judge) | A picture or a look; no script can say "reads as a dune" |
| | Unhandled testq failure (Lightspeed §1, point 1) | A cause no rule routes wakes a fixer |
| | Owner sittings (owner sittings) | Not an LLM: Mandrake |

The 2026-11-06 Lightspeed census found 93% of 5,225 test units need no LLM `[measured there:
lightspeed_2026-11-06.md]`. Most of the remaining LLM use is judging a look, not running a test.

---

## 4. Observations (overlaps, gaps, schemes that look dead)

**Overlaps**

- Two ladders share "GREEN" (RimFlow levels vs north-star rungs), and a third doc (`infrastructure\VALIDATION_LADDER.md`)
   has neither GREEN rung. One item can be "GREEN-MIN passed" in RimFlow while its mod is RED in modcheck.
- Three "judge a proof" systems: the Relentless Marker (stopped), the evidence gate (shadow), and the Conductor's
   PROVEN / WEAK / NO PROOF audit (manual, today). They ask nearly the same question with different rules.
- Two mutation families that do not know each other: mutmut on decision machinery (mutmut) and hand-planted bugs for
   fuzzers (planted-bug fuzz checks) plus `*_mut.py` checkers (hand-planted mutant tests). Only those run on a clock.
- Owner-look staging lives in at least five places (mod `northstar\` scene scripts, `Utils\stage_*.py`,
   `Utils\scenes\`, `relentless_showing.py`, savegame standards).

**Gaps**

- **Nothing turns the nightly RED into news.** RED 29 of 29 nights; the known-red list applied to 0 tests; the
   skip-when-unchanged cache answered 0 of 1,583.
- **Most live rows measure nothing.** 157 of 191 rows UNMEASURED in 7 days; 106 of 853 testq jobs INVALID.
- **Test queue reach is narrow.** 86% of testq jobs are FlowWorks; the nightly sweep timer defaults to FlowWorks only.
- **GREEN without the owner.** Six modcheck GREENs, all from 2026-10-05..07, none with the owner review the spec
   requires; no modcheck record newer than 2026-11-06.
- **Flyer state reads are held for him** although the rule says a state read is the way to avoid needing him.
- **Offline candidates** listed in 3(b): the GSS geometric FAIL rows and the pit heat model are the cheapest wins.
- **Instruments with holes:** the GPT call log stops at 2026-11-01 while GPT reviews continue; the FlowWorks offline
    program is filed UNMEASURED while all 1,287 checks pass; the testq tick service reads "failed" while its timer runs.

**Dormant, stopped, or never built**

- STOPPED with Relentless on 2026-11-06: exam (exam), live round (live round), Marker (Marker). Their self-tests still run nightly.
- DORMANT: mutmut (last record 2026-10-28), generic north-star driver (last results 2026-10-19), L1 expectations
    manifests (4 items; deleted 2026-11-12), Test Pilot (last sitting 2026-11-05), findings judge (re-enabled 2026-11-12,
    owner pick 8), player-truth sweep, V&V shipped matrix, frame judge, human review map.
- DESIGNED-NEVER-BUILT: the shared in-game C# scene runner (fast-testing step 8); the
    bridge validation observatory (`design\RimMandrake\bridge_validation_observatory.md`, "Nothing is built").
- **Stale text that disagrees with the code:** the levels addendum and `testing_policy_2026-10-28.md` §2.10 still
    name FOUNDRY as owner of acceptance and FlowWorks; FOUNDRY was retired 2026-11-02. I did not edit them (this
    run was read-only); they are owed a correction.

## Appendix: commands behind the measured numbers

- Nightly: `Transient\selftests_nightly.last` and `.log` in `\home\mandrake\rm\bench` (the data clone).
- Test queue: `D:\ClaudeWork\rimmandrake\testq\done\*.json`, 853 files, read with a Python counter.
- modcheck: `infrastructure\state\modcheck_status.json`, 71 entries.
- Relentless: `\home\mandrake\rm\relentless\store\` (`exams\`, `boxrun.jsonl`, `live_round.json`, `evidence_shadow.jsonl`, `journal.jsonl`).
- Timers: `systemctl --user list-timers --all` and `is-enabled` on Archmagi, 2026-11-12 10:22 PST.
- Counts of files: `find` and `ls` in the clone, excluding `obj\`, `bin\` and `whittle\`.
- Proof cost: `python3 src\RimMandrake\rimflow\proof_cost.py throughput --hours 168`.
- Code review: `python3 src\RimMandrake\Utils\code_review_status.py list`.
- Not checked: SteveDesktop's own disk (mutation shards, worker logs); a run log for agent-habit checks (targeted self-tests, patch validation, planted-bug fuzz checks, offline world and art models).
