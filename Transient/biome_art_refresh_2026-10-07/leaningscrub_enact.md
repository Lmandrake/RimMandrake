# Leaning Scrub sheet — enactment (2026-10-07/08, BENCH helper)

Source: `Transient/biome_ffar/leaningscrub_sheet_2026-10-05.decisions.json` (owner rows = those with `at`).

## Status
- [x] Venomvine root cause
- [x] Venomvine restore (sheet rebuild: pending)
- [x] Venomvine regen queued (front of queue)
- [x] Long Shade venomvine job folded / tint reported
- [x] decisions read (rest of sheet)
- [x] install / purge
- [x] regen queued
- [ ] names / descriptions / tiers / cuts
- [ ] validate + selftests
- [ ] commits

## Venomvine
Decisions md5 9986b4a3… (writeCount 521, savedAt 2026-10-07T22:50:10-0700); copy: infrastructure/state/art_rulings/2026-10-08_leaningscrub_sheet_2026-10-05.decisions.json.
`art.py ingest --defer-redo-jobs`: 177 rulings, 49 rejected, 195 purged, 3 refused (Eopie S/E/N bytes he KEPT on the Long Shade sheet).

### Root cause
- The "white pillar" is sha 9e0e6c1d33b1 = `_artsrc/RM_PillarArmB_east` (a Contagion monstrous-limb render). Artpipe job `rmvenomvine_v1`
  (2026-09-21, prompt: "a low, matted tangle") came back with those exact bytes, and **bbe171ebc** (2026-09-26, COLLECTION_GRAPHIC_ON_FLAT_PNG_1)
  wired it as `EnvironmentalHazards/Textures/Things/Plant/RM_Venomvine/RM_Venomvine_a.png` on a facts-PASS without looking.
  RM_Venomvine and RM_VenomvineThicket (same texPath by design) have shown it ever since.
- **7753208e5** (2026-10-06) added the six new forms (Rearing/Walking/Hoard/Quench/Sworn/Shedding) all pointing at the same folder as a "placeholder", so 8 defs wore it.
- The same bytes are also RM_Kudda_east / RSW_Kudda_east (2154ef2ea) — a second wrong-subject wiring, out of this sheet's scope, not touched.
- The Long Shade helper did NOT add a tint: RM_Venomvine has carried `<color>(112,68,48)</color>` since 10033074a and the thicket `(78,47,33)` since 4d41826a8; its note only flagged it. Tints are not the pillar's cause (the PNG itself is white/grey) but would multiply real rust/near-black renders toward black, so both were removed.

### Restored / wired (art ledger installs, `leaningscrub_venomvine_install.py`)
- RM_VenomvineThicket -> own folder `Things/Plant/RM_VenomvineThicket/_a` = RM_VenomvineThicket_v2 (his 10-06 pick C, ruling 74428c23…). His B (02098c) he also purged himself — not installed.
- RM_Venomvine `_a` -> interim real render leaningscrub_venomvinethicket_c (acfe6b, the low tangle its brief describes), mechanical reason.
- Six forms -> own folders `Things/Plant/RM_<Form>Venomvine/_a`, interim = his kept thicket render (mechanical reason) until their own renders land.
- Crown (B + A,C,D), Dripping (B + A,C,D), Hollow (A + B,C,D): his ticked variants installed as `_b/_c/_d` beside `_a` (rulings from ingest).
- No venomvine def references the pillar bytes any more. Pillar NOT purged (live in Kudda east and PillarArmB).

### Regen (`build_venomvine_regen_jobs.py` -> `venomvine_regen_jobs.json`): 43 jobs, priority 0, ids `0vv_*` -> pending positions 1–43 of 433 (artpiped claims by (priority, filename)).
- desert RM_Venomvine 4 (folds the withdrawn `regen_ls_x_venomvine_v2`, moved to `_artpipe/_withdrawn/`; his LS note verbatim)
- Rearing 4 + reared state 2, Walking 4, Hoard 4, Quench 4 + spent state 2, Sworn 4, Shedding 4 (fresh, from the 2026-10-03 pitch art briefs; Hoard/Quench/Rearing carry his note verbatim, the rest his chat words)
- Thicket 3, Twitcher 2, Dripping 2, Hollow 2, Crown 2 (anchored on his accepted picture as first canon_reference)

## Rest of sheet
Owner rows: 22 from 2026-10-06 (enacted 10-05/06 per leaningscrub_close_progress_2026-10-05.md, leftovers below), 54 from 2026-10-08.

### Install (`leaningscrub_install_plan.py` -> `leaningscrub_install_result.jsonl`, 3acc6123b)
- 62 slots installed via ledger rulings: Anooba L (Anooba_f), Cannok C, Corinathoth D, FeralNerf C, Fuzzrunner B, Fuzzviper B, Grank E (east only; N/S queued),
  Igitz E, KowakianMonkeyLizard C, Kreetle J, Lothcat D (east only; N/S queued), Massiff C, MossBeetle B, Pikobis D, Porg E, Pufferpig C, Qormot C,
  Scurrier C (Scurrier_f), Strill C east + D north/south (the derived N/S of that east), Urusai C, Whisperbird F (east only; N/S + flight queued), Zellik B,
  Grellbush B (replaces _a), arid grass B (UtinniPatches' own RG_DesertGrass override, DesertGrassA).
- RM_Chikka C and RM_Vurra B: had Alpha Animals / Horrors donor textures; installed at Things/Pawn/Animal/RM_Chikka|RM_Vurra (SWBestiary), PawnKindDefs repointed.
- Explicit variants: Pillowmoss B/C/D, Cruststar B/C/D (+ venomvine Crown/Dripping/Hollow above).
- Already current (pick = live bytes): Bantha E, Eopie E/H, Iriaz C, Mudhorn B/C, Ronto B, Skalder B/D, Sketto B, Voorpak D, Vulptex C, Worrt B/D/E, TruffleMole B,
  Anooba_m F, Igitz swim/j, Kreetle_j, Lothcat_m, Pikobis swim, Porg f/j, Scurrier_m. Cross-checked against tonight's Long Shade picks: same bytes for all 8 shared species.
- Ingest refused 3 purges: Eopie S/E/N old bytes he KEPT as Eopie on the Long Shade sheet (picks agree; nothing to do).
- NOT installed: pre-ticked default variants (Greentide method); donor ReGrowth plants Brambles B, CreepStern B, CrimsonCushion B, Dervish C (no owned slot — question).
- Placeholder check: ingest's detector flagged none of his picks; every install passed the ledger's placeholder refusal.

### Regen (`build_leaningscrub_regen_jobs.py` -> `leaningscrub_regen_jobs.json`): 48 jobs, priority 0, pending 341–388 of 477 (behind 0vv_* and earlier sheets)
- Grank N/S (canon, precisely), Lothcat N/S (less cartoonish), Whisperbird N/S + 4 flight frames, Convor redo x2 (from D, less cute), Kybuck redo x2 (head bone plate),
  Urusai canon redo x2 (from C), Zellik "more alien" x2 (from B), scrap-nest bird redo x2 (no canon entry: its own description). Sketto N/S already queued by Long Shade (same pick bytes).

### Names / descriptions / tiers / cuts
- RM_Durrok description rewritten to the picked image (RSW_Durrok has no separate def; same picture). RM_Chikka description reworded to match his pick C (round spiky ball).
- RM_Zellik description unchanged (fits B). Skorra: in no biome roster, nothing to cut.
