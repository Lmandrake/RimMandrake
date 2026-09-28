# The Wasteland survivor cast — full RM_ replacement bible

_DESIGN subagent under `WASTELAND_BEDAZZLE_SITTING_1`, 2026-09-28. Owner rulings
(recorded on that item's ledger, 2026-09-27/28): the Wasteland's donor cast gets FULL
RM_ replacement — new defs, names, art, no patches. Register: **"ugly warty life that
was already tough enough to survive the waste products… creatures that already ate
the waste of other beings, survived extreme environments."** SURVIVORS, not
sufferers — English ugly-tough names, never invented-exotic, never Star Wars. The
name map below is OWNER-ACCEPTED VERBATIM ("Full accept"); no defName collisions
found (repo-wide grep, sanity-probed), so every name ships unchanged._

_Read with `wasteland.md` (frozen sheet). §9's "fauna reads as pathos" is REVISED by
the register ruling: these read as tough ugly survivors, not suffering victims. All
§6 hard bans honored per entry below._

## 0. Contents

- §1 Scope, sources, what stays untouched
- §2 The wretched many — ported fauna (8 rows)
- §3 The new species — processors and the radiothermal solitary
- §4 The Middenshell — the giant (own section)
- §5 The brine trio — label-only renames (defNames frozen)
- §6 Flora — ports, keepers, and the new Cinderfelt
- §7 Roster wiring summary (wildAnimals / wildPlants, donor rows out)
- §8 Art commission — what is queued, what was found finished
- §9 Proposals tail (flyer niche note)

## 1. Scope, sources, what stays untouched

**Source roster** — `src/RimMandrake/Wasteland/Defs/BiomeDefs/RM_Wasteland_Biome.xml`
(the RM_ standalone mod, `WASTELAND_RM_MOD_BUILD_1`). Every donor `wildAnimals` row in
it is replaced by an owned RM_ species below; every donor `wildPlants` row that is a
mod's (not vanilla's) gets an owned port. **Vanilla rows stay untouched:**

- `Toxalope` — vanilla **Biotech** animal (already noted in the biome file). Owner map
  says Toxalope → Boilhide, so it IS ported despite being vanilla: the register ruling
  wants an owned, visibly-marked survivor, and a vanilla animal resident here would
  violate §6 ban 4 (no unmarked wildlife) anyway. The vanilla def is simply dropped
  from the roster; nothing patches it.
- `Plant_GrayGrass`, `Plant_TreePolux` — vanilla, stay.
- `Plant_Toxipotato` — **MEASURED vanilla Biotech** (`Data/Biotech/Defs/
  ThingDefs_Plants/Plants_Cultivated_Farm.xml`; no workshop mod defines it). Stays.

**Already-owned content that stays as-is** (no redesign, no rename):
`RM_DosimeterLawn`, `RM_VaultRoot`, `RM_WastelandScorchedStars`, the brine trio
(§5), `RM_BrineDeposit_*`, the brine terrains/hediff. Art status for these: §8.

**Ban compliance frame (§6 of the sheet), asserted once and honored per entry:** no
anomaly entities; nothing framed as an engineered weapon-organism; the wildlife is
never the headline threat — every dangerous entry below is dangerous only by dose,
proximity or defense, never by predation on the colony; everything is visibly marked
by contamination (warts, plating, mineral crusts, boils — never clean); nothing
depends on rain or on spoilage.

**Register:** every description is written as a creature that WON — it eats what
poisons everything else, it is content, its ugliness is armor and adaptation. No
pity language in labels or descriptions.

## 2. The wretched many — ported fauna

All eight are the biome's "wretched many" (sheet §4) re-read through the register
ruling: small, warty, short-lived — and completely at home. Commonalities carry the
donor row's value so the biome's texture doesn't shift. Diets are design targets;
FOUNDRY cribs the donor's statBases as the starting numbers when porting, then
applies the deltas noted. Def files live in
`src/RimMandrake/Wasteland/Defs/ThingDefs_Races/` (one file per species,
`RM_<Name>.xml`, ThingDef + PawnKindDef together), textures under
`Textures/Things/Pawn/<Name>/` at the artpipe's facing names.

