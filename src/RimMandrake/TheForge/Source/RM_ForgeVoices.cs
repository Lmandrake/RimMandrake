using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.Sound;

namespace RimMandrake.TheForge
{
    // ════════════════════════════════════════════════════════════════════
    // FORGE_GPT_ENRICHMENT_1 §3 — the four voices of the Forge.
    //
    // Owned (unsaved) by RM_GameCondition_ForgeCycle and ticked by it every
    // tick, so the voice always matches the phase the cycle is in:
    //
    //   still heat        the turbine throb (on-camera sustainer)
    //   gas wash          coughing vents: positional one-shots, starting when
    //                     the hiss letter lands in the still heat ("approach")
    //                     and running through the wash, at a steam geyser when
    //                     the map has one
    //   boiling rain      the deafening hiss (on-camera sustainer)
    //   freeze / growth   cooling basalt: ticks, and rarer glass notes, at
    //                     random crusted cells
    //   cracks / melt     the harmony drops out (no sustainer) and a deep
    //                     cracking pulse begins
    //
    // Every phase change plays one low stinger. Visual fallback: with the
    // setting on, or the game/ambient volume at zero, each phase's voice is
    // also named in a message as it starts.
    //
    // Only the map the player is looking at sounds; sustainers end the moment
    // the camera leaves the map, the toggle goes off or the cycle stops.
    // Every interval below is TUNED: chosen to read as "occasional" against
    // a 60-tick cycle step, not taken from any ruling.
    // ════════════════════════════════════════════════════════════════════
    public class RM_ForgeVoices
    {
        // TUNED: one vent cough every ~4 s of game time while the gas comes.
        private const int CoughIntervalTicks = 240;
        // TUNED: crust ticks every ~1.5 s, a glass note about one tick in five.
        private const int BasaltTickIntervalTicks = 90;
        private const float GlassSingChance = 0.2f;
        // TUNED: the cracking pulse every ~6 s, like a slow heartbeat.
        private const int CrackPulseIntervalTicks = 360;

        private Sustainer sustainer;
        private SoundDef sustainerDef;
        private ForgeCyclePhase lastPhase = (ForgeCyclePhase)(-1);

        public static bool Enabled => RM_TheForgeSettings.Active(RM_TheForgeSettings.forgeVoicesEnabled);

        public static bool VisualCuesNow
        {
            get
            {
                return RM_TheForgeSettings.forgeVoicesVisualCues
                    || Prefs.VolumeMaster <= 0.001f || Prefs.VolumeGame <= 0.001f || Prefs.VolumeAmbient <= 0.001f;
            }
        }

        public void Tick(RM_GameCondition_ForgeCycle cycle, Map map, bool hissSent)
        {
            bool active = Enabled && RM_GameCondition_ForgeCycle.CycleActive && map != null && Find.CurrentMap == map;
            if (!active)
            {
                Stop();
                // Track the phase silently, so returning to the map does not
                // play a stinger for a change that happened while away.
                lastPhase = cycle.Phase;
                return;
            }

            ForgeCyclePhase phase = cycle.Phase;
            if (phase != lastPhase)
            {
                bool first = (int)lastPhase < 0;
                lastPhase = phase;
                if (!first)
                {
                    RM_TheForgeDefOf.RM_ForgeVoice_PhaseStinger?.PlayOneShotOnCamera(map);
                    if (VisualCuesNow)
                    {
                        Messages.Message(CueText(phase), new TargetInfo(map.Center, map), MessageTypeDefOf.SilentInput, historical: false);
                    }
                }
            }

            SetSustainer(SustainerFor(phase));
            if (sustainer != null && !sustainer.Ended)
            {
                sustainer.Maintain();
            }

            int now = Find.TickManager.TicksGame;
            switch (phase)
            {
                case ForgeCyclePhase.StillHeat:
                    if (hissSent && now % CoughIntervalTicks == 0)
                    {
                        Cough(map);
                    }
                    break;
                case ForgeCyclePhase.GasWash:
                    if (now % CoughIntervalTicks == 0)
                    {
                        Cough(map);
                    }
                    break;
                case ForgeCyclePhase.Freeze:
                case ForgeCyclePhase.Growth:
                    if (now % BasaltTickIntervalTicks == 0)
                    {
                        BasaltTick(cycle, map);
                    }
                    break;
                case ForgeCyclePhase.Cracks:
                case ForgeCyclePhase.Melt:
                    if (now % CrackPulseIntervalTicks == 0)
                    {
                        RM_TheForgeDefOf.RM_ForgeVoice_CrackPulse?.PlayOneShotOnCamera(map);
                    }
                    break;
            }
        }

