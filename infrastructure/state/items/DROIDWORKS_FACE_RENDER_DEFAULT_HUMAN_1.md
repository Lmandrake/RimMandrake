## spec
Surfaced during `DROIDWORKS_PRIMITIVE_TIER_1`'s 2026-09-13 live spawn: every
Droidworks race (G2 included) is defined with `RSW_DW_HeadType_Blank` — a
transparent stub head meant to suppress the default human face render on an
AlienRace pawn — but a live spawn still shows a default human face on the
droid body. The body chassis art itself is correct and already
owner-reviewed; this is specifically about the HEAD/face layer.

Not the same thing as `DROIDWORKS_HEADS_BRAINS_SPIKES_1`, which is about
craftable identity heads (a gameplay mechanic), not AlienRace face
rendering (a def/graphics correctness question).

## verify
- Confirm the actual AlienRace head-type resolution chain for a Droidworks
  pawn (`AlienPartGenerator`, `GraphicPaths`, whichever field controls
  head-type selection per race) — read the def and the AlienRace framework
  source before assuming the fix, per this repo's own "never guess a
  defName/field" doctrine.
- Live-spawn a G2 (or any Droidworks race) and confirm no human face
  renders once fixed.

## Watch out
- This may affect ALL Droidworks races sharing `RSW_DW_HeadType_Blank`, not
  just G2 — check the blast radius before scoping a fix to one race.
