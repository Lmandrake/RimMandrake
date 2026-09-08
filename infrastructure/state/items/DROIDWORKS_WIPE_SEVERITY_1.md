## spec
Packet B10 of `design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` §5
(inputs: ruling 7, `Recipe_DWMemoryWipe`; outputs: `RSW_DW_RecentlyWiped`
7-day hediff with Moving/Manipulation ramps, random job interruption and
wall-bump collisions; service-record reset; permanent
`RSW_DW_HardwareQuirk` trait pool that accretes and never resets; verify:
"quicktest: wiped droid stumbles for 7 days, keeps the quirk after";
after: A1, already closed). Owner ruling 7, verbatim:

> *"Wipes: 7-day debuff + service-record reset, and make it REALLY severe.
> Like it bumps into walls, learns how to use its body, and frequently
> forgets what it was doing during that week. Frequently also adds a
> permanent hardware quirk that cannot be reset but only accrete
> further."*

`DROIDWORKS_WIPE_AND_SPIKE_1` had already built the recipe itself
(randomize traits, clear relations and social memories, set faction) and
its own header recorded that the severity half did not exist. Built
directly, FOUNDRY, 2026-09-08.

## Built
- **`RSW_DW_RecentlyWiped`, the 7-day debuff**
  (`Defs/HediffDefs/HediffDefs_Droidworks.xml`). `initialSeverity` 1.0 with
  `HediffCompProperties_SeverityPerDay` at `-0.142857` (= -1/7), so severity
  reaches 0 on day 7 and `Hediff.ShouldRemove` takes it off by itself —
  the same mechanism `RSW_DW_IonOverload` already uses, over days instead of
  hours. **Not `HediffCompProperties_Disappears`**: that expires at a fixed
  tick with severity flat throughout, which would impair the droid
  identically on day 6 and day 1 and then cure it in one frame. "Learns how
  to use its body" is a ramp. Three stages, ramping down as it heals —
  *blank slate* (Moving -0.45, Manipulation -0.50), *disoriented* (-0.25 /
  -0.30), *relearning* (-0.10 / -0.10). capMods are **offsets, not
  `setMax`** — a cap does nothing to a capacity already below it.
  Consciousness is deliberately untouched: below ~0.30 vanilla downs the
  pawn, and a wipe that collapses the droid is state 3, not a debuff.
- **`HediffComp_DWWipeStumble`** (`Source/Droidworks/
  HediffComp_DWWipeStumble.cs`), on that hediff. Every 250 ticks rolls
  `0.05 × severity`; on a hit it starts a vanilla `JobDefOf.GotoWander` to a
  random cell within 4 with `JobCondition.InterruptForced` and throws a
  "..." mote. One mechanism covers two clauses of ruling 7, because they are
  one event: the droid drops what it was doing ("frequently forgets") and
  blunders off ("bumps into walls"). The chance scales with severity, so the
  stumbling fades on the same curve the capMods do. Exempt: downed, dead,
  unspawned, drafted, in a mental state, already stumbling.
