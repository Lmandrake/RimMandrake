# Utils/ — RimWorld campaign scratch utilities

Small Python tools for inspecting/authoring the save-based campaign. Each is a
focused research probe; keep them assembly-free and dependency-light.

| Tool | Reads | Emits |
|---|---|---|
| `Savegame_mapview.py` | in-play map grids (terrain/roof/things) | PNG preview + legend JSON |
| `Savegame_detailed_items.py` | every item + its flavor/narrative text | items MD report + items JSON |
| `Savegame_ideoligions.py` | every ideoligion (religion) + full flavor | ideoligions MD report + JSON |
| `mapkit.py` | — (shared library) | terrain palette + `GameMap` model + renderer |
| `map_agent.py` | a `GameMap` | LLM briefing (coarse grid + regions), edit primitives, guardrail metrics |
| `loop_run.py` | an LLM-authored plan JSON | executes plan → before/after render + report + metric deltas |
| `map_loop_agent.py` | a base `GameMap` | **automated** perceive→propose→execute→re-judge loop (needs an LLM endpoint) |
| `Map_synth.py` | — | synthesizes plausible player-style base maps into `../player_maps/` |
| `Map_improver.py` | a `GameMap` | ⚠️ superseded heuristic improver — see note below |
| **`animal_inventory.py`** | **every active mod's `Defs/` + `Patches/`** | **6 CSVs: full animal roster, attacks, life stages, biome map, conflicts, patch watch** |

---

## Map improver — LLM-in-the-loop architecture (the current design)

**The point:** creatively "improve" a player map's terrain — more realistic
geography, more tactical interest, and exotic set-pieces (abandoned mine,
half-working refinery, dead droid in a crater, cavern, crashed-Factory-ship
scar) — with justifications for what changed, where, and why.

**Design principle (per user direction 2026-08-05):** the LLM is the reasoning
engine *in the loop each iteration*; Python is only the **hands**. The LLM looks
at a specific map, decomposes it into regions, judges each region
(realism / interest / tactical / artificiality), proposes specific edits with
real coordinates, executes them through a templated toolbox, then re-judges and
retries what didn't improve. Python never decides *what* or *where* — it only
perceives, executes parameterized primitives, and computes cheap objective
guardrail metrics (transition coherence, fragmentation, diversity). Those
metrics are guardrails/tie-breakers, **not** the subjective judge.

Why this replaced the first attempt: `Map_improver.py` (kept for reference)
baked all judgment into fixed Python heuristics with blind coordinates
(`rng.uniform(...)`), so placements couldn't respond to the actual map — the
output looked "ridiculous and unjustified." Moving the judgment to the LLM fixes
that.

### The three modules

- **`mapkit.py`** — shared foundation: `TERRAIN` palette (name→rgb+props from
  the verified `../biome_terrain_palette.md`), the `GameMap` semantic grid
  (cells hold terrain *names*, not live-save shortHashes — the hash problem is
  deliberately out of scope for this practice), `render`/`render_pair`.
- **`map_agent.py`** — the toolbox (no judgment):
  1. **Perception** — `perceive(gm)` → coordinate-labeled coarse ASCII grid +
     connected-region segmentation (family, area, bbox, centroid, terrain mix,
     edges) + histogram; `briefing_text()` formats it for a prompt. The LLM also
     views the PNG with vision.
  2. **Primitives** — `terrain_gradient`, `fractalize_edge` (coherent coastline
     meander, not per-cell noise), `scatter` (coherent patches), `path`, `blob`,
     `ring`, `rect`, `hill`, `carve_chamber` (carves only through solid rock so
     caves stay enclosed), `paint_cells` (freehand), `smooth`. Dispatched by name
     via `apply_edit(gm, op, **kwargs)`.
  3. **Metrics** — `metric_transition_coherence`, `metric_fragmentation`,
     `metric_family_diversity`. Objective guardrails only.
