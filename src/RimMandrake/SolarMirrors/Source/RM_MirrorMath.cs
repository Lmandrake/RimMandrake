using UnityEngine;

namespace RimMandrake.SolarMirrors
{
    // SOLAR_MIRRORS_MOD_DESIGN_1 §2.2. A Vector3 facade over Kernel/RM_MirrorKernel.cs, which holds the one implementation
    // (Verse-free, fuzzed offline). Axes: x east, y up, z north. All direction vectors are unit vectors.
    public static class RM_MirrorMath
    {
        /// <summary>Nominal height of a mirror's face above the ground, in cells (design §2.2).</summary>
        public const float FaceHeight = RM_MirrorKernel.FaceHeight;

        public static RM_Vec To(Vector3 v) { return new RM_Vec(v.x, v.y, v.z); }
        public static Vector3 From(RM_Vec v) { return new Vector3(v.X, v.Y, v.Z); }

        /// <summary>Unit vector from the ground toward the sun. shadowDir is the ground direction
        /// shadows fall (the shade grid's SunShadowDirection), so the sun stands the other way.</summary>
        public static Vector3 SunVector(float shadowDirX, float shadowDirZ, float elevationDeg)
        {
            return From(RM_MirrorKernel.SunVector(shadowDirX, shadowDirZ, elevationDeg));
        }

        /// <summary>A simple moving sun for maps with no pinned or fixed sun (PROVISIONAL model):
        /// rises due east at dayPercent 0.25, crosses toward the equator at noon, sets due west at
        /// 0.75. Peak elevation 90 - |latitude|. Returns false at night.</summary>
        public static bool MovingSun(float dayPercent, float latitudeDeg, out Vector3 sun)
        {
            RM_Vec s;
            bool up = RM_MirrorKernel.MovingSun(dayPercent, latitudeDeg, out s);
            sun = From(s);
            return up;
        }

        /// <summary>The mirror normal that sends light arriving from inDir toward outDir.</summary>
        public static Vector3 Normal(Vector3 inDir, Vector3 outDir)
        {
            return From(RM_MirrorKernel.Normal(To(inDir), To(outDir)));
        }

        /// <summary>Design §2.2 cosine law: the share of light delivered, sqrt((1 + s·t) / 2).</summary>
        public static float Efficiency(Vector3 inDir, Vector3 outDir)
        {
            return RM_MirrorKernel.Efficiency(To(inDir), To(outDir));
        }

        /// <summary>Change detection is on quantised light (design §2.7), never on raw floats.</summary>
        public static int Quantise(float v, float step = 0.05f)
        {
            return RM_MirrorKernel.Quantise(v, step);
        }

        /// <summary>Sun-stone hysteresis (design §3.4): turns on at onAt, off below offAt.</summary>
        public static bool Hysteresis(bool wasLit, float light, float onAt, float offAt)
        {
            return RM_MirrorKernel.Hysteresis(wasLit, light, onAt, offAt);
        }
    }
}
