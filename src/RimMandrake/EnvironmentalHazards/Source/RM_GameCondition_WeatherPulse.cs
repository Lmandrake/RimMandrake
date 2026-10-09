using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FORGE_MECHANICS_1 F1 build pass. See WeatherPulseExtension for the
    // XML surface and the "why a new class instead of reusing
    // GameCondition_EnvironmentalWeather unmodified" note
    // (forge_kit_spec.md F1: EnvironmentalWeather forces ONE weather and
    // damages continuously; the Forge's identity is the pulse between two
    // weathers with damage gated to the burst only).
    //
    // ForcedWeather() override point: GameCondition.ForcedWeather()
    // (Source/RimWorld/GameCondition.cs:345, verified this spec) is
    // vanilla's own per-tick hook for exactly this — the weather system
    // calls it every weather-decision tick, but WeatherDecider.WeatherDeciderTick
    // only moves to a newly forced weather once the current one is older
    // than 4000 ticks (or the forced def's Anomaly transitionTicksOverride),
    // which is longer than a whole 20-40 minute burst. So every change of
    // what this method returns is followed by SnapForcedWeather(), which runs
    // vanilla's own StartNextWeather at once (LIVE 2026-10-04: TheForge's
    // cycle_walk read 'Clear' 130 ticks into a forced Rain burst).
    //
    // 1 in-game hour = 2500 ticks (60000 ticks/day / 24), the same
    // conversion RM_CompScriptedDieOff already uses.
    public class RM_GameCondition_WeatherPulse : GameCondition
    {
        private const float TicksPerHour = 2500f;

        private bool inBurst;
        private int burstWeatherEndTick;
        private int ticksUntilScaldDamage;

        // FORGE_CYCLE_MECHANICS_1: read-only state + seams for a subclass
        // that drives the pulse as part of a longer cycle (TheForge's
        // RM_GameCondition_ForgeCycle). Default behaviour is unchanged: a
        // plain RM_GameCondition_WeatherPulse rolls its MTB bursts exactly
        // as before.
        public bool InBurst => inBurst;

        public int BurstEndTick => burstWeatherEndTick;

        protected WeatherPulseExtension PulseExtension => ExtensionInt;

        /// <summary>Whether the random MTB burst roll may run this tick.
        /// A cycle subclass narrows it to its own quiet phase.</summary>
        protected virtual bool AllowRandomBurstNow()
        {
            return true;
        }

        /// <summary>Weather to force while NOT bursting. Null keeps the
        /// extension's baseWeather.</summary>
        protected virtual WeatherDef NonBurstWeatherOverride()
        {
            return null;
        }

        /// <summary>Move each affected map to its forced weather now, through
        /// vanilla's own StartNextWeather (which picks ForcedWeather and sets a
        /// fresh duration), instead of waiting out WeatherDeciderTick's
        /// 4000-tick age gate. No-op when nothing is forced or it already
        /// shows.</summary>
        protected void SnapForcedWeather()
        {
            List<Map> maps = AffectedMaps;
            for (int i = 0; i < maps.Count; i++)
            {
                Map m = maps[i];
                if (m == null || m.weatherDecider == null || m.weatherManager == null)
                {
                    continue;
                }
                WeatherDef want = m.weatherDecider.ForcedWeather;
                if (want != null && m.weatherManager.curWeather != want)
                {
                    m.weatherDecider.StartNextWeather();
                }
            }
        }

        /// <summary>Start (or restart) a burst of an exact length instead
        /// of a rolled one. Runs the same flash-window start as a rolled
        /// burst.</summary>
        public void ForceBurst(int durationTicks)
        {
            WeatherPulseExtension ext = ExtensionInt;
            if (ext == null || ext.burstWeather == null)
            {
                return;
            }
            StartBurst(ext, durationTicks);
        }

        private WeatherPulseExtension ExtensionInt
        {
            get { return def != null ? def.GetModExtension<WeatherPulseExtension>() : null; }
        }

        public override void Init()
        {
            base.Init();

            WeatherPulseExtension ext = ExtensionInt;
            if (ext == null)
            {
                Log.WarningOnce(
                    "[RM EnvironmentalHazards] GameConditionDef " + (def != null ? def.defName : "(null)")
                    + " uses RM_GameCondition_WeatherPulse but carries no WeatherPulseExtension; it will run with no effects.",
                    def != null ? def.shortHash ^ 0x4F31 : 0x4F31);
                return;
            }

            ticksUntilScaldDamage = ext.scaldDamageIntervalTicks;
        }

        public override void GameConditionTick()
        {
            base.GameConditionTick();

            WeatherPulseExtension ext = ExtensionInt;
            if (ext == null || ext.burstWeather == null)
            {
                return;
            }

            if (!RM_MechanicGates.Enabled(def))
            {
                // Owning mod's settings switched this condition off (e.g. the
                // Scald's S1 steam sky): no bursts, no damage, and
                // ForcedWeather() below stops forcing, so the map's own
                // weather decider takes over. An in-flight burst is dropped.
                if (inBurst)
                {
                    EndBurst();
                }
                return;
            }

            if (inBurst)
            {
                if (Find.TickManager.TicksGame >= burstWeatherEndTick)
                {
                    EndBurst();
                    return;
                }

                DoScaldDamageTick(ext);
                return;
            }

            if (!RM_EnvironmentalHazardsSettings.weatherPulseEnabled)
            {
                return; // mod option: never start a new burst while off (see StartBurst's own note)
            }

            if (AllowRandomBurstNow() && Rand.MTBEventOccurs(ext.burstMtbHours, TicksPerHour, 1f))
            {
                StartBurst(ext, -1);
            }
        }

        private void StartBurst(WeatherPulseExtension ext, int forcedTicks)
        {
            inBurst = true;
            int nowTick = Find.TickManager.TicksGame;
            int burstTicks;
            if (forcedTicks > 0)
            {
                burstTicks = forcedTicks;
            }
            else
            {
                int burstMinutes = ext.burstDurationMinutesRange.RandomInRange;
                burstTicks = Mathf.Max(1, Mathf.RoundToInt(burstMinutes * (TicksPerHour / 60f)));
            }
            burstWeatherEndTick = nowTick + burstTicks;
            ticksUntilScaldDamage = ext.scaldDamageIntervalTicks;

            SnapForcedWeather();

            int flashWindowTicks = Mathf.Max(1, Mathf.RoundToInt(ext.flashWindowHoursAfterBurstStart * TicksPerHour));
            List<Map> maps = AffectedMaps;
            for (int i = 0; i < maps.Count; i++)
            {
                RM_MapComponent_FlashCycle flashCycle = maps[i].GetComponent<RM_MapComponent_FlashCycle>();
                if (flashCycle != null)
                {
                    flashCycle.StartWindow(nowTick, flashWindowTicks);
                }
            }
        }

        private void EndBurst()
        {
            inBurst = false;
            burstWeatherEndTick = 0;
            SnapForcedWeather();
            // The flash window deliberately keeps running past burst end
            // (it was set to burst-start + flashWindowHoursAfterBurstStart,
            // not to the burst weather's own, shorter end) —
            // RUT_Plant_FlashFlora reads RM_MapComponent_FlashCycle
            // directly and needs nothing further from this condition once
            // the burst weather itself is over.
        }

        // Reparameterized copy of GameCondition_EnvironmentalWeather.
        // DoPawnEffects' own damage half (same HazardTargeting gate, same
        // onlyUnroofed check, same settings-driven global multiplier — see
        // that class), gated additionally to "while a burst is running",
        // which the donor shape has no concept of and should not gain (it
        // is shared by every other kit that references
        // EnvironmentalWeatherExtension).
        private void DoScaldDamageTick(WeatherPulseExtension ext)
        {
            if (ext.scaldDamageDef == null || ext.scaldDamageAmount <= 0f)
            {
                return;
            }

            if (!RM_EnvironmentalHazardsSettings.environmentalDamageEnabled)
            {
                return; // mod option: shared "environmental weather damage" flag (see EnvironmentalWeatherExtension)
            }

            if (--ticksUntilScaldDamage > 0)
            {
                return;
            }

            ticksUntilScaldDamage = ext.scaldDamageIntervalTicks;

            List<Map> maps = AffectedMaps;
            for (int i = 0; i < maps.Count; i++)
            {
                DoScaldDamageOnMap(maps[i], ext);
            }
        }

        // Public so a quicktest can force one deterministic application
        // without waiting out an MTB roll and the damage interval — same
        // reasoning GameCondition_EnvironmentalWeather.DoPawnEffects gives
        // for being public.
        public void DoScaldDamageOnMap(Map map, WeatherPulseExtension ext)
        {
            if (map == null || ext == null)
            {
                return;
            }

            // Snapshot: damage can kill, and a kill mutates AllPawnsSpawned.
            List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
            float mult = Mathf.Max(0f, RM_EnvironmentalHazardsSettings.hazardDamageMultiplier);

            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn pawn = pawns[i];

                if (!HazardTargeting.Affects(pawn, ext.affects, ext.immuneThingDefs, ext.immunePawnKinds, ext.nativeTag))
                {
                    continue;
                }

                if (ext.onlyUnroofed && pawn.Position.Roofed(map))
                {
                    continue;
                }

                // FORGE_MECHANICS_1 F3: "scald bursts ... do not touch
                // drifters — they live in the steam." A comp flag this
                // method already has everything it needs to read, per this
                // build pass's own brief — not a fork of the damage shape,
                // just one more exemption alongside onlyUnroofed/affects
                // above. RM_CompVaporDrifter.Props.groundHazardImmune
                // defaults true but stays per-kind configurable.
                RM_CompVaporDrifter drifter = pawn.TryGetComp<RM_CompVaporDrifter>();
                if (drifter != null && drifter.Props.groundHazardImmune)
                {
                    continue;
                }

                pawn.TakeDamage(new DamageInfo(ext.scaldDamageDef, ext.scaldDamageAmount * mult, ext.armorPenetration, -1f));
            }
        }

        public override WeatherDef ForcedWeather()
        {
            WeatherPulseExtension ext = ExtensionInt;
            if (ext == null || !RM_MechanicGates.Enabled(def))
            {
                return null;
            }
            if (inBurst && ext.burstWeather != null)
            {
                return ext.burstWeather;
            }
            return NonBurstWeatherOverride() ?? ext.baseWeather;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref inBurst, "inBurst", false);
            Scribe_Values.Look(ref burstWeatherEndTick, "burstWeatherEndTick", 0);
            Scribe_Values.Look(ref ticksUntilScaldDamage, "ticksUntilScaldDamage", 0);
        }
    }
}
