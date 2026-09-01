using System.Text;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.Cooking;

public class CompMaturingAlcohol : ThingComp
{
	private float rotProgressInt;

	public CompProperties_MaturingAlcohol PropsRot => (CompProperties_MaturingAlcohol)(object)base.props;

	public float RotProgressPct => RotProgress / (float)PropsRot.TicksToRotStart;

	public float RotProgress
	{
		get
		{
			return rotProgressInt;
		}
		set
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			RotStage stage = Stage;
			rotProgressInt = value;
			if (stage != Stage)
			{
				StageChanged();
			}
		}
	}

	public RotStage Stage
	{
		get
		{
			if (!(RotProgress < (float)PropsRot.TicksToRotStart))
			{
				if (!(RotProgress < (float)PropsRot.TicksToDessicated))
				{
					return (RotStage)2;
				}
				return (RotStage)1;
			}
			return (RotStage)0;
		}
	}

	public int TicksUntilRotAtCurrentTemp
	{
		get
		{
			float ambientTemperature = ((Thing)base.parent).AmbientTemperature;
			ambientTemperature = Mathf.RoundToInt(ambientTemperature);
			return TicksUntilRotAtTemp(ambientTemperature);
		}
	}

	public bool Active
	{
		get
		{
			if (PropsRot.disableIfHatcher)
			{
				CompHatcher val = ThingCompUtility.TryGetComp<CompHatcher>((Thing)(object)base.parent);
				if (val != null && !val.TemperatureDamaged)
				{
					return false;
				}
			}
			return true;
		}
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<float>(ref rotProgressInt, "rotProg", 0f, false);
	}

	public override void CompTickInterval(int delta)
	{
		Tick(delta);
	}

	public override void CompTickRare()
	{
		Tick(250);
	}

	public override void CompTickLong()
	{
		Tick(2000);
	}

	private void Tick(int interval)
	{
		//IL_0033: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Invalid comparison between Unknown and I4
		//IL_00db: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e1: Invalid comparison between Unknown and I4
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_0132: Unknown result type (might be due to invalid IL or missing references)
		//IL_0138: Invalid comparison between Unknown and I4
		//IL_0125: Unknown result type (might be due to invalid IL or missing references)
		//IL_017c: Unknown result type (might be due to invalid IL or missing references)
		if (!Active)
		{
			return;
		}
		float rotProgress = RotProgress;
		float num = GenTemperature.RotRateAtTemperature(((Thing)base.parent).AmbientTemperature);
		RotProgress += num * (float)interval;
		if ((int)Stage == 1 && PropsRot.rotDestroys)
		{
			if (((Thing)base.parent).Map != null)
			{
				int stackCount = ((Thing)base.parent).stackCount;
				GenSpawn.Spawn(ThingDef.Named(PropsRot.thingToTransformTo), ((Thing)base.parent).Position, ((Thing)base.parent).Map, (WipeMode)0).stackCount = stackCount;
				((Thing)base.parent).Destroy((DestroyMode)0);
			}
			else
			{
				((Thing)base.parent).Destroy((DestroyMode)0);
			}
		}
		else if (Mathf.FloorToInt(rotProgress / 60000f) != Mathf.FloorToInt(RotProgress / 60000f) && ShouldTakeRotDamage())
		{
			if ((int)Stage == 1 && PropsRot.rotDamagePerDay > 0f)
			{
				((Thing)base.parent).TakeDamage(new DamageInfo(DamageDefOf.Rotting, (float)GenMath.RoundRandom(PropsRot.rotDamagePerDay), 0f, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false));
			}
			else if ((int)Stage == 2 && PropsRot.dessicatedDamagePerDay > 0f)
			{
				((Thing)base.parent).TakeDamage(new DamageInfo(DamageDefOf.Rotting, (float)GenMath.RoundRandom(PropsRot.dessicatedDamagePerDay), 0f, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false));
			}
		}
	}

	private bool ShouldTakeRotDamage()
	{
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Invalid comparison between Unknown and I4
		IThingHolder parentHolder = ((Thing)base.parent).ParentHolder;
		Thing val = (Thing)(object)((parentHolder is Thing) ? parentHolder : null);
		if (val != null && (int)val.def.category == 3)
		{
			return !val.def.building.preventDeteriorationInside;
		}
		return true;
	}

	public override void PreAbsorbStack(Thing otherStack, int count)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		float num = (float)count / (float)(((Thing)base.parent).stackCount + count);
		float rotProgress = ((ThingWithComps)otherStack).GetComp<CompMaturingAlcohol>().RotProgress;
		RotProgress = Mathf.Lerp(RotProgress, rotProgress, num);
	}

	public override void PostSplitOff(Thing piece)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		((ThingWithComps)piece).GetComp<CompMaturingAlcohol>().RotProgress = RotProgress;
	}

	public override void PostIngested(Pawn ingester)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		if ((int)Stage != 0 && FoodUtility.GetFoodPoisonChanceFactor(ingester) > float.Epsilon)
		{
			FoodUtility.AddFoodPoisoningHediff(ingester, (Thing)(object)base.parent, (FoodPoisonCause)3);
		}
	}

	public override string CompInspectStringExtra()
	{
		//IL_0011: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Invalid comparison between Unknown and I4
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0108: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0117: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00df: Unknown result type (might be due to invalid IL or missing references)
		if (!Active)
		{
			return null;
		}
		StringBuilder stringBuilder = new StringBuilder();
		if ((int)Stage == 0)
		{
			stringBuilder.Append(TaggedString.op_Implicit(Translator.Translate(PropsRot.maturingString) + "."));
		}
		if ((float)PropsRot.TicksToRotStart - RotProgress > 0f)
		{
			float num = GenTemperature.RotRateAtTemperature((float)Mathf.RoundToInt(((Thing)base.parent).AmbientTemperature));
			int ticksUntilRotAtCurrentTemp = TicksUntilRotAtCurrentTemp;
			stringBuilder.AppendLine();
			if (num < 0.001f)
			{
				stringBuilder.Append(TaggedString.op_Implicit(Translator.Translate(PropsRot.maturingStopped) + "."));
			}
			else if (num < 0.999f)
			{
				stringBuilder.Append(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(PropsRot.maturingSlowly, NamedArgument.op_Implicit(GenDate.ToStringTicksToPeriod(ticksUntilRotAtCurrentTemp, true, false, true, true, false))) + "."));
			}
			else
			{
				stringBuilder.Append(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(PropsRot.maturingProperly, NamedArgument.op_Implicit(GenDate.ToStringTicksToPeriod(ticksUntilRotAtCurrentTemp, true, false, true, true, false))) + "."));
			}
		}
		return stringBuilder.ToString();
	}

	public int ApproxTicksUntilRotWhenAtTempOfTile(PlanetTile tile, int ticksAbs)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		float temperatureFromSeasonAtTile = GenTemperature.GetTemperatureFromSeasonAtTile(ticksAbs, tile);
		return TicksUntilRotAtTemp(temperatureFromSeasonAtTile);
	}

	public int TicksUntilRotAtTemp(float temp)
	{
		if (!Active)
		{
			return 72000000;
		}
		float num = GenTemperature.RotRateAtTemperature(temp);
		if (num <= 0f)
		{
			return 72000000;
		}
		float num2 = (float)PropsRot.TicksToRotStart - RotProgress;
		if (num2 <= 0f)
		{
			return 0;
		}
		return Mathf.RoundToInt(num2 / num);
	}

	private void StageChanged()
	{
		ThingWithComps parent = base.parent;
		Corpse val = (Corpse)(object)((parent is Corpse) ? parent : null);
		if (val != null)
		{
			val.RotStageChanged();
		}
	}

	public void RotImmediately()
	{
		if (RotProgress < (float)PropsRot.TicksToRotStart)
		{
			RotProgress = PropsRot.TicksToRotStart;
		}
	}
}
