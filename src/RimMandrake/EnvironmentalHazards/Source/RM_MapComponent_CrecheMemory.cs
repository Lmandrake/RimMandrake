using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_MECHANICS_1 M6 build, §8 "everything living remembers it" —
    // the map-wide half of the despoiled-memory mechanic. RM_CompCrecheMarker
    // (one per despoiled crèche marker) registers a timed entry here rather
    // than holding the map-wide effect itself, because the spec's own text
    // is explicit this is a MAP-WIDE factor, not a per-marker one, and a
    // map can carry more than one crèche. Multiple simultaneously-active
    // despoilings stack multiplicatively (two despoiled crèches inside
    // their windows = the factor squared) — a defensible, undocumented-by-
    // the-spec but honest default for "more than one," not guessed at
    // beyond that.
    //
    // Auto-instantiated on every map by Map.FillComponents() (confirmed
    // against the live decompile — every non-abstract MapComponent
    // subclass with a Map constructor gets one per map, same as this mod's
    // own RM_MapComponent_GradientAxis), so it always exists to register
    // onto and to query, on every map in the game — harmless on any map
    // that never despoils anything (both lists stay empty, ManhunterChanceFactor
    // stays 1f).
    public class RM_MapComponent_CrecheMemory : MapComponent
    {
        private List<int> despoilExpireTicks = new List<int>();
        private List<float> despoilFactors = new List<float>();

        // Only pruned periodically (MapComponentTick), not on every read —
        // ManhunterChanceFactor() itself is called from a Harmony postfix on
        // a method the storyteller can call often, so it stays a cheap
        // forward scan over what should always be a tiny list rather than
        // mutating state (removals) on a read path.
        private const int PruneIntervalTicks = 2000;

        public RM_MapComponent_CrecheMemory(Map map)
            : base(map)
        {
        }

        public void RegisterDespoil(int durationTicks, float factor)
        {
            despoilExpireTicks.Add(Find.TickManager.TicksGame + (durationTicks < 1 ? 1 : durationTicks));
            despoilFactors.Add(factor);
        }

        // The seam RM_Patch_CrecheDespoilManhunterFactor.cs reads. 1f
        // (a true no-op) whenever nothing on this map has ever despoiled,
        // or every past despoiling has already expired.
        public float ManhunterChanceFactor()
        {
            if (despoilExpireTicks.Count == 0)
            {
                return 1f;
            }

            int now = Find.TickManager.TicksGame;
            float factor = 1f;
            for (int i = 0; i < despoilExpireTicks.Count; i++)
            {
                if (despoilExpireTicks[i] > now)
                {
                    factor *= despoilFactors[i];
                }
            }

            return factor;
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (despoilExpireTicks.Count == 0)
            {
                return;
            }

            if (Find.TickManager.TicksGame % PruneIntervalTicks != 0)
            {
                return;
            }

            int now = Find.TickManager.TicksGame;
            for (int i = despoilExpireTicks.Count - 1; i >= 0; i--)
            {
                if (despoilExpireTicks[i] <= now)
                {
                    despoilExpireTicks.RemoveAt(i);
                    despoilFactors.RemoveAt(i);
                }
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref despoilExpireTicks, "despoilExpireTicks", LookMode.Value);
            Scribe_Collections.Look(ref despoilFactors, "despoilFactors", LookMode.Value);

            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                despoilExpireTicks ??= new List<int>();
                despoilFactors ??= new List<float>();
            }
        }
    }
}
