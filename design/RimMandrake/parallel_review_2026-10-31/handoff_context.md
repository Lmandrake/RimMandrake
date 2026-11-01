# PARALLEL_BUILD_REVIEW_DEFEND_EVERY_LIMIT: handoff, context, concurrency

Read-only review, offline, 2026-10-31, clone `/home/mandrake/rm/bench`. Nothing here was changed, committed or filed.
Words: MEASURED (read from transcripts, journal or ledger), REPRODUCED (run in a throwaway repo), READ (follows from the
code, not exercised), ESTIMATE, UNMEASURED.

## Verdict

**The design does not survive 8-10 helpers per seat today, and it has not been tried: FOUNDRY's peak in 7 days was 7,
and it spent 0.5% of its busy minutes at 6 or more.** The storage layer is sound (ledger append, per-seat shards, `next`
under a lock). What fails is everything that assumes a seat periodically reaches a quiet moment: close-out, restart,
handoff and Conductor goodbye all wait for "no helper alive" while the seat's own rules order it never to be there. One
defect loses work now, at any concurrency above 1: `./publish` has no lock and can silently delete a peer's commit.

The owner's condition was "so long as it's reliable, work is fairly checked". Fix the items in "Requirements" before
raising the fan-out. Items 1-3 there are the gate; the rest can follow.

## Measured concurrency

FOUNDRY, 7 days ending 2026-10-31 about 22:50Z, 413 helper transcripts. MEASURED.

| measure | interval model (first to last record) | active model (wrote that minute) |
|---|---|---|
| minutes with at least 1 helper, of 10081 | 3309 | 2675 |
| mean helpers while busy | 2.17 | 1.88 |
| mean over all minutes | 0.71 | not computed |
| peak | 7 | 6 |
| busy minutes at 4 or more | 14.9% | 6.8% |
| busy minutes at 6 or more | 0.5% | not computed |
| busy minutes at 8 or more | 0 | not computed |

Interval-model histogram of helpers by minutes: 0: 6772, 1: 1350, 2: 738, 3: 729, 4: 323, 5: 154, 6: 14, 7: 1.

| day | peak | helper-min | busy-min | mean busy | spawned |
|---|---|---|---|---|---|
| 10-25 | 5 | 269 | 86 | 3.13 | 32 |
| 10-26 | 5 | 2037 | 817 | 2.49 | 150 |
| 10-27 | 0 | 0 | 0 | 0 | 0 |
| 10-28 | 0 | 0 | 0 | 0 | 0 |
| 10-29 | 2 | 387 | 381 | 1.02 | 44 |
| 10-30 | 7 | 1868 | 701 | 2.66 | 124 |
| 10-31 | 6 | 2605 | 1324 | 1.97 | 63 |

Helper duration p50 504 s, p90 2031 s, max 18618 s. Six helpers had an internal silent gap over 600 s. Types: rm-builder
255, rm-fixer 121, rm-judge 17, rm-bridge 17, rm-search 2, general-purpose 1.

The biggest loss of concurrency is not any cap: 67% of minutes had no helper at all, including two whole days. Those
10-27 and 10-28 zeros come from the transcripts of FOUNDRY's project folder; the review did not establish why the seat
was silent. The Dispatcher journal starts 10-28 22:00Z, so it cannot say. 218 `unwakeable:FOUNDRY` alarms in 3 days
("idle but no doorbell is armed", MEASURED) are the likelier single cause for the later gaps, and they are a wake
problem, not a slot problem.

FOUNDRY's real ceiling is not 10 either: 10-30 and 10-31, the busiest days, averaged 2.0-2.7.

## Findings (ranked)

### 1. `./publish` can silently delete a peer's commit, from the branch and from the disk (loses work today)

`publish.py` has no lock of any kind (grep: READ). `rebase()` reads `head` at line 127, replays the commits it listed
then, and at line 161 runs `git reset --keep <tip>`. That reset moves the branch to `tip` whatever HEAD is by then. A
peer helper that commits in the gap has a commit `tip` does not contain. **REPRODUCED** in a scratch repo with the same
plumbing sequence: reset exit 0, the peer's commit gone from `git log`, the peer's file GONE from disk, `git status`
clean, only the reflog holding it. The peer's own `./publish` then finds HEAD on origin and can print `PUBLISHED`.

