// MOVINGDUNES_COVERAGE_GAPS_1 -- live proof hooks for the north-star script (jawa/static_call).
// ProofMath runs the SHIPPED pure rules (transport attempts, influx debt, plant-choke sizing, wind-lock gate and
// bearing, clear-sand yield) under fixed settings; ProofBury drives the real burial API and, on a dune-field map, the
// real burial gate with burialEnabled on and off; ProofMove runs real transport batches on a dune-field map and counts
// the cells whose sand changed (depths restored). Settings restored in finally.
using System.Collections.Generic;
using System.Globalization;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.MovingDunes
{
    public static class MovingDunesProof
    {
        private static string F(float v) => v.ToString("0.####", CultureInfo.InvariantCulture);

        /// <summary>"mat=.. att1=.. att2=.. att05=.. infl_base1=.. infl_base2=.. infl_loss1=.. infl_loss2=.. choke1=.. choke2=..
        /// dmg_a=.. dmg_b=.. lock_tt=.. lock_ft=.. lock_tf=.. lock_tn=.. yield_on=.. yield_x2=.. yield_off=..
        /// bear_n=.. bear_e=.. wind_away_n=.. wind_toward_n=.. wind_away_e=.." (all derived from the shipped functions).</summary>
        public static string ProofMath(string args)
        {
            try
            {
                RM_DuneMaterialDef m = DefDatabase<RM_DuneMaterialDef>.GetNamedSilentFail("RM_Dunes_Sand");
                if (m == null) return "ERROR no RM_Dunes_Sand material";
                const int cells = 62500;
                string s = "mat=" + m.defName
                    + " att1=" + MapComponent_DuneField.TransportAttempts(m, cells, 1f)
                    + " att2=" + MapComponent_DuneField.TransportAttempts(m, cells, 2f)
                    + " att05=" + MapComponent_DuneField.TransportAttempts(m, cells, 0.5f)
                    + " infl_base1=" + F(MapComponent_DuneField.InfluxDebtDelta(m, 0f, 1f, 1f))
                    + " infl_base2=" + F(MapComponent_DuneField.InfluxDebtDelta(m, 0f, 1f, 2f))
                    + " infl_loss1=" + F(MapComponent_DuneField.InfluxDebtDelta(m, 10f, 1f, 1f) - MapComponent_DuneField.InfluxDebtDelta(m, 0f, 1f, 1f))
                    + " infl_loss2=" + F(MapComponent_DuneField.InfluxDebtDelta(m, 10f, 1f, 2f) - MapComponent_DuneField.InfluxDebtDelta(m, 0f, 1f, 2f))
                    + " choke1=" + MapComponent_DuneField.ChokeSamples(m, cells, 1f)
                    + " choke2=" + MapComponent_DuneField.ChokeSamples(m, cells, 2f)
                    + " dmg_a=" + MapComponent_DuneField.ChokeDamage(100f, 3f, 2f)
                    + " dmg_b=" + MapComponent_DuneField.ChokeDamage(1f, 3f, 50f);
                DuneFieldExtension locks = new DuneFieldExtension { lockBearingToSubstellar = true };
                DuneFieldExtension free = new DuneFieldExtension { lockBearingToSubstellar = false };
                s += " lock_tt=" + MapComponent_DuneField.WindLockApplies(true, locks)
                    + " lock_ft=" + MapComponent_DuneField.WindLockApplies(false, locks)
                    + " lock_tf=" + MapComponent_DuneField.WindLockApplies(true, free)
                    + " lock_tn=" + MapComponent_DuneField.WindLockApplies(true, null)
                    + " yield_on=" + F(Patch_ClearSand_Yield.YieldAmount(true, 0.5f, 6f, 1f))
                    + " yield_x2=" + F(Patch_ClearSand_Yield.YieldAmount(true, 0.5f, 6f, 2f))
                    + " yield_off=" + F(Patch_ClearSand_Yield.YieldAmount(false, 0.5f, 6f, 1f))
                    + " bear_n=" + F(DuneWindBearing.SunBearingDegrees(0f, 0f, 45f, 0f))
                    + " bear_e=" + F(DuneWindBearing.SunBearingDegrees(0f, 0f, 0f, 90f))
                    + " wind_away_n=" + DuneWindBearing.WindDirFromSunBearing(0f, false)
                    + " wind_toward_n=" + DuneWindBearing.WindDirFromSunBearing(0f, true)
                    + " wind_away_e=" + DuneWindBearing.WindDirFromSunBearing(90f, false);
                return s;
            }
            catch (System.Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
        }

        private static Thing Fresh(Map map, IntVec3 cell)
        {
            Thing t = ThingMaker.MakeThing(ThingDefOf.Steel);
            t.stackCount = 5;
            GenSpawn.Spawn(t, cell, map);
            return t;
        }

        /// <summary>"cell=.. cand=B cand_forbidden=B api_cache=B api_count=N api_spawned=B field=B arm_off_cache=B arm_off_spawned=B
        /// arm_on_cache=B arm_on_spawned=B". Scratch items and caches are destroyed in finally.</summary>
        public static string ProofBury(string args)
        {
            bool wasBurial = MovingDunesSettings.burialEnabled;
            Map map = Find.CurrentMap;
            List<Thing> scratch = new List<Thing>();
            IntVec3 cell = IntVec3.Invalid;
            try
            {
                if (map == null) return "ERROR no current map";
                if (!CellFinder.TryFindRandomCell(map, c => c.Standable(map) && !c.Roofed(map)
                        && !map.areaManager.Home[c] && map.thingGrid.ThingsListAtFast(c).Count == 0, out cell))
                    return "ERROR no free standable cell outside the home area";
                string s = "cell=" + cell.x + "," + cell.z;
                Thing a = Fresh(map, cell);
                scratch.Add(a);
                s += " cand=" + DuneBurialUtility.IsBurialCandidate(a, map, 0f);
                a.SetForbidden(true, false);
                s += " cand_forbidden=" + DuneBurialUtility.IsBurialCandidate(a, map, 0f);
                a.SetForbidden(false, false);
                Thing_BuriedCache cache = DuneBurialUtility.BuryThingsAt(cell, map, new List<Thing> { a });
                scratch.Add(cache);
                s += " api_cache=" + (cache != null && DuneBurialUtility.CacheAt(cell, map) == cache)
                    + " api_count=" + (cache == null ? -1 : cache.ContentsCount)
                    + " api_spawned=" + a.Spawned;
                if (cache != null && !cache.Destroyed) cache.Destroy();
                if (!a.Destroyed) a.Destroy();

                MapComponent_DuneField field = DuneFieldRegistry.Get(map);
                s += " field=" + (field != null);
                if (field == null) return s + " arm_off_cache=- arm_off_spawned=- arm_on_cache=- arm_on_spawned=-";
                Thing b = Fresh(map, cell);
                scratch.Add(b);
                MovingDunesSettings.burialEnabled = false;
                field.ProofTryBuryAt(cell);
                Thing_BuriedCache offCache = DuneBurialUtility.CacheAt(cell, map);
                s += " arm_off_cache=" + (offCache != null) + " arm_off_spawned=" + b.Spawned;
                if (offCache != null) { scratch.Add(offCache); offCache.Destroy(); }
                MovingDunesSettings.burialEnabled = true;
                field.ProofTryBuryAt(cell);
                Thing_BuriedCache onCache = DuneBurialUtility.CacheAt(cell, map);
                s += " arm_on_cache=" + (onCache != null) + " arm_on_spawned=" + b.Spawned;
                if (onCache != null) { scratch.Add(onCache); onCache.Destroy(); }
                if (!b.Destroyed) b.Destroy();
                return s;
            }
            catch (System.Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
            finally
            {
                MovingDunesSettings.burialEnabled = wasBurial;
                for (int i = 0; i < scratch.Count; i++)
                {
                    try { if (scratch[i] != null && !scratch[i].Destroyed) scratch[i].Destroy(); } catch (System.Exception) { }
                }
                if (map != null && cell.IsValid)
                {
                    Thing_BuriedCache left = DuneBurialUtility.CacheAt(cell, map);
                    if (left != null) left.Destroy();
                }
            }
        }

        /// <summary>"field=B wind=W thr=T changed=N before=X after=Y" -- runs `batches` (default 300) real transport + influx
        /// batches with the live drift slider and counts cells whose depth changed; depths restored afterwards.</summary>
        public static string ProofMove(string args)
        {
            Map map = Find.CurrentMap;
            try
            {
                if (map == null) return "ERROR no current map";
                MapComponent_DuneField field = DuneFieldRegistry.Get(map);
                if (field == null || field.Material == null) return "field=False";
                int batches = 300;
                int parsed;
                if (!string.IsNullOrEmpty(args) && int.TryParse(args.Trim(), out parsed) && parsed > 0) batches = parsed;
                SandGrid grid = map.sandGrid;
                int n = map.cellIndices.NumGridCells;
                float[] before = new float[n];
                for (int i = 0; i < n; i++) before[i] = grid.GetDepth(map.cellIndices.IndexToCell(i));
                float totalBefore = grid.TotalDepth;
                field.DebugRunBatches(batches);
                int changed = 0;
                float totalAfter = grid.TotalDepth;
                for (int i = 0; i < n; i++)
                {
                    IntVec3 c = map.cellIndices.IndexToCell(i);
                    if (Mathf.Abs(grid.GetDepth(c) - before[i]) > 1e-4f)
                    {
                        changed++;
                        grid.SetDepth(c, before[i]);
                    }
                }
                return "field=True wind=" + F(map.windManager.WindSpeed) + " thr=" + F(field.Material.windSpeedThreshold)
                    + " changed=" + changed + " before=" + F(totalBefore) + " after=" + F(totalAfter) + " batches=" + batches;
            }
            catch (System.Exception e)
            {
                return "ERROR " + e.GetType().Name + ": " + e.Message;
            }
        }
    }
}
