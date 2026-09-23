# GREENTIDE_WASP_SWARM_1 — the jungle's insect danger: tiny wasps, hives on plants, stings that stack

## the ruling

**Owner, 2026-09-22.** Asked what fills the Greentide's empty insect axis — offered a new
creature, dropping the axis, or a brood riding the existing plants — he **wrote in a fourth
answer that takes the best half of two of them**:

> *"Let's do some very small, numerous wasps that boil out of hives attached to plants. They are
> easy to kill and sting you for a very small irritating HEDIFF, but multiple stings add up
> quickly and overwhelm."*

⇒ **A new creature of ours (so the fauna law is satisfied), whose hives live on the plants we are
already building (so it costs no separate nest and ties the insect axis to the flora axis).**

🔑 **The threat model is arithmetic, not lethality.** Every single wasp is trivial — easy to
kill, one negligible hediff. The danger is that nothing about any individual sting tells you to
stop, and the count does. ⇒ **The content is the moment a player realises they are already past
the point where retreating is cheap.** That is the same shape as the ant hive's *"you decide how
deep to go, and then you decide too late"*, expressed in the open instead of in a corridor.

## 🔑 This is the FOURTH occurrence of one mechanism — build it once

A hive attached to a plant that **boils out** when disturbed is an alarm that propagates from a
plant-borne Thing. That is already three other things:

- **`RM_CompPlantAlarm`** (`src/RimMandrake/CreatureBehaviors/Source/`) — shipped. Radius alarm
  that fires when the carrying Thing takes damage or on a public trigger, content-blind, zero
  hardcoded species.
- **`HOSTILE_MOBILE_PLANTS_1`** — his ruling that a woken ambusher activates if others of its
  kind activate nearby.
- **`FEVERWOOD_ANT_HIVE_DUNGEON_1`** — the hive that notices, rallies and hunts.

⇒ ⛔ **Do not write a fourth alarm.** This is the cleanest and smallest of the four, which makes
it the best place to *prove* the shared mechanism before the hive dungeon needs it. The
propagation bound that item already names applies here with a twist: **wasp propagation is the
wasps themselves**, so the bound is a spawn count and a hive count per map, not a chain depth.

## ⚠️ UNMEASURED — engine questions, and the Mac has no game, no def dump, no decompiler

⛔ Name no field, class or value for any of these from reasoning.

1. **Whether many tiny pawns are affordable at all.** "Very small, numerous" is a performance
   question before it is a design one, and it is the one that can kill the feature. Read what the
   base game's own swarming insects do about count.
2. **How a hediff stacks from repeated identical applications** — whether severity accumulates on
   one instance or many instances coexist, and what caps it.
3. **Whether a hive can be a Thing attached to a plant** rather than a building on the ground,
   and what happens to the hive when the plant is cut or burns.
4. **What "boil out" is mechanically** — spawning pawns on trigger, versus a dormant group that
   wakes. These have different save/load and performance consequences.
5. **Whether a swarm can be made to lose interest** and return, which is what makes retreat a
   real option rather than a death sentence.

## spec

1. **Design this as the shared reaction mechanism's first proof**, in `mandrake.rm.creaturebehaviors`,
   extending `RM_CompPlantAlarm`'s comp-plus-extension pattern. State the spawn/hive bound.
2. Establish the five mechanism questions on the Desktop. ⛔ Author nothing before that, and
   answer question 1 first — if count is unaffordable, the whole shape changes.
3. **Name which plants of the 21-row roster carry hives** (`GREENTIDE_JUNGLE_TREE_ROSTER_1`), and
   what a player sees before they disturb one. A hive that cannot be spotted is not a decision.
4. Design the sting so it is **negligible once and frightening twenty times** — that curve is the
   feature. ⚠️ Not a detail: if one sting is ignorable and twenty are survivable, there is nothing
   here.
5. Mod Settings toggle and tuning per the standing every-mod-ships-settings rule — swarm size and
   sting severity are exactly the "a number is the experience" case.

## verify

Wasps are ours, live only in the Greentide, and their hives sit on named plants of our own
roster. Their reaction uses the shared alarm mechanism rather than a fourth implementation, with
a stated bound. One sting is trivial; an ignored swarm is lethal.
⛔ No live-proven claim from the Mac.

## criteria

You kill the first six without thinking, and then you look at the screen.

## Watch out

- 🔴 **Performance is the real risk here, not balance.** Numerous tiny pawns is the one thing in
  this design that could be simply impossible at the count that makes it work. Measure before
  designing around a number.
- ⚠️ **A swarm you cannot escape is not tension, it is a death notice.** The wasps must lose
  interest, be outrunnable, or be stoppable by something the player can carry — otherwise the
  correct play is never to enter the jungle, which deletes the biome.
- ⚠️ **`GREENTIDE_GRENADE_WEAPONS_1`'s stench smoke repels *beasts*.** Whether it repels wasps is
  unruled and it is a genuine question — the answer decides whether the jungle's first grenade is
  also the jungle's insect counter, which would be elegant or would defuse this feature
  entirely. ⇒ Flag it to him; do not decide it.
- ⛔ **Do not let the hives become a farmable resource** (honey, chitin, venom for the toxin
  grenade) without a bound. A hazard you harvest on purpose is fine — that is the Frenzy's whole
  design — but it must cost something each time.
