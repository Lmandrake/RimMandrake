<!-- status: transient -->
# port_tail_2026-09-20 — build report

Sheet: `Transient/port_tail_2026-09-20.html`
Decisions (pre-fill): `Transient/port_tail_2026-09-20.decisions.json`
Thumbnails: `Transient/port_tail_thumbs_2026-09-20/` (80 PNGs)

## check_sheet.py

Exit code **0**. 34 ok, 0 WARN, 0 FAIL.

## Rows: 95 total

- 21 — TAIL.json small-donor tail entries not yet asked (22 minus 1 reclassified as dead-mod).
- 60 — UNGUARDED.json entries that resolved to a REAL, active donor mod with no `MayRequire` guard.
- 14 — dead-mod rows (Biomes! Caverns, `biomesteam.biomescaverns`, not in the active 617-mod
  list): 1 from TAIL + 13 from UNGUARDED. Own group, pre-filled `undecided`.

## UNGUARDED triage (the required first job)

79 not-already-asked UNGUARDED rows resolved via the LIVE def dump (`defs.sqlite`, 617 active
mods, captured 2026-09-20T07:47:24Z), never by defName prefix:

- **60 → real active donor** (included, marked with a `guard: MISSING` chip): 52 Alpha Biomes,
  3 Primordial Geysers, 2 Alpha Genes, 1 ReGrowth 2, 1 GRiNDTerra Biomes, 1 Star Wars Animal
  Collection (Continued) — `Plant_TookeTrap_Wild`, a BARE defName with no `SW_`/`mlie` marker;
  a prefix rule would have called this vanilla, which is the exact trap the brief warned about.
- **13 → absent from the live dump entirely** (mod not active) — all `BMT_*`, matching the
  known-dead `biomesteam.biomescaverns` pattern from TAIL.json's own `modActive:false` row.
- **4 → vanilla Core/DLC** — excluded, out of scope: `Plant_Ambrosia` (Core), `Plant_Reeds`,
  `Plant_Fireweed`, `Plant_MagmaCactus` (Odyssey).
- **2 → our own mod** — excluded, out of scope: `RUT_Sytheclaw`, `VAEWaste_Megatardi`
  (`mandrake.rut.patches`) — already ported, not a donor question.

## Pre-fill

95/95 pre-filled (100%). `keep`: 81 (blacklist posture default). `undecided`: 14 (the dead-mod
group only — "restore the mod / port the species / drop the row" is a different question from
a live donor's, so it was not defaulted to keep or retire).

## Thumbnails

80/95 resolved (loose PNG or cached AssetBundle extract, verified non-blank). 15 unresolved,
all with a stated reason, never a guess:
- 14 — the dead-mod rows (mod not active → no def in the live dump → no texPath to resolve).
- 1 — `Visceral` (Horrors, `mlie.horrors`): ships an `AssetBundles/` folder but it isn't in the
  local bundle texture cache (`observed/inventory/bundle_textures/`); would need
  `extract_bundle_textures.py` run against that mod's bundle first.

## CONFIG.invented

Declared in the page (4 items): vanilla/own-mod exclusion, commonality = max per-biome weight
(not a field in the source data), dead-mod group defaults to `undecided` not `keep`, and
default-`keep` applied uniformly regardless of donor size (no auto-`replace` for tiny donors).

## Least-sure rows

- `Visceral` (Horrors) — no thumbnail, so its keep/retire call is being made blind on this page.
- The 60 UNGUARDED rows generally: "no MayRequire" was confirmed by the input file, not
  re-verified per-row against the live patch XML in this pass.
- Alpha Biomes' 55-row group is a size judgement call the owner has to make in one motion; the
  sheet did not attempt to sub-rank which of those 55 matter most beyond spawn commonality.
