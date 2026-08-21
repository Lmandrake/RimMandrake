# TRANSIENT — Upgrade plan: canon, ledger, and the board

**For secondary review. 2026-08-20. Nothing here is built; nothing here is decided.**
Supersedes nothing. Read with `TRANSIENT_RimFlow_Analysis.md` and `TRANSIENT_lorekeeping.md`.

**Scope, as ruled by the owner:** part A (canon + checker) · part B (item ledger) · the
visualizer. **No SQL, no SQLite, no ORM, no server framework.** JSONL and stdlib Python only.

---

## 0. Four decisions already taken

| decision | ruling |
|---|---|
| **Canon dumps** | The **full 578-mod list is canon.** ⭐ A differing mod count — greater *or* lesser — **does NOT invalidate the frozen dump.** Only the owner re-freezes. |
| **Priority** | Computed, deterministic: unblocked → this deployment → V1 row → oldest. No hand-ranking. |
| **Cutover** | The six `queue/*.md` files **stay**, regenerated as read-only views. Nothing looks different to the owner. |
| **Visualizer** | Extend `status_server.py` at `:8787`. Slow refresh, one process, one URL. |

## 0b. 🔴 New standing rule from the owner — the TRANSIENT prefix

> *"Ensure that all temporarily useful files or output has a filename prepended TRANSIENT so we
> never confuse this in the future as something to keep. This is how we ended up with too many
> markdown files."*

**Any file whose value ends when the current question is answered is named `TRANSIENT_<name>.md`.**

| TRANSIENT | not TRANSIENT |
|---|---|
| analyses, audits, comparisons, scratch reports | design docs, specs, doctrine |
| one-off census output, migration diffs | queue items, canon, the ledger |
| working sheets for a decision in flight | anything a future session must obey |

- **The test:** *would a reader six months from now be wrong to act on this?* If yes → `TRANSIENT_`.
- **Enforcement:** `queue_lint.py` warns on any new root-level `.md` that is neither `TRANSIENT_*`
  nor listed in `design/INDEX.md`.
- **Sweeping:** `rimflow sweep --transient` lists every `TRANSIENT_*` older than 14 days for deletion.
  It never deletes on its own.
- ⚠️ This applies to **this file too.** It is a review artifact. The permanent output of this work is
  `infrastructure/GAME_STATE_WORKFLOW.md` and the code — not this plan.

---

## 1. What is being built, in one paragraph each

**A — Canon.** One machine-readable file holds the ~40 numbers the lore repeats. A checker scans
every design doc and fails on a contradicting value. This exists because water is currently 8.1%
or 25% depending on the line, and the terminator is +14 °C or −37 °C depending on the file.

**B — The ledger.** An append-only `events.jsonl` becomes the truth for workflow state; each item
gets its own prose file; the six queue Markdown files become generated views. This exists because
the board currently reports 0 done against 28 real ones, and because a seat cannot hold its own
inbox in context.

**The board.** `status_server.py` grows the views that make the work graph visible — what is
moving, what is stuck, what caused what — colored by the *kind* of work.

**None of these three depends on the others.** Any one can ship alone.

---

## 2. Data model

Everything lives in git. Nothing is a binary. Nothing needs a daemon.

```
infrastructure/state/
  ledger/
    events.jsonl              ⭐ APPEND-ONLY. THE TRUTH. Nobody reads it by eye.
    events/2026-08.jsonl      monthly rolls once the live file passes ~5 MB
  items/
    <ID>.md                   prose only: spec / verify / criteria / notes
  dumps/
    REGISTRY.jsonl            which dumps exist, which are frozen
  canon.yml                   the numbers the lore must agree on
  queue/<SEAT>.md             GENERATED VIEW — "derived, do not edit"
  derived/board.json          GENERATED, gitignored, rebuilt on a timer
```

### 2.1 `events.jsonl`

One JSON object per line, `\n`-terminated, written `O_APPEND`.

```json
{"ts":"2026-08-20T18:01:12Z","seat":"CHECK","event":"verify","id":"C40","result":"fail","config":"full-578","evidence":"observed/logs/Player_2026-08-20.log","sha":"f0a9f6c","caused_by":null}
```

🔴 **THIS SAFETY ARGUMENT IS FALSE ON THE FILESYSTEM THIS REPO LIVES ON. Measured 2026-08-20.**

The argument was: on Linux a write to a file opened `O_APPEND` is atomic below `PIPE_BUF`
(4096 bytes), our events measure ~193, so four seats can append at once with no coordination.
That is true — **on a local filesystem.** ⛔ `/mnt/d` is a **9p / DrvFs** mount (WSL2 → a Windows
drive), and 9p does not serialise concurrent writes. 12 processes × 250 events of ~160 bytes,
run twice:

| filesystem | lines written | distinct events | torn lines |
|---|---|---|---|
| `/tmp` (tmpfs) | 3000 / 3000 | 3000 / 3000 | **0** |
| `/mnt/d` — **the repo** | 857 / 3000 | **502 / 3000** | **355** |
| `/mnt/d` — again | 657 / 3000 | **496 / 3000** | **161** |

**Five of every six events vanished**, in the one file that is supposed to be the truth. The
PIPE_BUF property was quoted from POSIX and never run here.

✅ **`model.append()` now takes an exclusive `flock`, and that fixes it completely** — 3000/3000,
zero torn, twice, at ~2 ms per event. Isolated further: **flock alone is sufficient** and
re-seeking under the lock changes nothing, so the defect is that 9p does not serialise the
*writes*, not that it mishandles the append offset.

⚠️ **`flock` is advisory**, so `model.append()` is the ONLY sanctioned writer. A shell `>>` still
tears lines. The PIPE_BUF ceiling is kept anyway: it bounds an event to one plausible write, keeps
prose out of the ledger, and restores the no-lock guarantee if this ever moves to ext4.

🔑 **The lesson is not about 9p.** `selftest_concurrency.py`'s first version used
`tempfile.mkdtemp()`, which is `/tmp`, and reported **3600/3600, zero torn** while the real
filesystem was losing 83% of writes. A green test measuring the wrong disk is worse than no test.
It now defaults to the directory the ledger actually lives in.

**Measured cost:** 193 B/event · ~1,100 events in the last 8 days · **~9 MB per year**.
Replaying a full year to current state: **53 ms**. Scanning for one seat: **6 ms**.

**Event vocabulary — 16 verbs, deliberately small.**

| verb | payload | who may emit |
|---|---|---|
| `file` | `for`, `title`, `kind`, `row`, `target`, `needs` | any seat |
| `claim` · `start` | — | owner seat |
| `block` · `unblock` | `reason`, `on` (item id, optional) | owner seat |
| `verify` | `result`, `config`, `evidence`, `sha` | owner seat |
| `finding` | `from` (run), `type`, `severity`, `name` | any seat |
| `spawn` | `from` (finding/item), `for`, `name` | any seat |
| `retarget` | `from`, `to`, `reason` | owner seat + DECIDE |
| `reassign` | `to`, `reason` | DECIDE only |
| `close` | `sha` | owner seat |
| `drop` · `supersede` | `reason` / `by` | owner seat |
| `note` | `text` | any seat |
| `seat` | `state` (ready/busy/idle), `reason`, `item` | self only |
| `bridge` | `state` (taken/released) | **CHECK only** |
| `game` | `state` | **owner only** |
| `admin` | `reason`, `patch` | **owner only** |

`caused_by` is the entire causal graph — run → finding → spawn → close.

🔴 **It carries a NAME, not an index. Corrected 2026-08-20 while building it.** The spec said
"the index of the event", which fails twice over: computing an index means counting the whole file
on every append (O(n²), and under 12 concurrent writers on 9p the re-read itself failed with
ENODATA), and — the one that matters — **line indices do not survive the monthly roll.** Past
~5 MB `events.jsonl` rolls into `events/2026-08.jsonl`, every index restarts at zero, and every
stored `caused_by` silently points at a different event. A causal graph that quietly relabels
itself is worse than none.

So `caused_by` names an item id, a finding name, or a run like `C40/run-3@full-578` — all already
unique, all already what §4's commands pass (`--from C40/run-3@full-578`), all roll-proof.

### 2.2 `items/<ID>.md` — prose only

🔑 **No front-matter, no `state:`, no metadata, no title.** The filename is the ID; the title and
every scalar live in the ledger. **A field cannot drift if it exists in exactly one place.**

```markdown
## spec
<what to build, in as many words as it takes>

## verify
<the command whose output settles it — written by someone other than the builder>

## criteria
<what a human would look at to agree it is done>

## notes
<argument, owner rulings quoted verbatim, warnings, reversals>
```

The owning seat edits this freely. Prose is never migrated into fields — that was the mistake the
original RimFlow spec made.

### 2.3 `canon.yml` — part A

```yaml
version: 1
as_of: 2026-08-20
planet:
  water_pct:        8.1
  tiles:            21872
  lapse_c_per_km:   5.5
  temp_curve_c:     {0: 70, 30: 58, 60: 38, 90: 14, 120: -22, 150: -58, 180: -80}
  habitable_ring:   [40, 57]      # arc degrees
factions:  {count: 13, cut: [UnboundHive]}
settlements: {total: 72}
modlist:
  official_count: 578
  as_of: 2026-08-20
  note: >
    A differing live count does NOT invalidate the frozen dump, greater or lesser.
    Only the owner re-freezes.
```

