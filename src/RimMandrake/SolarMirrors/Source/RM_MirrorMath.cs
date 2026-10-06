using System;
using UnityEngine;

namespace RimMandrake.SolarMirrors
{
    // SOLAR_MIRRORS_MOD_DESIGN_1 §2.2. Pure maths, no Verse types, so it can be self-tested
    // offline. Axes: x east, y up, z north (RimWorld's map axes plus height). All direction
    // vectors are unit vectors.
    public static class RM_MirrorMath
    {
        /// <summary>Nominal height of a mirror's face above the ground, in cells (design §2.2).</summary>
        public const float FaceHeight = 1.5f;

        /// <summary>Unit vector from the ground toward the sun. shadowDir is the ground direction
        /// shadows fall (the shade grid's SunShadowDirection), so the sun stands the other way.</summary>
        public static Vector3 SunVector(float shadowDirX, float shadowDirZ, float elevationDeg)
        {
            float e = Mathf.Clamp(elevationDeg, 0f, 90f) * Mathf.Deg2Rad;
            float ax = -shadowDirX;
            float az = -shadowDirZ;
            float len = Mathf.Sqrt(ax * ax + az * az);
            if (len < 1e-5f)
            {
                return Vector3.up;
            }
            float c = Mathf.Cos(e);
            return new Vector3(ax / len * c, Mathf.Sin(e), az / len * c).normalized;
        }

        /// <summary>A simple moving sun for maps with no pinned or fixed sun (PROVISIONAL model):
        /// rises due east at dayPercent 0.25, crosses toward the equator at noon, sets due west at
        /// 0.75. Peak elevation 90 - |latitude|. Returns false at night.</summary>
        public static bool MovingSun(float dayPercent, float latitudeDeg, out Vector3 sun)
        {
            sun = Vector3.up;
            float h = (dayPercent - 0.5f) * 2f * Mathf.PI; // hour angle; -pi/2 at sunrise
            float ch = Mathf.Cos(h);
            if (ch <= 0f)
            {
                return false;
            }
            float peak = 90f - Mathf.Min(89f, Mathf.Abs(latitudeDeg));
            float elev = peak * ch;
            float eq = latitudeDeg > 0f ? -1f : latitudeDeg < 0f ? 1f : 0f; // equatorward at noon
            float ax = -Mathf.Sin(h);
            float az = eq * ch;
            float len = Mathf.Sqrt(ax * ax + az * az);
            if (len < 1e-5f)
            {
                return true;
            }
            float e = elev * Mathf.Deg2Rad;
            sun = new Vector3(ax / len * Mathf.Cos(e), Mathf.Sin(e), az / len * Mathf.Cos(e)).normalized;
            return true;
        }

        /// <summary>The mirror normal that sends light arriving from inDir toward outDir.</summary>
        public static Vector3 Normal(Vector3 inDir, Vector3 outDir)
        {
            Vector3 n = inDir + outDir;
            return n.sqrMagnitude < 1e-8f ? inDir : n.normalized;
        }

        /// <summary>Design §2.2 cosine law: the share of light delivered, sqrt((1 + s·t) / 2). It
        /// equals n·s for the ideal normal, which is what Delivered uses for any normal.</summary>
        public static float Efficiency(Vector3 inDir, Vector3 outDir)
        {
            return Mathf.Sqrt(Mathf.Max(0f, (1f + Vector3.Dot(inDir, outDir)) * 0.5f));
        }

        /// <summary>Light a face with this normal passes on: cosine of incidence, never negative.</summary>
        public static float Cosine(Vector3 normal, Vector3 inDir)
        {
            return Mathf.Max(0f, Vector3.Dot(normal, inDir));
        }

        /// <summary>The outgoing direction of light arriving from inDir (pointing toward the source).</summary>
        public static Vector3 Reflect(Vector3 inDir, Vector3 normal)
        {
            return 2f * Vector3.Dot(normal, inDir) * normal - inDir;
        }

        /// <summary>Where a ray from a face at height faceY along dir meets the ground, if it does
        /// within maxRange cells of horizontal travel.</summary>
        public static bool GroundHit(float faceX, float faceY, float faceZ, Vector3 dir, float maxRange,
            out float x, out float z)
        {
            x = faceX;
            z = faceZ;
            if (dir.y > -0.01f)
            {
                return false; // into the sky, or skimming the ground forever
            }
            float k = faceY / -dir.y;
            float dx = dir.x * k;
            float dz = dir.z * k;
            if (dx * dx + dz * dz > maxRange * maxRange)
            {
                return false;
            }
            x = faceX + dx;
            z = faceZ + dz;
            return true;
        }

        /// <summary>Walks the cells strictly between (x0,z0) and (x1,z1) on a 4-connected
        /// Bresenham line (the same walk as GenSight.PointsOnLineOfSight, which skips its end
        /// cell; the caller tests the target separately). Returns false at the first cell
        /// blocked() says stops the beam.</summary>
        public static bool LineClear(int x0, int z0, int x1, int z1, Func<int, int, bool> blocked)
        {
            int dx = Math.Abs(x1 - x0);
            int dz = Math.Abs(z1 - z0);
            int x = x0;
            int z = z0;
            int n = 1 + dx + dz;
            int xInc = x1 > x0 ? 1 : -1;
            int zInc = z1 > z0 ? 1 : -1;
            bool sideOnEqual = x0 != x1 ? x0 < x1 : z0 < z1;
            int error = dx - dz;
            dx *= 2;
            dz *= 2;
            bool first = true;
            while (n > 1)
            {
                if (!first && blocked(x, z))
                {
                    return false;
                }
                first = false;
                if (error > 0 || (error == 0 && sideOnEqual))
                {
                    x += xInc;
                    error -= dz;
                }
                else
                {
                    z += zInc;
                    error += dx;
                }
                n--;
            }
            return true;
        }

        /// <summary>Change detection is on quantised light (design §2.7), never on raw floats.</summary>
        public static int Quantise(float v, float step = 0.05f)
        {
            return Mathf.RoundToInt(v / step);
        }

        /// <summary>Sun-stone hysteresis (design §3.4): turns on at onAt, off below offAt.</summary>
        public static bool Hysteresis(bool wasLit, float light, float onAt, float offAt)
        {
            return wasLit ? light >= offAt : light >= onAt;
        }
    }
}
