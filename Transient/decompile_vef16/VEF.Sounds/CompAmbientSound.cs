using System;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace VEF.Sounds;

public class CompAmbientSound : ThingComp
{
	protected Sustainer sustainerAmbient;

	protected bool isPawn;

	protected CompPowerTrader powerTrader;

	protected CompSchedule schedule;

	protected CompFlickable flickable;

	protected CompRefuelable refuelable;

	public CompProperties_AmbientSound Props => base.props as CompProperties_AmbientSound;

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
		isPawn = base.parent is Pawn;
		if (!isPawn)
		{
			powerTrader = base.parent.GetComp<CompPowerTrader>();
			schedule = base.parent.GetComp<CompSchedule>();
			flickable = base.parent.GetComp<CompFlickable>();
			refuelable = base.parent.GetComp<CompRefuelable>();
		}
		LongEventHandler.ExecuteWhenFinished((Action)StartSustainer);
	}

	public override void PostDeSpawn(Map map, DestroyMode mode = 0)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).PostDeSpawn(map, mode);
		EndSustainer();
	}

	public override void ReceiveCompSignal(string signal)
	{
		((ThingComp)this).ReceiveCompSignal(signal);
		if (signal == null)
		{
			return;
		}
		switch (signal.Length)
		{
		default:
			return;
		case 12:
			switch (signal[0])
			{
			default:
				return;
			case 'S':
				if (!(signal == "ScheduledOff"))
				{
					return;
				}
				break;
			case 'R':
				if (!(signal == "RanOutOfFuel"))
				{
					return;
				}
				break;
			}
			goto IL_00bc;
		case 14:
			if (!(signal == "PowerTurnedOff"))
			{
				return;
			}
			goto IL_00bc;
		case 10:
			if (!(signal == "FlickedOff"))
			{
				return;
			}
			goto IL_00bc;
		case 13:
			if (!(signal == "PowerTurnedOn"))
			{
				return;
			}
			break;
		case 11:
			if (!(signal == "ScheduledOn"))
			{
				return;
			}
			break;
		case 9:
			if (!(signal == "FlickedOn"))
			{
				return;
			}
			break;
		case 8:
			{
				if (!(signal == "Refueled"))
				{
					return;
				}
				break;
			}
			IL_00bc:
			EndSustainer();
			return;
		}
		StartSustainer();
	}

	protected void StartSustainer()
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Expected O, but got Unknown
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Expected O, but got Unknown
		if (!CanStartSustainer())
		{
			return;
		}
		SoundInfo val = SoundInfo.InMap(TargetInfo.op_Implicit((Thing)(object)base.parent), (MaintenanceType)0);
		ThingWithComps parent = base.parent;
		Pawn val2 = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (val2 != null)
		{
			Pawn val3 = val2;
			if (val3.pather == null)
			{
				val3.pather = new Pawn_PathFollower(val2);
			}
			val3 = val2;
			if (val3.stances == null)
			{
				val3.stances = new Pawn_StanceTracker(val2);
			}
		}
		sustainerAmbient = SoundStarter.TrySpawnSustainer(Props.ambientSound, val);
	}

	protected void EndSustainer()
	{
		if (sustainerAmbient != null)
		{
			sustainerAmbient.End();
			sustainerAmbient = null;
		}
	}

	protected virtual bool CanStartSustainer()
	{
		Sustainer val = sustainerAmbient;
		if (val != null && !val.Ended)
		{
			return false;
		}
		if (isPawn)
		{
			StartSustainer();
			return true;
		}
		CompPowerTrader val2 = powerTrader;
		if (val2 != null && !val2.PowerOn)
		{
			return false;
		}
		CompSchedule val3 = schedule;
		if (val3 != null && !val3.Allowed)
		{
			return false;
		}
		CompFlickable val4 = flickable;
		if (val4 != null && !val4.SwitchIsOn)
		{
			return false;
		}
		CompRefuelable val5 = refuelable;
		if (val5 != null && !val5.HasFuel)
		{
			return false;
		}
		return true;
	}
}
