# HOSTILE_MOBILE_PLANTS_1 — plants that hunt, built as animals

## the ruling

**Owner, 2026-09-22**, verbatim. Asked how dangerous the "parasitic moving plants" on his jungle-fish
list should be, he separated two different things:

> *"I had just meant it as a very strange kind of fish to catch. But yes we should ALSO make some
> "animals" that are hostile mobile plants too, that's cool."*

⇒ **Two distinct pieces of content.** The catch belongs to `GREENTIDE_EXOTIC_JUNGLE_FISH_1`. **This
item is the other half he approved: creatures that are plants, that move, and that are hostile.**

🔑 His quotation marks around *"animals"* are the whole design note: these are **animal defs**
(`ThingDef` with `race`, a `PawnKindDef`, real AI), not `Plant` defs. A RimWorld `Plant` cannot move
or attack; the only route to a mobile aggressive organism is the animal pipeline. That is why he put
the word in quotes rather than calling them plants.

## ✅ RULED 2026-09-22 — the creature's core is now specified

Three of the five open questions were answered the same evening, by card.

### 1. It reads as a plant by WAITING — plus one deliberate tell

He chose *"It waits, rooted and still"* and added, verbatim:

> *"but we should add a small animation that one of its leaves occasionally twitches if you watch
> carefully."*

🔑 **The twitch is the whole craft of this creature.** It solves the exact cost the option carried —
a motionless creature reading as a broken animal — by making the stillness demonstrably *alive* to
anyone paying attention, without giving the ambush away. Rooted, indistinguishable from scenery,
with a rare single-leaf movement.

⚠️ **Animation route is UNDECIDED and must not be guessed.** This is a small, occasional,
partial-body idle movement on an otherwise static sprite. 🔴 Do NOT assume the whole-body
directional flip-book that `PawnKindDef`'s `flyingAnimation*` fields drive — that mechanism exists
for flight and needs a full pose per frame per facing. A per-node idle wiggle
(`PawnRenderNodeProperties_Spastic`) is closer to the shape of this ask — **but note that approach
was REVERSED for flight on 2026-09-19** because it cannot express per-facing, per-frame motion and
misaligned a single texture across facings. ⇒ For *this* creature the requirement is the opposite of
flight's: one small part, one facing at a time, no locomotion. Establish which mechanism actually
delivers that **on the Desktop, against the engine**, before authoring art. Getting this wrong is
how the fire hawk cost a live test.

### 2. Hostile to anything that comes close — and they wake each other

He chose *"Anything that comes close"*, colonists included, and added, verbatim:

> *"plus activates if others of its own kind activate nearby: swarm"*

⇒ **Activation propagates between neighbours of the same species.** Triggering one wakes the others
in range, which converts a single ambush into a developing situation and makes a dense patch
genuinely dangerous. This is the mechanic that makes them worth building.

🔑 **Design consequences to settle, not assume:** the propagation radius, whether it chains
outward without limit or decays, and whether a woken plant re-roots after the threat leaves. ⚠️ An
unbounded chain across a biome *"choked with foliage"* (his density ruling below) is a
colony-killer — bound it deliberately and say what the bound is.
🔑 `src/RimMandrake/Greentide/Source/RM_MapComponent_SilenceCue.cs` and the shared
`mandrake.rm.creaturebehaviors` assembly already hold cross-creature map-wide reaction machinery —
read them before inventing a propagation system.

### 3. It belongs to a biome that is CHOKED — his density ruling

Answering what the new flora should *do*, he ruled the biome's feel as well, verbatim:

> *"most are useful, many are dangerous. There should be virtually no squares uncovered by lush
> foliage. Choked with foliage. Immediately intimidating to hack through, movement extremely
> difficult."*

⇒ Near-total plant coverage and severe movement cost. **That is what makes a rooted ambusher
frightening** — you cannot see the ground, so you cannot see what is standing on it. ⇒ It also
makes the swarm bound above load-bearing rather than academic. Recorded in full on
`GREENTIDE_BIOME_DENSITY_1`.

## ⚠️ Still UNSET — what a design sitting still owes him

