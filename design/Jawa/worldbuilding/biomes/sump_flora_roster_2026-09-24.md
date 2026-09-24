# The Sump — invented flora roster

_Drafted by a Fable design subagent, 2026-09-24, against the frozen sheet, for the
`RM_TheSump` sitting._

**Status: DESIGN PROPOSAL. Nothing authored.**

Subject: `RM_TheSump` (packageId `mandrake.rm.thesump`, `THESUMP_RM_MOD_BUILD_1`).
Companion doc: `sump_fauna_roster_2026-09-24.md`. Frozen sheet: `the_sump.md` —
its rulings bind; this roster adds detail and never changes one.

## READ FIRST — every plant on this page is OURS and INVENTED

Per the owner's standing method (2026-09-23, quoted in the Webwork/Fever Wood
rosters): invent the complete roster first; look for Star Wars injection
opportunistically afterward, on the Utinni layer, additively. Every row here is
**`RM_` tier — franchise-free, invented, cast inline** (Q11a,
`biome_mod_architecture.md` §7). The free mod must be **rich enough to stand
alone**; campaign patches only add.

🔴 **Ban 3 governs everything on this page: no sun-driven flora.** Every native
plant here is a **chemotroph feeding on the tar's energy** — root-taps into the
black, not leaves toward a sun that never rises. In def terms that is
`growMinGlow` 0 (a vanilla field — cave flora already grow in the dark; no new
C# is owed for darkness-growth) and zero fertility dependence on soil sun-logic.
A photosynthesis story anywhere in a description is a sheet violation.

🔑 **And one deliberate absence: nothing here glows.** Sheet §4/§9: *"the
biome's only living light is farmed fire-in-waiting"* — the wick-gardens and
derrick lamps are the only lights. A bioluminescent plant would hand the biome
a free lamp and break the artistic theme. No row below emits light, and an art
pass that adds glow has broken the design.

### The silhouette brief is the specification

Same rule as the sibling rosters: the **silhouette FORM** column is what art is
commissioned against. A row whose form duplicates another row's has failed —
the player must name a plant at a glance from a top-down sprite, in permanent
deep dusk, against every black there is.

---

## The tar ecology in one paragraph

The Pyrelands make the tar; drainage carries it down and nightward; the Sump —
1 m elevation, the planet's lowest ground — collects it, and the cold past the
terminator is the lid (sheet, R-H9 as reconciled). So the flora's energy source
arrives by gravity and never leaves: a biologically rich hydrocarbon larder
under permanent twilight. Everything green-grey here stands in a **ring at the
pit margins** (sheet §4: the edge-flora; donor plantDensity 0.25 kept for
exactly this edge-ring pattern), roots tapped sideways into the black. Out on
the pools themselves only a living sheen and a crust-growth survive — and one
plant that pretends to be the crust. The flora is also the biome's *index*:
what grows where tells you where the tar is shallow, where it breathes, where
it is holding something, and where it is lying.

---

## 1. The rulings this roster serves

| ruling | source | what the roster owes it |
|---|---|---|
| **Every native plant is chemotrophic on the tar** | sheet §6 ban 3; §4 edge-flora | every row's biology is a tar-tap; `growMinGlow` 0 across the board |
| **The only living light is farmed fire-in-waiting** | sheet §4, §9 | wick-plant is the signature crop; ⛔ no row glows |
| **No rain, no surface water; the only liquid is tar** | sheet §6 ban 4 | no row is a pond plant, a rain-drinker, or a dew-catcher |
| **No warm-climate donor flavor; cold country** | sheet §6 ban 5 | waxy, low, slow forms — nothing tropical, nothing sun-baked |
| **No vanilla-Earth flora** | sheet §6 ban 6 | zero Earth-nameable rows |
| **Edge-ring pattern; plantDensity 0.25** | sheet §0, §4 | the roster is a margin ring plus a tar-surface film — never a meadow |
| **Forageability 0.8 re-pointed at the edge-flora** | sheet §0 | one row (`RM_Skelver`) is explicitly the forage staple that number describes |
| **The tar takes slowly, keeps perfectly** | sheet §5 | two rows make the archive *legible*: the grave-bloom and the false floor |
| **Dig-lottery is core gameplay; booby traps weighted first** | sheet §7 | flora marks dig-worthy ground but never replaces the lottery — information, not loot |
| **The free mod stands rich alone** | Q11a | ten rows, no donor, no canon needed |

## Rows — ten plants in three registers

### 2. The farmed fire — the station crops (2 rows)

The only agriculture on the night edge. Both are grown in worked tar-beds at
the stations; both exist wild at low commonality so a fresh colony can find
starter stock.

| # | defName | label | silhouette FORM | what it looks like | job | mechanism | art |
|---|---|---|---|---|---|---|---|
| 1 | `RM_Plant_Wick` | wick-plant | **stiff upright candle-stalks in tended rows, pale wax over dark pith** | Knee-high rigid stems sheathed in dull wax, grey-green at the base shading to bone at the tip — a garden of unlit candles. | ⭐ **The signature crop** (sheet §4): slow-burning stems harvested as candles and lamp-stock. Light as a crop; the stations' lamp-gardens are wick-gardens. Fire-in-waiting, farmed. | ✅ **EXISTS** — shipped as `RUT_Plant_Wick` + `RUT_WickStem` (real art, `SUMP_MECHANICS_1`); renames to `RM_` in the mod build. Sheet-named; keeps its plain name (fauna doc, open ruling 6) | ✅ shipped |
| 2 | `RM_Dorvel` | dorvel | **squat segmented barrel-cluster hugging the ground, waxy bloom on top** | Fist-sized grey-green barrels packed like roe, each capped with a waxy rosette; grown in beds it tiles the ground like cobblestone. | 🔑 **The food crop — the reason a Sump colony can eat.** A cultivable chemotroph raised in worked tar-beds; bland, dense, reliable calories with no sun and no sunlamp. The stations live on it; so can the player. Wild dorvel (comm. ~0.05, station-adjacent) is starter stock. | new PlantDef, `sowTags` on tar-bed terrain (§5); no C# | **OWED** |

### 3. The edge ring — the chemotroph margin (5 rows)

The waxy grey-greens of sheet §9, standing in a ring at the pit margins where a
root can reach the tar without drowning in it.

| # | defName | label | silhouette FORM | what it looks like | job | mechanism | art |
|---|---|---|---|---|---|---|---|
| 3 | `RM_Skelver` | skelver | **flat splayed rosette, thick spatulate leaves, one tar-dark taproot scar at centre** | A dinner-plate rosette of fat waxy leaves, grey-green with a dark oily heart where the taproot goes down. Grows in arcs along pool edges — never away from black. | 🔑 **The forage staple** — the row that §0's forageability 0.8 actually points at. Edible raw at the usual penalty; the ring of skelver around a pool is the biome's baseline green and the first thing a hungry caravan learns. | none; `growMinGlow` 0 | **OWED** |
| 4 | `RM_Korveth` | korveth | **gnarled fist-sized black nodules on a low woody frame** | A knotted shin-high shrub whose branches swell into glossy black lumps, like a plant growing its own coal. The lumps weep a hard varnish. | ⭐ **The bitumen accumulator.** It concentrates the tar's heavy fraction into harvestable pitch-nodules — small-scale bitumen (waterproofing, adhesive, torch-fuel, §7) without sinking a dig. The plant version of the barrel trade: slow, renewable, unexciting, always wanted. | harvest yields a bitumen item (shared item def with the dig economy; `LIQUID_TYPES_MOD_1` owns tar *grades*, this is the solid) | **OWED** |
| 5 | `RM_Brindeth` | brindeth | **sparse twiggy broom-scrub, dark wood, almost leafless** | A waist-high broom of dark wiry twigs with mean little wax-scale leaves, standing in the outermost ring where even the tar's reach thins. Half of every brindeth is dead wood. | **The outer ring's woody margin — and the only stick of timber for a day's walk.** Twig-fuel and poor wood in a biome with no trees: enough for a derrick splint or a fuse post, never for a hall. Its thin, hard silhouette is the biome's tree-line joke. | none; low wood yield | **OWED** |
| 6 | `RM_Soffeth` | soffeth | **loose ring of soft grey bladder-stalks, each slightly bowed** | Ankle-high pale stalks tipped with soft gas-bladders, growing only in rings around seep-mouths where the tar breathes. They nod when a bubble passes below — the only plant here that moves. | 🔑 **The breather's tell.** Soffeth feeds on what the seeps exhale, so a soffeth ring means gas below: don't dig here, don't pour a moat here, don't ground a lamp here. Information, exactly like the mouse-lines — the biome keeps teaching you to read it. | placement keyed to seep/gas map cells (GenStep scatter rule; no per-tick C#) | **OWED** |
| 7 | `RM_Tolleth` | tolleth | **single pale bell-flower bowed on a dark leafless stem** | One waxy off-white bell on a bare black stem, head bowed, growing alone or in twos — never in beds. The only flower in the biome, and it only grows where the tar is holding something. | ⭐ 🔑 **The grave-bloom — "the trap that remembers" made botanical.** Tolleth roots down to entombed organics and feeds on the slow seep of what the tar keeps, so a tolleth marks a body, a hide, a find: the archive's index flowers. Junkers flag digs by tolleth; players learn the same. ⛔ Not valuable itself — its worth is where it stands. | placement biased to dig-lottery-rich cells (rides `RM_LotteryTableDef` seeding — PARTIAL, see §6) | **OWED** |

### 4. The black itself — what lives ON the tar (3 rows)

Sheet §5: nothing touches the tar but the mice, the grazer and the under-layer.
These three don't touch it either — they *are* its surface.

| # | defName | label | silhouette FORM | what it looks like | job | mechanism | art |
|---|---|---|---|---|---|---|---|
| 8 | `RM_Velloch` | velloch | **iridescent-dull film patches with curled lifting edges** | A living sheen on the still pools — matte rainbow-on-black patches whose edges curl and flake like old paint. Not a plant you notice until you notice it is everywhere. | **The tar's own micro-flora** — the base of the whole chemotroph chain and the direct replacement for donor `AB_TarPuddle` (today's only flora row, comm. 0.6). Ungatherable, unkillable, atmospheric: it makes the black read *alive*. | none; fert 0, decorative-density | **OWED** |
| 9 | `RM_Mirrelin` | mirrelin | **thin pale crust-lace spread flat on dark glass** | A frost-like lace of pale grey crust growing flat on the cooled sheet-tar of the glass reaches, in patches the size of rooms. Mouse-gnawed at every edge. | 🔑 **The glass-reach graze — what the sump-mice actually eat out there.** Mirrelin is why the mice run the black at all (fauna doc row 1): the prey base's pasture, and its gnawed trails are half of how a mouse-line forms. Walkable ground grows it; soft tar never does — so mirrelin underfoot is also a quiet promise the ground holds. | none; grows on cooled-tar terrain only | **OWED** |
| 10 | `RM_Pallick` | pallick | **a mirrelin-like crust that is subtly TOO even, no gnawed edges** | A pale crust-mat almost indistinguishable from mirrelin — but uniform, ungnawed, unbroken: a perfect skin. Because under a pallick mat there is no cooled glass, only soft deep tar the plant has roofed over. | 🔴 ⭐ **The false floor — the biome's one lying plant.** Pallick grows out *over* soft tar, mimicking safe crust; step on it and the skin fails: mired, held, hurt — never insta-killed (the tar takes *slowly*). The tell is the fauna: **mice do not cross pallick** — an unbroken pale patch no mouse-line touches is the lie, read exactly like a beast's back (sheet §4). Open ruling 5 (fauna doc). | NEW small comp: on pawn entry, collapse to deep-tar terrain + mire/stun (see §6) | **OWED** |

## 5. Donor terrain and flora dependencies to replace

What the standalone mod must stop depending on (build item §2/§4):

| donor def | role today | proposed replacement | note |
|---|---|---|---|
| `AB_TarPuddle` (Alpha Biomes plant, comm. 0.6) | the def's only wildPlants row | **`RM_Velloch`** (§4 row 8) | direct 1:1 — same job, ours, designed for the palette |
| `AB_GrassySand` (terrain, fert ≤0.25) | low-fertility ground | **`RM_TarPan`** — cracked ash-dark pan, the walkable between-pools ground | name PROPOSED here; terrain authoring belongs to the build |
| `AB_LushGrass` (terrain, fert >0.25) | high-fertility ground | **`RM_TarLoam`** — dark rich margin loam where ash and tar mix; the edge ring roots here; worked into **tar-beds** (`sowTags`) for wick and dorvel farming | ditto; "lush grass" was always the wrong picture for cold tar country (ban 5) |
| `AlphaBiomes.BiomeWorker_TarPits` (workerClass) | biome worker | `RimMandrake.TheSump.RM_BiomeWorker_TheSump` | already specified in `THESUMP_RM_MOD_BUILD_1` §11 step 2 — listed here only for completeness |

The kit's own terrain (`RUT_TarMoat`/`RUT_TarSpent`, the `RUT_TarShallow`
filth-acceptance patch) is ours already and simply renames `RM_` with the mod.

