<!-- status: live -->
# Restraining bolts — the technical spec

_A retired seat, 2026-08-13. Answers the four questions another retired seat posed in that seat's queue
C-v3; the fiction and the intent are `restraining_bolt_doctrine.md`, which this
does not restate. Drained out of the queue on its retirement to budget — the
queue keeps one line, this keeps the spec. Commit `8353622`._

**`[v2]` — lands with the Free Droid Enclaves, whose `FactionDef` is unbuilt.**

---

### 🔴 VERDICT: **CAP the ceiling.** One XML def + one ~40-line C# class. **Not a project.**

**And it beats all three options you offered**, because the mechanism that gives
the cap gives the *level* too, from the same class, recomputed from live state on
a timer the engine already runs. **Nothing is stored, nothing accumulates,
re-fire is impossible by construction.** Your "HELD, not ever-fitted" constraint
is not something we engineer around — it is the only thing this mechanism can
express.

`GoodwillSituationDef` / `GoodwillSituationWorker` is exactly what you suspected,
and it is fully mod-extensible: **three active mods already add their own.**
⛔ **Do not write a Harmony patch. Do not call `TryAffectGoodwillWith`.**

**The two numbers you are waiting on** — `RimWorld.FactionRelation::CheckKindThresholds`,
disassembled from `Assembly-CSharp.dll` with `src/RimMandrake/Utils/ilprobe/il.py`:

| event | threshold | IL |
|---|---|---|
| **Hostile** | effective goodwill **≤ −75** | IL_0021 `ldc.i4.s -75` → `bgt.s` skips; else `kind = 0` |
| **Ally** | effective goodwill **≥ +75** | IL_0049 `ldc.i4.s 75` → `blt.s` skips; else `kind = 2` |
| **Hostile → Neutral** | goodwill **≥ 0** | IL_0070 `ldc.i4.0 / blt.s`; else `kind = 1` |

**Hostility does not latch — but it does not un-latch where it latched.** You
fall in at −75 and only climb out at **0**. That is a 75-point trench, and staying
clear of it is the one hard constraint on your clamp.

---

### 1. Which mod supplies restraining bolts

**One mod. Only one. And it is not called what you think.**

