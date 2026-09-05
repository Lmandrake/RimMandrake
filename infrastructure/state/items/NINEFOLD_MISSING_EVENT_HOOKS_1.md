## spec
Ninefold had zero satiation inputs for 4 of 9 gods — Sh'kaar (battle), Mob'Unloo
(trade), Ta'Baa (launch/rooted), Ohm (droid-online) never moved in play, the
biggest gap between the shipped engine and `divine_satiation_engine.md`.

## what changed (commit `98863702`)
Four new Harmony patch files in `src/RimMandrake/Ninefold/Source/`:
- `Patch_BattleResolved.cs` — `Pawn.Kill` postfix, `dinfo.HasValue` distinguishes
  a violent death from a peaceful one → Sh'kaar. Magnitude is flat per-kill
  (Medium confidence; the doc's melee/ranged split needs per-verb tracking, not
  built here).
- `Patch_TradeCompleted.cs` — `TradeDeal.TryExecute` postfix (covers both normal
  and gift-mode trade), gated on `actuallyTraded` → Mob'Unloo (Medium; volume
  scaling needs `TradeDeal`'s private currency total, not exposed to a caller).
- `Patch_GravshipLaunched.cs` — `CompLaunchable.TryLaunch` postfix (vanilla's one
  entry point for shuttle/pod/gravship launches alike) → `Notify_Launched`,
  resets Ta'Baa's rooted-erosion clock and spikes satiation.
- `Patch_DroidOnline.cs` — droid pawn-generation/activation hook → Ohm.

Also added to `GameComponent_Ninefold.cs`: `RootedErosionPerHour` const,
`lastLaunchTick` field (Scribed as `ninefoldLastLaunchTick`, defaults to now on
fresh/pre-existing-save load so an old save doesn't instantly read as
maximally-rooted), `StepRootedErosion()` called from `GameComponentTick`, and
the public `Notify_Launched(reason)` entry point patches call into.
`God.cs` got `GodExtensions.CheckOrdinalContract()` — a frozen `Dictionary<God,int>`
asserting the 2026-08-30 ship ordinals, `Log.Error`s if violated — called once
from the component's constructor as a cheap sanity net for future god-list edits.

## verify
- [x] Builds clean, 0 warnings/errors (`dotnet build Ninefold.csproj`, re-confirmed
      2026-09-05 as part of this restart's batch).
- [ ] Live: `Def.ConfigErrors()`/Harmony patch report clean for all four new
      patch classes (this load, `EXPECTED_FAILURES_next_load.md`).
- [ ] Live: trigger each of the four events at least once (a kill, a trade, a
      launch, a droid coming online) and read `GameComponent_Ninefold`'s
      satiation fields back before/after to confirm they actually moved —
      NOT done yet, needs a bridge session with a colony that can do all four.

## criteria
- [ ] All 9 gods have at least one live satiation input (was 5/9).
- [ ] `CheckOrdinalContract()` never fires `Log.Error` on a real load (proves
      the ordinal table still matches `God.cs`'s enum order).

Left `doing` — the harness verify (event actually moves the number) is real
work still owed, distinct from "patch installed without exploding."
