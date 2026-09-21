# SHRUBLAND_GIANT_ENRAGE_1 — RSW_ShrublandGiant: large-young life-stage + parental enrage-on-approach C#

## what is wrong

`COMMISSION_LEDGER_CLEANUP_1`'s arid_shrubland sheet slug
`the-huge-grazer-large-young-parental-enrage-body-donors-famb` shipped its
**def** this pass (`RSW_ShrublandGiant`,
`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_ShrublandGiant.xml` — a
reskin of the already-ported `RSW_Fambaa`/`RSW_Dewback` body and art, wired
into `RUT_AridShrubland.xml`'s `wildAnimals` at 0.35) but ships as a plain
grazer with no special behaviour, exactly the `DESERT_SHADE_WHALE_FILTERFEED_1`
precedent (def lands first, mechanic comp follows in its own item).

`arid_shrubland.md`'s own size ladder (§4, owner-ratified) is explicit:

> **Large** — giants' children only, and 🔴 **approach is attack: the parent
> enrages if you even get near the young.** No warning is given.

And the biome doc's own "Owed" section lists this as part of a **still-unrun
engine feasibility pass**: "parental enrage on approach" sits alongside
venomvine's passability as one of the mechanics this biome has never had
checked against the actual engine.

## why it matters

Without it, "the large band is a void populated by exactly one thing — the
young of the huge" is prose with a juvenile lifestage sprite (already free,
Fambaa's own `Fambaa_j_*` art) but no teeth: nothing punishes getting close to
a calf, so the size ladder's own defining rule ("approach is attack") does not
exist in play.

## the work

1. **Engine feasibility check first** — this biome doc explicitly flags this
   as part of an unrun feasibility pass. Before writing C#, confirm what
   vanilla/Harmony hook can detect "a hostile-or-neutral pawn entered melee/
   interaction range of a juvenile-lifestage pawn of this race" without a
   per-tick full-map scan. Candidates to survey: a `Thing.Tick` override on
   the juvenile checking nearby pawns periodically (cheap, bounded radius);
   or a `JobGiver`/mental-state trigger on the ADULT that fires when its own
   juvenile (if `RSW_ShrublandGiant` gets any parent/offspring bond tracking
   vanilla already supports — check `Pawn_RelationsTracker`) is approached.
2. **The enrage state itself**: likely a short mental state (`MentalStateDef`,
   manhunter-like but scoped and time-boxed, "aggressive" toward the
   approaching pawn only) on the ADULT nearest the threatened juvenile, not a
   permanent manhunter flip — "no warning is given" describes the trigger,
   not a request for a berserk animal.
3. Wire onto `RSW_ShrublandGiant`'s `ThingDef` via a new `DefModExtension` +
   comp, same shape as `RM_ShadeSeekingWanderExtension`/
   `RM_FilterFeedExtension` (`RimMandrake.CreatureBehaviors`), so it can be
   MayRequire-gated and reused by any other "giant with young" species later
   without new C# per species.

## Watch out

- Do not touch `RSW_Fambaa` itself — `RSW_ShrublandGiant` is a separate
  defName reusing its body/art only, and `RSW_Fambaa` stays placed wherever
  it already is (swamp biomes, unrelated to this item).
- `RSW_ShrublandGiant`'s own comment block documents everything already
  decided about it (stats, life stages, working name) — read it before
  touching the def.
- This is a working-name def (`ARIDSHRUBLAND_SHIPPING_NAMES_1`); a rename
  there does not block this item, but keep both in sync if the rename lands
  first.

## criteria

Approaching a juvenile `RSW_ShrublandGiant` triggers a scoped aggressive
response from its nearest adult, verified live (quicktest or full load) —
this is explicitly a "never-observed mechanism" until someone runs it, same
caution `VENOMVINE_LIVE_VERIFY_1` records for its own build.

## status — BUILT, LIVE VERIFICATION OWED (2026-09-20, `5a853a4cb`)

Steps 1–3 are done. **The item stays open on its own criteria**: the mechanism
has never been observed running, and nothing below is a substitute for that.

### What was built

In `mandrake.rm.creaturebehaviors` (RM tier, names no species):

| file | role |
|---|---|
| `src/RimMandrake/CreatureBehaviors/Source/RM_ParentalEnrageExtension.cs` | `DefModExtension` carrying ALL tuning |
| `src/RimMandrake/CreatureBehaviors/Source/RM_CompParentalEnrage.cs` | the trigger — bounded radial scan on the CALF at `CompTickRare` |
| `src/RimMandrake/CreatureBehaviors/Source/RM_CompProperties_ParentalEnrage.cs` | bare ticker props; `ConfigErrors` refuses a carrier with no extension |
| `src/RimMandrake/CreatureBehaviors/Source/RM_MentalState_ParentalEnrage.cs` | the scoped, time-boxed rage |
| `src/RimMandrake/CreatureBehaviors/Defs/MentalStateDefs/RM_ParentalEnrage_MentalStates.xml` | `MentalStateDef RM_ParentalEnrage` |

Wired onto `RSW_ShrublandGiant` (`MayRequire="mandrake.rm.creaturebehaviors"`),
two XML blocks, no per-species C#. Mod Settings toggle #27
(`parentalEnrageEnabled`) shipped per the every-mod-ships-settings ruling.

### Step 1, the engine feasibility answer (the thing the item asked for first)

🔑 **No Harmony, and no think-tree patch of any kind is needed.** MEASURED
against the decompiled 1.6 engine, 2026-09-20:

- Core's `ThinkTreeDef MentalStateNonCritical` routes manhunting through
  **`ThinkNode_ConditionalMentalStateClass`**, whose `Satisfied()` is
  `stateClass.IsInstanceOfType(mentalState)` — an **instance** check, NOT the
  def-identity check its sibling `ThinkNode_ConditionalMentalState` performs
  (`pawn.MentalStateDef == state`). So a **subclass** of
  `MentalState_Manhunter` inherits `JobGiver_Manhunter`'s whole chase-and-melee
  behaviour for free. ⛔ This inheritance is load-bearing: flatten it and a pawn
  holds a mental state with no behaviour and nothing appears in the log.
- **Scope** is `GenHostility.HostileTo(Thing, Thing)` consulting
  `MentalState.ForceHostileTo(Thing)` before any faction logic.
  `RM_MentalState_ParentalEnrage` answers true for the intruder alone and
  `ForceHostileTo(Faction)` **false**, so faction hostility never flips and
  `AttackTargetFinder.BestAttackTarget`'s `searcher.HostileTo(thing)` filter
  finds exactly that pawn. A melee-only animal takes `BestAttackTarget`'s
  `GenClosest.ClosestThingReachable` branch, not `GetPotentialTargetsFor`, so
  a factionless wild giant genuinely can reach a player colonist this way.
  Hostility is symmetric for free, so the targeted pawn may fight back while
  their colony does not go to war with the wildlife.
- **Time-box** is vanilla's own `MentalState.forceRecoverAfterTicks`, already
  honoured by `MentalState.MentalStateTick`. No custom timer.
- 🔴 **There is no vanilla parent bond to hook for a WILD herd.**
  `Hediff_Pregnant.DoBirthSpawn` DOES add a real `PawnRelationDefOf.Parent`
  direct relation for any flesh race that gives live birth — so a calf **born**
  on the map knows its mother — but map-gen/ambient wildlife is generated
  pawn-by-pawn with no relation at all. Hence: relation used as a *preference*
  (`preferTrueParent`), nearest adult of the same race as the fallback.
- **Trigger cost**: `GenRadial.RadialDistinctThingsAround` bounded by
  `triggerRadius` (~80 cells at the shipped 5) on the calf at `CompTickRare`;
  adults carry the comp and are inert. The wider guardian search
  (`AllPawnsSpawned`) is paid **only** on the rare tick an intruder was found —
  cheaper than a 30-cell radial (~2800 cells) on the common path.

### Offline verification done

- `RM_CreatureBehaviors.csproj` builds **clean** (0 warnings, 0 errors).
- `validate_patch.py` clean on both XML files (full 618-mod load set for the
  ThingDef; the two `info` lines are the expected "first user of a new Class").
- `run_selftests.py`: **69/69 passed**, 0 failed.

### 🔴 What is OWED — do not close this item without it

The bridge was held by the other window (`FOUNDER_ROBE_MAGENTA_1`, provably
alive) for this whole pass, so **nothing has been deployed and nothing has been
observed**. Owed, in order:

1. `deploy_custom_mods.py --mod CreatureBehaviors --apply` and `--mod SWBestiary
   --apply`. ⚠️ Assemblies cannot be written while the game runs. ⚠️ As of this
   pass another agent had **uncommitted in-flight work** in SWBestiary
   (`ScrapNest`, `CompScrapHoarder`/`JobGiver_HoardScrap`, a modified
   `RimMandrakeBeastMechanicsRSW.dll`) — read the deploy PLAN before `--apply`
   and do not push a peer's untested work into the live Mods folder.
2. A tier with SWBestiary + CreatureBehaviors + the shrubland biome (per
   `modset_builder.py`; all tiers now force all five DLC).
3. Spawn an adult/juvenile `RSW_ShrublandGiant` pair close together, walk a
   colonist within 5 cells of the **juvenile**, and confirm the **adult**
   enrages. Spawn several pairs — one pawn's result can be pure RNG.

**The positive observation to name** (never "no error"): the adult's inspect
line reads **`Enraged: defending young: <calf label>`** and it takes an
`AttackMelee` job on the approaching colonist **specifically**.

**How a pass could be false:**
- The adult charges because the colonist walked near the **adult** too — keep
  the adult ≥ 8 cells from the intruder's path so only the calf is approached.
- The adult attacks because something **damaged** it: `RSW_ShrublandGiant` has
  `manhunterOnDamageChance 0.02`, an unrelated vanilla route. Do not hit it.
- It reads as working but is actually plain vanilla `Manhunter` — confirm the
  state is `RM_ParentalEnrage` (the inspect line above, not "Maddened:
  Manhunter") and that a **second, untouched colonist standing in plain sight
  is NOT attacked**. That second check is what proves the scoping, and it is
  the one that would be skipped.
- The calf is spawned as an adult: `jawa` spawn tools substitute silently, so
  verify the juvenile's life stage (its label should be **"giant calf"**)
  before believing anything.

## LIVE-VERIFIED 2026-09-21 — the mechanism was observed running, on all four pairs

Run environment: new `shrublandfauna` tier in `modset_builder.py` (19 mods, all
five DLC — the union of `beastmechanics` and `desertplants`, which is what this
item plus three others needed in one load). `deploy_custom_mods.py --mod
CreatureBehaviors --apply` landed the owed three files (the new MentalStateDef,
About.xml, `RimMandrake.CreatureBehaviors.dll`) and reported VERIFIED in sync;
SWBestiary and EnvironmentalHazards were already in sync, and the deployed
`RimMandrakeBeastMechanicsRSW.dll` was left alone (it is another item's work and
was already byte-current). Load was clean for this mod: `jawa/get_defs` resolved
`ThingDef/RSW_ShrublandGiant`, `PawnKindDef/RSW_ShrublandGiant` and
`MentalStateDef/RM_ParentalEnrage` 3 of 3, and `Player.log` carried no
`Could not find type named RimMandrake.CreatureBehaviors.*` line.

### The staging, built against this item's own four false-pass traps

Four independent clusters at X = 40 / 80 / 120 / 160 on one quicktest map:

| role | cell | distance to calf | distance to adult |
|---|---|---|---|
| calf | (X, 60) | — | 15 |
| adult | (X, 75) | 15 | — |
| intruder colonist | (X, 64) | **4** (inside `triggerRadius` 5) | **11** |
| control colonist | (X+9, 75) | 17.5 (outside 5) | 9, in plain sight |

- **Calf life stage verified before believing anything**, exactly as the trap
  says: `jawa/set_pawn_age biologicalYears=0.25 allowBackwards=true`, and
  `jawa/list_things includePawns=true` then read the label back as
  **`Giant calf`** for all four calves and **`The giant`** for all four adults.
  ⚠️ Worth knowing for the next run: 0.25 y is life-stage index 0 (`AnimalBaby`)
  and that is the ONLY stage the PawnKindDef gives a label to. An 0.7 y juvenile
  is index 1, is equally "young" to the comp, and still reads `The giant` — so
  the label check only works on a baby-aged calf.
- **The adult was kept 11 cells from the intruder** (trap asks for ≥ 8), so the
  only thing approached was the calf.
- **Nobody hit a giant.** Every colonist was stripped with
  `jawa/pawn_gear action=clear clearWhat=equipment` before the run, and three of
  the four adults finished the run with **zero hediffs**.

### What was observed (the positive reading this item named)

`rimworld/get_selection_semantics` on the guarding adult, verbatim:

```
inspectString : "Female, age 4 (29)\r\nEnraged: defending young: giant calf"
mentalState   : "RM_ParentalEnrage"
job           : "AttackMelee"
```

Enrage windows, sampled every 100 ticks (`ticksGame`):

| adult | entered | left | what ended it |
|---|---|---|---|
| `…39139` (X=120) | ≤ 5516 | 6316 | intruder went down |
| `…39137` (X=80) | 5716 | 6116 | intruder went down |
| `…39141` (X=160) | 5716 | ≤ 7316 | **timed out with the intruder still standing 4 cells from the calf, unhurt** — then re-triggered at 7416, consistent with the calf's own 1250-tick cooldown |
| `…39135` (X=40) | 6716 | 7516 | intruder went down |

**All four adults enraged**, so this is not one pawn's RNG.

### The four false-pass checks, each answered

1. **"The adult charges because the colonist walked near the ADULT too."** No —
   the intruder never came closer than 11 cells to the adult, and the adult was
   the thing that closed the distance: `…39139` walked (120,75) → (120,74) →
   (120,71) → (119,67) → (119,64), straight at the intruder at (119,63) and
   directly **away from** its own control colonist at (129,75).
2. **"The adult attacks because something damaged it"
   (`manhunterOnDamageChance` 0.02).** Excluded twice over: adults `…39137`,
   `…39139` and `…39141` ended the run with **0 hediffs**, and `…39139` was
   already in the state at (120,74) — 11 cells from the nearest pawn, before any
   contact. And that route produces vanilla `Manhunter`, not this def.
3. **"It reads as working but is plain vanilla Manhunter."** The state def read
   back is `RM_ParentalEnrage` and the inspect line is
   `Enraged: defending young: giant calf`, never `Maddened: Manhunter`.
4. **"A second, untouched colonist in plain sight is NOT attacked"** — the check
   the item says would be skipped. All four controls were alive, never downed,
   and still on their exact spawn cells after ~3,000 ticks. Final hediffs:
   ctrl0 **0**, ctrl2 **0**, ctrl1 `{Gunshot}`, ctrl3 `{BadBack, Frail, Gunshot}`
   — all pawn-generation hediffs, and **not one Bite / Scratch / Bruise**, which
   is what all three downed intruders carry. `ForceHostileTo(Thing)` scoping
   holds.

Time-box confirmed independently of the intruder going down: the `…39141` window
ran ~1,500–1,600 ticks and ended on its own while its intruder was still parked
4 cells from the calf with **zero hediffs** — short of the 2500-tick
`forceRecoverAfterTicks` ceiling, which is `recoveryMtbDays 0.05` rolling after
the 600-tick floor, as the def intends. Not a permanent manhunter flip.

Screenshot:
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\SHRUBLAND_GIANT_ENRAGE_live.png`
