using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// Public static fixtures for the validation harness (jawa/static_call). Not used by the game itself.
    /// </summary>
    public static class DroidworksProofs
    {
        /// <summary>
        /// Turns an already-spawned, non-player humanlike pawn (args = its ThingID) into a trader the
        /// jawa/trade_price_probe tool can open a session against: sets Pawn_TraderTracker.traderKind and puts
        /// stock in its inventory. Exists because TraderCaravanArrival can generate NO caravan on a list/tile where
        /// the faction's Trader group has no usable PawnGroupMaker, and the protocol-droid price hook
        /// (Patch_ProtocolTradeAdvantage) only needs a live TradeSession, not a caravan.
        /// </summary>
        public static string MakeTrader(string args)
        {
            Map map = Find.CurrentMap;
            if (map == null) return "FAIL: no current map";
            string id = (args ?? "").Trim();
            Pawn p = map.mapPawns.AllPawnsSpawned.FirstOrDefault(x => x.ThingID == id);
            if (p == null) return "FAIL: no spawned pawn " + id;
            if (p.trader == null) return "FAIL: pawn has no trader tracker (not humanlike?): " + id;
            if (p.Faction == null || p.Faction == Faction.OfPlayer) return "FAIL: pawn must be non-player faction: " + id;
            TraderKindDef kind = DefDatabase<TraderKindDef>.GetNamedSilentFail("Caravan_Outlander_BulkGoods")
                ?? DefDatabase<TraderKindDef>.AllDefsListForReading.FirstOrDefault(k => k.tradeCurrency == TradeCurrency.Silver);
            if (kind == null) return "FAIL: no silver TraderKindDef";
            p.trader.traderKind = kind;
            string[] stock = { "Steel", "ComponentIndustrial", "MedicineIndustrial", "Cloth" };
            int added = 0;
            foreach (string dn in stock)
            {
                ThingDef td = DefDatabase<ThingDef>.GetNamedSilentFail(dn);
                if (td == null) continue;
                Thing t = ThingMaker.MakeThing(td, GenStuff.DefaultStuffFor(td));
                t.stackCount = td.stackLimit > 1 ? System.Math.Min(td.stackLimit, 40) : 1;
                if (p.inventory.innerContainer.TryAdd(t)) added++; else t.Destroy();
            }
            return "OK kind=" + kind.defName + " stockStacks=" + added;
        }
    }
}
