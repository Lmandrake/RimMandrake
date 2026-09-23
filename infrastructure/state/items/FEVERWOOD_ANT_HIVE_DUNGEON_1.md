# FEVERWOOD_ANT_HIVE_DUNGEON_1 — ant hives are reactive procedural dungeons

## the ruling

**Owner, 2026-09-22.** Asked what the jungle's insect danger should be, he named the Ants and ruled
their hives are dungeons in their own right:

> *"The Ants are supposed to be around here I believe, yes? Their hives should be dungeons in their own
> right (procedural are fine, not plot based) with all sorts of gross insect symbiotic relationships in
> there."*

Told the Ants belong to the **Fever Wood** rather than the Greentide, and that he had already ruled on
them there, he placed the hives **in the Fever Wood, where they already live.**

Asked what makes a hive a dungeon rather than a nest to clear, he chose **a hive that reacts**: it
notices you, raises alarm, rallies, seals passages, and hunts you through its own corridors.

## ✅ Where the Ants actually are — MEASURED 2026-09-22, and he had ruled on them before

`design/Jawa/worldbuilding/biomes/the_fever_wood.md` already carries real Ant design, including a
prior owner ruling:

- 🔴 **"The Ants are never an existing faction"** (his ruling, recorded there) — no Geonosian tie. A
  **wild swarm entity**. Source is a specific third-party ant mod, called there as a BENCH decision.
- **Their raids haul thornbugs away ALIVE — theft, not slaughter.**
- **The Ants and the feralisks despise each other and will fight to the death.**
- Ant middens mark one margin of that war.
- Elsewhere in the same doc, *"even the Ants do not dig here"* is used as a measure of how bad another
  place is.

⇒ ⛔ **The Greentide's design doc contains no reference to ants at all** (MEASURED: zero word-bounded
matches). The hive inherits a war it is already part of, which is far richer than a hive in isolation —
that is the substance of his placement ruling.

## ✅ RESOLVED — the jungle's insect axis got its own creature, owner 2026-09-22

Putting the Ants in the Fever Wood left the Greentide's fourth danger axis (plants, beasts, diseases,
**insects**) unfilled. Offered a new jungle insect, dropping the axis, or a brood riding the existing
plants, he wrote in a fourth answer: **tiny numerous wasps whose hives attach to plants — trivial
individually, overwhelming in aggregate.** Filed on his verbatim words as `GREENTIDE_WASP_SWARM_1`.

⇒ **The Ants stay in the Fever Wood, unextended**, which is what this item required. ⛔ Still do not
move them into the Greentide; the jungle now has its own insect and there is no remaining reason to.

🔑 **Build-order consequence for THIS item:** the wasps' hive-boils-out reaction is the same mechanism
as the ant hive's rally, and it is far smaller. ⇒ **The wasps prove the shared mechanism; this hive is
its most complex instance, not its first.** Do not start the ant hive's reaction work ahead of them.

## 🔑 The reaction behaviour is ALREADY BEING BUILT — do not invent a second one

The hive's alarm-and-rally is the same behaviour family as two things already in motion, and the
owner's own instinct this session was to generalise a mechanism on its second occurrence rather than
copy it:

- **`RM_CompPlantAlarm`** (`src/RimMandrake/CreatureBehaviors/Source/`) — already shipped. A radius-based
  alarm that fires when the carrying Thing takes damage, or on demand via a public trigger. Its own
  header says it is *"generic and content-blind like every other mechanism in this assembly"*, built
  with a comp-plus-extension pattern and **zero hardcoded species**.
- **`HOSTILE_MOBILE_PLANTS_1`'s swarm activation** — his ruling that a woken ambusher *"activates if
  others of its own kind activate nearby"*. That is propagation, which is what a hive rallying is.

⇒ **The hive's reaction, the plant swarm and the existing plant alarm are one mechanism at three
scales.** Design them together. ⚠️ And the same bound applies that `HOSTILE_MOBILE_PLANTS_1` records:
an unbounded activation chain is a colony-killer — inside an enclosed hive it is worse, because the
player cannot retreat through open ground.

