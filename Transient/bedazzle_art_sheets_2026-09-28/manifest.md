# Bedazzle art review sheets — manifest (2026-09-28)

Four sheets, one per biome, built by `build_sheets.py` in this folder (chrome copied
verbatim from the reviewed `Transient/contagion_cast_art_review/sheet.html`; only
CONFIG/ITEMS swapped). All four pass `check_sheet.py` with **0 FAIL** (1 WARN each:
the decisions file has no per-row entries yet — expected for a fresh prefill
scaffold, same as the contagion sheet shipped with). Contagion's own sheet was NOT
touched.

## Job census (artpipe, measured 2026-09-28)

Every job of all four sittings is DONE — `pending/` and `active/` hold zero `*.json`,
`failed/` holds none of these sittings, and all 97 renders exist at
`infrastructure/artpipe/_artsrc/<job>/<job>.png` (97/97 present).

| Sitting | jobs done | pending | subjects | sheet |
|---|---|---|---|---|
| BLUEDESERT_BEDAZZLE_SITTING_1 | 11 | 0 | 5 | `blue_desert/sheet.html` |
| FLOODEDCANYON_BEDAZZLE_SITTING_1 (Cracked Lands) | 19 | 0 | 11 | `cracked_lands/sheet.html` |
| WASTELAND_BEDAZZLE_SITTING_1 | 48 | 0 | 22 | `wasteland/sheet.html` |
| CAULDRON_BEDAZZLE_SITTING_1 | 19 | 0 | 13 | `cauldron/sheet.html` |

Faced creatures (south/east/north = 3 jobs each): blue_desert 3, cracked_lands 4,
wasteland 13, cauldron 3. Everything else is a single render.

## Wired textures (repo copy only — NOT deployed)

Only 4 of 51 subjects have a def in the repo today (defName sweep over 1,744
`src/**/Defs|Patches/**/*.xml`; sanity probe RM_ToxinSealant/RM_Greatbole both hit).

| Subject | wired to | notes |
|---|---|---|
| RM_Tekk | `src/RimMandrake/Wasteland/Textures/Things/Item/Resource/RM_Tekk.png` | replaced the byte-for-byte RUT_Hardwood placeholder |
| RM_Drazz | `src/RimMandrake/Wasteland/Textures/Things/Item/Resource/RM_Drazz.png` | texPath repointed off the unguarded AB_CrystalHorn donor path (def edit in `RM_WastelandBrine_Items.xml`) |
| RM_BrinePlate | `src/RimMandrake/Wasteland/Textures/Things/Item/Resource/RM_BrinePlate.png` | same repoint (both defs shared ONE donor texPath, so neither could carry its own art without it) |
| RUT_CrackWax | `src/RimUtinni/UtinniPatches/Textures/Things/Item/Resource/RUT_CrackWax/RUT_CrackWax.png` | Graphic_StackCount folder form, like RUT_Bitumen. ⚠ the def carries `<color>(222,210,176)</color>` which will tint the full-colour render slightly warm — judge in game, drop the tint if it muddies |

Both defs files' header comments were corrected in the same change (the old text
described the placeholder state and would have been false once wired).

## Awaits def build (47 subjects — art staged on sheets only, no defs invented)

- **Blue Desert (5):** RM_BlueIce, RM_Murrek, RM_Ossivel, RM_Vhaulk, RM_Virr
- **Cracked Lands (10):** RM_CrackWaxSuit, RM_FossilDeepStratum, RM_FossilImpression,
  RM_FossilSkeleton, RM_Irqit, RM_Muttavaq, RM_Swale, RM_Tarruq, RM_Uttaqar, RM_Veqma
- **Wasteland (19):** RM_Boilbulb, RM_Boilhide, RM_Cinderfelt, RM_Gravelgut,
  RM_Grimewing, RM_Gristleswarm, RM_Middenbeetle, RM_Middenshell, RM_Pusberry,
  RM_Scabspinner, RM_Scumgrass, RM_Scumrat, RM_Slagmole, RM_Sloghog, RM_Smolderback,
  RM_SootGristleswarm, RM_Sootgrazer, RM_TallScumgrass, RM_Wartshrub
- **Cauldron (13):** RM_CauldronVent, RM_CorrodedCondenserStack, RM_CorrodedShrine,
  RM_CorrodedWellhead, RM_Eskith, RM_FilterCartridge, RM_FilterWorks,
  RM_GasTapScaffold, RM_Seismograph, RM_Vexxiss, RM_Vexxith, RM_Xithess, RM_Zisska

Their rows are tagged `[awaits def build]` on the sheets; wiring happens with each
biome's RULED_CONTENT / MECHANICS build.

## Open at (file fallback — no sidecar could be run from this subagent)

- `D:\Luke\dev\Rimworld\Transient\bedazzle_art_sheets_2026-09-28\blue_desert\sheet.html`
- `D:\Luke\dev\Rimworld\Transient\bedazzle_art_sheets_2026-09-28\cracked_lands\sheet.html`
- `D:\Luke\dev\Rimworld\Transient\bedazzle_art_sheets_2026-09-28\wasteland\sheet.html`
- `D:\Luke\dev\Rimworld\Transient\bedazzle_art_sheets_2026-09-28\cauldron\sheet.html`

Serving them live is one command each, from whoever holds a session:
`python3 /home/mandrake/.claude/skills/review-sheets/assets/serve_sheet.py --sheet <sheet.html> --decisions <decisions.json>`

Images are copied into each sheet's local `img/` so the pages work from disk.
Every row is prefilled **keep** (posture: blacklist — only improve/regenerate rows
spawn new art jobs). `decisions.json` files are prefill scaffolds
(`reviewStatus.state: "prefill"`); nothing has been ruled.