| | |
|---|---|
| **Mod** | Outer Rim - Droid Depot |
| **packageId** | `Neronix17.OuterRim.DroidDepot` (`About.xml:6`) |
| **workshop id / folder** | **`3096501398`** |
| **path** | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3096501398` |
| **active** | yes — `ModsConfig.xml:549` |
| **supports** | 1.4 / 1.5 / 1.6; deps `Neronix17.Asimov` (active, line 61) + `Neronix17.OuterRim.Core` (active, line 536) |

⚠️ **The term in the game is "restraint bolt", never "restraining bolt".** Every
literal search for "restraining bolt" / `RestrainingBolt` / "inhibitor bolt" /
"slave circuit" across all 1242 workshop mods returns **zero**. The doctrine doc
should keep "restraining bolt" as our fiction but must not use it as a defName.

Swept the whole workshop tree: **Outer Rim Core, the BTD/KotOR packs, JDS
Separatist Droid Army and every other Star Wars mod supply no bolt-equivalent
device.** Outer Rim - Core only lists the item as trader stock
(`2919227155/1.6/Defs/TraderKindDefs/TraderKinds_Base.xml:91`).

### 2. 🔴 What SHAPE the application is

**The *state* is a plain vanilla `Hediff`. The *application* has THREE routes in
two assemblies.** That split is the whole answer.

All paths below under `…\294100\3096501398\1.6\` (1.4/1.5/1.6 copies are byte-identical).

| def | type | class | file:line |
|---|---|---|---|
| `OuterRim_RestraintBolt` | **HediffDef** | `HediffWithComps` ← **vanilla, no comps** | `Defs\HediffDefs\Droid_General.xml:30-53` |
| `OuterRim_RestraintBolt` | ThingDef | `ThingWithComps` | `Defs\ThingDefs_Items\Items_Droids.xml:4-51` |
| `OuterRim_AttachRestraintBolt` | RecipeDef | `Recipe_InstallImplant` ← **vanilla** | `Defs\RecipeDefs\Recipes_Surgery_Droid.xml:19-52` |
| `OuterRim_RemoveRestraintBolt` | RecipeDef | `OuterRimDroids.Recipe_RemoveBolt` | same file `:54-73` |
| `OuterRim_RestrainDroid` | JobDef | `OuterRimDroids.JobDriver_RestrainDroid` | `Defs\ThingDefs_Items\Items_Droids.xml:53-58` |
| `OuterRim_UseRestraintBolt` | JobDef | `JobDriver_UseItem` | `Defs\Misc\Jobs.xml:4-9` — ⚠️ **dead def, referenced nowhere** |

The attach recipe, verbatim (`Recipes_Surgery_Droid.xml:23,28,29,39`):
```xml
<workerClass>Recipe_InstallImplant</workerClass>
<targetsBodyPart>false</targetsBodyPart>
<isViolation>true</isViolation>
<addsHediff>OuterRim_RestraintBolt</addsHediff>
```
No `<recipeUsers>`, no `<appliedOnFixedBodyParts>`. It is attached from the pawn
side — `Defs\ThingDefs_Automatons\Humanlike\Droid__BaseHumanoidDroid.xml:159-160`
and `…\Animal\Droid__BaseAnimalDroid.xml:89-90`.
⭐ **`targetsBodyPart false` means it is a whole-pawn hediff** — `HasHediff(def)`
is a valid one-line test, with no body-part walk.

⛔ **It is NOT apparel.** ThingDef `category: Item`, `is.apparel = false`,
`tickerType: Never`. There is no `Notify_Equipped` / `Notify_Unequipped` to hook,
and no equip event of any kind. Prose implying a *worn* bolt is fine as fiction;
it must not become a requirement.

**Why the shape would have made this a project — and no longer does.** A hook on
"application" must cover **all three** live routes:

1. **Surgery** → vanilla `Recipe_InstallImplant` (shared with hundreds of implants).
2. **Item use** → vanilla `CompUsable` (`useJob UseItem`) → `Comp_TargetableOnAnyDroid`
   → `OuterRimDroids.Comp_TargetEffect_Restrain.DoEffectOn`
   (`1.6\Source\OuterRimDroids\Comps\Targetable\Comp_TargetEffect_Restrain.cs:15-28`).
3. **Downed droid** → `OuterRimDroids.JobDriver_RestrainDroid.Restrain()`
   (`1.6\Source\OuterRimDroids\Jobs\JobDriver_RestrainDroid.cs:46-52`), which calls
   `pawn.health.AddHediff(...)` **directly — no droid check, no violation, no goodwill.**

**Four moments, two assemblies, two of them shared vanilla classes.** That is the
"project" answer and it is the one you would have got last week.

⭐ **Counting the hediff collapses all four to zero.** Every route ends at the same
`HediffDef`. We read the result instead of intercepting the act — and the removal
recipe (`<removesHediff>`) is covered for free by the same read.

### 3a. Cheaply countable — **YES**

```csharp
PawnsFinder.AllMapsCaravansAndTravellingTransporters_Alive_OfPlayerFaction
    .Count(p => p.health?.hediffSet?.HasHediff(boltHediff) ?? false)
