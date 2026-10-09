using System;

namespace RimMandrake.EnvironmentalHazards
{
    // Pure decisions behind two 2026-10-08 card rulings, kept free of Verse/Unity so the offline
    // SelfTest compiles this exact file (RimMandrake.EnvironmentalHazards.SelfTest.csproj lists it).
    //
    //   BLOWER_ROOM_COOLER_1: the dry-air blower is a room cooler that never heats a room.
    //   LAUNCH_HELD_COLONIST_WARNING_1: which held pawns the gravship launch warning names.
    public static class RM_RoomCoolerKernel
    {
        // Same per-rare-tick scale vanilla Building_Cooler uses (energyPerSecond * 4.1666665).
        public const float RareTickEnergyScale = 4.1666665f;

        // Energy budget for one rare tick: always <= 0, whatever sign the setting carries.
        public static float CoolingEnergyPerRareTick(float strengthPerSecond)
        {
            if (float.IsNaN(strengthPerSecond) || float.IsInfinity(strengthPerSecond))
            {
                return 0f;
            }
            return -Math.Abs(strengthPerSecond) * RareTickEnergyScale;
        }

        // The temperature change actually applied to the room. The never-heats guarantee lives here:
        // whatever vanilla's ControlTemperatureTempChange returns, a positive change is dropped.
        public static float ClampNeverHeat(float tempChange)
        {
            if (float.IsNaN(tempChange) || tempChange > 0f)
            {
                return 0f;
            }
            return tempChange;
        }

        // Power drawn this rare tick: full while cooling, the low factor while the room is at target
        // or there is no enclosed room behind it (the doorway curtain still runs).
        public static float PowerDraw(float wattsSetting, bool cooling, float lowFactor)
        {
            float w = Math.Max(0f, wattsSetting);
            return cooling ? w : w * Math.Max(0f, Math.Min(1f, lowFactor));
        }

        // A pawn the launch warning names: one of ours (colonist or colony prisoner), alive, not on
        // the map itself, not riding a transporter, and held by something that is not ours (a wild
        // creature's gut, a brine jacket, a raider carrying them). Our own caskets and our own
        // colonists carrying someone are not "held inside something".
        public static bool ShouldNameHeld(bool ours, bool dead, bool spawned, bool inTransporter,
                                          bool hasSpawnedHolder, bool holderIsOurs)
        {
            return ours && !dead && !spawned && !inTransporter && hasSpawnedHolder && !holderIsOurs;
        }
    }
}
