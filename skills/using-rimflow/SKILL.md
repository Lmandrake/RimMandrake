---
name: using-rimflow
description: "Use before ANY rimflow / src/RimMandrake/rimflow/cli.py call — file, claim, start, close, drop, supersede, note, next, seat, sweep, bridge take/release/who — and before passing --owner-said, committing a ledger shard (infrastructure/state/ledger/events/<SEAT>.jsonl), or reading the ledger or queue/*.md projections. Covers the sharded ledger layout, exact verb syntax from --help, the close --sha literal-string and silent-HEAD-fallback traps, --owner-said provenance (typed vs clicked), --seat on the Mac laptop, ledger commits being local-only, merge-order projection, and the bridge lock."
---

# Using rimflow

## What rimflow is

rimflow is one master queue derived from an append-only ledger. 🔴 **The ledger
is SEVERAL files since 2026-09-23** (`EVENTS_JSONL_SHARDING_1`, landed
`2b5947555`): `infrastructure/state/ledger/events.jsonl` is frozen history that
nothing appends to any more, and every `file`/`claim`/`close`/etc. call appends
to the calling seat's own shard, `infrastructure/state/ledger/events/<SEAT>.jsonl`
— so two seats can never rebase-conflict in one git-tracked file. `model.read()`
with no path merges history + every shard; `model.read(model.EVENTS)` reads the
frozen history alone and is almost never what you want. No other file is the
source of truth. Item prose (spec, context, decisions) lives separately in
`infrastructure/state/items/<ID>.md` while the item is open; on close/drop/
supersede its prose file moves to `infrastructure/state/items/closed/`. IDs
are `THREE_UPPER_SNAKE_WORDS_#`, guessable cold — never a number. `rimflow
next --seat <SEAT>` is the one command you need to start work; everything
else (`show`, `why`, `render`, `reindex`) derives a view from the same ledger.

## Verbs

Every verb takes the global flags `--seat`, `--target`, `--mode`,
`--owner-said`. Syntax below is exact, from `--help` — check `--help` again
before relying on flags not listed here; the CLI has more verbs
(`block`/`unblock`/`finding`/`spawn`/`needs`/`retarget`/`reassign`/`reclaim`/
`lint`/`artifact`/`render`/`reindex`/`game`/`capability`) not covered by this
skill.

```
rimflow file <ID> --for FOR --title TITLE [--kind K] [--row N]
             [--target-field v1|v2] [--needs offline|deploy|game-up|bridge|harvest|owner]
             [--spec PATH] [--caused-by ID] [--replaces ID]
             create work for ANY seat, including another's.
             --replaces ID supersedes ID in the same act (parent closes, names successor).

rimflow claim <ID>          take ownership; always reaches `ready`
rimflow start <ID>          begin work; never refused for missing prose

rimflow close <ID> [--sha SHA] [--reason REASON]
             close against a commit, any seat; --reason required in practice
             when the item is another seat's (see close --sha rules below)

rimflow drop <ID> --reason REASON        this will not be done (reason required)
rimflow supersede <ID> --by ID [--reason REASON]   a better item replaces it

rimflow note <ID> --text TEXT            a line of context; prose belongs in items/<ID>.md

rimflow show <ID>           everything the ledger says about one item
rimflow next [--bench]      the one item to work now; --bench is the board-triage view

rimflow verify <ID> --result pass|fail|partial --config CONFIG
             [--evidence PATH] [--sha SHA]
             record a RUN. Immutable — a fail stands forever.

rimflow seat {ready,busy,idle} [--reason R] [--item ID] [--note NOTE]
             announce what this seat is doing; --note is what a handoff reads

rimflow bridge {take,release,who,give} [to] [--for PURPOSE] [--force]
             `who` only reads/repairs the mirror; `take`/`release`/`give` write the
             ledger. --force takes it from an awake other window (recorded).

rimflow sweep [--transient]    lists stale TRANSIENT_* files. LISTS ONLY, no ledger write.
```

## Item hygiene

🔴 **An item filed alongside a finished analysis must cite the report path.**
Two items carried specs but no pointer to the prior window's `Transient/`
report, so the next window re-ran both analyses blind.

