# Build report — Lantern Deeps strange-life review sheet (2026-09-20)

Status: DONE. `check_sheet.py` exit 0 (0 FAIL, 0 WARN, 34 ok) against both the
sheet and its pre-fill decisions file.

## Plan
- Sheet: `Transient/lantern_deeps_strange_life_2026-09-20.html`
- Decisions: `Transient/lantern_deeps_strange_life_2026-09-20.decisions.json`
- Thumbs: `Transient/lantern_deeps_strange_life_thumbs_2026-09-20/`
- Rows: crystal-life cast (7, DESIGNED ONLY), lanternstone geology + renamed
  flora (3, BUILT), restyled cave fauna (8, BUILT), false-positive art name
  collisions (3, NOT DEEPS CONTENT).

## Status log
- Read `the_lantern_deeps.md`, `lantern_deeps_flora_names.md`, roster JSON,
  `DEEPS_FAUNA_VERDICTS_1.md`, `DEEPS_FAUNA_MECHANICS_1/2.md`,
  `CAVERNS_PARITY_BUILD_1.md`. Confirmed on disk: RUT_Kindled/RUT_Mindstone
  have zero def hits (only a defensive python poll references RUT_Mindstone
  by name); Creep/Cleavers/Chorus/Shard-mind have zero def or art hits beyond
  the sheet's own prose and ART_JOBS.md's "owed" note.
- Confirmed lanternstone crystal formations (chunk/small/medium/large/huge,
  terrain, wall, sowable, item) are all wired (texPath matches live texture
  files) — BUILT.
- Confirmed crystalcap->ThrakkCap and crystaltipbrambles->OsskBramble renames
  landed in `RUT_DeepFlora.xml` with matching deployed textures — BUILT.
- Confirmed the 8 restyled cave fauna (Drinker/Grabber/Soulchime/Gembug/
  Glowbulb/Megapleura/MossBeetleLarvae/Shatterjaw) are deployed: renamed
  labels + restyled art landed in `infrastructure/artpipe/done/` AND copied
  onto the LIVE SWBestiary texPaths per `DEEPS_FAUNA_VERDICTS_1`'s status
  log; still spawn in `RUT_LanternDeeps.xml`'s `<wildAnimals>` today —
  BUILT. Grabber/Soulchime/Drinker's special ability comps are compiled
  (`DEEPS_FAUNA_MECHANICS_2`) but not yet deployed (DLL locked by the running
  game) — noted on the row, not treated as a separate state.
- 🔴 Found 3 false-positive art matches: `creepstern_v1` (arid_shrubland
  flora `RG_Plant_CreepStern`, unrelated to "The Creep" crystal creature),
  `crystalflower_v1` (poison_forest `AB_CrystalFlower`), `crystalhorn_v1`
  (propane_lakes/blue_desert `AB_CrystalHorn`) — all three confirmed via
  their own manifest `rimflow_item_id`/`style_notes` to belong to
  `ART_REGEN_FLORA_WAVE1_QUEUE_1`, a general flora regen wave for OTHER
  biomes, not Lantern Deeps content. Included as their own group so the
  owner isn't left wondering why "the Creep" has no picture.
- Generated 14 thumbnails (`Transient/lantern_deeps_strange_life_thumbs_2026-09-20/`)
  from the real source PNGs: `infrastructure/artpipe/_artsrc/<id>/<id>.png` for
  every artpipe render, and the live deployed textures for Thrakk Cap / Ossk
  Bramble (post-rename, in `src/RimUtinni/LanternDeeps/Textures/...`). The 7
  crystal-life cast rows and the 2 Kindled-race rows have no thumbnail — there
  is genuinely nothing to show.
- Built sheet + decisions from `sheet_template.html` (chrome untouched, only
  CONFIG/ITEMS filled). `check_sheet.py` exit 0: 34 ok, 0 FAIL, 0 WARN.

## Final row counts by STATE
- BUILT: 11 (lanternstone geology, Thrakk Cap, Ossk Bramble, 8 restyled fauna)
- DESIGNED ONLY: 7 (Lantern, Creep, Cleavers, Chorus, Shard-minds, mindstone, Kindled)
- NOT DEEPS CONTENT (name collision, invented state): 3 (creepstern_v1, crystalflower_v1, crystalhorn_v1)
- Total: 21 rows, 21/21 pre-filled.

## Files written
- `Transient/lantern_deeps_strange_life_2026-09-20.html`
- `Transient/lantern_deeps_strange_life_2026-09-20.decisions.json`
- `Transient/lantern_deeps_strange_life_thumbs_2026-09-20/` (14 PNGs)
- `Transient/lantern_deeps_strange_life_build_20260920.md` (this file)

Nothing else touched: no git commit, no rimflow, no def/design-doc edits, no
deploy, no bridge, no `serve_sheet.py` run (parent serves it).
