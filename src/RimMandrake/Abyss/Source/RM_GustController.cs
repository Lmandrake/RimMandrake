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
        private const int SampleInterval = 10;
        private const float StartRatio = 1.30f;   // speed / average that opens a gust
        private const float EndRatio = 1.10f;     // speed / average that ends it
        private const int MinGustTicks = 120;
        private const int MaxGustTicks = 900;
        private const int CooldownTicks = 600;

        private float average = -1f;
        private int gustStartTick = -99999;
        private int gustEndTick = -99999;
        private int gustCount;

        public RM_MapComponent_GustController(Map map) : base(map) { }

        public bool IsGust => Find.TickManager.TicksGame < gustEndTick;
        public int GustStartTick => gustStartTick;
        public int GustCount => gustCount;

        /// <summary>Open a gust now (e.g. a storm call). Ignores the cooldown.</summary>
        public void ForceGust(int ticks)
        {
            int now = Find.TickManager.TicksGame;
            if (!IsGust)
            {
                gustStartTick = now;
                gustCount++;
            }
            gustEndTick = Math.Max(gustEndTick, now + Mathf.Max(MinGustTicks, ticks));
        }

        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (now % SampleInterval != 0 || map.windManager == null) return;
            float speed = map.windManager.WindSpeed;
            if (average < 0f) average = speed;
            average += (speed - average) * 0.01f;
            float baseline = Mathf.Max(0.05f, average);

            if (IsGust)
            {
                bool minDone = now - gustStartTick >= MinGustTicks;
                if (now - gustStartTick >= MaxGustTicks || (minDone && speed <= baseline * EndRatio))
                {
                    gustEndTick = now;
                }
            }
            else if (now - gustEndTick >= CooldownTicks && speed >= baseline * StartRatio)
            {
                gustStartTick = now;
                gustEndTick = now + MaxGustTicks;   // trimmed by the end test above
                gustCount++;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref average, "average", -1f);
            Scribe_Values.Look(ref gustStartTick, "gustStartTick", -99999);
            Scribe_Values.Look(ref gustEndTick, "gustEndTick", -99999);
            Scribe_Values.Look(ref gustCount, "gustCount", 0);
        }
    }
}
