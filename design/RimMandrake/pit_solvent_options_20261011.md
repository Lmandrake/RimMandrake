# Slime pit solvent: what is "the Rot's finest"? Options, 2026-10-11

Item: `GELATINOUSSLIME_PIT_SOLVENT_1`. Status: options only, nothing built.

## 1. What already exists

Read from `src/` before anything was proposed:

- **The free slice of this item is built** (`d1cdebec5`):
  `src/RimMandrake/GelatinousSlime/Defs/ThingDefs_Buildings/SlimePitSolvent.xml` adds
  `RM_Render_Toxipotato` (`RawToxipotato` → `RawPotatoes`) and `RM_Render_TwistedMeat`
  (`Meat_Twisted` → `MealSimple`) to `RM_SlimePit`. Both are switched on and off by
  `SlimeSettings.pitSolvent` through `Source/PitSolvent.cs`, which **hard-codes those two
  defNames**, so any new pit recipe has to be added to that list or the toggle will not cover
  it. The glurro salve (spec 2) has been cut (`c46bfc123`).
- **What is still missing is spec 3**: an input that is "the Rot's finest". No def in `src/`
  is called that. The sheets give two leads. `the_slime.md` §7 says the pit renders down
  "the indigestible, the toxic, the dangerous". `the_rot.md` §7b lists **ambrosyx shroom**
  as "an ambrosia analog — a gourmet-line candidate".
- **The Rot's ingestibles** (parsed from `src/RimMandrake/TheRot/Defs`, 31 ThingDefs with an
  `<ingestible>`). Three can stand as "dangerous or indigestible":
  - `RM_AmbrosyxShroom`: `DesperateOnly`. It causes `AmbrosiaHigh`, `AmbrosiaTolerance` and
    `AmbrosiaAddiction`. Its description says it "tastes wonderful".
  - `RM_MushroomLog`: `DesperateOnlyForHumanlikes`, `FoodPoisonChanceFixedHuman` 0.02. Its
    description says it is "largely indigestible". It is harvested from `RM_Arpeau` and
    `RM_GreenArpeau`.
  - The live ingredients and preparations (`RM_LiveIngredient_*`, `RM_Tea_*`,
    `RM_Symbiont_*`). Hard ban 4 rules these out (see §4).
  - Not food at all: `RM_BlastSpore` (fuel and chemfuel), `RM_ToxiChitin`.
- **Existing solvents and dissolvers**: none of them is a food mechanism.
  `RM_WeakTarSolvent` and `RM_StrongTarSolvent` (TheSump) release tar. `RM_Reaction_TarAcid`
  together with `RM_ReactionVat` (FlowWorks, `RM_LiquidReactionDef`) is a reaction between
  two liquids. `RM_Liquid_AcidWater` is a liquid. `RM_PourSolvent` is a job. Nothing here
  makes a toxic food safe, so no existing def is being reinvented.
- **Slime as a liquid exists**: the canal fluids `RM_Fluid_SlimeRed`, `RM_Fluid_SlimeGreen`,
  `RM_Fluid_SlimeWhite` and `RM_Fluid_SlimeYellow`
  (`src/RimMandrake/FlowWorks/Defs/Canals/FluidDefs/FlowWorks_Fluids.xml`) each have a
  `fillTerrainSuperdeep`. The superdeep pit itself is ruled but unbuilt
  (`PIT_SUPERDEEP_COLLAPSE_1`).
- **Tier fact**: `src/RimMandrake/Biomes.compose.json` puts both `GelatinousSlime` and
  `TheRot` at wave 2, and `compose_wave` is 2. Both therefore ship inside the one mod
  `mandrake.rm.biomes`, so a slime-pit recipe that names a Rot item resolves without any
  `MayRequire`. UNMEASURED: whether turning the Rot's per-biome toggle off removes its item
  defs or only stops them appearing.
- The vault flesh seal (`07bd43cb2`, `RUT_VaultFleshSeal` + `CompFleshSeal`) is a dissolve
  hook on a **structure**. It has nothing to do with food and gives this item nothing to
  build on.

## 2. The decision and its questions

**Decision:** which Rot thing goes into the slime pit as "the Rot's finest", and what that
recipe does. Three separate questions sit inside it:

1. **(primary) Is the Rot's finest a luxury or a staple?** The sheet calls it "the gourmet
   chain", but it also says the pit takes "the indigestible".
2. **Is the pit a bench or a hole full of slime?** The owner described it as "grown full of
   pure slime… then cleaned out and refilled". The pit ruling (`PIT_SUPERDEEP_COLLAPSE_1`)
   says a pit is a superdeep cell filled with a FluidDef, and slime is one of his listed fluids.
3. **Free or campaign?** Spec 3 says the patch comes from `src/RimUtinni/`. However, both
   inputs below are `RM_` free-tier defs, shipped in the same mod as the pit.

**Validity floor (fixed before any option was scored):** every input and output is an existing
defName in `src/` or vanilla, or a new def is named as a cost. No option may break a Rot hard
ban (`the_rot.md` §6). Every DLC is assumed present.

## 3. Options

### A. The luxury: ambrosyx with the addiction taken out

- **Mechanic:** a pit recipe that takes `RM_AmbrosyxShroom` and gives a lavish ingredient or
  dish. The slime takes away the addiction and keeps the taste.
