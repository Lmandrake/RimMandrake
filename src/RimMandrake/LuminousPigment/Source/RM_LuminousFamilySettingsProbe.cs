// DEEPFIRE_FAMILY_SETTINGS_SAVE_LOAD_1: live Scribe round trip of the keyed Cuisine family toggles, through the REAL
// settings file (ModSettings.Write -> Mod.WriteSettings, LoadedModManager.ReadModSettings), called by
// LuminousPigment/live_probes/lp_family_settings_roundtrip.py via jawa/static_call. Pattern: GimmeSomeSlack StyleProbe.
//   keyed:  disable one family, write, reset memory to all-on, read the file back -> that family (by key) is off again.
//   legacy: rewrite the file in the pre-keyed shape (positional <familyEnabled> list, no <familyDisabledKeys>), read it ->
//           the positional off migrates; write again -> the file now carries the key and no positional list.
// The pre-test file text and in-memory toggles are put back in `finally`, then written, so the file ends as it began.
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Xml;
using Verse;

namespace RimMandrake.LuminousPigment
{
    public static class RM_LuminousFamilySettingsProbe
    {
        public static string RoundTrip()
        {
            Mod mod = LoadedModManager.GetMod(typeof(LuminousPigmentMod));
            if (mod == null || LuminousPigmentMod.settings == null) return Json(false, "mod instance or settings not found", null);
            int n = DeepfireFamilies.All.Count;
            if (n < 3) return Json(false, "need at least 3 families to tell positions apart, have " + n, null);
            string folder = mod.Content.FolderName, handle = mod.GetType().Name;
            string file = Path.Combine(GenFilePaths.ConfigFolderPath, GenText.SanitizeFilename("Mod_" + folder + "_" + handle + ".xml"));
            bool[] snapshot = (bool[])LuminousPigmentSettings.familyEnabled.Clone();
            LuminousPigmentMod.settings.Write();   // pre-test state on disk first, so a throw mid-test loses nothing
            string pre = File.Exists(file) ? File.ReadAllText(file) : null;
            var r = new List<string>();
            bool ok = pre != null;
            if (!ok) r.Add(Kv("error", "settings file not written: " + file));
            int a = 1, b = n - 1;   // keyed test disables a middle family, legacy test the last: a position mix-up shows
            string keyA = DeepfireFamilies.All[a].key, keyB = DeepfireFamilies.All[b].key;
            try
            {
                if (ok)
                {
                    // --- A1 keyed round trip
                    SetAllOnExcept(a);
                    LuminousPigmentMod.settings.Write();
                    string text = File.ReadAllText(file);
                    bool fileHasKey = KeysInFile(text).Contains(keyA);
                    bool fileHasLegacy = HasNode(text, "familyEnabled");
                    SetAllOnExcept(-1);
                    LoadedModManager.ReadModSettings<LuminousPigmentSettings>(folder, handle);
                    bool backOk = OnlyOff(a);
                    bool a1 = fileHasKey && !fileHasLegacy && backOk;
                    r.Add(Kv("A1", a1 ? "PASS" : "FAIL"));
                    r.Add(Kv("A1_key", keyA));
                    r.Add(Kv("A1_fileHasKey", fileHasKey.ToString()));
                    r.Add(Kv("A1_fileHasLegacyList", fileHasLegacy.ToString()));
                    r.Add(Kv("A1_readBack", Bits()));

                    // --- A2 legacy list migrates to keys
                    var doc = new XmlDocument();
                    doc.LoadXml(text);
                    XmlNode ms = doc.SelectSingleNode("/SettingsBlock/ModSettings");
                    XmlNode keyed = ms?.SelectSingleNode("familyDisabledKeys");
                    if (keyed != null) ms.RemoveChild(keyed);
                    XmlElement legacy = doc.CreateElement("familyEnabled");
                    for (int i = 0; i < n; i++)
                    {
                        XmlElement li = doc.CreateElement("li");
                        li.InnerText = i == b ? "False" : "True";
                        legacy.AppendChild(li);
                    }
                    ms?.AppendChild(legacy);
                    File.WriteAllText(file, doc.OuterXml);
                    SetAllOnExcept(-1);
                    LoadedModManager.ReadModSettings<LuminousPigmentSettings>(folder, handle);
                    bool migratedOk = OnlyOff(b);
                    string migratedBits = Bits();
                    LuminousPigmentMod.settings.Write();
                    string after = File.ReadAllText(file);
                    var afterKeys = KeysInFile(after);
                    bool writtenAsKeys = afterKeys.Count == 1 && afterKeys[0] == keyB && !HasNode(after, "familyEnabled");
                    bool a2 = ms != null && migratedOk && writtenAsKeys;
                    r.Add(Kv("A2", a2 ? "PASS" : "FAIL"));
                    r.Add(Kv("A2_key", keyB));
                    r.Add(Kv("A2_migrated", migratedBits));
                    r.Add(Kv("A2_rewrittenKeys", string.Join(",", afterKeys)));
                    r.Add(Kv("A2_rewrittenHasLegacyList", HasNode(after, "familyEnabled").ToString()));
                    ok = a1 && a2;
                }
            }
            finally
            {
                if (pre != null)
                {
                    File.WriteAllText(file, pre);
                    LoadedModManager.ReadModSettings<LuminousPigmentSettings>(folder, handle);   // every pre-test value back
                }
                LuminousPigmentSettings.familyEnabled = snapshot;
                LuminousPigmentMod.settings.Write();
            }
            // the file as left must carry exactly the pre-test toggles, by key
            var keysNow = File.Exists(file) ? KeysInFile(File.ReadAllText(file)) : null;
            var keysWant = RM_DeepfireFamilyKeys.DisabledKeys(snapshot, DeepfireFamilies.All.ConvertAll(f => f.key));
            bool restored = keysNow != null && string.Join(",", keysNow) == string.Join(",", keysWant);
            r.Add(Kv("restoredFileKeys", keysNow == null ? "null" : string.Join(",", keysNow)));
            r.Add(Kv("restored", restored.ToString()));
            ok = ok && restored;
            r.Add(Kv("file", file));
            return Json(ok, null, r);
        }

