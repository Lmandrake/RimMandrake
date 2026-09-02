# FORSAKEN_CRAGS_PREDATORS_BUILD_1 — Cindermare + Skarnix, wild threat pair

Owner-approved design rows from `FORSAKEN_CRAGS_FAUNA_1` (closed) — both `approve`,
no edits requested. Full design content: `infrastructure/state/items/FORSAKEN_CRAGS_FAUNA_1.md`
and the ruled sheet `design/Jawa/worldbuilding/review/forsaken_crags_fauna_sheet.decisions.json`
(`decidedBy: owner-said`, frozen 2026-09-02).

Bundled as one build item (not split) because both are the same shape: wild
(untameable) `AB_RockyCrags` threats sharing an art context (the two promoted
`moornak_opt1`/`moornak_opt2` mockups) and a design register (environmental
valve rather than combat stats) — same pattern `LIVESTOCK_STARTER_TRIO_1` used
to batch onnik/karrask/moornak.

## spec

1. **Cindermare** (`moornak_opt1.png`) — wild threat, `AB_RockyCrags`. No mouth
   in the art, so its kill mechanic is a cold-drain grip (saps body heat on
   contact) rather than a bite. Solitary, untameable. Mane/hide harvested only
   from a kill (no live-shear/farm loop — this is a predator, not livestock).
2. **Skarnix** (`moornak_opt2.png`) — wild threat, `AB_RockyCrags`. Cat-large
   ambush stalker. Valve is behavioral, not combat: will not cross firelight
   or a heated space, so a lit camp neutralizes it without requiring fight
   stats. Untameable.

Both: RimStarWars tier (world/planet fauna, not campaign-specific), sprites
via `generating-rimworld-sprites` contract (128 px/cell, chroma-key alpha,
silhouette-first matching the promoted mockup art), beast-normalization
spirit (born normalized, no retrofit).

Invented premises carried over from the design pass (all declared, none
snuck in): the two names, Cindermare's cold-drain-grip mechanic (the art has
no mouth, so a bite kill was never on the table), Skarnix's firelight valve.

## verify

- Def compiles/loads clean, `validate_patch.py` 0 errors.
- Live quicktest: both spawn as wild `AB_RockyCrags` fauna, Cindermare's
  cold-drain attack registers a hypothermia-flavored damage/hediff on
  contact (not a bite wound), Skarnix demonstrably avoids a lit tile
  (`GlowGrid` check or observed pathing away from a heat/light source).
- Art matches the promoted mockups' silhouette (side-by-side check against
  `moornak_opt1.png`/`moornak_opt2.png`).

## criteria

Both creatures spawn on `AB_RockyCrags`, both untameable, Cindermare's
cold-drain and Skarnix's firelight valve are live-proven mechanics (not just
flavor text), art traced to the promoted mockups.
