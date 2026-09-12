# infrastructure/artpipe/ — the art-pipeline daemon's queue

ART_PIPELINE_DAEMON_1. Built by `src/RimMandrake/Utils/artpipe/artpiped.py`.

**Deliberately NOT under `infrastructure/state/`** — that prefix is rimflow's
ledger and its item files only. This is a plain file-based job queue with no
relationship to the rimflow event log; a job here carries a `rimflow_item_id`
for provenance, but claiming, finishing or failing a job is not a rimflow
event and rimflow's CLI never reads this directory.

## Layout

```
pending/    job JSON files a seat has filed, not yet claimed. fill_queue.py
            is the only intended writer.
active/     jobs claimed by a daemon (atomic `os.rename` from pending/) and
            currently running, or orphaned by a crashed daemon until the next
            one reconciles them back to pending/.
done/       finished, validated jobs: `<id>.json` + `<id>.manifest.json`.
failed/     jobs that did not survive worker error, a validator REJECT, or a
            grumpiness-detector stop: `<id>.json` + `<id>.manifest.json`.
_artsrc/    staging for the PNGs a worker actually produces. Wiring a
            finished, validated file into a mod's Textures/ tree is a
            separate concern this daemon does not do.
throughput.jsonl   one line per request (appended, never rewritten): wall
            clock, meter before/after, validator verdict. The calibration
            projection's raw data.
```

A job file is JSON: `id`, `rimflow_item_id`, `reference` (path to the sprite
being reskinned, or null for new art), `canvas` `{width,height}`, `prompt`,
`facing`/`facings`, `style_notes`, `priority` (lower claims sooner),
`background`. See `src/RimMandrake/Utils/artpipe/AGENTS.md` and
`manifest.schema.json` for the worker's side of the contract.

Need a solid black (non-transparent) backdrop instead of the usual
`background: "transparent"` sprite pipeline? `BACKGROUND_TEMPLATE.md` has
the proven wording — reference-less jobs skip the validator entirely, so
that wording was tested empirically, not just written; see
`BACKGROUND_TEMPLATE_LOG.md` for the raw results.

## Who writes here

- `fill_queue.py` writes `pending/` only, refusing a duplicate id.
- `artpiped.py` (the daemon) is the only mover between directories and the
  only writer of `.manifest.json` files and `throughput.jsonl`.
- Nothing else. If a file here looks hand-edited, treat it as suspect.

## "redo" semantics (owner ruling, 2026-09-10 — binds every art pass reading a review sheet)

A sheet row's `art: "redo"` means the art is particularly bad and must be **fully
regenerated — possibly the whole creature**, not touched up. Star Wars creatures are
**never renamed**: gather inspirational reference images online and converge on the
canonical look. Non-SW creatures: redo may include a full rename+redefine from the
creature's function. **When in doubt, ask the owner.** Review surfaces render
creatures in side profile (east-facing), not the south-facing headshot.

## "improve" semantics (owner ruling, 2026-09-11 — binds wave 4 and every later `art: "improve"` pass)

The current graphical quality on every `art: "improve"` row is unacceptable — this is
not a light touch-up, it is a full regeneration, same mechanism as `redo`. What
distinguishes `improve` from `redo` is naming discipline, not effort:

- **Star Wars-named creatures keep their canon identity.** The name means that
  creature — draw what it actually is, converging on the canonical look (same rule
  as `redo`'s SW handling).
- **Non-Star-Wars names are subject to change.** The *general kind* of creature
  (e.g. "a burrowing rodent", "a chitinous flyer") is the part that's fixed; the
  specific name/flavor is not — get inspired by what the creature seems like it was
  supposed to be, and invent or draw on Star Wars canon for a new name/character if
  the current one doesn't earn its place. The result should read as an interesting
  alien that belongs on a Star Wars-themed world, not a reskinned Earth animal.
- **Enforce proper black outline thickness.** Every `improve` prompt must ask for a
  outline heavy enough to read clean at standard zoom and below — this is the
  concrete, checkable half of "unacceptable quality": thin/absent outlines are the
  first thing to fix regardless of what else changes.

Same "when in doubt, ask the owner" rule as `redo` applies to any specific creature
where canon-vs-invented naming isn't obvious.

## Channel ruling — owner, 2026-09-11

**Codex only. Gemini is OFF** ("Do not use Gemini anymore, only Codex please.")
— enforced by `artpiped.py`'s default gemini budget of $0 (the admission gate
refuses the channel). Queue no `"channel": "gemini"` jobs; a job that carries
it will sit refused. Re-funding requires the owner's word and an explicit
`--gemini-budget-usd`.
