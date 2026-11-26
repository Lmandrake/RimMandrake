# BOUNDARY: the filing gate (`filing_gate.py`) and its set-down judge (`set_down_judge.py`), Design Version 0.4.0

Code: `src/RimMandrake/rimflow/filing_gate.py` (all of it); its two doors in `cli.py` (`_filing_door`, called by `_file`
and by `cmd_spawn`, with the flags `--not-now`, `--did-it` and `--not-worth-it`); the Stop hook
`.claude/hooks/filing_refusal_before_stop.py`; `detached_helper.filing_refusal_lines` and its use in `finish`; the
three other doors of a helper's defer in `cli.py` (`_defer_door`, called by `cmd_wait`, `cmd_block` and `cmd_note`);
the set-down judge `src/RimMandrake/rimflow/set_down_judge.py`, its brief `src/RimMandrake/rimflow/roles/set_down_judge.md`
and its calibration `src/RimMandrake/rimflow/set_down_calibration.py` (cases `set_down_cases.json`, table
`judge_agreement.md`, both beside this page); the `tolerate` field of `refusal_contract.judge_cases`.
Items: `RIMMANDRAKE_REFUSE_FILING_WITHOUT_EVIDENCE_WHY_NOT_FIX_IT_NOW`, and
`RIMMANDRAKE_TIGHTEN_SET_DOWN_CLASSES_ANY_TWELVE_LETTERS_PASS` (0.4.0: on 2026-11-25 the Conductor read 25 set-downs of
12 hours and found about 16 with no sincere attempt; the owner then ordered a filer that pushes back inside the run, a
refusal that states the requirements with no menu, and a block, not a daily statistic). Why: on 2026-11-24 three runs wrote up work in
place of doing the work. `CLAUDE.md` §Touching code has a cost (test 2) had the rule and no check. Each promise has a
test of its name in `src/RimMandrake/rimflow/selftest_filing_gate.py` (`t_`, and underscores for dashes), and each test
there is of a promise here. The hook has its own selftest, `.claude/hooks/selftest_filing_refusal_before_stop.py`.

## ACCEPTS (the only inputs this is built for)

- **a-filing.** The door (`file` or `spawn`), the id, the title, the kind of the ticket, the unit of the run that files
  it (`RM_ROLE_UNIT`, empty in a window), whether the filing carries the owner's authority (`--owner-said` or
  `--by-card`; `--per-ruling` alone is not his authority), the name of a program that files (`RM_FILING_PROGRAM`, set
  by the program in the env of its own cli call), and at most one of `--not-now`, `--did-it` and `--not-worth-it`.
- **a-headless-conductor-run.** A headless Conductor run carries `RM_ROLE_UNIT`, so the gate treats it as a helper. Only
  the Conductor window (no unit) is exempt.
- **the-state-folder.** `RM_DISPATCHER_STATE`, or else `/mnt/d/ClaudeWork/rimmandrake/dispatcher`. The refusals of a
  unit are in `<state>/filing_refusals/<unit>.jsonl`. A test process (`test_process.under_test()`) that has the real
  state folder files as a window: it writes no record into the real state. A test that brings its own state folder
  and sets a unit of its own gets the whole gate; the unit it inherited from its run (the `RM_ROLE_UNIT` in the launch
  env of its nearest test program, `/proc/<pid>/environ`) is not its own.
- **the-live-runs.** The units that `detached_helper` shows launching or running, or `None` when they cannot be read.
- **the-mod-folders.** A function that says if a folder of that name is in `design/concepts/` or `src/RimMandrake/`.
- **the-mod-of-the-run.** `RM_CONTROL_MOD` in the env of the filing unit's launch record (`detached_helper.py`; every
  maturation and Dispatch launch sets it), or `None` when the record cannot be read, has no such key, or says `none`.
- **a-defer.** In a helper run: the reason of `rimflow wait`, the reason of `rimflow block`, and the text of a
  `rimflow note` that starts `LEFT OPEN:` or holds `NEXT:` and names the Conductor or the owner.