⚠️ **An item's "NEXT:" note can be DISCHARGED by a later item** — acting on a
note without checking cost a whole redundant review sheet once, when a later
item filed the same day recorded that the noted work had already been served
and ruled. Before acting on any note, list items filed AFTER it that name the
same subject: `ls -t infrastructure/state/items/` is enough.

🔴 **`infrastructure/state/MODE` has no CLI setter — it is a plain file
`cli.py` only reads, and it can go stale.** A FOUNDRY window once read `afk`
from a prior session while the owner was live saying "go go go"; `rimflow why`
silently suppressed a fully-specified `needs=owner` item under that stale
mode with no warning that mode gating was the reason. If the owner is
actively present but items keep reading "needs owner, afk suppressed", check
this file before assuming the item is genuinely blocked.

🔴 **`rimflow unblock` refuses another seat's in-flight item, and names the
right move itself:** correct the false prose in their item file, commit by
explicit path, and use `note` to nudge. Do not force the state.

⚠️ **A gate citing an item by name should be treated as suspect the moment
that item's own state changes, not just after weeks.** `rimflow lint
--citations`' STALE_GATE sweep has found items describing another item as
"still open/blocked" that closed the SAME calendar day, one within the same
session that closed it — a doc can go stale within hours, not just weeks.

⚠️ **`.claude/hooks/block_forged_owner_said.py` can false-positive on prose
that merely MENTIONS the flag** — its regex takes a bare token after
`--owner-said`/`--said`, so a commit message or test harness discussing the
flag by name gets refused with a forgery message. Assemble the flag from
pieces in test code, and avoid the literal spelling followed by a word in
commit messages. Erring toward refusal is the safe direction here, so treat
this as friction, not a defect to work around by weakening the hook.

## `close --sha` rules

`--sha` defaults to `git HEAD` but does **not validate** what you pass it —
three distinct traps, all live-caught:

- **A literal `"HEAD"` string is written verbatim**, not resolved to a hash.
  Tooling that diffs "commits since" against `sha` breaks silently on it.
- **Any made-up string is accepted unvalidated** — an item was closed against
  the literal `"c1"` (a packet's short name typed by mistake) with no error.
- **A `--sha` that fails to parse (bad quoting, wrong flag position) silently
  falls back to `git rev-parse HEAD` AT CALL TIME**, not to a resolved value
  from earlier — in a shared worktree that can be a concurrent peer's commit
  that landed in the gap between your fix's commit and the close call.

Rule: **commit the fix first**, then close with the real hash from *after*
that commit — `--sha $(git rev-parse --short HEAD)` as a live command
substitution, never a hand-typed or pre-computed string. Closing against a
pre-fix HEAD (closing before committing) leaves a real but misleading sha on
the event just as surely as a typo does.

## `--owner-said` provenance

`--owner-said` stamps the event as acting AS OWNER (`seat: OWNER`) and records
the quote as the authorization on the ledger. rimflow itself only checks
*shape* (refuses a bare question, refuses bare assent) — it cannot tell
whether the owner actually said it. `.claude/hooks/block_forged_owner_said.py`
adds the real check, against the session transcript:

- **What he TYPES counts** — a chat turn he actually typed (`promptSource:
  "typed"`), or free text he typed into a question card's notes box / a
  free-text "Other" answer. Pass his words VERBATIM; never paraphrase, never
  invent.
- **An option LABEL he merely clicked does NOT count** — the assistant wrote
  that label, so quoting it back as his words launders your own sentence into
  his authorization. Record a card selection instead as **"decision taken by
  question card"**, with no `--owner-said` flag, and say so in the item prose.
- **Split an imperative from a question.** The guard correctly refuses a
  quote containing a question — "the owner asking about a thing is not the
  owner authorizing it." Quote only the imperative clause of his message.
- **Only the current session's transcript is read.** A true quote from an
  earlier session is refused — have him repeat it this session rather than
  reusing an old one.
- **A message that arrives MID-TURN is refused too** — one he typed while a
  tool was running reaches you inside the turn, and the guard does not find it
  in the transcript. Record it under your seat (`--seat BENCH`) with his words
  quoted in full in `--text`, naming it as his typed ruling.
- **`note --owner-said` stamps the WHOLE event as OWNER-authored**, not a
  disclaiming free-text field. Only use it when actually relaying an owner
  ruling; use bare `note` for your own investigation writeups.
- **A commit message that explains a refusal must paraphrase, not quote,
  itself** — the guard also inspects commit bodies. It is a `PreToolUse`
  hook, so it refuses the **whole compound command**: a chained
  write-then-commit loses the write too when the commit half is what trips it.

**If the guard refuses a genuine quote because it arrived mid-tool-call or as
an interjection (invisible to the transcript check), take its prescribed
exit without arguing: drop the `--owner-said` flag, act under your own seat,
and name whose call it is in `--reason`.** Never put the flag name itself
inside a `--reason` string — the regex takes the next bare token as a value
and refuses on that too.

## Seat identity

`--seat` is beaten by `RIMFLOW_SEAT` and refused if unresolvable. On the Mac
laptop neither rimflow nor `handoff.py` can derive the seat at all — no seat
profile, `CLAUDE_CODE_SESSION_ID` unset, and `set_agent_window.sh` only does
the window half — so every ledger call there needs an **explicit `--seat`**,
or a whole sitting's ledger trail lands mis-seated. Also: subcommand targets
take `--to` (e.g. `reassign --to FOUNDRY`, `needs --to bridge`); bare
positionals for a target are refused.

## Committing ledger writes

rimflow writes this seat's shard, `infrastructure/state/ledger/events/<SEAT>.jsonl`,
to disk immediately on every `claim`/`start`/`close`/`note`/etc. call — but it
has **no git integration at all**. Committing it is entirely on the calling seat, and it
is easy to miss: CLAUDE.md's "explicit paths, never `git add -A`" means a
commit that stages only the specific code/content files a fix touched will
never pick up the ledger delta as a side effect. A full session's queue
history can sit uncommitted — already-lost territory if the machine goes
down — until caught by accident.

Commit your seat's shard `infrastructure/state/ledger/events/<SEAT>.jsonl` (plus the rendered
`infrastructure/state/queue/*.md` projections) by **explicit path**, with
each close or at least once per work wave — not only at session end. Prefer
a dedicated "ledger sync" commit over folding it silently into a code
commit's file list; it keeps the code commit's message focused and makes the
ledger's own commit history legible.

🔴 **A torn/invalid line in ANY ledger file breaks `rimflow`/`./game` entirely
for every seat** — a torn line has no admin-event fix, because rimflow can't
finish reading the file to append one. This has happened from a botched `git
stash pop` landing unresolved conflict markers straight into the file. Since
the sharding a torn line is far likelier in a shard than in the frozen head.
`src/RimMandrake/Utils/repair_torn_ledger.py` is the fix: dry-run by default,
`--apply --owner-said "…"` to write, and `--seat <SEAT>` to target that seat's
shard (a seat name, never a path); it removes only lines that fail to
parse, backs up to `Transient/` first, and sanity-caps at 25 bad lines.

## Reading projections

Every ledger file is append-only and its own append order IS the truth for the
events inside it. **Never re-sort on `(ts, event)`** — same-second `start`+`close`
pairs get their alphabetical tiebreak inverted by an `event`-name sort, which
once turned 61 real "doing" items into a reported 102. Across files, the merged
order is `(ts, source rank, within-file order)` with the frozen history ranked
ahead of the shards — `model.read()` with no path implements it; if you are
deriving your own view of the ledger (rather than reading `rimflow show`/`next`/
the rendered `queue/*.md`), call that rather than merging by hand.

## Bridge lock

`rimflow bridge` decides who drives the live game — not for ownership, for
attributability. `take --for "<what for>"` says what you're driving it for so
the other window can judge whether to wait; `release` the moment you stop
driving, not at session end. It errs toward **allowing, never toward mutual
lockout**: a `take` is refused only while the holder is provably alive — an
event within the last 45 minutes; after that the lock is stale (event
silence, not game activity — the game can sit idle for hours while the
holder is still working) and the next window simply takes it, saying so.
`--force` always works and is recorded. Nobody announces a release across
windows — that channel is off — so if you want the bridge, check `bridge
who` again rather than waiting to be told.
