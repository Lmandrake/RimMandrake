<!-- status: live -->
## What was produced (spec-only, per F16's own framing)

Full spec: `design/Jawa/worldbuilding/sacred_sites_pass_1.md`, linked from
`design/Jawa/divine_satiation_engine.md` §11.

- **Tile→god annotation scheme**, a priority-ordered function keyed on
  biome/TileMutatorDef/LandmarkDef, deliberately NOT keyed on the 71 named
  regions — `REGIONS_THAT_LIE.md` shows 13 of them span 8+ biomes each, so a
  region label cannot carry a theological read.
- **Nine landmark reads**, one per god, grounded in the curated ~16-entry
  gazetteer table in `ASHKARR_WORLD_DEFINITION.md` §13.3 (no invented
  defNames): Oasis→Oomo, AncientQuarry/Ruins→Rekko, roads/non-palace Hutt
  holdings→Mob'Unloo, open Dune Sea/AncientLaunchSite-at-Scorch→Ta'Baa,
  Wasteland/DryLake/sw_Sarlacc→Zizzik, LavaLake/AncientHeatVent/volcanic
  province→Sh'kaar, HorrorWastes/nightside stack→Ishko,
  AB_MechanoidIntrusion core→Ohm, the dead-straight AncientAsphaltHighway→
  Ozzik. Ishko is flagged as genuinely short a curated landmark (needs a
  RimSage lookup against the unused ~46-item shortlist before authoring).
- **Four worked contested-tile cases** (the Scald, Rust Cathedral, the twin
  `AncientLaunchSite` instances, the Kiln) — deliberately not resolved to one
  god, per the engine doc's own "no act is clean" doctrine (§2.0d).
- **The tidal day/night split mapped onto real arc bands**: Sh'kaar arc
  0–~74 (bounded by the hard fact that no river tile exists past arc 71.52),
  a terminator battlefield ~74–100 (where the mycoid belt onset, both named
  seas, and the ruled-terminator GelatinousSuperorganism all cluster), Ishko
  ~110–180. Proposes routing a terminator-band landing through the
  already-built Council-of-Voices mechanism (§5c) instead of a single-god
  judgment.
- **Six drafted landing-judgment flavor lines**, Narrator voice
  (2026-08-30 ruling), covering dayside/volcanic/oasis/terminator/nightside/
  the Kiln — real prose, ready to use.
- **The build item spec'd but not built**: the `Page_SelectStartingSite` /
  landing-time hook that runs the annotation function and the two proposed
  ambient arc-residency nudges (generalizing Oomo's existing §3③ terrain
  coupling to Sh'kaar/Ishko) — flagged explicitly as new C#, not attempted
  blind.

## Honesty flags carried into the spec
- F16 asserts "the engine already reads tiles for Oomo and Ishko" — Oomo's
  read is confirmed (§3③ of the engine doc). An equivalent Ishko tile-read
  was not found in the current text; the spec treats it as PROPOSED, not
  pre-existing.
- Every biome/tile-count figure is quoted from `ASHKARR_WORLD_DEFINITION.md`'s
  last recorded pass, not re-measured for this item — several (HorrorWastes,
  AB_OcularForest) have changed counts across multiple passes in that doc's
  own history.

## Status
`doing` — spec complete, awaiting the owner's call to build the C# hook.
Nothing on the frozen map was touched.
