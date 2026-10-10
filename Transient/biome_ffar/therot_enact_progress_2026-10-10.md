# The Rot enact progress 2026-10-10

## Phase 1 enact — DONE
- dry run: /home/mandrake/.seat-tmp/BENCH/rot_dry.log; apply: /home/mandrake/.seat-tmp/BENCH/rot_apply.log
- ingest 68 events; install 0 (35 already live, 2 donor pictures left); queued 2 redraws (AA_AnimaColossus, Snoruuk); purged 19; cut 0
- CONFLICTS 3: RM_Thozzik render B (3 facings) x'd on RM_Thozzik but kept-by-default as a variant on RM_ThozzikSpawned (same texture)
- TODO 32
- Rows enact treats as UNDECIDED (purge clicked, no letter click) but carrying his typed note: AA_AngelMoth, AB_AgariluxPrime, RM_AgelessCap, RM_Nuitae, RM_RegenerantVeil — notes acted on anyway (the note is his)

## Phase 2 traps — DONE
- enact_4b7d5ca2_animacolossus: note says "Regenerate (S)" -> east/north jobs withdrawn to _withdrawn/; south job re-pointed from the in-game donor south to his kept variant B east+north (derive_from cleared)
- enact_6811876e_snoruuk: canon_reference = in-game donor A south (he asked to follow the MLIE donor art; not rejected) — OK
- notes_followed set on AA_AnimaColossus and Snoruuk by enact
- AA_Agaripod pick B installed by hand into the fold slot src/RimMandrake/TheRot/Textures/Things/Pawn/Animal/RM_Agaripod (enact saw no slot because the donor texPath is redirected by Agaripod_ArtFold.xml)

## Phase 3 TODO rows — work done (BENCH verify brief applied: no coined names)
- Descriptions rewritten: AA_Agaripod, AB_AgaricusDomeCap, AB_AgariluxPrime (dangerous behaviour), AB_ArbuscularMycorrhiza, AB_DribblingCap, AB_GiantAgarilux, AB_GlowingAgarilux, AB_Glowstool, AB_LilacBeacon, AB_SlimyPholiota, AB_WitchesOyster, AA_AngelMoth (new block), RM_AgelessCap, RM_BlastpodShroom, RM_Brightbell, RM_Brogg, RM_CrimsonCap, RM_FalseFruit, RM_FlakespireFungus, RM_GreyLady, RM_MortalMorelPlant(+Growable), RM_Nuitae, RM_PaleTree, RM_Pusmelon, RM_RegenerantVeil, RM_Sagecrust, RM_Skulltop, RM_VioletWimple, RM_Wrinklecap, RM_TollukCap (the live Rot def for the AB_Agarilux row)
- AA_AnimaColossus: label pluur'va (his name), description regenerated, adult/juvenile/baby drawSize x3 (4/5/6 -> 12/15/18)
- RM_Brogg: alternateGraphics colour tints removed
- Renames with no name given: labels LEFT AS THEY ARE, question recorded (see Questions)
- Picks enact called "already live" but were not: installed by Transient/biome_ffar/therot_todo_installs_2026-10-10.py — Arpeau B(+C variant), Brightbell C, EuphoricCrown B, FalseFruit B, GreyLady B, MortalMorel B; clicked variants AgelessCap B, Nuitae B+C, RegenerantVeil C, Shinecap B/C (grown) D/E (immature); retired the un-picked in-game A of Pusmelon (BMT_PusmelonA) and Sagecrust (BMT_SagecrustA); Arpeau huge-plant footprints regenerated
- Variant jobs: 48 rotvar_* (2 per "two more variants" row, reference = his pick), rotrow_angelmoth_south_v1, rotrow_snoruuk_v2 (donor + canon image); Snoruuk v1 north/south given the canon image too
- Job audit: 56 Rot jobs, 0 reference a ✕'d/purged picture

## Phase 4 deploy — DONE
- `deploy_custom_mods.py --compose biomes --apply` (TheRot is folded into RimMandrake.Biomes): 84 files deployed, INCLUDING the composed DLLs, with RimWorldWin64 running — none refused. Needs a game restart.
- 22 stale files are in the game copy and not in the repo (e.g. TheRot BMT_PusmelonA/BMT_SagecrustA just retired, BMT_VioletWimpleA/B, Wrinkle1-4, ShinecapImmature_a/b, Seadew BMT_*). Graphic_Random draws them, so his picks are not exclusive in game until a `--prune` run.
- UtinniPatches not deployed: its only change is a comment in RUT_TheRot.xml.

## Questions for the owner (recorded with --mark-done --evidence "OWNER: ...")
- Renames with no name given — current label kept: skarrow dome (AB_AgaricusDomeCap), tolluk cap (AB_Agarilux row -> RM_TollukCap), bollusk trunk, ruvvak weeper, vokkun pillar, ithra glowcap, nubbik stool, quessa spire, glissik slimecap, turrok shelf, rhessa cap, vennik salve, gubbra gourd, angel moth.
  NOTE: for the 11 rows that also had variant jobs, the modified enact.py files the OWNER mark as "followed" and does NOT list it under CONFLICTS (the match-branch ignores OWNER: evidence) — the questions live only in the ledger events and here.
- RM_ThozzikSpawned: RM_Thozzik minus meat/leather and hasGenders, same art/faction, nothing spawns it but its 0.2 roster row — delete it?
- RM_ThozzikQueen: not a duplicate (wild hive queen vs tame RM_ThozzikColonyQueen) — keep both?
- RM_Thozzik: 3 render-B ✕s not purged because RM_ThozzikSpawned's default-ticked variant B keeps them.

## Stale-sheet notes
- RM_MortalMorelPlant: sheet column A (IN GAME 88d5e0e2) was not what the slot held (render D 094319d5).
- Arpeau, Brightbell, MortalMorel, Nuitae, Shinecap folders hold _p3a/_p3b pictures, and Pusmelon/Sagecrust BMT_*B pictures, never shown on the sheet; left in place.
- AB_Agarilux row shows the donor texPath art; the Rot roster now carries RM_TollukCap, which draws different art.
- Undecided rows (no click at all, prefill only): AA_Agaripawn, AA_Swarmling (its A is a render, not in game), AB_RecurvedStropharia, RM_BleedingTooth, RM_Brullith, RM_Dewshrooms, RM_Durrok, RM_Grellik, RM_Mullgoth, RM_Shambles, RM_Skerrith, RM_ThozzikColony, RM_ThozzikColonyQueen.

## Final enact state
TODO 0, CONFLICTS 8 (3 Thozzik purges + 5 OWNER questions)

## Commits
pending
