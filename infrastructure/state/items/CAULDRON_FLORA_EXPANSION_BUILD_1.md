# CAULDRON_FLORA_EXPANSION_BUILD_1 — Build 6 admitted Cauldron flora

From `BEDAZZLE_FLORA_EXPANSION_1`. Admitted by question card 2026-10-02, all six. Look/behaviour
source: `design/Jawa/worldbuilding/biomes/cauldron_flora_expansion_pitch_2026-10-02.md` Pitches 1-6.
Coordinate with `CAULDRON_MECHANICS_BUILD_1` and `CAULDRON_FULL_RENAME_1` (same mod).

## spec

Mod: `src/RimMandrake/Cauldron/` (packageId `mandrake.rm.cauldron`). ALL defNames **`RM_`** (the
existing roster is all `RM_`-owned in `Defs/ThingDefs_Plants/RM_CauldronFlora.xml`; add the new
plants there or a sibling file). Items in `Defs/ThingDefs_Items/RM_CauldronItems.xml`. No green, no
leaves, nothing explodes, no warm light, no new heat. Palette gaps being filled: sulfur yellow,
cobalt blue, amber-orange, fuchsia, violet-lavender, interference colour.

1. **`RM_Tsevrix`** — FOOD. Sulfur-yellow waxy bladders, cinnabar veins. Raw -> new
   **`RM_TsevrixPulp`**: raw food, `ingestible.outcomeDoers` `IngestionOutcomeDoer_GiveHediff`
   `ToxicBuildup`. New RecipeDef roasts it into safe food (campfire/stove). Near vent ground and
   Xithess stands.
2. **`RM_Ixalith`** — BEAUTY. Black wire-stalks with oil-slick interference films. `harvestYield 0`,
   high `Beauty`, low `MaxHitPoints`; solitary in still pockets.
3. **`RM_Fexxil`** — HAZARD. Cobalt glass-burr thicket, high `pathCost`. Reuse the built
   `RimMandrake.EnvironmentalHazards.CompProperties_ContactVenom`
   (`src/RimMandrake/EnvironmentalHazards/Source/CompContactVenom.cs`) with a new DamageDef whose
   `additionalHediffs` gives `ToxicBuildup`. Adds a `mandrake.rm.environmentalhazards` dependency to
   Cauldron's About.xml (load-order entry too). Yield: small glass shards or none.
4. **`RM_Sessarix`** — MATERIAL. Amber-orange resin boils with tar-black core; on rock/ruin footing
   only, never soil; very slow regrowth. `harvestedThingDef` = vanilla `Chemfuel`, small yield. Keep
   rare (free-fuel-faucet risk).
5. **`RM_Kissaveth`** — HAZARD. Lavender gas-bladders. Vanilla `CompProperties_GasOnDamage`
   (`type ToxGas`) as on our race defs: damage splits it and it leaks tox gas (leak, NOT explosion).
   ⚠️ UNMEASURED: whether vanilla cut/harvest applies damage to a plant; if cutting does not trigger the
   puff, add a release-on-cut comp (M) using `CompTickLong`-safe code only (no `CompTick`).
6. **`RM_Selvix`** — MATERIAL (medicine). Fuchsia fleshy rosette, white crystal frost, wine-red
   heart; rings on stained ground. `harvestedThingDef` = vanilla `MedicineHerbal`.

Roster: `Defs/BiomeDefs/RM_Cauldron.xml` `<wildPlants>` (shorthand
`<DefName>commonality</DefName>`, 11 rows today, all `RM_`). No Utinni patch targets either
Cauldron BiomeDef (verified in pitch), so the BiomeDef is the only place. Proposed: Tsevrix 0.3,
Ixalith 0.12, Fexxil 0.25, Sessarix 0.15, Kissaveth 0.2, Selvix 0.2. The frozen `RUT_Cauldron` twin
stays untouched.

Mod Settings: `floraExpansionEnabled` (default true) in `RM_CauldronMod.cs` settings (beside
`metalYieldEnabled`); off removes the six rows; Fexxil's venom is its own toggle
(`fexxilVenomEnabled`, default true).

Art: `infrastructure/artpipe/art_lists/cauldron_flora_expansion_2026-10-02.csv`; item icons owed after
defs exist.

## criteria

Script checks in `src/RimMandrake/Cauldron/validation.py`:
- 6 plants + `RM_TsevrixPulp` + the roast recipe resolve via `get_defs` (`success`/`foundCount`/
  `notFound` — an unresolved comp class discards the def silently).
- `RM_Cauldron` live wildPlants contains all six (XML element parse, not `<li>`); control: an original
  row (`RM_Xithess`) still present; toggle off removes the six.
- Tsevrix pulp ingest -> `ToxicBuildup` hediff added; roasted product ingest -> none (both arms).
- Fexxil: pawn contact scratch applies `ToxicBuildup` via ContactVenom; control: a Palefloss-free
  plain plant tile does not.
- Kissaveth: damage it -> tox gas appears on its cell; read the gas grid, assert NO explosion event;
  cut/harvest arm recorded explicitly (PASS or documented FAIL -> comp owed).
- Sessarix harvest yields `Chemfuel`; Selvix yields `MedicineHerbal`; Ixalith `harvestYield 0`.
- Sessarix spawn rule: never on soil terrain (spawn sample over soil -> 0).
- No new plant has `CompTick` override.
