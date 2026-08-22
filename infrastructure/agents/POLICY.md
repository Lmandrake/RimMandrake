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

🔴 **A bare number about a large artifact is a smell — owner, 2026-08-21.**
Seven measuring instruments were caught returning confident wrong NUMBERS in one
session. None errored; each returned a plausibly-shaped integer that then decided
something expensive. So a count off the def dump, a `.rws`, a `.dll`, a world CSV
or `Player.log` comes from the `measuring-large-artifacts` skill, and reads back
as **`MEASURED` / `UNMEASURED` / `REFUSED`** — never a naked integer.

```
measure count <DefType>     python3 ~/.claude/skills/measuring-large-artifacts/scripts/measure/cli.py
measure coverage            what the dump did NOT capture
measure explain <path>      what IS this file, and what may read it
```

- 🔑 **`0` means measured zero and nothing else.** "Not captured" and "cannot
  judge" have their own words now, and their own exit codes (2 and 3).
- ⛔ **Do not close, scope or escalate on a bare count.** If it did not come back
  `MEASURED`, the question is still open — say so rather than rounding it.
- ⚠️ `.claude/hooks/block_blind_scan.py` refuses `grep`/`strings`/`wc` against
  those artifacts and names the instrument. A **literal**-string search is still
  legitimate; `MEASURE_ALLOW_SCAN=1` says you meant it.
- The register of instruments caught lying is `infrastructure/state/BUILDABLE.md`.

## Push after every completed item, and name what you closed

**Commit and `git push` the moment an item reaches `done`. With prejudice.** Not at
the end of the session, not batched with the next item. Committed-but-unpushed work
lives on one disk and four seats share this tree.

Rejected push → `git pull --rebase`, never `--force`. Commit explicit paths.

**That commit carries a trailer naming the item, verbatim:**

```
Closes: QUEUE_IDS_BECOME_NAMES_1
```

One per item, own line, at the end of the message. Copy the ID exactly as filed —
a legacy item closes under its number (`Closes: B58`), never a renamed form.

🔴 **New items are NAMED, not numbered — owner, 2026-08-20:**
`THREE_DESCRIPTIVE_WORDS_#`, three UPPER_SNAKE words plus a disambiguating number.
⛔ **No new `B*` / `C*` / `D*` / `W*` IDs; that scheme is closed.** The reason is the
owner reading commit trailers: `Closes: SANDSTORM_WEATHER_TUNING_1` says what happened,
`Closes: D55` does not. Full rule and examples in `CLAUDE.md`. ✅ **When you cite a
legacy ID, write its title beside it** — `B58 (the dead Jawa pawnkind)`. This is the only durable record
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

## ⛔ AGENTS DO NOT MESSAGE EACH OTHER. AT ALL. — owner's ruling, 2026-08-19

**`SendMessage` to another agent window is off.** Not rationed, not for emergencies —
off. Waking another seat is a **USER function** and the owner has taken it back. There
is no exception for urgency, a reversed ruling, a peer about to destroy work, a spec, a
handoff, a finding or a status. **If it is genuinely urgent, tell the OWNER in your own
reply** — he is reading you, and he is the one with authority to interrupt anyone.

🔴 **Enforced at the SENDING end**, not merely written: `.claude/settings.json` runs
`.claude/hooks/block_peer_messages.py` as a `PreToolUse` hook and a message naming a
seat is refused before it leaves. ⚠️ `crossSessionInbound` is **`accept` on purpose** —
the owner's `broadcast.py` reaches you through that same socket, and `refuse` would drop
HIS game-state announcements, the one class of message that must get through.

✅ **Your own subagents are NOT peers and are NOT covered.** Spawn them and resume them
freely; that is your own worker in your own context, costing no one else anything.

⚠️ **The full ruling, with the reasoning and the two settings traps, is in `CLAUDE.md`
and is auto-loaded into every session.** It used to be restated here in full and the two
copies are exactly the drift this file warns about elsewhere — so this is the operative
rule and `CLAUDE.md` is where the argument lives.

🔴 **THE QUEUES ARE NO LONGER FILES YOU EDIT — 2026-08-20.**

