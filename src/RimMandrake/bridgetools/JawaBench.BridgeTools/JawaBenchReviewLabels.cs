// JawaBenchReviewLabels.cs - floating text labels pinned to map cells, for human review maps.
//
// Owner, 2026-10-04: a "for the human" Northstar review configuration - a well presented tilemap with every
// station labelled IN WORLD. This is the dev-only labeller (never in a shipped mod).
//
// How it draws: a Harmony postfix on RimWorld.MapInterface.MapInterfaceOnGUI_BeforeMainTabs (decompiled 1.6:
// runs every OnGUI while a map is drawn, after MapComponentOnGUI) projects each label's cell centre with
// Vector3.MapToUIPosition and draws a dark box plus text. Installed lazily by the first jawa/ call of a session (JawaBenchInit) or review_label call.
//
// Deliberately NOT a MapComponent/GameComponent: those are found by reflection over every loaded assembly and
// are WRITTEN INTO THE SAVE, so a review save would carry a dev-assembly class name. Labels are process memory,
// keyed by map uniqueID: they survive pause, camera moves and save (they are simply not in it).
//
// SIGNS THAT COME BACK WITH THE SAVE (owner, 2026-10-15: "I need text signs added to the savegame to tell me what to
// DO at each station"). The save stays clean; the labels travel in a SIDECAR beside it:
//     <SaveDataFolder>/JawaBenchReviewSigns/<saveName>.txt   (header '# map <uniqueID>', then one add-op per line)
// A postfix on GameDataSaveLoader.SaveGame(string) writes it whenever the saved map carries labels (any save: the
// review builder's keeper, the owner's own re-save, an autosave); a prefix on LoadGame(string) remembers the name, and
// the first drawn frame of the loaded map reads the sidecar back. modcheck/reviewmap.write_signs writes the same file
// offline. ⚠️ All three hooks are installed by the first jawa/ call of the session (JawaBenchInit): a save loaded
// before ANY jawa/ call comes up bare, and the builder's --labels puts the labels back.
// A sub line may hold the two-character escape \n: each one is a line break (a sign: LOOK / DO / DECIDE lines). When
// the camera is zoomed out (a cell under 28 px) only the sub's first line is drawn, so signs never carpet the map.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using HarmonyLib;
using RimBridgeServer.Sdk;
using UnityEngine;
using RimWorld.Planet;
using Verse;

namespace JawaBench.BridgeTools
{
    internal sealed class JawaReviewLabel
    {
        public int MapId;
        public int X, Z;
        public string Text, Sub, Tag, SubRaw, SizeName;
        public Color Color;
        public GameFont Font;
    }

    internal static class JawaBenchReviewLabelDrawer
    {
        internal static readonly List<JawaReviewLabel> Labels = new List<JawaReviewLabel>();
        internal static bool Installed;
        internal static string InstallError;
        internal static int Draws;
        internal static bool Visible = true;
        private static bool _attempted;
        private static readonly Color Bg = new Color(0.10f, 0.07f, 0.04f, 0.82f);
        private static readonly Color SubColor = new Color(0.88f, 0.84f, 0.76f, 1f);
        internal static bool SidecarHooks;
        internal static string SidecarError, PendingSave, LastSidecarRead, LastSidecarWritten;
        internal static int LastSidecarCount;
        private const float SignMinCellPx = 28f;

        internal static string SidecarDir => Path.Combine(GenFilePaths.SaveDataFolderPath, "JawaBenchReviewSigns");

        internal static string SidecarPath(string saveName)
        {
            foreach (char c in Path.GetInvalidFileNameChars()) saveName = saveName.Replace(c, '_');
            return Path.Combine(SidecarDir, saveName + ".txt");
        }

        internal static string OpLine(JawaReviewLabel l)
        {
            return l.X.ToString(CultureInfo.InvariantCulture) + "|" + l.Z.ToString(CultureInfo.InvariantCulture) + "|" +
                   l.Text + "|" + (l.SubRaw ?? "") + "|#" + ColorUtility.ToHtmlStringRGB(l.Color) + "|" +
                   (l.SizeName ?? "medium") + "|" + (l.Tag ?? "");
        }

