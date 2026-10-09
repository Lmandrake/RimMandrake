// DUNES_TINT_GATE_PROOF_1 -- read-only jawa/static_call hook resolving MOVING_DUNES_BUILD_1.A3 (the design's shader-tint gate:
// MaterialColor vs VertexColor) by a state read of the exact material SectionLayer_DuneSand builds: a clone of MatBases.Sand.
using System.Collections.Generic;
using System.Globalization;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.MovingDunes
{
    public static class RM_DunesProof
    {
        /// <summary>type=RimMandrake.MovingDunes.RM_DunesProof method=ProofTint args="" -> "shader=.. hasColorProp=.. colorRoundTrip=..
        /// colorProps=.. vertexColorHint=.. defTintMode=.. defTint=..". Pure read: the clone is destroyed, nothing live is touched.</summary>
        public static string ProofTint(string unused)
        {
            try
            {
                Material sand = MatBases.Sand;
                if (sand == null || sand.shader == null) return "ERROR MatBases.Sand has no shader";
                Shader sh = sand.shader;
                var colorProps = new List<string>();
                int n = sh.GetPropertyCount();
                for (int i = 0; i < n; i++)
                {
                    string name = sh.GetPropertyName(i);
                    string low = name.ToLowerInvariant();
                    if (low.Contains("color") || low.Contains("tint")) colorProps.Add(name);
                }
                RM_DuneMaterialDef def = DefDatabase<RM_DuneMaterialDef>.GetNamedSilentFail("RM_Dunes_Sand");
                Material clone = new Material(sand);
                bool hasColor = clone.HasProperty("_Color");
                string roundTrip = "n/a";
                if (def != null && hasColor)
                {
                    clone.color = def.tint;
                    Color back = clone.color;
                    roundTrip = (Mathf.Abs(back.r - def.tint.r) < 0.01f && Mathf.Abs(back.g - def.tint.g) < 0.01f
                        && Mathf.Abs(back.b - def.tint.b) < 0.01f).ToString();
                }
                Object.Destroy(clone);
                // Vertex colours reach the fragment only if the shader declares a vertex colour input; Unity exposes no
                // reflection for that, so the hint is the sand shader family name plus the material's own _Color property.
                bool vertexHint = sh.name.ToLowerInvariant().Contains("vertex");
                return "shader=" + sh.name + " hasColorProp=" + hasColor + " colorRoundTrip=" + roundTrip
                    + " colorProps=" + string.Join("|", colorProps.ToArray()) + " vertexColorHint=" + vertexHint
                    + " defTintMode=" + (def == null ? "nodef" : def.tintMode.ToString())
                    + " defTint=" + (def == null ? "n/a" : def.tint.r.ToString("0.###", CultureInfo.InvariantCulture) + "," + def.tint.g.ToString("0.###", CultureInfo.InvariantCulture) + "," + def.tint.b.ToString("0.###", CultureInfo.InvariantCulture))
                    + " shaderPropCount=" + n;
            }
            catch (System.Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
        }
    }
}
