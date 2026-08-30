# BRIDGE_STORY_ALERT_TALE_TOOLS_1 — 5 gems from a full Find.X sweep

Filed 2026-08-29, FOUNDRY. Owner: "look more deeply... scour for any others. There
may be additional gems hiding." Method: cross-checked every static accessor on
`Verse/Find.cs` (~75 of them, the master list of every top-level game subsystem)
against the live tool surface. **43 were completely untouched.** Most are rendering/
UI internals with nothing worth exposing (WorldDebugDrawer, PawnCacheRenderer,
UniqueIDsManager, Tutor, ...); these five are real capabilities.

## Spec

New file `JawaBenchStoryTools.cs` (5 tools, all ungated):
- `jawa/alerts_list` — resolves the ORIGINAL roster's own UNCERTAIN row
  ("AlertsReadout.activeAlerts is private - list_alerts needs reflection"). One
  reflective field read; everything on `Alert` itself (`Active`, `Label`,
  `GetExplanation()`, `Priority`) is public. Answers "what does the game think is
  wrong right now", read-only.
- `jawa/tale_list` — `TaleManager.AllTalesListForReading`, public.
- `jawa/tale_record` — ⭐ **the answer to a problem this project already documented**:
  `JawaBenchPawnTools.cs`'s own header says there is NO free-text field on a Pawn,
  full stop, and that per-pawn notes would need storage built from scratch. Wrong —
  `TaleRecorder.RecordTale(def, pawn).customLabel = "..."` is exactly the mechanism
  the ENGINE ITSELF uses for its own custom-labeled tales (`GravshipUtility.
  SettleUtility` etc.). Scoped to 1-2 Pawn args on purpose — `TaleFactory.MakeRawTale`
  fills a Tale subclass's fields by matching ARG TYPES with no documented contract,
  and guessing a generic multi-type binder risked exactly the kind of wrong-guess
  this project's rules forbid. The pawn-only pattern covers most of the 90+ real
  `TaleRecorder.RecordTale` call sites grepped from source.
- `jawa/story_stats` — `StoryWatcher.statsRecord` (raid/threat/colonist-loss counts)
  + `StoryWatcher_Adaptation.AdaptDays`/`TotalThreatPointsFactor` — ⭐ the actual
  multiplier applied to every FUTURE threat's points from recent colonist losses.
  Nothing on the bridge could read this before; `jawa/weather_get`'s threat-points
  read is the storyteller's current roll, this is the adaptation factor feeding it.
- `jawa/faction_goodwill_situations` — `GoodwillSituationManager.GetSituations` etc.,
  the breakdown of WHY a faction's goodwill is capped/offset. Extends
  `jawa/faction_goodwill_check` (the number) with the reasons.

## Verify
Builds clean, 0 errors 0 warnings, first pass. 286 unique `jawa/…` names, no
duplicate alias (full-surface re-scan). **Not deployed** — game up, BENCH holds
bridge. Once deployed: `alerts_list` against a real active alert (e.g. a raid
warning); `tale_record` on a scratch pawn, confirm the customLabel sticks and
`tale_list` reads it back; `story_stats` after a colonist death, confirm
`adaptDays` moved.

## Live-verify 2026-08-30, FOUNDRY — 4 of 5 PASS, `alerts_list` is BROKEN. Not closed.

Full 585-mod list, fresh `start_debug_game_ready` quicktest map, bridge live.

### 🔴 `jawa/alerts_list` — FAILS every call. Real bug, cause identified exactly.

```
jawa/alerts_list {}  ->  success: false
  "AlertsReadout.activeAlerts could not be read by reflection - field may have been renamed."
```

Reproduced twice, `ticksGame` 1 and 563 — deterministic, not tick- or
content-dependent.

**The field was NOT renamed.** `RimWorld/AlertsReadout.cs:11` still declares
`private List<Alert> activeAlerts = new List<Alert>(16);` exactly as this item's
own header recorded it. The bug is in OUR reflection call:

`JawaBenchStoryTools.cs:82` uses the shared helper `FieldOrNull`, and that helper
(`JawaBenchVehicleTools.cs:102-109`) does `obj.GetType().GetField(name, PubInst)`
where `PubInst` is declared at `JawaBenchVehicleTools.cs:72` as

```csharp
private const BindingFlags PubInst = BindingFlags.Public | BindingFlags.Instance;
```

**`BindingFlags.NonPublic` is absent**, so `GetField` can never find a `private`
field and returns null unconditionally. The one tool in this batch whose whole
premise was "read a PRIVATE field by reflection" was wired to a public-only
helper. It has never worked and cannot work as built.

🔑 Confirmed it is the LOOKUP failing and not an empty alert list: an empty
`activeAlerts` would still be a non-null `List<Alert>`, so it would flow past the
`as IEnumerable` cast and return `count: 0`. Reaching the refusal branch proves
`GetField` returned null. `Find.Alerts` itself resolved fine — the earlier
`"No active AlertsReadout"` guard did not fire.

