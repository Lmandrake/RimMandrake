using Verse;

namespace RimMandrake.Stillsand
{
    /// <summary>
    /// WATER_LEDGER_DOUBLE_CHARGE_1's live row (validation.py water chain, component "still_water_charged_once"): static_call surfaces that
    /// read the water ledger's debt and run ONE solar-still cycle outright, so the row does not wait 6,000 sunlit ticks.
    /// Read-only except ProofStillCycle, which does exactly what a fired CompTickRare does (FindFeed + Consume), and
    /// ProofDrinkHook, which runs the water item's ingestion hook once without consuming it.
    /// </summary>
    public static class RM_WaterLedgerProof
    {
        /// <summary>"-" -&gt; "LEDGER live=bool debt=litres def=defName|none enabled=bool".</summary>
        public static string ProofLedger(string arg)
        {
            RM_WaterLedgerDef def = RM_WaterLedger.ActiveDef;
            RM_WaterLedger ledger = RM_WaterLedger.Current;
            bool live = def != null && ledger != null && RM_StillsandWaterSettings.ledgerEnabled;
            return "LEDGER live=" + live + " debt=" + (ledger != null ? ledger.Debt.ToString("0.###") : "none")
                + " def=" + (def?.defName ?? "none") + " enabled=" + RM_StillsandWaterSettings.ledgerEnabled
                + " countsHere=" + (def != null && Find.CurrentMap != null && def.CountsOn(Find.CurrentMap));
        }

        /// <summary>"x,z" (a cell of a solar or wringing still on the current map) -&gt; one cycle run now:
        /// "CYCLE ran=bool feed=defName units=n litres=n water=defName".</summary>
        public static string ProofStillCycle(string arg)
        {
            Map map = Find.CurrentMap;
            string[] a = (arg ?? "").Split(',');
            if (map == null || a.Length != 2 || !int.TryParse(a[0], out int x) || !int.TryParse(a[1], out int z))
            {
                return "REFUSED: arg must be x,z on a current map";
            }
            IntVec3 c = new IntVec3(x, 0, z);
            if (!c.InBounds(map))
            {
                return "REFUSED: out of bounds";
            }
            foreach (Thing t in c.GetThingList(map))
            {
                RM_CompSolarStill still = t.TryGetComp<RM_CompSolarStill>();
                if (still == null)
                {
                    continue;
                }
                if (!still.FindFeed(out Thing stock, out int units, out int litres))
                {
                    return "CYCLE ran=False feed=none still=" + t.ThingID;
                }
                string feed = stock.def.defName;
                still.Consume(stock, units, litres);
                return "CYCLE ran=True feed=" + feed + " units=" + units + " litres=" + litres
                    + " water=" + (RM_CompSolarStill.WaterDef()?.defName ?? "none") + " still=" + t.ThingID;
            }
            return "NONE: no still at " + x + "," + z;
        }

        /// <summary>"x,z" (a cell holding a still's water item) -&gt; the item's own drink hook run once, as an ingestion by
        /// the first free colonist would run it (RM_CompWaterVolume.PostIngested: books unless bookedAtSource). The item is
        /// not consumed. "DRINK item=defName bookedAtSource=bool by=pawn".</summary>
        public static string ProofDrinkHook(string arg)
        {
            Map map = Find.CurrentMap;
            string[] a = (arg ?? "").Split(',');
            if (map == null || a.Length != 2 || !int.TryParse(a[0], out int x) || !int.TryParse(a[1], out int z))
            {
                return "REFUSED: arg must be x,z on a current map";
            }
            IntVec3 c = new IntVec3(x, 0, z);
            if (!c.InBounds(map))
            {
                return "REFUSED: out of bounds";
            }
            Pawn drinker = map.mapPawns.FreeColonistsSpawned.FirstOrFallback();
            if (drinker == null)
            {
                return "REFUSED: no free colonist on the map";
            }
            foreach (Thing t in c.GetThingList(map))
            {
                RM_CompWaterVolume comp = t.TryGetComp<RM_CompWaterVolume>();
                if (comp == null)
                {
                    continue;
                }
                comp.PostIngested(drinker);
                return "DRINK item=" + t.def.defName + " bookedAtSource=" + comp.Props.bookedAtSource + " by=" + drinker.ThingID;
            }
            return "NONE: no water item at " + x + "," + z;
        }
    }
}
