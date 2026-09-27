using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // GREENTIDE_PLANT_SIGHT_BLOCK_ENGINE_1 — opt-in sight blocker.
    //
    // Content-blind: any ThingDef (a Plant is the case this was built for,
    // but nothing here requires one) adds this comp and its cells enter
    // RM_MapComponent_SightBlockGrid. The grid is consulted only by the
    // Harmony postfixes in RM_SightBlockPatches, and only while one of the
    // whitelisted "a pawn is LOOKING" call sites is on the stack — so fire
    // spread, explosions, facility links and spawn-cell finders never see it.
    //
    // Why a comp and not a bare modExtension: a plant's qualification changes
    // as it grows, and the comp's CompTickLong (plants tick Long) is the
    // incremental update point, so the hot LOS path reads a plain array and
    // never scans cell contents.
    // ════════════════════════════════════════════════════════════════════
    public class RM_CompProperties_SightBlocker : CompProperties
    {
        /// <summary>A Plant blocks sight only once its Growth reaches this. Ignored for non-plants (they always block).</summary>
        public float minGrowth = 0.5f;

        public RM_CompProperties_SightBlocker()
        {
            compClass = typeof(RM_CompSightBlocker);
        }
    }

    public class RM_CompSightBlocker : ThingComp
    {
        private Map registeredMap;
        private CellRect registeredRect;

        public RM_CompProperties_SightBlocker Props => (RM_CompProperties_SightBlocker)props;

        public bool Registered => registeredMap != null;

        public bool Qualifies
        {
            get
            {
                if (!parent.Spawned)
                {
                    return false;
                }
                if (parent is Plant plant)
                {
                    return plant.Growth >= Props.minGrowth;
                }
                return true;
            }
        }

        /// <summary>Re-evaluate and (un)register. Cheap; safe to call any time on the main thread.</summary>
        public void Refresh()
        {
            bool want = Qualifies;
            if (want && registeredMap != null && (registeredMap != parent.Map || registeredRect != parent.OccupiedRect()))
            {
                Unregister();
            }
            if (want && registeredMap == null)
            {
                registeredMap = parent.Map;
                registeredRect = parent.OccupiedRect();
                RM_MapComponent_SightBlockGrid.For(registeredMap)?.Register(registeredRect);
            }
            else if (!want && registeredMap != null)
            {
                Unregister();
            }
        }

        private void Unregister()
        {
            if (registeredMap == null)
            {
                return;
            }
            RM_MapComponent_SightBlockGrid.For(registeredMap)?.Deregister(registeredRect);
            registeredMap = null;
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            Refresh();
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            Unregister();
        }

        // Plants tick Long (every 2000 ticks); growth crossing minGrowth, or a
        // harvest resetting growth below it, is picked up here — worst case
        // 2000 ticks late, which for a plant that takes days to grow is nothing.
        public override void CompTickLong()
        {
            base.CompTickLong();
            Refresh();
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            Refresh();
        }
    }
}
