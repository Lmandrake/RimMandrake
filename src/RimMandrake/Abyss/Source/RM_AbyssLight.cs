using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Abyss
{
    // ════════════════════════════════════════════════════════════════════
    // ABYSS_LAMP_CROPS_BUILD_1 + ABYSS_FOLD_LAMP_BUILD_1 + ABYSS_SOUNDSCAPE_BUILD_1 (startup half).
    //
    // Startup: Mod Settings that change a DEF are applied once, after defs load (the settings screen says
    // "after a restart" for each):
    //  - lampCropsEnabled off: RM_Wickwood loses its overlight (it lights, it does not farm) and is struck from
    //    RM_Abyss's wild plants (the BiomeDef plant caches are cleared so the strike is seen).
    //  - gustSoundscapeEnabled off: RM_AbyssDark gets back the vanilla fog wind bed the soundscape replaced
    //    with silence.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_AbyssStartup
    {
        static RM_AbyssStartup()
        {
            if (!RM_AbyssSettings.lampCropsEnabled) StrikeLampCrops();
            if (!RM_AbyssSettings.gustSoundscapeEnabled) RestoreWindBed();
        }

        private static void StrikeLampCrops()
        {
            ThingDef wick = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Wickwood");
            if (wick == null) return;
            CompProperties_Glower g = wick.GetCompProperties<CompProperties_Glower>();
            if (g != null) g.overlightRadius = 0f;
            BiomeDef abyss = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Abyss");
            if (abyss?.wildPlants == null) return;
            abyss.wildPlants.RemoveAll(r => r.plant == wick);
            foreach (string f in new[] { "cachedPlantCommonalities", "cachedWildPlants", "cachedLowestWildPlantOrder", "cachedMaxWildPlantsClusterRadius" })
            {
                FieldInfo fi = typeof(BiomeDef).GetField(f, BindingFlags.Instance | BindingFlags.NonPublic);
                if (fi != null) fi.SetValue(abyss, null);
            }
        }

        private static void RestoreWindBed()
        {
            WeatherDef dark = DefDatabase<WeatherDef>.GetNamedSilentFail(RM_MapComponent_Dark.DarkWeather);
            SoundDef wind = DefDatabase<SoundDef>.GetNamedSilentFail("Ambient_Wind_Fog");
            if (dark == null || wind == null) return;
            if (dark.ambientSounds == null) dark.ambientSounds = new List<SoundDef>();
            if (!dark.ambientSounds.Contains(wind)) dark.ambientSounds.Add(wind);
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // ABYSS_FOLD_LAMP_BUILD_1 -- the lane of clear air out of a lit fold-lamp's throat.
    // A per-cell clearance (0 = untouched, 1 = fully clear) that RM_MapComponent_Dark.DarknessAt multiplies
    // the Dark by. Rebuilt lazily at most every RebuildTicks; nothing is saved (lamps are re-read).
    // Shape: a lane, not a dome -- 3 wide at the throat, 5 wide in the middle, 3 wide at the far end,
    // LaneLength long, fading over its last cells, stopped by any wall (Filled cell) in its column.
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_FoldLanes : MapComponent
    {
        public const string LampDef = "RM_FoldLamp";
        public const int LaneLength = RM_DarkKernel.LaneLength;
        private const int RebuildTicks = 250;

        // The lane shape (3 / 5 / 3 wide, fading over its last cells, stopped by walls) and the touched-cell grid are in
        // RM_DarkKernel (RM_AbyssKernel.cs), offline-fuzzed.
        private RM_DarkKernel.ClearGrid grid;
        private int lastBuild = -999999;
        private ThingDef lampDef;

        public RM_MapComponent_FoldLanes(Map map) : base(map) { }

        public static float ClearanceAt(Map map, IntVec3 c)
        {
            RM_MapComponent_FoldLanes comp = map?.GetComponent<RM_MapComponent_FoldLanes>();
            return comp == null ? 0f : comp.Get(c);
        }

        public int LitLampCount { get; private set; }

        private float Get(IntVec3 c)
        {
            int now = Find.TickManager.TicksGame;
            if (now - lastBuild >= RebuildTicks || now < lastBuild) Rebuild(now);
            if (grid == null || grid.touched.Count == 0 || !c.InBounds(map)) return 0f;
            return grid.clear[map.cellIndices.CellToIndex(c)];
        }

        public void Rebuild(int now)
        {
            lastBuild = now;
            if (grid == null) grid = new RM_DarkKernel.ClearGrid(map.cellIndices.NumGridCells);
            grid.Reset();
            LitLampCount = 0;
            if (!RM_AbyssSettings.foldLaneEnabled) return;
            if (lampDef == null) lampDef = DefDatabase<ThingDef>.GetNamedSilentFail(LampDef);
            if (lampDef == null) return;
            List<Thing> lamps = map.listerThings.ThingsOfDef(lampDef);
            for (int i = 0; i < lamps.Count; i++)
            {
                CompGlower g = lamps[i].TryGetComp<CompGlower>();
                if (g == null || !g.Glows) continue;
                LitLampCount++;
                Lay(lamps[i].Position, lamps[i].Rotation);
            }
        }

        private void Lay(IntVec3 origin, Rot4 rot)
        {
            IntVec3 fwd = rot.FacingCell;
            IntVec3 side = rot.Rotated(RotationDirection.Clockwise).FacingCell;
            RM_DarkKernel.LayLane(origin.x, origin.z, fwd.x, fwd.z, side.x, side.z,
                (x, z) => { var c = new IntVec3(x, 0, z); return !c.InBounds(map) || c.Filled(map); },
                (x, z, v) => Mark(new IntVec3(x, 0, z), v));
        }

        private void Mark(IntVec3 c, float v)
        {
            if (!c.InBounds(map)) return;
            grid.Mark(map.cellIndices.CellToIndex(c), v);
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // ABYSS_FOLD_LAMP_BUILD_1 -- discovery. "The first time a pawn watches heat open a clear pocket, a letter
    // fires and unlocks the research." Called from RM_MapComponent_Dark's pawn pass (Abyss, Dark present).
    // ════════════════════════════════════════════════════════════════════
    public static class RM_HeatFoldingDiscovery
    {
        public const string ObservationProject = "RM_DarkFoldsFromWarmth";
        private const float HeatRadius = 8f;
        private const float PocketMaxDarkness = 0.25f;
        private const float AmbientMinDarkness = 0.6f;

        public static ResearchProjectDef Observation => DefDatabase<ResearchProjectDef>.GetNamedSilentFail(ObservationProject);

        public static bool Discovered
        {
            get { ResearchProjectDef p = Observation; return p == null || p.IsFinished; }
        }

        /// <summary>Darkness the open air would have at the map's outdoor temperature, with no pocket noise.</summary>
        public static float AmbientDarkness(Map map)
        {
            return RM_MapComponent_Dark.DarknessForTemperature(map.mapTemperature.OutdoorTemp);
        }

        public static void Check(Map map)
        {
            if (!RM_AbyssSettings.foldDiscoveryByWatching || Discovered) return;
            if (AmbientDarkness(map) < AmbientMinDarkness) return;
            IReadOnlyList<Pawn> pawns = map.mapPawns.FreeColonistsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.Downed || !p.Awake()) continue;
                if (RM_MapComponent_Dark.DarknessAt(map, p.Position) > PocketMaxDarkness) continue;
                Thing heat = VisibleHeat(map, p);
                if (heat == null) continue;
                Discover(p, heat);
                return;
            }
        }

        public static Thing VisibleHeat(Map map, Pawn p)
        {
            List<Building> bld = map.listerBuildings.allBuildingsColonist;
            for (int i = 0; i < bld.Count; i++)
            {
                Building b = bld[i];
                if (!b.Position.InHorDistOf(p.Position, HeatRadius)) continue;
                CompHeatPusher h = b.TryGetComp<CompHeatPusher>();
                if (h == null || !h.ShouldPushHeatNow) continue;
                if (!GenSight.LineOfSight(p.Position, b.Position, map, skipFirstCell: true)) continue;
                return b;
            }
            return null;
        }

        public static void Discover(Pawn p, Thing heat)
        {
            ResearchProjectDef obs = Observation;
            if (obs == null || obs.IsFinished) return;
            Find.ResearchManager.FinishProject(obs, doCompletionDialog: false, researcher: p, doCompletionLetter: false);
            ResearchProjectDef next = DefDatabase<ResearchProjectDef>.GetNamedSilentFail("RM_HeatFolding");
            Find.LetterStack.ReceiveLetter("The Dark folds back from warmth",
                p.LabelShort + " has been standing in clear air beside " + heat.LabelShort + " while the country all around is blind. "
                + "The Dark is thinner where it is warm: it folds back from heat like frost from a breath.\n\n"
                + "Shape the warmth, and you could shape where the air stays clear. "
                + (next != null ? "The research project '" + next.LabelCap + "' is now open." : ""),
                LetterDefOf.PositiveEvent, new LookTargets(new List<TargetInfo> { new TargetInfo(p), new TargetInfo(heat) }));
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // foldDiscoveryByWatching OFF: the observation is granted silently on every game start/load, so heat-folding
    // is an ordinary bench project. (GameComponents are instantiated for every subclass by reflection.)
    // ════════════════════════════════════════════════════════════════════
    public class RM_AbyssGameComponent : GameComponent
    {
        public RM_AbyssGameComponent(Game game) { }

        public override void FinalizeInit()
        {
            if (RM_AbyssSettings.foldDiscoveryByWatching) return;
            ResearchProjectDef obs = RM_HeatFoldingDiscovery.Observation;
            if (obs != null && !obs.IsFinished)
                Find.ResearchManager.FinishProject(obs, doCompletionDialog: false, researcher: null, doCompletionLetter: false);
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // Proof hooks for validation.py (static_call): a deterministic STATE read, no screenshots.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_AbyssLightProof
    {
        /// <summary>Clearance along a fold-lamp's lane: at the throat+3, at +12, and one cell behind it.</summary>
        public static string ProofLane()
        {
            Map map = Find.CurrentMap;
            if (map == null) return "no map";
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(RM_MapComponent_FoldLanes.LampDef);
            List<Thing> lamps = def == null ? null : map.listerThings.ThingsOfDef(def);
            if (lamps == null || lamps.Count == 0) return "no fold-lamp on map";
            Thing l = lamps[0];
            map.GetComponent<RM_MapComponent_FoldLanes>()?.Rebuild(Find.TickManager.TicksGame);
            IntVec3 f = l.Rotation.FacingCell;
            return "lit=" + (l.TryGetComp<CompGlower>()?.Glows ?? false)
                + " near=" + RM_MapComponent_FoldLanes.ClearanceAt(map, l.Position + f * 3).ToString("0.00")
                + " far=" + RM_MapComponent_FoldLanes.ClearanceAt(map, l.Position + f * 12).ToString("0.00")
                + " behind=" + RM_MapComponent_FoldLanes.ClearanceAt(map, l.Position - f * 2).ToString("0.00");
        }

        /// <summary>Observation state and whether a colonist would discover it right now.</summary>
        public static string ProofDiscovery()
        {
            Map map = Find.CurrentMap;
            if (map == null) return "no map";
            return "discovered=" + RM_HeatFoldingDiscovery.Discovered
                + " ambientDark=" + RM_HeatFoldingDiscovery.AmbientDarkness(map).ToString("0.00")
                + " darkPresent=" + RM_MapComponent_Dark.DarkPresent(map);
        }

        /// <summary>Wickwood: overlight radius in force and whether the Abyss still lists it wild.</summary>
        public static string ProofWickwood()
        {
            ThingDef w = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Wickwood");
            BiomeDef b = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Abyss");
            if (w == null) return "no RM_Wickwood";
            return "overlight=" + (w.GetCompProperties<CompProperties_Glower>()?.overlightRadius ?? -1f).ToString("0.0")
                + " wildInAbyss=" + (b != null && b.CommonalityOfPlant(w) > 0f);
        }
    }
}
