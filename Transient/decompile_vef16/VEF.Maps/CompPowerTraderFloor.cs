using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Maps;

public class CompPowerTraderFloor : CompPowerTrader
{
	public List<TerrainComp_PowerTrader> acceptedComps = new List<TerrainComp_PowerTrader>();

	private float cachedCurPowerDemand;

	public float CurPowerDemand
	{
		get
		{
			float num = 0f;
			foreach (TerrainComp_PowerTrader acceptedComp in acceptedComps)
			{
				num += acceptedComp.PowerOutput;
			}
			return cachedCurPowerDemand = num;
		}
	}

	public override void SetUpPowerVars()
	{
		((CompPowerTrader)this).SetUpPowerVars();
		UpdatePowerOutput();
	}

	public virtual void ReceiveTerrainComp(TerrainComp_PowerTrader comp)
	{
		acceptedComps.Add(comp);
		UpdatePowerOutput();
	}

	public virtual void Notify_TerrainCompRemoved(TerrainComp_PowerTrader comp)
	{
		acceptedComps.Remove(comp);
		UpdatePowerOutput();
	}

	public void UpdatePowerOutput()
	{
		float curPowerDemand = CurPowerDemand;
		float powerOutput = 0f - ((CompPower)this).Props.PowerConsumption + curPowerDemand;
		((CompPowerTrader)this).PowerOutput = powerOutput;
	}

	public override string CompInspectStringExtra()
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit(((CompPowerTrader)this).CompInspectStringExtra() + TranslatorFormattedStringExtensions.Translate("FloorWire_InspectStringPart", NamedArgument.op_Implicit(acceptedComps.Count), NamedArgument.op_Implicit(0f - cachedCurPowerDemand)));
	}
}
