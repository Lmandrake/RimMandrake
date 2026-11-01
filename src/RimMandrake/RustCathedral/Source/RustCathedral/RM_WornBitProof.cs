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
        private const string NothingToAsk = "nothing to ask";
        private static readonly string[] WatchedStats = { "MoveSpeed", "WorkSpeedGlobal", "MiningSpeed", "ConstructionSpeed", "GeneralLaborSpeed",
            "MeleeHitChance", "ShootingAccuracyPawn", "PsychicSensitivity", "MentalBreakThreshold", "SocialImpact", "ArmorRating_Sharp" };
        private static RM_CompBorehulkDrill timedComp;
        private static readonly List<Thing> timedCells = new List<Thing>();
        private static bool timedKeep;

        private static Pawn Colonist(Map map)
        {
            return map.mapPawns.FreeColonistsSpawned.FirstOrDefault(p => p.skills?.GetSkill(SkillDefOf.Crafting)?.TotallyDisabled == false);
        }

        /// <summary>Steers the real irritation until the raw band reads the target; the composite also carries standing, so no
        /// fixed irritation names a band. Returns the band reached.</summary>
        private static int RaiseToBand(RM_MapComponent_BiomeAttitude a, Map map, int target)
        {
            for (float irr = 0f; irr <= 120f; irr += 1f)
            {
                a.ProofBandAt(irr);
                if (RM_MapComponent_BiomeAttitude.GetRawBand(map) >= target)
                {
                    break;
                }
            }
            return RM_MapComponent_BiomeAttitude.GetRawBand(map);
        }

        /// <summary>Solid cells of a def in standable cells close to the hulk, nearest first.</summary>
        private static List<Thing> PlaceNear(Pawn hulk, ThingDef def, int count)
        {
            var placed = new List<Thing>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(hulk.Position, 6f, useCenter: false))
            {
                if (placed.Count >= count)
                {
                    break;
                }
                if (c.InBounds(hulk.Map) && c.Standable(hulk.Map) && c.DistanceTo(hulk.Position) >= 2f && c.GetFirstPawn(hulk.Map) == null)
                {
                    placed.Add(GenSpawn.Spawn(def, c, hulk.Map));
                }
            }
            return placed;
        }

        private static void Take(RM_CompBorehulkDrill comp, RM_WornBitChoice choice)
        {
            comp.SetState(RM_BorehulkDrillState.Unbitted);
            comp.choice = choice;
            RM_WornBit.FinishRestoration(comp);
        }

        /// <summary>Both drill heads and the one restoration def, read from the databases: the short def type get_defs cannot take.</summary>
        public static string ProofDefs()
        {
            return "DEFS restorationDefs " + DefDatabase<RM_BorehulkRestorationDef>.AllDefsListForReading.Count
                + " wornMass " + RM_WornBitDefOf.RM_WornDrillHead.GetStatValueAbstract(StatDefOf.Mass)
                + " refurbishedMass " + RM_WornBitDefOf.RM_RefurbishedDrillHead.GetStatValueAbstract(StatDefOf.Mass);
        }

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
                int band = RaiseToBand(map.GetComponent<RM_MapComponent_BiomeAttitude>(), map, 2);
                for (int i = 0; i < 100; i++) { RM_WornBit.UnbitTick(comp, 2, 1f); }
                float stopped = comp.unbitProgress;
                map.GetComponent<RM_MapComponent_BiomeAttitude>().ProofBandAt(0f);
                int calm = RM_MapComponent_BiomeAttitude.GetRawBand(map);
                while (comp.State == RM_BorehulkDrillState.Worn) { RM_WornBit.UnbitTick(comp, 2, 2f); }
                int heads = map.listerThings.ThingsOfDef(RM_WornBitDefOf.RM_WornDrillHead).Count;
                RM_WornBitGame g = RM_WornBitGame.Instance;
                string factionName = g.yard?.Faction?.def.defName ?? "none";
                int quests = Find.QuestManager.QuestsListForReading.Count(q => q.root == RM_WornBitDefOf.RM_WornBitRefurbishment && q.State == QuestState.Ongoing);
                int yards = Find.WorldObjects.AllWorldObjects.Count(o => o.def == RM_WornBitDefOf.RM_RefurbishYard);
                bool yardCarries = g.yard?.Faction?.def.HasModExtension<RM_DrillRefurbisherExtension>() == true;
                bool pirateCarries = DefDatabase<FactionDef>.GetNamedSilentFail("Pirate")?.HasModExtension<RM_DrillRefurbisherExtension>() == true;
                bool campaign = DefDatabase<FactionDef>.GetNamedSilentFail("RUT_Jawa_Junkers") != null;
                return "STAGE1 lone " + lone + " two " + two + " band " + band + " stopped " + stopped + " calm " + calm + " state " + comp.State + " heads " + heads
                    + " quests " + quests + " yards " + yards + " yardfaction " + factionName + " yardCarries " + yardCarries
                    + " pirateCarries " + pirateCarries + " campaign " + campaign + " stage " + g.stage;
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
                return "YARD fee " + g.fee + " timer " + timer + " days " + RM_RustCathedralSettings.wornBitRefurbishDays + " staged " + staged + " after " + g.stage + " quest " + (g.quest?.State.ToString() ?? "none") + " yard " + (g.yard == null ? "gone" : "there");
            }
            finally
            {
                Clean(comp);
            }
        }

        private static string RestoreOffered(RM_CompBorehulkDrill comp, Pawn colonist)
        {
            FloatMenuOption o = comp.CompFloatMenuOptions(colonist).FirstOrDefault(x => x.Label.StartsWith("Restore the borehulk"));
            return o == null ? "absent" : o.Disabled ? "refused" : "offered";
        }

        /// <summary>The order on the borehulk with everything present, then with each item absent in turn. "GATE all:null order:offered |
        /// defName:refusal order:refused named:True | ..."</summary>
        public static string ProofRestoreGate()
        {
            Map map = Find.CurrentMap;
            RM_CompBorehulkDrill comp = SpawnHulk(map);
            Pawn colonist = Colonist(map);
            if (colonist == null)
            {
                Clean(comp);
                return "GATE refused: no colonist who can craft on the map";
            }
            SkillRecord crafting = colonist.skills.GetSkill(SkillDefOf.Crafting);
            int level = crafting.Level;
            try
            {
                crafting.Level = RM_WornBitDefOf.RM_BorehulkRestoration.minCrafting;
                comp.SetState(RM_BorehulkDrillState.Unbitted);
                RM_WornBitGame.Instance.stage = RM_WornBitStage.Collected;
                var rows = RM_WornBitDefOf.RM_BorehulkRestoration.ingredients;
                foreach (ThingDefCountClass row in rows)
                {
                    comp.delivered[row.thingDef] = row.count;
                }
                var pieces = new List<string> { "all:" + (RM_WornBit.RestorationRefusal(comp, colonist) ?? "null") + " order:" + RestoreOffered(comp, colonist) };
                foreach (ThingDefCountClass row in rows)
                {
                    comp.delivered.Remove(row.thingDef);
                    string refusal = RM_WornBit.RestorationRefusal(comp, colonist) ?? "null";
                    pieces.Add(row.thingDef.defName + ":" + refusal + " order:" + RestoreOffered(comp, colonist) + " named:" + refusal.Contains(row.thingDef.label));
                    comp.delivered[row.thingDef] = row.count;
                }
                return "GATE " + string.Join(" | ", pieces);
            }
            finally
            {
                crafting.Level = level;
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

        /// <summary>Takes a branch and reports its reads. keep=true Keep, keep=false Free. The hum starts high enough that the Free
        /// branch's fall is not held at 0, so the delta read is the whole delta.</summary>
        public static string ProofBranch(bool keep)
        {
            Map map = Find.CurrentMap;
            RM_CompBorehulkDrill comp = SpawnHulk(map);
            RM_MapComponent_BiomeAttitude a = map.GetComponent<RM_MapComponent_BiomeAttitude>();
            a.ProofBandAt(60f);
            float irr0 = a.ProofIrritation;
            Faction droids = Find.FactionManager.AllFactionsListForReading.FirstOrDefault(f => f.def.HasModExtension<RM_NeutralDroidsExtension>());
            int goodwill0 = droids == null ? 0 : Faction.OfPlayer.GoodwillWith(droids);
            Pawn colonist = Colonist(map);
            try
            {
                Take(comp, keep ? RM_WornBitChoice.Keep : RM_WornBitChoice.Free);
                float irritationDelta = a.ProofIrritation - irr0;
                Pawn hulk = (Pawn)comp.parent;
                var gizmos = RM_WornBit.Gizmos(comp).Select(g => g.GetType().Name).ToList();
                int floats = colonist == null ? -1 : comp.CompFloatMenuOptions(colonist).Count();
                bool overseer = MechanitorUtility.EverControllable(hulk);
                int now = Find.TickManager.TicksGame;
                comp.lastServiceTick = now - RM_CompBorehulkDrill.MaintenanceIntervalTicks - 1;
                bool mayDig = comp.MayDigKept;
                bool hostile = hulk.HostileTo(Faction.OfPlayer);
                int goodwillDelta = droids == null ? 0 : Faction.OfPlayer.GoodwillWith(droids) - goodwill0;
                return "BRANCH goodwillDelta " + goodwillDelta + " droids " + (droids?.def.defName ?? "none") + " faction " + (hulk.Faction?.def.defName ?? "null") + " state " + comp.State + " colonyMech " + hulk.IsColonyMech + " controllable " + overseer
                    + " gizmos " + gizmos.Count + " floats " + floats + " draftable " + (hulk.drafter != null) + " irritationDelta " + irritationDelta + " mayDigAfter5d " + mayDig + " hostile " + hostile;
            }
            finally
            {
                Clean(comp);
            }
        }

        private static string Snapshot(Map map)
        {
            var parts = new List<string>();
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned.OrderBy(x => x.thingIDNumber))
            {
                parts.Add(p.ThingID + ":" + string.Join(",", p.health.hediffSet.hediffs.Select(h => h.def.defName).OrderBy(n => n)));
                foreach (string name in WatchedStats)
                {
                    StatDef stat = DefDatabase<StatDef>.GetNamedSilentFail(name);
                    if (stat != null)
                    {
                        parts.Add(name + "=" + p.GetStatValue(stat, applyPostProcess: true, cacheStaleAfterTicks: -1).ToString("0.0000"));
                    }
                }
            }
            return string.Join(";", parts);
        }

        /// <summary>Every stage's state change in turn, colonists' hediffs and watched stats compared before and after each.
        /// The job drivers' own toils have no hook here: wornbit_problems greps their source for the same thing.</summary>
        public static string ProofNoBuff()
        {
            Map map = Find.CurrentMap;
            int colonists = map.mapPawns.FreeColonistsSpawned.Count;
            string before = Snapshot(map);
            int changed = 0;
            int stages = 0;
            void After()
            {
                stages++;
                if (Snapshot(map) != before)
                {
                    changed++;
                }
            }
            foreach (RM_WornBitChoice choice in new[] { RM_WornBitChoice.Keep, RM_WornBitChoice.Free })
            {
                RM_CompBorehulkDrill comp = SpawnHulk(map);
                try
                {
                    RM_WornBit.FinishUnbit(comp);
                    After();
                    RM_WornBitGame g = RM_WornBitGame.Instance;
                    g.OnHeadHandedOver(g.fee);
                    After();
                    Take(comp, choice);
                    After();
                }
                finally
                {
                    Clean(comp);
                }
            }
            return "NOBUFF colonists " + colonists + " stages " + stages + " changed " + changed;
        }

        /// <summary>One 1 or 0 per effect the toggles own, each read from the shipped decision on a fresh hulk.</summary>
        private static string Observe(Map map)
        {
            Pawn colonist = Colonist(map);
            RM_MapComponent_BiomeAttitude a = map.GetComponent<RM_MapComponent_BiomeAttitude>();
            int unbit, dig, stops, service, politics, landing, freeBore, favour;
            RM_CompBorehulkDrill comp = SpawnHulk(map);
            try
            {
                unbit = comp.CompFloatMenuOptions(colonist).Count() > 0 ? 1 : 0;
            }
            finally
            {
                Clean(comp);
            }
            comp = SpawnHulk(map);
            var cells = new List<Thing>();
            try
            {
                Pawn hulk = (Pawn)comp.parent;
                a.ProofBandAt(60f);
                float irr = a.ProofIrritation;
                Take(comp, RM_WornBitChoice.Keep);
                politics = a.ProofIrritation != irr ? 1 : 0;
                cells = PlaceNear(hulk, RM_WornBitDefOf.RM_CathedralDeckPlate, 1);
                RM_Area_BorehulkDig area = RM_WornBit.DigArea(map);
                area[cells[0].Position] = true;
                dig = RM_JobGiver_BorehulkWork.WorkTarget(hulk) != null ? 1 : 0;
                area[cells[0].Position] = false;
                service = comp.CompFloatMenuOptions(colonist).Count() > 0 ? 1 : 0;
                comp.lastServiceTick = Find.TickManager.TicksGame - RM_CompBorehulkDrill.MaintenanceIntervalTicks - 1;
                stops = comp.MayDigKept ? 0 : 1;
                RM_WornBitGame.Instance.ProofForgetLanding(map);
                irr = a.ProofIrritation;
                RM_WornBitGame.Instance.NoticeLandings();
                landing = a.ProofIrritation != irr ? 1 : 0;
            }
            finally
            {
                cells.Where(t => !t.Destroyed).ToList().ForEach(t => t.Destroy());
                Clean(comp);
            }
            comp = SpawnHulk(map);
            try
            {
                Pawn hulk = (Pawn)comp.parent;
                Take(comp, RM_WornBitChoice.Free);
                cells = PlaceNear(hulk, RM_WornBitDefOf.RM_CathedralDeckPlate, 1);
                comp.lastSelfBoreTick = Find.TickManager.TicksGame - GenDate.TicksPerYear;
                freeBore = RM_JobGiver_BorehulkWork.WorkTarget(hulk) != null ? 1 : 0;
                favour = RM_WornBitGame.Instance.FavourRefusal(map) != NothingToAsk ? 1 : 0;
            }
            finally
            {
                cells.Where(t => !t.Destroyed).ToList().ForEach(t => t.Destroy());
                Clean(comp);
            }
            return "unbit " + unbit + " dig " + dig + " stops " + stops + " service " + service + " politics " + politics + " landing " + landing + " freeBore " + freeBore + " favour " + favour;
        }

        /// <summary>The effects with one bool setting off ("none" for the baseline), the setting restored after.</summary>
        public static string ProofToggle(string field)
        {
            Map map = Find.CurrentMap;
            if (Colonist(map) == null)
            {
                return "TOGGLE refused: no colonist who can craft on the map";
            }
            System.Reflection.FieldInfo info = field == "none" ? null : typeof(RM_RustCathedralSettings).GetField(field);
            if (field != "none" && info == null)
            {
                return "TOGGLE refused: no field " + field;
            }
            object prior = info?.GetValue(null);
            try
            {
                info?.SetValue(null, false);
                return "TOGGLE " + Observe(map);
            }
            finally
            {
                info?.SetValue(null, prior);
            }
        }

        /// <summary>Starts a restored hulk on real game time: Keep with three plate cells in its dig area, Free with three plate cells and
        /// one sacred wall beside it. The caller advances the clock, then calls ProofTimedEnd.</summary>
        public static string ProofTimedBegin(bool keep)
        {
            Map map = Find.CurrentMap;
            timedKeep = keep;
            timedComp = SpawnHulk(map);
            Pawn hulk = (Pawn)timedComp.parent;
            Take(timedComp, keep ? RM_WornBitChoice.Keep : RM_WornBitChoice.Free);
            timedCells.Clear();
            timedCells.AddRange(PlaceNear(hulk, RM_WornBitDefOf.RM_CathedralDeckPlate, 3));
            if (keep)
            {
                RM_Area_BorehulkDig area = RM_WornBit.DigArea(map);
                timedCells.ForEach(t => area[t.Position] = true);
            }
            else
            {
                timedCells.AddRange(PlaceNear(hulk, ThingDef.Named("RM_SacredWall_Conduit"), 1));
            }
            return "TIMED begun cells " + timedCells.Count;
        }

        public static string ProofTimedEnd()
        {
            Map map = Find.CurrentMap;
            RM_CompBorehulkDrill comp = timedComp;
            if (comp == null)
            {
                return "TIMED refused: ProofTimedBegin was not called";
            }
            try
            {
                int plateLeft = timedCells.Count(t => !t.Destroyed && !RM_WornBit.IsSacred(t));
                int sacredLeft = timedCells.Count(t => !t.Destroyed && RM_WornBit.IsSacred(t));
                string job = ((Pawn)comp.parent).CurJobDef?.defName ?? "none";
                return "TIMED keep " + timedKeep + " mined " + comp.cellsMined + " sacredMined " + comp.sacredCellsMined + " plateLeft " + plateLeft + " sacredLeft " + sacredLeft + " job " + job;
            }
            finally
            {
                if (timedKeep)
                {
                    RM_Area_BorehulkDig area = RM_WornBit.DigArea(map);
                    timedCells.ForEach(t => area[t.Position] = false);
                }
                timedCells.Where(t => !t.Destroyed).ToList().ForEach(t => t.Destroy());
                timedCells.Clear();
                Clean(comp);
                timedComp = null;
            }
        }
    }
}
