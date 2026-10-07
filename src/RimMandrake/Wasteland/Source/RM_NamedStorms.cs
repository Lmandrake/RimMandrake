using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.Wasteland
{
    // ════════════════════════════════════════════════════════════════════
    // WASTELAND_GPT_ENRICHMENT_1 §1 — the named storms. Gives the two ruled
    // storms (RM_WastelandRadiationHalo = the DEADLIGHT HALO,
    // RM_WastelandPlasmaStorm = the CINDERWIRE STORM) an arrival: a quiet
    // warning phase with readable cues, then a hand-off to the existing storm
    // mechanics (RM_MapComponent_WastelandStorms' dose and fall, plus the
    // Cinderwire's EMP and lightning, which live here so the warning is quiet).
    //
    //   OnWeatherStart (RM_WeatherWorker_NamedStorm) -> BeginPhase.
    //   Warning: messages, accelerating instrument clicks, whine sustainer,
    //            crawling static, levitating scraps, pawn rim-light. The storm
    //            layer's dose and fall are HELD (IsHolding) until it ends.
    //   Unleashed: message, then the Cinderwire's EMP pulses and lightning.
    //
    // Not new storms: the WeatherDefs are the same two; only labels, sky and
    // this controller change. The Cinderwire stays terminator-only by being
    // ABSENT from RM_Wasteland's baseWeatherCommonalities (the terminator gate
    // itself is still an owed design call — see RM_WastelandStorms.xml).
    // ════════════════════════════════════════════════════════════════════

    /// <summary>Arrival script for a named storm, on its WeatherDef.</summary>
    public class RM_StormPhaseExtension : DefModExtension
    {
        /// <summary>Ticks of quiet warning before the storm's effects begin.</summary>
        public int warningTicks = 2500;

        /// <summary>Message on arrival (the warning's first line).</summary>
        [MustTranslate] public string warningMessage;

        /// <summary>Message when the warning ends and the storm's effects begin.</summary>
        [MustTranslate] public string unleashedMessage;

        // Instrument clicks: interval shrinks from Start to End over the warning.
        public SoundDef clickSound;
        public int clickIntervalStartTicks = 240;
        public int clickIntervalEndTicks = 20;
        /// <summary>Click interval once the storm is unleashed. 0 = silent afterwards.</summary>
        public int clickIntervalStormTicks;

        /// <summary>Sustained sound played only during the warning (the deep whine).</summary>
        public SoundDef warningSustainer;

        /// <summary>Fleck thrown on random unroofed cells during the warning (crawling static).</summary>
        public FleckDef staticFleck;
        public int staticPerSecond;

        /// <summary>Fleck lifted off loose items during the warning (levitating scraps).</summary>
        public FleckDef scrapFleck;
        public int scrapPerSecond;

        /// <summary>Rim-light on every unroofed pawn.</summary>
        public FleckDef rimFleck;
        public Color rimColor = Color.white;
        public float rimScale = 1.6f;
        public int rimIntervalTicks = 90;
        /// <summary>False: rim only during the warning. True: for the whole storm.</summary>
        public bool rimWholeStorm = true;

        // After the warning: EMP pulses and lightning, owned here so the warning is quiet.
        public float empRadius;
        public IntRange empIntervalTicks = new IntRange(900, 1800);
        public IntRange lightningStrikeIntervalTicks = IntRange.Zero;
        public IntRange lightningFlashIntervalTicks = IntRange.Zero;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (warningTicks < 0)
            {
                yield return "warningTicks must be >= 0.";
            }
            if (clickSound != null && (clickIntervalStartTicks <= 0 || clickIntervalEndTicks <= 0))
            {
                yield return "click intervals must be > 0 when clickSound is set.";
            }
            if (rimFleck != null && rimIntervalTicks <= 0)
            {
                yield return "rimIntervalTicks must be > 0 when rimFleck is set.";
            }
            if (empRadius > 0f && empIntervalTicks.min <= 0)
            {
                yield return "empIntervalTicks must be > 0 when empRadius is set.";
            }
        }
    }

    /// <summary>Tells the phase controller the moment a named storm starts.</summary>
    public class RM_WeatherWorker_NamedStorm : WeatherWorker
    {
        private readonly WeatherDef stormDef;

        public RM_WeatherWorker_NamedStorm(WeatherDef def) : base(def)
        {
            stormDef = def;
        }

        public override void OnWeatherStart(Map map)
        {
            base.OnWeatherStart(map);
            map?.GetComponent<RM_MapComponent_StormPhases>()?.BeginPhase(stormDef);
        }
    }

    /// <summary>
    /// The phase controller. Exists on every map (vanilla builds one of each
    /// MapComponent per map); does nothing unless the current weather carries
    /// <see cref="RM_StormPhaseExtension"/>. Not biome-gated: a named storm forced
    /// onto another biome still warns before it strikes.
    /// </summary>
    public class RM_MapComponent_StormPhases : MapComponent
    {
        private WeatherDef phaseWeather;
        private int phaseStartTick = -1;
        private bool unleashed;
        private int nextClickTick = -1;
        private int nextEmpTick = -1;
        private int nextStrikeTick = -1;
        private int nextFlashTick = -1;

        [Unsaved] private Sustainer whine;

        public RM_MapComponent_StormPhases(Map map) : base(map) { }

        public WeatherDef PhaseWeather => phaseWeather;
        public bool Unleashed => unleashed;
        public int PhaseStartTick => phaseStartTick;

        private static bool Enabled =>
            RM_WastelandSettings.wastelandEnabled && RM_WastelandSettings.namedStormPhasesEnabled;

        /// <summary>
        /// True while a named storm is in its warning: the storm layer holds its dose
        /// and fall. Read by <see cref="RM_MapComponent_WastelandStorms"/>.
        /// </summary>
        public bool IsHolding(WeatherDef weather)
        {
            return RM_StormKernel.IsHolding(Enabled, weather != null, State, Id(weather));
        }

        private static int Id(WeatherDef w) { return w == null ? -1 : w.index; }

        private PhaseState State
        {
            get { return new PhaseState { weather = Id(phaseWeather), startTick = phaseStartTick, unleashed = unleashed }; }
        }

        private void Apply(PhaseState s, WeatherDef cur)
        {
            phaseWeather = s.weather == -1 ? null : (s.weather == Id(cur) ? cur : phaseWeather);
            phaseStartTick = s.startTick;
            unleashed = s.unleashed;
        }

        public static RM_StormPhaseExtension ExtOf(WeatherDef w) =>
            w?.GetModExtension<RM_StormPhaseExtension>();

        public int WarningTicksFor(RM_StormPhaseExtension ext) =>
            RM_StormKernel.WarningTicks(ext.warningTicks, RM_WastelandSettings.namedStormWarningFactor);

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Defs.Look(ref phaseWeather, "phaseWeather");
            Scribe_Values.Look(ref phaseStartTick, "phaseStartTick", -1);
            Scribe_Values.Look(ref unleashed, "unleashed", false);
            Scribe_Values.Look(ref nextClickTick, "nextClickTick", -1);
            Scribe_Values.Look(ref nextEmpTick, "nextEmpTick", -1);
            Scribe_Values.Look(ref nextStrikeTick, "nextStrikeTick", -1);
            Scribe_Values.Look(ref nextFlashTick, "nextFlashTick", -1);
        }

        /// <summary>Start a storm's warning. Public so a debug action / state read can drive it.</summary>
        public void BeginPhase(WeatherDef weather)
        {
            RM_StormPhaseExtension ext = ExtOf(weather);
            PhaseState st = State;
            PhaseEvent e = RM_StormKernel.Begin(ref st, Id(weather), ext != null, Enabled,
                ext != null ? WarningTicksFor(ext) : 0, Find.TickManager.TicksGame);
            Apply(st, weather);
            OnEvents(e, ext);
        }

        /// <summary>The side effects of a phase transition (the state already moved in the kernel).</summary>
        private void OnEvents(PhaseEvent e, RM_StormPhaseExtension ext)
        {
            if ((e & PhaseEvent.Ended) != 0)
            {
                StopWhine();
                return;
            }
            if ((e & PhaseEvent.Began) != 0)
            {
                nextClickTick = phaseStartTick + ext.clickIntervalStartTicks;
                nextEmpTick = -1;
                nextStrikeTick = -1;
                nextFlashTick = -1;
                if (Enabled && !ext.warningMessage.NullOrEmpty())
                {
                    Messages.Message(ext.warningMessage, new LookTargets(map.Center, map),
                        MessageTypeDefOf.ThreatSmall, historical: true);
                }
            }
            if ((e & PhaseEvent.Unleash) != 0)
            {
                OnUnleashed(ext);
            }
        }

        private void EndPhase()
        {
            phaseWeather = null;
            phaseStartTick = -1;
            unleashed = false;
            StopWhine();
        }

        private void OnUnleashed(RM_StormPhaseExtension ext)
        {
            unleashed = true;
            StopWhine();
            int now = Find.TickManager.TicksGame;
            if (ext.empRadius > 0f)
            {
                nextEmpTick = now + RM_StormKernel.HandoffDelay(ext.empIntervalTicks.RandomInRange);
            }
            if (ext.lightningStrikeIntervalTicks.max > 0)
            {
                nextStrikeTick = now + RM_StormKernel.HandoffDelay(ext.lightningStrikeIntervalTicks.RandomInRange);
            }
            if (ext.lightningFlashIntervalTicks.max > 0)
            {
                nextFlashTick = now + RM_StormKernel.HandoffDelay(ext.lightningFlashIntervalTicks.RandomInRange);
            }
            if (Enabled && !ext.unleashedMessage.NullOrEmpty())
            {
                Messages.Message(ext.unleashedMessage, new LookTargets(map.Center, map),
                    MessageTypeDefOf.ThreatBig, historical: true);
            }
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            WeatherDef cur = map.weatherManager.curWeather;
            RM_StormPhaseExtension ext = ExtOf(cur);
            int now = Find.TickManager.TicksGame;
            PhaseState st = State;
            PhaseEvent e = RM_StormKernel.Tick(ref st, Id(cur), ext != null, Enabled,
                ext != null ? WarningTicksFor(ext) : 0, now, out float progress);
            Apply(st, cur);
            // Began covers a save made before this controller existed, or a weather set without OnWeatherStart.
            OnEvents(e, ext);
            if (ext == null)
            {
                return;
            }
            if ((e & PhaseEvent.Disabled) != 0)
            {
                StopWhine();
                return;
            }
            if ((e & PhaseEvent.Warn) != 0)
            {
                TickWarning(ext, now, progress);
            }
            if ((e & PhaseEvent.Storm) != 0)
            {
                TickStorm(ext, now);
            }

            if (ext.rimFleck != null && (ext.rimWholeStorm || !unleashed) && now % ext.rimIntervalTicks == 0)
            {
                RimPawns(ext);
            }
        }

        // ── warning ────────────────────────────────────────────────────

        private void TickWarning(RM_StormPhaseExtension ext, int now, float progress)
        {
            if (ext.clickSound != null && now >= nextClickTick)
            {
                PlayClick(ext);
                int interval = RM_StormKernel.ClickInterval(ext.clickIntervalStartTicks, ext.clickIntervalEndTicks, progress);
                nextClickTick = now + Mathf.Max(1, Mathf.RoundToInt(interval * Rand.Range(0.6f, 1.4f)));
            }
            if (ext.warningSustainer != null && map == Find.CurrentMap)
            {
                if (whine == null || whine.Ended)
                {
                    whine = ext.warningSustainer.TrySpawnSustainer(SoundInfo.OnCamera(MaintenanceType.PerTick));
                }
                whine?.Maintain();
            }
            else
            {
                StopWhine();
            }
            if (now % 30 == 0)
            {
                ThrowRandom(ext.staticFleck, ext.staticPerSecond / 2f, 0.9f, onItems: false);
                ThrowRandom(ext.scrapFleck, ext.scrapPerSecond / 2f, 0.7f, onItems: true);
            }
        }

        private void PlayClick(RM_StormPhaseExtension ext)
        {
            if (map == Find.CurrentMap)
            {
                ext.clickSound.PlayOneShotOnCamera(map);
            }
        }

        private void StopWhine()
        {
            if (whine != null && !whine.Ended)
            {
                whine.End();
            }
            whine = null;
        }

        private void ThrowRandom(FleckDef fleck, float count, float scale, bool onItems)
        {
            if (fleck == null || count <= 0f || map != Find.CurrentMap)
            {
                return;
            }
            int n = GenMath.RoundRandom(count);
            List<Thing> items = onItems ? map.listerThings.ThingsInGroup(ThingRequestGroup.HaulableEver) : null;
            for (int i = 0; i < n; i++)
            {
                Vector3 loc;
                if (onItems)
                {
                    if (items == null || items.Count == 0)
                    {
                        return;
                    }
                    Thing t = items.RandomElement();
                    if (!t.Spawned || t.Position.Roofed(map))
                    {
                        continue;
                    }
                    loc = t.DrawPos;
                }
                else
                {
                    IntVec3 c = CellFinder.RandomCell(map);
                    if (c.Roofed(map) || c.Fogged(map))
                    {
                        continue;
                    }
                    loc = c.ToVector3Shifted();
                }
                FleckCreationData data = FleckMaker.GetDataStatic(loc, map, fleck, scale * Rand.Range(0.7f, 1.2f));
                if (onItems)
                {
                    data.velocityAngle = Rand.Range(-15f, 15f); // 0 = straight up the screen
                    data.velocitySpeed = Rand.Range(0.15f, 0.35f);
                    data.rotationRate = Rand.Range(-40f, 40f);
                }
                map.flecks.CreateFleck(data);
            }
        }

        private void RimPawns(RM_StormPhaseExtension ext)
        {
            if (map != Find.CurrentMap)
            {
                return;
            }
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.Position.Roofed(map) || p.Position.Fogged(map))
                {
                    continue;
                }
                FleckCreationData data = FleckMaker.GetDataStatic(p.DrawPos, map, ext.rimFleck, ext.rimScale * p.BodySize.Clamp01OrMin(0.6f));
                data.instanceColor = ext.rimColor;
                map.flecks.CreateFleck(data);
            }
        }

        // ── storm (after the hand-off) ─────────────────────────────────

        private void TickStorm(RM_StormPhaseExtension ext, int now)
        {
            if (ext.clickSound != null && ext.clickIntervalStormTicks > 0 && now >= nextClickTick)
            {
                PlayClick(ext);
                nextClickTick = now + Mathf.RoundToInt(ext.clickIntervalStormTicks * Rand.Range(0.6f, 1.4f));
            }
            if (nextEmpTick >= 0 && now >= nextEmpTick)
            {
                if (RM_WastelandSettings.cinderwireEmpEnabled)
                {
                    DoEmpPulse(ext);
                }
                nextEmpTick = now + ext.empIntervalTicks.RandomInRange;
            }
            if (nextStrikeTick >= 0 && now >= nextStrikeTick)
            {
                map.weatherManager.eventHandler.AddEvent(new WeatherEvent_LightningStrike(map));
                nextStrikeTick = now + ext.lightningStrikeIntervalTicks.RandomInRange;
            }
            if (nextFlashTick >= 0 && now >= nextFlashTick)
            {
                map.weatherManager.eventHandler.AddEvent(new WeatherEvent_LightningFlash(map));
                nextFlashTick = now + ext.lightningFlashIntervalTicks.RandomInRange;
            }
        }

        /// <summary>One EMP pulse on a random unroofed cell. Public for debug/state reads.</summary>
        public bool DoEmpPulse(RM_StormPhaseExtension ext)
        {
            for (int attempt = 0; attempt < 20; attempt++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                if (c.Roofed(map))
                {
                    continue;
                }
                GenExplosion.DoExplosion(c, map, ext.empRadius, DamageDefOf.EMP, null);
                return true;
            }
            return false;
        }
    }

    internal static class RM_StormFloatExt
    {
        public static float Clamp01OrMin(this float v, float min) => Mathf.Max(min, Mathf.Min(1.5f, v));
    }
}
