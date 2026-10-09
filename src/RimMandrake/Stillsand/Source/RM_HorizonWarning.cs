using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_SKELETONS_TRACKS_1 §8 — "Nothing hides, including you."
    // Design: stillsand_turn3_development_2026-09-30.md §3.3.
    //
    // A prefix on Storyteller.TryFire(FiringIncident, bool queued). When a
    // raid (any IncidentWorker_Raid) or a neutral group (IncidentWorker_
    // NeutralGroup: traders, visitors, travellers) is about to fire on a map
    // whose biome carries RM_SkeletonBiomeExtension.horizonWarnings:
    //   1. its entry cell is chosen now (RCellFinder.TryFindRandomPawnEntryCell)
    //      and written to parms.spawnCenter — every edge walk-in and drop
    //      arrival mode honours a valid preset spawnCenter (RimSage:
    //      PawnsArrivalModeWorker_EdgeWalkIn / CenterDrop / EdgeDrop /
    //      ClusterDrop, IncidentWorker_NeutralGroup), so the bearing in the
    //      letter is where they really come from;
    //   2. the incident is re-queued on the storyteller's IncidentQueue
    //      RM_SkeletonSettings.horizonWarningHours later (IncidentParms is
    //      fully saved, spawnCenter included);
    //   3. a letter "Dust on the horizon, bearing north-west" and a dust plume
    //      at the entry cell, which keeps rising until arrival.
    // When the queue fires it, TryFire runs with queued=true and the prefix
    // lets it through. Quest-driven incidents (parms.quest / questTag) are
    // never delayed: their signals expect them on time.
    //
    // Wandering giants (STILLSAND_SKELETONS_REMAINDER_1 §6): herd migrations
    // and thrumbo-style passes choose their own entry cell through
    // RCellFinder.TryFindRandomPawnEntryCell and ignore spawnCenter. So for
    // those workers a prefix on IncidentWorker.TryExecute arms a one-shot
    // [ThreadStatic] ForcedEntry from the queued parms.spawnCenter, and a
    // prefix on TryFindRandomPawnEntryCell hands it back to the FIRST call
    // (both workers' first call is their entry cell; HerdMigration's exit
    // cell uses CellFinder.TryFindRandomEdgeCellWith, untouched). The
    // finalizer always disarms it. Gated by horizonPassersEnabled.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_HorizonWarningPatches
    {
        static RM_HorizonWarningPatches()
        {
            const string rule = "[RimMandrake.Stillsand] horizon warning: ";
            var tryFire = AccessTools.Method(typeof(Storyteller), nameof(Storyteller.TryFire));
            var tryExecute = AccessTools.Method(typeof(IncidentWorker), nameof(IncidentWorker.TryExecute));
            var entryCell = AccessTools.Method(typeof(RCellFinder), nameof(RCellFinder.TryFindRandomPawnEntryCell));
            if (tryFire == null || tryExecute == null || entryCell == null)
            {
                Log.Error(rule + "a patch target was NOT FOUND (TryFire " + (tryFire != null) + ", TryExecute "
                          + (tryExecute != null) + ", TryFindRandomPawnEntryCell " + (entryCell != null)
                          + "); horizon warnings are off this session.");
                return;
            }
            Harmony harmony = new Harmony("mandrake.rm.stillsand.horizon");
            try
            {
                // Entry forcing first, the deferring TryFire prefix last: if anything fails,
                // incidents are never deferred without their announced bearing being honoured.
                harmony.Patch(tryExecute,
                    prefix: new HarmonyMethod(typeof(RM_HorizonWarningPatches), nameof(TryExecutePrefix)),
                    finalizer: new HarmonyMethod(typeof(RM_HorizonWarningPatches), nameof(TryExecuteFinalizer)));
                harmony.Patch(entryCell,
                    prefix: new HarmonyMethod(typeof(RM_HorizonWarningPatches), nameof(EntryCellPrefix)));
                harmony.Patch(tryFire,
                    prefix: new HarmonyMethod(typeof(RM_HorizonWarningPatches), nameof(TryFirePrefix)),
                    postfix: new HarmonyMethod(typeof(RM_HorizonWarningPatches), nameof(TryFirePostfix)));
            }
            catch (Exception e)
            {
                harmony.UnpatchAll(harmony.Id);
                Log.Error(rule + "patching FAILED, all horizon patches removed: " + e);
            }
        }

        [System.ThreadStatic] private static IntVec3 forcedEntry;
        [System.ThreadStatic] private static Map forcedMap;

        /// <summary>Session counter for a dev/bridge read: passers that really entered from the
        /// announced bearing. Never saved.</summary>
        public static int PassersHonoured;

        /// <summary>The wandering-giant workers: they pick their own entry cell.</summary>
        public static bool IsPasser(System.Type w)
        {
            return w != null && (typeof(IncidentWorker_HerdMigration).IsAssignableFrom(w)
                                 || typeof(IncidentWorker_ThrumboPasses).IsAssignableFrom(w));
        }

        public static void TryExecutePrefix(IncidentWorker __instance, IncidentParms parms, out KeyValuePair<IntVec3, Map> __state)
        {
            // A nested incident must not wipe the outer one's announced entry: keep it, restore it after.
            __state = new KeyValuePair<IntVec3, Map>(forcedEntry, forcedMap);
            forcedEntry = IntVec3.Invalid;
            forcedMap = null;
            if (!RM_SkeletonSettings.horizonWarningsEnabled || !RM_SkeletonSettings.horizonPassersEnabled
                || parms == null || !parms.spawnCenter.IsValid || __instance?.def == null
                || !IsPasser(__instance.def.workerClass) || !(parms.target is Map map)
                || !Applies(__instance.def, parms, map))
            {
                return;
            }
            forcedEntry = parms.spawnCenter;
            forcedMap = map;
        }

        public static System.Exception TryExecuteFinalizer(System.Exception __exception, KeyValuePair<IntVec3, Map> __state)
        {
            forcedEntry = __state.Key;
            forcedMap = __state.Value;
            return __exception;
        }

        public static bool EntryCellPrefix(ref IntVec3 result, Map map, Predicate<IntVec3> extraValidator, ref bool __result)
        {
            if (forcedMap == null || map != forcedMap || !forcedEntry.IsValid)
            {
                return true;
            }
            IntVec3 c = forcedEntry;
            forcedEntry = IntVec3.Invalid; // one shot: the worker's first call only
            forcedMap = null;
            if (!c.InBounds(map) || !c.Standable(map) || c.Fogged(map)
                || (extraValidator != null && !extraValidator(c)))
            {
                return true; // the announced cell went bad: vanilla picks, the bearing may be off
            }
            result = c;
            __result = true;
            PassersHonoured++;
            return false;
        }

        public static bool TryFirePrefix(FiringIncident fi, bool queued, ref bool __result)
        {
            if (queued || !RM_SkeletonSettings.horizonWarningsEnabled || fi?.def?.Worker == null || fi.parms == null)
            {
                return true;
            }
            if (!(fi.parms.target is Map map) || !Applies(fi.def, fi.parms, map))
            {
                return true;
            }
            if (!fi.def.Worker.CanFireNow(fi.parms))
            {
                return true; // let vanilla decline it as it would have
            }
            bool passer = IsPasser(fi.def.workerClass);
            if (!fi.parms.spawnCenter.IsValid
                && !RCellFinder.TryFindRandomPawnEntryCell(out fi.parms.spawnCenter, map,
                    passer ? CellFinder.EdgeRoadChance_Animal : CellFinder.EdgeRoadChance_Hostile))
            {
                return true;
            }
            int delay = Mathf.Max(1, Mathf.RoundToInt(RM_SkeletonSettings.horizonWarningHours * GenDate.TicksPerHour));
            int fireTick = Find.TickManager.TicksGame + delay;
            Find.Storyteller.incidentQueue.Add(fi.def, fireTick, fi.parms, GenDate.TicksPerHour);
            RM_MapComponent_HorizonPlume.For(map)?.Add(fi.parms.spawnCenter, fireTick, fi.def.defName, Bearing(map.Center, fi.parms.spawnCenter));
            SendLetter(fi.def, fi.parms, map);
            __result = true;
            return false;
        }

        /// <summary>DUST_SETTLED_LETTER_1: a queued fire that went through means the announced group really arrived, so
        /// its plume ends now (not at a fixed tick) and no "turned back" letter is owed.</summary>
        public static void TryFirePostfix(FiringIncident fi, bool queued, bool __result)
        {
            if (!queued || !__result || fi?.parms == null || fi.def == null || !(fi.parms.target is Map map)
                || !fi.parms.spawnCenter.IsValid)
            {
                return;
            }
            RM_MapComponent_HorizonPlume.For(map)?.Notify_Arrived(fi.def.defName, fi.parms.spawnCenter);
        }

        /// <summary>Which incidents the horizon shows. Public for the selftest's
        /// shape and a dev state read.</summary>
        public static bool Applies(IncidentDef def, IncidentParms parms, Map map)
        {
            RM_SkeletonBiomeExtension ext = map.Biome?.GetModExtension<RM_SkeletonBiomeExtension>();
            if (ext == null || !ext.horizonWarnings)
            {
                return false;
            }
            if (parms.quest != null || !parms.questTag.NullOrEmpty())
            {
                return false;
            }
            System.Type w = def.workerClass;
            if (IsPasser(w))
            {
                return RM_SkeletonSettings.horizonPassersEnabled;
            }
            return w != null && (typeof(IncidentWorker_Raid).IsAssignableFrom(w)
                                 || typeof(IncidentWorker_NeutralGroup).IsAssignableFrom(w));
        }

        /// <summary>Eight-point bearing from the map centre to a cell, +z north.</summary>
        public static string Bearing(IntVec3 from, IntVec3 to)
        {
            float ang = Mathf.Atan2(to.z - from.z, to.x - from.x) * Mathf.Rad2Deg; // 0 = east, 90 = north
            string[] names = { "east", "north-east", "north", "north-west", "west", "south-west", "south", "south-east" };
            int i = Mathf.RoundToInt(((ang % 360f) + 360f) % 360f / 45f) % 8;
            return names[i];
        }

        private static void SendLetter(IncidentDef def, IncidentParms parms, Map map)
        {
            bool hostile = typeof(IncidentWorker_Raid).IsAssignableFrom(def.workerClass)
                           && parms.faction != null && parms.faction.HostileTo(Faction.OfPlayer);
            string bearing = Bearing(map.Center, parms.spawnCenter);
            string hours = RM_SkeletonSettings.horizonWarningHours.ToString("0.#");
            string who = parms.faction != null ? parms.faction.Name : "someone";
            if (IsPasser(def.workerClass))
            {
                Find.LetterStack.ReceiveLetter("Dust on the horizon: " + bearing,
                    "Dust on the horizon, bearing " + bearing + ", low and slow. Something big is walking the open "
                    + "sand, and out here it cannot hide. It should reach the edge of the map in about " + hours + " hours.",
                    LetterDefOf.NeutralEvent, new TargetInfo(parms.spawnCenter, map));
                return;
            }
            string text = "Dust on the horizon, bearing " + bearing + ". Out here you can see anything coming "
                          + "from hours away, and so can it.\n\n"
                          + (hostile
                              ? "It looks like a war band (" + who + "). It should reach the edge of the map in about " + hours + " hours."
                              : "A group (" + who + ") is crossing the sand toward you. It should arrive in about " + hours + " hours.");
            Find.LetterStack.ReceiveLetter("Dust on the horizon: " + bearing, text,
                hostile ? LetterDefOf.ThreatSmall : LetterDefOf.NeutralEvent,
                new TargetInfo(parms.spawnCenter, map));
        }
    }

    /// <summary>The dust plume at the entry cell, rising until the group really arrives. DUST_SETTLED_LETTER_1: the
    /// plume stands through the queue's retry window (RM_HorizonMath.PlumeUntil); if the group never arrives it goes out
    /// with a "the dust settled" letter. Entries from older saves carry no def name and just burn out quietly.</summary>
    public class RM_MapComponent_HorizonPlume : MapComponent
    {
        private List<IntVec3> cells = new List<IntVec3>();
        private List<int> untilTicks = new List<int>();   // the announced fire tick
        private List<string> defNames = new List<string>();
        private List<string> bearings = new List<string>();

        public RM_MapComponent_HorizonPlume(Map map) : base(map)
        {
        }

        public static RM_MapComponent_HorizonPlume For(Map map) => map?.GetComponent<RM_MapComponent_HorizonPlume>();

        public int ActiveCount => cells.Count;

        /// <summary>Session counter for a dev/bridge read: groups that turned back. Never saved.</summary>
        public static int TurnedBackCount;

        public void Add(IntVec3 cell, int fireTick, string defName = null, string bearing = null)
        {
            cells.Add(cell);
            untilTicks.Add(fireTick);
            defNames.Add(defName ?? "");
            bearings.Add(bearing ?? "");
        }

        private void RemoveAt(int i)
        {
            cells.RemoveAt(i);
            untilTicks.RemoveAt(i);
            defNames.RemoveAt(i);
            bearings.RemoveAt(i);
        }

        /// <summary>The announced group went through: end its plume.</summary>
        public void Notify_Arrived(string defName, IntVec3 cell)
        {
            for (int i = cells.Count - 1; i >= 0; i--)
            {
                if (RM_HorizonMath.Matches(defNames[i], cells[i].x, cells[i].z, defName, cell.x, cell.z))
                {
                    RemoveAt(i);
                    return;
                }
            }
        }

        public override void MapComponentTick()
        {
            if (cells.Count == 0 || Find.TickManager.TicksGame % 45 != 0)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            for (int i = cells.Count - 1; i >= 0; i--)
            {
                bool tracked = defNames[i].Length > 0;
                if (tracked ? now > RM_HorizonMath.PlumeUntil(untilTicks[i]) : now >= untilTicks[i])
                {
                    if (tracked && RM_SkeletonSettings.dustSettledLetterEnabled && RM_HorizonMath.TurnedBack(now, untilTicks[i], false))
                    {
                        TurnedBackCount++;
                        Find.LetterStack.ReceiveLetter("The dust settled: " + bearings[i],
                            "The dust on the horizon, bearing " + bearings[i] + ", has settled. Whoever it was never came: "
                            + "they turned back, or lost their way on the sand.",
                            LetterDefOf.NeutralEvent, new TargetInfo(cells[i], map));
                    }
                    RemoveAt(i);
                    continue;
                }
                Vector3 loc = cells[i].ToVector3Shifted() + new Vector3(Rand.Range(-2f, 2f), 0f, Rand.Range(-2f, 2f));
                FleckMaker.ThrowDustPuffThick(loc, map, Rand.Range(2.5f, 4f), new Color(0.82f, 0.72f, 0.55f, 0.8f));
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref cells, "plumeCells", LookMode.Value);
            Scribe_Collections.Look(ref untilTicks, "plumeUntil", LookMode.Value);
            Scribe_Collections.Look(ref defNames, "plumeDefs", LookMode.Value);
            Scribe_Collections.Look(ref bearings, "plumeBearings", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                cells = cells ?? new List<IntVec3>();
                untilTicks = untilTicks ?? new List<int>();
                if (cells.Count != untilTicks.Count)
                {
                    cells.Clear();
                    untilTicks.Clear();
                }
                // Saves from before this item carry no def names: pad them as untracked (quiet burn-out).
                defNames = defNames ?? new List<string>();
                bearings = bearings ?? new List<string>();
                while (defNames.Count < cells.Count) defNames.Add("");
                while (bearings.Count < cells.Count) bearings.Add("");
                if (defNames.Count > cells.Count) defNames.RemoveRange(cells.Count, defNames.Count - cells.Count);
                if (bearings.Count > cells.Count) bearings.RemoveRange(cells.Count, bearings.Count - cells.Count);
            }
        }
    }
}
