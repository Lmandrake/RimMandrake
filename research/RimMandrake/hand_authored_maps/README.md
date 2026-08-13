# hand_authored_maps/

Study library of **publicly-distributed, hand-authored RimWorld local maps** — real
`.rws` saves / `MapGeneratorBlueprints` that creators sculpted by hand (Map Designer
blockout → Dev Mode hand-editing → distribute). Reference material for authoring the
Kolyska campaign's destination tiles to "Tier C — authored expedition level."

Source census: [`../reference/rimworld_handcrafted_map_atlas.md`](../reference/rimworld_handcrafted_map_atlas.md).

## Acquisition status — ✅ COMPLETE (2026-08-07)

Direct download from this environment was **blocked** (`git`/HTTPS egress to GitHub
returned `403` from the proxy), so acquisition was routed through the user's
**Fetcher** manual-retrieval system. Fetcher ran the request and delivered **all 42
directives: 42 worked, 0 failed.**

- **Request:** `~/GDrive/<work>/dev/Fetcher/Requests/2026-08-07_handcrafted_maps.txt`
  (now in `Fetcher/Complete/`)
- **Delivered to:** `~/GDrive/<work>/dev/Fetcher/Delivery/2026-08-07_handcrafted_maps/`
- Each repo was pulled as a zip via GitHub's branch-agnostic zipball endpoint
  (`https://api.github.com/repos/OWNER/REPO/zipball`).
- Each archive was flattened (dropping the `OWNER-REPO-hash/` wrapper) and any nested
  map zip was unpacked so the `.rws` save sits directly in the map's subfolder here.

**Result: 39 of 40 repos yielded genuine RimWorld savegames** (validated as real
`<savegame>` XML with map/terrain data — not screenshots or placeholders). Several
repos bundle multiple saves (World 51 = 3 Darkrest variants; Worlds 29, 52, 60 = 2
each). **SickBoyWi_RimWorldMaps** is the historical blueprint-exporter C# project
(no `.rws`, as expected). The two `FETCH`ed repo-list pages are kept as `*.txt`
backstops in the Delivery folder.

### Game-version caveat (matters for loading vs. studying)

The saves span **RimWorld 1.4 → 1.6**. Only the newest load natively in your 1.6
campaign; older ones are still fully readable for **study and hand-editing** (the map
grid XML is stable across versions), but would need conversion/cleanup to load as a
live save.

- **1.6 (load-native):** World 56 (Kains Swamp), 57 (Ides Veil), 58 (the Dead City),
  59 (Secluded Cove), 60 (Satsuki), 61 (Dragons Fall).
- **1.5:** Worlds 43–55 (incl. the desert **World 45 In Memory of Rain**, 50 Lush
  River, 46 Cervantes Cliffs, 49 The Estuary).
- **1.4:** Worlds 25–42 + both Grapesforlifes maps (incl. desert **World 31 Deserted
  Trader**, arid **World 29 Blood Gulch**, **World 38 Point Sea**).

> Note: several maps carry **mod dependencies** in their `<meta><modIds>` (e.g. World
> 31 lists Map Designer, VFE-Core, Custom Map Sizes). For pure map-geometry study this
> is irrelevant; only matters if you try to load one live.

**Nothing was fabricated** — every file traces to the GitHub sources below via the
logged Fetcher run (`MANIFEST.txt` in the Delivery folder).

## What was requested (priority order)

### Tier 1 — highest value (desert/arid match + atlas §9 shortlist)

Desert/arid geomorphology (matches the campaign world):

| Map | Size | Terrain | Source |
|---|---|---|---|
| **World 45 — In Memory of Rain** | 325×325 | Desert; Slate & Marble | UnknwnBuilds/World_45 |
| **World 31 — Deserted Trader** | 275×275 | Desert; Marble/Granite/Sandstone | UnknwnBuilds/World_31 |
| **World 29 — Blood Gulch** | 250×250 | Arid Shrubland; Granite & Sandstone | UnknwnBuilds/World_29 |
| **World 50 — Lush River** | 250×250 | Arid Shrubland; Granite & Marble | UnknwnBuilds/World_50 |
| **World 38 — Point Sea** | 275×275 | Arid Shrubland; Sandstone & Slate | UnknwnBuilds/World_38 |

Atlas §9 study-first shortlist (storytelling/structure exemplars):

| Map | Why | Source |
|---|---|---|
| **World 61 — Dragons Fall** | landmark-as-geography; "story at a glance" | UnknwnBuilds/World_61 |
| **World 58 — the Dead City** | full authored ruined-city + custom danger nodes | UnknwnBuilds/World_58 |
| **World 57 — Ides Veil** | hand-designed terrain + bespoke ancient danger | UnknwnBuilds/World_57 |
| **World 49 — The Estuary** | explicit procedural-before/hand-after workflow | UnknwnBuilds/World_49 |
| **World 44 — Cathedral** | monumental ruin + catacomb focal point | UnknwnBuilds/World_44 |
| **World 43 — Sacraficial Altar** | authored focal ruin | UnknwnBuilds/World_43----SacraficialAltar |
| **World 42 — Lake Lands** | authored terrain | UnknwnBuilds/World_42---Lake-Lands |
| **World 32 — Ruined Dam** | infrastructure-as-archaeology | UnknwnBuilds/World_32 |
| **Lone Mountain Bay** | independent proof-of-concept for elevation + abandoned-site story | Grapesforlifes/Lone_Mountain_Bay_RW |
| **Yirah Valley** | independent authored valley map | Grapesforlifes/Yirah_Valley_RW |

### Tier 2 — remaining UnknwnBuilds worlds 25–60

Full set for completeness: Worlds 25, 26, 27, 28, 30, 33, 34, 35, 36, 37, 39, 40, 41,
46, 47, 48, 51, 52, 53 (The Tar Pits), 54, 55, 56, 59 (Secluded Cove), 60 (Satsuki).

### Tier 3 — historical tooling

**SickBoyWi/RimWorldMaps** — early save→`MapGeneratorBlueprints` XML exporter; a
predecessor of the modern "author once, reuse elsewhere" workflow. Source-of-interest,
not a map.

## Naming irregularities (verified against the atlas, do not "fix" these)

The GitHub repo slugs are inconsistent — the zipball URLs preserve the exact slug:

- World 28 uses a **hyphen**: `World-28` (all others `World_XX`).
- `World_42---Lake-Lands` (triple hyphen).
- `World_43----SacraficialAltar` (quadruple hyphen; "Sacraficial" is the creator's spelling).

## Not acquirable as files (reference only — see the atlas)

Reddit showcases, YouTube timelapses, Patreon (RWCC) posts, Discord, and Steam
Workshop **tool** pages (Map Designer, Map Preview, Map Edit Tools, Save Maps
Continued, Better Map Sizes, Geological Landforms) are documentation/tools, not
downloadable map files. They stay cited in the atlas.
