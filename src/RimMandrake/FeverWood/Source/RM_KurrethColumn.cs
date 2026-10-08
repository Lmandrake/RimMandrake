using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using RimWorld.QuestGen;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_KURRETH_COLUMN_RAIDBACK_1 (part B of FEVERWOOD_ANT_THEFT_RAIDBACK_1). When a kurreth column's theft
    // letter goes out, RM_Quest_KurrethColumn is generated (auto-accepted, never rolled by the storyteller): the column
    // makes camp a few tiles away (a Site, RM_KurrethColumnCamp) holding the stolen animals alive, bound in kurreth
    // paste (RM_KurrethBound: Moving capped at 0, so downed and never targeted). A bound animal is cut free once a
    // colonist stands within 2 cells of it and no awake hostile kurreth is within 6; every surviving animal freed =
    // success. If the camp is not entered within kurrethColumnDays the column reaches its hive: with a generated ant-hive
    // dungeon on the map they were taken from, the animals are carried bound into its deepest room (same freeing rule),
    // and kurrethHiveHoldDays later anything still bound there is gone (letter); with no hive there they are simply gone
    // (letter). No silent vanishing anywhere. Numbers // INVENTED. The quest's lifecycle (ends, letters) stays in XML.
    [DefOf]
    public static class RM_KurrethColumnDefOf
    {
        public static QuestScriptDef RM_Quest_KurrethColumn;
        public static SitePartDef RM_KurrethColumnCamp;
        public static HediffDef RM_KurrethBound;

        static RM_KurrethColumnDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_KurrethColumnDefOf));
        }
    }

    public static class RM_KurrethColumnUtility
    {
        public const string FactionDefName = "RM_FactionDef_KurrethSwarm";
        public const int MinTiles = 2;
        public const int MaxTiles = 6;

        public static Faction KurrethFaction(bool create)
        {
            FactionDef fd = DefDatabase<FactionDef>.GetNamedSilentFail(FactionDefName);
            if (fd == null)
            {
                return null;
            }
            Faction f = Find.FactionManager.FirstFactionOfDef(fd);
            if (f == null && create)
            {
                f = FactionGenerator.NewGeneratedFaction(new FactionGeneratorParms(fd));
                Find.FactionManager.Add(f);
            }
            return f;
        }

        /// <summary>Guards at the camp: three plus one per animal held, 4..9.</summary>
        public static int GuardCount(int victims)
        {
            return Mathf.Clamp(3 + victims, 4, 9);
        }

        /// <summary>Called from the theft letter: one quest per column. False when off or nothing qualifies.</summary>
        public static Quest TryStartColumnQuest(Map map, List<Pawn> victims)
        {
            if (!RM_FeverWoodSettings.kurrethColumnEnabled || map == null)
            {
                return null;
            }
            List<Pawn> alive = victims.Where(p => p != null && !p.Dead && !p.Destroyed).Distinct().ToList();
            if (alive.Count == 0)
            {
                return null;
            }
            Slate slate = new Slate();
            slate.Set("map", map);
            slate.Set("victims", alive);
            if (!RM_KurrethColumnDefOf.RM_Quest_KurrethColumn.CanRun(slate, map))
            {
                return null;
            }
            try
            {
                return QuestUtility.GenerateQuestAndMakeAvailable(RM_KurrethColumnDefOf.RM_Quest_KurrethColumn, slate);
            }
            catch (System.Exception e)
            {
                // The theft letter must still go out (no silent vanishing) even if quest generation breaks.
                Log.Error("[FeverWood] kurreth column quest failed to generate: " + e);
                return null;
            }
        }

        public static RM_QuestPart_KurrethColumn PartFor(MapParent parent)
        {
            foreach (Quest q in Find.QuestManager.QuestsListForReading)
            {
                if (q.Historical)
                {
                    continue;
                }
                foreach (QuestPart part in q.PartsListForReading)
                {
                    if (part is RM_QuestPart_KurrethColumn c && c.site == parent)
                    {
                        return c;
                    }
                }
            }
            return null;
        }

        /// <summary>Takes a held animal out of the swarm's kidnap list and the world, back to the player, and lays it
        /// down bound near the cell.</summary>
        public static bool SpawnBound(Pawn p, IntVec3 near, Map map)
        {
            if (p == null || p.Dead || p.Destroyed || p.Spawned)
            {
                return false;
            }
            Faction f = KurrethFaction(false);
            if (f?.kidnapped != null && f.kidnapped.KidnappedPawnsListForReading.Contains(p))
            {
                f.kidnapped.RemoveKidnappedPawn(p);
            }
            if (Find.WorldPawns.Contains(p))
            {
                Find.WorldPawns.RemovePawn(p);
            }
            if (p.Faction != Faction.OfPlayer)
            {
                p.SetFaction(Faction.OfPlayer);
            }
            IntVec3 cell = CellFinder.RandomClosewalkCellNear(near, map, 3);
            GenSpawn.Spawn(p, cell, map);
            if (!p.health.hediffSet.HasHediff(RM_KurrethColumnDefOf.RM_KurrethBound))
            {
                p.health.AddHediff(RM_KurrethColumnDefOf.RM_KurrethBound);
            }
            return true;
        }

        public static bool IsBound(Pawn p)
        {
            return p != null && !p.Dead && p.health.hediffSet.HasHediff(RM_KurrethColumnDefOf.RM_KurrethBound);
        }

        /// <summary>Cut free: a colonist within 2 cells, no awake hostile kurreth within 6.</summary>
        public static bool CanBeFreed(Pawn victim)
        {
            if (!victim.Spawned || !IsBound(victim))
            {
                return false;
            }
            Map map = victim.Map;
            bool colonistNear = false;
            bool guarded = false;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (p == victim || p.Dead)
                {
                    continue;
                }
                float d = p.Position.DistanceTo(victim.Position);
                if (p.IsColonist && !p.Downed && d <= 2f && p.CanReach(victim, PathEndMode.Touch, Danger.Deadly))
                {
                    colonistNear = true;
                }
                if (p.def.defName == "RM_Kurreth" && !p.Downed && p.Awake() && p.HostileTo(Faction.OfPlayer) && d <= 6f)
                {
                    guarded = true;
                }
            }
            return colonistNear && !guarded;
        }

        public static void Free(Pawn victim)
        {
            Hediff h = victim.health.hediffSet.GetFirstHediffOfDef(RM_KurrethColumnDefOf.RM_KurrethBound);
            if (h != null)
            {
                victim.health.RemoveHediff(h);
            }
            Messages.Message(victim.LabelShortCap + " is cut out of the kurreth paste and is free.", victim,
                MessageTypeDefOf.PositiveEvent);
        }
    }

    /// <summary>Slate in: map, victims (List&lt;Pawn&gt;). Slate out: site (unspawned, no faction), columnTicks,
    /// victimsLabel (both read by the description). Adds the RM_QuestPart_KurrethColumn that runs the camp, the hive and the ends.</summary>
    public class RM_QuestNode_KurrethColumn : QuestNode
    {
        public SlateRef<string> storeSiteAs = "site";
        public SlateRef<string> outSignalRecovered;
        public SlateRef<string> outSignalLost;

        protected override bool TestRunInt(Slate slate)
        {
            Map map = slate.Get<Map>("map");
            List<Pawn> victims = slate.Get<List<Pawn>>("victims");
            return RM_FeverWoodSettings.kurrethColumnEnabled && map != null && victims != null && victims.Count > 0
                   && TileFinder.TryFindNewSiteTile(out PlanetTile _, map.Tile, RM_KurrethColumnUtility.MinTiles,
                       RM_KurrethColumnUtility.MaxTiles);
        }

        protected override void RunInt()
        {
            Slate slate = QuestGen.slate;
            Map map = slate.Get<Map>("map");
            List<Pawn> victims = slate.Get<List<Pawn>>("victims");
            if (!TileFinder.TryFindNewSiteTile(out PlanetTile tile, map.Tile, RM_KurrethColumnUtility.MinTiles,
                    RM_KurrethColumnUtility.MaxTiles))
            {
                return;
            }
            Site site = SiteMaker.MakeSite(RM_KurrethColumnDefOf.RM_KurrethColumnCamp, tile, null);
            slate.Set(storeSiteAs.GetValue(slate), site);
            int columnTicks = Mathf.RoundToInt(RM_FeverWoodSettings.kurrethColumnDays * 60000f);
            slate.Set("columnTicks", columnTicks);
            slate.Set("victimsLabel", victims.Select(v => v.LabelShort).ToCommaList(true));
            var part = new RM_QuestPart_KurrethColumn
            {
                inSignalEnable = slate.Get<string>("inSignal"),
                site = site,
                originMap = map,
                victims = new List<Pawn>(victims),
                columnDeadline = Find.TickManager.TicksGame + columnTicks,
                hiveHoldTicks = Mathf.RoundToInt(RM_FeverWoodSettings.kurrethHiveHoldDays * 60000f),
                outSignalRecovered = QuestGenUtility.HardcodedSignalWithQuestID(outSignalRecovered.GetValue(slate)),
                outSignalLost = QuestGenUtility.HardcodedSignalWithQuestID(outSignalLost.GetValue(slate))
            };
            QuestGen.quest.AddPart(part);
        }
    }

    public class RM_QuestPart_KurrethColumn : QuestPartActivable
    {
        public enum Phase { Column, Camp, Hive, Done }

        private const int Interval = 250;

        public Site site;
        public Map originMap;
        public List<Pawn> victims = new List<Pawn>();
        public int columnDeadline = -1;
        public int hiveHoldTicks;
        public int hiveDeadline = -1;
        public Phase phase = Phase.Column;
        public string outSignalRecovered;
        public string outSignalLost;

        public override IEnumerable<GlobalTargetInfo> QuestLookTargets
        {
            get
            {
                if (site != null && !site.Destroyed)
                {
                    yield return site;
                }
                foreach (Pawn p in victims)
                {
                    if (p != null && p.Spawned)
                    {
                        yield return p;
                    }
                }
            }
        }

        public override string ExpiryInfoPart
        {
            get
            {
                int now = Find.TickManager.TicksGame;
                if (phase == Phase.Column && columnDeadline > now)
                {
                    return "The column reaches its hive in " + (columnDeadline - now).ToStringTicksToPeriod();
                }
                if (phase == Phase.Hive && hiveDeadline > now)
                {
                    return "Held in the hive for " + (hiveDeadline - now).ToStringTicksToPeriod() + " more";
                }
                return null;
            }
        }

        public List<Pawn> Living => victims.Where(p => p != null && !p.Dead && !p.Destroyed).ToList();

        /// <summary>RM_SitePartWorker_KurrethColumnCamp.PostMapGenerate: the held animals and their guards.</summary>
        public int SpawnCamp(Map map)
        {
            if (phase != Phase.Column)
            {
                return 0;
            }
            // The out parameter is overwritten (Invalid) on failure, so the fallback must be applied after the call.
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 12, c => c.Standable(map) && !c.Fogged(map), out IntVec3 centre))
            {
                centre = map.Center;
            }
            int n = 0;
            foreach (Pawn p in Living)
            {
                if (RM_KurrethColumnUtility.SpawnBound(p, centre, map))
                {
                    n++;
                }
            }
            Faction f = RM_KurrethColumnUtility.KurrethFaction(true);
            PawnKindDef ant = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Kurreth");
            if (f != null && ant != null)
            {
                var guards = new List<Pawn>();
                for (int i = 0; i < RM_KurrethColumnUtility.GuardCount(n); i++)
                {
                    Pawn g = PawnGenerator.GeneratePawn(ant, f);
                    GenSpawn.Spawn(g, CellFinder.RandomClosewalkCellNear(centre, map, 6), map);
                    guards.Add(g);
                }
                LordMaker.MakeNewLord(f, new LordJob_DefendPoint(centre, 6f, 10f), map, guards);
            }
            phase = Phase.Camp;
            return n;
        }

        public override void QuestPartTick()
        {
            base.QuestPartTick();
            if (Find.TickManager.TicksGame % Interval != 0 || phase == Phase.Done)
            {
                return;
            }
            Step();
        }

        /// <summary>One check; public so the proof can drive it without waiting for the interval.</summary>
        public void Step()
        {
            int now = Find.TickManager.TicksGame;
            switch (phase)
            {
                case Phase.Column:
                    if (now >= columnDeadline && (site == null || !site.HasMap))
                    {
                        ReachHive();
                    }
                    break;
                case Phase.Camp:
                    if (site == null || !site.HasMap)
                    {
                        if (Living.Any(RM_KurrethColumnUtility.IsBound))
                        {
                            Lose("The camp is behind you, and the kurreth went on with what they had. " + StillBoundLabel()
                                 + " will not be seen again.");
                            return;
                        }
                    }
                    CheckFreed();
                    break;
                case Phase.Hive:
                    CheckFreed();
                    if (phase == Phase.Hive && now >= hiveDeadline)
                    {
                        List<Pawn> lost = Living.Where(RM_KurrethColumnUtility.IsBound).ToList();
                        string label = StillBoundLabel();
                        foreach (Pawn p in lost)
                        {
                            p.Destroy();
                        }
                        Lose("Too long in the hive. The kurreth have finished with " + label + "; nothing of "
                             + (lost.Count == 1 ? "it" : "them") + " is left to bring home.");
                    }
                    break;
            }
        }

        private string StillBoundLabel()
        {
            List<Pawn> b = Living.Where(RM_KurrethColumnUtility.IsBound).ToList();
            return b.Count == 0 ? "the stolen animals" : b.Select(p => p.LabelShort).ToCommaList(true);
        }

        private void CheckFreed()
        {
            foreach (Pawn p in Living)
            {
                if (RM_KurrethColumnUtility.CanBeFreed(p))
                {
                    RM_KurrethColumnUtility.Free(p);
                }
            }
            List<Pawn> living = Living;
            if (living.Count == 0)
            {
                Lose("None of the stolen animals lived.");
                return;
            }
            if (living.All(p => !RM_KurrethColumnUtility.IsBound(p)))
            {
                phase = Phase.Done;
                Find.SignalManager.SendSignal(new Signal(outSignalRecovered));
            }
        }

        private void ReachHive()
        {
            if (site != null && !site.Destroyed && !site.HasMap)
            {
                site.Destroy();
            }
            Map hiveMap = originMap != null && Find.Maps.Contains(originMap) ? originMap : null;
            RM_MapComponent_AntHive hive = hiveMap?.GetComponent<RM_MapComponent_AntHive>();
            if (hive == null || !hive.HasHive)
            {
                Lose("The kurreth column reached a hive somewhere you cannot follow. " + StillBoundLabel()
                     + " will not be seen again.");
                return;
            }
            IntVec3 room = hive.QueenRoom;
            List<Pawn> carried = new List<Pawn>();
            foreach (Pawn p in Living)
            {
                if (RM_KurrethColumnUtility.SpawnBound(p, room, hiveMap))
                {
                    carried.Add(p);
                }
            }
            if (carried.Count == 0)
            {
                Lose("The kurreth column reached its hive, and nothing it carried came out alive.");
                return;
            }
            phase = Phase.Hive;
            hiveDeadline = Find.TickManager.TicksGame + hiveHoldTicks;
            Find.LetterStack.ReceiveLetter("Carried into the hive",
                "The column was not stopped. It has carried " + carried.Select(p => p.LabelShort).ToCommaList(true)
                + " down into the ant hive under your own ground, to the deepest chamber, still alive and bound.\n\n"
                + "Get a colonist to them while no kurreth stands guard close by and they can be cut free. Leave them "
                + "there " + hiveHoldTicks.ToStringTicksToPeriod() + " and there will be nothing left to cut free.",
                LetterDefOf.NegativeEvent, new LookTargets(carried));
        }

        private void Lose(string text)
        {
            phase = Phase.Done;
            Find.LetterStack.ReceiveLetter("Lost to the kurreth", text, LetterDefOf.NegativeEvent);
            Find.SignalManager.SendSignal(new Signal(outSignalLost));
        }

        public override void Cleanup()
        {
            base.Cleanup();
            if (site != null && !site.Destroyed && !site.HasMap)
            {
                site.Destroy();
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref site, "site");
            Scribe_References.Look(ref originMap, "originMap");
            Scribe_Collections.Look(ref victims, "victims", LookMode.Reference);
            Scribe_Values.Look(ref columnDeadline, "columnDeadline", -1);
            Scribe_Values.Look(ref hiveHoldTicks, "hiveHoldTicks");
            Scribe_Values.Look(ref hiveDeadline, "hiveDeadline", -1);
            Scribe_Values.Look(ref phase, "phase", Phase.Column);
            Scribe_Values.Look(ref outSignalRecovered, "outSignalRecovered");
            Scribe_Values.Look(ref outSignalLost, "outSignalLost");
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                victims = victims ?? new List<Pawn>();
                victims.RemoveAll(p => p == null);
            }
        }
    }

    public class RM_SitePartWorker_KurrethColumnCamp : SitePartWorker
    {
        public override void PostMapGenerate(Map map)
        {
            base.PostMapGenerate(map);
            RM_KurrethColumnUtility.PartFor(map.Parent)?.SpawnCamp(map);
        }
    }

    /// <summary>Proof hooks for the kurreth_column chain (static_call, args "current").</summary>
    public static class RM_KurrethColumnProof
    {
        private static RM_QuestPart_KurrethColumn Latest()
        {
            return Find.QuestManager.QuestsListForReading.Where(q => !q.Historical)
                .SelectMany(q => q.PartsListForReading.OfType<RM_QuestPart_KurrethColumn>()).LastOrDefault();
        }

        /// <summary>After ProofRaid + the theft letter: the open column quest, its site, phase and held ids.</summary>
        public static string ProofQuest(Map map)
        {
            RM_QuestPart_KurrethColumn part = Latest();
            if (part == null)
            {
                return "quest=0";
            }
            return "quest=1 phase=" + part.phase + " site=" + (part.site != null && !part.site.Destroyed ? 1 : 0)
                   + " siteTile=" + (part.site?.Tile.ToString() ?? "-") + " held=" + part.Living.Count
                   + " bound=" + part.Living.Count(RM_KurrethColumnUtility.IsBound)
                   + " victimIds=" + string.Join(",", part.victims.Select(v => v?.thingIDNumber.ToString() ?? "?"));
        }

        /// <summary>Forces the column's deadline to now and steps once (the hive carry, or the lost letter).</summary>
        public static string ProofHive(Map map)
        {
            RM_QuestPart_KurrethColumn part = Latest();
            if (part == null)
            {
                return "ERROR no column quest";
            }
            part.columnDeadline = Find.TickManager.TicksGame;
            part.Step();
            return ProofQuest(map);
        }
    }
}
