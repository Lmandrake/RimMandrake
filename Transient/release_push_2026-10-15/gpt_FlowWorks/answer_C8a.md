I found eight issues worth checking before release. None establishes liquid loss or save corruption from this input alone. Checks below are proposed, not executed. Locations use exact code quotations rather than uncertain line numbers.

**F1 — MEDIUM — A failed settings import is permanently marked complete**

**Where:** `RM_HoseLegacy.cs`, `ImportOnce()`:
```csharp
RM_HoseSettings.hoseSettingsImported = true;
```
This runs before file discovery, reads, parsing and assignment.

**What happens:** An I/O exception leaves the flag true, and the method still returns true—the documented instruction for its caller to write settings. Subsequent attempts immediately return false. Failure after importing hose values but before reading cord settings also leaves a permanently partial import.

**Repro:** Upgrade with the legacy settings file temporarily unreadable. Launch once, restore access, and restart. The import no longer retries.

**Suggested check:** Offline test with an injected file-read failure; assert that failure leaves import eligibility intact and does not commit partial values.

**Confidence:** High.

---

**F2 — LOW — Style import can choose an unrelated stale file over the preferred folder**

**Where:** `RM_HoseLegacy.cs`:
```csharp
foreach (string suf in RM_HoseLegacyMath.CordFileSuffixes)
    if ((cordFile = Pick(dir, prefer, suf)) != null) break;
```

**What happens:** Selection prioritizes suffix before preferred folder or modification time. Any `_GimmeSomeSlackMod.xml` file wins over every `_MessyConduitMod.xml` file—even when the latter belongs to the preferred deployed folder. `PickFile()` applies its preference only within the first suffix’s candidates.

**Repro:** Keep a stale GimmeSomeSlack settings file with one style and a preferred-folder MessyConduit settings file with another. Perform the first FlowWorks import. It inherits the stale style.

**Suggested check:** Offline fixture containing both suffixes, with the preferred folder represented only by the second. Assert that the preferred file wins across the combined candidate set.

**Confidence:** High.

---

**F3 — MEDIUM — Non-finite legacy numbers are accepted; NaN length disables length rejection**

**Where:** `RM_HoseLegacyMath.cs`:
```csharp
public static bool TryFloat(string s, out float v) => float.TryParse(s, NumberStyles.Float, CultureInfo.InvariantCulture, out v);
```
`RM_HoseLegacy.cs` assigns successfully parsed floats directly with `f.SetValue(null, x)`.

`HoseMath.cs`:
```csharp
public static bool Overlong(HoseLay lay, double maxLength) => Math.Max(lay.FlatLen, lay.PlumpLen) > maxLength + 1e-6;
```

**What happens:** `"NaN"` parses successfully. Migration preserves it. Comparisons against NaN are false, so the straight-distance, route-length and final `Overlong()` checks all fail open when supplied that length. Other imported non-finite shape parameters can contaminate geometry.

The shown import contains no validation; whether an omitted settings accessor subsequently repairs these values needs checking.

**Repro:** Put `<maxLength>NaN</maxLength>` in the legacy settings file before first import, then attempt a deployment beyond the normal limit.

**Suggested check:** SelfTest cases for `TryFloat("NaN")`, imported infinity, and `Overlong(validLay, double.NaN)`. Verify rejection or normalization before settings reach hose math.

**Confidence:** High for the math defect; medium for player impact pending `RM_HoseSettings`.

---

**F4 — MEDIUM — Short hoses are rejected using the reel centre instead of the routing mouth**

**Where:** `HoseMath.cs`, `CheckInstall()`:
```csharp
if (V2.Dist(reel.Centre, target.Centre) > maxLength) return "too far";
```
But `RoutePulled()` starts with:
```csharp
var pts = new List<V2> { reel.Mouth };
```

**What happens:** For a 2×2 reel, the mouth is almost one cell west of its centre. The early rejection can refuse a western target whose actual mouth-based route fits, including the 5% margin.

**Repro:** On open ground, use `HoseReelRect(20, 20, 2, 2)`, target cell `(11, 20)`, and length `9`. Centre distance is about `9.513`, so installation returns `"too far"`. Mouth distance is about `8.531`; multiplied by `RouteMargin`, it is about `8.957`.

**Suggested check:** SelfTest that exact fixture, comparing `CheckInstall()` with the mouth-based route calculation. Also check the finished nozzle lay.

**Confidence:** High.

---

**F5 — MEDIUM — Tight-corner fallback can accept a hose below its minimum bend radius**

**Where:** `HoseMath.cs`, `LayOnce()`:
```csharp
if (!Clear(w, F)) F = Geo.Resample(planPoints, Sample);
```
The eventual acceptance is:
```csharp
lay.MinBendFlat = MinBendRadius(lay.Flat, EndSkip);
lay.MinBendPlump = MinBendRadius(lay.Plump, EndSkip);
```
followed by `lay.Ok = true`.

