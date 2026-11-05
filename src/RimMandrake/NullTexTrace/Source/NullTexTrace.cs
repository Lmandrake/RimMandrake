// NullTexTrace - who passes a null texture to GUI.DrawTexture? (WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR)
//
// THE SYMPTOM. On the full list, Player.log fills with "null texture passed to GUI.DrawTexture"
// (19,519 lines in one load, 77 in the next). Unity writes that line with no managed stack.
//
// WHERE THE LINE COMES FROM (decompiled UnityEngine.IMGUIModule, RimWorld 1.6). Every public
// GUI.DrawTexture overload funnels into ONE internal 12-argument overload
//   (Rect, Texture, ScaleMode, bool, float, Color, Color, Color, Color, Vector4, Vector4, bool)
// which returns unless Event.current.type == Repaint, then: if (image == null) { LogWarning; return; }.
// The prefix below records under that SAME condition, so each count is one logged warning. It
// always returns true: the engine's behaviour is unchanged.
//
// WHY A MOD, NOT THE JAWABENCH COMPANION (jawa/nulltex_probe). The companion is lazy: nothing in it
// runs before the first jawa/ bridge call, so proving it needed a bridge site-prep dance, and that
// dance failed on bridge contention every time. A Mod constructor runs during
// LoadAllActiveMods, before the main menu ever draws. The result goes to Player.log, so the proof is
// a file read (nulltex_log_check.py) with no bridge.
//
// OUTPUT (UnityEngine.Debug.Log directly: Verse.Log stops at its message cap, and the flood itself
// can fill it). The parser lives in nulltex_log_check.py; keep the two in step:
//   [NullTexTrace] installed target=<...> rimthemes=<bool> menushell=<bool>
//   [NullTexTrace] NOT installed: <why>
//   [NullTexTrace] caller #<k> at n=<N> state=<ProgramState> longEvent=<bool>: <caller> <- <frame> <- ...
//   [NullTexTrace] summary n=<N> callers=<k> dropped=<d> top: <caller> x<count> || <caller> x<count> ...
// Summaries print at n = 1, 10, 100, ... 10^7. A caller line prints once per new caller, up to MaxCallers.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.NullTexTrace
{
    public class NullTexTraceMod : Mod
    {
        public NullTexTraceMod(ModContentPack content) : base(content)
        {
            NullTexTrace.Install();
        }
    }

    internal static class NullTexTrace
    {
        internal const string Tag = "[NullTexTrace] ";
        internal const string Target =
            "UnityEngine.GUI.DrawTexture(Rect, Texture, ScaleMode, bool, float, Color x4, Vector4, Vector4, bool)";
        internal static readonly Type[] TargetArgs =
        {
            typeof(Rect), typeof(Texture), typeof(ScaleMode), typeof(bool), typeof(float),
            typeof(Color), typeof(Color), typeof(Color), typeof(Color),
            typeof(Vector4), typeof(Vector4), typeof(bool)
        };
        internal const int MaxCallers = 64;  // distinct callers named; later new ones are only counted as dropped
        internal const int MaxFrames = 8;    // frames printed per caller line
        internal const int TopInSummary = 5;

        private static long _nullCalls;
        private static long _nextSummary = 1;
        private static long _dropped;
        private static bool _inRecord;
        private static readonly Dictionary<string, long> ByCaller = new Dictionary<string, long>();

        internal static void Install()
        {
            try
            {
                var m = AccessTools.Method(typeof(GUI), "DrawTexture", TargetArgs);
                if (m == null)
                {
                    UnityEngine.Debug.Log(Tag + "NOT installed: overload " + Target + " not found");
                    return;
                }
                new Harmony("mandrake.rm.nulltextrace").Patch(m, prefix: new HarmonyMethod(
                    typeof(NullTexTrace).GetMethod(nameof(Prefix), BindingFlags.Static | BindingFlags.NonPublic)));
                UnityEngine.Debug.Log(Tag + "installed target=" + Target +
                                      " rimthemes=" + Active("aRandomKiwi.RimThemes") +
                                      " menushell=" + Active("mandrake.rut.menushell"));
            }
            catch (Exception e)
            {
                UnityEngine.Debug.Log(Tag + "NOT installed: " + e.GetType().Name + ": " + e.Message);
            }
        }

        private static bool Active(string packageId)
        {
            try { return ModsConfig.IsActive(packageId); }
            catch { return false; }
        }

        // __1 is the second argument (the Texture), bound by position so a renamed parameter cannot
        // break the patch. Unity's == null also counts a destroyed texture, as the engine's test does.
        private static void Prefix(Texture __1)
        {
            if (__1 != null || _inRecord) return;
            try
            {
                var ev = Event.current;
                if (ev == null || ev.type != EventType.Repaint) return;
                _inRecord = true;
                Record();
            }
            catch (Exception e)
            {
                try { UnityEngine.Debug.Log(Tag + "record error: " + e.GetType().Name + ": " + e.Message); }
                catch { }
            }
            finally { _inRecord = false; }
        }

        // Frames that are the draw call itself: GUI, the Harmony replacement (no DeclaringType, or a DMD
        // wrapper), HarmonyLib/MonoMod, and this class.
        private static bool IsPlumbing(MethodBase m)
        {
            if (m == null) return true;
            var t = m.DeclaringType;
            if (t == null) return true;
            string n = t.FullName ?? t.Name ?? "";
            return n == "UnityEngine.GUI" || n.StartsWith("HarmonyLib.", StringComparison.Ordinal)
                   || n.StartsWith("MonoMod.", StringComparison.Ordinal)
                   || t == typeof(NullTexTrace)
                   || (m.Name ?? "").StartsWith("DMD<", StringComparison.Ordinal);
        }

        private static string Describe(MethodBase m)
        {
            if (m == null) return "<unknown>";
            var t = m.DeclaringType;
            string asm = "";
            try { asm = t?.Assembly.GetName().Name ?? ""; } catch { }
            return (t != null ? t.FullName : "<dynamic>") + "." + m.Name + (asm.Length > 0 ? " [" + asm + "]" : "");
        }

        // Main thread only (IMGUI), so no locking.
        private static void Record()
        {
            long n = ++_nullCalls;
            var frames = new StackTrace(1, false).GetFrames() ?? new StackFrame[0];
            var kept = new List<string>(MaxFrames);
            foreach (var f in frames)
            {
                var m = f.GetMethod();
                if (kept.Count == 0 && IsPlumbing(m)) continue;
                kept.Add(Describe(m));
                if (kept.Count >= MaxFrames) break;
            }
            string caller = kept.Count > 0 ? kept[0] : "<no managed caller above GUI.DrawTexture>";
            if (ByCaller.TryGetValue(caller, out var c)) ByCaller[caller] = c + 1;
            else if (ByCaller.Count < MaxCallers)
            {
                ByCaller[caller] = 1;
                string state = "unknown";
                bool longEvent = false;
                try { state = Current.ProgramState.ToString(); } catch { }
                try { longEvent = LongEventHandler.AnyEventNowOrWaiting; } catch { }
                UnityEngine.Debug.Log(Tag + "caller #" + ByCaller.Count + " at n=" + n + " state=" + state +
                                      " longEvent=" + longEvent + ": " + string.Join(" <- ", kept));
            }
            else _dropped++;

            if (n >= _nextSummary)
            {
                _nextSummary = _nextSummary >= 10000000 ? long.MaxValue : _nextSummary * 10;
                var top = ByCaller.OrderByDescending(kv => kv.Value).Take(TopInSummary)
                    .Select(kv => kv.Key + " x" + kv.Value);
                UnityEngine.Debug.Log(Tag + "summary n=" + n + " callers=" + ByCaller.Count + " dropped=" + _dropped +
                                      " top: " + string.Join(" || ", top));
            }
        }
    }
}
