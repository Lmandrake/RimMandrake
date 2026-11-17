#if RM_PROOFS
// Proof build only (RM_PROOFS). sc_goods_obstacles in design/concepts/ExplosiveKnockback/scenes.json (dl_goods_obstacles in
// record.json): real things in flight meeting a closed door, sandbags and deep water. Stage 6 visit 1 (2026-11-15) read it
// UNMEASURED because no entry existed (RIMMANDRAKE_WRITE_GOODS_OBSTACLES_SCENE_NAMED_NEVER_BUILT). NOT YET RUN LIVE.
// Offline check: selftest_explosiveknockback_goods_obstacles.py. Command: version/test_table.json.
using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.ExplosiveKnockback
{
    public static partial class RM_KnockbackProof
    {
        // ── sc_goods_obstacles: goods_obstacles (and its control goods_obstacles_control) ────────────

        /// <summary>The three lanes, each a component one cell east of its own grenade, five cells apart so no grenade
        /// reaches another lane: D a closed door two cells on (walls either side), S a sandbag line two cells on with open
        /// floor beyond, W deep water two cells on.</summary>
        private static readonly string[] ObstacleLanes = { "D", "S", "W" };
        private static readonly int[] ObstacleLaneZ = { 0, 5, -5 };

        /// <summary>Main: lane D's stack rebounds off the door with ReboundCells(left, goodsReboundKeepPercent) cells (about 0.7)
        /// and ends on the blast side, the door still closed; lane S's stack passes over the sandbags and lands beyond them;
        /// lane W's stack rests on the last cell before the water, spawned and unfogged, never in it. Every lane: zero
        /// despawn-spawn pairs in the thing trace, no carrier left. Control (_control): the obstacles left out, each stack
        /// lands on its kernel-planned open-floor cell beyond where the obstacle stood. Each start is asserted from the
        /// kernel plan (RM_KnockbackMath.Resolve on the live grid) and reads INVALID when it would not reach the obstacle.</summary>
        private static string GoodsObstacles(Scene s)
        {
            bool control = s.name.EndsWith("_control");
            // flyingGoods and goodsRebound are on, and restored, from Build's goods_obstacles case (RM_KnockbackProof.cs)
            for (int i = 0; i < ObstacleLanes.Length; i++)
            {
                string k = ObstacleLanes[i];
                int z = ObstacleLaneZ[i];
                Item(s, k, "ComponentIndustrial", 1, O(s, 1, z));
                if (control)
                {
                    continue;
                }
                if (k == "D")
                {
                    s.things["door"] = Build("Door", O(s, 3, z), "WoodLog");
                    Build("Wall", O(s, 3, z + 1), "BlocksGranite");
                    Build("Wall", O(s, 3, z - 1), "BlocksGranite");
                }
                else if (k == "S")
                {
                    for (int dz = -1; dz <= 1; dz++)
                    {
                        Build("Sandbags", O(s, 3, z + dz), "Cloth");
                    }
                }
                else
                {
                    for (int dx = 3; dx <= 6; dx++)
                    {
                        for (int dz = -1; dz <= 1; dz++)
                        {
                            Map.terrainGrid.SetTerrain(O(s, dx, z + dz), TerrainDefOf.WaterDeep);
                        }
                    }
                }
            }
            // the kernel plan of each stack, exactly as the hook will walk it (direction start - centre = +x)
            KbSettings ks = RimMandrakeExplosiveKnockbackSettings.Kernel();
            for (int i = 0; i < ObstacleLanes.Length; i++)
            {
                string k = ObstacleLanes[i];
                Thing t = s.things[k];
                int want = WantCellsFrom(s, k, O(s, 0, ObstacleLaneZ[i]), 2.9f);   // each lane blasts at its own centre (visit 2: from s.o, S and W read 0)
                if (want < 1)
                {
                    return "lane " + k + " component would not be thrown (want=0)";
                }
                float mass = t.GetStatValue(StatDefOf.Mass) * t.stackCount;
                KbResult plan = RM_KnockbackMath.Resolve(new RM_MapKbGrid(Map, t, false), t.Position.x, t.Position.z, 1f, 0f, want, KbKind.Item, mass, ks);
                s.numbers[k + "_want"] = want;
                s.numbers[k + "_planX"] = plan.destX;
                s.numbers[k + "_planZ"] = plan.destZ;
                string bad = RM_KnockbackVerdicts.ObstaclePlan(k, control, plan.stop, plan.destX, s.o.x + 3, s.o.x, want,
                    RimMandrakeExplosiveKnockbackSettings.goodsReboundKeepPercent, out int back);   // s.o.x + 3: the obstacle's column
                if (bad != null)
                {
                    return bad;
                }
                if (!control && k == "D")
                {
                    s.numbers["D_back"] = back;
                }
            }
            TraceGoods(s, ObstacleLanes, 600);
            if (!s.numbers.ContainsKey("traceRows0"))
            {
                return "the thing trace took no test row before the blasts";
            }
            foreach (int z in ObstacleLaneZ)
            {
                Blast(O(s, 0, z), 2.9f);
            }
            s.verdict = sc =>
            {
                var parts = new List<string>();
                bool all = true;
                for (int i = 0; i < ObstacleLanes.Length; i++)
                {
                    string k = ObstacleLanes[i];
                    int z = ObstacleLaneZ[i];
                    Thing t = sc.things[k];
                    string m = Moved(sc, k, out Thing tt, out int cells);
                    int hops = (int)GoodsNum(sc, k + "_hops");
                    int hidden = (int)GoodsNum(sc, k + "_hidden");
                    int inWater = (int)GoodsNum(sc, k + "_inWater");
                    bool rest = tt.Spawned && CarrierOf(tt.Map, t) == null;
                    bool flew = ForThing(sc, "item_move", t).Any(r => Equals(r["flying"], true));
                    var plan = new IntVec3((int)sc.numbers[k + "_planX"], 0, (int)sc.numbers[k + "_planZ"]);
                    string why;
                    bool bounced = false, closed = false, dry = false, visible = false;
                    if (control)
                    {
                        why = " plan=" + plan.x + "," + plan.z;
                    }
                    else if (k == "D")
                    {
                        var rb = ForThing(sc, "item_rebound", t);
                        bounced = rb.Count > 0 && RM_KnockbackVerdicts.DoorBounced(rb.Count, (string)rb[0]["hit"], Convert.ToInt32(rb[0]["left"]),
                            Convert.ToInt32(rb[0]["cells"]), RimMandrakeExplosiveKnockbackSettings.goodsReboundKeepPercent);
                        Thing door = sc.things["door"];
                        closed = door.Spawned && door is Building_Door bd && !bd.Open;
                        why = " back=" + sc.numbers["D_back"] + " keep%=" + RimMandrakeExplosiveKnockbackSettings.goodsReboundKeepPercent + " doorClosed=" + closed
                              + (rb.Count > 0 ? " [" + Rec(rb[0]) + "]" : " no item_rebound");
                    }
                    else if (k == "S")
                    {
                        why = " (sandbags at x+3)";
                    }
                    else
                    {
                        dry = rest && tt.Position.GetTerrain(tt.Map) != TerrainDefOf.WaterDeep;
                        visible = rest && !tt.Position.Fogged(tt.Map);
                        why = " (water from x+3) visible=" + visible + " inWater=" + inWater;
                    }
                    bool ok = RM_KnockbackVerdicts.ObstacleLane(k, control, rest, flew, tt.Position.x, tt.Position.z, plan.x, plan.z, sc.o.x + 3,
                        sc.o.z + z, bounced, closed, dry, visible, inWater, hops, hidden);
                    all &= ok;
                    parts.Add(k + (ok ? " ok " : " BAD ") + m + " want=" + sc.numbers[k + "_want"] + " flying=" + flew + " atRest=" + rest
                              + " hops=" + hops + " hidden=" + hidden + why);
                }
                return Result(sc, all, string.Join("; ", parts) + " traceRows=" + GoodsNum(sc, "traceRows") + " (step up to 600 ticks)");
            };
            return null;
        }

        private static float GoodsNum(Scene s, string key) => s.numbers.TryGetValue(key, out float v) ? v : 0f;

        /// <summary>The thing trace for loose stacks: one row now (traceRows0, the test row before the blasts) and one per tick
        /// stagedTick+1..ticks. A row reads each stack as spawned (its cell), in a knockback carrier (the carrier's drawn
        /// cell) or neither. Counts key_hops (a spawned stack on a new cell with no carrier row since its last spawned row: a
        /// despawn-spawn pair, the old hop), key_hidden (neither spawned, in a carrier nor destroyed), key_inWater (spawned or
        /// drawn on deep water), key_restTick (its last landing). A stale action after a reload sees another map and does nothing.</summary>
        private static void TraceGoods(Scene s, string[] keys, int ticks)
        {
            Map m0 = Map;
            var last = new Dictionary<string, IntVec3>();
            var flown = new HashSet<string>();
            Action<int> row = d =>
            {
                foreach (string k in keys)
                {
                    Thing t = s.things[k];
                    if (t.Destroyed && t.ParentHolder == null)
                    {
                        continue;
                    }
                    RM_ThingFlyer_Knockback c = CarrierOf(m0, t);
                    if (c != null && c.Spawned && !t.Spawned)
                    {
                        flown.Add(k);
                        IntVec3 drawn = c.DrawPos.ToIntVec3();
                        if (drawn.InBounds(m0) && drawn.GetTerrain(m0) == TerrainDefOf.WaterDeep)
                        {
                            s.numbers[k + "_inWater"] = GoodsNum(s, k + "_inWater") + 1;
                        }
                    }
                    else if (t.Spawned)
                    {
                        if (last.TryGetValue(k, out IntVec3 was) && was != t.Position && !flown.Contains(k))
                        {
                            s.numbers[k + "_hops"] = GoodsNum(s, k + "_hops") + 1;
                        }
                        if (flown.Remove(k))
                        {
                            s.numbers[k + "_restTick"] = d;
                        }
                        last[k] = t.Position;
                        if (t.Position.GetTerrain(m0) == TerrainDefOf.WaterDeep)
                        {
                            s.numbers[k + "_inWater"] = GoodsNum(s, k + "_inWater") + 1;
                        }
                    }
                    else
                    {
                        s.numbers[k + "_hidden"] = GoodsNum(s, k + "_hidden") + 1;
                    }
                }
                s.numbers["traceRows"] = GoodsNum(s, "traceRows") + 1;
            };
            row(0);
            if (keys.All(k => s.things[k].Spawned))
            {
                s.numbers["traceRows0"] = 1;
            }
            for (int d = 1; d <= ticks; d++)
            {
                int dd = d;
                RM_MapComponent_Knockback.ProofSchedule.Add(new KeyValuePair<int, Action>(s.stagedTick + d, () =>
                {
                    if (m0 == Find.CurrentMap)
                    {
                        row(dd);
                    }
                }));
            }
        }
    }
}
#endif
