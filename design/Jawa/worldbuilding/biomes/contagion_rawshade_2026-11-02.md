# Rawshade (`RM_Rawshade`): the Contagion creature made from Scaldhide render C

Item `SCALDHIDE_R1_DESIGN_NEW_CREATURE`. Owner, 2026-10-24, on the `owner_escalations_contagion` sheet
(he installed render B as the Scaldhide): *"Make (C) into a new creature, it's very cool. New name,
description, behavior."* The name, description and behaviour are a delegated `design` call
(`design/RimMandrake/delegation_policy.md` §1); a judge reviewed it in place of a card (§4, verdict below).
The defs, art install and C# are owed by the build item named at the end.

## The art it is built on

Render C = `arteval_RM_Scaldhide_r1`, 256 px canvas, kept (not purged) on the sheet. Files under
`D:\ClaudeWork\rimmandrake\artpipe\_artsrc\arteval_RM_Scaldhide_r1_<facing>\arteval_RM_Scaldhide_r1_<facing>.png`:

| facing | sha256 (first 12) |
|---|---|
| south | `a84db7fbaa9d` |
| east | `dc94663f97a2` |
| north | `69a6e7907900` |

What the picture shows: a dome of raw red flesh, veined and folded, held high on four long jointed stilt
legs with hoof-like feet. Black char crusts the top of the dome. The rim hangs down in a wet, scalloped
skirt. It has no head; on the east facing a small fold at the front edge could be a mouth.

## Name

**Rawshade** (`RM_Rawshade`, label `rawshade`). It fits the biome's naming register (owner, 2026-09-27:
*"bizarre one or two-word descriptions of the strangeness of the thing. Eyegore. Fleshsop. Bloody Mess."*):
plain English, grotesque, and it says what the thing is, raw meat that makes shade. Before the judge's
review, `Rawshade` had 0 hits in `src/`, `design/` and `infrastructure/state/items/` (sanity probe:
`Scaldhide` = 14 files). Alternates considered: Fleshtent, Stiltgut.

## Description (the in-game text)

> A dome of flayed meat carried high on four stilt legs, its sun side baked to a black crust and its rim
> hung with a wet, scalloped skirt. When the Burn comes it does not run. It stands still in the open and
> lets the light cook its back, and the small things fleeing the sky crawl into its shade. Then the skirt
> comes down.

## Behaviour

**Role in the biome: the false shelter on open ground.** The Danglemaw makes the tree canopy dangerous to
shelter under (`contagion_grotesque_cast_2026-09-27.md` §3). The Rawshade does the same for open ground,
where there are no trees.

1. **Between Burns.** It is a slow, solitary carnivore. It mostly stands still on its stilts, and its
   skirt sways. It hunts only small prey and does not hunt colonists.
2. **In a Burn.** It is an *armoured native*, the same kind as the Scaldhide and the Crispling (ban 2
   carve-out: Burn damage skips it and it does not dive). The black crust on its dome is where the sun
   burns it. It stops in the open, and **its dome is a canopy**. The Burn already decides shelter by what
   is overhead: a cell is sheltered under a roof, on water, or under a tree's canopy
   (`RM_ContagionSky.Exposed`). A Rawshade standing still has its dome overhead as well, so the cells
   under the dome are sheltered, the same way the cells under a tree are. A Rawshade that is walking
   shelters nothing. The dive search and the Burn damage both call the same `Exposed`, so a native
   that reaches the shade is also spared the damage. When UV-shy natives dive,
   they run to the nearest sheltered cell they can reach (`RM_GameCondition_ContagionBurn.TryDive`).
   On open ground, that cell is often under a Rawshade, and it eats them there.
3. **Colonists.** A colonist caught in a Burn can also take shelter under it. Because it does not hunt
   anything as large as a person, the shade is truly safe, for that colonist only. It fights back if hurt.
   The player has to choose between a creature that will not eat them and the Burn's dose.
