# Fauna tolerance census — Law 5 violations (offline, 2026-09-11)

Full census: `design/Jawa/worldbuilding/fauna_tolerance_census_2026-09-11.csv` (297 rows).
Law: comfy range must cover assigned domain envelope [p05,p95] of tile temp_c, +15 °C both sides (RULED 2026-09-11). Spec: `beast_normalization_spec.md` §2d.

Sources (sha256/16): `decisions=e45830e93d80fe77` · `move_mapping=6ed495e291cbfab4` · `tiles=756d9ffc8a22c3d2` · `animals_csv=ccbe56df39c9a157` · `modsconfig=b2b45866508f3a7f`

## Verdict: 196 of 279 measurable rostered animals VIOLATE · 83 OK · 15 ENV_UNMEASURED (fall_line / lantern_deeps / wreck_fields have no painted tiles) · 3 XML_UNMEASURED (def not in the base-XML animal set)

MEASURED from mod XML (inheritance-resolved, PRE-patch) vs the painted worldmap. The ruling's "23 flagged narrows" was a pre-law flag count from the graphs artifact — under the ruled law the true count is 196: most mod animals ship Earth-calibrated ranges and the assigned domains are extreme (deep_desert p95 61.6 °C, propane_lakes p05 −76.5 °C, rust_cathedral/scarlands ~+58–66 °C).

## Violations by mod

| mod | violations |
|---|---:|
| Star Wars Animal Collection (Continued) | 71 |
| Alpha Animals | 59 |
| Biomes! Caverns | 20 |
| RimMandrake: SW — Bestiary | 15 |
| Biomes! Polluted Lands | 13 |
| Vanilla Genetics Expanded | 9 |
| RimUtinni Patches (Jawa campaign) | 3 |
| Odyssey | 2 |
| Jurassic Rimworld - Dinosaurs Only (Continued) | 1 |
| They! (Giant Ants) | 1 |
| Alpha Genes | 1 |
| ReGrowth 2 | 1 |

## Violation rate by assigned biome (animal counted once per assigned biome)

| biome key | violating / measurable |
|---|---:|
| arid_shrubland | 37 / 38 |
| desert | 35 / 48 |
| the_miasma | 23 / 25 |
| the_greentide | 15 / 17 |
| the_rot | 15 / 21 |
| the_twilight_deep | 14 / 15 |
| the_contagion | 13 / 16 |
| poison_forest | 12 / 22 |
| wasteland | 11 / 13 |
| the_cracked_lands | 11 / 13 |
| the_fever_wood | 11 / 11 |
| deep_desert | 10 / 15 |
| dune_sea | 10 / 15 |
| the_scald | 8 / 8 |
| the_scarlands | 7 / 14 |
| the_pyrelands | 7 / 9 |
| weeping_stones | 7 / 9 |
| the_grey_deep | 6 / 8 |
| forsaken_crags | 6 / 14 |
| the_webwork | 5 / 6 |
| nightside_ice | 4 / 7 |
| the_forge | 4 / 8 |
| terminator_sea | 3 / 4 |
| the_slime | 3 / 6 |
| the_blue_desert | 2 / 2 |
| the_rust_cathedral | 1 / 3 |
| the_sump | 1 / 5 |
| the_propane_lakes | 1 / 4 |
| fall_line | 0 / 2 |

## 25 worst offenders (largest total gap, °C)

