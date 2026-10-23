# Art judgments — 2026-10-23 (FOUNDRY, delegated)

Two card answers carried out today. Both pictures were looked at by me first, then by an outside judge (GPT via
`gpt_consult.py`, images attached, `design/RimMandrake/art_judge_brief.md` inlined for the RustPuff pass).

## 1. Gale dust overlay — SCRUB_WIND_BUILD_LEAN_ON_PURPOSE ("Install dust art, then look")

**Found:** sheet A was already installed (your sheet pick, 2026-10-20) but as the raw render: an opaque RGB
black-and-grey square. The art list says brightness becomes alpha at install; that step was skipped, so in game it
would have drawn a dark streaked sheet over the map. Sheet B (the overlay's second layer) was not installed, so that
layer was still vanilla fog.

**Done:** both sheets cleaned and installed through the art ledger as white dust whose alpha is the old brightness
(black = clear air).
- Judge pass 1: A "FIX" (pebble-like specks, a scale-like rhythm of bright brooms), B "FIX" (curls and dots read as
  scratches or straw). I removed the compact specks and curls, cut A's brightest cores, smeared B into tapered downwind
  dashes, all with wrap-safe filters so the tiles still repeat without a seam.
- Judge pass 2: A **SHIP**, B one hook and one crescent left. Both erased. Composite: "convincing gale at full
  strength; vegetation remains readable."
- `selftest_scrub_wind.py` now requires both sheets, each carrying the dust in alpha (it catches the opaque install).
  OK, 11 breaks.
- **Not done:** the C# header comment in `RM_WeatherOverlay_GaleDust.cs` still says PLACEHOLDER. Another helper is
  rebuilding the LeaningScrub DLL, so the comment changes with the next build. No code change is needed: the overlay
  reads `owned (AB)` once both textures load. Not deployed. It needs a look in game (your note on the sheet said so).

Look at: `D:\Luke\dev\RimMandrake\src\RimMandrake\LeaningScrub\Textures\Weather\RM_GaleDust_A.png`,
`D:\Luke\dev\RimMandrake\src\RimMandrake\LeaningScrub\Textures\Weather\RM_GaleDust_B.png` (alpha images: they look
white on a white viewer). The composite (bare scrub vs. Gale at full strength) is in the FOUNDRY clone at
`\\wsl.localhost\Ubuntu\home\mandrake\rm\foundry\Transient\gale_dust_2026-10-23\compare_bare_vs_AB.png`.

**Veto:** say "put the old Gale A back" or "retire Gale B". The old A is in the art store
(sha `f2faddd3d246…`), so `art.py install LeaningScrub Weather/RM_GaleDust_A.png f2faddd3d2465b27ae567bf5c7f70b61843734f8fbf07b603894f59d5e83e553 --owner-said "…"`
restores it.

## 2. Contagion RustPuff variants B, C, D vs your kept A — REGEN_RENDERS_INSTALL_AS_THEY_LAND A2 ("Judge by a second agent, you veto")

Shown at true scale (0.6 cell, up to 4 per cell) beside a vanilla human and vanilla Agarilux, plus at 32 px/cell.
Plants have one facing.

| variant | my look | outside judge | verdict |
|---|---|---|---|
| B | same species, lumpier cluster | KEEP: same palette and lighting, broader uneven lobes add variety, legible in play | **KEEP** |
| C | taller, folded lobes | KEEP: useful silhouette variation, no defect | **KEEP** |
| D | closest to A | KEEP: big front lobe adds modest variety; near-duplicate is not a defect | **KEEP** |

**Nothing retired.** Judge's caveat: all four share A's "somewhat garlic-like" puffball shape. That is A's own look,
which you kept. Files: `D:\Luke\dev\RimMandrake\src\RimMandrake\TheRot\Textures\RotSporeKit\Things\Plant\RustPuff\RustPuff_B.png`
(`_C`, `_D` beside it; `_A` is yours).

**Veto:** say "retire RustPuff C" (any letter). It is retired through the art ledger with your words; the file is
archived in the art store, never deleted.
