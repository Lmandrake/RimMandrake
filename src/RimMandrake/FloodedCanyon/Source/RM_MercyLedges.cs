using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FloodedCanyon
{
    // ════════════════════════════════════════════════════════════════════
    // LEDGES OF MERCY — the physical half (CRACKEDLANDS_LEDGES_OF_MERCY_1).
    //
    // Form, decision taken by question card 2026-10-08: the ledge is CUT
    // INTO THE CLIFF FACE — a structure placed on cliff cells. Built as our
    // own map-generation step (no KCSG / framework dependency: this mod is
    // RM tier and standalone), on the same wall-face rule RM_FossilStrata
    // uses:
    //
    //   * A ledge is a pocket carved into a natural-rock face: up to 3 wide
    //     and 2 deep, opening onto walkable floor. The carved cells get the
    //     rock's smoothed floor and an RM_MercyLedge on each. RM_MercyLedge
    //     carries RM_RefugeLedgeExtension, so RM_MapComponent_LedgeRefuge
    //     treats every ledge cell as refuge and the flood never takes one.
    //   * One RM_MercyCarving (worn figures + an inscription) is cut into the
    //     pocket's back or side wall. A humanlike pawn that comes within
    //     sight of it gains RM_ReadMercyCarving once, ever, per carving.
    //   * One RM_ChimeLineAnchor is set in a side wall of each ledge, and as
    //     many again on other high faces across the map. They carry
    //     RM_ChimeAnchorExtension, so the flood's staged chimes toll from
    //     them (RM_MapComponent_CanyonFlood.ChimeCell -> NearestAnchorTo).
    //
    // Biased HIGH on the generator's elevation grid (fossils go low; ledges
    // go high). Only ever replaces natural, non-resource rock, so it never
    // touches a vein, a building or a seam already placed.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_MercyLedges
    {
        // PROVISIONAL (numbers ruling 2026-10-03, tuned live later):
        //   LedgesPer10k 0.5 — a 250x250 map (62,500 cells) asks for ~3.
        //   MinLedges 2 / MaxLedges 6 — clamp on that ask.
        //   MinLedgeSpacing 30 cells between ledge mouths.
        //   MinAnchorSpacing 20 cells between free-standing anchors.
        //   EdgeMargin 5 — never carve within 5 cells of the map edge.
        public const float LedgesPer10k = 0.5f;
        public const int MinLedges = 2;
        public const int MaxLedges = 6;
        public const int MinLedgeSpacing = 30;
        public const int MinAnchorSpacing = 20;
        public const int EdgeMargin = 5;

        public sealed class Result
        {
            public int ledges;
            public int ledgeCells;
            public int carvings;
            public int anchors;
        }

        public static bool IsCarvableRock(IntVec3 c, Map map)
        {
            if (!c.InBounds(map))
            {
                return false;
            }
            Building ed = c.GetEdifice(map);
            return ed != null && ed.def.building != null && ed.def.building.isNaturalRock && !ed.def.building.isResourceRock;
        }

        private static bool IsOpenFloor(IntVec3 c, Map map)
        {
            if (!c.InBounds(map) || c.GetEdifice(map) != null || !c.Walkable(map))
            {
                return false;
            }
            TerrainDef t = map.terrainGrid.TerrainAt(c);
            return t != null && !t.IsWater;
        }

        // A face cell with the direction INTO the rock (away from its open
        // walkable neighbour), or false.
        private static bool FaceInto(IntVec3 c, Map map, out IntVec3 into)
        {
            into = IntVec3.Invalid;
            if (c.x < EdgeMargin || c.z < EdgeMargin || c.x >= map.Size.x - EdgeMargin || c.z >= map.Size.z - EdgeMargin)
            {
                return false;
            }
            if (!IsCarvableRock(c, map))
            {
                return false;
            }
            for (int i = 0; i < 4; i++)
            {
                IntVec3 dir = GenAdj.CardinalDirections[i];
                if (IsOpenFloor(c + dir, map))
                {
                    into = IntVec3.Zero - dir;
                    return true;
                }
            }
            return false;
        }

        public static Result Generate(Map map, MapGenFloatGrid elevation)
        {
            Result res = new Result();
            ThingDef ledgeDef = RM_FloodedCanyonDefOf.RM_MercyLedge;
            if (ledgeDef == null)
            {
                return res;
            }

            List<IntVec3> faces = new List<IntVec3>();
            foreach (IntVec3 c in map.AllCells)
            {
                if (FaceInto(c, map, out _))
                {
                    faces.Add(c);
                }
            }
            if (faces.Count == 0)
            {
                return res;
            }

            System.Func<IntVec3, float> highWeight = c =>
            {
                if (elevation == null)
                {
                    return 1f;
                }
                return 0.15f + Mathf.InverseLerp(0.7f, 1.05f, elevation[c]);
            };

            int want = Mathf.Clamp(GenMath.RoundRandom(map.Area / 10000f * LedgesPer10k), MinLedges, MaxLedges);
            List<IntVec3> mouths = new List<IntVec3>();
            List<IntVec3> anchors = new List<IntVec3>();
            int tries = 0;
            while (res.ledges < want && tries < want * 40)
            {
                tries++;
                if (!faces.TryRandomElementByWeight(highWeight, out IntVec3 mouth))
                {
                    break;
                }
                if (!FaceInto(mouth, map, out IntVec3 into) || TooClose(mouth, mouths, MinLedgeSpacing))
                {
                    continue;
                }
                if (CarveLedge(map, mouth, into, ledgeDef, res, anchors))
                {
                    mouths.Add(mouth);
                }
            }

            // Free-standing anchors across the canyon: as many again as ledges.
            ThingDef anchorDef = RM_FloodedCanyonDefOf.RM_ChimeLineAnchor;
            int extra = res.ledges;
            tries = 0;
            while (extra > 0 && anchorDef != null && tries < 200)
            {
                tries++;
                if (!faces.TryRandomElementByWeight(highWeight, out IntVec3 c) || !IsCarvableRock(c, map) || TooClose(c, anchors, MinAnchorSpacing))
                {
                    continue;
                }
                if (Replace(map, c, anchorDef))
                {
                    anchors.Add(c);
                    res.anchors++;
                    extra--;
                }
            }
            return res;
        }

        private static bool TooClose(IntVec3 c, List<IntVec3> others, int spacing)
        {
            for (int i = 0; i < others.Count; i++)
            {
                if (c.InHorDistOf(others[i], spacing))
                {
                    return true;
                }
            }
            return false;
        }

        // Pocket: the mouth, its two lateral neighbours, and the row behind.
        private static bool CarveLedge(Map map, IntVec3 mouth, IntVec3 into, ThingDef ledgeDef, Result res, List<IntVec3> anchors)
        {
            IntVec3 side = new IntVec3(into.z, 0, -into.x);
            IntVec3[] pocket =
            {
                mouth, mouth + side, mouth - side,
                mouth + into, mouth + into + side, mouth + into - side,
            };
            int carvable = 0;
            for (int i = 0; i < pocket.Length; i++)
            {
                if (IsCarvableRock(pocket[i], map))
                {
                    carvable++;
                }
            }
            if (carvable < 3 || !IsCarvableRock(mouth + into, map))
            {
                return false;
            }

            List<IntVec3> carved = new List<IntVec3>();
            for (int i = 0; i < pocket.Length; i++)
            {
                IntVec3 c = pocket[i];
                if (!IsCarvableRock(c, map))
                {
                    continue;
                }
                // Every pocket cell touches the mouth or the cell behind it,
                // and both are carved (checked above), so the pocket is one
                // connected floor opening onto the face.
                Building rock = c.GetEdifice(map);
                TerrainDef floor = rock.def.building.naturalTerrain;
                TerrainDef smooth = floor?.smoothedTerrain ?? floor;
                rock.Destroy(DestroyMode.Vanish);
                if (smooth != null)
                {
                    map.terrainGrid.SetTerrain(c, smooth);
                }
                GenSpawn.Spawn(ThingMaker.MakeThing(ledgeDef), c, map);
                carved.Add(c);
            }
            res.ledges++;
            res.ledgeCells += carved.Count;

            // Carving in the back wall, else a side wall; an anchor in the
            // next free wall cell.
            IntVec3[] walls =
            {
                mouth + into + into, mouth + into + side + side, mouth + into - side - side,
                mouth + side + side, mouth - side - side,
            };
            bool carvingPlaced = false;
            bool anchorPlaced = false;
            for (int i = 0; i < walls.Length && !(carvingPlaced && anchorPlaced); i++)
            {
                IntVec3 w = walls[i];
                if (!IsCarvableRock(w, map))
                {
                    continue;
                }
                if (!carvingPlaced && RM_FloodedCanyonDefOf.RM_MercyCarving != null)
                {
                    carvingPlaced = Replace(map, w, RM_FloodedCanyonDefOf.RM_MercyCarving);
                    if (carvingPlaced)
                    {
                        res.carvings++;
                    }
                }
                else if (!anchorPlaced && RM_FloodedCanyonDefOf.RM_ChimeLineAnchor != null)
                {
                    anchorPlaced = Replace(map, w, RM_FloodedCanyonDefOf.RM_ChimeLineAnchor);
                    if (anchorPlaced)
                    {
                        anchors.Add(w);
                        res.anchors++;
                    }
                }
            }
            return true;
        }

        private static bool Replace(Map map, IntVec3 c, ThingDef def)
        {
            if (!IsCarvableRock(c, map))
            {
                return false;
            }
            c.GetEdifice(map).Destroy(DestroyMode.Vanish);
            GenSpawn.Spawn(ThingMaker.MakeThing(def), c, map);
            return true;
        }
    }

    // Registered on MapCommonBase (Patches/RM_FloodedCanyon_MercyLedges_Register.xml).
    // Gated on the biome (or the flood's own "other biomes" setting, since a
    // ledge only matters where the flood runs) and on its own setting.
    public class RM_GenStep_MercyLedges : GenStep
    {
        public override int SeedPart => 1628093517;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_FloodedCanyonSettings.mercyLedgesEnabled)
            {
                return;
            }
            if (map.Biome != RM_FloodedCanyonDefOf.RM_FloodedCanyon && !RM_FloodedCanyonSettings.featureInOtherBiomes)
            {
                return;
            }
            RM_MercyLedges.Generate(map, MapGenerator.Elevation);
        }
    }

    // ── the carving ──

    public class CompProperties_RM_MercyCarving : CompProperties
    {
        public ThoughtDef thought;
        // PROVISIONAL: a pawn within 2.9 cells (adjacent or one cell off)
        // with line of sight to the carving has read it.
        public float readRadius = 2.9f;
        // PLACEHOLDER lines until the owner writes the inscriptions
        // (drafts with him, see the item). Set in XML.
        public List<string> inscriptions = new List<string>();

        public CompProperties_RM_MercyCarving()
        {
            compClass = typeof(CompRM_MercyCarving);
        }
    }

    public class CompRM_MercyCarving : ThingComp
    {
        private int inscriptionIndex = -1;
        private List<int> readers = new List<int>();

        public CompProperties_RM_MercyCarving Props => (CompProperties_RM_MercyCarving)props;

        public int ReaderCount => readers.Count;

        public string Inscription
        {
            get
            {
                if (Props.inscriptions.NullOrEmpty())
                {
                    return null;
                }
                if (inscriptionIndex < 0 || inscriptionIndex >= Props.inscriptions.Count)
                {
                    inscriptionIndex = Rand.Range(0, Props.inscriptions.Count);
                }
                return Props.inscriptions[inscriptionIndex];
            }
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (!RM_FloodedCanyonSettings.carvingMemoryEnabled || Props.thought == null || !parent.Spawned)
            {
                return;
            }
            Map map = parent.Map;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (!p.RaceProps.Humanlike || p.Dead || p.Downed || !p.Awake() || p.needs?.mood == null)
                {
                    continue;
                }
                if (!p.Position.InHorDistOf(parent.Position, Props.readRadius) || readers.Contains(p.thingIDNumber))
                {
                    continue;
                }
                if (!GenSight.LineOfSightToThing(p.Position, parent, map))
                {
                    continue;
                }
                readers.Add(p.thingIDNumber);
                p.needs.mood.thoughts.memories.TryGainMemory(Props.thought);
            }
        }

        public override string CompInspectStringExtra()
        {
            string line = Inscription;
            string s = line != null ? "Inscription: " + line : null;
            string r = "Read by " + readers.Count + (readers.Count == 1 ? " person" : " people");
            return s != null ? s + "\n" + r : r;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref inscriptionIndex, "inscriptionIndex", -1);
            Scribe_Collections.Look(ref readers, "readers", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && readers == null)
            {
                readers = new List<int>();
            }
        }
    }
}