The gap holds `git cherry`, `merge-tree` per local commit, `commit-tree`, and `untracked_upstream` on a 5.5 GiB pack, and
is entered only when origin has moved. Width in this repo UNMEASURED. Both conditions rise with concurrency: FOUNDRY has
many publishers and BENCH pushes alongside it (205 publishes in 3 days, MEASURED).

Related: `commit()` raises at once on `.git/index.lock`, with no retry; `index_lock` hits appear in 3 of 5 FOUNDRY
windows (coarse substring count). The doc trap table says "wait a few seconds and retry", so every helper re-implements
this by hand.

Fix: one clone-wide `flock` around `commit()` through the end of `land()`, plus a compare before the reset (refuse if
HEAD is not `head`). Small, and it does not reduce build concurrency, since only the landing serialises.

### 2. A seat under fan-out can never close out, and the rules contradict each other

- `seat_restart.py cmd_request` refuses, exit 3, with any helper alive (`check_request`, lines 1808-1821), before it
  reaches the CONTEXT OK branch. So a window with a live helper cannot even get "CONTEXT OK, keep working".
- FOUNDRY.md lines 271-277, the ring text and the CONTEXT OK text say a helper is not idle: take the next item.
- The Full belt floor (lines 255-277) requires one bridge helper, the art pipeline and one offline builder "at all
  times": a floor that guarantees the refusal condition.

With 8-10 overlapping helpers at p50 8 minutes, a gap with none alive arrives only if the seat drains, and nothing tells
it to. ESTIMATE, from the shape of the rules: at full belt, never.

MEASURED signs at today's concurrency: refused-for-helpers appears 5 times in FOUNDRY transcripts and zero times in the
journal, because the refusal is seat-side, so the Dispatcher cannot see it. Only 2 real restarts in 3 days. Windows lived
5-25 hours against "fresh per ticket" (`FOUNDRY_CONTEXT_BUILD_FRESH_PER_TICKET`).

| window | span | max ctx | turns over 110k | over 200k | compactions | task notifications |
|---|---|---|---|---|---|---|
| 5ac3d971 | 10-29 03:50 to 10-30 04:50 | 527104 | 89% | 61% | 1 | 161 |
| 9d0e3b7a | 10-30 04:56 to 17:16 | 460329 | 98% | 78% | 0 | 67 |
| ca46deb4 | 10-30 17:17 to 22:30 | 235987 | 81% | 22% | 0 | 15 |
| 24d0ce06 | 10-30 22:31 to 10-31 21:02 | 441461 | 87% | 55% | 1 | 116 |
| 7a23f28b | 10-31 21:04 to 22:51 | 186240 | 64% | 0% | 0 | 13 |

Fairness note: the busy backstop landed only at 2026-10-31 19:10Z (e4711f7ef9), so the 400k+ windows predate it. It has
one tell on record (138552 tokens). It has not been tested under fan-out.

### 3. The hard limit binds nothing, and nothing drains

`_pending` holds on any live helper. Past 3600 s it raises `_no_boundary` and still kills nothing. That part is right
(never kill mid-turn), but no state follows: no drain mode, no spawn freeze. `block_agent_over_slots.py` and the
allocator know nothing of a pending restart, so a seat over its hard limit keeps spawning, and each helper's return
makes the window bigger. Context growth scales with concurrency: the window keeps the ledger for each helper (claim,
start, review, close; FOUNDRY.md 232-238) and 161 notifications landed in one window. 8-10 helpers is about 3-4 times
today's return rate. ESTIMATE.

`new_work` makes it worse: any helper's `next` or lease take writes to the seat shard, so it reads as "the seat took
work" and cancels a non-sized request. More helpers, more cancels. Same for the shard-unpublished refusal, which runs
first and is a moving target while helpers append.

### 4. Helper state dies with the helper; handoff cannot see helpers at all

- `handoff.py gates()` (277-342) checks unpushed commits, the bridge, and items started this window. There is **no**
  helper gate, despite FOUNDRY.md line 108 ("every subagent reported"). Lodestar's `stale_agents.py` step is a prose
  instruction only.
- The ledger knows only the seat: helpers write as the seat, so no record says which helper holds what. The lease token
  is the only identity and only the holder knows it. A dead helper's item waits 45 minutes or a manual `reclaim`. READ.