**`check_canon.py`** scans all 119 design docs and fails with `file:line` on a contradicting value.

⚠️ **The honest engineering cost:** each fact needs a match pattern, and prose that *documents* the
old number must not trip it. Exemption rule — a number is ignored if its line contains any of
`~~` · `superseded` · `was` · `formerly` · `dead` · `⛔`, or sits inside a blockquote. That is
pragmatic, not perfect; expect to tune it over the first week.

### 2.4 `dumps/REGISTRY.jsonl` — the frozen official dump

```json
{"id":"OFFICIAL-2026-08-21","kind":"official","frozen":true,"modlist_count":578,
 "modlist_sha":"…","path":"observed/inventory/DefDump_OFFICIAL/","by":"owner",
 "note":"the design target — build to this"}
{"id":"verify-2026-08-20","kind":"verification","frozen":false,"modlist_count":13,"path":"…"}
```

**Rules, straight from the owner's ruling:**

1. **`official` is the design target.** DECIDE and BUILD author against it.
2. 🔴 **A mod-count mismatch — greater or lesser — is NOT staleness.** Our own small custom mods
   will change the count constantly and must not force a re-freeze.
3. **Only the owner re-freezes**, deliberately, by running one command.
4. **`verification` dumps answer "does the live game match?"** — never "what should I design against?"
5. ⚠️ **This is a behaviour change to `refresh.py`.** Its entire job today is flagging artifacts
   stale when the mod list changes. It must learn to treat `frozen: true` as immune and say
   `FROZEN (by owner, 2026-08-21)` instead of `STALE`. The `frozen-artifacts` skill covers the pattern.

---

## 3. One master queue, and how "what's next" is decided

**Yes — one master queue.** There are no per-seat queues; `owner` is a field on an item. The six
`queue/<SEAT>.md` files become filtered views of the one ledger. This kills the class of bug where
`B53` sits in two queues with two different states, which is true today.

### The priority engine

```
rimflow next --seat BUILD

  filter  owner   == BUILD
  filter  state   == ready
  filter  blocked == false
  filter  target  == <active version, normally v1>
  filter  needs   is satisfiable in the CURRENT GAME STATE
  sort    1. needed_this_deployment   desc
          2. v1_row                   asc
          3. created_at               asc
  → one item, ~400 tokens
```

**`needs` is the coupling between the game and the queue** — this is the mechanism that makes the
whole game-state workflow work:

| `needs:` | satisfiable when |
|---|---|
| `offline` | always |
| `deploy` | game state is `DEPLOYING` |
| `game-up` | game state is `UP` |
| `bridge` | game state is `UP` **and** CHECK holds the bridge |
| `harvest` | a load has ended and its dumps/logs are not yet superseded |
| `owner` | owner is present (`MODE` is not `afk`) |

An item whose `needs` cannot be met **is not blocked** — it is simply not offered. That distinction
matters: `blocked` means something is wrong; `needs` means the window is closed. Today both are
written into the same prose field and the board can read neither.

---

## 4. Discovery — the R&D path, which is the point

**The requirement:** CHECK is testing, and uncovers a new build need, a new design question, or a
follow-up check it can still run *in this same deployment*. That must be cheap to record and must
not corrupt the record of what already happened.

```
CHECK finds a live failure:

  rimflow verify C40 --result fail --config full-578 --evidence observed/logs/Player_x.log
      → C40/run-3@full-578 recorded. C40 is NOT reopened. The failure stands forever.

  rimflow finding --from C40/run-3@full-578 --type integration --severity high \
                  --name BLACKSTAR_SPAWNS_VESSELLESS_1
      → BLACKSTAR_SPAWNS_VESSELLESS_1

  rimflow spawn --from BLACKSTAR_SPAWNS_VESSELLESS_1 --for BUILD --needs offline \
                --name BLACKSTAR_VESSEL_DEF_1 --spec items/draft.md
      → BLACKSTAR_VESSEL_DEF_1, owned by BUILD, state proposed
```

**Three shapes of follow-on, and each has a flag:**

| what CHECK found | command | effect |
|---|---|---|
| "one more check clarifies this, and I can do it now" | `spawn --for CHECK --needs bridge --this-deployment` | jumps to the top of CHECK's own `next`, gets done before the window closes |
| "BUILD must change something" | `spawn --for BUILD --needs offline` | lands in BUILD's queue, workable while the game is still up |
| "the design is wrong" | `spawn --for DECIDE --kind decision` | DECIDE picks it up; the spec defect is a new item, never a reopening |

🔑 **`--this-deployment` is the flag that makes live windows productive.** It is cleared
automatically when the game goes down, so it cannot leak into the next session as false urgency.

**Filing for another seat is normal and encouraged. Changing another seat's item is refused.**
That is the whole cross-posting rule, and it is enforced at the tool and again at the hook.

**The completeness gate replaces the manual refusal contract.** `POLICY.md` says BUILD must refuse
an item with an empty `spec:` or `verify:`. Under the ledger, an item filed **without** all three of
spec/verify/criteria simply **cannot enter `ready`** — it lands `proposed` and the tool names the
missing section. The refusal becomes a precondition instead of a bounce, and the four-day
invisibility failure becomes impossible.

---

## 5. The `rimflow` CLI — stdlib only, one file per concern

```
rimflow next   --seat BUILD              the only command a seat needs to start work
rimflow show   <ID>                      title, scalars, prose, history, causal chain
rimflow why    <ID>                      why is this blocked / not done / in v2
rimflow file   --for <SEAT> …            create work (any seat)
rimflow claim | start | close <ID>       lifecycle (owner seat only)
rimflow block  <ID> --reason "…"         with an optional --on <ID>
rimflow verify <ID> --result … --evidence …    records a RUN. Immutable.
rimflow finding --from <ITEM>/run-N --name THREE_WORD_# …   records a finding
rimflow spawn  --from <NAME> --for <SEAT> --name THREE_WORD_# [--this-deployment]
rimflow retarget <ID> v2 --reason "…"    planning move; lifecycle untouched
rimflow seat   ready | busy | idle --reason …
rimflow bridge take | release            CHECK only
rimflow game   <state>                   OWNER only
rimflow render                           regenerate queue/*.md + derived/board.json
rimflow reindex                          rebuild all derived state from the ledger
rimflow sweep  --transient               list stale TRANSIENT_* files (never deletes)
rimflow admin  <ID> --reason "…"         OWNER only, audited correction
```

**Refused by the tool, not by prompt discipline:** `close → ready` · `close → block` ·
`drop → ready` · editing a completed `verify` · touching an item you do not own ·
any seat but CHECK taking the bridge · any seat but the owner setting game state.

---

## 6. The agents, rewritten

### 6.1 The universal contract — identical in all four seat files

**Start of turn — three reads, in this order, and no others:**

```
1. rimflow game                → what state is the game in?
2. rimflow seat ready|busy     → announce yourself
3. rimflow next --seat <ME>    → your one item
```

⛔ **You do not open `queue/*.md`.** They are rendered for the owner, not for you. Reading one is
32,000 tokens to answer a question a command answers in 400.

**End of item — always:**

```
rimflow close <ID> --sha <commit>      or    rimflow block <ID> --reason "…"
git commit <explicit paths>  with  Closes: <ID>
git push
```

**Stop conditions — an agent keeps working until exactly one of these is true:**

| condition | what to do |
|---|---|
| **No ready work** | `rimflow seat idle --reason no-ready-work` |
| **Needs the owner, owner present** | `rimflow file --for OWNER --kind decision`, then keep working on something else; go idle only if that was the last item |
| **Needs the owner, owner AFK** | file the question, **do not idle** — carry on with anything else |
| **Context ≥ 90%** | 🔴 see below |
| **Waiting on a game state** | `rimflow seat idle --reason awaiting-game-state` |

### 6.2 The 90% context ritual — new, and load-bearing

At **90% of the context window**, an agent stops taking new work and performs, in order:

1. **Write down what it learned** where the next session will find it — `BUILDABLE.md` for a stack
   limit, `observed/LIVE.md` for a live fact, the relevant **skill** for a durable technique.
2. **Close or block** the item in hand. Never leave it `doing`.
3. **Commit and push.** Uncommitted work at 90% context is work about to be lost.
4. `rimflow seat idle --reason context-exhausted --note "<one line: where I stopped>"`

🔑 **The note is the handoff.** A fresh seat reads it from `rimflow next` and resumes without
re-deriving anything.

### 6.3 AFK

`infrastructure/state/MODE` gains a third value: `interactive` · `autonomous` · `afk`.

- **`afk`** — owner questions accumulate as `kind: decision` items owned by OWNER. **No agent idles
  waiting for the owner.** The board shows the queue depth so the owner sees the backlog on return.
- The owner clears it by setting `MODE` back and working `rimflow next --seat OWNER`.

### 6.4 Per seat — what changes

| seat | keeps | gains | loses |
|---|---|---|---|
| **DECIDE** | scope, specs, `V1.md`, acceptance criteria | owns **`canon.yml`** · the only seat that may `reassign` · answers `kind: decision` items | hand-editing queue files |
| **BUILD** | `src/`, offline proof, deploy | `rimflow verify` for every offline check — **the pasted output becomes a record, not a paragraph** | writing state into prose |
| **CHECK** | live game, the bridge, `observed/` | `bridge take/release` as ledger events · `--this-deployment` spawning | "sending items back to BUILD" — it files new ones instead |
| **REP** | board, `HUMAN.md`, `MODE` | the board reads the ledger, so REP stops reconstructing state from prose | maintaining a hand-kept status |

