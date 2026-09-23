# One reaction mechanism, four scales — spec

**Status: DESIGN. Nothing built by this document.** The thing it designs *around* is already shipped
and was read in full this pass; what is missing is named precisely below.

Consumers: `GREENTIDE_WASP_SWARM_1` · `HOSTILE_MOBILE_PLANTS_1` · `FEVERWOOD_ANT_HIVE_DUNGEON_1` ·
the shipped `RM_CompPlantAlarm`. Assembly: `mandrake.rm.creaturebehaviors`.

## Why this document exists

**Four separate items are each about to build "a thing notices you and its neighbours react."** One of
them already shipped. The owner's own instinct this session was to generalise on a mechanism's second
occurrence rather than copy it; this is the fourth, so the question is no longer whether to generalise
but what the generalisation actually is.

🔑 **The four are not four sizes of one behaviour. They differ on four independent axes**, and that is
the whole finding of this pass — a single comp with a bigger radius cannot express them:

| consumer | what TRIGGERS it | what PROPAGATES | what the RESPONSE is | where it happens |
|---|---|---|---|---|
| shipped plant alarm | the plant takes damage, or is harvested | **nothing** | nearby responder races go Manhunter | open ground |
| ambush-plant swarm | a plant is disturbed | **plant → plant, of its own kind** | the woken plant attacks | open ground, dense cover |
| wasp hive | the hive or its host plant is disturbed | **spawned wasps are the propagation** | wasps are **created**, not woken | open ground |
| ant hive rally | an intruder is detected | **responder → responder, inward** | ants converge, seal, hunt | an enclosed corridor |

⇒ **The mechanism is not one comp. It is four pluggable parts:** a trigger, a propagation rule, a
response, and a **budget**. The shipped comp welds trigger and response together and has neither of the
other two.

## What is already built — MEASURED 2026-09-23 by reading the source

`src/RimMandrake/CreatureBehaviors/Source/RM_CompPlantAlarm.cs` and its two companions.

- **Trigger:** `PostPostApplyDamage` (any damage to the carrying Thing), plus a public
  `TriggerAlarm()` that a harvest hook calls — `RUT_Plant_FalseFruit`'s `PlantCollected` override is
  the live caller, because harvesting is not damage and has no `TakeDamage` to hook.
- **Selection:** snapshots `map.mapPawns.AllPawnsSpawned`, keeps pawns within `radius` (default **18**),
  whose **race** carries `RM_AlarmResponderExtension` with a matching `tag`. A blank comp tag matches
  any race carrying the extension; a race without the extension never answers any alarm.
- **Response:** `TryStartMentalState(MentalStateDefOf.Manhunter, forceWake: true)`, then one
  `Messages.Message` if anything woke.
- **Bounds it has:** a per-source cooldown (`cooldownTicks`, default **2500**) and the radius. Saves
  `lastTriggerTick`. Gated by `RM_CreatureBehaviorsSettings.guardianAlarmEnabled`.
- **Pattern it establishes, and the one to keep:** comp + `DefModExtension` tag on the race, **zero
  hardcoded species**, content attached by XML patch from a content pack rather than by this assembly.

**Adjacent and deliberately NOT this:** `RM_MapComponent_SenseWeb` + `RM_CompSenseWebNode` register
*cells* and mark intruders who stand in them. That is **detection**, not reaction — it answers "is
something in the web", never "everyone wake up". ⛔ Do not extend SenseWeb into an alarm network; it is
the precedent for the *style* (map component, soft `GetNamedSilentFail` def lookup so it no-ops on a
mod set without the content) and not for the mechanism.

## The four gaps, stated as gaps

1. 🔴 **No propagation at all.** A woken responder is not itself a source. Both hives and the plant
   swarm are *defined* by propagation, so this is the substantive missing piece — and the dangerous one.
2. **The response is hardcoded to Manhunter.** A hive rally is coordinated convergence, not berserk;
   a wasp hive **creates** pawns rather than waking them. Neither is expressible today.
3. 🔴 **No budget.** Radius and cooldown bound *one source*. Nothing bounds how many sources fire, how
   far a chain reaches, or how many pawns one disturbance can ultimately produce. In the open that is a
   bad fight; in a hive corridor where retreat is a single tile wide, it is a colony wipe with no
   decision in it.
4. **No cancel path.** The stench grenade must be able to end a reaction in progress — the owner ruled
   it repels every animal in the biome, wasps included — and nothing in the shipped comp can be told to
   stop or to be ignored.

## The shape to build

