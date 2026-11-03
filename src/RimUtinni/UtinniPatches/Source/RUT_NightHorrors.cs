using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI.Group;
using RimMandrake.StarWars.WeatherSuite;

namespace RimMandrake.Utinni.UtinniPatches
{
    // HORRORS_RAIDING_FACTION_1 (2026-11-02): the Horrors as a raiding faction of the nightside, the starved-cold
    // Assailant weapon on patrol. Defs and the why: Defs/Misc/RUT_NightHorrors.xml. Owner ruled 2026-09-09 that the reach
    // is nightside/cold, "a threat you walk toward, not one that finds you": every Horror act below asks InReach first,
    // and InReach is the WeatherSuite nightside band (WeatherGeometryUtility, the shared arc formula, not reinvented).
    // No Harmony: vanilla RaidEnemy is kept off this faction by its zero raidCommonalityFromPointsCurve (weight 0 in
    // PawnGroupMakerUtility.TryGetRandomFactionForCombatPawnGroupWeighted), exactly as vanilla keeps it off Insect.

    [DefOf]
    public static class RUT_NightHorrorsDefOf
    {
        public static FactionDef RUT_Horrors;

        static RUT_NightHorrorsDefOf() { DefOfHelper.EnsureInitializedInCtor(typeof(RUT_NightHorrorsDefOf)); }
    }

    /// <summary>Pure decisions, no game state, so they can be read and checked on their own.</summary>
    public static class RUT_NightHorrorsKernel
    {
        /// <summary>A Horror act may happen here: the feature is on and the map's tile is in the nightside band.</summary>
        public static bool InReach(bool enabled, bool nightside) { return enabled && nightside; }

        /// <summary>A crysalis breaks open: an intruder within its radius, or its cell has thawed above the thaw line.</summary>
        public static bool ShouldWake(float nearestIntruderDistSq, float radius, float cellTemperature, float thawTemperature)
        {
            return nearestIntruderDistSq <= radius * radius || cellTemperature > thawTemperature;
        }
    }

    public static class RUT_HorrorFaction
    {
        /// <summary>The map is inside the reach. A pocket map (invalid tile) is never in it: ArcFromSubstellar fails closed.</summary>
        public static bool MapInReach(Map map, bool enabled)
        {
            return map != null && RUT_NightHorrorsKernel.InReach(enabled, WeatherGeometryUtility.MapInNightsideBand(map));
        }

        /// <summary>The one RUT_Horrors faction, made on first need. The shipped world is frozen and predates it, so it is
        /// never made at world start; NewGeneratedFaction places no settlement (that is FactionGenerator.InitializeFactions'
        /// job, which never runs again), and the def is hidden with settlementGenerationWeight 0 besides.</summary>
        public static Faction GetOrCreate()
        {
            FactionDef def = RUT_NightHorrorsDefOf.RUT_Horrors;
            Faction f = Find.FactionManager.FirstFactionOfDef(def);
            if (f != null) return f;
            f = FactionGenerator.NewGeneratedFaction(new FactionGeneratorParms(def));
            Find.FactionManager.Add(f);
            return f;
        }
    }