- **Service-record reset** (`Recipe_DWMemoryWipe.ResetServiceRecord`).
  Zeroes every `RecordDef` on `Pawn_RecordsTracker` — kills, damage taken,
  time as a colonist, distance walked — which is the pawn history the player
  can actually read, in the bio tab's Records page. Done by reflection
  (Harmony's `AccessTools`, already a reference of this assembly) onto its
  private `DefMap<RecordDef, float>`, then `DefMap.SetAll(0f)`: there is no
  public API that zeroes a record — `AddTo` `Log.Error`s on any
  `RecordType.Time` def, which is most of the service record, and there is
  no `Clear`. Resolved lazily and null-guarded so a future rename degrades
  to one warning instead of killing the recipe's `workerClass`.
- **Five permanent hardware quirks**
  (`Defs/TraitDefs/TraitDefs_Droidworks.xml`, new file):
  `RSW_DW_Quirk_ServoTwitch` · `_VocoderGlitch` · `_GyroDrift` ·
  `_MemoryHiccup` · `_NarrowFixation`. All `commonality 0` (vanilla's own
  idiom for a trait that must never be randomly rolled — Anomaly's
  `Traits.xml` uses it six times), no `exclusionTags`, no
  `conflictingTraits`, no disabled work tags. `_NarrowFixation` is a trade
  rather than a tax (ResearchSpeed ×1.10, SocialImpact ×0.80) — the
  framework doc §1.3's *"rare and valuable still even quirky"*.
- **The pool is a marker, not a list** (`Source/Droidworks/
  DroidworksHardwareQuirks.cs`): `HardwareQuirkExtension`, a
  `DefModExtension` on each quirk TraitDef. One marker answers both "which
  traits can a wipe grant?" and "which traits must a wipe never strip?", so
  the two can never drift apart, and a later packet adds a quirk in XML
  alone. Added to `DroidworksDefOf`: only `RSW_DW_RecentlyWiped` — the
  quirks deliberately are not there.
- **`Recipe_DWMemoryWipe` extended**: after the existing work it resets the
  service record, adds (or re-pins to severity 1) `RSW_DW_RecentlyWiped`,
  and rolls `QuirkChance = 0.6` for one quirk the droid does not already
  carry. **`RandomizeTraits` now skips quirks in both halves** — they are
  neither removed nor counted, so the droid gets back exactly as many
  ordinary traits as it lost and keeps every quirk on top. That single
  exclusion is what makes accretion real: wipe a droid three times, it
  carries three quirks.

## verify — live verify OWED, no bridge access this pass
The bridge was held by another FOUNDRY window for an unrelated full-list
cold-load restart the whole time this was built (`rimflow bridge who`:
*"held by FOUNDRY … for: confirming full-list restart for
DROIDWORKS_FULL_LIST_COEXIST_1 + B3-B6 content"*). One driver at a time, so
this packet stopped at offline proof deliberately. **Nothing here has been
seen running.**

- Build: `dotnet build Droidworks.csproj -c Release` — **0 errors, 0
  warnings**. All four new types confirmed present in the rebuilt
  `Assemblies/Droidworks.dll` (`HediffComp_DWWipeStumble`,
  `HediffCompProperties_DWWipeStumble`, `HardwareQuirkExtension`,
  `DroidworksHardwareQuirks`) rather than trusting "build succeeded" on a
  0.5 s incremental run.
- XML: all four changed/new files parse (`xml.etree.ElementTree`).
- Every engine field and method used was read from the RimWorld source
  before use, not guessed: `TraitDef.commonality` (private, XML-settable,
  read by `PawnGenerator.cs:1570`'s `RandomElementByWeight`),
  `TraitDegreeData`, `TraitSet.GainTrait`, `Pawn_RecordsTracker`,
  `DefMap.SetAll`, `MoteMaker.ThrowText`, `JobDefOf.GotoWander` (the exact
  call `JobGiver_Wander.cs:74` makes), and all seven StatDefs named in the
  quirk file (`Stats_Pawns_General/Social/WorkGeneral/Combat.xml`).
- **Owed to a bridge pass**: the packet's own verify line — quicktest a
  wiped droid, watch it stumble across the seven days, confirm the quirk is
  still on it afterwards and that a second wipe adds a second quirk rather
  than replacing the first. Also owed: a Player.log check for new
  `Config error in` lines from the new defs.

## Assumptions recorded (Charter: "record what you assumed")
1. **`QuirkChance = 0.6`** — FOUNDRY's own number for ruling 7's
   "frequently". Under 1.0 on purpose, so a wipe is a gamble and not a
   counter.
2. **Every capMod and stat number is FOUNDRY's own.** Ruling 7 gives an
   adjective ("REALLY severe"), no values. The severity lives in the seven
   days; the permanent quirks are deliberately mild (5–15 %).
3. **`stumbleChancePerCheck = 0.05` per 250 ticks, scaled by severity** —
   ~12 interruptions/day at full severity, ~6/day averaged across the week.
   FOUNDRY's own curve; "frequently", not "unusable".
4. 🔑 **Deviation from the packet's own wording, deliberate.** B10 names
   "wall-bump collisions via a `JobGiver` stub". A `ThinkNode` JobGiver
   is consulted only when a pawn NEEDS a new job, so it can make an idle
   droid wander but can never INTERRUPT the job it is already running — and
   interruption is the whole of "frequently forgets what it was doing". A
   HediffComp does both, lives on the hediff, and needs no think-tree
   insertion that could misfire on non-droid pawns. (Charter: "a named
   defName/xpath is an example, not a mandate".)
5. **"Service record" was resolved to vanilla's `Pawn_RecordsTracker`, not
   to a new stub.** A repo-wide grep for `ServiceRecord` returns **zero**
   hits in `src/` — there is no `CompServiceRecord` anywhere, and the
   droid-specific one is `DROIDWORKS_SERVICE_RECORD_DRIFT_1` (packet E2),
   unbuilt. Inventing a stub here would have pre-empted E2's design; doing
   nothing would have left a clause of ruling 7 unbuilt. Resetting the
   record vanilla already keeps — and the player already reads — satisfies
   the clause without touching E2's scope. **E2 remains fully owed.**
6. **Permanence is enforced by our own code, not by the engine.** Vanilla
   has no unremovable-trait flag; `TraitSet.RemoveTrait` will take anything.
   What holds the line is that the only trait-removing code in this mod
   (`RandomizeTraits`) asks `IsQuirk` first. Confirmed by a repo-wide grep:
   the only other `RemoveTrait` callers are `RimMandrake.Inhabited`'s
   `CharacterApplier` (a different mod) and the JawaBench bridge debug tool.
   Any future trait-removing code in Droidworks must make the same check —
   said so in `DroidworksHardwareQuirks`'s own header.
7. Drafted pawns are exempt from the stumble. A player who has taken manual
   control is mid-fight, and yanking the job there reads as a bug rather
   than as flavour. FOUNDRY's own scope call.
8. A second wipe on a still-wiped droid re-pins severity to 1.0 rather than
   no-opping — a second wipe must not be a way to shorten the first.

## finding, out of scope — filed here rather than acted on
🔴 **`CompPostTick` looks dead in RimWorld 1.6, and three Droidworks comps
use it.** `Pawn_HealthTracker.HealthTickInterval` (the 1.6 interval-tick
path) calls `Hediff.PostTickInterval` → `CompPostTickInterval`;
`CompPostTick` is only reached through the older `HealthTick` path.
`HediffComp_PoweredDown`, `HediffComp_DWBoltResentment` and
`HediffComp_IonOverloadsDroid` all override `CompPostTick` only. Whether
that means they never run depends on which `Pawn` tick path 1.6 actually
dispatches — `Pawn` overrides both `Tick()` and `TickInterval(delta)` and
this pass did not settle which one a spawned colony pawn takes, so this is
a **flag, not a verdict**. `HediffComp_DWWipeStumble` overrides **both**
entry points into one shared method (they are mutually exclusive branches,
so it cannot double-fire) precisely to be immune to the answer. Worth one
live check — if `CompPostTick` is dead, `RSW_DW_BoltResentment` has never
accumulated.
