# Facings needs-eyes sheet — enact follow-up (2026-10-17)

Sheet: Transient/biome_ffar/facing_regen_needs_eyes_sheet_2026-10-16.decisions.json (enact a372cc6e82).

## 1. TODOs
- DONE Blarth: picture C installed as swanimals/Blarth/BlarthV_C (art install), alternateGraphics 0.5 beside base D.
- DONE ColoClawFish: picture A (in-game, 4 facings) installed as ColoClawFishV_A, alternateGraphics 0.5 beside base C.
- DONE Gorg: adult drawSize 1.05 -> 0.5, younger stages in proportion (alternateGraphics kept).
- DONE Kreetle: adult drawSize 0.3 -> 0.5 (his "half a cell"; the sheet panel showed a stale 1-cell dump; 2026-10-08 ruling had set 0.3).
- DONE Varactyl: adult drawSize 4 -> 6 (6 cells long east); A out of the Varactyl_m pool: it is the only male base picture, its redraw is queued — nothing to remove until it lands.
- DONE OpeeSeaKiller: adult drawSize 2.25 -> 10; bodySize (1.4) left as is.
- DONE Hssiss: base A replaced by installed C; HssissA/B/C alternateGraphics removed (E/G/I out of pool). LEFT: re-add each HssissA/B/C entry when its queued redraw is kept.
- DONE Wampa: cub lifeStage draws the adult picture; Wampa_j (4 PNGs, b1 standtall) retired via ledger; Wampa_j redraw job withdrawn to _artpipe/_withdrawn.
- DONE MastiffPhalone: description rewritten from canon_references/mastiffphalone/description.md.

## 2. Cuts
- DONE RSW_KraytDragon cut: race file + its 2 eggs deleted; crossbreed lists (Greater, Kell) trimmed; RUT_KraytAttack sand-leviathan pawnKind -> RSW_GreaterKraytDragon; ExtremeDesert + Stillsand rosters drop it (Greater already there); MegafaunaYield, BeastNorm_Law3, AnimalBiomeDuplicates #258, TheReturn xpath, GiantSkeletons_Remains ops removed; 11 textures retired via ledger. KEPT: BodyDef RSW_KraytDragon (RSW_KellDragon uses it), leather/meat/sounds/skull (Greater, Kell, horn, den, skeletons use them).
- DONE RSW_Rycrit cut: race file, BodyDef, leather, meat, ate-meat thought, 4 sounds deleted; AnimalTolerances, Armour_Leather, PawnFlavor ops removed; 10 textures retired via ledger. Sound clips (Sounds/SWanimals/Pawn_Rycrit_*) left on disk, unreferenced.
- LEFT: historical records (design/*.json/.csv, art sheet snapshots, def_history) still name both — records, not live.

## 3. Yobshrimp
- DONE RSW_YobshrimpLand merged into RSW_Yobshrimp (SeaBeasts_Swarm.xml survives: it is the Miasma roster entry, the nursery juvenile parent and the redraw target). Moved over: canon description (rewritten to the purple canon look), Crustapod leather/meat, the 4 RSW_Pawn_Yobshrimp_* sounds. Removed: land race file, BodyDef RSW_YobshrimpLand, its 2 eggs, its tolerance pin; 13 swanimals/Yobshrimp textures retired. Label "pale yobshrimp" -> "yobshrimp" (juvenile "young yobshrimp"); the land def's vanilla-biome wildBiomes were NOT carried over.

## 4. Strill, Taozin, TeeMuss, Lothcat
- DONE Strill: B&W pencil sketch (wookieepedia_legends_2.webp, Lord Mirdalan) deleted with its lines in description.md; Must show now requires his six legs / four ears / toothy maw / gliding (queued Strill jobs reference the in-game sprite, not the sketch).
- DONE Taozin: proposal at design/RimStarWars/taozin_split_proposal_2026-10-17.md (adult RSW_Taozin predator in the Crags + new RSW_TaozinGrub, terracotta/white-in-brine). Not built.
- DONE TeeMuss: enact had NOT queued it; queued enact_followup_teemuss_v1_{north,south} (derived from the kept live east).
- DONE Lothcat: enact's single set (enact_4ecc64c3, done, awaiting pick) has no sex; female had east only, so queued enact_followup_lothcat_f_v1_{east,north,south} for swanimals/Lothcat/Lothcat_f.

## 5. Conflicts (enact re-run 2026-10-17, holds: KraytDragon (cut), RSW_Wampa (cub job withdrawn on purpose))
- DONE re-applied enact: 5 followed notes cleared, 3 purges, SWBestiary deployed.
- DONE Gorg: ENACT BUG — a ticked variant is installed at GorgV_<letter>, and letter G collided with the existing GorgV_G slot (his pick M), so each run overwrote M with variant G. Restored M at GorgV_G; variant G installed as GorgV_G2 (+ alternateGraphics, chance 0.923). Also variants were missing facings whose bytes were live elsewhere: filled C east, D north, E east/south, B east (in-game east, as C's); GorgV_I has an east only -> queued enact_followup_gorgv_i_v1_{north,south}.
- DONE Nexu pick D -> NexuW_north, Tukata pick B -> Tukata north/south, over the older keeps (his newest pick).
- DONE purged 9 superseded older keeps he ✕'d (Blarth 2, BloodletterPetrel 2, Shyrack 3, TeeMuss 1, Vornskyr 1); HssissA east/north retired + purged (out of the pool).
- LEFT for the owner (✕ on the only picture shipping, nothing to replace it yet): Bantha BanthaW S/E/N (StarWarsPatches; not a slot on the sheet); TeeMuss north/south (new N/S queued); Whisperbird south (his pick H has no south); Yobshrimp east (Things/.../SeaBeasts/Yobshrimp, redraw queued).
- LEFT: enact TODO still lists the Hssiss/Varactyl pool removals (done in defs / Varactyl_m is the only male picture, redraw queued); no --mark-done kind for pools.

## 6. Owner card 2026-10-17: "Crossed-out pictures that are the only art in their slot → Delete now and queue the missing redraws"
- DONE retired + purged: Bantha BanthaW south/east/north (StarWarsPatches), TeeMuss north/south, Whisperbird south, Yobshrimp east (sea).
- DONE queued enact_followup_banthaw_v1_{east,north,south} and enact_followup_whisperbird_v1_south. TeeMuss (enact_followup_teemuss_v1_{north,south}) and Yobshrimp (enact_ec92b98b) are already RENDERED, waiting for his pick.
- Kreetle stays 0.5 cells (owner by card: "0.5 cells, today's note").
- DEPLOY owed: SWBestiary + StarWarsPatches (texture deletions); game was up, not deployed.