    /// <summary>RUT_HorrorRaid: the only road to a Horror raid. Fires on a nightside map only; walks in and attacks.</summary>
    public class RUT_IncidentWorker_HorrorRaid : IncidentWorker_RaidEnemy
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            // Not base: PawnsArrive's check asks for an existing candidate faction, and this one is made on first fire.
            return RUT_HorrorFaction.MapInReach(parms.target as Map, UtinniPatchesSettings.nightHorrorRaidsEnabled);
        }

        protected override bool TryResolveRaidFaction(IncidentParms parms)
        {
            parms.faction = RUT_HorrorFaction.GetOrCreate();
            return parms.faction != null;
        }

        public override void ResolveRaidStrategy(IncidentParms parms, PawnGroupKindDef groupKind)
        {
            if (parms.raidStrategy == null) parms.raidStrategy = RaidStrategyDefOf.ImmediateAttack;
        }

        public override void ResolveRaidArriveMode(IncidentParms parms)
        {
            if (parms.raidArrivalMode == null) parms.raidArrivalMode = PawnsArrivalModeDefOf.EdgeWalkIn;
        }

        public override bool TryResolveRaidArriveMode(IncidentParms parms)
        {
            if (parms.raidArrivalMode != null) return false;
            parms.raidArrivalMode = PawnsArrivalModeDefOf.EdgeWalkIn;
            return true;
        }

        public override void ResolveRaidAgeRestriction(IncidentParms parms) { }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            if (!RUT_HorrorFaction.MapInReach(parms.target as Map, UtinniPatchesSettings.nightHorrorRaidsEnabled)) return false;
            return base.TryExecuteWorker(parms);
        }
    }

    /// <summary>Places one to three Assailant lairs on a newly generated nightside map; any other map is left alone.</summary>
    public class RUT_GenStep_NightHorrorLairs : GenStep
    {
        public IntRange lairCountRange = new IntRange(1, 3);
        public ThingDef hive, den, burrow, sinkhole, larder;
        public List<ThingDef> crysalises = new List<ThingDef>();
        public float minDistFromStart = 35f, minDistBetweenLairs = 30f;
        public int edgeMargin = 15, lairRadius = 7;

        public override int SeedPart => 418806271;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RUT_HorrorFaction.MapInReach(map, UtinniPatchesSettings.nightHorrorLairsEnabled)) return;
            int want = lairCountRange.RandomInRange, placed = 0;
            var centers = new List<IntVec3>();
            IntVec3 start = MapGenerator.PlayerStartSpotValid ? MapGenerator.PlayerStartSpot : map.Center;
            for (int i = 0; i < want; i++)
            {
                if (!CellFinder.TryFindRandomCell(map, c => CenterOk(c, map, start, centers), out IntVec3 center)) break;
                centers.Add(center);
                if (BuildLair(center, map)) placed++;
            }
            if (placed == 0) Log.Warning("[RUT_GenStep_NightHorrorLairs] nightside map " + map + ": no lair placed (no open ground away from the start?).");
        }

        private bool CenterOk(IntVec3 c, Map map, IntVec3 start, List<IntVec3> centers)
        {
            if (c.CloseToEdge(map, edgeMargin) || !Open(c, map)) return false;
            if (start.IsValid && c.InHorDistOf(start, minDistFromStart)) return false;
            foreach (IntVec3 o in centers) if (c.InHorDistOf(o, minDistBetweenLairs)) return false;
            return true;
        }

        private static bool Open(IntVec3 c, Map map)
        {
            if (!c.InBounds(map) || !c.Standable(map) || c.Roofed(map)) return false;
            TerrainDef t = c.GetTerrain(map);
            return t != null && !t.IsWater && t.passability != Traversability.Impassable;
        }

        private bool BuildLair(IntVec3 center, Map map)
        {
            if (!TrySpawn(hive, center, map, 0)) return false;
            TrySpawn(den, center, map, lairRadius);
            for (int i = Rand.RangeInclusive(1, 3); i > 0; i--) TrySpawn(burrow, center, map, lairRadius);
            if (Rand.Chance(0.5f)) TrySpawn(sinkhole, center, map, lairRadius);
            TrySpawn(larder, center, map, lairRadius);
            if (!crysalises.NullOrEmpty())
                for (int i = Rand.RangeInclusive(2, 5); i > 0; i--) TrySpawn(crysalises.RandomElement(), center, map, lairRadius);
            return true;
        }

        private bool TrySpawn(ThingDef def, IntVec3 center, Map map, int radius)
        {
            if (def == null) return false;
            for (int tries = 0; tries < 30; tries++)
            {
                IntVec3 c = radius == 0 ? center : center + GenRadial.RadialPattern[Rand.Range(1, GenRadial.NumCellsInRadius(radius))];
                CellRect rect = GenAdj.OccupiedRect(c, Rot4.North, def.size);
                if (!rect.Cells.All(x => Open(x, map) && x.GetEdifice(map) == null && !x.CloseToEdge(map, 3))) { if (radius == 0) radius = 2; continue; }
                foreach (IntVec3 x in rect.Cells)
                {
                    Plant p = x.GetPlant(map);
                    if (p != null) p.Destroy(DestroyMode.Vanish);
                }
                GenSpawn.Spawn(ThingMaker.MakeThing(def), c, map, Rot4.North, WipeMode.Vanish);
                return true;
            }
            return false;
        }
    }

    public class RUT_CompProperties_HorrorCrysalis : CompProperties
    {
        public PawnKindDef pawnKind;
        public float triggerRadius = 4f;
        public float thawTemperature = 0f;
        public float burstRadius = 1.9f;
        public int burstDamage = 6;
        public int scanIntervalTicks = 120;

        public RUT_CompProperties_HorrorCrysalis() { compClass = typeof(RUT_CompHorrorCrysalis); }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef)) yield return e;
            if (pawnKind == null) yield return "RUT_CompProperties_HorrorCrysalis on " + parentDef.defName + " has no pawnKind";
            if (parentDef.tickerType != TickerType.Normal) yield return "RUT_CompProperties_HorrorCrysalis on " + parentDef.defName + " needs tickerType Normal";
        }
    }

    /// <summary>The cold-dormancy mechanic: a crysalis sleeps until someone not of the weapon comes close or its cell thaws
    /// ("Mining is warming"), then a small burst of stored energy breaks it and the form inside joins the Horrors and
    /// attacks. Wild animals do not wake it; only the player's pawns and humanlikes do.</summary>
    public class RUT_CompHorrorCrysalis : ThingComp
    {
        private bool woken;

        public RUT_CompProperties_HorrorCrysalis Props => (RUT_CompProperties_HorrorCrysalis)props;

        public override void CompTick()
        {
            base.CompTick();
            if (woken || !parent.Spawned || !parent.IsHashIntervalTick(Props.scanIntervalTicks)) return;
            if (!UtinniPatchesSettings.nightHorrorLairsEnabled) return;
            Map map = parent.Map;
            Faction horrors = Find.FactionManager.FirstFactionOfDef(RUT_NightHorrorsDefOf.RUT_Horrors);
            float nearest = float.MaxValue;
            Pawn trigger = null;
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (p.Dead || p.Downed || (horrors != null && p.Faction == horrors)) continue;
                if (!(p.Faction == Faction.OfPlayer || p.RaceProps.Humanlike)) continue;
                float d = p.Position.DistanceToSquared(parent.Position);
                if (d < nearest) { nearest = d; trigger = p; }
            }
            if (RUT_NightHorrorsKernel.ShouldWake(nearest, Props.triggerRadius, parent.Position.GetTemperature(map), Props.thawTemperature))
                Wake(trigger);
        }

        public void Wake(Pawn trigger)
        {
            if (woken || !parent.Spawned) return;
            woken = true;
            Map map = parent.Map;
            IntVec3 pos = parent.Position;
            Faction horrors = RUT_HorrorFaction.GetOrCreate();
            Pawn form = PawnGenerator.GeneratePawn(new PawnGenerationRequest(Props.pawnKind, horrors, PawnGenerationContext.NonPlayer,
                forceGenerateNewPawn: true, mustBeCapableOfViolence: true));
            parent.Destroy(DestroyMode.Vanish);
            GenSpawn.Spawn(form, pos, map);
            FilthMaker.TryMakeFilth(pos, map, ThingDefOf.Filth_Slime, 3);
            GenExplosion.DoExplosion(pos, map, Props.burstRadius, DamageDefOf.Bomb, null, Props.burstDamage,
                ignoredThings: new List<Thing> { form });
            LordMaker.MakeNewLord(horrors, new LordJob_AssaultColony(horrors, canKidnap: false, canTimeoutOrFlee: false, canSteal: false),
                map, new List<Pawn> { form });
            if (trigger != null && trigger.Faction == Faction.OfPlayer)
                Messages.Message("RUT_HorrorCrysalisWoke".Translate(form.LabelShort), form, MessageTypeDefOf.ThreatSmall);
        }

        public override string CompInspectStringExtra()
        {
            return "RUT_HorrorCrysalisDormant".Translate(Props.thawTemperature.ToStringTemperature("F0"));
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref woken, "woken", false);
        }
    }
}
