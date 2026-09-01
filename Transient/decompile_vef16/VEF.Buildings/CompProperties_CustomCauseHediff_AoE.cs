using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using Verse;

namespace VEF.Buildings;

public class CompProperties_CustomCauseHediff_AoE : CompProperties
{
	public List<PawnCapacityDef> requiredCapacities;

	public HediffDef hediff;

	public bool mustBeAwake;

	public bool sameRoomOnly = true;

	public float range;

	public bool allowHumanlike = true;

	public bool allowInsects;

	public bool allowDryads;

	public bool allowAnimals;

	public bool allowMechanoids;

	public bool allowEntities;

	public bool worksInside = true;

	public bool worksOutside = true;

	public float startingSeverity = 1f;

	public int checkInterval = 100;

	public int hediffDuration = 120;

	protected virtual bool LogWorksBothInsideAndOutsideFieldAreFalse => true;

	public CompProperties_CustomCauseHediff_AoE()
	{
		base.compClass = typeof(CompCustomCauseHediff_AoE);
	}

	public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
	{
		foreach (string item in _003C_003En__0(parentDef))
		{
			yield return item;
		}
		if (LogWorksBothInsideAndOutsideFieldAreFalse && !worksInside && !worksOutside)
		{
			yield return ((Def)parentDef).defName + " has CompCustomCauseHediff_AoE with both worksInside and worksOutside set to false. The comp won't do anything at all.";
		}
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<string> _003C_003En__0(ThingDef parentDef)
	{
		return ((CompProperties)this).ConfigErrors(parentDef);
	}
}