- **`loop_run.py`** — runs ONE hand-authored plan (the manual/live mode we use
  in-session, since no LLM endpoint is reachable here). Applies edits, renders
  before/after, writes a report pairing every edit with the LLM's region
  judgment + rationale and showing metric deltas so the next iteration is
  informed.
- **`map_loop_agent.py`** — the **automated** harness: perceive → LLM proposes a
  plan → execute → re-perceive → LLM re-judges → convergence check → repeat.
  The LLM call is a pluggable seam (`caller`/`LLM_CALLER`) with a stub that
  raises `LLMNotConfigured`. **Scaffolded, not self-driving in this sandbox** —
  no LLM API host is allowlisted here. Every seam *around* the API call is real
  and was exercised with a fake caller; wire `call_llm(messages)->str` to run it
  live. A `converged()` guard can override the LLM's own "stop" verdict if a
  guardrail regressed.

### Worked example (coastal_mesa, driven live in-session)
Three iterations, each catching a real regression:
`v1` introduced a straight mud wall (diversity metric flagged 0.92→0.68) →
`v2` fixed the wall but shredded the coast into salt-and-pepper (fragmentation
7→84) → root-caused to per-cell primitives with no spatial coherence →
rewrote `fractalize_edge` (frontier moved by smooth along-coast noise) and
`scatter` (grows coherent patches) → `v3` converged (fragmentation back to 18;
clean depth-ramp coast, cave chamber in the massif, wash + hill + fertile
hollow + ruin). Plans live at `../player_maps/coastal_mesa_plan_v{1,2,3}.json`;
outputs at `../player_maps/coastal_mesa*_loop_*`.

---

## Savegame_ideoligions.py — .rws ideoligion (religion) reader

**Goal:** read every IDEOLIGION defined in a save and surface its full flavor —
name / adjective / member-name, leader titles, the generated origin-myth
description, memes, deities, roles, rituals (with their expected-desc blurbs),
relics, sacred buildings/weapons, virtues, issue positions, culture and style —
plus how many pawns follow each faith. Third companion to the map + items
probes.

### Run
```bash
python3 Savegame_ideoligions.py <path-to.rws> [--out DIR] [--max-desc N]
```
Pure standard library (ElementTree) — **no Pillow needed.**

Example:
```bash
python3 Savegame_ideoligions.py ../savegame/03_Gravtasm__starting_save.rws
```

### Outputs (next to the save, basename = save stem)
- `<stem>_ideoligions.md` — readable report: a roster table (religion / members
  called / culture / memes / follower count) followed by one detailed section
  per religion.
- `<stem>_ideoligions.json` — full machine-readable dump of every ideo.
- console — the roster summary.

### What it reads (verified against 03_Gravtasm__starting_save.rws, 1.6.4633)
Ideoligions live fully-expanded (not just a def reference) under
`<game><ideoManager><ideos><li>` — each `<li>` is one religion, so the save is a
self-contained authoritative source for the campaign's faiths. Per ideo: `<name>`
/ `<adjective>` / `<memberName>`, `<leaderTitleMale/Female>`, `<description>`
(the procedurally-generated origin myth — full readable prose, unlike item art
tales), `<culture>`, `<iconDef>`/`<colorDef>`, `<memes>` (structural pillars),
`<foundation Class="IdeoFoundation_Deity">` → `<def>`/`<place>`/`<deities>`, and
`<precepts>`. Precepts are grouped by `Class`: `Precept_RoleSingle/RoleMulti`
(roles), `Precept_Ritual` (rituals, with `ritualExpectedDesc` blurb),
`Precept_Building` (sacred buildings), `Precept_Relic`, `Precept_Weapon`,
`Precept_RitualSeat`, `Precept_GravshipLaunch`, `*.Precept_Virtue`, and
Class-less `<li>` = issue positions (slavery / execution / body-mod stances).
Pawn membership is tallied from each pawn's `<ideo>Ideo_<id></ideo>` reference.

