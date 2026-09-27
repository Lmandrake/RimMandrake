# The Scald — underwater flora design pass (2026-09-27)

Item: `SCALD_UNDERWATER_FLORA_1`. Owner commission (typed verbatim, 2026-09-26): *"Give it a
density, and we need a design pass to add a bunch of strange little underwater 'plants' like
strings and filaments of bacterial colonies, sponges, soft corals, all with alien twists. It
should not be barren."*

## Sources read

- `design/Jawa/worldbuilding/biomes/the_scald.md` — the frozen definition sheet (the mats,
  the walkers, the shoals, the sails, the six hard bans).
- `design/Jawa/worldbuilding/biomes/the_rust_cathedral_SCALD_HISTORY_amendment_draft.md` —
  the Scald as intended coolant reservoir; the Cathedral's hidden coolant circuit.
- `src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TheScald.xml` — live roster and fields.
- `src/RimMandrake/TerminalBiomes/Defs/TerrainDefs/RUT_ScaldWater.xml` and
  `RUT_ScaldMargin.xml` — the six boil terrains and the cool ring the plants must stand in.
- `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Items/RM_ScaldCatch.xml` and
  `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Items/RUT_ScaldFish.xml` — the existing cast
  (eesh, muddal, karrash, saal, bladderboil, doss, thuum, ekkel, shulla) these plants feed
  and shelter.
- `src/RimMandrake/LuminousPigment/Defs/ThingDefs_Plants/RM_Crowncarpet.xml` and
  `Defs/GenStepDefs/RM_GenStep_ShoreMats.xml` — the one existing Scald plant and the
  def-shape conventions (wildTerrainTags + completelyIgnoreFertility, GenStep scatter).
- `src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Buildings/RUT_ScaldVent.xml` — the vent
  def the vent-adjacent flora key on.

All ten proposed defNames collision-checked against `src/` (recursive grep, 2026-09-27):
every one FREE.

## Current state of the biome

`RM_TheScald` today: `plantDensity` unset, which the engine reads as **0** — so its one
`wildPlants` row (`RM_Crowncarpet 0.4`) never fires through the wild-plant spawner at all.
The only flora route that works is `RM_GenStep_ShoreMats` (map-gen scatter of crowncarpet
on tagged shore cells) plus bridge-placed `RUT_ScaldMargin` cells carrying the
`RUT_ScaldMarginMat` tag. The floor a gravship actually lands on
(`RUT_ScaldWaterOceanDeep`/`OceanShallow` via the GravTide `terrainsByFertility` block and
the `RM_SeaShoreExtension`) carries **no plant-bearing tag whatsoever** — a diver sees the
fauna roster swimming over bare glowing water. That is the barrenness the owner is ruling
against.

Two constraints shape everything below:

