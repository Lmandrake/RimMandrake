using System.Globalization;
using HarmonyLib;
using System.Linq;
using RimMandrake.FlowWorks.LiquidTypes;
using RimMandrake.FlowWorks.Machinery;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// Real-flow probe verbs (hose port step 8; the HoseProbe channel, read by northstar/proof_hose.py). State is read from the
    /// tanks, pumps and the net itself -- G3.11: a hose's carried units are read from the hose's FAR tank, never "the first tank
    /// beside the pump".
    ///   tank:x,z                        the tank at a cell: liquid, units, capacity
    ///   filltank:x,z=LiquidDef,units    staging: set a tank's contents (empty with units 0)
    ///   flick:x,z=on|off                a CompFlickable's switch (the pump's power switch)
    ///   pump:x,z                        a pump: powered, on, pour mode, last moved units and tick, Moved
    ///   net:x,z                         every tank the machine/tank at x,z reaches, with the reels on each route
    /// </summary>
    public static class HoseNetProbe
    {
        private static string S(string s) => HoseProbe.S(s);
        private static string B(bool b) => HoseProbe.B(b);

        private static IntVec3 Cell(string xz)
        {
            string[] p = xz.Split(',');
            return new IntVec3(int.Parse(p[0], CultureInfo.InvariantCulture), 0, int.Parse(p[1], CultureInfo.InvariantCulture));
        }

        private static T At<T>(Map map, IntVec3 c) where T : Thing => c.InBounds(map) ? c.GetThingList(map).OfType<T>().FirstOrDefault() : null;

        public static string TryRun(Map map, string cmd)
        {
            int colon = cmd.IndexOf(':');
            if (colon < 0) return null;
            string verb = cmd.Substring(0, colon), arg = cmd.Substring(colon + 1), val = null;
            int eq = arg.IndexOf('=');
            if (eq >= 0) { val = arg.Substring(eq + 1); arg = arg.Substring(0, eq); }
            switch (verb)
            {
                case "tank":
                {
                    Building_LiquidTank t = At<Building_LiquidTank>(map, Cell(arg));
                    if (t == null) return Fail(cmd, "no tank there");
                    return "{\"success\":true,\"cmd\":" + S(cmd) + ",\"id\":" + t.thingIDNumber + ",\"liquid\":" + S(t.storedLiquid?.defName) + ",\"units\":" + t.storedUnits +
                           ",\"capacity\":" + t.Capacity + ",\"tick\":" + Find.TickManager.TicksGame + "}";
                }
                case "filltank":
                {
                    Building_LiquidTank t = At<Building_LiquidTank>(map, Cell(arg));
                    if (t == null) return Fail(cmd, "no tank there");
                    string[] p = (val ?? "").Split(',');
                    int units = p.Length > 1 ? int.Parse(p[1], CultureInfo.InvariantCulture) : 0;
                    LiquidDef l = DefDatabase<LiquidDef>.GetNamedSilentFail(p[0]);
                    // C8b-F3: refuse a bad request BEFORE emptying, and put the old stock back if the refill is refused
                    if (units > 0 && (l == null || units > t.Capacity)) return Fail(cmd, "bad liquid or more units than the tank holds");
                    LiquidDef hadLiquid = t.storedLiquid;
                    int had = t.storedUnits;
                    t.TryRemoveLiquid(had);
                    bool ok = units <= 0 || t.TryAddLiquid(l, units);
                    if (!ok && had > 0 && hadLiquid != null) t.TryAddLiquid(hadLiquid, had);
                    return "{\"success\":" + B(ok) + ",\"cmd\":" + S(cmd) + ",\"liquid\":" + S(t.storedLiquid?.defName) + ",\"units\":" + t.storedUnits + "}";
                }
                case "flick":
                {
                    Thing th = Cell(arg).InBounds(map) ? Cell(arg).GetThingList(map).FirstOrDefault(x => x.TryGetComp<CompFlickable>() != null) : null;
                    CompFlickable f = th?.TryGetComp<CompFlickable>();
                    if (f == null) return Fail(cmd, "nothing flickable there");
                    bool on = val == "on";
                    if (f.SwitchIsOn != on)
                    {
                        f.DoFlick();
                        Traverse.Create(f).Field("wantSwitchOn").SetValue(on);
                    }
                    return "{\"success\":true,\"cmd\":" + S(cmd) + ",\"on\":" + B(f.SwitchIsOn) + "}";
                }
                case "pump":
                {
                    Building_LiquidPump p = At<Building_LiquidPump>(map, Cell(arg));
                    if (p == null) return Fail(cmd, "no pump there");
                    CompPowerTrader pw = p.GetComp<CompPowerTrader>();
                    return "{\"success\":true,\"cmd\":" + S(cmd) + ",\"powered\":" + B(pw == null || pw.PowerOn) + ",\"pourMode\":" + B(p.pourMode) +
                           ",\"lastMovedUnits\":" + p.lastMovedUnits + ",\"lastMovedTick\":" + p.lastMovedTick + ",\"moved\":" + p.Moved +
                           ",\"tick\":" + Find.TickManager.TicksGame + "}";
                }
                case "net":
                {
                    Thing o = Cell(arg).InBounds(map) ? Cell(arg).GetThingList(map).FirstOrDefault(x => RM_LiquidNet.RoleOfThing(x) != RM_NetRole.None) : null;
                    if (o == null) return Fail(cmd, "no liquid machine or tank there");
                    RM_NetResult r = RM_LiquidNet.Store(o);
                    var rows = r.Tanks.OfType<Building_LiquidTank>().Select(t => "{\"tank\":[" + t.Position.x + "," + t.Position.z + "],\"units\":" + t.storedUnits +
                        ",\"liquid\":" + S(t.storedLiquid?.defName) + ",\"route\":[" +
                        string.Join(",", r.Routes[t].Select(l => l.Reel is CompHoseReel rr ? "[" + rr.parent.Position.x + "," + rr.parent.Position.z + "]" : "null")) + "]}");
                    return "{\"success\":true,\"cmd\":" + S(cmd) + ",\"origin\":" + S(o.def.defName) + ",\"links\":" + RM_HoseLinks.For(map).All.Count +
                           ",\"tanks\":[" + string.Join(",", rows) + "],\"componentBuilds\":" + RM_LiquidNet.Components(map).Builds + ",\"revisionBumps\":" + RM_LiquidNet.Bumps + ",\"settles\":" + RM_LiquidNet.Settles + ",\"settledUnits\":" + RM_LiquidNet.SettledUnits +
                           ",\"dumpedUnits\":" + RM_LiquidNet.DumpedUnits + ",\"spilledUnits\":" + RM_LiquidSpill.SpilledUnits + ",\"hoseDrainedUnits\":" + RM_LiquidSpill.DrainedUnits +
                           ",\"moves\":" + RM_LiquidTransfer.Moves + ",\"putBacks\":" + RM_LiquidTransfer.PutBacks + ",\"theftCaught\":" + RM_LiquidTheft.caught + ",\"theftGoodwill\":" + RM_LiquidTheft.goodwillCharged + ",\"tooLarge\":" + B(r.Truncated) + ",\"indexRebuilds\":" + RM_HoseLinks.Rebuilds +
                           ",\"levelCycles\":" + RM_Levelling.Cycles + ",\"levelLinks\":" + RM_Levelling.LastLinks + ",\"levelMoves\":" + RM_Levelling.Moves + ",\"levelMovedDl\":" + RM_Levelling.MovedDl + "}";
                }
            }
            return null;
        }

        private static string Fail(string cmd, string why) => "{\"success\":false,\"cmd\":" + S(cmd) + ",\"error\":" + S(why) + "}";
    }
}
