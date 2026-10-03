using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Pits
{
    // PIT_COVER_FALL_REWIRE_1 — the covered pit, rebuilt on the D/F primitive (owner 2026-10-02:
    // "There's no 'pit' as a special thing, it's just a channel/canal dig."). A cover is a 1x1
    // building laid over a SUPERDEEP (D=4) cell. Neighbouring covers form one deck: the
    // CompPitCoverTrigger on the deck's lead cover sums the mass of everyone standing on the WHOLE
    // deck every 30 ticks, and once it crosses the tier's rating (PitCoverTier 40/120/220 kg, 220 is
    // the owner's number) every cover in the deck gives way and the pawns on it DESCEND through the
    // superdeep trap's own descent event (fall damage, then whatever hooks PitDescent). No despawn.
    //
    // While a cover stands, its cell is not a pit for anything that walks: no descent fires, nobody
    // is held, the shooting rule treats it as ground, and its path cost is the cover's, not the
    // hole's 300 (a trap nobody walks over catches nobody). The cover prints the terrain AROUND the
    // pit so the hole beneath it cannot be seen (TerrainMimicPrinter's open question — whether the
    // seam vanishes at play zoom — is still a live-eyes check, bar pit_covered_seam_at_max_zoom).
    public class RM_PitCoverExtension : DefModExtension
    {
        public PitCoverTier tier = PitCoverTier.WovenScrap;
    }

    public static class RM_PitCoverUtility
    {
        public static Building_PitCover CoverAt(Map map, IntVec3 c)
        {
            if (map == null || !c.InBounds(map))
            {
                return null;
            }
            List<Thing> things = c.GetThingList(map);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i] is Building_PitCover cover && cover.Covered)
                {
                    return cover;
                }
            }
            return null;
        }

        public static bool IsCovered(Map map, IntVec3 c)
        {
            return CoverAt(map, c) != null;
        }

        /// <summary>Every intact cover 4-way connected to this one (this one included).</summary>
        public static List<Building_PitCover> Deck(Building_PitCover start)
        {
            List<Building_PitCover> deck = new List<Building_PitCover>();
            if (start == null || !start.Spawned)
            {
                return deck;
            }
            Map map = start.Map;
            HashSet<IntVec3> seen = new HashSet<IntVec3> { start.Position };
            Queue<IntVec3> open = new Queue<IntVec3>();
            open.Enqueue(start.Position);
            while (open.Count > 0 && deck.Count < 400)
            {
                IntVec3 c = open.Dequeue();
                Building_PitCover cover = CoverAt(map, c);
                if (cover == null)
                {
                    continue;
                }
                deck.Add(cover);
                for (int i = 0; i < 4; i++)
                {
                    IntVec3 n = c + GenAdj.CardinalDirections[i];
                    if (seen.Add(n) && CoverAt(map, n) != null)
                    {
                        open.Enqueue(n);
                    }
                }
            }
            return deck;
        }

        /// <summary>The terrain the cover should look like: the commonest non-excavated terrain around it.</summary>
        public static TerrainDef SurfaceAround(Map map, IntVec3 c)
        {
            RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
            Dictionary<TerrainDef, int> counts = new Dictionary<TerrainDef, int>();
            for (int r = 1; r <= 4; r++)
            {
                foreach (IntVec3 n in GenRadial.RadialCellsAround(c, r, false))
                {
                    if (!n.InBounds(map) || (eng != null && eng.IsExcavated(n)))
                    {
                        continue;
                    }
                    TerrainDef t = n.GetTerrain(map);
                    if (t != null)
                    {
                        counts[t] = counts.TryGetValue(t, out int k) ? k + 1 : 1;
                    }
                }
                if (counts.Count > 0)
                {
                    break;
                }
            }
            TerrainDef best = null;
            int bestN = -1;
            foreach (KeyValuePair<TerrainDef, int> kv in counts)
            {
                if (kv.Value > bestN)
                {
                    best = kv.Key;
                    bestN = kv.Value;
                }
            }
            return best ?? TerrainDefOf.Soil;
        }
    }

    public class Building_PitCover : Building, IPitCoverHost
    {
        private bool sprung;

        public bool Covered => !sprung && Spawned;

        public bool Sprung => sprung;

        public PitCoverTier CoverTier => def.GetModExtension<RM_PitCoverExtension>()?.tier ?? PitCoverTier.None;

        /// <summary>One cover per deck scans (the lowest id), so a deck is summed once, not once per cell.</summary>
        public bool IsDeckLead
        {
            get
            {
                foreach (Building_PitCover c in RM_PitCoverUtility.Deck(this))
                {
                    if (c.thingIDNumber < thingIDNumber)
                    {
                        return false;
                    }
                }
                return true;
            }
        }

        public override void Print(SectionLayer layer)
        {
            Map map = Map;
            if (map == null)
            {
                return;
            }
            TerrainDef surface = RM_PitCoverUtility.SurfaceAround(map, Position);
            Material mat = surface?.graphic?.MatSingle;
            if (mat == null)
            {
                TerrainMimicPrinter.PrintTerrainMimic(this, layer);
                return;
            }
            Vector3 center = Position.ToVector3Shifted();
            center.y = DrawPos.y;
            Printer_Plane.PrintPlane(layer, center, Vector2.one, mat);
        }

        public void Spring(List<Pawn> fallers)
        {
            if (sprung || !Spawned)
            {
                return;
            }
            Map map = Map;
            List<Building_PitCover> deck = RM_PitCoverUtility.Deck(this);
            foreach (Building_PitCover c in deck)
            {
                c.sprung = true;
            }
            foreach (Building_PitCover c in deck)
            {
                if (c.Spawned)
                {
                    FilthMaker.TryMakeFilth(c.Position, map, ThingDefOf.Filth_RubbleRock, 1);
                    c.Destroy(DestroyMode.Vanish);
                }
            }
            RM_SuperdeepTrapState state = RM_SuperdeepTrap.EngineOf(map)?.SuperdeepTrap;
            Pawn first = null;
            foreach (Pawn p in fallers)
            {
                if (p == null || !p.Spawned || p.Dead || p.Flying)
                {
                    continue;
                }
                if (state != null)
                {
                    RM_SuperdeepTrap.OnDescent(p, p.Position, state);
                }
                first = first ?? p;
            }
            if (first != null)
            {
                Messages.Message("A pit cover gave way under " + first.LabelShort + (fallers.Count > 1 ? " and others." : "."),
                    new LookTargets(fallers), MessageTypeDefOf.NeutralEvent);
            }
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string line = "Gives way under " + CoverTier.TriggerMassKg().ToString("0") + " kg on the whole cover.";
            return s.NullOrEmpty() ? line : s + "\n" + line;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref sprung, "rmCoverSprung", false);
        }
    }

    /// <summary>A cover belongs over a superdeep (D=4) cell; anywhere else it would hide nothing.</summary>
    public class PlaceWorker_PitCoverOnSuperdeep : PlaceWorker
    {
        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot,
            Map map, Thing thingToIgnore = null, Thing thing = null)
        {
            RM_MapComponent_Excavation engine = map?.GetComponent<RM_MapComponent_Excavation>();
            if (engine == null || !engine.IsSuperdeepExcavation(loc))
            {
                return "A pit cover must be laid over a superdeep cell.";
            }
            return true;
        }
    }

    /// <summary>A covered superdeep cell costs what the cover costs to cross, not the hole's 300: the
    /// engine takes the MAX of terrain and thing costs, so only a postfix can lower it.</summary>
    [HarmonyPatch(typeof(PathGrid), nameof(PathGrid.CalculatedCostAt))]
    public static class RM_Patch_PathGrid_PitCoverCost
    {
        public static void Postfix(PathGrid __instance, IntVec3 c, ref int __result)
        {
            if (__result >= 10000)
            {
                return;
            }
            Map map = __instance.map;
            Building_PitCover cover = RM_PitCoverUtility.CoverAt(map, c);
            if (cover != null)
            {
                __result = Mathf.Max(cover.def.pathCost, 0);
            }
        }
    }
}
