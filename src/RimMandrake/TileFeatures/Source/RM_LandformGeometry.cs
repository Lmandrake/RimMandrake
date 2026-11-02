using System;
using System.Collections.Generic;

namespace RimMandrake.TileFeatures
{
    // VEE_LANDFORMS_BUILD_CRATERS_AND_COMPANY: the pure geometry shared by the landform workers (craters, ridges, canyons,
    // spires, sinkholes, tides). No Verse or Unity type appears here, so SelfTest/ compiles this file alone and checks it
    // with plain numbers; the workers in RM_LandformWorkers.cs only turn these answers into elevation and terrain.
    public enum RM_CraterZone { Outside, Rim, Basin, Pool, Dome }

    public struct RM_Disc
    {
        public int x, z, r;
        public RM_Disc(int x, int z, int r) { this.x = x; this.z = z; this.r = r; }
    }

    public static class RM_LandformGeometry
    {
        public const float TwoPi = (float)(Math.PI * 2.0);

        /// <summary>Radius of a wobbly circle at <paramref name="angle"/>: baseR * (1 + sum amp[k] sin((k+2) angle + phase[k])).
        /// Harmonics start at 2 so the shape never drifts off its centre. Bounded by baseR * (1 +/- sum |amp|).</summary>
        public static float WobbledRadius(float baseR, float angle, float[] amps, float[] phases)
        {
            float f = 1f;
            if (amps != null)
                for (int k = 0; k < amps.Length; k++)
                    f += amps[k] * (float)Math.Sin((k + 2) * angle + (phases != null && k < phases.Length ? phases[k] : 0f));
            return baseR * f;
        }

        /// <summary>Smallest absolute difference between two angles, in radians, in [0, pi].</summary>
        public static float AngleGap(float a, float b)
        {
            float d = (float)Math.IEEERemainder(a - b, TwoPi);
            return Math.Abs(d);
        }

        /// <summary>Crater profile by normalised distance t = dist / radius. Outside beyond 1; the outer rimWidth band is
        /// the rim wall, except inside a breach (a gap in the wall so the basin can be walked into); inside the rim the
        /// dome (t &lt; domeFrac) comes first, then the pool (t &lt; poolFrac), then the basin.</summary>
        public static RM_CraterZone CraterZone(float dist, float radius, float rimWidth, float poolFrac, float domeFrac,
            float angle = 0f, float[] breachAngles = null, float breachHalfWidth = 0f)
        {
            if (radius <= 0f || dist > radius) return RM_CraterZone.Outside;
            float t = dist / radius;
            if (t > 1f - rimWidth)
            {
                if (breachAngles != null)
                    foreach (float b in breachAngles)
                        if (AngleGap(angle, b) <= breachHalfWidth) return RM_CraterZone.Basin;
                return RM_CraterZone.Rim;
            }
            if (domeFrac > 0f && t < domeFrac) return RM_CraterZone.Dome;
            if (poolFrac > 0f && t < poolFrac) return RM_CraterZone.Pool;
            return RM_CraterZone.Basin;
        }

        /// <summary>A meandering line through (cx, cz) at <paramref name="angle"/>, 2*halfLength long, sampled at
        /// segments+1 points, each pushed sideways by amplitude * sin(2 pi waves t + phase).</summary>
        public static void Meander(float cx, float cz, float angle, float halfLength, int segments, float amplitude, float waves,
            float phase, out float[] xs, out float[] zs)
        {
            if (segments < 1) segments = 1;
            xs = new float[segments + 1];
            zs = new float[segments + 1];
            float dx = (float)Math.Cos(angle), dz = (float)Math.Sin(angle);
            float nx = -dz, nz = dx;
            for (int i = 0; i <= segments; i++)
            {
                float t = (float)i / segments;
                float along = (t * 2f - 1f) * halfLength;
                float side = amplitude * (float)Math.Sin(TwoPi * waves * t + phase);
                xs[i] = cx + dx * along + nx * side;
                zs[i] = cz + dz * along + nz * side;
            }
        }

        /// <summary>Distance from P to segment AB, and where along AB (0..1) the closest point lies.</summary>
        public static float DistToSegment(float px, float pz, float ax, float az, float bx, float bz, out float t)
        {
            float vx = bx - ax, vz = bz - az;
            float len2 = vx * vx + vz * vz;
            t = len2 <= 0f ? 0f : ((px - ax) * vx + (pz - az) * vz) / len2;
            if (t < 0f) t = 0f; else if (t > 1f) t = 1f;
            float qx = ax + vx * t - px, qz = az + vz * t - pz;
            return (float)Math.Sqrt(qx * qx + qz * qz);
        }

