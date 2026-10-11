// Verse-free (the FlowWorks SelfTest compiles this file): what an existing player's disk still names from before the hose
// moved from Gimme Some Slack into FlowWorks (hose port step 2, design v2 §6 / FINAL §3.8-3.9).
//   * saved type names: a colonist mid-carry is saved with curDriver Class="RimMandrake.GimmeSomeSlack.Hose.Jobs.JobDriver_…"
//     (or, from before GSS's own rename, RimMandrake.MessyConduit.Hose.…); MapTypeName maps both to RimMandrake.FlowWorks.Hose.…
//   * the hose settings file Mod_<folder>_FireHosesMod.xml (folder GimmeSomeSlack, MessyConduit or a Workshop id): read once,
//     by key name, into FlowWorks' hose section; the old file is never deleted;
//   * GSS's global cord style (key `style` in Mod_<folder>_GimmeSomeSlackMod.xml / _MessyConduitMod.xml): seeds FlowWorks'
//     hose default look once, so an unstyled reel keeps the look it had.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Xml;

namespace RimMandrake.FlowWorks.Hose
{
    public static class RM_HoseLegacyMath
    {
        public const string NewPrefix = "RimMandrake.FlowWorks.Hose.";
        public static readonly string[] OldPrefixes = { "RimMandrake.GimmeSomeSlack.Hose.", "RimMandrake.MessyConduit.Hose." };

        /// <summary>The FlowWorks type name for a saved pre-port hose type name, or null when it is not one of ours-and-old.</summary>
        public static string MapTypeName(string typeName)
        {
            if (string.IsNullOrEmpty(typeName)) return null;
            foreach (string p in OldPrefixes)
                if (typeName.StartsWith(p, StringComparison.Ordinal) && typeName.Length > p.Length)
                    return NewPrefix + typeName.Substring(p.Length);
            return null;
        }

        /// <summary>The GSS hose setting keys FlowWorks imports (15: 14 player-facing + maxLengthDefaults). useFlowWorksPumps and
        /// defaultFluid are NOT imported: they die with the real flow (step 6).</summary>
        public static readonly string[] ImportedKeys =
        {
            "enabled", "minBendRadius", "plumpAmount", "transitionTicks", "releaseTicks", "minPlumpDwell", "maxLength",
            "maxLengthDefaults", "couplingSpacing", "handlingTime", "windCellsPerSecond", "autoResumeDroppedHose", "slack",
            "tintByContents", "fillWobble",
        };

        public const string HoseFileSuffix = "_FireHosesMod.xml";
        public static readonly string[] CordFileSuffixes = { "_GimmeSomeSlackMod.xml", "_MessyConduitMod.xml" };

        /// <summary>Which of several candidate files to import: the one whose folder part is <paramref name="preferFolder"/>
        /// (GSS's deployed folder when GSS is loaded), else the newest by mtime; null when there are none.</summary>
        public static string PickFile(IList<(string path, DateTime mtime)> candidates, string preferFolder, string suffix)
        {
            if (candidates == null || candidates.Count == 0) return null;
            if (!string.IsNullOrEmpty(preferFolder))
                foreach (var c in candidates)
                    if (string.Equals(Path.GetFileName(c.path), "Mod_" + preferFolder + suffix, StringComparison.OrdinalIgnoreCase)) return c.path;
            string best = null;
            DateTime bt = DateTime.MinValue;
            foreach (var c in candidates)
                if (best == null || c.mtime > bt || (c.mtime == bt && string.CompareOrdinal(c.path, best) < 0)) { best = c.path; bt = c.mtime; }
            return best;
        }

        /// <summary>Key -> raw string value of every child of the file's ModSettings element, ignoring its Class attribute.
        /// Empty when the text is not a settings file.</summary>
        public static Dictionary<string, string> ReadKeys(string xml)
        {
            var d = new Dictionary<string, string>();
            try
            {
                var doc = new XmlDocument();
                doc.LoadXml(xml);
                XmlNode ms = doc.SelectSingleNode("//ModSettings");
                if (ms == null) return d;
                foreach (XmlNode n in ms.ChildNodes)
                    if (n.NodeType == XmlNodeType.Element) d[n.Name] = n.InnerText;
            }
            catch (XmlException) { }
            return d;
        }

        /// <summary>The imported subset (only ImportedKeys present in the file, with values that parse as their type).</summary>
        public static Dictionary<string, string> HoseImport(string xml)
        {
            Dictionary<string, string> all = ReadKeys(xml), d = new Dictionary<string, string>();
            foreach (string k in ImportedKeys)
                if (all.TryGetValue(k, out string v) && v != null) d[k] = v.Trim();
            return d;
        }

        /// <summary>GSS's CordStyle enum name -> hose look (the 4-row table of GSS AerialMaterials.LookOf). Unknown -> null.</summary>
        public static string LookOfCordStyle(string cordStyle)
        {
            switch ((cordStyle ?? "").Trim())
            {
                case "StarWarsJawa": return "Scrapper";
                case "StarWars": return "Industrial";
                case "ExtensionCord": return "Modern";
                case "Cybertek": return "Futuristic";
                default: return null;
            }
        }

        /// <summary>The look to seed from a GSS cord settings file's text: its `style` key mapped, else Scrapper (a file
        /// without the key was written with GSS's default style, StarWarsJawa = Scrapper).</summary>
        public static string LookFromCordSettings(string xml)
        {
            if (xml == null) return "Scrapper";
            ReadKeys(xml).TryGetValue("style", out string s);
            return LookOfCordStyle(s) ?? "Scrapper";
        }

        // ---- the universal pipe's def alias (hose port step 4, design v2 §6.2): RM_LiquidHose was renamed RM_UniversalPipe.
        // Scribe resolves a saved def name through BackCompatibility.BackCompatibleDefName; a postfix maps the old names
        // (the def and the engine's derived blueprint/frame defs) to the new ones, only for ThingDef and only when the
        // old name is not a live def (the caller checks that), so it can never shadow a real def.
        public static readonly IReadOnlyDictionary<string, string> PipeDefAliases = new Dictionary<string, string>
        {
            { "RM_LiquidHose", "RM_UniversalPipe" },
            { "Blueprint_RM_LiquidHose", "Blueprint_RM_UniversalPipe" },
            { "Frame_RM_LiquidHose", "Frame_RM_UniversalPipe" },
        };

        /// <summary>The current defName for a saved ThingDef name, or null when it is not one of the renamed ones.</summary>
        public static string MapDefName(string defTypeName, string defName)
        {
            if (defName == null || (defTypeName != null && defTypeName != "ThingDef" && defTypeName != "Verse.ThingDef")) return null;
            return PipeDefAliases.TryGetValue(defName, out string to) ? to : null;
        }

        public static bool TryBool(string s, out bool v) => bool.TryParse(s, out v);
        public static bool TryInt(string s, out int v) => int.TryParse(s, NumberStyles.Integer, CultureInfo.InvariantCulture, out v);
        public static bool TryFloat(string s, out float v) => float.TryParse(s, NumberStyles.Float, CultureInfo.InvariantCulture, out v);
    }
}