- **the-filing-transcript.** The transcript of the filing run: `CLAUDE_CODE_SESSION_ID` of the filing process, found by
  `detached_helper.find_transcript`. Or that it cannot be found or read.
- **the-judge-door.** One bare `claude -p` call: no tools, no settings, no MCP, no session kept, an empty folder. The
  model is `RM_SET_DOWN_JUDGE_MODEL`, or else the alias `opus`, which the CLI resolves from the environment. The account
  is the one the environment holds; the code names none. `RM_SET_DOWN_JUDGE=0`, a test process, or a process outside
  Claude Code (no `CLAUDECODE`) turns the judge off: the set-down then reads `could not judge: off`.
- **the-calibration.** The row `set_down_judge` of `infrastructure/state/judge_calibration.json`.
- **a-sha.** For `--did-it`: what git says of it in the clone (`RIMFLOW_GIT_CWD`, or else the repository): it exists,
  it is on `origin/main`, and it changes a path that is not a ledger path. Or that git cannot be read.

## DOES NOT SURVIVE

- A run that gives false evidence in good form. The gate checks what a program can check. The count by class on the
  ledger shows a class that is used as a habit.
- An agent that sets `RM_FILING_PROGRAM` or `RM_UNDER_SELFTEST` in its own shell. The gate cannot tell that agent from
  a program or a test. The rule is that only a program sets them, in the env of its own cli call.
