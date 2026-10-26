// COLD_STORAGE_ENGINE_BUILD_CLIMATE_COMP: the pure decisions of the cold storage engine.
// Spec: design/RimStarWars/cold_storage_line_2026-10-26.md §4.0 (engine) and §6 (Mod Settings).
//
// Every rule the engine applies lives here, as plain static functions over plain values, so the offline
// SelfTest (Source/SelfTest) proves the same code the game runs. The comps and Harmony patches only gather
// inputs (power state, room temperature, settings) and call these.
//
// There is no rot math of our own. A chill unit reports its own temperature to vanilla CompRottable, and
// vanilla's GenTemperature.RotRateAtTemperature does the rest. Stasis and sealed goods skip the rot tick.

using System;

namespace RimMandrake.ColdStorage
{
    /// <summary>How a unit or item preserves. Chill and Stasis belong to a building's cells; Sealed belongs to an item.</summary>
    public enum StorageMode
    {
        Chill,
        Stasis,
        Sealed,
    }

    /// <summary>What a storage building actually does once the Mod Settings are applied.</summary>
    public enum EffectiveMode
    {
        /// <summary>The engine is switched off for this unit: a plain shelf.</summary>
        None,
        Chill,
        Stasis,
    }

    public static class ColdStorageKernel
    {
        /// <summary>The setpoint a stasis unit falls back to when stasis is switched off (§6: "act as Chill at -10 °C").</summary>
        public const float StasisFallbackSetpoint = -10f;

        public const float TicksPerHour = 2500f;
        public const float TicksPerDay = 60000f;

        /// <summary>vanilla CompRottable.TicksUntilRotAtTemp's "never" value.</summary>
        public const int NeverRotTicks = 72000000;

        /// <summary>The unit's behaviour after the settings. Chill off: chill units are plain shelves. Stasis off:
        /// stasis units chill at <see cref="StasisFallbackSetpoint"/>, unless chill is off as well.</summary>
        public static EffectiveMode Resolve(StorageMode mode, bool chillOn, bool stasisOn)
        {
            switch (mode)
            {
                case StorageMode.Chill:
                    return chillOn ? EffectiveMode.Chill : EffectiveMode.None;
                case StorageMode.Stasis:
                    if (stasisOn)
                    {
                        return EffectiveMode.Stasis;
                    }
                    return chillOn ? EffectiveMode.Chill : EffectiveMode.None;
                default:
                    return EffectiveMode.None;
            }
        }

        /// <summary>The setpoint the unit drives toward. A stasis unit chilling because stasis is off uses the fallback.</summary>
        public static float EffectiveSetpoint(StorageMode mode, EffectiveMode effective, float setpoint)
        {
            if (mode == StorageMode.Stasis && effective == EffectiveMode.Chill)
            {
                return StasisFallbackSetpoint;
            }
            return setpoint;
        }

        /// <summary>
        /// One step of a chill unit's own temperature.
        /// Active (powered, fuelled, or needing neither): moves toward the setpoint at <paramref name="coolPerHour"/>
        /// degrees an hour. A unit that cannot heat never pushes above the room; when the room is colder it only drifts.
        /// A passive unit (<paramref name="passiveDrop"/> &gt; 0) can get no colder than room minus that drop.
        /// Inactive: drifts back toward the room, a fraction <paramref name="driftPerHour"/> of the gap an hour,
        /// slowed by <paramref name="insulationMult"/> (2 = twice as slow).
        /// </summary>
        public static float StepUnitTemperature(float current, float setpoint, float room, bool active, bool canHeat,
            float coolPerHour, float driftPerHour, float passiveDrop, float insulationMult, float hours)
        {
            if (hours <= 0f)
            {
                return current;
            }
            float target = setpoint;
            if (passiveDrop > 0f)
            {
                target = Math.Max(setpoint, room - passiveDrop);
            }
            if (!active)
            {
                return Drift(current, room, driftPerHour, insulationMult, hours);
            }
            if (current > target)
            {
                return Math.Max(target, current - coolPerHour * hours);
            }
            if (current < target)
            {
                if (canHeat)
                {
                    return Math.Min(target, current + coolPerHour * hours);
                }
                // Cannot heat: drift toward the room, but never past the target.
                float drifted = Drift(current, room, driftPerHour, insulationMult, hours);
                return drifted > target ? target : drifted;
            }
            return current;
        }

        /// <summary>Exponential approach toward the room. Insulation multiplier divides the rate; 0 or less is treated as 1.</summary>
        public static float Drift(float current, float room, float driftPerHour, float insulationMult, float hours)
        {
            if (insulationMult <= 0f)
            {
                insulationMult = 1f;
            }
            float k = Math.Max(0f, driftPerHour) / insulationMult;
            float f = 1f - (float)Math.Exp(-k * hours);
            return current + (room - current) * f;
        }

        /// <summary>The temperature an item held by the unit reads. Only a chilling unit overrides it; a stasis unit
        /// leaves items at room temperature (they come out unfrozen); a switched-off unit changes nothing.</summary>
        public static bool TryHeldTemperature(EffectiveMode effective, float unitTemp, out float temperature)
        {
            if (effective == EffectiveMode.Chill)
            {
                temperature = unitTemp;
                return true;
            }
            temperature = 0f;
            return false;
        }

