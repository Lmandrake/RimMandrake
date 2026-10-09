using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.Shared;

namespace RimMandrake.LuminousPigment
{
    // DEEPFIRE_WORN_GLOW_1, spec §3.4: one MOVING proxy light per glowing
    // pawn. Reuses this class's `entries` table and the LightEntry shape;
    // what differs from SetLight is the proxy and how it moves:
    //
    //  - The proxy is RM_DeepfireWornLightProxy, category ETHEREAL (the
    //    static RM_DeepfireLightProxy is Ethereal too since
    //    DEEPFIRE_PROXY_BLOCKS_STORAGE_1). A pawn walks through
    //    stockpiles; an Item-category proxy would (a) make GenSpawn.Spawn move an
    //    existing item aside when the cell is already at its item limit, and
    //    (b) counts in GridsUtility.GetItemCount, so the cell reads full
    //    (RimSage Verse/GenSpawn.cs Spawn, Verse/GridsUtility.cs). An
    //    Ethereal, Standable, fillPercent-0, non-edifice thing trips none of
    //    GenSpawn.SpawningWipes' rules, so it wipes nothing it spawns on.
    //  - It moves by `proxy.Position = cell; glower.ForceRegister(map)` (the
    //    spec's own shape), never destroy/respawn per step. Thing.Position's
    //    setter re-registers a spawned thing in thingGrid/regions itself, and
    //    GlowLight caches `position` at registration, so ForceRegister's
    //    DeRegister dirties the OLD rect and its Register lights the NEW one
    //    (RimSage Verse/Thing.cs, Verse/Glow/GlowLight.cs, Verse/GlowGrid.cs).
    //
    // Driven two ways: CompDeepfire's Notify_Equipped/Unequipped/WearerDied
    // and coat changes call MarkWornDirty (instant), and MapComponentTick
    // polls every WornLightTickInterval ticks for cell changes plus a
    // WornRescanInterval sweep of spawned pawns (rebuilds after load, since
    // proxies are never saved, and catches anything a notify missed).
    // Skipped while unspawned (caravan, carried, in a pod): the entry is
    // simply dropped and re-found by the next sweep. No off switch (ruling).
    public partial class MapComponent_DeepfireLights
    {
        private sealed class WornKey : System.IEquatable<WornKey>
        {
            public readonly Pawn Pawn;
            public WornKey(Pawn p) { Pawn = p; }
            public bool Equals(WornKey other) => other != null && other.Pawn == Pawn;
            public override bool Equals(object obj) => Equals(obj as WornKey);
            public override int GetHashCode() => (Pawn?.thingIDNumber ?? 0) ^ 0x5EED;
        }

        private readonly Dictionary<Pawn, WornKey> wornPawns = new Dictionary<Pawn, WornKey>();
        private readonly List<Pawn> tmpWornPawns = new List<Pawn>();
        private bool wornSweptOnce;

        public int WornLightCount => wornPawns.Count;

        public static void MarkWornDirty(Pawn pawn)
        {
            if (pawn == null) return;
            List<Map> maps = Find.Maps;
            for (int i = 0; i < maps.Count; i++)
            {
                Get(maps[i])?.RefreshWornPawn(pawn);
            }
        }

        public bool TryGetWornLight(Pawn pawn, out ColorInt color, out float radius)
        {
            color = default(ColorInt);
            radius = 0f;
            if (pawn == null || !wornPawns.TryGetValue(pawn, out WornKey key)) return false;
            if (!entries.TryGetValue(key, out LightEntry e) || e.Proxy == null || e.Proxy.Destroyed) return false;
            CompGlower glower = e.Proxy.TryGetComp<CompGlower>();
            if (glower == null) return false;
            color = glower.GlowColor;
            radius = glower.GlowRadius;
            return radius > 0f;
        }

        public bool TryGetWornProxyCell(Pawn pawn, out IntVec3 cell)
        {
            cell = IntVec3.Invalid;
            if (pawn == null || !wornPawns.TryGetValue(pawn, out WornKey key)) return false;
            if (!entries.TryGetValue(key, out LightEntry e) || e.Proxy == null || e.Proxy.Destroyed) return false;
            cell = e.Proxy.Position;
            return true;
        }