**Unchanged and deliberately so:** the four seats, the one-way routing, the no-peer-messaging
ruling, `Closes:` trailers, commit-and-push discipline, `git add -A` refusal.

### 6.5 What every seat file must now say, verbatim

> Work moves forward by adding evidence and creating linked descendants. A later failure never
> reopens earlier work. Record the failing run, file a finding, spawn the corrective item.
> A passing run afterwards is a **new run**, not an edit of the failed one.

> You may file work FOR any seat. You may change only work you OWN.

> Version allocation (v1 → v2 → vN-storage) is not a lifecycle move and never erases done-ness.

---

## 7. Game state workflow

**Specified in full in `infrastructure/GAME_STATE_WORKFLOW.md`** — a permanent doctrine file, not a
TRANSIENT one, because agents must obey it every session.

Summary of the machine:

```
DOWN ──(owner: "game load announced")──▶ DEPLOYING
   ▲                                          │ BUILD deploys content
   │                                          │ CHECK deploys bridge
   │                                          │ modlist checked
   │                                          │ both seats: rimflow seat ready
   │                                          ▼
   │                                      LOADING ──▶ UP ──▶ GOING_DOWN ──▶ DOWN
   └──────────────────────────────────────────────────────────────────────────┘
```

**The owner announces every state change.** CHECK announces only *bridge* possession and
*ready-to-close*. That split is deliberate: state is the owner's; the bridge is CHECK's.

---

## 8. Enforcement — the hooks

The project has already proved that a `PreToolUse` hook changes behaviour where prose does not.

| hook | fires on | action |
|---|---|---|
| **`queue_lint.py`** (new) | `Bash`, any `git commit` | 🔴 **BLOCKS**: hand-edit of `items/`-derived views · cross-seat write · backward transition · a new root `.md` not named `TRANSIENT_*` |
| **`warn_unclosed_queue_item.py`** (fix) | `git commit` | ✅ regex fixed. 🔴 **"make it block" is REFUSED and the plan is corrected, not obeyed** — the owner ruled 2026-08-15 that it warns and never gates: *"a hook that refuses a commit costs more than the miscount it prevents, and a seat that hits it mid-flow will work around it."* Unreversed, so it exits 1: red and visible, never a gate. It also now exempts a GENERATED view, where a heading leaving loses nothing |
| **`doc_budget.py`** (wire up) | `git commit` | 🔴 **RED ERROR on an over-budget file**, naming the file and the overrun. Exists and exits 1 today; nothing runs it |
| **`doc_roster.py`** (wire up) | `git commit` touching `design/` | ⚠️ **WARNS, does not regenerate.** A `PreToolUse` hook that writes changes the tree under a commit whose pathspec is already fixed, so the regenerated index would NOT be in the commit — leaving the repo dirty and the author believing it was handled. It names the command instead |
| **`check_canon.py`** (new) | `git commit` touching `design/` | 🔴 **BLOCKS** a number that contradicts `canon.yml` |
| **`block_blanket_git_stage.py`** | unchanged | keep |
| **`block_peer_messages.py`** | unchanged | keep |

⚠️ **Every hook in this repo runs `python3 … 2>/dev/null || true` — fail-open.** A hook that
silently stops running is worse than no hook. So: **stdlib only, no third-party imports in any
hook**, and `selftest_<hook>.py` beside each one, following the existing
`selftest_block_blanket_git_stage.py` pattern.

---

## 9. The visualizer

Extends `status_server.py` (390 lines, stdlib, `:8787`). A timer regenerates
`derived/board.json` every **60 s**; the page polls that file. No new process, no new port.

### 9.1 Views

1. **Deck** — the four seat lanes (ready / doing / blocked / idle-with-reason), game state, bridge
   holder, owner-question depth. The one screen that answers "what is happening".
2. **Flow** — the causal graph: `item → run → finding → spawn → item`. Progressive disclosure from
   one selected item. Never the whole graph at once.
3. **V&V matrix** — items × configurations (`minimal-13`, `full-578`, `bridge`, `offline`), each
   cell the **latest** run with drill-down to every historical run.
4. **Timeline** — the ledger, filtered. "What changed since I was last here."
5. **Item inspector** — prose, scalars, history, and the four *why* answers: why blocked, why v2,
   why not done, what caused this.

### 9.2 Palette — validated, not chosen by eye

Dark surface `#1a1a19`. These are the **reference categorical steps for dark mode**, and I ran the
validator rather than picking hues:

| slot | work type | hex | glyph |
|---|---|---|---|
| 1 | **Testing / V&V** | `#3987e5` | ◈ |
| 2 | **World authoring** | `#d95926` | ⬡ |
| 3 | **Config / XML patch** | `#199e70` | ⟨⟩ |
| 4 | **Document design** | `#c98500` | ▤ |
| 5 | **Art / asset generation** | `#d55181` | ✦ |
| 6 | **Source code** | `#008300` | ⌘ |
| 7 | **Infrastructure / process** | `#9085e9` | ⚙ |
| 8 | **Repair / known bug** | `#e66767` | ⤬ |

**Validator output, dark, adjacent pairs — ALL PASS:**
lightness band ✅ · chroma floor ✅ · CVD separation worst ΔE **8.4** (protan) ✅ ·
normal-vision floor worst ΔE **19.3** ✅ · contrast ≥ 3:1 on all eight ✅

🔴 **And the constraint that follows.** Under **all-pairs** — which is what the Flow graph is, since
any two work types can end up adjacent — it **FAILS**: `#d55181 ↔ #199e70` is ΔE **1.6** for
deuteranopia, and `#e66767 ↔ #d95926` is ΔE **7.1** even with normal vision.

⇒ **Every mark carries its glyph and its label. Color is never the only encoding.** On lanes and
stacked bars (fixed order, adjacent pairs) color alone is legal; on the Flow graph it is not.
This is a measured requirement, not a preference.

**Status is a separate channel and never a categorical hue** — `blocked` is a ring plus ⚠,
`doing` is full opacity, `done` is dimmed to 45%, `idle` is a dashed outline.

### 9.3 Look

Dark graphite base, thin luminous 1px borders, restrained cyan for neutral-active and amber for
attention. Crisp typography over chrome; high density, low motion. **No animated starfields, no
glow that costs legibility, no motion on a page that is left open all day.** The target is a
spacecraft engineering console, not a novelty dashboard.

### 9.4 Load

🔴 **The 53 ms was measured on the wrong filesystem, and the 100 ms target is UNREACHABLE here
by any caching strategy. Measured 2026-08-20 — and the conclusion is still that the load is fine.**

`rimflow render` is **374 ms** against the real ledger (352 events, 144 items) on `/mnt/d`, which
is a **9p / DrvFs** mount. The cost is not the code:

| on the repo's 9p mount, 144 item files | |
|---|---|
| `stat` all of them | **130 ms** |
| `open` + read all of them | **209 ms** |
| the same loop on tmpfs | **0.8 ms** |

⛔ **So a freshness-checking cache cannot help.** Any cache that verifies its entries are current
must `stat` them, and `stat` alone is 130 ms — already over the 100 ms target before a single line
of parsing. A per-process cache IS in `model._sections` and takes a warm replay to ~1 ms, which is
what matters for a long-lived board; a *cold* render cannot get under the filesystem.

✅ **And the target was never the real constraint — the LOAD argument was, and it still holds:**

| | duty cycle at the specified 60 s cadence |
|---|---|
| the plan's 53 ms | 0.088% of one core |
| the measured 374 ms | **0.623% of one core** |

*"Slow cadence, nothing that stresses the system"* is satisfied with room to spare at seven times
the assumed cost. ⇒ **The 100 ms figure is retired rather than chased.** Building a cache that
cannot reach it, to buy half a percent of one core, would trade a real cache-invalidation bug for
nothing.

---

## 10. Migration — designed around the fact that we are mid-build

🔑 **Every stage is additive. Nothing is deleted. Nothing stops working. Any stage can be the last.**

| step | what happens | risk |
|---|---|---|
| **M1** | Import the 167 items from the six queue files into `items/<ID>.md` + `file` events. Every imported event carries `imported: true` and `confidence: high\|low`. | none — pure addition |
| **M2** | Replay git: the **123 `Closes:` IDs** become real `close` events with their true sha and date. This history is recoverable and worth recovering. | none |
| **M3** | Generate `queue/<SEAT>.md` from the ledger into `queue/*.generated.md`. **Diff against the live file.** That diff is the acceptance test — a human reads it. | none |
| **M4** | When the diff is clean, the generated file replaces the live one and the hook starts refusing hand-edits. | ⭐ the cutover |
| **M5** | The originals move to `queue/archive/` — **only when the owner says so.** | none |

**Ambiguity is preserved, not invented.** An item whose `state:` prose cannot be parsed to one of
the five values imports as `confidence: low` with the original string in `notes`, and appears on the
board in a **needs-triage** lane. We currently have **68 of 167** in that category — they get
looked at, not guessed at.

