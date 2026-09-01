using RimWorld;
using Verse;

namespace VEF.Maps;

public class TerrainComp_PowerTrader : TerrainComp
{
	public readonly int tickInterval = 50;

	private float powerOutputInt;

	private CompPowerTraderFloor connectParentInt;

	private bool curSignal;

	public CompPowerTraderFloor ConnectParent
	{
		get
		{
			return connectParentInt;
		}
		set
		{
			connectParentInt?.Notify_TerrainCompRemoved(this);
			connectParentInt = value;
			value?.ReceiveTerrainComp(this);
		}
	}

	public TerrainCompProperties_PowerTrader Props => (TerrainCompProperties_PowerTrader)props;

	public bool PowerOn
	{
		get
		{
			if (ConnectParent != null)
			{
				return ((CompPowerTrader)ConnectParent).PowerOn;
			}
			return false;
		}
	}

	public virtual float PowerOutput
	{
		get
		{
			return powerOutputInt;
		}
		set
		{
			powerOutputInt = value;
			ConnectParent?.UpdatePowerOutput();
		}
	}

	public override void CompUpdate()
	{
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		if (!PowerOn && !Props.ignoreNeedsPower)
		{
			ActiveTerrainUtility.RenderPulsingNeedsPowerOverlay(parent.Position);
		}
	}

	public override void CompTick()
	{
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		if (PowerOn != curSignal)
		{
			parent.BroadcastCompSignal(PowerOn ? CompSignals.PowerTurnedOn : CompSignals.PowerTurnedOff);
			curSignal = PowerOn;
		}
		if (!PowerOn && Find.TickManager.TicksGame % tickInterval == this.HashCodeToMod(tickInterval))
		{
			CompPowerTraderFloor compPowerTraderFloor = ActiveTerrainUtility.TryFindNearestPowerConduitFloor(parent.Position, parent.Map);
			if (compPowerTraderFloor != null)
			{
				ConnectParent = compPowerTraderFloor;
			}
		}
	}

	public override void Initialize(TerrainCompProperties props)
	{
		base.Initialize(props);
		powerOutputInt = 0f - Props.basePowerConsumption;
	}

	public override void PostRemove()
	{
		ConnectParent = null;
	}

	public override void PostExposeData()
	{
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Invalid comparison between Unknown and I4
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		base.PostExposeData();
		Scribe_Values.Look<bool>(ref curSignal, "curCompSignal", false, false);
		Thing val = null;
		if ((int)Scribe.mode == 1 && ConnectParent != null)
		{
			val = (Thing)(object)((ThingComp)ConnectParent).parent;
		}
		Scribe_References.Look<Thing>(ref val, "parentThing", false);
		if (val != null)
		{
			ConnectParent = ((ThingWithComps)val).GetComp<CompPowerTraderFloor>();
		}
	}
}
