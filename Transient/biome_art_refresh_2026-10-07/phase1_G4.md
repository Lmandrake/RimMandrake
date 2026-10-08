# Phase 1 G4

## webwork
**Are the 23 decisions real human picks? Yes, they are real clicks, not prefill.** All 23 rows carry `decidedAt` (14:14:19Z to 14:33:26Z on 2026-10-07, one ~19 min sitting, 07:14-07:33 PDT). 20 of 23 differ from the prefill (`prefill` is "A" everywhere; only Brennoth, Ruddreth, Sorrivel stay A), 11 carry typed notes in his voice (e.g. Dulloth "Huge flat leaves ... Make it twice as big", Tooke "Please follow the original in-game version more closle,y"), and `variantsAt` stamps interleave within seconds of the decision clicks (explicit variant clicks; only Dulloth and TookeTrap have `variantsDefault: true`, i.e. UI default). Sidecar writeCount 128, savedBy review-sheet-sidecar, file mtime 07:36 PDT. `reviewStatus` still says "prefill" only because no one stamped it `ruled` (he typed no "sheet done" line); ingest ran on the decidedAt rows regardless (43 rulings, art.py status shows the 2026-10-07 keeps/redos). Do NOT stamp it ruled without his typed words.

Executed already (git ae9493dd9 "Collect finished art ... Webwork redo singles"): Brimlock, Kessaroth, Pellareth, Varrisk redo singles, Skennet x3, Cravvet east (v3 regen = live east 715dc630) are installed in src/RimMandrake/Webwork/Textures.

Leads (keep_not_live, 21 entries): all EXECUTED.
- Cravvet main B + variant B (2/3 on disk): EXECUTED. B north/south (d187e03a, 80bc56e6) are live; B east was the old v2 east, which he purged (164c8ac5 PURGED, keep released) with the note "Needs regen of the East facing"; the regen webwork_cravvet_east_regen_v3_east is done and installed as live east 715dc630.
- Skennet variant B and C (0/3): EXECUTED/superseded. Variant clicks (14:17:20) came before his redo+purge (14:18:03); the purge of those shas ran (PURGED, keeps released). Redo v3 east/north/south installed live (ae9493dd9).
- Kessaroth variant B (0/1): EXECUTED/superseded the same way (b6bad88d purged after variant click); redo v2 installed.
- Plant `_byname` B and `variant` B for Brennoth, Dulloth, Kollavane, Pellareth, Ruddreth, Sorrivel (12 entries), plus variant B for Quarrok (0/3), Sivvern (0/3), Varrisk (0/1): EXECUTED as protected keeps. Each sha has a 2026-10-07 `keep` ruling and art.py/ledger `protected`; the bytes are in the art store. `_byname` is the by-name render group (webwork_plant_<x>) with no texPath slot, so there is nothing to install. Quarrok/Sivvern main C and the A mains are live. Caveat for the owner only if wanted: for Brennoth/Ruddreth/Sorrivel he chose A (in game) and kept the by-name render B as an alternative; if he meant B to replace A the sheet decision would have said B.
- Plant_TookeTrap_Wild variant B (0/1): EXECUTED (protected keep 4bf9fbb9). Tooke redo status (record only, no regen proposed): his decision is `redo` ("follow the original in-game version more closely, this is a canon render"). webwork_tooketrap_redo_v2 and _v3 are both in artpipe failed/; the v3 render exists at /mnt/d/Luke/dev/_artpipe/_artsrc/webwork_tooketrap_redo_v3/webwork_tooketrap_redo_v3.png (failed the validator: small/off-centre). He will judge it himself; nothing installed.

Other leads:
- Plant_TookeTrap_Wild redo_nojob: NEEDS-OWNER (see above; both jobs failed validation, v3 render awaits his own judgement). No regen proposed.
- RM_Brimlock purge `9e0e6c1d33b1` (purge_on_disk): NEEDS-OWNER. That is the rejected webwork_plant_brimlock render, but identical bytes are the live art of RM_Venomvine_a.png (src/RimMandrake/EnvironmentalHazards/Textures/Things/Plant/RM_Venomvine/) and RSW_Kudda_east.png (src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/RSW_Kudda/). Purging would strip two other defs; ingest refused correctly. Brimlock itself already has a new redo render installed. Ask whether he wants Venomvine and Kudda east re-rendered.

Redo renders finished but NOT installed (await his pick; not leads): Dulloth v2 (8d8446d2), Kollavane v2a/b/c, Norrveth v2a/b/c, Vennick v3 east/north/south (all done/ records present). For parity with the singles installed in ae9493dd9, a lead could install Dulloth's single: `art.py install Webwork Things/Plant/RM_Dulloth/RM_Dulloth_a.png <sha from _artsrc/webwork_dulloth_redo_v2> --reason artpipe-collect` (dry-run first; refused if Dulloth A counts as owner-kept via variantsDefault). Kollavane/Norrveth asked for "variants" and need Graphic_Random wiring after he picks, so they are not mechanical. Note the size requests (Dulloth twice, Kollavane 50%, Norrveth twice) went into the render prompts only; no def drawSize was changed.
## pyrelands
Decisions with decidedAt: RM_FireHawk (M, note asking for ground-walk + flying art) and RSW_Orray (F). Other rows are purge-only clicks. reviewStatus ruled ("Finished pyrelands").