**The known messes M1 must handle explicitly:** `B53` in two files with different bodies · 21
`HUMAN.md` items with no fields at all · three ID schemes (107 legacy / 44 kebab-hash / 42 new) ·
2 genuinely lost items · the `5e12b7` hash collision.

⛔ **No fourth ID scheme.** Existing IDs keep their names forever; `aliases.json` maps retired names
so `git log -S` and old commit trailers keep resolving.

---

## 11. Stages and effort

Each stage ends at a point where stopping is reasonable.

| # | stage | days | stop here and you still have |
|---|---|---|---|
| **S0** | Fix `derive_matrix.py:277` (`state.split()[0]`), fix the hook regex, run `doc_roster.py --write`, wire `doc_budget` to red-error | **0.5** | a board that tells the truth: ≥28 done, 2 blocked, instead of 0 and 0 |
| **S1** | `canon.yml` + `check_canon.py` + fix the 21 contradictions | **1.5** | the lore can no longer disagree with itself |
| **S2** | `status:` headers on all 119 design docs + link checker | **1** | dead docs stop being cited as live |
| **S3** | `items/` split + M1–M3 import + generated views | **1.5** | the context tax gone; cross-filing impossible |
| **S4** | `events.jsonl` + `rimflow` CLI + priority engine | **2** | ⭐ the whole workflow spine |
| **S5** | Game state machine + `GAME_STATE_WORKFLOW.md` + all hooks + agent rewrite | **1.5** | deterministic deployments |
| **S6** | Visualizer | **2** | the picture |
| | **total** | **~10 days** | |

**If the world freeze is close: do S0 and S1 and stop.** Two days, and they catch the class of
defect that would otherwise bake 25% water or a −37 °C terminator into the one world you build.

---

## 12. Files touched

**New:** `infrastructure/GAME_STATE_WORKFLOW.md` · `infrastructure/state/canon.yml` ·
`infrastructure/state/ledger/events.jsonl` · `infrastructure/state/items/*.md` ·
`infrastructure/state/dumps/REGISTRY.jsonl` · `src/RimMandrake/Utils/rimflow/*.py` ·
`src/RimMandrake/Utils/check_canon.py` · `.claude/hooks/queue_lint.py` + its selftest

**Modified:** `derive_matrix.py` (classifier fix; reads the ledger) · `status_server.py` (+5 views) ·
`status_board.html` (palette, glyphs, dark theme) · `refresh.py` (**frozen dumps are immune to
modlist drift**) · `doc_budget.py` (+`design/` class, red output) · `doc_roster.py` (+status column) ·
`warn_unclosed_queue_item.py` (regex + block) · `.claude/settings.json` (hook registrations) ·
`CLAUDE.md` (TRANSIENT rule, ledger pointer) · `infrastructure/agents/{POLICY,BUILD,CHECK,DECIDE,REP}.md`

**Generated, gitignored:** `infrastructure/state/derived/board.json`

---

## 13. Where I changed the owner's plan, and why

| his plan | my change | why |
|---|---|---|
| "smart add to the queue" | Split into **`file`** (new work) and **`spawn --from`** (work caused by a finding) | Only `spawn` carries causality. Without the distinction, "why does this item exist" is unanswerable — and that question is most of what R&D needs |
| One master queue | Agreed, **and `owner` is just a field** | The six views cost nothing and the owner keeps reading what he reads today |
| Agents go idle when blocked on the owner | **Only when the owner is present.** AFK → file the question and keep going | Otherwise a single unanswered question idles the fleet |
| Colors per work type | **7 → 8 categories**, adding **world authoring** | Painting the planet is none of art/doc/code/config/test/infra/repair, and it is a large share of current work |
| "sci-fi and beautiful" | Kept — plus **every mark carries a glyph** | Measured: the palette fails all-pairs CVD at ΔE 1.6. Color alone would make the Flow graph unreadable for a deuteranopic viewer |
| Dumps frozen | **`refresh.py` must be taught that frozen ≠ stale** | Its whole current purpose is flagging drift; without this change it will nag about the official dump forever |
| Budget overruns → red | Agreed, **plus a `design/` budget class that did not exist** | `doc_budget.py:41` deliberately exempts design. That was right when design was small; at 46,488 lines — 55% of every markdown line in the repo — a generous class beats no class |

---

## 14. Open questions for the owner

1. **Who breaks a tie between two `--this-deployment` items when the window is closing?**
   My default: the priority engine, unchanged — oldest first. Alternative: CHECK picks. Worth a ruling.
2. **Should `V1.md` rows become items themselves?** Today `row:` is an unenforced foreign key and
   **20 of 32 referenced values do not exist in `V1.md`.** Making rows first-class items would fix
   that; it also expands scope.
3. **When the owner re-freezes the official dump, what happens to design that cited the old one?**
   My default: nothing automatic — `check_canon.py` reports the deltas and a human decides.
4. **Do you want `TRANSIENT_*` files gitignored, or committed and swept?** I have specced
   **committed and swept**, because losing an analysis to a reboot is the failure the commit-and-push
   rule exists to prevent. Say the word and it flips.

---

## 15. The honest risks

- **~10 days is ~10 days**, and the world freeze is ahead. S0+S1 is two days and carries a large
  share of the value; everything after S3 is a bet on remaining runway.
- **A generated file someone hand-edits is worse than a hand-kept one.** The hook must refuse those
  edits at the same commit as the first generated view — not "later".
- **`check_canon.py` will produce false positives in week one.** Budget an afternoon of tuning, and
  give it an inline `<!-- canon-ok: reason -->` escape so nobody disables the whole checker to land a commit.
- **The migration must not invent certainty.** 68 of 167 items have unparseable state. They import
  as `confidence: low` and land in a triage lane. Any import that silently guesses is worse than no import.
- **I am the BUILD seat specifying the system that grades BUILD.** Worth naming. Every acceptance
  test in S0–S1 is deliberately a number someone else can independently check.

---
---

# PART TWO — second review, 2026-08-20

Six rulings from the owner, then the planet harness, then the named backlog.

## 16. Rulings

### 16.1 🔴 BUILD is master of "this deployment" — he wins ties

**A deployment is a first-class object owned by BUILD.** When two `--this-deployment` items compete
for a closing window, **BUILD's ordering wins.** CHECK owns the *bridge*; BUILD owns the *deployment*.

```
rimflow deployment open   --name <THREE_WORD_#>     BUILD only
rimflow deployment add    <ITEM>                    any seat may request; BUILD confirms
rimflow deployment order  <ITEM> --before <ITEM>    BUILD only — this is the tie-break
rimflow deployment close                            on entering DOWN; clears --this-deployment
```

The priority engine gains one term above all others:

```
sort  0. deployment_rank        (BUILD's explicit order, when set)
      1. needed_this_deployment  desc
      2. v1_row / parent milestone priority
      3. created_at              asc
```

⭐ **Rank 0 is the only hand-set field in the whole engine, it is BUILD's alone, and it applies only
inside an open deployment.** Everything else stays computed.

### 16.2 🔴 Citations are BY NAME, and a new artifact triggers a dangling-reference sweep

> *"Citations should be by name, so nothing breaks with an index. But there could easily be a pass
> of running validators that depend on the dump that changed to ensure nothing has been left
> dangling. This should be codified in deterministic code that accepts a new game artifact asset."*

**Rule: nothing ever cites a dump by index, offset, row number or ordinal. Only by `defName`.**
A design doc says `OuterRim_GalacticEmpire`, never "row 412 of the dump".

**New tool — `rimflow artifact accept`.** One deterministic entry point for every new game artifact
(a dump, a log, a save, a modlist snapshot):

```
rimflow artifact accept <path> --kind dump|log|save|modlist [--official]

  1. register        append to dumps/REGISTRY.jsonl with sha, count, date, frozen flag
  2. re-run          EVERY validator that depends on this artifact kind:
                       check_refs.py · check_declarations.py · validate_patch.py --defs
                       validate_ideoligion.py · xenotype_check.py · check_canon.py
  3. resolve         every defName cited anywhere in design/ and src/ against the new artifact
  4. report          TRANSIENT_artifact_accept_<id>.md — three lists:
                       ✅ still resolves        (no action)
                       🔴 now dangling         (cited by name, absent from the artifact)
                       🆕 newly available      (present, cited by nothing)
  5. file            one item per dangling citation, named for what broke
  6. NEVER auto-fix  a dangling reference is a decision, not a repair
```

🔑 **This is the piece that makes re-freezing safe.** Answering the earlier open question directly:
when the owner re-freezes the official dump, nothing happens automatically — the sweep reports the
deltas by name and a human decides.

⚠️ And the frozen-dump rule stands above all of it: **a differing mod count, greater or lesser, is
never staleness.** The sweep reports; it never invalidates.

### 16.3 🔴 TRANSIENT files are COMMITTED

> *"Committed for certain, we can choose to eliminate them later optionally, but they are deeply
> valuable until then."*

Refining §0b with the owner's own driver:

| a `TRANSIENT_` file **is** | a `TRANSIENT_` file is **not** |
|---|---|
| a temporary analysis | ⛔ **anything the game routinely makes** — dumps, logs, renders, saves |
| a transition or migration plan | ⛔ a derived artifact a script regenerates |
| a comparison written to settle one decision | ⛔ doctrine, specs, canon, items, the ledger |

