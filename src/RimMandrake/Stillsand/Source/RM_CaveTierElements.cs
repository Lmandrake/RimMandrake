using System.Collections.Generic;
using RimMandrake.EnvironmentalHazards;
using RimWorld;
using Verse;

namespace RimMandrake.Stillsand
{
    // STILLSAND_CAVE_TIER_ROWS_1: element vocabulary the tier rows (krayt den, sarlacc seep,
    // debt cave) need. The rows themselves live in the RSW / Utinni mods; only these two
    // generic elements live here, with no canon names in them.

    /// <summary>One weighted either/or inside a row: with `chanceA` run the `a` elements, else the `b` elements.</summary>
    public class RM_CaveElement_Either : RM_SetPieceElement
    {
        public float chanceA = 0.5f;
        public List<RM_SetPieceElement> a = new List<RM_SetPieceElement>();
        public List<RM_SetPieceElement> b = new List<RM_SetPieceElement>();

        public override void SpawnAt(IntVec3 loc, Map map, GenStepParams parms)
        {
            List<RM_SetPieceElement> pick = Rand.Chance(chanceA) ? a : b;
            if (pick == null)
            {
                return;
            }
            for (int i = 0; i < pick.Count; i++)
            {
                pick[i].SpawnAt(loc, map, parms);
            }
        }
    }

    /// <summary>A long-dead person lying desiccated on the cave floor. The cave's preservation scan
    /// then keeps the corpse from changing further.</summary>
    public class RM_CaveElement_Mummy : RM_SetPieceElement
    {
        public PawnKindDef kind;
        public RM_CavePlace place = RM_CavePlace.back;

        public override void SpawnAt(IntVec3 loc, Map map, GenStepParams parms)
        {
            if (kind == null)
            {
                Log.Error("[Stillsand] RM_CaveElement_Mummy has no kind configured.");
                return;
            }
            RM_PreciousCaveContext ctx = RM_PreciousCaveContext.For(loc, map);
            IntVec3 cell = ctx.Pick(place, c => RM_PreciousCaveContext.FreeForItem(c, map));
            if (!cell.IsValid)
            {
                return;
            }
            Pawn pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null,
                PawnGenerationContext.NonPlayer, forceGenerateNewPawn: true, canGeneratePawnRelations: false,
                forceDead: true));
            Corpse corpse = pawn.Corpse;
            if (corpse == null)
            {
                return;
            }
            GenSpawn.Spawn(corpse, cell, map);
            CompRottable rot = corpse.GetComp<CompRottable>();
            if (rot != null)
            {
                rot.RotProgress = rot.PropsRot.TicksToDessicated + 1f;
            }
        }
    }
}