## ⚠️ What does NOT exist yet: procedural, non-plot dungeons

MEASURED 2026-09-22: this project has a dungeon spec (`design/Jawa/worldbuilding/dungeons_arc_spec.md`)
and two dungeon build items — `ASSAILANT_DUNGEON_BUILD_1` and `VAULT_DUNGEON_BUILD_1`. **Both are
FIXED, plot-bearing sites** (a crashed killer at a named tile; a frozen vault at an adjacent one), with
hand-placed content palettes and quest-signal gates.

⇒ His *"procedural are fine, not plot based"* is a **new kind** of dungeon here. ⛔ Do not assume the
existing spec's machinery generates layouts — read it and say what it actually provides before
planning to reuse it.

## the "gross symbiotic relationships"

✅ **RULED — owner, 2026-09-22: one of each, three chamber types.** Offered a single farmed-livestock
relationship, a parasite, a kept guard, or all three, he took **all three**, each its own chamber the
player passes through:

1. **A farm** — creatures kept alive, herded, milked, fattened. 🔑 Already implied by his own earlier
   ruling that ant raids haul thornbugs away **alive**: the hive is already a farm and nobody had drawn
   it. ⇒ Start here, and make the farmed species the thornbug unless that biome's doc says otherwise.
2. **A parasite the ants tolerate or cannot see** — something feeding on the hive itself. ⇒ This is the
   horror chamber, and it is also the one that can be an *ally*: whatever eats ants is not your enemy.
3. **A kept guard at the chokepoints** — a larger creature fed and housed by the hive, stationed where
   corridors narrow. ⇒ This converts layout into difficulty: depth becomes gated rather than merely long.

🔴 **This overrules the previous scope caution in this item, which warned that many relationships read
as set dressing. He chose the largest build on this list deliberately** — descent is a tour of
escalating relationships, and that IS the dungeon's content. ⛔ Do not trim it back to one later on
scope grounds; bring him the cut if the build genuinely cannot carry three.

⚠️ **Sequencing, because three creatures plus three behaviours is not one pass:** the guard is the
riskiest — it is a boss fight, a different design problem from a hive that reacts, and it can overshadow
the reaction mechanism he chose as the primary depth. ⇒ Build the farm first (cheapest, already implied),
the parasite second (the horror payload), the guard last, and judge whether the guard is still needed
once a reacting hive has been played.

## spec

1. **Read the Fever Wood doc's Ant material in full** and the third-party ant mod it names, before
   designing anything. ⛔ Its prior ruling (never an existing faction) binds.
2. **Read the dungeon spec** and report what it actually provides for layout generation.
3. **Design the reaction as one mechanism with the plant swarm**, in the shared behaviours assembly,
   extending `RM_CompPlantAlarm`'s pattern rather than duplicating it. State the propagation bound.
4. Build the three chambers in the order given above — farm, parasite, guard — each as a creature plus
   a behaviour, not as scenery. The relationships are ruled; ⛔ nothing left to card here.
5. Mod Settings toggles per the standing rule.

## verify

The hive is in the Fever Wood, built on that biome's existing Ant design and its no-faction ruling.
Its reaction shares a mechanism with the ambush-plant swarm rather than duplicating it, with a stated
propagation bound. Layout is procedural and carries no plot. ⛔ No live-proven claim from the Mac.

## criteria

You decide how deep to go, and then you decide too late.

## Watch out

- ⛔ **Do not move the Ants into the Greentide.** Offered and declined, and the axis is now filled by
  the wasps — there is no longer even a gap to argue from.
- ⚠️ **A reacting enemy the player cannot read feels unfair rather than tense.** His own stated cost on
  this choice. The hive must telegraph — sound, sealed doors, visible rallying — and that is judged by
  playing, not by reading a spec.
- ⚠️ **An enclosed space changes every hazard's maths.** Mechanics balanced on open ground (swarm
  propagation, area denial, fleeing) behave differently where retreat is a corridor.
