using System;
using UnityEngine;
using Verse;

namespace RimMandrake.Abyss
{
    // ════════════════════════════════════════════════════════════════════
    // ABYSS_GHARREK_BUILD_1 -- the MINIMAL shared gust signal (report §5 item 8 "RM_GustController").
    // Other systems (the gust soundscape, ABYSS_SOUNDSCAPE_BUILD_1) read IsGust / GustStartTick;
    // anything may force one with ForceGust. A gust is an excursion of the map's wind speed above
    // its own slow average, with a stillness cooldown between gusts so "the still" exists.
    // Reads only Map.windManager.WindSpeed (vanilla). Scribed so a save mid-gust resumes.
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_GustController : MapComponent
    {
        // The gust state machine (sampling, hysteresis, cooldown, ForceGust) is RM_GustKernel in RM_AbyssStateKernel.cs, so the
        // offline fuzz drives the same code. The state is Scribed field for field below.
        private GustState gust = GustState.Fresh();

        public RM_MapComponent_GustController(Map map) : base(map) { }

        public bool IsGust => RM_GustKernel.IsGust(gust, Find.TickManager.TicksGame);
        public int GustStartTick => gust.startTick;
        public int GustCount => gust.count;

        /// <summary>A proof/debug gust of at least MinGustTicks; never shortens one already running.</summary>
        public void ForceGust(int ticks)
        {
            RM_GustKernel.Force(ref gust, Find.TickManager.TicksGame, ticks);
        }

        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (now % RM_GustKernel.SampleInterval != 0 || map.windManager == null) return;
            RM_GustKernel.Sample(ref gust, now, map.windManager.WindSpeed);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref gust.average, "average", -1f);
            Scribe_Values.Look(ref gust.startTick, "gustStartTick", -99999);
            Scribe_Values.Look(ref gust.endTick, "gustEndTick", -99999);
            Scribe_Values.Look(ref gust.count, "gustCount", 0);
        }
    }
}
