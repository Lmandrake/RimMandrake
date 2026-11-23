// T_LOOK_ICONS_OFFLINE (Gimme Some Slack 0.2.0, bar look_menu_icons, design/concepts/GimmeSomeSlack/record.json; owner walk
// 2026-11-20: "the 'change style' really needs some proper icons to represent the different options (true on ALL mods that
// use our style switches)").
// Each look the player can pick in a GSS look menu (the build menu's look choice and the Restyle menus) shows its own icon,
// the same picture in every menu: UI/Looks/<Look> (the picture every RimMandrake mod with these looks ships).
//
// What runs is the SHIPPED decision: ConduitStyles.MenuKeys (the entries of every look menu; ConduitStylePicker.MenuKeys is
// it) and ConduitStyles.LookIconPath (the icon of an entry; ConduitStylePicker.Icon asks it first). The oracle is the bar's
// wording: an entry's look is the text before its first '_' ("Modern_Orange" is a Modern entry), its icon UI/Looks/<that look>.
//
// Declared range (every entry the menus can show; it is finite, so it is read whole):
//   * the build menu of a conduit def (looks + Modern's Mix, Multi and five colours: 11 entries), of a switch (4 looks);
//   * the Restyle menus: "This item" on a conduit (11), on a switch, pole or bracket (4), "All connected" and "All on map" (11,
//     they repaint conduit), "This item" on a floor or wall lamp (the 4 looks; "Match its cable run" is no look, no icon owed);
//   * the four pictures on disk: each exists, is 256 px square (commissions.md), and no two are the same bytes.
// Left out (why): the drawn float menu itself (the running UI: sc_look_menu_icons, Stage 6); a texture that fails to load in
// the game (Icon then falls back to the strand or style art so an entry is never blank: a load failure, not a menu rule).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using RimMandrake.GimmeSomeSlack.Aerial;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class LookIconChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "look icons: " + msg);

        /// <summary>Every (menu, entry key) the GSS look menus show, from the shipped MenuKeys.</summary>
        internal static List<(string menu, string key)> Entries()
        {
            var e = new List<(string, string)>();
            foreach (string k in ConduitStyles.MenuKeys(true)) e.Add(("build menu, conduit", k));
            foreach (string k in ConduitStyles.MenuKeys(false)) e.Add(("build menu, switch or lamp", k));
            foreach (string k in ConduitStyles.MenuKeys(true)) e.Add(("Restyle: this item, conduit", k));
            foreach (string k in ConduitStyles.MenuKeys(false)) e.Add(("Restyle: this item, switch/pole/bracket", k));
            foreach (string k in ConduitStyles.MenuKeys(true)) e.Add(("Restyle: all connected", k));
            foreach (string k in ConduitStyles.MenuKeys(true)) e.Add(("Restyle: all on map", k));
            foreach (string k in AerialStyles.Looks) e.Add(("Restyle: this lamp", k));
            return e;
        }

        /// <summary>The oracle: the bar's look of an entry is its text before the first '_'.</summary>
        private static string LookOfEntry(string key) => key.Split('_')[0];

        /// <summary>Entries whose icon is not their look's icon under <paramref name="iconOf"/> (the shipped rule, or a planted one).</summary>
        internal static List<string> Wrong(List<(string menu, string key)> entries, Func<string, string> iconOf)
        {
            var bad = new List<string>();
            foreach ((string menu, string key) in entries)
            {
                string want = "RimMandrake/GimmeSomeSlack/UI/Looks/" + LookOfEntry(key);
                string got = iconOf(key);
                if (got != want) bad.Add(menu + " / " + key + ": icon " + (got ?? "none") + ", want " + want);
            }
            return bad;
        }

        public static void Run()
        {
            List<(string menu, string key)> entries = Entries();
            List<string> wrong = Wrong(entries, ConduitStyles.LookIconPath);
            Console.WriteLine("look icons: " + entries.Count + " menu entries over " + entries.Select(x => x.menu).Distinct().Count() + " menus; wrong icons " +
                              wrong.Count + " (limit 0)" + (wrong.Count > 0 ? "; first: " + wrong[0] : ""));
            Check(entries.Count >= 50, "the menus read " + entries.Count + " entries (instrument floor 50)");
            Check(wrong.Count == 0, "every look entry takes its look's icon UI/Looks/<Look> (" + wrong.Count + " wrong of " + entries.Count + ")");
            Check(AerialStyles.Looks.All(l => entries.Any(x => LookOfEntry(x.key) == l)), "every look appears in the menus");
            Check(ConduitStyles.LookIconPath("MatchRun") == null && ConduitStyles.LookIconPath(null) == null, "an entry that is no look gets no look icon");

            // can fail: the old rule (a conduit entry on its strand art) and a colour entry on its own colour's picture go red
            List<string> strand = Wrong(entries, k => ConduitStyles.TryParseKey(k, out string l, out string c) && c != null
                ? "RimMandrake/GimmeSomeSlack/Styles/" + l + "/Strand_" + c : ConduitStyles.LookIconPath(k));
            Check(strand.Count > 0, "can fail: Modern colour entries back on their strand art read red (" + strand.Count + " wrong)");
            List<string> colourIcon = Wrong(entries, k => k == "Modern_Multi" ? "RimMandrake/GimmeSomeSlack/UI/Looks/Multi" : ConduitStyles.LookIconPath(k));
            Check(colourIcon.Count > 0, "can fail: the one-colour-per-run entry on a picture of its own reads red (" + colourIcon.Count + " wrong)");

            Pictures();
            Wiring();
        }

        // ------------------------------------------------------------------ the four pictures
        internal static string ModRoot()
        {
            string dir = SwitchFlipChecks.AerialSourceDir();
            return dir == null ? null : Path.GetFullPath(Path.Combine(dir, "..", ".."));
        }

        /// <summary>The mod's Textures/: --textures (the stage holds no PNGs), else beside Source/.</summary>
        internal static string TexturesDir()
        {
            if (Program.TexturesDir != null) return Program.TexturesDir;
            string root = ModRoot();
            return root == null ? null : Path.Combine(root, "Textures");
        }

        internal static (int w, int h) PngSize(byte[] b) =>
            b.Length < 24 || b[1] != 'P' || b[2] != 'N' || b[3] != 'G' ? (0, 0)
                : ((b[16] << 24) | (b[17] << 16) | (b[18] << 8) | b[19], (b[20] << 24) | (b[21] << 16) | (b[22] << 8) | b[23]);

        private static void Pictures()
        {
            string tex = TexturesDir();
            Check(tex != null && Directory.Exists(tex), "found the mod's Textures/ (" + (tex ?? "no Source/Aerial, no --textures") + ")");
            if (tex == null || !Directory.Exists(tex)) return;
            var hashes = new Dictionary<string, string>();
            using (SHA256 sha = SHA256.Create())
                foreach (string look in AerialStyles.Looks)
                {
                    string rel = ConduitStyles.LookIconPath(look);
                    string f = Path.Combine(tex, rel.Replace('/', Path.DirectorySeparatorChar) + ".png");
                    bool ok = File.Exists(f);
                    Check(ok, "the " + look + " icon exists (" + rel + ".png)");
                    if (!ok) continue;
                    byte[] b = File.ReadAllBytes(f);
                    (int w, int h) = PngSize(b);
                    Check(w == 256 && h == 256, "the " + look + " icon is 256 px square (commissions.md), is " + w + "x" + h);
                    hashes[look] = Convert.ToBase64String(sha.ComputeHash(b));
                }
            Console.WriteLine("look icons: " + hashes.Count + " pictures read, " + hashes.Values.Distinct().Count() + " distinct");
            Check(hashes.Count == AerialStyles.Looks.Length && hashes.Values.Distinct().Count() == hashes.Count, "the four look icons are four different pictures");
        }

        // ------------------------------------------------------------------ the Verse side asks the shipped rule (source read)
        internal static string Body(string text, string head)
        {
            int i = text.IndexOf(head, StringComparison.Ordinal);
            if (i < 0) return "";
            int b = text.IndexOf('{', i), depth = 0;
            for (int j = b; j >= 0 && j < text.Length; j++)
            {
                if (text[j] == '{') depth++;
                else if (text[j] == '}' && --depth == 0) return text.Substring(b, j - b + 1);
            }
            return "";
        }

        /// <summary>The wiring faults in the picker's source (empty = wired as this check composes it).</summary>
        internal static List<string> WiringFaults(string picker)
        {
            var f = new List<string>();
            string icon = Body(picker, "public static Texture2D Icon(ThingDef d, string key)");
            int ask = icon.IndexOf("ConduitStyles.LookIconPath(key)", StringComparison.Ordinal);
            int ret = icon.IndexOf("if (lookIcon != null) return lookIcon;", StringComparison.Ordinal);
            int other = Math.Min(Idx(icon, "StyleFor("), Idx(icon, "StrandPathOf("));
            if (icon.Length == 0) f.Add("ConduitStylePicker.Icon(ThingDef, string) not found");
            else if (ask < 0 || ret < 0 || ret > other) f.Add("Icon does not return the look icon (ConduitStyles.LookIconPath) before any strand or style art");
            if (!Regex.IsMatch(picker, @"public static List<string> MenuKeys\(bool conduit\) => ConduitStyles\.MenuKeys\(conduit\);"))
                f.Add("the picker's MenuKeys is not ConduitStyles.MenuKeys");
            string menuFor = Body(picker, "public static List<FloatMenuOption> MenuFor(");
            if (!menuFor.Contains("new FloatMenuOption(label, () => Pick(des, k), Icon(d, key), Color.white)"))
                f.Add("the build menu's entries do not take Icon(d, key)");
            string look = Body(picker, "public static List<FloatMenuOption> LookMenu(");
            if (!look.Contains("() => runs.RestyleLamp(b, k, true), Icon(b.def, k), Color.white)"))
                f.Add("the lamp's Restyle entries do not take Icon(b.def, k)");
            if (!look.Contains("act, Icon(piece ? b.def : pc, key), Color.white)"))
                f.Add("the Restyle entries do not take Icon(..., key)");
            // every look entry built in the two menus carries an icon; only "Match its cable run" (no look) has none
            foreach (Match m in Regex.Matches(menuFor + look, @"new FloatMenuOption\(([^;]*)\);"))
                if (!m.Groups[1].Value.Contains("Icon(") && !m.Groups[1].Value.Contains("\"Match its cable run\""))
                    f.Add("a look menu entry with no icon: " + m.Value);
            return f;
        }

        private static int Idx(string s, string what) { int i = s.IndexOf(what, StringComparison.Ordinal); return i < 0 ? int.MaxValue : i; }

        private static void Wiring()
        {
            string dir = SwitchFlipChecks.AerialSourceDir();
            Check(dir != null, "found Source/Aerial to read the picker");
            if (dir == null) return;
            string picker = File.ReadAllText(Path.Combine(dir, "ConduitStylePicker.cs"));
            List<string> faults = WiringFaults(picker);
            foreach (string x in faults) Check(false, "wiring: " + x);
            Check(faults.Count == 0, "the build menu and Restyle menus show Icon(), and Icon asks ConduitStyles.LookIconPath first (" + faults.Count + " faults)");
            // can fail: the 0.1.1 Icon (strand art first, no look icon) reads red
            string old = Regex.Replace(picker, @"string iconPath = ConduitStyles\.LookIconPath\(key\);[^\n]*\n[^\n]*\n[^\n]*if \(lookIcon != null\) return lookIcon;", "");
            Check(old != picker && WiringFaults(old).Count > 0, "can fail: the picker without the look icon in Icon reads red");
        }
    }
}
