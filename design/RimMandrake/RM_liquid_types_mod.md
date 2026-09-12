<!-- status: design brief — nothing here is built -->
# One Liquid System, Many Liquids — LIQUID_TYPES_MOD_1 (RimMandrake tier)

_Design brief, 2026-09-11, Fable pass. This doc **specifies**: no XML, no C#, no
art. Every value INVENTED here rather than derived from a ruling, sheet law, or
measurement is flagged **[INVENTED]**. Every engine claim below is verified
against the frozen official def dump (OFFICIAL-2026-08-29, capture
2026-08-29T13-30-02Z) or cites the file that verified it._

**The ruling this executes (owner, Rust Cathedral sitting 2026-09-06, verbatim
on the filing event):** *"I think we should author a mod for many different
kinds of water. This is true within tilemaps as well as on the worldmap.
Boiling water. Frigid water. Normal water. Liquid propane. Slime. Ooze. Tar.
Acid. Poison. Mineralized. coolant. (make up some more). Change the viscosity,
different damage types, acidity vs basic nature, color, fine sand, oil, and
opacity. Totally a good idea. Make a ticket for it. Indexing it into every
other mod will be the trick here."*

## 0. Identity and naming (per `design/NAMING_SCHEME_PLAN.md`)

| surface | value |
|---|---|
| tier | **RimMandrake** — passes the test: *a medieval-tribe player installs this alone and understands it.* Acid pools, tar pits and frozen water need no Star Wars and no Ash'karr |
| packageId | `mandrake.rm.liquidtypes` |
| display name | `RimMandrake: Liquid Types` |
| defName prefix | `RM_` throughout |
| folder | `src/RimMandrake/LiquidTypes/` |
| C# namespace | `RimMandrake.LiquidTypes` |
| DLC posture | TerrainDef suites + property extension: **base game**. The dump's `ToxicWater*`/`Lava*`/`HotSpring` calibration anchors are Odyssey content — anchors for VALUES only, never dependencies. No Odyssey def is referenced by name in shipped XML |
| campaign consumer | a thin **RUT layer** (§7) maps Ash'karr's ruled liquids onto the system |

**No worldgen, in any version.** The mod defines liquids; it never generates or
places them. On Ash'karr every placement is hand-authored on the frozen map;
for any other player, placement belongs to whatever biome/scenario references
these terrains. There is no knob here that could roll a planet.

---

## 1. What the engine already does — measured, not guessed

Verified against the frozen dump's `TerrainDef.json` (1,340 terrains) and
`LIQUID_BIOMES_MAP_1_RECONCILIATION.md`'s IL-verified findings. RimWorld 1.6's
TerrainDef natively carries **most of the owner's property list**:

| owner's property | native field(s) | evidence from the dump |
|---|---|---|
| viscosity (move cost) | `pathCost`, `passability`, `extraDraftedPerceivedPathCost` / `extraNonDraftedPerceivedPathCost` | WaterShallow 30/Standable, WaterDeep 300/Impassable, LavaShallow 300/Standable — "thick" is already expressible |
| damage on contact | `burnDamage` + `burnIntervalTicks`, `igniteRadius` + `ignitePawnsIntervalTicks`, `dangerous` | LavaShallow 3/120 + ignite 1.9/240; our own `RUT_ScaldWater*` ships 1–2/300–240 bracketed between HotSpring (0/0) and lava |
| poison | `toxicBuildupFactor` | Odyssey ToxicWaterShallow = 3, VEE_SulfuricWaterShallow = 1 |
| heat | `heatPerTick`, `meltSnowRadius` | HotSpring 0.01/4, Lava 0.25/4 |
| freezing | `canFreeze` | true on vanilla waters, false on HotSpring/lava/AB_PropaneLake |
| salinity / fishing bucket | `waterBodyType` | enum is exactly `None`/`Freshwater`/`Saltwater`/`Other` (ilprobe, reconciliation §1) — **the only salinity granularity the engine has** |
| color / glow | texture + `glowRadius`/`glowColor` | RUT_ScaldWater carries the cyan (2,154,229)/r2 |
| water look & feel | `edgeType: Water`, `waterDepthShader`, `takeSplashes`, `traversedThought`, `avoidWander`, `extinguishesFire`, `driesTo` | identical across every modded water in the stack — this is what "cloned off vanilla water" buys |
| mood of wading | `traversedThought` | SoakingWet / ToxWater / HotSpring / VEE_SulfuricWater — one ThoughtDef per liquid is the established grammar |

