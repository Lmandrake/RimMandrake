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

**That commit carries a trailer naming the item:**

```
Closes: B12
```

One per item, own line, at the end of the message. This is the only durable record
that the work happened — the item itself is about to leave the queue, and
`derive_matrix.py` reads the trailer back out of git to count progress. No trailer
means the board never learns, and 70 items have already been lost that way.

**An item leaves a queue exactly two ways: closed with a trailer, or `state:
dropped` with one line saying why.** Deleting it, renumbering it away, or quietly
retitling it into something else breaks the count and cannot be recovered later.

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

No live messaging between agents. An agent writes to the *next* agent's inbox and
stops. REP may issue short orders; that is the only exception.

```
infrastructure/state/queue/BUILD.md     DECIDE writes  ->  BUILD reads
infrastructure/state/queue/CHECK.md     BUILD  writes  ->  CHECK reads
infrastructure/state/queue/DECIDE.md    CHECK  writes  ->  DECIDE reads
infrastructure/state/queue/HUMAN.md     anyone writes  ->  REP reads
```

### Item format — the contract is structural

```
## <ID> <one-line title>
row:      <the V1.md row number this serves. Without it the board cannot place it.>
spec:     <exact: files, defNames, values, xpaths. No prose.>
verify:   <the OFFLINE check BUILD must pass. Command or explicit criterion.>
criteria: <the LIVE pass/fail CHECK will apply.>
state:    ready | doing | done | blocked | dropped
```

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
