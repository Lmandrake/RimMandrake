# Relentless builds Relentless, in stages (2026-11-06)

Item: SELFBUILD_DESIGN_STAGE_ZERO_KEEPS_KEYS. Inputs: the item's text (Conductor, from the owner's chat 2026-11-02:
"use relentless to create relentless; relentless could build the judge for a different relentless, validated by
rebuilding something already built"), survey rules 1, 2, 5, 6 and 8 (`design/RimMandrake/builder_agents_survey_2026-11-02.md`),
the E1 baseline (`design/RimMandrake/relentless_TRUST_2026-11-01.md`, RA_S00_BASELINE_MEASURE_BEFORE_BOASTING, closed).
Code: `src/RimMandrake/rimflow/relentless_selfbuild.py`, list `relentless_selfbuild.json`, test
`selftest_relentless_selfbuild.py`.

🔑 **Owner, 2026-11-02:** *"We are not going to spend much on pulsing known work. It's just to show some skill. Then we
get to work ok!"* Replays of already-built work and held-out comparisons are a **token sample** (`replay.token_max` 6,
`promotion.min_repeats` 2). Most of the money goes to real queue work. Nothing here is meant to grow into a benchmark.

## 1. Stages

- **Stage 0** is the Relentless running now, frozen at a named sha: supervisor, worker prompts, Judge. It is the builder.
- **Stage 1** is a candidate: a branch of changes stage 0 built as ordinary queue items. It changes the *builder's*
  side only (worker prompts, `.claude/agents/rm-builder.md` / `rm-fixer.md`, skills, non-grading modules).
- Stage 1 replaces stage 0 only through `promote` (section 3). Stage 0 stays runnable at its sha, so one revert of the
  swap commit rolls it back (survey rule 2, the DGM archive). The next round, stage 1 is frozen and becomes the builder.
- Stage 0 never grades itself. The Judge, Marker, wall, seeds and counting rules are the same at both stages, and that
  is what makes the two scores comparable.

## 2. The protected list (survey rule 1)

`relentless_selfbuild.py protected --base <stage0 sha> --head <candidate sha>` refuses (exit 1) any diff that touches:

- a listed grader file: the Judge gate in `relentless.py`, `relentless_wall.py`, `relentless_reach*.py`,
  `relentless_packet.py`, `relentless_seeds.py`, `relentless_trust.py`, the counting rules doc, `.claude/agents/rm-judge.md`,
  the checks of those, and this check, its list and its test;
- a protected key of `relentless_rules.json` (`walls`, `checker_agent`, `offbox_adapters`, `reach_*`, `hand_check`, ...);
- **any local module a protected `.py` imports, transitively, at either end of the diff.** Function-local imports count
  too. A new import that pulls a module in protects that module in the same diff. This is the OpenAI finding: protecting
  the test files alone left the modules the tests import open.

An unknown sha is UNMEASURED (exit 2), never a pass. The list is read **at the base sha**, never from the candidate, and
the supervisor runs **stage 0's copy** of the program: a candidate that edits the list or the check it is judged by
would otherwise judge itself. The supervisor runs this before any model reads the candidate.
The program does the guarding, not secrecy and not a prompt (DGM node 114 gamed a detector it could not see).

**Measured on this tree (2026-11-06): the closure is 119 files** (`relentless_selfbuild.py protected --base HEAD --list`). `relentless_seeds.py` imports `relentless.py`, and
`relentless.py` reaches most of `rimflow/` and many `Utils/`. So **today a stage-1 candidate may change prompts, agent
definitions, skills and modules outside that closure, and nothing in the supervisor.** That is right while the Judge
gate lives inside the supervisor. To give stage 1 more room, move the gate out into a small module with a narrow import
set. That is a refactor done by ordinary review, never by a candidate (filed, section 6).

A change to a grader part is not banned. It goes through ordinary review (Conductor and a second model), never through a
self-build candidate, and it starts a new stage-0 baseline, because the old scores were taken with the old grader.

## 3. Promotion: swap only on >= (survey rule 2)

`relentless_selfbuild.py promote <runs.json>` swaps stage 1 in only when all of these hold:

