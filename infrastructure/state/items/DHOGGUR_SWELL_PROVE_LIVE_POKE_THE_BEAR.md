# DHOGGUR_SWELL_PROVE_LIVE_POKE_THE_BEAR — prove the dhoggur's chemical swell live, then accept it

Follows `DHOGGUR_USE_DECIDE_SNUFFLING_FOR_A_JOB` (closed against `3536bca79`). Owner, 2026-10-16: *"improve the Dhoggur
to take advantage of some of the old Crescendo anole concept: if you mess with it, it swells with violent chemical
reactions that make it three times as big and spewing fire (firespit). Stays that way for 1/3 of a day, then it can't do
it again for another day. Super aggressive when angered, but otherwise totally docile and placid while foraging."* Cards:
trigger = ONLY taking damage; cooldown = one day from the moment the swell ENDS; size REAL (body size, health, melee
damage x3, sprite drawn 3x). And: *"Needs new angry art too... it should be very scary."*

## built (3536bca79; deployed, DLL md5 5679f178 = repo)

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

## live 2026-10-16 (FOUNDRY, donor_off_phase0 tier, quicktest map; DLL 5679f178 already deployed)

- `dhoggur_swell` chain **12/12 PASS** (Transient/northstar/TheForge_20261016T161326Z.json). No mod defect found.
  Three HARNESS defects fixed in `validation.py`: the action lookup's `_PREFIXES` lacked `Dhoggur swell:` / `Forge
  sky:`; the swell's own manhunter stopped `safe_advance` (now a declared `clockgate.expected_disturbance` for THIS
  dhoggur only); `_hit`'s Blunt 3 was deflected by the hide (`totalDamageDealt 0`, read as "did not swell") -> Blunt 10,
  retried, a hit that never lands is UNMEASURED. Also a float setting read back `2` for `2.0`.
- **Vanilla consumers see x3** (by hand): BodySize -> Mass 13.5 -> 40.5, CarryingCapacity 33.75 -> 101.25 (StatPart
  reads `Pawn.BodySize`); HealthScale -> same injuries, painTotal 0.0346 swollen -> 0.2067 shrunk = x5.97 = x3 health
  scale x the hediff's 0.5 painFactor (vanilla `Hediff_Injury.PainOffset`). The inlining risk did not show.
- **Death on shrink is REAL**: swollen, 46 damage on the Body (calm max ~36, swollen ~108), swell switched off ->
  dead within one rare tick; a corpse is left (a readable sign). Thematic per the risk note; **owner question**.
- **Environment triggers it**: `RUT_Scald` 4 (every 60 ticks in the boiling rain) got through the heat-1.0 hide on 8 of
  20 hits; the melt's Flame 18 on 1 of 4. So every wild dhoggur caught outdoors in a Rain phase swells within seconds,
  once per cooldown. **Owner question** (the risk note said to raise it).
- Calm adult dhoggur reads bodySize 0.45, healthScale 0.9 (as spawned by `spawn_pawn`).

## NEXT

`DHOGGUR_SWELL_PROVE_LIVE_POKE_THE_BEAR` — live-proven 12/12, no mod defect; NEXT: ask the owner (card) whether rain
scald / melt burns should trigger the swell (today they do, every Rain phase) and whether death-on-shrink stays, then
serve the swollen art sheet with `serve_gated.py` (below) and `art install` only what he picks; close on his answers.
Swollen art INSTALLED 2026-10-16 on his word (*"swollen dhoggur is awesome."*) via `art install` to
`TheForge/Textures/Things/Pawn/Animal/RM_Dhoggur/RM_Dhoggur_Swollen_{east,south,north}.png` (512px; the C# loads
`<body texPath>_Swollen`, so no def change). NEXT: deploy TheForge textures when the game is down, then look at it in game.
