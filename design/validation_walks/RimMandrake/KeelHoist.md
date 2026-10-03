# KeelHoist — validation walk
subject: src/RimMandrake/KeelHoist  (packageId mandrake.rm.keelhoist)
deps: brrainz.harmony, Ludeon.RimWorld.Odyssey
list: minimal
status-hint: the keel hoist, a gravship part, plus fixed ruined head-frames that site gensteps place beside portals and sealed holders: a MapPortal whose cable hangs on a cave mouth or an unreachable cell; cargo rides a hidden timer; downed strangers arrive prisoners, downed wild beasts arrive restrained; tether lock on launch; manifest tab; Open Line counter. Design `design/RimMandrake/ship_cargo_hoist_design_2026-10-01.md` §2, item HOIST_SHIP_PART_BUILD_1.

## must be true
- The hoist is a researched ship part: `RM_KeelHoist` (thingClass `RimMandrake.KeelHoist.RM_KeelHoist`) carries `PlaceWorker_NeedsGravEngine` and needs research `RM_KeelHoist`, whose prerequisite is `BasicGravtech` (design §2e). → defs_and_wiring.hoist_is_a_researched_ship_part
- The hoist, its research row and `RM_HoistRestraint` load in the live game. → defs_and_wiring.defs_resolve_live
- The hoist never generates a pocket map: `GetOtherMap` returns the target portal's map or its own (design §2d). → source_rules.no_pocket_map_ever
- Downed strangers and wild beasts reach the hoist's dialog through a postfix scoped to `RM_KeelHoist`, never through the shared `AllSendablePawns` (item). → source_rules.shared_sendable_list_untouched
- The ship refuses to launch while a hoist on its substructure has its cable down (design §2d tether lock). → source_rules.tether_lock_on_can_launch (static); live refusal → UNCOVERED: needs a live gravship with a powered hoist, no drive yet
- Every source file is compiled (the csproj sets EnableDefaultCompileItems false). → source_rules.csproj_lists_every_source
- Items and a downed wild animal go down `RM_LanternDeepMineshaft` and come back up; the animal arrives restrained and the manifest records both ways (item criteria). → UNCOVERED: needs a live gravship parked by a Lantern Deeps mouth, no drive yet
- A downed hostile humanlike lowered by the hoist arrives as a prisoner of the colony (design §2b). → UNCOVERED: needs a live capture drive
- The fixed head-frame `RM_HoistFrame` and the sealed holder `RM_SealedPit` are never player-buildable: no designationCategory, research or cost (HOIST_FIXED_SITE_FRAMES_1, owner ruling: placed only by site gensteps). → fixed_site_frames.frame_not_player_buildable
- `RM_HoistFrames` runs on Base_Player and the Foundry tower door carries `RM_HoistFrameSiteExtension`, guarded on the frame existing (design §3b first reuse). → fixed_site_frames.genstep_registered_and_tower_wired
- A holder's pawns come up only once its gate opens (ours/unowned, map is ours, faction defeated, or no able keeper left), never before (design §1b). → fixed_site_frames.holder_lift_waits_for_gate (static); live refusal-then-lift → UNCOVERED: needs a seeded RM_SealedPit on a live map
- The frame, pit and genstep load in the live game. → fixed_site_frames.frame_defs_resolve_live
- A Forge home map with a foundry tower door gets a frame beside it, cable paired, loadable by pawns on that map. → UNCOVERED: needs a live Forge map generation
- Every Mod Settings toggle degrades gracefully when off (item criteria). → UNCOVERED: settings are public static (set_setting cannot reach them); toggles listed in suite.toggles

## anti-guessing notes
- RULED OUT: a vanilla portal can send a downed wild animal — `Dialog_EnterPortal.AddPawnsToTransferables` passes `allowCapturableDownedPawns: false`, and `CaravanFormingUtility.CanListAsAutoCapturable` admits only `ShouldAutoCapture` pawns (RimSage, 2026-10-03).
- RULED OUT: an animal can be made a prisoner — no animal guest status in 1.6; capture is `RM_HoistRestraint` (Moving setMax 0) for the settings hours.
- RULED OUT: despawning a rider inside `OnEntered` — `JobDriver_EnterPortal` keeps using the pawn after `OnEntered` (drafter, carryTracker at `pawn.Position`); the hoist lifts the rider into transit on its next tick instead.

## the walk
1. [L] Player.log after load: no config error naming mandrake.rm.keelhoist; no Harmony patch failure for `Building_GravEngine.CanLaunch` or `Dialog_EnterPortal.AddPawnsToTransferables`
2. [L] research `RM_KeelHoist` appears after Basic gravtech; the hoist is buildable only on substructure of a map with a grav engine
3. [L] lower the cable onto `RM_LanternDeepMineshaft`; load steel and a downed wild animal; both arrive below after the cycle, the animal restrained; Raise cradle brings them back; the Manifest tab lists 2 DOWN and 2 UP
4. [L] with the cable down the pilot console refuses launch with "Reel in the keel hoist first."; reel in; launch allowed

## north star
state: DRAFT
validated-hash:

### the experience  (OWNER'S WORDS)
(not yet dictated)