1. **Which biomes?** The concept arose in the Greentide (jungle), but hostile flora is not obviously
   jungle-only — the Rot, the Miasma, the Webwork and the Poison Forest are all plausible homes.
   ⛔ Do **not** assume planet-wide: the standing fauna law is that a creature has ONE home unless
   there is an in-game mechanism reason, and 🔴 **rosters are settled per biome at that biome's own
   review sitting, never by a sweep** (`BIOME_SPECIFIC_FAUNA_LAW_1`; evictions were stopped by owner
   ruling 2026-09-22). So this lands as rows on a biome's sheet, biome by biome.
2. **How many, and how different?** One signature ambusher, or a small family with distinct
   behaviours (a grappler, a spore-thrower, a lurker)?
3. **What makes them read as plants rather than animals?** Rooted idle pose, no visible legs, a
   lure, growing when undisturbed. This is where the concept either lands or looks like a green
   monster.
4. **How dangerous, and to whom?** Colonists, livestock, or both. A card on exactly this question
   for the *catch* version was answered by redirecting to this item, so his appetite for danger here
   is genuinely unknown — ask, do not infer.
5. **Are they huntable/harvestable?** A plant-animal could plausibly yield wood, herbal medicine, or
   something stranger instead of meat and leather.

## what already exists — check these before inventing a mechanism

⚠️ **UNMEASURED — this item was filed from a ruling, not from a survey.** A design pass should
establish, from our own `src/` (the only readable source on the Mac):

- Whether any existing creature of ours already lures, roots, or ambushes — `RSW_ShiroTrap` and
  `Plant_TookeTrap_Wild` (a donor row on the Greentide) both *sound* like trap-flora and may already
  be this concept. 🔴 `Shiro`/`RSW_ShiroTrap` is explicitly flagged in
  `DUPLICATE_CANON_DEFNAME_PAIRS_1` as **not** an established pair — a trap-form may be a
  deliberately different creature. Read both before proposing anything.
- `src/RimStarWars/SWBestiary/Defs/SeaBeasts/ThingDefs_Races/SeaBeasts_Swarm.xml` — the existing
  pattern for a creature standing in for something that is not one discrete animal.
- Whether any shared behaviour assembly already has a lurk/ambush job giver;
  `mandrake.rm.creaturebehaviors` is the mod that holds generic cross-race behaviour
  (`RM_JobGiver_SeekShade`, `RM_MapComponent_SilenceCue` live there), so a new behaviour belongs
  there rather than in a biome mod.

## tiering

**By name provenance, per the owner's 2026-09-22 refinement of §7 Q11** — an **invented** exotic name
is not Star Wars IP and may live in the franchise-free `RM_` tier; only a **genuine canon** name must
sit in `RSW_` and reach a biome by patch. Full ruling in `GREENTIDE_JUNGLE_TREE_ROSTER_1`. ⇒ A
newly-invented hostile plant-animal can be `RM_`-tier and ship in the standalone mod.

## spec

1. Design sitting first: answer the five questions above as a card set for him. ⛔ Author nothing
   before that — he approved a concept, not a roster.
2. Then defs in the correct tier, with the behaviour in the shared behaviours mod rather than a biome
   mod, and a Mod Settings toggle per the standing every-mod-ships-settings rule.
3. Roster placement goes through the owning biome's own review sitting, not a patch sweep.

## verify

Each creature is an animal def with real AI, not a `Plant`. Behaviour lives in the shared behaviours
assembly and is generic (any race carrying the extension gets it), not hardcoded to one species.
No `RM_`-tier def names genuine Star Wars IP. `validate_patch.py` clean on every touched file.
⛔ No live-proven claim from the Mac — no game and no def dump here.

## criteria

Something you walked past twice turns out to have been waiting for you.

## Watch out

- ⛔ **Do not file these as flora.** A plant def cannot move or fight; filing one as a `Plant` would
  quietly produce a decorative bush and look like the feature failed.
- ⛔ **Do not scope this planet-wide to save a sitting.** That is exactly the sweep-versus-review
  failure the owner stopped on 2026-09-22, at the cost of a whole session.
- ⚠️ A creature that stands still by design will read as a broken animal to a player unless the idle
  state is visibly deliberate — this is an art-and-animation problem as much as a def problem, and
  flight animation on this project has already been re-architected once for exactly that reason.