🔑 **The source driver, in the owner's words: they become stale rapidly.** That is what the prefix
marks — not "unimportant", but **"had a shelf life, and it has probably expired."**

- **Committed and pushed**, always. Losing an analysis to a reboot is the exact failure the
  commit-and-push rule exists to prevent. Never gitignored.
- `rimflow sweep --transient` **lists** candidates older than 14 days. **It never deletes.**
- Routine machine output is not TRANSIENT — it is derived, and `.gitignore` already governs it.

### 16.4 🔴 V1 rows become first-class milestone items

`row:` is an unenforced foreign key today: `V1.md` defines rows 0–13, and queue items reference
**32 distinct values of which 20 do not exist** (`world-7`, `inhabited-3`, `bridge-6`, `doctrine`,
`dead`, `tooling`, `repo`, `v2`, `unassigned`). The board renders **56 rows for 14 real steps.**

```
items/FACTION_ROSTER_COMPLETE_9.md        kind: milestone
  ↑ parent
items/ROLE_KINDS_UNARMED_1.md             kind: build
items/BLACKSTAR_VESSEL_DEF_1.md           kind: build

rimflow why FACTION_ROSTER_COMPLETE_9
  → 11 done · 4 ready · 2 blocked (on OWNER_DECISION_VESSEL_ART_1) · 0 doing
```

- **Every V1 row becomes a `kind: milestone` item with a real name**, not a number.
- Items declare `parent:` instead of `row:`. `queue_lint` refuses a parent that is not a milestone.
- The 20 invented buckets are triaged: promote to a milestone, remap to an existing one, or mark
  `parent: none` deliberately.
- ⛔ **`V1.md` stays** — as a generated burn-down view rendered from milestone rollups, so the owner
  keeps the file he reads.

### 16.5 `Alien_Bestiary.md` — `status: aspirational`

78 named creatures, **0 on disk**, never named by a queue item or a commit. It stays in `design/`
and gains a header:

```html
<!-- status: aspirational ; 2026-08-20 ; 0 of 78 named creatures exist on disk -->
```

`check_canon.py` treats an `aspirational` doc as **non-binding**: its numbers never contradict canon,
and nothing may cite it as evidence that a thing exists. It remains readable, quotable as intent,
and honest about what it is.

### 16.6 🔴 My own naming mistake, corrected

The first draft of this plan used `RUN-0093` and `FND-0041` — precisely the opaque nonsense the
owner's 2026-08-20 naming ruling forbids. Corrected throughout:

| thing | naming | example |
|---|---|---|
| **Item** | `THREE_DESCRIPTIVE_WORDS_#` | `BLACKSTAR_VESSEL_DEF_1` |
| **Milestone** | same, numbered by V1 row | `FACTION_ROSTER_COMPLETE_9` |
| **Finding** | same — a finding **is** an item | `BLACKSTAR_SPAWNS_VESSELLESS_1` |
| **Run** | scoped to its item, never standalone | `C40/run-3@full-578` |
| **Deployment** | same | `INHABITED_FIRST_LIGHT_1` |

🔑 **A run is the only thing carrying a number, and it is never seen alone** — it always reads as
`<ITEM>/run-N@<config>`, which explains itself. `queue_lint` refuses any new name matching
`^[A-Z]\d+$` or `^[A-Z]-[A-Z0-9]+$`.

---

## 17. ⭐ THE PLANET HARNESS — reference-driven

> *"I'm having a lot of trouble making this planet surface. Seemed so easy, but it isn't."*

**The acceptance criteria already exist and are already good. They are simply not executable.**
`the_one_map.md` §"What realistic means here" lists seven binding reference images and **five named
defects**. Today a human has to hold both in their head while squinting at a render.

### 17.1 What exists right now

| | |
|---|---|
| references | **7 binding images**, all present in `research/Jawa/` |
| renders of the current map | **equirect only** — `world/view/ASHKARR_WORLDMAP.biome.equirect.png` |
| 🔴 **the gap** | **there is no orthographic render of the current map at all** — and the primary reference, `planet_map_tidal_lock_inspiration.webp`, is a **globe** |
| capability | `worldview.py` already supports `--projection ortho --center lat,lon`. Nothing has used it on Ash'karr |

**So the single most binding comparison in the project has never been made.** That alone may be a
large part of why this is hard.

### 17.2 `refmatch.py` — the tool

```
python3 src/RimMandrake/Utils/refmatch.py world/ASHKARR_WORLDMAP
```

**Step 1 — render to match, in the reference's own projection and scale:**

| reference | our render |
|---|---|
| `planet_map_tidal_lock_inspiration.webp` ⭐ THE TARGET | ortho globe, `--center 0,0` (day face) |
| `planet_inspiration_tidal_lock2.webp` | ortho, `--center 0,90` (terminator) and `0,180` (night cap) |
| `desert_map_inspiration2.jpg` ⭐ THE RIVERS | crop on the Scald trunk, arc 51→11 |
| `desert_tilemap_inspiration4.jpg` ⭐ THE DELTAS | crop on The Salt Gate |
| `desert_tilemap_inspiration3.jpg` (emptiness) | crop on The Dune Sea |
| `desert_zoomin_inspiration.jpg` (playas) | crop on The Salt |
| `desert_tilemap_inspiration2.jpg` (canyons) | crop on The Ashteeth |

**Step 2 — screen the five named defects.** These are the owner's own words, made computable:

| # | defect | test | flag when |
|---|---|---|---|
| 1 | ⛔ **circular seas** | circularity `4πA/P²` per water body | > 0.75 (a disc is 1.0) |
| 2 | ⛔ **comb rivers** | histogram of tributary junction angles | the 80–100° bin is over-represented; real drainage branches **acute** |
| 3 | ⛔ **rectangular roads** | run-length of constant bearing; closed loops | any straight run > N tiles, or a closed rectangle |
| 4 | ⛔ **concentric biome rings** | bearing-variance of each biome at fixed arc | variance too low ⇒ a bullseye ⇒ every direction out of the hot pole looks alike |
| 5 | ⛔ **inherited names** | every region/feature name ∩ the vanilla source tile CSV | any hit |

**Step 3 — one contact sheet**, `TRANSIENT_refmatch_<date>.html`: reference left, ours right, same
size, same projection, defect flags beneath each pair.

### 17.3 The doctrine this must not violate

🔑 **`the_one_map.md` is explicit: "The loop is LOOK, not measure"** — the old pipeline's numbers all
passed while the picture showed compass circles and comb rivers.

⇒ **The picture is the acceptance test; the five defect checks are a screen, never a verdict.**
The report leads with the images and puts numbers underneath. A green defect screen on an ugly map
means **the screen is wrong**, and that is the documented failure mode.

### 17.4 What I would do first, before writing any code

**Render the three ortho globes and put them beside `planet_map_tidal_lock_inspiration.webp`.**
That is one command, it has never been done, and it is the comparison the whole design is judged on.
It may make the next move obvious — or reveal that the map is closer than it feels.

```
python3 src/RimMandrake/Utils/worldview.py world/ASHKARR_WORLDMAP \
        --layer biome --projection ortho --center 0,0     # day face
        # then --center 0,90 (terminator) and --center 0,180 (night cap)
```

---

## 18. The named backlog

Every item from this plan and from `TRANSIENT_lorekeeping.md`, named so a cold reader knows what it
is. **No `Q104`, no `D55`, no bare numbers.**

### Milestones (from V1 rows — names to be confirmed against `V1.md`)

`PLANET_SURFACE_AUTHORED_?` · `FACTION_ROSTER_COMPLETE_?` · `FAITHS_AUTHORED_COMPLETE_?` ·
`WORLD_FROZEN_AND_SHIPPED_?`

### S0 — half a day, do these regardless

| item | what |
|---|---|
| `BOARD_STATE_CLASSIFIER_FIX_1` | `derive_matrix.py:277` → `state.split()[0]`. Recovers 28 done, 2 blocked |
| `CLOSES_TRAILER_REGEX_FIX_1` | `warn_unclosed_queue_item.py:40` has no `_` in its class; disagrees with `derive_matrix.py:88` on every new ID |
| `DESIGN_INDEX_REGENERATION_1` | `doc_roster.py --write` — **out of sync now**; `INHABITED_CAST_EMPIRE/TUSKEN` missing |
| `DOC_BUDGET_RED_ERRORS_1` | wire the existing exit-1 to a commit hook, red output |

### S1 — canon

