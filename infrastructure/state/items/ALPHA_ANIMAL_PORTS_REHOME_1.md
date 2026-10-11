# ALPHA_ANIMAL_PORTS_REHOME_1 — Alpha Animals ports re-homed from RSW_ to RM_, donor art swapped for our own

Spec: `Transient/belt_art_wiring2_20261002.md`. Ruling: Q12 (RSW_ to RM_ per biome sitting).

## spec

Five Alpha Animals creatures carried RSW_-prefixed ports: Wildpawn (`RM_Durrok`), Wildpod (`RM_Mullgoth`), Cactipine (`RM_Chikka`), Needlepost (`RM_Skorra`), Terrorworm (`RM_Vurra`). Nysyllin is canon Star Wars and stays `RSW_`.

Done at `818c513d9`: all five renamed to `RM_`; Durrok and Mullgoth wear the finished Rot art.
Done at `3acc6123b`: Chikka (pick C) and Vurra (pick B) installed from the Leaning Scrub sheet through the art ledger, off donor art.

## remaining

Skorra is the only open row. Its art exists (artpipe set `gapall_RSW_Skorra_v1`, 3 facings, validator passed, in `D:\Luke\dev\_artpipe`) but is NOT installed: it is not owner-approved. Owner ruling 2026-10-11 (decision taken by question card; typed: "I meant cut from where I said cut not from game."): the `cut` on the Leaning Scrub sheet (`infrastructure/state/art_rulings/2026-10-08_leaningscrub_sheet_2026-10-05.decisions.json`, key `RM_Skorra`) removes Skorra from the Leaning Scrub roster only; Skorra stays in the game and in its other biomes. No `RM_Skorra` roster row remains in `src/` XML (checked 2026-10-11), so no roster edit is owed.

Next art review sheet: put `gapall_RSW_Skorra_v1` on it for his keep/replace ruling; `art install` places it only after that. The Greentide sheet's `RM_Skorra` "A" is a prefill and authorises nothing.

## criteria
Skorra's art ruled on a review sheet and installed (or replaced) through `art install`; no `RSW_`-prefixed port of the five remains.
