# GREENTIDE_EXOTIC_JUNGLE_FISH_1 — the jungle's catch is exotic creatures, not base-game fish

## the ruling

**Owner, 2026-09-22**, verbatim. A card offered him a *vanilla-only* `fishTypes`/`maxFishPopulation`
pair for the generic Greentide (one of the three optional additions
`biome_mod_architecture.md` §4a names). He took the slot and **rejected the vanilla-only framing**:

> *"Create exotic new jungle fish to catch, not base game fish. Weird aquatic worms, eels,
> parasitic moving plants, toothy tadpoles, spiked eels... get wild"*

⇒ The §4a cherry-pick *"a vanilla-only `fishTypes`/`maxFishPopulation` pair"* is **superseded for
this biome**. ⛔ Do not author it; it is not a fallback to land first.

🔑 **"Get wild" is the brief.** Aquatic worms, eels, parasitic *moving plants*, toothy tadpoles,
spiked eels — his list is the register, not an exhaustive spec. A parasitic moving plant is a
creature, not a plant def; that is deliberate and is the kind of thing he is asking for.

## ⛔ This EXTENDS a ratified programme — do not re-derive a catch design

🔑 **Read `FISH_BESTIARY_BUILD_1` and
`design/Jawa/worldbuilding/fish_bestiary_commission_2026-09-10.md` first.** That programme is
ratified and part-built — 32 `RUT_` species across 8 registers on 7 waters, 4 prize items, 6
rare-catch tables, six waves done, every §6 question ruled 2026-09-18. New Greentide species are
**new entries in its register system**, not a parallel fish economy. `SEA_FLOOR_AND_CATCH_PASS_1`
carries the same warning for the same reason.

## what exists — MEASURED 2026-09-22 (parsed off our own files, on the Mac)

- **The campaign twin already has a full catch table.** `RUT_Greentide` carries `fishTypes` and
  `maxFishPopulation 720` **directly on the def** (FISH_BESTIARY_BUILD_1 waves 3 and 4), with
  `freshwater_Common` / `freshwater_Uncommon` bands and a `rareCatchesSetMaker`. Three of its
  entries are ours: `RSW_MeeCatch` 0.4, `RSW_FaaCatch` 0.3, `RSW_LaaCatch` 0.3.
- **The generic twin has none.** `RM_Greentide` has **no `fishTypes` and no `maxFishPopulation`** —
  MEASURED, both tags absent.
- ⚠️ `RUT_RareGreentideCatches` exists as a ThingSetMakerDef
  (`UtinniPatches/Defs/ThingSetMakerDefs/RUT_RareGreentideCatches.xml`) — check what it already
  holds before adding a rare band.
- 🔑 **Wiring a RACE def into `fishTypes` instead of an ITEM def makes a net produce a bare `Pawn`.**
  That is `GREENTIDE_FISH_ITEMS_FIX_1`'s own bug class, hit on this very biome. Every species here
  needs its two defs kept straight and named so they cannot be confused.

## ✅ NOT blocked by the parked sea item — and why that matters

`SEA_FLOOR_AND_CATCH_PASS_1` was stopped 2026-09-22 pending a Desktop lookup of how a shore map
depicts ocean water. **That block does not reach this item.** Its cause is that all four sea biomes
are `impassable=true` and generate 100% deep water with no shallow cells, so a fishing zone cannot
be placed. The Greentide is a **passable land biome** with ordinary rivers and pools — normal
fishing applies and nothing here depends on the shore question.

⚠️ Do confirm the Greentide actually generates water on its maps before claiming a live proof:
`QUICKTEST_RIVER_WATER_MISSING_1` records quicktest maps yielding **zero** water terrain across 6
tiles and 5 biomes, including controls that declared rivers. That is a quicktest defect, not a
Greentide defect, but it blocks live verification either way.

## spec

1. **Design the roster inside the commission's register system** — which band each species sits in,
   what it is worth, what it looks like. His five named shapes (aquatic worm, eel, parasitic moving
   plant, toothy tadpole, spiked eel) are the seed.
2. **Two defs per species where the pairing rule applies** — the ruled pattern from
   `SEA_FLOOR_AND_CATCH_PASS_1`: every catch species gets a floor/water creature, a shoal species
   gets ONE swarm creature standing in for the cloud, existing megafauna stay creature-only with no
   catch item. `SeaBeasts_Swarm.xml` is the file swarm creatures grow in, not a new one.
3. **Tier the defs correctly.** ⛔ A RimMandrake-tier def never names Star Wars
   (§7 Q11) — so bizarre-named species live in the `RSW_`/`RUT_` tier and reach the biome by
   patch, the way `WildAnimals_Greentide.xml` already delivers 22 Star Wars animals.
   Whether `RM_Greentide` gets any generic catch table at all is **left open**: his ruling rejected
   the vanilla-only list, and he has not been asked what the dependency-free fallback should be.
4. **Check for existing art before queuing any**, per CLAUDE.md's standing rule — search
   `infrastructure/artpipe/done/` and `_artsrc/` by subject, and check for a review sheet's
   `.decisions.json` in `Transient/` in case he has already ruled on a candidate's art.

## verify

Every Greentide catch resolves to an ITEM def, never a race def. Every catch species has its paired
water creature or a recorded reason it is catch-only. No `RM_`-tier def names Star Wars.
`validate_patch.py` clean on every touched file. ⛔ No live-proven claim while
`QUICKTEST_RIVER_WATER_MISSING_1` stands — say "authored, not live-proven" and mean it.

## criteria

Fishing the Greentide pulls out things that could not have come from anywhere else, and each of
them is also something you can meet in the water.

## Watch out

- ⛔ **Do not author the §4a vanilla-only fish pair.** He replaced it. Landing it "as a first step"
  would ship the exact content he declined.
- ⚠️ The campaign twin is **frozen** — its catch table is not to be edited for this work. New
  content lands in the correct tier and is patched on.
- ⚠️ A parasitic moving plant is a creature def, not a plant def. Filing it as flora would put it in
  `GREENTIDE_JUNGLE_TREE_ROSTER_1`'s scope by mistake; it belongs here.
