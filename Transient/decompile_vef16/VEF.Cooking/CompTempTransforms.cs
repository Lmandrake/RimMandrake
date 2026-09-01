using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Cooking;

public class CompTempTransforms : ThingComp
{
	protected float ruinedPercent;

	public const string RuinedSignal = "RuinedByTemperature";

	public CompProperties_TempTransforms Props => (CompProperties_TempTransforms)(object)base.props;

	public bool Ruined => ruinedPercent >= 1f;

	public override void PostExposeData()
	{
		Scribe_Values.Look<float>(ref ruinedPercent, "ruinedPercent", 0f, false);
	}

	public void Reset()
	{
		ruinedPercent = 0f;
	}

	public override void CompTickInterval(int delta)
	{
		DoTicks(delta);
	}

	public override void CompTickRare()
	{
		DoTicks(250);
	}

	public override void CompTickLong()
	{
		DoTicks(2000);
	}

	private void DoTicks(int ticks)
	{
		//IL_02f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_024a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0293: Unknown result type (might be due to invalid IL or missing references)
		//IL_0298: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_02ba: Unknown result type (might be due to invalid IL or missing references)
		if (!Ruined)
		{
			float ambientTemperature = ((Thing)base.parent).AmbientTemperature;
			if (ambientTemperature > Props.maxSafeTemperature)
			{
				ruinedPercent += (ambientTemperature - Props.maxSafeTemperature) * Props.progressPerDegreePerTick * (float)ticks;
			}
			else if (ambientTemperature < Props.minSafeTemperature)
			{
				ruinedPercent -= (ambientTemperature - Props.minSafeTemperature) * Props.progressPerDegreePerTick * (float)ticks;
			}
			if (ruinedPercent >= 1f)
			{
				ruinedPercent = 1f;
				base.parent.BroadcastCompSignal("RuinedByTemperature");
			}
			else if (ruinedPercent < 0f)
			{
				ruinedPercent = 0f;
			}
		}
		else
		{
			if (((Thing)base.parent).Map == null)
			{
				return;
			}
			Thing val = ThingMaker.MakeThing(ThingDef.Named(Props.thingToTransformInto), (ThingDef)null);
			val.stackCount = ((Thing)base.parent).stackCount;
			if (Props.preserveHp)
			{
				val.HitPoints = Mathf.Max(Mathf.CeilToInt((float)((Thing)base.parent).HitPoints / (float)((Thing)base.parent).MaxHitPoints * (float)val.MaxHitPoints), 1);
			}
			ThingWithComps val2 = (ThingWithComps)(object)((val is ThingWithComps) ? val : null);
			if (val2 != null)
			{
				List<ThingDef> list = base.parent.GetComp<CompIngredients>()?.ingredients;
				if (list != null && list.Count > 0)
				{
					ThingCompUtility.TryGetComp<CompIngredients>((Thing)(object)val2)?.ingredients?.AddRange(list);
				}
				if (Props.keepForbidden && val2.compForbiddable != null && base.parent.compForbiddable != null)
				{
					val2.compForbiddable.Forbidden = base.parent.compForbiddable.Forbidden;
				}
				if (Props.keepRottableProgress)
				{
					CompRottable comp = val2.GetComp<CompRottable>();
					if (comp != null)
					{
						CompRottable comp2 = base.parent.GetComp<CompRottable>();
						if (comp2 != null)
						{
							comp.RotProgress = comp2.RotProgressPct * (float)comp.PropsRot.TicksToRotStart;
						}
					}
				}
				if (Props.keepQuality)
				{
					if (val2.compQuality != null && base.parent.compQuality != null)
					{
						val2.compQuality.SetQuality(base.parent.compQuality.Quality, (ArtGenerationContext?)null);
					}
					CompArt comp3 = val2.GetComp<CompArt>();
					if (comp3 != null)
					{
						CompArt comp4 = base.parent.GetComp<CompArt>();
						if (comp4 != null)
						{
							NonPublicFields.CompArt_authorNameInt.Invoke(comp3) = NonPublicFields.CompArt_authorNameInt.Invoke(comp4);
							NonPublicFields.CompArt_titleInt.Invoke(comp3) = NonPublicFields.CompArt_titleInt.Invoke(comp4);
							NonPublicFields.CompArt_taleRef.Invoke(comp3) = NonPublicFields.CompArt_taleRef.Invoke(comp4);
						}
					}
				}
			}
			bool num = Find.Selector.IsSelected((object)base.parent);
			GenSpawn.Spawn(val, ((Thing)base.parent).Position, ((Thing)base.parent).Map, (WipeMode)0);
			((Thing)base.parent).Destroy((DestroyMode)0);
			if (num)
			{
				Find.Selector.Select((object)val, true, true);
			}
		}
	}

	public override void PreAbsorbStack(Thing otherStack, int count)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		float num = (float)count / (float)(((Thing)base.parent).stackCount + count);
		CompTempTransforms comp = ((ThingWithComps)otherStack).GetComp<CompTempTransforms>();
		ruinedPercent = Mathf.Lerp(ruinedPercent, comp.ruinedPercent, num);
	}

	public override bool AllowStackWith(Thing other)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		CompTempTransforms comp = ((ThingWithComps)other).GetComp<CompTempTransforms>();
		return Ruined == comp.Ruined;
	}

	public override void PostSplitOff(Thing piece)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		((ThingWithComps)piece).GetComp<CompTempTransforms>().ruinedPercent = ruinedPercent;
	}

	public override string CompInspectStringExtra()
	{
		//IL_000d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0044: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		if (Ruined)
		{
			return TaggedString.op_Implicit(Translator.Translate("RuinedByTemperature"));
		}
		if (ruinedPercent > 0f)
		{
			float ambientTemperature = ((Thing)base.parent).AmbientTemperature;
			string text;
			if (ambientTemperature > Props.maxSafeTemperature)
			{
				text = TaggedString.op_Implicit(Translator.Translate("Overheating"));
			}
			else
			{
				if (ambientTemperature >= Props.minSafeTemperature)
				{
					return null;
				}
				text = TaggedString.op_Implicit(Translator.Translate("Freezing"));
			}
			return text + ": " + GenText.ToStringPercent(ruinedPercent);
		}
		return null;
	}
}
