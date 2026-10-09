// MOD_OPTIONS_RETROFIT_1.A1 -- the debug hook the check was owed: opens every RimMandrake mod's settings page for real.
//
// jawa/static_call  type=RimMandrake.RimDefDump.RM_SettingsOpenSmoke  method=Run  args="<semicolon-separated>"
//   (args are ';'-separated because static_call splits on '|'.)  Keys, all optional:
//     filter=<substr>   which Mod subclasses: default = assembly name starts with "RimMandrake" or pack id starts with "mandrake.";
//                       with filter= a Mod qualifies when its type full name, assembly name or pack id contains <substr>
//     reset=1           discard a previous run and start again
//     report=1          do not start anything, only return the current result
//   First call starts a run and returns "started ..."; call again (or report=1) for the result:
//     "opened=N failed=Type:Exc|Type:Exc nosettings=M pending=P done=True|False"
//   PASS for A1: done=True, failed empty, opened == the number of our mods that have a settings class.
//
// WHY A WINDOW: DoSettingsWindowContents draws with Widgets/GUI, and Unity throws "You can only call GUI functions from inside
// OnGUI" if it is called from static_call's Update-time context -- that would fail every mod with a harness error and prove
// nothing. So Run only queues; a Window added to Find.WindowStack calls each page from inside the real OnGUI Repaint pass, one
// mod per repaint, each in its own try/catch. It sits far off-screen and closes itself when done.
// It cannot press buttons, so it proves "the page draws without throwing", not that every control works.
using System;
using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.RimDefDump
{
    public static class RM_SettingsOpenSmoke
    {
        internal static readonly List<Mod> Pending = new List<Mod>();
        internal static readonly List<string> Failed = new List<string>();
        internal static int Opened;
        internal static int NoSettings;
        internal static bool Started;
        internal static bool Done;

        public static string Run(string args)
        {
            try
            {
                string filter = null;
                bool reset = false, reportOnly = false;
                foreach (string raw in (args ?? "").Split(';'))
                {
                    string t = raw.Trim();
                    if (t.Length == 0) continue;
                    int eq = t.IndexOf('=');
                    string k = eq < 0 ? t : t.Substring(0, eq).Trim().ToLowerInvariant();
                    string v = eq < 0 ? "" : t.Substring(eq + 1).Trim();
                    if (k == "filter") filter = v;
                    else if (k == "reset") reset = v != "0";
                    else if (k == "report") reportOnly = v != "0";
                    else return "ERROR unknown arg '" + k + "' (filter=, reset=, report=)";
                }
                if (reportOnly || (Started && !reset)) return Report();

                Pending.Clear(); Failed.Clear(); Opened = 0; NoSettings = 0; Done = false; Started = true;
                foreach (Mod m in LoadedModManager.ModHandles)
                {
                    if (!Qualifies(m, filter)) continue;
                    string cat = null;
                    try { cat = m.SettingsCategory(); } catch (Exception e) { Failed.Add(Name(m) + ":SettingsCategory " + Short(e)); continue; }
                    if (string.IsNullOrEmpty(cat)) { NoSettings++; continue; }
                    Pending.Add(m);
                }
                if (Find.WindowStack == null) { Started = false; return "ERROR Find.WindowStack is null (game not at a UI state yet)"; }
                if (Pending.Count == 0) { Done = true; return "started targets=0 nosettings=" + NoSettings + " -- nothing qualified; " + Report(); }
                Find.WindowStack.Add(new SmokeWindow());
                return "started targets=" + Pending.Count + " nosettings=" + NoSettings + "; call again (report=1) for the result";
            }
            catch (Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
        }

        static bool Qualifies(Mod m, string filter)
        {
            Type t = m.GetType();
            string asm = t.Assembly.GetName().Name ?? "";
            string pid = m.Content != null ? (m.Content.PackageId ?? "") : "";
            if (string.IsNullOrEmpty(filter))
                return asm.StartsWith("RimMandrake", StringComparison.Ordinal) || pid.StartsWith("mandrake.", StringComparison.OrdinalIgnoreCase);
            return (t.FullName ?? "").IndexOf(filter, StringComparison.OrdinalIgnoreCase) >= 0
                || asm.IndexOf(filter, StringComparison.OrdinalIgnoreCase) >= 0
                || pid.IndexOf(filter, StringComparison.OrdinalIgnoreCase) >= 0;
        }

        static string Name(Mod m) { return m.GetType().FullName; }
        static string Short(Exception e)
        {
            Exception r = e; while (r.InnerException != null) r = r.InnerException;
            string msg = (r.Message ?? "").Replace('\n', ' ').Replace('|', '/');
            return r.GetType().Name + ": " + (msg.Length > 100 ? msg.Substring(0, 100) : msg);
        }

        internal static string Report()
        {
            if (!Started) return "ERROR no run yet (call Run first)";
            return "opened=" + Opened + " failed=" + string.Join("|", Failed.ToArray()) + " nosettings=" + NoSettings
                + " pending=" + Pending.Count + " done=" + Done;
        }

        internal static void Step(Rect inRect)
        {
            if (Pending.Count == 0) { Done = true; return; }
            Mod m = Pending[0];
            Pending.RemoveAt(0);
            try
            {
                m.DoSettingsWindowContents(inRect);
                Opened++;
            }
            catch (Exception e)
            {
                Failed.Add(Name(m) + ":" + Short(e));
                Log.Warning("[RM_SettingsOpenSmoke] settings page threw for " + Name(m) + ": " + e);
            }
            finally
            {
                Text.Font = GameFont.Small; Text.Anchor = TextAnchor.UpperLeft; Text.WordWrap = true; GUI.color = Color.white;
            }
            if (Pending.Count == 0)
            {
                Done = true;
                Log.Message("[RM_SettingsOpenSmoke] " + Report());
            }
        }

        sealed class SmokeWindow : Window
        {
            public SmokeWindow()
            {
                doCloseX = false; doCloseButton = false; closeOnClickedOutside = false; closeOnAccept = false; closeOnCancel = false;
                absorbInputAroundWindow = false; preventCameraMotion = false; drawShadow = false; forcePause = false;
                soundAppear = null; soundClose = null;
            }

            public override Vector2 InitialSize { get { return new Vector2(900f, 700f); } }

            protected override void SetInitialSizeAndPosition()
            {
                windowRect = new Rect(-5000f, -5000f, 900f, 700f);
            }

            public override void DoWindowContents(Rect inRect)
            {
                if (Event.current == null || Event.current.type != EventType.Repaint) return;
                if (Done) { Close(false); return; }
                Step(new Rect(0f, 0f, 880f, 640f));
                if (Done) Close(false);
            }
        }
    }
}