| item | what |
|---|---|
| `CANON_NUMBERS_SINGLE_SOURCE_1` | author `canon.yml` |
| `CANON_CONTRADICTION_CHECKER_1` | `check_canon.py` + the `<!-- canon-ok: -->` escape |
| `WATER_PERCENT_RECONCILE_1` | 8.1 vs 25 vs 8.6 vs 6.9 — `the_one_map.md` contradicts itself 30 lines apart |
| `TERMINATOR_TEMP_RECONCILE_1` | +14 vs −37, **51 °C apart**, and hydrology inherited the wrong one |
| `FACTION_COUNT_RECONCILE_1` | 14 / 13 / 12 / 11 — the Unbound Hive cut never propagated |
| `SETTLEMENT_COUNT_RECONCILE_1` | 72 / 66 / 37 — two are measurements of dead worlds |
| `SPECIES_COUNT_RECONCILE_1` | 42 / 44 / 54 / 70 / 79 / 80 |
| `MODLIST_STAMP_AS_OF_DATES_1` | nine different counts, no as-of anywhere |
| `LAKE_BIOME_CUT_OR_KEEP_1` | cut by the owner; **1.4% of the planet is `Lake`** |
| `GELATINOUS_CUT_REVERSAL_1` | cut 08-04, placed 08-18, palette never told |
| `SAVANNA_PREMISE_RESOLVE_1` | a 701-line doc's subject is blacklisted |
| `OASIS_OWNERSHIP_RULING_1` | Hutts or Deepwater Compact — inverts the water politics |
| `JAWA_LEADER_TITLE_RULING_1` | First Bargainer vs Prime Trader; the engine layer ticks ✅ while overwriting canon |
| `HABITABLE_RING_ARC_RULING_1` | 34–57 vs 40–57 — ~700 tiles |
| `BIOME_SURVIVOR_COUNT_FIX_1` | 36 / 37 / ~35 from a 66- or 57-def base |

### S2 — supersession

| item | what |
|---|---|
| `DESIGN_DOC_STATUS_HEADERS_1` | one header line on all 119 docs |
| `DEAD_DOC_LINK_REFUSAL_1` | checker refuses a live doc linking into a dead one |
| `SAVE_PIPELINE_DOC_RETIRE_1` | `⛔ DEAD DOCUMENT`, still linked, still in the index |
| `WORLDGEN_DEF_DEAD_NUMBERS_1` | its banner **points readers at** superseded measurements |
| `FACTION_SPEC_CLUSTER_POINTERS_1` | 4-way cluster; nothing tells `faction_stage3` it was replaced |
| `LEADER_CANON_RESCUE_1` | 2 of 12 named leaders exist **only** in the file slated for retirement |
| `LOST_ITEMS_RECOVER_1` | `softshadow-xtp-…-2f7c85` and `D-CHK1` — gone, and softshadow is still live |
| `BESTIARY_ASPIRATIONAL_HEADER_1` | 78 named, 0 built |
| `ROSTER_V2_FAITH_LAYER_RETIRE_1` | 12 faith names, **0 on disk**, superseded and unmarked |

### S3–S6 — the machinery

`ITEM_FILES_ONE_PER_ITEM_1` · `QUEUE_IMPORT_WITH_CONFIDENCE_1` · `CLOSES_HISTORY_REPLAY_1` ·
`GENERATED_QUEUE_VIEWS_1` · `EVENT_LEDGER_APPEND_ONLY_1` · `RIMFLOW_CLI_CORE_1` ·
`PRIORITY_ENGINE_DETERMINISTIC_1` · `DEPLOYMENT_OBJECT_BUILD_OWNED_1` ·
`ARTIFACT_ACCEPT_SWEEP_1` · `FROZEN_DUMP_IMMUNITY_1` (teach `refresh.py` frozen ≠ stale) ·
`GAME_STATE_MACHINE_WIRING_1` · `QUEUE_LINT_BLOCKING_HOOK_1` · `AGENT_SEAT_FILES_REWRITE_1` ·
`BOARD_DECK_VIEW_1` · `BOARD_FLOW_GRAPH_1` · `BOARD_VNV_MATRIX_1` · `BOARD_TIMELINE_VIEW_1`

### The planet — do this one first

| item | what |
|---|---|
| ⭐ `ORTHO_GLOBE_FIRST_RENDER_1` | **one command, never yet run.** Three ortho globes beside the target reference |
| `REFERENCE_MATCH_HARNESS_1` | `refmatch.py` — contact sheet + the five defect screens |
| `GAZETTEER_ZERO_TILE_AUDIT_1` | The Ash Verge · The Long Dark · The Ember Sink · `AB_OcularForest` · `Glowforest` · `HorrorWastes` — named, zero tiles |
| `CAST_PLACES_ON_THE_MAP_1` | 26 named places exist as `<place>` strings on 269 CharacterDefs and are bound to no tile |

---

## 19. Revised open questions

1. **Milestone names for the 14 V1 rows** — I will draft them from `V1.md`'s own step titles unless
   you would rather name them yourself. They are the most-read names in the system.
2. **The 20 invented `row:` buckets** — promote, remap, or drop? I would triage and bring you a
   one-page table rather than guess.
3. **`refmatch.py` defect thresholds** — circularity > 0.75, straight-run length, bearing-variance
   floor. I would calibrate these **against the reference images themselves** so the screen agrees
   with the photographs rather than with my taste.

---
---

# PART THREE — COLD-START EXECUTION RUNBOOK

**If you are a fresh BUILD seat with no context, everything you need is in Part Three.**
Parts One and Two are the *why*. This part is the *how*, and it assumes you have read neither.

---

## 20. Your first five minutes

You are the **BUILD seat**. You are the **only** fan-out point — subagents cannot spawn subagents.
Your job is to run the waves in §22, dispatching the briefs in §24, and to commit and push on
behalf of each wave.

```bash
cd /mnt/d/Luke/dev/Rimworld
git pull --rebase
python3 src/RimMandrake/Utils/check_git_locks.py     # a stale index.lock will wedge every agent
```

Then run §21 **before dispatching anything.** These numbers were measured 2026-08-20; if a wave's
premise has already been fixed by another seat, you must know that before you spend agents on it.

⛔ **Do not read `infrastructure/state/queue/*.md`.** They total ~207,000 tokens and you do not need
them. Everything actionable is in §18 and §24.

---

## 21. Ground truth — verify before you act

Run all six. Each line states what it returned on **2026-08-20**. A mismatch means the world moved;
re-plan rather than proceed.

```bash
# 1. The board is lying. Expect BEFORE W0: done 0, blocked 0.
#    AFTER W0 (measured 2026-08-20, post-fix): done 5, blocked 2, doing 7, closed 116.
#    ⚠️ The "28" this line originally predicted is not reachable under this metric and
#    was never measured: `mix.done` counts items filed done WITHOUT a `Closes:` trailer,
#    and 17 of the 22 done items in DECIDE/BUILD/CHECK already carry one, so they are
#    banked in `velocity.closed` (116) instead. done 5 + closed 116 is the true reading.
python3 src/RimMandrake/Utils/derive_matrix.py >/dev/null 2>&1
python3 -c "import json;d=json.load(open('infrastructure/state/status_matrix.json'));
m=[c['mix'] for r in d['rows'] for c in r['cells'].values()]
print('mix done:',sum(x['done'] for x in m),' blocked:',sum(x['blocked'] for x in m),
      ' blockers panel:',len(d['blockers']),' closed-from-git:',d['velocity']['closed'])"

# 2. Non-canonical state strings. Expect: 68 — but of 142 filed items, not 167.
#    58 of the 68 begin with an emoji (27 ✅, 21 ⛔ v2, 5 🔵, 4 ⭐, 1 🔴), which is why
#    the plain `.split()[0]` fix W0 originally specified still returned done 1.
grep -hE '^state:' infrastructure/state/queue/*.md | sed -E 's/^state: *//' | awk '{print $1}' \
  | grep -vcE '^(ready|doing|done|blocked|dropped)$'

# 3. The design index is stale. Expect: exit 1
python3 src/RimMandrake/Utils/doc_roster.py >/dev/null 2>&1; echo "doc_roster exit=$?"

# 4. Design tier size. Expect: 119 files, 46488 lines
git ls-files design | grep '\.md$' | wc -l
git ls-files design | grep '\.md$' | xargs wc -l | tail -1

# 5. The self-contradiction, verbatim. Expect line 100 = 25%, line 130 = ~8.6%
sed -n '100p;130p' design/Jawa/worldbuilding/the_one_map.md

# 6. The hook regex bug. Expect: no underscore in the class
grep -n 'HEADING = re.compile' .claude/hooks/warn_unclosed_queue_item.py
grep -n 'CLOSES_RE = re.compile' src/RimMandrake/Utils/derive_matrix.py
```

---

## 22. The wave plan

Waves are serial. **Inside a wave, everything runs concurrently.** Dispatch a whole wave in one
message with multiple `Agent` calls.

```
W0  solo, ~30 min ....... the four S0 fixes                    [no fan-out — touches .claude/]
      │
      ├────────────────────────────┐
      ▼                            ▼
W1a solo ................. canon.yml        W1b solo ....... ORTHO_GLOBE_FIRST_RENDER_1
      │                                          │            (independent; owner LOOKS)
      ▼                                          │
W2  ×9 parallel .......... reconcile all 38 docs against canon
      │
      ▼
W3  ×2 parallel .......... (a) status headers, 119 docs   (b) check_canon.py + dead-link checker
      │
      ▼
W4a solo ................. event schema + rimflow/model.py     [everything downstream needs it]
      │
      ▼
W4b ×3 parallel .......... importer │ CLI verbs │ render/views
      │
      ▼
W4c ×2 parallel .......... priority engine + deployment object │ artifact-accept sweep
      │
      ▼
W5  solo ................. hooks + agent seat file rewrite      [touches .claude/ and POLICY]
      │
      ▼
W6  ×1 + ×4 .............. board plumbing (solo) → then 4 view modules in parallel
      │
      ▼
W7  solo ................. refmatch.py            [ONLY after the owner has looked at W1b]
```

