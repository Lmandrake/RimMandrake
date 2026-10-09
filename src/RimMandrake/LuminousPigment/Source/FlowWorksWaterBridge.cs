using System;
using System.Collections;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // DESIGN_PASS LP-2 (GLOW_TANK_LIQUID_FEED_1): the GlowTank drinks from a FlowWorks liquid net. Reflection-only,
    // the same soft-binding idiom as NinefoldDeltaBridge (About.xml: no mandrake.* engine in modDependencies).
    // Verified against src/RimMandrake/FlowWorks/Source: `public static List<Building_LiquidTank>
    // RimMandrake.FlowWorks.Machinery.RM_LiquidNet.TanksFor(Thing origin)` (adjacent tanks plus every tank on a hose
    // run touching the origin), `Building_LiquidTank.storedLiquid` (public LiquidDef : Def) and
    // `public bool TryRemoveLiquid(int units)`. FlowWorks absent = Present false, a silent no-op.
    internal static class FlowWorksWaterBridge
    {
        private const string NetTypeName = "RimMandrake.FlowWorks.Machinery.RM_LiquidNet";
        private const string TankTypeName = "RimMandrake.FlowWorks.LiquidTypes.Building_LiquidTank";

        private static bool resolved;
        private static bool warned;
        private static MethodInfo tanksFor;
        private static FieldInfo storedLiquid;
        private static MethodInfo tryRemove;

        public static bool Present
        {
            get
            {
                Resolve();
                return tanksFor != null && storedLiquid != null && tryRemove != null;
            }
        }

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;
            Type net = AccessTools.TypeByName(NetTypeName);
            Type tank = AccessTools.TypeByName(TankTypeName);
            if (net == null || tank == null) return; // FlowWorks not loaded: normal
            tanksFor = AccessTools.Method(net, "TanksFor", new[] { typeof(Thing) });
            storedLiquid = AccessTools.Field(tank, "storedLiquid");
            tryRemove = AccessTools.Method(tank, "TryRemoveLiquid", new[] { typeof(int) });
            if ((tanksFor == null || storedLiquid == null || tryRemove == null) && !warned)
            {
                warned = true;
                Log.Warning("[LuminousPigment] FlowWorks is loaded but its liquid-net shape changed; the GlowTank water feed is off.");
            }
        }

        /// <summary>Takes one unit of salt or boiling water from a tank on <paramref name="origin"/>'s net. Returns
        /// the liquid's defName, or null when nothing on the net could give one.</summary>
        public static string TryDrawOceanUnit(Thing origin)
        {
            if (!Present || origin == null || !origin.Spawned) return null;
            try
            {
                if (!(tanksFor.Invoke(null, new object[] { origin }) is IEnumerable tanks)) return null;
                foreach (object t in tanks)
                {
                    string name = (storedLiquid.GetValue(t) as Def)?.defName;
                    if (!RM_GlowTankWater.IsOceanLiquid(name)) continue;
                    if (tryRemove.Invoke(t, new object[] { 1 }) is bool ok && ok) return name;
                }
            }
            catch (Exception e)
            {
                if (!warned)
                {
                    warned = true;
                    Log.Warning("[LuminousPigment] GlowTank water draw failed: " + e.Message);
                }
            }
            return null;
        }
    }
}
