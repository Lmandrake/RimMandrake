# ROT_SPORE_ALLERGY_PORT_1 — our own spore allergy (people and animals) replaces the Alpha Biomes pair in the free Rot

Caused by `ROT_SCORING_SITTING_1` (turn 1); ruled earlier at the 2026-09-24 cast sitting (*"Spore allergy:
port our own. Two RM_ HediffDefs of our own replace the `AB_Disease_SporesAllergy` pair so the free mod keeps
its signature disease without Alpha Biomes"*, decision taken by question card 2026-09-24), never built.
Free tier, `mandrake.rm.therot`. Design: `design/Jawa/worldbuilding/biomes/rot_bedazzle_review_2026-10-02.md`
§1 (a), §4 row 0, §8; `design/Jawa/worldbuilding/biomes/rot_rm_cast_proposal_2026-09-24.md` (Rulings).

## spec

1. Read the donor pair in the def dump / RimSage-equivalent for Alpha Biomes (`AB_Disease_SporesAllergy`,
   `AB_Disease_AnimalSporesAllergy`: the `IncidentDef`s and the `HediffDef`s they give) for shape only;
   author ours from vanilla parts (the vanilla disease incident worker and a severity-staged `HediffDef`), no
   C# unless a vanilla worker cannot express it.
2. **Defs:** `HediffDef RM_SporeAllergy` (humanlike), `HediffDef RM_AnimalSporeAllergy` (animals), and their
   `IncidentDef`s `RM_Disease_SporeAllergy`, `RM_Disease_AnimalSporeAllergy`. Our own label and description
   (a reaction to the Sheen's spores: wheezing, swelling, weeping eyes; tendable; immunity race), no donor
   text copied. Interaction with the Sheen: none new (the exposure ladder is separate and ruled).
3. **Swap** in `src/RimMandrake/TheRot/Defs/BiomeDefs/RM_TheRot_Biome.xml` (lines ~60, ~64): the two
   `diseaseInc` entries become ours, same commonalities, no `MayRequire`.
4. **Not in scope, recorded:** `RM_Contagion` (`src/RimMandrake/Contagion/Defs/BiomeDefs/RM_Contagion.xml`
   lines ~81, ~85) and the frozen twins `RUT_TheRot`/`RUT_Contagion` also name the donor pair. The twins stay
   frozen; whether the Contagion takes our allergy is that biome's sitting's call. The defs are written so it
   could (no Rot-only condition inside them).
5. Mod Settings: on/off and an incidence multiplier in the Rot screen's Biome section.

Depends on: none.

## criteria

Deterministic, in `THE_ROT_FIRST_SCRIPT_1`'s `validation.py`:
- `HediffDef/RM_SporeAllergy`, `HediffDef/RM_AnimalSporeAllergy`, `IncidentDef/RM_Disease_SporeAllergy`,
  `IncidentDef/RM_Disease_AnimalSporeAllergy` resolve (`foundCount` = 4) with Alpha Biomes **not** loaded.
- Offline XML parse: `RM_TheRot`'s `diseases` names no `AB_` def.
- Firing `RM_Disease_SporeAllergy` on a Rot test map adds `RM_SporeAllergy` to ≥ 1 colonist; the animal one
  adds `RM_AnimalSporeAllergy` to ≥ 1 animal; neither adds anything to the other kind.
- Toggle off: the incident's base chance on a Rot map reads 0.
</content>
</invoke>
<invoke name="Bash">
<parameter name="command">cd /home/mandrake/rm/bench/infrastructure/state/items; head -1 ROT_*.md