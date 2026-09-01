using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Maps;

public class TerrainComp_TempControl : TerrainComp_HeatPush
{
	public bool operatingAtHighPower;

	[Unsaved(false)]
	private CompTempControl parentTempControl;

	public new TerrainCompProperties_TempControl Props => (TerrainCompProperties_TempControl)props;

	public float AmbientTemperature => GenTemperature.GetTemperatureForCell(parent.Position, parent.Map);

	public float PowerConsumptionNow
	{
		get
		{
			float basePowerConsumption = parent.def.GetCompProperties<TerrainCompProperties_PowerTrader>().basePowerConsumption;
			if (!operatingAtHighPower)
			{
				return basePowerConsumption * Props.lowPowerConsumptionFactor;
			}
			return basePowerConsumption;
		}
	}

	public virtual CompTempControl HeaterToConformTo
	{
		get
		{
			//IL_002e: Unknown result type (might be due to invalid IL or missing references)
			if (parentTempControl != null && ((Thing)((ThingComp)parentTempControl).parent).Spawned)
			{
				parentTempControl = null;
				return parentTempControl;
			}
			Room room = GridsUtility.GetRoom(parent.Position, parent.Map);
			if (room == null)
			{
				return null;
			}
			return parentTempControl = room.GetTempControl(this.AnalyzeType());
		}
	}

	public float TargetTemperature
	{
		get
		{
			CompTempControl heaterToConformTo = HeaterToConformTo;
			if (heaterToConformTo == null)
			{
				return 21f;
			}
			return heaterToConformTo.TargetTemperature;
		}
	}

	protected override float PushAmount
	{
		get
		{
			//IL_0079: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
			if (Props.reliesOnPower)
			{
				TerrainComp_PowerTrader comp = parent.GetComp<TerrainComp_PowerTrader>();
				if (comp != null && !comp.PowerOn)
				{
					operatingAtHighPower = false;
					return 0f;
				}
			}
			float ambientTemperature = AmbientTemperature;
			float num = ((ambientTemperature < 20f) ? 1f : ((ambientTemperature > 120f) ? 0f : Mathf.InverseLerp(120f, 20f, ambientTemperature)));
			float num2 = Props.energyPerSecond * num * 4.1666665f;
			float num3 = GenTemperature.ControlTemperatureTempChange(parent.Position, parent.Map, num2, TargetTemperature);
			bool flag = !Mathf.Approximately(num3, 0f) && GridsUtility.GetRoom(parent.Position, parent.Map) != null;
			TerrainComp_PowerTrader comp2 = parent.GetComp<TerrainComp_PowerTrader>();
			if (flag)
			{
				GenTemperature.PushHeat(parent.Position, parent.Map, num3);
			}
			if (comp2 != null)
			{
				comp2.PowerOutput = (flag ? (0f - comp2.Props.basePowerConsumption) : ((0f - comp2.Props.basePowerConsumption) * Props.lowPowerConsumptionFactor));
			}
			operatingAtHighPower = flag;
			if (!flag)
			{
				return 0f;
			}
			return num3;
		}
	}

	public override void CompTick()
	{
		base.CompTick();
		if (Props.cleansSnow && Find.TickManager.TicksGame % 60 == this.HashCodeToMod(60))
		{
			CleanSnow();
			UpdatePowerConsumption();
		}
	}

	public virtual void CleanSnow()
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		float depth = parent.Map.snowGrid.GetDepth(parent.Position);
		if (!Mathf.Approximately(0f, depth))
		{
			operatingAtHighPower = true;
			float num = Mathf.Max(depth - Props.snowMeltAmountPerSecond, 0f);
			parent.Map.snowGrid.SetDepth(parent.Position, num);
		}
	}

	public void UpdatePowerConsumption()
	{
		TerrainComp_PowerTrader comp = parent.GetComp<TerrainComp_PowerTrader>();
		if (comp != null)
		{
			comp.PowerOutput = 0f - PowerConsumptionNow;
		}
	}

	public override string TransformLabel(string label)
	{
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit(base.TransformLabel(label) + " " + (operatingAtHighPower ? Translator.Translate("HeatedFloor_HighPower") : Translator.Translate("HeatedFloor_LowPower")));
	}
}
