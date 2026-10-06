# Sheet art redo — FOUNDRY, 2026-10-06 (numbers PROVISIONAL)

Items: RUSTCATHEDRAL_SHEET_ART_REDO_1, LANTERNDEEPS_SHEET_ART_REDO_1, NIGHTSIDEICE_SHEET_ART_REDO_1. Offline only, NOT committed.
Every install below: `artledger.install_file(..., reason="artpipe-collect")` (RIMFLOW_SEAT=FOUNDRY), artpipe job done + canon/facts PASS,
corners transparent, 0 magenta-flat, placeholder_detect `real`, facings viewed (east right-facing, north back, south front).
`art.py guard worktree`: 0 unledgered texture changes. Requeue jobs: `Transient/sheet_art_redo_requeue_20261006.json` (7, filed to artpipe pending).

## RUSTCATHEDRAL_SHEET_ART_REDO_1
- RM_LivingBolt: INSTALLED rustcathedral_livingbolt_v1 east/north/south over RustCathedral/Textures/Things/Pawn/Animal/RM_LivingBolt/.
- drawSize 0.1, roach size, Vozzik B, CoolantEelCatch, Mecharat cut: already done at the sitting (2026-10-05), nothing owed.
- Owed still: sheet rebuild (art_sheet.py is another agent's); RM_LivingBoltCorpse texture is missing (validate_patch flagged it before this pass).

## LANTERNDEEPS_SHEET_ART_REDO_1
- RM_BloodropMoth eyes: INSTALLED east/north/south.
- RM_MossBeetleLarvae eyes: INSTALLED north/south; east FAILED canon check (eye glint left) -> REQUEUED deeps_mossbeetlelarvae_eyes_v2_east.
- RM_Blinker v2 (three arms): INSTALLED east/north/south.
- RM_FacetMothLarvae eyes: all 3 FAILED validator (subject 2-3% past the reference footprint) -> REQUEUED v2 east/north/south with a footprint line.
- RM_Megapleura eyes: east/north pass, REFUSED by the ledger (live pictures owner-KEPT); south FAILED canon -> REQUEUED v2 south. Needs his ruling.
- RM_Gembug Blue eyes: all 3 pass, REFUSED by the ledger (owner-KEPT). Needs his ruling.
- Plant variants INSTALLED (next free letter, nothing overwritten): BrellikBulb C,D; Mycelium D,E; KuvraSpout c,d; NurrikGill C,D;
  PrennaLaceGrown D,E; QuorrFern E (varb FAILED -> REQUEUED v2); PufferGrown b (varc FAILED -> REQUEUED v2); VellokReed C,D; ZivvitTaper C,D.
- Gembug Green/Red/Yellow: NOT done. They are still the old donor-style pill bug, not a recolour of Blue; deriving them waits on the Blue ruling.

## NIGHTSIDEICE_SHEET_ART_REDO_1
- RSW_CaveLemming: INSTALLED nightsideice_cavelemming_v1 east/north/south over SWBestiary swanimals/.../CaveLemming/.
- AA_ShockGoat: INSTALLED to NightsideIce/Textures/Things/Pawn/Animal/AA_ShockGoat_NightsideIce/; WIRED by new
  NightsideIce/Patches/AA_ShockGoat_NightsideIce.xml (FindMod Alpha Animals, 3 lifeStages bodyGraphicData texPath; AA_Thunderbeast_BlueDesert shape).
- Tauntaun: INSTALLED to SWBestiary/Textures/Things/Pawn/Animal/RSW_Tauntaun_Canon/; WIRED by new SWBestiary/Patches/Tauntaun_CanonArt.xml
  (FindMod Star Wars Animal Collection (Continued), 3 lifeStages incl. taunlet; Vapaad_BlueDesertArt shape). Def stays the donor's.
- validate_patch --live on both patches: 0 errors, 0 warnings.

## Questions / skipped
- Megapleura (east/north) and Gembug Blue (3): eyeless / blue-gem renders pass, but the live pictures are owner-kept; installing needs his keep of the new sha.
- Gembug Green/Red/Yellow: should they be recolours of the accepted Blue (script tint) or new artpipe jobs?
- Tauntaun: the patch draws canon art on the donor def; is an RSW_Tauntaun port wanted, or is the patch enough?
- Desiccated graphics for ShockGoat/Tauntaun stay on donor art.
