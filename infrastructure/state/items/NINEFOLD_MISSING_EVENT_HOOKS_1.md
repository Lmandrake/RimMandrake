## 2026-09-12 (FOUNDRY, routed from BENCH) — 2 of 4 new hooks LIVE-CONFIRMED with real satiation moves; 2 remain genuinely untestable without new tooling; ordinal contract clean

**Sh'kaar (battle) — LIVE-CONFIRMED, observed organically.** During this
session's unrelated `WEBWORK_KIT_BUILD_1`/fast-forward testing, wildlife
combat on the test maps produced repeated real log lines, e.g.
`[Ninefold] Shkaar satiation +3.0 (downed in battle: Hevva, Counterterrorist)
-> 18.0 [Neutral]`, climbing across multiple kills to `-> 36.0 [Content]`.
`Patch_BattleResolved` is firing correctly on real `Pawn.Kill` calls with
`dinfo.HasValue`, no bridge staging needed.

**Ohm (droid online) — LIVE-CONFIRMED, deliberately triggered.** Spawned
`RSW_DW_KotORDroidColonist_T3UD` (Droidworks, a Humanlike/non-flesh droid
race) with `faction=none` via `jawa/spawn_pawn`, then flipped it to the
player via `jawa/set_pawn_faction {faction: "player"}` (calls
`Pawn.SetFaction` directly, the same choke point `Patch_DroidOnline` hooks).
Log: `[Ninefold] Ohm satiation +15.0 (droid brought online: Diver,
Mercenary) -> 100.0 [Exalted]` — magnitude matches `EventMagnitude.Large`
exactly.

**`CheckOrdinalContract()` — CONFIRMED clean.** Searched the full session's
`Player.log` (which spans many `GameComponent_Ninefold` constructions, one
per map/game reload tonight) for its own error tag,
`NINEFOLD_ENUM_ORDER_SAVE_TRAP_1`: zero hits. The ordinal table still
matches `God.cs`'s enum order.

**Mob'Unloo (trade) and Ta'Baa (launch) — NOT live-triggered, precisely
why:** both patches hook a choke point with no existing bridge route to
reach programmatically.
- `Patch_TradeCompleted` gates on `TradeDeal.TryExecute(out actuallyTraded)`,
  which only runs from inside `Dialog_Trade` after a human (or a UI-driving
  script) negotiates and confirms a deal. No `jawa/`/`rimworld/` tool calls
  it or drives that dialog; the only trade-related tool is
  `jawa/trade_price_probe` (reads prices, executes nothing). Debug actions
  (`Do trade caravan arrival...`, `Spawn trade ship`) only SPAWN the trader
  — they do not complete a transaction.
- `Patch_TransporterLaunched`/`Patch_GravshipLaunched` gate on
  `CompLaunchable.TryLaunch` actually committing (fuel + valid destination
  + group check all passing) or the gravship's `InitiateTakeoff`. Tried the
  cheapest apparent shortcut, `Actions\T: Force shuttle raid here` +
  `Actions\Force enemy shuttle departure` (category "Gravship Raids") — it
  reported `success: true` but spawned no `Shuttle` thing at all
  (`jawa/list_things` confirmed 0), consistent with this being an
  Odyssey-gravship-raid-only mechanic that no-ops without a live gravship
  colony present, which this disposable test map is not. Building a real
  launch (spawn `TransportPod`/`Shuttle`, fuel it, set a destination tile,
  load cargo, then actually launch) has no direct bridge tool either — every
  route goes through `Dialog_Transporter`/architect UI clicks the bridge
  cannot drive today.

Both are genuinely a `rimbridge-companion` gap (a `[Tool]` method that calls
`TradeDeal.TryExecute` or `CompLaunchable.TryLaunch` with synthetic
parameters), not something more bridge-driving effort would have found
tonight — flagging rather than guessing at a workaround.

**Net for tonight**: 5/9 → **7/9** gods now have at least one live-confirmed
satiation input (Sh'kaar and Ohm join the existing five); ordinal contract
verified clean. Leaving `doing` (not closed) — criteria still explicitly
wants all 9, and this item's own criteria line is unmet by exactly the two
gods above. `needs owner` isn't right either (this doesn't need a decision,
it needs a companion-tool build); leaving unset since none of `needs`'
values (offline|deploy|game-up|bridge|harvest|owner) fit "blocked on new
companion tooling" — the next session should file a small
`rimbridge-companion` item for `TradeDeal.TryExecute`/`CompLaunchable.
TryLaunch` synthetic-trigger tools rather than re-attempt this by hand.

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

## Routed 2026-09-12 (BENCH)
Build half done at 98863702; the remaining verify is LIVE bridge work (trigger
kill/trade/launch/droid-online, read satiation fields back) — reassigned to
FOUNDRY, who holds the bridge on the current full-list load. Spawn-many rule
applies: batch the four triggers, one driver.
