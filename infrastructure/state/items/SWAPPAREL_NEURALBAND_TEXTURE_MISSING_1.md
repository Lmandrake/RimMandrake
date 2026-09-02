# SWAPPAREL_NEURALBAND_TEXTURE_MISSING_1

Filed as "neuralband renders magenta" — confirmed real, and confirmed **systemic**,
not a one-off: all 12 KotOR headgear items in
`src/RimStarWars/Armoury/Defs/Absorbed_KotorWeapons/ThingDefs_Gadgets/Absorbed_KotorWeapons_GadgetApparel_KotORHeadgear.xml`
share the identical defect.

## Root cause (FOUNDRY, 2026-09-02, offline — no art was generated to prove this)

Each headband def carries two separate graphics:
- `<graphicData><texPath>SWApparel/Headbands/<name>Item</texPath>` — the
  inventory/menu icon. **Present** for all 12
  (`src/RimStarWars/Armoury/Textures/SWApparel/Headbands/<name>Item.png`,
  deployed copy confirmed byte-present too).
- `<apparel><wornGraphicPath>SWApparel/Headbands/<name>` — the sprite drawn
  on the PAWN. **Absent for all 12**, confirmed by directory listing: only
  the 12 `*Item.png` icons exist in `Textures/SWApparel/Headbands/`, zero
  `<name>.png`/`<name>_north.png`/`<name>_east.png`/`<name>_south.png`
  files for any of them.

This is the "icon-only apparel" trap: RimWorld happily loads and equips the
item (the icon renders fine everywhere it's shown as an icon), but the
worn-graphic lookup fails silently and falls back to the engine's magenta
placeholder the moment it's actually equipped on a pawn — exactly matching
the filed symptom, and exactly why nobody caught it earlier (icons look
fine in every list/trade/inventory view).

Reference pattern for what a working entry looks like, from this same
Armoury mod: `Textures/SWApparel/headwrap/maskedheadwrap.png` +
`_east`/`_north`/`_south` (4 files) for `maskedheadwrap`'s own
`wornGraphicPath`.

## The 12 affected defNames (all in the one file above)

`guy762_Headband_verpine`, `guy762_Headband_nerualband` (defName itself has
a transposed-letter typo — `nerualband` vs the correct `neuralband` used
in every texPath/label; NOT touching that rename here, out of scope and
risks a save-compat break — flag only), `guy762_Headband_lightscan`,
`guy762_Headband_bothan`, `guy762_Headband_demovisor`,
`guy762_Headband_exchange`, `guy762_Headband_medical`,
`guy762_Headband_regalvisor`, `guy762_Headband_interface`,
`guy762_Headband_breathmask`, `guy762_Headband_rebreathermask` (texPath
stem `stabilizermask`, defName says `rebreathermask` — another
name/texPath-stem mismatch worth a separate look, not blocking this fix
since the wornGraphicPath already correctly points at `stabilizermask`).

## spec

Generate the missing worn-graphic sprites for all 12 headbands, matching
the existing `*Item.png` icons' silhouette/style (per
`generating-rimworld-sprites` skill doctrine — validate against the
existing icon as the style/identity reference, not a blank prompt), each
as a small KotOR-style head-mounted gadget (headband/visor/goggles/mask)
sized to sit on the Eyes/Overhead layer per each def's `bodyPartGroups`.
This is a real AFK art batch (up to ~48 images: 12 items × up to 4 files
each, matching the `maskedheadwrap` reference pattern) — not a quick inline
fix, and belongs in a dedicated `generating-rimworld-sprites` pass, not
squeezed into a queue-check reply.

## verify

Per-file: the skill's own offline validator (canvas size, real alpha,
silhouette inside the reference icon's footprint). Live: dev-spawn one
pawn wearing each of the 12 (or at minimum `guy762_Headband_nerualband`,
the one actually reported) and confirm no magenta on the pawn — screenshot
or savegame per this project's "options he must LOOK at ship as a
savegame" rule if presenting a batch for review.

## criteria

All 12 headbands render their worn sprite correctly on an equipped pawn;
zero magenta. Icons are untouched (already correct). No defName/texPath
renames bundled into this fix — those are separately flagged, not blockers.
