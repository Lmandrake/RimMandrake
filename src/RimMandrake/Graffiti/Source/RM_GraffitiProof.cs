using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace RimMandrake.Graffiti
{
    /// <summary>
    /// GRAFFITI_V1_LIVE_PROOF_1. Deterministic set-ups and reads for jawa/static_call on the CURRENT map (a quicktest map), one
    /// clause phase per method, each answering one line "HEAD key value | key value ..." (or "REFUSED why"). Driven by
    /// src/RimMandrake/Graffiti/graffiti_v1_live_proof.py, which steps the clock between phases. jawa/static_call splits its args
    /// on '|' into parameters, so every method takes one string and splits it on ';'.
    ///
    /// Every set-up method rebuilds the same 20x12 site at the map centre: Concrete floor, unroofed, unfogged, home area, an
    /// 18-cell Steel wall along z = oz+6 with marks painted on its south face (z = oz+5) and raiders spawned on its north side.
    /// A2 alone also closes and roofs the south half into a room (BuildInterior) with one raider inside, so exterior is tested.
    /// The site is cleared of every non-colonist thing first, so a clause never reads another clause's marks.
    /// </summary>
    public static class RM_GraffitiProof
    {
        private const int W = 20, H = 12, WallRow = 6;
        private static IntVec3 origin = IntVec3.Invalid;
        private static Pawn colonist, spreePawn;
        private static int spreeTick = -1, raidTick = -1;
        private static Lord raidLord;
        private static Faction raidFaction;
        private static List<Pawn> raiders = new List<Pawn>();
        private static Filth_Mark ownMark, devotionalMark, controlMark;
        private static List<IntVec3> designated = new List<IntVec3>();
        private static List<ThingDef> chosen = new List<ThingDef>();
        private static List<ThingDef> designatedDefs = new List<ThingDef>();

        private static IntVec3 Cell(int dx, int dz) => new IntVec3(origin.x + dx, 0, origin.z + dz);
        private static IntVec3 Face(int dx) => Cell(dx, WallRow - 1);

        // ---------- site ----------

        private static string BuildSite(Map map)
        {
            colonist = map.mapPawns.FreeColonistsSpawned
                .Where(p => !p.Downed && !p.Dead && p.Ideo != null && !p.InMentalState)
                .OrderBy(p => p.WorkTypeIsDisabled(WorkTypeDefOf.Cleaning) ? 1 : 0)
                .ThenBy(p => ArtDisabled(p) ? 1 : 0)
                .FirstOrDefault();
            if (colonist == null)
            {
                return "REFUSED no free spawned colonist with an ideoligion on the current map";
            }
            origin = new IntVec3(map.Size.x / 2 - W / 2, 0, map.Size.z / 2 - H / 2);
            CellRect rect = new CellRect(origin.x, origin.z, W, H);
            foreach (IntVec3 c in rect)
            {
                if (!c.InBounds(map)) return "REFUSED site out of bounds at " + c;
                foreach (Thing t in c.GetThingList(map).ToList())
                {
                    if (t is Pawn p && p.Faction == Faction.OfPlayer) continue;
                    if (!t.Destroyed) t.Destroy(DestroyMode.Vanish);
                }
                map.terrainGrid.SetTerrain(c, TerrainDefOf.Concrete);
                map.roofGrid.SetRoof(c, null);
                map.fogGrid.Unfog(c);
                map.areaManager.Home[c] = true;
            }
            for (int dx = 1; dx < W - 1; dx++)
            {
                // a colonist standing where the wall goes is moved off it first (GenSpawn would put a building on a pawn)
                foreach (Pawn p in Cell(dx, WallRow).GetThingList(map).OfType<Pawn>().ToList()) Place(p, Cell(dx, 1));
                Thing wall = ThingMaker.MakeThing(ThingDefOf.Wall, ThingDefOf.Steel);
                wall.SetFaction(Faction.OfPlayer);
                GenSpawn.Spawn(wall, Cell(dx, WallRow), map);
            }
            Place(colonist, Cell(W / 2, 2));
            return null;
        }

        private static bool ArtDisabled(Pawn p)
        {
            WorkTypeDef art = DefDatabase<WorkTypeDef>.GetNamedSilentFail("Art");
            return art == null || p.WorkTypeIsDisabled(art);
        }

        private static void Place(Pawn p, IntVec3 c)
        {
            p.jobs?.StopAll();
            p.Position = c;
            p.Notify_Teleported(true, true);
        }

        private static string Setup(out Map map)
        {
            map = Find.CurrentMap;
            if (map == null) return "REFUSED no current map";
            return BuildSite(map);
        }

        private static Faction Enemy()
        {
            return Find.FactionManager.RandomEnemyFaction(allowHidden: false, allowDefeated: false, allowNonHumanlike: false);
        }

        private static Pawn EnemyPawn(Faction f)
        {
            PawnKindDef kind = f.def.basicMemberKind ?? f.RandomPawnKind();
            return PawnGenerator.GeneratePawn(kind, f);
        }

        private static void Retire(Pawn p)
        {
            if (p == null) return;
            p.GetLord()?.Notify_PawnLost(p, PawnLostCondition.ExitedMap);
            if (p.Spawned) p.DeSpawn();
            if (!p.IsWorldPawn()) Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.KeepForever);
        }

        private static IEnumerable<Filth_Mark> Marks(Map map)
        {
            return map.listerThings.ThingsInGroup(ThingRequestGroup.Filth).OfType<Filth_Mark>();
        }

        private static Filth_Mark MarkAt(Map map, IntVec3 c)
        {
            return c.GetThingList(map).OfType<Filth_Mark>().FirstOrDefault();
        }

        private static string B(bool b) => b ? "True" : "False";

        // ---------- A8: the probe is loaded ----------

        /// <summary>"LOADED graffiti True | ideology True | thought True | raidHook True" - read beside Player.log.</summary>
        public static string Loaded(string args)
        {
            bool thought = DefDatabase<ThoughtDef>.GetNamedSilentFail("RM_Graffiti_ViewedHostileMark") != null;
            bool hook = Harmony.GetPatchInfo(AccessTools.Method(typeof(Lord), nameof(Lord.GotoToil), new[] { typeof(LordToil) }))?
                .Postfixes.Any(p => p.owner == "mandrake.rm.graffiti.raidexittagger") ?? false;
            return "LOADED graffiti True | ideology " + B(ModsConfig.IdeologyActive) + " | thought " + B(thought) + " | raidHook " + B(hook);
        }

        // ---------- A1: spree ----------

        public static string SpreeStart(string args)
        {
            string r = Setup(out Map map);
            if (r != null) return r;
            spreePawn = colonist;
            spreeTick = Find.TickManager.TicksGame;
            MentalStateDef state = RMGraffitiDefOf.RM_GraffitiPaintingSpreeState;
            bool started = spreePawn.mindState.mentalStateHandler.TryStartMentalState(state, "GRAFFITI_V1_LIVE_PROOF_1", forced: true, forceWake: true);
            return "SPREE started " + B(started) + " | pawn " + spreePawn.ThingID + " | state " + (spreePawn.MentalStateDef?.defName ?? "none");
        }

        public static string SpreeRead(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null || spreePawn == null) return "REFUSED no spree started (SpreeStart first)";
            // only marks this spree made (placed since SpreeStart), never an older mark of the same pawn elsewhere on the map
            List<Filth_Mark> made = Marks(map).Where(m => m.maker == spreePawn && m.placedTick >= spreeTick).ToList();
            int faction = made.Count(m => m.makerFaction != null && m.makerFaction == spreePawn.Faction);
            int ideo = made.Count(m => m.makerIdeo != null && m.makerIdeo == spreePawn.Ideo);
            string stateNow = spreePawn.MentalStateDef?.defName ?? "none";
            if (made.Count > 0 && spreePawn.InMentalState) spreePawn.MentalState.RecoverFromState();   // the evidence is in: end the spree
            return "READ marks " + made.Count + " | factionOk " + faction + " | ideoOk " + ideo
                + " | defs " + string.Join(",", made.Select(m => m.def.defName).Distinct()) + " | state " + stateNow;
        }

        // ---------- A2: raid exit ----------

        public static string RaidStart(string args)
        {
            string r = Setup(out Map map);
            if (r != null) return r;
            raidFaction = Enemy();
            if (raidFaction == null) return "REFUSED no humanlike enemy faction in this game";
            BuildInterior(map);
            raiders = new List<Pawn>();
            raidTick = Find.TickManager.TicksGame;
            for (int i = 0; i < 3; i++)
            {
                Pawn p = EnemyPawn(raidFaction);
                GenSpawn.Spawn(p, Cell(3 + 2 * i, WallRow + 2), map);
                raiders.Add(p);
            }
            // one raider INSIDE the roofed room: the exit must not leave it an interior tag (A2 "on an exterior wall")
            Pawn inside = EnemyPawn(raidFaction);
            GenSpawn.Spawn(inside, Cell(14, WallRow - 3), map);
            raiders.Add(inside);
            raidLord = LordMaker.MakeNewLord(raidFaction, new LordJob_AssaultColony(raidFaction, canKidnap: false, canTimeoutOrFlee: false,
                sappers: false, useAvoidGridSmart: false, canSteal: false), map, raiders);
            return "RAID spawned " + raiders.Count + " | faction " + raidFaction.Name + " | marksIn " + Marks(map).Count(m => m.makerFaction == raidFaction && m.placedTick >= raidTick)
                + " | toil " + raidLord.CurLordToil?.GetType().Name;
        }

        // A2's interior: the south side of the site wall becomes a closed, roofed room (walls at dx 0 and W-1 for z 0..WallRow,
        // and along z 0), so the raid-exit finder's radius reaches interior wall faces from the raiders outside and from the one
        // raider inside. The proof reads interior by this geometry (InInterior) plus the roof, not by the mod's own predicate.
        private static bool InInterior(IntVec3 c) => c.x > origin.x && c.x < origin.x + W - 1 && c.z > origin.z && c.z < origin.z + WallRow;

        private static void BuildInterior(Map map)
        {
            var ring = new List<IntVec3>();
            for (int dz = 0; dz <= WallRow; dz++) { ring.Add(Cell(0, dz)); ring.Add(Cell(W - 1, dz)); }
            for (int dx = 1; dx < W - 1; dx++) ring.Add(Cell(dx, 0));
            foreach (IntVec3 c in ring)
            {
                foreach (Pawn p in c.GetThingList(map).OfType<Pawn>().ToList()) Place(p, Cell(W / 2, 2));
                Thing wall = ThingMaker.MakeThing(ThingDefOf.Wall, ThingDefOf.Steel);
                wall.SetFaction(Faction.OfPlayer);
                GenSpawn.Spawn(wall, c, map);
            }
            for (int dx = 1; dx < W - 1; dx++)
                for (int dz = 1; dz < WallRow; dz++)
                    map.roofGrid.SetRoof(Cell(dx, dz), RoofDefOf.RoofConstructed);
        }

        public static string RaidExit(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null || raidLord == null) return "REFUSED no raid started (RaidStart first)";
            // only marks made by THIS probe's raiders count, so another raid of the same faction elsewhere on the map never scores
            int mid = Marks(map).Count(m => m.placedTick >= raidTick && m.maker != null && raiders.Contains(m.maker));
            string before = raidLord.CurLordToil?.GetType().Name ?? "none";
            LordToil exit = raidLord.Graph.lordToils.FirstOrDefault(RaidExitTaggerMod.IsLeavingToil);
            if (exit == null) return "REFUSED the raid lord's graph holds no leaving toil";
            int standing = raiders.Count(p => p.Spawned && !p.Downed);
            raidLord.GotoToil(exit);
            List<Filth_Mark> after = Marks(map).Where(m => m.placedTick >= raidTick && m.maker != null && raiders.Contains(m.maker)).ToList();
            int eligible = after.Count(m => m.def.GetModExtension<ModExtension_Graffiti>()?.raidExitEligible ?? false);
            int onWall = after.Count(m => m.wallSide != RM_GraffitiKernel.NoWall);
            // exterior = outside the built room, unroofed, and in the SAME room as an open reference cell north of the wall (the map's
            // outdoors), so an unroofed courtyard of some other enclosed room near the site never counts
            Room outdoors = Cell(W / 2, H - 2).GetRoom(map);
            int exterior = after.Count(m => !InInterior(m.Position) && !m.Position.Roofed(map) && outdoors != null
                && m.Position.GetRoom(map) == outdoors);
            // the site can tell exterior from interior only if the interior is really closed and roofed when the exit fires
            int roofedInterior = 0, interiorCells = 0;
            for (int dx = 1; dx < W - 1; dx++)
                for (int dz = 1; dz < WallRow; dz++) { interiorCells++; if (Cell(dx, dz).Roofed(map)) roofedInterior++; }
            Room room = Cell(W / 2, 2).GetRoom(map);
            bool closed = room != null && !room.TouchesMapEdge && !room.PsychologicallyOutdoors;
            int inside = raiders.Count(p => p.Spawned && !p.Downed && InInterior(p.Position));
            foreach (Pawn p in raiders) Retire(p);
            raiders.Clear();
            return "EXIT mid " + mid + " | after " + after.Count + " | eligible " + eligible + " | onWall " + onWall
                + " | exterior " + exterior + " | outsideOpen " + B(outdoors != null && outdoors.PsychologicallyOutdoors) + " | interiorClosed " + B(closed && roofedInterior == interiorCells) + " | inside " + inside
                + " | standing " + standing + " | toil " + before + "->" + exit.GetType().Name;
        }

        // ---------- A3: tier-A sigil ----------

        public static string Sigil(string args)
        {
            string r = Setup(out Map map);
            if (r != null) return r;
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Graffiti_IdeoSigil");
            if (def == null) return "REFUSED RM_Graffiti_IdeoSigil is not loaded";
            Filth_Mark m = Filth_Mark.MakeMark(Face(3), map, def, colonist);
            if (m == null) return "REFUSED the sigil was not placed at " + Face(3);
            Ideo ideo = m.makerIdeo;
            Material frame = m.ProbeFrameMat, icon = m.ProbeIconMat;
            string frameTex = frame?.mainTexture?.name ?? "none";
            bool iconIsIdeo = icon != null && ideo != null && icon.mainTexture == ideo.Icon;
            bool tint = icon != null && ideo != null && Mathf.Abs(icon.color.r - ideo.Color.r) < 0.01f
                && Mathf.Abs(icon.color.g - ideo.Color.g) < 0.01f && Mathf.Abs(icon.color.b - ideo.Color.b) < 0.01f;
            map.mapDrawer.MapMeshDirty(m.Position, MapMeshFlagDefOf.Things, regenAdjacentCells: true, regenAdjacentSections: false);
            return "SIGIL ideo " + B(ideo != null) + " | frame " + frameTex + " | iconIsIdeo " + B(iconIsIdeo) + " | tinted " + B(tint)
                + " | wallSide " + m.wallSide + " | cell " + m.Position.x + "," + m.Position.z;
        }

        // ---------- A4: going-over ----------

        public static string GoingOver(string args)
        {
            string r = Setup(out Map map);
            if (r != null) return r;
            Faction enemy = Enemy();
            if (enemy == null) return "REFUSED no humanlike enemy faction in this game";
            Pawn rival = EnemyPawn(enemy);
            IntVec3 c = Face(5);
            Filth_Mark first = Filth_Mark.MakeMark(c, map, DefDatabase<ThingDef>.GetNamed("RM_Graffiti_Tag_A"), colonist);
            Filth_Mark second = Filth_Mark.MakeMark(c, map, DefDatabase<ThingDef>.GetNamed("RM_Graffiti_ThrowUp_A"), rival);
            Retire(rival);
            List<Filth_Mark> at = c.GetThingList(map).OfType<Filth_Mark>().ToList();
            Filth_Mark top = at.FirstOrDefault();
            return "OVER placed " + B(first != null && second != null) + " | firstGone " + B(first != null && first.Destroyed)
                + " | marksAtCell " + at.Count + " | def " + (top?.def.defName ?? "none") + " | rivalFaction " + B(top != null && top.makerFaction == enemy);
        }

        // ---------- A5: hostile-maker thought ----------

        public static string HostileThought(string args)
        {
            string r = Setup(out Map map);
            if (r != null) return r;
            ThoughtDef def = DefDatabase<ThoughtDef>.GetNamedSilentFail("RM_Graffiti_ViewedHostileMark");
            if (def == null) return "REFUSED RM_Graffiti_ViewedHostileMark is not loaded";
            Faction enemy = Enemy();
            if (enemy == null) return "REFUSED no humanlike enemy faction in this game";
            Pawn rival = EnemyPawn(enemy);
            Place(colonist, Cell(8, WallRow - 3));
            Filth_Mark m = Filth_Mark.MakeMark(Face(8), map, DefDatabase<ThingDef>.GetNamed("RM_Graffiti_Tag_A"), rival);
            Retire(rival);
            if (m == null) return "REFUSED the hostile mark was not placed";
            bool hostile = m.makerFaction != null && m.makerFaction.HostileTo(colonist.Faction);
            bool worker = def.Worker.CurrentState(colonist).Active;
            var sit = colonist.needs?.mood?.thoughts?.situational;
            sit?.Notify_SituationalThoughtsDirty();
            var got = new List<Thought>();
            sit?.AppendMoodThoughts(def, got);
            return "THOUGHT makerHostile " + B(hostile) + " | worker " + B(worker) + " | mood " + B(got.Count > 0)
                + " | viewerOn " + B(RM_GraffitiSettings.viewerReactionEnabled);
        }

        // ---------- A6: scrub ----------

        public static string CleanSetup(string args)
        {
            string r = Setup(out Map map);
            if (r != null) return r;
            Faction enemy = Enemy();
            if (enemy == null) return "REFUSED no humanlike enemy faction in this game";
            Pawn rival = EnemyPawn(enemy);
            ThingDef vandal = RMGraffitiDefOf.RM_Graffiti_Vandal, sigil = DefDatabase<ThingDef>.GetNamed("RM_Graffiti_IdeoSigil");
            ownMark = Filth_Mark.MakeMark(Face(11), map, vandal, colonist);
            devotionalMark = Filth_Mark.MakeMark(Face(12), map, sigil, rival);
            controlMark = Filth_Mark.MakeMark(Face(13), map, vandal, rival);
            Retire(rival);
            Place(colonist, Cell(12, WallRow - 3));
            // no colonist auto-cleans during the 600-tick thickening wait, so the unforced reads see every mark still standing
            foreach (Pawn p in map.mapPawns.FreeColonistsSpawned.ToList())
            {
                if (p.workSettings != null && p.workSettings.EverWork) p.workSettings.SetPriority(WorkTypeDefOf.Cleaning, 0);
            }
            return "CLEANSET own " + B(ownMark != null) + " | devotional " + B(devotionalMark != null) + " | control " + B(controlMark != null);
        }

        public static string CleanRead(string args)
        {
            if (ownMark == null || devotionalMark == null || controlMark == null || colonist == null) return "REFUSED CleanSetup first";
            if (ownMark.Destroyed || devotionalMark.Destroyed || controlMark.Destroyed)
                return "REFUSED a mark vanished during the wait: own " + B(ownMark.Destroyed) + " devotional " + B(devotionalMark.Destroyed) + " control " + B(controlMark.Destroyed);
            var wg = (WorkGiver_Scanner)DefDatabase<WorkGiverDef>.GetNamed("CleanFilth").Worker;
            bool uOwn = wg.HasJobOnThing(colonist, ownMark, false), uDev = wg.HasJobOnThing(colonist, devotionalMark, false);
            bool uCtl = wg.HasJobOnThing(colonist, controlMark, false);
            bool fOwn = wg.HasJobOnThing(colonist, ownMark, true), fDev = wg.HasJobOnThing(colonist, devotionalMark, true);
            bool ordered = false;
            if (fOwn && fDev)
            {
                Job job = JobMaker.MakeJob(JobDefOf.Clean);
                job.AddQueuedTarget(TargetIndex.A, ownMark);
                job.AddQueuedTarget(TargetIndex.A, devotionalMark);
                ordered = colonist.jobs.TryTakeOrderedJob(job, JobTag.Misc);
            }
            return "CLEAN unforcedOwn " + B(uOwn) + " | unforcedDevotional " + B(uDev) + " | unforcedControl " + B(uCtl)
                + " | forcedOwn " + B(fOwn) + " | forcedDevotional " + B(fDev) + " | ordered " + B(ordered);
        }

        public static string CleanDone(string args)
        {
            if (ownMark == null || devotionalMark == null) return "REFUSED CleanSetup first";
            return "DONE ownGone " + B(ownMark.Destroyed) + " | devotionalGone " + B(devotionalMark.Destroyed)
                + " | job " + (colonist?.CurJobDef?.defName ?? "none");
        }

        // ---------- A7: designator choice ----------

        public static string DesignateSetup(string args)
        {
            string r = Setup(out Map map);
            if (r != null) return r;
            chosen = GraffitiPool.AllDesignatorEligible()
                .Where(d => GraffitiPool.PainterMayPaint(d, colonist))
                .OrderBy(d => d.defName).Take(3).ToList();
            if (chosen.Count < 3) return "REFUSED fewer than 3 designator marks this colonist may paint: " + chosen.Count;
            var designator = new Designator_PaintGraffitiMark();
            var field = AccessTools.Field(typeof(Designator_PaintGraffitiMark), "chosenMark");
            designated = new List<IntVec3>();
            designatedDefs = new List<ThingDef>();
            int accepted = 0;
            for (int i = 0; i < chosen.Count; i++)
            {
                IntVec3 c = Face(15 + i);
                if (!designator.CanDesignateCell(c).Accepted) continue;
                accepted++;
                field.SetValue(designator, chosen[i]);
                designator.DesignateSingleCell(c);
                designated.Add(c);
                designatedDefs.Add(chosen[i]);
            }
            WorkGiverDef wgDef = DefDatabase<WorkGiverDef>.GetNamed("RM_PaintGraffitiDesignated");
            var wg = (WorkGiver_Scanner)wgDef.Worker;
            int ordered = 0;
            foreach (IntVec3 c in designated)
            {
                Job job = wg.JobOnCell(colonist, c, true);
                if (job == null) continue;
                job.workGiverDef = wgDef;
                if (colonist.jobs.TryTakeOrderedJob(job, JobTag.Misc, requestQueueing: ordered > 0)) ordered++;
            }
            return "DESIGNATED " + designated.Count + " | accepted " + accepted + " | ordered " + ordered
                + " | marks " + string.Join(",", chosen.Select(d => d.defName));
        }

        public static string DesignateRead(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null || designated.Count == 0) return "REFUSED DesignateSetup first";
            int painted = 0, matched = 0;
            var got = new List<string>();
            for (int i = 0; i < designated.Count; i++)
            {
                Filth_Mark m = MarkAt(map, designated[i]);
                got.Add(m?.def.defName ?? "none");
                if (m == null) continue;
                painted++;
                if (m.def == designatedDefs[i] && m.maker == colonist) matched++;
            }
            int pending = designated.Count(c => map.designationManager.DesignationAt(c, RMGraffitiDefOf.RM_PaintGraffitiHere) != null);
            return "READ painted " + painted + " | matched " + matched + " | of " + designated.Count + " | pending " + pending
                + " | got " + string.Join(",", got) + " | job " + (colonist?.CurJobDef?.defName ?? "none");
        }
    }
}
