# Auxiliary art categories — assessment (2026-10-08)

Owner, 2026-10-08 ~10:55: *"I'm wondering how many of these auxiliary categories there even are."*
Later additions the same morning: *"Then there's an entire another category of dead versions of the body and
desiccated versions of the body. Perhaps there's even yet more to consider."* and *"I'm wondering if there are also
sleeping versions."*

This is analysis only. No defs, art or jobs were changed. Engine facts come from RimSage (decompiled 1.6 plus all
five DLCs), read 2026-10-08. Our usage comes from a python parse of `src/**/{Defs,Patches}/*.xml`: 2,396 files, 0
parse failures, 15,983 top-level defs, 8,956 PNGs under `src/**/Textures`, excluding dev tooling.

**Headline: there are 13 kinds of extra creature art the engine will load from a file, and 4 of them multiply all
the others.** Nine more states that you might expect to need art are drawn by the engine with no art at all. Plants
have 7 kinds of extra art and items have 2.

---

## 1. Taxonomy (measured from the 1.6 engine)

### 1a. Axes that MULTIPLY every other category

| # | Axis | Engine field | Multiplier | If absent (measured) |
|---|---|---|---|---|
| M1 | **Facings** | `Graphic_Multi` loads `_north/_east/_south/_west` | ×3 (west mirrors east) | `Graphic_Multi.Init`: west is east flipped. A missing north falls back to south (or east), rotated. |
| M2 | **Colour mask** | `_northm/_eastm/_southm` when the shader is `CutoutComplex` | ×2 on the files it applies to | No mask means no second-colour tinting. The rotting path forces plain `Cutout`, so rot never uses a mask. |
| M3 | **Life stage** | `PawnKindDef.lifeStages[i].*GraphicData` (every field in 1b is per stage) | ×(number of stages), usually 3 | Each stage needs its own `bodyGraphicData`, but every stage can point at the same texPath and only change `drawSize`. **550 of our 579 kinds do exactly that.** |
| M4 | **Gender** | `female*GraphicData` beside each field: body, dessicated, corpse, rotting, swimming, stationary; plus `flyingAnimationFramePathPrefixFemale` | ×2 | Each female field falls back to the male/default field. Fully optional. |
| M5 | **Variants** (alternate graphics) | `PawnKindDef.alternateGraphics` (weighted, `alternateGraphicChance`). Each one carries its own texPath, rotting, dessicated, swimming and stationary paths | ×(1+N) on body, swim, stationary, rotting, dessicated | Each variant field falls back to the base graphic. **Flight frames and corpse art ignore variants entirely**: `AnimationDefGenerator_Flying` keys only on life-stage colour and gender. |

M5 is a fifth multiplier, but it is optional and only some creatures use it. The "4 multiply all the others" in the
headline means M1–M4.

### 1b. Creature states that load separate art from a file

| # | Category | Engine field | When it shows | If absent (measured) |
|---|---|---|---|---|
| C1 | **Base body** | `bodyGraphicData` | always | Required. Without it there is no animal-style kind. |
| C2 | **Flying frames** | `PawnKindDef.flyingAnimationFramePathPrefix` + `FrameCount` → `<prefix><N>_{east,north,south}`. These are `Graphic_Single` frames with no mask, one set per kind, scaled per stage. | While airborne | No prefix means the creature still flies (the `MaxFlightTime` stat) using its static sprite, with no wing-beat. |
| C3 | **Swimming** | `swimmingGraphicData` (+female, +variant) | Spawned on a water cell **and** `WaterCellCost` has a value (race `waterCellCost`, a gene, flying, or `Swimming`) | Draws the land sprite. The ground shadow is suppressed while swimming either way. |
| C4 | **Stationary** (Odyssey: hermit crab) | `stationaryGraphicData` (+female, +variant) | Whenever the pawn is **not moving** and no animation is playing. That includes standing still and lying asleep. | Draws the normal sprite. |
| C5 | **Fresh corpse** | `corpseGraphicData` (+female). It takes the live sprite's colours. Also used by Anomaly mutants with `useCorpseGraphics`. | Dead, before rotting | **Reuses the live sprite**, laid on its side (see 1c). Vanilla uses this for only 4 races (cow group, squirrel group, a Biotech one). |
| C6 | **Rotting** | `rottingGraphicData` (+female, +variant) | `RotDrawMode.Rotting` | **Reuses the corpse/live sprite with a procedural rotten tint** (`PawnRenderUtility.GetRottenColor`). Vanilla ships no rotting art. |
| C7 | **Dessicated** | `dessicatedBodyGraphicData` (+female, +variant) | `RotDrawMode.Dessicated`, the skeleton stage | 🔴 **No fallback.** `PawnRenderNode_AnimalPart.GraphicFor` returns **null**, so the body node draws nothing and the desiccated corpse is **invisible**. Insectoids get a fixed tint over their dessicated art. Vanilla shares one dessicated texture across look-alike species, for example `Dessicated_Tortoise`. |
| C8 | **Pack / saddlebags** | Implicit path: `<body texPath>Pack_{dir}`, using the female body path if one exists | `race.packAnimal` **and** the animal's inventory is non-empty, so in a caravan or carrying goods | 🔴 **No fallback.** `GraphicDatabase.Get<Graphic_Multi>` on a missing path logs "Failed to find any textures" and draws **BadMat (magenta)**. |
| C9 | **Silhouette** | `silhouetteGraphicData` (a single image) | The zoomed-out or occluded silhouette | Falls back to the body graphic. Only Anomaly entities and fleshbeasts set it. |
| C10 | **Custom render-tree parts** | race `renderTree` / `PawnRenderNodeProperties.texPath` (extra layers: wings, glows, heads) | Per node | Opt-in. Note the 2026-09-19 ruling against wing layers for flight. |
| C11 | **Activity / entity graphics** (Anomaly) | `Graphic_ActivityMask`, `Graphic_ActivityStaged` on entities | By activity level | Opt-in, entities only. |
| C12 | **Derived item art** | Egg (`CompProperties_EggLayer` items), leather/meat (auto-generated, generic) | Items, not the pawn | Eggs need art. Leather and meat need none. |
| C13 | **Shadow** | `ShadowData` (`volume`, `offset`) inside `bodyGraphicData`, plus `race.specialShadowData` | Standing only (`RenderPawnAt` skips shadows unless `posture == Standing`) | **Procedural mesh, no PNG.** Flight shadow is one shared material scaled by height. It costs numbers, not art. |