        private static void SetAllOnExcept(int off)
        {
            var arr = new bool[DeepfireFamilies.All.Count];
            for (int i = 0; i < arr.Length; i++) arr[i] = i != off;
            // restore-check: ok every caller is inside the probe's try; that finally reloads the file and writes snapshot back
            LuminousPigmentSettings.familyEnabled = arr;
        }

        private static bool OnlyOff(int off)
        {
            bool[] e = LuminousPigmentSettings.familyEnabled;
            if (e == null || e.Length != DeepfireFamilies.All.Count) return false;
            for (int i = 0; i < e.Length; i++) if (e[i] != (i != off)) return false;
            return true;
        }

        private static List<string> KeysInFile(string xml)
        {
            var keys = new List<string>();
            var doc = new XmlDocument();
            doc.LoadXml(xml);
            XmlNodeList lis = doc.SelectNodes("/SettingsBlock/ModSettings/familyDisabledKeys/li");
            if (lis != null) foreach (XmlNode li in lis) keys.Add(li.InnerText);
            return keys;
        }

        private static bool HasNode(string xml, string name)
        {
            var doc = new XmlDocument();
            doc.LoadXml(xml);
            return doc.SelectSingleNode("/SettingsBlock/ModSettings/" + name) != null;
        }

        private static string Bits() { return BitsOf(LuminousPigmentSettings.familyEnabled); }

        private static string BitsOf(bool[] e)
        {
            if (e == null) return "null";
            var sb = new StringBuilder();
            foreach (bool x in e) sb.Append(x ? '1' : '0');
            return sb.ToString();
        }

        private static string Kv(string k, string v) { return S(k) + ":" + S(v); }

        private static string Json(bool ok, string error, List<string> rows)
        {
            var sb = new StringBuilder("{\"success\":").Append(ok ? "true" : "false");
            if (error != null) sb.Append(",\"error\":").Append(S(error));
            if (rows != null) foreach (string row in rows) sb.Append(',').Append(row);
            return sb.Append('}').ToString();
        }

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
