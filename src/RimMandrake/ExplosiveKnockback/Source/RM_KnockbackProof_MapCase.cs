#if RM_PROOFS
// Proof build only (RM_PROOFS). The live half of the situation map (Source/SelfTest/KnockbackMap.cs,
// RIMMANDRAKE_RESCUE_KNOCKBACK_PAST_CEILING_CYCLE_SIX): stage one of the map's cases in the running game from its spec, set the
// blast off, and read where every thing ended, so proof/map_agreement.py can state how often the model and the game agree.
// A spec is ';'-separated, every cell relative to the blast:
//   c:<wall|door|sandbag|water|pit|cover>:<dx>:<dz>
//   t:<key>:<col|big|steel2|steel40|wood50|uran74>:<dx>:<dz>     col = a colonist pinned to 70 kg, big = one pinned to 200 kg
//   b:<bomb|gas>:<radius>
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.ExplosiveKnockback
{
    public static partial class RM_KnockbackProof
    {
        private static Scene mapCase;
        private static readonly List<IntVec3> mapCaseCovers = new List<IntVec3>();
        private static readonly List<int> mapCasePinned = new List<int>();

        /// <summary>"x,z@spec" (the bridge splits its arguments on a bar): stage the case with its blast at (x, z). Returns "STAGED map_case" or why not.</summary>
        public static string MapCase(string arg)
        {
            string[] head = (arg ?? "").Split('@');
            string[] xz = head[0].Split(',');
            if (head.Length != 2 || xz.Length != 2 || !int.TryParse(xz[0], out int x) || !int.TryParse(xz[1], out int z) || Map == null)
            {
                return "REFUSED: arg must be x,z@spec on a current map";
            }
            MapCaseForget();
            var s = new Scene { name = "map_case", o = new IntVec3(x, 0, z), stagedTick = Find.TickManager.TicksGame };
            try
            {
                Prepare(s.o, 7);
                foreach (IntVec3 c in CellRect.CenteredOn(s.o, 7).ClipInsideMap(Map))
                {
                    if (RM_KnockbackCompat.ClimbDepthAt(Map, c) != 0)
                    {
                        return "INVALID map_case site: climb depth at " + c.x + "," + c.z + " after prepare; stage it elsewhere";
                    }
                }
                string blast = null;
                float radius = 0f;
                var tokens = head[1].Split(new[] { ';' }, StringSplitOptions.RemoveEmptyEntries);
                foreach (string tok in tokens.Where(t => t.StartsWith("c:")))
                {
                    string[] p = tok.Split(':');
                    IntVec3 c = O(s, int.Parse(p[2]), int.Parse(p[3]));
                    switch (p[1])
                    {
                        case "wall": Build("Wall", c, "BlocksGranite"); break;
                        case "door": Build("Door", c, "WoodLog"); break;
                        case "sandbag": Build("Sandbags", c, "Cloth"); break;
                        case "water": Map.terrainGrid.SetTerrain(c, TerrainDefOf.WaterDeep); break;
                        case "pit":
                        case "cover":
                            if (!Pit(c, 1, 1))
                            {
                                return "INVALID map_case could not dig " + c.x + "," + c.z;
                            }
                            if (p[1] == "cover")
                            {
                                Build("RM_PitCover_WovenScrap", c);
                                if (RM_KnockbackCompat.CoverAt(Map, c) == null)
                                {
                                    return "INVALID map_case no cover at " + c.x + "," + c.z + " after building it";
                                }
                                mapCaseCovers.Add(c);
                            }
                            break;
                        default: return "REFUSED: cell type " + p[1];
                    }
                }
                foreach (string tok in tokens.Where(t => t.StartsWith("t:")))
                {
                    string[] p = tok.Split(':');
                    IntVec3 c = O(s, int.Parse(p[3]), int.Parse(p[4]));
                    switch (p[2])
                    {
                        case "col":
                        case "big":
                            Pawn pawn = Colonist(s, p[1], c);
                            PinnedMass[pawn.thingIDNumber] = p[2] == "big" ? 200f : 70f;
                            mapCasePinned.Add(pawn.thingIDNumber);
                            break;
                        case "steel2": Item(s, p[1], "Steel", 2, c); break;
                        case "steel40": Item(s, p[1], "Steel", 40, c); break;
                        case "wood50": Item(s, p[1], "WoodLog", 50, c); break;
                        case "uran74": Item(s, p[1], "Uranium", 74, c); break;
                        default: return "REFUSED: thing type " + p[2];
                    }
                }
                foreach (string tok in tokens.Where(t => t.StartsWith("b:")))
                {
                    string[] p = tok.Split(':');
                    blast = p[1];
                    radius = float.Parse(p[2], CultureInfo.InvariantCulture);
                }
                if (blast == "bomb")
                {
                    Blast(s.o, radius);
                }
                else if (blast == "gas")
                {
                    RM_MapComponent_Knockback.GasBurst(Map, s.o, null, "map_case");
                }
                else
                {
                    return "REFUSED: no blast in the spec";
                }
                mapCase = s;
                return "STAGED map_case";
            }
            catch (Exception ex)
            {
                return "ERROR map_case " + ex.Message;
            }
        }

        private static void MapCaseForget()
        {
            foreach (int id in mapCasePinned)
            {
                PinnedMass.Remove(id);
            }
            mapCasePinned.Clear();
            mapCaseCovers.Clear();
            mapCase = null;
        }

        /// <summary>"x,z": what stands on one cell now, read from the map alone (so it still answers after a reload, when a
        /// staged scene's own references are stale): "CELL pawns=N items=N superdeep=bool cover=bool flyers=N".</summary>
        public static string CellRead(string arg)
        {
            string[] xz = (arg ?? "").Split(',');
            if (xz.Length != 2 || !int.TryParse(xz[0], out int x) || !int.TryParse(xz[1], out int z) || Map == null)
            {
                return "REFUSED: arg must be x,z on a current map";
            }
            var c = new IntVec3(x, 0, z);
            List<Thing> l = c.GetThingList(Map);
            return "CELL pawns=" + l.Count(t => t is Pawn) + " items=" + l.Count(t => t.def.category == ThingCategory.Item)
                + " superdeep=" + RM_KnockbackCompat.IsSuperdeep(Map, c) + " cover=" + (RM_KnockbackCompat.CoverAt(Map, c) != null)
                + " flyers=" + Map.listerThings.AllThings.Count(t => t is PawnFlyer || t is RM_ThingFlyer_Knockback);
        }

        /// <summary>Where every staged thing is now, relative to the blast: "key=dx,dz,inPit,state;...|covers=dx,dz/..."
        /// state: ok, air (still flying), or merged (absorbed into a resident stack: its cell is the item_land line's).</summary>
        public static string MapRead(string _)
        {
            Scene s = mapCase;
            if (s == null)
            {
                return "INVALID map_case not staged";
            }
            var parts = new List<string>();
            foreach (KeyValuePair<string, Thing> kv in s.things)
            {
                Thing t = kv.Value;
                IntVec3 at = IntVec3.Invalid;
                string state = "ok";
                if (t.Spawned)
                {
                    at = t.Position;
                }
                else
                {
                    var land = ForThing(s, "item_land", t);
                    if (land.Count > 0 && land[land.Count - 1].TryGetValue("to", out object to) && to is IntVec3 c)
                    {
                        at = c;
                        state = "merged";
                    }
                    else
                    {
                        state = t is Pawn p && p.Dead ? "dead" : "air";
                    }
                }
                bool inPit = at.IsValid && RM_KnockbackCompat.IsSuperdeep(Map, at) && RM_KnockbackCompat.CoverAt(Map, at) == null
                    && !(t is Pawn pp && false);
                parts.Add(kv.Key + "=" + (at.IsValid ? (at.x - s.o.x) + "," + (at.z - s.o.z) : "?,?") + "," + (inPit ? 1 : 0) + "," + state);
            }
            string covers = string.Join("/", mapCaseCovers.Where(c => RM_KnockbackCompat.CoverAt(Map, c) != null).Select(c => (c.x - s.o.x) + "," + (c.z - s.o.z)));
            return "READ " + string.Join(";", parts) + "|covers=" + covers;
        }
    }
}
#endif
