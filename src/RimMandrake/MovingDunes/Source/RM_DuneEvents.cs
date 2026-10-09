using System;
using Verse;

namespace RimMandrake.MovingDunes
{
    /// <summary>DUNE_MOVED_EVENT_1: the one place other mods learn "this sand actually moved". Raised from the kernel's
    /// DepthMoved, so a move the dune engine declined or clamped back raises nothing. Listeners (the Stillsand's singing
    /// dunes and quake warning) subscribe by reflection to <c>SandMoved</c> with an Action&lt;Map, IntVec3, float, float&gt;
    /// (before, after) and need no reference to this assembly. Gated by MovingDunesSettings.announceSandMoved.</summary>
    [StaticConstructorOnStartup]
    public static class RM_DuneEvents
    {
        public static event Action<Map, IntVec3, float, float> SandMoved;

        /// <summary>Session counter for the bridge. Never saved.</summary>
        public static int Raised;

        static RM_DuneEvents()
        {
            RM_DuneKernel.DepthMoved += OnDepthMoved;
        }

        private static void OnDepthMoved(IDuneField f, int x, int z, float before, float after)
        {
            if (!MovingDunesSettings.announceSandMoved) return;
            Action<Map, IntVec3, float, float> handlers = SandMoved;
            if (handlers == null) return;
            MapDuneField field = f as MapDuneField;
            if (field == null) return;
            Raised++;
            handlers(field.Map, new IntVec3(x, 0, z), before, after);
        }
    }
}
