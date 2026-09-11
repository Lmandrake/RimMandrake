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
