using System.Collections.Generic;
using System.Text;
using RimWorld;
using Verse;

namespace VEF.Buildings;

public class CompStatsWhenPowered : ThingComp
{
	protected CompPowerTrader powerTrader;

	public CompProperties_StatsWhenPowered Props => (CompProperties_StatsWhenPowered)(object)base.props;

	public virtual bool IsPowered
	{
		get
		{
			CompPowerTrader val = powerTrader;
			if (val != null)
			{
				return val.PowerOn;
			}
			return false;
		}
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		powerTrader = base.parent.GetComp<CompPowerTrader>();
	}

	public override void ReceiveCompSignal(string signal)
	{
		if ((!(signal == "PowerTurnedOn") && !(signal == "PowerTurnedOff")) || 1 == 0)
		{
			return;
		}
		List<StatDef> clearStatCacheOnPowerChange = Props.clearStatCacheOnPowerChange;
		if (clearStatCacheOnPowerChange != null)
		{
			for (int i = 0; i < clearStatCacheOnPowerChange.Count; i++)
			{
				clearStatCacheOnPowerChange[i].Worker.ClearCacheForThing((Thing)(object)base.parent);
			}
		}
		if (Props.clearRoomCacheOnPowerChange)
		{
			Room room = RegionAndRoomQuery.GetRoom((Thing)(object)base.parent, (RegionType)15);
			if (room != null)
			{
				room.Notify_BedTypeChanged();
			}
		}
	}

	public override float GetStatOffset(StatDef stat)
	{
		if (IsPowered)
		{
			return StatUtility.GetStatOffsetFromList(Props.poweredStatOffsets, stat);
		}
		return StatUtility.GetStatOffsetFromList(Props.unpoweredStatOffsets, stat);
	}

	public override float GetStatFactor(StatDef stat)
	{
		if (IsPowered)
		{
			return StatUtility.GetStatFactorFromList(Props.poweredStatFactors, stat);
		}
		return StatUtility.GetStatFactorFromList(Props.unpoweredStatFactors, stat);
	}

	public override void GetStatsExplanation(StatDef stat, StringBuilder sb, string whitespace = "")
	{
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0086: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00be: Unknown result type (might be due to invalid IL or missing references)
		(string, List<StatModifier>, List<StatModifier>) tuple = ((!IsPowered) ? ("VEF.StatsReport_Unpowered", Props.unpoweredStatOffsets, Props.unpoweredStatFactors) : ("VEF.StatsReport_Powered", Props.poweredStatOffsets, Props.poweredStatFactors));
		(string, List<StatModifier>, List<StatModifier>) tuple2 = tuple;
		string item = tuple2.Item1;
		List<StatModifier> item2 = tuple2.Item2;
		List<StatModifier> item3 = tuple2.Item3;
		float statOffsetFromList = StatUtility.GetStatOffsetFromList(item2, stat);
		if (statOffsetFromList != 0f)
		{
			sb.AppendLine($"{Translator.Translate(item)}: {GenText.ToStringByStyle(statOffsetFromList, stat.toStringStyle, (ToStringNumberSense)3)}");
		}
		float statFactorFromList = StatUtility.GetStatFactorFromList(item3, stat);
		if (statFactorFromList != 1f)
		{
			sb.AppendLine($"{Translator.Translate(item)}: {GenText.ToStringByStyle(statFactorFromList, stat.toStringStyle, (ToStringNumberSense)2)}");
		}
	}
}
