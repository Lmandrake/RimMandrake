# rimflow: the work-item system, and why items get stuck (2026-10-07)

## 0. Purpose and how to read this

This is written for a reviewer who cannot see the repository. It describes `rimflow`, the
work-item tracker used by the AI agent windows that build a large RimWorld mod project, and
measures why work items get stuck in it. Every number below was measured on
2026-10-07 ~01:20 UTC by replaying the ledger with rimflow's own reader
(`model.read()` + `model.replay()`) and cross-checking against `git log`. A number that could not
be measured is marked **UNMEASURED**. The question for the reviewer is at the end (§6): how
should the system change so that finished work stops looking unfinished.

Context you need: the project is built by two long-running Claude agent "windows" (seats)
called **BENCH** (works with the human owner) and **FOUNDRY** (autonomous build queue), which
fan out short-lived subagents. A RimWorld cold load takes ~15 minutes, and only one window may
drive the live game (via a "bridge") at a time, so **live verification is scarce and offline
building is cheap**. That asymmetry drives most of what follows.

## 1. Architecture

### 1.1 The ledger (source of truth)
- Append-only JSONL. A frozen history file `infrastructure/state/ledger/events.jsonl`
  (10,890 lines) plus one shard per seat since 2026-09-23: `ledger/events/BENCH.jsonl` (1,223),
  `FOUNDRY.jsonl` (3,147), `OWNER.jsonl` (230). Total **15,490 events**, folding into
  **2,494 items**. Git merges shards with `merge=union`; the reader dedupes by content and
  orders by `ts`, `tsn`, subject, a fixed verb rank and seat — never file position.
- Event fields: `seat`, `event` (the verb), `id` (the item — **not** `item`), `ts`
  (UTC ISO second), `tsn`, plus verb-specific fields (`to`, `sha`, `reason`, `text`, `for`…).
  Example: `{"seat":"FOUNDRY","event":"start","id":"SHOKKWEAVE_SOLE_SOURCE_1","ts":"2026-09-24T05:24:08Z"}`.
- Only `rimflow` writes it (`model.append()` with an flock); a PreToolUse hook (`queue_lint.py`)
  refuses any other writer. A projection (`Item`) is rebuilt from scratch on every command;
  nothing about an item is stored except events.

### 1.2 Items, prose, views
- **Item id**: `SUBJECT_INTENT_TWIST` for new items (e.g. `BRIDGE_HANG_UNSTICK_THIRD_TIME_LUCKY`; `ticket_naming_2026-10-10.md`); legacy `…_1` ids such as `STILLSAND_SOLAR_STILL_1` stay valid.
- **Prose** (optional): `infrastructure/state/items/<ID>.md` with conventional sections
  `## spec`, `## verify`, `## criteria`. On close/drop/supersede the CLI moves it to
  `items/closed/`. 395 live prose files today.
- **Queue views**: `infrastructure/state/queue/<SEAT>.md`, gitignored, rendered on read by
  `rimflow queue <SEAT>` (`render.py`). Sections: NEXT (rank order), IN PROGRESS (`doing`),
  BLOCKED, WAITING ON A WINDOW, NOT THIS TARGET, PROPOSED. There is deliberately **no CLOSED
  section** and **no "built, awaiting proof" section**.
- **Seats**: `BENCH`, `FOUNDRY`, `OWNER` (the human). Legacy seats DECIDE/BUILD/CHECK/REP
  exist only so history replays. Subagents are not seats; they act under their window's seat.

### 1.3 Lifecycle
- **States** (`model.STATES`): `proposed` → `ready` → `doing` → terminal `done` | `dropped` |
  `superseded`. Terminal is absolute (no reopen; file a new item with `caused_by`).
- **`blocked` is a flag, not a state** — an item can be blocked while proposed, ready or
  doing. It means "something is WRONG". It never lifts itself; closing the blocker only
  prints a hint.
- **`needs`** is a second, independent axis: *when* the item can be worked —
  `offline | deploy | game-up | bridge | harvest | owner`. Default at filing is `offline`.
  It changes only via an explicit `rimflow needs <ID> --to X`.

