using System.Collections.Generic;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>
	/// The reusable liquid converter kit (owner, 2026-10-05: "Build the distillation and other associated
	/// machinery for liquids part of this mod"). One comp drives every still, filter, found works and the
	/// WreckedMachines ship distiller; what each does is DATA:
	///   • registry steps — a LiquidDef row's &lt;conversions&gt; (generator table LIQUID_CONVERSIONS): a step
	///     runs here when its process is in <see cref="processes"/> and its tier is at or below <see cref="tier"/>;
	///   • distillsAny — WRECKED_DISTILLATION_MODULE_1: any row flagged &lt;distillable&gt; reduces to
	///     <see cref="distillProduct"/> (tar, oil, chemfuel and slime are not flagged, so they are refused).
	/// Input comes from a tank on the machine's liquid net (RM_LiquidNet: touching it or hosed to it); the
	/// product goes into another tank on the net, or — for a step with productThing — is dropped as items when
	/// no tank takes it. Needs whatever vanilla comps the def carries: power on, fuel in, switch on; a solar
	/// still needs open sky in daylight. Every rate is PROVISIONAL.
	/// </summary>
	public class CompProperties_LiquidConverter : CompProperties
	{
		public LiquidConversionTier tier = LiquidConversionTier.Crude;
		public List<string> processes = new List<string>();

		public bool distillsAny;
		public LiquidDef distillProduct;
		public int distillInputUnits = 2;
		public int distillOutputUnits = 1;

		/// <summary>Input units this machine can process per day at 1x (PROVISIONAL per def).</summary>
		public float inputUnitsPerDay = 24f;

		/// <summary>Repair-tier multiplier (WreckedMachines grammar: kludged slower than repaired).</summary>
		public float tierRate = 1f;

		public bool needsSun;

		/// <summary>Fuel burned per working day when the def carries CompRefuelable (PROVISIONAL).</summary>
		public float fuelPerDay;

		public CompProperties_LiquidConverter()
		{
			compClass = typeof(CompLiquidConverter);
		}

		public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
		{
			foreach (string e in base.ConfigErrors(parentDef))
			{
				yield return e;
			}
			if (processes.NullOrEmpty() && !distillsAny)
			{
				yield return "CompProperties_LiquidConverter on " + parentDef.defName + " has no processes and does not distillsAny: it can never run.";
			}
			if (distillsAny && distillProduct == null)
			{
				yield return "CompProperties_LiquidConverter on " + parentDef.defName + ": distillsAny needs distillProduct.";
			}
			if (parentDef.tickerType != TickerType.Rare)
			{
				yield return "CompProperties_LiquidConverter on " + parentDef.defName + " needs <tickerType>Rare</tickerType> (it works on the rare tick).";
			}
		}
	}

	public class CompLiquidConverter : ThingComp
	{
		private float accrued;
		public int totalIn;
		public int totalOut;
		private string status = "";
		private LiquidDef lastRefused;

		public CompProperties_LiquidConverter Props => (CompProperties_LiquidConverter)props;

		public string Status => status;

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref accrued, "RM_convAccrued", 0f);
			Scribe_Values.Look(ref totalIn, "RM_convIn", 0);
			Scribe_Values.Look(ref totalOut, "RM_convOut", 0);
		}

		/// <summary>The step this machine would run on <paramref name="liquid"/>, or null.</summary>
		public LiquidConversion StepFor(LiquidDef liquid)
		{
			if (liquid == null)
			{
				return null;
			}
			if (!liquid.conversions.NullOrEmpty())
			{
				foreach (LiquidConversion c in liquid.conversions)
				{
					if (c?.product == null && c?.productThing == null)
					{
						continue;
					}
					if (c.tier <= Props.tier && Props.processes.Contains(c.process)
						&& (c.building == null || c.building == parent.def))
					{
						return c;
					}
				}
			}
			if (Props.distillsAny && liquid.distillable && liquid != Props.distillProduct)
			{
				return new LiquidConversion
				{
					tier = Props.tier,
					process = "distill",
					product = Props.distillProduct,
					inputUnits = Props.distillInputUnits,
					outputUnits = Props.distillOutputUnits
				};
			}
			return null;
		}

		private float EnvironmentFactor(out string why)
		{
			why = null;
			if (!RM_MachinerySettings.MachineOn(parent.def))
			{
				why = "RMFlow_MachineOffInSettings".Translate();
				return 0f;
			}
			CompFlickable flick = parent.GetComp<CompFlickable>();
			if (flick != null && !flick.SwitchIsOn)
			{
				why = "RMFlow_MachineSwitchedOff".Translate();
				return 0f;
			}
			CompPowerTrader power = parent.GetComp<CompPowerTrader>();
			if (power != null && !power.PowerOn)
			{
				why = "RMFlow_MachineNoPower".Translate();
				return 0f;
			}
			CompRefuelable fuel = parent.GetComp<CompRefuelable>();
			if (fuel != null && !fuel.HasFuel)
			{
				why = "RMFlow_MachineNoFuel".Translate();
				return 0f;
			}
			if (Props.needsSun)
			{
				float f = RM_ConversionMath.SunFactor(parent.Map.skyManager.CurSkyGlow, parent.Position.Roofed(parent.Map));
				if (f <= 0f)
				{
					why = "RMFlow_MachineNoSun".Translate();
				}
				return f;
			}
			return 1f;
		}

		public override void CompTickRare()
		{
			base.CompTickRare();
			if (parent.Map == null)
			{
				return;
			}
			float env = EnvironmentFactor(out string why);
			if (env <= 0f)
			{
				status = why ?? "";
				return;
			}
			float perTick = RM_ConversionMath.BudgetPerRareTick(Props.inputUnitsPerDay, Props.tierRate,
				RM_MachinerySettings.converterRateMultiplier, env);
			accrued += perTick;

			List<Building_LiquidTank> tanks = RM_LiquidNet.TanksFor(parent);
			LiquidDef refused = null;
			bool anyInput = false;
			foreach (Building_LiquidTank input in tanks)
			{
				if (input.Empty)
				{
					continue;
				}
				LiquidConversion step = StepFor(input.storedLiquid);
				if (step == null)
				{
					// The product's own tank is not "refused" — it is where the output goes.
					if (!IsSomeProduct(input.storedLiquid))
					{
						refused = refused ?? input.storedLiquid;
					}
					continue;
				}
				anyInput = true;
				accrued = RM_ConversionMath.CapAccrued(accrued, step.inputUnits, perTick);
				Building_LiquidTank output = step.product != null
					? RM_LiquidNet.TankToFill(parent, step.product, step.outputUnits, input)
					: null;
				int room = output != null
					? output.Capacity - output.storedUnits
					: (step.productThing != null ? -1 : 0);
				int n = RM_ConversionMath.Batches(accrued, step.inputUnits, step.outputUnits, input.storedUnits, room);
				if (n <= 0)
				{
					if (room == 0)
					{
						status = "RMFlow_ConverterNoOutput".Translate((step.product?.label ?? step.productThing?.label) ?? "?");
						return;
					}
					status = "RMFlow_ConverterWorking".Translate(input.storedLiquid.label,
						(step.product?.label ?? step.productThing?.label) ?? "?");
					return;
				}
				LiquidDef inputLiquid = input.storedLiquid;
				input.TryRemoveLiquid(n * step.inputUnits);
				int made = n * step.outputUnits;
				if (output != null)
				{
					output.TryAddLiquid(step.product, made);
				}
				else
				{
					DropItems(step.productThing, made);
				}
				accrued -= n * step.inputUnits;
				totalIn += n * step.inputUnits;
				totalOut += made;
				CompRefuelable fuel = parent.GetComp<CompRefuelable>();
				if (fuel != null && Props.fuelPerDay > 0f)
				{
					fuel.ConsumeFuel(Props.fuelPerDay / RM_ConversionMath.RareTicksPerDay);
				}
				status = "RMFlow_ConverterWorking".Translate(inputLiquid.label,
					(step.product?.label ?? step.productThing?.label) ?? "?");
				return;
			}
			if (!anyInput)
			{
				accrued = RM_ConversionMath.CapAccrued(accrued, 1, perTick);
			}
			if (refused != null)
			{
				status = "RMFlow_ConverterRefuses".Translate(refused.label);
				if (refused != lastRefused && parent.Faction == Faction.OfPlayer)
				{
					Messages.Message("RMFlow_ConverterRefusesMessage".Translate(parent.LabelCap, refused.label),
						parent, MessageTypeDefOf.RejectInput, historical: false);
				}
				lastRefused = refused;
				return;
			}
			status = tanks.Count == 0 ? "RMFlow_ConverterNoTank".Translate() : "RMFlow_ConverterNothingToDo".Translate();
		}

		private bool IsSomeProduct(LiquidDef liquid)
		{
			if (Props.distillsAny && liquid == Props.distillProduct)
			{
				return true;
			}
			foreach (LiquidDef l in DefDatabase<LiquidDef>.AllDefsListForReading)
			{
				if (l.conversions.NullOrEmpty())
				{
					continue;
				}
				foreach (LiquidConversion c in l.conversions)
				{
					if (c.product == liquid && Props.processes.Contains(c.process))
					{
						return true;
					}
				}
			}
			return false;
		}

		private void DropItems(ThingDef def, int count)
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
			return s + "\n" + "RMFlow_ConverterTotals".Translate(totalIn, totalOut);
		}
	}
}
