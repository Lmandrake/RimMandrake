# GREENTIDE_GRENADE_WEAPONS_1 — jungle grenades: stench, seeding and toxin

## the ruling

**Owner, 2026-09-22.** Asked which new jungle payoff to build first, he **redirected the question**:
the limb-regrowth idea moved to another biome (see `CONTAGION_GENOME_ORGAN_GROWING_1`), and for the
jungle he named a different reward category entirely:

> *"But for the jungle biome, unique grenade weapons could be fun: special smoke that makes beasts
> flee from the stench, or that plant jungle plants in the ground near a water source where they start
> their rapid growth, or powerful toxins that can fuel blow darts or taint water sources and anyone
> wading in them."*

⇒ **This is the jungle's first-built new reward**, and it is a category the design pass did not propose.

🔑 **Why it fits the exchange better than the categories that were offered:** the jungle's payoff
becomes *portable*. You carry the jungle out with you — its stench, its growth, its poison — and use
it somewhere else. That is a reward only a violently alive place could give a clan living on dead
sand, and it pays in capability rather than in goods, so it cannot inflate the economy.

### ✅ SCOPE RULED — the stench smoke goes first, owner 2026-09-22

Asked which of the three proves the category, he chose **stench smoke**. ⇒ **Build one grenade, not
three.** The seeding grenade and both toxin routes stay designed-but-unbuilt in this item — they are
**queued behind the proof, not dropped.**

🔑 It is also the least mechanically risky of the three, so the category gets proven before the two
features whose mechanisms may not be expressible at all are attempted.

✅ **And its target set is ruled too — owner, 2026-09-22: it repels the wasps as well.** Asked whether
the jungle's new insect (`GREENTIDE_WASP_SWARM_1`) counts as a beast, he chose *"one tool, all the
biome's animals."* ⇒ **The stench answers every animal threat in the biome, vertebrate or not.**

🔑 That makes this grenade the jungle's key item rather than a situational one, which raises the bar on
it: ⛔ **its cost is now load-bearing.** If smoke is cheap and stackable, it defuses both the predators
and the wasps permanently, and two danger axes quietly close. Price it like the answer to a biome, not
like a utility.

## the three he named

### 1. Stench smoke — beasts flee

A thrown smoke that repels **animals** rather than damaging anything. ⇒ Crowd control against exactly
the threat this biome is full of, and a non-lethal tool, which is unusual and interesting.
⚠️ Open: does it affect the biome's own predators, hostile human raiders' pack animals, and the
player's own livestock? *"Beasts"* is his word; how wide it reaches is unruled.

### 2. Seeding grenade — plants jungle flora that grows rapidly

Throws jungle plants into the ground **near a water source**, where they begin rapid growth.
🔑 This is a **terrain weapon**, not a damage weapon — you deny ground, build cover, or block a path
with living growth. It is also the only one of the three that turns the roster's 21 plants into
ammunition.
⚠️ Open: the water-source requirement is his, and it is a real constraint — it means this works at
home only where there is water, which usefully limits it.

### 3. Toxins — blow darts and poisoned water

Powerful plant toxins with **two delivery routes**: fuelling blow darts, and **tainting a water source
so anyone wading in it is poisoned**. ⇒ The water-tainting half is an area-denial trap rather than a
weapon, and it is the nastiest idea of the three.
⚠️ Open: whether tainted water affects the player's own colonists and animals — it should, or it is
not a real trap.

## ⛔ Do not design these in a vacuum — three existing things they must sit on

1. **The 21-plant roster** (`GREENTIDE_JUNGLE_TREE_ROSTER_1`) already contains the sources: acid pods,
   sap-bleeders, spore bladders that burst, and a strangler. ⇒ **Each grenade should trace to a named
   plant**, so the roster becomes ammunition rather than scenery. That link is the point.
2. **`GREENTIDE_RISK_REWARD_EXCHANGE_1`** is the frame this sits inside — it already records a
   concealment-biology category (scent-maskers, quieting resins) that is adjacent to the stench smoke.
   ⚠️ Check whether stench smoke and scent-masking are the same idea wearing two hats before building
   both.
3. **The biome's fire ruling applies to any smoke or vapour**: his ruling is that jungle plants take
   fire damage but are not ignition sources. ⇒ A flammable thrown weapon would contradict it; keep
   these chemical, not incendiary.

## ⚠️ UNMEASURED — engine questions, not guessable from the Mac

🔴 No game, no def dump, no decompiler here. ⛔ Name no field, class or value from reasoning.

1. **How a thrown weapon creates a lasting area effect** — smoke, gas and similar released volumes.
2. **Whether animals can be made to flee an area** by a released effect, and what drives it.
3. **Whether a thrown item can spawn plants at its landing point**, and whether "near a water source"
   is checkable at that moment.
4. **Whether water terrain can be given a temporary harmful state** that affects pawns moving through
   it — this is the least certain of the three and may be the hardest.
5. **Whether a blow dart is a distinct weapon class** or a reskin of an existing ranged weapon, and how
   a poison is attached to a projectile.

## spec

1. **Build the stench smoke only** (ruled above). ⛔ Do not open the seeding grenade or either toxin
   route until he has seen the smoke work.
2. Establish mechanism questions 1 and 2 on the Desktop — released volume effects, and whether
   animals can be made to flee one. Questions 3–5 belong to the unbuilt two and can wait.
   ⛔ Nothing authored before that.
3. Trace each grenade to its source plant in the roster, and add the harvest/craft route.
4. Settle the friendly-fire questions explicitly: stench on your own animals, toxin in your own water.
5. Mod Settings toggles per the standing rule.

## verify

Each weapon traces to a named plant of ours. Each is chemical rather than incendiary, consistent with
the biome's fire ruling. Friendly-fire behaviour is decided and recorded, not left emergent.
⛔ No live-proven claim from the Mac.

## criteria

A colonist packs jungle in their bag before leaving for somewhere that has none.

## Watch out

- ⚠️ **Three grenades is a category, not a task.** Do not attempt all of them in one pass; prove the
  category with one and let him see it.
- ⛔ **These must not become a general-purpose arsenal.** The point is that they are *jungle* tools —
  if they are simply good weapons, the biome's identity contributes nothing and the reward stops being
  tied to braving the place.
- ⚠️ **The seeding grenade could be an exploit**: rapid-growth plants on demand, near water, in a game
  where plants are food and wood. Bound it, and say how.