1. **Ban 4 of the frozen sheet** ("no macro-life in the boil itself... nothing swims the
   roiling surface layer but bubbles and sails"). The commission asks for *bacterial
   colonies, sponges, soft corals* — colonial micro-life and sessile filter-feeders, which
   is exactly what ban 4 permits. This roster therefore keeps everything in the boil
   colonial and small; anything with real architecture lives at depth (where the sheet's
   own walkers already live, "where the boil gentles to mere heat" — and where 350 m of
   pressure genuinely raises the boiling point) or at the margins.
2. **The seabed planet layer.** The floor is reached only by ship (`RM_SeaDiveHatch`) and
   sea floors are becoming a seabed layer — nothing below depends on a pocket map
   remembering state between visits. Every plant here is content a floor map can generate
   fresh every time (wild spawn or GenStep) and lose without cost.

## The roster

Nine new flora plus the existing crowncarpet makes ten. (A tenth, a cold endothermic 'chillbrace', was cut by owner ruling 2026-09-26: “No, this is silly. No cold.” — nothing in the Scald is cold.) The organizing law: **each
plant's survival trick in boiling water IS its alien twist**, and no two tricks repeat.
The tricks, named up front so the distinctness is checkable: *mirror* (reflects the heat),
*distillation* (boils on purpose), *circulation* (pumps its own coolant), *filtration*
(hoards what the water carries), *vitrification* (builds in glass), *anhydrobiosis* (dies
between wettings), *insulation* (wears its own gas), *ablation* (sheds a melting skin),
*refrigeration* (makes cold), *migration* (lives on the moving line). Crowncarpet already
owns *pigmentation* (temperature-banded thermophily), which is why nothing below is
rainbow-banded — that register is taken.

All names are invented and franchise-free (`RM_` tier, per Q11a); all ten defNames grepped
FREE against `src/`.

### 1. RM_Simmerlace — bacterial filament colony, boiling shallows

A lace of silver wire spread flat under the roil, each thread a rope of mirror-skinned
bacteria — the same heat-mirror trick the eesh wears as skin, grown instead into a mesh
that reflects the boil away from itself and cooks the water above it a half-degree hotter
for the favor. A shoal passing over simmerlace doubles in the mirror, and a pilgrim on the
rim who sees the shallows flash twice is seeing lace, not fish. It sheds: broken threads
knot in the current, and a knot that learns to roll is an **ekkel** — the fishermen swear
to it, and for once the fishermen are right.

- **Twist/survival:** living mirror; reflects rather than endures.
- **Art:** flat ground-hugging mesh, bright silver on the cyan, faint white specular
  glints; drawSize ~1.0, no glow of its own (it reflects the water's).
- **Harvest:** none — dressing, pathCost only. Beauty small positive.
- **Numbers:** growDays 4, commonality 0.9 (a common carpet-layer beside crowncarpet).

### 2. RM_Kettlewick — bacterial-colony string, margins and shallow edge

The biome's whole thesis at finger height: a single upright string of colony-flesh that
*boils itself on purpose*, wicking the fouled water up its length and sweating one clean
drop at a time off its tip — fouled heart, clean breath, three inches tall. Everything the
drop leaves behind, the wick keeps, growing a crusted collar of salt and mineral at its
base like a candle drowning in its own wax. Both faiths pick kettlewicks and press them
flat in books; each is certain the little distillery proves their reading of the shore.

- **Twist/survival:** it out-boils the boil — a living distillation column; the heat is
  its metabolism, not its enemy.
- **Art:** thin vertical filament, pale gold, one bright bead at the tip catching light;
  crusted white-grey collar at the base; drawSize ~0.6; faint warm glow (radius 1) at the
  tip bead.
- **Harvest:** the mineral collar — small yield tied to the steam-catch economy's register
  (suggest 2× a low-value mineral-salt item; whether that is a new item or an existing one
  is an owner question below — mechanically it must never be a drinkable, per Ban 1).
- **Numbers:** growDays 5, commonality 0.5, margins and shallow edge only.

### 3. RM_Vekkfan — soft coral, deep floor

A fan coral the height of a man that runs its own coolant loop: it drinks through a root
throat sunk into the cold bottom mud, pumps the deep water up through its vanes, and
exhales it warmed — a fountain running backwards, refrigerating itself with the crater's
own depths. Vekkfan stands where the dung-fall drifts thickest, combing the water the doss
and the eesh have not yet picked clean, and a stand of fans all lean the same way, into
the fall, like a congregation. The Cathedral cools itself through the Scald; the vekkfan
was doing it first, and nobody built it.

- **Twist/survival:** self-circulation — it imports its own cold from below.
- **Art:** broad pleated fan, dusty rose-to-ember gradient (warm tips, cool base — the
  gradient IS the mechanism made visible); drawSize 1.6–2.0; no glow.
- **Harvest:** none (beauty, moderate positive — the deep floor's furniture).
- **Numbers:** growDays 12, commonality 0.6, deep floor terrain only.

### 4. RM_Thurlsponge — sponge, deep floor and wrecks

The floor's kidney. A barrel sponge that filters the fouled water for a living and hoards
what it cannot spit out: metals, fines, the pan's whole mineral grief, packed lattice by
lattice into its own body. An old thurl is heavier than stone and rings when struck.
They colonize the wrecks for the iron — a hull the pan swallowed wears a coat of them
within a generation, and salvagers read a thick thurl-coat the way prospectors read an
outcrop: something worth eating is under there.

- **Twist/survival:** filtration and hoarding — it survives the foulness by owning it.
- **Art:** squat barrel, charcoal-brown with metallic flecks that catch the cyan glow;
  drawSize 1.0–1.3; no glow.
- **Harvest:** small Steel yield (suggest 5–8) at high harvestWork — the wreck-salvage
  economy in plant form, and the one flora a diving crew will strip on purpose.
- **Numbers:** growDays 20 (slow — an old thurl should feel old), commonality 0.4.

### 5. RM_Glasskelle — hard-soft coral, vent-adjacent only

The vent chimneys' own garden. Glasskelle builds its skeleton from the silica the vents
dissolve, drawing glass thread out of water no colony architecture should survive — and
it survives by *being already fired*: its tissue lives inside fused glass capillaries laid
down at vent temperature, so the boil reads to a glasskelle as pleasantly cool. It cannot
live off the vent; the glass must be drawn hot. When a colony dies it stays standing, and
a vent field is therefore a forest of clear dead spires with living color only at the
growing tips — centuries of glass, one season of flesh.

- **Twist/survival:** vitrification — born in the only water hot enough to build it.
- **Art:** branching clear spires, glass-white with cyan refraction, living tips picked
  out in ember orange; drawSize 1.2; faint glow at tips only (the vent's karrash and ekkel
  already own the vent-wall silhouette — glasskelle rises above them).
- **Harvest:** one unit of a glass-spire beauty item (rim-pilgrim keepsake register, like
  the karrash shell and the ekkel knot — market value ~8, Beauty on the item).
- **Numbers:** growDays 15, **not in wildPlants at all** — placed by vent-adjacency
  scatter (see route split).

### 6. RM_Pulsebead — bacterial colony, geyser margins

Alive for minutes at a time. Between geyser pulses a pulsebead is a dead ceramic pea baked
onto the stone; when the splash comes it wakes, swells, blooms into a soft grey-green
button, feeds, seeds, and bakes back to a bead as the stone dries — anhydrobiosis run on
a geyser's clock, a whole life lived in the wet intervals of the shore's percussion. The
geyser fields are drifts of them. Pilgrims call a blooming field "the applause."

- **Twist/survival:** it doesn't survive the boil — it dies between every boil, on
  schedule, and calls that living.
- **Art:** clustered small buttons, matte celadon green when bloomed; drawSize 0.5;
  no glow. (The bead state is description flavor, not a second graphic — no mechanism
  should depend on a live wet/dry cycle.)
- **Harvest:** none; negligible pathCost.
- **Numbers:** growDays 1 (the fastest thing on the planet — the point), commonality 0.7,
  shore/margin cells near geysers via the shore-mats GenStep's sibling (route split).

### 7. RM_Foamgorse — soft colonial shrub, boiling shallows

A low thicket that wears its own atmosphere: foamgorse respires a metabolic gas and keeps
it, trapping the bubbles under a shingled skin until the whole plant is jacketed in a
silver sleeve of foam — insulation first, and buoyancy the plant must constantly fight,
rooted and straining upward like a held balloon. The bubble lines the saal ride begin in
foamgorse beds as often as at the vents, and young sails shelter in its skirts until their
vanes stiffen — a foamgorse stand in season is hung with small bells like a market stall.

- **Twist/survival:** insulation — it never touches the water it lives in.
- **Art:** rounded shrub silhouette sheathed in specular silver bubbles over deep
  umber flesh; drawSize 0.9; no glow, strong highlight.
- **Harvest:** none (its economy is being the saal nursery).
- **Numbers:** growDays 6, commonality 0.7, shallow boil terrain.

### 8. RM_Seepcandle — soft coral, shallows and margins

A dripstone coral sheathed in mineral wax that never sets: the boil melts its skin
exactly as fast as the seepcandle lays it down, and the melt runs, refreezes lower,
and sculpts every colony into a guttered candle shaped by its own weather — ablation as a
way of life, the heat spent melting the coat never reaching the flesh. No two are alike
and none is symmetrical; the current writes them. Shore-folk read old seepcandles the way
sailors read driftwood: which way the water has been leaning all these years.

- **Twist/survival:** ablation — a skin that is always being lost is a skin that is
  always new.
- **Art:** dripped-candle silhouette, bone-ivory wax over a dark core, melt-gloss on the
  current-facing side; drawSize 1.0; no glow.
- **Harvest:** small wax yield — suggest 3× Chemfuel-register (the wax burns; the item
  can be an existing fuel or a tiny new one, owner question below).
- **Numbers:** growDays 10, commonality 0.5.

### 9. RM_Threshreed — filament band colony, the simmer line

Threshreed grows only on the moving boundary where simmer becomes boil — a band of copper
filaments, each rooted lightly and each dying the moment the line leaves it, the colony
surviving as a *wave* that re-seeds itself along the new edge day by day. A threshreed
band is therefore the crater's own thermometer drawn in copper: where it stands IS the
line, and the fishermen set their margin-nets a spear's length behind it and are never
scalded. The sheet says the mats band by temperature; threshreed is the banding made into
a single moving creature-of-many.

- **Twist/survival:** migration — the individual never survives; the line does.
- **Art:** narrow ribbon-band of upright copper filaments, reading as a drawn contour
  across the shallows; drawSize 0.8; no glow.
- **Harvest:** none; dressing with a navigation story.
- **Numbers:** growDays 2 (it must re-seed fast to be a wave), commonality 0.6, shallow
  boil terrain.

### The incumbent: RM_Crowncarpet

Stays, unchanged as a def, and stays in `wildPlants` — see the route split for the one
tag it needs to actually appear at depth. The mats remain the base of the whole economy;
everything above is punctuation on the carpet, not a replacement for it.

## plantDensity and the route split

### The density

**Proposed `plantDensity`: 0.30.** Calibration: vanilla desert runs 0.05, arid shrubland
~0.17, temperate forest 0.6. The owner's ruling is "it should not be barren", and the
sheet's own image is mats coating *everything* plus punctuation — but the crowncarpet mat
does the coating, and open water between stands is part of the sea-floor read (the fauna
must stay visible swimming over it). 0.30 puts a Scald floor between arid and forest:
unmistakably alive, never a jungle. If the first live look reads thin, the knob is this
one number; nothing else in the design has to move.

### Three routes, and which flora ride which

**Route A — `wildPlants` (density-driven, initial fill + ongoing regrowth).** The flora
whose placement law is just "this terrain": crowncarpet 0.4 (kept), simmerlace 0.9,
threshreed 0.6, foamgorse 0.7, vekkfan 0.6, seepcandle 0.5, kettlewick 0.5, thurlsponge 0.4. All follow the crowncarpet def-shape:
`completelyIgnoreFertility` + `wildTerrainTags`, since every cell here is water with
fertility the engine won't read. Two new terrain tags carry the split:

- `RM_ScaldFloorBed` — added to `RUT_ScaldWaterOceanDeep` and `RUT_ScaldWaterOceanShallow`
  (the dive-layer terrains, one `<li>` each in `RUT_ScaldWater.xml`). Deep-floor flora
  (vekkfan, thurlsponge) tag the deep variant's cells; shallow-boil flora
  (simmerlace, threshreed, foamgorse, seepcandle) the shallow.
- Margin flora (kettlewick, and seepcandle's second home) reuse the existing
  `RUT_ScaldMarginMat` tag on `RUT_ScaldMargin` — no new tag needed there.

**And the one-line fix the incumbent needs:** `RM_Crowncarpet`'s `wildTerrainTags` match
`RM_CrowncarpetBed` (patched onto vanilla `WaterOceanShallow` only) and
`RUT_ScaldMarginMat` — neither exists on the Scald's own floor terrains, so even with
density set, the mat the sheet says "coats everything in the depths" would spawn nowhere
a diver walks. Remedy on our side of the fence: add `RM_CrowncarpetBed` to
`RUT_ScaldWaterOceanShallow`'s tags in TerminalBiomes (string tag, no cross-reference, no
LuminousPigment edit). The existing `wildPlants` row `RM_Crowncarpet 0.4` then simply
starts working, which is the correct fate for it — kept, not cut, not re-weighted.

**Route B — GenStep scatter (map-gen one-time, the `RM_GenStep_ShoreMats` pattern).**
The flora whose placement law is *adjacency*, which `wildPlants` cannot express:

- **Glasskelle** — a small GenStep (or a scatterer keyed the way
  `RUT_ScaldSailScatterer` keys on the vent) that finds every `RUT_ScaldVent` on the map
  and rings it with 3–8 glasskelle within radius ~4, mixing in a few at max growth
  ("dead glass standing" is description flavor on the mature graphic — no persistent
  dead-thing def, per the seabed-layer constraint). Order after 760 so it lands with the
  same population wave as the shore mats.
- **Pulsebead** — the same GenStep or a sibling, drifts of 5–12 on shore/margin cells
  within a short radius of vents and geysers.

Both regenerate fresh each floor visit; neither carries state worth remembering — a glass
forest that re-rolls its exact spires between dives is geology-grade set dressing, not a
persistence bug.

**Route C — vent adjacency at runtime: not used.** No plant here needs ongoing
vent-coupled behavior (growth gated on a live vent, death when a vent stops). Glasskelle's
vent-dependence is a placement fact, fully paid by Route B, zero C# beyond one GenStep
worker. If the S4 Mod Settings gate turns vents' spray off, the glass forest is
unaffected — glass does not care, which is also true in the fiction.

### What this changes in `RM_TheScald.xml`, summarized

One field (`plantDensity` 0 → 0.30), eight new `wildPlants` rows beside the kept
crowncarpet row (shorthand `<DefName>commonality</DefName>` form — the sheet's own ⚠️
about `<li>` wrappers applies to `wildPlants` as it does to `wildAnimals`), and two tag
lines in `RUT_ScaldWater.xml`. Everything else is new defs in TerminalBiomes (plants) and
LuminousPigment stays untouched.

## Ecology — flora and fauna as one system

The sheet already ruled the economy's spine: mats coat, walkers mow, dung feeds, silver
darts, sails ride. This roster hangs every plant on that spine so nothing floats free:

- **The carpet layer** (crowncarpet + simmerlace) is the pasture. The walkers and the
  **muddal** mow crowncarpet; the **thuum** lives in the film beneath it; the **doss**
  picks what settles onto it. Simmerlace is the pasture's mirror-fringe — grazed by
  nothing (it is wire), but it *sheds*, and its knotted castoffs are where **ekkel** come
  from: the fishermen's origin story, now written down.
- **The dung-fall column** feeds twice: the **eesh** and **doss** work it in the water,
  and what they miss the **vekkfan** combs and the **thurlsponge** filters. Fans and
  sponges are the economy's cleanup crew — the reason the Scald's water, fouled with
  minerals, is never fouled with rot.
- **The vents** stack three tenants: **karrash** on the chimney walls eating mat,
  **ekkel** tumbling the chimney throats, **glasskelle** rising above both — and the
  glasskelle forest is where a karrash goes to molt, out of reach inside the glass.
- **The nursery**: young **saal** shelter in foamgorse skirts until their vanes stiffen;
  the bubble lines they will ride begin in the same beds. The **bladderboil** rests in
  margin pools among kettlewicks — two gas-bag lifestyles, plant and animal, one shore.
- **The people**: kettlewick collars and seepcandle wax join the karrash shell and ekkel
  knot in the pilgrim-keepsake register; thurlsponge iron joins the wreck-salvage economy;
  threshreed sets the margin-nets; pulsebead fields applaud the geysers. Both faiths keep
  reading the same shore and reaching opposite conclusions, as ruled.

Nothing in the roster eats a player-relevant resource, adds a predator, or touches the
water's potability. The boil stays lethal, the margins stay kind, and every ban on the
frozen sheet stands untouched.

## Art direction summary table

| plant | silhouette | palette | glow | drawSize |
|---|---|---|---|---|
| RM_Simmerlace | flat wire mesh | bright silver on cyan | none (reflective) | 1.0 |
| RM_Kettlewick | single upright string, crusted base | pale gold, white-grey collar | warm tip bead, r1 | 0.6 |
| RM_Vekkfan | pleated standing fan, leaning | rose→ember gradient | none | 1.6–2.0 |
| RM_Thurlsponge | squat barrel | charcoal-brown, metallic flecks | none | 1.0–1.3 |
| RM_Glasskelle | branching clear spires | glass-white, ember tips | tips only | 1.2 |
| RM_Pulsebead | clustered buttons | matte celadon | none | 0.5 |
| RM_Foamgorse | rounded shrub in bubble sleeve | silver over umber | none, strong highlight | 0.9 |
| RM_Seepcandle | guttered dripping candle | bone-ivory over dark core | none | 1.0 |
| RM_Threshreed | ribbon contour of filaments | copper | none | 0.8 |

Palette check against the sheet's §9: boiling white, scald cyan, thermophile rainbow
(crowncarpet's, unshared), basalt black — the new flora add silver, copper, bone, glass
and one deliberate cold blue, and nothing competes with the rainbow register or the cyan
water glow. The one tiny glow (kettlewick warm) is a single-cell accent
against the water's own radius-2 cyan, not new light sources.

## Ruled — decisions taken by question card, 2026-09-26

1. **Yes — all three other sea floors get their own strange-flora passes, commissioned
   now** (Grey, Twilight, Propane Lake; each in its own register, nothing shared).
5. **Thurlsponge yields real Steel** (5–8 at high work) — the floor's kidney pays in
   metal.
6. **Chillbrace is CUT entirely** — owner typed: "No, this is silly. No cold." Nothing
   in the Scald is cold; the roster above is already nine accordingly.
7. **Glasskelle re-roll accepted** — geology-grade dressing until the seabed layer
   ships persistence.

## Questions for the owner — still open

2. **plantDensity 0.30 — accept, or name a different number?** It is the single knob; the
   roster works unchanged anywhere from 0.15 (sparse) to 0.5 (lush).
3. **Kettlewick's harvest: what does the mineral collar yield?** A tiny new keepsake/
   mineral-salt item, an existing item, or nothing (pure dressing)? It must never be a
   drinkable (Ban 1).
4. **Seepcandle's wax: harvest as plain Chemfuel, a small new wax item, or nothing?**
8. **Simmerlace → ekkel as written origin lore** ("a knot that learns to roll is an
   ekkel"): keep as fishermen's folklore in both descriptions, or keep the plant and cut
   the cross-reference?