- A run that ends after the Stop hook let it go (two blocks). The run-end text still names each refusal.
- A set-down whose words dodge each pattern of the program check. The judge then reads it, in shadow until calibrated.
- A judge that is wrong in good form. Calibration measures it on 25 real set-downs; a binding judge may still disagree
  with the Conductor on at most 3 of 25 (the Conductor's ruling, 2026-11-25).
- A judge that cannot answer. The set-down passes, and its record says `could not judge` and the cause.

## PROMISES

- **a-helper-work-ticket-with-no-evidence-is-refused.** A run with a unit files a work ticket with no `--not-now`:
  refused, exit 6. The refusal leads with the fixer's words (`FIXER`): fix it in this run, test first.
- **the-refusal-is-a-path-to-pass.** The refusal text leads with `FIXER`. Then it states the requirement that the
  set-down tried to meet and what is missing, or, with no class, what a valid set-down shows, with one example. It names
  the form `<class>: <evidence>`. It never prints the list of classes: `rimflow file --help` holds it. `refusal()` is
  the one home of this wording.
- **evidence-of-a-known-class-files-the-ticket.** `--not-now "<class>: <evidence>"` with a class of the list and
  evidence of 12 characters or more that is not the class name again: filed, and the class and the evidence are
  recorded on the event (`not_now`).
- **an-unknown-class-is-refused.** A class outside the list is refused, "it is large" and "my work would not finish"
  included. The refusal does not list the classes.
- **files-held-names-a-live-run.** Class `files-held` passes only when its evidence names a unit that is live.
- **other-mod-names-a-mod-folder.** Class `other-mod` passes only when its evidence names a mod folder that exists. A mod folder is one
  of `design/concepts/<Mod>`, `src/RimMandrake/<Mod>`, `src/RimStarWars/<Mod>` or `src/RimUtinni/<Mod>` (all three shipping tiers).
- **other-mod-refuses-the-mod-of-the-run.** Class `other-mod` whose evidence names only the mod of the filing run (any
  letter case) is refused (item `RIMMANDRAKE_REFUSE_OWN_MOD_HANDOFF_DRIVER_RENAMED_NOTHING`: on 2026-11-25 a visit
  driver filed the rename of 12 of its own mod's defNames as other-mod). The refusal says: fix the fault in this
  sitting, red test first; if the cause is unknown after a sincere attempt, file with `fix-unknown` and name what you
  tried. Evidence that also names another mod folder passes, and the other mod is recorded.
- **fix-unknown-needs-three-theories-each-tested.** Class `fix-unknown` passes the program only when its evidence
  names three different theories (`theory 1:`, `theory 2:`, `theory 3:`), each with an experiment and a reading, and
  names a GPT consult. Real text of 2026-11-25: "seen in pictures only; whether it is ours is not known" is refused.
- **a-choice-between-known-fixes-is-refused.** Class `fix-unknown` or `no-tool` whose evidence offers two known fixes
  ("two fixes", "a design call", "(a) ... (b)") is refused. The refusal says: take the fix that you recommend, and log
  the choice as delegated. Real text: "two fixes are possible and which one is right is a design call".
- **owner-act-names-an-act-not-a-conductor-call.** Class `owner-act` whose evidence names the Conductor and none of the
  five acts or a looser bar is refused. Real text: "the Conductor decides at filing whether this goes on the Polish
  list". Evidence that names a looser bar, or does not name the Conductor, goes to the judge.
- **a-held-game-is-not-a-reason.** A set-down of any class but `files-held` whose evidence says a game is held, busy or
  not free is refused. The refusal says to wait with `game_lock.py run <game> --for "<what>" -- <command>`. Real text:
  "no free game: ArchBig and ArchSmall were both held".
- **a-workaround-is-refused.** A set-down whose evidence says that the run worked around the fault is refused: a hand
  workaround with no permanent fix is not allowed. Real text: "worked around in this run".
- **a-set-down-that-did-not-look-is-refused.** A set-down whose evidence says that the run did not read, try, look or
  check, or tried neither fix, is refused. Real text: "Operations did not read FlowWorks/validation.py".
- **the-judge-reads-the-transcript-and-answers.** After the program passes a set-down, the judge reads the set-down,
  its requirement and a digest of the filing run's transcript (each tool call, its first output, the run's own words,
  up to the filing). It answers PASS or REFUSED. A REFUSED answer names what is missing and the next act that would make
  the set-down valid; an answer without them, or with no JSON, is `could not judge`.
- **each-judgment-starts-fresh-with-the-earlier-refusals.** Each call is a new model call. Its prompt holds each
  earlier refusal of the same unit and id from `filing_refusals`, so the second judgment checks what the first asked.
- **a-judge-that-cannot-answer-passes-the-set-down-and-says-so.** No transcript or an unreadable one (then no model call
  is made), a model call that fails or times out, or a malformed answer: the set-down passes, and the event's
  `not_now.judge` says `could not judge` and the cause. A dead judge never stops filing.
- **the-judge-binds-only-when-calibrated.** While the row `set_down_judge` is not CALIBRATED at its brief's hash, the
  judge is in shadow: its verdict goes on the event (`not_now.judge`, `binds: false`) and in
  `<state>/set_down_judge/<unit>.jsonl`, and it stops nothing. When CALIBRATED, a REFUSED verdict refuses at the door
  (exit 6, recorded) with the judge's missing part and next act. `judge_cases` reads a row's `tolerate` (the count of
  planted cases that may come out the other way, 3 for this row by the Conductor's ruling); with no `tolerate` it is 0.
- **the-judge-is-told-no-spend.** The judge's prompt holds no spend, cost, budget or token figure, and the call passes
  no `--max-budget-usd`.
- **the-judge-call-is-one-bare-model-call.** The call is `claude -p` with `--tools ""`, `--setting-sources ""`,
  `--strict-mcp-config` and `--no-session-persistence`, in an empty folder, with the model of the environment.
- **the-other-doors-take-the-same-check.** In a helper run, `rimflow wait`, `rimflow block` and a `rimflow note` that
  defers to the Conductor or the owner (`LEFT OPEN:` or `NEXT:`) go through the same program check and the same judge.
  A wait or block whose reason names a reset, a timer, or a run that is live passes the program. A reason that names
  the Conductor or the owner passes only when it names one of the five acts, a looser bar, or a hold to lift. Such a reason is read as class `owner-act`: options that it names (his A or B on art he kept) are his to pick, so the choice-between-known-fixes check does not refuse it. A refusal
  exits 6, writes no event and is recorded. The same act done again that passes resolves that refusal. The owner,
  the Conductor window and a program are never refused.
- **the-blind-brief-asks-three-theories.** The blind judge's brief (`maturation.blind_brief_text`) names "the cause is
  still unknown after three theories, each tested", not "the fix is not known".
- **a-run-mod-that-cannot-be-read-is-not-a-refusal.** When the mod of the run cannot be read, `other-mod` is filed, the
  record says `could not look` (`own_mod`), and the door prints one note on stderr.
- **could-not-look-is-not-a-refusal.** When the live runs cannot be read, `files-held` is filed and the record says
  `could not look`.
- **the-owner-and-the-conductor-are-never-refused.** A filing with the owner's authority, and a filing from a window
  (no unit), pass with no flag.
- **per-ruling-alone-is-not-the-owner.** A helper that files with `--per-ruling` and no other flag is refused.
- **only-a-reminder-kind-passes-with-no-flag.** The kinds `owed`, `design`, `notice` and `alarm` pass with no flag: such
  a ticket holds a debt or a question, not work. Every other kind is work (`bug`, `task`, no kind, and each other word).
- **a-program-is-never-refused.** A filing by a named program (`RM_FILING_PROGRAM`) passes, and the name is recorded.
- **each-program-that-files-names-itself.** Each program that files through the cli sets `RM_FILING_PROGRAM` to its own
  module and function, in the env of that call, never in a shell.
- **the-door-calls-the-gate-before-it-writes.** `_file` and `cmd_spawn` call the one gate before they write the event,
  and record a resolution after it. Both doors take the three flags.
- **the-file-door-refuses-records-and-writes-nothing.** Through `cli.py file`: a refusal exits 6, records the refusal
  and writes no ledger event. Then a filing with evidence writes the event and resolves the refusal.
- **the-spawn-door-has-the-same-gate.** Through `cli.py spawn`: the same refusal, record and resolution.
- **every-refusal-is-recorded.** Each refusal writes one line `{"at", "unit", "id", "title", "kind", "why"}` to
  `<state>/filing_refusals/<unit>.jsonl`. A filing that passes writes no line.
- **a-record-that-cannot-be-written-never-changes-the-refusal.** When the line cannot be written, the refusal is the
  same, and one line on stderr says that the record failed.
- **filing-with-evidence-resolves-a-refusal.** A filing that passes, with the id of a refusal, records `filed`.
- **did-it-files-nothing-and-records-the-sha.** `--did-it <sha>` files nothing, prints
  `nothing filed: <ID> was done in this run at <sha>`, exits 0 and records `did`. A sha that does not exist, that is not
  on `origin/main`, or that changes only ledger paths is refused, exit 6.
- **did-it-reads-git-at-the-door.** Through `cli.py`, on a scratch git repository: a published work commit passes, and a
  ledger-only commit, a local commit and an unknown sha are refused.
- **a-sha-git-cannot-read-is-accepted-and-says-so.** When git cannot be read, `--did-it` is accepted, and the text and the
  record say `could not look`.
- **not-worth-it-files-nothing-and-records-why.** `--not-worth-it "<why>"` with a why of 12 characters or more files
  nothing, exits 0 and records `dropped`. A shorter why is refused.
- **one-way-at-a-time.** Two of the three flags at once: exit 2, nothing recorded.
- **unresolved-says-could-not-look.** `unresolved()` returns `None`, never an empty list, when the file cannot be read.
  A file that does not exist is no refusal.
- **a-test-with-the-real-state-files-as-no-run.** A test process with the real state folder files as a window.
- **a-unit-a-test-inherited-from-its-run-is-no-run.** A test process whose `RM_ROLE_UNIT` is the one that its nearest
  test program was launched with files as a window, with its own state folder too: a selftest run inside a helper
  inherits the helper's unit, and that unit is not the test's. A test that sets a unit of its own gets the whole gate.
- **the-run-end-names-each-unresolved-refusal.** `detached_helper.finish` adds one line
  `REFUSED FILING NOT RESOLVED: <id>: <title>` for each refusal not resolved, or `filing refusals: could not look (<why>)`,
  to its steps, its note and its wake.
- **the-stop-hook-keeps-the-run-until-each-refusal-is-resolved.** The Stop hook blocks a run that has a refusal not
  resolved, and names the id and the three ways. When each is resolved, it is silent.

## CALIBRATION (the set-down judge, measured 2026-11-25)

- The 25 set-downs, their rebuilt classes and the filing transcripts: `set_down_cases.json`. The Conductor named his
  classes by count and example only (reply of 2026-11-25 10:45 AM PST); each label is this run's reconstruction, and
  cases 5 and 16 are marked unsure.
- Run 1, the first brief: 20 of 25 agree; the judge refused 1, 10, 16, 17 and 19, which the labels pass. In each, the
  judge named a next experiment or another route that the run could have taken.
- The one correction of the brief: a sincere search is experiments run, each with a reading, and the count of
  theories is the program's; a refusal rests on a requirement that fails, never on an imagined route.
- Run 2, after the correction: 20 of 25 agree; the judge refused 1, 10, 16 and 19 and passed 11 (a held game).
- Run 3, after a wording-only repair of three pronouns that the landing's prose check found: 21 of 25 agree
  (`judge_agreement.md`); the judge refuses 1, 10 and 16 and passes 11. Case 19 came out REFUSED in runs 1 and 2 and
  PASS in run 3: the verdict on one case can vary between runs of the same brief. The bind rule (at most 3 of 25) is
  not met: the row reads FAILED, so the judge is in shadow. Each call took 9 to 26 s.
- The program half binds now. On the 25 it refuses 17 of the 18 weak set-downs (not 6, a looser bar, which only the
  judge refuses) and 3 of the 7 legitimate ones (10, 16 and 19, by the three-theory rule of 2026-11-25, which those
  texts predate).
- To bind the judge: the Conductor rules on the cases where the judge is stricter than the labels (1, 10, 16; 19 in
  two of three runs). Case 16 is one of the two unsure labels. Case 11 the judge passes, but the program refuses it.
  A ruling that the judge is right moves those labels; then `refusal_contract.py calibrate --model set_down_judge`
  measures again, and CALIBRATED binds it.

## LIMITS

- The transcript digest holds at most `DIGEST_MAX_CHARS` (80,000) characters: the first 30% and the last 70%, with the
  middle elided and counted. Danger: a prompt past the model's context window (about 200,000 tokens, about 800,000
  characters) fails the call, and the set-down then passes unjudged. 80,000 is a tenth of the window.
- The judge call has a hang guard, `JUDGE_TIMEOUT_S` (900 s). Danger: a call that never returns holds the helper's
  `rimflow file` for good. The measured need is in `judge_agreement.md` (the longest of the 25 calibration calls).

- Evidence of 12 characters or more, and a why of 12 characters or more. Danger: a one-word reason ("busy") passes.
  Evidence that it happens: none yet; the shortest true evidence is a unit name or a tool name with a verb, which is
  longer.
- The Stop hook blocks at most 2 times per unit (the same bound as `role_result_before_stop.py`). Danger: a run ends
  with a refusal not resolved. Then the run-end text names it to the Conductor.
- `--did-it` accepts a sha when git cannot be read. Danger: an unchecked sha. The record says `could not look`.
- A test that sets for its filing the same unit that its run has is read as a window. Danger: that test gets no gate.
  Evidence that it happens: none; the gate's own tests use units that no run has.
- Without `/proc` (not Linux), a test's launch env cannot be read, and a test with its own state folder that inherits a
  unit gets the whole gate. Danger: a red test on such a host. Evidence that it happens: none yet; the helpers seen
  here run on WSL2 Linux.
