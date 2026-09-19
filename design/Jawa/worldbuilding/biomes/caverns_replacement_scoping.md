# Caverns replacement scoping — CAVERNS_REPLACEMENT_SCOPING_1

Owner's order (2026-09-18): "Show me the replacement cost... isn't this where the
crystalline caverns come from? Scope out working a replacement right now given its issues."

Scope: the Biomes! family — Caverns (`biomesteam.biomescaverns`), Polluted Lands
(`biomesteam.biomespollutedlands`), Fossils (`biomesteam.biomesfossils`) — against the
standing KEEP-until-our-versions-retire-it ruling (`BIOMES_CAVERNS_DEEPSCAN_1`). All
counts MEASURED 2026-09-18 unless marked; census base:
`infrastructure/state/items/closed/BIOMES_CAVERNS_DEEPSCAN_1.md` and
`Transient/biomes_caverns_deepscan_2026-09-18.md`.

## 1. What we actually use today

**No BMT biome holds a surface tile on Ash'karr, by executed ruling.** The three
BiomeDefs enter worldgen via `workerClass GeologicalLandforms.ConfigurableBiomeWorker`
(donor `1.6/Defs/Biomes/BMT_CrystalCaverns.xml`; scores `depthInCaveSystem` 2-3 and
temp −15..5 °C per `LANTERN_DEEPS_INJECTION_1` spec §1) — and worldgen never runs on the
frozen world. The painted tiles they once had are gone:
- `BMT_FungalForest` 425 tiles → dissolved into the Rot/Wasteland,
  `FUNGALFOREST_RAID_MERGE_1` **done**, closed `1ad5a21d`.
- `BMT_CrystalCaverns` 578 tiles + 829 ring tiles → re-homed to ice sheet / Blue Desert,
  `HORRORWASTES_BIOME_DISSOLVE_1` **done**, closed `bb437a16`. Hard ban in the frozen
  sheet: "`BMT_CrystalCaverns` never holds a surface tile again"
  (`the_lantern_deeps.md` §6.1).
- `BMT_EarthenDepths`: never placed; its only reference in our source is a −4
  suppression scoreOffset (`src/RimUtinni/UtinniPatches/Patches/JawaWorld_BiomeMix.xml:151`).
- (Tile zeros are per the closed items; not re-parsed from the live `.rws` this pass — a
  save re-count at cut time is cheap insurance.)

**The one live route into a BMT biome is OURS**: `RUT_LanternDeepGenerator`
(`src/RimUtinni/LanternDeeps/Defs/MapGeneration/RUT_LanternDeepGenerator.xml:12`) — a
pocket-map MapGeneratorDef whose `pocketMapProperties/biome` is `BMT_CrystalCaverns`,
reached through two entrance buildings (emergence + mineshaft). The LanternDeeps mod is
**built, validated, deployed offline, with real Mod Settings**
(`LanternDeepsMod.cs:18,92`); item BLOCKED only on a live quicktest.

**Creatures (~90 PawnKindDefs):** `decisions_propagated.json` rules ~125 distinct `BMT_`
defNames (MEASURED, token census). `BMT_FAUNA_ABSORPTION_1`: **68/68 ruled creatures
already ported** to `RSW_*` in SWBestiary (274 defs incl. dependencies, 440 donor
textures copied; item file, FOUNDRY pass 2026-09-11). The 7 stragglers (ChemSnail ×2
biomes, CaveSpider, GiantSlug, GiantSnail, Pillbug, GlowBat) are **RULED CUT**
2026-09-11, deletion of their live biome rows still owed. `cast_assignment.csv`: 36
BMT-lineage rows, 26 already repointed to RSW ports; the stragglers remain, plus
**`BMT_Maguana` — live in the Forge trio (`RUT_TheForge.xml`, cast rows ×3), NOT among
the 68 ports (`RSW_Maguana` absent from src) and NOT in the cut ruling.** One unported
kept creature.

