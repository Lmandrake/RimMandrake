using System.Collections.Generic;
using System.Linq;
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
	/// product goes into another tank on the net; items come out only for a step that
	/// has a productThing and no liquid product (they are placed beside the machine, never a fallback for a full tank). Needs whatever vanilla comps the def carries: power on, fuel in, switch on; a solar
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
		/// <summary>G6 (L1): item output made but not yet placed (no room beside the machine). Saved; placed on later rare ticks,
		/// never dropped from the ledger. One item kind at a time: a different product waits until this is placed.</summary>
		public ThingDef pendingThing;
		public int pendingCount;
		/// <summary>C1-F16: the input liquid that ran last, so a machine with several inputs takes them in turn (saved).</summary>
		private LiquidDef lastInput;

		public CompProperties_LiquidConverter Props => (CompProperties_LiquidConverter)props;

		public string Status => status;

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref accrued, "RM_convAccrued", 0f);
			Scribe_Values.Look(ref totalIn, "RM_convIn", 0);
			Scribe_Values.Look(ref totalOut, "RM_convOut", 0);
			Scribe_Defs.Look(ref pendingThing, "RM_convPendingThing");
			Scribe_Values.Look(ref pendingCount, "RM_convPendingCount", 0);
			Scribe_Defs.Look(ref lastInput, "RM_convLastInput");
			if (Scribe.mode == LoadSaveMode.PostLoadInit && pendingThing == null)
			{
				pendingCount = 0;
			}
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
			PlacePending();
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
			string blocked = null;
			int now = Find.TickManager.TicksGame;
			RM_ConsumerRotation rotation = RM_LiquidNet.Rotation(parent.Map);
			int storeId = tanks.Count > 0 ? tanks.Min(t => t.thingIDNumber) : 0;   // C1-F4: turns are taken per store, never map-wide
			// P2 (hose port step 5; GPT review G1.15): every input LIQUID with a recipe is a candidate, in store order; the one
			// that runs is RM_ConversionMath.NextRunnable over their batch counts (selftested; C1-F16: after the one that ran last). L3 (rev 2 §3.2): a candidate is a
			// liquid, not a tank: its input may come from several tanks (draw plan) and its output may split across tanks (fill
			// plan). G9: a machine that drew a liquid last yields it while another machine on that liquid went without.
			var cand = new List<(LiquidDef input, LiquidConversion step, float capped)>();
			var batches = new List<int>();
			var seen = new HashSet<LiquidDef>();
			foreach (Building_LiquidTank tank in tanks)
			{
				if (tank.Empty || !seen.Add(tank.storedLiquid))
				{
					continue;
				}
				LiquidDef liquid = tank.storedLiquid;
				LiquidConversion step = StepFor(liquid);
				if (step == null)
				{
					// The product's own tank is not "refused" — it is where the output goes.
					if (!IsSomeProduct(liquid))
					{
						refused = refused ?? liquid;
					}
					continue;
				}
				anyInput = true;
				float capped = RM_ConversionMath.CapAccrued(accrued, step.inputUnits, perTick);
				int room = step.product != null
					? RM_LiquidNet.Room(parent, step.product)
					: (step.productThing != null ? -1 : 0);
				int n = RM_ConversionMath.Batches(capped, step.inputUnits, step.outputUnits, RM_LiquidNet.Available(parent, liquid), room);
				// "went without" (G9) means went without the LIQUID: budget and output room allowed a batch but the input did not,
				// or the rotation held us back. A machine idle for budget or a full output tank must not hold the other one back
				// (it would starve forever, and the machine that drew last could never draw again).
				bool wanted = n > 0 || RM_ConversionMath.Batches(capped, step.inputUnits, step.outputUnits, int.MaxValue, room) > 0;
				if (n > 0 && !rotation.MayDraw(RM_ConsumerRotation.Key(liquid, storeId), parent.thingIDNumber, now))
				{
					n = 0;   // our turn was last: the other machine on this liquid goes first this time
				}
				if (n <= 0)
				{
					if (wanted)
					{
						rotation.Starved(RM_ConsumerRotation.Key(liquid, storeId), parent.thingIDNumber, now);
					}
					if (blocked == null)
					{
						blocked = room == 0
							? (string)"RMFlow_ConverterNoOutput".Translate((step.product?.label ?? step.productThing?.label) ?? "?")
							: (string)"RMFlow_ConverterWorking".Translate(liquid.label, (step.product?.label ?? step.productThing?.label) ?? "?");
					}
				}
				cand.Add((liquid, step, capped));
				batches.Add(n);
			}
			int pick = RM_ConversionMath.NextRunnable(batches, cand.FindIndex(c => c.input == lastInput));
			if (cand.Count > 0)
			{
				accrued = cand[pick >= 0 ? pick : 0].capped;
			}
			if (pick >= 0)
			{
				var (inputLiquid, step, _) = cand[pick];
				int n = batches[pick];
				int made = n * step.outputUnits;
				List<(Building_LiquidTank tank, int units)> inPlan = RM_LiquidNet.DrawPlan(parent, inputLiquid, n * step.inputUnits);
				List<(Building_LiquidTank tank, int units)> outPlan = step.product != null ? RM_LiquidNet.FillPlan(parent, step.product, made) : null;
				if (inPlan == null || (step.product != null && outPlan == null))
				{
					status = "RMFlow_ConverterNoOutput".Translate((step.product?.label ?? step.productThing?.label) ?? "?");
					return;
				}
				// L1 (§4, G6): input and output are one committed move (in batches): the input is removed first and put back if the
				// output refuses; item output goes to the saved pending count, placed by PlacePending (never lost when there is no room)
				RM_TransferLeg dest = outPlan != null
					? RM_TransferLeg.Split(outPlan.Count, i => outPlan[i].units, (i, k) => outPlan[i].tank.CanAccept(step.product, k), (i, k) => outPlan[i].tank.TryAddLiquid(step.product, k), (i, k) => outPlan[i].tank.TryRemoveLiquid(k), step.outputUnits)
					: new RM_TransferLeg("pending", k => pendingCount == 0 || pendingThing == step.productThing, k => { pendingThing = step.productThing; pendingCount += k * step.outputUnits; return k; }, k => { pendingCount -= k * step.outputUnits; return true; });
				if (RM_LiquidTransfer.Move(n, RM_TransferLeg.Split(inPlan.Count, i => inPlan[i].units, (i, k) => inPlan[i].tank.CanProvide(k), (i, k) => inPlan[i].tank.TryRemoveLiquid(k), (i, k) => inPlan[i].tank.TryAddLiquid(inputLiquid, k), step.inputUnits),
					dest, out RM_MoveOutcome mv) == n)
				{
					foreach ((Building_LiquidTank tank, int units) p in inPlan) RM_LiquidNet.Credit(parent, p.tank, inputLiquid, p.units, RM_ConversionMath.RareTick);   // credit site: converter input
					foreach ((Building_LiquidTank tank, int units) p in outPlan ?? Enumerable.Empty<(Building_LiquidTank, int)>()) RM_LiquidNet.Credit(parent, p.tank, step.product, p.units, RM_ConversionMath.RareTick);   // credit site: converter output (items: no plan, no credit)
				}
				else
				{
					status = mv.DestRefused ? (string)"RMFlow_ConverterNoOutput".Translate((step.product?.label ?? step.productThing?.label) ?? "?") : (string)"RMFlow_ConverterNothingToDo".Translate();
					return;
				}
				rotation.Served(RM_ConsumerRotation.Key(inputLiquid, storeId), parent.thingIDNumber, now);
				lastInput = inputLiquid;
				PlacePending();
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
			if (blocked != null)
			{
				status = blocked;
				return;
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
			status = tanks.Count == 0 ? (RM_LiquidNet.TooLarge(parent) ? "RMFlow_NetTooLarge".Translate() : "RMFlow_ConverterNoTank".Translate()) : "RMFlow_ConverterNothingToDo".Translate();
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

		/// <summary>Places pending item output beside the machine; whatever finds no room stays pending (G6).</summary>
		private void PlacePending()
		{
			if (pendingThing == null || pendingCount <= 0 || parent.Map == null)
			{
				return;
			}
			IntVec3 at = parent.def.hasInteractionCell ? parent.InteractionCell : parent.Position;
			while (pendingCount > 0)
			{
				Thing t = ThingMaker.MakeThing(pendingThing);
				int count = System.Math.Min(pendingCount, pendingThing.stackLimit);
				t.stackCount = count;
				bool ok = GenPlace.TryPlaceThing(t, at, parent.Map, ThingPlaceMode.Near);
				int placed = ok || t.Destroyed ? count : count - t.stackCount;
				pendingCount -= placed;
				if (!ok)
				{
					break;
				}
			}
			if (pendingCount <= 0)
			{
				pendingCount = 0;
				pendingThing = null;
			}
		}

		public override string CompInspectStringExtra()
		{
			string s = status.NullOrEmpty() ? "RMFlow_ConverterIdle".Translate().ToString() : status;
			s += "\n" + "RMFlow_ConverterTotals".Translate(totalIn, totalOut);
			return pendingCount > 0 && pendingThing != null ? s + "\n" + "RMFlow_ConverterPending".Translate(pendingCount, pendingThing.label) : s;
		}
	}
}
