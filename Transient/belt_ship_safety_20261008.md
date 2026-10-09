# Ship safety batch 2026-10-08 (FOUNDRY helper)

## Step 0: items located
## Step 1: GS-1 RimSage read
CONFIRMED. GravshipUtility.GenerateGravship (GravshipUtility.cs:373-429) sets generatingGravship=true, Current.Game.Gravship=obj,
calls PreSwapMap on every ship thing, then DeSpawn(DestroyMode.WillReplace) on each (l.389). CompAerialAnchor.PostDeSpawn strips
every partner link regardless of mode -> every ship-mounted span drops. Landing: GravshipPlacementUtility.PlaceGravshipInMap
GenSpawn.Spawn's the SAME Thing instances (SpawnNonPawnThings), then GravshipPlacementUtility.PostSwapMap -> Thing.PostSwapMap ->
ThingComp.PostSwapMap on every ship thing (vanilla CompPower/CompGlower/CompPowerTrader use it).
## Step 2: GS-1 fix
## Step 3: X-2/DI-3 RimSage read
ANSWER: vanilla does NOT silently delete a living pawn held in an IThingHolder when its map closes; it records them LOST with a letter.
Chain (no grav anchor): WorldComponent_GravshipController.TakeoffEnded -> GravshipUtility.AbandonMap (spawned pawns only) ->
MapParent.Abandon -> Destroy -> MapParent.PostRemove -> Game.DeinitAndRemoveMap(map, notifyPlayer: true) -> MapDeiniter.Deinit ->
PassPawnsToWorld iterates map.mapPawns.AllPawns = spawned + AllPawnsUnspawned; AllPawnsUnspawned = ThingOwnerUtility.GetAllThingsRecursively(
map, Pawn group, alsoGetSpawnedThings:false), which walks Map.GetChildHolders -> AppendThingHoldersFromThings(listerThings ThingHolder group)
adding the thing if it is IThingHolder AND each comp that is IThingHolder. ThingRequestGroup.ThingHolder = ThingDef.ThisOrAnyCompIsThingHolder
(thingClass or any def-declared compClass is IThingHolder). For a player pawn: Lost thoughts, letter LetterPawnsLostBecauseMapClosed naming
them, Find.WorldPawns.PassToWorld (alive). Hostile-faction map: kidnapped + letter. Dead held pawns are excluded (corpses go with the map).
Per call site (all reachable): RM_Building_BrineEncasement (thingClass : Mineable, IThingHolder); RM_CompGutSwallow (Hwelgrue, XML comp);
RM_CompEngulfer (Titanoslime, XML comp); RM_CompKethrelShell and RM_CompHoard hold ITEMS/gear, not living pawns (PickUp / HoardSweep).
Verdict: no silent deletion; no helper built. Residual (not a deletion): the colonist is lost, not brought aboard; a launch warning is a
design nicety, not a safety fix.
## Step 4: holder-safety build
## Step 5: build/validate/selftests
## Step 6: publish + rimflow

## Step 2 result: GS-1 fix (GimmeSomeSlack)
AerialMath.PlanRemoval gained an `aboard` set -> Kept (span to a partner flying along) / Grounded (span to the ground, coiled).
CompAerialAnchor.PostDeSpawn: on DestroyMode.WillReplace while GravshipUtility.generatingGravship, aboard = anchors in
Current.Game.Gravship.Things; kept links survive on both ends; grounded spans coil with one message per launch.
CompAerialAnchor.PostSwapMap (new): after landing, prune dead links, Reseed, redraw. Setting: AerialSettings.keepWiresOnGravship
(default on). Selftests: AerialSelfTest.GravshipLaunch, 6 checks. winbuild OK; selftest_gimmesomeslack 824/824.
Live criterion owed: one joint flight with both masts aboard -> span lands strung and powered; one mast left behind -> coiled + message.

## Step 4-6
GS-1 published 9401f7a73; rimflow GRAVSHIP_WIRES_SURVIVE_LAUNCH_1 implemented -> built (owes A2 L1 load check, A3 L3 joint flight).
HOLDER_SAFETY_LAUNCH_1: no build (vanilla records held colonists lost with a letter). Ledger note with symbols; design doc rows DI-3/X-2 corrected; closed.
