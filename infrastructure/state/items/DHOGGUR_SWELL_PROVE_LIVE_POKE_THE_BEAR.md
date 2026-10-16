# DHOGGUR_SWELL_PROVE_LIVE_POKE_THE_BEAR — prove the dhoggur's chemical swell live, then accept it

Follows `DHOGGUR_USE_DECIDE_SNUFFLING_FOR_A_JOB` (closed against `3536bca79`). Owner, 2026-10-16: *"improve the Dhoggur
to take advantage of some of the old Crescendo anole concept: if you mess with it, it swells with violent chemical
reactions that make it three times as big and spewing fire (firespit). Stays that way for 1/3 of a day, then it can't do
it again for another day. Super aggressive when angered, but otherwise totally docile and placid while foraging."* Cards:
trigger = ONLY taking damage; cooldown = one day from the moment the swell ENDS; size REAL (body size, health, melee
damage x3, sprite drawn 3x). And: *"Needs new angry art too... it should be very scary."*

## built (3536bca79, NOT deployed)

- `src/RimMandrake/TheForge/Source/RM_ForgeDhoggurSwell.cs` + `Source/Kernel/RM_SwellKernel.cs` (fuzz units in
  `Source/SelfTest/TheForgeFuzz.cs`): ThingComp trigger on `PostPostApplyDamage` (damage actually dealt > 0), 20000-tick
  swell, cooldown stamped at the end; `RM_DhoggurSwell` hediff (`Defs/HediffDefs/`) grants `RM_FireSpit` through vanilla
  `HediffDef.abilities` (comp creates the ability tracker animals lack; AI casts via `JobGiver_Manhunter` ->
  `GetAbilityJob`); wild dhoggur goes Manhunter while swollen, recovers at the end; Harmony postfixes on `Pawn.BodySize`
  / `Pawn.HealthScale` (x scale); `MeleeDamageFactor` from the hediff stage; render tree `RM_DhoggurSwellBody` draws
  the body x scale and the `<texPath>_Swollen` art when installed (calm art 3x until then).
- Docile otherwise: `manhunterOnDamageChance`/`manhunterOnTameFailChance` 0.
- Mod Settings, "The dhoggur": on/off, manhunts on/off, hours (8), cooldown days (1), scale (3).
- `RM_FireSpit` stays owned by the Cauldron: both are wave-0 members of the composed `mandrake.rm.biomes`, and a def
  cross-reference resolves after all defs load.
- Script: `validation.py` chain `dhoggur_swell` (placid -> provoke -> x3 size/health/bite + fire + manhunter -> no
  refresh -> reverts at 1/3 day -> cooldown blocks -> rested swells again -> off shrinks at once), debug action
  `Dhoggur swell: report`. Offline selftest green (9 new breaks), never run live.

## risks to watch on the first live run

- `Pawn.BodySize`/`HealthScale` are one-line getters: if the JIT inlined them at some call sites, those sites ignore the
  postfix. The report reads `p.BodySize` from our assembly; a vanilla consumer (e.g. the health tab max HP) should be
  eyeballed once.
- When the swell ends, health scale drops back: a dhoggur badly hurt while swollen can die on the shrink. Thematic; say
  so to the owner if it shows.
- Any damage triggers it (card), including Forge environment damage (scald, gas-wash fire) that gets through its
  heat-1.0 hide. If wild dhoggurs swell constantly on the Forge map, raise it with the owner.

## NEXT

`DHOGGUR_SWELL_PROVE_LIVE_POKE_THE_BEAR` — built, DLL committed but not deployed; NEXT: deploy The Forge (composed
biomes) DLL + defs and run `northstar_driver/cli.py run --mod TheForge --plan src/RimMandrake/TheForge/northstar_plan.py`
(chain `dhoggur_swell`), fix what it finds, then put the swollen art (artpipe job from the art helper) on his review
sheet and `art install` only what he picks.
Swollen art: artpipe jobs `forgeslot_dhoggur_swollen_v1_{east,south,north}` (done, NOT installed; west mirrors east),
sheet `Transient/biome_ffar/dhoggur_swollen_sheet_2026-10-16.html` (built, gate-passed, NOT yet served: serve it with
`serve_gated.py`; its scale panel shows the swollen art at the calm 1.2, so show him
`Transient/biome_ffar/dhoggur_swollen_vs_calm_scale_2026-10-16.png` (human / calm 1.2 / swollen 3.6) beside it).
