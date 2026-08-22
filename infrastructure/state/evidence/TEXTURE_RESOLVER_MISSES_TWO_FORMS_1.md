# TEXTURE_RESOLVER_MISSES_TWO_FORMS_1 — evidence

REP, 2026-08-22. Measured against the live 578-mod load set (47,864 loose PNGs in
the Textures/ roots, 17,742 bundle names) and the 190-plant fixture
`design/Jawa/mods/plant_sprites/manifest.json`.

## The item said two forms. There were four.

| rung | example that failed before | where |
|---|---|---|
| bare-capital | `Plant_Agave` → `AgaveA.png` | loose |
| infix | `AB_HardyGrass` → `GrassA_Leafless.png` | loose |
| the `Graphic_Random` DIRECTORY | `Plant_Dandelion` → `dandelion/dandeliona.png` | loose |
| bundle directory, DIFFERENT stem | `Things/Plant/RG_Bush` → `rg_bush/busha.png` | bundle |

The last one is the one that hid the most: the texPath names a container and the
flattened entries inside are named for something else, so **no suffix on the
texPath's own stem can ever reach them**. Every ReGrowth retexture of a vanilla
plant lives there. The bundle cache is now indexed by containing directory as
well as by stem, matched from the right-hand end because a container path runs
deeper than the texPath.

## Result

| | before | after |
|---|---|---|
| plants that failed to resolve | **70 of 190** | **0 of 189 tested** |
| resolved to a different file than the fixture | 1 | 48 — of which **47 are a sibling variant of the same sprite** |

🔑 The single genuine difference is an improvement: `AB_SlimyPholiota` now takes
`AB_SlimyPholiotaA.png` where the fixture recorded `AB_SlimyPholiotaA copy.png`.

## The negative case — the one that matters

```
Plant_Berry_Leafless  Things/Plant/BerryPlant_Leafless
  -> None  (None)
  VERDICT: PASS - correctly unresolved
```

Its stem changed (ReGrowth's art is `BerryBush_Leafless*`), so only fuzzy matching
would reach it — and fuzzy matching is what put one mod's sprite on 42 Imperial
garments. ⭐ **A resolver that finds everything cannot tell MISSING from NOT FOUND,
which is its entire job.**

## Two defects found while verifying, both worth keeping

🔴 **The fast unit test caught a bug the slow fixture had MASKED.**
`VARIANT_LETTERS` is uppercase and every texture-index key is lowercased, so the
two loose rungs matched nothing. The 190-plant run still looked healthy because
other rungs happened to cover the same defs. ⇒ A fixture that exercises whole
behaviours can pass while a component inside it is dead.

⚠️ **The fixture silently skipped its own regression case.** The manifest entry for
`Plant_Berry_Leafless` carries no `texPath` key at all — only `missing`/`why` — so
a harness iterating on `texPath` skipped it and reported a clean sweep of 190.
`verify_resolve_texture_live.py` now names that path literally instead of reading
it from the fixture.

## What runs this again

```
python3 src/RimMandrake/Utils/test_resolve_texture.py            # 11 cases, instant
python3 src/RimMandrake/Utils/verify_resolve_texture_live.py     # the live set, ~4 min
```

## Not done, deliberately

`observed/inventory/sheets_plants/plants_sheet_index.csv` is **marked stale, not
refreshed** — it is gitignored (`.gitignore:198`), so refreshing it is a rebuild
needing a dump that matches the live mod list, not an edit. Marker written beside
it as `_STALE_2026-08-22.txt`, and the finding is on the item as a ledger note
because that marker is itself gitignored and will not survive a fresh checkout.
