# Biome-standalone-mod program — status, 2026-09-23

Source of rows: `design/RimMandrake/biome_mod_architecture.md` §2 (23 standalone mods, table
2a; the `TerminalBiomes` row there also absorbs the two 2b kit rows — Scald/PropaneLake/
TwilightSea/GreySea are one target mod folder) plus the `LanternDeeps` injection layer (§2c).
24 rows: one per distinct target mod folder, ordered by the spec's row number.

## Instruments (one line per column)

1. `mod` — target folder name, read from spec §2 table, column "target mod folder".
2. `folder` — `test -e src/RimMandrake/<Mod>/About/About.xml` (existence of the manifest file,
   not the bare directory).
3. `packageId` — parsed from that About.xml with `xml.etree`; compared to spec's packageId column.
4. `defs` — count of `<BiomeDef>` elements across `src/RimMandrake/<Mod>/Defs/**/*.xml`, parsed
   with `xml.etree` (never grep); `—` if no folder.
5. `build item` — id matching `<MOD>_RM_MOD_BUILD_*` or `*_STANDALONE_MOD_*` under
   `infrastructure/state/items/*.md` (live) or `infrastructure/state/items/closed/` (closed);
   state line quoted from `python3 src/RimMandrake/rimflow/cli.py show <id>`.
6. `design` — sheet file(s) named in spec §2, checked with `find design -name '<sheet>'`; kit
   spec checked the same way under `design/**/kits/`.
7. `deployed` — `test -e "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/<Mod>/About/About.xml"`.
8. `active` — packageId (lower-cased) membership in `ModsConfig.xml`'s `<activeMods>`, parsed
   with `xml.etree` (never grep -c — CLAUDE.md names this trap explicitly).
9. `blocker` — ≤12 words, only from the build item's own prose (headings like blocked/needs/
   owed) or spec §7 rulings; else `—`.

**Active-mod count (ModsConfig.xml, live parse, `find("activeMods")`, never grep):** **620**

## Status table

`folder`/`defs` measured against `src/RimMandrake/<Mod>/`. `deployed` measured against
`/mnt/c/.../RimWorld/Mods/<Mod>/About/About.xml` (mod-folder name, not packageId — a
packageId can be deployed under a differently-named folder; none found here). `active`
measured by packageId membership in the live `ModsConfig.xml` (620 entries); `—` means no
packageId exists yet to check (folder MISSING), not UNMEASURED.

