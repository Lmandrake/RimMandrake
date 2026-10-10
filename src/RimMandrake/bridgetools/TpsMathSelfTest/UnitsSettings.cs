// tps_settings.json parsing (MUST 13): a malformed file must be REFUSED with a stated reason, never half-read.
using System.IO;
using Set = JawaBench.BridgeTools.JawaBenchTpsSettings;

namespace JawaBench.BridgeTools
{
    internal static partial class Units
    {
        private static Set LoadText(string text, out string note)
        {
            string d = TempDir();
            File.WriteAllText(Path.Combine(d, "tps_settings.json"), text);
            return Set.Load(d, out note);
        }

        private static void Refused(string label, string text, System.Func<Set, bool> isDefault)
        {
            string note;
            var s = LoadText(text, out note);
            Check(note != null && note.Contains("invalid") && isDefault(s),
                  label + ": expected REFUSED with defaults and an 'invalid' note, got note=" + (note ?? "null") +
                  " sampler=" + s.Sampler + " retentionDays=" + s.RetentionDays + " retentionMB=" + s.RetentionMB);
        }

        private static void T_SettingsStrict()
        {
            System.Func<Set, bool> dflt = s => s.Sampler && s.Attribution && s.RetentionDays == 7 && s.RetentionMB == 256;
            Refused("duplicate key", "{\"sampler\":true,\"sampler\":false}", dflt);
            Refused("nested key", "{\"x\":{\"sampler\":false}}", dflt);
            Refused("truncated document", "{\"sampler\":false, \"retentionDays\": 9", dflt);
            Refused("truncated number", "{\"retentionDays\": 1e}", dflt);
            Refused("not finite", "{\"retentionDays\": 1e999}", dflt);
            Refused("wrong type", "{\"sampler\":\"no\"}", dflt);
            string note;
            var ok = LoadText("{\"sampler\":true,\"retentionDays\":1.4e1,\"retentionMB\":512,\"_doc\":\"x\"}", out note);
            Check(ok.RetentionDays == 14 && ok.RetentionMB == 512 && (note == null || !note.Contains("invalid")),
                  "a valid file with exponent syntax is read exactly: days=" + ok.RetentionDays + " MB=" + ok.RetentionMB + " note=" + note);
            var shrink = LoadText("{\"retentionMB\":16,\"logRetentionMB\":16,\"retentionDays\":2}", out note);
            Check(shrink.RetentionMB == 256 && shrink.LogRetentionMB == 1024 && shrink.RetentionDays == 7 && note != null,
                  "retention can only GROW (doc): MB=" + shrink.RetentionMB + " logMB=" + shrink.LogRetentionMB +
                  " days=" + shrink.RetentionDays + " note=" + note);
        }
    }
}
