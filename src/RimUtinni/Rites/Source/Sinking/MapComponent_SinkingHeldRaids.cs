// SUMP_SINKING_RITE_BUILD_1: EmpirePursuit raids that came due on a map under RUT_ImperialHoldOff (Patch_Sinking_PursuitRaid)
// wait here and are fired through the scenpart's own FireRaid_NewTemp on the first pursuit tick after the hold-off ends.
// Never lost (saved with the map), never sooner. Two deferred raids of the same strength collapse into one: the endless
// wave re-fires every pursuit tick, and a held week must not come back as a stack of identical raids.
using System.Collections.Generic;
using Verse;

namespace RimMandrake.Utinni.Rites
{
    public class MapComponent_SinkingHeldRaids : MapComponent
    {
        private List<float> mults = new List<float>();
        private List<float> floors = new List<float>();

        public MapComponent_SinkingHeldRaids(Map map) : base(map) { }

        public int Count => mults.Count;

        public void Hold(float pointsMultiplier, float minPoints)
        {
            for (int i = 0; i < mults.Count; i++)
                if (mults[i] == pointsMultiplier && floors[i] == minPoints) return;
            mults.Add(pointsMultiplier);
            floors.Add(minPoints);
        }

        public override void MapComponentTick()
        {
            if (mults.Count == 0 || Find.TickManager.TicksGame % SinkingGlue.PursuitInterval != 1) return;
            if (SinkingGlue.HeldOff(map)) return;
            var m = new List<float>(mults);
            var f = new List<float>(floors);
            mults.Clear(); floors.Clear();
            for (int i = 0; i < m.Count; i++)
                if (!SinkingGlue.FirePursuitRaid(map, m[i], f[i])) break; // pursuit gone or off this map: nothing to fire
        }

        public override void ExposeData()
        {
            Scribe_Collections.Look(ref mults, "sinkingHeldMults", LookMode.Value);
            Scribe_Collections.Look(ref floors, "sinkingHeldFloors", LookMode.Value);
            if (mults == null) mults = new List<float>();
            if (floors == null) floors = new List<float>();
            if (floors.Count != mults.Count) { int n = System.Math.Min(mults.Count, floors.Count); mults.RemoveRange(n, mults.Count - n); floors.RemoveRange(n, floors.Count - n); }
        }
    }
}
