using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.Abyss
{
    // ════════════════════════════════════════════════════════════════════
    // ABYSS_SOUNDSCAPE_BUILD_1 -- half 1, the gust soundscape (owner card turn 3, Q3 "both").
    //
    // Silence is the bed: RM_AbyssDark carries no ambient wind (RM_AbyssStartup puts the vanilla fog wind
    // back when the setting is off). Sound is the EVENT:
    //  - each gust (RM_MapComponent_GustController's GustCount ticks up) lands as an impact on the camera:
    //    RM_AbyssGustImpact, then 45-90 ticks later the gharrek gill-fans open in a rustle at up to three
    //    gharreks on the map (RM_AbyssGillRustle);
    //  - while grain falls (the Dark, a storm, the Unveiling x2) a grain tick sounds now and then on an unroofed
    //    building or rock near the camera (RM_AbyssGrainTick);
    //  - a lamp a krizzak is eating clatters (RM_AbyssLampClatter), called from RM_MapComponent_KrizzakDimming.
    // Only the map on screen plays anything. Nothing is saved but the last gust count seen.
    //
    // Half 2 (the Dark swallows sound), spike result: WORKS for our own sounds without Harmony -- every Sample
    // owns its AudioSource and vanilla's SoundParamTarget_PropertyLowPass adds an AudioLowPassFilter to that
    // source, driven by any SoundParamSource subclass named in XML. SoundParamSource_RM_DarkMuffle below
    // feeds the Dark's density at the camera into each soundscape def's low-pass cutoff (muffled in the Dark,
    // sharp in a warm pocket). Muffling EVERY game sound needs a Harmony hook on sample creation: filed as its
    // own item, not built here (this assembly carries no Harmony by design).
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_AbyssSoundscape : MapComponent
    {
        private const int RustleDelayMin = 45, RustleDelayMax = 90;
        private const int GrainTickMin = 240, GrainTickMax = 900;
        private const int GrainSearchRadius = 14;
        private const int MaxRustles = 3;

        private int lastGustCount = -1;
        private int pendingRustleTick = -1;
        private int nextGrainTick = -1;

        public int ImpactsPlayed { get; private set; }
        public int RustlesPlayed { get; private set; }
        public int GrainTicksPlayed { get; private set; }

        public RM_MapComponent_AbyssSoundscape(Map map) : base(map) { }

        private bool OnScreen => Find.CurrentMap == map && !Find.TickManager.Paused;

        public override void MapComponentTick()
        {
            if (map.Biome == null || map.Biome.defName != "RM_Abyss" || !RM_AbyssSettings.gustSoundscapeEnabled) return;
            int now = Find.TickManager.TicksGame;
            var gust = map.GetComponent<RM_MapComponent_GustController>();
            if (gust != null)
            {
                if (lastGustCount < 0) lastGustCount = gust.GustCount;
                if (gust.GustCount != lastGustCount)
                {
                    lastGustCount = gust.GustCount;
                    if (OnScreen) PlayImpact();
                    pendingRustleTick = now + Rand.RangeInclusive(RustleDelayMin, RustleDelayMax);
                }
            }
            if (pendingRustleTick >= 0 && now >= pendingRustleTick)
            {
                pendingRustleTick = -1;
                if (OnScreen) PlayRustles();
            }
            if (now % 60 == 0) GrainTick(now);
        }

        public void PlayImpact()
        {
            SoundDef s = DefDatabase<SoundDef>.GetNamedSilentFail("RM_AbyssGustImpact");
            if (s == null) return;
            s.PlayOneShotOnCamera(map);
            ImpactsPlayed++;
        }

        public void PlayRustles()
        {
            SoundDef s = DefDatabase<SoundDef>.GetNamedSilentFail("RM_AbyssGillRustle");
            ThingDef gharrek = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Gharrek");
            if (s == null || gharrek == null) return;
            List<Thing> all = map.listerThings.ThingsOfDef(gharrek);
            int played = 0;
            for (int i = 0; i < all.Count && played < MaxRustles; i++)
            {
                if (all[i] is Pawn p && !p.Dead)
                {
                    s.PlayOneShot(new TargetInfo(p.Position, map));
                    played++;
                }
            }
            RustlesPlayed += played;
        }

        private void GrainTick(int now)
        {
            if (RM_MapComponent_Dark.GrainMultiplier(map) <= 0f || RM_AbyssSettings.etchfallStrength <= 0.001f)
            {
                nextGrainTick = -1;
                return;
            }
            if (nextGrainTick < 0)
            {
                nextGrainTick = now + Rand.RangeInclusive(GrainTickMin, GrainTickMax);
                return;
            }
            if (now < nextGrainTick) return;
            nextGrainTick = now + Mathf.RoundToInt(Rand.RangeInclusive(GrainTickMin, GrainTickMax) / RM_MapComponent_Dark.GrainMultiplier(map));
            if (!OnScreen) return;
            SoundDef s = DefDatabase<SoundDef>.GetNamedSilentFail("RM_AbyssGrainTick");
            if (s == null) return;
            IntVec3 centre = Find.CameraDriver.MapPosition;
            for (int tries = 0; tries < 8; tries++)
            {
                IntVec3 c = centre + GenRadial.RadialPattern[Rand.Range(0, GenRadial.NumCellsInRadius(GrainSearchRadius))];
                if (!c.InBounds(map) || c.Roofed(map) || c.GetEdifice(map) == null) continue;
                s.PlayOneShot(new TargetInfo(c, map));
                GrainTicksPlayed++;
                return;
            }
        }

        /// <summary>A lamp a krizzak is eating: the soft clatter on its glass. Building lamps only.</summary>
        public static void LampClatter(Map map, Thing lamp)
        {
            if (map == null || lamp == null || !RM_AbyssSettings.gustSoundscapeEnabled || Find.CurrentMap != map) return;
            if (lamp.def.category != ThingCategory.Building) return;
            SoundDef s = DefDatabase<SoundDef>.GetNamedSilentFail("RM_AbyssLampClatter");
            s?.PlayOneShot(new TargetInfo(lamp.Position, map));
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref lastGustCount, "lastGustCount", -1);
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // ABYSS_SOUNDSCAPE_BUILD_1 half 2 (own sounds): 0 = clear air at the listener, 1 = full Dark.
    // The listener is the camera: the Dark's density at the camera's map cell, times the strength slider.
    // Off (setting) or off the Abyss = 0, so the curve leaves the sound untouched.
    // ════════════════════════════════════════════════════════════════════
    public class SoundParamSource_RM_DarkMuffle : SoundParamSource
    {
        public override string Label => "Abyss Dark density at the listener";

        public override float ValueFor(Sample samp)
        {
            if (!RM_AbyssSettings.darkMuffleEnabled || !RM_AbyssSettings.darkEnabled) return 0f;
            Map map = Find.CurrentMap;
            if (map == null || map.Biome == null || map.Biome.defName != "RM_Abyss") return 0f;
            return Mathf.Clamp01(RM_MapComponent_Dark.DarknessAt(map, Find.CameraDriver.MapPosition) * RM_AbyssSettings.darkStrength);
        }
    }

    public static class RM_AbyssSoundscapeProof
    {
        /// <summary>Force a gust now and report the counters plus the muffle value at the camera.</summary>
        public static string ProofGust()
        {
            Map map = Find.CurrentMap;
            if (map == null) return "no map";
            var gust = map.GetComponent<RM_MapComponent_GustController>();
            var sc = map.GetComponent<RM_MapComponent_AbyssSoundscape>();
            if (gust == null || sc == null) return "components missing";
            gust.ForceGust(300);
            return "gustCount=" + gust.GustCount + " impacts=" + sc.ImpactsPlayed + " rustles=" + sc.RustlesPlayed
                + " grainTicks=" + sc.GrainTicksPlayed
                + " muffle=" + new SoundParamSource_RM_DarkMuffle().ValueFor(null).ToString("0.00");
        }
    }
}
