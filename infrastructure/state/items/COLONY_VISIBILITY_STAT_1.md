## spec
Design pass (per F18/F12, `design/Jawa/salvation_engine_review.md`, and the
item's own brief) is DONE and offline: `design/Jawa/worldbuilding/colony_visibility_stat.md`,
linked from `design/Jawa/divine_satiation_engine.md` under the Matrix status
line. Nothing invented — every raise/lower hook cites an existing DEED,
BOON, DEMAND or CURSE already SHIPPED on a matrix page (Ishko, Ozzik, Ohm,
Sh'kaar, Ta'Baa); no new god behavior.

## 🔴 Owner ruled 2026-08-30: build the full replacement, not just the dial

Built and BUILDS CLEAN (0 errors / 0 warnings). Lives in `src/Jawa/Jawa_Doctrine/`
(the existing pantheon-wide-mechanics C# home used by
`DROIDWORKS_ISFLESH_RELATIONS_CRASH_1` — no new mod project needed; one
DLL per coherent concern, and Jawa_Doctrine's own About.xml already scopes
itself to "campaign-doctrine patches... enforce the Jawa design rules").
NOT deployed — game is up this session; queued for the next down window
with the rest of this session's pending fixes.

New files:
- `src/Jawa/Jawa_Doctrine/Source/DoctrineCore/ColonyVisibility.cs` — the
  safe-core `GameComponent_ColonyVisibility`.
- `src/Jawa/Jawa_Doctrine/Source/DoctrineCore/ColonyVisibilityRaidPatch.cs` —
  the F12 raid-point replacement + Ta'Baa launch-reset hook.
- `src/Jawa/Jawa_Doctrine/Source/DoctrineCore/DoctrinePatches.cs` — edited
  only to call `ColonyVisibilityRaidPatch.Apply(harmony)` alongside the
  existing patch.

### What's real and wired

- **The GameComponent itself.** `shipVisibility` (float, 0-100, starts 10),
  `ExposeData` persistence, the five-band ladder (`VisibilityBand`), and the
  one real generic mutator `Adjust(float delta, string reason)`. Registered
  automatically — `Verse.Game.FillComponents()` reflects over
  `GameComponent` subclasses (`AllSubclassesNonAbstract`, confirmed via
  RimSage read of `Source/Verse/Game.cs:472-489`), no Def/XML needed.
- **Ta'Baa's launch reset** (design doc §2 "Resets it"). A real Harmony
  postfix on `GravshipUtility.GenerateGravship` (verified via RimSage as the
  actual moment a gravship launch detaches the map into a `Gravship` world
  object — not guessed) calls `ResetOnLaunch()`, which drops
  `shipVisibility` to `Mathf.Clamp(shipVisibility * 0.15f, 5f, 15f)` per the
  design doc's own illustrative floor.
- **The F12 raid-point replacement, at ONE verified call site**:
  `Planet/TimedDetectionRaids.cs`'s `CompTickInterval` — a Harmony
  **transpiler** (justification below) swaps the call to
  `StorytellerUtility.DefaultThreatPointsNow` for
  `ColonyVisibilityRaidPatch.RaidThreatPointsNow`, which reimplements
  vanilla's pawn-power term (`num2`) verbatim and substitutes a
  Visibility-driven term for the wealth term (`num`), per the design doc's
  own §4.2/§4.3 plan. The transpiler logs an error (not a silent no-op) if
  it doesn't find exactly one call site to swap, so a future vanilla update
  that reshapes this method fails loud, not quiet.
- **Sh'kaar's escalation-meter seam**: `ShkaarEscalationMultiplier` field on
  the GameComponent, default `1f` (no-op), multiplied into the Visibility
  term only per §4.2's `finalFactor = visibilityFactor(V) *
  shkaarEscalationMultiplier`. Nothing sets it yet (Sh'kaar's meter isn't
  tracked in code) — TODO below.

### 🔴 Why only ONE of the spec doc's four named call sites got patched

Per this item's own instruction (#1: "confirm the exact current 1.6 source
of `DefaultThreatPointsNow` and its ~4 named call sites via RimSage... the
spec doc named them from source already, but verify against the LIVE 1.6
game version — don't trust the spec doc's line numbers blindly") — I did,
and **three of the four named citations do not match live 1.6 source**, and
would not have done what the spec doc thought even where the cited line
exists. Full re-read via `mcp__rimsage__read_csharp_symbol` /
`read_file` / `search_source`, not guessed:

1. **`IncidentWorker_RaidEnemy.TryExecuteWorker:88`** (spec doc's citation)
   — **wrong method**. `TryExecuteWorker` (lines 43-56 in current source)
   has no `DefaultThreatPointsNow` call at all. The actual call lives in
   `ResolveRaidPoints` (a *different*, sibling method), and it's a
   defensive fallback: `if (!(parms.points > 0f)) { Log.Error("RaidEnemy is
   resolving raid points. They should always be set before initiating the
   incident."); parms.points = StorytellerUtility.DefaultThreatPointsNow(...); }`.
   For an ordinary storyteller-fired raid, `parms.points` is **already set**
   before this runs — see below — so this branch does not execute in the
   normal game. Same story, same wrong-method mistake, for
   **`IncidentWorker_RaidFriendly.TryExecuteWorker:69`**.
2. **`QuestGen/QuestNode_GenerateThreats.cs:56`** — the line exists and does
   call `DefaultThreatPointsNow`, but only to build `storeThreatExampleAs`,
   a **cosmetic slate-text preview string**, not the actual quest-raid
   points computation. The real one is
   `RimWorld.ThreatsGenerator.GetIncidentParms`
   (`Source/RimWorld/ThreatsGenerator.cs:62`), reached from
   `QuestPart_ThreatsGenerator.MakeIntervalIncidents` — a different method
   entirely, not named in the spec doc.
3. **`Planet/TimedDetectionRaids.cs:138`** — verified correct as cited. The
   only one of the four that is both real and load-bearing.

**The actual dominant path for an ordinary wealth-scaled raid** — the
"storyteller looks at your wealth and decides to send a raid" case that F12
is fundamentally about — runs through `StorytellerComp_RandomMain
.GenerateParms` → `StorytellerUtility.DefaultParmsNow(incCat, target)` →
`DefaultThreatPointsNow`, **called before any `IncidentWorker` runs at
all**, populating `parms.points` on the `FiringIncident` that
`IncidentWorker.TryExecute` then just consumes. None of the spec doc's four
citations touch this path. Patching it narrowly requires distinguishing
"this `DefaultParmsNow` call is about to fire a raid" from "...an ambush /
mech cluster / manhunter pack / infestation / etc" — all of which share
`IncidentCategoryDefOf.ThreatBig` and reach `DefaultParmsNow` through the
identical call, before the specific `IncidentDef` is even chosen. **That is
the exact shared-function ambiguity §4.3 was written to dodge, one level up
the call graph** — real, load-bearing uncertainty about vanilla's behavior,
not something to guess through per this item's own instruction #4 ("if you
hit real uncertainty about vanilla's exact behavior at any of the 4 call
sites, STOP and document the uncertainty rather than guessing — a wrong
raid-scaling patch is a real gameplay-breaking risk, worse than leaving it
unbuilt").

**Net effect: the shipped patch genuinely changes the raid-point math for
detection raids only** (caravan/site "they found you" raids via
`TimedDetectionRaids`). Ordinary storyteller-fired wealth raids — most raids
a player will actually see — are **untouched by this build** and still run
on vanilla `PointsPerWealthCurve`. This is a real, correctly-scoped, honest
partial implementation of F12, not the full replacement the design doc
described — the doc's own call-site citations turned out to be wrong when
checked against the live source.

### TODO — not wired, explicitly flagged rather than guessed

1. **The dominant raid path** (`DefaultParmsNow`/`StorytellerComp
   .GenerateParms` for `ThreatBig`-category raids) — needs a fresh design
   pass on how to scope a patch there without also reshaping ambush,
   mech cluster, manhunter, and infestation point sizing. Not a rebuild of
   this item's transpiler technique; a genuinely open scoping question for
   the owner/BENCH.
2. **Quest-triggered raids** (`ThreatsGenerator.GetIncidentParms`) — same
   scoping question, one level down (shared with `MechCluster`).
3. **The other eight raise/lower hooks** in the design doc's §2 table
   (spotted/raided at home, challenge broadcasts, Renown, THE SHAMING,
   Overcurrent, melee fighting, flare-lighting, ambush kills,
   undetected-raid survival, concealed construction, darkness, blackout
   reign, Unseen Berth, the Unburdening rite) are **not called from
   anywhere**. Each needs either a new Harmony detection patch for a
   vanilla event with no discrete existing signal, or the not-yet-built
   satiation engine's own deed/boon/curse firing system to call into — and
   the doc's own magnitudes for these are explicitly "illustrative, not
   tuned" (decision #3 below). `Adjust()` and the `DeltaSmall/Medium/Large`
   constants are ready for that wiring; nothing invented past that.
4. **Orange Dusk / The Long Shadow** — structurally NOT one-shot `Adjust()`
   calls (they're decay-rate modifiers / night-pause effects). Flagged, not
   modeled — would need a modifier-list mechanism this pass doesn't build.
5. **Sh'kaar's escalation multiplier** — the seam exists
   (`ShkaarEscalationMultiplier`, default 1f) but nothing sets it; Sh'kaar's
   meter isn't tracked in code yet.
6. **F17's interface layer** (reign-calendar clause, band-crossing letters,
   inspect tag) — not built. `Adjust()`/`ResetOnLaunch()` log to
   `Log.Message` in dev mode only, as a debug aid, not the real UI.

## decisions owed (owner/BENCH, not mine to make)
1. **Re-scoped**: how (or whether) to patch the actual dominant raid path
   (`DefaultParmsNow` for `ThreatBig`) without touching ambush/mech
   cluster/infestation point sizing — a harder problem than the spec doc's
   original "4 call sites" framing assumed, discovered only by re-reading
   live source per this item's own instruction.
2. Whether quest-triggered `ThreatsGenerator` raids should also route
   through Visibility, given the `MechCluster` entanglement noted above.
3. Sh'kaar's meter multiplying the derived points only (recommended,
   already implemented as the seam's contract) vs. multiplying the
   displayed number too.
4. All S/M/L deltas and the Visibility→raid-points curve anchors — the
   shipped `VisibilityFactorCurve` and `DeltaSmall/Medium/Large` are the
   design doc's own illustrative anchors, explicitly not tuned, deferred to
   a throwaway-save test rig per the engine doc's own §9/§10 convention.
5. Launch-reset floor (illustrative 5-15, shipped as-is) and whether a
   "snatched free with enemies boarding" launch resets lower than a
   routine one.
6. Per-settlement Visibility for a colony that settles (F14) — out of scope
   v1, flagged only.

## ✅ DEPLOYED AND LOADING CLEAN — live check 3 of 3 done, 2026-08-30 (FOUNDRY)

`JawaDoctrineCore.dll` is deployed and in the running 585-mod build. Fresh
quicktest, game paused. **Verify step 3 below is DONE and passes; steps 1 and 2
are not, and this item stays `doing`.**

**Both Harmony patches are registered on the live game** — `jawa/harmony_patches`,
raw:
```
TimedDetectionRaids.CompTickInterval
  transpilerCount 1
    owner        mandrake.jawadoctrine.core
    patchMethod  JawaDoctrineCore.ColonyVisibilityRaidPatch.Transpiler_SwapDefaultThreatPoints
    patchAssembly JawaDoctrineCore     patchInfoError null

GravshipUtility.GenerateGravship
  postfixCount 1
    patchMethod  JawaDoctrineCore.ColonyVisibilityRaidPatch.Postfix_ResetVisibilityOnLaunch
```

**✅ Verify step 3 passes: the transpiler's failure error did NOT fire.**
`Player.log` (current session's, 703 KB, mtime 14:36) contains **zero** lines
matching `JawaDoctrineCore` or `ColonyVisibility`. Control: the same grep returns
40 hits for `Harmony`, so the instrument works and the file really does cover
startup. ⇒ the transpiler found exactly its one call site and swapped it; a
failed swap would have logged `"expected exactly 1 call-site swap"`
(`ColonyVisibilityRaidPatch.cs:175`) at patch time.

**The GameComponent is instantiated on a live game.** Proven by saving the
quicktest and reading the component list out of the `.rws`:
```
<li Class="JawaDoctrineCore.GameComponent_ColonyVisibility" />
```
⇒ `Game.FillComponents()` reflected over it and constructed it with no Def or XML,
exactly as designed, and it takes part in `ExposeData`. The element is
**self-closing and that is correct**: `ExposeData` writes
`Scribe_Values.Look(ref shipVisibility, "shipVisibility", 10f)` and
`shkaarEscalationMultiplier` with default `1f`, and a brand-new game holds both at
their defaults, which Scribe omits. Not evidence of a broken `ExposeData` — the
element's presence is the finding.
⚠️ **Not proven: that a CHANGED value round-trips.** Nothing on the bridge can call
`Adjust()`, so the persistence path was observed only at its defaults.

⚠️ Steps 1 and 2 below still owed, and neither is cheap: step 1 needs a real
gravship launch, step 2 needs a `TimedDetectionRaids` countdown driven to fire plus
a way to set `shipVisibility` (no debug gizmo exists yet). **The scoping decisions
owed above are the real blocker regardless** — the dominant storyteller raid path
remains unpatched by design.

## Verify — needs the bridge
Once deployed:
1. Quicktest: force a gravship launch, confirm `shipVisibility` drops to
   the 5-15 floor (dev-mode log line `[ColonyVisibility] launch reset:`).
2. Quicktest: drive `shipVisibility` to a few different values (dev console
   or a temporary debug gizmo), force a `TimedDetectionRaids` countdown to
   fire, confirm the resulting raid's `parms.points` moves with Visibility
   rather than tracking colony wealth — and confirm an ordinary
   storyteller-fired `ThreatBig` raid does NOT move with Visibility (proves
   the scoping held).
3. Confirm the transpiler's "expected exactly 1 call-site swap" log line
   does NOT fire (would mean the patch silently failed to apply against
   the deployed game's actual IL).

## Watch out
🔴 **This item stays `doing`, not `closed`.** Updated 2026-08-30: it is now
deployed, both patches are registered, the transpiler applied without error and
the GameComponent is instantiated on a live game — so *"unverified live"* is no
longer the blocker. What still blocks closing:
1. The raid-point math has never been **observed changing** — steps 1 and 2 of
   Verify (gravship launch reset, and a detection raid whose points track
   Visibility rather than wealth) are undone.
2. Three of the design doc's four F12 call sites were wrong against live source,
   so the **dominant storyteller raid path is genuinely unpatched** and the scoping
   decision for it is owed to the owner/BENCH (decisions 1 and 2 above).
