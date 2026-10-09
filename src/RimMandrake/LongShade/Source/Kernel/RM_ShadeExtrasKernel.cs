// Verse-free kernel of the Long Shade extras (LONGSHADE_SHADE_EXTRAS_1): the tollok's rent of resting in WILD shade, the lure awning's
// sheltering count and the overheated-herd stampede test. Same rule as RM_LongShadeKernel.cs: no Verse/RimWorld/UnityEngine here.
// Every number a caller passes in is PROVISIONAL (see the tuning fields in RM_ShadeExtras.cs).
using System;
using System.Collections.Generic;

namespace RimMandrake.LongShade
{
    public static partial class RM_LongShadeKernel
    {
        // ================================================================= tollok ticks (F2)
        /// <summary>Wild shade is shade nobody built: shaded enough, no roof over it, no shade gear over it.</summary>
        public static bool WildDeepShade(float shade, float roofShade, float gearShade, float deepShade)
        {
            return shade >= deepShade && roofShade <= 0.01f && gearShade <= 0.01f;
        }

        /// <summary>Dwell counter: grows by the scan step while the animal stays put in wild deep shade, resets the moment it does not.</summary>
        public static int TollokDwell(int dwell, bool stationaryInWildDeepShade, int stepTicks)
        {
            return stationaryInWildDeepShade ? dwell + Math.Max(0, stepTicks) : 0;
        }

        /// <summary>Severity added at a scan: nothing until the dwell passes the threshold, then one fixed gain per scan, capped at 1.</summary>
        public static float TollokGain(int dwell, int thresholdTicks, float gainPerScan, float current)
        {
            if (dwell < thresholdTicks) return 0f;
            return Math.Max(0f, Math.Min(gainPerScan, 1f - current));
        }

        // ================================================================= lure awning (N4)
        /// <summary>How many of the given cell shades count as sheltering (at least minShade).</summary>
        public static int ShelterCount(IList<float> shadesUnderAnimals, float minShade)
        {
            int n = 0;
            for (int i = 0; i < shadesUnderAnimals.Count; i++) if (shadesUnderAnimals[i] >= minShade) n++;
            return n;
        }

        // ================================================================= stampede for your roof (F3)
        /// <summary>A herd stampedes when it is big enough and at least minFraction of it is over its safe heat.</summary>
        public static bool StampedeReady(int herdSize, int overheated, int minHerd, float minFraction)
        {
            if (herdSize < minHerd || herdSize <= 0) return false;
            return overheated >= 0 && overheated <= herdSize && (float)overheated / herdSize >= minFraction;
        }

        /// <summary>A stampeder keeps running for the roof until it is back under its safe heat; at most maxTicks, then it is released.</summary>
        public static bool StampedeContinues(bool stillOverheated, int ticksSinceStart, int maxTicks)
        {
            return stillOverheated && ticksSinceStart < maxTicks;
        }

        // ================================================================= harrok (W2)
        /// <summary>
        /// Is the offset (dx, dz) from the harrok inside the strip its shadow lays along the unit sun vector (dirX, dirZ)?
        /// Along-distance must be within (0, length] and sideways distance within halfWidth.
        /// </summary>
        public static bool InShadowStrip(float dx, float dz, float dirX, float dirZ, float length, float halfWidth)
        {
            float along = dx * dirX + dz * dirZ;
            float side = Math.Abs(dx * -dirZ + dz * dirX);
            return along > 0f && along <= length && side <= halfWidth;
        }

        /// <summary>A harrok strikes a resting thing in its shadow only if the thing is small enough and its cooldown has run out.</summary>
        public static bool HarrokCanStrike(bool preyResting, float preyBodySize, float maxBodySize, int now, int lastStrike, int cooldownTicks)
        {
            return preyResting && preyBodySize <= maxBodySize && now - lastStrike >= cooldownTicks;
        }

        // ================================================================= Jawa return (I5)
        /// <summary>The hull counts as looted once a colonist has been inside, nothing hostile is left in it and at most maxItems loose items remain.</summary>
        public static bool HullLooted(bool entered, int hostilesInside, int itemsInside, int maxItems)
        {
            return entered && hostilesInside <= 0 && itemsInside <= maxItems;
        }

        /// <summary>Is (x, z) inside the w x h rect centred on (cx, cz)? Even sizes extend one more cell to the high side.</summary>
        public static bool InHullRect(int x, int z, int cx, int cz, int w, int h)
        {
            int minX = cx - w / 2, minZ = cz - h / 2;
            return x >= minX && x < minX + w && z >= minZ && z < minZ + h;
        }

        /// <summary>The tow is done when the clan has had towTicks since it arrived; a start of -1 means it has not arrived.</summary>
        public static bool TowDone(int startTick, int now, int towTicks)
        {
            return startTick >= 0 && now - startTick >= towTicks;
        }
    }
}