**Verified result on the Gravtasm save:** 14 ideoligions extracted; follower
counts resolve (Rules of Acquisition 8, Techno-Fidelism 6, …); deities, roles,
19-ritual lists, sacred buildings/relics and 56 issue positions all render;
full origin-myth descriptions captured verbatim.

### Notes / limits
- Unlike item `taleRef` seeds and terrain shortHashes, ideoligion
  **descriptions are stored as full text** in the save — no live-game
  regeneration needed. This is a legible, safe-to-READ node.
- Two "Holy Council of Liplicker" entries exist (ids 4 & 48) — duplicate/near-
  duplicate ideos are normal when multiple factions were generated from the same
  template; the tool reports both and their (possibly 0) follower counts.
- Follower count = pawns pointing at the ideo, a good proxy for prominence but
  not a faction-membership map (faction↔ideo linkage was not present as a simple
  node in this save).

---

## Savegame_detailed_items.py — .rws item & flavor-text reader

**Goal:** read every ITEM currently in a savegame and surface the
human-interesting flavor — unique names, art tales, quality, material, condition
— plus the free narrative TEXT (scenario intro, letters, messages,
quest/backstory descriptions). Companion to the map-preview probe.

### Run
```bash
python3 Savegame_detailed_items.py <path-to.rws> [--out DIR] \
        [--min-quality Good] [--max-text 4000]
```
Pure standard library (ElementTree) — **no Pillow needed.**

Example:
```bash
python3 Savegame_detailed_items.py ../savegame/03_Gravtasm__starting_save.rws
```

### Outputs (next to the save, basename = save stem)
- `<stem>_items.md` — readable report: summary, uniquely-titled items table
  (with wielder), high-quality items, quality/material breakdowns, top types,
  and all narrative text blocks.
- `<stem>_items.json` — full machine-readable inventory (every item + fields),
  plus `named_items` and `narrative`.
- console — short summary + the uniquely-titled items and who holds them.

### What it reads (verified against 03_Gravtasm__starting_save.rws, 1.6.4633)
An **item** is any XML element with BOTH a `<def>` and an `<id>` child (weapons,
apparel, chunks, plants, filth, buildings, pawns…). Parsed with **ElementTree**
(full file ~0.4s) so each flavor field stays bound to its own item. Per-item
flavor fields (all optional): `<title>` (unique name, e.g. *Ash Raven*,
*The Vulture*), `<quality>` (Awful..Legendary), `<stuff>` (material defName),
`<health>`, `<stackCount>`, `<taleRef><seed>` (procedural-art tale — only the
seed is stored). Held items are linked to their owning pawn by walking up to the
nearest `<name>` node. Narrative text is collected from `<text>` (letters /
messages) and `<description>` (scenario / quest / backstory), each tagged with a
best-effort source-class guess (e.g. `ScenPart_GameStartDialog`,
`StandardLetter`, `Message`).

**Verified result on the Gravtasm save:** 14,752 items / 166 defs; 4
uniquely-titled weapons correctly linked to their wielders; 227 quality-bearing
items; 30 narrative blocks including the debt-scenario intro.

### Notes / limits
- `taleRef` stores only a **seed**, not the rendered art description text — the
  full "story" of an art piece is regenerated in-engine from the seed (so, like
  the terrain shortHash, the readable prose needs the live game). The tool
  reports the seed so it can be cross-referenced later.
- Category tagging is a defName-prefix heuristic (good for triage, not
  authoritative typing); the raw `def` is always kept.

---

## Savegame_mapview.py — .rws map preview (research probe)

**Goal:** confirm we can *read and understand* the in-play map inside a RimWorld
1.6 savegame, and render a quick visual preview from it. Feeds the save-based
world-authoring pipeline (`../save_authoring_pipeline.md`,
`../rimworld_file_lore.md`).

### Run
```bash
python3 Savegame_mapview.py <path-to.rws> [--out DIR] [--scale N] [--no-image]
```
Requires **Pillow** (`pip install Pillow --break-system-packages`).

Example (the reference save):
```bash
python3 Savegame_mapview.py ../savegame/03_Gravtasm__starting_save.rws --scale 4
```

