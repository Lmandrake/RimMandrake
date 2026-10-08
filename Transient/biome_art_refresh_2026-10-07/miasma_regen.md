# Miasma canon regen — 2026-10-07 (BENCH helper)

Source: `Transient/biome_ffar/miasma_sheet_2026-10-05.decisions.json` (human rows = those with `at`).

## Status
- [x] artpipe filing mechanism + priority read (fill_queue.py; `priority` int, LOWER claims sooner; filed at **0**, below the lowest ever used (1))
- [x] existing-art search per subject (`artpipe_state.py find`, sanity probe `korrum` = 18 hits)
- [x] canon entries read (Vornskyr, LaaJuv→laascalefish, OpeeSeaKillerJuv→opeeseakiller, YobshrimpJuv→paleyobshrimp, Zakkeg, Blarth, Blixus, MarshHaunt, Bogwing)
- [x] jobs filed: 52 rows → 92 jobs, `Transient/biome_art_refresh_2026-10-07/miasma_regen_jobs.json` (built by `build_miasma_regen_jobs.py` beside it). Daemon (pid 441, `artpiped.py -N 5`) claimed the first 5 within seconds; nothing else was pending, so these are positions 1–92.
- [x] census → `canon_gap_census.md` (+ `.json`, `canon_gap_census.py`, `canon_gap_census_md.py`, sonnet visual verdicts `canon_gap_census_visual.jsonl`). 169 canon rows / 115 defs on 21 sheets; 137 rows / 104 defs are gaps. 104 rows (83 defs) still show donor art never regenerated, 63 of them with a canon-briefed render already sitting on the sheet uninstalled. Of the 38 defs whose in-game art is ours, 10 CONTRADICT Must show, 10 PARTIAL, 18 PASS.
- Daemon canon gate on the first finished jobs: vornskyr_v2 east 5/5, opeejuv east 7/7 (gpt-6.1-sol grader).

## Jobs filed (priority 0, item BIOME_FLORAFAUNA_ART_REVIEW_1, owner notes verbatim in `owner_note` + prompt lead)
- **RSW_Vornskyr**: `miasma_canon_vornskyr_v2` (3 jobs, 512px, canon vornskyr)
- **RSW_LaaJuv**: `miasma_canon_laajuv_v1` (3 jobs, 256px, canon laascalefish)
- **RSW_OpeeSeaKillerJuv**: `miasma_canon_opeejuv_v1` (3 jobs, 256px, canon opeeseakiller)
- **RSW_YobshrimpJuv**: `miasma_canon_yobshrimpjuv_v1` (3 jobs, 256px, canon paleyobshrimp)
- **RSW_Zakkeg**: `miasma_canon_zakkeg_v2` (3 jobs, 1024px, canon zakkeg)
- **RSW_Blarth**: `miasma_canon_blarth_v1` (3 jobs, 256px, canon blarth); `miasma_canon_blarth_v1_swim` (3 jobs, 256px, canon blarth, derive miasma_canon_blarth_v1_east)
- **RSW_Blixus**: `miasma_canon_blixus_v1` (3 jobs, 512px, canon blixus); `miasma_canon_blixus_v1_swim` (3 jobs, 512px, canon blixus, derive miasma_canon_blixus_v1_east)
- **RSW_MarshHaunt**: `miasma_canon_marshhaunt_v1` (3 jobs, 256px, canon marshhaunt); `miasma_canon_marshhaunt_v1_swim` (3 jobs, 256px, canon marshhaunt, derive miasma_canon_marshhaunt_v1_east)
- **RSW_Bogwing**: `miasma_canon_bogwing_v1` (3 jobs, 256px, canon bogwing); `miasma_canon_bogwing_flying_1_v1` (3 jobs, 256px, canon bogwing, derive miasma_canon_bogwing_v1_east); `miasma_canon_bogwing_flying_2_v1` (3 jobs, 256px, canon bogwing, derive miasma_canon_bogwing_v1_east); `miasma_canon_bogwing_flying_3_v1` (3 jobs, 256px, canon bogwing, derive miasma_canon_bogwing_v1_east); `miasma_canon_bogwing_flying_4_v1` (3 jobs, 256px, canon bogwing, derive miasma_canon_bogwing_v1_east)
- **AA_Lockjaw**: `miasma_siezer_v1` (3 jobs, 512px)
- **AA_Mantrap**: `miasma_lastvine_calm_v1` (3 jobs, 256px); `miasma_lastvine_reared_v1` (3 jobs, 256px)
- **RSW_PodWorm**: `miasma_hellslantern_v1` (3 jobs, 512px)
- **VFEI2_Swarmling**: `miasma_swarmling_green_v1_east` (1 job, 256px, derive rot_swarmling_v2_east); `miasma_swarmling_green_v1_south` (1 job, 256px, derive rot_swarmling_v2_south); `miasma_swarmling_green_v1_north` (1 job, 256px, derive rot_swarmling_v2_north)
- **RM_Aphreen**: `miasma_aphreen_v2` (1 job, 256px)
- **RM_Braskeen**: `miasma_braskeen_closed_v2` (1 job, 256px); `miasma_braskeen_open_v2` (1 job, 256px)
- **RM_Ommolyn**: `miasma_ommolyn_v2a` (1 job, 256px); `miasma_ommolyn_v2b` (1 job, 256px); `miasma_ommolyn_v2c` (1 job, 256px)
- **RM_Velluric**: `miasma_velluric_v2a` (1 job, 256px); `miasma_velluric_v2b` (1 job, 256px); `miasma_velluric_v2c` (1 job, 256px)
- **RM_Nemreth**: `miasma_nemreth_varb_v1` (1 job, 256px); `miasma_nemreth_varc_v1` (1 job, 256px)
- **RM_Nogtyl**: `miasma_nogtyl_varb_v1` (1 job, 1024px); `miasma_nogtyl_varc_v1` (1 job, 1024px)
- **RM_Nyssolet**: `miasma_nyssolet_varb_v1` (1 job, 256px); `miasma_nyssolet_varc_v1` (1 job, 256px)
- **RM_Pallasheen**: `miasma_pallasheen_varb_v1` (1 job, 256px); `miasma_pallasheen_varc_v1` (1 job, 256px)
- **RM_Sarrash**: `miasma_sarrash_varb_v1` (1 job, 256px); `miasma_sarrash_varc_v1` (1 job, 256px)
- **RM_Thessamor**: `miasma_thessamor_varb_v1` (1 job, 256px); `miasma_thessamor_varc_v1` (1 job, 256px)
- **RM_Thrannock**: `miasma_thrannock_varb_v1` (1 job, 256px); `miasma_thrannock_varc_v1` (1 job, 256px)
- **RM_Ullavess**: `miasma_ullavess_varb_v1` (1 job, 256px); `miasma_ullavess_varc_v1` (1 job, 256px)
- **RM_Vellamine**: `miasma_vellamine_varb_v1` (1 job, 256px); `miasma_vellamine_varc_v1` (1 job, 256px)
- **RM_Wessaline**: `miasma_wessaline_varb_v1` (1 job, 256px); `miasma_wessaline_varc_v1` (1 job, 256px)

