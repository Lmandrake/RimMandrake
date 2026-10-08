using System;
using System.Collections.Generic;

namespace RimMandrake.Stillsand
{
    // Verse-free water-debt ledger (RM_WaterLedger in RM_WaterLedger.cs): the debt book, the band lookup, the opening
    // throttle and the incident weight. RM_WaterLedger keeps one RM_LedgerBook and Scribes its public fields under the
    // same keys as before; every mutation goes through here so the offline fuzz sees exactly what the game runs.

    public struct RM_LedgerDraw
    {
        /// <summary>Goodwill change to apply (0 when none).</summary>
        public int goodwillDelta;
        /// <summary>The draw carried the debt across the opening threshold.</summary>
        public bool crossedOpening;
    }

    public sealed class RM_LedgerBook
    {
        public float debt;
        public float drawnTotal;
        public float paidTotal;
        public int openingSerial;
        public int lastOpeningTick = -999999;
        public int lastBand;

        /// <summary>Band i begins at bandLitres[i]; the highest band whose start the debt has reached.</summary>
        public static int BandFor(IList<float> bandLitres, float debt)
        {
            int band = 0;
            for (int i = 0; i < bandLitres.Count; i++)
            {
                if (debt >= bandLitres[i])
                {
                    band = i;
                }
            }
            return band;
        }

        /// <summary>Goodwill for moving up bands, then remember the band. A fall in band costs nothing and is remembered.</summary>
        private int AfterChange(IList<float> bandLitres, int goodwillPerBandUp)
        {
            int band = BandFor(bandLitres, debt);
            int delta = 0;
            if (band > lastBand && goodwillPerBandUp != 0)
            {
                delta = goodwillPerBandUp * (band - lastBand);
            }
            lastBand = band;
            return delta;
        }

        public RM_LedgerDraw Draw(float litres, IList<float> bandLitres, int goodwillPerBandUp, float openingThresholdLitres)
        {
            var r = new RM_LedgerDraw();
            float before = debt;
            debt += litres;
            drawnTotal += litres;
            r.goodwillDelta = AfterChange(bandLitres, goodwillPerBandUp);
            r.crossedOpening = before < openingThresholdLitres && debt >= openingThresholdLitres;
            return r;
        }

        /// <summary>Pay down the debt; returns the litres actually paid and the goodwill delta (always 0 on a payment).</summary>
        public float Pay(float litres, IList<float> bandLitres, int goodwillPerBandUp, out int goodwillDelta)
        {
            float paid = Math.Min(litres, debt);
            debt -= paid;
            paidTotal += paid;
            goodwillDelta = AfterChange(bandLitres, goodwillPerBandUp);
            return paid;
        }

        /// <summary>An opening counts only once per minTicksBetweenOpenings; each accepted one bumps the serial.</summary>
        public bool TryOpen(int now, int minTicksBetweenOpenings)
        {
            if (now - lastOpeningTick < minTicksBetweenOpenings)
            {
                return false;
            }
            lastOpeningTick = now;
            openingSerial++;
            return true;
        }

        /// <summary>Incident chance multiplier for an unpaid debt.</summary>
        public static float IncidentFactor(float debt, float weightPerHundredLitres, float maxWeight)
        {
            float v = 1f + debt / 100f * weightPerHundredLitres;
            float hi = Math.Max(1f, maxWeight);
            return v < 1f ? 1f : v > hi ? hi : v;
        }
    }
}