        /// <summary>Parse one add-op line onto a map. Returns null on success, else the refusal.</summary>
        internal static string AddOp(Map map, string line, string defaultTag)
        {
            string[] f = line.Split('|');
            if (f.Length < 3 || !int.TryParse(f[0], NumberStyles.Integer, CultureInfo.InvariantCulture, out int x)
                || !int.TryParse(f[1], NumberStyles.Integer, CultureInfo.InvariantCulture, out int z))
                return "need x|z|text";
            if (!new IntVec3(x, 0, z).InBounds(map)) return "cell out of bounds";
            Color col = new Color(1f, 0.82f, 0.50f, 1f);
            if (f.Length > 4 && f[4].Length > 0 && !ColorUtility.TryParseHtmlString(f[4], out col)) return "bad colour " + f[4];
            GameFont font = GameFont.Medium;
            string sz = "medium";
            if (f.Length > 5 && f[5].Length > 0)
            {
                sz = f[5].ToLowerInvariant();
                if (sz == "tiny") font = GameFont.Tiny;
                else if (sz == "small") font = GameFont.Small;
                else if (sz != "medium") return "size must be tiny/small/medium";
            }
            string raw = f.Length > 3 ? f[3] : null;
            Labels.Add(new JawaReviewLabel
            {
                MapId = map.uniqueID, X = x, Z = z, Text = f[2], SubRaw = raw,
                Sub = raw == null ? null : raw.Replace("\\n", "\n"),
                Color = col, Font = font, SizeName = sz,
                Tag = f.Length > 6 && f[6].Length > 0 ? f[6] : (defaultTag ?? "")
            });
            return null;
        }

        /// <summary>Write this map's labels beside the save. Returns the count written (0 = no file written).</summary>
        internal static int WriteSidecar(string saveName, Map map)
        {
            if (map == null || string.IsNullOrEmpty(saveName)) return 0;
            var mine = Labels.Where(l => l.MapId == map.uniqueID).ToList();
            if (mine.Count == 0) return 0;
            Directory.CreateDirectory(SidecarDir);
            var lines = new List<string> { "# map " + map.uniqueID.ToString(CultureInfo.InvariantCulture) };
            lines.AddRange(mine.Select(OpLine));
            File.WriteAllLines(SidecarPath(saveName), lines);
            LastSidecarWritten = saveName;
            return mine.Count;
        }

        /// <summary>Read a sidecar onto its map (the header's map id when it is loaded, else the current map), replacing
        /// that map's labels. Returns labels added, or -1 when there is no sidecar.</summary>
        internal static int ReadSidecar(string saveName)
        {
            string p = SidecarPath(saveName);
            if (!File.Exists(p)) return -1;
            string[] lines = File.ReadAllLines(p);
            Map map = Find.CurrentMap;
            if (lines.Length > 0 && lines[0].StartsWith("# map ") &&
                int.TryParse(lines[0].Substring(6).Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out int mid))
                map = Find.Maps.FirstOrDefault(m => m.uniqueID == mid) ?? map;
            if (map == null) return -1;
            Labels.RemoveAll(l => l.MapId == map.uniqueID);
            int n = 0;
            foreach (string raw in lines)
            {
                string line = raw.Trim('\r', ' ');
                if (line.Length == 0 || line.StartsWith("#")) continue;
                if (AddOp(map, line, "") == null) n++;
            }
            LastSidecarRead = saveName;
            LastSidecarCount = n;
            return n;
        }

        private static void SavePostfix(string fileName)
        {
            try { WriteSidecar(fileName, Find.CurrentMap); }
            catch (Exception e) { SidecarError = "write " + fileName + ": " + e.GetType().Name + ": " + e.Message; }
        }

        private static void LoadPrefix(string saveFileName)
        {
            // the old game's labels go with it: map uniqueIDs restart per save (a fresh map 0 would inherit them)
            Labels.Clear();
            PendingSave = saveFileName;
        }

        private static void TryPendingSidecar()
        {
            if (PendingSave == null || Current.ProgramState != ProgramState.Playing || Find.CurrentMap == null) return;
            string name = PendingSave;
            PendingSave = null;
            try { ReadSidecar(name); }
            catch (Exception e) { SidecarError = "read " + name + ": " + e.GetType().Name + ": " + e.Message; }
        }

