# Daily agent improvement pass (and the transfer audit that motivated it)

2026-11-02, BENCH, for the Conductor. Item: `AGENT_IMPROVE_BUILD_JUDGED_DAILY_DIFFS`.

The owner, 2026-11-01: *"We also should make sure nothing foundry and bench learned get lost. We are pretty good at
pulling lessons into skills and those should of course be made available. But it's worth a question whether some
transfer might benefit. Every day we should ask if each agent can be improved based on our evidence. That's the beauty
of making them agents. Same with reusable skills not agent specific."*

## 1. Transfer audit: what reaches the new agents

Measured by `D:\ClaudeWork\rimmandrake\bench_transfer\reach.py` over 114 units (every skill plus the fact files, rule
files and tools the seats lean on), weighted by how many lessons name each unit as `home:`.
Output: `reach_before.json` and `reach_after.json` beside it.

| channel | Relentless worker | Designer | Operations |
|---|---|---|---|
| CLAUDE.md (names 22 of 114 units) | loads (claude -p in a clone) | loads | loads |
| skill listing (~98 skills) | ambient | ambient | ambient |
| seats' auto-memory (156 files, 69-line index) | **0 of 263 clone project dirs** | loads (cwd bench) | loads |
| its own brief names, before | 1 of 114 | 0 | 3 |
| its own brief names, after 580ccf5e5e | 8 | 11 | 12 |

Gaps found:

1. **Briefs pointed at almost nothing.** Of the ten most-homed units, five appear neither in CLAUDE.md nor in any brief:
   `live-debugging-proof-harness` (56 homed lessons), `rimworld-review-sheets` (25), `rimworld-art-evaluation` (22),
   `git-efficiency` (18), `using-rimflow` (18); `clone-landing-commits`, which every Relentless commit needs, was not
   named either. Fixed in 580ccf5e5e: each brief now names the skills its steps need, as pointers, never pasted text.
2. **Relentless workers never get the seats' memory.** A worker's clone is a new project path, so Claude Code loads no
   `MEMORY.md` there. Fixed: the worker brief names the index and says to read only the entries the item touches.
3. **Reverse gap: Relentless learns and nobody reads it.** 107 `learned.md` files (239 KB) and the reject reasons in
   699 `attempts.jsonl` rows (blind_fail 41, proof_weak 20, bad_candidate 6, close_refused 4, ...) never reach a lesson
   or a skill. The daily pass below is its harvest.
4. **Not a gap:** the 1368-file lessons inbox. The owner retired it as a queue (`LESSONS_RETIRE_INBOX_AS_QUEUE`,
   2026-11-01): a corpus, promoted on recurrence, its backlog never counted. The daily pass promotes only on recurrence.

## 2. What already exists, and why none of it is this

| thing | what it does | why it is not the daily pass |
|---|---|---|
| `role_use.py` | per role per week: outputs that a later action used | report only, weekly, never a target, proposes nothing |
| `weekly-retrospective` skill | one change per week, with a success criterion | weekly, fleet-wide; its global changes are propose-only |
| Innovator role | proposals (folding into Operations and Relentless) | `enabled:false`; no diff, no judge |
| Auditor | weekly lesson curation with a budget | weekly, lessons only, never role files |
| fresh-context curation sessions | the only place skills are edited (CLAUDE.md, Skills) | ad hoc; nothing schedules one or feeds it evidence |

The daily pass **is** a fresh-context curation session that a program schedules and feeds, so the CLAUDE.md rule holds.

## 3. The design: five steps, one AI maker, one AI judge

**Step 0, gather (program, no AI): `src/RimMandrake/Utils/agent_improve.py gather --day D`.** Reads only day D's
evidence and routes each piece to a target (a role file under `rimflow/roles/`, `relentless.py`'s worker brief, or a repo
skill under `.claude/skills/`):

| evidence | source | routes to |
|---|---|---|
| lessons filed that day | `infrastructure/state/lessons/<utc>-<seat>-*.md`, `home:` | the skill or doc it names |
| Relentless reject reasons | store `items/*/attempts.jsonl`, `end` not finish/done | `relentless` |
| Relentless learned lines | store `items/*/learned.md`, `- <ts> gen N:` | `relentless` |
| Relentless alarms | store `journal.jsonl`, `do: alarm` | `relentless` |
| Operations alarms | `ops_watch/alarms.json`, `since` that day | `operations` |
| owner corrections | ledger `OWNER.jsonl`, `ownerSaid` that day | unrouted (the Curator routes) |

