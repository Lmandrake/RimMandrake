// JawaBenchTpsSettings.cs - tps_settings.json (the companion's Mod Settings stand-in).
// ⛔ NO Verse/Unity/Harmony: compiled into the offline harness too (BRIDGE_TPS_REVIEW2_FIXES_1, MUST 13).

using System;
using System.Collections.Generic;
using System.Text;
using System.Globalization;
using System.IO;
using System.Text.RegularExpressions;
using M = JawaBench.BridgeTools.JawaBenchTpsMath;

namespace JawaBench.BridgeTools
{
    internal sealed class JawaBenchTpsSettings
    {
        public bool Sampler = true, Attribution = true, Watchdog = true, ArchivePlayerLog = true;
        public double RetentionDays = M.RetentionDays;
        public double RetentionMB = M.RetentionBytes / 1048576.0;
        public double LogRetentionMB = M.LogRetentionBytes / 1048576.0;

        /// <summary>
        /// Read once, at sampler install: a change takes effect at the next game launch (MUST 13 reload policy).
        /// The file must be ONE flat JSON object of booleans, finite numbers, strings or null - parsed strictly:
        /// a duplicate key, a nested object/array, a truncated document or number, a non-finite number or a
        /// wrongly-typed known key makes the WHOLE file invalid, and the shipped defaults are used with the
        /// reason in `note` (written to the session row). Retention values can only GROW from the shipped
        /// defaults (the doc's promise), and are capped at sane maxima; both are stated in `note`.
        /// </summary>
        internal static JawaBenchTpsSettings Load(string dir, out string note)
        {
            var s = new JawaBenchTpsSettings();
            string p = Path.Combine(dir, "tps_settings.json");
            note = null;
            try
            {
                if (!File.Exists(p))
                {
                    File.WriteAllText(p, s.ToJson() + "\n");
                    note = "wrote defaults";
                    return s;
                }
                string t = File.ReadAllText(p);
                Dictionary<string, object> kv;
                string err = ParseFlat(t, out kv);
                if (err == null) err = Apply(s, kv, out note);
                if (err != null)
                {
                    note = "settings invalid (" + err + "): shipped defaults used";
                    return new JawaBenchTpsSettings();
                }
            }
            catch (Exception e) { note = "settings unreadable, defaults used: " + e.Message; return new JawaBenchTpsSettings(); }
            return s;
        }

        private static string Apply(JawaBenchTpsSettings s, Dictionary<string, object> kv, out string note)
        {
            note = null;
            var notes = new List<string>();
            foreach (var e in kv)
            {
                switch (e.Key)
                {
                    case "sampler": case "attribution": case "watchdog": case "archivePlayerLog":
                        if (!(e.Value is bool)) return e.Key + " is not true/false";
                        bool b = (bool)e.Value;
                        if (e.Key == "sampler") s.Sampler = b;
                        else if (e.Key == "attribution") s.Attribution = b;
                        else if (e.Key == "watchdog") s.Watchdog = b;
                        else s.ArchivePlayerLog = b;
                        break;
                    case "retentionDays": case "retentionMB": case "logRetentionMB":
                        if (!(e.Value is double)) return e.Key + " is not a number";
                        double v = (double)e.Value, lo, hi;
                        if (e.Key == "retentionDays") { lo = M.RetentionDays; hi = 3650; }
                        else if (e.Key == "retentionMB") { lo = M.RetentionBytes / 1048576.0; hi = 1048576; }
                        else { lo = M.LogRetentionBytes / 1048576.0; hi = 1048576; }
                        if (v < lo) { notes.Add(e.Key + " " + M.F(v, 2) + " raised to " + M.F(lo, 2) + " (retention can only grow)"); v = lo; }
                        if (v > hi) { notes.Add(e.Key + " " + M.F(v, 2) + " capped at " + M.F(hi, 2)); v = hi; }
                        if (e.Key == "retentionDays") s.RetentionDays = v;
                        else if (e.Key == "retentionMB") s.RetentionMB = v;
                        else s.LogRetentionMB = v;
                        break;
                    case "_doc": case "v":
                        break;
                    default:
                        notes.Add("unknown key " + e.Key + " ignored");
                        break;
                }
            }
            if (notes.Count > 0) note = string.Join("; ", notes);
            return null;
        }

