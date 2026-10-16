using System.Collections.Generic;
using System.Text;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using Verse;

namespace RimMandrake.Cauldron
{
    // ════════════════════════════════════════════════════════════════════
    // CAULDRON_MECHANICS_BUILD_1 part 3 — THE GAS-TAP SCAFFOLD. "caps a vent: stops the leak AND banks flow for refining —
    // safety and industry as one act."
    //
    // Built only exactly over a vent (RM_PlaceWorker_OnCauldronVent, the PlaceWorker_OnSteamGeyser shape). While it stands
    // the vent is capped (RM_Building_CauldronVent.IsCapped): no gas, no puffs. Every rare tick it banks condensate in
    // proportion to the vent's output (a chronic leak twice as fast, a silenced vent not at all) up to a small cap, and
    // pours whole units into any FlowWorks liquid tank TOUCHING it as RM_Liquid_VentCondensate — the input the Filter-Works
    // refines into reagents. Touching only, deliberately: it is not a FlowWorks net member (net roles are FlowWorks'
    // own types), so a hose line to it would do nothing; stand a tank beside it.
    //
    // A wild vexxiss still drinks a capped vent and pries at the scaffold while it does (RM_JobDriver_VexxissDrinkVent):
    // destroy the scaffold and the vent leaks again.
    // ════════════════════════════════════════════════════════════════════
    public class RM_CompProperties_GasTap : CompProperties
    {
        public LiquidDef condensate;

        public RM_CompProperties_GasTap()
        {
            compClass = typeof(RM_CompGasTap);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef)) yield return e;
            if (condensate == null) yield return "RM_CompProperties_GasTap on " + parentDef.defName + " has no condensate LiquidDef";
            if (parentDef.tickerType != TickerType.Rare) yield return "RM_CompProperties_GasTap on " + parentDef.defName + " needs <tickerType>Rare</tickerType>";
        }
    }

    public class RM_CompGasTap : ThingComp
    {
        public float bank;
        public int unitsDelivered;

        public RM_CompProperties_GasTap Props => (RM_CompProperties_GasTap)props;

        public RM_Building_CauldronVent Vent
        {
            get
            {
                if (!parent.Spawned) return null;
                List<Thing> things = parent.Position.GetThingList(parent.Map);
                for (int i = 0; i < things.Count; i++)
                    if (things[i] is RM_Building_CauldronVent v) return v;
                return null;
            }
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            RM_Building_CauldronVent vent = Vent;
            if (vent == null) return;
            bank = RM_VentGasKernel.TapAccrue(bank, RM_CauldronSettings.gasTapBanksCondensate, vent.Output,
                vent.temperament == RM_VentTemperament.Leaking);
            Deliver();
        }

        // LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS: one banked unit is 200 L of condensate (the old FlowWorks tank unit); a tank
        // counts decilitres, so each banked unit goes in as RM_Volume.Units(200 L).
        public const float LitresPerBankUnit = 200f;

        // Whole units into touching tanks, as many as they take.
        private void Deliver()
        {
            int ready = RM_VentGasKernel.TapReady(bank);
            if (ready <= 0 || Props.condensate == null) return;
            int per = RimMandrake.FlowWorks.RM_Volume.Units(LitresPerBankUnit);
            foreach (Building_LiquidTank tank in TouchingTanks())
            {
                if (ready <= 0) break;
                int n = ready;
                while (n > 0 && !tank.CanAccept(Props.condensate, n * per)) n--;
                if (n <= 0 || !tank.TryAddLiquid(Props.condensate, n * per)) continue;
                bank -= n;
                ready -= n;
                unitsDelivered += n;
            }
        }

        public List<Building_LiquidTank> TouchingTanks()
        {
            var result = new List<Building_LiquidTank>();
            if (!parent.Spawned) return result;
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(parent))
            {
                if (!c.InBounds(parent.Map)) continue;
                List<Thing> things = c.GetThingList(parent.Map);
                for (int i = 0; i < things.Count; i++)
                    if (things[i] is Building_LiquidTank t && !result.Contains(t)) result.Add(t);
            }
            return result;
        }

        public override string CompInspectStringExtra()
        {
            var sb = new StringBuilder();
            RM_Building_CauldronVent vent = Vent;
            if (vent == null)
            {
                sb.Append("Gas tap: not on a vent");
                return sb.ToString();
            }
            sb.Append("Gas tap: vent capped; condensate banked " + bank.ToString("0.0") + " / " + RM_VentGasKernel.TapBankCap.ToString("0"));
            sb.AppendLine();
            int tanks = TouchingTanks().Count;
            sb.Append("Delivered " + unitsDelivered + " units; " + (tanks == 0 ? "no tank touching it" : tanks + " tank(s) touching it"));
            sb.AppendLine();
            sb.Append("Scaffold: " + parent.HitPoints + " / " + parent.MaxHitPoints + " HP");   // read by validation.py (prying)
            return sb.ToString();
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref bank, "rmGasTapBank", 0f);
            Scribe_Values.Look(ref unitsDelivered, "rmGasTapDelivered", 0);
        }
    }

    // PlaceWorker_OnSteamGeyser's shape: the scaffold must stand exactly on a vent (same Position, the vent is 2x2 like it).
    public class RM_PlaceWorker_OnCauldronVent : PlaceWorker
    {
        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
        {
            List<Thing> things = loc.GetThingList(map);
            for (int i = 0; i < things.Count; i++)
                if (things[i] is RM_Building_CauldronVent v && v.Position == loc) return true;
            return "Must be placed exactly over a vent.";
        }

        public override bool ForceAllowPlaceOver(BuildableDef otherDef)
        {
            return otherDef == RM_CauldronDefOf.RM_CauldronVent;
        }
    }
}
