## spec
Now that `JawaIon_Damage` is actually fielded (`JawaIon_FieldOurOwnGun.xml`, deployed
2026-08-22), the mechanism behind it has never been proven in a live game.

`JawaIon_Damage` is not an ordinary damage type. Read off the dump:

    harmsHealth               false
    makesBlood                false
    externalViolence          false
    externalViolenceForMechanoids  true
    combatLogRules            Damage_EMP
    workerClass               JawaIonWeapons.DamageWorker_IonBuildup

⇒ It is meant to be a **capture** weapon — `setting_physics.md` L16: *"Downed is not dead,
and this is where most of our prisoners, salvage and mercy come from."* The C# worker is
supposed to accrue a buildup hediff whose top stage sets `Consciousness` to a floor,
downing the target alive.

🔴 **Nobody has ever watched it happen.** The mod's own source carries a `VERIFY IN-GAME`
note and a `KNOWN INERT` comment that may or may not be stale, and its `About.xml` says the
assembly is silent whether the worker fires or not. A silent worker is exactly the class of
failure this seat exists to catch.

## criteria
On a live map:
1. Spawn a **flesh** pawn and a **mechanoid**, and a shooter holding `JawaIon_Blaster`.
2. Fire until the flesh pawn goes down. Read back with `jawa/pawn_get`:
   - a `JawaIon_Stun`-family hediff **exists and its severity rose between shots**
   - the pawn is **downed and alive**, not dead
   - **no** `Gunshot` hediff and **no** blood filth — `harmsHealth false` must hold
3. Repeat against the mechanoid: `externalViolenceForMechanoids true` means it should be
   treated as an attack there.
4. ⚠️ If the buildup does NOT accrue, that is the real result — record `fail`, and the
   campaign's signature weapon is inert rather than merely unfielded.

## why it matters more than one gun
`faction_equipment_clusters.md` builds the Jawa faction identity on this weapon: the player
faction manufactures one thing, and it captures machines rather than killing people. If the
worker does not fire, that identity is fiction and the design needs a different spine.

⚠️ Needs a fresh quicktest map — the 2026-08-21 map is polluted with ~350 spawned pawns and
`step_game_ticks` times out on it, and this test needs ticks to advance.