| defName | mod | biomes | need | has | coldGap | heatGap |
|---|---|---|---|---|---:|---:|
| AA_Wildpawn | Alpha Animals | the_greentide+the_rot | -53.1..74.9 | -15..40 | 38.1 | 34.9 |
| Vapaad | Star Wars Animal Collection (Continued) | the_blue_desert | -71.6..-11.7 | 0..350 | 71.6 | 0 |
| AA_Swarmling | Alpha Animals | the_contagion+the_rot | -53.1..66.5 | -10..40 | 43.1 | 26.5 |
| AA_Thunderbeast | Alpha Animals | the_blue_desert | -71.6..-11.7 | -10..45 | 61.6 | 0 |
| AA_Wildpod | Alpha Animals | arid_shrubland+the_rot | -53.1..60.9 | -15..40 | 38.1 | 20.9 |
| AA_ShockGoat | Alpha Animals | nightside_ice | -62.4..-5.6 | -5..40 | 57.4 | 0 |
| BMT_FungalMantis | Biomes! Caverns | the_rot | -53.1..31.4 | 0..60 | 53.1 | 0 |
| BMT_FungalWeevil | Biomes! Caverns | the_rot | -53.1..31.4 | 0..60 | 53.1 | 0 |
| ShiroTrap | Star Wars Animal Collection (Continued) | the_rot | -53.1..31.4 | 0..60 | 53.1 | 0 |
| Snoruuk | Star Wars Animal Collection (Continued) | the_rot | -53.1..31.4 | -5..30 | 48.1 | 1.4 |
| BMT_Stoneback | Biomes! Caverns | arid_shrubland+desert+the_scarlands+wasteland | -28.1..80.9 | 0..60 | 28.1 | 20.9 |
| AA_DecayDrake | Alpha Animals | poison_forest+the_miasma | -22.1..73.2 | -10..40 | 12.1 | 33.2 |
| BMT_BovineBeetle | Biomes! Caverns | the_rot | -53.1..31.4 | -10..40 | 43.1 | 0 |
| BMT_SmogMoth | Biomes! Polluted Lands | the_rot | -53.1..31.4 | -10..57 | 43.1 | 0 |
| BMT_MossBeetle | Biomes! Caverns | arid_shrubland | -22.1..60.9 | 0..40 | 22.1 | 20.9 |
| JOE_Cephalope | RimUtinni Patches (Jawa campaign) | deep_desert+desert+dune_sea | -5.5..76.6 | 0..40 | 5.5 | 36.6 |
| AA_Terramorph | Alpha Animals | the_scarlands+wasteland | -28.1..80.9 | -40..40 | 0 | 40.9 |
| BMT_CrystalFairyMole | Biomes! Caverns | the_scarlands | 43.1..80.9 | -50..40 | 0 | 40.9 |
| Iriaz | Star Wars Animal Collection (Continued) | arid_shrubland+desert+the_pyrelands | -22.1..78.8 | -10..50 | 12.1 | 28.8 |
| AA_Aerofleet | Alpha Animals | terminator_sea+the_forge+the_grey_deep+the_twilight_deep | -24.5..70.8 | -25..30 | 0 | 40.8 |
| AA_ColossalAerofleet | Alpha Animals | terminator_sea+the_forge+the_grey_deep+the_twilight_deep | -24.5..70.8 | -25..30 | 0 | 40.8 |
| AA_TetraSlug | Alpha Animals | the_rust_cathedral | 43.7..80.2 | -10..40 | 0 | 40.2 |
| Gizka | Star Wars Animal Collection (Continued) | arid_shrubland+deep_desert+desert+dune_sea+the_greentide | -22.1..76.6 | 0..60 | 22.1 | 16.6 |
| AA_Helixien | Alpha Animals | poison_forest+the_contagion | -22.1..66.5 | -10..40 | 12.1 | 26.5 |
| AA_Agaripawn | Alpha Animals | the_rot | -53.1..31.4 | -15..40 | 38.1 | 0 |

## What the live harvest must confirm (this census cannot)

- Post-patch stat values: PatchOperations (any mod's), gene/comp/hediff stat offsets and CherryPicker state are invisible to base-XML parsing — the 196 list is pre-patch. Re-run the check on the live `jawa/animal_stats` harvest AFTER the modlist restore, fingerprint-matched.
- The 3 XML_UNMEASURED (GR_Mantistanis, MA_Sporemole, VAEWaste_Hydra) and the OuterRim droids (no `<race>` in scanned base XML — likely generated or inactive in the NEXT-load ModsConfig).
- Tile `temp_c` is the map-gen mean; realized in-game seasonal/diurnal extremes per biome (the +15 margin is the ruled cover, not a measured swing).
- Plots for the owner's sitting ride the POST-restore harvest — out of scope for this offline pass.
