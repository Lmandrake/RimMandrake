using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimMandrake.GimmeSomeSlack.Core;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>One styled cell as the cord layer reads it (stage 2).</summary>
    public sealed class CellStyle
    {
        public string Look, Colour;
        public bool Conduit;
    }

    /// <summary>
    /// Per-build style, STAGE 2: conduit runs (design/RimMandrake/messyconduit_style_per_build_design.md section 2, owner
    /// decisions 2026-10-04). Vanilla PowerConduit / WaterproofConduit / PowerSwitch get the engine's style field by guarded
    /// patch (Patches/RM_ConduitStyleable.xml) and carry one of the ThingStyleDefs in Defs/Aerial/RM_ConduitStyles.xml.
    /// This class adds, beside stage 1's StylePicker (which it leaves untouched):
    ///   * the build button's menu for conduit (4 looks, and for Modern: each colour, "one colour per run", "random mix")
    ///     and for the switch (4 looks); the designator style getter for these defs in every game mode;
    ///   * the switch drawn in its look, on and off (Building_PowerSwitch.Graphic postfix; legacy switches keep today's art);
    ///   * the vanilla floor lamp (StandingLamp, art round 5): same menu/getter/copy/Frame guard, NOT a run member (a lamp
    ///     ends a run); drawn by its ThingStyleDef's own graphic; unstyled (legacy) lamps keep vanilla art;
    ///   * the spawn hook that queues every new run member for the run rule (RM_MapComponent_ConduitRuns);
    ///   * the free "Restyle this run" gizmo on any member, and (round 6) "Restyle this lamp" on a floor lamp; a lamp hooked
    ///     to a run follows the run's Restyle unless it was given its own look (ConduitStyles.LampFollowsRun);
    ///   * the stage-1 copy-carries-style and Frame guard patches extended to these defs (StyleIndex flags).
    /// The cord layer reads <see cref="CellStyles"/> to pick each piece's material.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class ConduitStylePicker
    {
        private static readonly Dictionary<ThingDef, Dictionary<string, ThingStyleDef>> byDef = new Dictionary<ThingDef, Dictionary<string, ThingStyleDef>>();
        private static readonly Dictionary<ThingStyleDef, string[]> parsed = new Dictionary<ThingStyleDef, string[]>();
        private static readonly Dictionary<ThingDef, string> lastPicked = new Dictionary<ThingDef, string>();
        private static readonly HashSet<ThingDef> members = new HashSet<ThingDef>();
        private static readonly List<ThingDef> memberList = new List<ThingDef>();
        /// <summary>State read: style defs / defs missing, and defs that ended up WITHOUT the style field (patch skipped).</summary>
        public static readonly List<string> Missing = new List<string>();
        public static readonly List<string> NotStylable = new List<string>();
        public static int picks;

        /// <summary>The menu keys: the looks, plus Modern colour choices for conduit (Multi = one random colour per run).</summary>
        public static List<string> MenuKeys(bool conduit)
        {
            var l = new List<string>();
            foreach (string look in AerialStyles.Looks)
            {
                if (look != "Modern" || !conduit) { l.Add(look); continue; }
                l.Add(ConduitStyles.Key("Modern", ConduitStyles.Mix));
                l.Add(ConduitStyles.Key("Modern", ConduitStyles.Multi));
                foreach (string c in ConduitStyles.Colours) l.Add(ConduitStyles.Key("Modern", c));
            }
            return l;
        }

        static ConduitStylePicker()
        {
            StylePicker.IsStyled(null);                              // stage 1's registry and StyleIndex first
            var defs = new List<string>(ConduitStyles.ConduitDefs);
            defs.AddRange(ConduitStyles.SwitchDefs);
            defs.AddRange(ConduitStyles.LampDefs);
            foreach (string dn in defs)
            {
                ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(dn);
                if (d == null) { Missing.Add(dn); continue; }
                if (!d.CanBeStyled()) { NotStylable.Add(dn); continue; }
                var map = new Dictionary<string, ThingStyleDef>();
                foreach (string key in ConduitStyles.KeysFor(dn))
                {
                    string sn = dn + "_" + key;
                    ThingStyleDef s = DefDatabase<ThingStyleDef>.GetNamedSilentFail(sn);
                    if (s == null) { Missing.Add(sn); continue; }
                    map[key] = s;
                    ConduitStyles.TryParseKey(key, out string look, out string colour);
                    parsed[s] = new[] { look, colour };
                }
                byDef[d] = map;
            }
            foreach (string m in Missing) Log.Error("[GimmeSomeSlack] stage-2 style def missing: " + m);
            foreach (string m in NotStylable) Log.Warning("[GimmeSomeSlack] " + m + " has no style field (CompProperties_Styleable patch skipped?): its runs draw the default look");
            bool[] flags = StyleIndex.styled;
            foreach (ThingDef d in byDef.Keys) if (flags != null && d.index < flags.Length) flags[d.index] = true;
            foreach (string dn in AerialStyles.StyledDefs)
            {
                ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(dn);
                if (d != null) members.Add(d);
            }
            foreach (ThingDef d in byDef.Keys) if (!ConduitStyles.IsLampDef(d.defName)) members.Add(d);   // a lamp ends a run
            memberList.AddRange(members);
        }

        public static bool IsOurs(ThingDef d) => d != null && byDef.ContainsKey(d);
        public static bool IsMember(ThingDef d) => d != null && members.Contains(d);
        public static bool IsConduit(ThingDef d) => IsOurs(d) && ConduitStyles.IsConduitDef(d.defName);
        /// <summary>A styled floor lamp (registered: it carries the style field). Round 6: gets "Restyle this lamp".</summary>
        public static bool IsLamp(ThingDef d) => IsOurs(d) && ConduitStyles.IsLampDef(d.defName);
        public static IReadOnlyList<ThingDef> MemberDefs => memberList;

        public static ThingStyleDef StyleFor(ThingDef d, string key)
        {
            if (d == null || key == null) return null;
            if (byDef.TryGetValue(d, out Dictionary<string, ThingStyleDef> m)) return m.TryGetValue(key, out ThingStyleDef s) ? s : null;
            return AerialStyles.IsLook(key) ? StylePicker.StyleFor(d, key) : null;      // an anchor: the look alone
        }

        /// <summary>(look, colour) of a stored style: ours, or a stage-1 anchor style (colour null). Null look = none.</summary>
        public static string LookOf(ThingStyleDef s, out string colour)
        {
            colour = null;
            if (s == null) return null;
            if (parsed.TryGetValue(s, out string[] lc)) { colour = lc[1]; return lc[0]; }
            return StylePicker.LookOfStyle(s);
        }

        public static string RawLook(Thing t) => LookOf(StylePicker.RawStyle(t), out _);
        public static string RawColour(Thing t) { LookOf(StylePicker.RawStyle(t), out string c); return c; }

        /// <summary>The key a new button starts on: the default look (Mod Setting `style`); a Modern conduit button starts on
        /// the default colour mode (`extCordColorMode` / `extCordColor`, keys unchanged): one colour, or one colour per run.</summary>
        public static string DefaultKey(ThingDef d)
        {
            string look = StylePicker.DefaultLook;
            if (look != "Modern" || !IsConduit(d)) return look;
            return GimmeSomeSlackSettings.extCordColorMode == ExtCordColorMode.Single
                ? ConduitStyles.Key("Modern", ConduitStyles.Colours[Mathf.Clamp(GimmeSomeSlackSettings.extCordColor, 0, ConduitStyles.Colours.Length - 1)])
                : ConduitStyles.Key("Modern", ConduitStyles.Multi);
        }

        public static string LastPicked(ThingDef d) => d != null && lastPicked.TryGetValue(d, out string k) ? k : null;
        public static void ClearPicks() => lastPicked.Clear();

        /// <summary>The menu key the button stands on now: a Copy's carried style, else the last pick, else the default.</summary>
        public static string ResolveKey(Designator_Build des)
        {
            ThingDef d = des?.PlacingDef as ThingDef;
            if (!IsOurs(d)) return null;
            if (des.styleOverridden)
            {
                string look = LookOf(des.styleDef, out string colour);
                return look != null ? ConduitStyles.Key(look, colour) : DefaultKey(d);
            }
            return LastPicked(d) ?? DefaultKey(d);
        }

        /// <summary>The style handed to the blueprint / god-mode building: "one colour per run" resolves to a random colour
        /// here (the adopt rule then makes the whole run that colour); everything else is its own style def.</summary>
        public static ThingStyleDef Resolve(Designator_Build des)
        {
            ThingDef d = des?.PlacingDef as ThingDef;
            string key = ResolveKey(des);
            if (key == null) return null;
            if (key == ConduitStyles.Key("Modern", ConduitStyles.Multi))
                key = ConduitStyles.Key("Modern", ConduitStyles.Colours[Rand.Range(0, ConduitStyles.Colours.Length)]);
            return StyleFor(d, key);
        }

        public static bool Pick(Designator_Build des, string key)
        {
            ThingDef d = des?.PlacingDef as ThingDef;
            if (!IsOurs(d) || !MenuKeys(IsConduit(d)).Contains(key)) return false;
            lastPicked[d] = key;
            des.styleOverridden = false;
            des.styleDef = key == ConduitStyles.Key("Modern", ConduitStyles.Multi) ? StyleFor(d, "Modern") : StyleFor(d, key);
            picks++;
            return true;
        }

        public static string Label(string key)
        {
            if (!ConduitStyles.TryParseKey(key, out string look, out string colour))
                return key == ConduitStyles.Key("Modern", ConduitStyles.Multi) ? "Modern: one colour per run (multicolour)" : key;
            if (colour == null) return look;
            if (colour == ConduitStyles.Mix) return "Modern: random mix of colours";
            return "Modern: " + colour.ToLowerInvariant();
        }

        /// <summary>A menu icon: the strand art of that look / colour for conduit; the switch's own style art.</summary>
        public static Texture2D Icon(ThingDef d, string key)
        {
            if (!IsConduit(d))
            {
                ThingStyleDef s = StyleFor(d, key);
                return s?.UIIcon ?? (Texture2D)Widgets.GetIconFor(d, null, s);
            }
            ConduitStyles.TryParseKey(key, out string look, out string colour);
            look = look ?? "Modern";
            int v = ConduitStyles.IsColour(colour) ? ConduitStyles.ColourIndex(colour) : 0;
            return ContentFinder<Texture2D>.Get(CordMaterials.StrandPathOf(look, v), false) ?? (Texture2D)Widgets.GetIconFor(d, null, null);
        }

        public static List<FloatMenuOption> MenuFor(Designator_Build des)
        {
            var list = new List<FloatMenuOption>();
            ThingDef d = des.PlacingDef as ThingDef;
            string cur = ResolveKey(des), def = DefaultKey(d);
            foreach (string key in MenuKeys(IsConduit(d)))
            {
                string k = key;
                if (key != ConduitStyles.Key("Modern", ConduitStyles.Multi) && StyleFor(d, key) == null) continue;
                string label = Label(key) + (key == cur ? " (current)" : "") + (key == def ? " - default" : "");
                list.Add(new FloatMenuOption(label, () => Pick(des, k), Icon(d, key), Color.white));
            }
            return list;
        }

        // ------------------------------------------------------------------ the cord layer's read
        /// <summary>Every styled run member's cell on the map -> its stored (look, colour). Unstyled members are absent (legacy).</summary>
        public static Dictionary<Cell, CellStyle> CellStyles(Map map)
        {
            var d = new Dictionary<Cell, CellStyle>();
            foreach (ThingDef def in memberList)
            {
                bool conduit = IsConduit(def);
                foreach (Thing t in map.listerThings.ThingsOfDef(def))
                {
                    string look = LookOf(StylePicker.RawStyle(t), out string colour);
                    if (look == null) continue;
                    var c = new Cell(t.Position.x, t.Position.z);
                    if (d.TryGetValue(c, out CellStyle have) && have.Conduit) continue;
                    d[c] = new CellStyle { Look = look, Colour = colour, Conduit = conduit };
                }
            }
            return d;
        }

        // ------------------------------------------------------------------ the switch
        private static readonly Dictionary<string, Graphic> switchGraphics = new Dictionary<string, Graphic>();
        /// <summary>State read: the switch art path per look and state that resolved (null = art missing, vanilla shown).</summary>
        public static readonly Dictionary<string, string> SwitchPaths = new Dictionary<string, string>();

        public static string SwitchPath(string look, bool on) =>
            (look == "Scrapper" ? ConduitVisuals.SwitchTexPathOurs : CordMaterials.StyleDir + look + "/PowerSwitch") + (on ? "" : "_Off");

        /// <summary>The switch drawn in a look and state (held clamped and with the same shader / size ConduitVisuals gives
        /// the Scrapper switch), or null when that art is missing.</summary>
        public static Graphic SwitchGraphic(ThingDef switchDef, string look, bool on)
        {
            string path = SwitchPath(look, on);
            if (switchGraphics.TryGetValue(path, out Graphic g)) return g;
            Texture2D tex = ContentFinder<Texture2D>.Get(path, false);
            GraphicData gd = switchDef.graphicData;
            g = null;
            if (tex != null && gd != null)
            {
                tex.wrapMode = TextureWrapMode.Clamp;
                g = GraphicDatabase.Get<Graphic_Single>(path, (gd.shaderType ?? ShaderTypeDefOf.Cutout).Shader, gd.drawSize, Color.white);
            }
            switchGraphics[path] = g;
            SwitchPaths[path] = g == null ? null : path;
            return g;
        }

        // ------------------------------------------------------------------ placement hint
        private static IntVec3 hintCell = IntVec3.Invalid;
        private static int hintFrame = -1;
        private static string hintText;

        /// <summary>"joins Industrial run" / "bridges Modern + Industrial: Industrial wins" for a cell, or null. Recomputed only
        /// when the mouse cell changes (or every 30 frames), so a long run costs one flood fill per cell moved.</summary>
        public static string JoinsHint(Map map, IntVec3 c)
        {
            if (c == hintCell && Time.frameCount - hintFrame < 30) return hintText;
            hintCell = c; hintFrame = Time.frameCount;
            hintText = null;
            RM_MapComponent_ConduitRuns runs = map.GetComponent<RM_MapComponent_ConduitRuns>();
            if (runs == null) return null;
            var seen = new HashSet<Thing>();
            var infos = new List<ConduitStyles.Run>();
            foreach (IntVec3 cell in GenAdj.CellsAdjacentCardinal(c, Rot4.North, IntVec2.One).Concat(new[] { c }))
            {
                if (!cell.InBounds(map)) continue;
                foreach (Thing t in cell.GetThingList(map))
                {
                    if (!IsMember(t.def) || seen.Contains(t)) continue;
                    List<Thing> run = runs.RunOf(t);
                    seen.UnionWith(run);
                    infos.Add(RM_MapComponent_ConduitRuns.Info(run));
                }
            }
            if (infos.Count == 0) return null;
            string Look(ConduitStyles.Run r) => r.Look ?? StylePicker.DefaultLook;
            var looks = infos.Select(Look).Distinct().ToList();
            if (infos.Count == 1 || looks.Count == 1) hintText = "joins " + looks[0] + " run";
            else hintText = "bridges " + string.Join(" + ", looks) + " runs: " + Look(infos[ConduitStyles.Winner(infos)]) + " wins (most conduit)";
            return hintText;
        }

        // ------------------------------------------------------------------ restyle gizmo
        /// <summary>Round 6: "Restyle this lamp" on a floor lamp (one piece; a lamp is a machine, not a run member). The four
        /// looks, plus "match its cable run". A lamp left alone follows its run when the run is restyled
        /// (ConduitStyles.LampFollowsRun).</summary>
        public static Command RestyleLampGizmo(Building lamp)
        {
            string cur = RawLook(lamp);
            return new Command_Action
            {
                defaultLabel = "Restyle this lamp",
                defaultDesc = "Give this lamp another look (" + (cur ?? "vanilla") + " now). Art only: it costs nothing and changes nothing else.\n\n" +
                              "A lamp hooked to a cable run changes look with the run when the run is restyled, unless you give it a different look here.",
                icon = Icon(lamp.def, cur ?? StylePicker.DefaultLook),
                action = () =>
                {
                    var opts = new List<FloatMenuOption>();
                    RM_MapComponent_ConduitRuns runs = lamp.Map?.GetComponent<RM_MapComponent_ConduitRuns>();
                    foreach (string look in AerialStyles.Looks)
                    {
                        string k = look;
                        if (StyleFor(lamp.def, k) == null) continue;
                        opts.Add(new FloatMenuOption(look + (k == cur ? " (current)" : ""), () => runs?.RestyleLamp(lamp, k, true), Icon(lamp.def, k), Color.white));
                    }
                    opts.Add(new FloatMenuOption("Match its cable run", () => runs?.RestyleLamp(lamp, RM_MapComponent_ConduitRuns.LampMatchRun, true)));
                    Find.WindowStack.Add(new FloatMenu(opts));
                }
            };
        }

        public static Command RestyleGizmo(Building b)
        {
            var cmd = new Command_Action
            {
                defaultLabel = "Restyle this run",
                defaultDesc = "Repaint this whole run (every conduit cell, switch, pole and bracket connected to it) in another style. Art only: it costs nothing and changes nothing else.\n\n" +
                              "Floor lamps hooked to the run change with it, unless a lamp was given a different look of its own.",
                icon = Icon(DefDatabase<ThingDef>.GetNamedSilentFail("PowerConduit") ?? b.def, ConduitStyles.Key(RawLook(b) ?? StylePicker.DefaultLook, RawColour(b))),
                action = () =>
                {
                    var opts = new List<FloatMenuOption>();
                    ThingDef pc = DefDatabase<ThingDef>.GetNamedSilentFail("PowerConduit");
                    foreach (string key in MenuKeys(true))
                    {
                        string k = key;
                        opts.Add(new FloatMenuOption(Label(key), () => b.Map?.GetComponent<RM_MapComponent_ConduitRuns>()?.RestyleRun(b, k, true), Icon(pc, key), Color.white));
                    }
                    Find.WindowStack.Add(new FloatMenu(opts));
                }
            };
            return cmd;
        }
    }

    // ---------------------------------------------------------------------- patches

    /// <summary>The conduit / switch build button opens its style menu (after vanilla selected the designator).</summary>
    [HarmonyPatch(typeof(Designator_Build), nameof(Designator_Build.ProcessInput))]
    internal static class Patch_DesignatorBuild_ProcessInput_Conduit
    {
        private static void Postfix(Designator_Build __instance)
        {
            try
            {
                if (!ConduitStylePicker.IsOurs(__instance.PlacingDef as ThingDef) || !GimmeSomeSlackSettings.enabled) return;
                if (Find.DesignatorManager.SelectedDesignator != __instance) return;
                List<FloatMenuOption> opts = ConduitStylePicker.MenuFor(__instance);
                if (opts.Count > 0) Find.WindowStack.Add(new FloatMenu(opts));
            }
            catch (Exception ex) { Log.ErrorOnce("[GimmeSomeSlack] conduit style menu: " + ex, 0x5E1E02); }
        }
    }

    /// <summary>For conduit and the switch the designator's style is the picked (or copied) one in every game mode.</summary>
    [HarmonyPatch(typeof(Designator_Build), nameof(Designator_Build.ThingStyleDefNonPreceptSource), MethodType.Getter)]
    internal static class Patch_DesignatorBuild_StyleGetter_Conduit
    {
        private static void Postfix(Designator_Build __instance, ref ThingStyleDef __result)
        {
            if (__instance.sourcePrecept != null || !ConduitStylePicker.IsOurs(__instance.PlacingDef as ThingDef)) return;
            __result = ConduitStylePicker.Resolve(__instance) ?? __result;
        }
    }

    /// <summary>The placement cursor says what the cell will join (design 2.3: "joins Industrial run", so nothing is a
    /// surprise): one neighbouring run -> its look; two or more looks -> which one wins (the run with most conduit cells).</summary>
    [HarmonyPatch(typeof(Designator_Build), nameof(Designator_Build.DrawMouseAttachments))]
    internal static class Patch_DesignatorBuild_JoinsHint
    {
        private static void Postfix(Designator_Build __instance)
        {
            try
            {
                if (!GimmeSomeSlackSettings.enabled || !ConduitStylePicker.IsMember(__instance.PlacingDef as ThingDef)) return;
                Map map = Find.CurrentMap;
                IntVec3 c = UI.MouseCell();
                if (map == null || !c.InBounds(map)) return;
                string hint = ConduitStylePicker.JoinsHint(map, c);
                if (hint != null) Widgets.MouseAttachedLabel(hint, 0f, 32f);
            }
            catch (Exception ex) { Log.ErrorOnce("[GimmeSomeSlack] joins hint: " + ex, 0x5E1E05); }
        }
    }

    /// <summary>A styled switch draws its look's art, on and off. Unstyled (legacy) switches and Scrapper keep the art
    /// ConduitVisuals gives today; with the cords off, vanilla's.</summary>
    [HarmonyPatch(typeof(Building_PowerSwitch), nameof(Building_PowerSwitch.Graphic), MethodType.Getter)]
    internal static class Patch_PowerSwitch_Graphic
    {
        private static void Postfix(Building_PowerSwitch __instance, ref Graphic __result)
        {
            if (!ConduitVisuals.Applied) return;
            string look = ConduitStylePicker.RawLook(__instance);
            if (look == null || look == "Scrapper") return;
            bool on = __instance.GetComp<CompFlickable>()?.SwitchIsOn ?? true;
            Graphic g = ConduitStylePicker.SwitchGraphic(__instance.def, look, on);
            if (g != null) __result = g;
        }
    }

    /// <summary>Every new run member (conduit, switch, pole, bracket) is queued once for the run rule. Loading a save never
    /// queues: a loaded map is already resolved, and an older save must load unchanged.</summary>
    [HarmonyPatch(typeof(Building), nameof(Building.SpawnSetup))]
    internal static class Patch_Building_SpawnSetup_Runs
    {
        private static void Postfix(Building __instance, Map map, bool respawningAfterLoad)
        {
            if (respawningAfterLoad || map == null || !ConduitStylePicker.IsMember(__instance.def)) return;
            map.GetComponent<RM_MapComponent_ConduitRuns>()?.Queue(__instance);
        }
    }

    /// <summary>The "Restyle this run" gizmo on every run member the player owns.</summary>
    [HarmonyPatch(typeof(Building), nameof(Building.GetGizmos))]
    internal static class Patch_Building_GetGizmos_Restyle
    {
        private static IEnumerable<Gizmo> Postfix(IEnumerable<Gizmo> __result, Building __instance)
        {
            foreach (Gizmo g in __result) yield return g;
            if (!GimmeSomeSlackSettings.enabled || !__instance.Spawned || __instance.Faction != Faction.OfPlayer) yield break;
            if (ConduitStylePicker.IsMember(__instance.def)) yield return ConduitStylePicker.RestyleGizmo(__instance);
            else if (ConduitStylePicker.IsLamp(__instance.def)) yield return ConduitStylePicker.RestyleLampGizmo(__instance);
        }
    }

    /// <summary>Linking two anchors (by hand, or auto-link) can join two runs: queue the bridge check.</summary>
    [HarmonyPatch(typeof(CompAerialAnchor), nameof(CompAerialAnchor.TryLink))]
    internal static class Patch_TryLink_Bridge
    {
        private static void Postfix(CompAerialAnchor a, Thing target, LinkVerdict __result)
        {
            if (__result != LinkVerdict.Ok || a?.parent?.Map == null || target == null) return;
            a.parent.Map.GetComponent<RM_MapComponent_ConduitRuns>()?.QueueLink(a.parent, target);
        }
    }
}
