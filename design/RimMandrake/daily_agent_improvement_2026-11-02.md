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
| L2 | weekly | 5, from 3 or more task kinds | 28 days | L1 plus the generalization check before apply: refused if it reads overfit, unmeasured, or leans to harm, or if its cited pieces yield no source kinds (4.3) |

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

- Sample fresh from the last 14 days of the ledger: 12 closed items whose kind is NOT a source kind (held out), and 6
  items of a source kind. Fresh each time, because the task mix keeps changing. Six source items, because 5 pairs is the
  fewest that can pass the sign test below; a target whose source kinds closed fewer than 5 items cannot be called narrow.
- For each item, two fresh agents get the item's spec: one with the old version, one with the new; each writes its plan and first step. A blind judge (sees neither version nor which is new) picks the better
  of each pair or calls a tie, against what actually closed the item.
- Null control, on the same sample and recorded beside each check: the old version runs a second time on each judged
  item, and a blind judge compares the two old answers. What it reaches is how far this judge drifts on nothing.
- Verdict (the Conductor's 2026-11-02 rule, given a noise floor by `AGENT_IMPROVE_HARDEN_NOISE_CALLED_OVERFIT`, because
  the first real run called a one-line path fix overfit at 2-3-1 while the judge's reasons said the plans were nearly
  equivalent). A sample shows **harm** or **gain** only past both bars: |wins - losses| exceeds the null's
  |wins - losses| plus its failed null pairs, and an exact one-sided sign test on the win/loss pairs gives p <= 0.05
  (at 12 pairs with none tied, 10-2 or better). Harm on held-out kinds: reverted as **overfit**. Gain on held-out kinds without harm: kept
  as **general**. Gain on the source kind only, held-out no harm: kept and flagged **narrow** in its change record, so
  a pile-up of narrow changes on one target is visible (the digest line counts a target's narrow changes). Anything
  else is **no_signal**: it neither reverts nor keeps as general.
- A change record naming no source kinds cannot be checked (`AGENT_IMPROVE_HARDEN_CADENCE_EMPTY_KINDS`): its sample would
  exclude nothing, so no reading of it is about kinds the change did not come from. The check reads it unmeasured before any
  model runs, and the cadence spends no slot, writes no entry and reverts nothing, showing it as an `unmeasured` row on the
  pass's packet while it is due. A record on file cannot regain kinds its pieces do not name; a later version with kinds is
  checked as usual.
- Where a piece's kind comes from, and why a change below L2 may still name none (2026-11-11,
  `AGENT_IMPROVE_AUDIT_KINDLESS_RECORDS_ALL_TWO`). A piece's kind is the kind of its own item when its source records
  one: a lesson's `item:` footer (`lessons.py add` writes it from `--item`, else the session's `RIMFLOW_ITEM` or the
  Whittle loop's `WC_ITEM`; `item: NONE`, or an id with no intent word, gives no kind and is never second-guessed from
  the text), a Relentless reject or learned line's item, a Relentless alarm's `item` or its `clones/<item>` path, an
  owner note's item, an ops alarm's own id. Otherwise it is the first item named anywhere in the piece's whole text, not
  only the 200 characters the packet shows: of the 2391 lessons ever filed, the first line names a kind for 158 (7%), the
  whole text for 579 (24%). That fallback is a proxy, not provenance: the lesson's own seat wrote a ledger event on that
  item within 3 hours of filing for 27% of the first-line cases and 48% of the whole-text-only ones, so reading the whole
  text is no less sound than the first line was, and only the footer is sound. Each cited piece in a change record
  carries its `task_kind`.
  **A change at L0 or L1 whose cited pieces still name no item is applied, and its record says `source_kinds: []`: it
  stays uncheckable by design** (shown `unmeasured` while due, as above; refused only by the L2 gate). Why: no other
  sound source remains, and a guessed kind would make a held-out sample that is not held out, which is worse than an
  honest `unmeasured`. The two other candidates were measured on the records on file and both failed. The lesson's seat
  touched 8 (FOUNDRY) and 41 (BENCH) distinct items within an hour of filing it, and the commits that added the lessons
  name no item ("wave 74: …", "relentless_live: …"). Refusing such a change at L0 or L1 would be a new gate. L0 asks
  for no extra evidence (4.1: gross bugs first), and a refused diff counts as proposed and not applied, which pulls down
  the acceptance rate the ramp reads. Measured 2026-11-11: 2 of 2 change records on file have `source_kinds: []`
  (rimworld-modding v1 and using-rimflow v1, both L0, one lesson each). Neither lesson names an item anywhere, so this
  reading gives them none either. In the live inbox, 5 of 105 lessons name an item (1 by their first line), so most
  skill changes will stay unmeasured until lessons are filed inside an item and so carry its `item:` line. Measurement:
  `whittle/agent_improve_audit_kindless_records_all_two/evidence/measure_kindless.py` and `attribution_audit.py` beside it.
