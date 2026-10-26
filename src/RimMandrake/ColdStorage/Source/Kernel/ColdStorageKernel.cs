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

        /// <summary>
        /// Add <paramref name="item"/> to a per-key registry, replacing any entry with the same key. RimWorld constructs a
        /// map's components twice on load (Map.ConstructComponents, then the saved component list), and only the newest is
        /// the one the map keeps, so the newest entry for a map must win.
        /// </summary>
        public static void ReplaceOrAdd<T>(System.Collections.Generic.List<T> list, T item, Func<T, T, bool> sameKey) where T : class
        {
            for (int i = 0; i < list.Count; i++)
            {
                if (sameKey(list[i], item))
                {
                    list[i] = item;
                    return;
                }
            }
            list.Add(item);
        }

        // ---- review follow-ups (COLDSTORAGE_*_FIX/WIRE items, 2026-10-26) ----

        /// <summary>COLDSTORAGE_SEALED_READOUT_FIX_GATE. The rot factor the READOUTS (ticks-until-rot, inspect line) may
        /// show. Only the rot-tick prefix makes a factor real; if that patch failed to apply, food rots at vanilla's rate
        /// whatever the factor says, so the readout must say vanilla's (1).</summary>
        public static float ReadoutRotFactor(float factor, bool rotTickPatched)
        {
            return rotTickPatched ? factor : 1f;
        }

        /// <summary>COLDSTORAGE_STASIS_WIRE_GRADE_FACTOR. A stasis field's strength is the share of rot it stops
        /// (owner ruling by card 2026-10-26: strength follows the quality grade, 0.2 / 0.75 / full), so the rot factor on
        /// what it holds is 1 - strength.</summary>
        public static float StasisRotFactorFromStrength(float strength)
        {
            if (float.IsNaN(strength))
            {
                return 0f;
            }
            return 1f - Clamp01(strength);
        }

        /// <summary>The rot factor a stasis unit applies: its per-instance strength (a Wrecked Machines grade, or a value
        /// set by code such as vault loot) when it has one (not NaN), else the def's stasisRotFactor.</summary>
        public static float UnitStasisRotFactor(float defRotFactor, float instanceStrength)
        {
            return float.IsNaN(instanceStrength) ? Math.Max(0f, defRotFactor) : StasisRotFactorFromStrength(instanceStrength);
        }

        /// <summary>COLDSTORAGE_DECAY_READOUT_FIX_UNDER_STASIS. Apply a holding stasis field's factor to an item's
        /// deterioration rate. A field that stops deterioration entirely also clears the reasons list, so the inspect pane
        /// does not name causes (outdoors, rain) for a rate of zero.</summary>
        public static float ApplyStasisToDeterioration(float rate, float factor, System.Collections.Generic.List<string> reasons)
        {
            float r = rate * Math.Max(0f, factor);
            if (r <= 0f && reasons != null)
            {
                reasons.Clear();
            }
            return r;
        }

        /// <summary>COLDSTORAGE_MINIFIED_FIX_STALE_TEMP. A unit that is not spawned (minified, carried, in a caravan) is
        /// not ticked, so its own temperature is stale: it overrides nothing, and held items read their real ambient.</summary>
        public static bool TryHeldTemperature(EffectiveMode effective, float unitTemp, bool unitSpawned, out float temperature)
        {
            if (!unitSpawned)
            {
                temperature = 0f;
                return false;
            }
            return TryHeldTemperature(effective, unitTemp, out temperature);
        }

        /// <summary>How much of an evaporative unit's passive drop works on a tile: 1 at or under fullBelow mm of rain a
        /// year, 0 at or over zeroAt, linear between; 0 while it rains (rainRate above 0.1).</summary>
        public static float EvaporativeDryness(float rainfallMm, float rainRate, float fullBelow, float zeroAt)
        {
            if (rainRate > 0.1f || float.IsNaN(rainfallMm))
            {
                return 0f;
            }
            if (zeroAt <= fullBelow)
            {
                return rainfallMm <= fullBelow ? 1f : 0f;
            }
            return Clamp01((zeroAt - rainfallMm) / (zeroAt - fullBelow));
        }

        /// <summary>The next detent after <paramref name="current"/> in the list's order, wrapping; the first when the
        /// current setpoint is not on a detent.</summary>
        public static float NextDetent(System.Collections.Generic.IList<float> detents, float current)
        {
            for (int i = 0; i < detents.Count; i++)
            {
                if (Math.Abs(detents[i] - current) < 0.01f)
                {
                    return detents[(i + 1) % detents.Count];
                }
            }
            return detents[0];
        }

        /// <summary>Fuel a fuel-burning unit uses over a step: the full rate while cooling, the idle fraction at the
        /// setpoint, none when inactive.</summary>
        public static float FuelUsed(float perDay, float ticks, bool active, bool atSetpoint, float idleFactor)
        {
            if (!active || ticks <= 0f || perDay <= 0f)
            {
                return 0f;
            }
            return perDay * (ticks / 60000f) * (atSetpoint ? Clamp01(idleFactor) : 1f);
        }

        public static float Clamp01(float v)
        {
            return v < 0f ? 0f : (v > 1f ? 1f : v);
        }

        /// <summary>COLDSTORAGE_WALL_LIGHT_FIX_RESYNC: the game marks a building's cells as light blockers only when it
        /// spawns or despawns (Building.SpawnSetup / DeSpawn, if def.blockLight), so a wall-unit light switch flipped
        /// in play must patch the glow grid of every built unit: +1 add the blocker, -1 remove it, 0 nothing.</summary>
        public static int LightBlockerResync(bool blockedBefore, bool blocksNow)
        {
            return blockedBefore == blocksNow ? 0 : (blocksNow ? 1 : -1);
        }

        /// <summary>COLDSTORAGE_WALL_PRISON_FIX_HEMOGEN: social properness of an item held in a wall unit, judged by the
        /// room on the unit's facing side (the wall cell has none), with vanilla's rules: for a prisoner, proper when
        /// no pawn is given or he is in that room; a hemogen pack (Biotech) is improper only beside a prison cell
        /// holding a bloodfeeder; anything else is improper when that room is a prison cell.</summary>
        public static bool WallItemSociallyProper(bool forPrisoner, bool pawnGiven, bool pawnInFacingRoom,
            bool hemogenRule, bool bloodfeederInFacingRoom, bool facingRoomIsPrisonCell)
        {
            if (forPrisoner)
            {
                return !pawnGiven || pawnInFacingRoom;
            }
            if (hemogenRule)
            {
                return !bloodfeederInFacingRoom;
            }
            return !facingRoomIsPrisonCell;
        }
    }
}