- `wake_digest` gives last inputs, last words, todos, files, doing items and dirty files. It has no list of live or
  recent helpers, their briefs, their progress files or their transcripts. After a restart mid-fan-out, the running
  helpers are orphans: they may finish, but their notification goes to a dead window, and any findings in their last
  message are read by nobody. Whether the harness kills them on window exit: UNMEASURED; the transcript alone cannot
  show it. Either way the fresh window cannot name them.
- Helpers cannot be redirected (no SendMessage in the helper tool set here; a parent's correction arrives only if the
  harness offers it). A wrong helper runs to its end.
- `<<< WHOSE? >>>` needs each dirty line attributed. With 10 helpers in a clone the seat cannot do that from memory, and
  `--check` refuses until it is done.

### 5. Same-file safety rests on one sentence nobody can check

"Run writing helpers one at a time when their paths could overlap" (GIT_WORKFLOW.md 48-50, efficient-subagents 254-255,
night-shift line 41, the block_worktrees refusal text) is the real serialiser of the build. Nothing detects overlap,
and the rule is unenforceable by a seat that does not know which paths a helper will touch. Followed strictly it quietly
reduces writers toward 1; ignored, a pathspec commit carries a peer's half-edit (the trap table says so), and a peer's
`git add --all -- <path>` does the same. Tests also run against peers' half-written files, so a red or green is not
clean evidence, which goes to the owner's "fairly checked".

### 6. Conductor goodbye has the same flaw with no backstop

Goodbye is REFUSED with helpers alive, cancelled by any task notification, and the context backstop is OFF
(`backstop: false`). The Conductor is a light orchestrator whose work is all in helpers, and session mode has no helper
limit for 20 minutes after his last message. So a sitting with fan-out ends in "this window stays open" with no bound on
context. Worse at 8-10.

### 7. Quiet reductions to 1, and two definitions of alive

- `slot_rules.json fallback_n` gives FOUNDRY 1 when no budget is readable, so a broken allocator silently serialises the
  biggest seat. BENCH gets 3. Inverted against the v3 split (FOUNDRY takes the whole total).
- Disk brake: total 1 under 210 GB free. `ALMOST_OUT` 1. Both are defensible; only a visible alarm is missing.
- Spawn hook "running" is written within 900 s; `seat_restart` "alive" is 1800 s stale. A helper in a 20-minute gap is
  free for spawning yet blocks close-out.
- `helpers_of` returns UNMEASURED on any unreadable helper file. A torn line during a write gets likelier with N. Check
  that a partial trailing line is tolerated: not verified here. (READ, line 613-646.)
- `long_helpers_obs` watches BENCH only; FOUNDRY's 18618 s helper raised nothing.
- FOUNDRY's window is single-threaded: every Opus-class result is reviewed there, on Sonnet. Above some rate, review
  becomes the bottleneck or gets thinner. Rate UNMEASURED. This is the point where "fairly checked" and "maximised" meet.

### 8. What held up

Ledger append (flock plus O_APPEND, 3000/3000 no tear), per-seat shards with union merge, `next` under flock giving
distinct items, the never-kill-mid-turn rule, explicit-path commits, `reset --keep` over stash. **Correction to the
brief:** `next` is not one offer at a time in substance. It is serialised, but each call gets a different item, so it
is no concurrency limit. FOUNDRY.md's "your one item" wording is the only thing saying otherwise.

## Limit by limit: attack table