**What happens:** When rounded/stiffened poses cannot clear obstacles, the fallback restores the polygonal plan. That restores sharp corners. The final minimum radii are measured but never used to reject the lay. The outlet-specific radius check covers only its lead-out window, leaving downstream corners unchecked.

**Repro:** Deploy through a narrow right-angle corridor where rounding clips the inner corner but the original string-pulled segments remain clear. Inspect a downstream bend away from the nozzle.

**Suggested check:** SelfTest a tight corridor and assert that every successful lay meets the configured minimum radius outside explicitly exempt end regions. Exercise the polygonal fallback deliberately.

**Confidence:** High for the acceptance gap; medium for the exact corridor needed to trigger it.

---

**F6 — MEDIUM — A hose can pass through a wall while filling even when both endpoint poses pass clearance**

**Where:** `HoseMath.cs`, `Pose()`:
```csharp
for (int i = 0; i < n; i++) o.Add(lay.Flat[i] + (lay.Plump[i] - lay.Flat[i]) * e);
```
and:
```csharp
w.Add(o[i] + nn * Wobble(i / (double)(n - 1), ticksSinceChange, transitionTicks, plumpAmount));
```

**What happens:** `LayOnce()` checks flat and plump poses separately. `Pose()` neither checks the interpolation nor the added wobble. Clearance of both endpoints does not guarantee clearance of their intermediate positions around a corner. Wobble can also push a near-wall sample beyond the accepted tolerance.

**Repro:** Lay a hose close around a wall corner, then repeatedly start and stop flow. Look for transient clipping during filling/draining rather than in the settled poses.

**Suggested check:** SelfTest generated obstacle layouts: for each accepted lay, sweep blend values and wobble ticks, then run `Clear()` on every resulting pose.

**Confidence:** High that the clearance guarantee is missing; medium for occurrence frequency.

---

**F7 — LOW — Fitting overlap checks miss hoses in different pressure states**

**Where:** `HoseMath.cs`, `FootprintOn()`:
```csharp
foreach (bool plump in new[] { false, true })
{
    List<V2> P = plump ? a.Plump : a.Flat, Q = plump ? b.Plump : b.Flat;
```

**What happens:** It compares flat/flat and plump/plump only. Hoses have independent state machines, so flat/plump and plump/flat are ordinary live combinations. A joiner can overlap another hose only in one of those mixed states and therefore survive the suppression check. `FittingsOnTop()` shares the same blind spot.

**Repro:** Cross two hoses near a joiner, then run one while leaving the other flat. A fitting can appear over the other hose despite the layering rule.

**Suggested check:** SelfTest all four endpoint-state combinations for two lays, including a fixture where only a mixed combination overlaps. Extend coverage to intermediate blends if practical.

**Confidence:** High.

---

**F8 — LOW — Changing transition duration mid-transition causes an immediate visual jump**

**Where:** `HoseMath.cs`, `Blend()`:
```csharp
case HoseVis.Filling: return Geo.Clamp(B0 + (now - Since) / (double)T, 0, 1);
```
`Draining` uses the equivalent subtraction. `transitionTicks` is explicitly listed among player-facing imported settings.

**What happens:** The current duration is applied retroactively to all elapsed ticks. Changing it does not preserve the current blend. For example, a filling hose at tick 15 with duration 30 has blend `0.5`; changing duration to 300 makes it `0.05` immediately.

**Repro:** Start flow, pause halfway through filling, change transition duration substantially, and resume.

**Suggested check:** SelfTest a tuning change at a fixed tick. Assert blend continuity when adopting the new duration, then verify the subsequent rate.

**Confidence:** High.

## Outside this slice

The following omissions prevent stronger save/load, conservation and lifecycle conclusions:

- `CompHoseReel.ExposeData`, its load initialization, saved route representation, and migration defaults.
- `RM_MapComponent_Hoses` and `Patch_Map_ExposeComponents_SkipHoses`, especially component restoration on exceptions and loading.
- `RM_HoseSettings`, including validation, persistence and live-setting application.
- `CordWorld`, `Geo`, `CordPlanner`, `CordLayer`, `HoseTrail`, and `HoseRelay`.
- Pump timestamps, hose contents, draining, endpoint transfer/debit logic, job drivers and XML definitions.

Two additional local hazards need caller evidence before becoming player findings: `ResampleN()` indexes `s[j + 1]` for a singleton input, and `PumpFlowing()` accepts future timestamps because it has no nonnegative-age check. The cost-enabled bounded route search also retains only one cost/length label per cell; a cheaper longer arrival can suppress a feasible shorter arrival. `CheckInstall()` explicitly uses `costs: false`, so that is **not** evidence that the previously fixed installation bug remains.

`known_behaviours.md` was referenced but not supplied, so ledger deduplication beyond the brief was unavailable. No supplied file appeared truncated.