### 1.4 Verbs (from `rimflow --help`)
| verb | effect on projection | who may |
|---|---|---|
| `file` | creates item, `proposed`, needs default `offline` | any |
| `claim` | owner := caller, state → **`ready`** ("always reaches ready") | owning seat |
| `start` | → `doing` (no completeness gate since 2026-08-21) | owning seat |
| `block`/`unblock` | sets/clears flag + reason/`--on` | owning seat |
| `verify` | appends an immutable run record (pass/fail/partial, config, evidence) — **does not change state** | owning seat |
| `needs` | sets `needs` | BENCH or owning seat |
| `reclaim` | `doing` → `ready` for your own item | owning seat |
| `reassign` | owner := X; `doing` → `ready` | BENCH |
| `close --sha` | → `done`; **requires only a sha (defaults to HEAD)**, optional `--reason` | any seat (owner ruling 2026-09-19) |
| `drop --reason` / `supersede --by` | → terminal | any seat |
| `note --text` | appends a line; no state effect | any |
| `next`, `show`, `why`, `queue` | read-only | — |
| `sweep --transient`, `lint --citations` | read-only lists (see §4) | — |

### 1.5 `rimflow next` and `priority.rank()`
`rank()` is a pure function: owner == seat, **state == `ready`**, not blocked, target == v1,
`needs` satisfiable in the current game state (`offline` always true; `bridge` needs game
UP and the lock free or yours; `owner` false only in AFK mode). Sort: `this_deployment`
desc, v1 row asc, `created_at` asc (oldest first). `next` prints the top item's id, title,
and its `spec`/`verify`/`criteria` sections, then `-> rimflow start <ID>`. If nothing is
`ready` it offers the oldest `proposed` item to claim. **`doing` items are never offered**
(by design: the 2026-08-21 work stop parked items as `doing` precisely to hide them).

### 1.6 Closing doctrine (prose, not code)
`CHARTER.md`: "Close: `rimflow close <ID> --sha <commit>`, commit carrying `Closes: <ID>`,
push" and "**done means proven, dead means probed**". `FOUNDRY.md`: "Claim, start, work,
`close --sha`, commit with `Closes:`, push, next" and "A live check is owed only to a
mechanism never once observed running — the owner playing is the default validation."

### 1.7 Handoffs
At a context reboot a window writes `infrastructure/state/handoffs/<SEAT>_HANDOFF_<stamp>.md`
via `handoff.py` (189 files). Its half-done section is agent-authored pointers in the
fixed shape `` - `ITEM_ID` — state; NEXT: <one imperative action> `` (measured: pointers
with a concrete NEXT get near-100% pickup, prose ~0%). The next window runs
`handoff.py --wake`, which prints each pointer with its live ledger state.

## 2. How items get stuck — measured

### 2.1 The whole board
| state | items |
|---|---|
| done | 1,849 |
| dropped | 102 |
| superseded | 71 |
| proposed | 200 |
| ready | 40 |
| doing | 232 |
| **open (proposed+ready+doing)** | **472** |

Open items by (state, needs):

| state \ needs | offline | owner | bridge | deploy | game-up | total |
|---|---|---|---|---|---|---|
| proposed | 78 | 47 | 54 | 8 | 13 | 200 |
| ready | 27 | 11 | 2 | 0 | 0 | 40 |
| doing | 132 | 27 | 52 | 15 | 6 | 232 |

By owner: FOUNDRY holds 210 doing, 38 ready, 141 proposed; BENCH 22 doing, 2 ready, 51
proposed; OWNER 8 proposed. (`harvest` holds no open items.)

### 2.2 Staleness (age of the item's last ledger event of any kind)
| | count | >3 days | >7 days | >14 days |
|---|---|---|---|---|
| `doing` | 232 | **201** | **117** | 48 |
| `ready` | 40 | 6 | 5 | 4 |

Blocked: **96** open items carry the blocked flag (62 doing, 23 proposed, 11 ready); the
read-only `queue_staleness_review.py` lists 155 stale doing/blocked items and 19
`needs` mis-tags. Several blocked items are 19–27 days idle with reasons that reference
dependencies or owner decisions that have since moved (e.g. `TREE_GRAPHICS_OWNERSHIP_1`,
27 d, "true blocker moved and was never synced").

