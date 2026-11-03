using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Bones
{
    // BONES_LEAN_PORT_BUILD_TREELESS_WORLD live proof, reached through jawa/static_call (validation.py).
    // ProofButcher generates one throwaway pawn per kind (never spawned), runs the real Pawn.ButcherProducts (so the
    // Harmony postfix fires as in play) and counts RM_Bones: a muffalo yields some, an insect none, and with the
    // setting off the muffalo yields none. The setting is restored and every pawn and product discarded.
    public static class RM_BonesProof
    {
        private static int Bones(string kind, float efficiency, out int meat, StringBuilder sb)
        {
            meat = 0;
            PawnKindDef pk = DefDatabase<PawnKindDef>.GetNamedSilentFail(kind);
            if (pk == null)
            {
                sb.Append(kind).Append(": no such PawnKindDef; ");
                return -1;
            }
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(pk, null, PawnGenerationContext.NonPlayer, -1,
                forceGenerateNewPawn: true, fixedBiologicalAge: 5f, fixedChronologicalAge: 5f));
            int bones = 0;
            try
            {
                foreach (Thing t in p.ButcherProducts(null, efficiency))
                {
                    if (t == null) continue;
                    if (t.def == RM_BonesDefOf.RM_Bones) bones += t.stackCount;
                    else if (t.def == p.RaceProps.meatDef) meat += t.stackCount;
                    if (!t.Destroyed) t.Destroy();
                }
            }
            finally
            {
                if (!p.Discarded) Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.Discard);
            }
            return bones;
        }

        public static string ProofButcher(string unused)
        {
            StringBuilder sb = new StringBuilder();
            bool was = RM_BonesSettings.butcherBones;
            float mult = RM_BonesSettings.boneMultiplier;
            bool pass = true;
            try
            {
                RM_BonesSettings.butcherBones = true;
                RM_BonesSettings.boneMultiplier = 1f;
                int m1, m2, m3;
                int muff = Bones("Muffalo", 1f, out m1, sb);
                int bug = Bones("Megascarab", 1f, out m2, sb);
                RM_BonesSettings.butcherBones = false;
                int off = Bones("Muffalo", 1f, out m3, sb);
                sb.Append("muffalo bones=").Append(muff).Append(" meat=").Append(m1)
                  .Append("; megascarab bones=").Append(bug).Append(" meat=").Append(m2)
                  .Append("; muffalo with setting off bones=").Append(off).Append(" meat=").Append(m3);
                pass = muff > 0 && m1 > 1 && bug == 0 && off == 0;
            }
            finally
            {
                RM_BonesSettings.butcherBones = was;
                RM_BonesSettings.boneMultiplier = mult;
            }
            return (pass ? "PASS " : "FAIL ") + sb;
        }

        // Def side, read in the running game: RM_Bones is Woody stuff, the stat and the floor exist, and none of the
        // donor's defs is loaded (the aliases only apply when the old name resolves to nothing).
        public static string ProofDefs(string unused)
        {
            StringBuilder sb = new StringBuilder();
            ThingDef b = RM_BonesDefOf.RM_Bones;
            bool woody = b != null && b.IsStuff && b.stuffProps.categories.Contains(StuffCategoryDefOf.Woody);
            bool wall = woody && GenStuff.AllowedStuffsFor(ThingDefOf.Wall).Contains(b);
            bool stat = RM_BonesDefOf.RM_BoneAmount != null;
            bool floor = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_BoneFloor") != null;
            List<string> donor = new List<string>();
            foreach (string n in new[] { "BoneItem", "BoneChina", "Bonecrete", "BonePlastic", "BoneWall" })
            {
                if (DefDatabase<ThingDef>.GetNamedSilentFail(n) != null) donor.Add(n);
            }
            if (DefDatabase<StatDef>.GetNamedSilentFail("BoneAmount") != null) donor.Add("BoneAmount");
            sb.Append("woody=").Append(woody).Append(" wallStuff=").Append(wall).Append(" stat=").Append(stat)
              .Append(" floor=").Append(floor).Append(" donorDefsLoaded=[").Append(string.Join(",", donor)).Append("]");
            return (woody && wall && stat && floor && donor.Count == 0 ? "PASS " : "FAIL ") + sb;
        }
    }
}
