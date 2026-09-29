# The Cauldron (shipping as Poison Forest) — bedazzle review, 2026-09-28

Movement 1–2 of the bedazzle ritual (`BAROQUE_BEDAZZLE_PROGRAM_1`). Biome lives under TWO
names: shipping mod `PoisonForest`, owner-typed ruling 2026-09-27 renames it **The Cauldron**
(rename executed at this sitting, censused below — NOT executed by this review).

## What's there

**Item:** CAULDRON_BEDAZZLE_SITTING_1 · **Program:** BAROQUE_BEDAZZLE_PROGRAM_1 (row 5)
**Author:** DESIGN subagent (Fable), movement 1–2 pass. Sources read this pass:
`src/RimMandrake/PoisonForest/` (all defs + C#), the frozen twin
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_PoisonForest.xml`, both Utinni patches,
`rosters/poison_forest.json`, the frozen sheet `poison_forest.md`,
`noncanon_beast_names_poison_miasma_desert_scar_rot_dune_waste_cracked.md` Batch 4a,
artpipe `registry.jsonl`/`done/`/`_artsrc/`.

### BiomeDef(s)

Two, deliberately (twin architecture, `biome_mod_architecture.md` §5):

- **`RM_PoisonForest`** — label already reads **"the Cauldron"** (the label was renamed
  ahead of the defName; the defName, folder, packageId etc. are the rename census below).
  `src/RimMandrake/PoisonForest/Defs/BiomeDefs/RM_PoisonForest.xml`. Ships in
  `mandrake.rm.poisonforest` ("RimMandrake: Poison Forest"), built 2026-09-25
  (`POISONFOREST_RM_MOD_BUILD_1`). animalDensity 0.8, plantDensity 0.5, Fog-dominated
  weather, 8 vanilla diseases, own worker `RM_BiomeWorker_PoisonForest`.
- **`RUT_PoisonForest`** — the frozen campaign twin (byte-frozen, serves the live world).
  Same content plus the 5 Star Wars rows inline. Not this sitting's to edit except via the
  ruled rename ticket (live-tile/savegame check gates any defName change).

⚠️ Disclosed in About.xml and real: the RM mod is **NOT donor-free** — the worldmap
texture (`Biomes/PoisonForest`, BiomesPlus) and 7 Alpha Biomes wildPlants rows carry no
MayRequire.

### Flora roster (def + patch-added, merged)

No Utinni flora patch exists for this biome — flora is all inline on the RM def
(shorthand `<DefName>commonality</DefName>` form, parsed as such):

| def | comm | provenance |
|---|---|---|
| `RM_TwistingThornwood` | 0.6 | OURS — dup of RUT_ original (also serves RUT_CrackedLands), tree, WoodLog |
| `RM_TreeMartyr` | 0.5 | OURS — dup, "weeping" yucca-form tree, WoodLog |
| `RM_DarkCrust` (vein moss) | 0.25 | OURS — black/purple/red phototroph film, the sheet §4 underclass made real |
| `AB_CrystalFlower` | 0.5 | Alpha Biomes donor, no MayRequire |
| `AB_BloodBouquet` | 0.4 | donor |
| `AB_RavenNettle` | 0.4 | donor |
| `AB_GiantAgariTox` | 0.3 | donor tree |
| `AB_RedBugloss` | 0.3 | donor |
| `AB_KeeningCordax` | 0.2 | donor tree |
| `AB_GiantToxicFlower` | 0.08 | donor (owner move 2026-09-20, wasteland → here) |

Note: both owned trees still yield plain `WoodLog` — the sheet's §7 "old trunks assay
richer than the rock" (bio-accumulated metal, the biome's stated reason to exist) has no
def expression anywhere. See scorecard mark 3 and slate candidate B.

### Fauna roster (def + patch-added, merged)

RM def inline (14 rows) — parsed from the element form, not `<li>`:

| def | comm | note |
|---|---|---|
| `RM_Suush` | 0.2 | OURS — floating shot-detonating drifter, built 2026-09-26 with real art (`SUUSH_CAULDRON_DRIFTER_1`, closed) |
| `GR_Beetlefleet` | 0.7 | VGE chimera, pops on death |
| `AA_InfectedAerofleet` | 0.5 | Alpha Animals |
| `AA_OcularJelly` | 0.5 | eye-heavy signature |
| `AM_Dryad_Corruptor/Ocular/Tumorous` | 0.4×3 | Alpha Memes; wild-function still UNMEASURED per roster confidence block |
| `Visceral` | 0.35 | Horrors, sealed insectoid |
| `AA_BedBug` | 0.3 | paralysing ambusher |
| `AA_CrystalMit` | 0.15 | crystal-fan match |
| `AA_GiantCrownedSilkie` | 0.15 | silhouette eye-test still owed (roster note) |
| `AA_DecayDrake` | 0.1 | |
| `AA_Helixien` | 0.1 | GIANT band, spd 0.6 gas-form decayer |
| `AA_Wildpod` | 0.05 | GIANT band, venomous |

Patch-added (`UtinniPatches/Patches/WildAnimals_PoisonForest.xml`, one
PatchOperationConditional op targeting `Defs/BiomeDef[defName="RM_PoisonForest"]/wildAnimals`,
gated `mandrake.rsw.swbestiary` — read from the op's own xpath+value):
`RSW_Neebray` 0.8 · `RSW_Mynock` 0.2 · `RSW_GraniteSlug` 0.15 (the sheet's only legal
herbivore — mineral-rasper) · `RSW_Screecher` 0.35 (**multi-homed ON PURPOSE** — owner
2026-09-22, migrates here↔Wasteland to lay; do not "fix") · `RSW_VentStalker` 0.25
(OURS — the sheet's §4 signature "eyeless vibration-sensing ambusher", built via
Kinrath-body reuse, `COMMISSION_LEDGER_CLEANUP_1`).

**Campaign cast: 19 wired species; RM-standalone cast without any donor present: 1
(the Suush).** See roster gaps.

**Roster-vs-wiring gap (adjudicate at the sitting, no action taken):**
`rosters/poison_forest.json` carries 7 owner-ruled "round2 move mapping" imports that are
wired NOWHERE (neither twin nor patch): `Lylek` (apex 0.05), `AA_Plasmorph`, `AA_LuciferBug`,
`AA_Radyak`, `AA_RipperHound`, `Skalder` (huge-grazer 0.08), `Silooth`. Two internal
contradictions inside the roster itself: `AA_RipperHound` is BOTH evicted (ban 9, spd 5.5
MEASURED) and imported; `Skalder` is a huge-GRAZER import into a biome whose frozen sheet
§6 hard-bans open grazing body plans ("there is nothing to graze"). These look like
homeless-disposition rows that predate the freeze discipline — the sitting should rule
wire-or-strike per row rather than anyone bulk-wiring them.

### Terrain

`RM_PoisonSoil` (fertility 0.85, pathCost 3) and `RM_PoisonSoilRich` (fertility 1.2) —
net-new owned TerrainDefs replacing the twin's phantom BiomesPlus terrains; reuse vanilla
Soil/SoilRich textures, zero terrain art of their own. Marsh for lake beach/mud,
vanilla Riverbank. No unique visible ground yet — the "mineral rings and beaded
condensate" of the sheet is unexpressed.

### Weather

Live block on both defs: **Fog 90 · DryThunderstorm 1 · everything else 0.** That is a
donor placeholder wearing a ruled biome's clothes. The four weathers were **RULED and
ratified by owner card 2026-09-12** (sheet §4b): **scatter-dusk** (the standing state) ·
⭐ **vent bloom** (venting surge, toxic buildup outdoors, the signature hazard) ·
**vapour bank** (chemical fog) · **dewfall** (the only "precipitation"; every wet surface
is a dosed surface). Def work explicitly unblocked since 2026-09-12 and **zero WeatherDefs
exist in `src/`** (checked this pass). This is the single largest ruled-unbuilt gap.

### Mechanics / C#

`RM_PoisonForestBiome.cs` — worldgen worker + ranges extension only.
`RM_PoisonForestMod.cs` — Mod Settings, one rarity slider; its own header states it
plainly: *"No mechanics kit exists for this biome yet."*
Creature-level mechanics that DO exist: the Suush's `CompProperties_Explosive`
(startWickOnDamageTaken Bullet/Bomb, ToxGas post-explosion, explodeOnKilled) + core-1.6
flight fields; the VentStalker's dormant-ambush pair (CanBeDormant/WakeUpDormant).
Utinni side: the toxic-prized-meat chain IS built — `PoisonForest_ToxicPrizedMeat.xml`
points Neebray/RSW_Screecher/Visceral/AA_Helixien at 4 hand-authored `RUT_*Meat` defs
(`RUT_PoisonForestPrizedMeats.xml`).

### Art status per cast member

From `artpipe/registry.jsonl` + `done/` + `_artsrc/` (checked before any re-queue,
per the standing rule):

| subject | status |
|---|---|
| Suush (3 facings, `cauldron_suush_*`) | **DONE + validated + deployed** into the mod |
| RM_TwistingThornwood (`twistingthornwood_v1`) | done/validated; mod ships `_a`+`_b` PNGs |
| RM_TreeMartyr (`martyr_v1`) | done/validated; mod ships `_a`+`_b` |
| RM_DarkCrust (`rutdarkcrust_v1` in `_artsrc/`+`done/`) | done; deployed as `RM_DarkCrust_a` |
| AB_* flora ×7 (`crystalflower_v1`, `bloodbouquet_v1`, `ravennettle_v1`, `redbugloss_v1`, `keeningcordax_v1`, `giantagaritox_v1`, `gianttoxicflower_v1`) | **all generated+validated** — replacement art already exists for every donor flora row, unwired |
| RSW_VentStalker | rides Kinrath's generated art (`kinrath_v1`/`canon_kinrath_v1` confirmed real) — retint, deliberate |
| RSW_Screecher / Neebray / Mynock / GraniteSlug / Skalder | own art in SWBestiary / `desert_swaca_*` jobs done |
| Donor fauna (AA_/AM_/GR_/Visceral) | donor mods' own art; none of ours queued |

⛔ Nothing in this table may be re-queued at movement 4. The validated AB_-replacement
flora set is the interesting find: **the divergence art for the donor flora already
exists** and is sitting unused — wiring it to owned defs is a build ticket, not an art ask.

## Nine-mark scorecard

| # | Mark | Verdict | Evidence |
|---|---|---|---|
| 1 | Unique mechanic | **PARTIAL** | Creature-level only: the Suush's shot-triggered ToxGas detonation (`RM_PoisonForestFauna.xml`, CompProperties_Explosive w/ startWickOnDamageTaken) and the VentStalker's dormant ground-sense ambush are genuinely this biome's voice — but there is no biome-SCALE mechanic. `RM_PoisonForestMod.cs` says it itself: "No mechanics kit exists for this biome yet." The vents — the anomaly the whole sheet is built on — do nothing in game. |
| 2 | Discoverable technology | **MISS** | Nothing teaches the player anything they keep. The ready-made seam is sheet §8: capped wellheads, gas-tap scaffolds, condenser stacks, spent filter cartridges — a whole extraction industry described as set dressing with no defs and no discovery ladder. Slate candidates C/D. |
| 3 | Unique resources | **PARTIAL** | Toxic prized meat IS built (4 `RUT_*Meat` defs + `PoisonForest_ToxicPrizedMeat.xml`, Utinni tier). But §7's headline — **bio-accumulated metal, "old trunks assay richer than the rock", the biome's whole reason to exist for a scavenger clan** — is unbuilt: both owned trees yield plain WoodLog. Vent gas as a stock also unbuilt. Slate candidate B. |
| 4 | Surprising creatures | **HAVE** | The Suush (drifting translucent gasbag, docile, tamable, and a ToxGas bomb the moment anyone shoots it — built, own validated art) and the VentStalker (eyeless, reads the ground's hum through splayed feet — built) are both real "what" moments, both OURS, both shipped. |
| 5 | GIANT beast | **PARTIAL** | Giant-band residents exist but are donors at trace commonality: `AA_Helixien` (0.1, spd 0.6 gas-form) and `AA_Wildpod` (0.05). No owned colossus in the biome's own voice, nothing that makes the kill/harvest a strategic decision. Slate candidate F (the vexxiss). |
| 6 | Gravship touch | **MISS** | Nothing anywhere — no ruling, no def, no doc — gives the Cauldron a voice against the ship. (The biome's chemistry begs for one: everything here corrodes, plates and crystallizes what stays still. Slate candidate E.) |
| 7 | Soundscape | **MISS** | The sheet's acoustic identity is unusually strong AND unusually specific — "quiet in a way that is wrong" + the substrate hum (§1, §4) — and none of it exists: no SoundDefs, no ambients, no folder. The silence is a designable feature, not just missing audio. Slate candidate G. |
| 8 | Interesting weather | **PARTIAL (ruled + ratified, zero built)** | All four weathers RULED by owner card 2026-09-12 with names and behaviors ratified as written (scatter-dusk · vent bloom · vapour bank · dewfall, sheet §4b) and def work explicitly unblocked. Shipped block is still donor `Fog 90 / DryThunderstorm 1`. Sixteen days ruled-unbuilt. Ticket-ready more than volley material — but vent bloom is also the spine of slate candidate A. |
| 9 | Relationship to the gods | **MISS (one seed)** | No ruling, no content. The one recorded seed: §7's closing line — the wettest-looking biome on the planet cannot give you a drink, "in direct tension with Oomo, whose whole domain is the unspilled." Precedent to honor: at the Blue Desert volley the owner ruled mark 9 BIOME-LOCAL LORE, no campaign ideoligion defs — expect the same shape here. Slate candidate H. |

**Score: 1 HAVE, 4 PARTIAL, 4 MISS (2, 6, 7, 9).** The biome's paper identity (frozen
sheet) is one of the strongest on the planet; almost none of it is load-bearing in game
yet. The volley should aim at 2/6/7/9 and at converting the three ruled-unbuilt partials
(3, 5, 8) into tickets.

## Roster gaps

Q11a binds: the `RM_` tier must be rich enough to stand alone, looking the same as the
campaign tier minus canon. Today the RM mod standing alone (no donors installed) fields
**1 animal and 3 plants** — the deepest Q11a hole of any bedazzled-to-date biome, because
13 of 14 inline fauna rows are MayRequire'd donors and 7 of 10 flora rows are
no-MayRequire Alpha Biomes rows (disclosed in About.xml as out of the build's scope).

Structural role holes (independent of donor presence):

- **No owned colossus** (mark 5) — the giant band is two trace donors.
- **No owned mineral-rasper** — the sheet's only legal herbivory ("rasping crust off
  stone") is carried entirely by canon `RSW_GraniteSlug` on the Utinni layer; the RM tier
  has no herbivore at all.
- **No voice** — nothing that expresses the hum/silence acoustically (mark 7).
- **No owned filter-frond plant** — the sheet §1's defining flora silhouette ("a crown of
  fine chemical fronds held out like filters, stirring constantly") has no def; the two
  owned trees are ports whose descriptions still say "polluted arid environments"
  (RM_TwistingThornwood's description is donor text, pre-divergence).
- The **validated replacement art for all 7 AB_ flora already exists** (see art table) —
  the natural movement-4 ticket is "diverge the donor flora into owned defs wearing the
  already-validated art," which also retires most of the Q11a flora hole for free.

### Proposed fills (movement 2 pitches — owner admits or strikes at the sitting)

All NEW inventions, one home (the Cauldron), named in the biome's own ruled accent
(Batch 4a: *glass and acid — thin front vowels, ts/sk/x/ss clusters, -ix/-iss/-eth
endings*). Collision-swept this pass with `git grep -i` across `src/`, `design/`,
`infrastructure/state/` — sweep sanity-probed on `korrum` (**63 files** — instrument
proven able to see); every name below returned **0 hits**. `tsekket` was considered and
dropped (near-collides with Batch 4a's alternate *tsekkit*).

| name | defName | kind | role |
|---|---|---|---|
| **vexxiss** | `RM_Vexxiss` | creature (GIANT) | The colossus (mark 5). A slag-plated hill that walks — the oldest living thing in the forest, so long at the vents that it is more smelter-tailings than flesh: crystal fans down the spine, bark-scab armor, a face with no eyes at all. Rare, slow (the sheet's "nothing fast" law scales up), neutral. It IS the bio-accumulated-metal thesis in a body: it assays richer than the rock, and the kill-vs-shear decision is candidate F. |
| **zisska** | `RM_Zisska` | creature | The owned mineral-rasper (RM-tier legal herbivore). A plated, low, tortoise-broad crust-grazer scraping mineral rings off stone and old trunks — the RM twin of the GraniteSlug's job so the standalone tier has an ecology, not a re-home of anyone's species. Butchers into toxic prized meat + a trace of the metal it concentrated. |
| **eskith** | `RM_Eskith` | creature | The voice (mark 7 in fauna form). A knee-high, feather-footed drummer that talks by striking the ground — heard as knocks through the substrate, not through air. Whole clades fall silent the moment a vent bloom is coming: a living gas alarm (couples to slate A/G). Eye-banks per the sheet's "many eyes" lane. |
| **xithess** | `RM_Xithess` | flora | The filter-frond plant (the sheet's missing signature silhouette). A pale trunk-form holding a crown of constantly-stirring chemical fronds; harvest yields vent-chemistry stock rather than wood. The flora row that makes the owned understory read as chemosynthetic instead of merely dark. |

Also swept clean and held in reserve if the owner wants more: *thessix, skethiss,
skissath, vissketh, issveth, tsivvix-class variants* — but four pitches is the shape the
Blue Desert sitting proved out.

**Not proposed:** re-homing anything. The 7 unwired roster imports (Lylek, Plasmorph,
LuciferBug, Radyak, RipperHound, Skalder, Silooth) are the owner's rows to wire or strike
at the sitting — two of them contradict the frozen sheet's own bans (see What's-there),
which is exactly a review-sheet call, not a rule to apply.

## Rename census (PoisonForest → Cauldron)

For the rename ticket (`CAULDRON_FULL_RENAME_1`-shape, precedent `CRACKEDLANDS_FULL_RENAME_1`).
**Nothing renamed this pass.** Counts MEASURED via `git grep` 2026-09-28, `Transient/` excluded.
The BiomeDef label already reads "the Cauldron"; everything below still says PoisonForest.

| target | count | notes |
|---|---|---|
| `RM_PoisonForest` defName | **117 occurrences / 41 files** (17 src/RimMandrake, 3 src/RimUtinni incl. the WildAnimals patch xpath, 13 infrastructure/state, 5 design/Jawa, 2 design/RimMandrake, 1 dashboards) | the def itself + both Utinni patch xpaths + docs. 🔴 live-tile/savegame check gates the defName change (`BIOME_DEFNAME_DELETION` precedent — grep of `.rws` lies, tileBiome is shortHash-encoded) |
| `RUT_PoisonForest` defName | **702 occurrences / 52 files** | the FROZEN campaign twin — held by the live savegame. The rename ticket must rule whether the RUT_ def renames at all (frozen twin + live world) or only the RM_ tier renames now and the twin follows at world-remake (world-remake-is-the-last-step doctrine says the twin may simply die with the old world) |
| packageId `mandrake.rm.poisonforest` | 16 / 10 files | About.xml, compose manifest (`src/RimMandrake/Biomes.compose.json`), items, ModsConfig snapshots |
| C# namespace + assembly `RimMandrake.PoisonForest` | 7 / 5 files | namespace in 2 .cs, csproj AssemblyName/RootNamespace, DLL + `.srchash` (rebuild required — DLL_SOURCE_STAMP_GUARD_1: DLL and sidecar push together) |
| C# type names `RM_PoisonForest{Settings,Mod,BiomeRanges}` / `RM_BiomeWorker_PoisonForest` | in the 2 .cs + workerClass field in BiomeDef | workerClass string in XML must move in the same commit as the C# or the def dies silently |
| mod folder `src/RimMandrake/PoisonForest/` | 10 files reference the biome by name inside | folder rename + deploy-tool collision check (deploy tool needs unique mod names) |
| terrain defNames `RM_PoisonSoil`/`RM_PoisonSoilRich` | 18 / 6 files | owner call: are the soils "cauldron soil" or does "poison soil" survive as a common noun? |
| worldmap texture path `Biomes/PoisonForest` | 110 / 7 files | donor BiomesPlus texture reference — repaint/worldmap face is `WORLDMAP_BIOME_APPEARANCE_1` territory anyway |
| roster + sheet filenames `poison_forest.{json,md}` and `poison_forest` string | 409 / 106 files | bulk is docs/rosters/handoffs; the two canonical files should rename with a successor pointer; frozen-sheet freeze header carries over |
| Utinni patch files `WildAnimals_PoisonForest.xml`, `PoisonForest_ToxicPrizedMeat.xml`, `RUT_PoisonForestPrizedMeats.xml` | (inside the 30 UtinniPatches refs) | file renames + their internal xpaths track whichever defName ruling lands |
| mod display name "RimMandrake: Poison Forest" | About.xml | becomes "RimMandrake: The Cauldron" (packaging note: merges into `RimMandrake.Biomes` per BIOME_MOD_UNIFICATION_1 regardless) |
| ⛔ NOT rename targets | `world/**` (118 files) — exports/records of the planet (frozen CSV doctrine: records, never edited back); `observed/`, `research/`, closed items, handoffs — history stays history |

## Candidate mechanics slate

Ranked pitches for the four-turn volley, aimed at the MISSes (2, 6, 7, 9) and at
converting the ruled-unbuilt partials (3, 5, 8). All DLCs assumed present. Each is meant
to be unlike the others and unlike any shipped biome mechanic (Blue Desert = detonation
chain; Flooded Canyon = FlowWorks water; Pyrelands = fire; Miasma = vermin pressure —
nothing below reuses those spines).

**A. The Breathing Ground — vent bloom as a living system** *(marks 1 + 8; rank 1)*
Build the four ruled weathers, then make vent bloom more than a weather: during a bloom
the ground itself doses — a stacking "metal load" hediff accrues on anyone outdoors and
unroofed (sealed apparel and buildings negate), and every native creature reads it coming:
the map's fauna flattens and goes silent ~a day ahead. The tell IS the mechanic — the
player learns to read the forest like the animals do. *Engine:* WeatherDefs (ruled names)
+ exposure via `EnvironmentalWeatherExtension`-style hediff (the Blue Desert Haze shape,
already RimSage-proven, near-zero C#) + one MapComponent for the fauna hush. *Trade-off:*
the hush needs a light touch or it reads as AI breakage; the hediff must not double-tax
alongside vanilla toxic buildup.

**B. Assay the Trees — bio-accumulated metal** *(mark 3; rank 2)*
§7 built: old-growth flora carry the metal they plated themselves in. Chopping a
full-grown thornwood/martyr yields wood PLUS a growth-scaled trace of metal ore;
the richest lodes are the oldest trunks — visible as scab/crystal density (art already
distinguishes `_a`/`_b` variants). Mining the forest means deforesting it, on a
15-day-regrow biome: the extraction-vs-ecology loop is the mechanic. *Engine:* a small
harvest comp or `PlantProperties` second-yield patch — the greatbole heartwood precedent
covers mineable-plant hybrids. *Trade-off:* economy balance (free steel faucet if the
yield curve is lazy); interacts with tree-connection ideoligions deliciously or
disastrously.

**C. The Filter Economy — spent cartridges and sealed work** *(marks 2 + 3; rank 3)*
The discoverable technology: studying the corroded ruin kit (§8 — capped wellheads,
condenser stacks, the characteristic spent filter cartridge) teaches **filter-craft**: a
buildable condenser that pulls potable water out of a biome whose one impossibility is a
drink, and consumable filter cartridges that let colonists work a vent bloom unharmed.
The biome teaches you the thing IT is about: separation. *Engine:* Anomaly study-interactable
shape or Royalty techprint unlock on injected ruin pieces; condenser is a plain building
def with a power draw. *Trade-off:* needs the ruin injections authored (KCSG-style set
pieces) — a real content bill beyond the defs.

**D. Gas-Tap Scaffolds — vent gas as a resource node** *(marks 3 + 2; rank 4)*
Map-spawned vent cells (the anomaly made visible at last) can be capped with a gas-tap
scaffold: slow trickle of vent-gas stock — chemistry input for toxin weapons, preservation
(the sheet names both), and chemfuel refining. Uncapped vents are the bloom's local
epicenters, so capping them partially tames your map — industry as terraforming-lite.
*Engine:* a `ThingDef` special-spawn at mapgen (MapGenerator step or GenStep patch) + a
producing building gated on adjacency; same shape as Helixien gas vents (Odyssey/VE
precedent exists in-engine). *Trade-off:* overlaps candidate A's bloom logic — sequence
them as one system or they double-author the vents.

**E. The Ship Grows Scabs — corrosion tithe** *(mark 6; rank 5)*
The Cauldron's voice against the gravship: while landed, exterior hull and any building
outside a roof slowly grow crystal scab — a cosmetic overlay that, left unscrubbed, starts
costing beauty then deterioration; scrubbing it off yields trace metal. The ship becomes
the biome's newest tree: it is being plated too, and the biome pays you a little for the
insult. Departure with heavy scab has a visible cost (launch delay or minor hull damage).
*Engine:* MapComponent tick over things tagged exterior + a scrub job + a stackable
"scabbed" comp; no engine surgery. *Trade-off:* per-thing overlays need cheap rendering;
tuning so it reads as flavor-with-teeth, not chore tax.

**F. The Vexxiss Decision — the walking lode** *(marks 5 + 4; rank 6)*
The colossus as an economy: rare, neutral, and worth more alive. Shearing scab plates off
a living vexxiss (a work-giver operation, dorrak-hump lineage) is the richest metal
harvest on the planet and enrages it for days; killing one voids the lode (the metal is
IN the living metabolism — a corpse's plates crumble) and vents its gut-load as a map-scale
ToxGas event. Exactly inverts the usual kill-the-giant loop. *Engine:* big animal +
operation recipe on a body part + death event comp — all existing patterns (Suush
explosion, hump-shot trigger). *Trade-off:* "worth more alive" needs the shear yield to
genuinely beat the kill, or players will just bomb it.

**G. The Wrong Silence — soundscape as instrument** *(mark 7; rank 7)*
The quietest biome on the planet, scored: a near-subsonic hum sustainer as the ambient
floor, eskith knock-clusters as the mid-layer, and THE mechanic — total silence as the
alarm. When the hum layer drops out (vent bloom incoming, candidate A's hush made
audible), a listening player gets the warning before any letter fires. Optionally a
research-gated "seismograph" building translates the silence into a real alert for
players who play muted. *Engine:* SoundDef ambients keyed to weather + the A-system's
state; the seismograph is a plain building + alert. *Trade-off:* audio assets are a new
pipeline ask; the muted-player fallback is what keeps it a mechanic rather than vibes.

**H. Oomo's Refusal — the gods layer, biome-local** *(mark 9; rank 8)*
Per the Blue Desert precedent (mark 9 ruled BIOME-LOCAL LORE, no campaign ideoligion
defs): the Cauldron as the place Oomo will not go — the planet's wettest-looking land
where no drop can be kept. Carried in content, not precepts: the ruin kit's hauled-in
water tanks read as offerings that failed; a rare "unspilled cache" find (a sealed
pre-collapse water tank, the biome's one drinkable prize, guarded by the forest's worst);
condenser-building flavor text that frames filter-craft as doing by hand what the god
refuses to do here. *Engine:* pure content — ruin pieces, one incident/site def, strings.
*Trade-off:* genuinely his call whether Oomo tension is Cauldron canon or stays a sheet
aside; zero mechanics if he strikes it.

---

*Movement 1–2 complete on paper: the census is measured, the scorecard names its
evidence, the four fills are collision-proven pitches, the rename census is
ticket-ready, and the slate above is the movement-3 opening hand. Nothing here re-opens
a frozen ruling; no rename executed; no items filed; tile counts nowhere cited as
evidence (paint is terminal).*
