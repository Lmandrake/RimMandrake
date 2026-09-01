using System;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Hediffs;

public class HediffComp_Targeting : HediffComp
{
	public Mote mote;

	private Material targetingLine;

	public Action actionOnTick;

	public HediffCompProperties_Targeting Props => base.props as HediffCompProperties_Targeting;

	public Material TargetingLine
	{
		get
		{
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			if ((Object)(object)targetingLine == (Object)null)
			{
				targetingLine = MaterialPool.MatFrom(Props.targetingLineTexPath, ShaderDatabase.Transparent, Props.targetingLineColor);
			}
			return targetingLine;
		}
	}

	public void DrawTargetingEffects(LocalTargetInfo target, float progress)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
		if (Props.targetingMote != null)
		{
			if (mote == null || ((Thing)mote).Destroyed)
			{
				actionOnTick = delegate
				{
					//IL_005f: Unknown result type (might be due to invalid IL or missing references)
					//IL_002e: Unknown result type (might be due to invalid IL or missing references)
					if (((LocalTargetInfo)(ref target)).HasThing)
					{
						mote = MoteMaker.MakeAttachedOverlay(((LocalTargetInfo)(ref target)).Thing, Props.targetingMote, Vector3.zero, Props.initialTargetingMoteScale, -1f);
					}
					else
					{
						mote = MakeStaticMote(((LocalTargetInfo)(ref target)).CenterVector3, ((Thing)((HediffComp)this).Pawn).Map, Props.targetingMote, Props.initialTargetingMoteScale);
					}
				};
			}
			else
			{
				if (Props.sizeScalesWithProgress)
				{
					mote.Scale = progress;
				}
				mote.Maintain();
				if (mote is MoteAttached_TargetingLockDynamic moteAttached_TargetingLockDynamic)
				{
					moteAttached_TargetingLockDynamic.DrawTargetingLock(progress);
				}
			}
		}
		if (!GenText.NullOrEmpty(Props.targetingLineTexPath))
		{
			Vector3 val;
			if (((LocalTargetInfo)(ref target)).HasThing)
			{
				val = GenThing.TrueCenter(((LocalTargetInfo)(ref target)).Thing);
			}
			else
			{
				IntVec3 cell = ((LocalTargetInfo)(ref target)).Cell;
				val = ((IntVec3)(ref cell)).ToVector3Shifted();
			}
			Vector3 val2 = val;
			Vector3 val3 = GenThing.TrueCenter((Thing)(object)((HediffComp)this).Pawn);
			val2.y = Altitudes.AltitudeFor((AltitudeLayer)39);
			val3.y = val2.y;
			GenDraw.DrawLineBetween(val3, val2, TargetingLine, Props.targetingLineWidth);
		}
	}

	public override void CompPostTick(ref float severityAdjustment)
	{
		((HediffComp)this).CompPostTick(ref severityAdjustment);
		if (actionOnTick != null)
		{
			actionOnTick();
			actionOnTick = null;
		}
	}

	public static Mote MakeStaticMote(Vector3 loc, Map map, ThingDef moteDef, float scale = 1f)
	{
		//IL_0007: Unknown result type (might be due to invalid IL or missing references)
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Expected O, but got Unknown
		//IL_002a: Expected O, but got Unknown
		Mote val = (Mote)ThingMaker.MakeThing(moteDef, (ThingDef)null);
		val.exactPosition = loc;
		val.Scale = scale;
		GenSpawn.Spawn((Thing)val, IntVec3Utility.ToIntVec3(loc), map, (WipeMode)0);
		return val;
	}

	public override void CompExposeData()
	{
		((HediffComp)this).CompExposeData();
		Scribe_References.Look<Mote>(ref mote, "mote", false);
	}
}
