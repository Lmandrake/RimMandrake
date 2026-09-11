## spec
Standing owner instruction: "always have at least one background sub agent
working on art regeneration." Continuation of `ART_REGEN_WAVE4_QUEUE_1` /
`ART_REGEN_WAVE5_QUEUE_1`, same source pool: `art: "improve"` rows in
`design/Jawa/worldbuilding/review/round2/decisions_propagated.json`, same
binding semantics (`infrastructure/artpipe/README.md`, "'improve' semantics"
section): full regen (same mechanism as `redo`), Star Wars-named creatures
keep canon identity, non-SW names are free to be reimagined (general kind
fixed, specific name/character not), every prompt explicitly asks for heavy
black outlines.

**New this wave**: `design/RimStarWars/star_wars_canon_names.md` (built
2026-09-11 from a local mod raid + Wookieepedia research) now exists as a
permanent canon-name reference. Waves 1-5 guessed canon-vs-invented ad hoc
per creature; this wave checked every candidate directly against that doc's
Creatures/Species section instead of guessing — a solid (non-UNCERTAIN)
entry means SW-canon-keep, absence or UNCERTAIN-only means free-to-reimagine.

Of the 338 `art: "improve"` rows, restricted to `decision: "in"` rows with a
real biome assignment (`fauna:<biome>:Name` keys, excluding `homeless:*`
design-call rows — same carve-out as waves 4-5), minus every name already
spoken for in `infrastructure/artpipe/done/`/`failed/`/`active/`/`pending/`
(all of waves 1-5's `redo`/`improve` creatures, `AA_Lockjaw`/`AA_Mantrap`'s
mid-iteration attempts, and internal test jobs): **35 eligible candidates**
remained (deduplicated by name across biomes).

**7 creatures picked (batch size, mixing both halves of the ruling, same
3-kept/4-reimagined ratio as waves 4-5)**:

SW-canon, identity KEPT — confirmed present as solid (non-UNCERTAIN) entries
in `star_wars_canon_names.md`'s Creatures/Species master-bestiary list:
- `Wyyyschokk` (the_webwork, large, note "Perfectly hideous") — a genuine
  third-party SW creature-pack species name [B]; the doc's own Known Issues
  flags that this campaign's web-silk-glob/mouth-loom *mechanic* is
  Utinni-original, but the species *name* is real SW. Drawn as a repulsive
  large web-predator.
- `Boma` (weeping_stones, large) — confirmed both in the master bestiary and
  the Planets/Locations table ("Boma beast," Dxun). Drawn as a massive
  draft/warfare beast.
- `Ollopom` (weeping_stones, small) — confirmed in the master bestiary [B];
  no individual Wookieepedia writeup exists yet, so the general small-desert-
  scavenger kind came from the row's own size/biome context, not invented
  detail.

Non-SW names, REIMAGINED (general kind kept, name/character invented) —
checked against the doc and found nowhere in it (all donor-mod prefixed
names: Alpha Animals, BiomesTeam, an "RG_"-prefixed pack):
- `AA_TarGuzzler` (the_sump, large, note "This is superb!!") → invented
  **Sludrin**: a bloat-gutted, tar-slick sump wallower with a distended
  guzzling gullet, not a literal Earth animal.
- `AA_FireWasp` (the_pyrelands, small, note "I like this a lot") → invented
  **Cinderwing**: an ember-glowing flying stinger with heat-shimmer wings,
  not a literal wasp.
- `BMT_CrestedDragon` (the_miasma, medium, note "Make it green and mottled")
  → invented **Verdaunt**: a sail-crested, green-and-black mottled swamp
  reptile, not a literal dragon.
- `RG_Rimclaw` (the_scarlands, large) → invented **Scarrend**: an armored,
  oversized-clawed scarlands ambush predator, not a literal crab/lobster.

Each job's `style_notes` records which half of the ruling applied, cites the
canon-doc check explicitly (found/not-found, with provenance code where
found), and — for the reimagined four — the donor prefix that ruled them
out. Every prompt explicitly requests "heavy, clean black outline around the
whole silhouette and all major internal linework, thick enough to read
clearly at standard RimWorld zoom and below" per the outline requirement.

**Did the reference doc change any call vibes alone would have gotten
wrong?** Yes, on `Wyyyschokk` and `Boma`: both read, by ear, as could-go-
either-way invented-sounding names (an alien-sounding compound; a short
generic-sounding word) — the doc's master-bestiary line settled both as
genuine third-party SW creature-pack names rather than requiring a guess.
`Ollopom` likewise sounds fully invented but is listed. Conversely nothing
in this batch would have been wrongly called canon by vibes — the donor
prefixes (`AA_`/`BMT_`/`RG_`) were already a strong tell wave-4/5 style
guessing also used correctly. Net: the doc earned its keep by converting two
genuine coin-flips into checked facts, not by overturning a prior wrong
guess.

21 jobs filed (7 creatures x 3 facings south/east/north, 512x512
transparent, codex channel, reference: null — full regen, same shape as
waves 1-5) via `fill_queue.py --input Transient/art_regen_wave6_improve.json
--channel codex`, dry-run first (0 duplicates/errors) then for real.
`pgrep -f artpiped.py` confirmed the daemon already running (PID 699477,
up ~4h). All 21 jobs sat unclaimed in `pending/` past the usual ~60s window,
so checked `throughput.jsonl`/`art_status.json` and the daemon's own
`CodexGrumpiness` gate (`artpiped.py`) before assuming a hang: the last
completed job (wave 5's `vornskyr_v1_south`) reported `primary_used_percent:
90.0` with `grumpy: true` — at/above the FIVE_H_SLEEP threshold, which
deliberately sets `sleep_until = primary_resets_at` (a real epoch,
~2026-09-11T14:28Z at filing time) rather than keep hammering a near-capped
Codex 5-hour window. This is the daemon's own documented de-escalating
backoff, not a stall or crash — it will resume claiming from `pending/`
automatically once that window resets, no restart needed. Left running
rather than force-restarted (a restart would not bypass the same live rate
limit).

## verify
Each of the 7 creatures' 3 facings lands in `infrastructure/artpipe/done/`
with `worker_status: ok`. Wiring into a mod's `Textures/` tree is a separate
step this item does not do (same pattern as prior waves).

## criteria
21/21 jobs complete (done or a clean, explained failed), daemon left running
so it keeps draining the queue unattended. Queueing itself — not the art
finishing — is what closes this item.