A target is **signalled** only on recurrence: two or more pieces in the last seven days (the owner's promotion rule).
Day D's packet lists signalled targets, at most `MAX_TARGETS` (6), most pieces first, each with its pieces' paths and
first lines. Never the backlog. Out: `D:\ClaudeWork\rimmandrake\agent_improve\<D>\packet.json` and `packet.md`.

**Step 1, Curator (fresh `claude -p`).** Reads the packet and each target file. Per target, at most one diff of at most
~15 lines, pointer-not-paste, each with a one-line recheck (what tomorrow's evidence would show if it worked). It never
touches rulings, gates, caps, the schedule, `close_gate_rules.json`, CLAUDE.md or a global skill: those it writes as a
proposal line only. "No change" is a valid answer for every target.

**Step 2, Judge (a different fresh agent, the delegation protocol §4).** Sees the diff, the target file and the packet
pieces, not the Curator's reasoning. Returns KEEP / REDO / UNSURE per diff. The Curator cannot overrule REDO; one re-ask
of one new judge, once. Verdict JSON: `infrastructure/state/delegated/<D>/agent_improve_<target>.json`.

**Step 3, apply (program).** KEEP only: `git apply --check`, `skills/validate_skills.py` for a skill, the target's
selftests (`selftest_relentless` for the worker brief), then a commit whose body carries
`Delegated: technical — agent improvement <target>`, landed with `land.sh`. Any refusal leaves the diff in the packet
folder, unapplied.

**Step 4, digest.** `delegated_digest.py` already reads commit bodies and verdict files, so each applied diff is one
line in his daily digest with no new code. Proposals (CLAUDE.md, global skills) list in `packet.md`'s last block, which
the Conductor's digest step links. The next day's gather reads yesterday's applied diffs and their rechecks: a recheck
that failed becomes that target's first piece (a revert proposal).

**Cost bound.** Signalled targets only, at most six, one diff each: Curator plus Judge about 150k tokens a day. A day
with no recurrence spends nothing past the program.

**Schedule.** `dispatcher_schedule.json` `measure` row `agent_improve`, `enabled:false`, daily 06:40 local (before
Operations at 07:30 and the Conductor's digest). It runs gather only until steps 1 to 3 are built; switching on the
timer is the owner's, like `v3_vs_v2`.

## 4. Ramp, versions, generalization (owner ruling 2026-11-02)

The owner, 2026-11-02: *"at first there will be so many bugs and gross improvements we must do this. Then we increase
the length of review time and the required evidence to substantiate improvement. We must avoid overfitting to one task.
But there will be many different tasks all the time (big world problem) and we should keep different versions and
occasionally evaluate if they are just overfitting or actually improving in generalization."*

**4.1 Ramp, triggered by a measured number, never a date.** The number is the acceptance rate: applied KEEP diffs
divided by diffs proposed, over the last 10 passes (from the verdict files in `infrastructure/state/delegated/`). The
current level lives in `D:\ClaudeWork\rimmandrake\agent_improve\state.json`; gather reads its bar from it.

| level | interval | recurrence bar (pieces in window) | window | extra evidence |
|---|---|---|---|---|
| L0 | daily | 2 | 7 days | none (gross bugs) |
| L1 | every 3 days | 3, from 2 or more task kinds | 14 days | the recheck of the target's last change has passed |
| L2 | weekly | 5, from 3 or more task kinds | 28 days | L1 plus a generalization check passed (4.3) before apply |

Step up one level when the rate over the last 10 passes falls below 0.3; step back down when it rises above 0.6 (a
new crop of bugs). At most one step per 10 passes, so the rate is measured on the level that produced it.

**4.2 Versions, old ones kept and runnable.** Each applied change gets a git tag `agent/<target>/v<N>` on its commit
(N counts per target). Any version is runnable: `agent_improve.py materialize <target> v<N> <dir>` writes the role file
or skill folder as of that tag into a scratch dir, and a run points at it (`role_launch.py` `--instructions <path>`; a
skill is copied into the scratch clone's `.claude/skills/`). Nothing is deleted; a revert is a new version.

**4.3 Generalization check, on task KINDS the change did not come from.** A task's kind is the intent word in its item
id (`model.INTENT_WORDS`: BUILD, REPAIR, AUDIT, ...) plus its ledger `kind`. Each change records its source kinds (the
kinds of the items its evidence pieces came from). At L1 for every fifth change, at L2 for every change, and weekly for
the newest version of each target:

- Sample fresh from the last 14 days of the ledger: 6 closed items whose kind is NOT a source kind (held out), and 6
  items of a source kind. Fresh each time, because the task mix keeps changing. Six, because 5 pairs is the fewest that
  can pass the sign test below; a target whose source kinds closed fewer than 5 items cannot be called narrow.
- For each item, two fresh agents get the item's spec: one with the old version, one with the new, both in scratch
  clones; each writes its plan and first step. A blind judge (sees neither version nor which is new) picks the better
  of each pair or calls a tie, against what actually closed the item.
- Null control, on the same sample and recorded beside each check: the old version runs a second time on each judged
  item, and a blind judge compares the two old answers. What it reaches is how far this judge drifts on nothing.
- Verdict (the Conductor's 2026-11-02 rule, given a noise floor by `AGENT_IMPROVE_HARDEN_NOISE_CALLED_OVERFIT`, because
  the first real run called a one-line path fix overfit at 2-3-1 while the judge's reasons said the plans were nearly
  equivalent). A sample shows **harm** or **gain** only past both bars: |wins - losses| exceeds the null's
  |wins - losses| plus its failed null pairs, and an exact one-sided sign test on the win/loss pairs gives p <= 0.05
  (at 6 pairs, 5-0 or 6-0). Harm on held-out kinds: reverted as **overfit**. Gain on held-out kinds without harm: kept
  as **general**. Gain on the source kind only, held-out no harm: kept and flagged **narrow** in its change record, so
  a pile-up of narrow changes on one target is visible (the digest line counts a target's narrow changes). Anything
  else is **no_signal**: it neither reverts nor keeps as general, and at L2 the change is not applied, because the gate
  applies only a proven keep.
- Power of the sign bar alone, computed for 20% ties (the null margin can only lower it): at 6 pairs a change that truly
  wins 80% of its decided pairs is called general about 20% of the time (12 pairs: 46%); a change with no effect, about
  2%. Reading no_signal is the common result at this size, not a finding about the change. The first measurement, on
  rimworld-modding v1 2026-11-06: real 2-3-1, null 3-0-3, so the judge moved further on identical text than on the change. `AGENT_IMPROVE_TUNE_L2_GATE_SAMPLE_POWER` holds the L2 question.
- Cost bound: up to 36 short runs plus 24 judge calls per check (12 pairs, three runs and two judgments each), not yet
  measured against a token budget; it runs only at L1 and L2.
- Built (`AGENT_IMPROVE_BUILD_GENERALIZATION_CHECK`): `src/RimMandrake/Utils/agent_improve_general.py`, run as
  `agent_improve.py general <target> v<N>` and as the L2 pre-apply gate. The two agents are tool-less `claude -p` runs
The cadence
  and the revert version are `src/RimMandrake/Utils/agent_improve_cadence.py`, run by the pass
  (`AGENT_IMPROVE_WIRE_GENCHECK_HAND_RUN_ONLY`; at most 3 checks a pass, the rest stay due; a revert version is never
  itself checked). A hand run only records its verdict. The digest's narrow section lists each target's count.

**4.4 The evidence travels with the change.** Each applied change commits
`infrastructure/state/agent_improve/changes/<target>_v<N>.json`: the packet pieces that motivated it (paths and first
lines), their source kinds, the diff, the Judge verdict path, the recheck, and later every generalization verdict
with its flag, general, narrow, overfit or no_signal, and its null control (appended, never rewritten). The digest line links it.

## 5. Built now, and owed

Built with this design: step 0 (`agent_improve.py gather`), `selftest_agent_improve.py`, the paused schedule row.
Owed under `AGENT_IMPROVE_BUILD_JUDGED_DAILY_DIFFS`: steps 1 to 3 (Curator and Judge prompts, the apply program), the
systemd unit, section 4 (ramp state, tags and `materialize`, the generalization check,
the change records), and one hand-run day whose packet a human reads before the timer is enabled.
