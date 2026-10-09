using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using Verse;

namespace RimMandrake.TheRot
{
    // ═══════════════════════════════════════════════════════════════
    // ROT_NAVIGATOR_LOG_SITES_1 (Swallowed Navigator part B).
    //
    //   log       RM_NavigatorLogDef (Defs/Misc/RM_NavigatorLog.xml): eight entries. Every navigatorPingsPerEntry
    //             pings (RM_WorldComponent_SwallowedCore.pings, counted by RM_CompSwallowedCore.Ping) the next entry
    //             is read out as a letter. State lives on RM_WorldComponent_SwallowedCore (entriesRead, logCut), the
    //             component that already holds the world-unique carrier, rather than a second game component.
    //   sites     an entry in siteEntries also generates RM_NavigatorSalvageSite (vanilla item-stash shape, always
    //             defended when violent quests are allowed, no timeout). Free tier: QuestNode_GetSiteTile near the
    //             colony. Campaign: campaignSiteTiles (patched) are used in order, preset in the slate as siteTile.
    //   death     the carrier's death (RM_CompSwallowedCore.Notify_Killed) cuts the log mid-line with a letter;
    //             entries read and sites revealed stay. Pings stop with the carrier, so the count can never move.
    //   landing   a grav engine APPEARING on the carrier's map (landing, on a new map or an existing one) pings at
    //             once: RM_CompSwallowedCore tracks engine presence per 250-tick check. No patch at all, so the
    //             one-patch rule on GenStep_GravshipMarker (RM_Patch_GravshipArrivalLetter) holds, and a landing on
    //             an existing map (which that gen-step hook never sees) is caught too.
    // ═══════════════════════════════════════════════════════════════

    public class RM_NavigatorLogDef : Def
    {
        public List<string> entries = new List<string>();
        public List<int> siteEntries = new List<int>();
        public List<int> campaignSiteTiles = new List<int>();

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (entries.NullOrEmpty()) yield return "no entries";
            foreach (int i in siteEntries)
            {
                if (i < 1 || i > entries.Count) yield return "siteEntries names entry " + i + " of " + entries.Count;
            }
        }
    }

    public static class RM_NavigatorLog
    {
        public static RM_NavigatorLogDef Def => DefDatabase<RM_NavigatorLogDef>.GetNamedSilentFail("RM_NavigatorLog");

        /// <summary>Called after every counted ping. Reads the next entry when the ping count reaches it.</summary>
        public static void Notify_Ping(RM_WorldComponent_SwallowedCore w, Map map)
        {
            RM_NavigatorLogDef def = Def;
            if (!RM_TheRotKernel.LogReads(w != null, def != null, w != null && w.spent, w != null && w.logCut)) return;
            int due = RM_TheRotKernel.EntriesDue(w.pings, RM_TheRotSettings.navigatorPingsPerEntry, def.entries.Count);
            while (w.entriesRead < due)
            {
                ReadEntry(w, def, map);
            }
        }

        private static void ReadEntry(RM_WorldComponent_SwallowedCore w, RM_NavigatorLogDef def, Map map)
        {
            int n = ++w.entriesRead;
            string text = def.entries[n - 1];
            string tail = "";
            if (def.siteEntries.Contains(n) && TryRevealSite(w, def, map) != null)
            {
                w.sitesRevealed++;
                tail = "\n\nThe entry names a place. Your navigator has marked it on the map.";
            }
            Find.LetterStack.ReceiveLetter("Ship's log, entry " + n,
                "The pulse in the console has resolved into words: an old flight log, played back one entry at a time.\n\n\"" + text + "\"" + tail,
                LetterDefOf.NeutralEvent);
        }

        public static Quest TryRevealSite(RM_WorldComponent_SwallowedCore w, RM_NavigatorLogDef def, Map map)
        {
            QuestScriptDef script = DefDatabase<QuestScriptDef>.GetNamedSilentFail("RM_NavigatorSalvageSite");
            if (script == null) return null;
            Slate slate = new Slate();
            Map home = map ?? RimMandrake.EnvironmentalHazards.RM_SurfaceHome.AnyPlayerSurfaceHomeMap;
            if (home != null)
            {
                slate.Set("map", home);
                slate.Set("points", StorytellerUtility.DefaultThreatPointsNow(home));
            }
            int tileIndex = RM_TheRotKernel.CampaignTileIndex(w.sitesRevealed, def.campaignSiteTiles.NullOrEmpty() ? 0 : def.campaignSiteTiles.Count);
            if (tileIndex >= 0)
            {
                slate.Set("siteTile", new PlanetTile(def.campaignSiteTiles[tileIndex]));
            }
            if (!script.CanRun(slate, home)) return null;
            Quest quest = QuestUtility.GenerateQuestAndMakeAvailable(script, slate);
            if (quest != null && !quest.hidden && quest.root.sendAvailableLetter)
            {
                QuestUtility.SendLetterQuestAvailable(quest);
            }
            return quest;
        }

        /// <summary>The carrier died: the log stops mid-line.</summary>
        public static void Notify_CarrierDied(RM_WorldComponent_SwallowedCore w)
        {
            RM_NavigatorLogDef def = Def;
            if (w == null || def == null) return;
            // cut the log; a letter only if anyone ever heard an entry: RM_TheRotKernel.CutLogOnDeath (offline-fuzzed)
            if (!RM_TheRotKernel.CutLogOnDeath(ref w.logCut, w.entriesRead, def.entries.Count)) return;
            Find.LetterStack.ReceiveLetter("The log stops",
                "The console's pulse has stopped in the middle of a word. Whatever was left of the dead ship's log died "
              + "with the animal that carried its core. The entries you heard, and the places they named, are still yours.",
                LetterDefOf.NeutralEvent);
        }
    }

    /// <summary>Debug proofs for jawa/static_call (validation.py chain navigator_log).</summary>
    public static class RM_NavigatorLogProof
    {
        /// <summary>Adds n counted pings straight to the world component (no engine needed) and reports.
        /// "LOG pings p | entries e | sites s | quests q".</summary>
        public static string ProofPings(int n)
        {
            RM_WorldComponent_SwallowedCore w = RM_WorldComponent_SwallowedCore.Get;
            if (w == null) return "REFUSED: no world component";
            for (int i = 0; i < n; i++)
            {
                w.pings++;
                RM_NavigatorLog.Notify_Ping(w, Find.CurrentMap);
            }
            return Report(w);
        }

        /// <summary>Marks the carrier dead (as RM_CompSwallowedCore.Notify_Killed does) then adds n pings.</summary>
        public static string ProofKillThenPing(int n)
        {
            RM_WorldComponent_SwallowedCore w = RM_WorldComponent_SwallowedCore.Get;
            if (w == null) return "REFUSED: no world component";
            int before = w.entriesRead;
            w.spent = true;
            RM_NavigatorLog.Notify_CarrierDied(w);
            for (int i = 0; i < n; i++)
            {
                w.pings++;
                RM_NavigatorLog.Notify_Ping(w, Find.CurrentMap);
            }
            return "KILLED entries " + before + " -> " + w.entriesRead + " | cut " + w.logCut;
        }

        public static string Report(RM_WorldComponent_SwallowedCore w)
        {
            int quests = Find.QuestManager.QuestsListForReading.Count(q => q.root?.defName == "RM_NavigatorSalvageSite" && q.State == QuestState.Ongoing);
            return "LOG pings " + w.pings + " | entries " + w.entriesRead + " | sites " + w.sitesRevealed + " | quests " + quests;
        }
    }
}
