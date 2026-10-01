# ABYSS_DARK_BUILD_1 — the Dark, the Unveiling, the ghorrumak storm call (full, with strength slider)

Biome: the Abyss (`RM_Abyss` in `src/RimMandrake/Abyss/`, composed into `mandrake.rm.biomes`; campaign twin `RUT_Abyss`). Review/spec: `design/Jawa/worldbuilding/biomes/blackcrags_bedazzle_review_2026-09-30.md` (written under the old names Forsaken Crags / Black Crags; paths there predate the rename). Owner rulings of volley turn 1 (2026-09-30): the sitting item `BLACKCRAGS_BEDAZZLE_SITTING_1` and the report's 'Turn 1 rulings' section. Rule: every mod ships Mod Settings; the free `RM_` tier carries invented content, canon only through Utinni (Q11a).

## spec

Owner chose the full spine by question card 2026-09-30 (decision taken by question card): report §5 items 1-3.
1. **The Dark is real air**: blinds and swallows lamplight; **heat opens clear pockets**, so a warm base sees and a cold one is blind. Fighting here gets harder. Ships with a **strength slider** in Mod Settings (0 = off, graceful degrade).
2. **The Unveiling**: rarely the Dark lifts entirely for a few hours (sheet 4b, owner-authored weather); reveals what the Dark hides (durrgak rings etc., report §5 item 2).
3. **Ghorrumak storm call**: thunder in the storms is sometimes the ghorrumak (`AA_Behemoth` roster row, art approved `crags_ghorrumak_*`) calling. The ghorrumak and nighthrumbo are rostered but wired into neither BiomeDef today; wire them in the build.
Heat is the ONE vanilla heat (owner 2026-09-29): no new hediff. Search src/ before inventing: `RM_CompPlantPredator`, light/lamp aversion `CompLightAversion` and `SOLAR_HEAT_EXPOSURE_1` are neighbours. Etchfall/gust/turbine/lamp-crop items (report §5 items 4, 7, 8, 10) were NOT ruled on at turn 1; do not build them from this item.

## criteria

- Dark exists as a weather/overlay with a heat-cleared pocket mechanic and a Mod Settings strength slider (default = shipped strength).
- Unveiling exists and is rare.
- Ghorrumak wired into `RM_Abyss` (patch-added for the campaign cast per the twin rule) and storm-call implemented.
- Mod Settings toggles per feature; all-off degrades to plain donor weather.
- Rebuilt DLL committed with its `.srchash`; `RM_CreatureBehaviors.csproj` Compile lines if that assembly is touched.

## verify

Offline build + selftests green; live proof is a joint session, never an unattended flyer/visual hunt.
