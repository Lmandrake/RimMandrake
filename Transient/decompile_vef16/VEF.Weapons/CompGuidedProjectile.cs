using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Verse;
using Verse.AI;

namespace VEF.Weapons;

public class CompGuidedProjectile : ThingComp
{
	private GuidedProjectiles guidedProjectilesComp;

	public CompProperties_GuidedProjectile Props => (CompProperties_GuidedProjectile)(object)base.props;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
		guidedProjectilesComp = ((Thing)base.parent).Map.GetComponent<GuidedProjectiles>();
	}

	public override void CompTick()
	{
		//IL_028e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0293: Unknown result type (might be due to invalid IL or missing references)
		//IL_029e: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_024b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0173: Unknown result type (might be due to invalid IL or missing references)
		//IL_0178: Unknown result type (might be due to invalid IL or missing references)
		//IL_022e: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f3: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0209: Unknown result type (might be due to invalid IL or missing references)
		//IL_0210: Expected O, but got Unknown
		//IL_0217: Unknown result type (might be due to invalid IL or missing references)
		//IL_021c: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTick();
		ThingWithComps parent = base.parent;
		Projectile val = (Projectile)(object)((parent is Projectile) ? parent : null);
		if (Props.selectDifferentTargets)
		{
			if (guidedProjectilesComp.launcherTargets == null)
			{
				guidedProjectilesComp.launcherTargets = new Dictionary<Thing, Targets>();
			}
			if (guidedProjectilesComp.launcherTargets.TryGetValue(val.Launcher, out var targets))
			{
				Thing launcher = val.Launcher;
				Pawn val2 = (Pawn)(object)((launcher is Pawn) ? launcher : null);
				if (val2 != null)
				{
					if (targets.targetInfos == null)
					{
						targets.targetInfos = new Dictionary<Projectile, LocalTargetInfo>();
					}
					if (!targets.targetInfos.ContainsKey(val))
					{
						bool flag = false;
						List<Projectile> list = new List<Projectile>();
						foreach (KeyValuePair<Projectile, LocalTargetInfo> targetInfo in targets.targetInfos)
						{
							if (!((Thing)targetInfo.Key).Spawned || ((Thing)targetInfo.Key).Destroyed)
							{
								list.Add(targetInfo.Key);
							}
						}
						foreach (Projectile item in list)
						{
							targets.targetInfos.Remove(item);
						}
						foreach (KeyValuePair<Projectile, LocalTargetInfo> targetInfo2 in targets.targetInfos)
						{
							LocalTargetInfo value = targetInfo2.Value;
							if (((LocalTargetInfo)(ref value)).Thing == ((LocalTargetInfo)(ref val.intendedTarget)).Thing)
							{
								flag = true;
								break;
							}
						}
						if (flag)
						{
							float num = 8f;
							num = Mathf.Clamp(val2.CurrentEffectiveVerb.verbProps.range * 0.66f, 2f, 20f);
							Thing val3 = (Thing)AttackTargetFinder.BestAttackTarget((IAttackTargetSearcher)(object)val2, (TargetScanFlags)3, (Predicate<Thing>)((Thing x) => !targets.targetInfos.Where(delegate(KeyValuePair<Projectile, LocalTargetInfo> y)
							{
								//IL_0002: Unknown result type (might be due to invalid IL or missing references)
								//IL_0007: Unknown result type (might be due to invalid IL or missing references)
								LocalTargetInfo value2 = y.Value;
								return ((LocalTargetInfo)(ref value2)).Thing == x;
							}).Any()), 0f, num, default(IntVec3), float.MaxValue, false, true, false, false);
							if (val3 != null)
							{
								val.intendedTarget = LocalTargetInfo.op_Implicit(val3);
							}
						}
						targets.targetInfos[val] = val.intendedTarget;
					}
					goto IL_0272;
				}
			}
			Targets targets2 = new Targets();
			targets2.targetInfos = new Dictionary<Projectile, LocalTargetInfo> { { val, val.intendedTarget } };
			guidedProjectilesComp.launcherTargets[val.Launcher] = targets2;
		}
		goto IL_0272;
		IL_0272:
		if (((LocalTargetInfo)(ref val.intendedTarget)).IsValid)
		{
			ref Vector3 reference = ref NonPublicFields.Projectile_destination.Invoke(val);
			if (new IntVec3(reference) != ((LocalTargetInfo)(ref val.intendedTarget)).Cell)
			{
				reference = ((LocalTargetInfo)(ref val.intendedTarget)).CenterVector3;
			}
		}
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
	}
}