        public void Stop()
        {
            if (sustainer != null && !sustainer.Ended)
            {
                sustainer.End();
            }
            sustainer = null;
            sustainerDef = null;
        }

        private static SoundDef SustainerFor(ForgeCyclePhase phase)
        {
            switch (phase)
            {
                case ForgeCyclePhase.StillHeat:
                case ForgeCyclePhase.GasWash:
                    return RM_TheForgeDefOf.RM_ForgeVoice_StillThrob;
                case ForgeCyclePhase.Rain:
                    return RM_TheForgeDefOf.RM_ForgeVoice_RainHiss;
            }
            // Freeze/growth: the crust's own small sounds carry it. Cracks
            // and melt: the harmony has dropped out.
            return null;
        }

        private void SetSustainer(SoundDef def)
        {
            if (def == sustainerDef && (def == null || (sustainer != null && !sustainer.Ended)))
            {
                return;
            }
            Stop();
            sustainerDef = def;
            if (def != null)
            {
                sustainer = def.TrySpawnSustainer(SoundInfo.OnCamera(MaintenanceType.PerTick));
            }
        }

        private static void Cough(Map map)
        {
            SoundDef cough = RM_TheForgeDefOf.RM_ForgeVoice_VentCough;
            if (cough == null)
            {
                return;
            }
            IntVec3 at = IntVec3.Invalid;
            List<Thing> geysers = map.listerThings.ThingsOfDef(ThingDefOf.SteamGeyser);
            if (geysers != null && geysers.Count > 0)
            {
                at = geysers.RandomElement().Position;
            }
            else
            {
                at = CellFinder.RandomCell(map);
            }
            cough.PlayOneShot(SoundInfo.InMap(new TargetInfo(at, map)));
            if (geysers != null && geysers.Count > 0)
            {
                FleckMaker.ThrowSmoke(at.ToVector3Shifted(), map, 1.5f);
            }
        }

        private static void BasaltTick(RM_GameCondition_ForgeCycle cycle, Map map)
        {
            if (cycle.FrozenCellCount == 0)
            {
                return;
            }
            IntVec3 at = cycle.RandomFrozenCell();
            if (!at.IsValid)
            {
                return;
            }
            SoundDef def = Rand.Chance(GlassSingChance) ? RM_TheForgeDefOf.RM_ForgeVoice_GlassSing : RM_TheForgeDefOf.RM_ForgeVoice_BasaltTick;
            def?.PlayOneShot(SoundInfo.InMap(new TargetInfo(at, map)));
        }

        public static string CueText(ForgeCyclePhase phase)
        {
            switch (phase)
            {
                case ForgeCyclePhase.StillHeat: return "The mountain settles into its still-heat throb.";
                case ForgeCyclePhase.GasWash: return "The vents are coughing: the gas wash is coming through.";
                case ForgeCyclePhase.Rain: return "A deafening hiss: the boiling rain is falling.";
                case ForgeCyclePhase.Freeze: return "The crust ticks and sings like glass as the basalt cools.";
                case ForgeCyclePhase.Growth: return "The cooling crust is still ticking.";
                case ForgeCyclePhase.Cracks: return "The harmony has dropped out. A deep cracking pulse: the crust will melt.";
                case ForgeCyclePhase.Melt: return "The cracking pulse goes on. The crust is melting.";
            }
            return RM_GameCondition_ForgeCycle.PhaseLabel(phase);
        }
    }
}
