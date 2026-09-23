---
name: using-rimflow
description: "Use before ANY rimflow / src/RimMandrake/rimflow/cli.py call — file, claim, start, close, drop, supersede, note, next, seat, sweep, bridge take/release/who — and before passing --owner-said, committing infrastructure/state/ledger/events.jsonl, or reading events.jsonl/queue/*.md projections. Covers exact verb syntax from --help, the close --sha literal-string and silent-HEAD-fallback traps, --owner-said provenance (typed vs clicked), --seat on the Mac laptop, ledger commits being local-only, file-order projection, and the bridge lock."
---

# Using rimflow

## What rimflow is

rimflow is one master queue derived from an append-only ledger:
`infrastructure/state/ledger/events.jsonl`. Every `file`/`claim`/`close`/etc.
call appends an event there and nothing else — no other file is the source of
truth. Item prose (spec, context, decisions) lives separately in
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

rimflow writes `infrastructure/state/ledger/events.jsonl` to disk immediately
on every `claim`/`start`/`close`/`note`/etc. call — but it has **no git
integration at all**. Committing it is entirely on the calling seat, and it
is easy to miss: CLAUDE.md's "explicit paths, never `git add -A`" means a
commit that stages only the specific code/content files a fix touched will
never pick up the ledger delta as a side effect. A full session's queue
history can sit uncommitted — already-lost territory if the machine goes
down — until caught by accident.

Commit `infrastructure/state/ledger/events.jsonl` (plus the rendered
`infrastructure/state/queue/*.md` projections) by **explicit path**, with
each close or at least once per work wave — not only at session end. Prefer
a dedicated "ledger sync" commit over folding it silently into a code
commit's file list; it keeps the code commit's message focused and makes the
ledger's own commit history legible.

## Reading projections

`events.jsonl` is append-only and the append order IS the truth. **Project in
FILE ORDER, never by sorting on `(ts, event)`** — same-second `start`+`close`
pairs get their alphabetical tiebreak inverted by an `event`-name sort, which
once turned 61 real "doing" items into a reported 102. If you are deriving
your own view of the ledger (rather than reading `rimflow show`/`next`/the
rendered `queue/*.md`), preserve append order.

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