**Fix is one binding flag** (a `NonPublic`-including lookup for this call site,
without loosening the shared `FieldOrNull` other tools depend on), then rebuild +
redeploy. Not doable this pass: the game is UP and holds the DLL locked. Rides
the next game-down window.

### ✅ `jawa/tale_list` — PASS
Baseline read on the fresh map returned `totalCount: 1` and that one row is the
ENGINE's own custom-labeled tale: `{def: TileSettled, customLabel: "New
settlement", interestLevel: 0.01}` — i.e. the tool reads the exact mechanism
`tale_record` was built on, from a tale nobody on this side wrote.

### ✅ `jawa/tale_record` — PASS, customLabel sticks and reads back
```
tale_record {taleDef: "Recruited", pawn: Thing_Human743, otherPawn: Thing_Human739,
             customLabel: "FOUNDRY probe Recruited 2026-08-30"}
  -> success true, taleId 1, customLabel echoed,
     shortSummary "Person recruited: Blas 'Blas' Pieixoto, Kees 'Kees' Van Vugt"
```
Independent read-back `tale_list {onlyWithCustomLabel: true}` → `totalCount: 2`,
and row id 1 carries the exact label and the same two-pawn summary. ⇒ **a Pawn
CAN carry durable free text after all**, which is what this item claimed.

Refusals are honest, not silent: `taleDef: "Sick"` and `"Nonsense_NotADef"` both
→ `success: false, "No TaleDef 'X'."`; `"TileSettled"` (wrong arg shape for a
pawn-only call) → `success: false` naming all four real causes
(ignoreChance / colonistOnly / usableWithChildren / MakeRawTale class mismatch)
rather than reporting a tale it did not create.

### ✅ `jawa/story_stats` — PASS, proven by a real TRANSITION not one read
Killed a colonist (`Actions\T: Damage To Death` on Leonid, `Thing_Human747`),
stepped 120 ticks, re-read:

| field | before | after |
|---|---|---|
| `colonistsKilled` | 0 | **1** |
| `adaptDays` | 0.0 | **-30.0** |
| `totalThreatPointsFactor` | 0.8 | **0.4** |
| `greatestPopulation` | 3 | 3 |

`rimworld/list_colonists` independently confirms Leonid is gone (3 → 2). ⇒ the ⭐
claim holds: this reads the **live storyteller adaptation multiplier**, and it
visibly halved the points every future threat will be built with.

### ✅ `jawa/faction_goodwill_situations` — PASS, and internally consistent
```
Empire         maxGoodwill 100,  naturalGoodwillOffset -50
               situations: [Supremacist_All "Supremacist" (max 100, offset -50)]
PirateYttakin  maxGoodwill -100, naturalGoodwillOffset -40
               situations: [PermanentEnemy "Permanently hostile" (max -100, offset 0),
                            Guilty_All "Guilty" (+10), Raider_All "Raider" (-50)]
Insect         maxGoodwill 100,  offset 0, situations: []   (correct - hives have none)
```
🔑 The pirate row **checks out arithmetically against itself**: `0 + 10 + (-50) =
-40`, which is the reported `naturalGoodwillOffset`, and the `-100` cap traces to
the named `PermanentEnemy` situation. That is the breakdown this tool was for —
not a number, the reasons. Bad defName → `success: false, "No FactionDef 'X'."`.

## criteria
- [x] Owner directive: look deeper, scour for gems.
- [x] Full `Find.X` sweep (75 accessors), 43 untouched found, triaged for real value.
- [x] Every signature read from 1.6 source, not guessed — including the deliberate
      SCOPING-DOWN of tale_record rather than guessing a generic arg binder.
- [x] Builds clean, no duplicate alias (full surface re-scanned).
- [x] Deployed — all 5 registered on the live bridge (301 `jawa/` tools).
- [ ] Proven live. **4 of 5 pass** (`tale_list`, `tale_record`, `story_stats`,
      `faction_goodwill_situations`, each with a raw read-back or a before/after
      transition). `alerts_list` fails every call: `FieldOrNull`'s `BindingFlags`
      omit `NonPublic`, so the private `AlertsReadout.activeAlerts` can never be
      found. One-flag fix, needs a rebuild + a game-down deploy.

## Fix built, 2026-08-30, BENCH (offline pass, game UP — no deploy possible)

`FieldOrNull` (`JawaBenchVehicleTools.cs`, shared across the whole companion) now
looks up with `PubInst | BindingFlags.NonPublic` instead of `PubInst` alone —
additive only: every other caller of `FieldOrNull` (`JawaBenchPipeTools.cs`,
`JawaBenchSwcpCharacterTools.cs`, `JawaBenchVehicleAerialTools.cs`,
`JawaBenchVehicleTools.cs` itself) reads a known-public field, so nothing that
worked before can stop matching. `PropOrNull` and the file's other
`GetProperty(..., PubInst)` call sites were left untouched — only `FieldOrNull`
changed. Builds clean: `python.exe build.py --gm` → 0 errors, 0 warnings.
**Fixed in source, builds clean, awaiting next game-down deploy + live re-verify**
— criterion above stays unchecked until `alerts_list` is re-proven live.

--- history ---
