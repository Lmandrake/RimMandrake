You are a senior game designer consulting on a RimWorld mod campaign. The owner wants recommendations to ENRICH one biome that has already been through a design sitting. Be concrete, vivid and buildable in RimWorld 1.6 (XML defs, C# comps, Harmony, incidents, map components, weather, sounds).

BIOME: The Cauldron (formerly Poison Forest)

Standing rules of this project (binding on every recommendation):
- RimWorld 1.6 with ALL five DLCs assumed present; a Star Wars (old Tatooine / Jawa scavenger clan) campaign on one hand-made fixed planet. No worldgen, no alternative planets.
- Each animal lives in ONE biome unless there is an in-game reason (migration, life stage).
- Invented exotic names are fine; genuine Star Wars canon goes in a separate Star Wars layer.
- Heat is ONE planet-wide kind riding vanilla heatstroke; biomes differ by heat kind (overhead sun, low sun, ambient steam/volcanic).
- Animals or pawns must never vanish without a readable sign of what happened.
- If it flies in the fiction, it flies in the game.
- Every mod ships real Mod Settings.
- A biome's ideas must NOT echo another biome's signature; each biome has its own voice.
- The "bedazzle" bar is nine marks: unique mechanic, discoverable technology, unique resources, surprising creatures, a GIANT beast, a gravship touch, an interesting soundscape, interesting weather, a relationship to the gods.

WHAT THE OWNER HAS ALREADY RULED for this biome (ledger, verbatim; do NOT contradict or re-propose anything cut here):
- 2026-09-29: VOLLEY TURN 2, owner typed this session (guard could not see the turn; recording under BENCH). Ruling 1, soundscape - reverses the wrong-silence identity, ground is LOUD: "The ground should rush and groan and sigh and rumble and gurgle from all the strange chemistry flowing around. Hisses and dull slow roars. Like a slow steam engine."
- 2026-09-29: Ruling 2, slate B accepted with slow-harvest lever, owner verbatim: "The metallic infused trees should be slow to harvest." Ruling 3, slate C, owner verbatim: "So the discoverable tech is about conversion of one fluid to another via filtering."
- 2026-09-29: Ruling 4, vent gas, owner verbatim: "The gas is highly flammable with toxic smoke and should be stopped. It can also be refined for valuable liquid reagents."
- 2026-09-29: Ruling 5, vexxiss redesigned - no death explosion; owner verbatim: "Too many exploding giant beasts. This one should just be a solid giant that can inhale a vent deeply and temporarily pause its production. Also attacks if you ignite  them and puts them out. Transforms bodies of water touched into toxic waters."
- 2026-09-29: Ruling 6, mark 9, owner verbatim: "Oomo will dislike it but not refuse to go." Softens slate H from refusal to dislike.
- 2026-09-29: Ruling 7, soils, owner verbatim: "Poison ground gets renamed to this biome." RM_PoisonSoil/Rich become cauldron naming. Ruling 8, rename scope, owner verbatim: "Rename all to the cauldron all the way down to the defs." Full rename including defNames; live-tile shortHash check still gates the defName step; BENCH reads scope as including the frozen RUT_ twin, flagged for owner confirmation at turn 4.
- 2026-09-29: TURN 4 ruling A, owner typed this session: "Wire and keep." All 7 unwired imports (Lylek, Plasmorph, LuciferBug, Radyak, RipperHound, Skalder, Silooth) wire into the biome and stay - overrides the frozen sheet bans on the two contradicting rows; sheet amendment records the override.
- 2026-09-29: TURN 4 ruling B, owner verbatim: "Shear harvest turned instead to rare material immune to powerful acids and temperature." Vexxiss shearing kept; yield is a NEW unique rare material (acid-immune, temperature-immune), not metal. Volley complete - two full exchanges; ticket-out proceeds.
- 2026-09-29: Movement 4 commission DONE (692109fb3, bible 76f79e4b0): cast bible cauldron_bedazzle_cast_2026-09-28.md + 19 art jobs queued for 13 subjects (vexxiss/zisska/eskith 3 facings each; xithess, vexxith, gas-tap, filter-works, cartridge, seismograph, vent, 3 ruin pieces); 12 subjects skipped, validated art already in done/. Sitting now open for ART REVIEW only - all four movements complete.
- 2026-09-29: Art review DONE by owner (export: Transient/bedazzle_art_sheets_2026-09-28/cauldron/sheet.decisions.json): 10 keep, 2 improve (Eskith five eyes so side profile shows three; Vexxiss outside as colorful as the Cauldron Vents), 1 regen (Seismograph "weird, replace"). Owner typed: "Needs more color in palette and more plants."

THE BIOME'S DESIGN DOCS:
===== design/Jawa/worldbuilding/biomes/cauldron_bedazzle_review_2026-09-28.md =====
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

---

## Ruled at the sitting — 2026-09-28 volley outcomes

The four-turn volley closed same-day. Every ruling below is owner-typed, quoted
verbatim in `CAULDRON_BEDAZZLE_SITTING_1`'s ledger notes; tickets:
`CAULDRON_RULED_CONTENT_1` · `CAULDRON_MECHANICS_BUILD_1` · `CAULDRON_FULL_RENAME_1`.

1. **Soundscape REVERSED** — the ground is LOUD ("like a slow steam engine": rushes,
   groans, sighs, rumbles, gurgles, hisses, dull slow roars). The frozen sheet's
   "quiet in a way that is wrong" identity is overturned as baseline; the wrong
   silence survives inverted as the vent-bloom alarm (the engine falters).
2. **Slate B accepted** with the slow-harvest lever: metal-infused trees are slow
   to fell, yield growth-scaled metal.
3. **Slate C ruled**: the discoverable tech is conversion of one fluid to another
   via filtering (LiquidDef/FlowWorks lane).
4. **Vent gas ruled**: highly flammable, burns with toxic smoke, should be stopped
   (capping pressure); refines to valuable liquid reagents (C+D merged).
5. **Vexxiss redesigned**: solid giant, NO explosion ("too many exploding giant
   beasts"); inhales a vent to pause its production; attacks igniters and puts
   fires out; poisons water bodies on touch. Turn 4: shear harvest KEPT but yields
   a **rare material immune to powerful acids and temperature** (working name
   vexxith, collision sweep owed), not metal.
6. **Mark 9**: Oomo dislikes the Cauldron but does not refuse to go — slate H
   softened from refusal to grimace.
7. **The 7 unwired imports**: "Wire and keep." — all seven wire in; overrides the
   frozen sheet's bans on the two contradicting rows.
8. **Renames**: poison ground renames with the biome; full rename "all the way
   down to the defs" (BENCH reading: including the frozen RUT_ twin, stated at
   turn 3, not corrected at turn 4). Live-tile shortHash check gates.
9. **Fills admitted by ticket**: zisska, eskith, xithess stand as pitched.
10. **Not ruled either way**: slate E (gravship scab) — neither adopted nor struck;
    remains sitting-row material for a future pass. Mark 6 stays the one open MISS.


===== design/Jawa/worldbuilding/biomes/cauldron_bedazzle_cast_2026-09-28.md =====
<!-- status: cast bible — commissioned under CAULDRON_BEDAZZLE_SITTING_1 movement 4 -->
# The Cauldron — bedazzle cast bible (movement 4: commission)

**Item:** `CAULDRON_BEDAZZLE_SITTING_1` · **Program:** BAROQUE_BEDAZZLE_PROGRAM_1 (row 5)
**Date:** 2026-09-28 · **Author:** movement-4 commission agent (Fable)
**Feeds:** `CAULDRON_RULED_CONTENT_1` (defs) + `CAULDRON_MECHANICS_BUILD_1` (mechanics)
**Authorities:** `cauldron_bedazzle_review_2026-09-28.md` §Ruled-at-the-sitting (every
ruling below is fixed, owner-typed on the sitting item) · the review's art table and
proposed fills · rename is `CAULDRON_FULL_RENAME_1`'s scope — the mod is
`src/RimMandrake/PoisonForest/` today and **current defNames ship**; this document's
`RM_` names are the NEW defs' names (born post-ruling, so born Cauldron-voiced).

## 0. Shared law — every card obeys this without restating it

- **The ground is LOUD.** Owner ruling 1 REVERSED the frozen sheet's "quiet in a way
  that is wrong": the baseline is a slow steam engine underfoot — rushes, groans,
  sighs, rumbles, gurgles, hisses, dull slow roars. Silence survives only inverted, as
  the vent-bloom alarm (the engine falters). ⛔ No card, description or prompt below
  echoes the dead "silent biome" identity.
- **Name accent** (Batch 4a, ruled): glass and acid — thin front vowels, ts/sk/x/ss
  clusters, -ix/-iss/-eth endings. Invented exotic words, `RM_` tier (Q11a: "Star Wars
  style" naming is not Star Wars IP).
- **Art register (the Cauldron house style for every job below):** a poison forest of
  glass and acid under chemical fog — wet-lacquered darks (black-green, char-brown),
  the dark-crust film's black/purple/red sheen, pale crystal-fan accents, and the
  chemistry's sick green-amber ONLY where something pools, beads or stains; every
  surface carries condensate beading or mineral rings, because every wet surface is a
  dosed surface. Corrosion patina (acid-etch, verdigris, eaten metal) on anything
  industrial. Realistic painted natural-history illustration, grounded believable
  anatomy, matte natural surface texture with wet sheen, never cartoonish, never cute,
  no outlines, alien but biologically plausible. Faced jobs: north is a **true rear
  view from directly behind — no eyes, no face, no frontal features**.
- **One home.** All four natives are Cauldron-only; no multi-homing (owner law
  2026-09-21).
- **Numbers are design proposals** — FOUNDRY calibrates in the build tickets; the
  *relationships* (who is biggest, who is prey, what the shear is worth) are the ruled
  part.

## 1. Name sweep (MEASURED this pass, 2026-09-28)

Instrument: `git grep -il <name> -- src/ design/ infrastructure/state/`.
**Sanity probe: `korrum` → 65 files** (instrument proven able to see; the review's
own probe read 63 two commits earlier — same instrument, tree moved).

| name | files | verdict |
|---|---|---|
| `vexxith` | 4 | CLEAR — all 4 are this sitting's own commissioning prose (review doc, `CAULDRON_RULED_CONTENT_1`, BENCH ledger line, queue render). No def, no other subject. The owner's "collision sweep owed" is hereby paid: **`RM_Vexxith` stands.** |
| `GasTapScaffold` | 0 | CLEAR |
| `FilterWorks` | 0 | CLEAR |
| `FilterCartridge` | 0 | CLEAR |
| `Seismograph` | 2 | CLEAR — both hits are the review doc + mechanics ticket describing this very commission |
| `CauldronVent` | 0 | CLEAR |
| `CorrodedWellhead` | 0 | CLEAR |
| `CondenserStack` | 0 | CLEAR |
| `CorrodedShrine` | 0 | CLEAR |

(vexxiss / zisska / eskith / xithess were collision-swept clean at the review pass,
probe korrum 63; not re-litigated here.)

## 2. Art dedup (standing owner law — searched before queuing anything)

Instrument: filename search over `infrastructure/artpipe/` `done/` (3,873 files),
`pending/` (1), `active/` (1), `failed/` (62), `_artsrc/` (1,780) + content search of
`registry.jsonl` + all 16 `Transient/*.decisions.json`. **Sanity probes: suush → 6
files in done/, 24 registry hits; krissek → 10 files in done/** (the instrument sees).

**Empty everywhere — genuinely owed, queued below:** vexxiss, zisska, eskith,
xithess, vexxith, gas-tap scaffold, filter-works, filter cartridge, seismograph,
corroded ruin pieces (wellhead / condenser stack / shrine), and the Cauldron vent
(the only `vent` art anywhere is `scald2_ventbuilding_a/_b` — the **Scald sea's**
steam-vent building in that biome's register; not reusable here, different biome's
voice and chemistry).

**Found and NOT re-queued** — see §5 wired-by-FOUNDRY.

## 3. Cast entries — the four new natives

### RM_Vexxiss — the solid giant (mark 5)

**Ruled frame (fixed):** solid, **NO explosion anywhere on it** — alive, dying or
dead ("too many exploding giant beasts"). Inhales a vent deeply and that vent's
production pauses for days; pries at gas-tap scaffolds to drink. **Fire warden:**
ignition anywhere near it and it attacks the igniter and smothers the flames out.
Poisons water bodies on touch. Shearing plates off a LIVING vexxiss yields
`RM_Vexxith`; a kill wastes the lode.

**Description (in the biome's voice):**

> The ground here talks all day — rush and groan and gurgle, the slow engine of the
> forest's chemistry — and the vexxiss is the one thing that walks like it belongs in
> the machine. A hill of slag that moves: plates of smelter-scab and old bark grown
> together, crystal fans standing down the spine like vents on a boiler, no eyes
> anywhere on it because it has never needed to see anything. It drinks the ground's
> breath straight from the wellheads, it hates fire the way a lung hates smoke, and
> the crews that shear its plates say the trick is not the climbing. The trick is
> doing it without warming the shears.

**Silhouette/palette brief:** a walking hill — the read from distance is terrain.
Massive low-slung body on pillar limbs, armor of layered slag plates and bark-scab,
crystal spine-fans in a graded row down the back, a blunt eyeless prow of a head that
is more intake than face. Slag greys and char-browns, dark-crust purple-red film in
the plate seams, pale glass-crystal fans as the accent, condensate beading on the
lower plates. 🔴 **HARD BAN: nothing explosive-looking** — no glow-from-within, no
gas-bag translucence, no warning colours, no wick, no distended volatile-looking
volumes. It reads as stone and patience, never as ordnance. And NO eyes.

**Facings:** south, east, north (north = true rear: plated back, spine-fans from
behind, rear pillar limbs). **Canvas 512** — colossus precedent (Vhaulk/Muttavaq):
scale must carry in the pixels. **drawSize intent: ~7.0** (adult), bodySize ~6.0
class — the biggest thing in the forest; slow (the sheet's "nothing fast" law scales
up), rare (0.02-class commonality), neutral until fire or shears give it a reason.

**Def wiring pointers (build: `CAULDRON_RULED_CONTENT_1` §2; behaviors:
`CAULDRON_MECHANICS_BUILD_1` §5):** shear = work-giver operation on a plate body
part (dorrak-hump / vexxiss-plate lineage); no charge hediff of any kind.

### RM_Zisska — the plated crust-grazer

**Ruled frame (fixed):** the RM tier's own herbivore — mineral-rasper, the biome's
one legal herbivory (rasping crust off stone; there is nothing to graze). Butchers
to toxic prized meat + a trace of the metal it concentrated.

**Description:**

> Low and broad as a dropped shield, plated like the stones it eats. The zisska
> spends its life nose-down against rock and old trunks, rasping off the mineral
> rings the forest paints on everything that stands still — and everything it rasps
> stays in it. The Farmers of other countries would call it livestock. Here the
> butchers wear gloves to the elbow, and the meat is worth the gloves.

**Silhouette/palette brief:** tortoise-broad, low-slung, a dome of overlapping
plates with mineral-ring staining ground into them; a wide rasping under-slung mouth
barely visible below the shell rim; short digging limbs. Wet-lacquered dark plates,
purple-red crust film in the plate margins, pale mineral-ring stripes as the accent
— it wears the biome's paint because it eats the biome's paint. Small deep-set eye
band, nothing prominent.

**Facings:** south, east, north (north = plate dome and rear rim only). Canvas 256.
**drawSize intent: ~1.6**, bodySize ~1.0 class; slow, herd-adjacent, high wildness
but tamable at a price (a grazer that feeds on stone is a fence-proof pasture
animal — FOUNDRY prices it).

### RM_Eskith — the feather-footed ground-drummer

**Ruled frame (fixed):** the voice's fauna half. Talks by striking the ground —
heard as knocks through the substrate, through the engine's noise, not through air.
Goes silent ahead of a vent bloom: a living gas alarm, coupled to the falter tell
(`CAULDRON_MECHANICS_BUILD_1` §1).

**Description:**

> Knee-high, quick-footed, feet feathered out into wide soft pads that read the
> ground the way ears read air. Eskith talk in knocks — a drummed code sent through
> the rock, felt in your boot soles under the engine's rumble. The forest is never
> quiet, so nobody listens for sound here; they listen for the drumming. When the
> eskith stop answering each other, the old hands are already walking for the roof.

**Silhouette/palette brief:** a small upright ground-bird-adjacent body (no
Earth-nameable bird) on two strong drumming legs, the feet the signature — wide,
feather-fringed splayed pads, oversized for the body; a banked row of small eyes
(the biome's "many eyes" lane) across a blunt head; drab wet-forest darks with
crust-film iridescence at the feather-fringe, pale condensate beading on the
leg-feathering. The read is alert, harmless, tuned to the floor.

**Facings:** south, east, north (north = rear: back, folded fringe, drumming
haunches; the eye-bank invisible). Canvas 256. **drawSize intent: ~0.9**, bodySize
~0.35 class; common enough that the drumming is the biome's texture (0.4-class),
prey band, no manhunter.

### RM_Xithess — the filter-frond flora

**Ruled frame (fixed):** the sheet's missing signature silhouette, admitted as
pitched: a crown of fine chemical fronds held out like filters, **stirring
constantly**; harvest yields vent-chemistry stock, not wood.

**Description:**

> A pale trunk the height of a person, crowned with a fan of fine fronds that never
> stop moving — not in wind, in CHEMISTRY, combing the fog for what the vents
> exhale. Watch a xithess for a minute and you understand the whole forest: nothing
> here drinks water. It filters. Harvesters take the frond-crowns whole and sell
> them as they are — a xithess crown is a fistful of the forest's own refinery.

**Silhouette/palette brief:** single pale smooth trunk (bone-white going grey-green,
mineral-ringed at the base), no branches, all crown: a radial fan of many fine
graduated filter-fronds, caught mid-stir — visibly asymmetric, some fronds furled
and some spread, so the stillness of a sprite still reads as motion. Frond tips
carry the chemistry's green-amber bead-tips (the pooled-accent rule); condensate
strings between fronds. Transparent-edged fronds against the fog, never an opaque
mop.

**Facings:** single (plant; Graphic_Random variants derive from the master).
Canvas 256. **drawSize/visualSize intent: ~1.0–1.3 cells**; mid-tier field-former,
wild-clustered near vent ground.

## 4. Cast entries — material, industry and kit

### RM_Vexxith — the shear material (item + stuff)

**Ruled frame (fixed, owner-typed):** shearing a living vexxiss yields a **rare
material immune to powerful acids and temperature** — not metal. Only obtainable by
the shear; a corpse's plates crumble. Name sweep paid this pass (§1): `RM_Vexxith`
stands.

**Description:**

> A sheared vexxith plate, still holding the curve of the animal's flank. Acid beads
> off it. Fire cannot warm it. The forge-hands say working it is like arguing with
> something that has already decided — and everything made from it outlives the
> argument, the forge, and the smith.

**Silhouette/palette brief (item icon; the STUFF colour derives from it):** three or
four sheared plates stacked, curved like roof slates — layered slag-lamination
visible on the cut edge (the growth rings of a walking hill), surface a deep
matte iron-black with the purple-red crust sheen, cut edge pale and crystalline;
one plate showing acid-bead runoff standing on the surface, wetting nothing. Reads
as armor waiting to be asked.

**Facings:** single. Canvas 256. Item + StuffProps ride the def ticket
(`CAULDRON_RULED_CONTENT_1` §2); stuffable art tinting derives from this master.

### RM_GasTapScaffold — the gas-tap scaffold (building)

**Ruled frame (fixed):** the gas is highly flammable, burns with toxic smoke, and
**should be stopped**; capping a vent stops the leak AND banks flow for refining —
safety and industry as one act (`CAULDRON_MECHANICS_BUILD_1` §3). The vexxiss pries
at these to drink.

**Description:**

> A scavenger's answer to a hole in the world that breathes fire: a clamped scaffold
> of salvage steel stood over a wellhead, cap screwed down against the pressure,
> take-off line coiled to a banked tank. Every joint is doubled, because the ground
> pushes back. Every scaffold in the forest has pry-marks on it, because something
> out there prefers to drink from the tap.

**Silhouette/palette brief:** a squat 4-legged clamped frame over a capped vent
throat — Jawa salvage build language: mismatched steel, doubled clamps, a small
banked accumulator tank low on one leg, gauge with a cracked face. Corrosion patina
everywhere the fog touches; fresh bright metal only at the pry-marks. No flame, no
glow — a capped vent is a QUIET fixture; the danger reads as pressure, not fire.

**Facings:** single (building; def may rotate with Graphic_Single). Canvas 256.
**drawSize intent: ~1.5–2 cells** footprint.

### RM_FilterWorks — the filter-works (building) + RM_FilterCartridge (item)

**Ruled frame (fixed):** the discoverable tech is **conversion of one fluid to
another via filtering** (LiquidDef/FlowWorks lane): filter building + consumable
cartridges; launch recipes tapped-gas condensate → liquid reagents, toxic water →
potable water. Taught by studying the corroded ruin kit
(`CAULDRON_MECHANICS_BUILD_1` §4).

**Building description:**

> The forest's one lesson, learned from the ruins of the people who learned it
> first: everything here is something else wearing a solvent. The filter-works pulls
> them apart — one fluid in, a cartridge in the throat, a different fluid out. The
> Farmers call it doing by hand what the river god does by grace, and they say it
> quietly, because Oomo is known to grimace at this country.

**Building silhouette/palette:** a waist-high pressure vessel on a frame — intake
and outlet pipe stubs at opposite ends, a top-loading cartridge breech with one
cartridge seated half-visible, drip-tray beneath the outlet. Etched-metal patina,
mineral rings where drips dried, the green-amber accent ONLY as one bead at the
outlet. Facings: single. Canvas 256. Footprint ~2 cells.

**Cartridge (item) description:**

> A filter cartridge, packed the old way: crushed crust-mineral, frond-felt from the
> xithess crowns, a wax seal at each end. Spent ones turn the colour of what they
> caught. The ruins are full of spent ones.

**Cartridge silhouette/palette:** a hand-sized ribbed cylinder, wax-capped both
ends, pale frond-felt visible at a broken rib; one end stained the chemistry's
green-amber (a partly-spent read — provenance in one glance). Facings: single.
Canvas 256. *(Spent-cartridge ruin litter can ship as a retint of this master —
dressing, not a second commission.)*

### RM_Seismograph — the seismograph (building)

**Ruled frame (fixed):** research-gated; translates the falter tell into a real
alert for players who play muted — the engine's silence made into a letter
(`CAULDRON_MECHANICS_BUILD_1` §1).

**Description:**

> A drum, a stylus, a weighted needle sunk into bedrock — the Farmers' machine for
> listening to the machine. All day it writes the ground's talk in a fidgeting line:
> rush, groan, gurgle, roar. The one thing it is built for is the moment the line
> goes flat. A flat line here is not peace. It is the engine drawing breath.

**Silhouette/palette brief:** a knee-high instrument on a bedrock-bolted tripod — a
rotating paper drum with a scrawled trace line, a brass-dark stylus arm, a heavy
plumb mass below the frame. Scavenger-precise: this is the biome's one delicate
machine, kept oiled where everything else corrodes. The drum's white paper is the
lightest value in the whole cast — it should read across a dark room. Facings:
single. Canvas 256. Footprint 1 cell.

### RM_CauldronVent — the vent (ThingDef)

**Ruled frame (fixed):** vents are map-spawned ThingDefs that leak visible flammable
gas; ignition burns with toxic smoke; a gas-tap scaffold caps one; the vexxiss
inhales one and its production pauses for days (`CAULDRON_MECHANICS_BUILD_1` §3/§5).

**Description:**

> A throat in the ground, rimmed in mineral rings laid down one exhale at a time.
> This is where the engine's noise comes up loudest — the rush and the gurgle right
> under your feet — and where its breath comes up rawest. Unlit, it wavers the air
> and beads every surface downwind. Lit, it is a torch with poison for smoke. The
> Farmers cap them. The forest keeps making more.

**Silhouette/palette brief:** a natural surface feature (1×1 or 2×2 read): a dark
fissured throat in bare rock, concentric mineral-ring terracing (bone-white to
green-amber inner stain), condensate beading heavy on the downwind rim, faint
heat-shimmer distortion suggested at the mouth. ⛔ NO visible flame in the base
sprite — ignition is a state the mechanics own; the sprite is the UNLIT vent.
Facings: single. Canvas 256. **drawSize intent: ~1.5** over a 1-cell def.

### The corroded ruin kit — RM_CorrodedWellhead · RM_CorrodedCondenserStack · RM_CorrodedShrine

**Ruled frame (fixed):** the study-interactable ruin kit teaches the filter-works
(§4 of the mechanics ticket carries the set pieces); the shrine is Oomo's Grimace
made content — the owner ruled Oomo *"will dislike it but not refuse to go"*
(grudging shrine kit, sour flavor tint, no precept defs).

**RM_CorrodedWellhead:**

> A capped wellhead from before the collapse, the cap welded down by people who were
> not coming back for it. The mineral rings have climbed it like tree-bark. Study
> the welds and you learn the first thing the old crews knew: the ground's breath
> can be held.

Silhouette: a low industrial stub — flanged pipe collar, welded dome cap, chain-dog
clamps — half-swallowed by mineral-ring terracing; acid-etch patina, one seam
weeping the green-amber stain. Single facing, 256, ~1 cell.

**RM_CorrodedCondenserStack:**

> A condenser stack, tall as two people, its fins eaten to lace. It made water out
> of fog for somebody once — the one thing this country will not give away free.
> Study the fin spacing and the cartridge racks rotted into its base, and the
> filter-works stops being a mystery.

Silhouette: a slender vertical finned column on a square base, fins corroded
lace-thin at the top, an empty cartridge rack and two spent cartridges fused to the
base; streaked verdigris-and-rust patina, condensate still beading on the surviving
fins (it half-works, which is the poignant read). Single facing, 256, tall sprite —
**drawSize intent ~1×2.5** over a 1-cell def.

**RM_CorrodedShrine:**

> A river-god's shrine in a country with no river. The Farmers still build them here
> — smaller than they build them anywhere else, and facing away from the vents, the
> way you set a chair for a guest you know will not stay. The offering bowl is a
> filter cartridge. Nobody calls that disrespect. Oomo comes anyway, and grimaces,
> and keeps the water honest a little way around it.

Silhouette: a knee-high cairn-and-bowl shrine in the campaign's Oomo language (wave
motif carved shallow), the bowl holding a clean cartridge; the ONLY unstained clean
water bead in the whole cast sits in that bowl — the single point of grace. Stone
greys, shallow-carved motif, minimal green-amber anywhere near it. Single facing,
256, 1 cell.

## 5. Wired-by-FOUNDRY — validated art that exists; NOT re-queued (⛔ standing law)

From the review's art table, re-verified against `done/` this pass (all present):

| subject | art in `done/` | disposition |
|---|---|---|
| `AB_CrystalFlower` → owned divergence | `crystalflower_v1` | wire per `CAULDRON_RULED_CONTENT_1` §3 |
| `AB_BloodBouquet` | `bloodbouquet_v1` | wire |
| `AB_RavenNettle` | `ravennettle_v1` | wire |
| `AB_RedBugloss` | `redbugloss_v1` | wire |
| `AB_KeeningCordax` | `keeningcordax_v1` | wire |
| `AB_GiantAgariTox` | `giantagaritox_v1` | wire |
| `AB_GiantToxicFlower` | `gianttoxicflower_v1` | wire |
| `RM_Suush` | `cauldron_suush_south/east/north` | DONE + deployed; nothing owed |
| `RM_TwistingThornwood` | `twistingthornwood_v1` (+ shipped `_a`/`_b`) | nothing owed (description fix rides the def ticket) |
| `RM_TreeMartyr` | `martyr_v1` (+ shipped `_a`/`_b`) | nothing owed |
| `RM_DarkCrust` | `rutdarkcrust_v1` | nothing owed |
| `RSW_VentStalker` | rides `kinrath_v1`/`canon_kinrath_v1` retint | deliberate; nothing owed |
| the 7 wired-and-keep imports (Lylek, Plasmorph, LuciferBug, Radyak, RipperHound, Skalder, Silooth) | donor mods' own art | wiring is def work, no art owed |

## 6. Queued art — 13 subjects, 19 job files

**CSV:** `infrastructure/artpipe/art_lists/cauldron_bedazzle_cast.csv` —
`rimflow_item_id CAULDRON_BEDAZZLE_SITTING_1`, channel codex, transparent,
priority 70. Queued via `fill_queue.py`; per-facing jobs land in
`infrastructure/artpipe/pending/` with east as the derive-facings master
(ARTPIPE_FACING_COHERENCE_1 default).

| id | canvas | facings | kind |
|---|---|---|---|
| `RM_Vexxiss` | **512** | south,east,north | creature (colossus precedent: scale carries in pixels) |
| `RM_Zisska` | 256 | south,east,north | creature |
| `RM_Eskith` | 256 | south,east,north | creature |
| `RM_Xithess` | 256 | single | flora |
| `RM_Vexxith` | 256 | single | item/stuff master |
| `RM_GasTapScaffold` | 256 | single | building |
| `RM_FilterWorks` | 256 | single | building |
| `RM_FilterCartridge` | 256 | single | item |
| `RM_Seismograph` | 256 | single | building |
| `RM_CauldronVent` | 256 | single | map feature |
| `RM_CorrodedWellhead` | 256 | single | ruin kit |
| `RM_CorrodedCondenserStack` | 256 | single | ruin kit (tall) |
| `RM_CorrodedShrine` | 256 | single | ruin kit |

## 7. Handoff notes (defects/finds observed — nothing filed, per this brief)

- **`RM_CompResourceCondenser` / `RM_CompGatherableGas` already exist**
  (`src/RimMandrake/EnvironmentalHazards/Source/`, consumed by
  `RUT_SteamCatch.xml` in TerminalBiomes) — a comp family for a building that must
  sit on a vent/geyser ThingDef and bank a resource. `CAULDRON_MECHANICS_BUILD_1`
  §3's gas-tap scaffold looks like this exact shape; FOUNDRY should read those two
  files before writing new C# ("search src before designing" — this project keeps
  having already built it).
- The Scald sea owns `scald2_ventbuilding_a/_b` art — superficially similar subject,
  different biome register; nobody should "save a job" by reusing it here.
- Spent-cartridge ruin litter (mechanics §4's set dressing) can ship as a retint of
  the `RM_FilterCartridge` master — dressing, not a second art commission.
- Building sprites are commissioned single-facing per sitting precedent (Swale). If
  FOUNDRY defs any of them Graphic_Multi, file the extra facings as follow-on jobs
  rather than blocking the build.
- The review's roster-gap note stands: the 7 imports wire on the Utinni/donor layer
  per Q11/Q11a and two frozen-sheet ban lines need amending under ruling 7 — that is
  `CAULDRON_RULED_CONTENT_1` §1's work, restated here only so nobody reads this
  bible's silence as the sheet standing unamended.


TASK: Give 8 to 12 recommendations that would make The Cauldron (formerly Poison Forest) richer, more memorable and more distinct, filling the weakest of the nine marks first. Improve and extend what is ruled rather than restarting it. For each recommendation:
- **Name** and a one-line pitch
- What the player sees, hears and feels
- Which of the nine marks it lifts
- How it could be built in RimWorld 1.6 and a rough size (XML only / small C# / large C#)
- Why it belongs to THIS biome and no other

Then list your TOP 3 in rank order with one line of why each. Reply in Markdown, at most about 1500 words. Do not ask questions; do not modify any files.