# Map generator v0 — the CHOOSER (spec)

Item: `infrastructure/state/items/MACRO_GENERATOR_V0_1.md`. Parent research:
`design/RimMandrake/map_content_injection_research.md` §5.5, §5.8, §9.1 #7-8, §9.2-9.4.
The chooser takes a biome sheet + a seed (+ the world tile's facts) and writes ONE PLAN.
It paints no cells. Everything downstream (GL graph emitter, meso texture, gates, sheet)
reads the PLAN and never the sheet. Implement this without asking; where a value is
marked *owner grades*, the comparator sheet decides, not the implementer.

Inputs: `sheet` (one file under `design/Jawa/worldbuilding/biomes/`, fields 6 and 8 are
the only fields the chooser parses), `tile` (`{has_river, has_coast, elevation_m}` —
all default false/0 when unknown), `seed` (int), `map_size` (int, edge length).
Corpus biomes map to sheets: vanilla `Desert` → `desert.md`, `AridShrubland` →
`arid_shrubland.md`; `ExtremeDesert` → `deep_desert.md`; `Wasteland` → `wasteland.md`.
All four exist (read 2026-09-06). Every other sheet is parsed the same way.

## A. The PLAN schema

```json
{
  "schema_version": 1,                 // int — bump on any field change; validator refuses unknown versions
  "seed": 4127,                        // int — the only entropy; same (sheet, tile, seed, map_size) ⇒ byte-identical plan
  "biome": "Desert",                   // string — vanilla BiomeDef defName of the tile
  "sheet": "desert.md",                // string — the sheet file the weights came from
  "map_size": 275,                     // int — edge length; picks the calibration bucket
  "premise": "…",                      // string — ONE sentence ≤20 words a player could say about the map; names the landform noun and the anchor noun
  "landform": {
    "id": "Canyon",                    // string — one Id from V (rule 1)
    "source": "gl"                     // "gl" | "vanilla" — vanilla for the Ids GL yields to under Odyssey (§5.8 c)
  },
  "landform_params": {                 // object — the 2-4 PLAN knobs for this landform (rule 10); names are the plan's, the emitter maps them to GL nodes
    "footprint_fraction": 0.35,        // float — share of map area the landform occupies (per-landform range, rule 10)
    "orientation_deg": 40,             // int 0-359 — long axis; multiple of the biome's wind grain when the sheet has one
    "relief_class": "high"             // "low" | "mid" | "high" — elevation contrast; the emitter picks the numeric band
  },
  "hydrology": {
    "kind": "dry_riverbed",            // one of: none, dry_riverbed, salt_pan, brine_seep, spring, river, delta, coast_inlet
    "cause": "…"                       // string — MANDATORY when kind≠none; must name the landform id or the history (rule 4). When kind=none: "none, because …"
  },
  "anchor": {
    "position": "narrows",             // string — one of the 1-2 names the anchor table allows for this landform (rule 3)
    "cell_frac": [0.52, 0.48],         // [x, y] in 0-1 map fractions — the emitter/gates resolve to a cell
    "holds": "…"                       // string — WHAT sits there; a noun from the sheet's field 8 (v0: named only, not built — §E)
  },
  "history": "…",                      // string — ONE past-tense line: what happened here before the player (rule 9)
  "deletions": [                       // array ≥3 — what the premise FORBIDS on this map; each tagged with its source (rule 6)
    {"forbid": "any relief outside the canyon walls", "source": "landform"},
    {"forbid": "burn scars", "source": "sheet:6.5"},
    {"forbid": "a second channel or branch", "source": "premise"}
  ],
  "calibration": {                     // object — the corpus_map_stats.md ranges for this size bucket; downstream regression reads THESE, never the doc
    "bucket": "275",
    "region_count": [940, 2995], "largest_region_fraction": [0.080, 0.570],
    "perimeter_area_mean": [2.773, 3.053], "openness_top3": [0.522, 0.923],
    "openness_std_25": [0.127, 0.324], "distinct_terrains": [13, 24]
  }
}
```

Calibration buckets are copied verbatim from `corpus_map_stats.md` "By size bucket" (min/max; 250, 275, 300, 325+, 400+). Outside the range is information, not failure.
## B. The chooser's rules (each falsifiable)

1. **Closed vocabulary.** `landform.id` ∈ V. V = GL dryland Ids {DesertPlateau, Badlands,
   Canyon, Crater, Rift, Gorge, Sinkhole, Caldera, Cirque, LoneMountain, SecludedValley}
   (`source:"gl"`) ∪ the Ids GL disables under Odyssey in favour of vanilla mutators
   {DryLake, Oasis, Valley, Coast, Cove, Lake, Peninsula, CoastalIsland} (`source:"vanilla"`;
   the exact vanilla `TileMutatorDef` defName is read from the def dump by the emitter,
   never typed here). *Test:* any other string is rejected by the validator; a `gl` source
   on a vanilla-group Id is rejected (§5.8 c: the emitter must not target them).
2. **Weights come from field 8; bans come from field 6.** Each bullet (or table row) of the
   sheet's field 8 is matched against the noun lexicon below; every hit adds 1 to that
   landform's weight. Then every field-6 ban matched by the ban lexicon removes landforms.
   The seed draws proportionally from what survives. Unmatched bullets contribute nothing.
   *Test:* over 1,000 seeds on one sheet, each surviving landform's frequency is within
   ±5 pp of weight/Σweights; a removed landform appears 0 times; the chooser logs the bullet
   that gave each point (provenance is part of the plan's log, not the plan).

   | field-8 noun (regex, case-insens.) | adds weight to |
   |---|---|
   | `canyon\|gorge\|gulch\|ravine` | Canyon, Gorge |
   | `cave\|cavern\|throat\|sinkhole\|pit` | Sinkhole, Rift |
   | `ridge\|crag\|isolated rock\|rock island\|mountain` | LoneMountain, DesertPlateau |
   | `plateau\|mesa\|table\|shelf\|cliff` | DesertPlateau, Cirque |
   | `crater\|blast\|vitrified\|impact\|wreck fell\|debris fall` | Crater, Caldera |
   | `salt\|pan\|basin\|dead river\|lakebed\|pool` | DryLake (vanilla) |
   | `seep\|spring\|oasis\|dew` | Oasis (vanilla) |
   | `valley\|secluded\|hidden` | SecludedValley, Valley (vanilla) |
   | `dune\|scour\|badland\|gully\|yardang` | Badlands |
   | `coast\|shore\|bay\|headland\|sea` | Coast, Cove, Peninsula, CoastalIsland (vanilla) |

   | field-6 ban (regex) | removes |
   |---|---|
   | `no standing (surface )?water\|no potable\|no water\b\|no liquid water` | Oasis, Lake, Coast, Cove, Peninsula, CoastalIsland |
   | `no geothermal\|no volcanism\|no vents` | Caldera |
   | `no abundant shade\|no cover\|no relief` | Cirque, SecludedValley, Gorge |
   | `no open sand` | Badlands |
   | `no roads` | (no landform; forbids `history` mentioning a road, rule 9) |
   Also: `Coast/Cove/Peninsula/CoastalIsland` require `tile.has_coast`; `Valley`,
   `Oasis`, `river/delta` hydrology require `tile.has_river` or `has_coast`.
   *Test:* a landlocked tile never yields a coastal Id, whatever the sheet says.
3. **Anchor follows the landform.** Exactly one `anchor.position`, drawn (by seed) from
   the table; `cell_frac` is placed by the position's geometric definition, ≥0.12 of the
   map edge from any border. *Test:* validator rejects a position not in the row; the
   gate step (P12 flood-fill) rejects an anchor cell unreachable from two map edges.

   | landform | anchor positions (name — where it is) |
   |---|---|
   | DesertPlateau | `rim` — plateau edge above the lowland · `cliff_foot` — the lee base of the cliff |
   | Badlands | `table` — the largest flat between gullies · `mouth` — where the gullies leave the map |
   | Canyon | `head` — the box end · `narrows` — the one crossing |
   | Gorge | `rim_over_narrows` · `floor_wide_end` |
   | Rift | `floor_centre` — widest floor · `shoulder` — the rim above it |
   | Crater / Caldera | `ring_centre` · `rim_breach` — the lowest gap in the rim |
   | Sinkhole | `lip` · `pit_floor` (only if the gate proves it reachable) |
   | Cirque | `headwall` — the back of the amphitheatre · `threshold` — its lip |
   | LoneMountain | `lee_foot` — the shaded side's base · `flank_shelf` |
   | SecludedValley / Valley | `valley_end` — farthest from the entrance · `neck` — the entrance |
   | DryLake | `centre` — the last pool / former island · `inlet_shore` — where the river came in |
   | Oasis | `water_edge` (one position only) |
   | Coast / Cove / Peninsula / CoastalIsland | `tip_or_island` · `inlet_head` |
4. **Hydrology has a cause or is absent.** `kind ≠ none` ⇒ `cause` names the landform id
   or a word from `history`, and the kind is allowed by the sheet: any `no standing water`/
   `no water` ban ⇒ only {none, dry_riverbed, salt_pan, brine_seep}; `no rain` alone
   forbids nothing (rain is not surface water). `river`/`delta`/`coast_inlet` need the tile
   fact. `kind = none` ⇒ `cause` starts with `"none, because"`. *Test:* validator rejects
   empty cause, a cause naming neither landform nor history, and a kind the sheet bans.
5. **One idea.** One landform id, one hydrology kind, one anchor, one history line — every
   one a scalar in the JSON, never an array. If the landform is itself hydrological
   (DryLake, Oasis, Coast group), `hydrology.kind` is that landform's own kind or `none`;
   no plan carries a second water body. *Test:* a schema check (arrays rejected) plus a
   noun check: `premise` may contain at most ONE landform noun from the rule-2 lexicon.
6. **Deletions are mandatory and sourced.** ≥3 entries, each tagged `sheet:<field.n>`,
   `landform` or `premise`. Every field-6 ban naming a map-level object (water, sand,
   green, relief, fire scars, roads, structures) is copied in as `sheet:6.n`. The landform
   row contributes its fixed exclusion ("no relief outside …", "no second ring", "no second
   channel"). At least one `premise` entry must exist: the thing the premise's own sentence
   contradicts. *Test:* validator rejects <3 entries, any untagged entry, no `premise` entry,
   or a plan whose copied `sheet:6.n` entries are fewer than the sheet's matched bans.
7. **Determinism.** Same `(sheet, tile, seed, map_size)` ⇒ byte-identical plan. *Test:* run
   twice, diff is empty; changing only `seed` changes the plan.
8. **Variety.** Seeds 1-8 on one sheet yield ≥4 distinct landform ids when ≥4 survive rule 2;
   when fewer survive, the chooser emits `WARN sheet_narrow: <n> landforms` and the sheet,
   not the chooser, is the finding. *Test:* the 8-seed run for each of the four sheets.
9. **History is one past-tense line from the sheet's nouns**, and obeys the bans: a `no roads`
   sheet never gets a road; a `no rot`/`no decay` sheet never gets an overgrown or rotted
   ruin; the noun must appear in field 8 (wreck, farmstead, salt works, tree-road, holding,
   bone-field, trench, canal, waystation …). *Test:* regex against the sheet's field 8 text.
10. **Negative space.** `footprint_fraction` per landform: DesertPlateau/Badlands 0.30-0.55;
    Canyon/Gorge/Rift 0.15-0.30; Crater/Caldera/Sinkhole/Cirque 0.12-0.35; LoneMountain
    0.10-0.25; SecludedValley/Valley 0.35-0.60; DryLake/Oasis 0.15-0.40; Coast group
    0.30-0.60 (water counts). The rest of the map is the biome's plain. *Test:* validator
    rejects out-of-range; the R2 regression flags `largest_region_fraction` outside bucket.
11. **Grain.** When the sheet names a wind grain (deep desert §9 yardangs; dune sea), the
    long axis of a linear landform (Canyon, Gorge, Rift, Badlands) is `orientation_deg` =
    grain ±15°. *Test:* on `deep_desert.md`, 8 seeds' orientations lie in one 30° band.

Least certain: rule 2's lexicon is hand-built from four sheets; a noun it lacks contributes nothing silently, so the chooser must log unmatched bullets.
## C. Five calibration plans (as the chooser would write them; corpus maps are the reference, not measured)

**1. In Memory of Rain** — Desert, 325², sheet `desert.md`, tile `has_river:true` (a river
that dies).
`premise`: "A river fans into a dry delta and dies in the basin it once filled."
`landform` DryLake (vanilla) · `landform_params` {footprint 0.38, orientation 20, relief low}
· `hydrology` {delta, cause: "the world river enters from the N edge and braids into the
DryLake basin; nothing leaves"} · `anchor` {inlet_shore, [0.50,0.30], holds: "a silted canal
grid and its settlement on the last big shade patch"} · `history`: "An older people irrigated
the delta from canals that silted when the river failed." · `deletions`: no standing water
except the last pool (sheet:6.8 lush), no burn scars (sheet:6.5), no rock mass taller than
the channel banks (landform), no second basin or outflow (premise), no green off the dew line
of the pool (sheet:6.8) · `calibration` bucket 325+ (region 1133-3821, lrf 0.069-0.490,
p/a 2.725-2.975, openness 0.544-0.880, std 0.189-0.316, terrains 11-27).
*One idea:* everything on the map is a consequence of one river that stopped — the braids,
the basin, the canals, the settlement placed where the water last arrived.

**2. Deserted Trader** — Desert, 275², `desert.md`, landlocked.
`premise`: "One rock stands in a wide gap, and the waystation in its shade is empty."
`landform` LoneMountain (gl) · params {footprint 0.18, orientation 0, relief high} ·
`hydrology` {none, cause: "none, because the tile is 20°+ of arc from water; the station's
cistern is a thing, not hydrology"} · `anchor` {lee_foot, [0.55,0.52], holds: "the abandoned
caravanserai on the shade midden"} · `history`: "A trade road crossed the gap edge to edge
and the waystation on it was abandoned when the route moved." · `deletions`: no second rock
mass (landform), no water (premise), no green outside the mountain's dew line (sheet:6.8),
no burn scars (sheet:6.5), no shelter anywhere but the lee (premise) · bucket 275 (940-2995,
0.080-0.570, 2.773-3.053, 0.522-0.923, 0.127-0.324, 13-24).
*One idea:* the wide gap IS the map (desert field 8: "the last patch before a wide gap is
the most contested real estate"); one shadow, one road across nothing, one empty building.

**3. Lush River** — Arid Shrubland, 250², `arid_shrubland.md`, `has_river:true`.
`premise`: "A river runs the valley floor and every green thing on the map hugs its bank."
`landform` Valley (vanilla) · params {footprint 0.45, orientation 110, relief mid} ·
`hydrology` {river, cause: "the world river descends the Valley floor; the lush line is the
river line under the three-part lush rule"} · `anchor` {neck, [0.30,0.50], holds: "the one
ford, and the hedge-fort watching it"} · `history`: "A moisture farm on the far bank drank
its runway dry and was abandoned; its V-shaped blight wake still points downwind." ·
`deletions`: no open sand (sheet:6.7), no green beyond 12 cells of the bank (sheet:6.6 lush),
no thicket except venomvine (sheet:6.6), no second watercourse (premise), no relief above
the valley walls (landform) · bucket 250 (496-3056, 0.044-0.635, 2.619-3.064, 0.498-0.923,
0.136-0.296, 12-28).
*One idea:* the river is the only reason anything lives here, and the map says so by making
the green a line, not an area.

**4. Point Sea** — Arid Shrubland, 275², `arid_shrubland.md`, `has_coast:true`.
`premise`: "A headland pushes into the sea; the only shelter is the cove in its lee."
`landform` Peninsula (vanilla) · params {footprint 0.50, orientation 45, relief mid} ·
`hydrology` {coast_inlet, cause: "the sea wraps the Peninsula; the cove is its lee side"} ·
`anchor` {tip_or_island, [0.78,0.22], holds: "the named tree at the end of the sweetline
tree-road"} · `history`: "A tree-road ran the spine of the headland to a named tree at the
point; its markers still stand." · `deletions`: no inland water (premise), no second bay
(landform), no open sand (sheet:6.7), no dense flora off the spine (sheet:6.6), no natural
burn scars (sheet:6.2) · bucket 275 (as plan 2).
*One idea:* one shape — land into water — and the anchor sits where the shape points.

**5. Blood Gulch** — Arid Shrubland, 250², `arid_shrubland.md`, landlocked.
`premise`: "One red gulch cuts the shrubland corner to corner; the only way across is the
narrows."
`landform` Canyon (gl) · params {footprint 0.22, orientation 40, relief high} · `hydrology`
{dry_riverbed, cause: "the Canyon floor is the flash channel that cut it; no rain, so it
never runs"} · `anchor` {narrows, [0.52,0.48], holds: "a hedge-fort on the rim above the
crossing"} · `history`: "A hedge-fort held the crossing; its venomvine walls have gone wild."
· `deletions`: no relief outside the canyon walls (landform), no water in the channel
(sheet:6.1 no rain + premise), no second gulch or branch (premise), no open sand (sheet:6.7),
no thicket away from the fort (sheet:6.6) · bucket 250 (as plan 3).
*One idea:* a single cut and a single crossing; the map is a wall with one door.
## D. Failure modes the implementer must test

| failure | test (a validator, never taste) |
|---|---|
| everything everywhere | feed a plan with two landform ids, or two anchors, or two hydrology kinds (as arrays or a second premise noun) ⇒ validator REJECTS with the rule number. Feed each of the five §C plans ⇒ ACCEPTS |
| same landform every time | seeds 1-8 on each of the four sheets ⇒ ≥4 distinct ids, or a `sheet_narrow` warning naming the surviving count; a run that gives 1 id and no warning FAILS |
| premise with no consequence | `deletions` empty, <3, untagged, or lacking a `premise`-sourced entry ⇒ REJECT |
| hydrology without cause | `kind≠none` and empty cause, or cause naming neither landform nor a history word ⇒ REJECT; `river`/`delta`/`coast_inlet` on a tile without the fact ⇒ REJECT |
| banned landform leaks | 1,000 seeds on `deep_desert.md` ⇒ 0 Oasis/Lake/Coast plans; 0 Caldera on `forsaken_crags.md` |
| nondeterminism | same inputs twice ⇒ identical bytes |
| anchor off-composition | position not in the rule-3 row, or `cell_frac` within 0.12 of an edge ⇒ REJECT |
| road in a no-roads biome | `history` matching `road` on a sheet whose field 6 or 8 says `no roads` ⇒ REJECT |
## E. Deliberately left out of v0

- **Structures.** `anchor.holds` names a noun; nothing is placed. Step 7 (VEF PrefabDef /
  TileMutatorDef spawner) builds it later against the same field.
- **Residents.** Faction, guards, `DefendPoint` — step 9. A plan carries no pawns.
- **Dressing** (bone piles, debris, props inside implied shapes — §5.5 #6-7) — step 7-9;
  the plan's `deletions` already constrain what dressing may NOT appear.
- **Micro texture** (boundary jaggedness, ecotone bands, patch shapes) — G2, step 5, under
  the mask this plan implies; the plan carries only the calibration ranges it must land in.
- **The LLM plan author** (step 8) — it will write THIS schema; v0 is the deterministic
  chooser so the sheet grades a grammar, not a prompt.
- **World-tile targeting** (commonness/worldTileReq on the emitted GL graph) — the emitter's,
  §5.8 (a); the chooser knows only the tile's three facts.
