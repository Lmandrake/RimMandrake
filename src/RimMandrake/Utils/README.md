# src/RimMandrake/Utils/ — RimWorld campaign scratch utilities

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
| `rimworld_loadset.py` | `ModsConfig.xml` + each mod's `LoadFolders.xml` | — (shared library) the folders the game *actually* loads |
| **`def_inventory.py`** | **every active mod's `Defs/`, all 495 def types** | — (shared library) + per-type JSON: the resolved def set |
| **`animal_live_diff.py`** | **`animals.csv` + a live DefDump** | **`divergence.csv` — what the patches actually did** |
| **`animal_contact_sheet.py`** | **`animals.csv` + every mod's `Textures/`** | **paginated sprite sheets + index CSV + missing CSV** |
| **`deploy_custom_mods.py`** | **`../custom_patches/` + RimWorld's `Mods/`** | **pushes our authored mods into the game — the repo copy is NOT what the game loads; see `../custom_patches/README.md`** |

**Offline vs live.** Everything above reads files. Its counterpart is
`../mods/dev/RimDefDump`, a small C# mod that dumps the def database from inside
the running game, after patches have applied. Offline answers *"what did the
author write, and where do I patch it"*; live answers *"what actually exists at
runtime"*. Neither replaces the other — the value is in diffing them.

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
hollow + ruin). Plans live at `../src/RimMandrake/mapsynth/coastal_mesa_plan_v{1,2,3}.json`;
outputs at `../src/RimMandrake/mapsynth/coastal_mesa*_loop_*`.

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
Map `<size>` under `<maps>` → `(W, 1, H)` (here 225×225 = 50,625 cells), then the
terrain, roof and thing nodes. **The grid encoding and the shortHash→defName rule
are `../skills/rimworld-savegame/SKILL.md` §4–5.**

⚠️ This tool predates that rule and still labels its terrain names `~Name?` as a
tentative guess. Reversal **is** solved (`% 65535`, not a mask); prefer the live
dump's own `shortHash` field, which is ground truth and needs no computation.

### Other sibling grids present (not yet rendered)
`underGridDeflate`, `foundationGridDeflate`, `tempGridDeflate`,
`colorGridDeflate` (inside `<terrainGrid>`); `pollutionGrid`, `gasGrid` exist as
map children. `elevationGrid`/`fertilityGrid` were **not** present in this save.


---

## animal_contact_sheet.py — see the whole roster at once  (v1.0, 2026-08-10)

**The point:** 1,243 animals is far too many to judge from a spreadsheet. This
renders every animal's sprite into paginated contact sheets **in `animals.csv`
order** (which is grouped by mod), so style clashes, joke assets and off-theme
mods are obvious at a glance — the keep / cut / re-skin decision.

```bash
python src/RimMandrake/Utils/animal_contact_sheet.py --out observed/2026-08-13/inventory/contact_sheets
```

Requires **Pillow** (already used by `Savegame_mapview.py`). Runs in ~5s.

Committed output lives in `observed/2026-08-13/inventory/contact_sheets/` — 6 pages, 9.9 MB.
It is regenerable in seconds, so delete rather than curate it if the repo size
ever matters.

### Where animal art actually lives (this is not obvious)

