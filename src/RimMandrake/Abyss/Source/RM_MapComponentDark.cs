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
        public const string DarkWeather = "RM_AbyssDark";
        public const string UnveilWeather = "RM_AbyssUnveiling";
        public const string StormWeather = "RM_AbyssWitchfire";

        // Effective-temperature band over which the Dark thins: opaque at/below ClearStart, fully clear at/above ClearFull.
        private const float ClearStart = 8f;
        private const float ClearFull = 14f;
        private const float PocketAmplitude = 10f;   // deg C swing of the outdoor pocket noise
        private const float PocketScale = 0.07f;     // cells -> noise units
        private const float PocketDrift = 0.00005f;  // noise units per tick

        private const int PawnInterval = 150;
        private const int LampInterval = 250;
        private const float LampFloor = 0.3f;        // a lamp never shrinks below this share of its radius at full Dark
        private const float MurkStep = 0.05f;

        private const int RumbleMin = 3000, RumbleMax = 9000;
        private const int FlashDelayMin = 180, FlashDelayMax = 300;
        private const float SummChance = 0.2f;

        private int nextRumbleTick = -1;
        private int pendingFlashTick = -1;
        private bool pendingSummCome;

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

        public static bool IsUnveiling(Map map) { return WeatherName(map) == UnveilWeather; }

        /// <summary>The Dark is physically present (the Dark itself, or a Witchfire storm, which keeps it).</summary>
        public static bool DarkPresent(Map map)
        {
            string w = WeatherName(map);
            return w == DarkWeather || w == StormWeather;
        }

        /// <summary>Grain falling: 0 = none, 1 = the Dark / a storm, 2 = the Unveiling (the Dark collapsing to grain).</summary>
        public static float GrainMultiplier(Map map)
        {
            string w = WeatherName(map);
            if (w == UnveilWeather) return 2f;
            return (w == DarkWeather || w == StormWeather) ? 1f : 0f;
        }

        /// <summary>0 = clear air, 1 = fully opaque, at a cell, before the strength slider.</summary>
        public static float DarknessAt(Map map, IntVec3 c)
        {
            if (!DarkPresent(map) || !c.InBounds(map)) return 0f;
            float t = c.GetTemperature(map);
            if (!c.Roofed(map))
            {
                float n = Mathf.PerlinNoise(c.x * PocketScale + map.uniqueID * 17.31f,
                                            c.z * PocketScale + Find.TickManager.TicksGame * PocketDrift);
                t += (n - 0.5f) * 2f * PocketAmplitude;
            }
            // ABYSS_FOLD_LAMP_BUILD_1: a lit fold-lamp's lane of warm air holds the Dark open toward its throat.
            // ABYSS_FREE_CRYPTID_1: and, very rarely, a clear pocket opens over nothing at all.
            return DarknessForTemperature(t) * (1f - RM_MapComponent_FoldLanes.ClearanceAt(map, c))
                * (1f - RM_MapComponent_AbyssCryptid.PhantomClearanceAt(map, c));
        }

        /// <summary>0..1 darkness of air at an effective temperature (no lane, no slider).</summary>
        public static float DarknessForTemperature(float t)
        {
            return 1f - Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(ClearStart, ClearFull, t));
        }

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
                float sev = on ? DarknessAt(map, p.Position) * RM_AbyssSettings.darkStrength : 0f;
                if (sev < 0.03f)
                {
                    if (h != null) p.health.RemoveHediff(h);
                    continue;
                }
                if (h == null) h = p.health.AddHediff(def);
                if (h != null && Mathf.Abs(h.Severity - sev) >= MurkStep) h.Severity = sev;
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
                if (g == null || !g.Glows) continue;
                if (krizzak != null && krizzak.IsDimmed(g)) continue;   // a krizzak has this one; do not fight it
                float baseline = g.Props.glowRadius;
                float f = on ? 1f - (1f - LampFloor) * Mathf.Clamp01(DarknessAt(map, bld[i].Position) * RM_AbyssSettings.darkStrength) : 1f;
                float target = baseline * f;
                if (Mathf.Abs(g.GlowRadius - target) < 0.15f) continue;
                if (f < 0.999f) shrunk[g] = baseline;
                g.GlowRadius = target;
                g.ForceRegister(map);
            }
            // restore any lamp we shrank that is no longer in the Dark (or whose Dark is off)
            if (shrunk.Count == 0) return;
            scratch.Clear();
            scratch.AddRange(shrunk.Keys);
            for (int i = 0; i < scratch.Count; i++)
            {
                CompGlower g = scratch[i];
                if (g.parent == null || !g.parent.Spawned) { shrunk.Remove(g); continue; }
                if (!on && g.GlowRadius < shrunk[g] - 0.01f && (krizzak == null || !krizzak.IsDimmed(g)))
                {
                    g.GlowRadius = shrunk[g];
                    g.ForceRegister(map);
                    shrunk.Remove(g);
                }
            }
        }

        // ── the storm call ───────────────────────────────────────────

        private void StormCallTick(int now)
        {
            bool storm = WeatherName(map) == StormWeather;
            if (!storm || !RM_AbyssSettings.stormCallEnabled)
            {
                nextRumbleTick = -1; pendingFlashTick = -1; pendingSummCome = false;
                return;
            }
            if (nextRumbleTick < 0) nextRumbleTick = now + Rand.RangeInclusive(RumbleMin, RumbleMax);

            if (pendingFlashTick >= 0 && now >= pendingFlashTick)
            {
                // the flash that follows the call: light with NO lightning behind it
                map.weatherManager.eventHandler.AddEvent(new WeatherEvent_LightningFlash(map));
                if (pendingSummCome) TrySpawnSumm();
                pendingFlashTick = -1; pendingSummCome = false;
            }
            else if (pendingFlashTick < 0 && now >= nextRumbleTick)
            {
                SoundDef rumble = DefDatabase<SoundDef>.GetNamedSilentFail("Thunder_OffMap");
                if (rumble != null) rumble.PlayOneShotOnCamera(map);
                pendingFlashTick = now + Rand.RangeInclusive(FlashDelayMin, FlashDelayMax);
                pendingSummCome = Rand.Chance(Mathf.Clamp01(SummChance * RM_AbyssSettings.darkStrength));
                nextRumbleTick = now + Rand.RangeInclusive(RumbleMin, RumbleMax);
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
            Scribe_Values.Look(ref nextRumbleTick, "nextRumbleTick", -1);
            Scribe_Values.Look(ref pendingFlashTick, "pendingFlashTick", -1);
            Scribe_Values.Look(ref pendingSummCome, "pendingSummCome", false);
        }
    }
}
