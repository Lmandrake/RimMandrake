# LEANINGSCRUB_VENOMVINE_SITTING_1 — settle every venomvine form in one BENCH in-game sitting

The owner typed, 2026-10-08, on finishing the Leaning Scrub art sheet (relayed to a BENCH helper):

> "Ok, I finished the Leaning Scrub. More to do. We will need to settle all that Venomvine in a sitting on Bench in the game at some point since it's also a mechanic that grows in patches. There's still a lot to do on this sheet (waiting on graphics likely?) Please go ahead and cut anything that needs cutting at this time."

His typed note on the sheet's `RM_HoardVenomvine` row says the same thing: *"Keep all of these for now,
Venomvine is a mechanic as well as graphics, so we will need to reason about this during Bench settings.
Nice job."*

⇒ **No venomvine row on that sheet is enacted, installed, cut or regenerated ahead of this sitting.**
Venomvine is judged in the game, with the owner, as patches growing on the map: art and mechanic together.

## The sheet rows (state as of 2026-10-08)

Sheet decisions: `Transient/biome_ffar/leaningscrub_sheet_2026-10-05.decisions.json` (copy in
`infrastructure/state/art_rulings/2026-10-08_leaningscrub_sheet_2026-10-05.decisions.json`). Column
letters were picked by clicking the sheet. That is a decision taken by sheet, not a quote.

| row | sheet pick | column it names | his typed note |
|---|---|---|---|
| `RM_CrownVenomvine` | B | render gapfin_RM_CrownVenomvine_v1 | (none) |
| `RM_DrippingVenomvine` | B | render gapfin_RM_DrippingVenomvine_v1 | (none) |
| `RM_HoardVenomvine` | J | render 0vv_hoard_venomvine_v2 | "Keep all of these for now, Venomvine is a mechanic as well as graphics, so we will need to reason about this during Bench settings. Nice job." |
| `RM_HollowVenomvine` | A | our deployed art | (none) |
| `RM_QuenchVenomvine` | redo | (none) | "STOP USING THIS GRAPHIC AND MAKE VENOMVINE!" |
| `RM_RearingVenomvine` | redo | (none) | "STOP USING THIS GRAPHIC AND MAKE VENOMVINE!" |
| `RM_TwitcherVenomvine` | A | our deployed art | "variations" |
| `RM_VenomvineThicket` | B | render ls_regen_RM_Venomvine_v1 | "variations" |

Three forms in the `RM_LeaningScrub` wildPlants roster have **no row on the sheet at all**:
`RM_WalkingVenomvine`, `RM_SwornVenomvine`, `RM_SheddingVenomvine`. Bring them to the sitting too.
Defs: `src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/` (`RM_LeaningScrubVenomvineForms.xml`,
`RM_VenomvineSixForms.xml`). Roster weights: `src/RimMandrake/LeaningScrub/Defs/BiomeDefs/RM_LeaningScrub_Biome.xml`.

Related open item: `LEANINGSCRUB_VENOMVINE_FORMS_PITCH_1` (pitch further forms). Its question can be put in
the same sitting.

## needs

The owner present, the game up on a map with LeaningScrub patches spawned (`rimworld-live-review`).

## criteria

- Each of the 11 forms has his ruling on art and on mechanic/patch growth, recorded here and in
  `infrastructure/state/art_rulings/`.
- The two "STOP USING THIS GRAPHIC" rows get new venomvine art jobs, carrying his note verbatim, only after
  the sitting confirms the form stays.
- Context report: `Transient/leaningscrub_after_review_2026-10-08.md`.