| # | mod | folder | packageId | defs | build item | design | deployed | active | blocker |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Stillsand | MISSING | — | — | STILLSAND_RM_MOD_BUILD_1 (proposed) | EXISTS (dune_sea.md + deep_desert.md) | NO | — | — |
| 2 | LongShade | MISSING | — | — | LONGSHADE_RM_MOD_BUILD_1 (proposed) | EXISTS (desert.md) | NO | — | — |
| 3 | TheRot | MISSING | — | — | THEROT_RM_MOD_BUILD_1 (proposed) | EXISTS (the_rot.md + kits/rot_kit_spec.md) | NO | — | — |
| 4 | Wasteland | MISSING | — | — | WASTELAND_RM_MOD_BUILD_1 (proposed) | EXISTS (wasteland.md) | NO | — | — |
| 5 | NightsideIce | MISSING | — | — | NIGHTSIDEICE_RM_MOD_BUILD_1 (proposed) | EXISTS (nightside_ice.md) | NO | — | — |
| 6 | ForsakenCrags | MISSING | — | — | FORSAKENCRAGS_RM_MOD_BUILD_1 (proposed) | EXISTS (forsaken_crags.md) | NO | — | — |
| 7 | BlueDesert | MISSING | — | — | BLUEDESERT_RM_MOD_BUILD_1 (proposed) | EXISTS (the_blue_desert.md) | NO | — | — |
| 8 | FloodedCanyon | EXISTS | mandrake.rm.floodedcanyon (MATCH) | 1 | FLOODEDCANYON_RM_MOD_BUILD_1 (done, closed) | EXISTS (the_cracked_lands.md) | YES | NO | deployed but not in activeMods — matches `OUR_MODS_DEPLOYED_NEVER_ACTIVATED_1` pattern |
| 9 | LeaningScrub | MISSING | — | — | LEANINGSCRUB_RM_MOD_BUILD_1 (proposed) | EXISTS (arid_shrubland.md) | NO | — | — |
| 10 | PoisonForest | MISSING | — | — | POISONFOREST_RM_MOD_BUILD_1 (proposed) | EXISTS (poison_forest.md) | NO | — | — |
| 11 | TerminalBiomes | MISSING | — | — | TERMINALBIOMES_RM_MOD_BUILD_1 (proposed) | EXISTS (the_scald.md, kits/scald_kit_spec.md, the_propane_lakes.md, terminator_sea.md, the_twilight_deep.md, the_grey_deep.md) | NO | — | 4 biomes/1 mod, 4 toggles (§7 Q1); `RUT_Umbra` is a region, excluded |
| 12 | RustCathedral | MISSING | — | — | RUSTCATHEDRAL_RM_MOD_BUILD_1 (proposed) | EXISTS (the_rust_cathedral.md, kits/rust_cathedral_kit_spec.md) | NO (only legacy `RustCathedralHum`/`Roaches`/`Walls` deployed) | — | absorbs 3 legacy `mandrake.rut.rustcathedral*` mods, not yet merged |
| 13 | Greentide | EXISTS | mandrake.rm.greentide (MATCH) | 1 | GREENTIDE_RM_MOD_BUILD_1 (proposed) | EXISTS (the_greentide.md, kits/greentide_kit_spec.md) | YES | YES | step 5 (Desktop load-test) + step 6 (commit/push) remain |
| 14 | WeepingStones | MISSING | — | — | WEEPINGSTONES_RM_MOD_BUILD_1 (proposed) | EXISTS (weeping_stones.md) | NO | — | — |
| 15 | Pyrelands | EXISTS | mandrake.rm.pyrelands (MATCH) | 1 | PYRELANDS_RM_MOD_BUILD_1 (proposed) | EXISTS (the_pyrelands.md) | YES | YES | built NOT deployed trap noted in item (84d42c63b) — deploy already reflects rename, re-check before testing |
| 16 | Contagion | MISSING | — | — | CONTAGION_RM_MOD_BUILD_1 (proposed) | EXISTS (the_contagion.md) | NO | — | — |
| 17 | Webwork | MISSING | — | — | WEBWORK_RM_MOD_BUILD_1 (proposed) | EXISTS (the_webwork.md, kits/webwork_kit_spec.md) | NO | — | — |
| 18 | GelatinousSlime | EXISTS | mandrake.rm.gelatinousslime (MATCH) | 1 | GELATINOUSSLIME_RM_MOD_BUILD_1 (proposed) | EXISTS (the_slime.md, the_slime_gene_lists.md) | YES | YES | — |
| 19 | Miasma | MISSING | — | — | MIASMA_RM_MOD_BUILD_1 (proposed) | EXISTS (the_miasma.md, kits/miasma_kit_spec.md) | NO | — | — |
| 20 | Scarlands | MISSING | — | — | SCARLANDS_STANDALONE_MOD_1 (proposed) | EXISTS (the_scarlands.md, kits/scarlands_kit_spec.md) | NO (only legacy `ScarlandsLadder` deployed) | — | unblocked (naming picked); `mandrake.rut.scarlandsladder` stays RimUtinni (owner 2026-09-23, arch §7 Q15) |
| 21 | TheForge | MISSING | — | — | THEFORGE_RM_MOD_BUILD_1 (proposed) | EXISTS (the_forge.md, kits/forge_kit_spec.md) | NO | — | — |
| 22 | FeverWood | MISSING | — | — | FEVERWOOD_RM_MOD_BUILD_1 (proposed) | EXISTS (the_fever_wood.md, kits/fever_wood_kit_spec.md) | NO | — | — |
| 23 | TheSump | MISSING | — | — | THESUMP_RM_MOD_BUILD_1 (proposed) | EXISTS (the_sump.md, kits/sump_kit_spec.md) | NO | — | — |
| 24 | LanternDeeps | MISSING (still under `src/RimUtinni/LanternDeeps`) | — | — | LANTERNDEEPS_RM_MOD_BUILD_1 (proposed) | EXISTS (the_lantern_deeps.md) | YES (as `mandrake.rut.lanterndeeps`, not yet renamed) | YES (under old rut packageId) | skips step 3 (no `RUT_` twin); tier move only |