**Plants (~98):** `src/RimUtinni/UtinniPatches/Patches/BiomeFlora_Ashkarr.xml` today
carries **104 `BMT_` tokens, 39 distinct plant defNames** (down from 131 at
`mod_retirement_audit.md` §5 — the Rot's own def now runs on **34 `RUT_` plants** from
the RotSporeKit ingest, `RUT_TheRot.xml`). 89 files under `src/` still reference `BMT_`
somewhere (includes Polluted Lands fish and guarded compat patches).

**Other live couplings, MEASURED this pass:**
- ✅ **The shipped ideoligion — CLEARED 2026-09-18** (ruling 4). `src/Jawa/ideoligion/The
  Salvation.rid` names `RUT_FungusEating_DontCare`, our own twin in
  `src/RimUtinni/UtinniPatches/Defs/PreceptDefs/RUT_FungusEating.xml`. `FungusEating` is a
  vanilla Ideology issue, so only the position was donor-owned. Owed before the cut: deploy
  + game load + re-take the dump + re-run `validate_save_artifact.py`; and the same swap
  inside the baked `Ideo` of the canonical save, which still holds the donor defName.
- **SeasWaterline (folded into SWBestiary)**: `loadAfter` only, no hard dependency any
  more (`SWBestiary/About/About.xml:50`); `Waterline_Lane1.xml` holds 52 `BMT_` fish
  references in `PatchOperationConditional` blocks — they go silently inert on a cut
  (5 borrowed fish vanish from the lanes without an error).
- **Fossils**: our only coupling is the museum-thought text patch in
  `PawnFlavor/Patches/PawnFlavorPhase2_ThoughtDef.xml` (100 `BMT_VisitedMuseum` hits),
  entirely inside `PatchOperationFindMod` — inert on removal.
- **`GameCondition_SporeCloud` gate is already cleared in source**: `RUT_RotSporeKit_SporeCloud.xml:44`
  points at our own `RimMandrake.EnvironmentalHazards.GameCondition_EnvironmentalWeather`
  (ROT_SPORECLOUD_PORT_1) — `BMT_FAUNA_ABSORPTION_1`'s BLOCKED line still lists it and
  is stale on that gate.

## 2. The crystal caverns replacement

**Route recommendation: keep the pocket-map route. Not a biome tile, not a map
mutator.** The evidence: the owner's hard ban on worldmap placement
(`the_lantern_deeps.md` §6.1), the frozen world (a mutator would have to be authored
onto specific frozen tiles and still only alters a HOST map — the ruled experience is a
separate persistent underground layer), and the fact that the pocket-map build **already
exists and is deployed** (`LANTERN_DEEPS_INJECTION_1`, blocked on quicktest only). The
replacement is therefore not "build a crystal caverns" — it is **make the existing
Lantern Deeps pocket map donor-free**, so Biomes! Caverns can leave the load.

What the pocket map still borrows from the donor (MEASURED from
`RUT_LanternDeepGenerator.xml` + donor defs):