```

**This member satisfies your ownership ruling exactly**, and I verified the
cryptosleep clause rather than trusting the name:

- `PawnsFinder::get_AllMapsCaravansAndTravellingTransporters_Alive_OfPlayerFaction`
  IL_0021 `callvirt Thing::get_Faction` / IL_0027 `bne.un.s` — **filters on
  `Thing.Faction == Faction.OfPlayer`. Ownership, not presence.** Your rule, verbatim.
- It unions `AllMaps` + `AllCaravansAndTravellingTransporters_Alive`.
- `PawnsFinder::get_AllMaps` IL_002c → `MapPawns::get_AllPawns`.
- `MapPawns::get_AllPawns` IL_0000 → `get_AllPawnsUnspawned`, then IL_002d/IL_0039
  concatenates `pawnsSpawned` **plus** the unspawned set.
- `MapPawns::get_AllPawnsUnspawned` IL_0016 `ldc.i4.s 12 / ThingRequest::ForGroup`
  walks contained things recursively, dropping the dead at IL_0047 `Pawn::get_Dead`.

✅ **Cryptosleep caskets, containers and shelved droids are all counted** — the
undercount you flagged does not happen with this member. Caravans and travelling
transporters are in by name. A visitor's or raider's bolted droid in our base is
**out**. A droid sold is out the instant its `Faction` changes. Downed counts.

**Cost:** not cached — rebuilds its list per call, O(all pawns everywhere). At the
rate below that is free, but see the early-out in the build note; it is load-bearing.

### 3b. Periodic hook — **you do not need one**

`GoodwillSituationManager` already runs it.

```
FactionManager::FactionManagerTick  IL_0006 → GoodwillSituationManager::GoodwillManagerTick
GoodwillSituationManager::GoodwillManagerTick
    IL_000a: ldc.i4 1000
    IL_000f: rem
    IL_0010: brtrue.s IL_0019          ← only when TicksGame % 1000 == 0
    IL_0014: call GoodwillSituationManager::RecalculateAll