4. **A readable sign** (standing ruling: no animal vanishes without a readable sign). Most of its prey
   (Gawpsack, Sparkleech, Doublemaw, ikee) leave a corpse, so a kill leaves blood filth and a
   half-eaten corpse under where it stood. Goo-bud prey (Skinflap, Ogleknot, Sloshbelly) already die
   with `DeathActionProperties_Vanish` and leave 2 to 4 `Filth_Slime`, so their deaths leave a slime
   splash under the dome. After a Burn, the ground under a Rawshade is visibly fouled either way.
5. **Death.** It is a goo-bud line like the five enrichment species: at death it dissolves
   (`DeathActionProperties_Vanish`) into a large slime splash (`Filth_Slime` 5 to 8, larger than the
   Crispling's 2 to 4 because it is bigger). It leaves no corpse, so no meat and no leather (ban 3
   re-absorbable; ban 4 no human-consumable product). This follows the Crispling's wiring in
   `RM_ContagionFauna.xml`.

Not proposed: shade against Direct Sun. The Burn is the Contagion's own UV event, and its exposure test
(roof, water, tree) is a separate predicate from Direct Sun. Direct Sun is one global geometry model
(standing ruling, 2026-10-19), so whether a creature's body shades anyone from Direct Sun belongs to that
model (and its tree shade model), not to this creature.

## Numbers (PROVISIONAL, for the build item)

bodySize 2.2 · MoveSpeed 2.2 · commonality 0.06 (rarer than the Scaldhide's 0.1) · solitary ·
carnivore, `predator true`, `maxPreyBodySize 0.7` (the UV-shy divers Skinflap 0.15, ikee 0.3, Ogleknot 0.35,
Sparkleech 0.45, Doublemaw 0.6, Sloshbelly 0.6 and Gawpsack 0.7 are in range, measured from
`RM_ContagionFauna.xml` `baseBodySize`; a person at 1.0 is not) · wildness 0.97, not trainable · armour Sharp 0.30 / Blunt 0.35 /
Heat 0.70 · tools: *skirt clamp* (Blunt 14), *underside maw* (Bite 16) · lifeExpectancy 20 ·
`MeatAmount 0` / `LeatherAmount 0` · death `DeathActionProperties_Vanish`, `Filth_Slime` 5~8 · texPath `Things/Pawn/Animal/RM_Rawshade/RM_Rawshade` (render C,
256 canvas), adult drawSize set by the size rule at install.

## Wiring the build item owes

- `ThingDef` + `PawnKindDef` `RM_Rawshade` in `src/RimMandrake/Contagion/Defs/ThingDefs_Races/RM_ContagionFauna.xml`,
  following the Crispling's goo-bud pattern.
- Install render C as `RM_Rawshade` art through `art install` (the art ledger), not by copying files.
- Biome: the roster row in `design/Jawa/worldbuilding/biomes/rosters/the_contagion.json`, the `wildAnimals`
  entry with `animalDensity` unchanged, and `RM_Rawshade` added to `armoredNatives` in
  `src/RimMandrake/Contagion/Defs/BiomeDefs/RM_Contagion.xml`.
- C#: a generic `RM_LivingCanopy` def extension (no species list). **Footprint:** a square of
  Chebyshev radius `r = round(0.45 × drawSize)` around the pawn's cell. The 0.45 comes from measuring
  the dome: on the south render the opaque width is 229 of 256 px (alpha bbox x 9 to 238), so the dome is
  about 0.9 × drawSize cells wide, and half of that is the radius. At an adult drawSize of 2.2 to 3.3,
  r = 1, which covers 3 × 3 cells. **When:** only while the pawn is alive, spawned, not downed and not
  moving (`pather.Moving` false). Each Burn pulse, compute that cell set once, then have
  `RM_ContagionSky.Exposed` treat its cells as covered, the same as a tree's cell. The arithmetic goes in
  `RM_SkyKernel.Exposed`, whose inputs today are in-bounds, roofed, water and tree. "Under a living
  canopy" becomes a fifth parameter, and it gets an offline unit test that covers the radius formula
  and the moving/standing gate.
- Proof: a `burn_forced` row showing that a UV-shy native dives under a Rawshade and is counted as
  `sheltered`.
- Sheet amendment to `the_contagion.md` admitting it, like the five enrichment species.

## Judge verdict

Recorded in `design/Jawa/worldbuilding/biomes/contagion_rawshade_2026-11-02.judge.md`.
