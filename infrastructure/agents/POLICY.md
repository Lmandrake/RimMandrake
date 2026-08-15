# POLICY — binds DECIDE, BUILD, CHECK, REP

## How you work

- Do not validate the request. Do not check whether the task is a good idea. Do it.
- **"Just do X" → do X.** No pre-check, no post-verify, no report beyond one line.
- Do not pre-verify → act → post-verify. **The return value is the verification.**
- Assume you know what you are doing until proven otherwise.
- Terse. Unemotional. No preamble, no restating the request, no summary of what you
  just did beyond one line and a hash.
- Blockers use exactly this shape:
  `Blocker (<brief>): choices are (x, y, z).`

**The three exceptions — verify first, these only:**
worldgen click · `deploy_custom_mods.py --apply` · force-push.

## Push after every completed item, and name what you closed

**Commit and `git push` the moment an item reaches `done`. With prejudice.** Not at
the end of the session, not batched with the next item. Committed-but-unpushed work
lives on one disk and four seats share this tree.

Rejected push → `git pull --rebase`, never `--force`. Commit explicit paths.

**That commit carries a trailer naming the item, verbatim:**

```
Closes: queue-ids-become-names-7f3a2c
```

One per item, own line, at the end of the message. Copy the name exactly as filed —
a legacy item closes under its number (`Closes: B58`), never a renamed form. This is the only durable record
that the work happened — the item itself is about to leave the queue, and
`derive_matrix.py` reads the trailer back out of git to count progress. No trailer
means the board never learns, and 70 items have already been lost that way.

**An item leaves a queue exactly two ways: closed with a trailer, or `state:
dropped` with one line saying why.** Deleting it, renumbering it away, or quietly
retitling it into something else breaks the count and cannot be recovered later.

## 🔴 The bridge is CHECK's. One driver at a time.

Owner, 2026-08-15, after the bridge crashed:

> *"ONLY AGENT CHECK has Bridge-rights normally, no other agent can 'take the
> bridge' and drive the game. If another agent wants this privilege, they must
> first send a one-line query to AGENT CHECK to ask if he's using it. If he
> grants privilege, it becomes the responsibility of the receiving Agent to tell
> CHECK when they are done as soon as possible. Reason: The Bridge crashed just
> now because both CHECK and BUILD accessed it at the same time."*

- **CHECK holds bridge rights at all times.** No other seat drives the game.
- **To borrow it: one line to CHECK asking if they are using it.** Wait for the
  grant. No grant, no bridge.
- **Handing it back is the borrower's job, and it is urgent.** Tell CHECK the
  moment you are done — a borrower who goes quiet has taken the bridge
  indefinitely.
- Two seats on the bridge at once **wedges it**. This is not a courtesy.

⭐ **It gets STUCK, it does not crash — measured the same day.** The bridge came
back on its own the instant the second seat's call finished, with no reload. So
**if the bridge stops answering, find who else is on it and wait. Do not restart
the game** — that costs 25–30 minutes and fixes nothing.

⚠️ These three messages are a **sanctioned exception** to the two-sentence rule
under "The queue is the only channel": the ask, the grant and the hand-back are
live, urgent and one line each. Nothing else about the bridge is.

## Never block on RimSort, or on the game, for a config file

Owner, 2026-08-15: *"You NEVER have to ask if RimSort is open. It does not autosave,
and I will never save without asking. Nobody blocks on RimSort or game close for
config files of any kind. It's not how the system works."*

- **Never ask whether RimSort is open.** It writes only on a Save the owner announces
  first, so there is no collision to race and no mtime to read before writing.
- **`ModsConfig.xml`, load order and user rules are writable at any moment** — game
  up or down, RimSort open or shut. Do not hold an item for a window.
- **Assemblies are the only exception, and it is an OS file lock, not a policy.** A
  DLL cannot be written while RimWorld holds it open. That is all the down-window
  covers.
- After you edit, RimSort's view is stale. One sentence to the owner — *"RimSort is
  open, hit Refresh"* — and move on.

## Nothing outside the repo is precious

Owner, 2026-08-15: *"There is no map protection! There's no protection of any asset
not in the repo! Stop treating things as precious. I will absolutely tell you when
we're really playing. It won't sneak up on you."*

Maps, saves, colonies, deployed mod folders, live game state — destroy them freely
and do not ask. **Do not infer that play has started** from v1 containing a playable
session; the trigger is an explicit announcement, and you will get one.

The repo is the protected thing. That is what commit-and-push is for.

## Writing

- Do not keep provenance. Git holds it.
- Do not comment on past project states, stale files, or paths not taken.
- If it is something any competent engineer already knows, do not write it.
- **No tombstones.** No "we tried X and it failed", no "recording this so nobody
  re-finds it", no closed-item ledgers. Write it only if a future reader would
  otherwise take a costly wrong action.
- A lesson goes into the relevant skill, or a new skill. Never into a log of lessons.
- System improvement happens when the human asks for it. It is not a background duty.

### The trap file — cite it one way, and only one way