```

**Every 1000 ticks (~16.7 s real at 1×), plus on demand via `GetSituations`.**
No `GameComponentTick`, no `MapComponentTick`, no `WorldComponent`, no hediff tick.
We write a method; the engine decides when to call it.

### 3c. 🔴 Drift shape — **CONSTANT. "State a RATE" is dead.**

You were right to force this. `Faction::CheckReachNaturalGoodwill`, called from
`Faction::FactionTick` IL_0001:

```
IL_002a–IL_003e:  band = IntRange(NaturalGoodwill − 50, NaturalGoodwill + 50)
IL_0046:          if band.Includes(baseGoodwill) → naturalGoodwillTimer = 0; return
IL_0057:          naturalGoodwillTimer++
IL_006c:          ldc.i4 3000000                    ← below band
IL_0079:          if timer < 3000000 → return
IL_0084–IL_00ae:  TryAffectGoodwillWith(player, Mathf.Min(10, band.min − cur))
IL_00c5:          ldc.i4 3000000                    ← above band
IL_00dc–IL_0107:  TryAffectGoodwillWith(player, −Mathf.Min(10, cur − band.max))
```

**A flat ±10, at most once per 3,000,000 ticks, and only outside a ±50 dead band.**
3,000,000 ÷ 60,000 ticks/day = **50 in-game days**. Maximum drift the engine can
produce is **0.2 goodwill/day**, and inside ±50 of natural it is **exactly zero**.

**Constant, not proportional — the shape you feared.** A repeated-penalty design
is a step function: under 0.2/day it is absorbed entirely; over it, goodwill walks
to the floor regardless of N. **2, 12 and 40 bolts would NOT land at different
levels.** Your acceptance test fails on that route. Do not take it.

⚠️ **And it means `naturalGoodwillOffset` alone is nearly inert.** Moving *natural*
goodwill only re-aims a drift that needs 50 days to move 10 points, and does
nothing while current goodwill sits within 50 of the new target. **Setting the
level is necessary but not sufficient** — which is why the verdict is CAP, not
LEVEL, even though the same class provides both.

### 3c′. The ceiling — **exists, vanilla, and instant**

`Faction::GoodwillWith` — the value everything else reads:

```
IL_0002: call     Faction::BaseGoodwillWith
IL_000e: brfalse.s IL_0024                       ← if this is the player…
IL_0011: call     Find::get_GoodwillSituationManager
IL_0017: callvirt GoodwillSituationManager::GetMaxGoodwill
IL_001c: call     Mathf::Min                     ← effective = Min(base, maxGoodwill)
```

`GetMaxGoodwill` seeds **100** (IL_0008) and `Mathf::Min`s across every cached
situation (IL_0017). `GetNaturalGoodwill` **sums** every offset (IL_001b `add`).

**The cap applies the moment the cache recomputes — drift is not involved.**
`CheckKindThresholds` reads `GoodwillWith` (IL_0007), i.e. the *capped* value, so
the cap drives Hostile/Neutral/Ally directly. And after each recompute
`Recalculate` IL_0038 → `CheckHostilityChanged` →
`Faction::Notify_GoodwillSituationsChanged` IL_002a → `CheckKindThresholds`.

⭐ **So: free a droid, and within ≤1000 ticks the cap rises and the relation kind is
re-evaluated upward automatically.** Your "freeing droids stops the bleed" promise
holds mechanically, with **no removal hook at all** — provided base goodwill has
not itself been driven under 0 by real raids. That exception only exists if we go
hostile, which the clamp below prevents.

### 3c″. Is Jawa Trade Moot "capped at +75, never allied" an existing mechanism?

`design\Jawa\worldbuilding\faction_roster_v2.md:2317`. **Yes — this exact
mechanism. And the number in the roster is off by one.**
Ally fires at `goodwill >= 75` (`CheckKindThresholds` IL_0049 `blt.s`), so a cap of
**75 still allows Ally**. To mean "never allied" the worker must return **74**.
Same class we are about to write; fix the roster in the same commit.

⛔ **Trap that would otherwise have cost a game load:**
`GoodwillSituationDef.baseMaxGoodwill` **is read by nothing.**
`xref.py GoodwillSituationDef baseMaxGoodwill` → referenced by 1 method,
`GoodwillSituationDef::.ctor [stfld]`, and that is all. **Writing
`<baseMaxGoodwill>` in XML has literally no effect.** Only the worker's
`GetMaxGoodwill` return value is used (`Recalculate` IL_0026). Likewise
`naturalGoodwillOffset` is read only by `GoodwillSituationWorker_MemeCompatibility`
and `_SameIdeo` — a custom worker must read the field itself or it is ignored.
Base `GoodwillSituationWorker::GetMaxGoodwill` returns a hardcoded `100`
(IL_0000 `ldc.i4.s 100`); `GetNaturalGoodwillOffset` returns `0`. **Both must be
overridden.**

### 4. Does anything else patch bolt application — **NO**

- **Zero PatchOperations** anywhere in the workshop tree target `OuterRim_RestraintBolt`,
  `OuterRim_AttachRestraintBolt`, `OuterRim_RemoveRestraintBolt`, `OuterRim_RestrainDroid`,
  `Comp_TargetEffect_Restrain` or `Recipe_RemoveBolt`.
- **Zero foreign assemblies** reference `Recipe_RemoveBolt` or `Comp_TargetEffect_Restrain` —
  only Droid Depot's own `1.4|1.5|1.6\Assemblies\OuterRimDroids.dll`.
- **Zero mods anywhere** contain `CheckReachNaturalGoodwill`.

⭐ **And the chosen mechanism is the least collision-prone available.** Adding a
`GoodwillSituationDef` is **additive**: `Recalculate` IL_000f iterates
`DefDatabase<GoodwillSituationDef>.AllDefsListForReading` and each worker
contributes independently via `Min`/`sum`. **Two mods can both add situations
without fighting** — which a Harmony patch on a shared vanilla method cannot promise.
Proof it works in *this* stack: **42 situation defs are live today**, three of them
added by `llunak.moreprecepts` (`ModsConfig.xml:175`).

⚠️ **Neighbours to be aware of — active, and touching the same pipeline:**

| mod | `ModsConfig.xml` | what it does |
|---|---|---|
| `guy762.MM.KotORCore` | 577 | `Faction_CanChangeGoodwillFor_Postfix`, `GoodwillSituationWorker_PermanentEnemy_ArePermanentEnemies_Postfix` — **closest neighbour; a Star Wars mod rewriting goodwill rules** |
| `jaeger972.factionterritories` | 436 | patches `CanChangeGoodwillFor`, has `GoodwillToMakeHostile` |
| `azravos.factioncustomizer` | 147 | references `GoodwillSituationWorker` and `GoodwillSituationManager` |
| `ebsg.framework` | 25 | references `GoodwillSituationManager` |

None patch `GetMaxGoodwill` or `Recalculate`'s iteration, so none blocks us — but
if the cap ever reads as not applying, **`guy762.MM.KotORCore` is the first place
to look**, because it postfixes the gate our value flows through.

---

## ⛔ What the doctrine document cannot have as written

**1. "offset = −2.5 × N clamped at −100" declares war at 30 droids.**
Hostile is ≤ −75, and −2.5 × 30 = −75. **Clamp at −70, not −100** — margin, because
other negative situations stack via `Min` and are not exclusive.

**2. Make it a CEILING, not an offset — and your acceptance test passes.**
`maxGoodwill = 100 − 2.5N`, floored at −70:

| bolts | ceiling | what the player lives with |
|---|---|---|
| 2 | +95 | nothing lost; the dabbler is fine, as you required |
| 12 | +70 | **alliance now out of reach** — the first real bite |
| 40 | 0 | permanently neutral at best. No aid, no alliance, ever |
| 68+ | −70 | floor. Still **not** war |

⭐ **2, 12 and 40 land at visibly different levels, and drift is not an opponent** —
it carries the player *up* to the cap and stops, exactly as you hoped. And bolts
set **how much they help you, never whether they shoot**, which is your rule
expressed in the engine's own arithmetic rather than approximated by it.

**3. ⛔ "Bolt = minus. Unbolt = plus" describes a transaction that does not happen.**
There is no credit and no ledger. The count drops, the ceiling rises within 1000
ticks, and goodwill the player already earned becomes visible again. **This is a
better fit for the doctrine than a refund** — the Enclaves do not *reward* you for
stopping, they stop objecting. But the two-numbers framing should be reworded, or
whoever builds it will look for a payment that has nowhere to live.

**4. ⭐ The UI is free, and it is the beat you wanted.**
`GoodwillSituationManager::GetExplanation` IL_0048 appends each cached situation's
`LabelCap` to the faction card. **The player opens the Factions tab and reads a
line naming restraining bolts, with zero custom UI.** That is "somewhere a network
is counting", delivered by vanilla. Set `naturalGoodwillOffset` for this reason —
for the explanation line, not for effect.

**5. ⚠️ A live bug in Droid Depot will make us count things that are not droids.**
`1.6\Source\OuterRimDroids\Comps\Targetable\Comp_TargetableOnAnyDroid.cs:51-55`:
```csharp
pawn = t as Pawn;
if (pawn != null && pawn.def.HasModExtension<DefModExtension>())
    return true;
