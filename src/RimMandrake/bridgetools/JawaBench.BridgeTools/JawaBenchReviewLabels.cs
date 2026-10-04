// JawaBenchReviewLabels.cs - floating text labels pinned to map cells, for human review maps.
//
// Owner, 2026-10-04: a "for the human" Northstar review configuration - a well presented tilemap with every
// station labelled IN WORLD. This is the dev-only labeller (never in a shipped mod).
//
// How it draws: a Harmony postfix on RimWorld.MapInterface.MapInterfaceOnGUI_BeforeMainTabs (decompiled 1.6:
// runs every OnGUI while a map is drawn, after MapComponentOnGUI) projects each label's cell centre with
// Vector3.MapToUIPosition and draws a dark box plus text. Installed lazily by the first review_label call.
//
// Deliberately NOT a MapComponent/GameComponent: those are found by reflection over every loaded assembly and
// are WRITTEN INTO THE SAVE, so a review save would carry a dev-assembly class name. Labels are process memory,
// keyed by map uniqueID: they survive pause, camera moves and save (they are simply not in it), and vanish on a
// game restart or a load. Re-run the review script's --labels to put them back.

using System;
using System.Collections.Generic;
using System.Globalization;
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
        public string Text, Sub, Tag;
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
                h.Patch(m, postfix: new HarmonyMethod(typeof(JawaBenchReviewLabelDrawer).GetMethod("Postfix",
                    System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic)));
                Installed = true;
            }
            catch (Exception e) { InstallError = e.GetType().Name + ": " + e.Message; }
        }

        private static void Postfix()
        {
            try
            {
                if (!Visible || Labels.Count == 0 || Event.current.type != EventType.Repaint) return;
                Map map = Find.CurrentMap;
                if (map == null || !WorldRendererUtility.DrawingMap) return;
                int id = map.uniqueID;
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
                    if (!string.IsNullOrEmpty(l.Sub)) { Text.Font = GameFont.Small; s2 = Text.CalcSize(l.Sub); }
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
                        Widgets.Label(new Rect(r.x, r.y + 2f + s1.y, w, s2.y + 2f), l.Sub);
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
                "them). Refuses an op with a cell out of bounds and reports each refusal.",
            ResultDescription = "success, installed, added, refused[], removed, count (this map), labels[] for list, draws.")]
        public static async Task<object> ReviewLabel(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "add | clear | list | show | hide")] string action = "list",
            [ToolParameter(Description = "add: newline-separated 'x|z|text[|sub[|#rrggbb[|size[|tag]]]]'")] string ops = null,
            [ToolParameter(Description = "clear: only labels with this tag (empty = all on this map); add: default tag for ops without one")] string tag = null)
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
                        string[] f = line.Split('|');
                        if (f.Length < 3 || !int.TryParse(f[0], NumberStyles.Integer, CultureInfo.InvariantCulture, out int x)
                            || !int.TryParse(f[1], NumberStyles.Integer, CultureInfo.InvariantCulture, out int z))
                        { refused.Add(line + " -> need x|z|text"); continue; }
                        if (!new IntVec3(x, 0, z).InBounds(map)) { refused.Add(line + " -> cell out of bounds"); continue; }
                        Color col = new Color(1f, 0.82f, 0.50f, 1f);
                        if (f.Length > 4 && f[4].Length > 0 && !ColorUtility.TryParseHtmlString(f[4], out col))
                        { refused.Add(line + " -> bad colour " + f[4]); continue; }
                        GameFont font = GameFont.Medium;
                        if (f.Length > 5 && f[5].Length > 0)
                        {
                            string sz = f[5].ToLowerInvariant();
                            if (sz == "tiny") font = GameFont.Tiny;
                            else if (sz == "small") font = GameFont.Small;
                            else if (sz != "medium") { refused.Add(line + " -> size must be tiny/small/medium"); continue; }
                        }
                        L.Add(new JawaReviewLabel
                        {
                            MapId = map.uniqueID, X = x, Z = z, Text = f[2], Sub = f.Length > 3 ? f[3] : null,
                            Color = col, Font = font, Tag = f.Length > 6 && f[6].Length > 0 ? f[6] : (tag ?? "")
                        });
                        added++;
                    }
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
                    return Fail("Unknown action '" + action + "'. Use add, clear, list, show or hide.");
                }
                var mine = L.Where(l => l.MapId == map.uniqueID).ToList();
                return (object)new
                {
                    success = JawaBenchReviewLabelDrawer.Installed && refused.Count == 0,
                    action = act,
                    installed = JawaBenchReviewLabelDrawer.Installed,
                    installError = JawaBenchReviewLabelDrawer.InstallError,
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
