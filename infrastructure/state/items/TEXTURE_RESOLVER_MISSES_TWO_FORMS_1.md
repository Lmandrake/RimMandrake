## spec
🔴 **`reading-rimworld-graphics`'s `resolve_texture()` ladder misses two real variant forms.
Together they accounted for 69 of 190 plant sprites** — a third of the set would have come
back "missing" from a resolver that is supposed to prove absence.

Measured 2026-08-22 while extracting sprites for `design/Jawa/mods/plant_review.html`
(189 of 190 resolved once the two forms were added):

1. **Bare-capital `Graphic_Random` suffixes.** texPath `Things/Plant/Grass` with files
   `GrassA.png`, `GrassB.png` — no separator before the letter. The ladder tries
   `Grass_a`, `Grass_A`, `Grass/a` and stops.
2. **The bundle DIRECTORY form.** The texPath names a container directory and the
   flattened files inside carry a **different stem**: `things/plant/rg_bush/busha.png`
   under texPath `Things/Plant/RG_Bush`.

Plus a third, smaller: an **infix** rule — `Grass_Leafless` → `GrassA_Leafless`.

## why it matters beyond plants
🔑 **The skill's whole promise is that it can tell "this texture does not exist" from "I
could not find it".** A ladder with holes reports the second as the first, and that is
exactly the failure `prove-art-missing-before-generating` exists to stop — someone
generates art for a sprite that was on disk the whole time.

## a second finding, separate and also worth keeping
⚠️ **The def dump's `texPath` values are POST-PATCH.** ReGrowth rewrites ~25 vanilla plants
to `Things/Plant/RG_*`. ⇒ **`plants_sheet_index.csv` (2026-08-15) is stale** for at least
`Plant_Dandelion`, `Plant_PincushionCactus` and `Plant_SaguaroCactus`. Anything keyed off
that file is resolving to paths the live game no longer uses.

## the one genuine miss, for calibration
`Plant_Berry_Leafless` (Odyssey) declares `Things/Plant/BerryPlant_Leafless`; ReGrowth moved
the art to `rg_berryplant_leafless/` with stem `BerryBush_Leafless*`. That is a **stem**
change, not a suffix change — only a fuzzy match would find it, and the skill rightly
forbids fuzzy matching. ✅ **Correct behaviour: report it missing with the reason.** Use it
as the regression case that must stay unresolved.

## verify
Re-run the resolver over the 190 defNames in `design/Jawa/mods/plant_cherrypick_candidates.csv`.
**189 must resolve; `Plant_Berry_Leafless` must NOT.** A working implementation of all three
rules exists in the sprite-extraction script that produced
`design/Jawa/mods/plant_sprites/manifest.json` — every entry there carries a `variant` field
naming which ladder rung fired, so the two new forms are traceable case by case.

## criteria
The ladder resolves the bare-capital and bundle-directory forms; `plants_sheet_index.csv` is
either refreshed or marked stale in place.

## note on ownership
Filed for REP because `reading-rimworld-graphics` is broadly shared (`skills/README.md`).
DECIDE used it and found this; DECIDE does not own it.