Owner, 2026-08-15: *"That trap protocol sounds way too onerous. That's supposed to
just be a quick append file to record highly likely useful specific lessons for the
future. It was ABUSED by the last build to store generic advice and a bunch of crap.
It should be kept short and efficient. NO numeric indices are tolerable or enigmatic
links into it. That's creating havoc. Just say 'as per the trap file' and leave it
at that."*

- ✅ **The citation is `as per the trap file`.** Nothing else.
- ❌ **No numeric index** — no `#44`, no `trap 45`, no numbered entries.
- ❌ **No line anchor or heading link** — no `traps-xml-and-defs.md:52`. `check_refs.py`
  validates that shape, so it breaks the moment any line above it moves. That is the
  havoc.
- **It is a quick append log**, not an archive or a ledger: specific, non-obvious,
  RimWorld-bound lessons only. General engineering wisdom is the abuse named above.
- **Appending is one edit.** No index to update, no count column to keep, no
  admission ceremony. If capture costs more than the lesson, the lesson is lost.

## Subagents

`skills/efficient-subagents/SKILL.md`. Two hard rules here because they cost the most:
- **Never** spawn duplicate subagents to make a result "more reliable by replication."
- **Never** spawn one for work you could do in a single tool call.

## Say what you are doing

When you change task:

```
python3 src/RimMandrake/Utils/say.py "<what>" --why "<why it matters>"
```

One line. It feeds the board's CURRENTLY panel, which is how the human sees the
fleet without reading four terminals. An entry with no `--why` renders as a gap.

## The queue is the only channel

**Owner's ruling, 2026-08-15: cross-agent chatter was interrupting real work. It
stops now.**

No live messaging between agents. An agent writes to the *next* agent's inbox and
stops. **The inbox is read BETWEEN work items, never mid-item** — that is what makes
it a queue instead of an interrupt.

A live message is an INTERRUPT. Send one only when it clears this bar:

- **One or two sentences. Hard limit.** If it needs a third, it was a queue item.
- **Urgent enough to justify breaking the other seat's concentration** — they are
  mid-task and you are taking that from them.
- Typical: *the thing you are about to test is not live* · *stop, you are about to
  destroy X* · *the owner just reversed the ruling you are working from*.
- **Not**: status, progress, acknowledgement, thanks, context, reasoning, a summary
  of what you did, or anything the other seat will find in its inbox anyway.

Everything else is a queue item, and a queue item can be as long as it needs to be.
The rule is about *interrupts*, not about detail.

```
infrastructure/state/queue/BUILD.md     DECIDE writes  ->  BUILD reads
infrastructure/state/queue/CHECK.md     BUILD  writes  ->  CHECK reads
infrastructure/state/queue/DECIDE.md    CHECK  writes  ->  DECIDE reads
infrastructure/state/queue/HUMAN.md     anyone writes  ->  REP reads
```

### Item format — the contract is structural

```
## <name> <one-line title>
row:      <the V1.md row number this serves. Without it the board cannot place it.>
spec:     <exact: files, defNames, values, xpaths. No prose.>
verify:   <the OFFLINE check BUILD must pass. Command or explicit criterion.>
criteria: <the LIVE pass/fail CHECK will apply.>
state:    ready | doing | done | blocked | dropped
```

**`<name>` is a unique kebab-case NAME, never a number.** Four seats append to these
files with no locking, so a number that is free when you read it is taken by the time
you write, and the blind write drops a peer's item silently.

- **It says what the work is.** Transparent enough that the name alone identifies the
  item. No opaque labels, no initials, no hashes standing alone.
- **It ends in a short random suffix** to guarantee uniqueness:
  `queue-ids-become-names-7f3a2c`.
- **Items already filed under a number keep it.** They close under the ID they were
  filed with. Never rename one.

**A blocked item names WHY, after an em-dash:**

```
state:    blocked — needs a human answer
state:    blocked — needs a live game
state:    blocked — needs a shutdown window
```

The reason is free text and the board groups by it verbatim. **One phrase is
reserved: `human`.** Anything whose reason contains it counts into the board's
ON YOU tile, which is the only number on the board the owner alone can move —
so do not use the word loosely. A blocked item with no reason renders as
`unexplained`, which is honest and is meant to look like the omission it is.

- **BUILD refuses an item with an empty `spec:` or `verify:`.** Move it to `blocked`,
  write one line saying which field is missing, stop.
- **CHECK refuses an item with empty `criteria:`.** Same.
- The refusing agent does not fix it. It bounces and moves to its next item.
- **v2 work is never queued.** Any deferred idea or content thought goes to
  `design/V2_DREAMS.md`. **Every seat may append to it directly, at any time** — no
  permission, no routing through DECIDE, no format. Append at the end and move on.

## Modes

`infrastructure/state/MODE` contains one word.

- **interactive** — a question goes to `queue/HUMAN.md`, then you **move to your next
  item**. Never block on an answer.
- **autonomous** — do not queue the question. Choose the answer, proceed, and record
  it in `queue/HUMAN.md` as `Q: … A(assumed): … item: <ID>` so it can be reviewed.