Sprites come from **`PawnKindDef.lifeStages[].bodyGraphicData.texPath`**, NOT
`ThingDef.graphicData` — which is `null` for every animal. So the tool joins
ThingDef → PawnKindDef (via the pawnkind's `<race>`) → the **last** life stage,
because the first is the juvenile form and nobody wants a contact sheet of
calves.

It reads pawnkinds from the inheritance-**resolved** element, unlike
`animal_inventory.py`: many modded pawnkinds declare only `defName`/`race` and
inherit the entire `lifeStages` block, so pre-inheritance they have no texture
at all.

Textures are indexed across each mod's loaded content dirs **and** root, in load
order, last-writer-wins. That override rule demonstrably fires: `AA_Gallatross`
resolves to *Alpha Animals Retextured*, not Alpha Animals.

### KNOWN LIMITATION — ~40% of the roster has no previewable art

**737 of 1,243 animals render.** This is expected and not a bug:

| Reason | Count |
|---|---|
| `no_loose_png` — art packed in a Unity asset bundle | 446 |
| `no_defName` — abstract base rows, nothing to draw | 47 |
| `no_pawnkind` / `no_texPath` / `blank_png` | 14 |

**Vanilla and DLC art is not on disk as PNGs** — `Data/Core` has no `Textures/`
folder at all. Several large mods bundle theirs too: Star Wars Animal Collection
ships exactly **one** loose PNG despite 160 animals, and Jurassic Rimworld has no
`Textures/` directory whatsoever. Extracting Unity bundles would need another
dependency and is deliberately out of scope.

`animal_textures_missing.csv` is therefore a deliverable in its own right:
grouped by mod, it is the list of **which mods bundle their art**.

### Layout choices worth knowing

- **Packed-earth background** (`--bg earth`, the default) with a soft ground
  shadow under each sprite. The brown sits in the same mid-luminance band a
  checkerboard did, which is the point: Alpha Animals ships near-black
  silhouettes and arctic mods ship near-white ones, and both have to stay
  readable against the same backdrop. The texture is **generated**, not sampled
  — vanilla terrain art is packed in Unity bundles and is not on disk (same
  reason 40% of the animals cannot be previewed), so there was nothing to copy.
  Three octaves of value noise plus scattered pebbles, built once per run and
  reused for every cell.
  The shadow earns its place: a mottled ground is busier than a flat
  checkerboard, so sprite edges lose separation without one. It is derived from
  each sprite's own alpha, so it follows the real silhouette.
  `--bg checker` restores the old look, `--flat-bg RRGGBB` forces a flat colour,
  `--no-shadow` drops the shadow.
- **Sprites are trimmed to their alpha bbox by default**, which is a big
  legibility win but destroys relative scale — a chinchilla and a thrumbo fill
  the same cell. Use `--no-trim` when comparing sizes.
- Upscale is capped at 2× with NEAREST, so a small cell honestly means a small
  art asset rather than a blurry enlargement.
- Duplicate defNames are **not** deduped: a doubled cell means two mods claim
  that animal, which is a finding rather than noise. `duplicateDefName` is
  carried into the index CSV.

---

## def_inventory.py — the generic offline extractor  (v1.0, 2026-08-10)

**Layer 1 of three.** Resolves the load set, scans every def XML once, and
resolves `<ParentName>` inheritance for **all 495 def types** — not just
animals. Everything else offline is built on this.

The three layers, and why they are separate:

| Layer | Module | Job |
|---|---|---|
| 1 extraction | `def_inventory.py` | load set + inheritance, category-agnostic |
| 2 projection | `animal_inventory.py` (+ future weapons/apparel) | curation: which columns, which derived flags |
| 3 diff | `animal_live_diff.py` | offline vs live |

The split exists because the *machinery* is generic but the *curation* is not.
`FAST_BREEDER`, `RENEWABLE_YIELD` and `HEAT_HARDY` encode standing project rules,
not facts about RimWorld; dissolving them into a generic field dump would lose
the judgment. Equally, a projection must never redo inheritance — layer 1 hands
it a resolved element and that is the whole interface.

```python
from def_inventory import build
ds = build(config, workshop, local, data)   # ~4 s, 51,408 defs, 495 types
for rec in ds.of_type("ThingDef"):
    rec.element      # inheritance-RESOLVED element  <- what projections read
    rec.own          # raw declaration as written    <- for own-vs-inherited diffs
```

`DefRecord` also carries `defType`, `defName`, `abstractName`, `parentName`,
`modName`, `packageId`, `loadOrder`, `sourceFile`, `inheritDepth`,
`inheritChain`, `unresolvedParent`, `duplicateOwners`, `shortHashCandidate`.

```bash
python src/RimMandrake/Utils/def_inventory.py --summary                    # per-type census
python src/RimMandrake/Utils/def_inventory.py --out DIR                    # defs/<Type>.json + manifest
python src/RimMandrake/Utils/def_inventory.py --out DIR --types ThingDef   # fast iteration
```

**Merging is lazy.** Chain *walking* is eager (so `inheritDepth` / `inheritChain`
/ `unresolvedParent` are always populated and `--summary` is cheap); the
deepcopy-merge happens on first `.element` access and is cached. A projection
only pays for the defs it touches — so if a caller suddenly gets much slower, it
is probably forcing merges it does not need.

**Scale:** 51,408 defs / 495 types / 8,293 files in ~4 s in-memory; a full
`--out` dump is **90.6 MB in ~11 s**. Do not commit the raw dump — commit the
projections. (8,294 files exist on disk; one, ReGrowth's `GreaterSwamps.xml`, is
malformed XML that RimWorld also rejects.)

**`loadOrder` is 1-based**, matching `rimworld_loadset` and `animals.csv`.
`RimDefDump` was changed to match, so live and offline join without an
off-by-one.

### Known: 128 defs with an unresolvable parent

Not a bug, and worth understanding before it alarms you again — it split into
two causes, neither of which is a broken game:

- **68** are Stonecutting Extended recipes carrying
  `MayRequire="Kura.ExtraStone"` for a mod that is **not active**. The game skips
  them entirely. We do not evaluate `MayRequire` — a documented limitation
  behaving exactly as documented.
- **28** were Adaptive Storage dependants, and those were a **real bug in
  `rimworld_loadset.py`**, now fixed: without a `LoadFolders.xml` the resolver
  returned `<mod>/<version>` *or* the mod root, never both. RimWorld loads both.
  35 active mods ship a root `Defs/` alongside a version folder — 667 def nodes
  and 24 PatchOperations were invisible. Full write-up in the skill's
  `traps.md`.
- The remainder are small clusters, several of them parents that a
  `PatchOperation` creates at load time — genuinely invisible offline.

Contested `(defType, defName)` keys stack-wide: **375**. See
`vendor/wisdom/def_override_clusters.md`.

---

## animal_live_diff.py — offline vs live  (v1.0, 2026-08-10)

**The point:** `animal_inventory.py` knows *where to patch*; `RimDefDump` knows
*what resulted*. This is the join, and the join is the deliverable — it turns
"I think this xpath hits the right thing" into a verified statement.

```bash
python src/RimMandrake/Utils/animal_live_diff.py --live "%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump" --out .\out
python src/RimMandrake/Utils/animal_live_diff.py --selftest      # no game load needed
```

It retires three documented limitations of the offline scan at once:

| Offline limitation | How the diff settles it |
|---|---|
| PatchOperation results invisible | field deltas on matched defs — literally the list of what patches changed |
| override winners flagged, not resolved | `modMatch=NO` rows name both claimants |
| `shortHashCandidate` is a guess | `hashMatch=NO` counts exactly how often the guess was wrong |

**Reading `status`:** `both` (check the deltas) · `live_only` (patch-created, or
a def whose `<race>` is purely inherited — the offline tool selects animals on
the def's *own* `<race>`) · `offline_only` (patch-removed, lost to an override,
or `MayRequire`-gated, which the offline scan does not evaluate). None of these
is automatically a bug; they are the list of things worth explaining.

Comparison is deliberately lenient in three ways, or the noise would bury the
signal: floats compared to a relative tolerance, booleans normalised across
`True`/`true`/`1`, and an **empty offline value counts as "no opinion"** rather
than a disagreement.

**Verified by self-test, not by a real dump yet.** `--selftest` builds a
synthetic dump in the exact shape `RimDefDump` emits and asserts all 19
classifications (both/live_only/offline_only, delta detection, hash and mod
mismatches, the leniency rules, biome-pair diffs). The first real run is still
pending a game load.

---

## animal_inventory.py — full animal roster → CSV  (v1.4, 2026-08-10)

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

`identity` · `inheritance` (inheritDepth, inheritChain, inheritedFields,
unresolvedParent — added v1.3; `inheritedFields` names exactly which columns
came from a parent rather than the def itself) · `temperament` (wildness, trainability, petness, nuzzleMtbHours,
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

### KNOWN LIMITATIONS — measured on the 562-mod stack, 2026-08-10 (v1.4)

`<ParentName>` inheritance **is resolved** as of v1.3, cross-mod, using
RimWorld's own merge semantics. Coverage after v1.3 + v1.4:

| Field | Coverage | Note |
|---|---|---|
| mass / tickerType | 100 % | 0.6 % / 1 % before inheritance |
| bloodDef / thinkTreeMain / hasGenders / toxicResistance | 98–99.7 % | all under 11 % before |
| moveSpeed / lifeExpectancy / comfyTempMin / baseBodySize | 97–98 % | |
| trainability | 91.7 % | |
| wildness | 89.1 % | was **0 %** — dead xpath, not inheritance (v1.4) |
| gestationPeriodDays | 58.2 % | genuinely absent on many defs |
| comfyTempMax | 56.6 % | |
| deathActionWorker | 6.2 % | was 0 % — dead xpath (v1.4); matches the 77 defs that declare one |

Still approximate: duplicate abstract `Name`s across mods (last-in-load-order
wins here, the game's winner may differ), **`MayRequire` gating is not
evaluated** on inherited list nodes (so an inherited `comps` list can contain
Anomaly-gated entries a real load would drop — this matters more now that
inheritance works), and **PawnKindDef inheritance is not resolved**, so
`combatPower` / `ecoSystemWeight` / `wildGroupSize*` / `canArriveManhunter`
still read own-XML only.

Still invisible: **PatchOperation results** (mitigated by `patch_watch.csv`),
**mod-vs-mod override winners** (flagged in `duplicateDefName`, not resolved),
and **true shortHashes** — `shortHashCandidate` uses RimWorld's
`StableStringHash` but the game resolves collisions across the whole loaded set
per defType, so treat it as a candidate until a live dump confirms it. All three
are what `src/RimMandrake/RimDefDump` exists to settle.

⚠️ **Dead-xpath trap (the v1.4 lesson).** Four columns were reading fields
RimWorld 1.6 no longer uses, which made them look like inheritance failures:
`wildness` became a StatDef; `deathActionWorker` moved to `race/deathAction`
(as a `workerClass` child on 63 defs, a `Class` attribute on 14 — reading only
the attribute silently loses Boomalope and every explode-on-death animal);
`nameOnNuzzleChance` no longer exists; `Insulation_Cold/Heat` are apparel-only,
so `effectiveTemp*` always equals `comfyTemp*`. **Treat a 0 % column as a
suspected dead xpath, not an empty field.**

⚠️ **Sentinel values.** Some mods use placeholder temperatures (50000 °C, 999,
3500) and some ship Fahrenheit→Celsius artifacts (`37.7778..352.222`). Filter
`effectiveTempMax` above ~200 before drawing conclusions.

✅ **Fixed in v1.2:** Core/DLC used to show `modName = "?"`; the About name now
falls back to the folder name.

⚠️ **v1.1 output was wrong by ~7% and should not be reused.** It resolved mod
folders with a hardcoded `("1.6","1.5","Common","")` list and never read
`LoadFolders.xml`, so it invented 24 animals the game never loads and missed 61
it does. v1.2 delegates folder resolution to `rimworld_loadset.py`. Full
breakdown in `observed/2026-08-13/inventory/README.md`.

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

### Headline results (562 mods, 2026-08-10, **v1.4**)

**1,243 rows / 1,197 distinct defNames** (the 46-row gap is mods redefining each
other; see the `duplicateDefName` column) across 115 columns. 67 biomes,
**3,614** attacks, **3,345** life stages, 4,618 (biome, animal) pairs, 1,873
animal/biome PatchOperations, 3 conflicts. Runs in seconds. Committed output
lives in `observed/2026-08-13/inventory/`, whose README carries the full v1.3/v1.4 breakdown.

Attacks and life stages grew (from 3,353 and 3,169) because inherited `tools`
and `lifeStageAges` now resolve. `unresolvedParent` is empty for all 1,243 rows,
and `inheritDepth` runs 0–5 with the bulk at 2.

_v1.1 reported 1,168 real animals (+44 abstract bases)._ **Only 3 conflicts**: `Desert ×
Armadillo` and `AridShrubland × Armadillo` (Beasts of the Rim redefines the
vanilla `Armadillo` *and* `Penguin`, then re-registers Armadillo via
`wildBiomes` into biomes Core already lists it in — this is what kills Choose
Wild Animal Spawns at startup), plus `TropicalSwamp × Titan`, where the Titans
mod registers the same biome twice inside its own file.
