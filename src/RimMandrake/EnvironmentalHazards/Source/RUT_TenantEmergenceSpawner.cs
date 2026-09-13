using RimWorld;

namespace RimMandrake.EnvironmentalHazards
{
    // FEVER_WOOD_MECHANICS_1 F4 spike. The deep thing built in full,
    // plot-reserved: "built... so that it can emerge at some point... the
    // emergence is plot-reserved, never ambient" (the_fever_wood.md §4);
    // ban §6.1's linter check is that no def with RUT_Tenant in its
    // defName is reachable from any ambient IncidentDef/ThinkTree — this
    // class itself is the gate: it is referenced by NOTHING (no def below
    // instantiates a RUT_TenantEmergenceSpawner ThingDef), so the linter
    // check passes by construction, not by a separate audit pass.
    //
    // Engine seam CONFIRMED (spec cited this at
    // Source/RimWorld/BuildingGroundSpawner.cs:35; re-checked here against
    // the live 1.6/Odyssey decompile at RimWorld/BuildingGroundSpawner.cs
    // — the class, its PostMakeInt/Spawn override shape, and its re-
    // terraining on spawn for affordance are all real and unchanged from
    // the spec's citation). GroundSpawner base itself confirmed at
    // RimWorld/GroundSpawner.cs.
    //
    // SPIKE SCOPE: this is the minimal compiling proof that the seam
    // exists and that a subclass needs no overrides to be valid (the base
    // class's PostMakeInt already reads def.building.groundSpawnerThingToSpawn,
    // so an XML-only BuildingDef pointing at this class plus a
    // groundSpawnerThingToSpawn is sufficient — the class body below is
    // intentionally empty). Explicitly NOT done here, and not silently
    // skipped: RUT_TenantEmergedMass (central mass ThingDef/building),
    // RUT_TenantTentacle (PawnKindDef — tentacles must be pawns, per
    // sarlacc_spec.md's family register, not a non-pawn animator), the
    // tentacle-pawn spawn wiring around the emerged mass, and all art —
    // all of it is the L-effort remainder of F4, off the critical path of
    // the playable biome by design, and rides the standing art pipeline
    // and the roster pass rather than this C# spike.
    public class RUT_TenantEmergenceSpawner : BuildingGroundSpawner
    {
    }
}
