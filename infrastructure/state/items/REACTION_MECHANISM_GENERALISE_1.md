# REACTION_MECHANISM_GENERALISE_1 — one reaction mechanism, four consumers

## why this exists

**Four items are each about to build "a thing notices you and its neighbours react," and one of them
already shipped.** The owner's own instinct this session was to generalise a mechanism on its *second*
occurrence rather than copy it. This is the fourth.

Spec: `design/RimMandrake/reaction_mechanism_spec.md`. Assembly: `mandrake.rm.creaturebehaviors`.

Consumers: `GREENTIDE_WASP_SWARM_1` · `HOSTILE_MOBILE_PLANTS_1` · `FEVERWOOD_ANT_HIVE_DUNGEON_1` · the
shipped `RM_CompPlantAlarm`.

## 🔑 The finding that makes this worth doing

**The four are not four sizes of one behaviour.** They differ on four independent axes — what triggers
them, what propagates, what the response is, and whether it happens in the open or in a corridor. ⇒ A
single comp with a bigger radius **cannot** express them, and the shipped comp welds trigger to response
while having no propagation and no budget at all. The spec's table is the argument.

⇒ The mechanism is **four pluggable parts**: trigger, propagation rule, response, and budget.

## 🔴 The one decision everything else hangs on

**The reaction event must be a first-class object carrying a SHARED budget**, not a function call that
each source bounds for itself.

Ten plants each politely waking "only" eight neighbours is eighty pawns, and **no rule was broken.**
That is how an unbounded chain happens in practice — not from a missing limit, but from per-source
limits that compose. A shared budget makes the *total* the tunable number, which is the number that
decides whether a fight is survivable. ⛔ Do not build per-source caps and call it bounded.

## ✅ What is already built — MEASURED 2026-09-23 from our own source

`RM_CompPlantAlarm.cs` + `RM_CompProperties_PlantAlarm.cs` + `RM_AlarmResponderExtension.cs`, read in
full. Trigger is damage-or-harvest; selection is a whole-map pawn snapshot filtered by radius (18) and
a race-level tag extension; response is `Manhunter` with `forceWake`; bounds are that radius and a 2500-tick
per-source cooldown. **Zero hardcoded species** — keep that.

⛔ **`RM_MapComponent_SenseWeb` is NOT this and must not be extended into it.** It registers cells and
marks intruders — detection, not reaction. It is the precedent for the *style* (map component, soft
`GetNamedSilentFail` lookup so it no-ops cleanly on a mod set without the content), not the mechanism.

## spec

1. **Build the event object, the shared budget and the spawn response under the wasps**
   (`GREENTIDE_WASP_SWARM_1`) — smallest consumer, and its failure mode is measurable rather than
   subjective.
2. **Add propagation under the plant swarm** (`HOSTILE_MOBILE_PLANTS_1`): same-kind-within-radius,
   spending the shared budget.
3. **The ant hive is last** (`FEVERWOOD_ANT_HIVE_DUNGEON_1`) — the only consumer inside an enclosed
   space, where every bound behaves differently because retreat is a corridor.
4. **Migrate the shipped plant alarm onto the general path with NO behaviour change** (propagation none,
   response wake-to-Manhunter). ⚠️ If the Rot's guardian groves behave differently afterwards, the
   migration is wrong — not the groves.
5. **Suppression is part of the mechanism, not a grenade feature.** The owner ruled the stench smoke
   repels every animal in the biome including the wasps, so the grenade becomes one *caller* of a general
   reaction-suppression rather than a special case.
6. Mod Settings per the standing rule. `guardianAlarmEnabled` already exists; the budgets are exactly
   the "a number is the experience" case.

## ⚠️ UNMEASURED — the Mac has no game, no def dump, no decompiler

⛔ Name no field, class or value from reasoning; the measured section above came from our own source.
The five engine questions are enumerated in the spec — chiefly **whether many tiny pawns are affordable
at all** (the wasps' central risk, and the one that can kill a feature rather than shrink it), and what
a "rally without berserk" even is, since `Manhunter` is the only response this project has ever used.

## verify

One mechanism, four consumers, no second alarm implementation. Every consumer states its budget as a
**total**, not per-source. The shipped Rot guardian groves behave identically after migration.
⛔ No live-proven claim from the Mac.

## criteria

A hive that coordinates, a swarm that spreads, and a grove that wakes are one file's behaviour with
three sets of numbers.

## Watch out

- 🔴 **The scan is a whole-map pawn snapshot per trigger.** Fine for one plant on a 2500-tick cooldown;
  not obviously fine once several events are in flight inside a hive. ⇒ Measure it before assuming the
  existing selection code scales.
- ⚠️ **The ant hive must telegraph** — sound, sealed doors, visible rallying. That was the owner's own
  stated cost when he chose a reacting hive over a static one: a reacting enemy the player cannot read is
  unfair rather than tense. It is a requirement on this mechanism, not on that item's art.
- ⛔ **No consumer ships with "the default is fine."** 18 cells and 2500 ticks were chosen for a single
  guardian plant in the Rot. A hive is not a guardian plant.
- ⚠️ **Migrating the Rot alarm is the riskiest step even though it changes nothing by design** — it is
  live content, and a regression there is a regression in a shipped mod. Do it last and diff the
  behaviour, not the code.
