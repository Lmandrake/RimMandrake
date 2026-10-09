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

        /// <summary>type=RimMandrake.MovingDunes.RM_DunesProof method=ProofTintLayer args="r,g,b" (default 0.6,0.4,0.3) ->
        /// "tint=.. shader=.. color=.. fallback=..": builds the material through the SHIPPED SectionLayer_DuneSand.BuildMaterial
        /// (MaterialColor mode) and reports shader name, material colour (or n/a) and whether the Map/Transparent fallback was taken.
        /// The throwaway material is destroyed unless pooled. Read-only.</summary>
        public static string ProofTintLayer(string args)
        {
            try
            {
                float[] c = { 0.6f, 0.4f, 0.3f };
                if (!string.IsNullOrEmpty(args) && args != "-")
                {
                    string[] p = args.Split(',');
                    for (int i = 0; i < 3 && i < p.Length; i++)
                    {
                        c[i] = float.Parse(p[i].Trim(), CultureInfo.InvariantCulture);
                    }
                }
                Color tint = new Color(c[0], c[1], c[2], 1f);
                bool fallback;
                Material m = SectionLayer_DuneSand.BuildMaterial(tint, DuneTintMode.MaterialColor, out fallback);
                string res = "tint=" + Fmt(tint) + " shader=" + m.shader.name + " hasColor=" + m.HasProperty("_Color")
                    + " color=" + (m.HasProperty("_Color") ? Fmt(m.color) : "n/a") + " fallback=" + fallback
                    + " vanillaShader=" + MatBases.Sand.shader.name;
                if (!fallback)
                {
                    Object.Destroy(m);
                }
                return res;
            }
            catch (System.Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
        }

        /// <summary>type=RimMandrake.MovingDunes.RM_DunesProof method=ProofTintLive args="" -> reads the sand material the
        /// current map's built SectionLayer_DuneSand layers actually hold: counts layers, and reports shader/colour/fallback of the
        /// first one that has built a material. Read-only (reflection over MapDrawer sections).</summary>
        public static string ProofTintLive(string unused)
        {
            try
            {
                Map map = Find.CurrentMap;
                if (map == null) return "ERROR no current map";
                var sections = HarmonyLib.AccessTools.Field(typeof(MapDrawer), "sections").GetValue(map.mapDrawer) as System.Array;
                var layersF = HarmonyLib.AccessTools.Field(typeof(Section), "layers");
                if (sections == null || layersF == null) return "ERROR reflection failed sections=" + (sections != null) + " layers=" + (layersF != null);
                int layers = 0, built = 0, fb = 0;
                string first = "none";
                foreach (object o in sections)
                {
                    var sec = o as Section;
                    if (sec == null) continue;
                    var list = layersF.GetValue(sec) as List<SectionLayer>;
                    if (list == null) continue;
                    foreach (SectionLayer l in list)
                    {
                        var d = l as SectionLayer_DuneSand;
                        if (d == null) continue;
                        layers++;
                        bool f;
                        Material m = d.ProofLiveMaterial(out f);
                        if (m == null) continue;
                        built++;
                        if (f) fb++;
                        if (first == "none")
                            first = "shader=" + m.shader.name + " color=" + (m.HasProperty("_Color") ? Fmt(m.color) : "n/a") + " fallback=" + f;
                    }
                }
                return "duneLayers=" + layers + " builtMaterial=" + built + " fallbackLayers=" + fb + " first{" + first + "}";
            }
            catch (System.Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
        }

        private static string Fmt(Color c)
        {
            return c.r.ToString("0.###", CultureInfo.InvariantCulture) + "," + c.g.ToString("0.###", CultureInfo.InvariantCulture) + "," + c.b.ToString("0.###", CultureInfo.InvariantCulture);
        }
    }
}
