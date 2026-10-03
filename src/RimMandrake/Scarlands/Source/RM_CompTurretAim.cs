using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Scarlands
{
    // WARSCAR_TURRETS_TRACK_1. A VERBLESS aim comp for the broken ancient turrets: it owns no Verb, no
    // projectile and no target-finding of the turret machinery, so it cannot fire by construction.
    // The barrel top turns to follow the nearest MOVING pawn in range. Also hosts the refit gizmo that
    // converts the wreck into RM_OldLineTurret (a blueprint the colonists build).
    public class CompProperties_TurretAim : CompProperties
    {
        public float range = 30f;
        public float turnDegreesPerTick = 3f;
        public int scanIntervalTicks = 15;
        public string topTexPath = "Things/Building/Security/TurretMini_Top";
        public Vector2 topDrawSize = new Vector2(2f, 2f);
        public string refitDef = "RM_OldLineTurret";

        public CompProperties_TurretAim() { compClass = typeof(CompTurretAim); }
    }

    public class CompTurretAim : ThingComp
    {
        public float aimAngle;          // degrees, 0 = north, clockwise (Quaternion.AngleAxis convention)
        public Pawn trackedPawn;       // state read: who the barrel is following, null when idle
        private Material topMat;
        private IntVec3 lastSeenCell = IntVec3.Invalid;

        public CompProperties_TurretAim Props { get { return (CompProperties_TurretAim)props; } }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref aimAngle, "aimAngle", 0f);
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!RM_WarscarSettings.turretTrackingEnabled || !parent.Spawned) { trackedPawn = null; return; }
            if (parent.IsHashIntervalTick(Props.scanIntervalTicks)) trackedPawn = FindMover();
            if (trackedPawn == null) return;
            float want = (trackedPawn.DrawPos - parent.DrawPos).AngleFlat();
            aimAngle = Mathf.MoveTowardsAngle(aimAngle, want, Props.turnDegreesPerTick);
        }

        // Nearest pawn in range that is moving. In a Settling these are the only moving things.
        private Pawn FindMover()
        {
            Map map = parent.Map;
            Pawn best = null;
            float bestDist = Props.range * Props.range;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.Dead || p.Downed) continue;
                if (p.pather == null || !p.pather.Moving) continue;
                float d = (p.Position - parent.Position).LengthHorizontalSquared;
                if (d < bestDist) { bestDist = d; best = p; }
            }
            return best;
        }

        public override void PostDraw()
        {
            base.PostDraw();
            if (!RM_WarscarSettings.turretTrackingEnabled) return;
            if (topMat == null)
                topMat = MaterialPool.MatFrom(Props.topTexPath, ShaderDatabase.Cutout);
            Vector3 pos = parent.DrawPos;
            pos.y = AltitudeLayer.BuildingOnTop.AltitudeFor();
            Matrix4x4 m = default(Matrix4x4);
            m.SetTRS(pos, Quaternion.AngleAxis(aimAngle, Vector3.up),
                new Vector3(Props.topDrawSize.x, 1f, Props.topDrawSize.y));
            Graphics.DrawMesh(MeshPool.plane10, m, topMat, 0);
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_WarscarSettings.turretTrackingEnabled) return null;
            return trackedPawn != null ? "Barrel turning to follow movement." : null;
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            if (!RM_WarscarSettings.turretRefitEnabled) yield break;
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(Props.refitDef);
            if (def == null) yield break;
            Command_Action cmd = new Command_Action
            {
                defaultLabel = "Refit",
                defaultDesc = "Strip this wreck and lay down a blueprint for an old-line turret on its footprint. "
                              + "Colonists build it from " + CostText(def) + ". The wreck is consumed.",
                icon = def.uiIcon,
                action = delegate { DoRefit(); }
            };
            yield return cmd;
        }

        private static string CostText(ThingDef def)
        {
            List<string> parts = new List<string>();
            if (def.costList != null)
                foreach (ThingDefCountClass c in def.costList) parts.Add(c.count + " " + c.thingDef.label);
            return string.Join(", ", parts.ToArray());
        }

        // Public so a validation harness can call it, but only effective for the player.
        public bool DoRefit()
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(Props.refitDef);
            if (def == null || !parent.Spawned) return false;
            Map map = parent.Map;
            IntVec3 pos = parent.Position;
            parent.Destroy(DestroyMode.Vanish);
            GenConstruct.PlaceBlueprintForBuild(def, pos, map, Rot4.North, Faction.OfPlayer, null);
            return true;
        }
    }

    // Applies the Mod Settings damage/cooldown multipliers to the old-line turret once defs are loaded.
    // Takes effect on game start (defs are shared), as the setting's own label says.
    [StaticConstructorOnStartup]
    public static class OldLineTurretTuning
    {
        static OldLineTurretTuning()
        {
            ThingDef bullet = DefDatabase<ThingDef>.GetNamedSilentFail("RM_OldLineTurret_Bullet");
            ThingDef turret = DefDatabase<ThingDef>.GetNamedSilentFail("RM_OldLineTurret");
            if (bullet != null && bullet.projectile != null)
            {
                // damageAmountBase is a private field in 1.6, so scale it by reflection.
                System.Reflection.FieldInfo f = typeof(ProjectileProperties).GetField("damageAmountBase",
                    System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic);
                if (f != null)
                    f.SetValue(bullet.projectile, Mathf.Max(1, Mathf.RoundToInt(
                        (int)f.GetValue(bullet.projectile) * RM_WarscarSettings.oldLineDamageFactor)));
            }
            if (turret != null && turret.building != null)
                turret.building.turretBurstCooldownTime *= RM_WarscarSettings.oldLineCooldownFactor;
        }
    }
}
