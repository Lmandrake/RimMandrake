# MIASMA_SCUTTLER_PREDATION_1 — wire the five carnivorous plants to actually eat the arthropod floor

Caused by `MIASMA_FAUNA_FLOOR_ROSTER_1`.

## what

`src/RimMandrake/Miasma/Defs/ThingDefs_Plants/RM_Miasma_Predators.xml` ships five
carnivorous plants (`RM_Ullavess`, `RM_Nemreth`, `RM_Velluric`, `RM_Braskeen`,
`RM_Ommolyn`) whose own header says plainly: *"No carnivory C# is built in this
pass... wiring real predation onto these five is follow-on work once the
scuttler roster lands."* The scuttler roster has now landed —
`MIASMA_FAUNA_FLOOR_ROSTER_1` shipped all four arthropod-floor scuttlers
(`RM_Karravel`/`RUT_Karrobel`/`RM_Karrimeth`/`RM_Karrolun`, shared population
pool via `RM_VerminPressureExtension`'s `RM_MiasmaScuttlers` group tag). The
prey exists now; the predation mechanism itself does not.

## why this is its own item, not folded into the parent

The parent item's own text calls this a genuine **engine question,
UNMEASURABLE on the Mac**: *"can a plant consume a small wild animal at all,
and can it be restricted to one species?"* — and says explicitly that none of
the three flagged engine questions may be reasoned out from a doc. Building
blind C# against an unverified engine hook risks the same "confident wrong
number" failure mode this repo has hit repeatedly elsewhere. This item exists
so the work is tracked rather than silently dropped into a closed parent's
prose.

## spec (draft — Desktop pass owed first)

1. **Desktop engine check first.** Does `Plant` (or something reachable from
   it) expose any hook for "consume a spawned Pawn on this or an adjacent
   cell"? If not, what is the real choke point — likely a Harmony patch on
   plant tick/growth, or a custom comp that scans nearby cells for an eligible
   scuttler pawn and kills+absorbs it, mirroring how
   `RM_PollinationGateExtension`/`RM_Patch_PollinationGate.cs` found their own
   choke point (`WildPlantSpawner.CalculatePlantsWhichCanGrowAt`) for a
   different "no comp hook exists" problem in this same biome.
2. **Restrict to the scuttler clade only**, never a colonist or tame animal —
   owner ruling already recorded in the predators file's own header.
3. Each plant's "visible consequence" text (too-clear water, scuttler-free
   mud, closed blades, cloudy vessel) should become a real, readable tell once
   a plant has fed, not just flavor text — same posture as `RM_Pallasheen`
   germinating only where `RM_Karrobel` has worked.
4. Feed from the shared `RM_MiasmaScuttlers` population pool
   (`RM_MapComponent_VerminPopulation`) rather than a separate untracked kill,
   so the vermin-breeder pool's replenishment and the predation drawdown are
   the same accounting the roster's own "one population, four draws on it"
   describes.

## verify

- `validate_patch.py --defs` on whatever new def/patch lands.
- Zero new Config errors in `Player.log`.
- A quicktest map, looked at: a predator plant should visibly and
  measurably reduce nearby scuttler numbers over time, without ever
  targeting a colonist or tame animal.

## criteria

The five carnivorous plants have a real mechanical effect on the arthropod
floor's population, restricted to the four `karr-` scuttler species, with a
readable in-world tell — not just descriptive text with no mechanism behind
it.
