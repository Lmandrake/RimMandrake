# Rot flora/fauna + new-art review sheet — build report (2026-09-18)

**55 rows.** Group A (flora) 40, Group B (fauna) 10, Group C (new art, other waves) 5.
`check_sheet.py`: **0 FAIL, 1 WARN, 33 ok, exit 0** (WARN is "55 rows missing from the
decisions file" — expected, nobody has reviewed it yet).

**Thumbnails: 50 of 55 (up from 28).** Two coordinator corrections in sequence:
(1) Alpha Biomes and Alpha Animals ARE locally reachable, at the Workshop ids
supplied (`1841354677`, `1541721856`), plus three `*ArtOverride` mods in the game's
own Mods folder that take priority where they exist; (2) the 4 AlphaBiomes plant
rows that read as "absent" (AB_Bryolux, AB_Glowstool, AB_Agarilux,
AB_GlowingAgarilux) are not a content gap at all — their texPaths
(`Things/Plant/Bryolux`/`Agarilux`/`Glowstool`, confirmed against
`.../1841354677/1.6/Defs/ThingDefs_Plants/Plants_MycoticJungle.xml`) are vanilla
Core cave-plant textures the donor mod deliberately reuses rather than shipping its
own (Core has stocked this art since 1.4), so they live in `resources.assets`
exactly like the RUT_PaleTree/RUT_PaleMoss/RUT_Emberscythe rows already extracted.
Pulled `BryoluxA`, `AgariluxA` (also covers AB_GlowingAgarilux, same texPath) and
`GlowstoolA` via UnityPy under Windows `python.exe` — bare letter-suffix
Graphic_Random names, no prefix, first alphabetically. Their art-status chip is now
`vanilla`, not `donor`.

**Only 5 rows remain with no thumbnail**, all the same reason: RUT_FalseFruit,
RUT_AgelessCap, RUT_RegenerantVeil, RUT_EuphoricCrown, RUT_FurnaceCap are
shared-placeholder RUT_ rows whose new-art jobs FAILED tonight on quota; their
placeholder texPaths (CrimsonCap / GreyLadyGrown / VioletWimple / FruitingBodies)
already have a thumbnail on THEIR OWN row (RUT_CrimsonCap, RUT_GreyLady,
RUT_VioletWimple, RUT_FruitingBodies) — not duplicated onto every def that reuses
the same texPath, to avoid five identical thumbnails scattered across the sheet
with no visual distinction.

## Group A — Rot flora (40 rows)
32 wildPlants entries in `RUT_TheRot.xml` + 5 patch-added (RotPaleTree_WildSpawn.xml,
RotGuardianGroves_WildSpawn.xml x4) + 3 non-wild RotSporeKit-only plant ThingDefs
(RUT_DulcisPlant, RUT_FurnaceCap, RUT_PaleMoss). Art: 20 owned (real PNGs on disk,
confirmed by folder listing), 9 donor (AlphaBiomes) resolved from
`/mnt/c/.../workshop/content/294100/1841354677/Textures/Things/Plants/...` (first
variant alphabetically per folder), 4 vanilla-reuse rows resolved from the base
`resources.assets` (AB_Bryolux, AB_Glowstool, AB_Agarilux, AB_GlowingAgarilux —
vanilla Core cave-plant art the donor mod deliberately reuses), 2 more
vanilla-reuse rows (RUT_PaleTree, RUT_PaleMoss) extracted from the Royalty
AssetBundle / base resources.assets, and 5 shared-placeholder rows still without
their own thumbnail (art queued, failed on quota tonight). RUT_DulcisPlant is owned
art that also got a same-day regen pass (dulciscropitem_v1 etc, PASS, not yet
wired) — noted on its row.

## Group B — Rot fauna (10 rows)
**MEASURED 9 wildAnimals in the live `RUT_TheRot.xml`, not the 15 the build brief
named.** Checked every `Patches/*.xml` for a patch adding the other 6 (all BMT_
cavern kinds named in `rot_fauna_assignment_draft_20260918.md`'s table) — none
exists. That draft's 15-row table reads as a proposed roster, not a landed one;
reported as measured (9) with the discrepancy flagged on the page, not silently
matched to the briefed number. Plus RUT_Emberscythe (ships in RotSporeKit, Pyrelands
not Rot) = 10 rows. Mend column prints "mend ∝ bodySize" per tonight's ruling, not a
flat number.

**All 10 rows now have a thumbnail and a real bodySize.** The 6 AA_ (Alpha Animals)
rows resolved from `.../1541721856/Textures/Things/Pawn/Animal/<defName>/<defName>_south.png`
(bodySize from `1.6/Defs/ThingDefs_Races/Races_*.xml`: Agaripod 4.0, Agaripawn 1.4,
MycoidColossus 6.0, Swarmling 0.3, Wildpawn 1.4, Wildpod 4.0); 3 of the 6
(Agaripod, MycoidColossus, Wildpod) use the game Mods folder's `*ArtOverride`
instead of the base donor art, since that override takes priority in the live load
order. RUT_Emberscythe's art (a deliberate vanilla Megascarab recolor per its own
header comment) is now extracted from the base `resources.assets`
(`Megascarab_south`). The 3 RSW_ (SWBestiary) rows were already owned art.

## Group C — new art landed, other waves (5 rows)
93 artpipe manifests finished after 2026-09-18 00:00 PDT. Excluded 39 canon_*
creature-fidelity renders (already served by their own sheet,
`Transient/canon_regen_wave1_2026-09-18/`) and 45 Lantern Deeps texture-slot
manifests (already served by `Transient/deeps_art_review_2026-09-18.html`) — showing
either again would be a second, disagreeing review surface over the same renders.
4 dulcis* jobs excluded too: their target (RUT_DulcisPlant) is already a Group A row
in this same sheet. Remaining 5: twisting thornweed (unrelated biome, genuinely new)
+ 4 Lantern Deeps puffer stages that finished AFTER that sibling sheet was built (it
still shows them "pending"). All 5: facts PASS, validator skipped (no reference),
checked `wired` via literal md5 match against every PNG under `src/**/Textures/` —
**0 of 5 wired.**

## Rules invented
Listed in full in `CONFIG.invented` inside the sheet itself (required by the skill,
never omitted) — same 7 items summarized above: the `<plant>`-block scoping rule for
Group A, the 9-vs-15 fauna discrepancy, the AA_/AB_ donor-unreachable calls, the
Group C exclusion scoping, and the md5-based `wired` definition.

## Outputs
- `src/RimUtinni/RotSporeKit/build_review_sheet.py`
- `Transient/rot_flora_fauna_review_2026-09-18.html`
- `Transient/rot_flora_fauna_review_2026-09-18.decisions.json` (posture: blacklist, default keep)
- `Transient/rot_review_thumbs_2026-09-18/` (28 PNGs, 160px max)
