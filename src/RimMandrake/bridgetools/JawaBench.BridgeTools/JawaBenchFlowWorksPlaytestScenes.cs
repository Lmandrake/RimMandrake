// JawaBenchFlowWorksPlaytestScenes.cs - the FlowWorks playtest runner's coverage scenes (2026-10-06).
//
// A fixed catalogue of C# scenario functions on the Approach A runner (JawaBenchFlowWorksPlaytest.cs owns the
// controller, timing, journal and verdict). No scenario language: each scene below is one iterator.
// Design: design/RimMandrake/flowworks_playtest_runner_A.md, section "Coverage scenes".
//
// Same rules as the pilot: terrain writes, Deepen(), TrySetDriverFill(), direct spawns and the vanilla dev
// "toggle power on" build FIXTURES only; the evidence route is always the production path (the flow pulse, the
// pump's own Tick, a vanilla Fire's SpawnSetup hook, the river component's own MapComponentTick, the pather).
// FlowWorks is reached strictly by reflection.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using RimWorld;
using Verse;
using Verse.AI;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private const BindingFlags QBF = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
        private const BindingFlags QSBF = BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic;
        private const string QNs = "RimMandrake.FlowWorks.";

        // ════════════════════════════════════════════════════════════════
        // reflection helpers
        // ════════════════════════════════════════════════════════════════

        private static Type QT(string fullName) => GenTypes.GetTypeInAnyAssembly(fullName);

        private static object QGet(object o, string name)
        {
            for (Type t = o.GetType(); t != null; t = t.BaseType)
            {
                FieldInfo f = t.GetField(name, QBF | BindingFlags.DeclaredOnly);
                if (f != null) return f.GetValue(o);
                PropertyInfo p = t.GetProperty(name, QBF | BindingFlags.DeclaredOnly);
                if (p != null) return p.GetValue(o, null);
            }
            throw new MissingMemberException(o.GetType().Name, name);
        }

        private static void QSet(object o, string name, object v)
        {
            for (Type t = o.GetType(); t != null; t = t.BaseType)
            {
                FieldInfo f = t.GetField(name, QBF | BindingFlags.DeclaredOnly);
                if (f != null) { f.SetValue(o, v); return; }
                PropertyInfo p = t.GetProperty(name, QBF | BindingFlags.DeclaredOnly);
                if (p != null && p.CanWrite) { p.SetValue(o, v, null); return; }
            }
            throw new MissingMemberException(o.GetType().Name, name);
        }

        /// <summary>Instance method by name and argument count, walking base types.</summary>
        private static object QCall(object o, string name, params object[] args)
        {
            for (Type t = o.GetType(); t != null; t = t.BaseType)
            {
                foreach (MethodInfo m in t.GetMethods(QBF | BindingFlags.DeclaredOnly))
                    if (m.Name == name && m.GetParameters().Length == args.Length)
                        return m.Invoke(o, args);
            }
            throw new MissingMethodException(o.GetType().Name, name);
        }

        private static object QStatic(Type t, string name)
        {
            if (t == null) return null;
            FieldInfo f = t.GetField(name, QSBF);
            if (f != null) return f.GetValue(null);
            PropertyInfo p = t.GetProperty(name, QSBF);
            return p?.GetValue(null, null);
        }

        private static Def QFluid(string defName) => GenDefDatabase.GetDefSilentFail(QT(QNs + "FluidDef"), defName, false);

        private static int QFill(PCtx c, IntVec3 x) => Convert.ToInt32(QCall(c.exc, "FillAt", x));
        private static string QFluidAt(PCtx c, IntVec3 x) => (QCall(c.exc, "FluidAt", x) as Def)?.defName;
        private static bool QSetFill(PCtx c, IntVec3 x, int f, Def fluid) => (bool)QCall(c.exc, "TrySetDriverFill", x, f, fluid);

        private static void QDig(PCtx c, IntVec3 x, int depth)
        {
            for (int i = 0; i < 6 && c.Depth(x) < depth; i++) c.Call("Deepen", x);
        }

        private static Thing QMake(ThingDef def)
        {
            Thing t = ThingMaker.MakeThing(def, def.MadeFromStuff ? GenStuff.DefaultStuffFor(def) : null);
            return t;
        }

        private static Pawn QGenPawn(PCtx c, Faction f, int salt)
        {
            Rand.PushState(c.run.seed * 104729 + f.loadID * 31 + salt);
            try
            {
                Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(f.def.basicMemberKind ?? PawnKindDefOf.Villager, f, forceGenerateNewPawn: true));
                p.equipment?.DestroyAllEquipment();
                p.inventory?.DestroyAll();
                return p;
            }
            finally { Rand.PopState(); }
        }

        private static void QGoto(Pawn p, IntVec3 dest)
        {
            Job j = JobMaker.MakeJob(JobDefOf.Goto, dest);
            j.locomotionUrgency = LocomotionUrgency.Walk;
            p.jobs.StartJob(j, JobCondition.InterruptForced);
        }

        private static void QVanish(Thing t)
        {
            if (t != null && !t.Destroyed && t.Spawned) t.Destroy(DestroyMode.Vanish);
        }

        private static Faction QFriendFaction() =>
            Find.FactionManager.RandomNonHostileFaction(allowHidden: false, allowDefeated: false, allowNonHumanlike: false);

        private static void QSetExpectedFail(PCtx c, string item) => c.expectedFailUntil = item;

        // ════════════════════════════════════════════════════════════════
        // depth_fill: every legal (D,F), D1-D4, created and read back; path cost and a crossing per state
        // ════════════════════════════════════════════════════════════════

        private static IEnumerable<PWait> ScnDepthFill(PCtx c)
        {
            c.ev["route"] = "Deepen + TrySetDriverFill (fixture) read back through DepthAt/FillAt/FluidAt; vanilla PathGrid.Cost; a Goto along each strip through the real pather";
            Map m = c.map;
            Def water = QFluid("RM_Fluid_Water");
            Faction friend = QFriendFaction();
            if (water == null || friend == null) { c.Invalid("missing " + (water == null ? "RM_Fluid_Water" : "a non-hostile humanlike faction")); yield break; }
            PathGrid pg = m.pathing.Normal.pathGrid;

            var states = new List<int[]> { new[] { 0, 0 } };
            for (int d = 1; d <= 4; d++) for (int f = 0; f <= d; f++) states.Add(new[] { d, f });
            var rows = new List<Dictionary<string, object>>();
            c.ev["states"] = rows;
            var readFails = new List<string>();
            IntVec3 near = m.Center + new IntVec3(30, 0, -30);
            Pawn walker = null;
            try
            {
                foreach (int[] st in states)
                {
                    int D = st[0], F = st[1];
                    string key = "D" + D + "F" + F;
                    c.Phase("setup");
                    if (!PFindRect(c, near, 9, 3, 2, true, out CellRect r))
                    {
                        c.Invalid("no clean 9x3 soil strip with a dry 2-cell margin for " + key);
                        yield break;
                    }
                    near = r.CenterCell + new IntVec3(0, 0, 8);
                    PClearPlants(m, r.Cells);
                    foreach (IntVec3 x in r.Cells) QDig(c, x, D);
                    if (F > 0) foreach (IntVec3 x in r.Cells) QSetFill(c, x, F, water);
                    int bad = 0;
                    foreach (IntVec3 x in r.Cells)
                    {
                        bool ok = c.Depth(x) == D && QFill(c, x) == F && (F == 0 ? QFluidAt(c, x) == null : QFluidAt(c, x) == water.defName);
                        if (!ok) bad++;
                    }
                    if (bad > 0) readFails.Add(key + ":" + bad + "/" + r.Area + " cells");
                    IntVec3 mid = r.CenterCell;
                    IntVec3 start = new IntVec3(r.minX, 0, mid.z), dest = new IntVec3(r.maxX, 0, mid.z);
                    var row = PD("state", key, "D", D, "F", F, "rect", PD("x", r.minX, "z", r.minZ, "w", r.Width, "h", r.Height),
                        "readBackBadCells", bad,
                        "terrainBase", m.terrainGrid.BaseTerrainAt(mid)?.defName, "terrainTemp", m.terrainGrid.TempTerrainAt(mid)?.defName,
                        "topTerrain", m.terrainGrid.TopTerrainAt(mid)?.defName,
                        "pathCost", pg.Cost(mid), "walkable", pg.Walkable(mid));
                    rows.Add(row);

                    // crossing: a non-player pawn walks the strip's middle row end to end
                    if (!pg.Walkable(start) || !pg.Walkable(dest)) { row["crossTicks"] = null; row["crossNote"] = "not walkable"; continue; }
                    walker = QGenPawn(c, friend, D * 10 + F);
                    GenSpawn.Spawn(walker, start, m);
                    c.Phase("exec");
                    int t0 = TicksGameSafe(), lastOrder = t0, reissues = 0;
                    Pawn wk = walker;
                    QGoto(wk, dest);
                    void Watch()
                    {
                        if (!wk.Spawned || wk.Position == dest || wk.Downed) return;
                        if (TicksGameSafe() - lastOrder >= 120 && wk.CurJobDef != JobDefOf.Goto) { reissues++; lastOrder = TicksGameSafe(); QGoto(wk, dest); }
                    }
                    PWait w = PUntil(() => !wk.Spawned || wk.Position == dest, 2500, Watch);
                    yield return w;
                    c.Phase("observe");
                    row["crossTicks"] = w.satisfied && wk.Spawned ? (object)(TicksGameSafe() - t0) : null;
                    row["crossTimedOut"] = w.timedOut;
                    row["crossReissues"] = reissues;
                    row["crossCells"] = r.Width - 1;
                    row["fillAfterCross"] = QFill(c, mid);
                    QVanish(walker); walker = null;
                }

                // illegal F > D must clamp to D (the engine's own guard, never a write past the cell)
                c.Phase("setup");
                if (!PFindRect(c, near, 1, 1, 2, true, out CellRect cr)) { c.Invalid("no clean cell for the clamp check"); yield break; }
                IntVec3 cc = cr.CenterCell;
                PClearPlants(m, new[] { cc });
                QDig(c, cc, 1);
                bool accepted = QSetFill(c, cc, 2, water);
                int clamped = QFill(c, cc);
                c.ev["clamp"] = PD("cell", PCell(cc), "D", c.Depth(cc), "asked", 2, "accepted", accepted, "fillAfter", clamped);

                // movement assertions. Route PLANNING still sees ruling 17's rising dry cost (pg.Cost), but the walk
                // itself follows the owner's 2026-10-06 ruling (FLOWWORKS_REVIEW_LOOKS_ROUND_1 item 9): "people stuck
                // inside a pit do NOT walk slowly... Only when they are climbing in or out do they move slowly." The
                // walker crosses the strip end to end AT ONE DEPTH, so its time must match the surface baseline.
                object Cost(string k) => rows.First(rw => (string)rw["state"] == k)["pathCost"];
                object Cross(string k) => rows.First(rw => (string)rw["state"] == k).TryGetValue("crossTicks", out object v) ? v : null;
                var fails = new List<string>();
                if (readFails.Count > 0) fails.Add("D/F/fluid did not read back: " + string.Join(", ", readFails));
                if (clamped != 1) fails.Add("F=2 written to a D=1 cell read back as " + clamped + " (expected clamp to 1)");
                int c0 = (int)Cost("D0F0"), c1 = (int)Cost("D1F0"), c2 = (int)Cost("D2F0"), c3 = (int)Cost("D3F0");
                if (!(c1 > c0)) fails.Add("dry D1 path cost " + c1 + " not above surface " + c0);
                if (!(c2 >= c1 && c3 >= c2)) fails.Add("dry path cost not non-decreasing D1..D3: " + c1 + "," + c2 + "," + c3);
                object x0 = Cross("D0F0");
                if (x0 == null) fails.Add("surface baseline crossing did not complete");
                else
                    foreach (string k in new[] { "D1F0", "D2F0", "D3F0" })
                    {
                        object xk = Cross(k);
                        if (xk == null) fails.Add(k + " crossing did not complete");
                        else if (Math.Abs((int)xk - (int)x0) > Math.Max(20, (int)x0 / 4))
                            fails.Add(k + " crossing along the pit floor took " + xk + " ticks against surface " + x0
                                + " (walking at one depth must be normal speed)");
                    }
                c.ev["note"] = "wet and D4 rows are recorded, not asserted (no ruled number yet)";
                if (fails.Count == 0) c.Pass("all " + states.Count + " (D,F) states read back; F clamps to D; dry planning cost rises with depth; walking along a pit floor is normal speed");
                else c.Defect(string.Join("; ", fails));
            }
            finally { QVanish(walker); }
        }

        // ════════════════════════════════════════════════════════════════
        // fire: a vanilla Fire beside tar lights it and the front advances; water does not light; detonation if defined
        // ════════════════════════════════════════════════════════════════

        private static IEnumerable<PWait> ScnFire(PCtx c)
        {
            c.ev["route"] = "vanilla Fire spawned beside the strip (FireUtility.TryStartFireIn, else the same spawn it does) -> Fire.SpawnSetup postfix -> RM_LiquidFire front";
            Map m = c.map;
            Type settings = QT(QNs + "RimMandrakeFlowWorksSettings");
            if (!(QStatic(settings, "canalFireEnabled") is bool on) || !on) { c.Invalid("canalFireEnabled is off (or unreadable)"); yield break; }
            object fire = QGet(c.exc, "LiquidFire");
            Def tar = QFluid("RM_Fluid_Tar"), water = QFluid("RM_Fluid_Water");
            if (fire == null || tar == null || water == null) { c.Invalid("RM_LiquidFire / RM_Fluid_Tar / RM_Fluid_Water not resolvable"); yield break; }
            Type fluidT = QT(QNs + "FluidDef");
            Def deton = GenDefDatabase.GetAllDefsInDatabaseForDef(fluidT).FirstOrDefault(d => QGet(d, "fireKind")?.ToString() == "Detonation");
            c.ev["fireFrontTicksPerCellTar"] = QGet(tar, "fireFrontTicksPerCell");
            c.ev["fireFrontSpeedMultiplier"] = QStatic(settings, "fireFrontSpeedMultiplier");
            c.ev["detonationFluid"] = deton?.defName;

            var cases = new List<Dictionary<string, object>>();
            c.ev["cases"] = cases;
            var fails = new List<string>();
            IntVec3 near = m.Center + new IntVec3(-30, 0, -30);
            var fluids = new List<Def> { tar, water };
            if (deton != null) fluids.Add(deton);
            foreach (Def fl in fluids)
            {
                string kind = fl == water ? "control" : fl == tar ? "fuse" : "detonation";
                c.Phase("setup");
                if (!PFindRect(c, near, 8, 1, 3, true, out CellRect r)) { c.Invalid("no clean 8x1 strip with a dry 3-cell margin (" + fl.defName + ")"); yield break; }
                near = r.CenterCell + new IntVec3(0, 0, 9);
                PClearPlants(m, r.ExpandedBy(3).ClipInsideMap(m).Cells);
                IntVec3 fireCell = new IntVec3(r.minX, 0, r.minZ);
                var strip = r.Cells.Where(x => x != fireCell).OrderBy(x => x.x).ToList();
                foreach (IntVec3 x in strip) { QDig(c, x, 1); QSetFill(c, x, 1, fl); }
                int wet = strip.Count(x => QFill(c, x) == 1 && QFluidAt(c, x) == fl.defName);
                if (wet != strip.Count) { c.Invalid(fl.defName + " strip: only " + wet + "/" + strip.Count + " cells hold the fixture fluid"); yield break; }
                var lit = new Dictionary<IntVec3, int>();
                bool Burning(IntVec3 x) => (bool)QCall(fire, "IsBurning", m, x);
                void Watch() { foreach (IntVec3 x in strip) if (!lit.ContainsKey(x) && Burning(x)) lit[x] = TicksGameSafe(); }

                c.Phase("exec");
                int t0 = TicksGameSafe();
                bool viaUtility = FireUtility.TryStartFireIn(fireCell, m, 0.5f, null);
                if (!viaUtility)
                {
                    Fire fth = (Fire)ThingMaker.MakeThing(ThingDefOf.Fire);
                    fth.fireSize = 0.5f;
                    GenSpawn.Spawn(fth, fireCell, m);
                }
                Watch();
                if (kind == "control") yield return PTicks(900, Watch);
                else yield return PUntil(() => lit.Count >= strip.Count, kind == "fuse" ? 4000 : 600, Watch);

                c.Phase("observe");
                var order = strip.Select(x => lit.TryGetValue(x, out int t) ? t - t0 : -1).ToList();
                int litCount = order.Count(t => t >= 0);
                bool monotone = true;
                for (int i = 1; i < order.Count; i++) if (order[i] >= 0 && (order[i - 1] < 0 || order[i] < order[i - 1])) monotone = false;
                var fillsAfter = strip.Select(x => QFill(c, x)).ToList();
                cases.Add(PD("fluid", fl.defName, "kind", kind, "rect", PD("x", r.minX, "z", r.minZ), "fireCell", PCell(fireCell),
                    "fireVia", viaUtility ? "FireUtility.TryStartFireIn" : "GenSpawn Fire (TryStartFireIn refused: bare cell)",
                    "cells", strip.Count, "cellsLit", litCount, "igniteTicksByDistance", order, "frontMonotone", monotone,
                    "fillsAfter", fillsAfter, "burnedLevelsTotal", QGet(fire, "BurnedLevelsTotal")));
                if (kind == "control" && litCount > 0) fails.Add("water strip caught fire (" + litCount + " cells)");
                if (kind == "fuse")
                {
                    if (order[0] < 0 || order[0] > 300) fails.Add("tar beside the fire did not light within 300 ticks (" + order[0] + ")");
                    if (litCount < strip.Count) fails.Add("tar front stalled at " + litCount + "/" + strip.Count + " cells in 4000 ticks");
                    if (!monotone) fails.Add("tar front did not advance cell by cell away from the fire: " + string.Join(",", order));
                }
                if (kind == "detonation")
                {
                    if (litCount < strip.Count) fails.Add(fl.defName + " detonation front lit only " + litCount + "/" + strip.Count + " in 600 ticks");
                    if (fillsAfter.Any(f => f > 0)) fails.Add(fl.defName + " not consumed after detonating (fills " + string.Join(",", fillsAfter) + ")");
                }

                // cleanup: put the strip out and remove the vanilla fires so the next case starts cold
                c.Phase("setup");
                QCall(fire, "ExtinguishAll", m);
                foreach (IntVec3 x in r.ExpandedBy(4).ClipInsideMap(m).Cells)
                    foreach (Thing t in x.GetThingList(m).ToList()) if (t is Fire) t.Destroy(DestroyMode.Vanish);
            }
            if (deton == null) c.ev["detonationNote"] = "no FluidDef with fireKind Detonation is defined; that case was not run";
            if (fails.Count == 0) c.Pass("vanilla fire lit tar and the front crossed the strip in order; water did not light" + (deton == null ? "; no detonating fluid defined" : "; detonation consumed"));
            else c.Defect(string.Join("; ", fails));
        }

        // ════════════════════════════════════════════════════════════════
        // pump: a powered pump moves liquid between a channel and a tank; capacity clamp; wrong-fluid refusal
        // ════════════════════════════════════════════════════════════════

        private static IEnumerable<PWait> ScnPump(PCtx c)
        {
            c.ev["route"] = "Building_LiquidPump's own Tick (250-tick cycle) -> TryDraw/TryPour -> excavation TryTakeLevel/TryPourLevel + Building_LiquidTank; power via the vanilla DEV 'toggle power on' (fixture)";
            Map m = c.map;
            ThingDef pumpDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_LiquidPump");
            ThingDef tankDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_LiquidTank");
            Def water = QFluid("RM_Fluid_Water"), tar = QFluid("RM_Fluid_Tar");
            Type liqT = QT(QNs + "LiquidTypes.LiquidDef");
            Def LiquidFor(Def fluid) => liqT == null ? null : GenDefDatabase.GetAllDefsInDatabaseForDef(liqT).FirstOrDefault(l => QGet(l, "canalFluid") == fluid);
            Def lWater = LiquidFor(water), lTar = LiquidFor(tar);
            if (pumpDef == null || tankDef == null || lWater == null || lTar == null)
            { c.Invalid("missing " + (pumpDef == null ? "RM_LiquidPump " : "") + (tankDef == null ? "RM_LiquidTank " : "") + (lWater == null ? "water LiquidDef " : "") + (lTar == null ? "tar LiquidDef" : "")); yield break; }
            Type settings = QT(QNs + "RimMandrakeFlowWorksSettings");
            if (!(QStatic(settings, "liquidPumpEnabled") is bool on) || !on) { c.Invalid("liquidPumpEnabled is off"); yield break; }

            if (!PFindRect(c, m.Center + new IntVec3(30, 0, 30), 5, 4, 2, true, out CellRect r)) { c.Invalid("no clean 5x4 pump site"); yield break; }
            PClearPlants(m, r.Cells);
            IntVec3 ch = new IntVec3(r.minX, 0, r.minZ + 1);
            IntVec3 pumpCell = new IntVec3(r.minX + 1, 0, r.minZ + 1);
            IntVec3 tankPos = IntVec3.Invalid;
            foreach (IntVec3 x in r.Cells)
            {
                CellRect o = GenAdj.OccupiedRect(x, Rot4.North, tankDef.size);
                if (o.minX == r.minX + 2 && o.minZ == r.minZ + 1) { tankPos = x; break; }
            }
            if (!tankPos.IsValid) { c.Invalid("could not place the " + tankDef.size + " tank beside the pump"); yield break; }

            Thing pump = null, tank = null;
            try
            {
                QDig(c, ch, 3);
                QSetFill(c, ch, 3, water);
                pump = QMake(pumpDef); pump.SetFaction(Faction.OfPlayer); GenSpawn.Spawn(pump, pumpCell, m, Rot4.North);
                tank = QMake(tankDef); tank.SetFaction(Faction.OfPlayer); GenSpawn.Spawn(tank, tankPos, m, Rot4.North);
                CompPowerTrader power = ((ThingWithComps)pump).GetComp<CompPowerTrader>();
                QSet(pump, "pourMode", false);
                if (power != null && power.PowerOn) power.PowerOn = false;
                int cap = (int)QGet(tank, "Capacity");
                int Units() => (int)QGet(tank, "storedUnits");
                string Liquid() => (QGet(tank, "storedLiquid") as Def)?.defName;
                int Moved() => (int)QGet(pump, "Moved");
                string Status() => QGet(pump, "lastStatus") as string;
                var steps = new List<Dictionary<string, object>>();
                c.ev["steps"] = steps;
                c.ev["layout"] = PD("channel", PCell(ch), "pump", PCell(pumpCell), "tank", PCell(tankPos), "tankCapacity", cap, "hasPowerComp", power != null);
                Dictionary<string, object> Snap(string label) =>
                    PD("step", label, "channelD", c.Depth(ch), "channelF", QFill(c, ch), "channelFluid", QFluidAt(c, ch),
                       "tankUnits", Units(), "tankLiquid", Liquid(), "pumpMoved", Moved(), "pumpStatus", Status(),
                       "powerOn", power?.PowerOn, "ticks", TicksGameSafe());
                var fails = new List<string>();

                // A. unpowered: nothing moves
                c.Phase("exec");
                yield return PTicks(600);
                c.Phase("observe");
                var a = Snap("unpowered_600"); steps.Add(a);
                if (power != null && (Moved() != 0 || QFill(c, ch) != 3 || Units() != 0)) fails.Add("unpowered pump moved liquid");

                // B. powered draw: one level channel -> tank, 5 units
                c.Phase("setup");
                if (power != null) power.PowerOn = true;
                c.Phase("exec");
                yield return PUntil(() => Units() > 0, 700);
                c.Phase("observe");
                var b = Snap("powered_draw"); steps.Add(b);
                if (Units() != 5 || Liquid() != lWater.defName || QFill(c, ch) != 2)
                    fails.Add("powered draw: expected tank 5 units of " + lWater.defName + " and channel F 2, got " + Units() + " " + Liquid() + " F " + QFill(c, ch));

                // C. capacity clamp: tank 5 short of full takes exactly one more level and then refuses
                c.Phase("setup");
                QSet(tank, "storedUnits", cap - 5);
                int movedC = Moved();
                c.Phase("exec");
                yield return PUntil(() => Units() >= cap, 700);
                yield return PTicks(600);
                c.Phase("observe");
                var cc = Snap("capacity_clamp"); steps.Add(cc);
                if (Units() != cap || QFill(c, ch) != 1 || Moved() - movedC != 1)
                    fails.Add("capacity clamp: expected tank " + cap + ", channel F 1, one move; got " + Units() + ", F " + QFill(c, ch) + ", moves " + (Moved() - movedC));

                // D. wrong fluid: tank of tar may not pour into a channel holding water
                c.Phase("setup");
                QSet(pump, "pourMode", true);
                QSet(tank, "storedLiquid", lTar);
                QSet(tank, "storedUnits", 50);
                int movedD = Moved();
                c.Phase("exec");
                yield return PTicks(600);
                c.Phase("observe");
                var dd = Snap("wrong_fluid_refused"); steps.Add(dd);
                if (QFill(c, ch) != 1 || QFluidAt(c, ch) != water.defName || Units() != 50 || Moved() != movedD)
                    fails.Add("wrong-fluid pour was not refused: channel F " + QFill(c, ch) + " " + QFluidAt(c, ch) + ", tank " + Units());

                // E. pour into an empty channel: tar goes in, tank pays 5 units a level
                c.Phase("setup");
                QSetFill(c, ch, 0, null);
                c.Phase("exec");
                yield return PUntil(() => QFill(c, ch) >= 1, 700);
                c.Phase("observe");
                var e = Snap("pour_into_empty"); steps.Add(e);
                if (QFill(c, ch) < 1 || QFluidAt(c, ch) != tar.defName || Units() != 50 - 5 * QFill(c, ch))
                    fails.Add("pour: expected tar in the channel and the tank down 5 a level; got F " + QFill(c, ch) + " " + QFluidAt(c, ch) + ", tank " + Units());

                if (power == null) c.ev["note"] = "pump def has no CompPowerTrader; the unpowered step proves nothing";
                if (fails.Count == 0) c.Pass("unpowered idle; powered draw 1 level = 5 units; tank clamps at " + cap + "; tar refused into water; tar poured into an empty channel");
                else c.Defect(string.Join("; ", fails));
            }
            finally { QVanish(pump); QVanish(tank); }
        }

        // ════════════════════════════════════════════════════════════════
        // river: the scheduled shove moves a pawn in the current; ford and ferry rope exempt
        // ════════════════════════════════════════════════════════════════

        private static IEnumerable<PWait> ScnRiver(PCtx c)
        {
            c.ev["route"] = "RM_MapComponent_RiverCurrent.MapComponentTick (scan 250 / process 15) on a pawn holding a Wait job; ford = RM_FordStones terrain beside it; ferry = two RM_FerryPost spawns";
            Map m = c.map;
            Type rcT = QT(QNs + "Rivers.RM_MapComponent_RiverCurrent");
            Type rs = QT(QNs + "Rivers.RM_RiversSettings");
            Type rm = QT(QNs + "Rivers.RM_RiverMath");
            MapComponent rc = rcT == null ? null : m.components.FirstOrDefault(x => rcT.IsInstanceOfType(x));
            if (rc == null || rs == null || rm == null) { c.Invalid("river current component / settings / math not resolvable"); yield break; }
            if (!(QStatic(rs, "CurrentActive") is bool act) || !act) { c.Invalid("river current is switched off in mod settings"); yield break; }
            if (!(bool)QGet(rc, "AnyCurrent")) { c.Invalid("no river current on this map (needs a map with a river)"); yield break; }
            int[] sx = (int[])QStatic(rm, "StepX"), sz = (int[])QStatic(rm, "StepZ");
            bool carryStrangers = QStatic(rs, "carryStrangers") is bool cs && cs;
            Faction fac = carryStrangers ? QFriendFaction() : Faction.OfPlayer;
            if (fac == null) { c.Invalid("no non-hostile faction for the swimmer"); yield break; }
            TerrainDef ford = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_FordStones");
            ThingDef post = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FerryPost");
            int Dir(IntVec3 x) => (int)QCall(rc, "FlowDirAt", x);
            bool Has(IntVec3 x) => (bool)QCall(rc, "HasCurrent", x);
            bool NearFord(IntVec3 x) => (bool)QCall(rc, "NearFord", x);
            IntVec3 Down(IntVec3 x) { int d = Dir(x); return new IntVec3(x.x + sx[d], 0, x.z + sz[d]); }
            var used = new List<IntVec3>();
            bool Usable(IntVec3 x)
            {
                if (!x.InBounds(m) || x.x < 12 || x.z < 12 || x.x >= m.Size.x - 12 || x.z >= m.Size.z - 12) return false;
                if (x.Fogged(m) || !Has(x) || !x.Standable(m) || x.GetFirstPawn(m) != null || x.GetEdifice(m) != null || NearFord(x)) return false;
                if (used.Any(u => u.DistanceTo(x) < 10)) return false;
                IntVec3 d1 = Down(x), d2 = d1.InBounds(m) && Has(d1) ? Down(d1) : IntVec3.Invalid;
                return d1.InBounds(m) && Has(d1) && d1.Standable(m) && d2.IsValid && d2.InBounds(m) && d2.Standable(m);
            }
            var candidates = m.AllCells.Where(Usable).OrderBy(x => (x - m.Center).LengthHorizontalSquared).ToList();
            IntVec3 Pick()
            {
                foreach (IntVec3 x in candidates) if (Usable(x)) { used.Add(x); return x; }
                return IntVec3.Invalid;
            }

            var cases = new List<Dictionary<string, object>>();
            c.ev["cases"] = cases;
            c.ev["swimmerFaction"] = fac.Name;
            Pawn swimmer = null; var placed = new List<Thing>(); var restore = new List<KeyValuePair<IntVec3, TerrainDef>>();
            var fails = new List<string>();
            try
            {
                IEnumerable<PWait> Swim(string label, IntVec3 at, bool expectMove)
                {
                    c.Phase("setup");
                    swimmer = QGenPawn(c, fac, cases.Count);
                    GenSpawn.Spawn(swimmer, at, m);
                    Pawn sp = swimmer;
                    void Hold() { if (sp.Spawned && sp.CurJobDef != JobDefOf.Wait && !sp.Downed) sp.jobs.StartJob(JobMaker.MakeJob(JobDefOf.Wait, 20000), JobCondition.InterruptForced); }
                    Hold();
                    var path = new List<IntVec3> { at };
                    void Watch() { Hold(); if (sp.Spawned && sp.Position != path[path.Count - 1]) path.Add(sp.Position); }
                    c.Phase("exec");
                    int t0 = TicksGameSafe();
                    int expected = Dir(at);
                    IntVec3 down = Down(at);
                    PWait w = expectMove ? PUntil(() => !sp.Spawned || sp.Position != at, 1500, Watch) : PTicks(1500, Watch);
                    yield return w;
                    if (expectMove && w.satisfied) yield return PTicks(300, Watch);
                    c.Phase("observe");
                    bool moved = path.Count > 1 || !sp.Spawned;
                    cases.Add(PD("case", label, "cell", PCell(at), "lane", QCall(rc, "LaneAt", at), "flowDir", expected,
                        "expectedFirstStep", PCell(down), "moved", moved, "ticksToFirstShove", expectMove && w.satisfied ? (object)(TicksGameSafe() - t0) : null,
                        "path", path.Select(PCell).ToList(), "spawnedAtEnd", sp.Spawned, "downed", sp.Downed));
                    if (expectMove && !moved) fails.Add(label + ": pawn in the current was not shoved within 1500 ticks");
                    if (expectMove && moved && path.Count > 1 && path[1] != down) fails.Add(label + ": first shove went to " + path[1] + ", not downstream " + down);
                    if (!expectMove && moved) fails.Add(label + ": pawn was carried although exempt (path " + string.Join(" ", path) + ")");
                    QVanish(swimmer); swimmer = null;
                }

                IntVec3 c1 = Pick();
                if (!c1.IsValid) { c.Invalid("no standable current cell with two standable cells downstream, away from fords and edges"); yield break; }
                foreach (PWait x in Swim("current_shoves", c1, true)) yield return x;

                // ford: RM_FordStones on a cell beside the swimmer (perpendicular to the flow)
                IntVec3 c2 = Pick();
                if (ford == null || !c2.IsValid) cases.Add(PD("case", "ford_exempt", "skipped", ford == null ? "RM_FordStones not defined" : "no second current cell"));
                else
                {
                    int d = Dir(c2);
                    IntVec3 side = new IntVec3(c2.x + sx[(d + 2) % 8], 0, c2.z + sz[(d + 2) % 8]);
                    restore.Add(new KeyValuePair<IntVec3, TerrainDef>(side, m.terrainGrid.TopTerrainAt(side)));
                    m.terrainGrid.SetTerrain(side, ford);
                    if (!NearFord(c2)) fails.Add("ford fixture did not read as NearFord");
                    foreach (PWait x in Swim("ford_exempt", c2, false)) yield return x;
                }

                // ferry: posts on the first standable dry bank either side, perpendicular to the flow
                IntVec3 c3 = Pick();
                IntVec3 Bank(IntVec3 from, int dir)
                {
                    for (int i = 1; i <= 40; i++)
                    {
                        IntVec3 x = new IntVec3(from.x + sx[dir] * i, 0, from.z + sz[dir] * i);
                        if (!x.InBounds(m)) return IntVec3.Invalid;
                        TerrainDef t = x.GetTerrain(m);
                        if (t != null && !t.IsWater && x.Standable(m) && x.GetEdifice(m) == null) return x;
                    }
                    return IntVec3.Invalid;
                }
                if (post == null || !c3.IsValid) cases.Add(PD("case", "ferry_exempt", "skipped", post == null ? "RM_FerryPost not defined" : "no third current cell"));
                else
                {
                    int d = Dir(c3);
                    IntVec3 b1 = Bank(c3, (d + 2) % 8), b2 = Bank(c3, (d + 6) % 8);
                    if (!b1.IsValid || !b2.IsValid) cases.Add(PD("case", "ferry_exempt", "skipped", "no dry bank within 40 cells on both sides"));
                    else
                    {
                        foreach (IntVec3 b in new[] { b1, b2 })
                        {
                            Thing pt = QMake(post); pt.SetFaction(Faction.OfPlayer); GenSpawn.Spawn(pt, b, m); placed.Add(pt);
                        }
                        bool paired = QGet(placed[0], "Partner") != null;
                        c.ev["ferry"] = PD("posts", new[] { PCell(b1), PCell(b2) }, "paired", paired, "onRope", (bool)QCall(rc, "OnRope", c3));
                        if (!paired) fails.Add("ferry posts at " + b1 + " / " + b2 + " did not pair");
                        foreach (PWait x in Swim("ferry_exempt", c3, false)) yield return x;
                    }
                }
            }
            finally
            {
                QVanish(swimmer);
                foreach (Thing t in placed) QVanish(t);
                foreach (var kv in restore) if (kv.Value != null) m.terrainGrid.SetTerrain(kv.Key, kv.Value);
            }
            if (fails.Count == 0) c.Pass("pawn in the current shoved downstream; ford and ferry rope exempt (skipped cases listed)");
            else c.Defect(string.Join("; ", fails));
        }

        // ════════════════════════════════════════════════════════════════
        // sluice: written against the RULED behaviour (FLOWWORKS_SLUICE_TWO_DOORS_1)
        // ════════════════════════════════════════════════════════════════

        private static IEnumerable<PWait> ScnSluice(PCtx c)
        {
            c.ev["route"] = "flow pulse across a 5-cell D2 channel with a flow door spawned on the middle cell (doors closed unless held open)";
            c.ev["ruling"] = "owner 2026-10-06: sealed sluice gate holds liquid when shut, passes when open; grate gate always passes";
            Map m = c.map;
            Def water = QFluid("RM_Fluid_Water");
            ThingDef sluice = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Sluice");
            ThingDef grate = DefDatabase<ThingDef>.GetNamedSilentFail("RM_SecurityGrateDoor");
            if (water == null || sluice == null || grate == null) { c.Invalid("RM_Fluid_Water / RM_Sluice / RM_SecurityGrateDoor not resolvable"); yield break; }
            var cases = new List<Dictionary<string, object>>();
            c.ev["cases"] = cases;
            var unexpected = new List<string>(); bool sealedFailed = false;
            IntVec3 near = m.Center + new IntVec3(-30, 0, 30);
            var runs = new[] { new { label = "grate_closed", def = grate, open = false, expectPass = true },
                               new { label = "sluice_shut", def = sluice, open = false, expectPass = false },
                               new { label = "sluice_open", def = sluice, open = true, expectPass = true } };
            Thing door = null;
            try
            {
                foreach (var run in runs)
                {
                    c.Phase("setup");
                    if (!PFindRect(c, near, 5, 1, 3, true, out CellRect r)) { c.Invalid("no clean 5x1 channel site (" + run.label + ")"); yield break; }
                    near = r.CenterCell + new IntVec3(0, 0, 8);
                    PClearPlants(m, r.Cells);
                    var cells = r.Cells.OrderBy(x => x.x).ToList();
                    foreach (IntVec3 x in cells) QDig(c, x, 2);
                    QSetFill(c, cells[0], 2, water); QSetFill(c, cells[1], 2, water);
                    IntVec3 gate = cells[2];
                    door = QMake(run.def); door.SetFaction(Faction.OfPlayer); GenSpawn.Spawn(door, gate, m);
                    if (run.open)
                    {
                        QSet(door, "holdOpenInt", true);
                        QCall(door, "DoorOpen", 2000000);
                    }
                    bool openAtStart = door is Building_Door bd0 && bd0.Open;
                    int firstWetBeyond = -1, maxBeyond = 0, t0 = TicksGameSafe();
                    void Watch()
                    {
                        int beyond = QFill(c, cells[3]) + QFill(c, cells[4]);
                        if (beyond > maxBeyond) maxBeyond = beyond;
                        if (beyond > 0 && firstWetBeyond < 0) firstWetBeyond = TicksGameSafe() - t0;
                    }
                    c.Phase("exec");
                    yield return PTicks(2000, Watch);
                    c.Phase("observe");
                    bool openAtEnd = door is Building_Door bd1 && bd1.Open;
                    bool passed = maxBeyond > 0;
                    cases.Add(PD("case", run.label, "door", run.def.defName, "openAtStart", openAtStart, "openAtEnd", openAtEnd,
                        "fillsAfter", cells.Select(x => QFill(c, x)).ToList(), "gateCell", PCell(gate),
                        "liquidReachedFarSide", passed, "ticksToFarSide", firstWetBeyond, "maxFarSideLevels", maxBeyond,
                        "expected", run.expectPass ? "passes" : "holds"));
                    if (passed != run.expectPass)
                    {
                        if (run.label == "sluice_shut") sealedFailed = true;
                        else unexpected.Add(run.label + (passed ? " passed liquid" : " held liquid") + " (expected " + (run.expectPass ? "passes" : "holds") + ")");
                    }
                    if (run.open && !openAtStart) unexpected.Add(run.label + ": fixture could not hold the sluice open");
                    QVanish(door); door = null;
                }
            }
            finally { QVanish(door); }
            QSetExpectedFail(c, "FLOWWORKS_SLUICE_TWO_DOORS_1");
            if (unexpected.Count > 0) { c.expectedFailUntil = null; c.Defect(string.Join("; ", unexpected) + (sealedFailed ? "; and the shut sluice passed liquid" : "")); }
            else if (sealedFailed) c.Defect("shut sealed sluice passed liquid (ruled: holds) - expected until FLOWWORKS_SLUICE_TWO_DOORS_1 is built");
            else c.Pass("grate passes, shut sluice holds, open sluice passes (XPASS: FLOWWORKS_SLUICE_TWO_DOORS_1 looks built)");
        }

        // ════════════════════════════════════════════════════════════════
        // save_reload: phase A arms (fixture, save, uninterrupted branch); phase B (after the launcher loads the
        // save) continues the same N ticks and compares. Checkpoint = a plain text file beside the journal.
        // ════════════════════════════════════════════════════════════════

        private const int QReloadTicks = 1500;

        private static string QCheckpointPath(string runId) =>
            Path.Combine(GenFilePaths.SaveDataFolderPath, "JawaBench", "playtest", runId + ".checkpoint.txt");

        /// <summary>One line per watched cell "cell x z D F fluid", one "body stock capacity receded limitless".</summary>
        private static List<string> QReloadSnapshot(PCtx c, List<IntVec3> channel, IntVec3 pondCell)
        {
            var lines = new List<string>();
            foreach (IntVec3 x in channel)
                lines.Add("cell " + x.x + " " + x.z + " " + c.Depth(x) + " " + QFill(c, x) + " " + (QFluidAt(c, x) ?? "-"));
            object stock = QGet(c.exc, "Stock");
            object body = QCall(stock, "BodyAt", c.map, pondCell, c.exc);
            lines.Add(body == null ? "body none" :
                "body " + Convert.ToSingle(QGet(body, "stock")).ToString("F3", CultureInfo.InvariantCulture) + " "
                + Convert.ToSingle(QGet(body, "capacity")).ToString("F3", CultureInfo.InvariantCulture) + " "
                + ((System.Collections.ICollection)QGet(body, "receded")).Count + " " + QGet(body, "limitless"));
            return lines;
        }

        private static IEnumerable<PWait> ScnSaveReloadA(PCtx c)
        {
            c.ev["route"] = "flow pulse from a natural pond into a dry D2 channel; GameDataSaveLoader.SaveGame mid-flow; uninterrupted branch recorded";
            Map m = c.map;
            if (!PFindRect(c, m.Center + new IntVec3(0, 0, -40), 12, 3, 3, true, out CellRect r)) { c.Invalid("no clean 12x3 site"); yield break; }
            PClearPlants(m, r.Cells);
            foreach (IntVec3 x in r.Cells) if (x.x <= r.minX + 2) m.terrainGrid.SetTerrain(x, TerrainDefOf.WaterShallow);
            int mz = r.minZ + 1;
            var channel = Enumerable.Range(r.minX + 3, 9).Select(xx => new IntVec3(xx, 0, mz)).ToList();
            foreach (IntVec3 x in channel) QDig(c, x, 2);
            IntVec3 pondCell = new IntVec3(r.minX + 2, 0, mz);
            c.Phase("exec");
            yield return PTicks(500);   // two pulses: mid-flow
            c.Phase("observe");
            var s0 = QReloadSnapshot(c, channel, pondCell);
            int ticksAtSave = TicksGameSafe();
            string save = "JBPT_" + c.run.id;
            string path = GenFilePaths.FilePathForSavedGame(save);
            DateTime before = DateTime.UtcNow.AddSeconds(-1);
            GameDataSaveLoader.SaveGame(save);
            bool saved = File.Exists(path) && File.GetLastWriteTimeUtc(path) >= before;
            if (!saved) { c.Invalid("SaveGame wrote no fresh file at " + path + " (it swallows its own exceptions - see Player.log)"); yield break; }
            c.Phase("exec");
            yield return PTicks(QReloadTicks);
            c.Phase("observe");
            var s1 = QReloadSnapshot(c, channel, pondCell);
            var cp = new List<string> { "runId " + c.run.id, "save " + save, "ticksAtSave " + ticksAtSave, "n " + QReloadTicks,
                "pond " + pondCell.x + " " + pondCell.z };
            cp.AddRange(s0.Select(l => "s0 " + l));
            cp.AddRange(s1.Select(l => "s1 " + l));
            File.WriteAllLines(QCheckpointPath(c.run.id), cp.ToArray());
            c.ev["saveName"] = save; c.ev["savePath"] = path; c.ev["ticksAtSave"] = ticksAtSave; c.ev["n"] = QReloadTicks;
            c.ev["checkpoint"] = QCheckpointPath(c.run.id);
            c.ev["s0"] = s0; c.ev["s1"] = s1;
            c.ev["resumeRecipe"] = "save_reload_b";
            c.ev["weather"] = m.weatherManager.curWeather?.defName;
            c.status = "PENDING";
            c.reason = "armed: saved " + save + " at tick " + ticksAtSave + "; verdict owed by save_reload_b (resume=" + c.run.id + ") after loading that save";
        }

        private static IEnumerable<PWait> ScnSaveReloadB(PCtx c)
        {
            c.ev["route"] = "the loaded save continues the same N ticks under the same pulse; snapshot compared line by line with the uninterrupted branch";
            string resume = c.run.resume;
            if (string.IsNullOrEmpty(resume)) { c.Invalid("save_reload_b needs resume=<runId of the save_reload run>"); yield break; }
            string cpPath = QCheckpointPath(resume);
            if (!File.Exists(cpPath)) { c.Invalid("no checkpoint " + cpPath); yield break; }
            string[] cp = File.ReadAllLines(cpPath);
            string Val(string k) => cp.FirstOrDefault(l => l.StartsWith(k + " "))?.Substring(k.Length + 1);
            int ticksAtSave = int.Parse(Val("ticksAtSave"), CultureInfo.InvariantCulture);
            int n = int.Parse(Val("n"), CultureInfo.InvariantCulture);
            string[] pp = Val("pond").Split(' ');
            IntVec3 pondCell = new IntVec3(int.Parse(pp[0]), 0, int.Parse(pp[1]));
            var s0 = cp.Where(l => l.StartsWith("s0 ")).Select(l => l.Substring(3)).ToList();
            var s1 = cp.Where(l => l.StartsWith("s1 ")).Select(l => l.Substring(3)).ToList();
            var channel = s0.Where(l => l.StartsWith("cell ")).Select(l => { string[] p = l.Split(' '); return new IntVec3(int.Parse(p[1]), 0, int.Parse(p[2])); }).ToList();
            c.ev["resume"] = resume; c.ev["save"] = Val("save"); c.ev["ticksAtSave"] = ticksAtSave; c.ev["ticksAtLoad"] = TicksGameSafe();
            // A load lands 0-2 ticks past the save (live round 2: +1 on 3 of 4 loads). Compare STATE, not the tick count:
            // run only the remaining ticks so the reloaded branch ends at the same game tick as the uninterrupted one.
            int offset = TicksGameSafe() - ticksAtSave;
            c.ev["loadTickOffset"] = offset;
            if (offset < 0 || offset > 2) { c.Invalid("current game is at tick " + TicksGameSafe() + ", not within 0-2 ticks of the checkpoint's " + ticksAtSave + " - load " + Val("save") + " first"); yield break; }
            n -= offset;
            var l0 = QReloadSnapshot(c, channel, pondCell);
            var d0 = s0.Zip(l0, (a, b) => a == b ? null : "saved[" + a + "] loaded[" + b + "]").Where(x => x != null).ToList();
            c.Phase("exec");
            yield return PTicks(n);
            c.Phase("observe");
            var l1 = QReloadSnapshot(c, channel, pondCell);
            var d1 = s1.Zip(l1, (a, b) => a == b ? null : "uninterrupted[" + a + "] reloaded[" + b + "]").Where(x => x != null).ToList();
            c.ev["loadedEqualsSaved"] = d0.Count == 0; c.ev["diffsAtLoad"] = d0;
            c.ev["branchesEqual"] = d1.Count == 0; c.ev["diffsAfterN"] = d1; c.ev["reloaded"] = l1;
            c.ev["weather"] = c.map.weatherManager.curWeather?.defName;
            if (d0.Count > 0) c.Defect("the loaded game does not match what was saved: " + string.Join("; ", d0));
            else if (d1.Count > 0) c.Defect(d1.Count + " line(s) diverged from the uninterrupted branch after " + n + " ticks: " + string.Join("; ", d1));
            else c.Pass("loaded state equals saved state; after " + n + " ticks D/F/fluid per cell and the pond body's stock equal the uninterrupted branch");
        }
        // ════════════════════════════════════════════════════════════════
        // pits: ladder release (routed inside to the ladder, then out) and fall-only-when-forced
        // ════════════════════════════════════════════════════════════════

        /// <summary>A side x side D4 pit (side = max(3, RequiredWidth+1)) with a standable 4-cell ring, by Deepen().</summary>
        private static bool QBuildPit(PCtx c, IntVec3 near, int side, out CellRect pit, out string why)
        {
            Map m = c.map;
            why = null;
            if (!PFindRect(c, near, side, side, 4, true, out pit,
                    rr => rr.ExpandedBy(4).Cells.Where(x => !rr.Contains(x)).All(x => x.Standable(m))))
            { why = "no clean " + side + "x" + side + " pit site with a standable 4-cell ring"; return false; }
            PClearPlants(m, pit.ExpandedBy(4).ClipInsideMap(m).Cells);
            foreach (IntVec3 x in pit.Cells) QDig(c, x, 4);
            if (!pit.Cells.All(c.IsSuperdeep)) { why = "Deepen() did not bring every pit cell to SUPERDEEP"; return false; }
            return true;
        }

        private static IEnumerable<PWait> ScnPitLadderRelease(PCtx c)
        {
            c.ev["route"] = "Goto to a cell BEYOND the far side of the pit from the ladder: the pather must take the held pawn inside to the lowered ladder, up, then round (RM_PitPathing route plan); hostile control must stay";
            Map m = c.map;
            Type trap = QT(QNs + "RM_SuperdeepTrap");
            ThingDef ladderDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Ladder");
            Faction friend = QFriendFaction();
            Faction enemy = Find.FactionManager.RandomEnemyFaction(allowHidden: false, allowDefeated: false, allowNonHumanlike: false);
            if (trap == null || ladderDef == null || friend == null || enemy == null) { c.Invalid("RM_SuperdeepTrap / RM_Ladder / a friendly and an enemy humanlike faction needed"); yield break; }
            if (!(QStatic(trap, "RuleOn") is bool on) || !on) { c.Invalid("capture/ladder rule is switched off in mod settings"); yield break; }
            MethodInfo isHeld = trap.GetMethod("IsHeld", QSBF), reqW = trap.GetMethod("RequiredWidth", QSBF);
            Pawn fr = QGenPawn(c, friend, 1), ho = QGenPawn(c, enemy, 2);
            int w = Math.Max((int)reqW.Invoke(null, new object[] { fr }), (int)reqW.Invoke(null, new object[] { ho }));
            int side = Math.Max(4, w + 2);
            if (!QBuildPit(c, m.Center + new IntVec3(25, 0, 0), side, out CellRect pit, out string why)) { QVanish(fr); QVanish(ho); c.Invalid(why); yield break; }
            IntVec3 ladderCell = new IntVec3(pit.CenterCell.x, 0, pit.maxZ);
            IntVec3 start = new IntVec3(pit.minX, 0, pit.minZ);
            IntVec3 dest = new IntVec3(pit.CenterCell.x, 0, pit.minZ - 3);   // beyond the side AWAY from the ladder
            Thing ladder = QMake(ladderDef); ladder.SetFaction(Faction.OfPlayer); GenSpawn.Spawn(ladder, ladderCell, m);
            object state = QGet(c.exc, "SuperdeepTrap");
            int descents0 = (int)QGet(state, "DescentCount");
            c.ev["pit"] = PD("x", pit.minX, "z", pit.minZ, "side", side); c.ev["ladderCell"] = PCell(ladderCell); c.ev["dest"] = PCell(dest);
            var attempts = new List<Dictionary<string, object>>();
            c.ev["attempts"] = attempts;
            Pawn sub = null;
            try
            {
                foreach (var a in new[] { new { p = fr, label = "friendly_with_ladder", expectOut = true, timeout = 2500 },
                                          new { p = ho, label = "hostile_with_ladder", expectOut = false, timeout = 900 } })
                {
                    c.Phase("setup");
                    sub = a.p;
                    GenSpawn.Spawn(sub, start, m);
                    bool held = (bool)isHeld.Invoke(null, new object[] { sub });
                    var path = new List<IntVec3> { start };
                    int lastOrder = TicksGameSafe(), reissues = 0, exitTick = -1, t0 = TicksGameSafe();
                    Pawn sp = sub;
                    QGoto(sp, dest);
                    void Watch()
                    {
                        if (!sp.Spawned) return;
                        if (sp.Position != path[path.Count - 1]) path.Add(sp.Position);
                        if (exitTick < 0 && !pit.Contains(sp.Position)) exitTick = TicksGameSafe() - t0;
                        if (exitTick < 0 && TicksGameSafe() - lastOrder >= 120 && sp.CurJobDef != JobDefOf.Goto && !sp.Downed) { reissues++; lastOrder = TicksGameSafe(); QGoto(sp, dest); }
                    }
                    c.Phase("exec");
                    if (a.expectOut) yield return PUntil(() => sp.Spawned && sp.Position == dest, a.timeout, Watch);
                    else yield return PTicks(a.timeout, Watch);
                    c.Phase("observe");
                    int firstOut = path.FindIndex(x => !pit.Contains(x));
                    int ladderIdx = path.IndexOf(ladderCell);
                    attempts.Add(PD("attempt", a.label, "heldAtStart", held, "leftPit", firstOut >= 0, "ticksToExit", exitTick,
                        "reachedDest", sp.Spawned && sp.Position == dest, "viaLadder", ladderIdx >= 0 && (firstOut < 0 || ladderIdx < firstOut),
                        "cellsVisited", path.Count, "orderReissues", reissues, "path", path.Select(PCell).ToList(),
                        "downed", sp.Downed, "dead", sp.Dead, "job", sp.CurJobDef?.defName));
                    QVanish(sub); sub = null;
                }
            }
            finally { QVanish(sub); QVanish(fr); QVanish(ho); QVanish(ladder); }
            int descents = (int)QGet(state, "DescentCount") - descents0;
            c.ev["descentsDuringScene"] = descents;
            Dictionary<string, object> A(string l) => attempts.FirstOrDefault(x => (string)x["attempt"] == l);
            var fails = new List<string>();
            var f = A("friendly_with_ladder"); var h = A("hostile_with_ladder");
            if (f == null || h == null) { c.Invalid("not both attempts ran"); yield break; }
            if ((bool)h["downed"] || (bool)h["dead"]) { c.Invalid("hostile downed/dead during the must-stay attempt"); yield break; }
            if (!(bool)f["heldAtStart"] || !(bool)h["heldAtStart"]) fails.Add("a pawn spawned in the D4 pit did not read IsHeld");
            if (!(bool)f["leftPit"]) fails.Add("friendly did not get out by the lowered ladder within 2500 ticks");
            else if (!(bool)f["viaLadder"]) fails.Add("friendly left the pit without passing the ladder cell");
            if ((bool)f["leftPit"] && !(bool)f["reachedDest"]) fails.Add("friendly left the pit but never reached the far-side destination");
            if ((bool)h["leftPit"]) fails.Add("hostile climbed the lowered ladder");
            if (descents > 0) fails.Add(descents + " descent(s) recorded - someone fell during a ladder scene");
            if (fails.Count == 0) c.Pass("friendly routed inside to the ladder, out, and round to the far side; hostile held");
            else c.Defect(string.Join("; ", fails));
        }

        private static IEnumerable<PWait> ScnPitFallForced(PCtx c)
        {
            c.ev["route"] = "walk: Goto straight across an open pit through the real pather (must go round, never descend); forced: a teleport into the pit (a skip's arrival) seen by the trap's own descent detector";
            Map m = c.map;
            Type trap = QT(QNs + "RM_SuperdeepTrap");
            Faction friend = QFriendFaction();
            if (trap == null || friend == null) { c.Invalid("RM_SuperdeepTrap / a non-hostile humanlike faction needed"); yield break; }
            Type settings = QT(QNs + "RimMandrakeFlowWorksSettings");
            if (!(QStatic(settings, "superdeepCaptureEnabled") is bool cap) || !cap) { c.Invalid("superdeepCaptureEnabled is off"); yield break; }
            MethodInfo isHeld = trap.GetMethod("IsHeld", QSBF);
            if (!QBuildPit(c, m.Center + new IntVec3(-25, 0, 0), 4, out CellRect pit, out string why)) { c.Invalid(why); yield break; }
            object state = QGet(c.exc, "SuperdeepTrap");
            int Desc() => (int)QGet(state, "DescentCount");
            c.ev["pit"] = PD("x", pit.minX, "z", pit.minZ, "side", 4);
            var fails = new List<string>();
            Pawn walker = null, pushed = null;
            try
            {
                // 1. careless pathing: straight line west->east across the pit's middle row
                c.Phase("setup");
                IntVec3 from = new IntVec3(pit.minX - 3, 0, pit.CenterCell.z), to = new IntVec3(pit.maxX + 3, 0, pit.CenterCell.z);
                walker = QGenPawn(c, friend, 11);
                GenSpawn.Spawn(walker, from, m);
                int d0 = Desc();
                var path = new List<IntVec3> { from };
                Pawn wk = walker; int lastOrder = TicksGameSafe(), reissues = 0;
                QGoto(wk, to);
                void Watch()
                {
                    if (!wk.Spawned) return;
                    if (wk.Position != path[path.Count - 1]) path.Add(wk.Position);
                    if (TicksGameSafe() - lastOrder >= 120 && wk.CurJobDef != JobDefOf.Goto && !wk.Downed && wk.Position != to) { reissues++; lastOrder = TicksGameSafe(); QGoto(wk, to); }
                }
                c.Phase("exec");
                PWait w1 = PUntil(() => !wk.Spawned || wk.Position == to, 2000, Watch);
                yield return w1;
                c.Phase("observe");
                int inPit = path.Count(x => pit.Contains(x));
                c.ev["walk"] = PD("from", PCell(from), "to", PCell(to), "reached", wk.Spawned && wk.Position == to, "pitCellsStepped", inPit,
                    "descents", Desc() - d0, "orderReissues", reissues, "path", path.Select(PCell).ToList(), "heldAtEnd", wk.Spawned && (bool)isHeld.Invoke(null, new object[] { wk }));
                if (inPit > 0 || Desc() - d0 > 0) fails.Add("a walking pawn stepped into the open pit (" + inPit + " cells, " + (Desc() - d0) + " descents) - pathing must go round");
                else if (!(wk.Spawned && wk.Position == to)) fails.Add("walker never reached the far side in 2000 ticks");
                QVanish(walker); walker = null;

                // 2. forced arrival: a pawn standing on the lip is moved into the pit (teleport, like a skip)
                c.Phase("setup");
                IntVec3 lip = new IntVec3(pit.CenterCell.x, 0, pit.maxZ + 1), into = new IntVec3(pit.CenterCell.x, 0, pit.maxZ);
                pushed = QGenPawn(c, friend, 12);
                GenSpawn.Spawn(pushed, lip, m);
                pushed.jobs.StartJob(JobMaker.MakeJob(JobDefOf.Wait, 5000), JobCondition.InterruptForced);
                yield return PTicks(5);   // the descent detector learns the pawn's last cell
                int d1 = Desc();
                float hp0 = pushed.health.summaryHealth.SummaryHealthPercent;
                c.Phase("exec");
                pushed.pather?.StopDead();
                pushed.Position = into;
                pushed.Notify_Teleported(true, true);
                Pawn pp = pushed;
                PWait w2 = PUntil(() => Desc() > d1, 120);
                yield return w2;
                c.Phase("observe");
                var recent = (List<string>)QGet(state, "RecentDescents");
                string mine = recent.LastOrDefault(l => l.StartsWith(pp.ThingID + "@"));
                bool heldNow = pp.Spawned && (bool)isHeld.Invoke(null, new object[] { pp });
                c.ev["forced"] = PD("lip", PCell(lip), "into", PCell(into), "descents", Desc() - d1, "descentLine", mine,
                    "healthBefore", hp0, "healthAfter", pp.health.summaryHealth.SummaryHealthPercent, "heldAfter", heldNow,
                    "fallDamageEnabled", QStatic(settings, "fallDamageEnabled"));
                if (Desc() - d1 < 1 || mine == null) fails.Add("forced arrival in the pit was not counted as a fall within 120 ticks");
                if (!heldNow) fails.Add("forced-in pawn is not held by the pit");
            }
            finally { QVanish(walker); QVanish(pushed); }
            if (fails.Count == 0) c.Pass("walker went round the open pit without a descent; a forced arrival fell and is held");
            else c.Defect(string.Join("; ", fails));
        }
    }
}
