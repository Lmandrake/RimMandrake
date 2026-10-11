# CANON_MATERIALS_BUILD_1 — build the decided canon materials design

## spec
Spec: `design/RimMandrake/canon_materials_design_2026-10-09.md`, the single source of truth: §0 (rulings),
§3 (materials, sources, defs), §4 (key jobs held as preferences), §5 (save migration), §6 duties 1–6. Parent:
CANON_MATERIALS_DESIGN_1. The owner ruled the frame and the fabrication and census questions on 2026-10-09
(his typed words and the card decisions are in the design's §0 and on this item's notes). Nothing here checks
a part's era (*"Not a great idea, ignore"*).

Split out to their own FOUNDRY items, not built here: `SHIP_ALLOY_FORGE_1` (alloy forge, progressive
unlocks, plasteel recipe, durasteel from steel + zersium), `ASTEROID_DESERT_ORES_1` (doonium asteroid ore
with glower crust, desert phrikite), `GLASS_TO_TRANSPARISTEEL_1`, `MATERIAL_MERGES_CLEANUP_1` (merges and
bronzium removal), `BESKAR_ARMORER_QUEST_1`.

## criteria
- L1 L0: `RSW_Durasteel` exists in the RimStarWars tier with `KOTOR_AlloyDurasteel`'s stats, sharp armor power raised to 0.9; no mineable or deep-drill producer makes it; `kotor_IngotDurasteel_recipe` (+10×, steel + uranium) removed
- L2 L0: every donor durasteel of §3.2 converts to or yields `RSW_Durasteel` and is no longer produced; durasteel salvage (slag, ship chunks) re-melts to `RSW_Durasteel` aboard; donor defs stay loadable for saves
- L3 L0: both recipe audits done and written into this item: fixed `Plasteel` costs untouched where the consumer needs plasteel, durasteel references redirected, broad filters admitting both listed
- L4 L0: the only recipe that makes `Plasteel` from other materials is the alloy forge's (owned by `SHIP_ALLOY_FORGE_1`); `Make_PlasteelGF` and `kotor_Plasteel_recipe` (+10×) removed; plasteel salvage re-melts aboard; Odyssey asteroid generation (`SpaceMapGenerator.xml`, `GeneratedLocations.xml` paths) no longer places `MineablePlasteel` or `MineableComponentsIndustrial`, by explicit allowlist
- L5 L0: salvage (ship chunks, crashed ships, B1 remains) yields durasteel, plasteel, duranium and doonium by composition, with no double plasteel route from B1 remains
- L6 L0: `RSW_Duranium`, `RSW_Doonium`, `RSW_Phrik`, `RSW_Transparisteel`, `RSW_Stygium`, `RSW_Coaxium` defined with canon descriptions and stocked by orbital traders and the Bazaar; stygium and coaxium have no other source; donor stygium items convert to `RSW_Stygium`; stygium's description says it cloaks ships
- L7 L0: beskar is never reforged by the colony: `kotor_IngotBeskar_recipe` (+10×) removed; smelting beskar or anything made of it yields lesser ores (steel, slag), never beskar; beskar mining routes produce nothing
- L8 L0: the §3.9 roles are in the defs' descriptions: `RM_CloakLacquer` personal camouflage only (never a ship); `RUT_Mindstone` the droid-mind crystal; `RSW_Leather_KraytDragon` an ordinary top leather with no heirloom or quest rule
- L9 L0: the six key jobs of §4 are preferences only: each names its right material in the layout's grading, and no recipe or building enforces it through a fixed ingredient list
- L10 L1: one minimal-list load with the touched mods shows no config or cross-reference errors naming any def above

## open question for the owner (L9) — nothing that depends on it is built

Two of your rulings on the six key jobs disagree, and the build waits for you to pick one.

- **Earlier, typed 2026-10-09** (design §0, §4, and L9 above): *"Yes, hold hard rules, wait for census"*, recorded as
  every key job being a preference: any eligible material works; the right one just gives the best result.
- **Later, by question card 2026-10-09 15:01** (BENCH note on this item, 23:06Z): durasteel is hard nowhere, but
  **plasteel is required** for droid shells and for prosthetics and implants, **duranium is required** for large frames,
  and **doonium is required** for reactor and ship cores.

**Question: should those four jobs refuse every other material (the card), or stay preferences (the earlier hold)?**

What each choice costs, from the census (`Transient/canon_materials_l9_census_20261011.csv`):

- **Required (the card).** The rare-material hunt gets real teeth: a wreck with a duranium frame becomes the thing that
  lets you build a factory. But duranium and doonium come only from salvage, rare trade and (doonium) asteroids, so a
  colony that has not found them cannot build those machines at all. The design's own rule says a gravship-gated supply
  must never block the first gravship, so cores and frames on that ship would need a ground salvage route first.
  It also means changing recipes: today no large frame uses duranium and no core uses doonium (the census finds about
  30 large-frame defs, by a keyword rule that catches some noise, and 35 core defs), and the 2 droid-shell defs use
  steel. Prosthetics already require plasteel in 80 places, so that row changes little. The census you said to wait for
  now exists.
- **Preferences (the earlier hold).** Nothing is ever refused and no existing recipe has to change; the right material
  only builds better (stronger, lighter, faster) as the layout page grades it. The rare finds matter less, because
  steel always works.
- **Mixed** is possible too, e.g. required only for the two big-build rows (duranium frames, doonium cores) and a
  preference for the plasteel rows, or the reverse.

## verify
Record each with `rimflow verify CANON_MATERIALS_BUILD_1 --criterion <ID> --result pass|fail|partial --evidence <path>`.
L0 is offline (def parse, validate_patch, selftests); L1 is one minimal-list load read through Player.log.
Do not add key-job exclusivity: the owner held those rules as preferences.