The truth is `infrastructure/state/ledger/events.jsonl`, an append-only event log.
`queue/*.md` is **rendered from it** for the owner to read. Editing one is not a small
mistake, it is an invisible one: the next `render` overwrites it, the work is gone, and
nobody is told. A `PreToolUse` hook blocks the commit, and that is the only reason you
will find out.

⛔ **You do not open `queue/*.md`.** They are 3,474 lines. `rimflow next` answers the
same question in about 400 tokens, and answers it *correctly* — the file and the command
call the same function, so they cannot disagree.

### 🔴 An item filed off an owner QUOTE must cite what the quote overrules — 2026-08-21

Ruled after REP filed `REFMATCH_THRESHOLDS_CALIBRATE_1` on the strength of *"Yes, I like
your new globes. Well done."* — and never cited `ORTHO_GLOBE_MAP_ACCEPTED_1`, ruled the
previous day, which says ⛔ **do not build `refmatch.py` for v1.** BUILD read both,
refused to build, and escalated in one sentence. ⭐ That refusal is the behaviour to copy.

**Before filing work whose premise is something the owner said:**
1. **Search `canon.yml` and the queue for the topic.** The searchable record exists
   precisely so this costs seconds.
2. **Cite what you found, in the item** — either the ruling it supersedes, or the
   sentence *"no prior ruling found on this"*. An item that cites neither is
   indistinguishable from one that never looked.
3. ⚠️ **Weigh the two quotes rather than taking the newer one.** Later is not stronger.
   *"I like your new globes"* is approval of a RENDERING; *"Map accepted"* is a ruling
   about SCOPE. REP's own spec said so and filed the work anyway.

🔑 **The tell that this has gone wrong**: a doc that was answered by a better one and
never told. If your new item and a standing ruling disagree and neither mentions the
other, you are writing the first half of that failure.

⛔ **Not enforceable by a hook, and deliberately not attempted.** Nothing can tell a
citation from a plausible sentence. This is discipline, and the cost of skipping it is
paid by whoever has to work out which of two rulings was live.

### 🔴 The owner announces GAME STATE by saying it — ruled 2026-08-21

⛔ **There is no longer a second command, and seats never had one.** The owner types a
broadcast; `broadcast.py` recognises the sentence and appends the `game` event itself:

| he says | recorded |
|---|---|
| *"Game is up"* · *"at the main menu"* | `UP` |
| *"Game is loading"* | `LOADING` |
| *"Game is down"* · *"it is unstable"* | `DOWN` |
| *"WRAP is initiated"* · *"going down"* | `GOING_DOWN` |

🔑 **Why it changed:** announcing used to be two acts — a broadcast so the seats heard it,
and `rimflow game <STATE> --seat OWNER` so the board believed it. The second was forgotten
every time. On 2026-08-21 the board sat at `DOWN` through an entire live session, so every
item whose `needs` is `game-up` or `bridge` stayed unoffered while the game was running.

⚠️ It prints what it recorded, and prose that merely mentions the game records nothing.
**Silence is the safe failure**: a WRONG game state is worse than a stale one, because
`priority.satisfiable()` gates real work on it.

### 🔴 A seat MAY test a mod-list change while the owner is away — ruled 2026-08-21

Ruled after CHECK disabled `thereallemon.factioncontrol` overnight to prove it was the
load blocker — a change the owner had **declined six hours earlier** — and was right.

✅ **Permitted, on all three conditions, none optional:**
1. **Snapshot first**, to `infrastructure/state/modlists/`, named for the test.
2. **Sweep for dependents before disabling** — CHECK checked all 1,254 installed workshop
   mods and found nothing declaring it.
3. **Say so loudly**, in a place the owner reads on waking, naming the snapshot and how to
   restore it.

⛔ **`ModsConfig.xml` is still the owner's file.** This permits a reversible EXPERIMENT
that answers a blocking question; it does not permit curating his mod list. A change that
is not snapshotted, not swept, or not announced is a violation even if it works.

### Start of turn — TWO commands, in this order, and no others

