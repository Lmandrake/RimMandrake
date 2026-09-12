using System.Collections.Generic;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // Per-cell dive cooldown, keyed by map. Deliberately NOT tied to any
    // building or zone (no such Thing exists in this mod, by design — see
    // About.xml "why a dive SITE, not a bottom-walker pawn"): the cell
    // itself, via its tagged terrain, is the whole interaction surface.
    public class RM_MapComponent_DiveSites : MapComponent
    {
        private List<IntVec3> cellKeys = new List<IntVec3>();
        private List<int> cellTicks = new List<int>();
        private Dictionary<IntVec3, int> lastDiveTick = new Dictionary<IntVec3, int>();

        public RM_MapComponent_DiveSites(Map map) : base(map)
        {
        }

        public bool OnCooldown(IntVec3 cell, out int ticksRemaining)
        {
            if (lastDiveTick.TryGetValue(cell, out int last))
            {
                int elapsed = Find.TickManager.TicksGame - last;
                if (elapsed < RM_DivingSettings.diveCooldownTicks)
                {
                    ticksRemaining = RM_DivingSettings.diveCooldownTicks - elapsed;
                    return true;
                }
            }
            ticksRemaining = 0;
            return false;
        }

        public void RecordDive(IntVec3 cell)
        {
            lastDiveTick[cell] = Find.TickManager.TicksGame;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref lastDiveTick, "lastDiveTick", LookMode.Value, LookMode.Value,
                ref cellKeys, ref cellTicks);
            if (lastDiveTick == null)
            {
                lastDiveTick = new Dictionary<IntVec3, int>();
            }
        }
    }
}
