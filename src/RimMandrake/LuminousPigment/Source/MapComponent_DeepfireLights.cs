using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §10 step 1's answer (recorded on DEEPFIRE_PAINT_LIVE_VERIFY_1,
    // no live bridge needed to derive it -- confirmed against decompiled
    // Verse/CompGlower.cs + Verse/GlowGrid.cs): CompGlower.ShouldBeLitNow
    // gates on parent.Spawned, and only PostSpawnSetup registers a glower
    // with map.glowGrid. An UNSPAWNED proxy structurally cannot light the
    // grid, so every light this class owns is a real SPAWNED, invisible,
    // unselectable RM_DeepfireLightProxy (category/altitudeLayer Item, NOT
    // Building -- MEASURED live 2026-09-29 that a Building-layer proxy gets
    // WIPED, along with whatever it was meant to light, by GenSpawn.Spawn's
    // default WipeMode.Vanish; see the def's own header) carrying CompGlower, whose colour
    // and radius are set at runtime via the comp's own override setters --
    // never spawn/destroy per movement (the expensive pattern spec
    // painting_integration.md §4 warns against; here a light only respawns
    // when its CELL actually changes, which for step 5's Thing-anchored
    // lights only happens on minify/reinstall, already handled by
    // CompDeepfire's own PostDeSpawn/PostSpawnSetup hooks).
    //
    // One proxy per registered KEY:
    //  - step 5: the coated Thing itself (multi-cell furniture, art,
    //    apparel, weapons on the ground).
    //  - step 6 (DEEPFIRE_FLOOR_PAINT_1, MapComponent_DeepfireLights.Clusters.cs):
    //    a ClusterKey per 3x3 block x kind x coats x colour, covering coated
    //    floor cells and coated 1x1 buildings (walls, small furniture).
    //  - the RegisterHediffGlow/DeregisterHediffGlow pair below: the
    //    contract HediffComp_DeepfireGlow.cs (Cuisine, already shipped)
    //    already soft-binds to by reflection. That hediff comp re-registers
    //    every 250 ticks on its own (CompPostTick -> Apply()), so a plain
    //    "move this key's proxy to the pawn's CURRENT cell" here is enough
    //    to track a moving pawn at that cadence with NO extra polling built
    //    in this class.
    //  - worn/equipped gear (DEEPFIRE_WORN_GLOW_1, spec §10 step 8,
    //    MapComponent_DeepfireLights.Worn.cs): one MOVING Ethereal proxy per
    //    glowing pawn, polled every 15 ticks and moved by Position, not
    //    respawned.
    public partial class MapComponent_DeepfireLights : MapComponent
    {
        private class LightEntry
        {
            public Thing Proxy;
            public IntVec3 Cell;
        }

        private readonly Dictionary<object, LightEntry> entries = new Dictionary<object, LightEntry>();

        public MapComponent_DeepfireLights(Map map) : base(map)
        {
        }

        // One-entry cache: BeautyUtility.CellBeauty (postfixed for the floor
        // bonus) runs hundreds of times per beauty sample, and GetComponent<T>
        // is a linear scan over every mod's map components. Map instances are
        // never reused, so a stale entry can only miss, never mis-hit.
        private static Map cachedMap;
        private static MapComponent_DeepfireLights cachedComp;

        public static MapComponent_DeepfireLights Get(Map map)
        {
            if (map == null) return null;
            if (map == cachedMap && cachedComp != null) return cachedComp;
            MapComponent_DeepfireLights mc = map.GetComponent<MapComponent_DeepfireLights>();
            cachedMap = map;
            cachedComp = mc;
            return mc;
        }

        // ---- Thing-anchored lights (step 5) ----

        // DEEPFIRE_FLOOR_PAINT_1 (spec §3.6): a 1x1 Building (walls, small
        // furniture) no longer owns a proxy of its own -- it joins the 3x3
        // block cluster in MapComponent_DeepfireLights.Clusters.cs, so a
        // 400-cell hall is ~45 lights, not 400. Larger things keep one proxy
        // per Thing (they already cover several cells with one light).
        public void RegisterThingLight(Thing thing, Color color, float radius)
        {
            if (thing == null || !thing.Spawned || thing.Map != map) return;
            if (IsClusterable(thing))
            {
                RegisterClusteredThing(thing);
                return;
            }
            SetLight(thing, thing.Position, color, radius);
        }

        public void DeregisterThingLight(Thing thing)
        {
            if (thing == null) return;
            if (DeregisterClusteredThing(thing)) return;
            RemoveLight(thing);
        }

        // ---- HediffComp_DeepfireGlow.cs's soft-bound contract (Cuisine) ----

        private readonly struct PawnHediffKey : System.IEquatable<PawnHediffKey>
        {
            private readonly Pawn pawn;
            private readonly HediffDef def;

            public PawnHediffKey(Pawn p, HediffDef d)
            {
                pawn = p;
                def = d;
            }

            public bool Equals(PawnHediffKey other) => pawn == other.pawn && def == other.def;
            public override bool Equals(object obj) => obj is PawnHediffKey k && Equals(k);
            public override int GetHashCode()
            {
                int a = pawn?.thingIDNumber ?? 0;
                int b = def?.shortHash ?? 0;
                return a * 397 ^ b;
            }
        }

        public static void RegisterHediffGlow(Pawn pawn, HediffDef def, Color color, float radius)
        {
            if (pawn?.Map == null || !pawn.Spawned) return;
            MapComponent_DeepfireLights mc = Get(pawn.Map);
            mc?.SetLight(new PawnHediffKey(pawn, def), pawn.Position, color, radius);
        }

        public static void DeregisterHediffGlow(Pawn pawn, HediffDef def)
        {
            if (pawn == null) return;
            PawnHediffKey key = new PawnHediffKey(pawn, def);
            List<Map> maps = Find.Maps;
            for (int i = 0; i < maps.Count; i++)
            {
                Get(maps[i])?.RemoveLight(key);
            }
        }

        // ---- shared proxy machinery ----

        private void SetLight(object key, IntVec3 cell, Color color, float radius)
        {
            if (radius <= 0f)
            {
                RemoveLight(key);
                return;
            }

            if (!entries.TryGetValue(key, out LightEntry e) || e.Proxy == null || e.Proxy.Destroyed)
            {
                e = new LightEntry { Proxy = SpawnProxy(cell), Cell = cell };
                entries[key] = e;
            }
            else if (e.Cell != cell)
            {
                e.Proxy.Destroy(DestroyMode.Vanish);
                e.Proxy = SpawnProxy(cell);
                e.Cell = cell;
            }

            CompGlower glower = e.Proxy.TryGetComp<CompGlower>();
            if (glower != null)
            {
                glower.GlowColor = new ColorInt(color);
                glower.GlowRadius = radius;
                glower.ForceRegister(map);
            }
        }

        private Thing SpawnProxy(IntVec3 cell)
        {
            Thing proxy = ThingMaker.MakeThing(DeepfireDefOf.RM_DeepfireLightProxy);
            GenSpawn.Spawn(proxy, cell, map, WipeMode.Vanish);
            return proxy;
        }

        private void RemoveLight(object key)
        {
            if (entries.TryGetValue(key, out LightEntry e))
            {
                if (e.Proxy != null && !e.Proxy.Destroyed) e.Proxy.Destroy(DestroyMode.Vanish);
                entries.Remove(key);
            }
        }

        public override void MapRemoved()
        {
            base.MapRemoved();
            entries.Clear();
            ClearClusterState();
            ClearWornState();
            if (cachedMap == map)
            {
                cachedMap = null;
                cachedComp = null;
            }
        }
    }
}