**What has NO native field — the mod's actual C# surface (§4):** acidity vs
basicity; opacity as mechanics (it is art/shader only); a damage TYPE other
than burn/toxic (acid gear corrosion, cold-shock); immersion (deep) vs contact
(shallow) severity split; ignition of the liquid BODY (lava's `igniteRadius`
ignites pawns, never the sea); sediment/oil as surface films.

---

## 2. Prior art in the live stack — learn, don't duplicate (spec's order)

All present in the frozen dump; none is a dependency:

- **Odyssey `ToxicWater*`** — the DLC itself ships a full 6-def toxic clone of
  the vanilla water family (`toxicBuildupFactor 3`, own `ToxWater` thought,
  `waterBodyType Other`). The pattern is first-party canon.
- **Vanilla Landmarks Expanded `VEE_Sulfuric*` / `VEE_Irradiated*` /
  `VEE_Anima*`** — the VE answer the spec asks about: per-flavor suites cloned
  off vanilla, one thought each, `toxicBuildupFactor` for harm. No property
  layer, no generator — every suite hand-authored, which is why VEE stops at
  three flavors.
- **GRiNDTerra Biomes** — SIX full recolored water suites (Clean, GreenSpring,
  Purple, GRimond, GRuby, Toxlands), ~7 defs each. Proof of the combinatorial
  explosion: flavors × 7 defs is exactly what a generator must own (§5).
- **Alpha Biomes** — `AB_PropaneLake`, `AB_Tar`/`AB_ArtificialTar`,
  `AB_LiquidSlime`, `GU_RedWater*`: the campaign's donor liquids. Notably
  **inert**: AB_PropaneLake and AB_Tar carry zero damage, zero ignition,
  `extinguishesFire: true` — a propane sea that puts fires out. Flavor
  paint, no properties. This mod is what makes them mean something.
- **Biomes! Core** — `BMT_DeepWaterBridgeable` appears on EVERY water in the
  stack including vanilla's: third parties patch vanilla waters by defName,
  which is the indexing problem in the wild (§5).
- **Dubs Bad Hygiene** — consumes the `dbh_water` tag; present on vanilla
  waters, absent from Odyssey's own ToxicWater. A cloned suite that forgets a
  consumer tag silently breaks that consumer (`RUT_ScaldWater.xml` already
  learned this).
- **Our own `RUT_ScaldWater*`** (`src/RimUtinni/UtinniPatches/Defs/TerrainDefs/
  RUT_ScaldWater.xml`, shipped 2026-09-06) — the house prototype: 6 defs off
  the `Name=`-carrying bases (`WaterDeepBase`/`WaterChestDeepBase`/
  `WaterShallowBase` — the ONLY safe parents; `Lake`/`Ocean`/`IceSheet` carry
  no `Name=`), boiling-lift damage values, `gravshipReplacementTerrain`
  repointed within the family so a gravship landing never converts boiling
  water back to vanilla water. Everything it did by hand, §5's generator does
  by table.

---

## 3. The architecture — evaluated as the spec asked

**Ruling sought: adopt route A.** Per-liquid TerrainDef suites cloned off the
vanilla bases (engine water logic — pathing, fishing, bridges, splashes,
shaders — holds for free) **+ one `RM_LiquidProperties` ModExtension** on every
liquid terrain (ours AND, by patch, vanilla/DLC/donor waters) that the C#
systems read **+ a build-time generator** that emits the suites and the
compatibility patch index from one data table. Alternatives considered:

- *Custom `RM_LiquidDef` def type with a custom loader* — rejected: the
  `<li>` custom-loader trap discards whole defs silently
  (`rimworld-custom-loader-li-trap`), and a new def type is invisible to every
  existing consumer. The TerrainDef IS the liquid's engine face; fighting that
  buys nothing.
