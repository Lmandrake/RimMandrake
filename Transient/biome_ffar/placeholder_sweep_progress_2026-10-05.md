# Placeholder sweep progress 2026-10-05

Owner (verbatim): "Ok, I did half the Grey Sea... something very wrong with that sheet. Most of the images look like nothing, trivially simple imagery, or cactus. Please investigate and repair."

## Cause
The Grey Sea's live art is placeholder: creatures are script-drawn flat shapes (1-3 colours), flora and catch items borrow vanilla plant textures (Echeveria, Schlumbergera, ...). Gap-fill and the sheet gate counted any live file as "art of ours".

## Detector
`src/RimMandrake/Utils/art/placeholder_detect.py` (selftest: `selftest_placeholder_detect.py`, 16/16 incl. a sanity probe on real renders).
- FLAT: >= 300 opaque px, <= 8 distinct colours (5-bit quantised), >= 0.85 of neighbouring pixel pairs equal within 6/765.
- BORROWED: creature/fish row on a `Things/Plant/*` texPath; or an RM_/RSW_/RUT_ def whose texPath tail lacks its own subject name AND the texture is shared by 2+ subjects or sits under a vanilla folder (own `RM_` folders and donor-mod trees exempt).
- A row is PLACEHOLDER only if every body texture is.
Calibration (flat placeholders vs real, `placeholder_detect.py calibrate`):
```
FLAT (live census)     n=  76 ncol   min    1.000 p5    1.000 median    2.000 p95    3.000 max    8.000
FLAT (live census)     n=  76 smooth min    0.910 p5    0.935 median    0.985 p95    1.000 max    1.000
live census not flat   n= 822 ncol   min   13.000 p5  102.000 median  480.000 p95 2103.350 max 6363.000
live census not flat   n= 822 smooth min    0.050 p5    0.081 median    0.248 p95    0.789 max    0.921
artpipe real renders   n= 594 ncol   min    4.000 p5  142.650 median  586.000 p95 1997.950 max 11091.000
artpipe real renders   n= 594 smooth min    0.050 p5    0.083 median    0.193 p95    0.626 max    1.000
```

## Census sweep (all 27 biomes with rows; UNMEAS = texture file not on disk here, e.g. donor art; never counted REAL)
```
biome                      rows  PLACEHOLDER  REAL  UNMEAS  NONE
RM_GreySea                   46       43         3      0      0
RM_FeverWood                 38       24        13      1      0
RM_Webwork                   23       22         0      1      0
RM_WeepingStones             51       20        21     10      0
RM_TwilightSea               34       15        18      1      0
RM_Greentide                 64        7        51      6      0
RM_TheChill                  29        7        22      0      0
RM_GelatinousSlime           12        3         7      2      0
RM_Miasma                    63        3        51      9      0
RM_FloodedCanyon             25        1        20      4      0
RM_TheScald                  23        1        22      0      0
RM_TheSump                   21        1        20      0      0
RM_LongShade                 67        0        66      1      0
RM_Stillsand                 30        0        30      0      0
RM_BlueDesert                20        0        18      2      0
RM_Abyss                     27        0        14     13      0
RM_Cauldron                  46        0        29     17      0
RM_Contagion                 35        0        35      0      0
RM_LanternDeeps              39        0        39      0      0
RM_LeaningScrub              78        0        69      9      0
RM_NightsideIce               4        0         2      2      0
RM_Pyrelands                 18        0        18      0      0
RM_RustCathedral              5        0         3      2      0
RM_TheForge                  24        0        14     10      0
RM_TheRot                    56        0        52      4      0
RM_Warscar                   19        0        14      5      0
RM_Wasteland                 21        0        18      3      0
```
Per-row verdicts and reasons: `Transient/biome_ffar/placeholder_sweep_2026-10-05.json`.
Seas: Grey Sea 43/46 placeholder, Twilight Sea 15/34, The Chill 7/29, The Scald 1/23, The Sump 1/21. Also Fever Wood 24, Webwork 22, Weeping Stones 20 (script-drawn plants/creatures, shared vanilla Tortoise/Cobra/meat).

## Jobs
`Transient/biome_ffar/placeholder_regen_jobs_2026-10-05.json` (builder `src/RimMandrake/Utils/art/placeholder_jobs.py`): 64 rows, 92 artpipe jobs filed to pending (ids `phreg_<def>_v1`; Grey Sea priority 8, other open sheets 10, rest 15). Creatures east master + south/north derived; plants single; catch items 128px item sprites anatomy-referenced to the floor creature's render when one exists.
Rows skipped because a render already exists in artpipe (done/pending): 83, listed in `placeholder_regen_jobs_2026-10-05_render_exists_not_installed.json` (Fever Wood, Webwork, Weeping Stones, 4 Grey Sea: essarn/fessk/otheska/sorruth, etc.). Those renders are NOT installed; the live art stays placeholder until `art install`.

## Integration owed in art_sheet.py / scaled_review_gate.py (not edited here)
1. In the row's "live art" evaluation call `placeholder_detect.classify_row(row, placeholder_detect.shared_map(census))`; verdict PLACEHOLDER means the live art is NOT art of ours: req 3 (a render of ours exists) counts the row as having no art of ours, so gap-fill queues it and the gate fails the sheet until a real render is on it.
2. The sheet badges those rows "placeholder" (reasons string from the classification) instead of showing the live art as the incumbent.
3. UNMEASURED (file not found) is never treated as REAL.
