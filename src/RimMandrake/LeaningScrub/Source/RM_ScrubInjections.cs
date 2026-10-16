using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // LEANINGSCRUB_MECHANICS_BUILD_1 part 8 — inhabited injections.
    //
    // Owner, typed: "Lots of inhabited injections all over here from ruins to current living denizens."
    // Q10 (card 2026-10-15): "Ruins plus living camps". N1 (typed): "Scavengers and vapor farming new".
    // Q8 (card): the vaporator is "learned from a dead farmstead".
    //
    // A map step (RM_LeaningScrub's extraGenSteps, order 915: after Plants 900 and the sweetline trees 910, before
    // Animals 1200) that places, spread wide and clear of the map centre:
    //   ruins  — the first is always a DEAD FARMSTEAD (broken wall, a comb-row of vaporator wrecks, the vaporator
    //            techprint inside while the colony has not learned it: the study source); the rest are SMOTHER-CLAIMED
    //            FIELDS (venomvine under blankets, found mid-cycle) or HEDGE HOMESTEADS (a hut in a venomvine ring).
    //   camps  — a LIVING CAMP of the comb-row farmers (RM_Faction_CombHolds, the new people) and one of a scavenger
    //            clan (scavengerFactions: empty in this franchise-free tier; UtinniPatches adds the Jawa clans).
    //            A camp is skipped when its faction is missing from the world or hostile to the player. Its people
    //            hold the camp (RM_LordJob_ScrubCamp: defend, and assault only once the colony is their enemy; vanilla
    //            LordJob_DefendBase would assault on a timer, a 3% roll and hunger, announcing an attack while at peace) and
    //            RM_MapComponent_ScrubCamps keeps them fed and rested: sustenance is present, not produced (the
    //            same answer as the Inhabited mod's InhabitedPlaceDef notes; NPCs cannot farm).
    // Settings: scrubInjectionsEnabled (ruins), scrubCampsEnabled (camps), scrubRuinsPerMap. New maps only.
    // Numbers PROVISIONAL (RM_InjectionKernel).
    // ════════════════════════════════════════════════════════════════════
    public class RM_GenStep_ScrubInjections : GenStep
    {
        public ThingDef ruinVaporatorDef;
        public ThingDef vaporatorDef;
        public ThingDef waterDef;
        public ThingDef thicketDef;
        public ThingDef blanketDef;
        public ResearchProjectDef studyResearch;
        public FactionDef farmerFaction;
        public List<FactionDef> scavengerFactions = new List<FactionDef>();
        public int edgeMargin = 14;
        public float minSpacing = 32f;
        public float startClearance = 36f;
        public IntRange campPawns = new IntRange(3, 5);
        public int maxTries = 300;

        public override int SeedPart => 734512093;

        private readonly List<IntVec3> placed = new List<IntVec3>();

        public override void Generate(Map map, GenStepParams parms)
        {
            placed.Clear();
            // Only the player's own home maps: the step rides the biome's extraGenSteps, so it would otherwise also run
            // on enemy bases, quest sites and ambush maps of this biome.
            if (map.ParentFaction == null || map.ParentFaction != Faction.OfPlayerSilentFail)
            {
                return;
            }
            List<CellRect> used = MapGenerator.UsedRects;
            if (RM_WindCalendar.On(RM_LeaningScrubSettings.scrubInjectionsEnabled))
            {
                int ruins = RM_InjectionKernel.Clamp(RM_LeaningScrubSettings.scrubRuinsPerMap, 0, 8);
                for (int i = 0; i < ruins; i++)
                {
                    int kind = RM_InjectionKernel.RuinKind(i, Rand.Value);
                    int radius = kind == RM_InjectionKernel.RuinHedgeHomestead ? 6 : 5;
                    if (!TryFindSite(map, radius, used, out IntVec3 c)) continue;
                    Clear(map, c, radius);
                    if (kind == RM_InjectionKernel.RuinFarmstead) DeadFarmstead(map, c);
                    else if (kind == RM_InjectionKernel.RuinSmotherField) SmotherField(map, c);
                    else HedgeHomestead(map, c);
                    Claim(c, radius, used);
                }
            }
            if (RM_WindCalendar.On(RM_LeaningScrubSettings.scrubCampsEnabled))
            {
                TryCamp(map, used, LivingFaction(farmerFaction), farmers: true);
                Faction scav = null;
                for (int i = 0; i < scavengerFactions.Count && scav == null; i++)
                {
                    scav = LivingFaction(scavengerFactions[i]);
                }
                TryCamp(map, used, scav, farmers: false);
            }
        }

        /// <summary>The faction of that def in this world, when it is not hostile to the player; else null.</summary>
        public static Faction LivingFaction(FactionDef def)
        {
            if (def == null || Find.FactionManager == null) return null;
            Faction f = Find.FactionManager.FirstFactionOfDef(def);
            if (f == null || f.defeated || f.IsPlayer) return null;
            if (Faction.OfPlayerSilentFail != null && f.HostileTo(Faction.OfPlayer)) return null;
            return f;
        }

        private bool TryFindSite(Map map, int radius, List<CellRect> used, out IntVec3 site)
        {
            int[] xs = new int[placed.Count], zs = new int[placed.Count];
            for (int i = 0; i < placed.Count; i++) { xs[i] = placed[i].x; zs[i] = placed[i].z; }
            IntVec3 centre = map.Center;
            for (int t = 0; t < maxTries; t++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                if (c.CloseToEdge(map, edgeMargin + radius)) continue;
                if (!RM_InjectionKernel.Spaced(c.x, c.z, xs, zs, xs.Length, minSpacing, centre.x, centre.z, startClearance)) continue;
                if (SiteOk(map, CellRect.CenteredOn(c, radius), used))
                {
                    site = c;
                    return true;
                }
            }
            site = IntVec3.Invalid;
            return false;
        }

        private static bool SiteOk(Map map, CellRect rect, List<CellRect> used)
        {
            if (used != null)
            {
                for (int i = 0; i < used.Count; i++)
                {
                    if (used[i].Overlaps(rect)) return false;
                }
            }
            foreach (IntVec3 c in rect)
            {
                if (!c.InBounds(map) || !c.Standable(map) || c.Roofed(map) || c.GetEdifice(map) != null) return false;
                TerrainDef terrain = c.GetTerrain(map);
                if (terrain == null || terrain.IsWater || !terrain.affordances.Contains(TerrainAffordanceDefOf.Light)) return false;
                if (c.GetFirstPawn(map) != null) return false;
            }
            return true;
        }

        private void Claim(IntVec3 c, int radius, List<CellRect> used)
        {
            placed.Add(c);
            used?.Add(CellRect.CenteredOn(c, radius));
        }

        private static void Clear(Map map, IntVec3 c, int radius)
        {
            foreach (IntVec3 cell in CellRect.CenteredOn(c, radius))
            {
                List<Thing> here = cell.GetThingList(map);
                for (int i = here.Count - 1; i >= 0; i--)
                {
                    Thing t = here[i];
                    if (t is Plant || t.def.category == ThingCategory.Item || t.def.category == ThingCategory.Filth)
                    {
                        t.Destroy();
                    }
                }
            }
        }

        private static Thing Build(Map map, ThingDef def, ThingDef stuff, IntVec3 at, Faction faction, bool ruined)
        {
            if (def == null || !at.InBounds(map)) return null;
            if (def.MadeFromStuff && stuff == null) stuff = GenStuff.DefaultStuffFor(def);
            Thing t = ThingMaker.MakeThing(def, def.MadeFromStuff ? stuff : null);
            if (faction != null && def.CanHaveFaction) t.SetFaction(faction);
            if (ruined && def.useHitPoints) t.HitPoints = RM_InjectionKernel.RuinHitPoints(t.MaxHitPoints, Rand.Value);
            return GenSpawn.Spawn(t, at, map, Rot4.North, WipeMode.Vanish);
        }

        private static void Drop(Map map, ThingDef def, int count, IntVec3 at)
        {
            if (def == null || count <= 0) return;
            Thing t = ThingMaker.MakeThing(def);
            t.stackCount = Mathf.Min(count, def.stackLimit);
            GenPlace.TryPlaceThing(t, at, map, ThingPlaceMode.Near);
        }

        private static void Rubble(Map map, IntVec3 c, int radius, int count)
        {
            ThingDef rubble = DefDatabase<ThingDef>.GetNamedSilentFail("Filth_RubbleBuilding");
            if (rubble == null) return;
            for (int i = 0; i < count; i++)
            {
                IntVec3 at = c + new IntVec3(Rand.RangeInclusive(-radius, radius), 0, Rand.RangeInclusive(-radius, radius));
                if (at.InBounds(map) && at.Standable(map)) FilthMaker.TryMakeFilth(at, map, rubble);
            }
        }

        // ── ruins ────────────────────────────────────────────────────────
        private void DeadFarmstead(Map map, IntVec3 c)
        {
            CellRect hut = CellRect.CenteredOn(c, 2);
            foreach (IntVec3 cell in hut.EdgeCells)
            {
                if (RM_InjectionKernel.WallStands(Rand.Value)) Build(map, ThingDefOf.Wall, ThingDefOf.WoodLog, cell, null, ruined: true);
            }
            // A comb-row of wrecked vaporators along the hut's north side, set across the wind.
            for (int dx = -2; dx <= 2; dx += 2)
            {
                Build(map, ruinVaporatorDef, null, c + new IntVec3(dx, 0, 4), null, ruined: false);
            }
            // The study source: the farm's own build plans, left where the family lived.
            if (studyResearch != null && !studyResearch.IsFinished)
            {
                ThingDef print = DefDatabase<ThingDef>.GetNamedSilentFail("Techprint_" + studyResearch.defName);
                if (print != null) Drop(map, print, 1, c);
            }
            Rubble(map, c, 4, 6);
        }

        private void SmotherField(Map map, IntVec3 c)
        {
            if (thicketDef == null) return;
            int claim = RM_CompSmotherable.ClaimTicks;
            // On a brand-new game TicksGame is 0, so MidCycleStart clamps to 0 and these claims start fresh; on any
            // later map they are found part-way through.
            int now = Find.TickManager.TicksGame;
            foreach (IntVec3 cell in CellRect.CenteredOn(c, 4))
            {
                if (!Rand.Chance(0.6f) || !cell.InBounds(map) || cell.GetPlant(map) != null) continue;
                if (!(GenSpawn.Spawn(ThingMaker.MakeThing(thicketDef), cell, map) is Plant p)) continue;
                p.Growth = 1f;
                p.TryGetComp<RM_CompSmotherable>()?.StartSmotherAt(RM_InjectionKernel.MidCycleStart(now, claim, Rand.Value));
            }
            if (blanketDef != null && Rand.Chance(0.5f)) Drop(map, blanketDef, 1, c + new IntVec3(5, 0, 0));
        }

        private void HedgeHomestead(Map map, IntVec3 c)
        {
            CellRect hut = CellRect.CenteredOn(c, 2);
            IntVec3 door = new IntVec3(c.x, 0, hut.minZ);
            foreach (IntVec3 cell in hut.EdgeCells)
            {
                if (cell == door) Build(map, ThingDefOf.Door, ThingDefOf.WoodLog, cell, null, ruined: true);
                else Build(map, ThingDefOf.Wall, ThingDefOf.WoodLog, cell, null, ruined: true);
            }
            if (thicketDef == null) return;
            CellRect ring = CellRect.CenteredOn(c, 5);
            IntVec3 gate = new IntVec3(c.x, 0, ring.minZ);
            foreach (IntVec3 cell in ring.EdgeCells)
            {
                if (cell == gate || !cell.InBounds(map) || cell.GetPlant(map) != null) continue;
                if (GenSpawn.Spawn(ThingMaker.MakeThing(thicketDef), cell, map) is Plant p) p.Growth = 1f;
            }
        }

        // ── living camps ─────────────────────────────────────────────────
        private void TryCamp(Map map, List<CellRect> used, Faction faction, bool farmers)
        {
            if (faction == null || !TryFindSite(map, 5, used, out IntVec3 c)) return;
            Clear(map, c, 5);
            Build(map, ThingDefOf.Campfire, null, c, faction, ruined: false);
            for (int i = 0; i < 4; i++)
            {
                Build(map, ThingDefOf.Bedroll, ThingDefOf.Cloth, c + new IntVec3(-3 + 2 * i, 0, -3), faction, ruined: false);
            }
            if (farmers)
            {
                for (int dx = -2; dx <= 2; dx += 2) Build(map, vaporatorDef, null, c + new IntVec3(dx, 0, 4), faction, ruined: false);
                Drop(map, waterDef, 20, c + new IntVec3(3, 0, 0));
            }
            else
            {
                Drop(map, ThingDefOf.Steel, 40, c + new IntVec3(3, 0, 0));
                ThingDef slag = DefDatabase<ThingDef>.GetNamedSilentFail("ChunkSlagSteel");
                for (int i = 0; i < 3 && slag != null; i++) Build(map, slag, null, c + new IntVec3(-4, 0, i - 1), null, ruined: false);
            }
            List<Pawn> people = MakePeople(faction, map.Tile, campPawns.RandomInRange);
            for (int i = 0; i < people.Count; i++)
            {
                GenSpawn.Spawn(people[i], CellFinder.RandomClosewalkCellNear(c, map, 3), map);
            }
            if (people.Count > 0)
            {
                LordMaker.MakeNewLord(faction, new RM_LordJob_ScrubCamp(faction, c), map, people);
                map.GetComponent<RM_MapComponent_ScrubCamps>()?.Add(people);
            }
            Claim(c, 5, used);
        }

        private static List<Pawn> MakePeople(Faction faction, PlanetTile tile, int want)
        {
            var result = new List<Pawn>();
            if (faction.def.pawnGroupMakers != null && faction.def.pawnGroupMakers.Any(m => m.kindDef == PawnGroupKindDefOf.Settlement))
            {
                var parms = new PawnGroupMakerParms
                {
                    groupKind = PawnGroupKindDefOf.Settlement,
                    faction = faction,
                    tile = tile,
                    points = Mathf.Max(faction.def.MinPointsToGeneratePawnGroup(PawnGroupKindDefOf.Settlement), 300f),
                    generateFightersOnly = false,
                };
                foreach (Pawn p in PawnGroupMakerUtility.GeneratePawns(parms))
                {
                    if (result.Count < want) result.Add(p);
                    else Find.WorldPawns.PassToWorld(p, PawnDiscardDecideMode.Discard);
                }
            }
            if (result.Count == 0 && faction.def.basicMemberKind != null)
            {
                for (int i = 0; i < want; i++) result.Add(PawnGenerator.GeneratePawn(faction.def.basicMemberKind, faction));
            }
            return result;
        }

        /// <summary>Bridge proof (jawa/static_call): run the real step on the current map with every switch on;
        /// report what it placed. Settings restored after.</summary>
        public static string ProofInjections()
        {
            Map map = Find.CurrentMap;
            GenStepDef def = DefDatabase<GenStepDef>.GetNamedSilentFail("RM_ScrubInjections");
            if (map == null || !(def?.genStep is RM_GenStep_ScrubInjections step)) return "REFUSED: no map or no RM_ScrubInjections step";
            bool m = RM_LeaningScrubSettings.modEnabled, r = RM_LeaningScrubSettings.scrubInjectionsEnabled, k = RM_LeaningScrubSettings.scrubCampsEnabled;
            int ruinsBefore = step.ruinVaporatorDef == null ? 0 : map.listerThings.ThingsOfDef(step.ruinVaporatorDef).Count;
            var camps = map.GetComponent<RM_MapComponent_ScrubCamps>();
            int campBefore = camps?.Count ?? 0;
            try
            {
                RM_LeaningScrubSettings.modEnabled = true;
                RM_LeaningScrubSettings.scrubInjectionsEnabled = true;
                RM_LeaningScrubSettings.scrubCampsEnabled = true;
                step.Generate(map, default(GenStepParams));
            }
            finally
            {
                RM_LeaningScrubSettings.modEnabled = m;
                RM_LeaningScrubSettings.scrubInjectionsEnabled = r;
                RM_LeaningScrubSettings.scrubCampsEnabled = k;
            }
            int ruinsAfter = step.ruinVaporatorDef == null ? 0 : map.listerThings.ThingsOfDef(step.ruinVaporatorDef).Count;
            return string.Format("PLACED sites={0} vaporatorWrecks=+{1} campPeople=+{2} farmers={3} scavengers={4}",
                step.placed.Count, ruinsAfter - ruinsBefore, (camps?.Count ?? 0) - campBefore,
                LivingFaction(step.farmerFaction) != null, step.scavengerFactions.Exists(f => LivingFaction(f) != null));
        }
    }

    /// <summary>A living camp's lord: defend the camp; assault the colony only once its faction is the colony's enemy,
    /// and go back to defending if peace returns. No timer, chance, hunger or clamor trigger (vanilla DefendBase has all
    /// four, and fires a ThreatBig "attacking your colony" message with each).</summary>
    public class RM_LordJob_ScrubCamp : LordJob
    {
        private Faction faction;
        private IntVec3 baseCenter;

        public RM_LordJob_ScrubCamp()
        {
        }

        public RM_LordJob_ScrubCamp(Faction faction, IntVec3 baseCenter)
        {
            this.faction = faction;
            this.baseCenter = baseCenter;
        }

        public override StateGraph CreateGraph()
        {
            StateGraph graph = new StateGraph();
            LordToil_DefendBase defend = new LordToil_DefendBase(baseCenter);
            graph.StartingToil = defend;
            LordToil_AssaultColony assault = new LordToil_AssaultColony(attackDownedIfStarving: true) { useAvoidGrid = true };
            graph.AddToil(assault);
            Transition toWar = new Transition(defend, assault);
            toWar.AddTrigger(new Trigger_BecamePlayerEnemy());
            toWar.AddPostAction(new TransitionAction_WakeAll());
            graph.AddTransition(toWar);
            Transition toPeace = new Transition(assault, defend);
            toPeace.AddTrigger(new Trigger_BecameNonHostileToPlayer());
            graph.AddTransition(toPeace);
            return graph;
        }

        public override void ExposeData()
        {
            Scribe_References.Look(ref faction, "faction");
            Scribe_Values.Look(ref baseCenter, "baseCenter");
        }
    }

    /// <summary>Keeps the people of the Scrub's living camps fed and rested while they are not at war with the
    /// colony. Nobody in a camp farms (NPCs cannot); the camp's sustenance is simply present.</summary>
    public class RM_MapComponent_ScrubCamps : MapComponent
    {
        private const int Interval = 2500;
        private List<Pawn> people = new List<Pawn>();

        public int Count => people.Count;

        public RM_MapComponent_ScrubCamps(Map map) : base(map)
        {
        }

        public void Add(List<Pawn> more)
        {
            for (int i = 0; i < more.Count; i++)
            {
                if (!people.Contains(more[i])) people.Add(more[i]);
            }
        }

        public override void MapComponentTick()
        {
            if (people.Count == 0 || Find.TickManager.TicksGame % Interval != 0)
            {
                return;
            }
            people.RemoveAll(p => p == null || p.Dead || p.Destroyed || p.MapHeld != map);
            for (int i = 0; i < people.Count; i++)
            {
                Pawn p = people[i];
                if (!p.Spawned || p.Faction == null || p.Faction.IsPlayer || p.HostileTo(Faction.OfPlayer) || p.needs == null)
                {
                    continue;
                }
                if (p.needs.food != null) p.needs.food.CurLevel = p.needs.food.MaxLevel;
                if (p.needs.rest != null) p.needs.rest.CurLevel = 1f;
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            if (Scribe.mode == LoadSaveMode.Saving)
            {
                people.RemoveAll(p => p == null || p.Dead || p.Destroyed || p.Discarded);
            }
            Scribe_Collections.Look(ref people, "rmScrubCampPeople", LookMode.Reference);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (people == null) people = new List<Pawn>();
                people.RemoveAll(p => p == null);
            }
        }
    }

    // Proof hook for jawa/static_call (validation.py chain "injections", row vaporator_learned_from_farmstead): the
    // vaporator is a powered fog-water spawner behind a techprint-only research project whose techprint exists (the
    // dead farmstead's study source). Def-level; the placement itself is ProofInjections.
    public static class RM_VaporatorProof
    {
        public static string ProofVaporator()
        {
            ThingDef vap = DefDatabase<ThingDef>.GetNamedSilentFail("RM_WindVaporator");
            ResearchProjectDef res = DefDatabase<ResearchProjectDef>.GetNamedSilentFail("RM_WindVaporators");
            if (vap == null || res == null) return "FAIL: vaporator or its research is missing";
            CompProperties_Spawner sp = vap.GetCompProperties<CompProperties_Spawner>();
            if (sp == null || !sp.requiresPower || sp.thingToSpawn == null || sp.thingToSpawn.defName != "RM_FogWater")
                return "FAIL: the vaporator is not a powered fog-water spawner";
            if (vap.researchPrerequisites == null || !vap.researchPrerequisites.Contains(res)) return "FAIL: the vaporator is not behind RM_WindVaporators";
            ThingDef print = DefDatabase<ThingDef>.GetNamedSilentFail("Techprint_RM_WindVaporators");
            if (res.TechprintCount < 1 || print == null) return "FAIL: no techprint for RM_WindVaporators: the farmstead has nothing to teach";
            return "PASS vaporator powered, spawns RM_FogWater, learned from " + print.defName;
        }
    }
}
