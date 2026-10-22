using System.Collections.Generic;
using System.Linq;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.Webwork
{
    /// <summary>
    /// WEB_SIEGE_DESIGN_SPIDERS_BRING_SHADE. Deterministic reads/triggers for jawa/static_call on the CURRENT map, behind the
    /// `siege` chain of validation.py (design/RimMandrake/webwork_spider_siege_2026-10-22.md §8). Each takes ONE string
    /// (';'-separated parts: static_call splits '|' into parameters), sets what it needs for the call and restores it.
    /// Test pawns and doors are made here, never the player's colonists. ProofSpin and ProofSlick run real game ticks
    /// (TickManager.DoSingleTick) so the SPIDER does the work; nothing is placed for it.
    /// </summary>
    public static class RM_WebworkSiegeProof
    {
        private static Map Map => Find.CurrentMap;

        private static string[] Parts(string args) => (args ?? "").Split(new[] { ';', '|' });

        private static Lord NewestSiege(Map map)
        {
            return map.lordManager.lords.Where(l => l.LordJob is RM_LordJob_WebworkSiege && l.ownedPawns.Count > 0)
                .OrderByDescending(l => ((RM_LordJob_WebworkSiege)l.LordJob).siegeId).FirstOrDefault();
        }

        private static IntVec3 FreeCellNear(Map map, IntVec3 c, System.Predicate<IntVec3> extra = null)
        {
            return CellFinder.TryFindRandomCellNear(c, map, 12, x => x.Standable(map) && x.GetEdifice(map) == null
                && x.GetFirstPawn(map) == null && !RM_WebworkSiegeUtility.HasWebAt(map, x) && (extra == null || extra(x)), out IntVec3 r)
                ? r : IntVec3.Invalid;
        }

        private static Pawn TestColonist(Map map, IntVec3 near)
        {
            Pawn p = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
            IntVec3 at = FreeCellNear(map, near);
            if (!at.IsValid)
            {
                Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.Discard);
                return null;
            }
            GenSpawn.Spawn(p, at, map);
            return p;
        }

        /// <summary>args "hook;enabled" (bools, default false;true). "ELIG reason R | measurable B | sampled N | shaded M |
        /// canFire B".</summary>
        public static string ProofEligibility(string args)
        {
            Map map = Map;
            if (map == null) return "REFUSED: no current map";
            string[] a = Parts(args);
            bool hook = a.Length > 0 && a[0].Trim().ToLowerInvariant() == "true";
            bool enabled = !(a.Length > 1 && a[1].Trim().ToLowerInvariant() == "false");
            bool wasHook = RM_WebworkSettings.siegeTestIgnoreMapChecks, wasOn = RM_WebworkSettings.siegeEnabled;
            try
            {
                RM_WebworkSettings.siegeTestIgnoreMapChecks = hook;
                RM_WebworkSettings.siegeEnabled = enabled;
                SiegeEligibility e = RM_WebworkSiegeUtility.EligibilityFor(map, out int sampled, out int shaded, out bool measurable);
                IncidentParms parms = StorytellerUtility.DefaultParmsNow(IncidentCategoryDefOf.ThreatBig, map);
                parms.forced = true;
                bool can = RM_WebworkSiegeDefOf.RM_WebworkSiege.Worker.CanFireNow(parms);
                return "ELIG reason " + e + " | measurable " + measurable + " | sampled " + sampled + " | shaded " + shaded
                    + " | canFire " + can + " | why " + RM_WebworkSiegeKernel.Describe(e).Replace(' ', '_');
            }
            finally
            {
                RM_WebworkSettings.siegeTestIgnoreMapChecks = wasHook;
                RM_WebworkSettings.siegeEnabled = wasOn;
            }
        }

        /// <summary>args "points" (default 800). Fires the real worker (forced) with the test hook on. "FIRE ok B | spiders N |
        /// insects B | dormant D | lords L | siegeId I".</summary>
        public static string ProofFire(string args)
        {
            Map map = Map;
            if (map == null) return "REFUSED: no current map";
            float points = float.TryParse(Parts(args)[0], out float pt) ? pt : 800f;
            bool wasHook = RM_WebworkSettings.siegeTestIgnoreMapChecks;
            try
            {
                RM_WebworkSettings.siegeTestIgnoreMapChecks = true;
                int before = map.lordManager.lords.Count(l => l.LordJob is RM_LordJob_WebworkSiege);
                IncidentParms parms = StorytellerUtility.DefaultParmsNow(IncidentCategoryDefOf.ThreatBig, map);
                parms.forced = true;
                parms.points = points;
                bool ok = RM_WebworkSiegeDefOf.RM_WebworkSiege.Worker.TryExecute(parms);
                Lord lord = NewestSiege(map);
                int after = map.lordManager.lords.Count(l => l.LordJob is RM_LordJob_WebworkSiege);
                if (lord == null) return "FIRE ok " + ok + " | spiders 0 | lords " + before + "->" + after;
                List<Pawn> ps = lord.ownedPawns;
                int dormant = ps.Count(p => p.TryGetComp<CompCanBeDormant>() is CompCanBeDormant d && !d.Awake);
                return "FIRE ok " + ok + " | spiders " + ps.Count + " | allOllathrix " + ps.All(p => p.def.defName == "RM_Ollathrix")
                    + " | insects " + ps.All(p => p.Faction == Faction.OfInsects) + " | dormant " + dormant + " | lords " + before + "->" + after
                    + " | siegeId " + ((RM_LordJob_WebworkSiege)lord.LordJob).siegeId;
            }
            finally
            {
                RM_WebworkSettings.siegeTestIgnoreMapChecks = wasHook;
            }
        }

        /// <summary>args "maxTicks" (default 2500). A siege spider is given a spin job on the cell the production finder picks;
        /// real ticks run until the web stands or the budget ends. "SPIN cell (x,z) | exposed B | ticks T | web B | tagged B |
        /// spun A->B".</summary>
        public static string ProofSpin(string args)
        {
            Map map = Map;
            if (map == null) return "REFUSED: no current map";
            int max = int.TryParse(Parts(args)[0], out int m) ? m : 2500;
            Lord lord = NewestSiege(map);
            if (lord == null) return "SPIN noSiege";
            var siege = (RM_LordJob_WebworkSiege)lord.LordJob;
            Pawn spider = lord.ownedPawns.FirstOrDefault(p => p.Spawned && !p.Downed);
            if (spider == null) return "SPIN noSpider";
            if (!RM_WebworkSiegeUtility.TryFindSpinCell(spider, siege, out IntVec3 cell)) return "SPIN noCell | spun " + siege.spun;
            int spun0 = siege.spun;
            spider.jobs.StartJob(JobMaker.MakeJob(RM_WebworkSiegeDefOf.RM_WebSiegeSpin, cell), JobCondition.InterruptForced);
            int t = 0;
            Thing web = null;
            for (; t < max && web == null; t++)
            {
                Find.TickManager.DoSingleTick();
                web = cell.GetFirstThing(map, RM_WebworkSiegeDefOf.RM_Webwork_SiegeWeb);
            }
            bool tagged = web?.TryGetComp<RM_CompSiegeSilk>()?.siegeId == siege.siegeId;
            return "SPIN cell (" + cell.x + "," + cell.z + ") | exposed " + RM_Hediff_SunScald.ExposedAt(map, cell) + " | ticks " + t
                + " | web " + (web != null) + " | tagged " + tagged + " | spun " + spun0 + "->" + siege.spun;
        }

        /// <summary>A test colonist stands on a fresh siege web for 180 ticks; an ollathrix on another for the same.
        /// "SLICK before 0 | after S | ollathrixAfter O".</summary>
        public static string ProofSlick(string args)
        {
            Map map = Map;
            if (map == null) return "REFUSED: no current map";
            Pawn p = TestColonist(map, map.Center);
            if (p == null) return "SLICK noCell";
            HediffDef slick = DefDatabase<HediffDef>.GetNamedSilentFail("RM_Webwork_Slick");
            Pawn spider = PawnGenerator.GeneratePawn(RM_WebworkSiegeDefOf.RM_Ollathrix, null);
            IntVec3 sc = FreeCellNear(map, p.Position);
            var made = new List<Thing>();
            try
            {
                made.Add(GenSpawn.Spawn(ThingMaker.MakeThing(RM_WebworkSiegeDefOf.RM_Webwork_SiegeWeb), p.Position, map));
                if (sc.IsValid)
                {
                    GenSpawn.Spawn(spider, sc, map);
                    made.Add(GenSpawn.Spawn(ThingMaker.MakeThing(RM_WebworkSiegeDefOf.RM_Webwork_SiegeWeb), sc, map));
                }
                float before = p.health.hediffSet.GetFirstHediffOfDef(slick)?.Severity ?? 0f;
                for (int i = 0; i < 180; i++)
                {
                    p.pather.StopDead();
                    if (spider.Spawned) spider.pather.StopDead();
                    Find.TickManager.DoSingleTick();
                }
                float after = p.health.hediffSet.GetFirstHediffOfDef(slick)?.Severity ?? 0f;
                float oll = spider.Spawned ? spider.health.hediffSet.GetFirstHediffOfDef(slick)?.Severity ?? 0f : -1f;
                return "SLICK before " + before.ToString("0.000") + " | after " + after.ToString("0.000") + " | ollathrixAfter " + oll.ToString("0.000");
            }
            finally
            {
                foreach (Thing t in made) if (!t.Destroyed) t.Destroy();
                if (spider.Spawned) spider.Destroy();
                if (p.Spawned) p.Destroy();
            }
        }

        /// <summary>args "cuts" (default 30). One fresh siege id: that many webs cut (DestroyMode.Deconstruct, what vanilla
        /// Deconstruct ends in), then one more broken by force. "CUT cap C | perCut P | cuts N | total T | forceBroken F".</summary>
        public static string ProofCut(string args)
        {
            Map map = Map;
            if (map == null) return "REFUSED: no current map";
            int cuts = int.TryParse(Parts(args)[0], out int c) ? c : 30;
            var mc = map.GetComponent<RM_MapComponent_WebworkSiege>();
            if (mc == null) return "CUT noComponent";
            int id = mc.NewSiegeId();
            int total = 0;
            for (int i = 0; i <= cuts; i++)
            {
                IntVec3 at = FreeCellNear(map, map.Center);
                if (!at.IsValid) return "CUT noCell after " + i;
                Thing web = ThingMaker.MakeThing(RM_WebworkSiegeDefOf.RM_Webwork_SiegeWeb);
                web.TryGetComp<RM_CompSiegeSilk>().SetSiege(id);
                GenSpawn.Spawn(web, at, map);
                bool force = i == cuts;
                web.Destroy(force ? DestroyMode.KillFinalize : DestroyMode.Deconstruct);
                if (force)
                {
                    int forced = RM_CompSiegeSilk.lastYieldSpawned;
                    return "CUT cap " + RM_WebworkSettings.siegeSilkYieldCap + " | perCut " + RM_WebworkSiegeKernel.YieldPerCut + " | cuts " + cuts
                        + " | total " + total + " | ledger " + mc.YieldedBy(id) + " | forceBroken " + forced;
                }
                total += RM_CompSiegeSilk.lastYieldSpawned;
            }
            return "CUT unreachable";
        }

        /// <summary>Two test doors near the centre, one wrapped. "DOOR wrappedOpens B | controlOpens B | afterCutOpens B |
        /// controlAfter B".</summary>
        public static string ProofDoor(string args)
        {
            Map map = Map;
            if (map == null) return "REFUSED: no current map";
            ThingDef doorDef = DefDatabase<ThingDef>.GetNamedSilentFail("Door");
            Pawn p = TestColonist(map, map.Center);
            if (doorDef == null || p == null) return "DOOR noDoorDefOrCell";
            var made = new List<Thing>();
            try
            {
                Building_Door Make()
                {
                    IntVec3 at = FreeCellNear(map, p.Position);
                    if (!at.IsValid) return null;
                    var d = (Building_Door)ThingMaker.MakeThing(doorDef, ThingDefOf.WoodLog);
                    d.SetFaction(Faction.OfPlayer);
                    GenSpawn.Spawn(d, at, map);
                    made.Add(d);
                    return d;
                }
                Building_Door wrapped = Make(), control = Make();
                if (wrapped == null || control == null) return "DOOR noCell";
                RM_Building_SiegeDoorWrap wrap = RM_WebworkSiegeUtility.WrapDoor(wrapped);
                bool wOpens = wrapped.PawnCanOpen(p), cOpens = control.PawnCanOpen(p);
                wrap?.Destroy(DestroyMode.Deconstruct);
                return "DOOR wrapSpawned " + (wrap != null) + " | wrappedOpens " + wOpens + " | controlOpens " + cOpens
                    + " | afterCutOpens " + wrapped.PawnCanOpen(p) + " | controlAfter " + control.PawnCanOpen(p);
            }
            finally
            {
                foreach (Thing t in made) if (!t.Destroyed) t.Destroy();
                if (p.Spawned) p.Destroy();
            }
        }

        /// <summary>args "rescue" | "deadline". A generated test colonist is downed and cocooned; rescue opens it, deadline
        /// ages the clock past siegeCocoonDeathHours (vanilla's death letter for the test pawn still shows). The test pawn, its
        /// corpse and the cocoon are always removed. "COCOON made B | inside B | MODE ... ".</summary>
        public static string ProofCocoon(string args)
        {
            Map map = Map;
            if (map == null) return "REFUSED: no current map";
            string mode = Parts(args)[0].Trim().ToLowerInvariant();
            Pawn p = TestColonist(map, map.Center);
            if (p == null) return "COCOON noCell";
            RM_Building_SiegeCocoon cocoon = null;
            try
            {
                HealthUtility.DamageUntilDowned(p, allowBleedingWounds: false);
                if (!p.Downed) return "COCOON notDowned";
                cocoon = RM_WebworkSiegeUtility.Cocoon(p);
                string head = "COCOON made " + (cocoon != null) + " | inside " + (cocoon?.Inside == p) + " | spawned " + p.Spawned;
                if (cocoon == null) return head;
                if (mode == "deadline")
                {
                    cocoon.Debug_AgeBy(RM_WebworkSiegeKernel.CocoonDeathTicks(RM_WebworkSettings.siegeCocoonDeathHours) - 1);
                    cocoon.CheckClock();
                    bool earlyDead = p.Dead;
                    cocoon.Debug_AgeBy(2);
                    cocoon.CheckClock();
                    return head + " | DEADLINE deadBefore " + earlyDead + " | deadAfter " + p.Dead
                        + " | cause " + (p.health.hediffSet.GetFirstHediffOfDef(RM_WebworkSiegeDefOf.RM_Webwork_SilkSuffocation) != null);
                }
                cocoon.Open();
                return head + " | RESCUE out " + p.Spawned + " | alive " + !p.Dead + " | cocoonGone " + cocoon.Destroyed;
            }
            finally
            {
                // The test colonist never stays in the save (deadline mode: vanilla still sends its death letter).
                if (cocoon != null && !cocoon.Destroyed) cocoon.Destroy();
                if (p.Corpse != null && !p.Corpse.Destroyed) p.Corpse.Destroy();
                if (p.Spawned) p.Destroy();
            }
        }

        /// <summary>Kills half of the newest siege (rounded up) and lets the lord check its triggers. "BREAK killed K of N |
        /// toil T | letter B".</summary>
        public static string ProofBreak(string args)
        {
            Map map = Map;
            if (map == null) return "REFUSED: no current map";
            Lord lord = NewestSiege(map);
            if (lord == null) return "BREAK noSiege";
            var siege = (RM_LordJob_WebworkSiege)lord.LordJob;
            List<Pawn> ps = lord.ownedPawns.ToList();
            int k = (ps.Count + 1) / 2;
            for (int i = 0; i < k; i++) ps[i].Kill(null);
            for (int i = 0; i < 300; i++) Find.TickManager.DoSingleTick();
            return "BREAK killed " + k + " of " + ps.Count + " | toil " + (lord.CurLordToil?.GetType().Name ?? "none")
                + " | letter " + siege.breakLetterSent;
        }
    }
}