        internal static void Install()
        {
            if (_attempted) return;
            _attempted = true;
            try
            {
                var t = AccessTools.TypeByName("RimWorld.MapInterface");
                var m = t == null ? null : AccessTools.Method(t, "MapInterfaceOnGUI_BeforeMainTabs");
                if (m == null) { InstallError = "RimWorld.MapInterface.MapInterfaceOnGUI_BeforeMainTabs not found"; return; }
                var h = new Harmony("mandrake.jawabench.reviewlabels");
                const System.Reflection.BindingFlags F = System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic;
                h.Patch(m, postfix: new HarmonyMethod(typeof(JawaBenchReviewLabelDrawer).GetMethod("Postfix", F)));
                Installed = true;
                try
                {
                    var save = AccessTools.Method(typeof(GameDataSaveLoader), nameof(GameDataSaveLoader.SaveGame), new[] { typeof(string) });
                    var load = AccessTools.Method(typeof(GameDataSaveLoader), nameof(GameDataSaveLoader.LoadGame), new[] { typeof(string) });
                    if (save == null || load == null) { SidecarError = "GameDataSaveLoader.SaveGame/LoadGame(string) not found"; return; }
                    h.Patch(save, postfix: new HarmonyMethod(typeof(JawaBenchReviewLabelDrawer).GetMethod("SavePostfix", F)));
                    h.Patch(load, prefix: new HarmonyMethod(typeof(JawaBenchReviewLabelDrawer).GetMethod("LoadPrefix", F)));
                    SidecarHooks = true;
                }
                catch (Exception e2) { SidecarError = "sidecar hooks: " + e2.GetType().Name + ": " + e2.Message; }
            }
            catch (Exception e) { InstallError = e.GetType().Name + ": " + e.Message; }
        }

