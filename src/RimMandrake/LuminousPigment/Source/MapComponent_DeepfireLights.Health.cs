using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_HEALTH_CHECK_1. A read-only audit of the light book against the map: it changes nothing, spawns nothing,
    // destroys nothing. Three classes of drift, each zero on a clean map:
    //   orphan proxies        a spawned RM_DeepfireLightProxy that no book entry owns, or an entry whose proxy is gone,
    //                         despawned or on another map;
    //   wrong-map pawn lights a pawn-keyed light (hediff glow or worn gear) whose pawn is not spawned on THIS map;
    //   uncovered members     a coated floor cell, clustered building or own-light thing that no live light of the right
    //                         coat count reaches.
    public sealed class DeepfireHealthReport
    {
        public int TrackedLights;
        public int ProxiesOnMap;
        public int OrphanProxies;
        public int DeadEntries;
        public int PawnLights;
        public int WrongMapPawnLights;
        public int CoatedFloorCells;
        public int UncoveredFloorCells;
        public int CoatedThings;
        public int UncoveredThings;
        public readonly List<string> Examples = new List<string>();

        public int Problems => OrphanProxies + DeadEntries + WrongMapPawnLights + UncoveredFloorCells + UncoveredThings;

        public void Note(string s)
        {
            if (Examples.Count < 8) Examples.Add(s);
        }
    }

    public partial class MapComponent_DeepfireLights
    {
        private struct LiveLight
        {
            public int Coats;
            public IntVec3 Pos;
            public float Radius;
        }

        private static bool ProxyLive(LightEntry e, Map m)
        {
            return e != null && e.Proxy != null && !e.Proxy.Destroyed && e.Proxy.Spawned && e.Proxy.Map == m;
        }

        public DeepfireHealthReport Health()
        {
            var r = new DeepfireHealthReport { TrackedLights = entries.Count };
            var owned = new HashSet<Thing>();
            var byBlock = new Dictionary<long, List<LiveLight>>();

            foreach (KeyValuePair<object, LightEntry> kv in entries)
            {
                LightEntry e = kv.Value;
                if (e.Proxy != null) owned.Add(e.Proxy);
                if (!ProxyLive(e, map))
                {
                    r.DeadEntries++;
                    r.Note("entry " + kv.Key + " has no live proxy on this map");
                }
                Pawn pawn = kv.Key is PawnHediffKey hk ? hk.Pawn : (kv.Key is WornKey wk ? wk.Pawn : null);
                if (kv.Key is PawnHediffKey || kv.Key is WornKey)
                {
                    r.PawnLights++;
                    if (pawn == null || !pawn.Spawned || pawn.Map != map || pawn.Dead)
                    {
                        r.WrongMapPawnLights++;
                        r.Note("pawn light for " + (pawn?.LabelShort ?? "null") + " but the pawn is not spawned on this map");
                    }
                }
                if (kv.Key is DeepfireClusterKey ck && ProxyLive(e, map))
                {
                    CompGlower g = e.Proxy.TryGetComp<CompGlower>();
                    long slot = ((long)ck.Kind << 32) | (uint)ck.Block;
                    if (!byBlock.TryGetValue(slot, out List<LiveLight> list)) byBlock[slot] = list = new List<LiveLight>();
                    list.Add(new LiveLight { Coats = ck.Coats, Pos = e.Proxy.Position, Radius = g?.GlowRadius ?? 0f });
                }
            }

            if (DeepfireDefOf.RM_DeepfireLightProxy != null)
            {
                List<Thing> proxies = map.listerThings.ThingsOfDef(DeepfireDefOf.RM_DeepfireLightProxy);
                r.ProxiesOnMap = proxies.Count;
                for (int i = 0; i < proxies.Count; i++)
                {
                    if (!owned.Contains(proxies[i]))
                    {
                        r.OrphanProxies++;
                        r.Note("orphan light proxy at " + proxies[i].Position);
                    }
                }
            }

            int size = DeepfireLightBook<Thing, UnityEngine.Color>.BlockSizeOf(LuminousPigmentSettings.clusterBlock);
            byte[] grid = bookField?.FloorGrid;
            if (grid != null && grid.Length == map.Size.x * map.Size.z)
            {
                for (int i = 0; i < grid.Length; i++)
                {
                    int coats = grid[i];
                    if (coats <= 0) continue;
                    r.CoatedFloorCells++;
                    int x = i % map.Size.x, z = i / map.Size.x;
                    int block = DeepfireLightBook<Thing, UnityEngine.Color>.BlockIndexOf(x, z, map.Size.x, size);
                    if (!Reaches(byBlock, DeepfireLightBook<Thing, UnityEngine.Color>.KindFloor, block, coats, x, z))
                    {
                        r.UncoveredFloorCells++;
                        r.Note("coated floor cell " + x + "," + z + " (" + coats + " coats) is outside every light");
                    }
                }
            }

            CheckThings(map.listerBuildings.allBuildingsColonist, size, byBlock, r);
            CheckThings(map.listerBuildings.allBuildingsNonColonist, size, byBlock, r);
            return r;
        }

        private void CheckThings(List<Building> buildings, int size, Dictionary<long, List<LiveLight>> byBlock, DeepfireHealthReport r)
        {
            if (buildings == null) return;
            for (int i = 0; i < buildings.Count; i++)
            {
                Thing t = buildings[i];
                CompDeepfire comp = t.TryGetComp<CompDeepfire>();
                if (comp == null || comp.coats <= 0) continue;
                r.CoatedThings++;
                bool ok;
                if (IsClusterable(t))
                {
                    int block = DeepfireLightBook<Thing, UnityEngine.Color>.BlockIndexOf(t.Position.x, t.Position.z, map.Size.x, size);
                    ok = Reaches(byBlock, DeepfireLightBook<Thing, UnityEngine.Color>.KindBuilding, block, comp.coats, t.Position.x, t.Position.z);
                }
                else
                {
                    ok = entries.TryGetValue(t, out LightEntry e) && ProxyLive(e, map)
                        && (e.Proxy.TryGetComp<CompGlower>()?.GlowRadius ?? 0f) > 0f;
                }
                if (!ok)
                {
                    r.UncoveredThings++;
                    r.Note("coated " + t.def.defName + " at " + t.Position + " (" + comp.coats + " coats) has no light reaching it");
                }
            }
        }

        private static bool Reaches(Dictionary<long, List<LiveLight>> byBlock, byte kind, int block, int coats, int x, int z)
        {
            if (!byBlock.TryGetValue(((long)kind << 32) | (uint)block, out List<LiveLight> list)) return false;
            for (int i = 0; i < list.Count; i++)
            {
                if (list[i].Coats != coats) continue;
                float dx = list[i].Pos.x - x, dz = list[i].Pos.z - z;
                if (dx * dx + dz * dz <= list[i].Radius * list[i].Radius + 0.01f) return true;
            }
            return false;
        }
    }
}
