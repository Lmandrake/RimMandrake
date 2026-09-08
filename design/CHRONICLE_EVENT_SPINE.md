# RimChronicle event spine — one-page spec (CHRONICLE_EVENT_SPINE_1)

Adopted by owner card 2026-09-08. RimChronicle (`mandrake.rm.chronicle`, né
Aftermath, R5) is the shared event spine of the RM engine suite. Battle-scoped
v1: the hook API is designed for more kinds; only the kinds below exist.

## The event row: `ChronicleEvent`

Generalizes the existing `BattleRecord` (`Aftermath/Source/BattleRecord.cs`)
and `TakingEvent` (`Property/Source/TakingEvent.cs`). In-memory only, not
`IExposable` — same documented limitation as `BattleRecord`: an event open at
save time is not resumed.

| Field | Type | Battle source (exists) | Taking source (exists) |
|---|---|---|---|
| `Kind` | `string` | `"battle.closed"` | `"property.taking"` |
| `Tick` | `int` | `BattleRecord.ClosedTick` | `TakingEvent.Tick` |
| `Map` | `Map` | `BattleRecord.Map` | `TakingEvent.Thing.Map` |
| `Actors` | `List<Pawn>` | `BattleRecord.OriginalPawns` | actor pawn + `TakingEvent.Witnesses` |
| `Thing` | `Thing` | null | `TakingEvent.Thing` |
| `Outcome` | `string` | `BattleOutcome` enum name (`Repelled`/`Routed`/`Stalemate`/`Lost`) | `WasAuthorized` → `"Authorized"`/`"Unauthorized"` |
| `Payload` | `object` | the `BattleRecord` itself | the `TakingEvent` itself |

Flat fields serve reflection consumers; `Payload` lets a consumer that chose a
compile-time reference downcast for the rich record (e.g. `StorytellerPoints`,
`ColonistCasualty`, `PriorClaim`).

## Subscription

```csharp
// In RimChronicle:
public static class ChronicleEvents {
    public static event Action<ChronicleEvent> EventClosed;
    public static void Raise(ChronicleEvent e) => EventClosed?.Invoke(e);
}
// In a consumer's Mod ctor (soft — no assembly reference):
var t = AccessTools.TypeByName("RimMandrake.Chronicle.ChronicleEvents");
if (t != null) t.GetEvent("EventClosed").AddEventHandler(null, handler);
```

Static C# event, not a Def-registered hook: it is the idiom this suite already
ships (`PropertyEvents.UnauthorizedTakingWitnessedByOwner`), needs no
load-order Def resolution, and reflection-binds cleanly when Chronicle is
absent. Emission point: `MapComponent_BattleRecorder.Close()`, where
`AftermathRuleRunner.Instance?.OnBattleClosed(record)` is called today.

## v1 producers and consumers — the complete roster

| Engine | Role | Wiring |
|---|---|---|
| RimChronicle recorder | battle records IN | `MapComponent_BattleRecorder.Close()` raises `battle.closed` (in-assembly) |
| RimProperty | taking-events IN | `PropertyEngine.Fire` raises `property.taking` into Chronicle via reflection, if present |
| RimPursuit | noticedness FROM record | subscribes; `GameComponent_ColonyVisibility.Adjust(delta, reason)` per `battle.closed` |
| Ninefold | god-deltas FROM record | subscribes; `GameComponent_Ninefold.ApplyDelta(God.Shkaar, …)` — replaces Chronicle's current outbound `ApplyNinefoldDelta` |
| ChronicleRites | rules FROM record | `RM_AftermathRuleDef.triggerOutcomes` matching, via today's `OnBattleClosed(record)` path |

## The soft-hook law (testable)

1. No `<modDependencies>` entry in any engine's About.xml names another
   `mandrake.*` engine (grep the five About.xml files; Harmony/Ludeon allowed).
2. No `<Reference Include="RimMandrake…">` between engine csproj files.
3. Every cross-engine XML node sits behind `MayRequire`; every cross-engine C#
   call sits behind `AccessTools.TypeByName` (or equivalent) with a null guard.
4. Each engine cold-loads standalone (engine + Harmony only) with zero errors.

## Explicitly OUT of v1

- Any event kind with no consumer named above — Ninefold's 17 `Patch_*` hooks
  (research, trade, marriage, …) stay Ninefold-internal, not spine kinds.
- Any universal recorder ambition; no persistence, no history query API beyond
  the recorder's existing `closedHistory` cap.