- The L2 gate (`AGENT_IMPROVE_TUNE_L2_GATE_SAMPLE_POWER`, decided before the ramp first reached L2, with
  two noise-floor checks on record, both no_signal, so mostly from computation: 2 of 2 is no rate). It applies what reads general,
  and a narrow or no_signal that does not lean to harm (wins >= losses on 6 or more judged held-out pairs); it refuses overfit,
  unmeasured, and a narrow or no_signal that leans to harm: a source gain never buys off held-out losses. It also refuses, before any model runs, a change whose cited pieces yield no source kinds (`AGENT_IMPROVE_HARDEN_GATE_EMPTY_SOURCE_KINDS`): the recurrence bar counts gathered pieces, not cited ones, and with no kinds nothing is excluded, so the held-out sample is not held out. The verdict stays as read in the change record. Why not only a proven keep, the first
  rule here: exact power through the live rule, 20% real ties and 50% null ties (`selftest_agent_improve_general.py`):

  | true win rate of decided pairs | general at 6 / 12 / 24 pairs | overfit at 6 / 12 / 24 | through this gate at 6 / 12 |
  |---|---|---|---|
  | 0.20 (harmful) | 0 / 0 / 0 | .20 / .46 / .83 | .11 / .03 |
  | 0.50 (no effect) | .02 / .02 / .03 | .02 / .02 / .03 | .59 / .56 |
  | 0.65 (modest gain) | .07 / .13 / .30 | 0 / 0 / 0 | .82 / .87 |
  | 0.80 (large gain) | .20 / .46 / .83 | 0 / 0 / 0 | .96 / .99 |

  So a proven-keep gate refuses a large gain 4 times in 5 at 6 pairs, and a modest one 7 times in 10 even at 24 pairs, at four
  times the cost, so no affordable sample rescues it. It would also trap the ramp: a refused diff counts as proposed
  and not applied, so at L2 the acceptance rate could not climb back over the 0.6 that steps down. The gate is not what
  carries L2's extra evidence: the change has already cleared 5 pieces from 3 task kinds, the Judge and the recheck, and the owner's
  worry is overfitting, which is harm on other kinds. What this costs: a no-effect change passes about half the time. It stays
  visible in its change record, and the weekly check of the newest version can still revert it as overfit. Twelve
  pairs rather than 6 because they make harm visible: a harmful change slips through 3% against 11%, and reads overfit
  46% against 20%. The sign bar's false call on a no-effect change stays 2 to 3%.
- First measurement, on rimworld-modding v1 2026-11-06: real 2-3-1, null 3-0-3, so the judge moved further on identical
  text than on the change. Second, on using-rimflow v1 2026-11-06, the first at 12 pairs: real 6-4-2, null 2-4-6, no_signal, 117 s
  of wall clock. Together real pairs tied 3 of 18 and null pairs 9 of 18, the rates the table assumes.
- Cost bound: up to 54 short runs plus 36 judge calls per check (18 pairs, three runs and two judgments each), not yet
  measured against a token budget; it runs only at L1 and L2.
- Built (`AGENT_IMPROVE_BUILD_GENERALIZATION_CHECK`): `src/RimMandrake/Utils/agent_improve_general.py`, run as
  `agent_improve.py general <target> v<N>` and as the L2 pre-apply gate. The two agents are tool-less `claude -p` runs
  with the target text inlined, not scratch clones, on purpose: a clone per run would spend the whole 16-clone pool on a plan and a first step. The cadence
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