```
It tests the **base class** `DefModExtension` instead of `DefModExt_Droid`, so the
bolt can be aimed at **any pawn whose def carries any mod extension at all —
humans from other mods included.** A bolted human colonist would be counted by our
worker and would read to the Enclaves as an enslaved droid. **Not our bug and not
worth patching**; decide whether the worker filters to droid defs or accepts it.
⭐ I would **accept it**: "they object to the act, not the victim" is more in
character than a species check, and it costs us nothing.

---

## Build note — what this actually is

**One XML def + one C# class, ~40 lines, no Harmony.**

```xml
<GoodwillSituationDef>
  <defName>Jawa_RestrainingBolts</defName>
  <label>restraining bolts</label>
  <workerClass>RimMandrake.GoodwillSituationWorker_RestrainingBolts</workerClass>
</GoodwillSituationDef>
```

```csharp
public class GoodwillSituationWorker_RestrainingBolts : GoodwillSituationWorker
{
    public override int GetMaxGoodwill(Faction other)
    {
        if (other?.def != JawaDefOf.FreeDroidEnclaves) return 100;   // early-out FIRST
        return Mathf.Max(-70, 100 - Mathf.RoundToInt(2.5f * BoltedCount()));
    }
}
```

🔴 **The early-out is load-bearing, not tidiness.** `Recalculate` runs **every**
situation worker for **every** faction with `HasGoodwill`, on every recache — 42+
defs × the faction list — and `PawnsFinder.…_OfPlayerFaction` rebuilds its list on
each call. Return 100 on the faction check *before* counting, and the real walk
happens once per 1000 ticks instead of hundreds of times.

**Dependencies:** the Free Droid Enclaves `FactionDef` (unbuilt — deferred to v2),
and the bolt hediff. Resolve the latter with
`DefDatabase<HediffDef>.GetNamedSilentFail("OuterRim_RestraintBolt")` and return
100 if null, so the assembly degrades quietly if Droid Depot is ever dropped
rather than throwing on every recache.

`[v2]` — lands with the Enclaves.

---
