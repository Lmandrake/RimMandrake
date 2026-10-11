# Traps — each one happened

| trap | what happened | the check |
|---|---|---|
| A sheet of game art built outside the gated builder | 7 non-biome art sheets in a week (sluice box, junk reskins, creatures, icons) shipped with no scale panel; one declared itself `non-art` while showing 311 sprites (2026-10-03…10) | build with `art_sheet.py --subjects`; `game_art.py deliver <html>` before giving it to him |
| A whitelist in the generator | a `SCALE_BIOMES` whitelist silently left 21 sheets with no panel (2026-10-06 handoff) | the gate checks every row, never only the opted-in ones |
| "Current art" taken from a def's LAST texture path | 65 of 109 desert rows showed the dessicated corpse (2026-10-04) | resolve the body graphic by role, never by list position |
| A rebuild re-letters columns he already ruled | 28 spurious rejection events from one rebuild (2026-10-09) | `remap_decisions.py` after every rebuild of a touched sheet; letters are append-only |
| A note followed twice | 7 Greentide notes already filed as jobs were briefed out again (2026-10-08); an old note rode along on a new click (2026-10-07) | enact moves followed notes to `notes_followed`; compare the job's `created` with `decidedAt`, never `at` |
| A redo carrying the rejected picture as its reference | a "make it alien" redo kept redrawing the rejected creature and failed canon twice (2026-10-10) | a redo whose note rejects the anatomy carries NO reference; build the prompt from the def's description |
| Pre-snapshot decisions | 229 rows of legacy (pre-2026-10-04) decisions were refused by enact | `legacy_redo_triage.py`; never hand-translate them |
| A served sheet invisible in RimPulse | server stdout went elsewhere (2026-10-10) | serve into `<sheet>.serve.log` beside the sheet |
| A size that was never measured | plants drawn at the fallback size while their defs set sizes several times larger | every size prints its source; FALLBACK is flagged on the row and checked by the gate |
| Enacting slowly | four helpers chained serially took ~2 h (2026-10-08) | one `art.py enact` pass, one batched card at most |
