using System.Collections.Generic;
using Verse;

namespace RimMandrake.FluidCanals
{
	public class CompProperties_FluidReservoir : CompProperties
	{
		public FluidDef fluidDef;

		/// <summary>Volume of the small, frequent release -- "the reservoir
		/// breathes": a steady trickle that keeps a dug canal wet between the
		/// occasional big releases below. Owner ruling 2026-09-04
		/// (canon_reintegration_plan.md sec G8, "Fluid canal refill"): BOTH a
		/// drip and a periodic re-flood, not either/or -- "the drip carries the
		/// simulation, the flood carries the drama." Tuned by FOUNDRY (a bounded
		/// implementation choice, not a design call the ruling left open).</summary>
		public float dripVolume = 3f;

		/// <summary>Ticks between one drip and the next.</summary>
		public int dripIntervalTicks = 2500;

		/// <summary>Volume of the rare, large release -- the occasion. Fires
		/// once immediately when a canal first opens adjacent to this reservoir
		/// (the engine's original one-shot behavior, preserved), then again on
		/// this same cadence for as long as the canal stays open.</summary>
		public float reFloodVolume = 60f;

		/// <summary>Ticks between one re-flood occasion and the next. Default is
		/// 3 in-game days (GenDate.TicksPerDay = 60000) -- frequent enough to
		/// read as a recurring event, rare enough to stay an occasion rather
		/// than noise.</summary>
		public int reFloodIntervalTicks = 180000;

		public CompProperties_FluidReservoir()
		{
			compClass = typeof(CompFluidReservoir);
		}

		public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
		{
			foreach (string error in base.ConfigErrors(parentDef))
			{
				yield return error;
			}
			if (fluidDef == null)
			{
				yield return "CompProperties_FluidReservoir on " + parentDef.defName + " has no fluidDef set.";
			}
			if (dripVolume < 0f)
			{
				yield return "dripVolume must be >= 0.";
			}
			if (dripIntervalTicks < 1)
			{
				yield return "dripIntervalTicks must be >= 1.";
			}
			if (reFloodVolume < 0f)
			{
				yield return "reFloodVolume must be >= 0.";
			}
			if (reFloodIntervalTicks < 1)
			{
				yield return "reFloodIntervalTicks must be >= 1.";
			}
			// Both cadences are driven by CompTickRare -- the parent Thing must
			// actually tick at Rare (or faster, Normal) or the comp never fires
			// at all past the first canal-open, same class of check as vanilla's
			// own CompProperties_ProximityFuse/CompProperties_Rottable.
			if (parentDef.tickerType != TickerType.Rare && parentDef.tickerType != TickerType.Normal)
			{
				yield return "CompFluidReservoir needs tickerType " + TickerType.Rare + " or " +
					TickerType.Normal + ", " + parentDef.defName + " has " + parentDef.tickerType +
					" -- drip/re-flood cadence would never fire.";
			}
		}
	}
}