## Handoff pointers (8 named items)

| item | state (`rimflow show` header line) | what closes it |
|---|---|---|
| FALL_LINE_MAJOR_REGION_LABEL_1 | `doing  row -  needs owner  target v1` | Owner decides whether the other 70 world features get a size hierarchy / which regions count as "major" — Fall Line itself is already done (VERIFIED, histogram 26 vs floor 10, canonical save untouched) |
| FOUNDERS_IMPORTER_OWED_1 | `done  row -  needs offline  target v1` (closed) | Already closed — round-trip founders import proven live on a foreign save, 5/8 fields identical, 3 differ only by expected date/hediff drift |
| TITANOSLIME_SLIME_BIOME_1 | `doing  row -  needs offline  target v1` | Deployed and in sync (dry run: 30 files, md5 identical repo/deployed, MEASURED 2026-09-23); `TITANOSLIME_PERMANENT_GROWTH_LIVE_1` closed PASS — ledger state has not caught up |
| DESERT_FAMILY_PORT_EXECUTION_1 | `proposed  row -  needs offline  target v1` | Owner needs to rule on the one open conflict (replace `Rat` with nothing, since it's not ambient-wired) before the 109-row port finishes; art jobs already filed |
| BIOME_MOD_SPLIT_EXECUTION_1 | `proposed  row -  needs offline  target v1` | Closes when all 23 standalone + TerminalBiomes + LanternDeeps items (this table) close — start order is the four twins (Greentide, GelatinousSlime, Pyrelands, FloodedCanyon) since they carry double maintenance today |
| ASHKARR_PAINTER_NAMES_DIVERGED_1 | `proposed  row -  needs offline  target v1` | Owner call on 5 painter literals that match no live feature (`The Ashteeth`, `The Ember Sink`, `The Fall Line Barrens`, `The Scald Spine`, `The Umbra Trap`) — `ashkarr_settle.py` must not run until `BARREN_REGIONS_NAME_NOTHING_1`'s 10 barren-region mismatches are resolved too |
| OUR_MODS_DEPLOYED_NEVER_ACTIVATED_1 | `proposed  row -  needs deploy  target v1` | Item's own prose says DONE 2026-09-21 (GelatinousSlime added to activeMods, 619→620, verified by byte-delta) — closes on the next cold load per `COLD_LOAD_RUN_SHEET_4`; ledger state line has not caught up to that prose |
| FORGE_ROSTER_UNRECONCILED_BMT_1 | `done  row -  needs offline  target v1` (closed) | Already closed — every `BMT_` donor name in the Forge/Miasma/FeverWood/Greentide rosters wired to an owned def or recorded as a decision |

## Ready to wire tonight

Strict filter (folder EXISTS + design EXISTS + build item still open) returns only **3**
of 24 rows — folder-existence is the bottleneck, 20 of 24 mods have no `src/RimMandrake/`
folder yet:

1. **Greentide (#13)** — folder + design both EXIST, `GREENTIDE_RM_MOD_BUILD_1` open; only
   steps 5 (Desktop load-test) and 6 (commit/push) remain.
2. **Pyrelands (#15)** — folder + design both EXIST, `PYRELANDS_RM_MOD_BUILD_1` open; item
   flags a built-not-deployed trap (`84d42c63b`) to re-check before testing.
3. **GelatinousSlime (#18)** — folder + design both EXIST, `GELATINOUSSLIME_RM_MOD_BUILD_1`
   open, already active in the live mod list; cleanest of the three, no flagged trap.

(FloodedCanyon, the 4th mod with an existing folder, is excluded — its build item is
already `done`/closed; its only open issue is `active: NO`, which is
`OUR_MODS_DEPLOYED_NEVER_ACTIVATED_1`'s pattern, not a build task.)