### Outputs (next to the save, basename = save stem)
- `<stem>_preview.png` — terrain (one color per distinct terrain), translucent
  roof overlay, red dots for pawns.
- `<stem>_legend.json` — map size, terrain shortHash legend + cell counts,
  roof stats, thing-type counts, pawn positions.
- console — human-readable summary.

### What it decodes (verified against 03_Gravtasm__starting_save.rws, 1.6.4633)
- Map `<size>` under `<maps>` → `(W, 1, H)` (here 225×225 = 50,625 cells).
- Terrain: `<terrainGrid><topGridDeflate>` = base64 of a **raw DEFLATE** stream
  (`zlib.decompress(data, -15)`) → **W·H little-endian uint16**, one per cell.
- Roofs: `<roofGrid><roofsDeflate>` — same encoding; `0` = no roof.
- Things: `<def>/<id>/<pos>` triples; `<pos>` is `(x, 0, z)`. Origin is
  bottom-left, so the renderer flips z for image rows.

### KNOWN LIMITATION — terrain codes are shortHashes, not names
The uint16 terrain values are RimWorld `ShortHashGiver` hashes (base
`StableStringHash`, then per-DefType collision-adjusted across the **active load
order** at load time). They **cannot be reliably reversed to a defName from save
text alone** — you'd need to replay the exact mod list/load order. The tool:
- colors + counts purely by raw hash (zero assumptions), and
- adds a **tentative** best-effort vanilla-name guess via `StableStringHash`
  (labeled `~Name?`; may be wrong due to collision bumps).

For authoritative terrain/biome names use the **live route** (RimBridgeServer
`get_cell(s)_info`) or build an **offline legend** by loading the campaign's
exact mod set once and dumping every `TerrainDef.shortHash → defName`.
(Same shortHash blocker documented for the biome grid in
`../save_authoring_pipeline.md`.)

### Other sibling grids present (not yet rendered)
`underGridDeflate`, `foundationGridDeflate`, `tempGridDeflate`,
`colorGridDeflate` (inside `<terrainGrid>`); `pollutionGrid`, `gasGrid` exist as
map children. `elevationGrid`/`fertilityGrid` were **not** present in this save.


---

## animal_inventory.py — full animal roster → CSV  (v1.1, 2026-08-10)

**The point:** dump every animal in the modded game to a spreadsheet you can
sort, filter and diff. Built to answer seven jobs at once: (1) find duplicate
biome/animal registrations that crash mods, (2) attribute every animal to its
originating mod, (3) compare stats for renormalization, (4) support bulk
renaming for Star Wars theming, (5) plan biome-association patches, (6) flag
Cherry-Pick candidates, (7) supply shortHash candidates for savegame decoding.

### Why offline, and when to use the live bridge instead

It reads **Defs on disk**. The game does not need to be running and no savegame
is touched. That is deliberate: for *patching* work the file matters more than
the resolved value — you cannot write a `PatchOperation` without knowing which
mod and which xpath to target, and a live dump hides provenance.

> **This is the authoring tool. A live RimBridge dump is the verification tool.**

### Run

```bash
# defaults are already the Windows install paths — no args needed
python animal_inventory.py --out D:\Luke\dev\rimtools\out

# explicit
python animal_inventory.py \
  --config  "...\RimWorld by Ludeon Studios\Config\ModsConfig.xml" \
  --workshop "...\steamapps\workshop\content\294100" \
  --local    "...\steamapps\common\RimWorld\Mods" \
  --data     "...\steamapps\common\RimWorld\Data" \
  --out      .\out
```

⚠️ **Run it natively on Windows.** Measured through the Cowork device bridge the
filesystem does ~210 files/sec, and the scan touches tens of thousands of XML
files — >10 minutes. Natively it is seconds.

### Outputs

