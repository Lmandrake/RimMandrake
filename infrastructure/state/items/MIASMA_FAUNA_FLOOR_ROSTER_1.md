# MIASMA_FAUNA_FLOOR_ROSTER_1 — the arthropod floor, the fever-swarm, and the stranded as a condition

**the Miasma**

🔑 **The roster IS the specification — read it, do not re-derive it from here:**
`design/Jawa/worldbuilding/biomes/miasma_fauna_roster_2026-09-23.md`. Authored at the owner's
sitting of 2026-09-23. Sheet: `design/Jawa/worldbuilding/biomes/the_miasma.md`.

## why this exists

The sheet books five creatures as owed. **MEASURED 2026-09-23: exactly one exists** —
`RUT_WardenMother`. The starred arthropod floor, the `karr-` fever-swarm, the delta-loam
composter and the stranded are all nothing. ⚠️ And the two shipped `karr-` creatures,
`RUT_Karrun` and `RUT_Karrash`, are the **Greentide's and the Scald's** crab-things: they
establish the clade's naming and art register, not this biome's swarm.

## spec

1. **Four scuttler defs** — `RM_Karravel` (the flat disc that carpets the mud film),
   `RM_Karrobel` (the burrower whose castings **are** the delta loam), `RM_Karrimeth` (only ever
   a moving mass), `RM_Karrolun` (hand-sized; the harvest industry's target). Four rather than
   one because the floor is now prey to five carnivorous plants, every nursery juvenile, every
   refugee predator **and** a harvest, while also producing the loam — four jobs on one
   silhouette is what splitting avoids.
2. **One fever-swarm def** — `RM_Karrathil`, the mangals' only pollinator **and** the disease
   vector, closer to a weather effect than a pawn. It is the green-gold breath seen close up.
3. 🔴 **The stranded are a CONDITION, not a cast** — owner ruling, decision taken by question
   card: they are the sea nursery's failures, the same creatures as the crowded young, carrying
   a deformation from the muck. ⛔ **Author no "stranded species".** Wire instead:
   - trigger — a juvenile caught in a stranding pool. ✅ `RM_StrandingPoolsExtension` shipped
     2026-09-13 and has had nothing to strand.
   - deformation — a hediff. The built precedent is `RM_HediffComp_ForgeOnSurvival`, which
     already turns surviving something into a permanent change.
   - behaviour — **suppress** `RM_JobGiver_ReturnToWater`; the tell is an animal trying to
     reach water it can no longer use.
4. **Fold the composter into the scuttler clade** (`RM_Karrobel`) rather than authoring a
   separate family — owner chose both overlapping options with the overlap stated on the card.
   `RM_Pallasheen` from `MIASMA_FLORA_ROSTER_1` germinates only where it has worked, so the
   plant is this animal's visible receipt.

## verify

- `validate_patch.py <path> --defs …` on every new def file; confirm rows landed from a
  post-load def dump, since an unmatched `PatchOperationAdd` is silent.
- Zero new Config errors in `Player.log` — grep it.
- A quicktest map, looked at: the floor must read as *constant small life*, a karrimeth mass
  must read as an event, and a stranding pool left behind by a surge must produce a stranded
  animal.
- 🔴 Search `infrastructure/artpipe/done/`, `_artsrc/`, `registry.jsonl` and any review sheet's
  `.decisions.json` by subject before queueing art (owner's standing rule, 2026-09-20).

## criteria

The Miasma's food pyramid stands on creatures that exist; the delta loam has a producer and a
findable tell; the fever bargain is real in both directions; and the surge generates stranded
animals that differ every game instead of a fixed cast of three.

## Watch out

- 🔴 **`RM_Stranded` is ALREADY TAKEN** — it is an unrelated rescue quest in
  `src/RimMandrake/StrandedQuest/`. Do not reuse that defName, and name carefully so a future
  search cannot conflate a rescue quest with a deformed fish.
- ⛔ **Do not add a second pollinator.** It is the obvious balance fix and it deletes the
  sheet's central bargain. ⛔ Do not add a second giant either — the giant lane is the warden
  mothers', which is why `AA_OvergrownColossus` is evicted.
- 🔴 **If killing karrathil is strictly good, the biome is broken.** The pollination half must
  be mechanically real, which means flora reproduction has to be able to fail.
- ⚠️ **Two of five are not creature portraits.** `RM_Karravel` must work as a carpet and
  `RM_Karrimeth` only ever appears as a mass. An art brief delivering handsome hero sprites has
  delivered the wrong thing.
- 🔑 **Read `RM_CompVerminBreeder` + `RM_MapComponent_VerminPopulation` before writing any C#
  for the floor.** A population drawn down by plants, predators and a harvest is exactly what a
  vermin-population component is, and in the last comparable sitting four of six "new"
  mechanisms were already built.
- 🔴 **Three engine questions, all UNMEASURABLE on the Mac** — Desktop pass, and ⛔ none may be
  reasoned out from a doc: can a plant's reproduction be gated on a nearby animal; how much can
  a hediff alter an animal's rendered appearance; can a plant consume a small wild animal and be
  restricted to one species.
- ⛔ **This item does not re-adjudicate the 32 existing fauna rows** on `RUT_Miasma`, nor the
  37-row eviction list. Evictions are stopped (owner, 2026-09-22) and rosters are handled at
  each biome's own sitting.
- ⏳ **The free tier's nursery depends on `SEA_BEASTS_TIER_RULING_1`, which is now RULED and
  owed** (2026-09-23, decision taken by question card: the 11 invented sea beasts move to the
  `RM_` tier, the 7 canon ones stay). ⇒ Until that lands, a franchise-free Miasma has no
  juveniles and therefore no stranded. ✅ It is no longer an open question, so ⛔ do not re-raise
  it — just sequence this item's stranded work after it.