### Scumrat (port of GR_ParagonRat, commonality 0.7)

- **Hook:** the rat that made the dump its estate — fat on what nothing else will
  touch, bald in patches, wart-knuckled, and doing fine.
- **Class:** wretched many. **Stats sketch:** bodySize ~0.35, omnivore/carrion
  (OmnivoreRoughAnimal-family food type — an everything-eater), speed brisk
  (~4.4). Breeds fast; the biome's baseline meat animal.
- **Marked by:** hairless wart-clustered hide over the shoulders, salt-stained
  muzzle, mineral staining down the flanks.
- **Danger frame:** none beyond a cornered bite. Never a threat headline.

### Slagmole (port of GR_Molebear, commonality 0.4)

- **Hook:** a barrel of muscle that digs through vitrified crust like frost — its
  claws are worn glassy and its hide is set with embedded grit it never sheds.
- **Class:** wretched many (heavy end). **Stats sketch:** bodySize ~1.6, herbivore/
  root-feeder (digs vault-root and buried growth), slow (~3.0), high armor-blunt
  from the grit hide. Tameable pack-digger flavor text, no mechanic owed.
- **Marked by:** slag-grit embedded along the back like a cobbled road; one milky
  eye is common.
- **Danger frame:** defensive only; revenge-prone if dug out.

### Scabspinner (port of GR_Spidercat, commonality 0.4)

- **Hook:** a patchy-furred ambusher whose webs are half silk, half scab — it
  spins over its own sores and over its burrow mouth alike, and both hold.
- **Class:** wretched many (the closest thing to a predator, kept small).
  **Stats sketch:** bodySize ~0.75, carnivore of scumrats and middenbeetles only
  (predator of the small cast, never man-hunting), speed ~4.0.
- **Marked by:** crusted spinnerets, fur missing in mange-map patches, scabbed
  joints it re-silks daily.
- **Danger frame:** hunts the small cast; flees pawns. Never the biome's threat.

### Boilhide (port of Toxalope — vanilla Biotech row dropped, commonality 0.4)

- **Hook:** the grazing herd animal whose hide is a landscape of sealed boils —
  each one a pocket where its body walled poison off and moved on.
- **Class:** wretched many (herd). **Stats sketch:** bodySize ~0.7, herbivore
  (grazes the toxic flora rows freely — scumgrass, boilbulb), speed quick (~4.6,
  it is still an antelope-shape under the warts). Leather: "boilhide" — ugly,
  cheap, tox-resistant flavor.
- **Marked by:** the boil-field hide, antlers fused into a single mineral-crusted
  club.
- **Danger frame:** none; it runs.

### Middenbeetle (port of GR_Beetlefleet, commonality 0.7)

- **Hook:** a fist-sized beetle that files across the flats in caravan lines,
  hauling scraps of everything back to middens it defends from nobody.
- **Class:** wretched many (detritivore). **Stats sketch:** bodySize ~0.2,
  detritivore/carrion, speed ~3.8, travels in loose lines (herd animal flag).
- **Marked by:** carapace pitted like struck flint, salt rime at every seam.
- **Danger frame:** none. Swarms a carcass, never a colonist.

### Gristleswarm (port of VFEI2_Swarmling, commonality 0.6)

- **Hook:** a knee-high scuttler of gristle and plate that lives in rot-slow
  country by eating what cannot rot — sinew, hide, bone-rind — and thriving on it.
- **Class:** wretched many (pack detritivore). **Stats sketch:** bodySize ~0.3,
  carrion/detritivore, speed ~4.2, spawns in small packs (3–6).
- **Marked by:** exposed gristle at the joints gone leathery and grey, back plates
  crazed like dried mud.
- **Danger frame:** pack defense only; a pack fights back as one when one is hurt.

### Soot Gristleswarm (port of VFEI2_BlackSwarmling, commonality 0.6)

