using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Greentide
{
	/// <summary>
	/// GREENTIDE_STANDALONE_MOD_1 (M8). Digs out whatever RM_MapComponent_MudSwallow
	/// buried at a designated cell. Reuses vanilla JobDriver_AffectFloor (same
	/// engine as FlowWorks' JobDriver_DigCanal) for reservation, work-speed
	/// ticking and the progress bar; only DoEffect and the work amount differ.
	/// </summary>
	public class RM_JobDriver_DigOutBuried : JobDriver_AffectFloor
	{
		// Cached the first time it's read, not recomputed live. Unlike
		// FlowWorks' JobDriver_DigCanal (whose BaseWorkAmount depends only on
		// terrain depth that DoEffect alone changes, so it never moves mid-
		// toil), this amount is derived from elapsed buried-ticks, which keep
		// climbing every tick the pawn works. JobDriver_AffectFloor.MakeNewToils
		// reads BaseWorkAmount TWICE — once to seed workLeft, and again on
		// every progress-bar frame via `1f - workLeft / BaseWorkAmount` — so an
		// uncached getter would inflate its own denominator as the dig
		// progresses, desyncing the displayed progress from the frozen
		// workLeft the job actually completes against. -1 means "not yet
		// computed" since a real amount is always >= 300.
		private int cachedWorkAmount = -1;

		// INVENTED: 300 base + 1 tick of work per 10 buried ticks, capped —
		// "work scaled to time buried" (spec M8) without letting an old cache
		// become a multi-day dig.
		protected override int BaseWorkAmount
		{
			get
			{
				if (cachedWorkAmount < 0)
				{
					RM_MapComponent_MudSwallow comp = Map.GetComponent<RM_MapComponent_MudSwallow>();
					int age = comp?.BuriedDurationAt(job.targetA.Cell) ?? 0;
					cachedWorkAmount = Mathf.Clamp(300 + age / 10, 300, 6000);
				}
				return cachedWorkAmount;
			}
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref cachedWorkAmount, "cachedWorkAmount", -1);
		}

		protected override DesignationDef DesDef => RM_DefOf.RM_DesignationDigOutBuried;

		protected override StatDef SpeedStat => StatDefOf.MiningSpeed;

		protected override void DoEffect(IntVec3 c)
		{
			Map.GetComponent<RM_MapComponent_MudSwallow>()?.DigOut(c);
		}
	}
}