### 2.3 Built but not closed — the core finding
- **186 of the 272 `ready`+`doing` items (68%) are named in the *subject line* of at least
  one commit** since 2026-08-15 (99 doing/offline, 16 ready/offline, 20 doing/owner,
  20 doing/bridge, 14 doing/deploy, …). Naming in a subject is the house convention for
  "this commit is that item's work".
- **146** ready/doing items carry a `note` whose text says built / published / pushed /
  landed / "at <sha>" (128 doing, 18 ready; 123 authored by FOUNDRY; 104 cite a sha). By
  needs: 96 offline, 18 owner, 17 bridge, 11 deploy, 4 game-up.
- **6** open `doing` items even have a `Closes: <ID>` trailer in a commit
  (`VAULT_DUNGEON_BUILD_1` b54836745, `KYBER_TRADE_PLOT_1` 90059a2a1,
  `DROIDWORKS_WIPE_SEVERITY_1` 07db73738, `FEVERWOOD_ANT_HIVE_DUNGEON_1` e7fc2faea,
  `SCALD_WATER_AGITATION_FLECKS_1` 03338952d, `DIRTY_CODE_REVIEW_STANDING_LOOP_1`).
  Sanity probe: 655 `done` items have such a trailer, so the matcher works.
- Only **3** ready/doing items have any `verify` run recorded, and **0** of those passed.
  The `verify` verb is essentially unused as a path to closure on current work.

### 2.4 This session's dispatch, verified
In the 2026-10-06 FOUNDRY session roughly 14 of 15 offline items an agent was sent to build
turned out to be already built and pushed. Every example below was checked: the commit exists,
its subject names the item, and the item is **still open today**.

| item | state / needs now | built at | ledger events |
|---|---|---|---|
| WEBWORK_TRACTION_LANCE_BUILD_1 | ready / offline | 598dec613 (10-06 18:48Z) | file 10-02, claim 10-06 18:19, note "598dec613: offline build published; live proof … owed" |
| GREENTIDE_STELLOCK_LACE_BUILD_1 | ready / offline | 598dec613 | file, claim, note "offline build published; live criteria + art install owed" |
| WEBWORK_DEAD_GIANT_BUILD_1 | ready / offline | 598dec613 | file, claim, note "… art install, live check, validation.py chain owed" |
| RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1 | ready / offline | db013a05e | file, claim, note |
| MINDSTONE_MATRIX_KINDLED_BUILD_1 | ready / offline | 721e81866 | file, claim (no note) |
| UNFINISHED_LINE_TITHE_BEAT_1 | ready / offline | 490988350 | file, claim (no note) |
| FEVERWOOD_RM_CAST_COMPLETION_1 | ready / offline | 5833cced4 ("4 of 7 owed") | file, note, claim |
| WARSCAR_TOTCHAK_WAKES_1 | doing / offline | 455e8e147 (10-03) | file, claim, start — nothing since |
| STILLSAND_SOLAR_STILL_1 | doing / offline | 72a77c044 (10-03) | file, claim, start — nothing since |
| GELATINOUSSLIME_TITAN_CHUNK_BOMB_1 | doing / offline | ab069c26e (10-03) | file, claim ×2, start |
| ARMOURY_JUMPPACK_INVALID_IL_1 | ready / offline, **no prose file** | 618463ba1 (10-05) | file, claim, note "Only a live run confirms … NEXT: confirm in the next live run, then close" |

`SALVAGE_WRECKAGE_EVERYWHERE_1` (ready/offline, FOUNDRY): reassigned from BENCH 10-03 after
nine design notes; claimed 10-06 18:33Z and **claimed again** 10-07 01:21Z. Its prose file
`items/SALVAGE_WRECKAGE_EVERYWHERE_1.md` did not exist until commit 1fbac6c48 (10-07 01:25Z),
so for every earlier offer `next` printed *"(items/SALVAGE_WRECKAGE_EVERYWHERE_1.md has no
sections — it should not have reached `ready`)"* and showed no spec at all. Meanwhile its
work had shipped: slice 1 96f8113e9, slice 2 398519ab3, slice 3 562214d81 (all 10-06
18:51–19:22Z, i.e. after the first claim), step 5 1fbac6c48. **No ledger event records any of
those four commits**, so the item stayed `ready` and `next` kept offering it as fresh work.

