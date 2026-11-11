// Complete production TheftTick extracted at every build. Engine doubles below model only
// enumeration, witness availability, letters and goodwill; live proof checks those real boundaries.
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.Machinery;
namespace RimMandrake.FlowWorks.SelfTest.TheftHarness
{
    internal class Thing { }
    internal sealed class LiquidDef { }
    internal sealed class Building_LiquidTank : Thing
    {
        public int storedUnits = 100, theftSeenUnits = 100, theftTicks;
        public LiquidDef storedLiquid, theftSeenLiquid;
        public Faction Faction, theftCaughtBy;
        public string LabelShort => "tank";
        public bool PlayerReach = true;
    }
    internal sealed class Map { public readonly Lister listerThings = new Lister(); }
    internal sealed class Lister
    {
        public readonly List<Thing> Things = new List<Thing>();
        public IEnumerable<Thing> ThingsInGroup(ThingRequestGroup g) => Things;
    }
    internal enum ThingRequestGroup { BuildingArtificial }
    internal sealed class Faction
    {
        public static readonly Faction OfPlayer = new Faction();
        public bool defeated; public int PlayerGoodwill; public readonly FactionDef def = new FactionDef();
        public string Name => "owner";
        public bool TryAffectGoodwillWith(Faction victim, int delta, bool canSendMessage, bool canSendHostilityLetter, object reason, GlobalTargetInfo target)
        { victim.PlayerGoodwill += delta; return true; }
    }
    internal sealed class FactionDef { public bool permanentEnemy; }
    internal sealed class Pawn { public string LabelShortCap => "witness"; }
    internal static class RM_LiquidNet { public static bool IsForeign(Building_LiquidTank t) => t.Faction != null && t.Faction != Faction.OfPlayer; }
    internal static class RM_MachinerySettings { public static bool liquidTheftEnabled = true; public static int liquidTheftGoodwillPerDay = 2; }
    internal static class GenDate { public const int TicksPerDay = 60000; }
    internal static class Find { public static readonly Letters LetterStack = new Letters(); }
    internal sealed class Letters { public void ReceiveLetter(string label, string text, object def, LookTargets targets) {} }
    internal static class LetterDefOf { public static readonly object NegativeEvent = new object(); }
    internal static class RM_LiquidTheftDefOf { public static readonly object RM_LiquidTheftCaught = new object(); }
    internal sealed class LookTargets { public LookTargets(params object[] objects) {} }
    internal sealed class GlobalTargetInfo { public GlobalTargetInfo(object target) {} }
    internal static class Text { public static string Translate(this string s, params object[] args) => s; }
    internal static partial class RM_LiquidTheft
    {
        public static int caught, charges, goodwillCharged;
        public static bool HasWitness = true;
        public static bool PlayerReaches(Building_LiquidTank t) => t.PlayerReach;
        public static Pawn Witness(Thing t, Faction victim) => HasWitness ? new Pawn() : null;
    }
    internal static class TankTheftChecks
    {
        public static void Run(Action<string, Action> Case)
        {
            Case("TankTheft_production_owner_use_idle_or_unrelated_active_player_reaches", () =>
            {
                var tank = new Building_LiquidTank { Faction = new Faction() };
                var map = new Map(); map.listerThings.Things.Add(tank);
                RM_LiquidTheft.caught = RM_LiquidTheft.charges = 0;
                // Owner's production stock delta, with player reach and a valid witness.
                tank.storedUnits -= 10;
                RM_LiquidTheft.TheftTick(map);
                if (RM_LiquidTheft.caught != 0 || RM_LiquidTheft.charges != 0 || tank.theftCaughtBy != null)
                    throw new Exception("owner stock 100 -> 90 was billed as player theft solely because player equipment reaches the tank");
            });
        }
    }
}
