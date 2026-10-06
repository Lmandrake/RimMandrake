using System.Collections.Generic;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Machinery.Kits
{
	/// <summary>
	/// Two liquids that react when mixed (SUMP_GASLIGHT_1: "tar + acid → green gas"). Data, not code: a kit
	/// adds a row or patches a product onto one. Per batch the vat eats <see cref="unitsA"/> of A and
	/// <see cref="unitsB"/> of B and makes, in order of preference:
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
		public int unitsA = 1;
		public int unitsB = 1;
		public LiquidDef productLiquid;
		public ThingDef productThing;
		public int productUnits = 1;
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
			if (unitsA < 1 || unitsB < 1 || productUnits < 1)
			{
				yield return defName + ": unitsA, unitsB and productUnits must be at least 1.";
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

		private static Building_LiquidTank Holding(List<Building_LiquidTank> tanks, LiquidDef liquid, int units)
		{
			foreach (Building_LiquidTank t in tanks)
			{
				if (!t.Empty && t.storedLiquid == liquid && t.storedUnits >= units)
				{
					return t;
				}
			}
			return null;
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
				Building_LiquidTank a = Holding(tanks, r.reactantA, r.unitsA);
				Building_LiquidTank b = Holding(tanks, r.reactantB, r.unitsB);
				if (a == null || b == null)
				{
					continue;
				}
				Building_LiquidTank outTank = r.productLiquid != null
					? RM_LiquidNet.TankToFill(parent, r.productLiquid, r.productUnits, a)
					: null;
				int room = outTank != null ? outTank.Capacity - outTank.storedUnits : -1;
				int n = RM_KitMath.ReactionBatches(accrued, r.unitsA, r.unitsB, a.storedUnits, b.storedUnits,
					r.productUnits, room);
				if (n <= 0)
				{
					status = "RMFlow_ReactorWorking".Translate(r.reactantA.label, r.reactantB.label, r.ProductLabel);
					return;
				}
				a.TryRemoveLiquid(n * r.unitsA);
				b.TryRemoveLiquid(n * r.unitsB);
				accrued -= n;
				batchesRun += n;
				bool made = false;
				if (outTank != null)
				{
					made = outTank.TryAddLiquid(r.productLiquid, n * r.productUnits);
				}
				else if (r.productThing != null)
				{
					Drop(r.productThing, n * r.productUnits);
					made = true;
				}
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
			status = tanks.Count == 0 ? "RMFlow_ConverterNoTank".Translate() : "RMFlow_ReactorNoPair".Translate();
		}

		private void Drop(ThingDef def, int count)
		{
			while (count > 0)
			{
				Thing t = ThingMaker.MakeThing(def);
				t.stackCount = System.Math.Min(count, def.stackLimit);
				count -= t.stackCount;
				IntVec3 at = parent.def.hasInteractionCell ? parent.InteractionCell : parent.Position;
				GenPlace.TryPlaceThing(t, at, parent.Map, ThingPlaceMode.Near);
			}
		}

		public override string CompInspectStringExtra()
		{
			string s = status.NullOrEmpty() ? "RMFlow_ConverterIdle".Translate().ToString() : status;
			return s + "\n" + "RMFlow_ReactorTotals".Translate(batchesRun, gasVented);
		}
	}
}
