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