- the candidate passed `protected`;
- both stages ran the **same frozen case list** on each promotion set. Its hash (`manifest_hash`, sha256 of the sorted
  ids) is recorded when stage 0 is frozen, so a re-picked list is refused even when both stages used it;
- each stage ran each set at least `min_repeats` times (2: a token, per the owner);
- on **every** set, stage 1's `pass^k` is >= stage 0's. `pass^k` counts a case only if it passed on every repeat, so a
  candidate that passes a case once is not credited with it. A tie swaps, which is what the item says.

The sets are **E1**, as the item says, and **E2** as a held-out certify set. E1 was used for tuning after the baseline
(`relentless_counting_rules_2026-11-01.md`, "a prompt tuned on E1 is retested on a retest set"), so E1 alone cannot
certify a change. E2 is never used to choose anything. Both are frozen in the private `seeds/split.json`, which never
moves.

Expect noise: E1 holds about 30 counted cases, so a tie or a one-case gain proves no improvement. The swap rule is
"no worse", not "better". A claim of improvement needs a bar he sets.

## 4. Cross-build: A builds a Judge for B (survey rules 6 and 8)

Instance A may build a Judge for instance B. `relentless_selfbuild.py cross <manifest.json>` refuses unless:

- A and B are both named and differ;
- every label, held-out case and mutant has a recorded author, and **none is A**. Labels come from the store (owner
  verdicts, escapes, accepted closes); mutants are real reverted fixes (`relentless_seeds.py`) or come from a third
  instance;
- there is at least one known-good the Judge must **PASS** and at least one fault it must **FAIL**. A Judge that fails
  everything scores badly; the E1 baseline already showed 4 of 9 controls false-failed;
- the replays are exactly `draw(pool, seed)`, and every drawn replay has a known outcome among the labels. The seed is
  recorded before A starts building. The pool is the store's rows, built by the supervisor, never by A.

**Replay selection bias:** `draw` makes A unable to choose its exam. It is stratified by (outcome, leaf class), round-robin
in a seeded order, so every stratum present is drawn once before any is drawn twice, and it is capped at the token size.
Rows A authored are dropped. The draw is a function of the seed, not of row order (tested).

**Rebuilds see no future (rule 8):** a replay's builder gets the item's original lease sha, exported without `.git`, and
no store rows, ledger notes or conversations dated after it. The model may still remember our public repo, so a rebuild
score is an **upper bound**, and is reported as one.

## 5. Hack-watch (survey rule 5)

A separate pass reads each self-build candidate's transcript and its diff to tests, oracles, fixtures and their imports,
looking for gaming. This adds to `protected`, which sees only paths, while the watcher sees intent. A flag holds the
candidate for the Conductor and a second model, and is counted in `trust`. It is **never** fed back to the builder as an
instruction, and never made a target to tune against: OpenAI measured that tuning against a monitor teaches hiding. The
watcher is its own unit, walled from the Marker. Neither sees the other's verdict.

## 6. What must exist before the first self-build: `ready`

`relentless_selfbuild.py ready` refuses until `relentless_rules.json` has an enforced `walls.builder` profile that denies
the seed keys (`RM_SEEDS_PRIVATE`) and the store. **Today it refuses:** only `walls.marker` exists, so a worker could read
the keys of the exam it is building toward. Owed, each its own item:

- the builder wall on the real worker launch path, so `ready` passes (BUILDERWALL_BUILD_EXAM_KEYS_SHUT);
- the Judge gate moved out of `relentless.py` into a module with a narrow import set (section 2), done by ordinary review (JUDGEGATE_SHRINK_CLOSURE_IS_118_FILES);
- the hack-watch unit, section 5 (HACKWATCH_BUILD_NEVER_TUNED_AGAINST);
- supervisor wiring: `protected` and `promote` run by the supervisor on a candidate branch, report-only first (design
  §13 order: measure, wall, change; SELFBUILD_REWIRE_REPORT_ONLY_FIRST).

## 7. What this does not prove

Our numbers are our own measurements, not a borrowed guarantee. No published work shows a mutation-testing gate that
makes a self-modified checker trustworthy. `protected` guards paths and imports, not behaviour reached through data
files, environment or the network, and section 5 is the only defence there. Two repeats on about 30 cases cannot
separate small effects. That matches the owner's token-sample ruling, and it is why a swap claims "no worse", not "better".