- **Hook:** the gristleswarm of the ash country — the same animal run through the
  chimney: soot-black, grease-sheened, ember-eyed.
- **Class:** wretched many; **plain-modifier variant of Gristleswarm** (owner's
  accepted form: "Soot Gristleswarm", never an invented second name). Same body,
  same behavior; ash-country color and a slightly better cold tolerance.
- **Stats sketch:** as Gristleswarm; ComfyTemperatureMin ~ −30.
- **Def note:** its own ThingDef/PawnKindDef (`RM_SootGristleswarm`) — a variant
  def, not a color channel — because the donor pair were two defs and the roster
  weights them separately.

### Gravelgut (port of AA_Terramorph, commonality 0.2)

- **Hook:** a low armored slab that eats the ground itself — gravel, glass-crumb,
  mineral crust — and passes it as smooth sorted pebbles the locals kick apart to
  read what is buried underneath.
- **Class:** extremophile-odd (the roster's resident oddity; a lesser excretor,
  kept distinct from the Sloghog: it sorts minerals, it does not concentrate
  contamination). **Stats sketch:** bodySize ~2.0, mineral-feeder (dendrovore-style
  diet flag off; custom "eats rock chunk" flavor is text only, mechanically a
  slow-grazing herbivore so no new needs system is owed), speed ~2.2.
- **Marked by:** mouthparts worn to polished stone, hide set with a mosaic of
  swallowed-and-rejected glass.
- **Danger frame:** ignores everything; hits like a wall if attacked.

**Donor removal (per port, same change):** the donor row comes OUT of
`RM_Wasteland_Biome.xml`'s `<wildAnimals>` in the very commit that adds the RM_
row — shorthand element form both directions (`<RM_Scumrat>0.7</RM_Scumrat>`,
never `<li>`). No patches, no `MayRequire` residue: the RM_ mod's roster ends the
change with zero donor references.

## 3. The new species

Owner-ruled, developed fully here. These are the sheet §4 "leveraging few" made
concrete: two excretor/processors and the radiothermal solitary. All three are
economic animals — the biome's uniquely-available §7 columns (excretor refining,
radiothermal heating) given bodies.

### Sloghog — the ranchable excretor (commonality 0.3)

- **Hook:** a warty, barrel-bodied hog that grazes poisoned ground with total
  contentment and periodically coughs up the poison as a stone you can sell.
