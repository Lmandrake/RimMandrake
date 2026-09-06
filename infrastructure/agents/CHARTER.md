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
5. **History and others' work** — force-push, `reset --hard` on the shared tree,
   deleting work not yours: warn in one line, then only with the owner's word.
6. **Anything the owner must LOOK at** — always with the complete native path in
   backticks, spaces as spaces.

Ceremony means: the one pre-check the tool names, evidence in the closing commit,
spec/verify prose only here. Everything not on this list — including maps, saves,
colonies and deployed mod folders outside the repo — is not precious; the repo is the
protected thing.

## Git

CLAUDE.md owns the rules ("Git" + the Transient rule). Charter's additions only:
commit when a unit of work exists, and `git status --porcelain <path>` before
touching a file another window may hold.

## Queue

An item is one line — `THREE_UPPER_SNAKE_WORDS_# · lane · the ask` — plus optional
prose in `infrastructure/state/items/<ID>.md` for expensive-list items only. The
ledger (`events.jsonl`, written only by `rimflow`) is the truth; `queue/*.md` are
rendered views you never edit. Close: `rimflow close <ID> --sha <commit>`, commit
carrying `Closes: <ID>`, push. **Stale default:** one grep/probe — if it doesn't
prove the item live, `rimflow drop <ID> --reason "stale-drop: <the probe>"`; real
work re-files itself. Naming: CLAUDE.md's "Queue items are NAMED" section. v2 ideas
go straight to `design/V2_DREAMS.md`, any window, no permission.

## Decisions

The owner decides. A ruling is one dated line in `infrastructure/state/canon.yml`
(numbers, rosters — every value with a `src:`) or on the item (scope). A reversal
**replaces** the old line in the same commit and propagates to every file naming the
item, same commit. A ruling under 24 h old is a draft — reversible without ceremony.

## Rules and lessons

An enforced rule is a **hook** (`.claude/hooks/`); propose the hook, not a paragraph.
A default worth stating is a **line in this charter**, replacing one. Everything else
is deleted — git is the archive. Lessons: one line each into
`infrastructure/state/LESSONS_INBOX.md`, at any time and at reboot; skills are edited
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

## Game state and the bridge

He says it, you run it, verbatim: `./game --said "<his words>" up|down|loading`.
Never infer state; bare `./game` measures and corrects the ledger, any window.
`broadcast.py` is his, with that single carve-out. The bridge is one-driver-at-a-time:
`rimflow bridge take` / `release`, release the moment you stop driving. **Superseded
2026-09-02 — CLAUDE.md's own "The bridge is passed through one file" is now
canonical**: it errs toward ALLOWING, not mutual lockout — a stale (45-minute-idle)
hold is simply taken, `take --force` always works, `infrastructure/state/BRIDGE`
is the one-glance mirror, `./bridge bench|foundry|free` is the owner's override.
Never message the other window about it — that channel is off. Config files
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
write the handoff with `python3 src/RimMandrake/Utils/handoff.py`, fill
the four sections it leaves marked, pass `--check`, then say **HANDOFF READY** as
your last line and start nothing new. He reboots on his own clock while the cache is
warm; the phrase is the signal, and only a seat may say it — the script refuses to.
Say it **once**: until real work comes in, `handoff.py` reports ALREADY HANDED OFF
and writes nothing, because a signal given every idle turn is not a signal.