- *Properties as C# comps on terrain* — rejected: TerrainDef has no comp
  system (comps are ThingWithComps machinery). ModExtension is the engine's
  own extension point for exactly this.
- *One shared "liquid" terrain recolored at runtime* — rejected: fishing,
  biome terrain-override fields, patches and saves all address terrain by
  defName; a runtime-colored singleton is invisible to all of them.

### The property extension — `RM_LiquidProperties` [field set INVENTED, build verifies each against a real consumer]

```
viscosityClass   thin | water | thick | heavy      (documents the pathCost the generator wrote; C# may read it for swim/wade speed later)
pH               0..14, water = 7                   (acid < 4 and base > 10 trigger §4's corrosion at scaling severity)
damageOnContact  DamageDef + float                  (shallow/wading)
damageOnImmersion DamageDef + float                 (deep/chest-deep — the split the engine lacks)
opacity          0..1                               (art contract + §4's fish/visibility hook, v2)
surfaceFilm      none | oil | sediment | scum       (film variants, §4c)
flammable        bool + igniteTemp                  (the liquid BODY; §4b's propane rule)
freezesTo / boilsAwayTo                             (TerrainDef refs — extends native canFreeze/driesTo grammar)
```

Native fields stay authoritative where they exist (toxic buildup, burn ticks,
heat, glow, waterBodyType); the extension carries only what the engine cannot
say. **A liquid with an empty extension is still a complete, working liquid** —
the mod degrades to "VEE with a generator," and the game is whole with the C#
absent.

---

## 4. The C# systems (small, each its own spike)

a. **Corrosion/pH** — a MapComponent (or terrain-aware hediff giver) applying
   `RM_AcidBurn` [INVENTED hediff] to pawns in liquid with pH beyond
   thresholds; apparel/armor takes proportional HP loss (the part XML cannot
   do). Basic liquids mirror at the other end of the scale — same code path.
