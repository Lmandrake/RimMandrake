// Execute the complete shipping reflection bridge and gas-tap delivery body against
// the same extracted production tank/actor service. Only discovery and adjacency are doubles.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using RimMandrake.FlowWorks.Machinery;
namespace RimMandrake.FlowWorks.SelfTest.TheftHarness
{
    internal static class ExternalAccessTools
    {
        public static Type TypeByName(string name) => name switch
        {
            "RimMandrake.FlowWorks.Machinery.RM_LiquidNet" => typeof(ExternalNet),
            "RimMandrake.FlowWorks.LiquidTypes.Building_LiquidTank" => typeof(Building_LiquidTank),
            "RimMandrake.FlowWorks.RM_Volume" => typeof(RM_Volume),
            "RimMandrake.FlowWorks.Machinery.RM_LiquidTheft" => typeof(RM_LiquidTheft),
            _ => null
        };
        public static MethodInfo Method(Type type,string name,Type[] args) => type?.GetMethod(name,BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance|BindingFlags.Static,null,args,null);
        public static FieldInfo Field(Type type,string name) => type?.GetField(name,BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance);
    }
    internal static class ExternalNet
    {
        public static List<Building_LiquidTank> TanksFor(Thing origin) => origin.Map.listerThings.Things.OfType<Building_LiquidTank>().ToList();
    }
    namespace External
    {
        internal sealed partial class GasTapHarness
        {
            public Thing parent; public float bank; public int unitsDelivered;
            public sealed class Properties { public LiquidDef condensate; }
            public Properties Props = new();
            public List<Building_LiquidTank> tanks = new();
            public List<Building_LiquidTank> TouchingTanks() => tanks;
            public void Pulse() => Deliver();
        }
    }
    internal static class ExternalTankTheftChecks
    {
        private static void Assert(bool ok,string why) { if(!ok) throw new Exception(why); }
        public static void Run(Action<string,Action> Case)
        {
            Case("TankTheft_external_actual_Luminous_reflection_player_and_owner", () =>
            {
                var f = new TankTheftChecks.Fixture();
                f.water.defName = "RM_Liquid_SaltWater"; f.tank.storedUnits = 5000; f.tank.Capacity = 10000;
                Assert(External.FlowWorksWaterBridge.TryDrawOceanUnit(f.own) == f.water.defName && f.tank.storedUnits == 3000,"owner reflection draw did not happen");
                f.Tick(); f.NoTheft();
                Assert(External.FlowWorksWaterBridge.TryDrawOceanUnit(f.player) == f.water.defName && f.tank.storedUnits == 1000,"player reflection draw did not happen");
                Assert(f.tank.theftPlayerChanges.TryGetValue(f.water,out int delta) && delta == -2000,"Luminous player's real foreign-tank draw has no actor attribution");
                f.Tick(); Assert(RM_LiquidTheft.caught == 1,"Luminous theft not caught");
            });
            Case("TankTheft_external_actual_Luminous_refusal_has_no_pending", () =>
            {
                var f = new TankTheftChecks.Fixture(); f.water.defName = "RM_Liquid_SaltWater";
                Assert(External.FlowWorksWaterBridge.TryDrawOceanUnit(f.player) == null && f.tank.storedUnits == 100,"short reflection draw must refuse");
                f.Take(f.own,f.tank,10); f.Tick(); f.NoTheft();
            });
            Case("TankTheft_external_actual_Cauldron_player_and_owner_delivery", () =>
            {
                var f = new TankTheftChecks.Fixture(); f.tank.Capacity = 10000;
                var tap = new External.GasTapHarness { parent=f.own,bank=2,tanks=new(){f.tank} };
                tap.Props.condensate=f.water; tap.Pulse();
                Assert(f.tank.storedUnits == 4100 && tap.bank == 0 && tap.unitsDelivered == 2,"owner condensate delivery");
                f.Tick(); f.NoTheft();
                tap.parent=f.player; tap.bank=1; tap.Pulse();
                Assert(f.tank.storedUnits == 6100 && f.tank.theftPlayerChanges.TryGetValue(f.water,out int delta) && delta == 2000,"Cauldron player's real foreign-tank credit has no actor attribution");
                f.Tick(); Assert(RM_LiquidTheft.caught == 1,"condensate theft not caught");
            });
            Case("TankTheft_external_actual_Cauldron_refusal_keeps_bank_and_no_pending", () =>
            {
                var f = new TankTheftChecks.Fixture(); f.tank.Capacity=100;
                var tap = new External.GasTapHarness { parent=f.player,bank=1,tanks=new(){f.tank} };
                tap.Props.condensate=f.water; tap.Pulse();
                Assert(f.tank.storedUnits==100 && tap.bank==1 && tap.unitsDelivered==0 && f.tank.theftPlayerChanges.Count==0,"refused condensate delivery changed stock/bank/attribution");
                f.Tick(); f.NoTheft();
            });
        }
    }
}
