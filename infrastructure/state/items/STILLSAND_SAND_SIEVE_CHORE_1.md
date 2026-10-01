# STILLSAND_SAND_SIEVE_CHORE_1 — sifting glass sand into fine sand as a pawn chore with a carried sieve

From `STILLSAND_GLASS_LENS_CHAIN_1` §2. Owner, typed (card 2026-09-30 18:11 PDT): *"Can we make
pawns get the sand sieve and do it as a chore? If not, the sand sieve becomes just a recipe at a
new processing building called the Sand Sieve."*

## feasibility finding (offline, 2026-10-01)

**The chore form is feasible and needs no building.** Vanilla does not require a work table for
a pawn job. A `WorkGiver_Scanner` (under Crafting or Hauling) can scan `RM_GlassSand` stacks and
only offer the job when the pawn carries a sieve. Vanilla has no generic "tool required" field, so
that check is ours, and it is a trivial test of `pawn.inventory.innerContainer`. A `JobDriver`
then walks to the stack, works N ticks with a progress bar, consumes X glass sand, and drops fine
sand plus the grit-find rolls. The player sets the scope with an allowed area, a stack
designation, or simply "sift glass sand in the home area". The whole thing is one C# file plus a
WorkGiverDef, a JobDef and the sieve ThingDef (a craftable tool item). The fallback (a Sand Sieve
building or the High Cuisine "sifter") is not needed.

## spec

1. `RM_SandSieve`: a cheap craftable tool item, carried in inventory. If the pawn has no sieve when
   it takes the chore, it fetches one first.
2. The sifting chore turns glass sand into `RM_FineSand`, with a yield slider in the "Stillsand:
   glass and lenses" settings. Small chances of grit finds: `RM_BiosilicaGrit`/`RM_Biosilica`
   fragments, glasscrust grit, and rarely an `RM_GlassPearl` seed.
3. A Mod Settings toggle and the sifting-yield slider (parent §12).
4. Art: artpipe job `RM_SandSieve` is already registered. Check `infrastructure/artpipe/` before
   queuing anything.

## criteria
- A pawn carrying a sieve sifts glass sand in the home area without being ordered, and fine sand
  appears. A pawn without a sieve is never offered the chore.
