using System.Collections.Generic;
using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.Abyss
{
    // ABYSS_LIGHTFALL_BROOD_WRECK_1 — the Ship in the Wall. A wrecked rescue gravship driven into the
    // lair wall. It is a SALVAGE SITE, never a second ship (owner, typed 2026-10-01: "You can't have two
    // ships but you can cannibalize that one to improve yours ... their ship only wants certain parts.
    // It likes what it is and doesn't want deep redesign. Just repair.").
    //
    // Salvage = bills at the wreck (vanilla WorkGiver_DoBill drives the work, no custom job). Each cut
    // spends one unit of that part's stock and feeds the brood's wake meter by the part's greed weight.
    // Parts fitted to the player's ship (CompUseEffect below) repair worn ship buildings; a part the ship
    // will not take says so in plain words and stays loot (sell or smelt).

    public class RM_WreckStockExtension : DefModExtension
    {
        public List<ThingDefCountClass> stock = new List<ThingDefCountClass>();
    }

    public class RM_ShipPartExtension : DefModExtension
    {
        public float greed = BroodWakeLogic.PartWeightDefault;
    }

    public class Building_RM_ShipWreck : Building_WorkTable
    {
        private Dictionary<ThingDef, int> left;

        private void EnsureStock()
        {
            if (left != null) return;
            left = new Dictionary<ThingDef, int>();
            RM_WreckStockExtension ext = def.GetModExtension<RM_WreckStockExtension>();
            if (ext == null) return;
            foreach (ThingDefCountClass s in ext.stock) if (s.thingDef != null) left[s.thingDef] = s.count;
        }

        public int Left(ThingDef part)
        {
            EnsureStock();
            return part != null && left.TryGetValue(part, out int n) ? n : 0;
        }

        public int TotalLeft()
        {
            EnsureStock();
            int t = 0;
            foreach (int n in left.Values) t += n;
            return t;
        }

        public void Spend(ThingDef part, RecipeDef recipe)
        {
            EnsureStock();
            if (part == null || !left.ContainsKey(part)) return;
            left[part] = System.Math.Max(0, left[part] - 1);
            if (left[part] == 0)
            {
                for (int i = BillStack.Bills.Count - 1; i >= 0; i--)
                    if (BillStack.Bills[i].recipe == recipe) BillStack.Delete(BillStack.Bills[i]);
            }
            if (TotalLeft() == 0)
                Messages.Message("The rescue ship in the wall is stripped. Nothing more worth cutting remains.", this, MessageTypeDefOf.NeutralEvent);
        }

        public override string GetInspectString()
        {
            EnsureStock();
            var sb = new StringBuilder(base.GetInspectString());
            if (sb.Length > 0) sb.AppendLine();
            int total = TotalLeft();
            sb.Append(total > 0
                ? "Still worth cutting: " + total + " fittings. Cutting is loud work, and she is asleep nearby."
                : "Stripped.");
            return sb.ToString();
        }

        public override void ExposeData()
        {
            base.ExposeData();
            List<ThingDef> keys = null;
            List<int> vals = null;
            if (Scribe.mode == LoadSaveMode.Saving) EnsureStock();
            Scribe_Collections.Look(ref left, "partsLeft", LookMode.Def, LookMode.Value, ref keys, ref vals);
        }
    }

    public class RM_RecipeWorker_WreckSalvage : RecipeWorker
    {
        private ThingDef Part => recipe.products != null && recipe.products.Count > 0 ? recipe.products[0].thingDef : null;

        public override bool AvailableOnNow(Thing thing, BodyPartRecord part = null)
        {
            if (thing is Building_RM_ShipWreck w) return w.Left(Part) > 0;
            return base.AvailableOnNow(thing, part);
        }

        public override void Notify_IterationCompleted(Pawn billDoer, List<Thing> ingredients)
        {
            base.Notify_IterationCompleted(billDoer, ingredients);
            if (!(billDoer?.CurJob?.targetA.Thing is Building_RM_ShipWreck w)) return;
            ThingDef p = Part;
            w.Spend(p, recipe);
            float greed = p?.GetModExtension<RM_ShipPartExtension>()?.greed ?? BroodWakeLogic.PartWeightDefault;
            RM_MapComponent_BroodWake.For(w.Map)?.Notify(greed, "salvage cutting");
        }
    }

    // ── fitting a part to the player's own ship ───────────────────────────────
    public class CompProperties_RM_FitToShip : CompProperties_UseEffect
    {
        public bool accepted = true;
        public int repairBudget = 400;
        public CompProperties_RM_FitToShip() { compClass = typeof(RM_CompUseEffect_FitToShip); }
    }

    public class RM_CompUseEffect_FitToShip : CompUseEffect
    {
        private CompProperties_RM_FitToShip Props => (CompProperties_RM_FitToShip)props;

        private static List<Building> WornShipBuildings(Map map)
        {
            var worn = new List<Building>();
            if (map == null) return worn;
            List<Building> all = map.listerBuildings.allBuildingsColonist;
            for (int i = 0; i < all.Count; i++)
            {
                Building b = all[i];
                if (!b.def.useHitPoints || b.HitPoints >= b.MaxHitPoints) continue;
                if (map.terrainGrid.FoundationAt(b.Position)?.IsSubstructure ?? false) worn.Add(b);
            }
            return worn;
        }

        public override AcceptanceReport CanBeUsedBy(Pawn p)
        {
            FitResult r = ShipFitLogic.Decide(Props.accepted, WornShipBuildings(p.Map).Count);
            if (r != FitResult.Fits) return ShipFitLogic.Reason(r);
            return base.CanBeUsedBy(p);
        }

        public override void DoEffect(Pawn usedBy)
        {
            base.DoEffect(usedBy);
            List<Building> worn = WornShipBuildings(usedBy.Map);
            int[] missing = new int[worn.Count];
            for (int i = 0; i < worn.Count; i++) missing[i] = worn[i].MaxHitPoints - worn[i].HitPoints;
            int[] give = ShipFitLogic.Spread(missing, Props.repairBudget);
            int restored = 0, fixedCount = 0;
            for (int i = 0; i < worn.Count; i++)
            {
                if (give[i] <= 0) continue;
                worn[i].HitPoints += give[i];
                usedBy.Map.listerBuildingsRepairable.Notify_BuildingRepaired(worn[i]);
                restored += give[i];
                fixedCount++;
            }
            Messages.Message("The ship takes the " + parent.LabelNoCount + ": " + fixedCount + " worn fittings aboard restored (" + restored + " points). It is a little more what it was.",
                usedBy, MessageTypeDefOf.PositiveEvent);
        }
    }
}
