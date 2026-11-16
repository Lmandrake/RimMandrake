#if RM_PROOFS
// Proof build only (RM_PROOFS). RIMMANDRAKE_FIX_DRY_PIT_HAULER_DESCENT_SWIMS_HID_IT: sc_pit_fetch's hauler never climbed
// down the portable ladder into the dry pit (visit 2). PitProbe("pit_goods_fetch") reads, on the staged scene, every gate
// between the hauler and the pit-floor steel: the haul job offer, vanilla reachability, FlowWorks' reach veto and route
// planner, the ladder, and the climb depths, so the failing gate is measured instead of guessed.
using System;
using System.Linq;
using System.Reflection;
using System.Text;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.ExplosiveKnockback
{
    public static partial class RM_KnockbackProof
    {
        /// <summary>PitProbe("pit_goods_fetch") -> one line of key=value reads for the hauler h and the steel st.</summary>
        public static string PitProbe(string name)
        {
            bool log = name != null && name.EndsWith("+log");
            name = log ? name.Substring(0, name.Length - 4) : name;
            if (!scenes.TryGetValue(name ?? "", out Scene s))
            {
                return "INVALID " + name + " not staged";
            }
            Pawn h = s.things.TryGetValue("h", out Thing ht) ? ht as Pawn : null;
            Thing st = s.things.TryGetValue("st", out Thing t) ? t : null;
            if (h == null || st == null || !h.Spawned || Map == null)
            {
                return "INVALID " + name + " hauler or steel missing (h=" + (h != null) + " hSpawned=" + (h != null && h.Spawned)
                    + " hDead=" + (h != null && h.Dead) + " hHolder=" + h?.ParentHolder + " st=" + (st != null) + " stSpawned="
                    + (st != null && st.Spawned) + " stDestroyed=" + (st != null && st.Destroyed) + " stHolder=" + st?.ParentHolder
                    + ")";
            }
            if (log && h.jobs != null)
            {
                h.jobs.debugLog = true;     // every job start/end of the hauler, with its end condition, into Player.log
            }
            var sb = new StringBuilder("PROBE " + name);
            Kv("carrying", () => h.carryTracker?.CarriedThing?.LabelShort ?? "-");
            Kv("toil", () => h.jobs?.curDriver?.CurToilIndex);
            Kv("moving", () => h.pather != null && h.pather.Moving);
            Kv("dest", () => h.pather?.Destination.Cell.x + "," + h.pather?.Destination.Cell.z);
            Kv("next", () => h.pather?.nextCell.x + "," + h.pather?.nextCell.z);
            Kv("pathLeft", () => h.pather?.curPath?.NodesLeftCount);
            Kv("jobCount", () => h.CurJob?.count);
            Kv("hDepth", () => RM_KnockbackCompat.ClimbDepthAt(Map, h.Position));
            Kv("d13_13", () => RM_KnockbackCompat.ClimbDepthAt(Map, O(s, 1, 1)));
            Kv("lastJobEnd", () => h.jobs?.curDriver?.ended);
            void Kv(string k, Func<object> f)
            {
                string v;
                try
                {
                    v = Convert.ToString(f());
                }
                catch (Exception ex)
                {
                    v = "EXC:" + ex.GetType().Name + ":" + (ex.InnerException?.Message ?? ex.Message);
                }
                sb.Append(' ').Append(k).Append('=').Append((v ?? "null").Replace(' ', '_'));
            }
            Map map = Map;
            Kv("tick", () => Find.TickManager.TicksGame);
            Kv("h", () => h.Position.x + "," + h.Position.z);
            Kv("job", () => h.CurJobDef?.defName);
            Kv("jobTarget", () => h.CurJob?.targetA.ToString());
            Kv("st", () => st.Spawned ? st.Position.x + "," + st.Position.z : "unspawned");
            Kv("stCount", () => st.stackCount);
            Thing corpse = s.things.TryGetValue("corpse", out Thing ct) ? ct : null;
            Kv("corpse", () => corpse == null ? "none" : corpse.Spawned ? corpse.Position.x + "," + corpse.Position.z
                : corpse.Destroyed ? "destroyed" : "held:" + corpse.ParentHolder);
            Kv("corpseHaul", () => corpse == null ? "-" : (StoreUtility.TryFindBestBetterStoreCellFor(corpse, h, map,
                StoragePriority.Unstored, h.Faction, out IntVec3 cc, true) ? cc.x + "," + cc.z : "none") + "/forbidden="
                + corpse.IsForbidden(h) + "/reach=" + h.CanReach(corpse, PathEndMode.ClosestTouch, Danger.Deadly));
            Kv("reserver", () =>
            {
                Pawn r = map.reservationManager.FirstRespectedReserver(st, h);
                return r == null ? "-" : r.LabelShort + "/" + r.CurJobDef?.defName + (r == h ? "/self" : "");
            });
            Kv("freeColonists", () => map.mapPawns.FreeColonistsSpawned.Count);
            Kv("hostiles", () => map.mapPawns.AllPawnsSpawned.Count(x => x.HostileTo(Faction.OfPlayer) && !x.Downed));
            Kv("hostileNames", () => string.Join("|", map.mapPawns.AllPawnsSpawned.Where(x => x.HostileTo(Faction.OfPlayer)
                && !x.Downed).Take(4).Select(x => x.def.defName + "@" + x.Position.x + "," + x.Position.z)));
            Kv("hThreat", () => h.mindState?.meleeThreat?.LabelShort ?? "-");
            Kv("haulers", () => string.Join("|", map.mapPawns.FreeColonistsSpawned.Where(x => x.CurJob != null
                && (x.CurJob.targetA.Thing == st || x.CurJob.targetB.Thing == st)).Select(x => x.LabelShort + "/" + x.CurJobDef.defName)));
            Kv("stForbidden", () => st.IsForbidden(h));
            Kv("haulActive", () => h.workSettings != null && h.workSettings.WorkIsActive(WorkTypeDefOf.Hauling));
            Kv("listed", () => map.listerHaulables.ThingsPotentiallyNeedingHauling().Contains(st));
            Kv("canHaulFast", () => HaulAIUtility.PawnCanAutomaticallyHaulFast(h, st, false));
            Kv("storeCell", () => StoreUtility.TryFindBestBetterStoreCellFor(st, h, map, StoragePriority.Unstored, h.Faction,
                out IntVec3 c, true) ? c.x + "," + c.z : "none");
            Kv("canReach", () => h.CanReach(st, PathEndMode.ClosestTouch, Danger.Deadly));
            Kv("canReachPawnless", () => map.reachability.CanReach(h.Position, st, PathEndMode.ClosestTouch,
                TraverseParms.For(TraverseMode.PassDoors)));
            Kv("canReserve", () => h.CanReserve(st));
            Kv("workGiver", () =>
            {
                var wg = DefDatabase<WorkGiverDef>.GetNamedSilentFail("HaulGeneral")?.Worker as WorkGiver_Scanner;
                if (wg == null)
                {
                    return "no HaulGeneral";
                }
                Job j = wg.JobOnThing(h, st, false);
                return wg.HasJobOnThing(h, st, false) + "/" + (j?.def?.defName ?? "nojob") + "/" + JobFailReason.Reason;
            });
            Type trap = AccessTools.TypeByName("RimMandrake.FlowWorks.RM_SuperdeepTrap");
            Kv("relativeVeto", () => AccessTools.Method(trap, "RelativeVeto")?.Invoke(null, new object[]
                { map, h.Position, new LocalTargetInfo(st), PathEndMode.ClosestTouch, h }));
            Kv("relativeVetoPawnless", () => AccessTools.Method(trap, "RelativeVeto")?.Invoke(null, new object[]
                { map, h.Position, new LocalTargetInfo(st), PathEndMode.ClosestTouch, null }));
            Type pp = AccessTools.TypeByName("RimMandrake.FlowWorks.RM_PitPathing");
            Kv("route", () => AccessTools.Method(pp, "ProofRoute")?.Invoke(null, new object[] { h, st.Position }));
            Kv("path", () =>
            {
                using (PawnPath p = map.pathFinder.FindPathNow(h.Position, st, h, null, PathEndMode.ClosestTouch))
                {
                    return p == null || !p.Found ? "none" : p.NodesLeftCount + "nodes/cost" + p.TotalCost;
                }
            });
            Type joins = AccessTools.TypeByName("RimMandrake.FlowWorks.RM_ClimbJoins");
            MethodInfo lowered = joins == null ? null : AccessTools.Method(joins, "LoweredLadderAt", new[] { typeof(Map), typeof(IntVec3) });
            foreach (int dx in new[] { 1, 2, 3, 4, 5 })
            {
                IntVec3 c = O(s, dx, 0);
                Kv("d" + dx, () => RM_KnockbackCompat.ClimbDepthAt(map, c));
                Kv("lad" + dx, () =>
                {
                    Thing l = c.GetThingList(map).FirstOrDefault(x => x.def.defName.StartsWith("RM_Ladder"));
                    return l == null ? "-" : l.def.defName + "@" + l.Rotation.ToStringHuman() + "/lowered="
                        + (lowered?.Invoke(null, new object[] { map, c }));
                });
            }
            return sb.ToString();
        }
    }
}
#endif