Notes:
- Canon rows attach ONE canon image as anatomy guidance (`canon_reference`, never `reference`): Vornskyr = `wookieepedia_alienarchive.jpg` (his 2026-09-14 ruling), Zakkeg = `wookieepedia_kotor2_juvenile.png` (his ruling, the red one), Yobshrimp = `paleyobshrimp/wookieepedia_legends_1.webp` (the purple live animal; the entry's canon_1 is a food photo), Laa/Opee/Blixus/Bogwing/MarshHaunt = `wookieepedia_canon_1.webp`, Blarth = legends_1 (no canon image exists). `canon` field folds each entry's Visual brief + Must show into style_notes.
- Swim graphics (`*_Swimming`) and the Bogwing's 4 whole-body flip-book frames (`Bogwing_Flying_1..4`, frame count from the PawnKindDef) derive from the new standing east master, so they are the same individual; the daemon holds them until it finishes.
- Lastvine (AA_Mantrap): two states filed — calm closed pod and reared gaping maw — both anchored on his column E render. The reared state has no texPath yet (`AA_Mantrap_Reared` is a proposed name); wiring a two-state graphic is def work for after his review.
- Swarmling: per-facing edits of `rot_swarmling_v2` (column B, the bulbous milk-white sac) recoloured sickly green.
- Plant variants: 2 new variants (b, c) per "add variants" plant, each anchored on his chosen column A render; Ommolyn and Velluric get 3 fresh redesigns each. Nogtyl at 1024 (12-cell tree; generator ceiling ≈85 px/cell).
- Canvas from the def's adult drawSize at 128 px/cell (Zakkeg 5.0 → 1024, Blixus 4.0 / Vornskyr 3.0 / Hell's Lantern 3.25 / Siezer 2.25 → 512, rest 256).
- Not filed (no art asked): rename/description-only rows (DecayDrake→Fermatalis, RaptorShrimp→Sharpshrimp, Thermadon→Duskfire, SiltLampreyJuv→Gillclamper, AaroxisDendoria→Liliana, BlackSwarmling) and holds/cuts.

## Already generated, not on the sheet (listed, did not replace the new jobs)
- `miasma_nemreth_v2` (done 2026-10-04, a "low flat spreading mat" Nemreth) — never shown on the Miasma sheet; a candidate extra variant.
- `lockjaw_improve_a_r13`, `lockjaw_improve_b_r10` — later rounds of the old crocodilian lockjaw brief, which his note now rejects.
- `vornskyr_v1`, `zakkeg_v1` (2026-09-11) — pre-canon-library renders, superseded by `canon_*_v1` (which he called wrong).
- `nogtyl_v1` (2026-09-13) — the pre-`rot_nogtyl_v2` design.
- NO finished art at all for: opee, yobshrimp, blarth, blixus, marshhaunt, bogwing, podworm, siezer, lastvine (the sheet's in-game art for these is donor art).
