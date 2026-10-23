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
    //   last camp ROT_WARM_MAT_BUILD_WORKS_FOR_FOOD (owner by card 2026-10-22: the living mat root is a QUEST REWARD). The
    //             entry named lastCampEntry (the log's last site, entry 8) reveals lastCampQuest (RM_NavigatorLastCamp) instead
    //             of a plain salvage site: the crew's last camp, where the warm mat took them in and a root of it knotted where
    //             they lay. Its stash holds a minified RM_LivingMatRoot (RM_QuestNode_AddMinifiedToStash). With the root
    //             switched off in Mod Settings (portableWarmMat) the entry reveals a plain salvage site. The cost of this route:
    //             the root is earned only by a player who keeps the giant alive long enough to hear the whole log
    //             (lastCampEntry x navigatorPingsPerEntry pings); cutting the core out early ends the log, and the root with it.
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
        public int lastCampEntry = -1;
        public QuestScriptDef lastCampQuest;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (entries.NullOrEmpty()) yield return "no entries";
            foreach (int i in siteEntries)
            {
                if (i < 1 || i > entries.Count) yield return "siteEntries names entry " + i + " of " + entries.Count;
            }
            if (lastCampEntry > 0 && (lastCampQuest == null || !siteEntries.Contains(lastCampEntry)))
            {
                yield return "lastCampEntry " + lastCampEntry + " must be one of siteEntries and name a lastCampQuest";
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
            if (def.siteEntries.Contains(n) && TryRevealSite(w, def, map, SiteScriptFor(def, n)) != null)
            {
                w.sitesRevealed++;
                tail = "\n\nThe entry names a place. Your navigator has marked it on the map.";
            }
            Find.LetterStack.ReceiveLetter("Ship's log, entry " + n,
                "The pulse in the console has resolved into words: an old flight log, played back one entry at a time.\n\n\"" + text + "\"" + tail,
                LetterDefOf.NeutralEvent);
        }

        /// <summary>The quest an entry's site uses: the last camp (the mat root's quest) for lastCampEntry while the root is
        /// switched on, otherwise the plain salvage site (null).</summary>
        public static QuestScriptDef SiteScriptFor(RM_NavigatorLogDef def, int entry)
        {
            return entry == def.lastCampEntry && def.lastCampQuest != null && RM_TheRotSettings.portableWarmMat ? def.lastCampQuest : null;
        }

        public static Quest TryRevealSite(RM_WorldComponent_SwallowedCore w, RM_NavigatorLogDef def, Map map, QuestScriptDef scriptOverride = null)
        {
            QuestScriptDef script = scriptOverride ?? DefDatabase<QuestScriptDef>.GetNamedSilentFail("RM_NavigatorSalvageSite");
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

    /// <summary>
    /// QuestGen node (ROT_WARM_MAT_BUILD_WORKS_FOR_FOOD): puts one minified <c>thingDef</c> into the site's item stash, after
    /// Util_GenerateSite and before the stash's QuestNode_AddItemsReward, and appends it to generatedItemStashThings so the reward
    /// listing shows it. The stash's own [itemStashContents] text was written before this node runs, so the quest text names the
    /// added thing itself. A site with no stash part logs an error and gives nothing (never a silent miss).
    /// </summary>
    public class RM_QuestNode_AddMinifiedToStash : QuestNode
    {
        public SlateRef<ThingDef> thingDef;
        public SlateRef<Site> site;

        protected override bool TestRunInt(Slate slate)
        {
            return thingDef.GetValue(slate) != null;
        }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            ThingDef def = thingDef.GetValue(slate);
            Site s = site.GetValue(slate);
            SitePart part = s?.parts?.FirstOrDefault(p => p.things != null);
            if (def == null || part == null)
            {
                Log.Error("[TheRot] RM_QuestNode_AddMinifiedToStash: no " + (def == null ? "thingDef" : "item-stash site part") + "; the reward was not added.");
                return;
            }
            Thing inner = ThingMaker.MakeThing(def);
            Thing reward = def.Minifiable ? inner.MakeMinified() : inner;
            part.things.TryAdd(reward, false);
            slate.Get<List<Thing>>("generatedItemStashThings")?.Add(reward);
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

        /// <summary>Generates the last-camp quest directly (sitesRevealed is not moved) and reads its site's stash.
        /// "CAMP quest Q | site S | stash n | root R" or "REFUSED: why".</summary>
        public static string ProofLastCamp()
        {
            RM_WorldComponent_SwallowedCore w = RM_WorldComponent_SwallowedCore.Get;
            RM_NavigatorLogDef def = RM_NavigatorLog.Def;
            if (w == null || def == null) return "REFUSED: no world component or log def";
            if (def.lastCampQuest == null) return "REFUSED: the log names no lastCampQuest";
            Quest q = RM_NavigatorLog.TryRevealSite(w, def, Find.CurrentMap, def.lastCampQuest);
            if (q == null) return "REFUSED: " + def.lastCampQuest.defName + " could not run here";
            Site site = q.PartsListForReading.OfType<QuestPart_SpawnWorldObject>().Select(p => p.worldObject).OfType<Site>().FirstOrDefault();
            SitePart part = site?.parts?.FirstOrDefault(p => p.things != null);
            int n = part?.things?.Count ?? 0;
            bool root = part != null && part.things.Any(t => (t as MinifiedThing)?.InnerThing?.def.defName == "RM_LivingMatRoot");
            return "CAMP quest " + q.root.defName + " | site " + (site != null) + " | stash " + n + " | root " + root;
        }

        public static string Report(RM_WorldComponent_SwallowedCore w)
        {
            int quests = Find.QuestManager.QuestsListForReading.Count(q => q.root?.defName == "RM_NavigatorSalvageSite" && q.State == QuestState.Ongoing);
            return "LOG pings " + w.pings + " | entries " + w.entriesRead + " | sites " + w.sitesRevealed + " | quests " + quests;
        }
    }
}
