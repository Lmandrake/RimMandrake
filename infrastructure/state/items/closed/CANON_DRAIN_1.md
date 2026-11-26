## the goal (owner, 2026-09-10)

A total canon drain: reconcile every lore doc to **one level of truth**, grinding out
every superseded, obsoleted, or contradicted statement — so that for at least one
moment the project has a single, non-contradictory canon. Not a light edit pass; a
deliberate reconciliation of the whole lore corpus.

## 🔴 THE TRIGGER — when to run it (BENCH's recommendation, owner-accepted)

**Gate: the biome-cast wave has settled.** Run it once BOTH are true:
- Fauna round-2 per-biome sittings are complete (casts/moves/groupings ruled), AND
- Flora is ruled.

**Do NOT gate on the FOUNDRY build backlog** (Cryptoforge retire, VQE curation, boom
cut, Mo'Events, mech/fish patches, etc.) — those change code/defs, not lore truth, and
tying the drain to them pushes it out for no benefit; let them run in parallel.

Reason: a drain's product is a durable single-truth snapshot. The fauna/flora/biome
sittings REWRITE the biome sheets — the largest surface a drain touches — so draining
before they land means doing it twice. Draining after them makes the snapshot hold.

## method

- A **dedicated fresh-context pass**, not squeezed between sittings — it wants clean
  context, like the skill-curation sessions.
- Prove a line is genuinely dead with the **two-blind-arms doc audit** (`skills`:
  two independent passes that cannot see each other, cut only where they agree; last
  run found 29% of 380 doctrine claims dead). See `two-blind-arms-doc-audit` memory
  and `Utils/doc_claims.py` for mechanical claim extraction.
- Obey **delete-don't-supersede** (owner, 2026-09-09): remove wrong/dead content
  outright (git is provenance), fix every inbound reference in the same change; a
  top-of-doc successor pointer only for content that MOVED.
- Scope = every lore doc: `design/Jawa/worldbuilding/**` (biome sheets, data),
  `design/Jawa/reconciled_lore/**`, `design/Jawa/**` canon, plus the frozen sheets
  (drain amends them under the freeze rule where a line is dead, recorded on this item).

## reducing its eventual cost (do NOW, ongoing)

- Keep the delete-don't-supersede discipline on EVERY decision as it lands (as done
  through 2026-09-10: coolant-leak retirement, the river "occurred" fix, the Contagion
  naming). Every clean ruling is one line the drain won't have to hunt.
- Defuse any actively-misleading contradiction the MOMENT a pending sitting would hit
  it (targeted, in-context), rather than letting it wait for the sweep.

## verify / criteria

- After the drain: no lore doc contradicts another on any ruled fact; every "superseded"
  / "old working name" / "retired" line is either deleted or is a MOVED-pointer with a
  live target; a spot audit of N random ruled facts finds one and only one statement of
  each.
- The owner can open any lore doc and trust every line is current.
