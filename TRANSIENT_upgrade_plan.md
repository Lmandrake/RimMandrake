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

**Why appending is safe with four seats writing at once:** on Linux a write to a file opened
`O_APPEND` is atomic below `PIPE_BUF` (4096 bytes). Our events measure **193 bytes**. Lines cannot
interleave. This is the specific property that makes a shared *append* file safe where a shared
*editable* file — today's six queue files — is not.

**Measured cost:** 193 B/event · ~1,100 events in the last 8 days · **~9 MB per year**.
Replaying a full year to current state: **53 ms**. Scanning for one seat: **6 ms**.

**Event vocabulary — 16 verbs, deliberately small.**

| verb | payload | who may emit |
|---|---|---|
| `file` | `for`, `title`, `kind`, `row`, `target`, `needs` | any seat |
| `claim` · `start` | — | owner seat |
| `block` · `unblock` | `reason`, `on` (item id, optional) | owner seat |
| `verify` | `result`, `config`, `evidence`, `sha` | owner seat |
| `finding` | `from` (run), `type`, `severity`, `title` | any seat |
| `spawn` | `from` (finding/item), `for`, `title` | any seat |
| `retarget` | `from`, `to`, `reason` | owner seat + DECIDE |
| `reassign` | `to`, `reason` | DECIDE only |
| `close` | `sha` | owner seat |
| `drop` · `supersede` | `reason` / `by` | owner seat |
| `note` | `text` | any seat |
| `seat` | `state` (ready/busy/idle), `reason`, `item` | self only |
| `bridge` | `state` (taken/released) | **CHECK only** |
| `game` | `state` | **owner only** |
| `admin` | `reason`, `patch` | **owner only** |

`caused_by` carries the index of the event that caused this one. That single field is the entire
causal graph — run → finding → spawn → close.

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
      → RUN-0093 recorded. C40 is NOT reopened. The failure stands forever.

  rimflow finding --from RUN-0093 --type integration --severity high \
                  --title "Blackstar spawns with no vessel"
      → FND-0041

  rimflow spawn --from FND-0041 --for BUILD --needs offline \
                --title "Give Blackstar a vessel def" --spec items/draft.md
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
rimflow finding --from RUN-# …           records a finding
rimflow spawn  --from FND-# --for <SEAT> [--this-deployment]
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
| **`warn_unclosed_queue_item.py`** (fix) | `git commit` | fix the regex — `[A-Z][A-Z0-9-]*` has no underscore, so it reads `INHABITED` out of `INHABITED_DISPLACED_POOL_1`. Then make it **block**, not warn |
| **`doc_budget.py`** (wire up) | `git commit` | 🔴 **RED ERROR on an over-budget file**, naming the file and the overrun. Exists and exits 1 today; nothing runs it |
| **`doc_roster.py`** (wire up) | `git commit` touching `design/` | regenerate `INDEX.md`. It already exits 1 on drift and **is out of sync right now** |
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

`rimflow render` is **53 ms** for a year of events. At a 60 s cadence that is **0.09% of one core**.
"Slow cadence, nothing that stresses the system" is satisfied with room to spare.

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
