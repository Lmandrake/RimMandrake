using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_BEDAZZLE_CONTENT_1 §7 — the zuurrik, the blood-waker swarm.
    //
    // Design source: stillsand_bedazzle_review_2026-09-29.md §6 fill #1 (admitted by
    // owner card 2026-09-30). A dormant filament-swarm in the top hand of sand,
    // woken by BLOOD ON THE SAND — never by footfall and never by a clock of
    // day (the no-circadian ban). Fighting here starts a clock: kill, loot fast,
    // leave. A battle left standing becomes a zuurrik bloom.
    //
    // Mechanism. This map component polls blood filth on sand cells, on maps
    // whose biome is RM_Stillsand. When a cluster of blood cells reaches the
    // threshold it wakes a swarm there (RM_Zuurrik pawns spawned on the sand
    // beside the stain). The swarm's feeding is vanilla and shipped behaviour,
    // not code here: a carnivore diet that includes corpses, plus
    // RM_EatCleanableExtension which strips filth. The swarm never attacks the
    // unwounded (manhunterOnDamageChance 0, no melee targeting beyond defence).
    // When no blood filth and no corpse remains near the swarm it re-buries:
    // each pawn is removed with a dust puff, and the swarm that wakes next time
    // is fatter by what this one ate (saved in `fatness`). Dormant is simply
    // "not on the map", so there is nothing to find until blood wakes it.
    //
    // READABLE SIGN (no animal ever vanishes without one): a message when the
    // stain wakes ("the sand boils"), and a dust puff at every pawn's cell as it
    // re-buries.
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_Zuurrik : MapComponent
    {
        private const int PollIntervalTicks = 600;
        // Radius a stain cluster is measured in, and the radius around the swarm
        // that counts as "there is still something to strip".
        private const float ClusterRadius = 7.9f;
        private const float WatchRadius = 14.9f;
        private const int QuietPollsToBury = 3;
        private const int CooldownTicks = 15000;
        private const int MaxFatness = 12;
        private const int MaxBloodCellsScanned = 600;

        private List<Pawn> swarm = new List<Pawn>();
        private int quietPolls;
        private int bloodAtWake;
        private int fatness;
        private int lastBuryTick = -999999;

        private static List<ThingDef> bloodFilthDefs;

        public RM_MapComponent_Zuurrik(Map map) : base(map)
        {
        }

        private static List<ThingDef> BloodFilthDefs
        {
            get
            {
                if (bloodFilthDefs == null)
                {
                    bloodFilthDefs = new List<ThingDef>();
                    foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
                    {
                        if (d.category == ThingCategory.Filth && d.defName.Contains("Blood"))
                        {
                            bloodFilthDefs.Add(d);
                        }
                    }
                }
                return bloodFilthDefs;
            }
        }

        private bool Active =>
            RM_StillsandMod.settings != null
            && RM_StillsandMod.settings.zuurrikEnabled
            && map.Biome != null
            && map.Biome.defName == "RM_Stillsand";

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % PollIntervalTicks != 0 || !Active)
            {
                return;
            }
            swarm.RemoveAll(p => p == null || p.Destroyed || p.Dead || !p.Spawned);
            if (swarm.Count == 0)
            {
                quietPolls = 0;
                TryWake();
            }
            else
            {
                TryBury();
            }
        }

        private static bool OnSand(IntVec3 c, Map m)
        {
            TerrainDef t = c.GetTerrain(m);
            return t != null && t.defName.Contains("Sand");
        }

        private List<IntVec3> BloodCellsOnSand()
        {
            List<IntVec3> cells = new List<IntVec3>();
            HashSet<IntVec3> seen = new HashSet<IntVec3>();
            foreach (ThingDef def in BloodFilthDefs)
            {
                List<Thing> things = map.listerThings.ThingsOfDef(def);
                for (int i = 0; i < things.Count && cells.Count < MaxBloodCellsScanned; i++)
                {
                    IntVec3 c = things[i].Position;
                    if (OnSand(c, map) && seen.Add(c))
                    {
                        cells.Add(c);
                    }
                }
            }
            return cells;
        }

        private void TryWake()
        {
            if (Find.TickManager.TicksGame - lastBuryTick < CooldownTicks)
            {
                return;
            }
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Zuurrik");
            if (kind == null)
            {
                return;
            }
            List<IntVec3> cells = BloodCellsOnSand();
            int threshold = Mathf.Max(1, RM_StillsandMod.settings.zuurrikBloodThreshold);
            if (cells.Count < threshold)
            {
                return;
            }
            // The densest cluster: the cell with the most stained neighbours.
            IntVec3 best = IntVec3.Invalid;
            int bestCount = 0;
            for (int i = 0; i < cells.Count; i++)
            {
                int n = 0;
                for (int j = 0; j < cells.Count; j++)
                {
                    if (cells[i].DistanceToSquared(cells[j]) <= ClusterRadius * ClusterRadius)
                    {
                        n++;
                    }
                }
                if (n > bestCount)
                {
                    bestCount = n;
                    best = cells[i];
                }
            }
            if (bestCount < threshold || !best.IsValid)
            {
                return;
            }

            int count = Mathf.Clamp(3 + fatness / 2, 3, 10);
            int spawned = 0;
            for (int k = 0; k < count; k++)
            {
                if (!CellFinder.TryFindRandomCellNear(best, map, 3,
                        c => c.InBounds(map) && c.Standable(map) && OnSand(c, map), out IntVec3 cell))
                {
                    continue;
                }
                Pawn p = PawnGenerator.GeneratePawn(kind, null);
                GenSpawn.Spawn(p, cell, map);
                swarm.Add(p);
                spawned++;
            }
            if (spawned == 0)
            {
                return;
            }
            bloodAtWake = bestCount;
            quietPolls = 0;
            Messages.Message("The blood-stained sand boils. Something in it has woken to strip the stain, and what lies beside it.",
                new TargetInfo(best, map), MessageTypeDefOf.NeutralEvent, false);
        }

        private void TryBury()
        {
            // Quiet means quiet around EVERY member, not just the first one.
            for (int i = 0; i < swarm.Count; i++)
            {
                if (swarm[i] != null && swarm[i].Spawned && HasWorkNear(swarm[i].Position))
                {
                    quietPolls = 0;
                    return;
                }
            }
            quietPolls++;
            if (quietPolls < QuietPollsToBury)
            {
                return;
            }
            for (int i = 0; i < swarm.Count; i++)
            {
                Pawn p = swarm[i];
                if (p != null && p.Spawned)
                {
                    FleckMaker.ThrowDustPuff(p.Position.ToVector3Shifted(), map, 1.4f);
                    p.Destroy();
                }
            }
            swarm.Clear();
            fatness = Mathf.Min(MaxFatness, fatness + Mathf.Max(1, bloodAtWake / 5));
            lastBuryTick = Find.TickManager.TicksGame;
            quietPolls = 0;
        }

        private bool HasWorkNear(IntVec3 centre)
        {
            foreach (ThingDef def in BloodFilthDefs)
            {
                List<Thing> things = map.listerThings.ThingsOfDef(def);
                for (int i = 0; i < things.Count; i++)
                {
                    if (things[i].Position.InHorDistOf(centre, WatchRadius))
                    {
                        return true;
                    }
                }
            }
            List<Thing> corpses = map.listerThings.ThingsInGroup(ThingRequestGroup.Corpse);
            for (int i = 0; i < corpses.Count; i++)
            {
                if (corpses[i].Position.InHorDistOf(centre, WatchRadius))
                {
                    return true;
                }
            }
            return false;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref swarm, "swarm", LookMode.Reference);
            Scribe_Values.Look(ref quietPolls, "quietPolls", 0);
            Scribe_Values.Look(ref bloodAtWake, "bloodAtWake", 0);
            Scribe_Values.Look(ref fatness, "fatness", 0);
            Scribe_Values.Look(ref lastBuryTick, "lastBuryTick", -999999);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (swarm == null)
                {
                    swarm = new List<Pawn>();
                }
                swarm.RemoveAll(p => p == null);
            }
        }
    }
}
