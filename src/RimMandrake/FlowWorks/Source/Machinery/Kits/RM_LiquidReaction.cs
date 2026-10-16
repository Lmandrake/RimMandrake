using System.Collections.Generic;
using System.Linq;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Machinery.Kits
{
	/// <summary>
	/// Two liquids that react when mixed (SUMP_GASLIGHT_1: "tar + acid → green gas"). Data, not code: a kit
	/// adds a row or patches a product onto one. Per batch the vat eats <see cref="litresA"/> of A and
	/// <see cref="litresB"/> of B (LITRES) and makes, in order of preference:
	///   productLiquid — into a tank on the vat's net that takes it;
	///   productThing  — dropped beside the vat as items (the Sump patches RM_TarGas here);
	///   else the reaction VENTS: <see cref="ventGas"/> rises from the vat (a readable sign, never a silent loss).
	/// <see cref="ventGasAmount"/> also escapes on every batch that does make a product, when &gt; 0 and
	/// <see cref="ventAlways"/> is set. All amounts PROVISIONAL.
	/// </summary>
	public class RM_LiquidReactionDef : Def
	{
		public LiquidDef reactantA;
		public LiquidDef reactantB;
		/// <summary>One batch in LITRES (LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS: the old per-batch units × 200 L).</summary>
		public float litresA = 200f;
		public float litresB = 200f;
		public LiquidDef productLiquid;
		public ThingDef productThing;
		/// <summary>Product liquid per batch, litres.</summary>
		public float productLitres = 200f;
		/// <summary>Product items per batch when no tank takes the product (productThing).</summary>
		public int productCount = 1;

		/// <summary>The batch in tank units (decilitres).</summary>
		public int UnitsA => RM_Volume.Units(litresA);
		public int UnitsB => RM_Volume.Units(litresB);
		public int ProductUnits => RM_Volume.Units(productLitres);
		public GasType ventGas = GasType.ToxGas;
		public int ventGasAmount = 40;
		public bool ventAlways;

		public override IEnumerable<string> ConfigErrors()
		{
			foreach (string e in base.ConfigErrors())
			{
				yield return e;
			}
			if (reactantA == null || reactantB == null)
			{
				yield return defName + ": a reaction needs reactantA and reactantB.";
			}
			if (reactantA != null && reactantA == reactantB)
			{
				yield return defName + ": reactantA and reactantB are the same liquid.";
			}
			if (UnitsA < 1 || UnitsB < 1 || ProductUnits < 1 || productCount < 1)
			{
				yield return defName + ": litresA, litresB and productLitres must be at least 0.1, productCount at least 1.";
			}
		}

		public string ProductLabel => productLiquid?.label ?? productThing?.label ?? "gas";
	}

	/// <summary>A reaction vat: runs every RM_LiquidReactionDef whose two reactants it finds in tanks on its
	/// liquid net (or only <see cref="reactions"/>, when listed). Honours power/fuel/switch like a converter.</summary>
	public class CompProperties_LiquidReactor : CompProperties
	{
		public List<RM_LiquidReactionDef> reactions;

		/// <summary>Batches per day at 1x (PROVISIONAL).</summary>
		public float batchesPerDay = 12f;

		public CompProperties_LiquidReactor()
		{
			compClass = typeof(CompLiquidReactor);
		}

		public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
		{
			foreach (string e in base.ConfigErrors(parentDef))
			{
				yield return e;
			}
			if (parentDef.tickerType != TickerType.Rare)
			{
				yield return "CompProperties_LiquidReactor on " + parentDef.defName + " needs <tickerType>Rare</tickerType>.";
			}
		}
	}

	public class CompLiquidReactor : ThingComp
	{
		private float accrued;
		public int batchesRun;
		public int gasVented;
		private string status = "";

		public CompProperties_LiquidReactor Props => (CompProperties_LiquidReactor)props;

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref accrued, "RM_reactAccrued", 0f);
			Scribe_Values.Look(ref batchesRun, "RM_reactBatches", 0);
			Scribe_Values.Look(ref gasVented, "RM_reactGas", 0);
		}

		private IEnumerable<RM_LiquidReactionDef> Candidates()
		{
			return Props.reactions.NullOrEmpty()
				? (IEnumerable<RM_LiquidReactionDef>)DefDatabase<RM_LiquidReactionDef>.AllDefsListForReading
				: Props.reactions;
		}

		private bool Blocked(out string why)
		{
			why = null;
			if (!RM_KitSettings.liquidReactionsEnabled || !RM_MachinerySettings.MachineOn(parent.def))
			{
				why = "RMFlow_MachineOffInSettings".Translate();
				return true;
			}
			CompFlickable flick = parent.GetComp<CompFlickable>();
			if (flick != null && !flick.SwitchIsOn)
			{
				why = "RMFlow_MachineSwitchedOff".Translate();
				return true;
			}
			CompPowerTrader power = parent.GetComp<CompPowerTrader>();
			if (power != null && !power.PowerOn)
			{
				why = "RMFlow_MachineNoPower".Translate();
				return true;
			}
			CompRefuelable fuel = parent.GetComp<CompRefuelable>();
			if (fuel != null && !fuel.HasFuel)
			{
				why = "RMFlow_MachineNoFuel".Translate();
				return true;
			}
			return false;
		}

		public override void CompTickRare()
		{
			base.CompTickRare();
			if (parent.Map == null)
			{
				return;
			}
			if (Blocked(out string why))
			{
				status = why ?? "";
				return;
			}
			float perTick = RM_KitMath.BatchesPerRareTick(Props.batchesPerDay, RM_KitSettings.reactionRateMultiplier);
			accrued = System.Math.Min(accrued + perTick, System.Math.Max(1f, perTick));
			List<Building_LiquidTank> tanks = RM_LiquidNet.TanksFor(parent);
			foreach (RM_LiquidReactionDef r in Candidates())
			{
				if (r?.reactantA == null || r.reactantB == null)
				{
					continue;
				}
				// L3 (rev 2 §3.2): each reactant may come from several tanks (draw plan) and the product may split across tanks
				// (fill plan); G9: a vat that drew reactant A last yields it while another machine on A went without
				int now = Find.TickManager.TicksGame;
				RM_ConsumerRotation rotation = RM_LiquidNet.Rotation(parent.Map);
				object rotKey = RM_ConsumerRotation.Key(r.reactantA, tanks.Count > 0 ? tanks.Min(t => t.thingIDNumber) : 0);   // C1-F4: per store
				int haveA = RM_LiquidNet.Available(parent, r.reactantA), haveB = RM_LiquidNet.Available(parent, r.reactantB);
				if (haveA < r.UnitsA || haveB < r.UnitsB)
				{
					if (haveA > 0 && haveB > 0)
					{
						rotation.Starved(rotKey, parent.thingIDNumber, now);
					}
					continue;
				}
				int roomP = r.productLiquid != null ? RM_LiquidNet.Room(parent, r.productLiquid) : -1;
				bool toTank = r.productLiquid != null && roomP >= r.ProductUnits;
				int n = RM_KitMath.ReactionBatches(accrued, r.UnitsA, r.UnitsB, haveA, haveB, r.ProductUnits, toTank ? roomP : -1);
				if (n > 0 && !rotation.MayDraw(rotKey, parent.thingIDNumber, now))
				{
					rotation.Starved(rotKey, parent.thingIDNumber, now);
					n = 0;
				}
				if (n <= 0)
				{
					status = "RMFlow_ReactorWorking".Translate(r.reactantA.label, r.reactantB.label, r.ProductLabel);
					return;
				}
				List<(Building_LiquidTank tank, int units)> pa = RM_LiquidNet.DrawPlan(parent, r.reactantA, n * r.UnitsA);
				List<(Building_LiquidTank tank, int units)> pb = RM_LiquidNet.DrawPlan(parent, r.reactantB, n * r.UnitsB);
				List<(Building_LiquidTank tank, int units)> pp = toTank ? RM_LiquidNet.FillPlan(parent, r.productLiquid, n * r.ProductUnits) : null;
				if (pa == null || pb == null || (toTank && pp == null))
				{
					status = "RMFlow_ReactorWorking".Translate(r.reactantA.label, r.reactantB.label, r.ProductLabel);
					return;
				}
				// L1 (§4): both reactants and the product are one committed move (in batches). A and B are removed first and put
				// back together if the product tanks refuse; with no product tank the product is dropped as items, else it vents.
				RM_TransferLeg dest = pp != null
					? RM_TransferLeg.Split(pp.Count, i => pp[i].units, (i, k) => pp[i].tank.CanAccept(r.productLiquid, k), (i, k) => pp[i].tank.TryAddLiquid(r.productLiquid, k), (i, k) => pp[i].tank.TryRemoveLiquid(k), r.ProductUnits)
					: RM_TransferLeg.Sink(k => { if (r.productThing != null) Drop(r.productThing, k * r.productCount); });
				if (RM_LiquidTransfer.Move(n, RM_TransferLeg.All(RM_TransferLeg.Split(pa.Count, i => pa[i].units, (i, k) => pa[i].tank.CanProvide(k), (i, k) => pa[i].tank.TryRemoveLiquid(k), (i, k) => pa[i].tank.TryAddLiquid(r.reactantA, k), r.UnitsA), RM_TransferLeg.Split(pb.Count, i => pb[i].units, (i, k) => pb[i].tank.CanProvide(k), (i, k) => pb[i].tank.TryRemoveLiquid(k), (i, k) => pb[i].tank.TryAddLiquid(r.reactantB, k), r.UnitsB)), dest, out _) == n)
				{
					foreach ((Building_LiquidTank tank, int units) p in pa) RM_LiquidNet.Credit(parent, p.tank, r.reactantA, p.units, RM_ConversionMath.RareTick);   // credit site: reactor A
					foreach ((Building_LiquidTank tank, int units) p in pb) RM_LiquidNet.Credit(parent, p.tank, r.reactantB, p.units, RM_ConversionMath.RareTick);   // credit site: reactor B
					foreach ((Building_LiquidTank tank, int units) p in pp ?? Enumerable.Empty<(Building_LiquidTank, int)>()) RM_LiquidNet.Credit(parent, p.tank, r.productLiquid, p.units, RM_ConversionMath.RareTick);   // credit site: reactor product (no tank: no credit)
				}
				else
				{
					status = "RMFlow_ReactorWorking".Translate(r.reactantA.label, r.reactantB.label, r.ProductLabel);
					return;
				}
				rotation.Served(rotKey, parent.thingIDNumber, now);
				accrued -= n;
				batchesRun += n;
				bool made = pp != null || r.productThing != null;
				if ((!made || r.ventAlways) && r.ventGasAmount > 0)
				{
					IntVec3 at = parent.def.hasInteractionCell ? parent.InteractionCell : parent.Position;
					GasUtility.AddGas(at, parent.Map, r.ventGas, n * r.ventGasAmount);
					gasVented += n * r.ventGasAmount;
				}
				status = "RMFlow_ReactorWorking".Translate(r.reactantA.label, r.reactantB.label,
					made ? r.ProductLabel : "RMFlow_ReactorVented".Translate().ToString());
				return;
			}
			status = tanks.Count == 0 ? (RM_LiquidNet.TooLarge(parent) ? "RMFlow_NetTooLarge".Translate() : "RMFlow_ConverterNoTank".Translate()) : "RMFlow_ReactorNoPair".Translate();
		}

		private void Drop(ThingDef def, int count)
		{
			while (count > 0)
			{
				Thing t = ThingMaker.MakeThing(def);
				t.stackCount = System.Math.Min(count, def.stackLimit);
				count -= t.stackCount;
				IntVec3 at = parent.def.hasInteractionCell ? parent.InteractionCell : parent.Position;
				RM_LiquidBottleUtility.PlacePaidFor(t, at, parent.Map);   // C1-F13: the reactants are already spent
			}
		}

		public override string CompInspectStringExtra()
		{
			string s = status.NullOrEmpty() ? "RMFlow_ConverterIdle".Translate().ToString() : status;
			return s + "\n" + "RMFlow_ReactorTotals".Translate(batchesRun, gasVented);
		}
	}
}