        public void RefreshWornPawn(Pawn pawn)
        {
            if (pawn == null) return;
            // DEEPFIRE_MOD_SETTINGS_1, spec §7 wornLightEnabled: "off = worn
            // items glow only on the ground". The item is despawned while
            // worn (its own thing-light is already gone via PostDeSpawn), so
            // simply never granting/holding a worn proxy is the whole gate.
            bool here = LuminousPigmentSettings.wornLightEnabled
                && pawn.Spawned && pawn.Map == map && !pawn.Dead && !pawn.Destroyed;
            if (here && WornGlowUtility.TryComputeLight(pawn, out Color color, out float radius) && radius > 0f)
            {
                if (!wornPawns.TryGetValue(pawn, out WornKey key))
                {
                    key = new WornKey(pawn);
                    wornPawns[pawn] = key;
                }
                SetMovingLight(key, pawn.Position, color, radius);
                return;
            }
            if (wornPawns.TryGetValue(pawn, out WornKey old))
            {
                RemoveLight(old);
                wornPawns.Remove(pawn);
            }
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            int ticks = Find.TickManager.TicksGame;
            if (!wornSweptOnce || ticks % DeepfirePaintDefaults.WornRescanInterval == 0)
            {
                wornSweptOnce = true;
                SweepWornPawns();
            }
            else if (ticks % System.Math.Max(1, LuminousPigmentSettings.wornLightTickInterval) == 0)
            {
                PollWornPositions();
            }
        }

        public void PollWornPositions()
        {
            if (wornPawns.Count == 0) return;
            tmpWornPawns.Clear();
            tmpWornPawns.AddRange(wornPawns.Keys);
            for (int i = 0; i < tmpWornPawns.Count; i++)
            {
                Pawn p = tmpWornPawns[i];
                WornKey key = wornPawns[p];
                if (!p.Spawned || p.Map != map || p.Dead || p.Destroyed
                    || !entries.TryGetValue(key, out LightEntry e) || e.Proxy == null || e.Proxy.Destroyed)
                {
                    RefreshWornPawn(p); // drops it (or rebuilds a lost proxy)
                    continue;
                }
                if (e.Cell != p.Position) MoveLight(e, p.Position);
            }
        }

        private void SweepWornPawns()
        {
            // Drop stale entries first, then (re)register every spawned pawn
            // with coated gear -- colour/radius re-read, so a missed
            // Notify_ColorChanged on worn gear also self-heals here.
            tmpWornPawns.Clear();
            tmpWornPawns.AddRange(wornPawns.Keys);
            for (int i = 0; i < tmpWornPawns.Count; i++) RefreshWornPawn(tmpWornPawns[i]);

            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.apparel == null && p.equipment == null) continue;
                if (wornPawns.ContainsKey(p)) continue;
                RefreshWornPawn(p);
            }
        }

        private void SetMovingLight(WornKey key, IntVec3 cell, Color color, float radius)
        {
            bool moved = false;
            if (!entries.TryGetValue(key, out LightEntry e) || e.Proxy == null || e.Proxy.Destroyed)
            {
                Thing proxy = ThingMaker.MakeThing(DeepfireDefOf.RM_DeepfireWornLightProxy);
                GenSpawn.Spawn(proxy, cell, map, WipeMode.Vanish);
                e = new LightEntry { Proxy = proxy, Cell = cell };
                entries[key] = e;
            }
            else if (e.Cell != cell)
            {
                e.Proxy.Position = cell;
                e.Cell = cell;
                moved = true;
            }

            CompGlower glower = e.Proxy.TryGetComp<CompGlower>();
            if (glower != null)
            {
                // LIGHT_LEDGER_ONE_1: radius as the light ledger's base; the pawn as its carrier, so another mod can ask
                // "is this pawn carrying a light" (DEEPFIRE_WORLD_LIGHT_1 d: no lacquer cloak while glowing)
                glower.GlowColor = new ColorInt(color);
                LightLedger.SetBase(glower, radius);
                LightLedger.SetCarrier(glower, key.Pawn);
                // a moved light re-registers at its new cell even when neither colour nor radius changed
                // (GlowLight caches its position at registration)
                if (moved) glower.ForceRegister(map);
            }
        }

        private void MoveLight(LightEntry e, IntVec3 cell)
        {
            e.Proxy.Position = cell;
            e.Cell = cell;
            e.Proxy.TryGetComp<CompGlower>()?.ForceRegister(map);
        }

        private void ClearWornState()
        {
            wornPawns.Clear();
            wornSweptOnce = false;
        }
    }
}
