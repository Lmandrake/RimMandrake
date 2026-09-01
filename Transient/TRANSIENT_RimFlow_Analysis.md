# RimFlow — the simple version

**Rewritten 2026-08-20 after the owner asked for it plainly. Nothing here is decided.**

---

## The problem, in one line

**Markdown is being asked to be a database, and it has stopped being able to do it.**

Right now the board says **116 items closed** (it counts those from git commit trailers — correct)
and in the same file says **0 done, 0 blocked** (it counts those by reading the queue's `state:`
field). 28 finished items and 2 blocked items are invisible. The board contradicts itself.

**Why the difference matters more than the bug:** the half that works reads **git**. The half
that's broken reads **prose**. That one fact should decide the whole design.

---

## The fix, in one line

**Keep every word of prose. Move the ~8 facts about each item into something a program writes.**

Nothing you read today goes away. The owner rulings, the arguments, the warnings — all stay in
Markdown, all stay readable, all stay in git. What changes is that `state: ready`, `row: 9`,
`target: v1` stop being typed by hand into a shared file.

---

## Your question: why doesn't the ledger flood everyone's context?

**Because nobody reads it. Not you, not an agent. A command reads it.**

That is the entire answer, and it's the opposite of how it sounds.

```
BUILD sits down to work.

TODAY                                  AFTER
opens queue/BUILD.md                    runs:  rimflow next --seat BUILD
  → 128 KB, 32,000 tokens                 → ~400 tokens:
  → 27 items, 25 not his                     ROLE_KINDS_UNARMED_1
  → must skim to find his one                spec:     <8 lines>
                                             verify:   <3 lines>
                                             blocked:  no
```

The ledger can be 9 MB. The answer is still 400 tokens. **The size of the store and the size of
the answer are unrelated** — same reason `git log -1` is instant on a 312 MB `.git` folder.

**Measured, so this isn't hand-waving:**

| | |
|---|---|
| one event | **193 bytes** |
| all activity in these 8 days | ~1,100 events = **211 KB** |
| a full year at this pace | **~9 MB** |
| what a seat reads to get its next item | **~400 tokens, regardless** |

And when 9 MB does start to feel silly, you roll it: `events/2026-08.jsonl`, `events/2026-09.jsonl`.
Never rewritten, just a new file each month. Git handles append-only files extremely well.

**Today's context problem is caused by the exact thing we're removing** — agents reading the state
file with their eyes. 827 KB of queue and state Markdown, ~207,000 tokens. A seat cannot hold its
own inbox today. After, it never tries.

---

## The two rules you asked for, and how each is actually enforced

### "No agent posts into anyone else's queue"

**Today there is nothing stopping it.** Queue files are ordinary files; every seat can write every
one of them. Worse, `git commit <path>` commits the *working tree* at that path, so one seat can
sweep up a peer's half-finished edits without meaning to.

**After:** an item is one file, `items/<ID>.md`, and it carries `owner: BUILD`. The tool stamps
the actor from `AGENT_SEAT` — the seat can't claim to be someone else — and refuses a write to an
item it doesn't own. A pre-commit hook refuses direct hand-edits to `items/`.

🔑 **Filing work *for* another seat stays legal — that's the whole workflow.** What becomes
impossible is *changing* another seat's item.

### "No moving work backward"

**Today:** measured **11 real instances** in 8 days. A `✅ RULED` decision that reversed to
`ready — NEVER IMPLEMENTED` four days later. A `DONE` item flipped to `⛔ v2`, losing that it was done.

**After:** the tool refuses `done → ready`, `done → blocked`, `dropped → ready`. A failed check
doesn't reopen the build — it **appends a new record** and creates a new linked item. The old
record stays true forever, because appending is the only thing the file format allows.

🔑 **And "v1 → v2" stops being a backward move.** That's a separate field. `B25` was moved to v2
while it was done, and the move erased the done-ness. Two facts, two fields, no collision.

---

## What it looks like on disk

```
infrastructure/state/
  events.jsonl        append-only, committed to git. The truth. Nobody opens it.
  items/<ID>.md       ONE FILE PER ITEM. Prose on top, ~8 facts in a header.
  queue/<SEAT>.md     still here, still readable — but GENERATED. "derived, do not edit."
  index.sqlite        gitignored. Deletable. `rimflow reindex` rebuilds it in seconds.
```

