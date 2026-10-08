using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.JawaIkee
{
    /// <summary>
    /// Which xenotypes are COMFORTED by an ikee rather than unsettled by it.
    /// This lives on the ThoughtDef as a DefModExtension deliberately: the owner's
    /// list is a design call that will be tuned, and tuning it must not require a
    /// rebuild of this assembly. Add or remove names in the XML.
    /// </summary>
    public class IkeeToleranceExtension : DefModExtension
    {
        public List<XenotypeDef> tolerantXenotypes = new List<XenotypeDef>();

        /// <summary>Cells around the pawn that count as "nearby".</summary>
        public float radius = 12f;
    }

    /// <summary>
    /// "The ikee is watching me."
    ///
    /// Owner, 2026-08-23: a positive mood buff for Jawa, Hutt and the other Star Wars
    /// species known to keep creepy pets; every other xenotype takes a creep factor.
    ///
    /// Stage 0 = comforted (tolerant xenotype).  Stage 1 = unsettled (everyone else).
    /// </summary>
    public class ThoughtWorker_IkeeNearby : ThoughtWorker
    {
        // Resolved once. def.defName is compared rather than a hard reference so that
        // this assembly does not need a compile-time dependency on Alpha Animals.
        private const string IkeeDefName = "AA_Eyeling";

        protected override ThoughtState CurrentStateInternal(Pawn p)
        {
            // Animals do not have opinions about other animals, and an unspawned or dead pawn has no map to search.
            bool onMap = p != null && p.Spawned && p.Map != null;
            bool humanlike = onMap && p.RaceProps != null && p.RaceProps.Humanlike;
            var ext = humanlike ? def.GetModExtension<IkeeToleranceExtension>() : null;
            float radius = ext?.radius ?? RSW_IkeeKernel.DefaultRadius;

            // 🔑 No genes tracker means a baseliner-equivalent pawn: not tolerant.
            XenotypeDef xeno = humanlike ? p.genes?.Xenotype : null;
            bool tolerant = xeno != null && ext != null && ext.tolerantXenotypes.Contains(xeno);

            int stage = RSW_IkeeKernel.Stage(RSW_JawaIkeeSettings.ikeeThoughtEnabled, onMap, humanlike, () => IkeeNear(p, radius), tolerant);
            return stage == RSW_IkeeKernel.Inactive ? ThoughtState.Inactive : ThoughtState.ActiveAtStage(stage);
        }

        private static bool IkeeNear(Pawn p, float radius)
        {
            // ⚠️ AllPawnsSpawned is IReadOnlyList<Pawn> in 1.6, not List<Pawn>.
            IReadOnlyList<Pawn> all = p.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < all.Count; i++)
            {
                Pawn other = all[i];
                if (other == null || other == p) continue;
                if (other.def == null || other.def.defName != IkeeDefName) continue;
                if (other.Dead) continue;
                IntVec3 d = other.Position - p.Position;
                if (!RSW_IkeeKernel.Nearby(d.x, d.z, radius)) continue;
                return true;
            }
            return false;
        }
    }
}
