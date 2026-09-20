# PYRELANDS_SOUTH_TOPDOWN_REGEN_1 — findings

Status: DONE — no jobs queued, item is already fully executed and unclosed

## Item file
No `infrastructure/state/items/PYRELANDS_SOUTH_TOPDOWN_REGEN_1.md` exists (never
written — ledger `thin:` flag confirms "no items/... yet"). The ledger
(`infrastructure/state/ledger/events.jsonl`) is the actual authority here and
tells the whole story.

## What the ledger shows (2026-09-17)
- Filed by BENCH 16:29, owner directive to find top-down souths via
  `facing_set_audit.py`'s viewpoint gate.
- Owner ruling 16:44: scope is exactly Mantistanis / FurnaceBeast / FireWasp
  (Razorjack/Barbslinger high-angle fronts explicitly KEPT, not in scope).
- BENCH background art agent regenerated all three souths eye-level via
  artpipe painterly family, gated per-creature by the viewpoint judge (wasp
  took 3 passes, furnacebeast 2 passes). Commits `dfbfa3a5c` (mantistanis),
  `81246e666` (furnacebeast), `f5e25eeaa` (firewasp) — all exist in git.
- Owner approved all three in-sitting ("Yes", 19:55). Wired at `d3aa7fb5d`
  ("Three eye-level souths wired") — 19:55:31, deployed same window.
- BENCH reassigned item to itself 20:32; **no close event follows**. Item
  never closed (queue still lists it `proposed`, unassigned row) even though
  the work is done — a bookkeeping gap, not missing art.

## Verified live on disk (not just trusted to the ledger)
- `d3aa7fb5d` touched exactly:
  `src/RimUtinni/FireWaspArtOverride/.../AA_FireWasp_south.png`,
  `src/RimUtinni/MantistanisArtOverride/.../GR_Mantistanis_south.png`,
  `src/RimUtinni/UtinniPatches/.../FurnaceBeast/FurnaceBeast_south.png`.
- `PYRELANDS_DONOR_PORT_4` (later) `git mv`-renamed the FireWasp file to
  `src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireWasp/FireWasp_south.png`
  — confirmed via `git log --follow -p` showing `rename from/to`, byte content
  carried forward untouched.
- All three south files' only edit since 09-17 wiring is the repo-wide
  `1135036ce` (2026-09-20) "zero the sub-visible export halo across 241 of our
  facing sprites" — a global alpha-edge cleanup pass touching hundreds of
  sprites, not a content revert.
- Confirmed each def's live `texPath` resolves to these exact current files:
  `RUT_FireWasp` -> `Things/Pawn/Animal/Pyrelands/FireWasp/FireWasp`,
  `Megafauna/Insectoid/GR_Mantistanis`, `Pyrelands/FurnaceBeast/FurnaceBeast`
  (RUT_PyrelandsFauna.xml / RUT_PyrelandsPortedFauna.xml).

## Per-creature

### GR_Mantistanis
Already regenerated, owner-approved, wired, deployed, live-texPath-confirmed.
**Not queued.** artpipe `done/` also shows the full prior lineage
(v3/v4/v4b/v5 south attempts) consistent with the ledger's account that v5
was the stale unattended draft superseded by this regen.

### FurnaceBeast
Already regenerated, owner-approved, wired, deployed, live-texPath-confirmed.
**Not queued.**

### AA_FireWasp
Already regenerated, owner-approved, wired, deployed, live-texPath-confirmed
(file relocated by an unrelated later rename, content unchanged).
**Not queued.**

## Jobs queued
NONE. Queuing any of these three would throw away an owner ruling from
2026-09-17 ("Yes" approving all three) per the CLAUDE.md rule on checking for
existing regenerated/ruled art first.

## Verify status
The item has no `## verify` section (never written). Per the ledger, the
*work itself* is complete and satisfies the original directive (three souths
now eye-level, gate-green, owner-approved, wired, deployed). The only thing
outstanding is administrative: the item was never closed (still `proposed` in
the queue) after BENCH reassigned it to itself 2026-09-17T20:32Z — that is a
close/bookkeeping action for the parent window, not a new art job.
