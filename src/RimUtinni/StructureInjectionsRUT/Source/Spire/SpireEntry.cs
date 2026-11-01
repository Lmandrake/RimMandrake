using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    // SPIRE_DUNGEONS_MERGE_DARK_TOWER: the Cathedral's trust grants ENTRY to the Spire, never the
    // codes (owner, 2026-10-10, card 7). The stage lives per map on RM_MapComponent_BiomeAttitude and
    // the player stands on another map when it matters, so this keeps the last reading game-wide.
    // That component is on EVERY map; GetStage answers -1 off Cathedral ground, and the kernel skips it.
    // Reflection on the live component: this mod does not depend on the Rust Cathedral mod.
    public class GameComponent_SpireEntry : GameComponent
    {
        private const string AttitudeType = "RimMandrake.RustCathedral.Hum.RM_MapComponent_BiomeAttitude";
        private const int PollTicks = 250;

        public int cathedralStage;
        private int sourceMap = -1;

        public GameComponent_SpireEntry(Game game)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref cathedralStage, "rutSpireCathedralStage", 0);
            Scribe_Values.Look(ref sourceMap, "rutSpireCathedralSourceMap", -1);
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
            cathedralStage = SpireEntryKernel.Fold(cathedralStage, ref sourceMap, ObservedStages());
        }

        private static IEnumerable<KeyValuePair<int, int>> ObservedStages()
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
                        yield return new KeyValuePair<int, int>(map.uniqueID, (int)getStage.Invoke(null, new object[] { map }));
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
}