### 2.5 Prose completeness
- **78** open items have no prose file (50 proposed, 22 doing, 6 ready).
- **151** open items have a prose file with no `## criteria`.
- **347 of 472** open items lack at least one of spec/verify/criteria.
- Of the 159 ready/doing items marked `needs: offline`: 47 have criteria that are purely
  offline, **44 have criteria worded for a live game** (quicktest, in-game, bridge,
  Player.log, spawned…; regex heuristic, sanity-probed), 44 have no criteria section, 24 have
  no file. So at least 44 items are labelled "offline" while their own definition of done
  requires the game.

## 3. Why it happens — read from the code

**3.1 Close does not require live proof in code — the requirement lives in doctrine and
criteria, so agents enforce it on themselves.** `model.VERBS["close"]` requires only `sha`;
`cmd_close` defaults it to HEAD. Nothing checks a `verify` run. The barrier is three
layers of text: CHARTER's "done means proven"; item `## criteria` that are written as live
observations (WEBWORK_TRACTION_LANCE_BUILD_1: "Quicktest: a manned `RM_TractionLance` … pulls
a spawned raider N cells"; WARSCAR_TOTCHAK_WAKES_1: "A Warscar quicktest with ruins places one
dormant totchak…"); and a PreToolUse hook (`warn_close_live_proof_owed.py`, backed by
`live_proof_lint.py`) that warns when a closing commit says "live proof owed" without a
spawned successor. FOUNDRY.md adds "a live check is owed only to a mechanism never once
observed running" — which is every new build. So an honest builder who finishes the offline
part writes a note ("offline build published; live proof owed") and leaves the item open.
Live runs are scarce (one bridge, 15-minute cold loads), so the item waits indefinitely.
There is **no state** that means "offline part done, live proof owed"; the only choices are
open (and indistinguishable from unbuilt) or closed (felt to be dishonest).

**3.2 `needs` is never updated when the offline part ships.** It is set at `file` (default
`offline`) and changes only on an explicit `rimflow needs` (318 such events in 15,490). No
verb, note or commit hook moves an item from `offline` to `bridge`/`game-up` when the remaining
work becomes live-only. So a built item keeps `needs: offline` and stays in the pool that is
offered to *offline builders* — the one audience that cannot finish it.

**3.3 `Closes:` trailers close nothing.** Doctrine says commit with `Closes: <ID>`, and 364
commit bodies since 2026-09-06 carry one. But no code in `rimflow/` reads them: a comment in
`model.py` says "`importer.py` walks those trailers out of git", and **no `importer.py` exists
in the repo**. The trailer is only read by `warn_unclosed_queue_item.py` (a warning on hand
edits to the old markdown queues) and by humans. 6 open items carry one (§2.3).

**3.4 `claim` puts an item straight into the offered pool.** `claim` sets owner and
transitions to `ready` unconditionally (the "completeness gate" was removed by owner ruling
2026-08-21). `rank()` offers exactly `ready`. So claim = "make it the thing `next` offers";
only `start` (→ `doing`) hides it. 36 of the 40 `ready` items were claimed and never started.
The four 598dec613 items show the cycle: claimed 18:19–18:30Z, built 18:48Z, noted 18:49Z,
never started, never closed — so `next` re-offers them, oldest-first, ahead of genuinely
unbuilt work. The message *"has no sections — it should not have reached `ready`"* is a
leftover from the removed gate (it is printed when `read_prose()` returns nothing, i.e. the
file is missing); the code that would have prevented it no longer exists.

**3.5 `doing` is a black hole in the other direction.** `rank()` never offers `doing`, and
the view's IN PROGRESS section says only "Started, and therefore not offered again".
WARSCAR/STILLSAND/GELATINOUSSLIME were started 10-03, built the same night, and have had no
event since. Nothing distinguishes "being worked", "built, awaiting live", and "abandoned";
201 of 232 `doing` items have been silent >3 days.

