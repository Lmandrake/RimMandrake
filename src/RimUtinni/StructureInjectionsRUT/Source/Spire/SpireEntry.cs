using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    // SPIRE_DUNGEONS_MERGE_DARK_TOWER: the Cathedral's trust grants ENTRY to the Spire, never the
    // codes (owner, 2026-10-10, card 7). The stage lives per map on RM_MapComponent_BiomeAttitude and
    // the player stands on another map when it matters, so this keeps the last reading game-wide.
    // Reflection on the live component: this mod does not depend on the Rust Cathedral mod.
    public class GameComponent_SpireEntry : GameComponent
    {
        private const string AttitudeType = "RimMandrake.RustCathedral.Hum.RM_MapComponent_BiomeAttitude";
        private const int PollTicks = 250;

        public int cathedralStage;

        public GameComponent_SpireEntry(Game game)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref cathedralStage, "rutSpireCathedralStage", 0);
        }

        public override void GameComponentTick()
        {
            if (Find.TickManager.TicksGame % PollTicks == 0)
            {
                Poll();
            }
        }

        public void Poll()
        {
            cathedralStage = SpireEntryKernel.Fold(cathedralStage, ObservedStages());
        }

        private static IEnumerable<int> ObservedStages()
        {
            foreach (Map map in Find.Maps)
            {
                foreach (MapComponent comp in map.components)
                {
                    if (comp.GetType().FullName != AttitudeType)
                    {
                        continue;
                    }
                    MethodInfo getStage = comp.GetType().GetMethod("GetStage", BindingFlags.Public | BindingFlags.Static);
                    if (getStage != null)
                    {
                        yield return (int)getStage.Invoke(null, new object[] { map });
                    }
                }
            }
        }
    }

    public static class SpireEntry
    {
        private static GameComponent_SpireEntry Comp => Current.Game?.GetComponent<GameComponent_SpireEntry>();

        public static int CathedralStage
        {
            get
            {
                GameComponent_SpireEntry comp = Comp;
                if (comp == null)
                {
                    return 0;
                }
                comp.Poll();
                return comp.cathedralStage;
            }
        }

        public static bool SealOpens => SpireEntryKernel.SealOpens(StructureInjectionsRUTSettings.spireEntryGated, CathedralStage);

        // The GM blackboard's lane for a stage with no Cathedral map loaded to carry it.
        public static void RecordCathedralStage(int stage)
        {
            GameComponent_SpireEntry comp = Comp;
            if (comp != null)
            {
                comp.cathedralStage = stage;
            }
        }
    }

    public class CompProperties_SpireHull : CompProperties
    {
        public CompProperties_SpireHull()
        {
            compClass = typeof(CompSpireHull);
        }
    }

    public class CompSpireHull : ThingComp
    {
        public override void PostPreApplyDamage(ref DamageInfo dinfo, out bool absorbed)
        {
            absorbed = true;
        }
    }

    public class CompProperties_SpireSeal : CompProperties
    {
        public CompProperties_SpireSeal()
        {
            compClass = typeof(CompSpireSeal);
        }
    }

    public class CompSpireSeal : ThingComp
    {
        public override void PostPreApplyDamage(ref DamageInfo dinfo, out bool absorbed)
        {
            absorbed = true;
        }

        public override void CompTick()
        {
            if (parent.Spawned && parent.IsHashIntervalTick(60) && SpireEntry.SealOpens)
            {
                Open();
            }
        }

        private void Open()
        {
            Map map = parent.Map;
            IntVec3 pos = parent.Position;
            parent.Destroy(DestroyMode.Vanish);
            Messages.Message("The seal at the foot of the Spire has drawn back. Nobody touched it.",
                new TargetInfo(pos, map), MessageTypeDefOf.NeutralEvent, false);
        }
    }

    // Thick rock over the whole hull: the seal stays the only way in, against pods and shells alike.
    // Linked to RUT_SpireSite after the structure step, so the hull walls are already on the map.
    public class GenStep_SpireRoof : GenStep
    {
        public override int SeedPart => 794122601;

        public override void Generate(Map map, GenStepParams parms)
        {
            ThingDef hull = DefDatabase<ThingDef>.GetNamed("RUT_SpireHullWall");
            List<Thing> walls = map.listerThings.ThingsOfDef(hull);
            if (walls.Count == 0)
            {
                Log.Error("[SPIRE] no hull on the map: the structure step did not place RUT_Spire_HighCommand");
                return;
            }
            int minX = map.Size.x, minZ = map.Size.z, maxX = 0, maxZ = 0;
            foreach (Thing wall in walls)
            {
                IntVec3 c = wall.Position;
                minX = System.Math.Min(minX, c.x);
                minZ = System.Math.Min(minZ, c.z);
                maxX = System.Math.Max(maxX, c.x);
                maxZ = System.Math.Max(maxZ, c.z);
            }
            foreach (IntVec3 c in CellRect.FromLimits(minX, minZ, maxX, maxZ))
            {
                map.roofGrid.SetRoof(c, RoofDefOf.RoofRockThick);
            }
        }
    }
}
