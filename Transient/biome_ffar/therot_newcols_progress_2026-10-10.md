# The Rot — new-columns enactment progress (2026-10-10)

Owner: "The updated ROT sheet has been processed due to the new art that was added. do not re-interpret any comments, they are simply the ones from before. Be careful."

## 1. Diff of decisions vs last committed (HEAD 7b75022a2), resolved letter->sha through both snapshots
No letters shifted (every old column keeps its sha). No note text changed (0 rows). 26 rows changed:
- Pick changed: RM_CrimsonCap A->G (render rotvar_crimsoncap_a_v1); RM_BlastpodShroom A->C (BoomshroomGrown_C, which he also ✕'d); AA_AngelMoth A->C (C = B's east+north, already live).
- New ✕ on folder pictures: CrimsonCap a-f (all six), Boomshroom Grown_B, Grown_C, Immature, FruitingBodyA/B/C, Flakespirefungus_b, GreyLadyImmature_a (+ render greyladyimmature_a_v1 and GreyLady A), RegenerantVeil_C, Brightbell A, Sagecrust A, MortalMorel A, VioletWimple A, Wrinklecap A, BleedingTooth A.
- New ticked variants (renders from today's rotvar jobs): GlowingAgarilux/Glowstool/LilacBeacon/SlimyPholiota/WitchesOyster B+C, AgelessCap D+E, Brightbell D+E, CrimsonCap G+H, FalseFruit C+D, FlakespireFungus C+D, FruitingBodies E+F, Blastpod E+F, MortalMorel F+G, Nuitae F+G, PaleTree D+E, Pusmelon C+D, RegenerantVeil D+E, Sagecrust D.
- New ticks on already-live pictures (no action): VioletWimple/Wrinklecap/MortalMorel E,F (re-encoded copies), Nuitae A, PaleTree A, AgelessCap A, Glowing/Glowstool/Lilac A, BleedingTooth B-F (sheet default tick).


## 2. Notes check
All 26 rows' note text is byte-identical to HEAD. No note acted on; nothing queued.


## 3. Enact plan / actions — DONE (`Transient/biome_ffar/therot_newcols_2026-10-10.py --apply`, log `therot_newcols_apply_2026-10-10.log`)
`art.py enact` dry run was NOT applied: it would install MortalMorel C/D and PaleTree B/C (letters unchanged since the
first enact), skip every row with a new ✕ but no pick re-click (purgeTouched without decidedAt reads as undecided, so
AgelessCap/Nuitae/RegenerantVeil/FruitingBodies/Flakespire ticks never install), drop CrimsonCap's pick G behind its
--mark-done, never place Blastpod E/F (by-name renders on a two-graphic row; the jobs target BoomshroomGrown), and move
21 open notes. The script applies only the changed actions:
- Ingest of the 23 changed rows only (47 rulings); 10 variant keeps recorded for ticks on purge-touched rows (ingest leaves them out).
- Installed 33 renders into their Graphic_Random folders (CrimsonCap g/h, Blastpod Grown e/f, FruitingBodies e/f, Flakespire c/d, AgelessCap d/e, Nuitae f/g, RegenerantVeil d/e, Brightbell d/e, FalseFruit c/d, Pusmelon c/d, Sagecrust d, MortalMorel f/g, PaleTree d/e, Glowing/Glowstool/Lilac/SlimyPholiota b/c).
- Retired 13 ✕'d folder pictures: CrimsonCap_a-f, BoomshroomGrown_B/C, FruitingBodyA/B/C, Flakespirefungus_b, RegenerantVeil_C. CrimsonCap_a carried his earlier pick-A keep from this same file; released by his ✕ here.
- Purged 21 ✕'d shas.
- Kept (✕ but the folder's only picture): BoomshroomImmature.png, GreyLadyImmature_a.png.

## Questions for BENCH (nothing done)
- RM_BlastpodShroom: he picked C and ✕'d C. The ✕ wins (enact rule), so C was retired; the grown folder is A + renders E/F. Confirm A should stay.
- RM_BlastpodShroom immature / RM_GreyLady immature: he ✕'d the only young picture (GreyLady also ✕'d the young render). Both kept. A young redraw is needed before they can go.
- AB_WitchesOyster B/C ticked: a single-texture plant (RotSpecies/WitchesOyster.png), no folder slot. Shipping them needs a def change to Graphic_Random. Not done.
- Out of scope, but enact keeps planning them: PaleTree B/C and MortalMorel C/D (ticked at the first ruling) are not live under those shas. MortalMorel C's pixels ship as MortalMorel_p3b. Decide whether they still owe an install.


## 4. Deploy — DONE
`deploy_custom_mods.py --compose biomes --apply --prune`: 46 files (33 added, 13 pruned), VERIFIED in sync. RimWorld was running; no DLL in the plan, nothing refused. Needs a game restart.


## 5. Landing
(pending)
