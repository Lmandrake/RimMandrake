using System.Collections.Generic;
using Verse;

namespace RimMandrake.StarWars.SWBestiary
{
    /// <summary>One size of sarlacc pit RSW_GenStep_SarlaccPit may land (Defs/DonorPackPort/RSW_DonorPack_Sarlacc.xml).</summary>
    public class RSW_SarlaccPitSize
    {
        public ThingDef thingDef;
        public float weight = 1f;
        /// <summary>Cells cleared around the pit; 0 keeps the genstep's own clearSpaceSize.</summary>
        public int clearSpaceSize;
    }

    /// <summary>SARLACC_PIT_WIDEN_THE_BIG_ONES. A vanilla GenStep_ScatterThings that first rolls which size of pit this map
    /// gets (owner, 2026-10-16: "Superb though that is just a moderate one. They can get much bigger."). The roll is
    /// RSW_SarlaccPitKernel.Pick over the listed weights, smallest size first; with the "Big sarlacc pits" setting off it is
    /// always the first (moderate) size. If the rolled size finds no room, each smaller size is tried in turn, so a cramped
    /// map gets the biggest pit that fits, not none. Mapgen runs inside a seeded Rand state, so a tile always rolls the same.
    /// The scatter itself is vanilla: this only swaps thingDef and clearSpaceSize for the call and restores them after.</summary>
    public class RSW_GenStep_SarlaccPitSized : GenStep_ScatterThings
    {
        public List<RSW_SarlaccPitSize> sizes = new List<RSW_SarlaccPitSize>();

        public override void Generate(Map map, GenStepParams parms)
        {
            if (sizes.NullOrEmpty())
            {
                base.Generate(map, parms);
                return;
            }
            var weights = new List<float>(sizes.Count);
            foreach (RSW_SarlaccPitSize s in sizes) weights.Add(s?.thingDef == null ? 0f : s.weight);
            int picked = RSW_SarlaccPitKernel.Pick(weights, Rand.Value, RSW_BeastMechanicsSettings.bigSarlaccPitsEnabled);
            ThingDef ownDef = thingDef;
            int ownClear = clearSpaceSize;
            try
            {
                foreach (int i in RSW_SarlaccPitKernel.TryOrder(picked, sizes.Count))
                {
                    RSW_SarlaccPitSize s = sizes[i];
                    if (s?.thingDef == null) continue;
                    thingDef = s.thingDef;
                    clearSpaceSize = s.clearSpaceSize > 0 ? s.clearSpaceSize : ownClear;
                    int before = map.listerThings.ThingsOfDef(thingDef).Count;
                    base.Generate(map, parms);
                    if (map.listerThings.ThingsOfDef(thingDef).Count > before) return;
                }
            }
            finally
            {
                thingDef = ownDef;
                clearSpaceSize = ownClear;
            }
        }
    }
}