**On the SQLite worry — you had this right.** The database never holds anything git doesn't.
It's a lookup table rebuilt from the ledger, exactly like `closed_ledger.json` already is today
("delete it and the next run rebuilds it"). If it's lost, nothing is lost. **Git stays the record
of progress, which is the part you said mattered.**

**One file per item is the single biggest win**, and it's independent of everything else:

- a seat reads its 6 ready items, not a 141 KB file
- four seats stop colliding on six hot files
- `git log -- items/B53.md` is that item's whole life, free
- **`B53` cannot be filed in two queues at once** — which it is, right now, with two different
  `state:` values. One ID, one path, structurally impossible.

---

## The three choices

| | what you get | what it costs |
|---|---|---|
| **A. Just enforce the rules** | Board tells the truth. Backward moves refused. Missing fields refused. | **1 day.** No new dependencies. Nothing to migrate. |
| **B. A + one file per item + the ledger** ⭐ | All of A, plus: context tax gone, cross-posting impossible, test results become data, you can ask "why is this blocked" and get an answer | **4–6 days**, staged. Still no new dependencies. |
| **C. Full RimFlow as proposed** | A graph UI, forecasting, portable to other projects | **3–4 weeks**, 12 new packages, and the database problem you already spotted |

**I'd do B, shipping A on day one as its first stage.** If B stalls, A has still fixed the board.
And B is the honest on-ramp to C later — the ledger is exactly what a future database would replay.

---

## The order I'd go in

1. **Day 1 — make the board honest.** Fix the classifier (one line: `state.split()[0]`), fix the
   hook regex, add the blocking lint. *Test: the board reports ≥28 done and 2 blocked instead of 0 and 0.*
2. **Split the items.** Mechanical, scriptable, reviewable as one diff. Kills the context tax.
3. **Add the ledger.** Seats start calling `rimflow` instead of typing state.
4. **Record test results.** This is the one that would have caught the ✅ decision that never
   reached disk — it becomes a query instead of something someone has to remember.
5. **Extend the board** with a per-item "why is this blocked" view. Only after 3 and 4 have run a week.

---

## The evidence, compressed

Everything below was measured in this repo, not estimated.

| what | number |
|---|---|
| Commits that are **pure bookkeeping** — no code, no design | **470 of 1,554 = 30%** |
| Queue + state Markdown | **827 KB ≈ 207,000 tokens** |
| Items whose `state:` isn't one of the 5 valid words | **68 of 167** |
| `state:` line length | median **80 chars**, longest **202** — it's prose |
| Items whose `state:` starts with an emoji, not a word | **58 of 142** |
| Backward transitions in 8 days | **11**, plus 3 ruling reversals |
| Items genuinely lost — no trailer, not in v2, not in the ledger | **2** |
| Item invisible to every seat because it had no `state:` line | **1, for 4 days** |
| Same ID filed in two queues right now, with different bodies | **B53** |
| ID schemes live at once | **3** — 107 legacy, 44 kebab-hash, 42 new |
| Structured pass/fail records anywhere in the repo | **0** |
| Player.log lines linked to the item they decide | **0 of 37,543** |

**Two live bugs, worth fixing whatever you choose — under an hour together:**

1. `.claude/hooks/warn_unclosed_queue_item.py:40` matches IDs with `[A-Z][A-Z0-9-]*`. **No
   underscore.** So it reads `INHABITED` out of `INHABITED_DISPLACED_POOL_1` and disagrees with
   `derive_matrix.py:88` on every new-style ID. It also always exits 0, so it can only nag.
2. `derive_matrix.py:277` compares `state == "done"` against a field that now contains a sentence.
   One line fixes it and 28 items reappear.

---

## What I'd want you to push back on

- **4–6 days is 4–6 days**, and the world freeze is ahead. Stage 1 alone is one day and captures a
  large share of the value. Stages 2–5 are a bet that there's enough runway left to repay them.
- **A generated queue file that someone hand-edits is worse than a hand-kept one.** The hook has to
  refuse those edits from day one, not "later".
- **I'm the BUILD seat proposing to rebuild the system that grades BUILD.** Worth naming. The Stage 1
  test is deliberately a number someone else can check.
