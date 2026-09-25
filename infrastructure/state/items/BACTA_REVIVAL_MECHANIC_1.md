# BACTA_REVIVAL_MECHANIC_1 — bacta revival of the recently dead

Filed by BENCH 2026-09-14, reassigned to FOUNDRY 2026-09-21 (owner, verbatim: *"Shipping
implementation items to FOUNDRY is a good idea. Let's enable that as much as possible."*).
Owner ruling (title, verbatim): *"works on dead bodies IF retrieved within a few hours"* —
corpse-freshness window, tank accepts fresh corpse, revives minus brain/mental damage
which stays unhealed; vanilla `ResurrectionUtility` as the base; settings toggle + window
tunable. Extends `BACTA_TANK_CORE_1` (built and live-tested this same session) rather than
duplicating it — same mod, `mandrake.rsw.bacta`, `src/RimStarWars/Bacta/`.

## spec (written by FOUNDRY — no prior spec/verify existed on this item)

1. **Corpse-freshness window.** `Corpse.Age` (ticks since `timeOfDeath`, vanilla field,
   `Verse/Corpse.cs`) compared against a tunable hours value, default 6h (owner said "a few
   hours"; 6 was FOUNDRY's judgment call for the shipped default, freely retunable).
2. **Tank accepts a fresh corpse.** A new hauling job (`WorkGiver_CarryCorpseToBactaTank` +
   `JobDriver_CarryCorpseToBactaTank` + `RSW_CarryCorpseToBactaTank` JobDef) scans corpses on
   the map (not the tank, which is how the existing living-pawn path works — a corpse can't
   select anything for itself) and carries an eligible one to an empty, powered, fuelled tank.
   Eligibility mirrors the existing living-occupant `CanAcceptPawn` checks (colonist / slave-
   of-colony / prisoner-of-colony / player animal, flesh only, not Anomaly's `UnnaturalCorpse`)
   plus the freshness window.
3. **Revival via `ResurrectionUtility.TryResurrect`**, not `TryResurrectWithSideEffects` — a
   deliberate choice: bacta is a controlled medical process, not a raw ritual, so it does not
   roll vanilla's rot-scaled dementia/blindness/resurrection-psychosis chances. Brain and
   mental damage are left exactly alone: `TryResurrect` itself never touches the brain (that's
   `TryResurrectWithSideEffects`'s job, which this code does not call), and once revived the
   pawn is a normal `CompBactaImmersion` occupant, whose existing heal loop already excludes
   anything on the `ConsciousnessSource` body part. `restoreMissingParts: false` on the
   `ResurrectionParams` is the same "does not regrow" law the healing comp already enforces —
   confirmed against `Pawn_HealthTracker.Notify_Resurrected` (decompiled source): that flag is
   the only thing gating missing-part restoration.
4. **Settings**: `revivalEnabled` (existing bool, was a dead reserved toggle in
   `BACTA_TANK_CORE_1`, now live) + new `revivalWindowHours` tunable, both in the existing
   `BactaSettings`/Mod Settings screen — no new screen, per the 2026-09-12 standing rule.
   Shipped default `revivalEnabled = false` (reviving the dead is a bigger claim than healing
   the living; opt-in).

**Design decision, stated plainly**: revival is NOT a separate multi-tick process. The corpse
is accepted and resurrected in the same call (`Building_BactaTank.TryAcceptCorpse`). There is
nothing to tick during "revival" itself — the existing `CompBactaImmersion` 250-tick heal loop
takes over the instant the pawn is alive again, because a freshly revived pawn (badly wounded,
by construction — that's why it died) is exactly the occupant that loop already exists to
heal. Two mechanisms, one shared loop, no new tick-state, no new Scribe fields on the building.

## What was built

- `Source/BactaTuning.cs`: `TicksPerHour` const, `RevivalWindowHours` default (6f).
- `Source/BactaMod.cs`/`BactaSettings`: `revivalWindowHours` tunable (Scribed), `revivalEnabled`
  now wired live (was inert/reserved), settings UI section rewritten from "Not yet built" to a
  real toggle + conditional slider.
- `Source/Building_BactaTank.cs`: `CanAcceptCorpse(Corpse)` (`AcceptanceReport`) and
  `TryAcceptCorpse(Corpse)` — extracts the corpse's `InnerPawn`, destroys the corpse shell
  (same step `ResurrectionUtility.TryResurrect` performs on a spawned corpse), inserts the bare
  pawn into the tank's `innerContainer` exactly like a carried-in living occupant, then
  resurrects it there. Stale comment corrected in the same file ("Revival … is
  BACTA_REVIVAL_MECHANIC_1, not this item" — it now is this item).
- `Source/WorkGiver_CarryCorpseToBactaTank.cs` (new), `Source/JobDriver_CarryCorpseToBactaTank.cs`
  (new): the corpse-hauling job, modelled on vanilla `WorkGiver_HaulCorpses` (corpse scan) and
  `JobDriver_CarryToBuilding` (carry-and-hand-off toils), generalised from a live-Pawn takee to
  a Corpse one.
- `Defs/JobDefs/RSW_BactaJobDefs.xml` (new file): `RSW_CarryCorpseToBactaTank` JobDef.
- `Defs/WorkGiverDefs/RSW_BactaWorkGivers.xml`: new `RSW_CarryCorpseToBactaTank` WorkGiverDef.
- `Source/BactaDefOf.cs`: `RSW_CarryCorpseToBactaTank` JobDef field.
- `Languages/English/Keyed/RSW_Bacta.xml`: `RSW_BactaTankRevived`,
  `RSW_BactaTankRevivalFailed`, `RSW_BactaTankRevivalDisabled`, `RSW_BactaTankReportTooLate`.
- `About/About.xml`: one paragraph documenting the (off-by-default) revival feature.
- `.csproj`: both new `.cs` files wired into `<Compile Include>` — checked against the
  `EnableDefaultCompileItems false` trap CLAUDE.md warns about; this project already sets that
  flag, both new files are explicitly listed.

Every RimWorld API used (`Corpse.timeOfDeath`/`Age`, `ResurrectionUtility.TryResurrect`,
`ResurrectionParams`, `Pawn.Corpse`, `Pawn_HealthTracker.Notify_Resurrected`,
`WorkGiver_Scanner`, `GenClosest.ClosestThingReachable`, `ReservationUtility.CanReserveAndReach`,
`ToilFailConditions.FailOnDestroyedOrNull`/`FailOnDespawnedNullOrForbidden`,
`Toils_Haul.StartCarryThing`) was read from
`/mnt/d/Luke/dev/reference/rimworld-decompiled` before being called — nothing guessed.

## verify

Offline, done this pass:
- **Build**: `dotnet build … -c Release` — 0 warnings, 0 errors. DLL mtime newer than every
  `.cs` source.
- **XML well-formedness**: all 4 touched/added XML files parse clean
  (`RSW_BactaJobDefs.xml`, `RSW_BactaWorkGivers.xml`, `RSW_Bacta.xml` (Languages),
  `About.xml`).
- **`validate_patch.py`** re-run on the mod's one patch file (unchanged this pass,
  `RSW_Bacta_TraderStock.xml`): `OK - 0 errors, 3 warnings` (same pre-existing stylistic
  warnings noted in `BACTA_TANK_CORE_1`, not touched by this work).
- **`.csproj` wiring** confirmed by inspection, not just by successful build (both new files
  explicitly present in `<Compile Include>`).
- **`deploy_custom_mods.py --mod Bacta --apply`**: 4 of 5 changed files deployed
  (`About.xml`, `RSW_BactaJobDefs.xml`, `RSW_BactaWorkGivers.xml`, `RSW_Bacta.xml`). The
  **assembly DLL failed to write** — `[Errno 22] Invalid argument` writing into the live
  `Mods/Bacta/Assemblies/` folder — because RimWorld currently has it open (OS file lock;
  `rimworld-deploy`'s documented "companion DLL cannot be written while the game runs" trap).
  The bridge coordination file (`infrastructure/state/BRIDGE`) reads FREE, but the game
  **process** is a separate, OS-level lock the bridge file doesn't track. **Re-run
  `deploy_custom_mods.py --mod Bacta --apply` once RimWorld is closed** to finish the deploy —
  the four def/lang/about files are live already; only the compiled behaviour is not.

**Not done this pass, and what a live proof needs to check** (this pass had no bridge access
and was explicitly briefed not to attempt one):
1. Deploy the DLL (above), then a cold load or `modset_builder.py` tier with `mandrake.rsw.bacta`
   active (it already is, per `BACTA_TANK_CORE_1`'s status section).
2. Kill a disposable pawn (debug tools, not `jawa/pawn_health` + `WoundInfection` — that call
   is a known INSTANT, silent, `success:true` kill per
   `skills/rimbridge/references/silent-failures.md`, filed this same session; use a plain
   lethal `DamageInfo` instead) whose corpse stays within the tunable window.
3. Confirm a hauler auto-picks up the corpse (`RSW_CarryCorpseToBactaTank` WorkGiver actually
   fires) and carries it into an empty tank with power+fluid.
4. Confirm `TryAcceptCorpse` fires: the corpse Thing is destroyed, the pawn reappears alive
   (`pawn.Dead == false`) inside the tank, a `RSW_BactaTankRevived` message fires.
5. Confirm the LAW holds on the revived pawn: any `Hediff_MissingPart` the pawn had at death is
   STILL there after revival (not restored); any hediff on the `ConsciousnessSource` part
   (brain) is untouched; the existing wound-healing loop then proceeds on remaining physical
   injuries exactly as it does for a living occupant (already live-proven in
   `BACTA_TANK_CORE_1`'s second pass).
6. Confirm the freshness window is enforced: a corpse older than `revivalWindowHours` is
   correctly refused (`CanAcceptCorpse` returns `RSW_BactaTankReportTooLate`) and no hauler
   job is generated for it.
7. Confirm both settings toggles behave: `revivalEnabled = false` → the WorkGiver's own
   `ShouldSkip` makes it inert (no jobs, no corpse hauling) and `CanAcceptCorpse` refuses
   outright; `revivalWindowHours` changes what "fresh" means.
8. Watch for a real engine risk this pass could not rule out from source alone: whether
   `ResurrectionUtility.TryResurrect` with `dontSpawn: true` on a pawn that was never
   `GenSpawn.Spawn`-ed in the first place (ours goes straight from Corpse to tank
   `innerContainer`, unlike the vanilla dev-gizmo path which resurrects a corpse still lying
   on the map) behaves cleanly — `pawn.Drawer`, `pawn.jobs`, and colonist-bar/quest hooks it
   touches were read as safe for an unspawned pawn by source inspection only, not observed.

## acceptance criteria

- [ ] DLL deployed (blocked on game restart, not on this pass's work)
- [ ] Corpse freshness window enforced live
- [ ] Fresh corpse successfully hauled into tank and revived via a real job, not a debug poke
- [ ] Missing parts stay missing after revival (live-observed)
- [ ] Brain/mental hediffs untouched after revival (live-observed)
- [ ] Revived pawn heals normally afterward (already proven for the general case in
      `BACTA_TANK_CORE_1`; needs one live rep on a just-revived pawn specifically)
- [ ] Both settings (toggle + window) proven to change behaviour live
- [ ] `rimflow close BACTA_REVIVAL_MECHANIC_1` only after the above, per this item's own brief
      (do not close without a live proof)

## status (FOUNDRY, 2026-09-24)

Built, offline-validated, fully deployed as of `b5d418d49` (DLL rebuilt + deployed once the
game was down; Bacta is 22/22 files in sync, md5-verified). Live proof of the revival
mechanic (corpse freshness, tank job, missing-parts/brain preservation, healing, both
settings) is the only thing left, per this item's own do-not-close-without-live-proof brief.

Resumed 2026-09-24 (later pass): `bridge who` reports it held by another live FOUNDRY
window ("FireHawk flight live verify", idle ~2 min at check time — provably alive, not
stale). Per this item's own brief, not force-taking a live-held bridge. Blocked rather than
closed; the acceptance checklist below is unchanged and still gates the close.
