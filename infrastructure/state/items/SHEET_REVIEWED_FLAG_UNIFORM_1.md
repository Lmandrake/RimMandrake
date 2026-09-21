# SHEET_REVIEWED_FLAG_UNIFORM_1 — you cannot tell a ruled sheet from a prefill by looking

## what is wrong

A `*.decisions.json` sidecar is how a review sheet's verdicts outlive the conversation.
Some hold **the owner's actual choices**. Some hold **an agent's pre-filled guesses that
nobody has looked at**. They are the same shape, and **there is no single field that says
which.**

MEASURED 2026-09-21 across all 13 sheets in `Transient/`:

| how the sheet declares review status | sheets |
|---|---|
| `reviewed_by` / `owner_said` | 3 |
| `approvedBy` / `approvedAt` / `approvedSaid` | 3 |
| `savedBy` + `writeCount` only | 2 |
| `decidedCount: 0` | 1 |
| `generatedBy: "…(agent pre-fill…)"` | 1 |
| **a sentence buried in the free-text `criterion` string** | 1 |
| nothing at all | 3 |

⇒ An agent that checks one key gets a confident answer that is wrong for ten of the
thirteen. 🔑 **This is not hypothetical — it is how today's `RSW_MossBeetle` contradiction
happened**: one sheet's verdicts were read as owner-approved and collided with a blanket
ruling given a day later, and it took the owner's own word to settle.

Three sheets are 100% prefill-identical with zero human input today:
`desert_art_verdict_2026-09-20` (25 rows), `landmark_density_2026-09-19` (26),
`lantern_deeps_strange_life_2026-09-20` (21).
⚠️ All three ARE honest about themselves — each in a different key. Honesty nobody can
query uniformly is not a safeguard.

## spec

1. **One required key on every sidecar**, written by the generator: an explicit reviewed
   state plus who and when. Absent ⇒ treated as UNREVIEWED, never as neutral.
2. **A reader** — one function, used by every consumer — that returns
   `ruled` / `prefill` / `unknown`, and **refuses rather than guessing** on `unknown`.
   🔴 The refusal is the deliverable. A reader that defaults to "probably ruled" rebuilds
   the defect.
3. **Backfill the 13 existing sheets** from the evidence each already carries. ⛔ Do not
   infer "ruled" from row content — `decision == prefill` on every row is exactly what a
   genuine all-keep ruling looks like too, so the row data cannot distinguish them. Use
   only each file's own provenance keys, and mark anything ambiguous UNKNOWN.
4. Teach it in `~/.claude/skills/review-sheets` so new sheets are born with the key.

## Watch out

- ⚠️ **`decision == prefill` proves nothing on its own.** A human who agrees with every
  prefill produces a byte-identical file to one nobody opened. Only provenance separates
  them — which is the whole reason this item exists.
- ⚠️ A sheet can be genuinely half-reviewed. `ruled`/`prefill` may need a per-row answer,
  not just a per-file one; `decidedCount` already gestures at this.
- ⛔ Do not rewrite a sheet's `decisions` block while backfilling. Those are curation
  artifacts — patch the metadata, never re-generate the file
  (`~/.claude/skills/frozen-artifacts`).

## criteria

Every `*.decisions.json` carries an explicit reviewed state, one shared reader returns it,
and a consumer handed an UNREVIEWED or UNKNOWN sheet refuses instead of proceeding.
