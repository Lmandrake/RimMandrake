using System;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.Patches
{
    // LOVIN_LOGSPAM_DIAGNOSE_IN_PLAY_EVICTIONS. Two third-party mods write debug lines at about 0.3 a tick: session ee0fbaa8
    // had 7 rises of 1000 or more Verse.Log messages between two scans made almost wholly of them (5485 at 20:26Z, 99.5%
    // Mood Chain Reaction), which fills the 1000-entry queue, reaches the 10000-message stop and hides every later error.
    // Each mod logs through one method, so a prefix on it drops all of that mod's debug lines and nothing else:
    //   Intimacy - A Lovin' Expansion (workshop 3498422643): SexUtilities.HandNotesToEuterpe(string), 35 callers, the only
    //     way it logs in play. Its own IntimacySettings.logging defaults to true, with no player need for it.
    //   Mood Chain Reaction (workshop 3721381956): Hediff_MCRMoodChain.DebugLog(Pawn, string), logs when Prefs.DevMode.
    // Either mod absent: nothing is patched and nothing is logged. A named method gone: one warning, and that mod keeps
    // logging, because silence must never be claimed when it was not achieved.
    [StaticConstructorOnStartup]
    public static class LogSpamOffStartup
    {
        static LogSpamOffStartup() => LogSpamOff.Install();
    }

    public static class LogSpamOff
    {
        public const string IntimacyType = "LoveyDoveySexWithEuterpe.SexUtilities";
        public const string IntimacySink = "HandNotesToEuterpe";
        public const string MoodChainType = "MoodChainReaction.Hediff_MCRMoodChain";
        public const string MoodChainSink = "DebugLog";
        public const string LogTag = "[RimMandrake Patches] log spam off:";
        public const string HarmonyId = "mandrake.rm.patches.logspamoff";

        private static bool installed;
        private static int intimacyDropped, moodChainDropped;
        private static bool intimacyPatched, moodChainPatched;

        public static string Status
        {
            get
            {
                if (!intimacyPatched && !moodChainPatched)
                    return "Neither mod is loaded: nothing to silence.";
                if (!RM_PatchesSettings.quietThirdPartyLogSpam)
                    return "Off: those mods log as they ship.";
                return "Dropped this session: " + intimacyDropped + " Intimacy lines, " + moodChainDropped
                    + " Mood Chain Reaction lines.";
            }
        }

        public static void Install()
        {
            if (installed)
                return;
            installed = true;
            var harmony = new Harmony(HarmonyId);
            intimacyPatched = Bind(harmony, IntimacyType, IntimacySink, nameof(Prefix_Intimacy));
            moodChainPatched = Bind(harmony, MoodChainType, MoodChainSink, nameof(Prefix_MoodChain));
        }

        private static bool Bind(Harmony harmony, string typeName, string method, string prefix)
        {
            Type type = AccessTools.TypeByName(typeName);
            if (type == null)
                return false;
            MethodInfo target = AccessTools.Method(type, method);
            if (target == null)
            {
                Log.Warning(LogTag + " " + typeName + "." + method + " not found (the mod changed): it keeps logging.");
                return false;
            }
            try
            {
                harmony.Patch(target, prefix: new HarmonyMethod(typeof(LogSpamOff), prefix));
            }
            catch (Exception e)
            {
                Log.Warning(LogTag + " could not patch " + typeName + "." + method + ": " + e.Message + ". It keeps logging.");
                return false;
            }
            Log.Message(LogTag + " patched " + typeName + "." + method + ".");
            return true;
        }

        public static bool Prefix_Intimacy() => Drop(ref intimacyDropped, IntimacyType);

        public static bool Prefix_MoodChain() => Drop(ref moodChainDropped, MoodChainType);

        // The first drop of each source writes one line: a later silence is then provably a silenced sink, not one that
        // never ran on this map. false skips the original method, so the mod's own line is never written.
        private static bool Drop(ref int count, string source)
        {
            if (!RM_PatchesSettings.quietThirdPartyLogSpam)
                return true;
            if (count++ == 0)
                Log.Message(LogTag + " first line dropped from " + source);
            return false;
        }
    }
}