### 1c. States that need no art: the engine draws them itself (the owner asked about "sleeping")

| # | State | What the engine does (measured) |
|---|---|---|
| N1 | **Sleeping / resting / lying / downed** | **Rotation only.** `PawnRenderer.BodyAngle` rotates the live sprite: downed or dead uses `wiggler.downedAngle`; an animal lying down turns to West/East by thingID parity; `LayingFacing()` picks the facing. **There is no sleeping-graphic field anywhere in 1.6.** The one exception is C4: a creature with stationary art shows it while asleep, because asleep counts as "not moving". |
| N2 | Dead body (fresh) | Same rotation, live sprite (C5 overrides it if set) |
| N3 | Rotting | Tint (C6 overrides it if set) |
| N4 | Wounds and bandages | One shared library per `FleshTypeDef` (`genericWounds`, `bandagedWounds`). Per-hediff wounds are humanlike-only by default. No per-creature art. |
| N5 | Fire, firefoam, damage flash | Shared overlays (`PawnRenderNodeWorker_OverlayFirefoam`, `flasher`) |
| N6 | Mutant / shambler skin (Anomaly) | Tint via `MutantUtility.GetMutantSkinColor`, plus C5 corpse art when `useCorpseGraphics` is set |
| N7 | Invisibility, statues, portraits | Materials and shaders over the same sprite |
| N8 | Roping / leashes | Shared `UI/Overlays/Rope` |
| N9 | **Sheared, milked, pregnant, frozen, tame/bonded** | **No engine support.** A search across all 1.6 source for a graphic tied to shear, milk, pregnant, rope, pack, tame, frozen or burning found only the pack path (C8) and the rope overlay. These states do not exist as art without our own C#. |

### 1d. Non-creature families, for completeness

**Plants** (`PlantProperties`, read in `Plant.Graphic`):

- immature
- leafless
- leafless-immature
- polluted (Biotech)
- snow overlay, leafless snow overlay and immature snow overlay (3 fields)

That is 7 fields, and **every one falls back to the base graphic.** Leafless from poison has its own tint fallback.
Plants also get `Graphic_Random` variants. There is no harvested or dying graphic.

**Items:**

- `Graphic_StackCount`: images for 1, few and many
- `Graphic_Random` / `Graphic_Cluster` variants

**Humanlike species** use a separate system: body types, heads, hair, beards, tattoos, worn apparel per body type, and
`BodyTypeDef.bodyDessicatedGraphicPath`. Vanilla shares that art. It is out of scope here.

---

## 2. Use in our content (measured)

There are **579 animal-style PawnKindDefs**, defined as kinds whose life stages carry `bodyGraphicData`. They cover
575 distinct races: RM 344, RSW 217, RUT 14, other 4.

Sanity probes:

- `RM_Fessk` and `RSW_Gizka` were both found, as expected.
- A third probe, `RUT_Sytheclaw`, missed. That was my mistake in the name: the real def is `RM_Sytheclaw`.