| File | One row per | Use |
|---|---|---|
| `animals.csv` | animal (ThingDef with `<race>`) — ~112 cols | the master sheet |
| `animal_attacks.csv` | attack tool | combat detail; animals carry 2–5 attacks |
| `animal_lifestages.csv` | life stage | age thresholds |
| `biome_animals.csv` | (biome, animal) pair, **both directions** | biome planning |
| `conflicts.csv` | pair registered >1× | **the crash class** |
| `patch_watch.csv` | PatchOperation touching animals/biomes | what the scan can't see |

### Column groups in `animals.csv`

`identity` · `temperament` (wildness, trainability, petness, nuzzleMtbHours,
roamMtbDays, nameOnNuzzleChance) · `combat` (predator, manhunter chances,
attackCount/BestPower/BestDPS/Summary, armour, moveSpeed, deathActionWorker) ·
`physiology` · `temperature` (comfy + insulation → effectiveTempMin/Max,
tempRangeC, HEAT_HARDY, COLD_HARDY) · `reproduction` (+ derived
maxLittersPerYear, annualOffspringMax, FAST_BREEDER) · `production` (milk/wool/
egg → RENEWABLE_YIELD) · `ecology` · `performance` (tickerType, compCount) ·
`trade` · `meta`.

Two derived groups encode standing project rules rather than raw fields:
**FAST_BREEDER** (annual offspring ≥ 12) and **RENEWABLE_YIELD** together
implement the "never ranch a herd into a meat/leather/wool printer" guardrail.

### KNOWN LIMITATIONS — measured on the 562-mod stack, 2026-08-10

Structural fields read well; inherited ones do not, because `<ParentName>`
chains are not resolved across mods:

| Field | Coverage |
|---|---|
| moveSpeed / baseBodySize / attacks / marketValue | 90–95 % |
| trainability | 83 % |
| gestationPeriodDays | 57 % |
| wildness | 48 % |
| comfyTempMax | 44 % |
| nuzzleMtbHours | 33 % |

Also invisible: **PatchOperation results** (mitigated by `patch_watch.csv`),
**mod-vs-mod override winners** (flagged in `duplicateDefName`, not resolved),
and **true shortHashes** — `shortHashCandidate` uses RimWorld's
`StableStringHash` but the game resolves collisions across the whole loaded set
per defType, so treat it as a candidate until a live dump confirms it.

⚠️ **Sentinel values.** Some mods use placeholder temperatures (50000 °C, 999,
3500) and some ship Fahrenheit→Celsius artifacts (`37.7778..352.222`). Filter
`effectiveTempMax` above ~200 before drawing conclusions.

Cosmetic bug (v1.1): Core/DLC show `modName = "?"` because Ludeon's About.xml is
not parsed for `<name>`; `packageId` is still correct. Fix by falling back to
packageId in `about_of()`.

### Maintenance — adding a column

1. Simple `<race>` field → append to `RACE_SIMPLE` as `(csvColumn, "race/xpath")`.
2. `statBases` entry → add to `STAT_MAP` as `"StatDefName": "csvColumn"`.
3. Comp-derived → extend `parse_comps()`.
4. Derived/computed → compute in `scan_defs()` after the comp block.
5. **Then add the name to `COLUMNS`** — `DictWriter` uses
   `extrasaction="ignore"`, so a column missing from `COLUMNS` is silently
   dropped. This is the one easy mistake.

Test with the synthetic-tree smoke test rather than the full stack: build two
tiny mods (one animal, one biome) in a temp dir and run against them; the
Armadillo double-registration reproduces in about a second.

### First run — headline results (562 mods, 2026-08-10)

1,168 real animals (+44 abstract bases). **Only 3 conflicts**: `Desert ×
Armadillo` and `AridShrubland × Armadillo` (Beasts of the Rim redefines the
vanilla `Armadillo` *and* `Penguin`, then re-registers Armadillo via
`wildBiomes` into biomes Core already lists it in — this is what kills Choose
Wild Animal Spawns at startup), plus `TropicalSwamp × Titan`, where the Titans
mod registers the same biome twice inside its own file.
