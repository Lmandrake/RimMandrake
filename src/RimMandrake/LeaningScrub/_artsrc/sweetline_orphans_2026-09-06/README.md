# Sweetline-tree orphans, recovered 2026-09-06

Fourteen finished sweetline-tree images that `codex_image.py` reported as
timeouts and threw away. They were never failures: the PNG landed, the
wrapper's ceiling expired during Codex's wrap-up turn, and `run_codex()` raised
before `harvest_new()` could run. Fixed under `CODEX_WRAPPER_HARVEST_FIX_1`;
these are the images that bug stranded, recovered out of
`C:\Users\Mandrake\.codex\generated_images\<session>\` — a volatile app cache,
not a place work should live.

Attribution is not filename guesswork: each session's own rollout
(`C:\Users\Mandrake\.codex\sessions\2026\09\06\rollout-*.jsonl`) carries the
verbatim `Use $imagegen to A single massive ancient tree…` prompt from
`TREE_GRAPHICS_OWNERSHIP_1`, and all fourteen were opened and looked at
(`CONTACT_SHEET.png`). Every file was re-read after copying: valid IHDR, intact
IEND chunk, byte-identical to the source.

## Contents

| # | file | size | alpha |
|---|---|---|---|
| 0 | `sweetline_003749_01a075a6_d2725998.png` | 1254x1254 | green chroma background |
| 1 | `sweetline_003956_01a075a7_087c7a95.png` | 1536x1024 | **native, corners (1,1,1,0)** |
| 2 | `sweetline_004035_01a075a7_e0b7b756.png` | 1536x1024 | green chroma background |
| 3 | `sweetline_004204_01a075a9_e83a0029.png` | 1536x1024 | **native** |
| 4 | `sweetline_004421_01a075ab_ce342645.png` | 1536x1024 | **native** |
| 5 | `sweetline_004456_01a075ab_b79b36ba.png` | 1536x1024 | green chroma background |
| 6 | `sweetline_005028_01a075b1_958b1a33.png` | 1254x1254 | green chroma background |
| 7 | `sweetline_005247_01a075b3_240b3bac.png` | 1536x1024 | **native** |
| 8 | `sweetline_005324_01a075b3_7224d3fd.png` | 1536x1024 | green chroma background |
| 9 | `sweetline_005742_01a075b8_2bc62790.png` | 1198x1313 | green chroma background |
| 10 | `sweetline_010813_01a075c1_57c072c4.png` | 1536x1024 | **native** |
| 11 | `sweetline_015509_01a075ec_6456c361.png` | 1218x1292 | **native, corners (0,0,0,0)** |
| 12 | `sweetline_015747_01a075ef_f26185e7.png` | 1536x1024 | **native** |
| 13 | `sweetline_015824_01a075ef_acde51de.png` | 1536x1024 | green chroma background |

Filename is `sweetline_<HHMMSS>_<session prefix>_<exec id prefix>.png`; the
session prefix is the rollout that proves the prompt.

Seven carry a real alpha channel (42–54% alpha-0, transparent corners). That is
independent corroboration of the native-transparency measurement this pass
acted on: it holds across seven generations, not one. **Prefer those seven** —
they need no key removal at all. The seven green ones came from the same prompt
with the old chroma-key clause appended.

## What is still owed

`Textures/Things/Plant/RUT_SweetlineTree/RUT_SweetlineTreeA.png` is **still
empty**, deliberately. Choosing which of fourteen becomes the sweetline tree —
and where its base registers on a 768x768 canvas — is an art call for the owner,
not something to settle by picking the newest file. `conform_sprite.py` also
wants a reference sprite for that canvas, and this def has none yet.

Look at `CONTACT_SHEET.png` (rendered over a checkerboard, so transparency reads
as transparency), pick one, then conform it to 768x768 (128 px/cell x 6.0 cells)
and run `validate_sprite.py` before landing it.