| Category | Kinds using it | Points at OUR texture / at vanilla or donor art | Texture files in repo (name-pattern match) |
|---|---|---|---|
| C1 base body | 579 | 542 / 37 | 547 distinct body texPaths. Only 43 have a `_west`. |
| M3 distinct life-stage art | **29** kinds use more than one body texPath (28 use 2, 1 uses 3) | — | — |
| M4 gender (female body) | **18** (17 RSW + `RM_Aurrok`). Female dessicated: 6. Female swim: 1. Female flight prefix: 5. | 18 / 0 | "female" in animal textures: 8 names (the other 535 matches are humanlike/apparel) |
| M5 variants | **26** kinds, **98** alternates in total (20 RSW kinds, 6 RM) | — | ~435 files match a numbered/lettered-variant name pattern (UNMEASURED how many are creature variants) |
| M2 colour mask | 17 kinds use `CutoutComplex` bodies. 7 body texPaths have a mask file. | — | 31 masks in animal folders (332 repo-wide) |
| C2 flying frames | **29** of **64** races with `MaxFlightTime > 0` have frames. **35 flyers fly with no frames.** | 28 / 1 (`RM_Kirruk` points at vanilla `Chicken_Flying_`) | 297 frame files. 95 frame-sets in total: N=1 ×11 (BiomesTeam ports), N=3–5 ×15, N=8 ×2 |
| C3 swimming | **75** | 73 / 2 | 186 |
| C4 stationary | 4 (`RM_Piinnok`, `RM_Dhokkur`, `RM_Dhuvvox`, `RM_Dakkra`) | 2 / 2 | 0 named "Stationary" |
| C5 corpse | 4 (`RUT_CathedralRoach`, `RM_CathedralRoach`, `RSW_Pufferpig`, `RSW_Clodhopper`) | 4 / 0 | 6 |
| C6 rotting | 0 | — | 0 |
| C7 dessicated | **268** have it. 🔴 **311 kinds have none, so their desiccated corpse is invisible.** | 191 / 77. The 77 borrow vanilla look-alikes, and `Dessicated_Tortoise` alone serves 11 kinds. | 203 |
| C8 pack | 39 pack animals. 🔴 **36 have no `…Pack_*` texture in the repo.** That is a magenta candidate when they carry cargo. | — | 21 |
| C9 silhouette | 0 | — | 1 |
| C10 custom render tree | 6 kinds (`RM_DormantAnimalBody` ×2, `Devourer`, `RSW_Beldon`, `RSW_Lylek`, `RM_KethrelTree`) | — | 0 named "Wing" in animal folders |
| C12 eggs | 100 egg-layer races | — | UNMEASURED |
| Shear / milk | 16 / 20. No art is possible (see N9). | — | — |

**Caveats on the 🔴 rows:** my resolver follows `ParentName` within our own XML only. It does not merge inherited
child fields, and it cannot see donor or vanilla parents.

- The **36 pack-art gaps** are therefore candidates until someone checks them against merged defs or watches a live
  caravan.
- **Swimming has the same problem.** 31 races with `waterCellCost` have no swim art, and 15 kinds have swim art but
  no `waterCellCost` my resolver could find. That art never displays unless the field is inherited. UNVERIFIED either
  way.
- The **311 no-dessicated count** is reliable: it is a missing life-stage field, not an inherited flag.

**Plants:** 328 plant ThingDefs. Immature art 13, leafless 6, snow overlay 1, immature snow 1, polluted 0. 226 use
`Graphic_Random`.

**Items:** 265 ThingDefs use `Graphic_StackCount`, plus 3 `Graphic_MealVariants`, 9 `Graphic_Cluster` and 324
`Graphic_Random` across all ThingDefs.

---

## 3. Combinatorics

The unit here is a **facing set**: north + east + south, with west mirrored. Flight frame-sets count the same way.
The mapping from facing sets to artpipe jobs is an assumption: one job per facing set.

**One creature with every category populated.** Assumptions: 3 life stages, 2 genders, 4 variants (V = 5 counting the
base), a pack animal, a flyer with 8 frames.

| Category | Formula | Sets |
|---|---|---|
| body, swim, stationary, rotting, dessicated (5 states) | L3 × G2 × V5 each | 150 |
| corpse | L3 × G2 (variants ignored) | 6 |
| pack | L3 × G2 | 6 |
| flight frames | F8 × G2 (one set per kind, scaled per stage) | 16 |
| silhouette | L3 single images | ~1 |
| **Total** | | **≈ 179 sets ≈ 540 PNGs**, plus ~270 masks if CutoutComplex: **≈ 800 files** |

**Whole cast:** 575 races × 179 ≈ **103,000 facing sets, roughly 300,000+ PNGs.** That is the "extraordinarily large
amount" the owner suspected.

