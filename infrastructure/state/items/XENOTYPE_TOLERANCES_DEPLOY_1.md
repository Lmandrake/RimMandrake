## spec
🔴 **DECIDE authored the renormalization; the deploy is BUILD's** — owner's ruling 2026-08-23.

**Deploy `src/Jawa/Jawa_Patches/Patches/XenotypeTolerances_Ashkarr.xml`** (committed `63e1bfa7`),
12 operations, 5.7 KB. Rule and reasoning: `design/Jawa/mods/xenotype_tolerances.py`.

**Six authored xenotypes get the widest realistic vanilla adaptation** — `MinTemp_LargeDecrease`
(−20) and `MaxTemp_LargeIncrease` (+20), replacing any lesser gene in the same exclusion group.

| xenotype | before | after |
|---|---|---|
| MandrakeJawa · RimMandrakeTusken | 20.5 … 46 | **−4 … 46** |
| RimMandrakeJawa | 16 … 46 | **−4 … 46** |
| RimMandrakeHutt | 16 … 36 | **−4 … 46** |
| Jawa_Xeno_Gamorrean | 16 … 26 | **−4 … 46** |
| RimMandrakeWookiee | 6 … 26 | **−14 … 46** (`Furskin` is in the `Fur` group and stacks) |

🔑 **Vanilla `Human` is deliberately NOT patched, and that is the design.** Every one of our 72
pawnkinds is `race=Human`, so widening Human would adapt every offworlder, raider and visitor at
once and delete the clothing-and-heaters survival loop. **Natives adapt; outsiders dress for the
planet.**

## Watch out
⚠️ **`MinTemperature` / `MaxTemperature` are exclusionTags — only ONE gene of each may apply**, so
the patch REMOVES a lesser tier before adding the larger. A collision here fails silently.
⚠️ **`XenotypeDef.genes` is a plain `List<GeneDef>`, so `<li>` is correct** — verified against
`XenotypeDef.cs`. This is NOT the `LoadDataFromXmlCustom` field where an `<li>` discards the whole
def, the trap that cost 26 BiomeDefs.
⚠️ **METABOLISM COST, stated not buried.** Both genes are `biostatMet −2`, so every adapted species
eats more; for MandrakeJawa and RimMandrakeTusken the swing is **−3**, because the `+1` penalty gene
they shed was paying for itself. On a scavenger world where food is scarce this is a real balance
change — and it is the reason not to reach for a bigger gene.
⛔ **This does NOT need the biome cast** (unlike `ANIMAL_TOLERANCES_DEPLOY_1`) and has no ordering
dependency. It can ship alone.

## verify
Generate a pawn of each authored faction and read its comfy range in the Gear tab: **−4 … 46**,
and **−14 … 46** for a Wookiee. Zero red errors naming `XenotypeTolerances_Ashkarr`, and all six
xenotypes still generate — a silent exclusionTag collision shows up as a xenotype that stops
producing pawns, not as an error.

## criteria
- [ ] All six xenotypes read their new band in game.
- [ ] All six still generate pawns.
- [ ] No red errors.