Leads (keep_not_live, 2), both on RSW_Orray:
- RSW_Orray variant A (0/3 on disk): EXECUTED as a protected alternative. `variants:["A","F","G"]` with `variantsDefault:true` = UI default, not a click; ingest recorded keep rulings with `variant_of: F` (art.py status RSW_Orray shows three 2026-10-07 keep rulings). Variants are never installed (ledger design: protected alternatives may stay undeployed). A's bytes are the repo copy of the 2026-09-20 set. No variant slot exists in the def. Nothing to run.
- RSW_Orray variant G (2/3): EXECUTED the same way. Note: G south = `2a7aa4433e9f`, which is in his own purge list and now PURGED; G east/north equal F (live). Cosmetic conflict only (a kept variant containing one purged picture); no action unless he wants G's south replaced. Not an install target.
- RSW_Orray main F: EXECUTED. Live OrrayArtOverride shas 3f25a5d6/1ec66634/cf76274a equal F's east/north/south (3/3 live), his purges show PURGED in art.py status.

Non-lead observations:
- RM_FireHawk (M): owned by a separate agent per the 2026-10-07 owner instruction; the note is an edit request (ground-walk art + separate flying art), not executed here. Out of scope; flagged.
- Gizka female south `3599473822d4` purge refused by ingest (live at GizkaArtOverride GizkaW_south.png; his pick A needs installing onto GizkaW_*). Close record says it needs his typed words: NEEDS-OWNER (not a keep_not_live lead).
- FireWasp frame 8 east job `pyrelands_firewasp_flight8_8r_east` was pending at close (close record item 8).
## rustcathedral
Decisions with decidedAt (all 5 real, notes typed, reviewStatus ruled "rust cathedral sheet done."): GR_Mecharat hold ("cut no longer need"), RM_CathedralRoach A ("smaller than a rat"), RM_CoolantEelCatch A + picks _byname C, RM_LivingBolt redo (chrome nut and bolt note), RSW_Vozzik B + purge of the C set.

Lead (keep_not_live, 1):
- RM_CoolantEelCatch main A (0/1): EXECUTED. Column A is the vanilla donor Dogfish picture; the def's texPath is already `Things/Item/Fish/Dogfish` (src/RimMandrake/RustCathedral/Defs/ThingDefs_Items/RM_CoolantEelCatch.xml:40) and the ledger holds two keep rulings. Nothing to copy. False positive.

Other lines on this sheet (not keep_not_live leads):
- RSW_Vozzik B: EXECUTED. SWBestiary RSW_Vozzik_{east,north,south}.png shas aed6bf8a/6607239b/54eaebc7 equal B.
- RSW_Vozzik purge of column C (`a629e6f73237`, `f398a29e7916`, `ade25a4b9d3a`): NEEDS-OWNER. Those bytes are the live art of a different def, RM_Vozzik (src/RimMandrake/Stillsand/Textures/Things/Pawn/Animal/RM_Vozzik/, in Stillsand, Warscar, NightsideIce rosters). Ingest refused. Purging strips a shipping creature's art, and a 2026-10-05 deep-desert ruling on the same subject said "This should go into the Warscar". If he confirms: install B onto RM_Vozzik (`art.py install Stillsand Things/Pawn/Animal/RM_Vozzik/RM_Vozzik_<dir>.png <B sha of dir> --ruling <id>`) for east/north/south, then `art.py purge <sha>` x3 with his typed words.
- RM_LivingBolt redo: EXECUTED. Body jobs rustcathedral_livingbolt_v1_{east,south,north} done 2026-10-06 and corpse jobs rustcathedral_livingbolt_corpse_v1_* done 2026-10-07 (in _artsrc); live art is still the rejected B (cfce652f). Not installed on purpose: they await his judgment as new columns on a rebuilt sheet (sheet rebuild not run). No regen proposed.
- RM_CathedralRoach A and GR_Mecharat cut: EXECUTED per close record (roach live, size edits made, Mecharat removed from wildAnimals).
## thesump
Decisions with decidedAt: 10 real rows with typed notes (Brommet hold/cut, Dredgel redo, Skelver A "variants please", Soffeth redo, SumpMouse redo, Thrummel/Broodmother/Warden redo, Hssiss redo + Swimming pick B, Wick hold/cut). reviewStatus ruled ("Sump done").