        /// <summary>Distance from P to a polyline, and the arc length (in cells, from the first point) of the closest point.</summary>
        public static float DistToPolyline(float px, float pz, float[] xs, float[] zs, out float arcAt)
        {
            float best = float.MaxValue, walked = 0f;
            arcAt = 0f;
            for (int i = 0; i + 1 < xs.Length; i++)
            {
                float segLen = (float)Math.Sqrt((xs[i + 1] - xs[i]) * (xs[i + 1] - xs[i]) + (zs[i + 1] - zs[i]) * (zs[i + 1] - zs[i]));
                float d = DistToSegment(px, pz, xs[i], zs[i], xs[i + 1], zs[i + 1], out float t);
                if (d < best)
                {
                    best = d;
                    arcAt = walked + t * segLen;
                }
                walked += segLen;
            }
            return best;
        }

        /// <summary>Is P inside a band of halfWidth around the polyline, outside the open gap [gapStart, gapEnd] measured as
        /// arc length along it (gapStart &lt; 0: no gap)? The gap is a pass through a ridge, or a bridge of rock over a canyon.</summary>
        public static bool OnBand(float px, float pz, float[] xs, float[] zs, float halfWidth, float gapStart, float gapEnd)
        {
            float d = DistToPolyline(px, pz, xs, zs, out float arc);
            if (d > halfWidth) return false;
            return !(gapStart >= 0f && arc >= gapStart && arc <= gapEnd);
        }

        public static float PolylineLength(float[] xs, float[] zs)
        {
            float walked = 0f;
            for (int i = 0; i + 1 < xs.Length; i++)
                walked += (float)Math.Sqrt((xs[i + 1] - xs[i]) * (xs[i + 1] - xs[i]) + (zs[i + 1] - zs[i]) * (zs[i + 1] - zs[i]));
            return walked;
        }

        /// <summary>Non-overlapping discs inside a sizeX x sizeZ map: every disc keeps <paramref name="margin"/> cells from the
        /// edge and <paramref name="spacing"/> cells of clear ground from every other disc. Stops early when the map is full;
        /// <paramref name="allowed"/> may veto a centre (rock, water).</summary>
        public static List<RM_Disc> PlaceDiscs(int sizeX, int sizeZ, int count, int rMin, int rMax, int margin, int spacing,
            Random rng, Func<int, int, int, bool> allowed = null, int triesPerDisc = 30)
        {
            List<RM_Disc> placed = new List<RM_Disc>();
            if (rMax < rMin) rMax = rMin;
            for (int n = 0; n < count; n++)
            {
                for (int attempt = 0; attempt < triesPerDisc; attempt++)
                {
                    int r = rng.Next(rMin, rMax + 1);
                    int lo = margin + r;
                    int hiX = sizeX - 1 - margin - r, hiZ = sizeZ - 1 - margin - r;
                    if (hiX < lo || hiZ < lo) break;
                    int x = rng.Next(lo, hiX + 1), z = rng.Next(lo, hiZ + 1);
                    bool clear = true;
                    foreach (RM_Disc d in placed)
                    {
                        int need = d.r + r + spacing;
                        if ((d.x - x) * (d.x - x) + (d.z - z) * (d.z - z) < need * need) { clear = false; break; }
                    }
                    if (!clear || (allowed != null && !allowed(x, z, r))) continue;
                    placed.Add(new RM_Disc(x, z, r));
                    break;
                }
            }
            return placed;
        }

        /// <summary>Tide height 0..1 over one period: 0 at low tide (tick 0), 1 at high tide (half a period).</summary>
        public static float TideLevel(long ticks, int periodTicks)
        {
            if (periodTicks <= 0) return 0f;
            double phase = (double)(ticks % periodTicks) / periodTicks;
            return (float)(0.5 - 0.5 * Math.Cos(phase * Math.PI * 2.0));
        }

        /// <summary>A land cell <paramref name="distToSea"/> steps from the sea is under water when the tide reaches it: the
        /// water climbs reach * level cells inland. The sea itself (0) and unreached cells (negative) are never flooded.</summary>
        public static bool TideFloods(int distToSea, int reach, float level)
        {
            if (distToSea <= 0 || reach <= 0) return false;
            return distToSea <= (int)Math.Round(level * reach);
        }
    }
}
