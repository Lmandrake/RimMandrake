# hand_authored_maps/

Study library of **publicly-distributed, hand-authored RimWorld local maps** — real
`.rws` saves / `MapGeneratorBlueprints` that creators sculpted by hand (Map Designer
blockout → Dev Mode hand-editing → distribute). Reference material for authoring the
Kolyska campaign's destination tiles to "Tier C — authored expedition level."

Source census: [`../Utils/rimworld_handcrafted_map_atlas.md`](../Utils/rimworld_handcrafted_map_atlas.md).

## Acquisition status (2026-08-07)

Direct download from this environment is **blocked** — `git`/HTTPS egress to GitHub
returns `403` from the proxy, and the web tools cannot reach the raw archives. So the
actual map files are being acquired through the user's **Fetcher** manual-retrieval
system.

- **Request filed:** `~/GDrive/<work>/dev/Fetcher/Requests/2026-08-07_handcrafted_maps.txt`
- **Results will land in:** `~/GDrive/<work>/dev/Fetcher/Delivery/2026-08-07_handcrafted_maps/`
- Each repo is requested as a zip via GitHub's branch-agnostic zipball endpoint
  (`https://api.github.com/repos/OWNER/REPO/zipball`), which redirects to the repo's
  default branch whether it is `main` or `master`.
- Once delivered, unpack each zip into a named subfolder here (e.g.
  `World_45_In_Memory_of_Rain/`).

**Nothing has been fabricated.** This folder holds only this manifest until the
Fetcher delivery arrives; the map files themselves come from the sources below.

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