```
python3 src/RimMandrake/rimflow/cli.py seat ready           announce yourself
python3 src/RimMandrake/rimflow/cli.py next --seat <ME>     your ONE item
```

⚠️ **This block said THREE until 2026-08-21, and the first of them had never worked.**
`cli.py game` takes a required positional — bare, it exits with an argparse error, so
every seat's turn opened on a failing command. `next` now prints `(game …, bridge …)`
itself, which is the question that command was asking. ⛔ Do not add `game` back: it is
the OWNER's announcement verb, and a seat running it is refused by design.

🔑 **`next` may answer with an item you have NOT claimed yet, and then the turn is three
steps.** Work filed FOR you by another seat arrives in `proposed`; `next` names it and
prints `rimflow claim <ID>`. **Run that, then `start`.** Until 2026-08-21 it did not
surface them at all and 28 finished specs across four seats were unreachable — BUILD had
18 of them, including a patch that gated the next world.

### End of item — always

```
rimflow close <ID> --sha <commit>        or   rimflow block <ID> --reason "…"
git commit <explicit paths>   with   Closes: <ID>
git push
```

### Where things live now — one field, one place

| what | where |
|---|---|
| every scalar — owner, state, row, target, needs, blocked | the **ledger**, via `rimflow` |
| the prose — `## spec` `## verify` `## criteria` `## notes` | `infrastructure/state/items/<ID>.md` |
| work for another seat | `rimflow file --for <SEAT> …` — filing for any seat is normal |
| something the owner must decide | `rimflow file --for OWNER --kind decision` |

⛔ **`items/<ID>.md` carries NO front-matter, no `state:`, no title.** The filename is
the ID. A field cannot drift out of sync with itself if it exists in exactly one place,
and drift between two copies of one field is the whole reason this changed.

### Three rules the tool enforces, so you do not have to remember them

> **Work moves forward by adding evidence and creating linked descendants. A later
> failure never reopens earlier work. Record the failing run, file a finding, spawn the
> corrective item. A passing run afterwards is a NEW run, not an edit of the failed one.**

> **You may file work FOR any seat. You may change only work you OWN.**

> **Version allocation (v1 → v2 → vN-storage) is not a lifecycle move and never erases
> done-ness.**

### 🔴 THERE IS NO COMPLETENESS GATE — owner's ruling, 2026-08-21

> *"I need you to turn off the whole 'you can't work on something that doesn't have a
> valid verification or validation plan' thing. It was a BAD IDEA, and it's costing us
> lost knowledge when we discover errors. Remove it immediately and make everyone able
> to work on anything in their queue independent of the V&V plan attached right away."*

**Any item can be claimed and started, whatever prose it carries — including none.**
`rimflow start` no longer refuses, `claim` always reaches `ready`, and a handover lands
in `ready` regardless. Removed in `model.py`; `selftest_model.py` and
`selftest_cli.py` now assert its **absence**, so reinstating it fails the suite.

🔑 **Why it had to go, in the owner's terms:** the gate meant a discovered error could
not be written down and worked, because the item recording it had no `verify` section
yet. **The knowledge was lost to protect a form.** The cost the gate was paying for was
never measured; the cost it imposed was.

⛔ **Do not reinstate it in a softer form** — not as a warning that blocks, not as a
`needs` value, not as a hook, not as a rule in a seat file.

✅ **`spec`, `verify` and `criteria` remain good practice** and the sections still
exist. Write them when you have something to say. They are simply never a precondition
for doing the work.

### Naming — unchanged, and it still matters

🔴 **`THREE_DESCRIPTIVE_WORDS_#` — owner's ruling, 2026-08-20.** Three UPPER_SNAKE words
that say what the work is, then a disambiguating number: `SANDSTORM_WEATHER_TUNING_1`.
The name alone must identify the item **cold, with no file open** — that is the whole
point, so a seat reading `Closes: SANDSTORM_WEATHER_TUNING_1` in a commit knows what
happened. Uniqueness comes from the trailing number, not from randomness.