**Why W2 is nine agents and not fifteen:** the contested numbers are not spread one-per-document.
`ASHKARR_WORLD_DEFINITION.md` and `worldgen_interactive_def.md` each carry **four** of them.
Fanning out by *item* would put seven agents inside the same file. Fan out by **file cluster**, and
the clusters are disjoint by construction.

---

## 23. Fan-out rules — how not to corrupt a shared worktree

Four seats share one checkout. These are not style points.

1. **Every subagent owns a disjoint file set**, given explicitly in its brief. It writes nothing else.
2. ⛔ **Never `git add -A`, `git add .`, or `git commit -a`.** A `PreToolUse` hook blocks it, and the
   reason is that it sweeps peers' mid-edit work into your commit.
3. ⚠️ **`git commit <path>` commits the WORKING TREE at that path, not your index** — including
   another agent's uncommitted edits to that same path. This is why disjointness is mandatory.
4. **Subagents commit; only YOU push.** Push once per wave, after every agent in it has returned.
   *(A deliberate, bounded deviation from commit-and-push-immediately: nine agents racing
   `pull --rebase` produces conflicts that cost more than the minutes of exposure. The window is one
   wave.)*
5. **On `index.lock` contention**, retry with backoff. `src/RimMandrake/Utils/check_git_locks.py`
   diagnoses a stale one.
6. **No subagent messages another agent.** `SendMessage` to a seat is blocked at the sending end.
   Your own subagents are exempt and you resume them normally.
7. **Give every subagent an output budget.** "Report ≤ 400 words: files changed, acceptance-test
   output, anything you could not do." You are the one holding context.

---

## 24. Subagent briefs — copy-paste

### W0 — do this yourself, no fan-out

| item | change | acceptance |
|---|---|---|
| `BOARD_STATE_CLASSIFIER_FIX_1` | `derive_matrix.py` — one `state_of()` classifier used at every comparison site, including `blockers()`. ⚠️ `.split()[0]` alone is NOT enough: 58 of 142 states lead with an emoji, so the keyword must be found past it and mapped (`closed`/`built`/`ruled` → done, `v2` → dropped, `v1` → ready), with the emoji as fallback and `ready` as the default for anything unrecognised | §21 check 1 reports **done 5, blocked 2, doing 7, closed 116** — done ≥ 28 was wrong, see check 1 |
| `CLOSES_TRAILER_REGEX_FIX_1` | `.claude/hooks/warn_unclosed_queue_item.py:40-41` — `[A-Z][A-Z0-9-]*` → `[A-Za-z][A-Za-z0-9._-]*`, matching `derive_matrix.py:88`. Then make it exit non-zero | `INHABITED_DISPLACED_POOL_1` matches whole, not just `INHABITED` |
| `DESIGN_INDEX_REGENERATION_1` | `python3 src/RimMandrake/Utils/doc_roster.py --write` | exit 0; `INHABITED_CAST_EMPIRE` and `_TUSKEN` now in `design/INDEX.md` |
| `DOC_BUDGET_RED_ERRORS_1` | register `doc_budget.py` as a `PreToolUse:Bash` hook; red output naming file + overrun | an over-budget file produces a red message on commit |

⚠️ **Hooks are fail-open (`2>/dev/null || true`). Stdlib only — no third-party imports, ever.**
Write `selftest_<hook>.py` beside each, following `selftest_block_blanket_git_stage.py`.

### W1a — `canon.yml` (solo, you)

Author `infrastructure/state/canon.yml` per §2.3. **Every value must trace to a ruling or a
measurement — no guesses.** Where two sources disagree, canon takes the one backed by the painted
map or the owner's most recent ruling, and records the loser in a `superseded:` comment.

### W1b — brief for one agent

> Render Ash'karr as three orthographic globes and build a comparison sheet. This has never been
> done — every existing render is equirectangular, while the binding reference is a globe.
>
> ```
> python3 src/RimMandrake/Utils/worldview.py world/ASHKARR_WORLDMAP \
>         --layer biome --projection ortho --center 0,0     # day face
> # repeat with --center 0,90 (terminator) and --center 0,180 (night cap)
> ```
> Then write `TRANSIENT_refmatch_globes.html`: our three globes beside
> `research/Jawa/planet_map_tidal_lock_inspiration.webp` and
> `research/Jawa/planet_inspiration_tidal_lock2.webp`, same display size, labelled.
> Do NOT judge the result and do NOT change the map. Report the output paths only.
> Files you may write: `world/view/*`, `TRANSIENT_refmatch_globes.html`.

### W2 — nine agents, one per cluster

**Shared preamble for all nine** (paste into each, then append that cluster's file list):

> You are reconciling design documents against a single source of truth.
> Read `infrastructure/state/canon.yml` — it holds the authoritative value for every contested
> number. **Fix every number in YOUR FILES ONLY that contradicts canon.**
>
> Rules:
> - ⛔ Touch no file outside your list. Other agents are editing theirs right now.
> - **Never delete the history of a number.** Replace `25%` with `8.1%` and, where the old value is
>   load-bearing to an argument, keep it struck through with a date: `~~25%~~ → 8.1% (owner, 2026-08-18)`.
> - Where your file is the one that was WRONG, add one line at the top naming what changed.
> - Prose that *documents* an old number (inside `~~`, a blockquote, or a line containing
>   `superseded`/`was`/`formerly`/`dead`) is correct as-is — leave it.
> - Commit your own paths only, with a `Closes:` trailer. **Do not push.**
> - Report ≤ 400 words: numbers changed (file:line, old → new), anything you could not resolve.

| cluster | files |
|---|---|
| **C1 world-core** | `ASHKARR_WORLD_DEFINITION.md` · `the_one_map.md` |
| **C2 world-physics** | `tidally_locked_world.md` · `hydrology_and_fire_ecology.md` · `setting_physics.md` · `desert_world_design.md` · `water_doctrine.md` |
| **C3 faction-engine** | `FACTION_SPEC.md` · `faction_world_spec.md` · `faction_stage3_buildable_spec.md` |
| **C4 faction-fiction** | `faction_roster_v2.md` · `faction_religions.md` · `faction_religions_spec.md` · `faction_equipment_guidance.md` · `pawnkind_roster.md` |
| **C5 worldgen-legacy** | `worldgen_interactive_def.md` · `worldgen_interactive_build_concepts.md` · `row8_build_order.md` |
| **C6 biome-fauna** | `biome_and_fauna_roster.md` · `biome_terrain_palette.md` · `biome_review_comments.md` · `fauna_placement.md` · `Alien_Bestiary.md` · `Livestock_Trade_Utility_Pets_v1.md` |
| **C7 bridge-scenario** | `design/Jawa/bridge/*.md` · `SCENARIO_SPEC.md` · `SCENARIO_SETTINGS_SPEC.md` · `tile_augmentation_catalogue.md` |
| **C8 mods-and-rest** | `design/Jawa/mods/*.md` · `design/RimMandrake/*.md` · `design/Jawa/art/*.md` · `build_plan.md` · `droid_ruling.md` |
| **C9 stragglers** | `EMPIRE_GAP_AUDIT.md` · `force_users_build_spec.md` · `gravship_pursuer_mechanism.md` · `ship_deck_plan.md` · `ship_designs.md` · `what_the_machines_are.md` · `droid_chassis_coverage.md` · `V2_DREAMS.md` |

**Cluster-specific additions:**

- **C1** also fixes the self-contradiction at `the_one_map.md:100` vs `:130`, and adds a pointer back
  from `ASHKARR_WORLD_DEFINITION.md` to `the_one_map.md` (the link is one-way today).
- **C2** — 🔴 **REWRITTEN 2026-08-20 from the mod's own C# source. Read all of this first.**
  The audit's verdict was right and its diagnosis was not. `canon.yml > temperature_curves`
  carries the full trace; the short form:

  `Alien Worlds - Tidally Locked` ships `<avgTempByLatitudeCurve>` = `0.0,70 · 0.1,65 · 0.5,14 ·
  1.0,−37 · 1.3,−70 · 2.0,−80`. **The name says latitude; the code does not.**
  `Source/PlanetTypeDef.cs` evaluates it at `Acos(cos lon · cos lat) · Rad2Deg / 90` — the
  great-circle **arc** from the substellar point, over 90. So **x = 1.0 is the terminator at
  −37 °C**, and **x = 0.5 is arc 45°, deep on the dayside, at +14 °C.**

  🔑 **Our design tier read x = 0.5 as the terminator, and everything downstream is off by one
  point on the same curve.** Three defects in `tidally_locked_world.md` and one inherited:

  | file:line | says | is |
  |---|---|---|
  | `tidally_locked_world.md:162` | `0.5 → +14 °C — this is the terminator` | arc 45°, dayside |
  | `tidally_locked_world.md:351-352` | "the axis: **latitude**, with 0.5 = +14 = the terminator" | the axis is **arc/90**, and 0.5 is not the terminator |
  | `tidally_locked_world.md:453-454` | "a nightside running −37 at latitude 1.0" | x=1.0 **is** the terminator |
  | `hydrology_and_fire_ecology.md:528-531` | "the active planet curve already agrees" | it does not agree — see below |

  ✅ **But the conclusion that only biomes need forcing SURVIVES, for a different reason, and you
  must write the new reason in rather than deleting the ruling.** The mod is **worldgen-only**:
  `FieldPatcher.cs` patches the curve into `WorldGenStep_Terrain.BaseTemperatureAtLatitude` and the
  transpiler targets `WorldGenStep_Terrain.GenerateTileFor`. Nothing recomputes tile temperature at
  runtime. Our planet is hand-painted and ships frozen, so **the mod's −37 °C terminator can never
  reach it.** The curves disagree; it does not matter. ⛔ Do NOT change our +14 °C.

  ✅ `ASHKARR_WORLD_DEFINITION.md:74-83` already had this right and is the table to cite.
  Correct `tidally_locked_world.md:153` *"LATITUDE IS THE AXIS"* — the axis is **arc**, for the
  mod as well as for our painted world (correlation −0.98, `ashkarr_paint.py:13`).

- **C3** — `faction_world_spec.md` §1 states *"water increases with latitude"* **above** its
  superseded banner, so it survives every harvest. Fix it. Add the missing forward pointer from
  `faction_stage3_buildable_spec.md` to `FACTION_SPEC.md`.
  ⛔ **The "rescue Kiknik and Tarn Vox" instruction is WITHDRAWN — they are already shipped.**
  Verified 2026-08-20: both are PawnKindDef labels at
  `src/Jawa/Jawa_Patches/Defs/PawnKindDefs/JawaFactionRoster.xml:848` and `:938`, generated by
  `src/RimMandrake/Utils/gen_pawnkind_roster.py:127,132`. Nothing is at risk if the design doc
  retires. ⚠️ They are LABELS, not defNames, so a rename in the generator changes them silently —
  that is worth a line in canon, not a rescue.
- **C4** — `faction_roster_v2.md` names **12 faiths that do not exist on disk** (verified: 0 hits for
  all of them under `src/`). Mark that layer superseded by `faction_religions.md`, which produced the
  12 real `<ideoName>` values — confirmed on disk 2026-08-20: eight in our own FactionDefs (the
  Balance · the Continuity Protocol · the Green Oath · Meckgin · The Salvation · the Ascendant
  Genome · the Reckoning of Debts · the Weight) and four patched onto other mods' factions (the
  Contract · the Sun-Debt · the Covenant of Free Wells · The Rising Order). ⚠️ Both sets number
  twelve, which is exactly why the collision went unnoticed — say WHICH twelve, every time.
