// Complete shipping TheftTick, actor scopes, tank mutations and ExposeData run unchanged.
// Engine doubles model enumeration/witness availability, letters, goodwill and scribe fields.
// Live proof owns real topology, witnesses, vanilla goodwill and on-disk saves.
using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks.Machinery;
namespace RimMandrake.FlowWorks.SelfTest.TheftHarness
{
    internal class Thing
    {
        public Faction Faction; public Map Map;
        public virtual void ExposeData() {}
    }
    internal sealed class LiquidDef { public string Name; public override string ToString() => Name; }
    internal sealed partial class Building_LiquidTank : Thing
    {
        public int storedUnits = 100, theftTicks, Capacity = 1000;
        public LiquidDef storedLiquid;
        public Faction theftCaughtBy, theftPendingVictim;
        public Dictionary<LiquidDef, int> theftPlayerChanges = new();
        private int volumeModel = RM_Volume.CurrentModel;
        public RM_TankMode mode;
        public bool Empty => storedLiquid == null || storedUnits <= 0;
        public bool PlayerReach = true;
        public string LabelShort => "tank";
    }
    internal sealed class Map { public readonly Lister listerThings = new(); }
    internal sealed class Lister
    {
        public readonly List<Thing> Things = new();
        public IEnumerable<Thing> ThingsInGroup(ThingRequestGroup g) => Things;
    }
    internal enum ThingRequestGroup { BuildingArtificial }
    internal sealed class Faction
    {
        public static readonly Faction OfPlayer = new();
        public bool defeated; public int PlayerGoodwill; public readonly FactionDef def = new();
        public string Name => "owner";
        public bool TryAffectGoodwillWith(Faction victim, int delta, bool canSendMessage, bool canSendHostilityLetter, object reason, GlobalTargetInfo target)
        { victim.PlayerGoodwill += delta; return true; }
    }
    internal sealed class FactionDef { public bool permanentEnemy; }
    internal sealed class Pawn { public string LabelShortCap => "witness"; }
    internal static class RM_LiquidNet { public static bool IsForeign(Building_LiquidTank t) => t.Faction != null && t.Faction != Faction.OfPlayer; }
    internal static class RM_MachinerySettings { public static bool liquidTheftEnabled = true; public static int liquidTheftGoodwillPerDay = 2; }
    internal static class GenDate { public const int TicksPerDay = 60000; }
    internal static class Find { public static readonly Letters LetterStack = new(); }
    internal sealed class Letters { public void ReceiveLetter(string label, string text, object def, LookTargets targets) {} }
    internal static class LetterDefOf { public static readonly object NegativeEvent = new(); }
    internal static class RM_LiquidTheftDefOf { public static readonly object RM_LiquidTheftCaught = new(); }
    internal sealed class LookTargets { public LookTargets(params object[] objects) {} }
    internal sealed class GlobalTargetInfo { public GlobalTargetInfo(object target) {} }
    internal static class Text { public static string Translate(this string s, params object[] args) => s; }
    internal static class Log { public static void Warning(string s) {} }
    internal enum LoadSaveMode { Saving, LoadingVars, PostLoadInit }
    internal enum LookMode { Def, Value }
    internal static class Scribe
    {
        public static LoadSaveMode mode;
        public static Dictionary<string, object> data = new();
        public static void Look<T>(ref T field, string key, T defaultValue = default)
        {
            if (mode == LoadSaveMode.Saving) data[key] = field;
            if (mode == LoadSaveMode.LoadingVars) field = data.TryGetValue(key, out object v) ? (T)v : defaultValue;
        }
    }
    internal static class Scribe_Values { public static void Look<T>(ref T f, string k, T d = default) => Scribe.Look(ref f, k, d); }
    internal static class Scribe_Defs { public static void Look<T>(ref T f, string k) => Scribe.Look(ref f, k); }
    internal static class Scribe_References { public static void Look<T>(ref T f, string k) => Scribe.Look(ref f, k); }
    internal static class Scribe_Collections
    {
        public static void Look<K,V>(ref Dictionary<K,V> f, string k, LookMode keys, LookMode values)
        {
            if (Scribe.mode == LoadSaveMode.Saving) Scribe.data[k] = f == null ? null : new Dictionary<K,V>(f);
            if (Scribe.mode == LoadSaveMode.LoadingVars) f = Scribe.data.TryGetValue(k, out object v) && v != null ? new Dictionary<K,V>((Dictionary<K,V>)v) : null;
        }
    }
    internal static partial class RM_LiquidTheft
    {
        public static int caught, charges, goodwillCharged;
        public static bool HasWitness = true;
        public static bool PlayerReaches(Building_LiquidTank t) => t.PlayerReach;
        public static Pawn Witness(Thing t, Faction victim) => HasWitness ? new Pawn() : null;
    }
    internal static class TankTheftChecks
    {
        private static void Assert(bool ok, string msg) { if (!ok) throw new Exception(msg); }
        private sealed class Fixture
        {
            public Map map = new(); public Faction owner = new();
            public LiquidDef water = new() { Name = "water" }, tar = new() { Name = "tar" };
            public Thing player, own;
            public Building_LiquidTank tank;
            public Fixture()
            {
                RM_MachinerySettings.liquidTheftEnabled = true;
                RM_LiquidTheft.HasWitness = true;
                RM_LiquidTheft.caught = RM_LiquidTheft.charges = RM_LiquidTheft.goodwillCharged = 0;
                player = new Thing { Faction = Faction.OfPlayer, Map = map };
                own = new Thing { Faction = owner, Map = map };
                tank = Tank(owner);
            }
            public Building_LiquidTank Tank(Faction faction)
            {
                var t = new Building_LiquidTank { Map = map, Faction = faction, storedLiquid = water };
                map.listerThings.Things.Add(t); return t;
            }
            public void Tick() => RM_LiquidTheft.TheftTick(map);
            public void Take(Thing who, Building_LiquidTank t, int units)
            {
                using var scope = RM_LiquidTheft.As(who);
                Assert(RM_LiquidTransfer.Move(units, Leg(t), RM_TransferLeg.Sink(null), out _) == units, "transfer failed");
            }
            public RM_TransferLeg Leg(Building_LiquidTank t)
            {
                var liquid = t.storedLiquid;
                return RM_TransferLeg.Store(t.CanProvide, t.TryRemoveLiquid, n => t.TryAddLiquid(liquid, n));
            }
            public void NoTheft() => Assert(RM_LiquidTheft.caught == 0 && RM_LiquidTheft.charges == 0 && tank.theftCaughtBy == null && tank.theftTicks == 0, "owner/refused/restored activity billed as theft");
        }
        public static void Run(Action<string, Action> Case)
        {
            Case("TankTheft_production_owner_use_idle_or_unrelated_active_player_reaches", () =>
            {
                var f = new Fixture();
                f.Take(f.own, f.tank, 10); f.Tick(); f.NoTheft();
                var unrelated = f.Tank(Faction.OfPlayer);
                f.Take(f.player, unrelated, 10);
                f.Take(f.own, f.tank, 10); f.Tick(); f.NoTheft();
                Assert(unrelated.storedUnits == 90 && f.tank.storedUnits == 80 && f.tank.PlayerReach, "negative control did not move stock/reach");
            });
            Case("TankTheft_production_player_caught_goodwill_and_idle", () =>
            {
                var f = new Fixture(); f.Take(f.player, f.tank, 10); f.Tick();
                Assert(RM_LiquidTheft.caught == 1 && f.tank.theftCaughtBy == f.owner && f.tank.theftTicks == 0, "first cycle must catch, without accrual");
                f.tank.theftTicks = GenDate.TicksPerDay - RM_PumpMath.CycleTicks;
                f.Take(f.player, f.tank, 10); f.Tick();
                Assert(RM_LiquidTheft.charges == 1 && RM_LiquidTheft.goodwillCharged == -2 && f.owner.PlayerGoodwill == -2 && f.tank.theftTicks == 0, "existing goodwill rule lost");
                f.Take(f.own, f.tank, 10); f.Tick(); f.Tick();
                Assert(RM_LiquidTheft.charges == 1 && f.tank.theftTicks == 0, "owner/idle accrued caught ticks");
            });
            Case("TankTheft_owner_replenishment_does_not_hide_player_transfer", () =>
            {
                var f = new Fixture(); f.Take(f.player, f.tank, 10);
                using (RM_LiquidTheft.As(f.own)) Assert(f.tank.TryAddLiquid(f.water, 10), "owner fill refused");
                Assert(f.tank.storedUnits == 100, "equal total control"); f.Tick();
                Assert(RM_LiquidTheft.caught == 1, "total-stock gate hid genuine theft");
            });
            Case("TankTheft_production_refusal_and_restored_stock_cancel", () =>
            {
                var f = new Fixture();
                using (RM_LiquidTheft.As(f.player))
                {
                    Assert(RM_LiquidTransfer.Move(10, f.Leg(f.tank), RM_TransferLeg.World(n => true, n => false), out var o) == 0 && o.Lost == 0, "refusal/rollback");
                    Assert(RM_LiquidTransfer.Move(10, f.Leg(f.tank), RM_TransferLeg.World(n => false, n => true), out _) == 0, "Can refusal");
                    Assert(!f.tank.TryRemoveLiquid(10000), "unavailable remove");
                    Assert(!f.tank.TryAddLiquid(f.tar, 10), "identity refusal");
                    Assert(f.tank.TryRemoveLiquid(10) && f.tank.TryAddLiquid(f.water, 10), "restore before cycle");
                }
                Assert(f.tank.storedUnits == 100 && f.tank.theftPlayerChanges.Count == 0, "put-backs left pending attribution");
                f.Take(f.own, f.tank, 10); f.Tick(); f.NoTheft();
            });
            Case("TankTheft_production_partial_split_bills_only_retained_units", () =>
            {
                var f = new Fixture(); var b = f.Tank(f.owner); var ts = new[] { f.tank, b };
                using (RM_LiquidTheft.As(f.player))
                {
                    var split = RM_TransferLeg.Split(2, i => 10, (i,n) => ts[i].CanProvide(n), (i,n) => ts[i].TryRemoveLiquid(n), (i,n) => ts[i].TryAddLiquid(f.water,n));
                    Assert(RM_LiquidTransfer.Move(20, split, RM_TransferLeg.Boundary(n => true, n => 15), out var o) == 15 && o.Lost == 0, "partial settlement");
                }
                Assert(f.tank.theftPlayerChanges[f.water] == -10 && b.theftPlayerChanges[f.water] == -5 && f.tank.storedUnits == 90 && b.storedUnits == 95, "partial undo attribution wrong");
                f.Tick(); Assert(RM_LiquidTheft.caught == 2, "retained player changes not caught per tank");
            });
            Case("TankTheft_equal_volume_liquid_identity_swap_is_visible", () =>
            {
                var f = new Fixture();
                using (RM_LiquidTheft.As(f.player)) Assert(f.tank.TryRemoveLiquid(100) && f.tank.TryAddLiquid(f.tar,100), "swap failed");
                Assert(f.tank.storedUnits == 100 && f.tank.theftPlayerChanges.Count == 2, "identity changes netted across liquids");
                f.Tick(); Assert(RM_LiquidTheft.caught == 1, "identity theft missed");
            });
            Case("TankTheft_nested_owner_unowned_and_exception_scopes_restore_actor", () =>
            {
                var f = new Fixture();
                using (RM_LiquidTheft.As(f.player))
                {
                    f.Take(f.own, f.tank, 10);
                    f.Take(null, f.tank, 10);
                    try { using var scope = RM_LiquidTheft.As(f.own); throw new InvalidOperationException("injected"); } catch (InvalidOperationException) {}
                    Assert(f.tank.TryRemoveLiquid(10), "outer actor lost");
                }
                Assert(f.tank.theftPlayerChanges[f.water] == -10, "nested owner charged or previous actor not restored");
                try { using var scope = RM_LiquidTheft.As(f.player); throw new InvalidOperationException("injected"); } catch (InvalidOperationException) {}
                Assert(f.tank.TryRemoveLiquid(10), "unscoped setup failed");
                Assert(f.tank.theftPlayerChanges[f.water] == -10, "exception leaked actor");
            });
            Case("TankTheft_witness_route_and_no_global_tank_blame", () =>
            {
                var f = new Fixture(); var other = f.Tank(f.owner);
                f.Take(f.player, other, 10); other.PlayerReach = false;
                f.Take(f.own, f.tank, 10); f.Tick();
                Assert(f.tank.theftCaughtBy == null && other.theftCaughtBy == f.owner && RM_LiquidTheft.caught == 1, "global reach blame or removed-route bypass");
                f = new Fixture(); RM_LiquidTheft.HasWitness = false; f.Take(f.player,f.tank,10); f.Tick();
                RM_LiquidTheft.HasWitness = true; f.Tick(); f.NoTheft();
                f.Take(f.player,f.tank,10); f.Tick(); Assert(RM_LiquidTheft.caught == 1, "fresh witnessed transfer missing");
            });
            Case("TankTheft_settings_and_ownership_consume_stale_changes", () =>
            {
                var f = new Fixture(); f.Take(f.player,f.tank,10);
                RM_MachinerySettings.liquidTheftEnabled = false; f.Tick(); f.Take(f.player,f.tank,10);
                RM_MachinerySettings.liquidTheftEnabled = true; f.Take(f.own,f.tank,10); f.Tick(); f.NoTheft();
                f.Take(f.player,f.tank,10); f.tank.Faction = Faction.OfPlayer; f.Tick();
                f.tank.Faction = f.owner; f.Tick(); f.NoTheft();
                f.Take(f.player,f.tank,10); f.owner.defeated = true; f.Tick(); f.owner.defeated = false; f.Tick(); f.NoTheft();
            });
            Case("TankTheft_actual_ExposeData_keeps_pending_caught_ticks_and_old_save_defaults", () =>
            {
                var f = new Fixture(); f.Take(f.player,f.tank,10);
                Scribe.data.Clear(); Scribe.mode = LoadSaveMode.Saving; f.tank.ExposeData();
                var loaded = f.Tank(f.owner);
                Scribe.mode = LoadSaveMode.LoadingVars; loaded.ExposeData();
                Scribe.mode = LoadSaveMode.PostLoadInit; loaded.ExposeData();
                f.map.listerThings.Things.Remove(f.tank); f.tank = loaded;
                f.Tick(); Assert(RM_LiquidTheft.caught == 1 && loaded.storedUnits == 90, "save/load forgave/invented pending attribution");
                loaded.theftTicks = 1234; Scribe.mode = LoadSaveMode.Saving; loaded.ExposeData();
                loaded.theftTicks = 0; loaded.theftCaughtBy = null;
                Scribe.mode = LoadSaveMode.LoadingVars; loaded.ExposeData(); Scribe.mode = LoadSaveMode.PostLoadInit; loaded.ExposeData();
                f.Take(f.own,loaded,10); f.Tick(); Assert(loaded.theftCaughtBy == f.owner && loaded.theftTicks == 1234 && RM_LiquidTheft.caught == 1, "historical caught state changed or owner accrued");
                Scribe.data.Remove("rmTheftPlayerChanges"); Scribe.data.Remove("rmTheftPendingVictim");
                Scribe.mode = LoadSaveMode.LoadingVars; loaded.ExposeData(); Scribe.mode = LoadSaveMode.PostLoadInit; loaded.ExposeData();
                Assert(loaded.theftPlayerChanges != null && loaded.theftPlayerChanges.Count == 0, "old save pending defaults"); f.Tick();
                Assert(RM_LiquidTheft.caught == 1 && RM_LiquidTheft.charges == 0, "old-save owner stock invented theft");
            });
            TankTheftCallerChecks.Run(Case);
        }
    }
}
