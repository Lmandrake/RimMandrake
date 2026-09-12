# WORLDMAP_FINAL_REVIEW_1 — offline audit: names (plot-leak/register) + rivers/roads reconciliation

Instruments (all live dumps, 2026-09-12 unless noted): `Transient/worldreview/features.json`,
`settlements.json`, `landmarks.json`, `links_rivers_roads.json`; `world/ASHKARR_WORLDMAP_tiles.csv`
(frozen worldmap tile table, read via `csv.DictReader`). Read-only pass; no writes outside this file.

---

## Job 1 — text / plot-leak pass

Scope actually checked: all 71 feature names (`features.json`), all 96 named settlement/world-object
names + their faction labels (`settlements.json`, 196 objects total), and all 3414 landmark
`label`/`name` pairs (`landmarks.json`). Cross-checked every name in all three files against a
word-list of reveal-gated terms (`overdrive`, `splice`/`spliced`, `contagion`, `made`, `rakata`,
`assailant`, `helix`, `reveal`, `engineered`, `forged`, `adoption`, `ascendant`, `archotech`,
`kindled`) and against a debug/placeholder pattern (`test`, `todo`, `tbd`, `xxx`, `debug`,
`placeholder`, `temp`, `unnamed`, `foo`, `bar`, `lorem`, `sample`, `dummy`, `new colony`).

**Concealment-law check (register note, `design/Jawa/cathedral_concealment_arc_spec.md`):**
"Rust Cathedral" appears as feature #`21`-adjacent entry (236 tiles) — this is the FROZEN canon
name for the biome/region/mind (`design/Jawa/worldbuilding/biomes/the_rust_cathedral.md` line 11,
`BIOME_FREEZE_FABLE_REVIEW_1`), not a leak: the name itself carries no agency/aliveness claim, it's
an architectural metaphor. No feature, settlement, or landmark name contains "alive", "hungry",
"wants", "mind", "sentinel", or any Cathedral-agency word. **No violation.**

No name in any of the three files matches the reveal-gated word-list except **"Helix Landing"**
(a settlement of the Ascendant Helix faction) — this only echoes the faction's own public name,
which is legitimate map furniture (same as "Galactic Empire" settlements being Imperial-named);
it does not name the splice, the forged-kinship reveal, or the Overdrive program. **No literal
violation.**

No debug/placeholder-pattern hits anywhere in 3680 unique names across the three files.

### Findings (5 total; 1 medium, 3 low, 1 informational)

1. **[MEDIUM] Ascendant Helix settlement names thematically gesture at the reveal-gated splice/
   forged-kinship secret, without naming it.** `Specimen Hall`, `The Revision`, `The Fair Copy`,
   `Cold Archive` (all Ascendant Helix, `settlements.json`) read, in sequence, like a genetics/
   cloning-lab register — "Specimen" and "Fair Copy" especially. `04_factions.md` §9 states the
   Helix's core secret (spliced Rakatan sequence to fake descent; "forged-adoption reveal") is
   late-game/reveal-gated. These names never use the words "splice", "clone", "gene", "DNA", or
   "kinship" and so do not break the letter of the concealment law — a player reading them
   in-world sees an eccentric gene-cult's architecture, not a stated fact. But they are the
   closest thing to a leak found in this pass (thematically pointed, not neutral), and worth an
   owner look before calling the name set final.
2. **[LOW] Duplicate/near-duplicate feature-name roots.** `Fall Line` (155 tiles) and
   `Fall Line Barrens` (153 tiles) share an identical prefix; `Scald` (312 tiles) and
   `Scald Spine` (174 tiles) share an identical root. Both pairs are presumably adjacent regions
   sharing a theme, but on a player-facing world map two same-rooted labels close together read
   as one place with a typo, not two. Cosmetic, not a leak.
3. **[LOW] Settlement name "Colony" (faction: New Arrivals) is a bare generic noun** — it is
   literally the vanilla default-settlement word, not an evocative name, unlike every other
   faction's settlements (`Sunspire`, `Boilquay`, `Coldfire`, etc.). Arguably in-register for a
   faction called "New Arrivals" (they haven't earned a proper name yet) but reads as a
   placeholder next to everything else on the map; owner call.
4. **[INFORMATIONAL, not actionable] 32 exact-duplicate names inside the 3414-entry landmark
   dump** (e.g. `Dead Sarlacc` ×7, `Black Caverns` ×3, `Mindy's Caves` ×3, `Combarro Karst
   Hollows` ×3, plus 28 more pairs — full list reproducible from `landmarks.json`). These are
   vanilla RimWorld's own procedural landmark-namer output (person-name + noun-bank
   combinations: caverns, valleys, ruins, oases, etc.), not hand-authored design content, and
   duplicates are statistically expected at this landmark density from a finite name bank. No
   plot-leak or register risk — flagged only for completeness since the instructions named
   "any landmark labels" in scope.
