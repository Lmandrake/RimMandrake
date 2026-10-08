using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // GELATINOUSSLIME_TITAN_CHUNK_BOMB_1. The existing RM_TitanoslimeChunk (SealBreach) is also a thrown
    // grenade: on landing it drenches everyone in the radius to a late stage of slimification and turns the
    // ground to slime for a day. Off the body it shrinks (CompChunkShelf + MapComponent_ChunkShelf), so it is a
    // carried, timed weapon and never a stockpile. [INVENTED] numbers throughout.
    public static class ChunkBombUtility
    {
        public const float BurstRadius = 3.9f;
        // Stage 2 "half absorbed": holds in ordinary country, only dry ground and the antidote undo it.
        public const float DrenchSeverity = RM_SlimeLadder.DrenchSeverity;
        public const int SlimeGroundTicks = 60000;
        public const int ShelfSweepTicks = 250;
        public const float TicksPerDay = 60000f;

        public static ThingDef Chunk
        {
            get { return DefDatabase<ThingDef>.GetNamedSilentFail("RM_TitanoslimeChunk"); }
        }

        public static int ShelfTicks
        {
            get { return RM_SlimeWorld.ShelfTicks(SlimeSettings.chunkShelfDays, TicksPerDay); }
        }

        public static void Burst(Map map, IntVec3 centre)
        {
            if (map == null) return;
            List<string> drenched = new List<string>();
            List<Pawn> hit = new List<Pawn>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(centre, BurstRadius, true))
            {
                if (!c.InBounds(map)) continue;
                List<Thing> things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                {
                    Pawn p = things[i] as Pawn;
                    if (p == null || p.Dead || hit.Contains(p)) continue;
                    hit.Add(p);
                    if (Drench(p)) drenched.Add(p.LabelShortCap);
                }
            }
            MapComponent_ChunkBurst mc = map.GetComponent<MapComponent_ChunkBurst>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(centre, BurstRadius, true))
            {
                if (!c.InBounds(map)) continue;
                if (SlimeDefs.SlimeSmear != null && c.Walkable(map)) FilthMaker.TryMakeFilth(c, map, SlimeDefs.SlimeSmear);
                if (mc != null) mc.Convert(c);
            }
            FleckMaker.ThrowDustPuffThick(centre.ToVector3Shifted(), map, 3f, new Color(0.35f, 0.65f, 0.25f));
            string who = drenched.Count == 0 ? "no one" : string.Join(", ", drenched.ToArray());
            Messages.Message("The titanoslime chunk bursts. Drenched: " + who + ".", new TargetInfo(centre, map),
                drenched.Count == 0 ? MessageTypeDefOf.NeutralEvent : MessageTypeDefOf.ThreatBig, false);
        }

        // True when the pawn was drenched. No armour check; only resistance (identity or the gene) stops it.
        public static bool Drench(Pawn p)
        {
            if (!SlimeSettings.slimificationEnabled || SlimeDefs.Slimification == null) return false;
            if (SlimeUtility.IsResistant(p) || p.health == null) return false;
            Hediff h = p.health.hediffSet.GetFirstHediffOfDef(SlimeDefs.Slimification);
            if (h == null) h = p.health.AddHediff(SlimeDefs.Slimification);
            if (h == null) return false;
            h.Severity = RM_SlimeLadder.Drench(h.Severity);
            return true;
        }
    }

    // The thrown chunk. base.Impact destroys the projectile and clears Map/Position, so snapshot first.
    public class Projectile_SlimeChunk : Projectile
    {
        protected override void Impact(Thing hitThing, bool blockedByShield = false)
        {
            Map map = Map;
            IntVec3 cell = Position;
            base.Impact(hitThing, blockedByShield);
            if (map == null) return;
            if (!SlimeSettings.chunkBomb)
            {
                Messages.Message("The chunk lands and sits inert.", new TargetInfo(cell, map), MessageTypeDefOf.RejectInput, false);
                return;
            }
            ChunkBombUtility.Burst(map, cell);
        }
    }

    public class CompProperties_ChunkShelf : CompProperties
    {
        public CompProperties_ChunkShelf() { compClass = typeof(CompChunkShelf); }
    }

    // Remembers when the chunk left the body. Expiry is enforced by MapComponent_ChunkShelf, because items
    // in an inventory or a hand are not ticked.
    public class CompChunkShelf : ThingComp
    {
        public int born = -1;

        public override void PostPostMake()
        {
            base.PostPostMake();
            born = Find.TickManager != null ? Find.TickManager.TicksGame : -1;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref born, "born", -1);
        }

        public override string CompInspectStringExtra()
        {
            if (born < 0) return null;
            int left = born + ChunkBombUtility.ShelfTicks - Find.TickManager.TicksGame;
            return "Keeps for " + Mathf.Max(0f, left / ChunkBombUtility.TicksPerDay).ToString("0.0") + " more days";
        }
    }

    public class MapComponent_ChunkShelf : MapComponent
    {
        public MapComponent_ChunkShelf(Map map) : base(map) { }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % ChunkBombUtility.ShelfSweepTicks != 0) return;
            ThingDef def = ChunkBombUtility.Chunk;
            if (def == null) return;
            int now = Find.TickManager.TicksGame;
            int shelf = ChunkBombUtility.ShelfTicks;
            List<Thing> expired = new List<Thing>();
            List<Thing> all = new List<Thing>(map.listerThings.ThingsOfDef(def));
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p.inventory != null)
                    for (int j = 0; j < p.inventory.innerContainer.Count; j++)
                        if (p.inventory.innerContainer[j].def == def) all.Add(p.inventory.innerContainer[j]);
                if (p.equipment != null)
                    foreach (ThingWithComps e in p.equipment.AllEquipmentListForReading)
                        if (e.def == def) all.Add(e);
            }
            for (int i = 0; i < all.Count; i++)
            {
                CompChunkShelf comp = all[i].TryGetComp<CompChunkShelf>();
                if (comp == null) continue;
                if (RM_SlimeWorld.ShelfSweep(ref comp.born, now, shelf)) expired.Add(all[i]);
            }
            for (int i = 0; i < expired.Count; i++)
            {
                Thing t = expired[i];
                IntVec3 pos = t.PositionHeld;
                if (t.Spawned && SlimeDefs.SlimeSmear != null) FilthMaker.TryMakeFilth(pos, map, SlimeDefs.SlimeSmear);
                Messages.Message("A titanoslime chunk has run to slime.", new TargetInfo(pos, map), MessageTypeDefOf.NeutralEvent, false);
                t.Destroy(DestroyMode.Vanish);
            }
        }
    }

    // Ground the burst turned to slime for a while; reverts when the day is up.
    public class MapComponent_ChunkBurst : MapComponent
    {
        private List<IntVec3> cells = new List<IntVec3>();
        private List<TerrainDef> originals = new List<TerrainDef>();
        private List<int> until = new List<int>();

        public MapComponent_ChunkBurst(Map map) : base(map) { }

        public void Convert(IntVec3 c)
        {
            TerrainDef mud = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_Slime_Mud");
            if (mud == null) return;
            TerrainDef cur = map.terrainGrid.TerrainAt(c);
            // Only open natural ground: not built floor, not water, not already slime.
            if (!RM_SlimeWorld.CanConvertGround(cur != null, cur != null && cur.natural, cur != null && cur.IsWater, cur != null && cur.HasTag(SlimeDefs.SlimeTerrainTag),
                    map.terrainGrid.FoundationAt(c) != null && map.terrainGrid.FoundationAt(c) != cur)) return;
            map.terrainGrid.SetTerrain(c, mud);
            cells.Add(c);
            originals.Add(cur);
            until.Add(Find.TickManager.TicksGame + ChunkBombUtility.SlimeGroundTicks);
        }

        public override void MapComponentTick()
        {
            if (cells.Count == 0 || Find.TickManager.TicksGame % ChunkBombUtility.ShelfSweepTicks != 0) return;
            int now = Find.TickManager.TicksGame;
            TerrainDef mud = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_Slime_Mud");
            for (int i = cells.Count - 1; i >= 0; i--)
            {
                if (now < until[i]) continue;
                if (map.terrainGrid.TerrainAt(cells[i]) == mud) map.terrainGrid.SetTerrain(cells[i], originals[i]);
                cells.RemoveAt(i); originals.RemoveAt(i); until.RemoveAt(i);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref cells, "cells", LookMode.Value);
            Scribe_Collections.Look(ref originals, "originals", LookMode.Def);
            Scribe_Collections.Look(ref until, "until", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (cells == null || originals == null || until == null || cells.Count != originals.Count || cells.Count != until.Count)
                { cells = new List<IntVec3>(); originals = new List<TerrainDef>(); until = new List<int>(); }
            }
        }
    }
}
