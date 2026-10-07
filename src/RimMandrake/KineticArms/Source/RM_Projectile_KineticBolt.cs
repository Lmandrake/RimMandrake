using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.KineticArms
{
    /// <summary>Per-projectile (or kicker mine) cone, read by RM_Projectile_KineticBolt and RM_Building_KickerMine.</summary>
    public class RM_KineticBoltExtension : DefModExtension
    {
        /// <summary>Total cone angle opening ahead of the back-stepped centre.</summary>
        public float coneDegrees = 90f;
    }

    /// <summary>
    /// A bolt whose blast pushes ALONG THE SHOT (design §10). The flight vector is captured at impact from the
    /// projectile's own origin/destination (never from where the shooter is now). The blast is centred one cell back
    /// along it, and only the cone ahead of that centre (plus the impact cell) is affected; the launcher is ignored.
    /// If the back cell is out of bounds or impassable the blast falls back to an ordinary radial one at the impact.
    /// </summary>
    public class RM_Projectile_KineticBolt : Projectile_Explosive
    {
        protected override void Explode()
        {
            Map map = Map;
            IntVec3 impact = Position;
            float cone = def.GetModExtension<RM_KineticBoltExtension>()?.coneDegrees ?? 90f;
            List<Thing> ignored = launcher != null ? new List<Thing> { launcher } : null;
            List<IntVec3> cells = null;
            IntVec3 centre = impact;
            if (RM_KineticMath.Dir(origin.x, origin.z, destination.x, destination.z, out float dx, out float dz))
            {
                RM_KineticArmsUtil.ConeBlast(map, impact, dx, dz, def.projectile.explosionRadius, cone, out centre, out cells);
            }
            Destroy();
            GenExplosion.DoExplosion(centre, map, def.projectile.explosionRadius, DamageDef, launcher, DamageAmount, ArmorPenetration,
                def.projectile.soundExplode, equipmentDef, def, intendedTarget.Thing, ignoredThings: ignored, overrideCells: cells);
            RM_KineticArmsJournal.Add("bolt", def.defName, impact, centre, cells?.Count ?? -1);
        }
    }

    public static class RM_KineticArmsUtil
    {
        /// <summary>Back-step centre and the cone cells for a push along (dx,dz) from <paramref name="impact"/>. Returns
        /// cells == null (radial fallback at the impact) when the back cell is unusable.</summary>
        public static void ConeBlast(Map map, IntVec3 impact, float dx, float dz, float radius, float cone, out IntVec3 centre, out List<IntVec3> cells)
        {
            RM_KineticMath.BackStep(impact.x, impact.z, dx, dz, out int bx, out int bz);
            centre = new IntVec3(bx, 0, bz);
            cells = null;
            if (!centre.InBounds(map) || centre.Impassable(map))
            {
                centre = impact;
                return;
            }
            cells = new List<IntVec3>();
            foreach (var (x, z) in RM_KineticMath.ConeCells(bx, bz, impact.x, impact.z, dx, dz, radius, cone))
            {
                var c = new IntVec3(x, 0, z);
                if (c.InBounds(map) && (c == impact || GenSight.LineOfSight(centre, c, map, skipFirstCell: true)))
                {
                    cells.Add(c);
                }
            }
        }
    }
}
