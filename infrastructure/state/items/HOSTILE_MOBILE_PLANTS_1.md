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

## ⚠️ Scope is UNSET — this needs a design sitting before anything is authored

He approved the concept in one sentence while ruling on something else. **Nothing below is ruled**,
and these are the questions a design pass owes him:

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