- **Class:** processor (excretor — sheet §4: "they extract; they never heal —
  that is the plants' monopoly").
- **Behavior/product:** grazes polluted/toxic terrain and the toxic flora rows;
  every ~4–6 days a fed adult produces one **bezoar** — a dense metal-salt lump of
  refined contamination (new ThingDef `RM_ContaminantBezoar`: heavy, valuable to
  the right buyer, mildly dangerous to stockpile in quantity — flavor + a small
  beauty/toxic-environment footnote, not a new hazard system). **A kept herd is a
  slow refinery** — the ranching loop is the point: pen them on ruined ground,
  collect the poison as a handleable object.
- **Mechanic shape:** `CompHasGatherableBodyResource` subclass (the milk/wool
  shape — well-trodden engine ground; FOUNDRY: crib `CompMilkable`, gate the
  fill rate on standing on polluted terrain when Biotech pollution is present,
  else on time). Pollution-CONSUMPTION per the owner's processor ruling: where
  the engine allows, grazing a polluted cell occasionally un-pollutes it — the
  herd genuinely processes, one mouthful at a time. If the un-pollute call proves
  awkward, the bezoar output alone satisfies the ruling's economy half; note it
  and ship.
- **Stats sketch:** bodySize ~1.2, speed ~3.4, herd 2–5, tameness high (it was
  bred-adjacent once, or acts like it). Meat: edible, faintly awful. Leather:
  wart-hog hide, cheap and tough.
- **Marked by:** wart fields down both flanks, tusks capped in mineral crust,
  content half-shut eyes.
- **Danger frame:** none. It is the closest this biome comes to livestock.

### Sootgrazer (commonality 0.25)

- **Hook:** a slab-shouldered grazer that works the ash-fall like pasture — it
  eats deposition itself and presses what it can't burn into brick.
- **Class:** processor. **Behavior/product:** eats ash/pollution deposition
  (mechanically: grazes on ash-family and polluted terrain; same terrain-gated
  gatherable comp as the Sloghog); a fed adult yields **fuel-grade soot bricks**
  (`RM_SootBrick` — chemfuel-adjacent burnable, stackable, sells low but the
  supply is endless where the sky keeps falling).
- **Stats sketch:** bodySize ~1.0, speed ~3.6, small herds, cold-tolerant (the
  ash country is the margin and the dark scour's edge).
- **Marked by:** hide the exact grey of settled ash with darker rain-shadow
  streaks it never had rain to earn — the streaks are grease; nostrils fringed
  with filter-bristle combs.
- **Danger frame:** none.

### Smolderback — the radiothermal solitary (commonality 0.05, rare)

- **Hook:** so hot with its own decay it must dump heat to live — a living
  furnace that haunts the cold dark scour and cannot stand its own company.
- **Class:** radiothermal solitary (sheet §4 verbatim: "a warm boulder in the
  black country means one passed; a tamed one is a living furnace that heats a
  shelter all winter and irradiates it the entire time").
- **Behavior/product:** constant heat output (a `CompHeatPusher` on the pawn —
  the vanilla comp, cheap and proven); constant low toxic/radiation dose to its
  room (Biotech tox-buildup on nearby pawns, small hediff-per-rare-tick comp —
  the DOSE is ambient, never an attack). **Solitary spacing:** its own kind cook
  each other — spawns alone, wanders alone; a mental-map spacing mechanic is NOT
  owed (spawn-alone + lone-wanderer flags read as the behavior; note in def).
- **The trade:** tame one and winter is solved and dosed at once. Heats a shelter
  all winter, doses it the whole time. That sentence goes in the description.
- **Stats sketch:** bodySize ~1.8, speed ~2.6, carnivore/scavenger (eats the
  frozen dead of the scour; hunts nothing bigger than a gristleswarm), ComfyTemp
  min ~ −60 (it brings its own weather).
- **Marked by:** back plates split by glowing seams — the sickly-radiance §9
  accent made flesh; snow never lies on it; the ground steams where it beds.
- **Danger frame:** proximity dose + heat only. It never attacks unprovoked; the
  ban on wildlife-as-headline-threat holds because avoiding it is trivial — it
  is the *keeping* of it that costs.

## 4. The Middenshell — the giant

**THE giant, owner-ruled TWENTY CELLS WIDE.** A colossal, ancient excretor — the
Sloghog's deep-time cousin grown into geography. Its hardened shell is a rampart of
fused waste, scavenge debris and its own vitrified bezoars: centuries of what it
processed, worn as architecture. It is the sheet's silhouette law made animal —
"horizons of nothing, then one enormous thing."

- **Hook:** the oldest survivor on the planet's worst ground, wearing everything it
  ever ate.
- **Class:** giant (excretor lineage). **Never hostile** — it does not fight, it
  does not hunt, it barely notices. **Proximity is the dose:** a radius aura of
  toxic/radiation buildup around the body (same ambient-dose comp family as the
  Smolderback, larger radius, stronger near the shell). **Its walk is the danger:**
  a destruction wake — crushed terrain, flattened structures, snapped flora along
  its path. Getting near it is a choice you pay for; being in front of it is a
  mistake the ground remembers.
- **Engine wiring:** rides the **TitanicCreatures engine** — `RM_TitanicExtension`,
  multi-cell body via Large Pawns, wander-route AI, destruction wake, and
  **corpse-becomes-harvestable-landmark**: a dead Middenshell hardens into a
  permanent map feature, and that feature is a **bezoar quarry** — the shell mined
  like a resource rock for vitrified bezoars (`RM_ContaminantBezoar` + a rarer
  `RM_VitrifiedBezoar` grade), the single richest excretor-refining prize in the
  biome, priced in the dose you take digging it.
- 🔴 **FOUNDRY verification bar (goes in the wiring item):** verify the
  TitanicCreatures engine's maximum footprint tier actually handles a **20-cell**
  body, and REPORT if it does not — the width is an owner ruling, so an engine
  ceiling below 20 is an escalation, never a silent shrink.
- **Spawn shape:** never in `<wildAnimals>` (it is not weather, it is an event) —
  one-per-map-at-most via mutator/incident wiring in the titanic engine's own
  spawn machinery; the dark scour and war-ground families are its range.
- **Stats sketch:** bodySize maximal for the engine tier (target: the 20-cell
  tier's own number), speed glacial (~0.8), diet: everything and nothing — it
  grazes terrain like the processors, at landscape scale.
- **Marked by:** the shell IS the marking — fused slag, hull-plate scraps, ribs of
  something that lost, all grouted in vitrified black-green bezoar glass with
  sickly-radiance seams deep in the crevices.
- **Ban compliance:** never hostile, so never the headline threat (the ground
  still is — the Middenshell just concentrates it); visibly nothing BUT
  contamination; no anomaly flavor — it is an animal, old, not wrong; no
  weapon-organism framing — nobody made it, it simply refused to die.

### Art note

The Middenshell's job renders at **512** so the scale carries in the pixels (the
contagion cast's Meltgut precedent); the read must be "landscape that turns out to
be an animal", walking, all four limbs load-bearing under visible mass.

## 5. The brine trio — label-only renames

`RM_BrinePlate`, `RM_Drazz`, `RM_Tekk` (`Defs/ThingDefs_Items/
RM_WastelandBrine_Items.xml` + the three `RM_BrineDeposit_*` beds). **defNames
FROZEN** — the canonical save may reference them — and the register ruling lands as
**label-only renames** (labels + descriptions' first noun; deposit-bed labels
follow):

| defName (frozen) | old label | new label |
|---|---|---|
| `RM_Drazz` | drazz | **brineleech** |
| `RM_Tekk` | tekk | **sparkcrab** |
| `RM_BrinePlate` | brine plate | brine plate (stays) |

Deposit beds re-label to match: "brineleech bed", "sparkcrab bed"; descriptions
swap the old nouns in place. Mechanics, stats, hediff, terrains: untouched.

**Art finding (checked, per brief):** `RM_Tekk`'s PNG is a byte-copy of
`RUT_Hardwood.png` — a wood resource icon, not sparkcrab art; `RM_Drazz` and
`RM_BrinePlate` still point at an Alpha Biomes donor texture
(`Things/Plants/AB_CrystalHorn/AB_CrystalHornA`) that does not resolve on a
standalone load (the file's own REMAINS note calls for an art-lane decision).
This commission IS that decision: all three get real item-icon jobs (§8).

## 6. Flora

Def file for the ports + Cinderfelt: `Defs/ThingDefs_Plants/RM_WastelandFlora.xml`
(alongside the existing three). Vanilla rows (`Plant_GrayGrass`, `Plant_TreePolux`,
`Plant_Toxipotato` — vanilla Biotech, MEASURED §1) stay untouched.

### Scumgrass (port of RG_Plant_ToxiGrass, commonality 1.2)

The biome's default green — a wiry, grease-slicked grass that grows on ground that
kills cleaner plants, salt-crusted at the blade tips. Stats: ground-cover grass
family (crib donor statBases), fertilityMin low, fertilitySensitivity 0. Grazing
animals eat it without complaint; that is what half the cast lives on.

### Tall Scumgrass (port of RG_Plant_TallToxiGrass, commonality 0.8)

The same grass where the ground is richest — which here means worst. Waist-high,
sight-blocking, its plain-modifier name per the accepted map. Own def
(`RM_TallScumgrass`), donor pair kept as two rows at donor weights.

### Pusberry (port of AB_WeepingToxberry, commonality 0.2 — tree)

A small tree whose pale berries sit in weeping, wax-sealed sockets — the tree
walls its fruit off from its own sap the way the boilhide walls off poison.
Berries edible processed; raw is a lesson. Tree family stats off the donor.

### Boilbulb (port of AB_ToxiBulb, commonality 0.1)

A ground bulb swollen into a blistered dome, mineral-crusted at the base, faintly
warm to the hand. A forage staple for the cast and a processed-food input for
colonists.

### Wartshrub (port of VRE_PoluxBush, commonality 0.08)

A knee-high shrub whose bark is one continuous wart-field — sequestration in
miniature (it locks what it drinks into its galls; the polux lineage's little
cousin). Galls harvestable as a low-grade chemfuel/chemical input.

### Cinderfelt — NEW (commonality: not a standing row — see wiring)

**A felt-grey mat that grows ONLY on fresh ash fall; the post-storm marker.** The
sheet's exhumation-lottery doctrine given a visible face: after every ash storm
the flats grow a grey pelt, and where the felt is thickest, the fall was — which
is where the survey (and the dose) is. Fast-growing, short-lived, dies as the
fall compacts.

- **Wiring:** not a standing `<wildPlants>` weight — it germinates from the ash
  storm's own aftermath (the storm weather def's post-effect scatters it, or a
  MapComponent seeds it on ash-deposition terrain after the weather ends; FOUNDRY
  picks the cheaper). A token 0.02 wildPlants row is acceptable as a fallback so
  the def is never dead content while the storm wiring lands.
- **Stats sketch:** growDays ~1.5, lifespan short (dies in ~8 days),
  fertilitySensitivity 0, purple-grey felt texture, maxMeshCount 4 mat form like
  the dosimeter lawn.
- **Ban compliance:** depends on ash fall, not rain (§6 ban 5 clean); marks the
  storm the way the dosimeter lawn marks the ground.

## 7. Roster wiring summary

Target roster in `RM_Wasteland_Biome.xml` after the build (shorthand element form
throughout — `BiomeAnimalRecord`/`BiomePlantRecord` custom loaders read node NAME
as the def and node TEXT as commonality; a `<li>` silently discards the def):

```xml
<wildAnimals>
  <RM_Scumrat>0.7</RM_Scumrat>
  <RM_Middenbeetle>0.7</RM_Middenbeetle>
  <RM_Gristleswarm>0.6</RM_Gristleswarm>
  <RM_SootGristleswarm>0.6</RM_SootGristleswarm>
  <RM_Boilhide>0.4</RM_Boilhide>
  <RM_Slagmole>0.4</RM_Slagmole>
  <RM_Scabspinner>0.4</RM_Scabspinner>
  <RM_Sloghog>0.3</RM_Sloghog>
  <RM_Sootgrazer>0.25</RM_Sootgrazer>
  <RM_Gravelgut>0.2</RM_Gravelgut>
  <RM_Grimewing>0.15</RM_Grimewing>
  <RM_Smolderback>0.05</RM_Smolderback>
</wildAnimals>
```

`wildPlants`: donor rows (`RG_Plant_ToxiGrass`, `RG_Plant_TallToxiGrass`,
`AB_WeepingToxberry`, `AB_ToxiBulb`, `VRE_PoluxBush`) replaced at the same weights
by `RM_Scumgrass` 1.2 / `RM_TallScumgrass` 0.8 / `RM_Pusberry` 0.2 /
`RM_Boilbulb` 0.1 / `RM_Wartshrub` 0.08; vanilla rows and the existing RM_ rows
unchanged; `RM_Cinderfelt` 0.02 fallback row (§6). Middenshell: never a roster
row (§4). **Every donor row removal lands in the same change as its RM_
replacement** — the mod ends the build with zero donor `MayRequire` references in
its roster. The `RUT_` twin's patch-added campaign roster
(`UtinniPatches/Patches/WildAnimals_Wasteland.xml`) is NOT this pass's scope; its
donor rows are the absorption campaign's (`MLIE_ABSORPTION_BIOME_WIRING_1`
family), noted here so nobody re-discovers them as this cast's leftovers.

New item defs owed alongside: `RM_ContaminantBezoar`, `RM_VitrifiedBezoar`,
`RM_SootBrick` (§3–§4). C# owed: the terrain-gated gatherable comp (Sloghog/
Sootgrazer), the ambient-dose comp (Smolderback/Middenshell aura), Middenshell
titanic wiring — all FOUNDRY items; **`RM_CreatureBehaviors.csproj`-style
explicit-Compile listing applies if any of it lands in an existing assembly: a
new .cs without a `<Compile Include>` line compiles into nothing, silently.**

## 8. Art commission

CSV: `infrastructure/artpipe/art_lists/wasteland_survivor_cast.csv`, format per
`contagion_grotesque_cast.csv`, `rimflow_item_id=WASTELAND_BEDAZZLE_SITTING_1`,
channel codex, transparent, priority 70. Fauna faced `south,east,north` at 256;
**Middenshell at 512**; flora and item icons single at 256. Style register:
realistic natural-history illustration + grime/wart/mineral-crust texture
language, sheet §9 palette (salt white, ash grey, vitrified black-green, sickly
radiance accents), the true-rear-view north line on every faced job, no camera
words anywhere. Register line on every job: tough content survivor, never
pitiable.

**Pre-queue check (done 2026-09-28, per the owner's existing-art ruling):**
`done/`, `_artsrc/`, `registry.jsonl` searched per subject —

- `rutdosimeterlawn_v1`, `rutvaultroot_v1` — **finished art exists** in `done/` +
  `_artsrc/` (generated for the RUT_ twins, `COMMISSION_LEDGER_CLEANUP_1`).
  **Skipped from this commission.** Owed instead (FOUNDRY): copy the finished
  PNGs into this mod's `Textures/` at the defs' texPaths (`Things/Plant/
  DosimeterLawn`, `Things/Plant/VaultRoot`) — both texPaths currently resolve to
  no PNG in the repo.
- `scorchedstars_v1` — finished (`ART_REGEN_FLORA_WAVE1_QUEUE_1`) and the mod
  already ships `ScorchedStars_a/b.png`. Skipped. (Its Q13 divergent-identity
  regen remains owed on the build item, separately — not silently re-queued
  here.)
- All new cast subjects (Scumrat…Middenshell, Scumgrass…Cinderfelt, the three
  brine icons): **no existing art anywhere** — queued.

Queued: **21 jobs** — 12 faced fauna, 6 single flora, 3 single item icons
(brineleech, sparkcrab, brine plate — §5's art finding).

## 9. The Grimewing — ruled in (decision taken by question card, 2026-09-28)

**The flyer niche is FILLED.** The **Grimewing** — a carrion-finder that rides the
storm-thermals: the biome's exhumation lottery means fresh finds after every storm,
and this wretched, half-bald scavenger bird circling a fresh exhumation is the
visible "the map re-dealt here" marker, the way the cinderfelt marks the fall.

- **Class:** wretched many (aerial scavenger). Per the standing flyer rule it is a
  **real flyer**: `MaxFlightTime`/`FlightCooldown` statBases + race flight fields,
  Locust shape, `canLeaveMapFlying` true (it is a bird; it lairs nowhere).
- **Stats sketch:** bodySize ~0.5, carrion diet, speed ~4.0 ground / flightSpeedFactor
  ~2.5. Commonality **0.15** (`<RM_Grimewing>0.15</RM_Grimewing>` joins the §7
  roster block).
- **Marked by:** patchy moth-eaten feathers over bare warty grey skin, salt-stained
  hooked beak, wing gaps where feathers never grew back.
- **Danger frame:** none — it eats what the storm digs up, never what walks.
- **Art:** 3 faced jobs queued 2026-09-28 (`RM_Grimewing_*` in pending/; row
  appended to the cast CSV). Build lands with `WASTELAND_RULED_CONTENT_1`.
