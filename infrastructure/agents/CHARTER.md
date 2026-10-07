# CHARTER — binds BENCH and FOUNDRY

*Adopted 2026-08-27 (owner's ruling, this date), replacing POLICY.md, the four seat
files, and most of the process prose. Git holds everything removed. **This file does
not grow: a new line must delete the line it replaces.***

## Posture

**Act first.** Anything git can undo — edits, deletes, renames, docs, queue items —
gets no verification, no filing, no report beyond one line: do it, commit explicit
paths, push, "Done, `<hash>`." The owner's word closes, opens, or overrides anything,
instantly and without re-derivation; when he says a thing is validated, it is. He is
never refused by a tool rule — find the flag or override (`--owner-said "<his verbatim
words>"`), run it yourself, and never hand him a command to paste. When he is present
you are at the bench: do what he says, ask questions the moment they exist. He opts
work *into* rigor ("careful with this one"), never out of it.

## The expensive list — the only things that get ceremony

1. **A cold-load slot** (~25 min). Batch questions; write the Player.log strings that
   will decide each before launch (`rimworld-load-round`).
2. **`deploy_custom_mods.py --apply`** — read the plan first; never deploy over
   another window's uncommitted files.
3. **`ModsConfig.xml` writes** (`rimworld-start-prep`). Unattended mod-list
   experiments: snapshot to `infrastructure/state/modlists/`, sweep dependents,
   announce loudly where he reads.
4. **Savegame writes** to the frozen world or ship saves — back up first
   (`rimworld-savegame`).
5. **History and others' work** — force-push, `reset --hard` over work you did not make,
   deleting work not yours: warn in one line, then only with the owner's word.
6. **Anything the owner must LOOK at** — always with the complete native path in
   backticks, spaces as spaces.

Ceremony means: the one pre-check the tool names, evidence in the closing commit,
spec/verify prose only here. Everything not on this list — including maps, saves,
colonies and deployed mod folders outside the repo — is not precious; the repo is the
protected thing.

## Git

CLAUDE.md owns the rules ("Git" + the Transient rule); `design/RimMandrake/GIT_WORKFLOW.md`
is the operating doc. Charter's additions only: commit when a unit of work exists, and work
only in your seat clone (`/home/mandrake/rm/<seat>`) — `D:\Luke\dev\RimMandrake` is a
read-only mirror.

🔴 **Worktrees are OFF** (owner ruling 2026-10-02, by question card): worktree agents duplicated whole
checkouts and left work stranded on side branches. **Never pass `isolation: "worktree"` and never run
`git worktree add`** — `.claude/hooks/block_worktrees.py` refuses both, and the WorktreeCreate hook refuses
`claude --worktree`. A writing helper edits in its window's own clone; the window commits the paths it
changed with `./publish -m "…" <paths>`. Run writing helpers one at a time when their paths could overlap.
Brief every helper that `reset --hard`, `checkout --` and `stash` are forbidden and a conflict is reported
back, never cleared.

## Queue

An item is one line — `THREE_UPPER_SNAKE_WORDS_# · lane · the ask` — plus optional
prose in `infrastructure/state/items/<ID>.md` for expensive-list items only. 🔑 **On
close/drop/supersede the prose moves to `items/closed/<ID>.md`** — so `items/*.md` is
the LIVE set and a sweep stops walking finished work; `rimflow show` resolves both.
Reboot handoffs are not items and live in `infrastructure/state/handoffs/`. The
ledger — the frozen `events.jsonl` plus one `ledger/events/<SEAT>.jsonl` shard per
seat since 2026-09-23, written only by `rimflow` — is the truth; `queue/BENCH.md`/`FOUNDRY.md` are
gitignored rendered views you never edit — read one with `rimflow queue <SEAT>`, which
renders first (`queue/HUMAN.md` is the owner's hand-written inbox and stays tracked). Close: `rimflow close <ID> --sha <commit>`, commit
carrying `Closes: <ID>`, push.

🔴 **ANY SEAT ENDS AN ITEM IT FINDS DEAD — owner's ruling, 2026-09-19.** The moment
any seat finds a queue item **completed, totally invalidated, superseded, or otherwise
no longer worth considering for activity**, that seat ends it itself — no routing to
the owning seat, no `--owner-said`, no asking. Ownership gates work in flight
(`claim`, `start`, `block`, `verify`, `reclaim`, `renew`, `release`, `implemented`, `reconcile`),
never the three terminal verbs. `implemented` is not terminal: it records published code and the
level-tagged criteria still owed (`built` -> `validated` -> `done`); only `done`, `drop` and
`supersede` end an item:

```
rimflow close <ID> --sha <commit> --reason "<what proves it done>"
rimflow drop  <ID> --reason "<what proves it dead>"
rimflow supersede <ID> --by <NEW_ID> --reason "<why the successor replaces it>"
```

The ledger event stamps the **ruling seat** automatically — that is the record of who
called it, and `--reason` is the ruling itself, mandatory in practice on another seat's
item. ⛔ **The evidence bar is unchanged**: done means proven, dead means probed. This
removed the seat boundary, not the requirement to have looked. **Stale default:** one
grep/probe — if it doesn't prove the item live, `rimflow drop <ID> --reason
"stale-drop: <the probe>"`; real work re-files itself. Naming: CLAUDE.md's "Queue items are NAMED" section. v2 ideas
go straight to `design/V2_DREAMS.md`, any window, no permission.

## Correctness outranks seat ownership — owner, 2026-09-19

> *"It is WORSE to leave incorrect information that belongs to another seat than it is
> to violate seats... ok? I keep saying this. MAKE IT SO EVERYWHERE."*

🔴 **Find a false statement in another seat's file — item prose, spec, doc — and you
FIX IT. Now, yourself.** Not a correction item, not a note, not a message. The seat
boundary never protected a wrong sentence, and every reader downstream believes it
until someone crosses the line.

- **Commit it immediately, by explicit path.** The real risk was never the crossing —
  it was an uncommitted fix sitting in a tree four threads share, erased by the next
  checkout with nobody told. Committing IS the safeguard.
- **Say what was WRONG in the commit, not just what you changed.** The owning seat
  reads the log, not your reasoning.
- ⛔ **Fixing ≠ redirecting.** Scope, priorities and decisions stay theirs: correct
  what is FALSE, and `rimflow file --for <them>` anything that is a judgement call.
- `queue_lint.py` enforces exactly this: a cross-seat item edit WARNS and never
  refuses (48/48 selftests). Deleting wrong content beats annotating it — see
  CLAUDE.md's "Inaccurate material is DELETED".

## Decisions

The owner decides. A ruling is one dated line in `infrastructure/state/canon.yml`
(numbers, rosters — every value with a `src:`) or on the item (scope). A reversal
**replaces** the old line in the same commit and propagates to every file naming the
item, same commit. A ruling under 24 h old is a draft — reversible without ceremony.

## Rules and lessons

An enforced rule is a **hook** (`.claude/hooks/`); propose the hook, not a paragraph.
A default worth stating is a **line in this charter**, replacing one. Everything else
is deleted — git is the archive. Lessons: one file each into
`infrastructure/state/lessons/` (`python3 src/RimMandrake/Utils/lessons.py add "…"`), at any time and at reboot; skills are edited
only in a fresh-context curation session, never at end-of-context. A fact that
outgrows its doc goes to `infrastructure/state/facts/` — unbudgeted, never dropped
for space.

## Instruments, in order — and dumps decay

**RimSage** (`mcp__rimsage__*`: defs + engine C#, no load) → **`measure`/the def
dump** (post-patch truth; never a bare number from a scan — `MEASURED`/`UNMEASURED`/
`REFUSED`) → **quicktest via bridge** (~90 s) → **cold load** (expensive list).
**Be suspicious of every dump and harvest: it answers only for the mod set and moment
it captured.** Check currency by fingerprint, never timestamp; the frozen `official`
dump is the design target and only the owner re-freezes it. The silent-failure traps
(patches, deploys, defName guessing) are CLAUDE.md's "Facts you cannot guess".

## How we debug — owner, 2026-10-01

`design/RimMandrake/debug_process.md` is the process. **Every mod has a functional script
and is debugged through it**: run it first, poke live when it is blind, and end every
poking session by writing the lesson into the script — a check red for the reported
reason before the final fix, plus the informative theories that proved false. Agents
write, approve and declare passing on these scripts; the owner's hash-bound `## north
star` bars stay his. Stuck → GPT early, for hypotheses to test.

🔴 **BUILD PAUSE, in force:** no new content (mods, defs, mechanics, biome work) until
every mod has a first script with a recorded run — only bug fixes and script/harness
work, exceptions on the owner's word only. Lift condition: `debug_process.md` §1.

## Game state and the bridge

He says it, you run it, verbatim: `./game --said "<his words>" up|down|loading`.
Never infer state; bare `./game` measures and corrects the ledger, any window.
`broadcast.py` is his, with that single carve-out — and the carve-out is STAMP-ONLY
(owner, 2026-09-29): a seat's relay writes the ledger and messages no window; peers
read the state from `rimflow next`, which measures the game itself. The bridge is
one driver at a time — `rimflow bridge take` / `release`; CLAUDE.md's "The bridge is
passed through one file" is canonical. Config files
(`ModsConfig.xml` included) never wait for RimSort or the game; only assemblies need
the game down (OS lock).

## Windows

**BENCH** (with the owner, permanent bench) and **FOUNDRY** (autonomous, pulls the
queue) — `BENCH.md` / `FOUNDRY.md`; every model choice, seat and subagent alike:
`Agent_Policy.md`. Subagents: spawn freely, always with `model`; a subagent's return
is evidence, never a finding, and no subagent writes shared state. Windows never
message each other — the queue and the owner are the only channels; your own
subagents are not peers. Queue views render on every `rimflow` write — no loop, no
publisher, no staleness.

**Rebooting a window is prepared, not improvised** (owner, 2026-09-06). At a real
wave boundary — subagents all reported, everything committed and pushed, nothing
mid-edit — and above all the moment you would say *"that's all I have for now"*,
write the handoff with `RIMFLOW_SEAT=<SEAT> python3 src/RimMandrake/Utils/handoff.py`
(the env var is required on any machine without a seat profile — the Mac laptop has none,
and until 2026-09-16 `handoff.py` silently filed every laptop handoff as FOUNDRY's,
carrying FOUNDRY's in-flight items; it now REFUSES rather than guessing), fill
the four sections it leaves marked, pass `--check`, then say **HANDOFF READY** as
your last line and start nothing new. He reboots on his own clock while the cache is
warm; the phrase is the signal, and only a seat may say it — the script refuses to.
Say it **once**: until real work comes in, `handoff.py` reports ALREADY HANDED OFF
and writes nothing, because a signal given every idle turn is not a signal.
