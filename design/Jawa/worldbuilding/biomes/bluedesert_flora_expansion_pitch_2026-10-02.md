<!-- status: pitch — design only, nothing filed, nothing built -->
# Blue Desert — flora expansion pitch (2026-10-02)

**Item:** `BEDAZZLE_FLORA_EXPANSION_1` (owner, 2026-09-29: *"Need more plant-like members of this
biome"*). **Second Blue Desert list.** The first is the Carbon Garden
(`bluedesert_carbon_garden_2026-09-30.md`: milelace, hazebell, longglass — unshipped, awaiting
its art sheet). Nothing here repeats it or the built four (palefloss, glassfern, chimeglobe,
virr in `src/RimMandrake/BlueDesert/Defs/ThingDefs_Plants/RM_BlueDesertFlora.xml`; roster
`RM_BlueDesert` `<wildPlants>`, shorthand form, 4 rows).

## 0. Constraints every pitch obeys (not restated per card)

- **Hydrocarbon only** (owner, typed 2026-09-30: *"Only hydrocarbon plants please."*). Every
  card is cold-stable and warm-reactive: `RimMandrake.BlueDesert.CompProperties_PlantCharge`,
  the palefloss plant block (`completelyIgnoreFertility`, −90…−1 °C band, `growMinGlow 0`,
  `dieIfNoSunlight false`), `Flammability 0.05`, the ButaneGut outcome doer, MaxHP ≤ 40 so a
  blast chains.
- **Hard bans** (`the_blue_desert.md` §6): no water metabolism; **never sowable** (no
  `sowTags`); **no warm-safe hydrocarbon produce** — any new yield item carries the cold-wax
  comps (`CompTemperatureRuinable` + `RM_CompRuinedDetonator` + `CompExplosive`). The one
  exception below (Kethevar) yields pure carbon, which is not a hydrocarbon.
- **Palette.** The owner's 2026-09-29 law (*"Your color palette is too uniform per biome.
  Needs more variety"*) is answered with **real hydrocarbon colour chemistry**: polyene
  pigments (lycopene-class scarlet/orange), tholins (rust/maroon), aromatic fluorescence
  (violet/magenta), thin-film oil sheen (iridescent), graphite (silver-black). The bodies stay
  **glassy and translucent** — tinted glass, not opaque leaf — so the flora still reads as
  native. ⛔ **Nothing is blue up close** (§5 "Always true") — no card uses blue. ⚠️ This does
  break §9's "glass-clear and grey underfoot" palette line on purpose — question 1 in §8.
- **Accent:** names coined in the biome's register (vhaulk, murrek, krissek, dovvik, virr):
  hard consonants, doubled letters, `-ek/-uk/-eth` endings, varied syllable count (1–3).
- **One biome, one home:** all six are Blue Desert only; none reuses another biome's plant.

## 1. Qeshra — FOOD (fodder)

- **Look (art brief):** a knee-low cushion of glassy beads, each bead a translucent
  scarlet-to-tangerine sphere (polyene pigment) packed like roe on a clear stalk-mat;
  frost-rimmed at the cushion's rim. The one *red* thing on the plateau.
- **Where / behaviour:** sparse clumps in the lee of drifts; slow to grow, dense in
  nutrition. Native grazers (utikka, ossivel, dorrak) seek it out — a qeshra patch draws a
  herd, and the herd draws the krissek.
- **Harvest / yield:** cut → **qeshra roe**, a cold-wax-family item that is *animal feed
  only* (`ingestible`, preferability `RawBad`, `foodType` matched to the natives). It is how
  a colony feeds tamed natives (tameability relaxed, cast bible §0) without kibble — stored
  on the existing cold-sink rack; warm storage detonates it like cold wax.
- **Why here:** the relaxed-tameability ruling created a feeding gap (a tamed ossivel choir
  needs a native-safe food); hydrocarbon grazers cannot eat a warm-safe feed by ban 3.
- **Mechanism + cost:** vanilla PlantDef + one new item ThingDef copying `RM_ColdWax`'s comp
  stack; high `ingestible.nutrition` on the plant for grazing. **XML only. Cost S.**
  Art: plant + item icon.
- **Collision:** `qeshra` — 0 substring hits; no defName within 2 edits; nearest words are
  2-edit noise (`nashra`, `ephra`). **Clear.**

## 2. Uzhmek — HAZARD (tar-snarl)

- **Look:** a low snarl of knotted, glossy cords the colour of old tholin — rust-maroon
  shading to near-black, with a sticky sheen and sulphur-pale beads of exudate at the knots.
  Reads as tar that grew.
- **Where / behaviour:** mats across the ablation line and around wreckage, where pawns walk
  most. It is *slow ground*: crossing a mat costs heavily, and a pawn stuck in a mat is a
  pawn standing in a blast radius when the neighbouring chimeglobe goes up.
- **Harvest / yield:** cut → `RM_ColdWax` × 1 (no new item). Cutting a path is the player's
  answer — labour against risk.
- **Why here:** the biome's danger is chain detonation; Uzhmek makes *position* matter in it
  without adding a new damage source. Tholins are the signature hydrocarbon-haze solid —
  literally what the Haze leaves behind.
- **Mechanism + cost:** vanilla `pathCost` on the plant ThingDef (high, e.g. 40) +
  `PlantCharge`. **XML only. Cost S.** Optional later: a mild `RM_` slowed hediff on
  contact (C#, M) — not needed for v1.
- **Collision:** `uzhmek` — 0 substring hits, 0 near defNames, 0 near words. **Clear.**
  (Rejected en route: `thessrik` — 1 edit from `thessik` in `CastRoster_HUTT.xml`;
  `drekkash` — reads like `drekkis`, Abyss/Black Crags docs.)

## 3. Kethevar — MATERIAL (char-lace)

- **Look (living):** a hand-high spiral coil of pleated glassy ribbon, pale chartreuse-gold
  (perylene-yellow) with a faint inner glitter. **Look (yield):** a silver-black graphite
  lattice — the same coil, fused to carbon.
- **Where / behaviour:** rare singles on open ice. Harmless until killed.
- **Harvest / yield — the twist:** cut it and you get ordinary `RM_ColdWax` × 1. **Kill it
  with fire or a blast and it leaves `char-lace`** — a pure-carbon lattice, *not* a
  hydrocarbon, so it is the biome's one **warm-safe** product. Light, strong, beautiful: a
  stuffable material (or a component ingredient) the colony can bring indoors. The player
  earns it by *deliberately* detonating a field.
- **Why here:** turns the biome's defining hazard into a reason to set fires on purpose — the
  quarries' "it is all still here" economy, made from the plants.
- **Mechanism + cost:** vanilla `killedLeavings` on the plant ThingDef → new `RM_CharLace`
  ThingDef (stuff props). ⚠️ UNMEASURED: whether `killedLeavings` also fires on
  `KillFinalizeLeavingsOnly` (the harvest/cut mode) — verify against decompiled
  `Thing.Destroy`/`GenLeaving` before building; if it does, gate it in `CompPlantCharge`'s
  existing KillFinalize branch (≈10 lines C#). **Cost S (XML) or M (if the gate is needed).**
  Art: plant + item + stuff colour.
- **Collision:** `kethevar` — 0 substring, 0 near defNames, 0 near words at ≤ 2 edits.
  **Clear.**

## 4. Lisqueth — BEAUTY (fluorescent rosette)

- **Look:** a flat starburst rosette, waist-wide, of smoky-violet translucent ribs; the rib
  edges **fluoresce magenta-pink** (aromatic-hydrocarbon fluorescence under starlight). Dim
  and cool — never warm/orange: the krissek halo keeps *"the only warm light for a hundred
  kilometres."*
- **Where / behaviour:** sparse, in hollows. Gives a small, static, cool-pink light pool —
  the nightside's one natural lamp. High plant `Beauty`; colonists walking past get the
  beauty mood.
- **Harvest / yield:** cut → `RM_ColdWax` × 1. Killing the light is the cost.
- **Why here:** a pitch-dark plateau with no sun is exactly where a glowing plant is worth
  something — navigation and mood, and a field of them is a postcard.
- **Mechanism + cost:** vanilla `CompGlower` (glowstool precedent, static — no pulse, so
  `TWINKLE_FLORA_SPIKE_1`'s per-plant glow-cost verdict does not bite) + `Beauty` stat.
  **XML only. Cost S.**
- **Collision:** `lisqueth` — 0 substring, 0 near defNames, 0 near words. **Clear.**
  (Rejected en route: `sefrenn` — 2 edits from `sevren` in the neighbouring Nightside Ice
  review; `ylvekka` — near `RM_Vekka` and this biome's own `vekkit`.)

## 5. Oskelloth — BEAUTY / SALVAGE SIGN (wreck-sheen crust)

- **Look:** a flat crust of overlapping glassy scales, black underneath with a full
  **oil-slick iridescent sheen** — gold, green, rose and violet bands shifting by angle
  (thin-film interference, not pigment).
- **Where / behaviour:** grows only beside the fallen — wreckage, meteoritic metal, the
  freeze-dried dead at the ablation line — feeding on the hydrocarbon residue they shed. The
  crews' saying writes itself: *where the sheen is, the salvage is.* A Jawa signpost plant.
- **Harvest / yield:** cut → `RM_ColdWax` × 1; its value is the sign, not the yield.
- **Why here:** binds the flora to §5's "the ablation line surfaces the fallen" and to the
  scavenger-clan premise; no other biome has an ablation line.
- **Mechanism + cost:** the placement is the work — vanilla wild-plant spawning cannot target
  "beside wreckage." Needs a small spawn hook (a GenStep after the fallen are placed, or the
  fallen-injection code seeding it in a radius). **C#, Cost M.** Without the hook it is a
  plain rare crust (S) and loses its point. Depends on the fallen-injection work existing.
- **Collision:** `oskelloth` — 0 substring, 0 near defNames, 0 near words. **Clear.**
  (Rejected en route: `zhurrom` — near `RUT_Zhurr`/`RUT_Hurrok`; `ozzhik` — near
  `RM_Vozzik`.)

## 6. Vashpuk — MATERIAL (fuel well)

- **Look:** a squat waist-high bladder of smoky honey-amber translucent skin, a slow
  milky-white sediment swirling inside, ringed at the base by stubby clear feeder roots.
  Visibly *full*.
- **Where / behaviour:** rare, solitary. The biggest charge among the flora after the
  chimeglobe — and **it regrows after tapping**, so one bladder is a renewable cold-wax well
  the colony will build a cold path to and guard.
- **Harvest / yield:** tap (harvest) → `RM_ColdWax` × 6, and the plant survives, refilling
  over ~10 days. Overlap, stated plainly: cold wax already refines to chemfuel, so Vashpuk
  adds no new item — it adds a **reliable source**, the scavengers' fuel tap.
- **Why here:** a sandcrawler clan needs fuel; this is a fuel well that is also a bomb you
  must never let warm.
- **Mechanism + cost:** vanilla `harvestAfterGrowth` (the berry-bush regrow idiom) +
  `PlantCharge` at a large radius. **XML only. Cost S.**
- **Collision:** `vashpuk` — 0 substring, 0 near defNames; nearest word `vashik` (2 edits,
  `ludicrous_livestock_deep_design.md`, unrelated). **Clear.**

## 7. Collision sweep — method and result

Python script over every `.xml/.md/.csv/.py/.cs/.json/.txt` under `src/` and `design/`
(**5,527 files, 7,172 defNames, 95,548 distinct words**): case-insensitive substring per name;
Levenshtein ≤ 2 against every defName (prefix `RM_/RSW_/RUT_/ZBiome_/Plant_` stripped) and
≤ 2 against every word token. **Sanity probe `korrum`: 48 files** — the sweep can see.

| name | substring | near defName | verdict |
|---|---|---|---|
| qeshra | 0 | none | clear |
| uzhmek | 0 | none | clear |
| kethevar | 0 | none | clear |
| lisqueth | 0 | none | clear |
| oskelloth | 0 | none | clear |
| vashpuk | 0 | none | clear (`vashik` 2-edit, unrelated doc) |
| *rejected:* oruuk | 39 files | `RM_Grusk` | collides (`snoruuk`, `orruk`, `ruuk`) |
| *rejected:* ylvekka | 0 | `RM_Vekka` | too near own-biome `vekkit` |
| *rejected:* zhurrom | 0 | `RUT_Zhurr`, `RUT_Hurrok` | near-miss |
| *rejected:* thessrik | 0 | — | 1 edit from `thessik` |
| *rejected:* drekkash / sefrenn / skorrel / ozzhik | 0 | various | near-misses |

Not swept: game `Data/`, local `Mods/`, workshop (the Carbon Garden sweep covered those for
its names; do the same before any def ships).

## 8. Owner questions

1. The colour these six carry breaks the sheet's "glass-clear and grey underfoot" palette
   line, under your 2026-09-29 uniformity law. Keep them coloured (tinted glass), or tone some
   back toward clear?
2. Kethevar's char-lace is the biome's one warm-safe product. Allowed, since it is carbon, not
   hydrocarbon?
3. Oskelloth only works if it grows beside the fallen, which waits on the fallen being built.
   Take it now as a rare crust, or hold it until then?

## Card draft

- **Qeshra** — scarlet bead cushions natives graze; harvest is the feed for tamed natives. Gives tamed animals food, but herds it attracts bring predators.
- **Uzhmek** — rust-black tar snarl that makes ground slow to cross. Makes fights about position, but colonists waste time cutting paths.
- **Kethevar** — golden coil; burn it and it leaves a black carbon lattice, the biome's only material you can bring indoors. Rewards setting fires deliberately.
- **Lisqueth** — violet rosette glowing soft pink, the dark side's only natural lamp. Cheap beauty and light; adds no resource.
- **Oskelloth** — oil-sheen crust that grows only beside wreckage, so it marks salvage. Most flavourful, but needs extra code and waits on wreckage.
- **Vashpuk** — amber fuel bladder you can tap repeatedly. A steady fuel source, but a large bomb sitting in your supply line.