Leads (keep_not_live): none. The audit has only keep_live (RM_Skelver A, RSW_Hssiss Swimming B) and redo/purge items:
- RM_Skelver main A: EXECUTED (live, 1/1). Note "variants please": jobs thesump_Skelver_var1..3 are all DONE in artpipe done/ and _artsrc; they are unwired alternatives awaiting his pick (close record: Graphic_Random wiring owed when he picks). NEEDS-OWNER to pick, not mechanical.
- RSW_Hssiss Swimming pick B: EXECUTED (live 3/3). Redo (canon precisely) jobs thesump_Hssiss_v2_{east,south,north} DONE; await his review.
- Redo rows Dredgel, Soffeth (+var1-3), SumpMouse, Thrummel, Broodmother, Warden, Hssiss: EXECUTED - every job in thesump_jobs_2026-10-05.json (38) has a finished done/ record; nothing missing, no regen needed (artpipe_state find confirmed for skelver/livingbolt-style checks; done/ checked for all 38 ids).
- RM_Dredgel purge `2ca18c6ede1b` (purge_on_disk, in TheSump RM_Dredgel_{south,north}.png and east): NEEDS-OWNER. It is the live picture in all three facings (one image copied to every direction, his complaint). Ingest refused until a replacement is live. Replacement renders exist (column D north f2a5b3f5 / south 39e45d48; v2 jobs done) but he has not picked them; installing unreviewed renders over art he said he likes is his call. Once he picks: `art.py install TheSump Things/Pawn/Animal/RM_Dredgel/RM_Dredgel_<dir>.png <sha> --ruling <id>` x3, then `art.py purge 2ca18c6ede1bbe0239a6b3a6f880c971f8bacc8ea422ce0c6ae0920185d28212` with his typed words.
- Brommet / Wick cuts: EXECUTED per close record (removed from RM_TheSump wildAnimals/wildPlants).
## warscar
Decisions with decidedAt: 8 real rows, typed notes on 6 (Helixien B "Rename to Bileworm", SpinedGow hold "Cut this", CrystalFairyMole hold "cut", Mynock redo, Juggernautbeetles B "Redo description"; Megaphorid redo, Electricgryllotalpa/Electrictick B no note). reviewStatus ruled ("Done with Warscar").

Leads (keep_not_live, 2):
- AA_SpinedGow graphics AA_SpinedGowFemale B and AA_SpinedGowMale C (0/3 each): EXECUTED. Row decision is `hold` ("Cut this, no longer needed"); the B/C `picks` are UI leftovers on a cut row, not art rulings. Cut done per close record: no AA_SpinedGow in src/RimMandrake/Scarlands/Defs/BiomeDefs/RM_Warscar.xml (grep 0); only residue is donor wildBiomes evictions in BiomeCastEvictions_WildBiomes.xml (not a cast). Nothing to install. False positive.

Other lines (not keep_not_live leads):
- AA_Helixien B: EXECUTED. Renamed Bileworm in src/RimUtinni/UtinniPatches/Patches/Warscar_Rename.xml (donor def, no owned texPath so no install; Warscar casts the port RM_Bileworm).
- SW_Electricgryllotalpa B, SW_Electrictick B, SW_Juggernautbeetles B: EXECUTED as donor picks (live 3/3 = the donor art; no owned texPath). Juggernaut "redo description" was carried by the RM_JuggernautBeetle port (WARSCAR_SHEET_DONOR_PORT_1), which carries the description itself.
- RSW_Mynock redo + RSW_MegaphoridLarva redo: EXECUTED. All jobs in warscar_jobs_2026-10-05.json (warscar_Mynock_v2, warscar_MegaphoridLarva_v2 east/north/south) have done/ records; renders await his review, none installed. Mynock purge of the 3 render shas ran (0 on disk).
- AA_SpinedGow/CrystalFairyMole cuts: EXECUTED per close record.
## Summary
| sheet | leads | executed | unexecuted-mechanical | needs-owner | proposed-regen |
|---|---|---|---|---|---|
| webwork | 23 (21 keep_not_live + Brimlock purge + Tooke redo) | 21 | 0 | 2 (Brimlock purge shared with Venomvine/Kudda; TookeTrap v3 owner judges) | 0 |
| pyrelands | 2 | 2 | 0 | 0 (side note: Gizka female south purge needs his words; FireHawk is another agent's) | 0 |
| rustcathedral | 2 (1 keep_not_live + Vozzik purge) | 1 | 0 | 1 (Vozzik C purge hits live RM_Vozzik in Stillsand) | 0 |
| thesump | 1 (Dredgel purge; no keep_not_live) | 0 | 0 | 1 (Dredgel purge awaits his pick of v2 renders) | 0 |
| warscar | 2 | 2 | 0 | 0 | 0 |
| total | 30 | 26 | 0 | 4 | 0 |

Common false-positive causes confirmed: variant/_byname keeps are protected alternatives (never installed); keeps on cut (`hold`) rows; vanilla/donor texPaths; purges that supersede an earlier variant click.