**3.6 Queue views cannot show "built but unverified".** `view_sections()` partitions on
state/blocked/needs only. It never reads notes, commits, or verify runs, so a built item
renders as NEXT (if `ready`) or IN PROGRESS (if `doing`) exactly like an unstarted one.

**3.7 Handoffs carry the debt forward as "NEXT: run live".** Because the ledger has no
place for "built, live proof owed", the window writes it into the handoff pointer:
FOUNDRY_HANDOFF_202610070107: *"`CAULDRON_ENRICHMENT_VISUALS_1` and
`LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1` — built offline, pushed, claimed in the ledger, not
closed; NEXT: run each live … and close with the sha"*, and *"`UNFINISHED_LINE_WORLD_FOUNDRY_1`
— … committed and pushed at 420d184ee; never run in game; NEXT: run the world-foundry debug
actions live"*. All three are still `ready` in the ledger (the first two `needs: owner`,
UNFINISHED_LINE_WORLD_FOUNDRY_1 `needs: offline`), so the next window's live agent may pick
them up from the handoff while its offline agent is handed the same items by `next`.

**3.8 What stops double-work: very little.** (a) `rank()` filters by owner, so BENCH and
FOUNDRY never get each other's items. (b) A second `claim` within 30 minutes of the holding
claim is recorded as *contested* and the loser is warned (19 such in the ledger); a re-claim
after 30 minutes is treated as routine. (c) Nothing distinguishes subagents within one
window: `next` is deterministic, so two FOUNDRY subagents asking get the **same** top item,
and there is no lease, no "claimed by subagent X", no expiry. (d) Nothing checks git before
offering. SALVAGE_WRECKAGE_EVERYWHERE_1 was claimed twice 7 hours apart by FOUNDRY with four
build commits in between, and nothing reported it.

## 4. Existing lint/sweep tooling and why it missed this

| tool | what it does | why it did not catch built-but-open |
|---|---|---|
| `rimflow sweep --transient` | lists aging files in `Transient/` | the only sweep; never looks at items |
| `rimflow lint --citations` | flags docs that cite a closed item as live | the inverse problem (dead cited as live), not live-but-done |
| `queue_staleness_review.py` (Utils, read-only) | doing idle >7 d, blocked idle >3 d, `needs: bridge/game-up` whose window opened ≥2 times | idle time only. A just-built item (event yesterday) is "fresh". It explicitly skips `needs: offline` ("no satisfying event"). Not run by `next`, handoff, or any hook; referenced only from a dashboard tab. Today it reports 155 stale, which nobody acts on. |
| `live_proof_lint.py` + `warn_close_live_proof_owed.py` hook | at close time, warns if the commit body says "live proof owed" with no spawned successor (37 historical closes) | fires only on a **close**; the stuck items were never closed. It also *discourages* closing with debt, reinforcing §3.1. |
| `warn_unclosed_queue_item.py` hook | warns when a commit deletes a `## <ID>` heading from a queue markdown without `Closes:` | targets the pre-ledger markdown queues; views are now generated and gitignored |
| `queue_lint.py` hook | refuses hand-edits to ledger/views; warns on cross-seat prose edits | integrity, not liveness |
| "decay sweep" | a practice (any seat may close/drop dead items, owner ruling 2026-09-19; "stale default: one grep/probe") | **no tool by that name exists** in the repo; it depends on an agent choosing to look. Builders are told to "stale-drop" items that are *not* provably live, not to close items that are provably built. |
| `rimflow why <ID>` | explains why `next` is not offering an item | answers the opposite question |

Common gap: **no instrument joins the ledger with git.** Every check reads one or the
other, and the evidence that an item is built lives in git (commit subject naming the id,
`Closes:` trailer) and in free-text notes.

## 5. Candidate fixes (options with costs)

These are options, not decisions. Constraints the reviewer should respect: the ledger is
append-only and terminal states are final; the owner has twice forbidden a "completeness
gate" that refuses to start thin items (2026-08-21/22); hooks that *block* commits are
disliked, warnings are preferred; agents are the main users and follow whatever `next` says.