**What we populate today**, in measured sets:

| Category | Sets |
|---|---|
| body | 547 |
| variants | 98 |
| dessicated (ours) | 191 + 6 female |
| swim | 73 + 1 |
| female body | 18 |
| corpse | 4 |
| stationary | 2 |
| flight frames | 95, across 29 kinds |
| pack | ~7 |
| **Total** | **≈ 1,040 sets ≈ 1 % of full** |

**The three most expensive categories if populated fully:**

1. **Variants (M5).** These multiply five states at once: ×5 per state for 4 variants.
2. **Gender (M4).** ×2 on everything, including flight.
3. **Distinct life-stage art (M3).** ×3 on everything except flight.

Flight frames are the most expensive *single* state per creature, at 4–8 sets each. They are also the only state
with motion, so a stable body across frames is the hard part.

---

## 4. Policy options

Every figure below is an incremental job estimate, at one job per facing set.

| Tier | What it covers | Why | Jobs |
|---|---|---|---|
| **(a) Required for every creature** | **C7 dessicated** for the 311 kinds without it. A shared dessicated texture across look-alikes is fine, as vanilla does. **C8 pack** for the pack animals confirmed missing it. | These are the only two states that **break** when the art is absent: one is invisible, the other is magenta. | ≤ 311 (fewer if shared, perhaps ~150) + ≤ 36 → **~190–350** |
| **(b) Only where the creature's nature calls for it** | **C2 flight frames** for every `MaxFlightTime > 0` race, per the 2026-09-19 standing rule: 35 have no frames, and 11 ports have only N=1. **C3 swimming** for the 31 water-cost races without it. | Without these the behaviour reads as fake: gliding with no wing-beat, or walking on water. | 35 × 4 + 11 × 3 (topping up to 4) ≈ 173 frame-sets + 31 → **~200** |
| **(c) Only where gameplay or canon shows it** | **M4 gender** only where dimorphism is canon and visible at sprite scale (estimated 5–10 % of the cast). It applies to body, dessicated, and swim or flight where those exist. **C4 stationary** only for creatures with a real resting form (shell, coil, roost). **M5 variants** only where they already exist or canon shows colour morphs. | Visible and story-relevant, but optional. | ~30–60 creatures × ~2 sets → **~60–120** |
| **(d) Never: rely on the engine** | M3 distinct life-stage art (use `drawSize` scaling as 550/579 already do). C5 corpse, C6 rotting, C9 silhouette. Sleeping/downed (N1, rotation). Wounds/fire/mutant (N4–N6). Shear/milk/pregnant/frozen (N9, impossible without C#). Shadow (C13, numbers only). | The engine's fallback is correct and the state is mostly invisible. | **0** |

**Recommended policy, (a)+(b)+(c):** **~450–670 jobs.** That is about half of what exists today again, against
~103,000 if everything were populated.

**Order of work:**

1. Base static.
2. Dessicated and pack, derived from the approved base rather than regenerated from scratch.
3. Flight and swim.
4. Gender last.

### Interactions

- **Flyer stable-body study** (`D:\Luke\dev\RimMandrake\Transient\flyer_stable_body_study_2026-10-08.md`, still
  skeletal when this was written):
  - Tier (b) flight is exactly its scope. Its census should use the **64 `MaxFlightTime` races / 29 with frames /
    35 without / 11 at N=1** figures above as the population to regenerate.
  - Any flyer that also gets gender (5 already carry `flyingAnimationFramePathPrefixFemale`) doubles its frame-sets.
    Decide gender for flyers **before** regenerating frames, or the frames get done twice.
  - `RM_Kirruk` borrows vanilla `Chicken_Flying_` frames. It is a candidate for its own frames.
- **Sketto pilot** (`D:\Luke\dev\RimMandrake\Transient\sketto_design_2026-10-08.md`, still skeletal):
  - `RSW_Sketto` already has 4 frames × 3 directions. The pilot should fix the **frame count standard**: 4 like most
    of our flyers, versus 8 like vanilla birds. That one number scales tier (b) by 2×.
  - The pilot should also fix whether flight frames get their own `_m` masks. They cannot: they are `Graphic_Single`,
    and `flyingAnimationInheritColors` only tints. So a masked creature's flight frames must carry their colours baked
    in.
- **Dessicated is the cheapest large win.** It is the only category where 54 % of the cast currently renders
  *nothing*, and vanilla shows that one shared skeleton per body plan is acceptable.

Measurement scripts (throwaway):
`/home/mandrake/.seat-tmp/BENCH/claude-1000/-home-mandrake-rm-bench/de9591de-4057-4f6c-aad5-1e5606db025e/scratchpad/aux.py`
and `aux2.py`. The per-kind data is `kinds.json` in the same folder.