## 6. Mechanism inventory (exists / partial / new)

Per the standing rule — this project keeps re-inventing what is already built —
every mechanism named above, checked against `SUMP_MECHANICS_1` (S1–S6 shipped,
all C# in `mandrake.rm.environmentalhazards`) and the kit XML on disk:

| proposal | status |
|---|---|
| darkness growth for all chemotrophs | ✅ EXISTS — vanilla `growMinGlow` 0 (cave-flora precedent); def field, no C# |
| wick-plant crop + harvest item | ✅ EXISTS — `RUT_Plant_Wick` + `RUT_WickStem`, shipped with real art |
| permanent dusk the flora lives under | ✅ EXISTS — `RUT_SumpWeather` + `RUT_SumpDuskLock` + `Patches/RUT_SumpDuskLock_BiomeWiring.xml` |
| moat/burn economy the wick and brindeth fuel feeds | ✅ EXISTS — `RM_CompFloodIgniter`, `RM_CompTimedTerrainBurn`, `RM_MapComponent_ThresholdSmokeColumn` |
| dig-lottery the tolleth indexes | ✅ EXISTS — `RM_LotteryTableDef` + `RUT_DigStratumTable` + `RM_CompWorkedLottery` + `RM_WorkGiver_WorkLottery`/`RM_JobDriver_WorkLottery` |
| tolleth placement biased to lottery-rich cells | ⚠️ PARTIAL — the lottery tables exist; a GenStep/scatter rule reading them for plant placement does not. Small, data-driven, build-item work |
| soffeth placement on gas seeps | 🆕 NEW (small) — a seep-cell scatter rule at mapgen; no per-tick code. There is no gas-seep map layer today; the scatter rule can invent its own seed points |
| pallick false-floor collapse | 🆕 NEW (small) — one comp: on pawn entry, convert cell to deep-tar terrain + apply mire (movement) hediff. ⛔ Never lethal on its own; the tar takes slowly |
| korveth bitumen harvest item | 🆕 NEW def only — the item; no C#. Tar *grades* stay `LIQUID_TYPES_MOD_1`'s |
| dorvel tar-bed farming | 🆕 NEW def only — `sowTags` on the `RM_TarLoam` worked-bed terrain; no C# |
| mirrelin/pallick reading by mouse behaviour | ✅ EXISTS on the fauna side — `RM_MapComponent_DreadField` + `RM_JobGiver_DreadAvoidWander` + `RM_CompFilthTrail` (mouse-lines); pallick joins as a dread source region, which is PARTIAL (fauna doc §6) |

## 7. Canon injection (additive, Utinni layer)

**No canon flora is recommended for this biome.** The Sump's flora story —
farmed fire, a chemotroph ring, a lying crust — is complete in ten invented
rows, and no surveyed canon plant survives ban 3 (chemotrophy) plus the
opportunistic-injection bar. If a candidate ever surfaces it is verified
through the Wookieepedia search API (`action=query&list=search&srsearch=`) —
never a guessed title, never a donor mod's defName, and absence from
`canon_references/` (137 entries by design) proves nothing.

## 8. Art brief hooks (roll-up)

One line each, against sheet §9 (*"black glass under horizon-glow, ringed in
farmed lamplight"* — every black, horizon amber, lamp gold, waxy grey-greens,
derrick rust; ⛔ nothing glows):

- **wick-plant** — a garden of unlit candles, wax over dark pith *(shipped)*
- **dorvel** — grey-green roe-barrels tiling a worked black bed
- **skelver** — a waxy dinner-plate rosette with an oily dark heart, arcing along a pool edge
- **korveth** — a shrub growing its own coal, varnish-weeping black nodules
- **brindeth** — a half-dead wire broom against a flat horizon, the biome's only "tree"
- **soffeth** — soft grey bladder-stalks ringing a seep, caught mid-nod
- **tolleth** — one bowed bone-white bell on a bare black stem, alone
- **velloch** — dull rainbow-on-black film, edges curling like old paint
- **mirrelin** — pale frost-lace flat on dark glass, gnawed at every edge
- **pallick** — the same lace, too perfect, no gnawed edge anywhere — the wrongness must be findable but subtle at display size

## Appendix — collision sweep (MEASURED, this pass)

Python sweep (never a zsh loop), case-insensitive, over all
`.md/.xml/.json/.cs/.py/.txt/.csv` under `design/` and `src/` — **4,584 files
scanned**. Sanity probes first: `korrum` 39 occurrences in 11 files,
`stoneback` 164 in 43, `hawkbat` 261 in 50. ✅ The instrument sees.

**Result: all 9 new flora names on this page have 0 occurrences outside the
Sump sitting docs.** The sweep caught one real collision before this doc was
written: the food crop was first named *gorrel* — already the Alien Bestiary's
chickenrabbit vermin (4 occurrences, `Alien_Bestiary.md`,
`Livestock_Trade_Utility_Pets_v1.md`). Renamed **`RM_Dorvel`**, re-swept: 0
occurrences anywhere.
