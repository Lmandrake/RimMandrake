# Rot art landing report — 2026-09-20

Status: DONE.

## Summary
Both waves fully drained and landed in one pass because they collided on 7
defs (same def, art generated twice — the collision had to be resolved
before either could be wired safely):

- **ROT_ART_WAVE_1**: 22 jobs. 1 already landed pre-session (EuphoricCrown),
  15 non-colliding jobs landed this session, 6 lost their collision to the
  wave-2 re-ruled regen (not deployed, superseded), 1 (PaleTree) won on
  quality as an interim until its own wave-2 line produced a clean v3.
- **ROT_FLORA_FAUNA_VERDICTS_1 STEP 5**: 58 `rot_*_v2` jobs (40 flora + 6
  fauna x3 facings) + 4 same-day `rot_*_v3` regens (filed and cleared by the
  daemon within this session) for the renders rejected/failed below.

**Net: 57 of 58 STEP-5 defs plus 21 of 22 WAVE-1 defs now carry real,
deployed bespoke art** (PaleTree counted once, under wave 2; `AA_Agaripod`/
`RSW_FungalMantis` are keep-rename with no art job, not counted against 58).

## Rejected renders (3, all caught by direct look, not just the automated screen)
- `rot_paletree_v2`, `rot_greylady_v2`, `rot_agariluxprime_v2` — all flat,
  purely achromatic renders (zero hue anywhere sampled), same defect class
  as `rut_agelesscap_v1` (the prior session's catch). Confirmed by comparing
  each against a real-color sibling from the same batch.
- `rot_recurvedstropharia_v2` FAILED (not rejected) — worker returned
  1254x1254 against a requested 1024x1024, a pipeline size-mismatch, not a
  quality issue.

## Regens filed and landed (all 4, same session)
Filed `rot_paletree_v3`, `rot_greylady_v3`, `rot_agariluxprime_v3`,
`rot_recurvedstropharia_v3` via `fill_queue.py` (never hand-written) with
style_notes documenting each rejection and demanding visible color where the
original brief called for it. **The live daemon cleared all 4 while the rest
of this landing pass was underway** — confirmed real color/shading on direct
look, all 4 landed and deployed:
- `rot_paletree_v3` replaced the wave-1 interim art.
- `rot_greylady_v3` replaced not just the rejected v2 but a stale flat-cel
  placeholder trio (`GreyLadyGrownA/B/C.png`) that predated this campaign.
- `rot_agariluxprime_v3` and `rot_recurvedstropharia_v3` landed as first real
  art for those two donor defs.

## v1-vs-v2 collisions and resolution (7 defs)
All resolved by "wave-2 wins" except PaleTree, which needed a second regen
round before wave-2's art actually cleared quality:
| def | v1 (wave 1) | v2/v3 (wave 2) | winner |
|---|---|---|---|
| RUT_AgelessCap | rejected v1 + wave-1's own v2 regen | rot_agelesscap_v2 | wave 2 |
| RUT_RegenerantVeil | rut_regenerantveil_v1 | rot_regenerantveil_v2 | wave 2 |
| RUT_EuphoricCrown | rut_euphoriccrown_v1 (already landed) | rot_euphoriccrown_v2 | wave 2 (replaced) |
| RUT_FalseFruit | rut_falsefruit_v1 | rot_falsefruit_v2 | wave 2 |
| RUT_FurnaceCap (plant) | rut_furnacecap_plant_v1 | rot_furnacecap_v2 | wave 2 |
| RUT_PaleMoss | rut_palemoss_v1 | rot_palemoss_v2 | wave 2 |
| RUT_PaleTree | rut_paletree_v1 (real quality) | rot_paletree_v2 (REJECTED) → rot_paletree_v3 (clean) | wave 1 interim, then wave 2's v3 |

## Mechanism notes
- 27 RUT_ RotSporeKit flora: 7 collision movers got NEW dedicated texPath
  folders (freeing `CrimsonCap`, `GreyLady/GreyLadyGrown`, `FruitingBodies`
  for their own rightful species); 20 already had a distinct folder and just
  needed the PNG dropped in.
- 13 Alpha Biomes flora + 5 Alpha Animals fauna + `RSW_FungalWeevil`: new
  `graphicData/texPath` (flora) or `bodyGraphicData/texPath` (fauna, all 3
  lifeStages) `PatchOperationConditional` blocks appended to
  `RotSpecies_NamesAndSizes.xml` (same gate as the existing label/size ops),
  pointing at new art under each OWNING mod's own `Textures/RotSpecies/`
  folder — never the donor mod's Steam Workshop folder. `RSW_FungalWeevil`
  is a direct edit (ours), not a patch.
- `AA_MycoidColossus`: `rot_mycoidcolossus_v2_east` + `_south` (owner
  pre-approved per the v3 job's own manifest note) + `rot_mycoidcolossus_v3_north`
  (a recompose regen — v2_north's subject aspect ratio didn't match east/south,
  so the creature changed size as it turned) — NOT `v2_north`.
- `RUT_LivingFurnaceCap` moved off the shared `RUT_MortalMorelPlant` item
  texPath onto its own folder.
- `RUT_FruitingBodies`'s new art (`rot_fruitingbodies_v2`) renders as a
  scattered field of small sprigs rather than one centered subject — real
  color/shading, just an atypical composition; flagged on the contact sheet
  rather than rejected outright.
- Deleted stale "ART OWED: placeholder" comment blocks in `RUT_RotSporeKit_FurnaceCap.xml`
  (x2), `RUT_RotSporeKit_GuardianGroves.xml` (touched via texPath edits) and
  `RUT_PaleTree.xml` — those claims are false now (per CLAUDE.md's
  delete-inaccurate-material rule).

## Validation and deploy
`validate_patch.py` against `RotSpecies_NamesAndSizes.xml`, full-list
ModsConfig snapshot (`infrastructure/state/modlists/ModsConfig_full_plus_longhunger_2026-09-19.xml`):
**0 errors** across both patch commits, every new operation matched exactly
1 node, 1 benign pre-existing warning (unrelated Agaripod label pattern).
Deployed and verified in sync: RotSporeKit (37 files total across 2 commits),
UtinniPatches (30 files), SWBestiary (4 files). Every deploy plan showed only
my own files plus pre-existing `DEPLOY_HOLD.txt` entries or another window's
unrelated held art — never applied over live cross-window drift.

## Contact sheet for the owner's eye
`review-sheets` skill template + `check_sheet.py` (0 FAIL, 1 benign WARN
about the prefill already being "reviewed" by my own script — expected).
61 rows, thumbnails for every render (except `AB_RecurvedStropharia`'s
original failed job, which never produced a PNG — its v3 is shown instead).

Native Windows path: `D:\Luke\dev\Rimworld\Transient\rot_art_landed_20260920\index.html`

The sheet was built to the `review-sheets` skill's format (served-sidecar
ready) but NOT served interactively from this session — I'm a one-shot
background subagent, not the owner's live BENCH window. Open it directly, or
run `python3 /home/mandrake/.claude/skills/review-sheets/assets/serve_sheet.py
--sheet Transient/rot_art_landed_20260920/index.html --decisions
Transient/rot_art_landed_20260920/rot_art_landed_20260920.decisions.json`
from a live session for the interactive save-back workflow.

## Item files
`ROT_ART_WAVE_1.md`: false "19 of 22 still pending" line DELETED (not
superseded-in-place), replaced with the full landing account, marked
**closed**.
`ROT_FLORA_FAUNA_VERDICTS_1.md`: STEP 5 entry appended to the existing status
log (FOUNDRY-owned item; no commit-hook refusal hit editing it this session).

## Not finished / gated on
- `RUT_BrewingVessel` east+north views (wave-1's original filing note flagged
  these as still owed; out of scope for this landing pass — no jobs filed
  for them, needs a fresh art-list entry if wanted).
- `RUT_Gene_Furnaceblood` icon's fit in this pipeline at all — flagged, not
  resolved, since the original wave-1 filing note.
- `RUT_NuitaeMarsh`/`RUT_WrinklecapMarsh`/`RUT_GreenArpeau`/`RUT_NogtylMarsh`/
  `RUT_MortalMorelPlantGrowable` marsh/growable sibling variants still carry
  their base def's OLD label (flagged in STEP 1, unchanged) — not an art gap,
  a label-consistency follow-on.
- Everything else in scope for both items is landed; no outstanding artpipe
  jobs remain for either wave as of this report.

## Claims
- All landing, collision resolution, validation and deploy counts above:
  **CONFIRMED** (measured via `validate_patch.py`, `deploy_custom_mods.py`
  plan/apply output, and direct image inspection of every rejected/flagged
  render plus a spot-check sample of the rest).
- "0 outstanding artpipe jobs for either wave": **CONFIRMED** —
  `infrastructure/artpipe/pending/` and `active/` contain no `rut_*` or
  `rot_*` ids as of the last check this session.
- Whether every one of the 73 landed renders is a good STYLE fit (not just
  free of the flat-achromatic defect): **UNCERTAIN** for the ~45 rows I did
  not individually view (screened only by the automated saturation check,
  which catches the "no color fill" defect but not composition or anatomy
  problems) — that's exactly what the contact sheet is for.