        /// <summary>Strict parser for ONE flat JSON object. Returns an error, or null with the values (bool,
        /// double, string, or null) in <paramref name="kv"/>.</summary>
        internal static string ParseFlat(string t, out Dictionary<string, object> kv)
        {
            kv = new Dictionary<string, object>(StringComparer.Ordinal);
            int i = 0;
            Ws(t, ref i);
            if (i >= t.Length || t[i] != '{') return "not a JSON object";
            i++;
            Ws(t, ref i);
            if (i < t.Length && t[i] == '}') { i++; Ws(t, ref i); return i == t.Length ? null : "trailing text"; }
            while (true)
            {
                Ws(t, ref i);
                string k;
                string e = Str(t, ref i, out k);
                if (e != null) return e;
                Ws(t, ref i);
                if (i >= t.Length || t[i] != ':') return "expected ':' after " + k;
                i++;
                Ws(t, ref i);
                if (i >= t.Length) return "truncated after " + k;
                object v;
                char c = t[i];
                if (c == '"') { string sv; e = Str(t, ref i, out sv); if (e != null) return e; v = sv; }
                else if (c == '{' || c == '[') return "nested value for " + k;
                else if (string.CompareOrdinal(t, i, "true", 0, 4) == 0) { v = true; i += 4; }
                else if (string.CompareOrdinal(t, i, "false", 0, 5) == 0) { v = false; i += 5; }
                else if (string.CompareOrdinal(t, i, "null", 0, 4) == 0) { v = null; i += 4; }
                else
                {
                    var m = Regex.Match(t.Substring(i), "^-?(0|[1-9][0-9]*)(\\.[0-9]+)?([eE][+-]?[0-9]+)?");
                    if (!m.Success || m.Length == 0) return "bad value for " + k;
                    double d;
                    if (!double.TryParse(m.Value, NumberStyles.Float, CultureInfo.InvariantCulture, out d) ||
                        double.IsNaN(d) || double.IsInfinity(d)) return "non-finite number for " + k;
                    i += m.Length;
                    if (i < t.Length && (char.IsLetterOrDigit(t[i]) || t[i] == '.')) return "malformed number for " + k;
                    v = d;
                }
                if (kv.ContainsKey(k)) return "duplicate key " + k;
                kv[k] = v;
                Ws(t, ref i);
                if (i >= t.Length) return "truncated document";
                if (t[i] == ',') { i++; continue; }
                if (t[i] == '}') { i++; Ws(t, ref i); return i == t.Length ? null : "trailing text"; }
                return "expected ',' or '}' after " + k;
            }
        }

        private static void Ws(string t, ref int i) { while (i < t.Length && char.IsWhiteSpace(t[i])) i++; }

        private static string Str(string t, ref int i, out string s)
        {
            s = null;
            if (i >= t.Length || t[i] != '"') return "expected a string";
            var sb = new StringBuilder();
            i++;
            while (i < t.Length)
            {
                char c = t[i++];
                if (c == '"') { s = sb.ToString(); return null; }
                if (c == '\\')
                {
                    if (i >= t.Length) break;
                    char x = t[i++];
                    switch (x)
                    {
                        case '"': sb.Append('"'); break;
                        case '\\': sb.Append('\\'); break;
                        case '/': sb.Append('/'); break;
                        case 'n': sb.Append('\n'); break;
                        case 't': sb.Append('\t'); break;
                        case 'r': sb.Append('\r'); break;
                        case 'b': sb.Append('\b'); break;
                        case 'f': sb.Append('\f'); break;
                        case 'u':
                            if (i + 4 > t.Length) return "truncated escape";
                            int cp;
                            if (!int.TryParse(t.Substring(i, 4), NumberStyles.HexNumber, CultureInfo.InvariantCulture, out cp)) return "bad escape";
                            sb.Append((char)cp); i += 4; break;
                        default: return "bad escape";
                    }
                }
                else if (c < 0x20) return "control character in string";
                else sb.Append(c);
            }
            return "truncated string";
        }

        internal string ToJson()
        {
            return "{\"sampler\":" + B(Sampler) + ",\"attribution\":" + B(Attribution) + ",\"watchdog\":" + B(Watchdog) +
                   ",\"archivePlayerLog\":" + B(ArchivePlayerLog) + ",\"retentionDays\":" + M.F(RetentionDays, 2) +
                   ",\"retentionMB\":" + M.F(RetentionMB, 1) + ",\"logRetentionMB\":" + M.F(LogRetentionMB, 1) +
                   ",\"_doc\":\"design/RimMandrake/tps_record.md - defaults are the shipped behaviour; retention can only grow; read at game launch\"}";
        }

        private static string B(bool b) => b ? "true" : "false";
    }
}
