// Gimme Some Slack core: Verse-free (see CordMath.cs header); Source/SelfTest compiles this file directly.
//
// The mod shipped as Messy Conduit (packageId mandrake.rm.messyconduit, namespace RimMandrake.MessyConduit, folder
// MessyConduit) until GIMMESOMESLACK_RENAME_1 (owner, 2026-10-04: "Let's call it Gimme Some Slack."). Two things on a
// player's disk still carry the old name and are carried over here:
//   * saved type names: a save writes Class="RimMandrake.MessyConduit.X" for our map components and job drivers, and a
//     settings file writes <ModSettings Class="RimMandrake.MessyConduit.MessyConduitSettings"/>; MapTypeName maps them
//     (used by the GenTypes.GetTypeInAnyAssembly prefix in GimmeSomeSlackMod.cs and by MigrateSettingsText);
//   * the settings files: Verse names them Mod_<deployed folder>_<Mod class>.xml, so the old ones are
//     Mod_MessyConduit_{MessyConduitMod,AerialLinesMod,FireHosesMod}.xml. MigrateSettingsFiles copies each one to its
//     new name once, only when the new file does not exist yet, and never deletes the old file.
// defNames and Scribe keys did not change in that rename. One settings key changed later (A12/B15, 2026-10-06):
// the loop budget, read through LoopBudgetOnLoad.
using System;
using System.Collections.Generic;
using System.IO;

namespace RimMandrake.GimmeSomeSlack.Core
{
    public static class LegacyName
    {
        public const string OldNamespace = "RimMandrake.MessyConduit";
        public const string NewNamespace = "RimMandrake.GimmeSomeSlack";
        public const string OldFolder = "MessyConduit";

        /// <summary>Old type short names that were renamed along with the namespace (every other type kept its name).</summary>
        public static readonly IReadOnlyDictionary<string, string> RenamedTypes = new Dictionary<string, string>
        {
            { "MessyConduitMod", "GimmeSomeSlackMod" },
            { "MessyConduitSettings", "GimmeSomeSlackSettings" },
            { "MessyConduitDefOf", "GimmeSomeSlackDefOf" },
            { "MessyConduitProbe", "GimmeSomeSlackProbe" },
        };

        /// <summary>(old Mod class, new Mod class) for each of the three settings files.</summary>
        public static readonly (string Old, string New)[] SettingsHandles =
        {
            ("MessyConduitMod", "GimmeSomeSlackMod"),
            ("AerialLinesMod", "AerialLinesMod"),
            ("FireHosesMod", "FireHosesMod"),
        };

        /// <summary>Sentinel for "this key was not in the settings file" (no real slider value is negative).</summary>
        public const float Unset = -1f;
        /// <summary>The loop budget's settings key before GPT source read 2026-10-06 A12/B15 renamed it to loopBudget.</summary>
        public const string OldLoopBudgetKey = "sprawlCap";

        /// <summary>The loop budget after a settings load: the new key when the file has it, else the old key's value, else
        /// the default. A file saved after the rename carries only the new key, so the old one is read at most once.</summary>
        public static float LoopBudgetOnLoad(float loaded, float legacy, float dflt)
        {
            if (loaded >= 0f) return loaded;
            if (legacy >= 0f) return legacy;
            return dflt;
        }

        /// <summary>The current full type name for a saved pre-rename one, or null when the name is not ours-and-old.</summary>
        public static string MapTypeName(string typeName)
        {
            if (string.IsNullOrEmpty(typeName) || !typeName.StartsWith(OldNamespace + ".", StringComparison.Ordinal))
                return null;
            string rest = typeName.Substring(OldNamespace.Length + 1);
            int dot = rest.LastIndexOf('.');
            string shortName = dot < 0 ? rest : rest.Substring(dot + 1);
            if (RenamedTypes.TryGetValue(shortName, out string renamed))
                rest = (dot < 0 ? "" : rest.Substring(0, dot + 1)) + renamed;
            return NewNamespace + "." + rest;
        }

        /// <summary>An old settings file's text with every Class="..." type name mapped to the current one.</summary>
        public static string MigrateSettingsText(string xml)
        {
            if (xml == null) return null;
            const string attr = "Class=\"";
            var sb = new System.Text.StringBuilder(xml.Length + 32);
            int i = 0;
            while (true)
            {
                int a = xml.IndexOf(attr, i, StringComparison.Ordinal);
                if (a < 0) { sb.Append(xml, i, xml.Length - i); break; }
                int s = a + attr.Length;
                int e = xml.IndexOf('"', s);
                if (e < 0) { sb.Append(xml, i, xml.Length - i); break; }
                sb.Append(xml, i, s - i);
                string name = xml.Substring(s, e - s);
                sb.Append(MapTypeName(name) ?? name);
                i = e;
            }
            return sb.ToString();
        }

        /// <summary>Copy each old settings file to its new name when the new one is absent. Returns the files written.
        /// The old files stay (a rollback to the old build still finds them).</summary>
        public static List<string> MigrateSettingsFiles(string configDir, string newFolder)
        {
            var written = new List<string>();
            if (string.IsNullOrEmpty(configDir) || !Directory.Exists(configDir) || newFolder == OldFolder) return written;
            foreach (var (oldH, newH) in SettingsHandles)
            {
                string from = Path.Combine(configDir, "Mod_" + OldFolder + "_" + oldH + ".xml");
                string to = Path.Combine(configDir, "Mod_" + newFolder + "_" + newH + ".xml");
                if (File.Exists(to) || !File.Exists(from)) continue;
                File.WriteAllText(to, MigrateSettingsText(File.ReadAllText(from)));
                written.Add(to);
            }
            return written;
        }
    }
}