| limit | what it limits | requirement claimed | survives? | call |
|---|---|---|---|---|
| Close-out refused while a helper lives | a request, even a CONTEXT OK | do not lose a helper's result | Partly. Protects the kill, not the note | **Loosen**: request always accepted; only the kill defers |
| Restart hold on live helper | the kill | no orphan | Yes, with a bound | **Keep**, add drain plus timeout policy |
| No kill at the hard limit | the kill | never kill mid-turn | Yes | **Keep**; add spawn freeze |
| 110k tell, 200k hard | window context | cost and compaction quality | Yes; 228908 compaction floor stands | **Keep**; test under fan-out |
| Fresh window per ticket | window life | cheap context | No at fan-out: tickets overlap, so no moment is between them. Measured 5-25 h | **Replace** with fresh per drain, by context |
| Full belt floor "at all times" | idle | keep working | Yes, except during a drain | **Loosen**: suspended while draining |
| `next` "your one item" wording | nothing real | one owner per item | Lease does that | **Reword** |
| 45 min lease lapse | re-offer of a dead item | a slow worker keeps its item | Yes, but a dead helper is known within 15-30 min | **Keep** TTL; **add** auto-reclaim when the holder's transcript is finished. Lapses UNMEASURED; 270 takes, 185 renews, 74 releases in 7 days |
| Lease token per process | who may renew | no shared-identity theft | Yes, but it must outlive its holder | **Keep**; write token to the helper's progress file |
| Clone-local lease lock | two clones racing | documented gap | Only while one clone per seat | **Keep**; **must change** if clones per helper |
| One bridge driver | live game | one game | Yes | **Keep** |
| Slots total 10 | helpers | "more than about 10 never paid" [A] | Unproven: never reached by FOUNDRY, 8+ on 0 minutes | **Keep** as the test ceiling; decide from the trial arms |
| Cruise 6 | helpers | budget | Budget question, others' review | **Keep** |
| `fallback_n` FOUNDRY 1 | helpers on broken allocator | safety | No: wrong way round | **Loosen** to 3, with an alarm |
| Disk brake 1 | helpers | disk | Yes | **Keep**; alarm |
| Hook fails open | enforcement | never block on bug | Yes | **Keep** |
| 900 s vs 1800 s liveness | two counts | none stated | No | **Remove** one; single function |
| Stall 240 s, one ticket per ring | dispatch | no idle ring | Yes for a busy window; slow for filling 8 slots | **Loosen**: ring states free slots |
| Wake caps 12/h, 96/day | rings | no ring storm | Yes; 25 cap alarms | **Keep**, recheck after unwakeable is fixed |
| 600 s watchdog | a silent helper | a hung helper must die | Yes; six long gaps survived or died unread | **Keep**; progress writes are the fix |
| No SendMessage for helpers | redirection | none stated | Not a chosen rule | **Accept**; brief files must be complete |
| Helpers spawn no helpers | nesting | bounded tree | Yes | **Keep** |
| Goodbye refused with helpers | closing | his words are safe | Partly: note and rulings can be written now | **Loosen**: as restart; add a backstop decision for him |
| Any input cancels goodbye | restart | never lose his words | Yes for his words; no for a task notification | **Loosen**: helper returns do not cancel. His ruling touches this: put it to him |
| Shared clone, no worktrees | isolation | his ruling | See next section | **His call** |
| Writers one at a time on overlap | writers | no half-edits | Requirement yes, mechanism no | **Replace** with declared paths |
| Explicit-path commits | commit scope | no sweep | Yes, not sufficient | **Keep** |
| `./publish` unlocked | nothing | none | No | **Add a lock** |
| Handoff with no helper gate | nothing | "every subagent reported" | Rule unenforced | **Add** |

## Worktrees: the case for the owner

His ruling (by card, 2026-10-02) stands and nothing here assumes otherwise. I read its enforcement, `block_worktrees.py`,
not the card. Its stated reasons are two real failures: worktree agents duplicated full 4 GB checkouts by the hundred,
and reported work as committed while it sat on side branches or uncommitted.

**Case for changing it, narrowly.** Those are failures of worktree handling, not of isolation. The shared clone has
since cost: the lost-commit race (finding 1), index.lock failures, half-edits riding along, and test results polluted by
peers' files. A soft rule that serialises writers defeats his newer ruling on maximising parallel development. A bounded
pool of per-helper isolated copies would answer both old reasons: a hard count of about 10 reused slots stops the
hundreds, and a closing check that origin contains the helper's sha answers stranding.

**Case against.** The lock in finding 1 and path declaration fix most of the known loss with no change to his ruling.
Cost is real: `rimflow next` locks per clone, so distinct-item safety is lost unless the lock moves to a machine-wide
path; ledger writes from many clones reach origin late; a helper can no longer see a peer's change before it lands;
deploys and C# builds assume a seat clone; disk is already braked at 210 GB. Measured need is also unproven: FOUNDRY's
mean is 2.

