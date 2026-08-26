# Player.log harvest — 2026-08-26, seat CHECK, game down

🔴 **`Player.log` rotates to `Player-prev.log` on launch and the old prev is destroyed.** This
folder is the only surviving copy of that load's evidence. Harvested from the 973,786-byte log of
the session that ran the C40, template-engine and world-port work, full 582-mod list.

| file | what |
|---|---|
| `cherrypicker_removals.txt` | **1,211 defs Cherry Picker removed** — 1,162 ThingDef · 25 BiomeDef · 8 IncidentDef · 7 PawnKindDef · 5 HediffDef · 2 RecipeDef · 2 GeneDef |
| `config_errors.txt` | 16 distinct `Config error in …` lines |
| `cross_reference_failures.txt` | 10 distinct `Could not resolve cross-reference …` |
| `xml_errors.txt` | 3 distinct `XML error: …` |

## What the harvest settled

**🔴 Ours, and now diagnosed — three apparel config errors.** `Jawa_Tribal_Scavenger` and
`Jawa_Tribal_Elder` carry `apparelRequired` entries that cannot be worn together. Full mechanism and
fix in `JAWA_HOOD_NEVER_WORN_1`; the game had been printing it every load and nobody had read it.

**✅ Not ours — the 8 `BMT_*` and `VWE_Tool_Whip` cross-reference failures.** Tested against the
removal set: **none of them is a Cherry Picker cut**, so they are absent because their source mod is
not installed or not active. `Biomes! Caverns` and a TraderGen↔Vanilla-Weapons-Expanded integration.
The `TG_Husbandry` NullReferenceException is the same root cause —
`StockGenerator_SingleDef.ConfigErrors` throws when its `thingDef` is null, and the null is
`VWE_Tool_Whip`. Third-party, not actionable here, recorded so it is not re-investigated.

**✅ The 25 cut BiomeDefs do not touch Ash'karr.** Checked every one against the live tile export:
`AB_IdyllicMeadows` `AG_NereidPocketPlane` `AG_PocketPlane` `BorealForest`
`COMIGO_GreaterSwamp_Cold` `COMIGO_GreaterSwamp_Temperate` `ColdBog` `GlacialPlain` `Grasslands`
`Labyrinth` `MetalHell` `Savanna` `TemperateForest` `TemperateSwamp` `TropicalRainforest`
`TropicalSwamp` `Tundra` `Wetland` and seven `ZBiome_*`. **Zero of them is used by any of the
21,872 tiles.** Ash'karr uses 30 distinct biomes and every one survives — the curation is doing
exactly what it was meant to on a desert world.
And the three biomes `BIOME_FLORA_LOOKS_RIGHT_1` needs are all alive with real tile counts:
**Desert 4,205 · HorrorWastes 1,711 · AB_MycoticJungle 1,939.**

**🔴 `PawnKindDef/Ghoul` IS a Cherry Picker cut**, which corrects a claim in
`xenotype_nonfaction_routes_2026-08-26_CHECK.md` — see that file's own correction note.

**⚙️ Cosmetic, recorded not chased:** nine `Sign*` defs are "impassable, player-buildable building
that can be shot/seen over"; two Techprint descriptions have trailing whitespace; three XML errors
name fields that no longer exist (`<wildness>` on RaceProperties, `<drawStyleCategory>` on
BuildingProperties, `<loadBottom>` on ModMetaDataInternal). All third-party.