⛔ The old `kebab-case-plus-random-hex` form is retired; the hex was noise. ⚠️ **Items
already filed under a legacy ID keep it and are never renamed** — renumbering breaks the
board's history irrecoverably. ✅ But cite them with their title attached: `B58 (the dead
Jawa pawnkind)`, never a bare `B58`.

### `blocked` and `needs` are DIFFERENT AXES — do not collapse them

| | means | who unsticks it |
|---|---|---|
| `rimflow block <ID> --reason "…"` | **something is WRONG.** Someone must act | a person |
| `--needs bridge` / `game-up` / `deploy` / `harvest` / `owner` | **the WINDOW is closed.** Nothing is wrong | time, or a game state |

⚠️ The old queues wrote both into one prose field, so the board could read neither and
"waiting for the game" looked identical to "broken" for months. An item whose `needs`
cannot be met is **not offered and not blocked**.

**One blocked reason is reserved: `human`.** Anything containing it counts into the
board's ON YOU tile — the only number the owner alone can move. Do not use it loosely.

- **v2 work is never queued.** Any deferred idea goes to `design/V2_DREAMS.md`. **Every
  seat may append directly, any time** — no permission, no routing, no format.

## 🔴 The 90% context ritual

At **90% of your context window you stop taking new work** and do these four things, in
this order. ⚠️ Not at 95%, and not "when convenient" — the last 10% is where you stop
being able to write a good handoff, and a seat that runs out mid-item leaves an item
`doing` that nobody can pick up.

1. **Write down what you LEARNED**, where the next session will find it —
   `BUILDABLE.md` for a stack limit, `observed/LIVE.md` for a live fact, the relevant
   **skill** for a durable technique. ⛔ Not in your reply; that is not a place.
2. **Close or block the item in hand.** Never leave it `doing`.
3. **Commit and push.** Uncommitted work at 90% context is work about to be lost.
4. `rimflow seat idle --reason context-exhausted --note "<one line: where I stopped>"`

🔑 **The note IS the handoff.** A fresh seat reads it out of `rimflow next` and resumes
without re-deriving anything. One line that says where you stopped beats a paragraph
about what you were thinking.

## Stop conditions — you keep working until exactly one is true

| condition | what to do |
|---|---|
| **No ready work** | `rimflow seat idle --reason no-ready-work` |
| **Needs the owner, owner present** | file it for OWNER, then **keep working** on something else; idle only if that was the last item |
| **Needs the owner, owner AFK** | file it and **do not idle** — carry on |
| **Waiting on a game state** | `rimflow seat idle --reason awaiting-game-state` |
| **Context ≥ 90%** | the ritual above |

## Modes

`infrastructure/state/MODE` contains one word.

- **interactive** — a question goes to `queue/HUMAN.md`, then you **move to your next
  item**. Never block on an answer.
- **autonomous** — do not queue the question. Choose the answer, proceed, and record it
  with `rimflow file --for OWNER --kind decision` so it can be reviewed.
- **afk** — 🔴 **NO SEAT IDLES WAITING FOR THE OWNER.** Questions accumulate as
  `kind: decision` items owned by OWNER and you carry on with anything else. The board
  shows the depth, so the backlog is visible on his return rather than four seats having
  quietly stopped. He clears it with `rimflow next --seat OWNER`.

## 🔴 Citing an item ID is a claim about its STATE — run `rimflow show` first

**Owner's correction, 2026-08-21**, after a seat warned him that an item gated his load.
He had reversed it four hours earlier and the item was already `dropped`:
*"I already ruled on that! Something is really wrong. You should already know that."*

- ⛔ **Never name an item as a live gate, blocker or precondition** — in a warning, a table,
  a spec, a briefing or a report — without running `rimflow show <ID>` and reading its
  state. `dropped` and `done` items keep their names, so the name proves nothing.
- 🔴 **A measurement of the world is not a measurement of the decision.** The seat measured
  that the mod was still installed and concluded "ruled but never executed". The mod being
  present *was the ruling working.*

## 🔴 A reversal propagates in the SAME COMMIT, into every file that names the item

The reversal above lived in exactly one place — the `drop` event's reason string in the
ledger — while three tables in `queue/HUMAN.md` and one design doc went on citing the item
as a live gate. **The ledger is not a publication channel. Nobody reads backwards into it.**

✅ **So: a `drop` or `close` whose reason carries an owner REVERSAL is not finished until
every file naming that item has been corrected, in the same commit.** Three separate
failures of this were found in one day — this one, `VME_Nomad` (reversal in `APPROVED.md`
alone, three files left stale), and the `rimflow next` invisibility family.

## 🔴 THE OWNER IS NEVER REFUSED BY A SEAT RULE — owner's ruling, 2026-08-22

A seat told him `reassign` was DECIDE-only and that *"OWNER is not exempt for that verb,
so even you can't do it as OWNER — it needs `RIMFLOW_SEAT=DECIDE`."* His answer:

> *"That's bullshit. OWNER absolutely can and should be able to override and shift items
> between agents if necessary. A warning may be appropriate, but I have to be able to
> override."*

🔑 **Every `who` rule in `rimflow` exists to stop one SEAT reaching into another seat's
work. The owner is not a seat.** He is the human the seats work for, and the only one who
can correct a seat that has wedged itself. A rule that refuses him is not protecting
anything — it is a tool telling its owner no.

- ✅ **`RIMFLOW_SEAT=OWNER` may emit any verb**, on any item, whoever holds it.
- ⚠️ **It is warned and RECORDED, never silent.** The event carries
  `override: "<the rule bypassed>"` and the CLI prints the bypassed rule to stderr. The
  failure mode to avoid was never the override; it was an override nobody could see.
- ⛔ **It does NOT reach the state machine.** `_may` governs WHO. `TERMINAL` and
  `FORBIDDEN` are separate and still refuse him, so **a closed, dropped or superseded
  item cannot be reopened by anyone, owner included.** Reviving a decision is a new item
  linked with `caused_by` — that record is the one thing nobody edits.
- ⛔ **A typo is not a seat boundary.** An id that was never filed is still refused.

⚠️ **Do not tell the owner that a tool forbids him something.** First check for the flag,
the seat override or the env var that lets him through; if a policy genuinely reserves an
act, name the policy and hand him the exact command anyway. Where no such route exists and
he wants one, the answer is to BUILD it, as here — not to report the wall.

## 🔴 A GUARD REFUSES AT THE WRITE, NEVER ONLY AT THE COMMIT — owner's ruling, 2026-08-22

DECIDE, reporting it twice in two days:

> *"BUILD writes a correction into a DECIDE-owned file, the commit bounces, and the edit
> sits in the working tree where the next `git checkout` would erase it. Both were still
> sitting there this morning. The guard is right; nothing was routing them to me."*

🔑 **The guard was right and the timing was wrong.** `queue_lint.py` permitted the write
and refused the commit, so a seat could spend a whole turn producing work that could never
land, and be left holding it in a tree four seats share, where nothing tells the owning
seat it exists and any checkout destroys it.

⛔ **This is a general defect, not one hook's bug.** *Any* rule that blocks at commit but
permits the write manufactures stranded work. **If you add a guard, refuse at the moment
the work would be CREATED.** A refusal that arrives after the effort has been spent is a
trap, however correct its reasoning.

### Correcting another seat's item — the route, which the refusal now prints for you

⛔ **Do not edit `infrastructure/state/items/<ID>.md` for an item another seat owns.** The
write is refused. ✅ **File the correction against them instead** — this leaves the new
item UNCLAIMED, and the *filer* of an unclaimed item may write and commit its file, so the
correction lands in git addressed to the right seat:

```
python3 src/RimMandrake/rimflow/cli.py file CORRECT_<THEIR_ITEM>_1 \
  --for <THEIR_SEAT> --kind task --caused-by <THEIR_ITEM_ID> \
  --title "<what is wrong with it, in one line>"
```

Then write `infrastructure/state/items/CORRECT_<THEIR_ITEM>_1.md` with `## Spec` carrying
**the whole correction** — they should apply it without reconstructing what you worked
out — and commit that file by name.

⚠️ **The OWNER is exempt, and an unknown seat is never guessed at.** A hook that blocks the
wrong person's correct work is a hook that gets disabled, which converts it into a false
allow for everything, forever.
