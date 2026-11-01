using System.Collections.Generic;
using System.Linq;
using RimMandrake.RustCathedral.Hum;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.RustCathedral
{
    /// <summary>RUSTCATHEDRAL_WORN_BIT_ARC_1: deterministic reads and triggers for jawa/static_call on the CURRENT map, used by
    /// validation.py's worn_bit chain. Each proof spawns its own hulk, binds the map's attitude to the Cathedral's def as the
    /// hum proof does, and destroys the hulk after. Every return is a one-line "KEY value" record.</summary>
    public static class RM_WornBitProof
    {
        private const string AttitudeDefName = "RM_RustCathedralAttitude";

        private static RM_CompBorehulkDrill SpawnHulk(Map map)
        {
            RM_MapComponent_BiomeAttitude a = map.GetComponent<RM_MapComponent_BiomeAttitude>();
            a?.ProofUseDef(DefDatabase<RM_BiomeAttitudeDef>.GetNamed(AttitudeDefName));
            a?.ProofReset();
            a?.ProofUseDef(DefDatabase<RM_BiomeAttitudeDef>.GetNamed(AttitudeDefName));
            a?.ProofBandAt(0f);
            Pawn hulk = PawnGenerator.GeneratePawn(PawnKindDef.Named("RM_Borehulk"), null);
            GenSpawn.Spawn(hulk, CellFinder.RandomClosewalkCellNear(map.Center, map, 8), map);
            return hulk.TryGetComp<RM_CompBorehulkDrill>();
        }

        private static void Clean(RM_CompBorehulkDrill comp)
        {
            Thing t = comp.parent;
            if (t != null && !t.Destroyed)
            {
                t.Destroy();
            }
            RM_WornBitGame g = RM_WornBitGame.Instance;
            if (g != null)
            {
                g.yard?.Destroy();
                if (g.quest != null && g.quest.State == QuestState.Ongoing)
                {
                    g.quest.End(QuestEndOutcome.Unknown, sendLetter: false);
                }
                g.yard = null;
                g.quest = null;
                g.hulk = null;
                g.stage = RM_WornBitStage.None;
                g.demandRolled = false;
                g.secondFee = 0;
                g.haggled = false;
            }
            Map map = Find.CurrentMap;
            foreach (ThingDef d in new[] { RM_WornBitDefOf.RM_WornDrillHead, RM_WornBitDefOf.RM_RefurbishedDrillHead })
            {
                foreach (Thing x in map.listerThings.ThingsOfDef(d).ToList())
                {
                    x.Destroy();
                }
            }
        }

        /// <summary>STAGE1 lone L two T band2 B done state heads</summary>
        public static string ProofStage1()
        {
            Map map = Find.CurrentMap;
            RM_CompBorehulkDrill comp = SpawnHulk(map);
            try
            {
                for (int i = 0; i < 2500; i++) { RM_WornBit.UnbitTick(comp, 1, 1f); }
                float lone = comp.unbitProgress;
                for (int i = 0; i < 100; i++) { RM_WornBit.UnbitTick(comp, 2, 1f); RM_WornBit.UnbitTick(comp, 2, 1f); }
                float two = comp.unbitProgress;
                map.GetComponent<RM_MapComponent_BiomeAttitude>().ProofBandAt(55f);
                int band = RM_MapComponent_BiomeAttitude.GetBand(map);
                for (int i = 0; i < 100; i++) { RM_WornBit.UnbitTick(comp, 2, 1f); }
                float stopped = comp.unbitProgress;
                map.GetComponent<RM_MapComponent_BiomeAttitude>().ProofBandAt(0f);
                int calm = RM_MapComponent_BiomeAttitude.GetBand(map);
                while (comp.State == RM_BorehulkDrillState.Worn) { RM_WornBit.UnbitTick(comp, 2, 2f); }
                int heads = map.listerThings.ThingsOfDef(RM_WornBitDefOf.RM_WornDrillHead).Count;
                RM_WornBitGame g = RM_WornBitGame.Instance;
                string factionName = g.yard?.Faction?.def.defName ?? "none";
                int quests = Find.QuestManager.QuestsListForReading.Count(q => q.root == RM_WornBitDefOf.RM_WornBitRefurbishment && q.State == QuestState.Ongoing);
                return "STAGE1 lone " + lone + " two " + two + " band " + band + " stopped " + stopped + " calm " + calm + " state " + comp.State + " heads " + heads
                    + " quests " + quests + " yardfaction " + factionName + " stage " + g.stage;
            }
            finally
            {
                Clean(comp);
            }
        }

        /// <summary>Delivering head and fee starts the timer; attacking voids and loses the head. Runs against a dev caravan-free
        /// path: the deliver call is the same one the dialog calls after its own caravan checks.</summary>
        public static string ProofYard()
        {
            Map map = Find.CurrentMap;
            RM_CompBorehulkDrill comp = SpawnHulk(map);
            try
            {
                RM_WornBit.FinishUnbit(comp);
                RM_WornBitGame g = RM_WornBitGame.Instance;
                int before = Find.TickManager.TicksGame;
                g.OnHeadHandedOver(g.fee);
                int timer = g.readyTick - before;
                string staged = g.stage.ToString();
                g.VoidOrder();
                return "YARD fee " + g.fee + " timer " + timer + " expected " + RM_WornBitGame.RefurbishTicks + " staged " + staged + " after " + g.stage + " quest " + (g.quest?.State.ToString() ?? "none") + " yard " + (g.yard == null ? "gone" : "there");
            }
            finally
            {
                Clean(comp);
            }
        }

        /// <summary>The order's refusal with everything present, then with each item absent in turn.</summary>
        public static string ProofRestoreGate()
        {
            Map map = Find.CurrentMap;
            RM_CompBorehulkDrill comp = SpawnHulk(map);
            var spawned = new List<Thing>();
            try
            {
                comp.SetState(RM_BorehulkDrillState.Unbitted);
                var rows = RM_WornBitDefOf.RM_BorehulkRestoration.ingredients;
                var pieces = new List<string>();
                foreach (ThingDefCountClass row in rows)
                {
                    comp.delivered[row.thingDef] = row.count;
                }
                pieces.Add("all:" + (RM_WornBit.RestorationRefusal(comp, null) ?? "null"));
                foreach (ThingDefCountClass row in rows)
                {
                    comp.delivered.Remove(row.thingDef);
                    pieces.Add(row.thingDef.defName + ":" + RM_WornBit.RestorationRefusal(comp, null));
                    comp.delivered[row.thingDef] = row.count;
                }
                return "GATE " + string.Join(" | ", pieces);
            }
            finally
            {
                spawned.ForEach(t => t.Destroy());
                Clean(comp);
            }
        }

        /// <summary>Kept: a plate cell and a sacred wall in the area mine out to 0, and the sacred one is recorded. Free: over the
        /// same two cells the self-bore picks plate only. Places its own cells next to the hulk.</summary>
        public static string ProofDig()
        {
            Map map = Find.CurrentMap;
            RM_CompBorehulkDrill comp = SpawnHulk(map);
            Pawn hulk = (Pawn)comp.parent;
            var placed = new List<Thing>();
            try
            {
                IntVec3[] cells = GenAdj.CardinalDirections.Select(d => hulk.Position + d * 2).Where(c => c.InBounds(map) && c.Standable(map)).Take(2).ToArray();
                if (cells.Length < 2)
                {
                    return "DIG refused: no room beside the hulk";
                }
                placed.Add(GenSpawn.Spawn(RM_WornBitDefOf.RM_CathedralDeckPlate, cells[0], map));
                placed.Add(GenSpawn.Spawn(ThingDef.Named("RM_SacredWall_Conduit"), cells[1], map));
                comp.SetState(RM_BorehulkDrillState.Restored);
                Thing bore = RM_DigFinder.SelfBoreTarget(hulk);
                bool plateOnly = bore != null && !RM_WornBit.IsSacred(bore);
                hulk.SetFaction(Faction.OfPlayer);
                comp.lastServiceTick = Find.TickManager.TicksGame;
                RM_Area_BorehulkDig area = RM_WornBit.DigArea(map);
                area[cells[0]] = true;
                area[cells[1]] = true;
                int warned = RM_DigFinder.SacredCellsInArea(map);
                int? standing0 = RM_MapComponent_BiomeAttitude.GetStanding(map);
                int mined = 0;
                Thing t;
                while (mined < 10 && (t = RM_DigFinder.KeptTarget(hulk)) != null)
                {
                    RM_DigFinder.MineOne(hulk, t);
                    mined++;
                }
                int left = cells.Count(c => RM_DigFinder.DiggableAt(c, map) != null);
                area[cells[0]] = false;
                area[cells[1]] = false;
                int? standing1 = RM_MapComponent_BiomeAttitude.GetStanding(map);
                return "DIG mined " + mined + " left " + left + " sacred " + comp.sacredCellsMined + " warned " + warned + " plateOnly " + plateOnly + " standingDelta " + ((standing1 ?? 0) - (standing0 ?? 0));
            }
            finally
            {
                placed.Where(t => !t.Destroyed).ToList().ForEach(t => t.Destroy());
                Clean(comp);
            }
        }

        /// <summary>Takes a branch and reports its reads. keep=true Keep, keep=false Free.</summary>
        public static string ProofBranch(bool keep)
        {
            Map map = Find.CurrentMap;
            RM_CompBorehulkDrill comp = SpawnHulk(map);
            RM_MapComponent_BiomeAttitude a = map.GetComponent<RM_MapComponent_BiomeAttitude>();
            float irr0 = a.ProofIrritation;
            Faction droids = Find.FactionManager.AllFactionsListForReading.FirstOrDefault(f => f.def.HasModExtension<RM_NeutralDroidsExtension>());
            int goodwill0 = droids == null ? 0 : Faction.OfPlayer.GoodwillWith(droids);
            try
            {
                comp.SetState(RM_BorehulkDrillState.Unbitted);
                comp.parent.TryGetComp<RM_CompBorehulkDrill>().choice = keep ? RM_WornBitChoice.Keep : RM_WornBitChoice.Free;
                RM_WornBit.FinishRestoration(comp);
                Pawn hulk = (Pawn)comp.parent;
                var options = RM_WornBit.Gizmos(comp).Select(g => g.GetType().Name).ToList();
                bool overseer = MechanitorUtility.EverControllable(hulk);
                int now = Find.TickManager.TicksGame;
                comp.lastServiceTick = now - RM_CompBorehulkDrill.MaintenanceIntervalTicks - 1;
                bool mayDig = comp.MayDigKept;
                bool hostile = hulk.HostileTo(Faction.OfPlayer);
                int goodwillDelta = droids == null ? 0 : Faction.OfPlayer.GoodwillWith(droids) - goodwill0;
                return "BRANCH goodwillDelta " + goodwillDelta + " droids " + (droids?.def.defName ?? "none") + " faction " + (hulk.Faction?.def.defName ?? "null") + " state " + comp.State + " colonyMech " + hulk.IsColonyMech + " controllable " + overseer
                    + " gizmos " + options.Count + " irritationDelta " + (a.ProofIrritation - irr0) + " mayDigAfter5d " + mayDig + " hostile " + hostile;
            }
            finally
            {
                Clean(comp);
            }
        }
    }
}
