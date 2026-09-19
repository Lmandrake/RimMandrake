## spec

Wire the 5 owner-approved landed sprites from Group C of
`Transient/rot_flora_fauna_review_2026-09-18.decisions.json`:
- twistingthornweed_v1_r2
- twitchingpuffer_grown_v1
- twitchingpuffer_harvested_v2
- twitchingpuffer_immature_v1
- twitchingpuffer_tendrils_v1

Also wire any other approved-but-unwired Deeps sprite from
`Transient/deeps_art_review_2026-09-18.decisions.json` (PrennaLace,
TwitchingPuffer per the deeps species sheet).

Rot cuts: remove `RSW_BovineBeetle` from `<wildAnimals>` in
`src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheRot.xml` (now the Deeps'
Grabber). `RUT_Emberscythe` marked cut but is not in Rot's tables (Pyrelands
fauna shipped inside RotSporeKit) — no XML change, flag for owner: move to a
Pyrelands mod?

Validate + deploy LanternDeeps, UtinniPatches, and twistingthornweed's mod;
commit only own files; rimflow note.

## status log

- 2026-09-19: skeleton written, starting investigation.
- 2026-09-19: TASK 1 investigated. All 4 `twitchingpuffer_*` and `twitchingpuffer_tendrils_v1`
  sprites were ALREADY wired and committed (`a1e40ff04`, `DEEP_FLORA_RENAME_1`) — pixel-identical
  to the artsrc PNGs (bytes differ, PIL recompression, but `ImageChops.difference` confirmed
  identical pixels), no action needed. PrennaLace (`greylady*`) likewise already wired and
  committed (`e1427a149`). Ran `wire_art.py` plan mode against the deeps decisions file: 44 kept,
  and a pixel-diff sweep of all 44 found exactly ONE actually unwired: `lanternstonesowableimmature_v1`
  (dest `RUT_LanternDeeps/Things/Crystals/LanternstoneSowableImmature.png` did not exist). Copied it
  by hand (not via `wire_art.py --apply`, which does unconditional `shutil.copy2` on all 44 rows and
  would have rewritten the 43 already-identical files with different bytes — pure noise in the diff).
  `twistingthornweed_v1_r2`: only ONE regen job was queued (not an a/b pair), existing
  `TwistingThornweed_a.png`/`_b.png` (from `POLLUTED_LANDS_FLORA_PORT_1`) are still in place;
  wired the new approved sprite as a third Graphic_Random variant, `TwistingThornweed_c.png`,
  per the task's literal instruction (append per the folder's existing convention) rather than
  replacing a/b, which would need an explicit owner ruling. Note: new art is 256x256, existing
  a/b are 128x128 — inconsistent canvas within one Graphic_Random folder; not blocking (RimWorld
  doesn't require matching sizes across variants) but flagging.
  PNGs wired this session:
  - `src/RimUtinni/LanternDeeps/Textures/RUT_LanternDeeps/Things/Crystals/LanternstoneSowableImmature.png`
  - `src/RimUtinni/UtinniPatches/Textures/Things/Plant/TwistingThornweed/TwistingThornweed_c.png`
- 2026-09-19: TASK 2 done. `RSW_BovineBeetle` line removed from `<wildAnimals>` in
  `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheRot.xml` (was line 135, weight 0.2).
  `RUT_Emberscythe` confirmed NOT present anywhere in `RUT_TheRot.xml` — grep found no match,
  matching `build_review_sheet.py`'s own note ("NOT in RUT_TheRot ... Pyrelands fire-follower
  shipped in this same kit [RotSporeKit]"). "cut" is therefore already true for the Rot; no XML
  change made. Open question for the owner: should `RUT_Emberscythe` MOVE out of RotSporeKit
  into a dedicated Pyrelands mod, since it's Pyrelands fauna currently shipped inside a Rot-named
  kit with placeholder art (a vanilla Megascarab recolor, per its own header comment)?
