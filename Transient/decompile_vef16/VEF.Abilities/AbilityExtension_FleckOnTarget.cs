using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace VEF.Abilities;

public class AbilityExtension_FleckOnTarget : AbilityExtension_AbilityMod
{
	public bool allTargets;

	public FleckDef fleckDef;

	public List<FleckDef> fleckDefs;

	public int preCastTicks = -1;

	public float scale = 1f;

	public SoundDef sound;

	public bool tryCenter;

	public override IEnumerable<string> ConfigErrors()
	{
		if (allTargets && tryCenter)
		{
			yield return "AbilityExtension_FleckOnTarget: cannot set both allTargets and tryCenter";
		}
	}

	public override void Cast(GlobalTargetInfo[] targets, Ability ability)
	{
		base.Cast(targets, ability);
		if (preCastTicks <= 0)
		{
			SpawnAll(targets, ability);
		}
	}

	public override void WarmupToil(Toil toil)
	{
		base.WarmupToil(toil);
		if (preCastTicks <= 0)
		{
			return;
		}
		toil.AddPreTickAction((Action)delegate
		{
			if (toil.actor.jobs.curDriver.ticksLeftThisToil == preCastTicks)
			{
				CompAbilities comp = ((ThingWithComps)toil.actor).GetComp<CompAbilities>();
				SpawnAll(comp.currentlyCastingTargets, comp.currentlyCasting);
			}
		});
	}

	private void SpawnAll(GlobalTargetInfo[] targets, Ability ability)
	{
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		if (allTargets)
		{
			for (int i = 0; i < targets.Length; i++)
			{
				SpawnOn(targets[i]);
			}
		}
		else if (tryCenter)
		{
			SpawnOn(((LocalTargetInfo)(ref ability.firstTarget)).ToGlobalTargetInfo(((GlobalTargetInfo)(ref targets[0])).Map));
		}
		else
		{
			SpawnOn(targets[0]);
		}
	}

	private void SpawnOn(GlobalTargetInfo target)
	{
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0061: Unknown result type (might be due to invalid IL or missing references)
		//IL_006e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Unknown result type (might be due to invalid IL or missing references)
		if (!GenList.NullOrEmpty<FleckDef>((IList<FleckDef>)fleckDefs))
		{
			for (int i = 0; i < fleckDefs.Count; i++)
			{
				SpawnFleck(target, fleckDefs[i]);
			}
		}
		if (fleckDef != null)
		{
			SpawnFleck(target, fleckDef);
		}
		SoundDef obj = sound;
		if (obj != null)
		{
			SoundStarter.PlayOneShot(obj, SoundInfo.op_Implicit((TargetInfo)(((GlobalTargetInfo)(ref target)).HasThing ? TargetInfo.op_Implicit(((GlobalTargetInfo)(ref target)).Thing) : new TargetInfo(((GlobalTargetInfo)(ref target)).Cell, ((GlobalTargetInfo)(ref target)).Map, false))));
		}
	}

	private void SpawnFleck(GlobalTargetInfo target, FleckDef def)
	{
		//IL_0029: Unknown result type (might be due to invalid IL or missing references)
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		if (((GlobalTargetInfo)(ref target)).HasThing)
		{
			FleckMaker.AttachedOverlay(((GlobalTargetInfo)(ref target)).Thing, def, Vector3.zero, scale, -1f);
		}
		else
		{
			FleckMaker.Static(((GlobalTargetInfo)(ref target)).Cell, ((GlobalTargetInfo)(ref target)).Map, def, scale);
		}
	}
}
