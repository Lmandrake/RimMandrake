using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using Verse;
using Verse.Sound;

namespace VEF.Buildings;

public class SwappableBuilding : Building
{
	public int tickCounter;

	private SwappableBuildingDetails cachedExtension;

	public SwappableBuildingDetails SwappableExtension
	{
		get
		{
			if (cachedExtension == null)
			{
				cachedExtension = ((Def)((Thing)this).def).GetModExtension<SwappableBuildingDetails>();
			}
			return cachedExtension;
		}
	}

	public override void ExposeData()
	{
		((Building)this).ExposeData();
		Scribe_Values.Look<int>(ref tickCounter, "tickCounter", 0, false);
	}

	public override IEnumerable<Gizmo> GetGizmos()
	{
		foreach (Gizmo item in _003C_003En__0())
		{
			yield return item;
		}
		if (DebugSettings.ShowDevGizmos)
		{
			Command_Action val = new Command_Action();
			((Command)val).defaultLabel = "Activate";
			val.action = delegate
			{
				Notify_Swap();
			};
			yield return (Gizmo)(object)val;
		}
	}

	protected override void Tick()
	{
		((ThingWithComps)this).Tick();
		SwappableBuildingDetails swappableExtension = SwappableExtension;
		if (swappableExtension == null || swappableExtension.swappingTimer != -1)
		{
			if (tickCounter > SwappableExtension.swappingTimer)
			{
				Notify_Swap();
			}
			tickCounter++;
		}
	}

	public virtual void Notify_Swap()
	{
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		if (SwappableExtension == null)
		{
			return;
		}
		if (SwappableExtension.buildingLeft != null)
		{
			Thing val = GenSpawn.Spawn(ThingMaker.MakeThing(SwappableExtension.buildingLeft, (ThingDef)null), ((Thing)this).Position, ((Thing)this).Map, ((Thing)this).Rotation, (WipeMode)0, false, false);
			if (val.def.CanHaveFaction)
			{
				val.SetFaction(((Thing)this).Faction, (Pawn)null);
			}
		}
		if (SwappableExtension.deconstructSound != null)
		{
			SoundStarter.PlayOneShot(SwappableExtension.deconstructSound, SoundInfo.op_Implicit((Thing)(object)this));
		}
		if (((Thing)this).Spawned)
		{
			((Entity)this).DeSpawn((DestroyMode)0);
		}
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Gizmo> _003C_003En__0()
	{
		return ((Building)this).GetGizmos();
	}
}
