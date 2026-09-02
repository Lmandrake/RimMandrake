# DROIDWORKS_CHARGER_STATE_MACHINE_SWEEP_1

Opus code review (2026-09-02) of the Droidworks ion/power-down state
machine, alongside `DROIDWORKS_POWEREDDOWN_NOT_WIRED_1`'s 3 root-cause
fixes. These 4 are real but lower-urgency than the root cause, not yet
independently re-verified against source.

## spec

1. `CompDWCharger.CompTick` (`CompDWCharger.cs:36-52`) checks only
   `Props.radius > 0` and its tick interval — never consults
   `RSW_DW_ChargeNimbus`'s own `CompPowerTrader`/`CompFlickable`. The
   nimbus charges every droid in radius while unpowered, grid-down, or
   switched off. Fix: bail on `TryGetComp<CompPowerTrader>()?.PowerOn ==
   false` or `CompFlickable.SwitchIsOn == false` before the radial scan.
2. Same method accepts ANY pawn with a `Need_Power` in radius — no
   faction/hostility filter, so a raiding battle droid or a prisoner you're
   deliberately starving gets topped off. Add a `pawn.HostileTo(parent.
   Faction)` skip (and consider prisoner status).
3. `Recipe_RebootDroid.ApplyOnPawn` (`Recipe_RebootDroid.cs:22-29`) never
   calls `base.ApplyOnPawn` — drops `TaleRecorder.RecordTale` and any
   surgery-outcome/fail handling. If "reboot always succeeds" is the
   intent, state it in the file header and add an explicit
   `<surgerySuccessChanceFactor>` to `RSW_DW_RebootDroid`'s def, the way
   `RSW_DW_InstallRestrainingBolt` already does — right now the two
   disagree silently on whether reboot can fail.
4. `HediffComp_DWBoltResentment.CompPostTick` (`:41-52`) does a linear
   `HasHediff()` scan every single tick, forever, for any pawn that has
   ever worn a restraining bolt (the hediff is deliberately never
   removed). Gate the body on `parent.pawn.IsHashIntervalTick(60)` and
   scale the per-tick gain by 60 — `HediffComp_PoweredDown.CompPostTick`
   already has the cheaper shape to copy.

## verify

Each fix compiles (`Droidworks.csproj`); 1-2 need a live charger + a
hostile/prisoner droid in radius to confirm; 3-4 are offline-verifiable
(read the recipe's resulting Tale/outcome behavior, or just confirm the
interval-gated math still accumulates the same total per day).

## criteria

All 4 fixed, or explicitly triaged with the check that ruled a fix
unnecessary named.