- **Builds on:** `RM_AmbrosyxShroom`, `RM_SlimePit`, and the vanilla `AmbrosiaHigh` (the
  joy/mood effect is kept or dropped as a design choice). The output is either vanilla
  `MealLavish` (no new def) or one new named delicacy ThingDef (the abyss and rot sheets'
  "named ingredients, lavish-meal multipliers, trade goods").
- **Cost:** S if the output is `MealLavish`: one RecipeDef, plus one line in `PitSolvent.cs`.
  M if the output is a new delicacy: a ThingDef, its art, its tuning, and possibly a
  meal-quality hook.
- **Risk:** it removes the one cost that ambrosyx carries, so the slime becomes a way to
  launder a drug, which may be exactly the joke he wants. It also needs ambrosyx to be rare
  enough that the recipe stays a treat.
- **Unique contribution:** it is the only option that makes the chain actually *gourmet*, and
  it uses the input the Rot sheet itself names as the candidate.

### B. The staple: mushroom logs become food

- **Mechanic:** a pit recipe that takes `RM_MushroomLog` (the Rot's timber, "largely
  indigestible") and gives `RawFungus` or `MealSimple`.
- **Builds on:** `RM_MushroomLog` (from `RM_Arpeau`/`RM_GreenArpeau`), `RM_SlimePit`, and
  vanilla `RawFungus`/`MealSimple`. No new def.
- **Cost:** S: one RecipeDef, plus one line in `PitSolvent.cs`.
- **Risk:** it is not "finest". It answers the "indigestible" half of the sheet's sentence,
  not the gourmet half. It also turns a building material into food, which might crowd out the
  Rot's food scarcity if the yield is set high.
- **Unique contribution:** it is the only option that changes survival. A slime colony with
  Rot timber has a food supply, while A only gives it a mood dish.

### C. The vessel: the pit is a superdeep cell full of slime

- **Mechanic:** a superdeep cell filled with one of the `RM_Fluid_Slime*` fluids. A raw toxic
  or indigestible item hauled into it dissolves over time into its safe product, and the fill
  is used up, so it has to be "cleaned out and refilled" as he described. The inputs would be
  the same as A, B and the two built recipes. This option is about **how** the pit works, not
  what goes into it.
- **Builds on:** `RM_Fluid_SlimeGreen` (or any of the four colours) and its
  `fillTerrainSuperdeep`, the depth-4 cell of `PIT_SUPERDEEP_COLLAPSE_1`, and the FlowWorks
  fill/volume model. `RM_SlimePit` would either stay as a cooking bench or be retired.
- **Cost:** L. It needs C#: a dissolve tick on an item lying in a slime-filled cell, and fill
  being used up. It is blocked on the superdeep pit, which is unbuilt.
- **Risk:** it waits on the largest unbuilt item in FlowWorks. It also gives "pit" two
  meanings for one name, because `RM_SlimePit` is a *building* today, while his pit ruling
  says a pit is a cell and not a building.
- **Unique contribution:** it is the only option that matches his own description of the pit
  as a vessel you fill, use up and refill, and that makes it the same object as his one-pit
  model.
- **Cheap interim, not a separate seat:** the existing bench could consume `RM_RawSlime` as a
  charge (vanilla `CompProperties_Refuelable`), which gives "refill" without the superdeep work.

**Free or campaign, whichever option is chosen:** both `RM_AmbrosyxShroom` and `RM_MushroomLog`
are free-tier and ship in `mandrake.rm.biomes` with the pit. The cheapest correct place for
the recipe is therefore `SlimePitSolvent.xml` itself, not a RimUtinni patch. Spec 3's
"campaign" wording would only be needed if the finest were a Star Wars or Utinni thing, and
neither candidate is. The doc assumes the free placement unless he says otherwise.

## 4. Rejected at the floor

- **The live ingredients and preparations** (`RM_LiveIngredient_AgelessCap`, `…_RegenerantVeil`,
  `…_EuphoricCrown`, `RM_Tea_*`, `RM_Symbiont_*`): these are the most obvious "finest" and they
  break hard ban 4. Rendering them into a meal produces a version that can be refrigerated or
  exported, and his ruling forbids that: *"you come to the biome and prepare it in your vessel,
  right now."*
- **`RM_BlastSpore`**: dangerous, but it is fuel, not food. Nothing it could be rendered into
  makes sense as cuisine.

## 5. The question for the owner

> The slime pit already makes toxipotatoes and twisted meat safe to eat. Its last recipe needs
> one thing from the Rot to be "the Rot's finest". Which should it be?
> **(a) Ambrosyx shroom.** The slime keeps the taste and removes the addiction, giving a
> luxury dish. This is cheap and on-theme, but the slime becomes a way to clean a drug.
> **(b) Mushroom logs.** The Rot's inedible timber becomes everyday food. This is cheap and
> keeps slime colonies fed, but it is a staple, not a delicacy.
> **(c) Wait, and rebuild the pit as a hole filled with slime** that you drop things into and
> refill, the way you first described it. This matches your pit ruling, but it is a large job
> and it waits on the unbuilt superdeep pit.
> (Either way, both Rot items ship in the same biomes mod as the pit, so the recipe goes in the
> free mod, not the campaign layer, unless you say otherwise.)
