# RimFlow — would it help us?

**Analysis for the owner, 2026-08-20. Written in the BUILD seat.**
Source proposal: `C:\Users\Mandrake\OneDrive\Desktop\RimFlow_Discovery_Architecture_and_Integration_Spec.md`
Everything numeric below was measured in this repo today, not estimated.

⚠️ **TRANSIENT.** This is a discussion document, not doctrine. Nothing here is decided.

---

## The one-paragraph answer

**Yes — but the proposal has the architecture backwards, and the evidence is in this repo already.**
RimFlow diagnoses the problem correctly and in some places understates it. But this project has
*already built* RimFlow's kernel, twice, and the results are conclusive: **the half of the board
backed by git works perfectly; the half backed by Markdown prose reads zero.** Right now
`status_matrix.json` says **116 items closed** (counted from `Closes:` commit trailers — correct)
and in the same file says **0 done, 0 blocked** (parsed from the queues' `state:` field), while its
own blockers panel, using different code on the same data, finds **2 blockers**. The board
contradicts itself inside one file.

That is the whole finding. It says the fix is not "move to SQLite" — it is **stop asking prose to
be a database, and put the ledger where durability already lives, which is git.** Build RimFlow's
domain model; do not build RimFlow's persistence layer.

---

## Part 1 — What is actually true here

### 1.1 The scale of the bookkeeping

| Measure | Value |
|---|---|
| Total commits | **1,554**, one author, **8 calendar days** (2026-08-13 → 08-20) |
| Commits touching `infrastructure/state/` | **697 = 44.9%** |
| Commits touching **only** state — pure bookkeeping, no code, no design | **470 = 30.2%** |
| Queue + state Markdown on disk | **827 KB ≈ 207,000 tokens** (`queue/` alone is 580 KB) |
| Items parsed across the six queue files | 167 (the derived matrix counts 176 — section banners parse as items) |
| Peak day | 452 commits (08-14) |

**Three in every ten commits in this repo move no work forward.** They move a line in a Markdown
file. And the queue is now larger than a 200k context window — `queue/CHECK.md` alone is 141 KB
(~35k tokens), so **no seat can hold its own inbox.** `doc_budget.py` already reports every queue
file over budget; `CHECK.md` is **+1,721 lines** past it.

### 1.2 The `state:` field is prose, and the board cannot read it

`state:` was designed as an enum. It is not one any more.

- Median `state:` line: **80 characters.** Longest: **202.** 91 of 142 exceed 60.
- **58 of 142 begin with an emoji**, not a word: ✅ 27, ⛔ 21, 🔵 5, ⭐ 4, 🔴 1.
- **68 of 167 items** carry a first token outside `{ready, doing, done, blocked, dropped}`.
- `queue/HUMAN.md` — 21 items — has **no `state:` field at all.** Nor `spec:`, `verify:` or `criteria:`.

`derive_matrix.py:277` classifies by exact string equality (`state == "done"`), and the parser
captures the whole rest of the line. So `state: done 2026-08-20, f0a9f6c.` **is not `done`.**
Measured against the live queue: exact `"done"` **0** · exact `"blocked"` **0** · exact `"ready"` 29
· everything else **56**, of which **28 actually say done/✅ DONE/built/PASSED** and **2 say blocked**.

**28 completed items are invisible to the board as done. Both blocked items are invisible as blocked.**

The docstring shows this is a *repeat* failure — it records the same collapse measured 2026-08-14
("the board was reporting 1/50"). The fix then was to count closures from `Closes:` trailers, which
worked and still works. **The filed-item classifier was never fixed and has silently re-broken.**
That is the strongest single argument in this document: the git-derived half survived four days of
churn and three ID-scheme migrations; the prose-derived half rotted in under a week.

### 1.3 Work does go backward — 11 measured instances

The proposal's central worry is real, though it is not the most expensive defect.

| Commit | Item | Transition |
|---|---|---|
| `365730e` | `seven-factions-have-no-required-count-9c4e17` | `✅ RULED (2026-08-15)` → `ready — RULED AND NEVER IMPLEMENTED` |
| `97bdb1a` | `B67` | `🔴 DONE, premise mostly WRONG` → `🔴 DO IT NOW — OWNER` |
| `97bdb1a` | `B25` | `ready — (b) DONE 2026-08-15 (4c2ddf8)` → `⛔ v2` (a finished half deferred out of v1) |
| `eab5e3c` | `B56` | `dropped — Mechanitors are cut` → `fixed offline, awaiting live half` (resurrection) |
| `b3af026` | `BLACKSTAR_HAS_NO_VESSEL_1` | `blocked on DECIDE` → `superseded` |
| …plus 6 more | | |

Three further reversals happened at the ruling layer rather than the state field — most notably
**B53**, whose "SEQUENCED AFTER WORLDGEN" ruling of 08-15 was reversed on 08-19 after four days.

The worst instance is `365730e`, whose own commit subject reads: *"A ruling four days old had never
reached the disk: seven factions still generate zero."* **A decision was marked ✅ and the code was
never written.** Nothing in the system could have noticed, because ✅ is not a state and nothing
links a decision to the artifact that satisfies it.

### 1.4 Blindness costs more than backward flow

- One item — `the-shipping-xenotype-drops-four-of-our-own-genes-7e31aa` — records in its own body:
  *"⚠️ This item had NO `state:` line for four days, so it was invisible to the board and to every
  seat sweeping by state."* **A missing field hid live work for four days.**
- **2 items are genuinely lost**: `softshadow-xtp-drops-two-renamed-genes-2f7c85` and `D-CHK1` —
  gone from the queue, absent from `V2_DREAMS.md`, absent from `closed_ledger.json`, no `Closes:`
  trailer. `softshadow`'s subject matter is *still live*, and `DECIDE.md` currently contradicts
  itself about it three lines apart.
- **`## B53` exists in both `queue/BUILD.md` and `queue/CHECK.md`** right now, with different
  `state:` and `verify:` bodies. The matrix counts it twice.
- **10 closures explicitly record that the work was already done or the premise already stale** —
  items opened against work that already existed.
- Live example created during this very session: a queue item is filed **blocked on Pillow**;
  Pillow 12.3.0 was installed twenty minutes ago and nothing updated the item. The blocker cleared
  and the state did not.

### 1.5 Verification is prose. There is no pass/fail anywhere as data.

`verify:` is a free-text field (129 occurrences; **HUMAN.md has 0**). Results get written *into the
`state:` prose* — `state: ✅ DONE — PASSED 2026-08-19, by cell diff…`.

I searched every JSON under `infrastructure/state/` for a key matching `pass|fail|verif|test|result|
evidence|proof`. **There are none.** `closed_ledger.json` stores `{row, col, sha, at}`.
`status_matrix.json` stores `{rows, blockers, velocity}`. The three `Player.log` files in
`observed/logs/` (18,563 + 11,730 + 7,250 lines) are **linked to no item ID at all** — the most
expensive evidence this project produces, at ~25 minutes a cold load, is stored unjoined.

This is RimFlow's sharpest correct insight (§4.6/§4.7) and it is the gap with the highest payoff.

### 1.6 The vocabulary and the IDs have already forked twice

- Three ID schemes coexist on disk **today**: **107 legacy** (`B41`, `C1`, `D-CHK2`, `W6`) ·
  **44 kebab-slug-hash** · **42 `SCREAMING_#`** · plus ~50 headings parsing as none of the three.
  The new scheme *is* being adopted (45 of 59 new items on 08-20), but it is the **third** in eight days.
- Two distinct slugs share the supposedly-unique 6-hex suffix `5e12b7`.
- `38c4908` records *"two agents raced onto the same number"* — B63 → B64.
- **`row:` is an unenforced foreign key into `V1.md`.** V1 defines rows 0–13; queue items reference
  **32 distinct values, 20 of which do not exist in V1.md** (`bridge-6`, `world-7`, `inhabited-3`,
  `doctrine`, `tooling`, `dead`, `repo`, `v2`, `unassigned`…). A parallel taxonomy grew inside a
  field with no integrity check.
- Deleted queue locations found in history: `queue/{CREATE,BRIDGE,OPS,PROJECT,VISION}.md`,
  `AGENT_*_state.md`, `TODO.md`, `TODO_v2.md`, `CLOSED.md`, `V1_SCOPE.md`, `blockers.json`,
  `facts/{LIVE,BUILDABLE}.md`. **The queue system has been re-architected at least twice in eight days.**
  A third rewrite needs to be the last one, which is an argument for a small, boring, durable core.

### 1.7 Two live defects worth naming, independent of any decision here

1. **`.claude/hooks/warn_unclosed_queue_item.py:40-41` uses `[A-Z][A-Z0-9-]*` — underscores are not
   in the class.** `derive_matrix.py:88` uses `[A-Za-z][A-Za-z0-9._-]*`, which includes them. Under
   the owner's new naming rule the hook matches only the first word — `INHABITED` out of
   `INHABITED_DISPLACED_POOL_1`. The two tools disagree on **every new-style ID**, and the hook
   `exit 0`s unconditionally so it can only nag.
2. **The classifier bug in §1.2.** One-line fix (`state.split()[0]`), and it recovers 28 done items
   and 2 blockers immediately.

Fix both regardless of which option below is chosen. Together they are under an hour.

### 1.8 What the environment will actually support

- **Python 3.14.4, system interpreter. No venv, no `pyproject.toml`, no `requirements.txt`.**
- Available: `numpy`, `lxml`, `PyYAML`, `requests`, `rich`, `Pillow`.
  **Absent: `fastapi`, `pydantic`, `sqlalchemy`, `alembic`, `jinja2`, `flask`, `pandas`, `scipy`.**
- **No CI, no `Makefile`, no `.pre-commit-config.yaml`, no `tests/` directory.** Enforcement in this
  project happens in **Claude Code hooks** and hand-run `selftest_*.py` — and it *works*:
  `block_blanket_git_stage.py` and `block_peer_messages.py` both changed behaviour where prose alone
  had not.
- `sqlite3` is stdlib, so it is free. Everything else RimFlow §8 names is a new dependency on a
  machine with no dependency management.
- **There is not a single `.db` or `.sqlite` file in the repo.** Every store is a flat file, and
  `.gitignore` is 213 lines of discipline about which are derived.

---

## Part 2 — Where the proposal is right, and where this repo overrules it

### Right, and confirmed by measurement

| RimFlow claim | Verdict |
|---|---|
| §1.1 current state is hard to reconstruct | **Confirmed** — the board reads 0 done against 28 real ones |
| §1.2 work gets pushed backward | **Confirmed** — 11 instances + 3 ruling reversals |
| §1.4 tests are status, not evidence | **Confirmed, and worse** — zero structured results exist anywhere |
| §2.4 stable IDs joinable across systems | **Confirmed** — 3 schemes, a hash collision, a race on B63 |
| §2.5 append evidence, never overwrite | **Confirmed** — and already half-implemented via `Closes:` trailers |
| §4.13 append-only event ledger | **Confirmed** — `closed_ledger.json` *is* one, derived from git |
| §5.2 prohibited backward transitions | **Confirmed** as the right rule |
| §2.2 lifecycle ⟂ planning horizon | **Confirmed** — `B25` was moved to v2 *while done*, losing the done-ness |

### Overruled by this repo

**1. §2.7 / §8 — "SQLite initially", and §9 "keep the active `.db` outside ordinary Git history".**
This collides head-on with the owner's standing rule that *committed and pushed is the only durable
state*, issued after a reboot destroyed a session's scratchpad. A binary DB outside git is exactly
the artifact that rule exists to forbid. **And it is unnecessary: git already gives us an
append-only, replicated, human-diffable ledger with authorship and timestamps, and the one part of
the board that works is the part that reads it.** Put the events in git; make SQLite a *rebuildable
index*, deletable at any time, like `closed_ledger.json` already is.

**2. §8 — FastAPI + SQLAlchemy + Alembic + Pydantic + Jinja2 + HTMX.**
Six new dependencies on a system interpreter with no venv, in a repo whose 33.5k lines of Python are
stdlib-first by policy. The board already exists (`status_server.py`, 390 lines, stdlib, serving
`localhost:8787`) and already consumes derived JSON. Extend it.

**3. §10–§11 — "creative mission control", eight UI views.**
That is a product. This project has a hand-built world with a freeze deadline ahead of it, and 96%
of its disk is game assets. The Command Deck's content — agent lanes, blockers, velocity, human
attention — is *already computed* in `status_matrix.json` and already rendered.

**4. §12 / §16 — estimation, forecasting, estimate-error learning.**
`status_matrix.json` already carries `{closed: 116, remaining: 60, per_day: 16.57, eta_days: 4}`.
Eight days of history across three ID schemes and two queue re-architectures cannot train anything
better than that. The rollup is honest because it is coarse.

**5. §17 / §22 Stage 5 — migrating the Markdown queues into the database.**
The queue prose is not a database record with formatting noise. It is **argument** — owner rulings
quoted verbatim, reversals with dates, warnings about what a check cannot prove. `B41`'s `verify:`
field is a paragraph explaining why `raidsForbidden` must be an `Add` and not a `Replace`. That
belongs in Markdown forever. **What must leave Markdown is the ~8 scalar fields per item, not the prose.**

**6. §6 — "agents must not receive raw write access".**
Every seat here has `Bash(python3 *)` and a full shell. A capability boundary implemented as an API
is advisory. **The boundary that works in this repo is a `PreToolUse` hook**, which is enforced by
the harness before the tool runs and has already proven itself twice.

---

## Part 3 — Three options

### Option A — Enforce the contract that already exists
*Keep Markdown as the source of truth. Make a machine check it and refuse bad writes.*

**Build**
1. Fix `derive_matrix.py`'s classifier (`state.split()[0]`) and the hook's regex. *(~1 hour, recovers 28 done + 2 blockers)*
2. `queue_lint.py` — a **blocking** `PreToolUse:Bash` hook on any `git commit` touching `queue/`. Refuses:
   - `state:` whose first token is outside the enum;
   - a new `## <ID>` item missing `spec:` / `verify:` / `criteria:`;
   - a duplicate ID across queue files (catches the live B53);
   - an ID matching no known scheme;
   - a `row:` value absent from `V1.md`;
   - **a backward transition** — diff the item's `state:` against `HEAD`, refuse `done → ready`,
     `done → blocked`, `dropped → ready` without an explicit `--admin "reason"` escape.
3. `/queue-item` skill that emits a correctly-shaped skeleton.

**Cost** ~500 LOC stdlib Python. **One day.** Zero new dependencies. Zero migration.

| For | Against |
|---|---|
| Fixes the measured blindness immediately | Does nothing about the **207k-token** context tax |
| Enforcement at the layer already proven to work here | `verify:` results stay prose — the evidence gap is untouched |
| Nothing to migrate, nothing to learn, nothing to lose | No fan-out graph: a decision still cannot point at its builds |
| Reversible in one commit | Six files stay merge-hot across four seats |
| **This is strictly a prerequisite for B and C** — do it either way | Prose will drift again; a linter slows decay, it does not stop it |

---

### Option B — Ledger in git, one file per item, Markdown queues become rendered views ⭐
*RimFlow's domain model, on this project's existing durability story.*

**The shape**

```
infrastructure/state/
  events.jsonl          APPEND-ONLY. Committed. THE source of truth.
  items/<ID>.md         one file per item: YAML front-matter + prose body
  queue/<SEAT>.md       GENERATED VIEW. Header says "derived — do not edit."
  index.sqlite          gitignored, rebuildable: `rimflow reindex`
```

- **`events.jsonl` is the truth and it lives in git.** One JSON object per line, appended, never
  rewritten: `{ts, actor, event, id, payload, caused_by}`. Git supplies durability, replication,
  authorship, timestamps and `git blame`. Append-only merges cleanly — this is the one file format
  where four seats writing at once is a *non-problem*.
- **`items/<ID>.md` — one file per item.** This single change carries most of the value:
  - kills the 207k-token tax (a seat reads its ~6 ready items, not 141 KB);
  - kills merge contention on six hot files across four seats;
  - makes `git log -- items/B53.md` the item's whole history for free;
  - makes the duplicate-B53 class *structurally impossible* — one ID, one path.
- **Front-matter carries the ~8 scalars. Prose stays prose, below the fence, untouched.**
- **The overloaded `state:` splits into four orthogonal fields**, which is RimFlow §5.1's best idea:

  | field | values | today's conflation |
  |---|---|---|
  | `lifecycle` | `proposed ready doing done dropped` | everything crammed here |
  | `blocked` | `false` \| `"<reason>"` | `blocked` competes with `done` |
  | `disposition` | `—` \| `passed` \| `failed` | `✅ DONE — PASSED` is two facts |
  | `target` | `v1` \| `v2` \| `vN-storage` | `⛔ v2` erased `B25`'s done-ness |

- **Verification becomes data.** `rimflow verify <ID> --result pass|fail --evidence <path> --config <modlist>`
  appends a run event. **A run is never edited; a re-run is a new event.** This closes §1.5 and
  finally joins the Player.log files — the most expensive evidence we produce — to the items they decide.
- **`rimflow` CLI, stdlib-only**, roughly the vocabulary already spoken here:
  `ready --seat BUILD` · `claim` · `block "<why>"` · `verify` · `finding` · `rework --from` ·
  `retarget <ID> v2 --reason` · `close` · `render` · `reindex` · `why <ID>`.
- **The lint hook from Option A stays**, now refusing hand-edits to generated queue files and
  enforcing forward-only transitions at the event layer.
- **`derive_matrix.py` keeps reading `Closes:` trailers** — that mechanism is proven; it becomes one
  event source among several rather than the only one that works.

**Cost** ~1,500–2,500 LOC stdlib Python. **Four to six focused days**, and it can ship in stages —
Option A is literally its stage 1, and `items/` split is a mechanical migration of files that already
have consistent headings.

| For | Against |
|---|---|
| Solves **all four** measured defects: blindness, backward flow, context tax, evidence gap | Four to six days that are not the world, the roster or the faiths |
| Durability is git — no new backup story, obeys the standing commit-and-push rule | `events.jsonl` grows unboundedly (~40 KB/1000 events; irrelevant at this scale) |
| Prose survives untouched, which is where the actual project knowledge lives | Rendered queues mean seats must learn "don't hand-edit that file" — the hook enforces it |
| SQLite is a cache you can delete — **the failure mode of C cannot happen** | Migration touches all 167 items (mechanical, scriptable, reviewable as a diff) |
| Fan-out becomes real: a decision points at its builds, a run at its finding, a finding at its rework | Still no GUI beyond the existing board |
| Zero new dependencies; runs on the system interpreter as-is | A fourth ID scheme is tempting — **resist it**, add an alias map instead |
| Commit volume should fall hard: much of the 30% pure-bookkeeping churn becomes one appended line | |

---

### Option C — RimFlow as specified
*SQLite primary, service layer, FastAPI, MCP, eight-view mission-control UI.*

**Cost** three to four weeks, six new dependencies, and a second product to maintain beside the game.

| For | Against |
|---|---|
| The graph view genuinely answers "why is this not done" better than any text can | The DB is a binary blob; keeping it out of git contradicts the standing durability rule, and putting it in git makes every mutation a merge conflict |
| Policy hooks (§13.4) would encode rules currently living only in POLICY.md prose | `fastapi`+`sqlalchemy`+`alembic`+`pydantic`+`jinja2` on a system interpreter with **no venv** |
| Genuinely portable to other projects, which is a real long-term want | Forecasting (§16) has 8 days of history across 3 schemas to learn from |
| The Validation Matrix (§11.4) is the right picture of live-config coverage | Migration into the DB pulls owner rulings out of the prose that carries their argument |
| | The queue has been re-architected twice in 8 days; the third rewrite should be the *smallest* one that lasts, not the largest |
| | It competes for the exact days the world freeze needs |

**C is the right destination if RimFlow becomes a product in its own right.** It is the wrong next
step. Note that **B is the honest on-ramp to C**: `events.jsonl` is precisely the import source a
future SQLite kernel would replay, so nothing built in B is thrown away by later choosing C.

---

## Part 4 — What I recommend

**Option B, with Option A shipped on day one as its first stage — and A alone is a legitimate place to stop.**

The ordering matters because A's payoff is immediate and its cost is a rounding error, while B's
payoff needs a migration. If B stalls, A has still recovered a board that tells the truth.

### Stage 1 — the day's work *(do this regardless of anything else)*
- Fix `derive_matrix.py:277` (`state.split()[0]`) and the `warn_unclosed_queue_item.py` regex.
- Land `queue_lint.py` as a **blocking** hook.
- Reconcile the two lost items (`softshadow-xtp-…-2f7c85`, `D-CHK1`) and the duplicate `B53`.
- Clear the stale Pillow blocker.

**Verification that Stage 1 worked:** `status_matrix.json` reports **≥28 done and 2 blocked** instead
of 0 and 0, and a deliberate `done → ready` edit is refused by the hook.

### Stage 2 — split the items *(highest value per hour in the whole plan)*
Mechanical migration of the 167 items to `items/<ID>.md` with front-matter; `render.py` regenerates
the six queue files as views. Nothing else changes yet. This alone removes the context tax and the
merge contention, and it is reviewable as a diff.

### Stage 3 — the ledger
`events.jsonl` + the `rimflow` CLI. Seats stop hand-editing state and start appending events.
`render.py` and `derive_matrix.py` both read the ledger. Forward-only enforced at the event layer.

### Stage 4 — evidence
`rimflow verify` records runs as immutable events with a config fingerprint and an evidence path,
joining `observed/logs/*.log` to the items they decide. **This is the stage that would have caught
`365730e`** — a ✅ decision with no artifact and no run against it becomes a query, not a memory.

### Stage 5 — surface *(only once 3 and 4 have run for a week)*
Extend `status_board.html` with a per-item "why" view off the ledger. An MCP wrapper over the CLI is
the natural last step — thin, calling the same code — but the CLI has to be right first.

### Rules I would hold to throughout
1. **Git is the ledger. SQLite is a cache you can `rm` at any time.** Never the durable copy.
2. **Prose is never migrated into structured fields.** Only the ~8 scalars move.
3. **No fourth ID scheme.** Freeze the current three, add `aliases.json` so old IDs resolve forever.
4. **Every enforcement point is a hook**, because in this repo that is the only boundary that has
   ever held.
5. **The queue files stay readable by a human with `cat`,** generated or not. The owner reads them.
6. **Ship Stage 1 before anything else is designed.** A board that lies is costing us now.

---

## Part 5 — Answers to the spec's §25 questions, from evidence

| # | Question | Measured answer |
|---|---|---|
| 1 | What is a root Feature? | A **V1.md row** (0–13). Already exists, already the `row:` key — but 20 of 32 referenced values aren't in V1.md |
| 2 | Which concepts are Findings vs Work? | Findings have no representation at all today; they live inside `state:` prose |
| 4 | What makes work READY? | Nothing checks it. `ready` is the parser's **default** for any unrecognised string — which is why 56 items read `ready` |
| 5 | BUILD completion? | Artifact in `src/`, `verify:` output **pasted not asserted**, item appended to `CHECK.md`, `Closes:` trailer. Well-defined in POLICY.md, enforced nowhere |
| 7 | Which configurations recur? | Two, sharply: **13-mod minimal (22 s)** and **577-mod full (~25 min)**. This is the natural `configuration` dimension and it is already how the project thinks |
| 8 | Which bridge actions should record evidence? | Any `world_*` write, and every load round — `observed/logs/*.log` is currently orphaned from all item IDs |
| 10 | Commits ↔ work when several share one commit? | Already solved: multi-`Closes:` trailers. 151 commits carry 123 unique IDs |
| 13 | v1/v2/vN mapping? | v1 = queue files, v2 = `design/V2_DREAMS.md` (explicitly *not* a queue), vN = does not exist. `B25` proves the gap: moving it to v2 **erased that it was done** |
| 16 | Which history is importable? | `closed_ledger.json`'s 116 resolved items — high confidence, derived from git. The `state:` fields — low confidence, 68/167 non-canonical |
| 18 | Hardest REP questions? | "What is actually done" — the board cannot answer it. "What did that failure cause" — nothing links a run to a rework |
| 20 | What does the repo contradict? | **§2.7/§8/§9** (SQLite-primary, DB outside git), **§10–11** (mission-control UI), **§16** (forecasting), **§17** (migrating prose) |

---

## Part 6 — Honest risks in my own recommendation

- **Four to six days is four to six days.** The world freeze is ahead, and one hand-made planet is
  the deliverable. Stage 1 (one day) captures a disproportionate share of the value; stages 2–5 are
  a genuine bet that this project has enough runway left to repay them.
- **`render.py` is a new drift machine.** A generated file that someone hand-edits is worse than a
  hand-kept one. The hook must refuse those edits from day one, not "later".
- **`events.jsonl` needs a compaction story eventually.** Not at this scale — 1,554 commits would be
  a few thousand events, well under a megabyte — but it should not be discovered as a surprise.
- **I am the BUILD seat proposing to rebuild the system that grades BUILD.** That is a conflict worth
  naming. The verification criteria in Stage 1 are deliberately written as numbers someone else can check.