5. **[Ruled out, not a finding]** All other Hutt Cartel (`Gorga the Immense's Palace`, `Hurgo's
   Kennels`, etc.), Homestead Defense League, Wildsteam Clan, Free Droid Enclaves, Blackstar
   Company, Deep Desert Tribes, and Deepwater Compact settlement names read as an internally
   consistent plain-noun/faction-flavor register (droid names lean code/philosophy —
   `Unbound Exception`, `Second Speaker`, `Vent Nine`; homesteaders lean utilitarian —
   `Reservoir 7`, `Pumphouse`, `The Sumps`) with no register breaks found.

---

## Job 2 — rivers/roads reconciliation

All numbers below are MEASURED against the named instrument; no number is inferred across files.

### Rivers

- **Live bridge read (`links_rivers_roads.json`, 2026-09-12), edge/adjacency definition:**
  1562 total linked tiles in the dump. Of these, **335 distinct tiles carry at least one
  `potentialRivers` edge or `visibleRivers > 0`** (river-linked tiles). The `potentialRivers`
  adjacency list is fully symmetric (652 directed entries, every `(a,b)` paired with a `(b,a)`)
  → **326 undirected river edges** (652 / 2).
- **Frozen CSV (`world/ASHKARR_WORLDMAP_tiles.csv`), flow-accumulation definition:**
  **298 tiles have a nonzero `river_flow` value** (of 21872 total tile rows), out of 205 distinct
  nonzero flow values — this is a per-tile hydrology scalar, not a graph-edge count.
- **canon.yml's `rivers_tiles: 298`** is an exact match to the CSV's river_flow-nonzero count —
  canon was measured under the CSV's flow-accumulation definition, not the live WorldGrid's
  edge/adjacency definition.
- **Reconciling against "326 river edges / 217 origin tiles" (earlier offline read):** the 326
  edge count matches the live bridge read's 326 undirected `potentialRivers` edges exactly — same
  instrument, same definition, confirmed current. The 217 "origin tiles" figure does **not**
  match the live read's 335 distinct river-linked tiles, and I have no visibility into how the
  earlier offline read defined "origin tile" (first endpoint per edge? a `riverDist==0` filter
  under a different data source? this dump's own `riverDist` field is a distance/index value,
  not a presence flag — 1238 of 1562 tiles show `riverDist==0` as an apparent unset default, so
  it cannot be used here to reproduce "origin"). **UNKNOWN** — cannot state whether 217 is still
  correct without knowing that instrument's tile-counting rule.
- **Verdict:** three definitions, three legitimate numbers — 335 tiles / 326 edges (live
  WorldGrid adjacency, 2026-09-12), 298 tiles (frozen CSV `river_flow` accumulation), 217 tiles
  (unreconciled, prior instrument, method unknown). canon's 298 is CONSISTENT with — and appears
  sourced directly from — the CSV's `river_flow`-nonzero definition; it is answering a different
  question than the live edge-count read, not a competing measurement of the same thing.

### Roads

- **Total road-carrying tiles (live read):** **1275** distinct tiles carry a `potentialRoads`
  edge or `visibleRoads > 0`, out of the same 1562-tile dump (1275 road-only + 48 tiles carrying
  both a river and a road link + 287 tiles carrying only a river = 1562, so 1275 + 335 − 48 =
  1562 checks out exactly).
- **Road-on-water check, joined against the CSV `biome` column:** biomes whose name contains
  "Sea" or "Lake" — `RUT_TwilightSea`, `RUT_GreySea`, `RUT_PropaneLake`, `AB_PropaneLakes` — are
  crossed by **34 road tiles**, ALL 34 on `AB_PropaneLakes` (tile ids include 61, 301, 627, 1528,
  2791, 3147, 3872, 6143, 6182, 6186, 7649, 7651, 8002, 8008, 8734–8737, 9077, 9087, …; full list
  reproducible from the two source files). **Zero** road tiles fall on `RUT_TwilightSea`,
  `RUT_GreySea`, or `RUT_PropaneLake`.
- **Representation caveat (measured, not inferred):** the CSV also carries a `water` boolean per
  tile. Every tile in `RUT_TwilightSea`/`RUT_GreySea`/`RUT_PropaneLake` has `water=1` (100% of
  607/472/57 tiles respectively) — a reliable ground-truth water flag. But every one of the 34
  `AB_PropaneLakes` road tiles has `water=0` in the same column: this biome is named "Lakes" but
  is represented as land terrain by the engine/CSV, not water. So: **by biome name, 34 road-on-
  water offenders; by the CSV's own water flag (engine ground truth), 0.** Report both — do not
  collapse to one number, per the map-representation-is-not-measurement pattern seen before on
  this project.