| # | option | what it fixes | cost / risk |
|---|---|---|---|
| A | **New state `built`** (or `awaiting-proof`) between `doing` and `done`, entered by `rimflow built <ID> --sha`; never offered to offline builders; shown in its own view section; offered to the bridge agent when the game is up | §3.1, 3.4, 3.5, 3.6 in one move; makes "honest open" distinguishable from "unbuilt" | schema + replay + views + selftests change; risk that `built` becomes the new graveyard unless something drains it (pair with D or F) |
| B | **Split `needs`, or auto-retag on build**: a `built` / note-with-sha event sets `needs` to `bridge`/`game-up` automatically | §3.2 without a new state | still overloads one field; items whose remaining work is art install or owner review need other targets |
| C | **Close on offline evidence, spawn the live proof**: make "close at sha + `spawn <ID>_LIVE_PROOF` for the bridge seat" the standard ending; one verb `close --live-owed` does both | uses existing verbs; the build item is honestly done, the debt is a separate, correctly-tagged item | doubles item count; owner's "done means proven" doctrine must be rewritten to "done means the offline scope is proven"; live-proof items pile up (37 historical debts already unspawned) |
| D | **Staleness/git probe before `next` offers**: before printing, search `git log` for commits naming the id (subject or `Closes:`) since its last ledger event; if found, print "already built at <sha> — close, mark built, or say why" instead of the spec | catches today's failure directly (186 of 272 would trip); cheap (one batched `git log`) | heuristic (a subject can name an item it only touched); `next` stops being a pure function of the ledger, which the design values; slow drvfs git (~2 s) |
| E | **Make `Closes:` real**: a post-commit / pre-push step (or `./publish`) that emits `close --sha` for every `Closes:` trailer, or `built` for a softer trailer like `Built: <ID>` | §3.3; the doctrine already tells agents to write the trailer | auto-closing on a trailer bypasses the evidence bar; trailers written mid-work would close early; needs to run as the right seat |
| F | **Split criteria into `## criteria-offline` and `## criteria-live`** (or tag each bullet); `close` allowed when offline criteria are met and live criteria become a spawned item or the `built` state | makes the definition of done match what an offline agent can do; 44 offline-tagged items have live-worded criteria | prose migration over ~244 files with criteria; agents must write two sections |
| G | **Lease on claim**: `claim` records claimant (window + subagent tag) and an expiry; `next` skips items leased by someone else and warns on re-claim | §3.8 double-work | ledger schema change; subagents have no stable identity today |
| H | **Stop claim → ready**: `claim` goes straight to `doing` (or `next` offers `proposed`+`ready` but `claim` hides it) | §3.4: claiming stops advertising the item | reverses the 2026-08-21 design in which `ready` = "claimed and offerable"; reclaim/reassign semantics shift |
| I | **Wire the existing staleness review into the handoff and `next --bench`**, and add a "built per git, still open" section to it | cheap, uses existing code | report-only; 155 stale items are already reported and ignored, so a report alone has a poor record here |
| J | **One-time cleanup**: close or mark built the ~115 offline ready/doing items named in a commit subject, after a per-item check | resets the board so `next` is trustworthy now | judgement-heavy; does not prevent recurrence |

Rough pairing that addresses all measured mechanisms: A (or C) + D + E-as-`built` + J.

## 6. Questions for the reviewer

1. Is a distinct "built, awaiting live proof" state (A) better than closing on offline
   evidence and spawning a proof item (C), given live verification is the scarce resource
   and a single bridge serializes it?
2. Should `next` stay a pure function of the ledger, with git evidence pushed *into* the
   ledger by a commit/publish step (E), or should `next` probe git directly (D)?
3. How should the definition of done be split so an offline agent can finish its part
   without lowering the bar (F), and who drains the live-proof backlog?
4. What is the minimal claim/lease design (G/H) that stops two subagents of one window, or
   one window across a reboot, from being handed the same already-built item?
5. Anything structurally missing: e.g. should `blocked` with `--on` auto-surface when the
   blocker closes, given 96 blocked items, many idle 19–27 days?
