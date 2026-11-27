# BOUNDARY: one no-model command lands the fast part of an owner ruling, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/ruling_fast.py`. Item: `RIMMANDRAKE_BUILD_RULING_FAST_PATH_SENTENCE_TOOK_NINETY_MINUTES`,
written 2026-11-26. Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_ruling_fast.py`.

Why: on 2026-11-26 the owner ruled in one sentence that the Deep Desert Tribes mod sleeps. A model worker took about
40 minutes to carry the ruling, and its landing then waited over 50 minutes in the publish line. His hold was not on
disk for that time. His words (2026-11-26): *"Yes please build the automated script that would accelerate the small
fast part independently of the larger items of work."*

    python3 src/RimMandrake/rimflow/ruling_fast.py <ITEM> --said "<his words>" --section "<heading>" \
        [--hold <Mod>]... [--park <ID>]... [--title "<a short lead, our text>"] [--why "<the Conductor's order>"]
    python3 src/RimMandrake/rimflow/ruling_fast.py <ITEM> --per-ruling <item-id|event> --why "<the Conductor's order>" \
        --section "<heading>" [--park <ID>]...

The command composes parts that exist. It writes no second copy of any of them:
`rimflow note --owner-said`, `mod_owner_hold.py hold`, `rimflow block --kind owner`, `rimflow file --kind owed`,
`./publish --ledger` (the ledger door) and `./publish` (a Markdown-only commit takes the text door,
`design/specs/2026-11-24-treecheck-slots/boundary.md`, a-text-publish-passes-held-slots).

## ACCEPTS (the only inputs this is built for)

- **his-words-and-what-they-act-on.** An item that the ledger knows, his words as he typed them (or the Conductor's
  route: a standing ruling cited with `--per-ruling` and its reason in `--why`), the heading of one
  section of `design/RimMandrake/standing_rulings.md`, and any number of mods to hold (each a folder
  `design/concepts/<Mod>`) and tickets to park (each an item that the ledger knows).
- **a-clone-of-this-repo.** The command runs at the top of a clone that can land with `./publish`: the Conductor's seat
  clone, or a helper clone with the Conductor's order.

## DOES NOT SURVIVE (not promised)

- **local-commits-under-the-text.** The text commit lands with `./publish`, which also pushes the clone's earlier
  local commits. When the clone holds an unpublished commit of code, the text commit then takes the ordinary door and
  waits for a slot. The command says so in its output before it publishes.
- **a-section-heading-that-moves.** The section is found by its heading text at the moment of the call. Its words go
  at the end of that section.
- **a-ledger-write-that-fails-half-way.** The acts run in order and stop at the first failure, with the cause named.
  The acts before it stay done (the ledger is append-only); the undo line names how to take each back.
- **the-hold-mirror.** `mod_owner_hold.py hold` writes the hold into the control store, which binds every launch at
  once and is copied to git by `rm-control-acts-export.timer`. The store's mirror `mod_owner_hold.json` is a pipeline
  file: its publish waits for a slot. The command leaves the mirror written in the clone and names its publish in the
  follow-up item.

## PROMISES (each one is owed a test of the same name)

- **the-acts-run-in-order.** The command records his words on the item (`--owner-said`), then holds each named mod and
  parks each named ticket with his words, then writes his words into the named section, then files one follow-up item
  of kind `owed` caused by the item. The ledger acts land through the ledger door before the text is written. The
  text lands through `./publish` of `standing_rulings.md` alone.
- **his-words-go-in-word-for-word-with-the-event-date.** The section gains one bullet that holds his words exactly as
  given, the Pacific date and time of the ledger event that recorded them, that event's `tsn`, and the item.
- **only-what-the-caller-names.** The command holds only the mods and parks only the tickets that the call names. With
  none named, it holds and parks nothing. It never searches for a mod or a ticket.
- **a-bad-call-does-nothing.** The command refuses before its first act, and names the repair, when: it has neither
  his words nor the Conductor's route, or both; the route has no `--why`; the route names a mod to hold (a hold is his
  act alone, `mod_owner_hold.py`); the item, a ticket to park or a mod to hold does not exist; the heading matches no section or more than one;
  `standing_rulings.md` has uncommitted edits in the clone.
- **the-follow-up-holds-the-slow-part.** The follow-up item names the slow part: the rule line in `CLAUDE.md`, the
  search for lines that say the opposite, the search for tickets that he did not name, and (when a mod was held) the
  publish of the hold mirror.
- **the-conductor-route-cites-the-ruling.** With `--per-ruling` and `--why`, the note and each park cite the ruling
  (CLAUDE.md §A fault of form is repaired where it is found: no tool refuses the Conductor's act for lack of a quote).
  The bullet says that the act is the Conductor's under that ruling, and gives the reason as our text, never quoted as
  his words.
- **at-most-five-lines.** The command prints at most 5 lines: what landed with its published sha, the follow-up item,
  and the undo.

## LIMITS

- None of its own. Each part that it calls keeps its own limits; each call is a hang guard of
  `time_budget.CALL_S`.

## PROOF

- The selftest is green on the fix, with planted faults caught (`evidence/plants.txt`).
- One timed real use on a scratch item, from the call to the published sha (`evidence/real_use.txt`), Archmagi,
  2026-11-26 7:06 PM PST, while 5 publishes waited for a tree-check slot: 264.7 s from the call to the last sha. His
  words and the park landed by the ledger door in 18.3 s; the rule text by the text door in 151.3 s. The same ruling
  by a model worker took about 90 minutes on the same day.
