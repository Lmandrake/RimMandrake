# Alpha Animals port sheet build — 2026-09-20

## Status: DONE — check_sheet.py exit 0 (0 FAIL, 0 WARN, 34 ok)

## Scope
- Input: `Transient/port_sheets_20260920/ALPHAANIMALS.json` (69 rows, all `kind: fauna`)
- 14 rows already asked in the desert sheet (`Transient/desert_family_review_2026-09-20.html`) — EXCLUDED
- 55 rows in scope for this sheet
- `-lisk` clade check against the full 69: none survive (confirmed by grep before build)

## Mod source
- Alpha Animals workshop id 1541721856, packageId `sarg.alphaanimals`
- `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/1541721856`
- v1.6 loadFolders: `/`, `1.6`, plus conditional compat folders (VFEInsectoids2, etc.)
- `VFEI2_BlackSwarmling` is defined inside AA's own conditional
  `1.6/Mods/VFEInsectoids2/Defs` folder (loads only when VFE Insectoids 2 is
  active) — that is why its defName carries a different mod's prefix while its
  packageId resolves to sarg.alphaanimals. Not a resolver error; flagged on its row.

## Progress log
- [x] Extract defName -> texPath for all 55 species from AA's own XML
      (`PawnKindDef` -> last lifeStage -> `bodyGraphicData.texPath`; all 55 resolved)
- [x] Resolve loose PNG thumbnails: 55/55 resolved on the first rung (`_south`) against
      AA's own loose `Textures/` tree (1,649 PNGs indexed); none needed a directory/mask
      fallback. Copied + downscaled (max 200px) to
      `Transient/port_alphaanimals_thumbs_2026-09-20/<defName>.png`; spot-checked 6
      at random, all carry real (non-blank) alpha.
- [x] Pre-fill rule (stated in CONFIG.invented too): explicit Earth-named/Earth-lineage
      -> retire (13 rows); alien + commonality-sum >= 0.4 -> replace (11, incl. 2 manual
      bumps: AA_Nightling clade-anchor, AA_MycoidColossus biome flagship); alien +
      single-biome + commonality < 0.10 -> retire as negligible; everything else -> keep
      (19); 5 rows left undecided/contested on purpose (AA_DuskRat, VFEI2_BlackSwarmling,
      AA_Agaripawn, AA_Helixien, AA_Mime) — see their notes in the decisions file.
- [x] Build ITEMS json (55 rows, grouped by dominant biome) + decisions.json pre-fill
- [x] Build HTML from template — CAUGHT A BUG: the template's own top-of-file comment
      contains literal example `<script id="CONFIG" type="application/json">` text as
      documentation, and a naive first-match regex spliced the real CONFIG/ITEMS JSON
      into THAT comment instead of the real script tags, leaving the shipped page on
      the untouched demo config (check_sheet failed on fold/sticky/CONFIG-not-found —
      all defects of the comment injection, not real chrome gaps). Fixed by splitting
      the template at the end of that leading comment (`-->`) and only pattern-matching
      inside the body past that point.
- [x] check_sheet.py — 0 FAIL, 0 WARN, 34 ok, exit 0
- [x] Did NOT run serve_sheet.py — forbidden by this task's hard rules. Sheet and
      decisions file are written to disk; delivery/serving is left to the coordinator.

## -lisk clade check
Checked the FULL 69-row input (not just the 55 in scope) for Feralisk/Cinderlisk/
Animalisk/Dunealisk/Junglelisk (retired at `7bad94185`). None present. No finding.

## Cross-mod oddity found
`VFEI2_BlackSwarmling` — defName looks like VFE Insectoids 2, but it is genuinely
defined inside Alpha Animals' OWN conditional `1.6/Mods/VFEInsectoids2/Defs` folder
(loads only when VFE Insectoids 2 is also active). Its `mod: sarg.alphaanimals`
attribution in the bounded input is correct, not a resolver error — flagged on its
row and left undecided (cross-mod dependency, not a simple keep/cut).
