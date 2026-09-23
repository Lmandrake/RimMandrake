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

## ⚠️ CONSEQUENCE, left OPEN rather than assumed: the jungle's insect axis is now empty

He named four danger axes for the Greentide — plants, beasts, diseases, **insects** — and the
risk/reward audit established there is **no authored insect threat of ours in that biome at all**.
Putting the Ants in the Fever Wood leaves that axis unfilled.

⇒ 🔑 **This is an open question for him, not a gap to fill unilaterally.** Either the jungle gets its
own insect (a different creature, built around the hidden floor and choking foliage) or the axis is
dropped there. ⛔ **Do not solve it by extending the Ants into the Greentide** — that is the
multi-biome placement his standing fauna law restricts to creatures with a real in-game mechanism
reason, and roster placement belongs to a biome's own review sitting. It was offered to him as an
option and he declined it.

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

He asked for them, and chose the reacting hive over them as the *primary* depth mechanism — ⚠️ but he
did not rule them out, and they were in his original wording. ⇒ Treat them as **content inside the
reactive hive**, not as an alternative to it: other species farmed, milked, parasitised or kept in the
chambers you pass through. Each is a creature plus a behaviour, so scope deliberately and propose a
small number that read clearly rather than many that read as set dressing.

## spec

1. **Read the Fever Wood doc's Ant material in full** and the third-party ant mod it names, before
   designing anything. ⛔ Its prior ruling (never an existing faction) binds.
2. **Read the dungeon spec** and report what it actually provides for layout generation.
3. **Design the reaction as one mechanism with the plant swarm**, in the shared behaviours assembly,
   extending `RM_CompPlantAlarm`'s pattern rather than duplicating it. State the propagation bound.
4. Card him on the symbiotic relationships — how many, and which.
5. Mod Settings toggles per the standing rule.

## verify

The hive is in the Fever Wood, built on that biome's existing Ant design and its no-faction ruling.
Its reaction shares a mechanism with the ambush-plant swarm rather than duplicating it, with a stated
propagation bound. Layout is procedural and carries no plot. ⛔ No live-proven claim from the Mac.

## criteria

You decide how deep to go, and then you decide too late.

## Watch out

- ⛔ **Do not move the Ants into the Greentide.** Offered and declined; the jungle's insect axis is a
  separate open question for him.
- ⚠️ **A reacting enemy the player cannot read feels unfair rather than tense.** His own stated cost on
  this choice. The hive must telegraph — sound, sealed doors, visible rallying — and that is judged by
  playing, not by reading a spec.
- ⚠️ **An enclosed space changes every hazard's maths.** Mechanics balanced on open ground (swarm
  propagation, area denial, fleeing) behave differently where retreat is a corridor.
