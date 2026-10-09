using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.Shared;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_LIVE_FAILURES_1: thingClass of RM_DeepfireLightProxy and
    // RM_DeepfireWornLightProxy. The proxy's lifetime belongs to
    // MapComponent_DeepfireLights, and its anchor's despawn removes it
    // synchronously -- so any caller destroying from a per-cell SNAPSHOT
    // (vanilla GenDebug.ClearArea: GetThingList(map).ToList() then Destroy
    // each; RimSage Verse/GenDebug.cs) reaches the proxy a second time after
    // the coated building on the same cell already took it down, and vanilla
    // Thing.Destroy logs "Tried to destroy already-destroyed thing". Measured
    // live 2026-09-30 (x4 across the Deepfire proofs). A second destroy of a
    // proxy has nothing left to do, so it is a no-op here.
    public class DeepfireLightProxy : ThingWithComps
    {
        // LIGHT_LEDGER_ONE_1 / DEEPFIRE_WORLD_LIGHT_1: every deepfire light says so in the shared light ledger, so other
        // mods can treat it as deepfire (the Abyss Dark spares it, glow-seekers are drawn to it) without referencing this
        // assembly. Runs on every spawn, so a fresh proxy is tagged before its first radius is set.
        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            LightLedger.Tag(GetComp<CompGlower>(), "deepfire");
        }

        public override void Destroy(DestroyMode mode = DestroyMode.Vanish)
        {
            if (Destroyed) return;
            base.Destroy(mode);
        }
    }

    // Spec §10 step 1's answer (recorded on DEEPFIRE_PAINT_LIVE_VERIFY_1,
    // no live bridge needed to derive it -- confirmed against decompiled
    // Verse/CompGlower.cs + Verse/GlowGrid.cs): CompGlower.ShouldBeLitNow
    // gates on parent.Spawned, and only PostSpawnSetup registers a glower
    // with map.glowGrid. An UNSPAWNED proxy structurally cannot light the
    // grid, so every light this class owns is a real SPAWNED, invisible,
    // unselectable RM_DeepfireLightProxy (altitudeLayer Item, NOT Building --
    // MEASURED live 2026-09-29 that a Building-layer proxy WIPES whatever it
    // was meant to light via GenSpawn.Spawn's default WipeMode.Vanish; and
    // category Ethereal, NOT Item -- an Item-category proxy shoved real items
    // off its cell and made the cell read full to storage,
    // DEEPFIRE_PROXY_BLOCKS_STORAGE_1; see the def's own header) carrying CompGlower, whose colour
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
            public ColorInt LastColor;
            public float LastRadius = -1f;
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
            Book.RegisterThing(thing, thing.Position.x, thing.Position.z, IsClusterable(thing), color, radius);
        }

        public void DeregisterThingLight(Thing thing)
        {
            if (thing == null) return;
            if (bookField != null) bookField.DeregisterThing(thing);
        }

        // ---- HediffComp_DeepfireGlow.cs's soft-bound contract (Cuisine) ----

        private readonly struct PawnHediffKey : System.IEquatable<PawnHediffKey>
        {
            private readonly Pawn pawn;
            private readonly HediffDef def;

            public Pawn Pawn => pawn;

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

        // GPT review #9: an unspawned/dead pawn (left the map, caravan,
        // corpse) loses its light everywhere, and a pawn now on a different
        // map drops the stale entry on every other map before re-registering.
        public static void RegisterHediffGlow(Pawn pawn, HediffDef def, Color color, float radius)
        {
            if (pawn == null) return;
            PawnHediffKey key = new PawnHediffKey(pawn, def);
            Map here = pawn.Spawned && !pawn.Dead ? pawn.Map : null;
            List<Map> maps = Find.Maps;
            for (int i = 0; i < maps.Count; i++)
            {
                if (maps[i] != here) Get(maps[i])?.RemoveLight(key);
            }
            if (here == null) return;
            Get(here)?.SetLight(key, pawn.Position, color, radius);
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

            bool fresh = false;
            if (!entries.TryGetValue(key, out LightEntry e) || e.Proxy == null || e.Proxy.Destroyed)
            {
                e = new LightEntry { Proxy = SpawnProxy(cell), Cell = cell };
                entries[key] = e;
                fresh = true;
            }
            else if (e.Cell != cell)
            {
                e.Proxy.Destroy(DestroyMode.Vanish);
                e.Proxy = SpawnProxy(cell);
                e.Cell = cell;
                fresh = true;
            }

            // GPT review #30: an unchanged light on an unchanged proxy is not
            // re-registered (hediffs call this every 250 ticks while idle).
            ColorInt ci = new ColorInt(color);
            if (!fresh && e.LastRadius == radius && e.LastColor.r == ci.r && e.LastColor.g == ci.g
                && e.LastColor.b == ci.b && e.LastColor.a == ci.a) return;

            CompGlower glower = e.Proxy.TryGetComp<CompGlower>();
            if (glower != null)
            {
                // the colour setter re-registers a lit glower itself; the radius is this light's BASE in the shared
                // light ledger (LIGHT_LEDGER_ONE_1), which re-registers on a real change
                glower.GlowColor = ci;
                LightLedger.SetBase(glower, radius);
                if (fresh && key is PawnHediffKey hk) LightLedger.SetCarrier(glower, hk.Pawn);
                e.LastColor = ci;
                e.LastRadius = radius;
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
