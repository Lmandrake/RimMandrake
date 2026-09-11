using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Greentide
{
	/// <summary>
	/// GREENTIDE_STANDALONE_MOD_1 (M8). Digs out whatever RM_MapComponent_MudSwallow
	/// buried at a designated cell. Reuses vanilla JobDriver_AffectFloor (same
	/// engine as FluidCanals' JobDriver_DigCanal) for reservation, work-speed
	/// ticking and the progress bar; only DoEffect and the work amount differ.
	/// </summary>
	public class RM_JobDriver_DigOutBuried : JobDriver_AffectFloor
	{
		// INVENTED: 300 base + 1 tick of work per 10 buried ticks, capped —
		// "work scaled to time buried" (spec M8) without letting an old cache
		// become a multi-day dig.
		protected override int BaseWorkAmount
		{
			get
			{
				RM_MapComponent_MudSwallow comp = Map.GetComponent<RM_MapComponent_MudSwallow>();
				int age = comp?.BuriedDurationAt(job.targetA.Cell) ?? 0;
				return Mathf.Clamp(300 + age / 10, 300, 6000);
			}
		}

		protected override DesignationDef DesDef => RM_DefOf.RM_DesignationDigOutBuried;

		protected override StatDef SpeedStat => StatDefOf.MiningSpeed;

		protected override void DoEffect(IntVec3 c)
		{
			Map.GetComponent<RM_MapComponent_MudSwallow>()?.DigOut(c);
		}
	}
}
