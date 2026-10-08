# Droidworks L2 triage 2026-10-07
Edited: `src/RimStarWars/Droidworks/validation.py`, new `Source/Droidworks/DroidworksProofs.cs` (+ csproj line). winbuild OK, DLL + srchash left uncommitted. Nothing committed. Not run live.
Live re-check for all: `python.exe Transient/l2sweep_run.py Droidworks` on a quicktest map (salvage_on_death, bolt_core, detonation, passive_charging, protocol_trade_advantage, ion_overload_shutdown chains).
Note: the DLL must be deployed (deploy_custom_mods.py --mod Droidworks --apply, game closed) before protocol_trade_advantage can pass: it calls the new DroidworksProofs.MakeTrader.

## head_drops_with_identity
HARNESS. Evidence: l2sweep_Droidworks.json detail list is exactly 60 rows (= limit=60) with 56 CollapsedRocks; the generic 12x12 ring list was truncated, so the head was never visible (parts, which sort earlier, were). The `Bomb 5000` kill also collapses the roof. Mod code CompDWHeadDropper.cs:25-45 is correct (chassisClass 3 -> RSW_DW_Head_Battle; snapshot name in Thing_DWHead label, CompHeadIdentity.cs). The same check PASSED at 11:48.
Fix: kill with `jawa/pawn_force_incapacitate action=kill` (Pawn.Kill(null), no roof collapse), then query per defName (head + 6 parts) in a 16x16 rect. Check itself unchanged (head present, label carries name).
Unconfirmed: whether a roof collapse also destroyed the head in that run; the new kill path removes that variable.

## mood_penalty_nearby
HARNESS (fixture drift). Evidence: bolt_core pawn_get shows walker at (125,125) before the 1200-tick wait and (138,148) after: free colonists wander ~27 cells apart. ThoughtWorker_NearBoltedDroid.cs:29-37 requires a bolted pawn within boltMoodRadius=12; bystander thoughts list correctly lacks it. Earlier 11:48 run passed (they happened to stay near). No Config file overrides the radius.
Fix: draft both colonists after spawn (stand still); before asserting, read both positions and, if >10 apart, order_pawn the bystander next to the walker; distance is recorded as evidence. Assertion unchanged.

## nimbus_charges_in_range
Passes in the latest sweep (12:57) and 11:48; failed once (12:56, `l2sweep_Droidworks.prev.json`): after the 720-tick wait `jawa/pawn_get` said "No pawn matching RSW_DW_Race_OuterRim_GNKDroid59083" (droid no longer spawned; the check then misread an empty read as level 0.0 "still 0.0"). Classification: FIXTURE (undrafted free droid wandered/was lost; cause not recoverable, Player.log has since been overwritten). Mod code CompDWCharger is not implicated by any evidence.
Fix: draft the droid so it stays in the 6.9 radius, and an empty pawn read now fails with an accurate message ("droid no longer a spawned pawn") instead of "still 0.0". If it recurs with that message, look at the droid's corpse/hediffs.

## full_charge_detonates_on_death
HARNESS (flaky lethality). Evidence: `.prev.json` jawa/damage Bomb 5000 on the GNK reported totalDamageDealt 85, dead=false, so "still on the map" (one hit on one part). Passed in the other two sweeps. CompDroidDetonation.Notify_Killed does not read dinfo (grep: no dinfo use), so a plain kill is faithful.
Fix: `jawa/pawn_force_incapacitate action=kill`. Still proves death only (module docstring gap 7); explosion read-back is not available.

## ion_overload_shuts_down_droid
LIST ARTIFACT (expected). Evidence: "No HediffDef 'RSW_JawaIon_Stun'" (Patches/IonBuildup_PowersDownDroid.xml is FindMod-gated to mandrake.rsw.ionweapons). Mod source HediffComp_IonOverloadsDroid.cs untouched.
Fix: chain now probes `jawa/get_defs HediffDef/RSW_JawaIon_Stun` first (reading success / notFound / foundCount, a failed ask is also UNMEASURED) and reports `UNMEASURED(list): ... Jawa Ion Weapons absent` via upstream_failed instead of FAIL. With the mod loaded it runs the original check unchanged.
Re-check with ionweapons in the list to get a real verdict.

## protocol_droid_shifts_prices
HARNESS+LIST: TraderCaravanArrival cannot generate a caravan on this tile (Player.log "no usable PawnGroupMakers ... groupKind=Trader"); the mod's hook (Patch_ProtocolTradeAdvantage.CurrentAdvantage) needs only a live TradeSession + a non-player trader, not a caravan.
Fix (sturdier route): removed the incident/faction walk. Harness spawns a `Villager` in OutlanderCivil/TribeCivil/OutlanderRough/hostile, then calls new public static `RimMandrake.StarWars.Droidworks.DroidworksProofs.MakeTrader(string pawnId)` via jawa/static_call, which sets `Pawn_TraderTracker.traderKind` (a plain field, read in RimSage) and stocks Steel/Components/Medicine/Cloth. `jawa/trade_price_probe` is then pointed at that trader (traderPawnId) for the before/after-protocol-droid differential; comparison logic unchanged. If no non-player humanlike can be spawned the component is UNMEASURED, never FAIL.
Risks to watch live: (1) static_call is GM-tools only; (2) the Villager kind must exist (Core); (3) trader pawn has no Lord so TraderParty() = {trader} and the trader term is +1 in both probes, so the differential is still 2 x 0.06.