b. **Ignition of a flammable body** — `flammable` liquids catch from an
   adjacent fire/explosion/hot source and propagate across contiguous liquid
   cells. 🔴 Binds `the_propane_lakes.md` hard ban #4 verbatim: **no ignition
   without a thermal or electrical trigger** — the system IS that rule,
   generalized. (Donor AB_PropaneLake's `extinguishesFire: true` is corrected
   by the RUT layer's extension patch, not by editing the donor.)
c. **Surface films** — oil/sediment/scum as a per-cell overlay (fire spreads
   on an oil film over water; sediment settles to `driesTo` variants). Honest
   sizing: this is the largest and least-precedented system — **v2 candidate**,
   ships last or not at all [INVENTED scope — owner may cut].
d. **Cold liquids** — frigid/cryo damage: verify at build whether negative
   `heatPerTick` behaves (UNMEASURED — never assumed); else the corrosion code
   path with a hypothermia-accelerant hediff.

---

## 5. "Indexing into every other mod" — the trick, made concrete

Three directions, three answers:

1. **What third parties gave vanilla waters must reach ours.** BMT affordances,
   DBH tags, TST meditation affordances all land on vanilla defs by patch. So
   the generator **clones each suite from the frozen dump's POST-PATCH shape**
   of the vanilla leaf — the resolved def as the live stack actually has it —
   not from raw Core XML. Union-carried tags/affordances ride along exactly as
   `RUT_ScaldWater` hand-carried `dbh_water`. Regenerate when the owner
   re-freezes the dump; never regenerate against a live capture (dumps decay).
2. **What we are must reach third parties.** The generator also emits a
   **patch index**: `PatchOperationFindMod`-guarded patches adding our
   extension (with sane defaults: pH 7, water viscosity) to OTHER mods'
   water terrains — Odyssey toxics, VEE suites, AB liquids — so OUR systems
   see THEIR liquids. ⚠️ A patch that matches nothing logs nothing: the
   index ships with a validation list `validate_patch.py` can check.
3. **What cannot be reached, named.** C# that hard-compares
   `TerrainDefOf.WaterShallow` by reference will never know our terrains.
   Accepted limit, documented per-consumer in the compat notes; where it
   matters (fishing did — `waterBodyType` covers it) the engine's own
   field is the bridge, not a Harmony patch. Harmony here only by proven
   need, per case, at build.

**Map-gen indexing without worldgen:** `BiomeDef.waterDeepTerrain` /
`oceanShallowTerrain` / etc. (IL-verified, reconciliation §1) is how a biome
elects a liquid suite for its LOCAL maps. The RUT layer sets these on the four
liquid biomes; any other mod's biome opts in the same way. Plus
`gravshipReplacementTerrain` repointed within each family (RUT_ScaldWater's
precedent) so landings never launder a liquid back to water.

---

## 6. The liquid roster — owner's list plus the extensions he asked for

Mechanics columns are the GENERATOR'S INPUT ROW, not new rulings; campaign
values defer to frozen sheets. All numbers [INVENTED unless cited].

| liquid | base | native fields carry | extension carries | first consumer |
|---|---|---|---|---|
| normal water | vanilla (no clone) | everything | pH 7 row via patch | baseline |
| boiling water | `RM_WaterBoiling*` | burn 1–2/300–240, no-freeze, glow — **values already ruled** (`REGROWTH_BOILING_LIFT_SPEC.md` R-B4a, shipped in RUT_ScaldWater) | immersion>contact split | the Scald; terminator boiling shores |
| frigid water | `RM_WaterFrigid*` | canFreeze, pathCost ↑ | cold-shock damage (§4d) | nightside open water |
| brine (grades) | `RM_WaterBrackish*` / `RM_WaterBrine*` | `waterBodyType Saltwater` (the engine's whole salinity axis) | pH ~8, viscosityClass up the ladder | Greentide fresh→brackish→brine→**salt grave**; Twilight/Grey seas; Miasma muck; Grey Deep saturated brine |
| acid | `RM_Acid*` | dangerous, toxic 1 | **pH 1–3, corrosion** | Scarlands rainbow pools ("the color isn't life, it's reaction and acid" — owner) |
| poison | `RM_WaterPoisoned*` | `toxicBuildupFactor` 2–3 (Odyssey anchor: 3) | — | Scarlands all-toxic variants |
| liquid propane | `RM_Propane*` | no-freeze, cold | **flammable + igniteTemp (§4b)**, thin viscosity | the Propane Lake (57 painted tiles; hard ban #4 rides the mechanism) |
| tar | `RM_Tar*` | pathCost 300 Standable ("walk in, slowly"), no-splash | heavy viscosity, film=scum, trapped-wildlife hook v2 | the Sump ("the only liquid is tar" — its sheet's ban #4; grades owned here) |
| slime | `RM_Slime*` | AB_LiquidSlime shape | thick viscosity | the Slime biome / `RM_GelatinousSlime` (that mod authors its OWN suite; this mod supplies the property grammar it fills in) |
| ooze | `RM_Ooze*` | between slime and mud | thick, film=sediment | wetland grades |
| mineralized | `RM_WaterMineral*` | `waterBodyType Other` | pH 9–10 basic, sediment | hot-spring country, the Flats' margins |
| coolant | `RM_Coolant*` | mild toxic 1, no-freeze, faint glow | pH 7, thin | Rust Cathedral canals — the 8 river tiles ("liquid properties ride LIQUID_TYPES_MOD_1", sheet §3); fish bucket follows §CARD-2 |
| **made-up, as invited:** | | | | |
| rainbow reaction-liquor | `RM_ReactionLiquor*` | heatPerTick + toxic + dangerous | pH extreme, opacity 0 (crystal-clear lie) | the rainbow pools' exact chemistry |
| fuel-sap liquor | `RM_FuelSap*` | — | flammable, thick | Greentide stills (economy, mostly containers not terrain) |
| blood/ichor | `RM_Ichor*` | — | film=scum, opacity 1 | Webwork nests [INVENTED — no sheet ruling; RUT layer only if its sheet adopts it] |
| cryo-ammonia | `RM_Ammonia*` | no-freeze at map temps | cold-shock + mild corrosion (polar solvent) | the Ammonia Flats |
| mud grades (churnmud) | native `Mud`/`Marsh` + one `RM_Churnmud` | pathCost ladder | sediment film | wet-season crossings |

Suite depth is per-liquid, not always 6: a canal or pool liquid ships
shallow+deep only; ocean/moving variants exist where a consumer does
(generator column, not doctrine).

---

## 7. The RUT layer (thin, campaign-side)

- Patches `RM_LiquidProperties` rows onto the already-shipped `RUT_ScaldWater*`
  (which otherwise stands — no rename, no re-authoring ahead of
  `NAMING_SCHEME_EXECUTION_1`) and onto the donor terrains the frozen map
  actually uses (`AB_PropaneLake`, `AB_Tar`, `AB_LiquidSlime`).
- Sets the BiomeDef water-terrain overrides on `RUT_TheScald`,
  `RUT_TwilightSea`, `RUT_GreySea`, `RUT_PropaneLake` (worldmap tiles already
  painted and frozen under `LIQUID_BIOMES_MAP_1` — this mod adds no tile).
- Assigns the Rust Cathedral's 8 canal tiles the coolant suite (map-authoring
  pass, bridge work, its own item at build).
- Salinity gradient on the Greentide river: per-map terrain assignment down
  the course (its sheet's "salinity map-gen" line) — placement rides that
  biome's build item, the liquids ride here.

## 8. Spike list (sizing per house precedent: prove on ONE def, measure, report)

| spike | proves | size |
|---|---|---|
| A — GENERATOR | one liquid row → suite XML off the dump's post-patch leaf, tag/affordance union, patch index + match-validation list | M |
| B — EXTENSION + CORROSION | RM_LiquidProperties loads; pH damage + gear corrosion on one acid def; game whole with DLL absent | M |
| C — BODY IGNITION | propane cell catches from adjacent fire only; propagation; extinguish state | M–L |
| D — COLD | negative heatPerTick verified or refuted (UNMEASURED today); frigid path chosen accordingly | S |
| E — CONSUMER PROOF | DBH drinks from a cloned suite; fishing respects waterBodyType on it; bridge/gravship behave | S |
| F — FILMS (v2 gate) | oil film over water burns off | L, deferred |

## 9. Open questions → CARD lines (frozen sheets: detail added above, no ruling touched)

1. **CARD — the Scald basin's salinity.** `RUT_ScaldWater` ships the lake
   variants Freshwater because no doc rules the basin saline (its own flagged
   open question, inherited here). Boiling terminal pan with eight inflows and
   no outlet argues brine; fresh keeps the DBH water economy live on the
   hottest coast. One word decides the fishing bucket and the thirst economy.
2. **CARD — coolant's fishing bucket.** `fish_bestiary_commission_2026-09-10.md`
   §canals: "fresh until LIQUID_TYPES_MOD_1 says otherwise." Options: fresh
   (eels stay ordinary fishing), Other (own bucket, own bestiary row). The
   coolant eels ruling reads better with Other; fresh is zero extra work.
3. **CARD — films in v1 or v2.** Sediment/fine-sand/oil is the owner's list;
   §4c prices it as the big system. Ship v1 without films, or hold v1 for them?

## 10. Sources read

- `infrastructure/state/items/LIQUID_TYPES_MOD_1.md` (the spec) ·
  `LIQUID_BIOMES_MAP_1.md` + `design/Jawa/worldbuilding/LIQUID_BIOMES_MAP_1_RECONCILIATION.md`
  (the four liquid biomes, IL-verified BiomeDef/TerrainDef facts)
- Frozen dump OFFICIAL-2026-08-29 `defs/TerrainDef.json` — every field/value
  cited in §1–§2 read from it directly
- `src/RimUtinni/UtinniPatches/Defs/TerrainDefs/RUT_ScaldWater.xml` (the house
  prototype and its verified traps)
- Biome sheets (all FROZEN; consumed, not amended): `the_propane_lakes.md`,
  `the_rust_cathedral.md`, `the_scarlands.md`, `the_greentide.md`,
  `the_sump.md`, `the_miasma.md`, `the_grey_deep.md`, `the_twilight_deep.md`,
  `the_fever_wood.md`, `the_scald.md`; `the_seas.md`
- `design/RimMandrake/RM_gelatinous_slime_mod.md` (tier precedent, format) ·
  `design/NAMING_SCHEME_PLAN.md`