- **C5** — `worldgen_interactive_def.md`'s banner **actively points readers at dead measurements**
  (*"read this file for its rulings and its measurements"* — 6.9% water, 37 settlements, 11 factions,
  all superseded). Rewrite the banner to kill the measurements too.
- **C6** — add `<!-- status: aspirational -->` to `Alien_Bestiary.md`: 🔴 **108 named creatures, 0
  on disk** — not 78. The 78 came from parsing only the tables sharing one header row; §3.12–§3.14
  use different headers and were skipped, and the file's own header says "all 104 VGE creatures plus
  the four special outputs" = 108. Two independent extractions agree. **Zero** appear under `src/`
  as a defName or label; every raw grep hit is a substring coincidence.
  ⛔ **`Lake` is RESOLVED and the answer is KEEP — do not cut it.** `The Scald`, one of the three
  ruled seas, is painted `Lake` for all 312 of its tiles; the other two seas are `Ocean`. Cutting
  the def deletes a named sea. `biome_review_comments.md:54` is the only file saying cut, and it
  flags itself "worth a second look" — this was the second look. `AB_GelatinousSuperorganism`
  (cut 08-04, placed 08-18, 96 tiles, palette never told) stays open for the owner.

### W3 — two agents

**(a) status headers.** One header line on all 119 design docs: `live` · `superseded-by: <path> ;
<date> ; <what changed>` · `dead ; <date> ; <why>` · `aspirational`. HTML comments, so nothing
renders. Known: `save_authoring_pipeline.md` is `⛔ DEAD DOCUMENT`, still linked and still indexed.
Files: `design/**/*.md`.

🔴 **DONE 2026-08-20 — and the four statuses were not enough.** Two gaps found in the doing:

- **A doc can be live in its RULINGS and dead in its NUMBERS.** `worldgen_interactive_def.md` is
  cited for decisions that are current while every figure in it measures a planet that no longer
  exists. Marked `live`, the machine-readable half of its own banner is lost — and `live` is the
  status that *invites* quoting. Added one optional field rather than a fifth status:
  `<!-- status: live ; numbers-superseded-by: <path> ; <date> ; <why> -->`, which `design/INDEX.md`
  renders as *"⚠ do not quote its numbers"*.
- ⚠️ **A header hand-written into a GENERATED file is deleted by the next regeneration, silently,
  and a missing status looks exactly like a doc nobody got to.** `design/Jawa/art/SALVAGE_PALETTE.md`
  is rewritten whole by `design/Jawa/art/salvage_filter.py`; the generator now emits the header
  itself. `design/INDEX.md` was safe only by luck — `doc_roster.py`'s `splice()` preserves
  everything above its BEGIN marker. **Before stamping any doc, ask what writes it.**

**(b) the checkers.** `src/RimMandrake/Utils/check_canon.py` (fails on a number contradicting canon,
with the `<!-- canon-ok: reason -->` escape) and a dead-link checker (a `live` doc may not link into
a `dead` one). Files: `src/RimMandrake/Utils/*.py` only.

🔴 **The §2.3 exemption rule is unsafe as written, and the two counter-examples are already known.**
Exempting a whole line because it *contains* `~~` or `⛔` breaks on table rows, where the marker
belongs to one cell and the claim to another:

| line | what the rule does | what is true |
|---|---|---|
| `the_one_map.md:130` | exempt — the row's right-hand cell holds `~~worldgen_sea_spec.md req 1 (22–28%)~~` | the LEFT cell asserts a live target of ~8.6% |
| `fauna_placement.md:113` | exempt — the line opens `⛔ **Not** …` | the `⛔` negates a *fauna placement*, not the biome |

⚠️ Both fail in the same direction — a **silent miss**, which is the expensive one: the checker
reports clean and the contradiction survives. Scope the marker to the **cell** in a table row (split
on `|` and test the cell holding the number), not to the line.

### W4–W7

Follow §18's named items and §2's data model. Sequence and file ownership are in §22.
**W7 (`refmatch.py`) does not start until the owner has looked at W1b's globes** — its five defect
thresholds are calibrated against the reference photographs, not chosen.

---

## 25. Acceptance — how you know a wave is done

| wave | test |
|---|---|
| **W0** | §21 check 1 → `done 5, blocked 2, doing 7, closed 116`; check 3 → `exit=0`; both hook selftests 7/7 and 6/6 |
| **W1a** | `canon.yml` parses; every value carries a source |
| **W1b** | three `*.ortho.png` exist for `ASHKARR_WORLDMAP`; the sheet opens |
| **W2** | 🔴 **that grep is the wrong test — corrected 2026-08-20.** `25%` is an ordinary percentage: after W2 it survives 15 times in `design/` as a droid ratio, a research-speed boost, a spacer-equipment share and an armour-penetration figure, none of them about water. The real test is `python3 src/RimMandrake/Utils/check_canon.py` → **0 contradictions** (39 advisory, all undated mod counts), because it tests the number *against its context* |
| **W3** | `check_canon.py` exits 0 across all 119 docs, and `selftest_check_canon.py` passes 28/28; `check_doc_links.py` reports no live→dead link. ⚠️ It also reports 117 docs with **no status header** — and *unmarked is not a pass*, which is what W3(a) exists to fix. Once the headers are written, the gate is `check_doc_links.py --require-status` |
| **W4** | `rimflow next --seat BUILD` returns one item in < 1 s; `rimflow reindex` rebuilds from the ledger alone |
| **W5** | a deliberate `done → ready` edit is **refused**; a cross-seat write is **refused** |
| **W6** | board renders at `:8787`; regeneration < 100 ms |
| **W7** | contact sheet opens; the five defect screens run |

---

## 26. Guardrails

- ⛔ **Never take the bridge.** CHECK only, always, no exception.
- ⛔ **Never announce a game state.** The owner alone does that; `broadcast.py` is his tool.
- ⛔ **Never `deploy_custom_mods.py --apply` without `--mod`** — it overwrites the game copy with the
  repo as it currently is.
- ⛔ **No new opaque IDs.** Not `Q104`, not `D55`, not `B-FIX2`. `THREE_DESCRIPTIVE_WORDS_#`, always.
  A run is the sole exception and is never seen alone: `<ITEM>/run-N@<config>`.
- ⛔ **No file over ~50 MB** in a commit. Hosts hard-reject at 100.
- ✅ **Any new scratch output is `TRANSIENT_<name>.md`**, committed, never gitignored.
- ✅ **At 90% context**: write down what you learned, close or block the item, commit, push,
  `rimflow seat idle --reason context-exhausted --note "<where I stopped>"`.
- ⚠️ **Numbers in this plan were measured 2026-08-20 and decay.** §21 is how you check. When a
  measurement here disagrees with the repo, **the repo is right** — re-measure and correct this file.

---

## 27. What I would actually do first

**W0 is thirty minutes and makes the board stop lying.** **W1b is one command** that produces the
single comparison this project has never made — the map as a globe, beside the globe it is meant to
resemble. Neither depends on anything else in this plan, and W1b may change what the rest of it
should say.
