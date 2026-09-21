# DESERT_SHADE_PLANTS_DESIGN_1 — design pass on the desert's defending shade plants

## what is wrong

desert.md §4b ("The shade plants, which defend") names 2-3 plants that hold
the desert's shaded patches by injury — "strange vines and thorny venom
writhing around some areas" and "mossy growth leaching nutrients as fast as it
can" — and none has a def. `DESERT_SIGNATURE_FLORA_1` authored the ultracactus
and filed this item and `DESERT_STAGGERSEED_BUILD_1` as its correctly-scoped
successors rather than building all three at once.

## why it matters

These plants are the reason "a patch that looks like the best shelter for a
kilometre may be somebody's" (§4b) — they are load-bearing for the desert's
"the shelter is the trap" thematic (§4) and for the patch-as-commons/stratified
competition idea. Without them, every shaded patch in the biome is free real
estate, which contradicts the frozen sheet.

## the work — this item is DESIGN, not build

Two named mechanisms, both **thorn/contact damage dealt to a pawn or animal
that enters or lingers in the plant's territory** — and neither has a native
`CompProperties` equivalent in 1.6:

- `grep -rln "CompProperties_Thorn\|CompProperties_Contact.*Damage" "$RW/Data"`
  returns nothing (checked against the tier ladder in `rimworld-modding`'s §3 —
  "prove a comp exists before scoping tier b around it"). The nearest vanilla
  shapes are `CompProperties_SelfHeal` on plants (no damage-dealing) and
  `Hediff`-driven "toxic gas" zones (a MapComponent per-cell effect, not a
  plant-territorial one).
- **The venomous/thorny vine** ("holds territory by injury") needs something
  that damages a pawn for passing through or lingering in its cell radius —
  closest existing mechanism is a `Zone`/`MapComponent` periodic damage tick
  (as used by extreme-heat/toxic-fallout zones) keyed to the plant's own
  position and radius, or a Harmony patch on pathing/standing-still checks.
  Needs a design decision on trigger (on-enter vs per-tick-while-inside),
  damage type (a new DamageDef, or reuse `Scratch`/`Burn`), and whether it is
  avoidable by a work-around (careful pathing, protective gear) or a flat tax
  on using the patch.
- **The mossy nutrient-leacher** ("fast, shallow, opportunistic, racing
  everything else to whatever the wind just delivered") reads as a pure
  fertility/growth-rate competitor against neighbouring plants rather than a
  pawn-damage mechanic — this one may be buildable in tier b alone (a plant
  with an aggressive `fertilitySensitivity`/`growDays` profile that
  out-competes slower plants for the same tile) and worth separating from the
  vine's tier-c thorn mechanic during the design pass.

## the work — what this item must decide

1. Confirm whether 2 or 3 plants are being built (desert.md says "2-3").
2. For each, name the trigger, damage shape, and whether it needs a new
   `CompProperties` class (tier c) or can be approximated in XML (tier b) —
   per plant, not as a single verdict for all of them.
3. Hand the C#-needing plant(s) off as a build item once the mechanism is
   decided; the moss (if pure-fertility) can ship straight from this pass
   without a further item.

## decided — 2026-09-20, `design/Jawa/worldbuilding/desert_shade_plants_design.md`

**Two plants, not three.** §4b has two bullets, and arid_shrubland.md §Venomvine
names its venomvine ("a scratch carries venom with serious results") as **"Desert
lineage"** — so "strange vines and thorny venom" is one plant, the venomvine's
ancestral form, sharing one mechanism with the shrubland's thicket form.

| plant | tier | trigger | damage shape |
|---|---|---|---|
| **venomvine** (desert form) | **c** | one scratch on first contact with any vine cell, then one per in-game hour of lingering (per-pawn contact clock, sampled every 15 ticks by a MapComponent over a cell set the plant's comp maintains — the `Building_Trap.Tick` shape, which a Long-ticking plant cannot do itself) | new `RM_VenomvineScratch` (`ParentName="Scratch"`, `additionalHediffs`, the `ScratchToxic` shape) → new `RM_VenomvineVenom` hediff; not `ToxicBuildup`. Avoidable by route (`pathCost 60`), Sharp armour, flight, or a race `DefModExtension`; a flat tax only where a stand walls the patch |
| **leachmoss** (working name) | **b** | none — never touches a pawn | none. MEASURED: 1.6 `PlantProperties` has no reproduction fields and no plant affects a neighbour, so "leaching" is owning `WildPlantSpawner`'s rolls on Gravel/Soil (`fertilityMin 0.5`, highest commonality, `plantRespawningCommonalityFactor 2`) — split out from the vine, ships independently |

Both land in `mandrake.rm.environmentalhazards` (`RM_` prefix, generic content).
The shrubland thicket's body-size passability is NOT this mechanism and stays an
owed commission slug. No owner card: the sheets answered count, name and
seriousness; every remaining number is a Mod Settings default.

Successors: `VENOMVINE_CONTACT_VENOM_BUILD_1` (tier c) and
`DESERT_LEACHMOSS_BUILD_1` (tier b — filed rather than shipped from this pass
because the parent ruled this pass design-only, no XML).

## verify

A design doc or item update names, per plant: the mechanism decided (tier b or
c), the trigger, the damage shape, and — for anything needing new C# — a filed
successor build item.

## criteria

The desert's shade-plant defence mechanic has a decided design, on record,
that a build pass can execute without re-deriving the trigger/damage-shape
questions above.
