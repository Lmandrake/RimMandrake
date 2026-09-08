using System.Linq;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    public class CompProperties_DWHeadDropper : CompProperties
    {
        public CompProperties_DWHeadDropper() => compClass = typeof(CompDWHeadDropper);
    }

    /// <summary>
    /// DROIDWORKS_HEADS_BRAINS_SPIKES_1 (packet B3). On DW_Race_Base so every
    /// droid, any family, drops its own head on death - the salvage half of
    /// the shop economy ("Personality matrices... you keep using them,
    /// because they're rare and valuable still even quirky", ruling 6).
    /// Same Notify_Killed hook CompDroidDetonation already uses (state 5);
    /// the two are independent - a detonating droid still drops its head.
    /// </summary>
    public class CompDWHeadDropper : ThingComp
    {
        public override void Notify_Killed(Map prevMap, DamageInfo? dinfo = null)
        {
            if (prevMap == null) return;
            Pawn pawn = parent as Pawn;
            if (pawn == null) return;
            // Same LastOrDefault reasoning as CompDroidDetonation.Notify_Killed:
            // XML inheritance APPENDS modExtensions, so the race's own (more
            // specific) DroidworksExtension always sorts after the family
            // abstract's inherited copy.
            DroidworksExtension ext = pawn.def.modExtensions?.OfType<DroidworksExtension>().LastOrDefault();
            ThingDef headDef = HeadDefFor(ext?.chassisClass ?? 0);
            if (headDef == null) return;
            Thing head = ThingMaker.MakeThing(headDef);
            (head as ThingWithComps)?.GetComp<CompHeadIdentity>()?.SnapshotFrom(pawn);
            GenPlace.TryPlaceThing(head, pawn.PositionHeld, prevMap, ThingPlaceMode.Near);
        }

        // chassisClass ints per DroidworksExtension's own comment: 0 labour,
        // 1 protocol, 2 astromech, 3 battle, 4 heavy, 5 probe, 6 power,
        // 7 primitive (DROIDWORKS_PRIMITIVE_TIER_1, packet B9).
        private static ThingDef HeadDefFor(int chassisClass)
        {
            switch (chassisClass)
            {
                case 0: return DroidworksDefOf.RSW_DW_Head_Labour;
                case 1: return DroidworksDefOf.RSW_DW_Head_Protocol;
                case 2: return DroidworksDefOf.RSW_DW_Head_Astromech;
                case 3: return DroidworksDefOf.RSW_DW_Head_Battle;
                case 4: return DroidworksDefOf.RSW_DW_Head_Heavy;
                case 5: return DroidworksDefOf.RSW_DW_Head_Probe;
                case 6: return DroidworksDefOf.RSW_DW_Head_Power;
                case 7: return DroidworksDefOf.RSW_DW_Head_Primitive;
                default: return DroidworksDefOf.RSW_DW_Head_Labour;
            }
        }
    }
}
