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

## Art style — painterly, restored (owner ruling, ART_PAINTERLY_RESTORATION_1, 2026-09-14)

**The wave-4/5 prompt family is the canonical style.** Exemplar: `ronto_v1_east`
(`done/ronto_v1_east.json`, ART_REGEN_WAVE4_QUEUE_1, 2026-09-11, canvas 512).
Shape:

> "RimWorld creature sprite, side view, **painterly vanilla-RimWorld animal art
> style**: [canon identity + rich anatomical description — legs, hide, folds,
> real creature]. Single creature, centered, standing pose, no ground shadow,
> no background scenery. Heavy, clean black outline around the whole silhouette
> and all major internal linework, thick enough to read clearly at standard
> RimWorld zoom and below."

Real anatomy (legs included) and high resolution are back — "as long as the
user will actually see the resolution" (owner's words).

🔴 **Painterly is the ONLY style law. There is no cartoonish option** (owner,
2026-09-15). The calm-flat-cel toy-figurine lawset, the ≤2-fused-stub leg
budget, and the "no painterly" word-ban are deleted outright — not preserved,
not selectable, not a fallback. Never author a prompt asking for flat cel
shading, jointless or fused-stub limbs, or a toy/figurine read.

**Resolution: `canvas` sizing is a rule of thumb, not a refusal.**
`drawSize×128`, rounded up to the next power of two (floor 256), stays the
sizing heuristic (owner's 2026-08-23 ruling) — but `fill_queue.py` no longer
REFUSES a row that exceeds it; it warns and files the job. The 2026-09-13
"stored resolution above 128 changes nothing measurable" finding was measured
at VANILLA zoom tiers only (96/32/18 px); the owner is not convinced it holds
at the enhanced zoom levels in the current mod stack, so canvas sizing errs
**GENEROUS** until re-measured at the modded maximum zoom-in (512 is fine for
a large `drawSize`) — never quote that finding against a high-res request.

**The legibility gate is advisory only, never a rejector.**
`src/RimMandrake/Utils/art_legibility.py` can still score a transparent-bg
sprite at 96/32/18 px on keyline, structure, ground separation and coverage,
and `art_zoom_sim.py` remains a useful EYE for a borderline call by hand — but
`artpiped.py` no longer fails a candidate on that score ("the whole scoring
metric nonsense", owner's words). The fitted 3-band model, the auto-reinforce
stroke, and their distinct statuses (`REINFORCED_PASS` ·
`legibility_borderline_unrescued` · `insufficient_margin` · `reinforce_failed`)
are dead code paths, not deleted, kept only in case the gate is ever re-funded
as a REPORTED number. A running daemon process needs a restart to pick this
up — it's a code change, not a config flip.

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
