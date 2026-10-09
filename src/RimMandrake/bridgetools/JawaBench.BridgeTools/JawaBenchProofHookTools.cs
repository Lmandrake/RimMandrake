// JawaBenchProofHookTools.cs - PROOF_HOOKS_20261009 (belt acceptance pass).
//
// 1. jawa/map_comp_read: the missing GENERAL read for a MapComponent's private state (comp_read reads ThingComps only).
//    Hediff lists are already jawa/pawn_health, inspect strings jawa/inspect_string, settings jawa/mod_settings_field.
// 2. JawaBenchSettingsSmoke (jawa/static_call target): SETTINGS_OPEN_SMOKE_HOOK_1. Mod.DoSettingsWindowContents draws with
//    IMGUI, which only works inside OnGUI, so Start() opens a 1x1 invisible Window whose DoWindowContents runs every
//    mandrake.* mod's settings page once on an off-screen rect, catching each exception; Result() reads the outcome.
//    Read-only apart from the (briefly open) window; it never writes settings.
//
// THREAD AFFINITY: everything touching a Map runs inside ctx.MainThread.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using UnityEngine;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/map_comp_read",
            Description =
                "Reflectively read a MapComponent on the CURRENT map, INCLUDING private fields and non-indexer " +
                "properties (the MapComponent twin of comp_read). comp = a substring of the component's type name " +
                "(ambiguous substrings are refused with the candidates). members = comma list of field/property names; " +
                "blank reads EVERY instance field. Collections render as a count plus the first 12 entries. READ-ONLY. " +
                "A member that does not exist is reported under missing[], never silently dropped.",
            ResultDescription = "success, compType, values{name:text}, missing[], ticksGame.")]
        public static async Task<object> MapCompRead(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Substring of the MapComponent type name.")] string comp,
            [ToolParameter(Description = "Comma list of members; blank = all instance fields.")] string members = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Current.ProgramState != ProgramState.Playing) return Fail("Not in a loaded game.");
                Map map = Find.CurrentMap;
                if (map == null) return Fail("No current map.");
                var hits = map.components.Where(x => x.GetType().Name.IndexOf(comp ?? "", StringComparison.OrdinalIgnoreCase) >= 0).ToList();
                if (hits.Count == 0) return Fail("No map component matches '" + comp + "'.", new { components = map.components.Select(x => x.GetType().Name).ToList() });
                if (hits.Count > 1) return Fail("Ambiguous component substring.", new { candidates = hits.Select(x => x.GetType().Name).ToList() });
                object c = hits[0];
                Type ct = c.GetType();
                const BindingFlags F = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.FlattenHierarchy;
                var values = new Dictionary<string, string>();
                var missing = new List<string>();
                if (string.IsNullOrWhiteSpace(members))
                {
                    for (Type tt = ct; tt != null && tt != typeof(MapComponent) && tt != typeof(object); tt = tt.BaseType)
                        foreach (FieldInfo fi in tt.GetFields(F | BindingFlags.DeclaredOnly))
                            if (!values.ContainsKey(fi.Name))
                            {
                                try { values[fi.Name] = ProbeRenderOwner(fi.GetValue(c)); }
                                catch (Exception e) { values[fi.Name] = "ERR " + e.GetType().Name; }
                            }
                }
                else
                {
                    foreach (string raw in members.Split(','))
                    {
                        string name = raw.Trim();
                        if (name.Length == 0) continue;
                        FieldInfo fi = null;
                        for (Type tt = ct; tt != null && fi == null; tt = tt.BaseType) fi = tt.GetField(name, F | BindingFlags.DeclaredOnly);
                        PropertyInfo pi = fi == null ? ct.GetProperty(name, F) : null;
                        try
                        {
                            if (fi != null) values[name] = ProbeRenderOwner(fi.GetValue(c));
                            else if (pi != null && pi.GetIndexParameters().Length == 0 && pi.CanRead) values[name] = ProbeRenderOwner(pi.GetValue(c));
                            else missing.Add(name);
                        }
                        catch (Exception e) { values[name] = "ERR " + (e.InnerException ?? e).GetType().Name + ": " + (e.InnerException ?? e).Message; }
                    }
                }
                return (object)new { success = true, compType = ct.FullName, values, missing, ticksGame = TicksGameSafe() };
            });
        }
    }

    /// <summary>SETTINGS_OPEN_SMOKE_HOOK_1: type=JawaBench.BridgeTools.JawaBenchSettingsSmoke, method Start then (a moment
    /// later) Result, both args "". Result: "done=B opened=N failed=[Mod:Exception;...] skipped=N total=N".</summary>
    public static class JawaBenchSettingsSmoke
    {
        internal static string outcome;
        internal static bool done;

        public static string Start(string unused)
        {
            if (Current.ProgramState != ProgramState.Playing && Current.ProgramState != ProgramState.Entry)
                return "ERROR not in Entry or Playing";
            done = false;
            outcome = null;
            Find.WindowStack.Add(new SettingsSmokeWindow());
            return "started";
        }

        public static string Result(string unused)
        {
            return done ? "done=True " + outcome : "done=False";
        }

        internal static string RunAll()
        {
            int opened = 0, skipped = 0, total = 0;
            var failed = new List<string>();
            Rect rect = new Rect(0f, 0f, 900f, 700f);
            foreach (Mod mod in LoadedModManager.ModHandles.ToList())
            {
                string pid = mod.Content?.PackageIdPlayerFacing ?? "";
                if (!pid.StartsWith("mandrake.", StringComparison.OrdinalIgnoreCase)) continue;
                total++;
                string cat;
                try { cat = mod.SettingsCategory(); } catch { cat = null; }
                if (string.IsNullOrEmpty(cat)) { skipped++; continue; }
                try
                {
                    mod.DoSettingsWindowContents(rect);
                    opened++;
                }
                catch (Exception e)
                {
                    Exception inner = e.InnerException ?? e;
                    failed.Add(mod.GetType().Name + ":" + inner.GetType().Name + ":" + inner.Message.Replace(';', ',').Replace('\n', ' '));
                }
                finally
                {
                    Text.Font = GameFont.Small;
                    Text.Anchor = TextAnchor.UpperLeft;
                }
            }
            return "opened=" + opened + " failed=[" + string.Join(";", failed.ToArray()) + "] skipped=" + skipped + " total=" + total;
        }
    }

    internal class SettingsSmokeWindow : Window
    {
        private bool ran;

        public override Vector2 InitialSize => new Vector2(2f, 2f);

        public SettingsSmokeWindow()
        {
            doCloseButton = false;
            doCloseX = false;
            doWindowBackground = false;
            drawShadow = false;
            absorbInputAroundWindow = false;
            preventCameraMotion = false;
            closeOnClickedOutside = false;
            onlyOneOfTypeAllowed = true;
        }

        public override void DoWindowContents(Rect inRect)
        {
            if (ran || Event.current.type != EventType.Repaint) return;
            ran = true;
            try { JawaBenchSettingsSmoke.outcome = JawaBenchSettingsSmoke.RunAll(); }
            catch (Exception e) { JawaBenchSettingsSmoke.outcome = "ERROR " + e.GetType().Name + ": " + e.Message; }
            JawaBenchSettingsSmoke.done = true;
            Close(false);
        }
    }
}