Keep `RM_CompPlantAlarm`'s comp-plus-extension pattern and its content-blindness. Split what it does:

**1. The event is a first-class object, not a function call.** A disturbance creates one reaction event
carrying: its origin, its tag, a **remaining-responder budget**, and a **remaining hop count**. Every
propagation step spends from the *same* event's budget.

🔑 **This is the design's load-bearing decision.** The alternative — each source bounding only itself —
is what makes chains unbounded: ten plants each politely waking "only" eight neighbours is eighty
pawns, and none of them broke a rule. A shared budget makes the total the thing you tune, which is the
number that actually decides whether the fight is survivable.

**2. Propagation is a rule on the event, not a property of the source.** Three cases are enough for all
four consumers: **none** (shipped behaviour, unchanged), **to others of the same kind within a radius**
(the plant swarm), and **to responders already woken by this event** (the hive rally, which is what
makes a hive feel like it is coordinating rather than reacting in a wave).

**3. The response is pluggable.** The three the consumers need: wake existing responders to Manhunter
(shipped, keep as the default), **spawn** a bounded group (the wasps), and rally existing responders
toward the origin without berserking them (the ant hive). ⚠️ The spawn response is the one that can
hurt performance and it is the one the wasps need, so it is the one to build first and measure.

**4. Suppression is part of the mechanism, not a grenade feature.** A cell or area can be marked
reaction-suppressed; responders in it do not answer, and an in-flight event does not propagate through
it. ⇒ The stench grenade becomes *one caller* of a general suppression, which is the right place for it
— and it gives every future counter-tool a hook instead of a special case.

## The bound, stated as the consumers must state it

Each consumer owes a number, and the item that builds it must write the number down:

- **plant swarm** — how many plants one disturbance can ultimately wake, total, not per-source.
- **wasp hive** — how many wasps exist per hive and per map at once. ⚠️ This is a **performance** bound
  before it is a balance bound.
- **ant hive** — how many ants converge, and 🔴 **the hive must telegraph** (sound, sealed doors, visible
  rallying). A reacting enemy the player cannot read is unfair rather than tense; that was the owner's
  own stated cost when he chose the reacting hive.

⛔ **No consumer ships with "the default is fine."** The default is 18 cells and 2500 ticks, chosen for
a single guardian plant in the Rot, and it is not a hive.

## ⚠️ UNMEASURED — this is the Mac, so no game, no def dump, no decompiler

⛔ Name no field, class or value for any of these from reasoning. The measured section above came from
our own source; everything below needs the engine.

1. **Whether many tiny pawns are affordable**, and at what count. The wasps' central risk, and it can
   kill the feature rather than shrink it.
2. **What a "rally without berserk" actually is** — a mental state, a duty, a job giver, or a lord.
   `MentalStateDefOf.Manhunter` is the only response this project has ever used here.
3. **How a pawn group is spawned and kept coherent**, and what happens to it on save/load and on the
   hive's destruction.
4. **How suppression could be expressed** so that both a pawn's answer and an event's propagation can
   consult it cheaply.
5. **Whether `AllPawnsSpawned` is still the right scan** once several events can be in flight at once.
   ⚠️ The shipped comp snapshots the whole map's pawn list *per trigger* — acceptable for one plant on a
   2500-tick cooldown, and not obviously acceptable for a hive.

## Build order

1. **The wasps prove the mechanism** (`GREENTIDE_WASP_SWARM_1`). They need the spawn response and a
   hard count bound, they are the smallest consumer, and their failure mode is measurable rather than
   subjective. ⇒ Build the event object, the budget and the spawn response here.
2. **The plant swarm adds propagation** (`HOSTILE_MOBILE_PLANTS_1`) — same-kind-within-radius, spending
   a shared budget.
3. **The ant hive is last** (`FEVERWOOD_ANT_HIVE_DUNGEON_1`), because it is the only consumer inside an
   enclosed space and every bound behaves differently where retreat is a corridor. ⛔ Do not start its
   reaction work ahead of the wasps.
4. **The shipped plant alarm migrates onto the general path with no behaviour change** — propagation
   none, response wake-to-Manhunter, budget its existing radius. ⚠️ If migrating it changes what the Rot
   guardian groves do, the migration is wrong, not the groves.

## Mod Settings

Per the standing every-mod-ships-settings rule. `RM_CreatureBehaviorsSettings.guardianAlarmEnabled`
already exists and gates the shipped alarm; the new parts need their own toggles, and the **budgets are
exactly the "a number is the experience" case** — a player who finds hives unfair should be able to turn
the total down without turning the mechanism off.
