# Utils/ — RimWorld campaign scratch utilities

Small Python tools for inspecting/authoring the save-based campaign. Each is a
focused research probe; keep them assembly-free and dependency-light.

| Tool | Reads | Emits |
|---|---|---|
| `Savegame_mapview.py` | in-play map grids (terrain/roof/things) | PNG preview + legend JSON |
| `Savegame_detailed_items.py` | every item + its flavor/narrative text | items MD report + items JSON |
| `Savegame_ideoligions.py` | every ideoligion (religion) + full flavor | ideoligions MD report + JSON |

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
