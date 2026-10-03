using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimMandrake.CreatureBehaviors;
using RimMandrake.EnvironmentalHazards;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_PRECIOUS_CAVES_1 — the rare rock, and the precious cave under
    // almost every one. Owner, typed, volley turn 2: "The rare rock should be
    // celebrated and almost always featuring a precious cave."
    // Design: stillsand_turn3_development_2026-09-30.md §2.6; turn-4 rulings in
    // stillsand_bedazzle_cast_2026-09-30.md §0 (sinkholes OUT: every cave is in rock).
    //
    // TWO GenSteps, wired onto RM_Stillsand through BiomeDef.extraGenSteps
    // (Patches/RM_PreciousCaves_BiomeGenSteps.xml) — MapGenerator.GenerateMap
    // concatenates a biome's extraGenSteps into every map of that biome
    // (MEASURED, RimSage, Verse/MapGenerator.cs).
    //   1. RM_GenStep_PreciousCaveCarve, order 245: after RocksFromGrid (200),
    //      Terrain (210) and RemoveTinyIslands (240), before every structure,
    //      ruin, player-start and scatter step. Shapes the largest natural-rock
    //      outcrop as a yardang laid along the wind, carves one roofed chamber at
    //      its deepest point and a tunnel out of its SHADE face; on a rockless
    //      map, sometimes seats one small tor first.
    //   2. RM_GenStep_PreciousCaveContents, order 965: after Plants (900), before
    //      Animals (1200) — rolls the precious table (RM_PreciousCaveDef, one roll
    //      per cave, weights from Mod Settings) and runs the row's elements.
    //
    // WHY NOT THE VANILLA/ODYSSEY CAVE MUTATORS (spec 1: "evaluate first").
    // MEASURED via RimSage: Caves / Cavern / UndergroundCave are TileMutatorDefs
    // whose workers (TileMutatorWorker_Caves → MapGenCavesUtility.GenerateCaves)
    // carve noise-steered tunnel networks through every elevation>0.7 cell in
    // GeneratePostElevationFertility. They are a property of a world TILE (the
    // planet is painted once, at the end — CLAUDE.md), they cut networks rather
    // than one chamber, nothing about them knows a sun, and Cavern requires
    // Mountainous hilliness, which a Stillsand outcrop is not. So none fits
    // "one chamber off the shade face, sized to the rock"; this step owns it.
    //
    // WHY THE ROWS REUSE RM_SetPieceElement BUT NOT RM_GenStep_PlacedSetPieces.
    // The shipped scatterer (EnvironmentalHazards) picks its own random scatter
    // sites; a cave's site is the carved chamber, decided here. What is reused is
    // its content vocabulary — every row's <elements> are RM_SetPieceElement
    // subclasses, so the shipped RM_SetPieceElement_SpawnMarker /
    // RM_SetPieceElement_AnchoredPawn drop straight into a row, and the cave
    // elements below also work inside a plain RM_GenStep_PlacedSetPieces (they
    // fall back to cells around the scatter site when no cave context is set).
    // The RSW / Utinni rows (krayt den, sarlacc seep, debt cave) arrive as
    // RM_PreciousCaveDefs in their own tiers' mods, by def, never by edit here.
    // ════════════════════════════════════════════════════════════════════

    public enum RM_CavePlace
    {
        back,
        centre,
        mouth,
        any,
    }

    /// <summary>One row of the precious table.</summary>
    public class RM_PreciousCaveDef : Def
    {
        /// <summary>Default table weight; Mod Settings may override per row.</summary>
        public float weight = 1f;

        /// <summary>Which naming tier owns the row (RM / RSW / RUT). Documentation only.</summary>
        public string tier = "RM";

        public List<RM_SetPieceElement> elements = new List<RM_SetPieceElement>();

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (weight < 0f)
            {
                yield return "weight is negative";
            }
            if (elements == null)
            {
                yield return "elements is null";
            }
        }
    }

    /// <summary>The cave being furnished. Set by RM_GenStep_PreciousCaveContents
    /// for the duration of one row's elements; null otherwise.</summary>
    public class RM_PreciousCaveContext
    {
        public static RM_PreciousCaveContext Current;

        public Map map;
        public List<IntVec3> floor = new List<IntVec3>();
        public IntVec3 centre;
        public IntVec3 mouth;
        public ThingDef rock;

        /// <summary>A floor cell for an element. back = farthest third from the
        /// mouth, mouth = nearest third, centre = nearest third to the chamber
        /// centre, any = anywhere. Invalid when no floor cell passes `ok`.</summary>
        public IntVec3 Pick(RM_CavePlace where, Predicate<IntVec3> ok)
        {
            List<IntVec3> cands = floor.Where(c => ok == null || ok(c)).ToList();
            if (cands.Count == 0)
            {
                return IntVec3.Invalid;
            }
            switch (where)
            {
                case RM_CavePlace.back:
                    cands.SortByDescending(c => c.DistanceToSquared(mouth));
                    break;
                case RM_CavePlace.mouth:
                    cands.SortBy(c => c.DistanceToSquared(mouth));
                    break;
                case RM_CavePlace.centre:
                    cands.SortBy(c => c.DistanceToSquared(centre));
                    break;
                default:
                    return cands.RandomElement();
            }
            int take = Math.Max(1, cands.Count / 3);
            return cands[Rand.Range(0, take)];
        }

        /// <summary>Cave context, or a stand-in built from the cells around `loc`
        /// when an element runs outside a cave (e.g. in RM_GenStep_PlacedSetPieces).</summary>
        public static RM_PreciousCaveContext For(IntVec3 loc, Map map)
        {
            if (Current != null && Current.map == map)
            {
                return Current;
            }
            RM_PreciousCaveContext ctx = new RM_PreciousCaveContext { map = map, centre = loc, mouth = loc };
            foreach (IntVec3 c in GenRadial.RadialCellsAround(loc, 3.9f, true))
            {
                if (c.InBounds(map) && c.Standable(map))
                {
                    ctx.floor.Add(c);
                }
            }
            return ctx;
        }

        public static bool FreeForItem(IntVec3 c, Map map)
        {
            return c.InBounds(map) && c.Standable(map) && c.GetEdifice(map) == null
                   && !c.GetThingList(map).Any(t => t.def.category == ThingCategory.Item
                                                    || t.def.category == ThingCategory.Building);
        }
    }

    // ── elements ───────────────────────────────────────────────────────────

    /// <summary>Paints a connected patch of terrain on the cave floor (the brine seep).</summary>
    public class RM_CaveElement_Terrain : RM_SetPieceElement
    {
        public TerrainDef terrain;
        public IntRange cells = new IntRange(4, 8);
        public RM_CavePlace place = RM_CavePlace.back;

        public override void SpawnAt(IntVec3 loc, Map map, GenStepParams parms)
        {
            if (terrain == null)
            {
                Log.Error("[Stillsand] RM_CaveElement_Terrain has no terrain configured.");
                return;
            }
            RM_PreciousCaveContext ctx = RM_PreciousCaveContext.For(loc, map);
            IntVec3 seed = ctx.Pick(place, c => c.GetEdifice(map) == null);
            if (!seed.IsValid)
            {
                return;
            }
            HashSet<IntVec3> floor = new HashSet<IntVec3>(ctx.floor);
            int want = cells.RandomInRange;
            Queue<IntVec3> q = new Queue<IntVec3>();
            HashSet<IntVec3> seen = new HashSet<IntVec3> { seed };
            q.Enqueue(seed);
            int painted = 0;
            while (q.Count > 0 && painted < want)
            {
                IntVec3 c = q.Dequeue();
                map.terrainGrid.SetTerrain(c, terrain);
                painted++;
                foreach (IntVec3 n in GenAdj.CardinalDirections.Select(d => c + d).InRandomOrder())
                {
                    if (floor.Contains(n) && seen.Add(n) && n.GetEdifice(map) == null)
                    {
                        q.Enqueue(n);
                    }
                }
            }
        }
    }

    /// <summary>Spawns things on the cave floor: item stacks, buildings, filth.
    /// `softThingDefs` names defs from mods that may be absent — the first loaded
    /// one is used and none-loaded spawns nothing (no cross-reference error).
    /// `rockChunk` spawns the outcrop's own chunk instead of `thing`.</summary>
    public class RM_CaveElement_Things : RM_SetPieceElement
    {
        public ThingDef thing;
        public List<string> softThingDefs;
        public bool rockChunk;
        public ThingDef stuff;
        public IntRange stackCount = new IntRange(1, 1);
        public IntRange stacks = new IntRange(1, 1);
        public RM_CavePlace place = RM_CavePlace.any;

        public override void SpawnAt(IntVec3 loc, Map map, GenStepParams parms)
        {
            RM_PreciousCaveContext ctx = RM_PreciousCaveContext.For(loc, map);
            ThingDef def = Resolve(ctx);
            if (def == null)
            {
                return;
            }
            int n = stacks.RandomInRange;
            for (int i = 0; i < n; i++)
            {
                if (def.IsFilth)
                {
                    IntVec3 fc = ctx.Pick(place, c => c.InBounds(map) && c.Standable(map));
                    if (fc.IsValid)
                    {
                        FilthMaker.TryMakeFilth(fc, map, def, Math.Max(1, stackCount.RandomInRange));
                    }
                    continue;
                }
                IntVec3 cell = ctx.Pick(place, c => RM_PreciousCaveContext.FreeForItem(c, map));
                if (!cell.IsValid)
                {
                    return;
                }
                ThingDef useStuff = def.MadeFromStuff ? (stuff ?? GenStuff.DefaultStuffFor(def)) : null;
                Thing t = ThingMaker.MakeThing(def, useStuff);
                if (def.stackLimit > 1)
                {
                    t.stackCount = Mathf.Clamp(stackCount.RandomInRange, 1, def.stackLimit);
                }
                GenSpawn.Spawn(t, cell, map);
            }
        }

        private ThingDef Resolve(RM_PreciousCaveContext ctx)
        {
            if (rockChunk)
            {
                return ctx.rock?.building?.mineableThing;
            }
            if (thing != null)
            {
                return thing;
            }
            if (softThingDefs != null)
            {
                for (int i = 0; i < softThingDefs.Count; i++)
                {
                    ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(softThingDefs[i]);
                    if (d != null)
                    {
                        return d;
                    }
                }
            }
            return null;
        }
    }

    /// <summary>Spawns wild animals (no faction) on the cave floor.</summary>
    public class RM_CaveElement_Pawns : RM_SetPieceElement
    {
        public PawnKindDef kind;
        public IntRange count = new IntRange(1, 1);
        public RM_CavePlace place = RM_CavePlace.back;

        public override void SpawnAt(IntVec3 loc, Map map, GenStepParams parms)
        {
            if (kind == null)
            {
                Log.Error("[Stillsand] RM_CaveElement_Pawns has no kind configured.");
                return;
            }
            RM_PreciousCaveContext ctx = RM_PreciousCaveContext.For(loc, map);
            int n = count.RandomInRange;
            for (int i = 0; i < n; i++)
            {
                IntVec3 cell = ctx.Pick(place, c => c.InBounds(map) && c.Standable(map) && c.GetFirstPawn(map) == null);
                if (!cell.IsValid)
                {
                    return;
                }
                Pawn pawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, null,
                    PawnGenerationContext.NonPlayer, forceGenerateNewPawn: true, canGeneratePawnRelations: false));
                GenSpawn.Spawn(pawn, cell, map);
            }
        }
    }

    // ── map component: the outcrop's record and the landing letter ────────

    public class RM_MapComponent_PreciousCave : MapComponent
    {
        // Saved: what the letter needs, so it can fire once the map is home.
        public bool hasOutcrop;
        public bool hasCave;
        public bool isTor;
        public bool letterSent;
        public string outcropLabel;
        public string compassWord;
        public string rowDefName;
        public IntVec3 lookCell = IntVec3.Invalid;

        // STILLSAND_CAVE_AS_PLACE_1: the cave floor, kept (it used to be mapgen-only) so the
        // preservation register can tell a cave cell later; and the things it has frozen.
        public List<IntVec3> caveCells = new List<IntVec3>();

        /// <summary>STILLSAND_EVENT_CREATURES_REMAINDER_1: set once the den quest clears the den.</summary>
        public bool denCleared;

        public List<Thing> frozenThings = new List<Thing>();

        // Mapgen-only hand-off from the carve step to the contents step.
        [Unsaved] public List<IntVec3> chamberFloor = new List<IntVec3>();
        [Unsaved] public IntVec3 chamberCentre = IntVec3.Invalid;
        [Unsaved] public IntVec3 mouthCell = IntVec3.Invalid;
        [Unsaved] public ThingDef rockDef;

        public RM_MapComponent_PreciousCave(Map map) : base(map)
        {
        }

        public static RM_MapComponent_PreciousCave For(Map map)
        {
            return map?.GetComponent<RM_MapComponent_PreciousCave>();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref hasOutcrop, "hasOutcrop");
            Scribe_Values.Look(ref hasCave, "hasCave");
            Scribe_Values.Look(ref isTor, "isTor");
            Scribe_Values.Look(ref letterSent, "letterSent");
            Scribe_Values.Look(ref outcropLabel, "outcropLabel");
            Scribe_Values.Look(ref compassWord, "compassWord");
            Scribe_Values.Look(ref rowDefName, "rowDefName");
            Scribe_Values.Look(ref lookCell, "lookCell", IntVec3.Invalid);
            Scribe_Values.Look(ref denCleared, "denCleared");
            Scribe_Collections.Look(ref caveCells, "caveCells", LookMode.Value);
            Scribe_Collections.Look(ref frozenThings, "frozenThings", LookMode.Reference);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                caveCells = caveCells ?? new List<IntVec3>();
                frozenThings = frozenThings ?? new List<Thing>();
                frozenThings.RemoveAll(t => t == null);
            }
        }

        public override void MapComponentTick()
        {
            if (hasCave && Find.TickManager.TicksGame % RM_CavePreservation.ScanInterval == 0)
            {
                RM_CavePreservation.Scan(this);
            }
            if (letterSent || !hasOutcrop || Find.TickManager.TicksGame % 120 != 0 || !map.IsPlayerHome)
            {
                return;
            }
            letterSent = true;
            Find.LetterStack.ReceiveLetter("Rock island", LetterText(), LetterDefOf.NeutralEvent,
                lookCell.IsValid ? new LookTargets(new TargetInfo(lookCell, map)) : LookTargets.Invalid);
        }

        /// <summary>A giant (body size 3 or more) that no one owns is inside the cave and the den has not
        /// been cleared: the cave is a den, not yet a precious cave, and preserves nothing.</summary>
        public bool DenHeld()
        {
            if (denCleared || !hasCave)
            {
                return false;
            }
            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (!p.Dead && p.Faction == null && p.RaceProps.Animal && p.BodySize >= 3f && caveCells.Contains(p.Position))
                {
                    return true;
                }
            }
            return false;
        }

        public string LetterText()
        {
            StringBuilder sb = new StringBuilder();
            string where = compassWord == "centre"
                ? "stands at the heart of the plain"
                : "stands to the " + compassWord;
            sb.Append("A rock island " + where + ": " + "the " + outcropLabel
                      + ", the one stone for a long way in any direction, laid along the wind like a hull.");
            if (isTor)
            {
                sb.Append(" It is small, and it is all there is.");
            }
            sb.Append("\n\nIts lee is the only real shade on the map.");
            if (hasCave)
            {
                sb.Append(" On that dark side, a mouth opens into the stone. The air inside is cool, and somewhere in the dark there is a drip.");
            }
            return sb.ToString();
        }
    }

    // ── genstep 1: the rock and the chamber ───────────────────────────────

    public class RM_GenStep_PreciousCaveCarve : GenStep
    {
        public int minOutcropCells = 24;
        public int maxShapeCells = 5000;
        public float yardangAspect = 2.6f;
        public float yardangTaper = 0.45f;
        public int minChamberRadius = 1;
        public int maxChamberRadius = 6;
        public IntRange torArea = new IntRange(45, 110);
        public int torEdgeMargin = 15;

        public override int SeedPart => 412907713;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_PreciousCaveSettings.genStepEnabled || map == null || map.IsPocketMap
                || (map.generatorDef?.isUnderground ?? false) || map.TileInfo == null || map.TileInfo.WaterCovered)
            {
                return;
            }
            RM_MapComponent_PreciousCave comp = RM_MapComponent_PreciousCave.For(map);
            if (comp == null)
            {
                return;
            }
            bool wasEnabled = map.regionAndRoomUpdater.Enabled;
            map.regionAndRoomUpdater.Enabled = false;
            try
            {
                Carve(map, comp);
            }
            catch (Exception e)
            {
                Log.Error("[Stillsand] precious cave carve failed, map keeps its rock as generated: " + e);
            }
            finally
            {
                map.regionAndRoomUpdater.Enabled = wasEnabled;
            }
        }

        private void Carve(Map map, RM_MapComponent_PreciousCave comp)
        {
            int w = map.Size.x;
            int h = map.Size.z;
            ShadowDirection(map, out double sdx, out double sdz, out string sunSource);

            List<int> outcrop = LargestOutcrop(map, w, h);
            bool tor = false;
            if (outcrop.Count < minOutcropCells)
            {
                if (!RM_PreciousCaveSettings.torEnabled || !Rand.Chance(RM_PreciousCaveSettings.torChance))
                {
                    Log.Message("[Stillsand] precious cave: no outcrop of " + minOutcropCells + "+ cells and no tor rolled; map stays rockless.");
                    return;
                }
                if (!SeatTor(map, w, h, sdx, sdz))
                {
                    Log.Message("[Stillsand] precious cave: rockless map, tor rolled but found no clear ground to seat it.");
                    return;
                }
                tor = true;
                outcrop = LargestOutcrop(map, w, h);
                if (outcrop.Count == 0)
                {
                    return;
                }
            }

            ThingDef rock = DominantRock(map, outcrop, w);
            bool shaped = false;
            if (!tor && RM_PreciousCaveSettings.yardangShapingEnabled && outcrop.Count <= maxShapeCells)
            {
                shaped = ShapeYardang(map, outcrop, w, h, rock, sdx, sdz);
                outcrop = LargestOutcrop(map, w, h);
            }

            bool[] rockGrid = RockGrid(map, w, h);
            int[] depth = RM_PreciousCaveGeometry.DepthMap(rockGrid, w, h);
            int centreIdx = RM_PreciousCaveGeometry.DeepestCell(outcrop, depth, w);
            if (centreIdx < 0)
            {
                return;
            }
            IntVec3 centroid = Centroid(outcrop, w);
            comp.hasOutcrop = true;
            comp.isTor = tor;
            comp.rockDef = rock;
            comp.outcropLabel = (rock?.label ?? "stone") + (tor ? " tor" : " yardang");
            comp.compassWord = RM_PreciousCaveGeometry.CompassWord(centroid.x - w / 2.0, centroid.z - h / 2.0);
            if (Math.Abs(centroid.x - w / 2.0) < w * 0.08 && Math.Abs(centroid.z - h / 2.0) < h * 0.08)
            {
                comp.compassWord = "centre";
            }
            comp.lookCell = centroid;

            int r = RM_PreciousCaveGeometry.ChamberRadius(outcrop.Count, depth[centreIdx], minChamberRadius, maxChamberRadius);
            IntVec3 centre = new IntVec3(centreIdx % w, 0, centreIdx / w);
            string shapeNote = tor ? "tor" : (shaped ? "yardang-shaped" : "as generated");
            if (r <= 0)
            {
                Log.Message("[Stillsand] precious cave: " + comp.outcropLabel + " (" + outcrop.Count + " cells, " + shapeNote
                            + ") is too thin for a chamber; rock kept, no cave.");
                MapGenerator.UsedRects.Add(CellRect.FromCellList(outcrop.Select(i => new IntVec3(i % w, 0, i / w))));
                return;
            }

            List<int> tunnel = new List<int>();
            double angle = RM_PreciousCaveGeometry.ShadeMouth(rockGrid, w, h, centre.x, centre.z, sdx, sdz, tunnel, out int exitIdx);
            if (double.IsNaN(angle))
            {
                Log.Message("[Stillsand] precious cave: no shade-side way out of " + comp.outcropLabel + "; rock kept, no cave.");
                return;
            }

            ThingDef floorRock = rock;
            TerrainDef floor = floorRock?.building?.naturalTerrain;
            HashSet<IntVec3> chamber = new HashSet<IntVec3>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(centre, r + 0.5f, true))
            {
                if (c.InBounds(map) && (c.DistanceTo(centre) <= r - 0.5f || Rand.Chance(0.55f)))
                {
                    chamber.Add(c);
                }
            }
            IntVec3 perp = new IntVec3((int)Math.Round(-sdz), 0, (int)Math.Round(sdx));
            List<IntVec3> tunnelCells = new List<IntVec3>();
            foreach (int ti in tunnel)
            {
                IntVec3 c = new IntVec3(ti % w, 0, ti / w);
                tunnelCells.Add(c);
                if (r >= 3)
                {
                    IntVec3 side = c + perp;
                    if (side.InBounds(map) && side.GetEdifice(map) is Building b && b.def.building.isNaturalRock)
                    {
                        tunnelCells.Add(side);
                    }
                }
            }

            foreach (IntVec3 c in chamber.Concat(tunnelCells))
            {
                Building ed = c.GetEdifice(map);
                if (ed != null && ed.def.building != null && ed.def.building.isNaturalRock)
                {
                    ed.Destroy(DestroyMode.Vanish);
                }
                if (floor != null && !c.GetTerrain(map).IsWater)
                {
                    map.terrainGrid.SetTerrain(c, floor);
                }
                map.roofGrid.SetRoof(c, RoofDefOf.RoofRockThick);
            }

            IntVec3 exit = new IntVec3(exitIdx % w, 0, exitIdx / w);
            comp.hasCave = true;
            comp.chamberCentre = centre;
            comp.mouthCell = exit;
            comp.chamberFloor = chamber.Where(c => c.InBounds(map)).ToList();
            comp.lookCell = exit;
            MapGenerator.UsedRects.Add(CellRect.FromCellList(outcrop.Select(i => new IntVec3(i % w, 0, i / w))));

            double mdx = exit.x - centre.x;
            double mdz = exit.z - centre.z;
            double dot = (mdx * sdx + mdz * sdz) / Math.Max(1e-6, Math.Sqrt(mdx * mdx + mdz * mdz));
            Log.Message("[Stillsand] precious cave: " + comp.outcropLabel + " " + comp.compassWord + " (" + outcrop.Count
                        + " cells, " + shapeNote + "), chamber r=" + r + " at " + centre + ", mouth " + exit
                        + " (" + angle.ToString("0") + " deg off the shadow line, facing-away dot " + dot.ToString("0.00")
                        + ", sun from " + sunSource + ").");
        }

        // The tile's sun bearing (§2.7): the pinned-sun geometry when the biome
        // carries RM_PinnedSunExtension (Stillsand does), else the sun-heat
        // extension's substellar point, else a random bearing. Read from the
        // biome's data, not the Mod Settings sky toggle: where the sun stands is
        // a fact of the tile whether or not the sky is pinned.
        private static void ShadowDirection(Map map, out double dx, out double dz, out string source)
        {
            RM_MapComponent_PinnedSun pin = RM_MapComponent_PinnedSun.For(map);
            if (pin != null && pin.Extension != null && map.Tile.Valid)
            {
                Vector2 v = pin.ShadowDirection;
                dx = v.x;
                dz = v.y;
                source = "pinned sun";
                return;
            }
            RM_SunHeatExtension heat = map.Biome?.GetModExtension<RM_SunHeatExtension>();
            if (heat != null && map.Tile.Valid && Find.WorldGrid != null)
            {
                Vector2 ll = Find.WorldGrid.LongLatOf(map.Tile);
                RM_MapComponent_PinnedSun.SunGeometry(ll.y, ll.x, heat.substellarLatitude, heat.substellarLongitude,
                    out float bearing, out float _);
                float b = bearing * Mathf.Deg2Rad;
                dx = -Mathf.Sin(b);
                dz = -Mathf.Cos(b);
                source = "substellar point";
                return;
            }
            float a = Rand.Range(0f, 360f) * Mathf.Deg2Rad;
            dx = Mathf.Sin(a);
            dz = Mathf.Cos(a);
            source = "random (biome has no sun data)";
        }

        private static bool IsNaturalRock(Building b)
        {
            return b != null && b.def.building != null && b.def.building.isNaturalRock;
        }

        private static bool[] RockGrid(Map map, int w, int h)
        {
            bool[] grid = new bool[w * h];
            for (int z = 0; z < h; z++)
            {
                for (int x = 0; x < w; x++)
                {
                    grid[z * w + x] = IsNaturalRock(new IntVec3(x, 0, z).GetEdifice(map));
                }
            }
            return grid;
        }

        private static List<int> LargestOutcrop(Map map, int w, int h)
        {
            bool[] grid = RockGrid(map, w, h);
            bool[] seen = new bool[w * h];
            List<int> best = new List<int>();
            List<int> cur = new List<int>();
            Queue<int> q = new Queue<int>();
            for (int start = 0; start < grid.Length; start++)
            {
                if (!grid[start] || seen[start])
                {
                    continue;
                }
                cur.Clear();
                seen[start] = true;
                q.Enqueue(start);
                while (q.Count > 0)
                {
                    int i = q.Dequeue();
                    cur.Add(i);
                    int x = i % w;
                    int z = i / w;
                    if (x > 0) Visit(i - 1);
                    if (x < w - 1) Visit(i + 1);
                    if (z > 0) Visit(i - w);
                    if (z < h - 1) Visit(i + w);
                }
                if (cur.Count > best.Count)
                {
                    best = new List<int>(cur);
                }
            }
            return best;

            void Visit(int j)
            {
                if (grid[j] && !seen[j])
                {
                    seen[j] = true;
                    q.Enqueue(j);
                }
            }
        }

        private static IntVec3 Centroid(List<int> cells, int w)
        {
            double sx = 0, sz = 0;
            foreach (int i in cells)
            {
                sx += i % w;
                sz += i / w;
            }
            return new IntVec3((int)Math.Round(sx / cells.Count), 0, (int)Math.Round(sz / cells.Count));
        }

        private static ThingDef DominantRock(Map map, List<int> cells, int w)
        {
            Dictionary<ThingDef, int> counts = new Dictionary<ThingDef, int>();
            foreach (int i in cells)
            {
                Building b = new IntVec3(i % w, 0, i / w).GetEdifice(map);
                if (b != null && b.def.IsNonResourceNaturalRock)
                {
                    counts[b.def] = counts.TryGetValue(b.def, out int n) ? n + 1 : 1;
                }
            }
            if (counts.Count > 0)
            {
                return counts.OrderByDescending(kv => kv.Value).First().Key;
            }
            return Find.World.NaturalRockTypesIn(map.Tile).RandomElementWithFallback();
        }

        private bool ShapeYardang(Map map, List<int> outcrop, int w, int h, ThingDef rock, double ux, double uz)
        {
            if (rock == null)
            {
                return false;
            }
            IntVec3 c0 = Centroid(outcrop, w);
            RM_PreciousCaveGeometry.YardangAxes(outcrop.Count, yardangAspect, out double a, out double b);
            HashSet<int> inRock = new HashSet<int>(outcrop);
            int trimmed = 0, filled = 0;
            int reach = (int)Math.Ceiling(a) + 1;
            for (int z = Math.Max(0, c0.z - reach); z <= Math.Min(h - 1, c0.z + reach); z++)
            {
                for (int x = Math.Max(0, c0.x - reach); x <= Math.Min(w - 1, c0.x + reach); x++)
                {
                    double dx = x - c0.x;
                    double dz = z - c0.z;
                    double du = dx * ux + dz * uz;
                    double dv = -dx * uz + dz * ux;
                    if (!RM_PreciousCaveGeometry.InYardang(du, dv, a, b, yardangTaper))
                    {
                        continue;
                    }
                    int i = z * w + x;
                    if (inRock.Remove(i))
                    {
                        continue; // already rock and inside: keep
                    }
                    IntVec3 c = new IntVec3(x, 0, z);
                    if (x < 2 || z < 2 || x > w - 3 || z > h - 3 || c.GetTerrain(map).IsWater
                        || c.GetEdifice(map) != null || MapGenerator.UsedRects.Any(rr => rr.Contains(c)))
                    {
                        continue;
                    }
                    GenSpawn.Spawn(rock, c, map);
                    if (rock.building?.naturalTerrain != null)
                    {
                        map.terrainGrid.SetTerrain(c, rock.building.naturalTerrain);
                    }
                    filled++;
                }
            }
            // Whatever of the old outcrop is left in inRock lies outside the yardang.
            foreach (int i in inRock)
            {
                IntVec3 c = new IntVec3(i % w, 0, i / w);
                Building ed = c.GetEdifice(map);
                if (!IsNaturalRock(ed))
                {
                    continue;
                }
                ed.Destroy(DestroyMode.Vanish);
                map.roofGrid.SetRoof(c, null);
                TerrainDef open = OpenGroundNear(map, c);
                if (open != null)
                {
                    map.terrainGrid.SetTerrain(c, open);
                }
                trimmed++;
            }
            return filled > 0 || trimmed > 0;
        }

        private static TerrainDef OpenGroundNear(Map map, IntVec3 c)
        {
            for (int radius = 2; radius <= 12; radius += 2)
            {
                foreach (IntVec3 n in GenRadial.RadialCellsAround(c, radius, false))
                {
                    if (n.InBounds(map) && n.GetEdifice(map) == null && !n.GetTerrain(map).IsWater)
                    {
                        return n.GetTerrain(map);
                    }
                }
            }
            return null;
        }

        private bool SeatTor(Map map, int w, int h, double ux, double uz)
        {
            ThingDef rock = Find.World.NaturalRockTypesIn(map.Tile).Where(d => d.IsNonResourceNaturalRock).RandomElementWithFallback();
            if (rock == null)
            {
                return false;
            }
            int area = torArea.RandomInRange;
            RM_PreciousCaveGeometry.YardangAxes(area, yardangAspect, out double a, out double b);
            int reach = (int)Math.Ceiling(a) + 1;
            int margin = Math.Max(torEdgeMargin, reach + 3);
            if (w - 2 * margin < 1 || h - 2 * margin < 1)
            {
                return false;
            }
            for (int attempt = 0; attempt < 40; attempt++)
            {
                IntVec3 c0 = new IntVec3(Rand.Range(margin, w - margin), 0, Rand.Range(margin, h - margin));
                List<IntVec3> cells = new List<IntVec3>();
                bool ok = true;
                for (int z = c0.z - reach; z <= c0.z + reach && ok; z++)
                {
                    for (int x = c0.x - reach; x <= c0.x + reach; x++)
                    {
                        double dx = x - c0.x;
                        double dz = z - c0.z;
                        if (!RM_PreciousCaveGeometry.InYardang(dx * ux + dz * uz, -dx * uz + dz * ux, a, b, yardangTaper))
                        {
                            continue;
                        }
                        IntVec3 c = new IntVec3(x, 0, z);
                        if (!c.InBounds(map) || c.GetTerrain(map).IsWater || c.GetEdifice(map) != null
                            || MapGenerator.UsedRects.Any(rr => rr.Contains(c)))
                        {
                            ok = false;
                            break;
                        }
                        cells.Add(c);
                    }
                }
                if (!ok || cells.Count < minOutcropCells)
                {
                    continue;
                }
                foreach (IntVec3 c in cells)
                {
                    GenSpawn.Spawn(rock, c, map);
                    if (rock.building?.naturalTerrain != null)
                    {
                        map.terrainGrid.SetTerrain(c, rock.building.naturalTerrain);
                    }
                }
                return true;
            }
            return false;
        }
    }

    // ── genstep 2: the precious table ─────────────────────────────────────

    public class RM_GenStep_PreciousCaveContents : GenStep
    {
        public override int SeedPart => 690331517;

        public override void Generate(Map map, GenStepParams parms)
        {
            RM_MapComponent_PreciousCave comp = RM_MapComponent_PreciousCave.For(map);
            if (comp == null || !comp.hasCave || comp.chamberFloor.NullOrEmpty() || !RM_PreciousCaveSettings.genStepEnabled)
            {
                return;
            }
            comp.caveCells = new List<IntVec3>(comp.chamberFloor);
            List<RM_PreciousCaveDef> rows = DefDatabase<RM_PreciousCaveDef>.AllDefsListForReading
                .Where(RM_PreciousCaveSettings.RowEnabled).ToList();
            List<double> weights = rows.Select(d => (double)Math.Max(0f, RM_PreciousCaveSettings.RowWeight(d))).ToList();
            int pick = RM_PreciousCaveGeometry.WeightedPick(weights, Rand.Value);
            string table = string.Join(", ", rows.Select((d, i) => d.defName + "=" + weights[i].ToString("0.##")));
            if (pick < 0)
            {
                Log.Message("[Stillsand] precious cave roll: no row enabled with weight > 0 [" + table + "]; the cave stays bare.");
                RM_CavePlaceUtil.PlaceDrip(map, comp);
                return;
            }
            RM_PreciousCaveDef row = rows[pick];
            comp.rowDefName = row.defName;
            Log.Message("[Stillsand] precious cave roll: " + row.defName + " (" + row.tier + ") in the "
                        + comp.outcropLabel + " at " + comp.chamberCentre + " [" + table + "]");

            RM_PreciousCaveContext.Current = new RM_PreciousCaveContext
            {
                map = map,
                floor = comp.chamberFloor,
                centre = comp.chamberCentre,
                mouth = comp.mouthCell,
                rock = comp.rockDef,
            };
            try
            {
                foreach (RM_SetPieceElement el in row.elements)
                {
                    try
                    {
                        el?.SpawnAt(comp.chamberCentre, map, parms);
                    }
                    catch (Exception e)
                    {
                        Log.Error("[Stillsand] precious cave row " + row.defName + ": element " + el?.GetType().Name + " failed: " + e);
                    }
                }
            }
            finally
            {
                RM_PreciousCaveContext.Current = null;
            }
            RM_CavePlaceUtil.PlaceDrip(map, comp);
        }
    }
}