        /// <summary>Whether the rot tick of an item held by the unit is skipped: only while a stasis field holds.</summary>
        public static bool StasisHolds(EffectiveMode effective, bool active)
        {
            return effective == EffectiveMode.Stasis && active;
        }

        /// <summary>Whether a sealed item's rot is suspended. Sealed goods never rot until opened; aging is separate.</summary>
        public static bool SealSuspendsRot(bool sealedNow)
        {
            return sealedNow;
        }

        /// <summary>
        /// The fixed multiplier on an item's rot tick. Sealed: 0. In a holding stasis field: the unit's
        /// <paramref name="unitRotFactor"/> (0 for a true stasis field). Times the item's own
        /// <paramref name="itemRotFactor"/> (sand-dried x0.1, pickled x0.05; 1 for ordinary food). Never negative.
        /// </summary>
        public static float RotFactor(EffectiveMode effective, bool active, bool sealedNow, float unitRotFactor, float itemRotFactor)
        {
            if (SealSuspendsRot(sealedNow))
            {
                return 0f;
            }
            float f = Math.Max(0f, itemRotFactor);
            if (StasisHolds(effective, active))
            {
                f *= Math.Max(0f, unitRotFactor);
            }
            return f;
        }

        /// <summary>
        /// The rot progress an item gains per tick, composed exactly as the game composes it: the vanilla rate
        /// (<paramref name="vanillaRate"/>, GenTemperature.RotRateAtTemperature) at the temperature the item reads,
        /// times <see cref="RotFactor"/>. Used by the SelfTest to prove each unit type end to end.
        /// </summary>
        public static float RotPerTick(EffectiveMode effective, bool active, bool sealedNow, float unitTemp, float roomTemp,
            Func<float, float> vanillaRate, float unitRotFactor = 0f, float itemRotFactor = 1f)
        {
            float f = RotFactor(effective, active, sealedNow, unitRotFactor, itemRotFactor);
            if (f <= 0f)
            {
                return 0f;
            }
            float t = TryHeldTemperature(effective, unitTemp, out float held) ? held : roomTemp;
            return vanillaRate(t) * f;
        }

        /// <summary>vanilla's "ticks until rot" under a rot factor: unchanged at 1, never at 0, else stretched.</summary>
        public static int TicksUntilRotWithFactor(int vanillaTicks, float factor)
        {
            if (factor == 1f || vanillaTicks >= NeverRotTicks || vanillaTicks <= 0)
            {
                return factor <= 0f && vanillaTicks > 0 ? NeverRotTicks : vanillaTicks;
            }
            if (factor <= 0f)
            {
                return NeverRotTicks;
            }
            double t = vanillaTicks / (double)factor;
            return t >= NeverRotTicks ? NeverRotTicks : (int)Math.Round(t);
        }

        /// <summary>Power the unit draws (positive watts). Holding the setpoint draws <paramref name="idleFactor"/> of the full
        /// draw; a switched-off unit draws nothing.</summary>
        public static float PowerDraw(EffectiveMode effective, float basePower, float powerMult, bool atSetpoint, float idleFactor)
        {
            if (effective == EffectiveMode.None)
            {
                return 0f;
            }
            float draw = basePower * Math.Max(0f, powerMult);
            if (effective == EffectiveMode.Chill && atSetpoint)
            {
                draw *= Clamp01(idleFactor);
            }
            return draw;
        }

        /// <summary>Ticks a sealed item needs to age. Days 0 or less, or aging switched off: never (-1).</summary>
        public static int AgingTicks(float agingDays, float agingMult, bool agingOn)
        {
            if (!agingOn || agingDays <= 0f)
            {
                return -1;
            }
            double ticks = agingDays * Math.Max(0.01f, agingMult) * TicksPerDay;
            return ticks >= int.MaxValue ? int.MaxValue : (int)Math.Round(ticks);
        }

        /// <summary>Whether an item sealed at <paramref name="sealedTick"/> has aged by <paramref name="now"/>.</summary>
        public static bool HasAged(int sealedTick, int now, int agingTicks)
        {
            return agingTicks >= 0 && sealedTick >= 0 && now - sealedTick >= agingTicks;
        }

        /// <summary>The chance an aging transition ruins the goods. Multiplier 0 means never.</summary>
        public static float SealFailureChance(float baseChance, float failureMult)
        {
            return Clamp01(baseChance * Math.Max(0f, failureMult));
        }

        /// <summary>The sealing tick of a merged stack: stack-weighted, as vanilla merges rot progress.</summary>
        public static int MergedSealTick(int tickA, int countA, int tickB, int countB)
        {
            int total = countA + countB;
            if (total <= 0)
            {
                return Math.Max(tickA, tickB);
            }
            return (int)Math.Round(((double)tickA * countA + (double)tickB * countB) / total);
        }

        public static float Clamp01(float v)
        {
            return v < 0f ? 0f : (v > 1f ? 1f : v);
        }
    }
}
