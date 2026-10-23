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
        public Game Game;          // the game it was pinned in: map uniqueIDs restart per game, so a label never crosses
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
        private static Map _mapAtLoad;     // the map current when a load was requested: the sidecar waits for a NEW one
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
                MapId = map.uniqueID, Game = Current.Game, X = x, Z = z, Text = f[2], SubRaw = raw,
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
            var mine = Labels.Where(l => l.MapId == map.uniqueID && l.Game == Current.Game).ToList();
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
            Labels.RemoveAll(l => l.MapId == map.uniqueID || l.Game != Current.Game);
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
            _mapAtLoad = Find.CurrentMap;
        }

        private static void TryPendingSidecar()
        {
            // LoadGame only QUEUES the load: until it runs, the old map is still current and still Playing
            if (PendingSave == null || Current.ProgramState != ProgramState.Playing || Find.CurrentMap == null ||
                Find.CurrentMap == _mapAtLoad) return;
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
                try
                {
                foreach (JawaReviewLabel l in Labels)
                {
                    if (l.MapId != id || l.Game != Current.Game) continue;
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
                }
                finally
                {
                    Text.Font = oldFont;
                    Text.Anchor = oldAnchor;
                    GUI.color = oldColor;
                }
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
                    removed = L.RemoveAll(l => (l.Game != Current.Game) ||
                                               (l.MapId == map.uniqueID && (string.IsNullOrEmpty(tag) || l.Tag == tag)));
                }
                else if (act == "show" || act == "hide")
                {
                    JawaBenchReviewLabelDrawer.Visible = act == "show";
                }
                else if (act != "list")
                {
                    return Fail("Unknown action '" + action + "'. Use add, clear, list, show, hide, save_sidecar or load_sidecar.");
                }
                var mine = L.Where(l => l.MapId == map.uniqueID && l.Game == Current.Game).ToList();
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

        // ---------------------------------------------------------------------------------------- review signs
        // SIGNS IN THE SAVE ITSELF (BENCH, 2026-10-15: the signs "must survive a plain load by the owner with no agent
        // tool touching the game first"). The overlay labels above cannot: this assembly is loaded by RimBridgeServer
        // from BridgeTools/, NOT as a mod, so GenTypes (Assembly-CSharp + RunningMods' assemblies, decompiled 1.6
        // GenTypes.AllActiveAssemblies) never sees its classes - a MapComponent here would never be constructed and a
        // save naming it would log "Could not find class" - and none of its code runs before the first jawa/ call.
        // So a sign is a VANILLA object: a Core 1.5+ Novel (Verse.Book) whose own scribed fields carry the text -
        // title (its label: shown when the mouse is over it and on the inspect pane) and descriptionFlavor + description
        // (its info card, the i button). Forbidden, so no colonist reads or hauls it. Nothing of ours is in the save.
        private const string SignDef = "Novel";
        // STATION_SIGNS_FIX_LOOK_LIKE_BOOKS: FlowWorks' Book-class signboard; Novel is the fallback when it is not loaded.
        private const string SignBoardDef = "RM_StationSign";

        [Tool(
            "jawa/review_sign",
            Description = "DEV ONLY (human review maps). In-save signs that need no mod and no bridge to read: each is a " +
                "vanilla Novel (Verse.Book) whose title and description ARE the sign, spawned forbidden. action=place: " +
                "ops = newline-separated 'x|z|title|body' (body may hold the escape \\n for line breaks). action=clear: " +
                "destroys every Book on the current map whose title starts with 'prefix' (default 'SIGN '). action=list: " +
                "returns them. Mouse-over shows the title; the info card shows the body.",
            ResultDescription = "success, placed[] {id,x,z}, refused[], removed, count, signs[] for list.")]
        public static async Task<object> ReviewSign(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "place | clear | list")] string action = "list",
            [ToolParameter(Description = "place: newline-separated 'x|z|title|body'")] string ops = null,
            [ToolParameter(Description = "clear/list: title prefix that marks a sign (default 'SIGN ')")] string prefix = "SIGN ")
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                ThingDef novel = DefDatabase<ThingDef>.GetNamedSilentFail(SignDef);
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(SignBoardDef) ?? novel;
                if (def == null) return Fail("ThingDef " + SignDef + " not found (Core 1.5+).");
                var fTitle = AccessTools.Field(typeof(Book), "title");
                var fFlavor = AccessTools.Field(typeof(Book), "descriptionFlavor");
                var fDesc = AccessTools.Field(typeof(Book), "description");
                var fInval = AccessTools.Field(typeof(Book), "descCanBeInvalidated");
                if (fTitle == null || fFlavor == null || fDesc == null || fInval == null)
                    return Fail("Verse.Book fields title/descriptionFlavor/description/descCanBeInvalidated not found.");
                string pre = prefix ?? "SIGN ";
                string act = (action ?? "list").Trim().ToLowerInvariant();
                var placed = new List<object>();
                var refused = new List<string>();
                int removed = 0;
                Func<List<Book>> mine = () => map.listerThings.ThingsOfDef(def).Concat(
                        novel != null && novel != def ? map.listerThings.ThingsOfDef(novel) : new List<Thing>()).OfType<Book>()
                    .Where(b => (b.Title ?? "").StartsWith(pre, StringComparison.Ordinal)).ToList();
                if (act == "place")
                {
                    if (string.IsNullOrEmpty(ops)) return Fail("action=place needs ops.");
                    foreach (string raw in ops.Split('\n'))
                    {
                        string line = raw.Trim('\r', ' ');
                        if (line.Length == 0) continue;
                        string[] f = line.Split(new[] { '|' }, 4);
                        if (f.Length < 3 || !int.TryParse(f[0], NumberStyles.Integer, CultureInfo.InvariantCulture, out int x)
                            || !int.TryParse(f[1], NumberStyles.Integer, CultureInfo.InvariantCulture, out int z))
                        { refused.Add(line + " -> need x|z|title|body"); continue; }
                        var cell = new IntVec3(x, 0, z);
                        if (!cell.InBounds(map)) { refused.Add(line + " -> cell out of bounds"); continue; }
                        string title = f[2];
                        string body = (f.Length > 3 ? f[3] : "").Replace("\\n", "\n");
                        var book = (Book)ThingMaker.MakeThing(def);     // PostMake -> quality -> GenerateBook: overwritten below
                        fTitle.SetValue(book, title);
                        fFlavor.SetValue(book, body);
                        fDesc.SetValue(book, title + "\n\n" + body);
                        fInval.SetValue(book, false);
                        // BARREL_PAIR_FIX_SIZE_MISMATCH: vanilla draws every item 0.8x when its cell holds more than one
                        // (Graphic.Print, MultipleItemsPerCellDrawn), so a sign dropped on a staged barrel shrank it next to
                        // its twin. Put the sign on the nearest walkable cell that holds no item.
                        IntVec3 target = cell;
                        Func<IntVec3, bool> itemFree = c => c.InBounds(map) && c.Walkable(map)
                            && !c.GetThingList(map).Any(t => t.def.category == ThingCategory.Item);
                        if (!itemFree(cell))
                        {
                            foreach (IntVec3 c in GenRadial.RadialCellsAround(cell, 8f, false))
                                if (itemFree(c)) { target = c; break; }
                        }
                        if (!GenPlace.TryPlaceThing(book, target, map, ThingPlaceMode.Direct) &&
                            !GenPlace.TryPlaceThing(book, cell, map, ThingPlaceMode.Near))
                        {
                            if (!book.Destroyed) book.Destroy(DestroyMode.Vanish);
                            refused.Add(line + " -> could not place");
                            continue;
                        }
                        RimWorld.ForbidUtility.SetForbidden(book, true, warnOnFail: false);
                        placed.Add(new { id = book.ThingID, x = book.Position.x, z = book.Position.z, moved = book.Position != cell });
                    }
                }
                else if (act == "clear")
                {
                    foreach (Book b in mine()) { b.Destroy(DestroyMode.Vanish); removed++; }
                }
                else if (act != "list")
                {
                    return Fail("Unknown action '" + action + "'. Use place, clear or list.");
                }
                var now = mine();
                return (object)new
                {
                    success = refused.Count == 0,
                    action = act,
                    placed, refused, removed,
                    count = now.Count,
                    signs = act == "list" ? now.Select(b => new { id = b.ThingID, x = b.Position.x, z = b.Position.z, title = b.Title }).ToList() : null,
                    ticksGame = TicksGameSafe()
                };
            });
        }
    }
}
