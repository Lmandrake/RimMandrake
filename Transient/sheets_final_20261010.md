# Sheets final 20261010

Nothing installed. Nothing re-queued.

## Batch 3 icons (24/24 rendered, all 128x128)
Metric: edge-black share vs interior (3px in) black share; OUTLINE only if edge>=0.10 and edge-interior>0.25. Script: Transient/icon_contact_batch3_20261010.py. Sheet: Transient/icon_renders_contact_batch3_20261010.png (old | new, labelled).
- Genuine outline failures: 0 of 24 (viewed the sheet). Highest edge-int gaps: MeatOnAStick 0.19, LittleMeatOnAStick 0.16, FungusOnAStick 0.13, FruitOnAStick 0.15: these are dark charred meat/mushroom edges, no drawn rim visible.
- Dark material, not outline: Iliss (0.33/0.32, black eel), SimpleResearchKit, BlendOnAStick.
- Subject drift to rule on: Noolim (old = shoal of many small fish, new = one large fish); Weloon (old olive-green turtle-like, new pale blue isopod); Aluun (old winged leaf, new white flower); Iliss new is mirrored vs old. Skewer meals read as roasted food rather than the old alien colours (old were stylised coloured); research kits are now opened cases, not the old bag/gadget icons. These are design changes, owner call.

## Gap art (10 jobs)
Sheet: Transient/gap_art_contact_20261010.png. All 8 rendered ones: correct size (512/128/256), fully transparent corners.
- SmallCrystal: OK, neutral white-grey (chroma 6), dyeable.
- CrawlSmear: OK, neutral dark grey-brown, soft edges.
- AssayFlecks Light/Heavy: transparent overlays, tree-footprint scatter, OK. Heavy is strongly orange/gold (chroma 85) vs Light silver/pale gold: intended gradation, check tint in game.
- Dewfall x5 (CrystalFlower, BloodBouquet, RedBugloss, KeeningCordax, GiantToxicFlower): good dew-bead renders but each is a full redrawn plant; "same pose/silhouette as existing sprite" NOT verified (no side-by-side done). KeeningCordax is much sparser (cov 0.22) than the others.
- Dakkra_rest north/south: NOT RENDERED. artpipe failed/ has gap_RM_Dakkra_rest_v1_north and _south with note "master ls_regen_RM_Dakkra_rest_v1_east failed; derivation impossible". The east master later rendered (done/ and _artsrc/ls_regen_RM_Dakkra_rest_v1_east) but a stale failed copy also exists. NEXT: re-queue north/south now that the east master is done.
