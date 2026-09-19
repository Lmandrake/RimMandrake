# ASHKARR_NIGHTSIDE_LAYER_SUPERSEDED_1 — ashkarr_layer_nightside.py's carve targets are both dead, and the owner's underlying ruling may still be unfulfilled

Discovered 2026-09-07 (FOUNDRY, code-review sweep).

## spec
- **The script** (`src/RimMandrake/Utils/ashkarr_layer_nightside.py`, 2026-08-23) carves a
  `HorrorWastes` band and a `BMT_CrystalCaverns`/`AB_PropaneLakes` deep-cold split out of
  `AB_RockyCrags`, per the owner's 2026-08-23 ruling: *"eliminating any RockyCrags that are
  still above freezing"* as part of the hot-to-cold nightside stack.
- **Both carve targets are now superseded**, discovered independently of and after this
  script was written:
  - `HorrorWastes` — 0 tiles remain (dissolved into the Blue Desert/ice sheet mosaic by
    `HORRORWASTES_BIOME_DISSOLVE_1`).
  - `BMT_CrystalCaverns` — 0 tiles remain, and `the_lantern_deeps.md` hard ban #1 now
    **forbids** it as a worldmap biome at all ("never holds a surface tile again" — it's
    the Lantern Deeps' injected cave-map layer instead, per `LANTERN_DEEPS_INJECTION_1`).
  - The script now refuses `--apply` outright when both read 0 (added this session) rather
    than silently recreating a dissolved band and writing a banned biome onto the worldmap.
- 🔴 **The substantive question this leaves open**: is the owner's actual underlying ruling
  — no `AB_RockyCrags` tile above freezing — still satisfied? The script's own docstring
  premise for that clause ("measured 2026-08-23, AB_RockyCrags holds zero tiles above 0 C")
  predates the 2026-09-07 savegame-export rebase (which changed biome on 5,411 tiles and
  hilliness on 7,275). A live report-mode run today shows `AB_RockyCrags` at 1,984 tiles
  with samples up to +15.0°C (region "Damp") and +13.7°C (region "Wither") — the ruling
  appears to be currently VIOLATED, not satisfied, on live data.
- **This needs a fresh mechanism, not a resurrection of the old one**: whatever fixes the
  above-freezing RockyCrags tiles today must NOT write `HorrorWastes` or
  `BMT_CrystalCaverns` back onto the worldmap (both routes are now closed). The owner
  should confirm: (a) is the "no RockyCrags above freezing" ruling still standing as
  written, and (b) if so, what should above-freezing RockyCrags convert TO now, given
  neither original destination survives.

## verify
Owner rules on (a)/(b) above; a new or adapted script converts the actual current
above-freezing `AB_RockyCrags` population to whatever the owner names, without touching
`HorrorWastes` or `BMT_CrystalCaverns`; a live report-mode run afterward shows 0
`AB_RockyCrags` tiles above 0°C.