**Recommendation.** Do not change it yet. Fix publish and declare paths, run 8-10 on that, count overlap refusals and
collisions. If writers are still queueing, bring him the numbers and ask for a bounded pool. Note the current hook blocks
worktrees, not `git clone`, so a clone-per-helper would pass the hook while breaking the spirit of his ruling. Nobody
should take that route without him.

## Requirements for 8-10 helpers per seat

Gate, before raising fan-out:

1. `./publish`: clone-wide flock over commit and land, and a HEAD compare before `reset --keep`; retry on `index.lock`.
2. Close-out split in two. The request always records (note, context reading, intent); only the kill waits. A live helper
   gets `DEFERRED`, never REFUSED, and the Dispatcher journals it. Rewrite FOUNDRY.md to match. Conductor goodbye the same.
3. Drain state. On a sized request or the hard limit: seat stops taking work, spawn hook refuses, Full belt suspended,
   running helpers finish. Bound: at 3600 s alarm with their names. Helper lease events and shard appends do not count as
   new work during a drain.

3a. Clones stay reclaimable. Every helper that makes a clone leaves it reclaimable: under a scratch root the expiry
    covers, work pushed or bundleable, no keeper inside, no live process left in it. Many subagents make this a capacity
    requirement, not tidiness: 8-10 helpers per seat multiply clones and session dirs, and before expiry ran the root disk
    lost 47 GB in a day. The expiry timer and its last-run alarm must be green before fan-out rises
    (`rimflow_v3_2026-10-26.md` section 3.1).

Next:

4. Helper registry on disk, one file per helper, written at spawn and updated by the helper: brief, item id, lease token,
   declared paths, progress path, transcript path. Survives the window. `wake_digest` and `handoff.py gates()` read it.
5. Auto-reclaim of a lease whose helper's transcript has ended or gone stale.
6. Declared write paths in the brief, checked at spawn: refuse overlap with a live helper; a pre-commit check refuses a
   path outside the declaration. This replaces "one at a time when paths could overlap".
7. Helper returns lighter on the window: a one-line result, details in a file, and the ledger close done by the helper
   where the item permits it, so context stops scaling with N. Independent review stays: a batched judge helper rather
   than the Sonnet window reading each. Keep "fairly checked" as a separate read.
8. One liveness function; `fallback_n` FOUNDRY 3 with an alarm; `long_helpers_obs` over FOUNDRY; ring says free slots.
9. Fix `unwakeable:FOUNDRY` first if the aim is real throughput: 218 alarms, and two-thirds of minutes at zero.
10. Trial: a measured run at 8 and at 10 on a seat with items 1-3 live. Report peak, collisions, lost commits, restart
    success, cost per closed item. Until then the 10 ceiling stays an unproven number in both directions.

## Evidence and gaps

Scratch (all in `/home/mandrake/.seat-tmp/BENCH/claude-1000/-home-mandrake-rm-bench/4cc19c6f-2fd0-4f11-9605-14783b9cc67e/scratchpad/`):
`conc.py`, `conc_foundry.txt` (concurrency), `ctx.py`, `ctx.txt` (context curves), `jr.py`, `jr.txt` (journal), `race/`
(publish reproduction, plumbing sequence by hand, not `publish.py` under a real race). Journal:
`/mnt/d/ClaudeWork/rimmandrake/dispatcher/journal.jsonl`, covering only 2026-10-28T22:00Z to 2026-10-31T22:29Z.

Counts of index_lock, refused_helpers and notifications are coarse substring matches over tool results: indicative only.

UNMEASURED: lease lapses and reclaims; whether a helper survives its window's exit; actual width of the publish race and
whether it has ever fired (walk the reflogs of both seat clones to find out, the first follow-up to do); same-file
collisions in the last 7 days; review throughput of the FOUNDRY window; why 10-27 and 10-28 had no helpers.

Not read: the worktree ruling card, `standing_rulings.md` git section, `doorbell.py` body, `helper_budget.py`,
`delegation_policy`, `Agent_Policy.md`, the `git-efficiency` skill. `night-shift-orchestration` and
`parallel-agent-worktrees` were grepped, not read through. The `helpers_of` torn-line handling needs a direct test.
BENCH's own concurrency was not measured; the brief asked for FOUNDRY.

Not filed: the brief was read-only, so no rimflow item or lesson exists for these findings. Finding 1 should be filed
first; it is live.
