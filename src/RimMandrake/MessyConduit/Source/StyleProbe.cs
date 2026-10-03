using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using HarmonyLib;
using RimMandrake.MessyConduit.Aerial;
using RimMandrake.MessyConduit.Core;
using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit
{
    /// <summary>
    /// Lane C (2026-10-02) state read for the art-style selector, answered through MessyConduitProbe's
    /// "styles" command (validation.py ST rows). Read-only: what the CURRENT style resolved (strand variants,
    /// decal slots, fallbacks to the Jawa set, missing/null/bad-texture materials), what the section meshes on the
    /// map actually print (distinct strand textures in RM_MessyCords sub-meshes), the per-net variant histogram,
    /// and the aerial span / shadow textures.
    /// </summary>
    public static class StyleProbe
    {
        public static string Report(Map map, RM_MapComponent_CordGraph comp)
        {
            var sb = new StringBuilder("{\"success\":true,\"cmd\":\"styles\"");
            void F(string k, string v) => sb.Append(",\"").Append(k).Append("\":").Append(v);
            F("style", S(MessyConduitSettings.style.ToString()));
            F("extCordColorMode", S(MessyConduitSettings.extCordColorMode.ToString()));
            F("extCordColor", MessyConduitSettings.extCordColor.ToString(CultureInfo.InvariantCulture));
            F("builtKey", S(CordMaterials.BuiltKey));
            F("currentKey", S(CordMaterials.CurrentKey()));
            F("rebuilds", CordMaterials.Rebuilds.ToString(CultureInfo.InvariantCulture));
            F("variantCount", CordMaterials.VariantCount.ToString(CultureInfo.InvariantCulture));
            F("strandPaths", Arr(CordMaterials.StrandPaths.Select(S)));
            var strandTex = new List<string>();
            var bad = new List<string>();
            for (int i = 0; i < CordMaterials.VariantCount; i++)
            {
                Material m = CordMaterials.StrandFor(i);
                strandTex.Add(S(TexName(m)));
                if (IsBad(m)) bad.Add(S("strand" + i));
            }
            F("strandTex", Arr(strandTex));
            var slots = new List<string>();
            var nulls = new List<string>();
            foreach (DecalKind k in Enum.GetValues(typeof(DecalKind)))
            {
                Material m = CordMaterials.Decal(k);
                if (m == null) nulls.Add(S(k.ToString()));
                else if (IsBad(m)) bad.Add(S(k.ToString()));
                slots.Add(S(k.ToString()) + ":{\"tex\":" + S(TexName(m)) + ",\"id\":" + (m?.mainTexture != null ? m.mainTexture.GetInstanceID() : 0) + "}");
            }
            foreach (KeyValuePair<string, Material> kv in new Dictionary<string, Material>
                     { { "Shadow", CordMaterials.Shadow }, { "StrandFace", CordMaterials.StrandFace }, { "StrandLod", CordMaterials.StrandLod },
                       { "LiveGlow", CordMaterials.LiveGlow }, { "SparkGlow", CordMaterials.SparkGlow }, { "Highlight", CordMaterials.Highlight },
                       { "AerialSpan", AerialMaterials.Span }, { "AerialShadow", AerialMaterials.Shadow }, { "AerialFallen", AerialMaterials.Fallen } })
            {
                if (kv.Value == null) nulls.Add(S(kv.Key));
                else if (IsBad(kv.Value)) bad.Add(S(kv.Key));
            }
            F("slots", "{" + string.Join(",", slots) + "}");
            F("slotPaths", "{" + string.Join(",", CordMaterials.SlotPaths.Select(kv => S(kv.Key) + ":" + S(kv.Value))) + "}");
            F("fallbacks", Arr(CordMaterials.Fallbacks.Select(S)));
            F("missing", Arr(CordMaterials.Missing.Select(S)));
            F("nulls", Arr(nulls));
            F("bad", Arr(bad));
            F("aerialSpanPath", S(AerialMaterials.SpanPath));
            F("aerialSpanTex", S(TexName(AerialMaterials.Span)));
            F("aerialShadowTex", S(TexName(AerialMaterials.Shadow)));
            F("aerialBuiltKey", S(AerialMaterials.BuiltKey));
            // per-net variants over the laid pieces (edges only: node pieces carry no strand of their own net choice)
            var hist = new Dictionary<int, int>();
            var seedsPerVariant = new Dictionary<int, HashSet<int>>();
            foreach (LaidPiece p in comp.Pieces)
            {
                if (p.Strands.Count == 0) continue;
                int v = comp.VariantOf(p);
                hist[v] = hist.TryGetValue(v, out int c) ? c + 1 : 1;
                if (!seedsPerVariant.TryGetValue(v, out HashSet<int> hs)) seedsPerVariant[v] = hs = new HashSet<int>();
                hs.Add(comp.NetSeedOf(p));
            }
            F("piecesPerVariant", "{" + string.Join(",", hist.OrderBy(kv => kv.Key).Select(kv => S(kv.Key.ToString()) + ":" + kv.Value)) + "}");
            F("netsPerVariant", "{" + string.Join(",", seedsPerVariant.OrderBy(kv => kv.Key).Select(kv => S(kv.Key.ToString()) + ":" + kv.Value.Count)) + "}");
            F("cordNets", seedsPerVariant.Values.SelectMany(x => x).Distinct().Count().ToString(CultureInfo.InvariantCulture));
            // what the section meshes actually hold right now
            var printed = new Dictionary<string, int>();
            var sections = Traverse.Create(map.mapDrawer).Field("sections").GetValue<Section[,]>();
            if (sections != null)
                foreach (Section sec in sections)
                    foreach (SectionLayer l in Traverse.Create(sec).Field("layers").GetValue<List<SectionLayer>>())
                    {
                        if (!(l is SectionLayer_RM_MessyCords)) continue;
                        foreach (LayerSubMesh m in l.subMeshes.Where(m => m.finalized && m.verts.Count > 0))
                        {
                            string n = TexName(m.material) + (CordMaterials.IsLod(m.material) ? "(lod)" : "");
                            printed[n] = printed.TryGetValue(n, out int c) ? c + m.verts.Count : m.verts.Count;
                        }
                    }
            F("printedTex", "{" + string.Join(",", printed.OrderBy(kv => kv.Key).Select(kv => S(kv.Key) + ":" + kv.Value)) + "}");
            var installed = new List<string>();
            foreach (CordStyle s in Enum.GetValues(typeof(CordStyle))) installed.Add(S(s.ToString()) + ":" + (CordMaterials.StyleInstalled(s) ? "true" : "false"));
            F("installed", "{" + string.Join(",", installed) + "}");
            sb.Append("}");
            return sb.ToString();
        }

        /// <summary>Settings round trip through the real file: set a non-default style, write the settings file,
        /// reset the statics in memory, read the file back (ExposeData restores the statics), report, then put the
        /// pre-test values back and write them again so the on-disk file ends as it began in memory.</summary>
        public static string SettingsRoundTrip()
        {
            CordStyle s0 = MessyConduitSettings.style;
            ExtCordColorMode m0 = MessyConduitSettings.extCordColorMode;
            int c0 = MessyConduitSettings.extCordColor;
            Mod mod = MessyConduitMod.Settings != null ? LoadedModManager.GetMod(typeof(MessyConduitMod)) : null;
            if (mod == null) return "{\"success\":false,\"cmd\":\"settingsroundtrip\",\"error\":\"mod instance not found\"}";
            string folder = mod.Content.FolderName, handle = mod.GetType().Name;
            string file = System.IO.Path.Combine(GenFilePaths.ConfigFolderPath, GenText.SanitizeFilename("Mod_" + folder + "_" + handle + ".xml"));
            MessyConduitSettings.style = CordStyle.Cybertek;
            MessyConduitSettings.extCordColorMode = ExtCordColorMode.Single;
            MessyConduitSettings.extCordColor = 3;
            MessyConduitMod.Settings.Write();
            string text = System.IO.File.Exists(file) ? System.IO.File.ReadAllText(file) : "";
            MessyConduitSettings.ResetToDefaults();
            string mid = MessyConduitSettings.style + "/" + MessyConduitSettings.extCordColorMode + "/" + MessyConduitSettings.extCordColor;
            LoadedModManager.ReadModSettings<MessyConduitSettings>(folder, handle);
            string back = MessyConduitSettings.style + "/" + MessyConduitSettings.extCordColorMode + "/" + MessyConduitSettings.extCordColor;
            MessyConduitSettings.style = s0;
            MessyConduitSettings.extCordColorMode = m0;
            MessyConduitSettings.extCordColor = c0;
            MessyConduitMod.Settings.Write();
            MessyConduitSettings.Apply();
            string restored = System.IO.File.Exists(file) ? System.IO.File.ReadAllText(file) : "";
            return "{\"success\":true,\"cmd\":\"settingsroundtrip\",\"file\":" + S(file) + ",\"written\":\"Cybertek/Single/3\",\"afterReset\":" + S(mid) +
                   ",\"readBack\":" + S(back) + ",\"fileHadStyle\":" + (text.Contains("<style>Cybertek</style>") ? "true" : "false") +
                   ",\"fileHadMode\":" + (text.Contains("<extCordColorMode>Single</extCordColorMode>") ? "true" : "false") +
                   ",\"restoredTo\":" + S(s0 + "/" + m0 + "/" + c0) + ",\"restoredFileHasCybertek\":" + (restored.Contains("<style>Cybertek</style>") ? "true" : "false") + "}";
        }

        private static string TexName(Material m) => m == null ? null : m.mainTexture == null ? "<none>" : m.mainTexture.name;

        private static bool IsBad(Material m) => m != null && (m.mainTexture == null || m.mainTexture == BaseContent.BadTex);

        private static string Arr(IEnumerable<string> xs) => "[" + string.Join(",", xs) + "]";

        private static string S(string s)
        {
            if (s == null) return "null";
            var b = new StringBuilder("\"");
            foreach (char c in s)
            {
                if (c == '"' || c == '\\') b.Append('\\').Append(c);
                else if (c < 32) b.Append("\\u").Append(((int)c).ToString("x4"));
                else b.Append(c);
            }
            return b.Append('"').ToString();
        }
    }
}
