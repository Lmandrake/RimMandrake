using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace RimMandrake.Abyss
{
    // ════════════════════════════════════════════════════════════════════
    // ABYSS_DARK_BUILD_1 -- the Dark as real air, the Unveiling, the storm call.
    //
    // The Dark is aurora-ash (tholin rime): where it is cold it is opaque, where an ambient-temperature pocket
    // exists the coating sublimates and the grain collapses, and the air is clear. So darkness at a cell is a
    // function of its EFFECTIVE TEMPERATURE: the cell's real temperature, plus (outdoors only) a slow drifting
    // noise offset that makes clear pockets appear and close on the open ground. A warm base is clear; a cold
    // one is blind. Nothing but a thermometer tells a clear pocket from the wall beside it.
    //
    // What it does (all scaled by RM_AbyssSettings.darkStrength; 0 = nothing):
    //  - hediff RM_Murk on humanlike pawns: sight, aim and melee suffer.
    //  - building lamps (CompGlower) shrink their radius; living glow plants are the biome's own lamps and are not touched.
    // The Unveiling (weather RM_AbyssUnveiling) removes all of it, letters the durrgak cairns, and collapses the
    // grain (etchfall runs x2). The storm call lives in a Witchfire storm: a rumble, a flash with no lightning,
    // and sometimes the Summ comes down. Nothing is stored except the storm-call timers.
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_Dark : MapComponent
    {
        // The Dark's arithmetic (temperature curve, murk, lamp shrink) is RM_DarkKernel and the storm-call timers are RM_StormKernel
        // (RM_AbyssKernel.cs / RM_AbyssStateKernel.cs), so the offline fuzz drives the same code the game runs.
        public const string DarkWeather = RM_DarkKernel.DarkWeather;
        public const string UnveilWeather = RM_DarkKernel.UnveilWeather;
        public const string StormWeather = RM_DarkKernel.StormWeather;

        private const float PocketScale = 0.07f;     // cells -> noise units
        private const float PocketDrift = 0.00005f;  // noise units per tick

        private const int PawnInterval = 150;
        private const int LampInterval = 250;

        private StormState stormCall = StormState.Fresh();   // Scribed field for field below

        private bool wasUnveiling;
        private bool initialised;
        private readonly Dictionary<CompGlower, float> shrunk = new Dictionary<CompGlower, float>();
        private readonly List<CompGlower> scratch = new List<CompGlower>();

        public RM_MapComponent_Dark(Map map) : base(map) { }

        // ── state reads ──────────────────────────────────────────────

        private static string WeatherName(Map map)
        {
            return map?.weatherManager?.curWeather?.defName;
        }

        public static bool IsUnveiling(Map map) { return RM_DarkKernel.IsUnveiling(WeatherName(map)); }

        /// <summary>The Dark is physically present (the Dark itself, or a Witchfire storm, which keeps it).</summary>
        public static bool DarkPresent(Map map) { return RM_DarkKernel.DarkPresent(WeatherName(map)); }

        /// <summary>Grain falling: 0 = none, 1 = the Dark / a storm, 2 = the Unveiling (the Dark collapsing to grain).</summary>
        public static float GrainMultiplier(Map map) { return RM_DarkKernel.GrainMultiplier(WeatherName(map)); }

        /// <summary>0 = clear air, 1 = fully opaque, at a cell, before the strength slider.</summary>
        public static float DarknessAt(Map map, IntVec3 c)
        {
            string weather = WeatherName(map);
            if (!RM_DarkKernel.DarkPresent(weather) || !c.InBounds(map)) return 0f;
            float t = c.GetTemperature(map);
            bool roofed = c.Roofed(map);
            float noise = roofed ? 0f : Mathf.PerlinNoise(c.x * PocketScale + map.uniqueID * 17.31f,
                                                          c.z * PocketScale + Find.TickManager.TicksGame * PocketDrift);
            // ABYSS_FOLD_LAMP_BUILD_1: a lit fold-lamp's lane of warm air holds the Dark open toward its throat.
            // ABYSS_FREE_CRYPTID_1: and, very rarely, a clear pocket opens over nothing at all.
            return RM_DarkKernel.DarknessAt(weather, true, t, roofed, noise,
                RM_MapComponent_FoldLanes.ClearanceAt(map, c), RM_MapComponent_AbyssCryptid.PhantomClearanceAt(map, c));
        }

        /// <summary>0..1 darkness of air at an effective temperature (no lane, no slider).</summary>
        public static float DarknessForTemperature(float t) { return RM_DarkKernel.DarknessForTemperature(t); }

        private static bool Active =>
            RM_AbyssSettings.darkEnabled && RM_AbyssSettings.darkStrength > 0.001f;

        // ── tick ─────────────────────────────────────────────────────

        public override void MapComponentTick()
        {
            if (map.Biome == null || map.Biome.defName != "RM_Abyss") return;
            int now = Find.TickManager.TicksGame;

            if (now % 60 == 0) WatchWeather();
            if (now % PawnInterval == 0)
            {
                MurkPass();
                // ABYSS_FOLD_LAMP_BUILD_1: the first colonist to stand in a warm clear pocket beside a lit heat source.
                if (Active && DarkPresent(map)) RM_HeatFoldingDiscovery.Check(map);
            }
            if (now % LampInterval == 0) LampPass();
            StormCallTick(now);
        }

        private void WatchWeather()
        {
            bool unveiling = IsUnveiling(map);
            if (unveiling && !RM_AbyssSettings.unveilingEnabled)
            {
                WeatherDef dark = DefDatabase<WeatherDef>.GetNamedSilentFail(DarkWeather);
                if (dark != null) map.weatherManager.TransitionTo(dark);
                return;
            }
            if (initialised && unveiling && !wasUnveiling) AnnounceUnveiling();
            wasUnveiling = unveiling;
            initialised = true;
        }

        private void AnnounceUnveiling()
        {
            List<Thing> all = map.listerThings.AllThings;
            var targets = new List<TargetInfo>();
            for (int i = 0; i < all.Count && targets.Count < 6; i++)
            {
                if (all[i].def.defName == "RM_DurrgakCairn") targets.Add(new TargetInfo(all[i]));
            }
            string body = "The Dark has folded away all at once. For a few hours the country stands naked and lit."
                + (targets.Count > 0 ? " Rings of shards you could not see before show plainly on the ground." : " Nothing stirs that you can see.");
            Find.LetterStack.ReceiveLetter("The Unveiling", body, LetterDefOf.PositiveEvent,
                targets.Count > 0 ? new LookTargets(targets) : null);
        }

        // ── blindness ────────────────────────────────────────────────

        private void MurkPass()
        {
            HediffDef def = DefDatabase<HediffDef>.GetNamedSilentFail("RM_Murk");
            if (def == null) return;
            bool on = Active;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.Dead || p.RaceProps == null || !p.RaceProps.Humanlike) continue;
                Hediff h = p.health.hediffSet.GetFirstHediffOfDef(def);
                float sev = RM_DarkKernel.MurkTarget(on, on ? DarknessAt(map, p.Position) : 0f, RM_AbyssSettings.darkStrength);
                RM_DarkKernel.MurkResult r = RM_DarkKernel.MurkStepFor(h != null, h != null ? h.Severity : 0f, sev, def.initialSeverity);
                if (r.removed) p.health.RemoveHediff(h);
                else
                {
                    if (r.added) h = p.health.AddHediff(def);
                    if (r.set && h != null) h.Severity = r.severity;
                }
            }
        }

        // ── lamplight ────────────────────────────────────────────────

        private void LampPass()
        {
            var krizzak = map.GetComponent<RM_MapComponent_KrizzakDimming>();
            bool on = Active;
            List<Thing> bld = map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial);
            for (int i = 0; i < bld.Count; i++)
            {
                CompGlower g = bld[i].TryGetComp<CompGlower>();
                if (g == null) continue;
                // the per-lamp rule (shrink toward the floor in the Dark, restore when it is gone, leave a krizzak's lamp alone)
                // is RM_DarkKernel.DarkLampPass; this only reads the lamp in and writes it back
                var lamp = new RM_DarkKernel.Lamp
                {
                    radius = g.GlowRadius,
                    baseline = g.Props.glowRadius,
                    kPresent = krizzak != null && krizzak.IsDimmed(g)
                };
                if (shrunk.TryGetValue(g, out float shrunkBaseline)) { lamp.shrunkKnown = true; lamp.shrunkBaseline = shrunkBaseline; }
                float darkness = on && g.Glows && !lamp.kPresent ? DarknessAt(map, bld[i].Position) : 0f;
                bool changed = RM_DarkKernel.DarkLampPass(ref lamp, g.Glows, on, darkness, RM_AbyssSettings.darkStrength);
                if (lamp.shrunkKnown) shrunk[g] = lamp.shrunkBaseline; else shrunk.Remove(g);
                if (changed)
                {
                    g.GlowRadius = lamp.radius;
                    g.ForceRegister(map);
                }
            }
            // forget lamps that left the map
            if (shrunk.Count == 0) return;
            scratch.Clear();
            scratch.AddRange(shrunk.Keys);
            for (int i = 0; i < scratch.Count; i++)
            {
                CompGlower g = scratch[i];
                if (g.parent == null || !g.parent.Spawned) shrunk.Remove(g);
            }
        }

        // ── the storm call ───────────────────────────────────────────

        private void StormCallTick(int now)
        {
            StormOut o = RM_StormKernel.Step(ref stormCall, now, WeatherName(map) == StormWeather, RM_AbyssSettings.stormCallEnabled,
                RM_AbyssSettings.darkStrength, Rand.RangeInclusive, Rand.Chance);
            if (o.flash)
            {
                // the flash that follows the call: light with NO lightning behind it
                map.weatherManager.eventHandler.AddEvent(new WeatherEvent_LightningFlash(map));
                if (o.summ) TrySpawnSumm();
            }
            if (o.rumble)
            {
                SoundDef rumble = DefDatabase<SoundDef>.GetNamedSilentFail("Thunder_OffMap");
                if (rumble != null) rumble.PlayOneShotOnCamera(map);
            }
        }

        // RM_Summ is wired by ABYSS_DONOR_BEASTS_FREED_1 and may not exist yet: absent, the call is only sound and light.
        private void TrySpawnSumm()
        {
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Summ");
            if (kind == null) return;
            if (!CellFinder.TryFindRandomEdgeCellWith(c => c.Standable(map) && !c.Fogged(map), map, CellFinder.EdgeRoadChance_Neutral, out IntVec3 cell)) return;
            Pawn summ = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null, PawnGenerationContext.NonPlayer, map.Tile));
            GenSpawn.Spawn(summ, cell, map);
            summ.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.Manhunter, "the storm call", forced: true);
            Find.LetterStack.ReceiveLetter("Something answers the thunder",
                "The roll in the storm was not thunder. A summ has come down from the crags and is crossing the land toward you.",
                LetterDefOf.ThreatBig, summ);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref stormCall.nextRumbleTick, "nextRumbleTick", -1);
            Scribe_Values.Look(ref stormCall.pendingFlashTick, "pendingFlashTick", -1);
            Scribe_Values.Look(ref stormCall.pendingSumm, "pendingSummCome", false);
        }
    }
}