| borrowed piece | donor content | replacement |
|---|---|---|
| the biome def itself | `BMT_CrystalCaverns` (isCavern, `BMT_Calm` weather, disabledIncidents) | 1 new `RUT_` BiomeDef + 1 WeatherDef, data only |
| terrain | `terrainsByFertility`: vanilla Gravel/Soil/WaterShallow + `BMT_Crystal` terrain + `BMT_Crystal` TerrainAffordanceDef | 1-2 RUT TerrainDefs + 1 affordance, data + 1-2 textures |
| crystal formations | GenStepDef `BMT_CrystalsGenerator` → C# `BiomesCaverns.GenSteps.GenStep_ScatterCrystals` + crystal building ThingDefs (sowable blue crystal line) | one Scatterer-pattern GenStep in our DLL (we already ship 4 GenSteps in this mod: portal ×2, kyber, pyrinth) + ~4-8 building/plant defs |
| flora | 12 `wildPlants` (mycelium, gleamtip, crystalcap, grey lady, glow-fungi…) | port as RUT defs, art copied from donor per the SWBestiary precedent; partial overlap with RotSporeKit flora already ported |
| fauna | 28 `wildAnimals` − 6 evicted crystal animals (our `RUT_LanternDeepEvictCrystalFauna.xml` already strips them) | repoint the ~22 survivors to the **existing `RSW_*` ports** (glowslug, aaroxis, shatterjaw, bloodrop line etc. are already in SWBestiary) — data only |
| dropped outright | Caveworld Flora Unleashed sub-pack (`MapComponent_CaveFungus` fungus spreader) | nothing — vanilla `WildPlantSpawner` grows the ported flora; our darkness mechanic is already a correctly-scoped `CustomMapComponent` |

Also owed at the same sitting: repoint the KotOR crystal-formation injector
(`Armoury/.../Absorbed_Kotorweapons_BiomesCaverns_Patch_KotORCrystalFormationInjector.xml`,
un-gated, would go silently dead) at our new GenStepDef, and swap the `.rid` precept
(§1). Mod Settings: LanternDeeps already ships them; the new toggles (crystal density,
collapse on/off if built) join the existing screen.

**Art volume:** ~12 plant sprites + crystal formation set (several sizes) + 1-2 terrains
≈ **20-30 textures, all copyable from the donor** (precedent: 440 files copied verbatim
for the fauna port). Zero generation required unless the owner orders a restyle.

