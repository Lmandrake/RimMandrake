# CHARTER

*Draft replacement for POLICY.md and the seat files. ~650 words. This file does not
grow: a new line must delete the line it replaces; git holds everything removed.*

## Posture

**Act first.** Anything git can undo gets no verification, no filing, no report
beyond one line: do it, commit explicit paths, push, "Done, `<hash>`."
The owner's word closes, opens, or overrides anything, instantly and without
re-derivation. When he is present you are at the bench: do what he says, ask
questions the moment they exist. He opts work *into* rigor ("careful with this
one"), never out of it.

## The expensive list — the only things that get ceremony

1. **A cold-load slot** (~25 min). Batch questions; write the Player.log strings that
   will decide each before launch (`rimworld-load-round`).
2. **`deploy_custom_mods.py --apply`** — read the plan first; never deploy over
   another window's uncommitted files.
3. **`ModsConfig.xml` writes** (`rimworld-start-prep`).
4. **Savegame writes** to the frozen world or ship saves — back up first
   (`rimworld-savegame`).
5. **History and others' work** — force-push, `reset --hard` on the shared tree,
   deleting what you have not looked at: warn in one line, then only with the
   owner's word.
6. **Anything the owner must LOOK at** — always with the complete native path.

Ceremony means: the one pre-check the tool names, evidence in the closing commit,
spec/verify prose only here.

## Git

Explicit paths, never `add -A`/`.`/`-a`. Commit when a unit of work exists; push is
the second half of commit. `git status --porcelain <path>` before touching a file
another window may hold. Nothing over ~50 MB. Human-once output → `Transient/`;
machine cache → `/tmp`; work products → the repo, committed.

## Queue

An item is one line: `NAME · lane · the ask` (names: three UPPER_SNAKE words + `_#`).
The commit trailer `Closes: NAME` is the close. Expensive-list items alone carry
spec/verify sections and the `verify` step. **Stale default:** one grep/probe — if it
doesn't prove the item live, `stale-drop` it; real work re-files itself.

## Decisions

The owner decides. A ruling is one dated line in `canon.yml` (numbers, rosters) or on
the item (scope). A reversal **replaces** the old line in the same commit. A ruling
under 24 h old is a draft and may be reversed without ceremony.

## Rules

An enforced rule is a **hook** (`.claude/hooks/`); propose the hook, not a paragraph.
A default worth stating is a **line in this charter**, replacing one. Everything else
is deleted — git is the archive. Lessons go to
`infrastructure/state/LESSONS_INBOX.md`, one line each; skills are edited only in a
fresh-context curation session, never at end-of-context.

## Instruments, in order

**RimSage** (defs + engine C#, no load) → **`measure`/def dump** (post-patch truth;
never a bare number from a scan) → **quicktest via bridge** (90 s) → **cold load**
(expensive list). A number about a large artifact comes from `measure`. A patch that
matches nothing logs nothing. The game reads the Steam `Mods` folder, never this
repo — writing is not deploying.

## Game state

He says it, you run it, verbatim: `./game --said "<his words>" up|down|loading`.
Never infer state; `./game` with no argument measures it. `broadcast.py` is his, with
that single carve-out.

## Windows

**PAIR** (with the owner, permanent bench) and **FACTORY** (autonomous, pulls the
queue by lane) — see WINDOWS.md. Subagents: spawn freely, always with `model`
(haiku enumerate · sonnet interpret · opus/fable only when the return is acted on
unverified). Windows never message each other; the queue and the owner are the only
channels. Board and queue views render by script, not by seat.

## Facts you cannot guess

Cold load ~25 min; quicktest ~90 s — never "restart and see."
`facts/` is unbudgeted: nothing learned is dropped for space.
Never guess a defName, field, or namespace — RimSage or the def, never memory.
Full native paths in backticks for anything he must open, every time.
