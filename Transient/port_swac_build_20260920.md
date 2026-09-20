# SWAC port review sheet — build report (2026-09-20)

## What this is
Keep/retire/replace review sheet for the 36 of 102 `mlie.starwarsanimalcollection` rows
NOT already covered by the desert sheet (`alreadyAskedInDesertSheet: false` in
`Transient/port_sheets_20260920/SWAC.json`). The other 66 rows are in the desert sheet
already in the owner's hand — asking twice is the defect this split avoids.

## Outputs
- `Transient/port_swac_2026-09-20.html` — the sheet (36 rows)
- `Transient/port_swac_2026-09-20.decisions.json` — pre-filled decisions, posture `blacklist`
- `Transient/port_swac_thumbs_2026-09-20/` — 36 PNG thumbnails, one per row, keyed by defName

## check_sheet.py
Exit 0. 0 FAIL, 0 WARN, 34 ok. Thumbnails: 36/36 resolve on disk.

## Thumbnail resolution
All 36/36 resolved from `observed/inventory/bundle_textures/mlie.starwarsanimalcollection/`
(SWAC ships AssetBundle-only, no loose PNGs — matched per the
`reading-rimworld-graphics` skill). Fauna: `swanimals/<lowercase defName>/<name>_south.png`
(gendered species Mott and PekoPeko used the `_f_south.png` variant). Flora: 5 rows are
`Graphic_Random` plants with no facing — used the lettered `a` variant from
`swplants/<stem>/`. No fallback or cross-source matching was needed; every folder name
matched the defName directly.

## Canon flag
Checked against `design/RimStarWars/canon_references/` (137-entry library, covers
creatures/species/droids only, not flora):
- **16 RULED** — owner already picked a specific reference image (2026-09-13/14 review
  sheet): Beldon, Boma, Borcatu, CanCell, Dalgo, Dewback, Dianoga, Dragonsnake, Fanback,
  Hawkbat, Kinrath, PekoPeko, Shiro, Vornskyr, Wyyyschokk, Zakkeg.
- **3 unreviewed** — entry exists, owner hasn't ruled a visual yet: Dactillion, Fambaa,
  Ollopom.
- **17 not in library** — 12 fauna (Neebray, Yobshrimp, ShiroTrap, Snoruuk, Gelagrub,
  Klorslug, Mott, Gornt, LavaFlea, Hssiss, Woolamander, Lylek) + all 5 flora. Absence is
  NOT treated as "not canon" — each of those rows carries a note naming what I know about
  the creature from general SW knowledge (mostly KOTOR-era Legends material), flagged as my
  own judgment, not library-sourced.

## Pre-fill split (36 rows)
`replace` 26 · `undecided` 7 · `retire` 3 · `keep` 0

Zero `keep` prefills is intentional, not an oversight — the owner's ruling driving this
whole pass is "move everything to our own thing defs," so nothing scored as "leave on the
donor forever." `undecided` still counts as posture-"in" (stays on the donor for now) until
he rules it.

## CONFIG.invented (stated in the page)
1. The footprint thresholds (>=0.6/0.25-0.6/<0.25 for fauna, >=1.0/0.5-1.0/<0.5 for flora)
   that turn a continuous commonality number into replace/undecided/retire bands — my cutoffs,
   not the owner's.
2. Calling the 12 uncatalogued fauna "real Star Wars creatures, just uncatalogued" rather than
   "not canon" — sourced from my own general knowledge, not the design library.
3. Treating ShiroTrap as inheriting Shiro's RULED canon status as an ambush variant of the
   same creature — nobody confirmed that relationship.

## Rows I'm least sure of
- **Snoruuk, Klorslug, Mott, Gornt, LavaFlea** (all `undecided`, footprint 0.25–0.5, not in
  the canon library) — real named SW background creatures, but I can't tell from here whether
  they're worth the art budget. Genuinely contested.
- **ShiroTrap** — decision rides on an inherited-identity guess (see invented #3).
- **Hssiss, Woolamander** — prefilled `retire` on footprint alone (0.18, 0.15) despite being
  reasonably well-known Legends creatures; footprint said cut, canon-recognizability argues
  the other way.

## What I did NOT do
No git commit, no rimflow, no deploy, no bridge, no serve_sheet.py (parent serves). Only new
files under `Transient/`.