**What is NOT replacement:** the sheet's crystal-life cast — the Lantern, the Creep, the
Cleavers, the Chorus, the Shard-minds animating dead gear (`the_lantern_deeps.md` §4,
"Owed: crystal-life authoring") — is **new content already owed by the frozen sheet**,
donor or no donor (the donor's crystal fauna is evicted by hard ban 3). It is its own
L-sized C#+art program and should not be billed to the retirement.

**Effort tier: M.** One C# GenStep on an existing pattern in an existing DLL, ~20-30
data defs, art copy, the `.rid` precept swap, then a deploy + dump refresh + quicktest
round. The drivers are the GenStep and the expensive-list cycles (deploy, dump, save
re-ingest for the precept), not authoring volume. It becomes L only if the owner bundles
the crystal-life cast or a collapse mechanic into the same wave.

## 3. The other two biomes

- **`BMT_EarthenDepths` — cut without replace.** Zero tiles ever placed, no sheet, no
  ruling builds on it, only reference in src is a suppression offset (§1). Its generic
  rock-cavern niche is fully covered by the Lantern Deeps + the ruled cave-entrance
  program. Nothing to build.
- **`BMT_FungalForest` — already replaced in substance.** The raid-and-merge is done
  (RotSporeKit: spore kit, terrains, drugs, hediffs, guardian groves as RUT defs; the
  Rot's def carries 34 RUT plants). Residue at cut time: the handful of `BMT_` entries
  still in `RUT_TheRot.xml` (Brightbells + the ruled-cut straggler animals) and the
  BiomeFlora rows among the 39 distinct (§1). Sweep work, not build work — no new biome.

## 4. The cut path

Ordered so each step is independently shippable and nothing dangles:

1. **Fossils (LOW) — first, nearly free.** Couplings: 2 donor patches outward, our
   museum-thought patches FindMod-guarded (inert). One real gate: **the canonical save**
   — "safe to add, not safe to remove" means placed fossil/museum Things are a third
   reference class (donor-retirement lesson). Grep the `.rws` for its defNames before
   cutting; if present, the cut lands with the next save-era regen. Unblocks: proves the
   family-retirement pattern cheap, drops 1 mod from the 599-load.
2. **Polluted Lands (MEDIUM) — after the owner's mutation ruling (§5 Q2).** It ships
   zero biomes; its value is 39 creatures/40 plants injected into 23+ biomes plus the
   18-gene mutation system. If the ruling is DROP: delete/inert-check the 52 Waterline
   fish refs (already Conditional-guarded), repoint the ~dozen Wasteland/PoisonForest
   flora rows in BiomeFlora, keep the already-ruled `BMT_PustuleHornets` faction zeroing
   as historical. If REPLACE: the gene system is its own M-sized port item and should be
   filed separately, not block the family.
3. **Caverns (HIGH) — last, gated on §2 parity.** Gates, in order: (a) Lantern Deeps
   donor-free build (§2); (b) `.rid` precept swap + Salvation re-ingest; (c) BiomeFlora
   `BMT_` residue repoint (39 distinct, incl. FungalForest/Rot rows); (d) `BMT_Maguana`
   port-or-cut ruling for the Forge; (e) `BMT_FAUNA_ABSORPTION_1`'s one genuinely open
   gate — regenerate `BiomeCast_Ashkarr.xml` after deploy + dump refresh (the SporeCloud
   gate is already cleared in source, §1); (f) delete the 7 cut stragglers' biome rows.
   Note the absorption item retires `biomesteam.biomescore` in the same breath — Core is
   Caverns' dependency and goes with it, which is where the last `BiomesCore.*` class
   references must be checked.

**How the crash risk dies:** `MapComponent_CaveFungus` is a plain `MapComponent` in the
bundled `Caveworld_Flora_Unleashed.dll`. MEASURED via RimSage (`Verse/Map.cs`,
`FillComponents`, lines 710-748): the engine instantiates **every non-abstract,
non-Custom `MapComponent` subclass on every map** — so the fungus spreader lives and
ticks on every quicktest and surface map as long as the DLL loads, which is exactly why
it appears in two quicktest crash stacks. No def edit, Cherry Picker cut, or settings
toggle removes a MapComponent; **the crash surface dies at step 3 and only at step 3.**
(The only earlier mitigation would be hand-deleting the sub-folder inside the Steam
workshop copy — a donor-file edit Steam can silently revert; not recommended.)

## 5. Owner decision list

1. **Crystal art: copy or restyle?** Copy the donor's crystal/flora textures into RUT
   (fast, ships this wave, look unchanged) vs regenerate to the sheet's blue-on-black
   palette (owns the look, adds an art pass + your review round).
2. **Polluted Lands mutation system:** ✅ **RULED DROP** — owner, 2026-09-18 (ruling 6 of
   this doc's six questions, on the `CAVERNS_PARITY_BUILD_1` file event), and already
   executed 2026-09-09 in `BIOME_OWNERSHIP_WAVE_1`: `RUT_Wasteland`, `RUT_TheForge` and
   `RUT_RustCathedral` strip `BMT_Disease_Mutapox` from their disease lists because the
   Wasteland's disease register is radiological, not wildlife epidemiology. The 18
   `BMT_MutaGenes` have zero live consumers in our defs. Mechanism, for the record:
   `Transient/_polluted_lands_eval_2026-09-18.md`.
3. **The Salvation's precept:** ✅ **RULED (replace) and BUILT 2026-09-18** — `.rid` now
   names `RUT_FungusEating_DontCare`, def in `UtinniPatches`. The re-ingest turned out to
   be a no-op: the canonical start save's baked Salvation carries vanilla
   `FungusEating_Despised`, never the donor precept (MEASURED by parsing the save).
4. **Collapse/cave-in:** build the sheet's ruled collapse hazard into the donor-free
   Deeps now (adds C# to this wave, M→L risk) or defer it to the crystal-life program?
5. **Timing:** run the M-tier Caverns parity build now — the crash surface on every
   quicktest argues for it — or batch it with the next cold-load round alongside the
   LANTERN_DEEPS quicktest and the BiomeCast regenerate, since all three spend the same
   deploy + dump + load cycle?
