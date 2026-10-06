# FlowWorks build pass 2026-10-05 (FOUNDRY)

## Progress
- started 17:41
- inventory 9a2685639; prison room + charity piggyback + bottle revert built (one DLL)

## NEW ROWS NEEDED

### SUPERDEEP_PRISON_ROOM_1 (built offline, live owed)
- feature: enclosed D=4 area is its own Room (region/district/room split at the pit wall, LAW 2 exception [D])
  assert live: 3x3 D=4 area ringed by D0 -> `cell.GetRoom()` of a pit cell != room of the lip cell; pit room ProperRoom, !TouchesMapEdge; adding a prisoner bed -> room.IsPrisonCell true; pathing still crosses (a pawn with a lowered ladder walks out); filling one cell in re-forms rooms. settings: superdeepRoomsEnabled (flip -> RebuildAllMaps; off => pit room == lip room)
- feature: capture down (float menu "Capture X from the edge of the pit", JobDef RM_CaptureDown)
  assert live: held hostile humanlike in a prison-bed pit -> after job IsPrisonerOfColony; warden Position never IsSuperdeepExcavation during the job; too-wide pawn (BodySize vs width) not offered; bare pit (no bed) shows disabled option. settings: captureDownEnabled, superdeepRoomsEnabled
- feature: lip service (warden/doctor jobs redirected to a lip cell: PrisonerAttemptRecruit/Convert/Enslave/ReduceWill/InterrogateIdentity within 6 cells LOS; TendPatient 8-adjacent; DeliverFood drops onto targetC from an adjacent lip)
  assert live: convert/recruit a prisoner in a pit -> warden never on D=4, interaction lands (resistance/certainty moves); food appears on the pit floor. settings: wardenFromLipEnabled
- selftest table owed: northstar/site_spec.py SETTINGS needs "superdeepRoomsEnabled": True, "captureDownEnabled": True, "wardenFromLipEnabled": True, "bottleRevertEnabled": True (selftest_flowworks_northstar.py parity check FAILS until added — I may not edit northstar/*.py)
### PIT_TEMPERATURE_SOFTENING_1 leftover (built)
- feature: RM_ExposedPrisoner only for colonists whose ideo holds a Charity precept listening for CharityRefused_Beggars (RM_PitExposure.FeelsForExposedPrisoners)
  assert live: two colonists, ideo with Charity_Worthwhile vs ideo without a charity precept; exposed prisoner -> only the first gains RM_ExposedPrisoner; psychopath never. settings: pitExposureEnabled
### LIQUID_BOTTLE_LOOP_1 revert timer (built)
- feature: bottled boiling/icy water reverts to fresh after revertTicks (2500/5000 PROVISIONAL) via injected RM_CompLiquidRevert
  assert live: spawn RM_Bottle_BoilingWater x3, step 2500+ ticks -> RM_Bottle_FreshWater x3 at the cell; merged stacks average age; settings off -> no change. settings: bottleRevertEnabled
### FLOWWORKS_BUILD_PROGRAM_1 Phase 6 owed (built)
- feature: explosions light liquid (DamageWorker.ExplosionAffectCell postfix; Flame/Bomb/*incendiary*/*thermobaric*/*napalm*)
  assert live: tar channel, DoExplosion Bomb r=2 on it with no Fire left -> LiquidFire.BurningCount > 0; EMP blast -> 0. settings: explosionIgnitesLiquidEnabled, canalFireEnabled
- feature: firefoam smothers (Filth_FireFoam on a burning cell -> extinguished, cannot relight while foam lies; Extinguish blasts smother directly)
  assert live: lit tar row, firefoam popper over half of it -> those cells stop burning and stay out while neighbours burn. settings: foamSmothersLiquidFireEnabled
- feature: rain douses (unroofed burning cell, 0.03 x rainRate per 60-tick check)
  assert live: force rain on a lit open channel vs a roofed twin -> open burning count falls, roofed unchanged. settings: rainDousesLiquidFireEnabled
- site_spec SETTINGS owed: explosionIgnitesLiquidEnabled, foamSmothersLiquidFireEnabled, rainDousesLiquidFireEnabled (all True)
### FLOWWORKS_QUARRY_DIGGING_1 FlowWorks half (built; registry-independent core)
- feature: canal-dig finds (JobDriver_DigCanal.DoEffect -> RM_DigDiscoveryState.OnCut). Pool = this map's resource rock by cell count; D>=3 cut also draws the deep resource grid under the cell (50%); none -> local rock chunk; components/plasteel/Manufactured never; rolledDepth guard; budget = digFindBudgetPercent% of map ore units; letter on first find per material.
  assert live: static_call RimMandrake.FlowWorks.RM_DigDiscoveryProof.ProofReport("force") then dig one cell one level -> a find item on a non-excavated lip cell, Finds+1, def is a mineableThing of a rock on the map (or a chunk); fill in + re-dig after "force" -> no find (rolledDepth); 200 forced finds -> zero ComponentIndustrial/Plasteel. settings: digFindsEnabled, digFindsLocalOnly, digFindChanceMultiplier, digFindBudgetPercent, digFindLetterEnabled
- site_spec SETTINGS owed: digFindsEnabled True, digFindsLocalOnly True, digFindChanceMultiplier 1.0, digFindBudgetPercent 5.0, digFindLetterEnabled True
### FLOWWORKS_BUILD_PROGRAM_1 Phase 8 slice 1: universal pump (built; hoses/adapters later)
- feature: RM_LiquidPump (powered 150 W, flickable) beside an RM_LiquidTank: DRAW one level/250 ticks from an adjacent wet dug cell (TryTakeLevel) or natural source (Stock.TryDebit volumePerTile) into the tank as 5 units; POUR (gizmo) one level from the tank into the adjacent dug cell with most room (TryPourLevel; fluids never mix)
  assert live: pump between a 3-cell water channel and a tank -> after 750 ticks channel levels -3, tank +15 RM_Liquid_FreshWater; pour mode with tar in tank -> dry channel gains tar levels; water channel refuses tar; unpowered -> nothing. settings: liquidPumpEnabled
- art owed: RM_LiquidPump uses the vanilla MoisturePump texture as placeholder
- site_spec SETTINGS owed: liquidPumpEnabled True
