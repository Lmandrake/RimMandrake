# Biome Work Triage Sweep — 2026-09-20

Read-only triage. Game up on 15-mod test tier held by another window — bridge/game-up UNAVAILABLE.

## Method
- Scanned infrastructure/state/items/*.md for biome items (Lantern Deeps, deserts, Pyrelands, The Rot, Greentide, Cracked Lands, Miasma, Webwork, Weeping Stones, Scarlands, Contagion, Fever Wood, The Forge, Umbra, Slime, Sump, Blue Desert, Arid Shrubland, Wasteland, Forsaken Crags)
- For each: `rimflow show`, read item prose, spot-check code/ledger where prose makes claims

## Rows

Format: ID — state — needs — actionable-now(no game/bridge)? — next action — evidence grade

### Pyrelands
- PYRELANDS_WRONG_BIOME_DEF_1 — doing — offline — YES — owner already RULED 2026-09-20: don't repoint, content stays on RM_FE_Pyrelands (0 tiles now by design, repaint carries it later). Still owed and SMALL: `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml` hits RM_FE_Pyrelands 6x + ZBiome_Grasslands 1x (fix the stray line); `AshStorms_Pyrelands.xml` hits only ZBiome_Grasslands (repoint/duplicate onto RM_FE_Pyrelands too). C# layer already biome-aware of both, fine. — CONFIRMED (read full item file)

### The Rot
- ROT_ROSTER_DEAD_DONOR_NAMES_1 — proposed — offline — YES — 17 BMT_ fauna names in the_rot.json roster point at a donor mod (Biomes! Caverns) not in the active 621-mod list; re-rule each (port to our own def, or drop) rather than wire as-is — CONFIRMED state/needs, item prose read partially
- ROT_SIZE_REJUDGE_APPLY_1 — doing — offline — YES — apply the owner's 11 re-judged Rot flora sizes (fixed a generator bug that undersized AlphaBiomes rows up to 6x); in progress, continuable — CONFIRMED state, prose partially read

### Biome-wide hygiene (cross-cutting, not one biome)
- DEAD_BIOME_DEFS_IN_PROSE_1 — proposed — offline — YES — small doc-correction: 3 known instances of pre-repaint donor biome defNames still embedded in item/design prose where a number/plot fact depends on them; find+fix — CONFIRMED
- BIOME_ROSTER_DEAD_SPECIES_REFS_1 — proposed — offline — YES — 23 species rows across 5 live biome defs (incl. 7 droids/desert, BMT_GiantLeaf in Greentide) name mods NOT in the active list; MayRequire-guarded so no crash, but never spawn — re-rule/fix per row — CONFIRMED

### Deserts (RUT_Desert / RUT_ExtremeDesert / RUT_BlueDesert)
- DESERT_FAMILY_PORT_EXECUTION_1 — proposed — offline — YES (huge scope) — owner ruled ALL 109 desert-sheet species REPLACE with our own defs+art; ~99 donor + 6 vanilla to re-author (4 already ours). This supersedes DESERT_FAMILY_VERDICT_PASS_1. Very large multi-day build, but startable now, offline — CONFIRMED
- DESERT_SHADE_PLANTS_DESIGN_1 — proposed — offline — YES — design pass for 2-3 "defending" desert shade plants (thorn/contact damage), no native CompProperties to reuse; small, self-contained design doc — CONFIRMED
- BLUE_DESERT_LIFE_AUTHORING_1 — proposed — offline — YES — RUT_BlueDesert (1029 tiles) has ZERO fauna/flora though owner-ratified hydrocarbon biology (Swallowers/Burners/Pickers + transparent fractal flora) was specced and never built — CONFIRMED
- EXTREME_DESERT_SIGNATURE_FLORA_1 — doing — offline — YES but UNCERTAIN progress — author glass-nub light-pipe + "ollim" (silverbole) flora; rimflow itself flags: a commit (ef3bca1a) cites this item but never touched the item file, so prose may be stale — check `git log --grep` before assuming unstarted — UNCERTAIN
- DESERT_WRAPS_ART_COMMISSION_1 — doing — offline — YES — original desert-wrap apparel art (full body-type matrix) + devolved head shape; art-pipeline work, in progress — CONFIRMED
- DESERT_STAGGERSEED_BUILD_1 — proposed — **owner** — NO — needs the owner to name the plant before building (ultracactus already named, this one isn't) — CONFIRMED, BLOCKED on owner

### The Slime
- TITANOSLIME_SLIME_BIOME_1 — doing — offline — YES — fresh owner ask (2026-09-20): a Titanoslime apex, devour-whole + grows-as-it-eats; design spec already started this session (see recent commits dd1adf4f6/f738b745a) — CONFIRMED, actively being worked THIS session
- SLIME_GENE_ARCHIVE_BUILD_1 — proposed — offline — YES (large) — owner-ACCEPTED 33-target/25-rider gene lists (frozen 2026-09-06) are still design-only; 1 of 34 GeneDefs built, a 17-gene placeholder archive ships instead — headline mechanic of the biome is fake in-game — CONFIRMED

### Sarlacc (Weeping Stones region)
- SARLACC_HABITAT_BUILD_1 — ready/BLOCKED — offline (partially) — PARTIAL — creature/mechanics already built+pushed; owed: pocket-map dungeon interior (not built anywhere — offline XML/levelgen work, doable now), real art (offline), DBH water wiring; but "live verify" and world placement need bridge/game — MIXED, CONFIRMED via item header

### Large in-progress C# mechanics kits (all "doing", all offline-continuable right now)
- FEVER_WOOD_MECHANICS_1 — doing — offline — YES — Tenant aquifer entity, marsh terrain, pool-state, mirror-break events
- FORGE_MECHANICS_1 — doing — offline — YES — boiling-rain weather, beldon/tibanna, vapor flight layer, foundry dungeon shell, Contagion die-off ring, geothermal industry
- MIASMA_MECHANICS_1 — doing — offline — YES — surge/salt-line system, boon tables, miasma weather, warden-mother placement
- SUMP_MECHANICS_1 — doing — offline — YES — tar moat+ignition, dig-lottery tables, tar beast set-pieces, wick-garden
- SCARLANDS_MECHANICS_2 — doing — offline — YES — Scarlands mark hediff, plated-grazer scaria onset, Sentinel defend-AI, pre-sprung dressing
- GREENTIDE_MECHANICS_2 — doing — offline — YES — wet-bulb/gear, dry-air blower, Roil/Breaklight weather, tree-fall, Lunger, Greatbole
- SCALD_MECHANICS_1 — doing — offline — YES — steam-catch industry, fishing/bath rec, set-pieces, geyser fields
- RUST_CATHEDRAL_MECHANICS_1 — doing — **bridge** — NO — hum-mood system needs live tuning/bridge work — BLOCKED
- BIOME_KITS_PUSH_TO_TEST_1 — doing — offline — umbrella tracker only, no standalone action

All eight above CONFIRMED via `rimflow show` + item header (spec sections read); none show a stale-prose warning except EXTREME_DESERT_SIGNATURE_FLORA_1 above.

### Blocked-only (bridge/game-up/owner) — not actionable now
- DEEPS_FAUNA_MECHANICS_1 — needs bridge (creature ability tuning needs live test)
- BIOME_ENRICHMENT_DESERT_WASTELAND_1 — needs bridge (in-game placement)
- BIOME_WORLD_SWITCH_WAVE_1 — needs bridge (world tile repaint via jawa/world_* tools)
- DESERT_FAMILY_VERDICT_PASS_1 — superseded by DESERT_FAMILY_PORT_EXECUTION_1, needs owner (moot)

### No live item found (checked, none exist)
Umbra, Contagion, Webwork, Weeping Stones (bare), Cracked Lands, Forsaken Crags — no dedicated biome-conversion item in the live set as of this sweep (grep across items/*.md for each name, case-insensitive, only generic/unrelated hits).

## Shortlist (final) — best first, no game/no bridge required
1. PYRELANDS_WRONG_BIOME_DEF_1 — small, clear, already ruled what to do
2. DEAD_BIOME_DEFS_IN_PROSE_1 — small doc fix
3. BIOME_ROSTER_DEAD_SPECIES_REFS_1 — bounded fix, 23 rows
4. ROT_ROSTER_DEAD_DONOR_NAMES_1 — bounded re-ruling, 17 names
5. ROT_SIZE_REJUDGE_APPLY_1 — already in progress, finish it
6. DESERT_SHADE_PLANTS_DESIGN_1 — small design pass
7. TITANOSLIME_SLIME_BIOME_1 — design continuing this session
8. Any of the 7 biome C# mechanics kits (Fever Wood/Forge/Miasma/Sump/Scarlands/Greentide/Scald) — all "doing", all offline, all large
9. BLUE_DESERT_LIFE_AUTHORING_1 / SLIME_GENE_ARCHIVE_BUILD_1 / DESERT_FAMILY_PORT_EXECUTION_1 — large builds, offline, startable now

Blocked: DEEPS_FAUNA_MECHANICS_1, RUST_CATHEDRAL_MECHANICS_1, BIOME_ENRICHMENT_DESERT_WASTELAND_1, BIOME_WORLD_SWITCH_WAVE_1 all need bridge (game up on wrong tier); DESERT_STAGGERSEED_BUILD_1 needs owner (a name).

