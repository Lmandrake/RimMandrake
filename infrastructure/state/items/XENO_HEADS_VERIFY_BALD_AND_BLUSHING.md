# XENO_HEADS_VERIFY_BALD_AND_BLUSHING

Owner (2026-10-20): *"I REALLY want to see a screenshot of aliens with these head types installed."*
First live shots (`D:\ClaudeWork\screenshots\2026-10-20\heads_lineup_ALL_FACINGS.png`,
`Transient/live_testing_2026-10-20d/RESULTS.md`) showed three defects in the four painted heads he picked.
Fixed OFFLINE (not deployed); this item is the live check. Needs: deploy StarWarsRaces + restart + bridge.

## What changed (all reversible; nothing repainted)
| defect | change | revert |
|---|---|---|
| Lasat rolls gene hair over the painted head | `RSW_RimMandrakeLasat`: `Outland_BaldMale` → `Hair_BaldOnly` | swap the gene back |
| Nelvaanian rolls gene hair over the painted head | `RSW_RimMandrakeNelvaanian`: `Hair_LongOnly` → `Hair_BaldOnly` (`Hair_InkBlack` left, now inert) | swap back |
| Mimbanese red head on a grey body | `RSW_RimMandrakeMimbanese`: removed `Outland_Skin_Brown` + `RSW_Skin_MidGray`, kept `Skin_DeepRed` (150,62,62 ≈ head mean 139,72,67). `RSW_Mimbanese_Head` gets `TabulaRasa.DefModExt_HeadTypeStuff` `shaderType CutoutComplex` + all-black masks `Heads/Mimbanese/Mimbanese_Head_{south,east,north}m.png` so the head draws as painted (the skin shader multiplied it by skin colour: measured ~0.65 grey in the first shot; red skin would have turned it near-black) | remove the 2 genes' deletion, the modExtension and the 3 mask PNGs |
| Ortolan head rides high facing east | `Heads/Ortolan/Ortolan_Head_east.png` translated 31 px down (bbox 94..365 → 125..396; cranium top/eye line now match south). Cause: `fit_head_canvas.py` aligns each facing's bbox BOTTOM, and the east bottom is an ear tip. No def-side per-facing head offset exists (HeadTypeDef and Tabula Rasa's ext have none). Art ledger: old sha `b25d03e3…`, new `d1bef40f…` | `art.py install` the old sha |
| Gene attachments drew a second set of ears/eyes/ridges over the painted heads (owner: *"I agree to all your proposed head efforts."*, 2026-10-20; design `design/RimStarWars/head_parts_painted_vs_attached_2026-10-20.md` rule 3) | removed, each judged against the PNGs: **Ortolan** `RSW_Eyes_Big`, `Ears_Floppy`; **Nelvaanian** `RSW_Eyes_Big`, `Outland_Ears_FlatPointed`; **Lasat** `Ears_Pointed`, `RSW_Eyes_BigYellow`, `RSW_Eyes_BigGreen`, `RSW_GS_Eyes_Yellow`; **Mimbanese** `RSW_FacialRidges_bumpy`, `RSW_FacialRidges_broad`, `RSW_Eyes_Big`, `RSW_Brow_Ridged`. `Ears_Human` (no render node) put in the ear slot of Ortolan, Nelvaanian, Lasat. All removed genes are render-node only (no stats, capacities or other references; READ from `SW_Genes.xml` and the def dump). KEPT: Lasat `RSW_FacialRidges_bumpy` (the painted Lasat head shows fur stripes, not ridges) and `RSW_Beard_Chops` (not in this pass) | put the genes back |
| Ortolan head blue-on-blue tinted (darker than body) | `RSW_Ortolan_Head` gets the Mimbanese treatment: `DefModExt_HeadTypeStuff` `shaderType CutoutComplex` + all-black masks `Heads/Ortolan/Ortolan_Head_{south,east,north}m.png`. Skin: `Skin_Blue` + `Outland_Skin_PaleAzure` → `Outland_Skin_DeepAzure` only (73,107,167; painted head mean, alpha>128, all facings 68,101,149, south 64,108,169) | remove the modExtension and 3 masks, restore the 2 skin genes |

Files: `src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`,
`src/RimStarWars/StarWarsRaces/Defs/HeadTypeDefs/SW_HeadTypes.xml`, the PNGs above,
writer `src/RimMandrake/Utils/art/head_facing_fix.py`.

## Verify live (checklist)
1. Deploy `StarWarsRaces` (`deploy_custom_mods.py --mod StarWarsRaces` plan, then `--apply`); restart. Harvest: 0 new
   signatures; no texture-miss for `Mimbanese_Head_*m` or `Ortolan_Head_east`; no config error naming
   `RSW_Mimbanese_Head` / `DefModExt_HeadTypeStuff`.
2. Load `XENO_HEADS_REVIEW_2026-10-20.rws` is NOT enough — existing pawns keep their rolled hair and skin. Spawn
   FRESH pawns: 4 Lasat (≥2 female: `Outland_BaldMale` let females roll hair), 3 Nelvaanian, 3 Mimbanese, 2 Ortolan
   (one Fat, one Hulk body), plus a human pair for scale; midday, Clear; FA must stay off (`Human-RSW_*` list).
3. State reads (bridge, before any picture): every Lasat/Nelvaanian `story.hairDef` = `Bald`; every Mimbanese
   `story.SkinColor` ≈ (0.59,0.24,0.24) and `headType` = `RSW_Mimbanese_Head`; every Ortolan `story.SkinColor` ≈
   (0.29,0.42,0.65). No pawn of the four species carries any gene removed above (`genes.GenesListForReading`);
   Ortolan/Nelvaanian/Lasat carry `Ears_Human`.
4. Pictures, all four facings (`shoot_lineup_facings.py --zoom 13`):
   - Lasat/Nelvaanian: no hair mesh over the painted head in any facing.
   - Mimbanese: body red, head the same red family and NOT darkened (compare with the painting
     `src/RimStarWars/StarWarsRaces/Textures/RimMandrakeSW/Heads/Mimbanese/Mimbanese_Head_south.png`); north and east too.
   - Ortolan east (and west, mirrored): head sits on the shoulders at the same height as south; north unchanged.
   - Ortolan: head the painted blue, NOT darker than the body (compare `Heads/Ortolan/Ortolan_Head_south.png`).
   - All four: no second ears, no extra black/yellow eyes below the painted ones, no ridge overlay on Mimbanese;
     Lasat still shows its `RSW_FacialRidges_bumpy` overlay (kept) — note whether it reads as wrong.
5. Pass → close with the shots' paths; fail → note which facing/species and the measured value.

## Watch out
- Still drawn over a painted head: Lasat `RSW_FacialRidges_bumpy` and `RSW_Beard_Chops` (males); not painted features, so kept this pass.
- Lasat and Nelvaanian heads are still skin-tinted (they looked right because skin ≈ painting hue); the same
  CutoutComplex + black mask would show them exactly as painted — owner's call.
- The mask route (Mimbanese, Ortolan) depends on Tabula Rasa (`neronix17.toolbox`, active); without it the head falls back to tinted.
- `SW_HeadTypes.xml`/`RimMandrakeXenotypes.xml` say "GENERATED by gen_races_mod.py", which is broken and must not be
  re-run; a future regen must fold these hand edits (as it did f19fc83a9's).
