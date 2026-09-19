## spec
Standing owner instruction, reaffirmed 2026-09-11: "Fan out and continue full
belt at all times... there should always be at least one agent regenerating
graphics." Continuation of `ART_REGEN_WAVE4_QUEUE_1` through
`ART_REGEN_WAVE7_QUEUE_1`, same source pool: `art: "improve"` rows in
`design/Jawa/worldbuilding/review/round2/decisions_propagated.json`, same
binding semantics (`infrastructure/artpipe/README.md`, "'improve' semantics"
section) under the owner's `ART_REGEN_WAVE4_SOURCE_DECISION_1` ruling
(2026-09-11T23:56:18Z, `infrastructure/state/ledger/events.jsonl`): full
regen, Star Wars-named creatures keep canon identity, non-SW names free to
be reimagined, heavy black outlines enforced.

Of the pool filtered to `decision: "in"` rows with a real biome assignment
(excluding `homeless:*` design-call rows), minus every name already spoken
for by waves 1-7 (28 names) plus `AA_Lockjaw`/`AA_Mantrap`'s mid-iteration
attempts, and further excluding `AA_Eyeling` (owner explicitly kept the
donor art as-is, 2026-09-07, `IKEE_MYNOCK_ART_REGEN_1`): 21 eligible
candidates remained.

**3 creatures picked** (a modest slice, not the whole remaining pool):
- `Kinrath` (the_greentide) — SW-canon, confirmed against
  `design/RimStarWars/star_wars_canon_names.md`.
- `Shiro` (the_greentide/the_miasma) — SW-canon, confirmed against the same
  reference.
- `Borcatu` (wasteland) — SW-canon, confirmed against the same reference.

18 candidates remain in the pool for a future wave 9.

## verify
`fill_queue.py --input Transient/art_regen_wave8_improve.json --channel
codex` filed 9 job files (3 facings × 3 creatures) into
`infrastructure/artpipe/pending/`. Confirmed on disk: 8 in `pending/`
(`borcatu_v1_{north,south}`, `kinrath_v1_{east,north,south}`,
`shiro_v1_{east,north,south}`), 1 already picked up into `active/`
(`borcatu_v1_east`). Daemon (`artpiped.py -N 3`, pid 699477) confirmed alive
via `pgrep` at filing time.

## criteria
(a) Jobs filed and the daemon confirmed consuming them — MET, see verify.
Wiring the finished art into game defs (once the daemon validates/completes
each facing) is a follow-up step for whoever next reviews `done/` — not part
of this item's own close criterion, matching wave 4/5/6/7's own precedent
(queue-and-confirm, not full wire-in).