        private static void Postfix()
        {
            try
            {
                if (Event.current.type != EventType.Repaint) return;
                TryPendingSidecar();
                if (!Visible || Labels.Count == 0) return;
                Map map = Find.CurrentMap;
                if (map == null || !WorldRendererUtility.DrawingMap) return;
                int id = map.uniqueID;
                Vector2 c0 = new Vector3(0.5f, 0f, 0.5f).MapToUIPosition();
                Vector2 c1 = new Vector3(1.5f, 0f, 0.5f).MapToUIPosition();
                bool zoomedOut = Mathf.Abs(c1.x - c0.x) < SignMinCellPx;
                GameFont oldFont = Text.Font;
                TextAnchor oldAnchor = Text.Anchor;
                Color oldColor = GUI.color;
                foreach (JawaReviewLabel l in Labels)
                {
                    if (l.MapId != id) continue;
                    Vector2 p = new Vector3(l.X + 0.5f, 0f, l.Z + 0.5f).MapToUIPosition();
                    if (p.x < -400 || p.y < -100 || p.x > UI.screenWidth + 400 || p.y > UI.screenHeight + 100) continue;
                    Text.Font = l.Font;
                    Vector2 s1 = Text.CalcSize(l.Text);
                    Vector2 s2 = Vector2.zero;
                    string sub = l.Sub;
                    if (zoomedOut && sub != null && sub.IndexOf('\n') >= 0) sub = sub.Substring(0, sub.IndexOf('\n'));
                    if (!string.IsNullOrEmpty(sub)) { Text.Font = GameFont.Small; s2 = Text.CalcSize(sub); }
                    float w = Mathf.Max(s1.x, s2.x) + 14f, hgt = s1.y + s2.y + 6f;
                    var r = new Rect(p.x - w / 2f, p.y - hgt / 2f, w, hgt);
                    Widgets.DrawBoxSolid(r, Bg);
                    GUI.color = l.Color;
                    Widgets.DrawBox(r, 1);
                    Text.Anchor = TextAnchor.UpperCenter;
                    Text.Font = l.Font;
                    Widgets.Label(new Rect(r.x, r.y + 2f, w, s1.y + 2f), l.Text);
                    if (s2.y > 0)
                    {
                        GUI.color = SubColor;
                        Text.Font = GameFont.Small;
                        Widgets.Label(new Rect(r.x, r.y + 2f + s1.y, w, s2.y + 2f), sub);
                    }
                    GUI.color = Color.white;
                }
                Text.Font = oldFont;
                Text.Anchor = oldAnchor;
                GUI.color = oldColor;
                Draws++;
            }
            catch (Exception e)
            {
                Visible = false;      // a throwing OnGUI postfix would spam every frame: switch off, say why
                InstallError = "drawer disabled after exception: " + e.GetType().Name + ": " + e.Message;
            }
        }
    }

    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/review_label",
            Description = "DEV ONLY (human review maps). Floating text labels pinned to map cells, drawn every frame " +
                "over the current map until cleared. action=add: ops is newline-separated label lines " +
                "'x|z|text[|sub[|#rrggbb[|tiny,small,medium[|tag]]]]' (sub = a smaller second line; default colour " +
                "#ffd27f, size medium). action=clear: removes the labels of the current map whose tag equals 'tag' (all " +
                "of this map's labels when tag is empty). action=list: returns them. action=show/hide toggles drawing. " +
                "Labels live in process memory only: NOT saved into the savegame, gone after a restart or a load (re-add " +
                "them), EXCEPT that every SaveGame writes this map's labels to a sidecar " +
                "(<SaveDataFolder>/JawaBenchReviewSigns/<save>.txt) and loading that save reads them back. A sub may hold " +
                "the escape \\n for line breaks (signs); zoomed out, only its first line draws. action=save_sidecar / " +
                "load_sidecar (saveName) does that by hand. Refuses an op with a cell out of bounds and reports each refusal.",
            ResultDescription = "success, installed, added, refused[], removed, count (this map), labels[] for list, draws.")]
        public static async Task<object> ReviewLabel(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "add | clear | list | show | hide")] string action = "list",
            [ToolParameter(Description = "add: newline-separated 'x|z|text[|sub[|#rrggbb[|size[|tag]]]]'")] string ops = null,
            [ToolParameter(Description = "clear: only labels with this tag (empty = all on this map); add: default tag for ops without one")] string tag = null,
            [ToolParameter(Description = "save_sidecar / load_sidecar: the save name (no .rws) whose sign sidecar to write from / read onto this map")] string saveName = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                JawaBenchReviewLabelDrawer.Install();
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                var L = JawaBenchReviewLabelDrawer.Labels;
                string act = (action ?? "list").Trim().ToLowerInvariant();
                int added = 0, removed = 0;
                var refused = new List<string>();
                if (act == "add")
                {
                    if (string.IsNullOrEmpty(ops)) return Fail("action=add needs ops.");
                    foreach (string raw in ops.Split('\n'))
                    {
                        string line = raw.Trim('\r', ' ');
                        if (line.Length == 0) continue;
                        string why = JawaBenchReviewLabelDrawer.AddOp(map, line, tag);
                        if (why == null) added++;
                        else refused.Add(line + " -> " + why);
                    }
                }
                else if (act == "save_sidecar" || act == "load_sidecar")
                {
                    if (string.IsNullOrEmpty(saveName)) return Fail("action=" + act + " needs saveName.");
                    try
                    {
                        if (act == "save_sidecar") added = JawaBenchReviewLabelDrawer.WriteSidecar(saveName, map);
                        else
                        {
                            added = JawaBenchReviewLabelDrawer.ReadSidecar(saveName);
                            if (added < 0) return Fail("no sidecar at " + JawaBenchReviewLabelDrawer.SidecarPath(saveName));
                        }
                    }
                    catch (Exception e) { return Fail(act + ": " + e.GetType().Name + ": " + e.Message); }
                }
                else if (act == "clear")
                {
                    removed = L.RemoveAll(l => l.MapId == map.uniqueID && (string.IsNullOrEmpty(tag) || l.Tag == tag));
                }
                else if (act == "show" || act == "hide")
                {
                    JawaBenchReviewLabelDrawer.Visible = act == "show";
                }
                else if (act != "list")
                {
                    return Fail("Unknown action '" + action + "'. Use add, clear, list, show, hide, save_sidecar or load_sidecar.");
                }
                var mine = L.Where(l => l.MapId == map.uniqueID).ToList();
                return (object)new
                {
                    success = JawaBenchReviewLabelDrawer.Installed && refused.Count == 0,
                    action = act,
                    installed = JawaBenchReviewLabelDrawer.Installed,
                    installError = JawaBenchReviewLabelDrawer.InstallError,
                    sidecarHooks = JawaBenchReviewLabelDrawer.SidecarHooks,
                    sidecarError = JawaBenchReviewLabelDrawer.SidecarError,
                    sidecarDir = JawaBenchReviewLabelDrawer.SidecarDir,
                    lastSidecarRead = JawaBenchReviewLabelDrawer.LastSidecarRead,
                    lastSidecarCount = JawaBenchReviewLabelDrawer.LastSidecarCount,
                    lastSidecarWritten = JawaBenchReviewLabelDrawer.LastSidecarWritten,
                    visible = JawaBenchReviewLabelDrawer.Visible,
                    added, removed, refused,
                    count = mine.Count,
                    draws = JawaBenchReviewLabelDrawer.Draws,
                    labels = act == "list" ? mine.Select(l => new { x = l.X, z = l.Z, text = l.Text, sub = l.Sub, tag = l.Tag }).ToList() : null,
                    ticksGame = TicksGameSafe()
                };
            });
        }
    }
}
