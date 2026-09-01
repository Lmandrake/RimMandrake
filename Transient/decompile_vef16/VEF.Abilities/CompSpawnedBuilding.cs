using Verse;

namespace VEF.Abilities;

public class CompSpawnedBuilding : ThingComp
{
	public int finalTick = -1;

	public int damagePerTick;

	public int lastDamageTick;

	public override void CompTickInterval(int delta)
	{
		((ThingComp)this).CompTickInterval(delta);
		TickCheck();
	}

	public override void CompTickRare()
	{
		((ThingComp)this).CompTickRare();
		TickCheck();
	}

	public override void CompTickLong()
	{
		((ThingComp)this).CompTickLong();
		TickCheck();
	}

	private void TickCheck()
	{
		int ticksGame = Find.TickManager.TicksGame;
		bool flag = false;
		if (damagePerTick > 0 && lastDamageTick < ticksGame)
		{
			ThingWithComps parent = base.parent;
			((Thing)parent).HitPoints = ((Thing)parent).HitPoints - damagePerTick * (ticksGame - lastDamageTick);
			lastDamageTick = ticksGame;
			if (((Thing)base.parent).HitPoints <= 0)
			{
				flag = true;
			}
		}
		if (finalTick > 0 && finalTick < ticksGame)
		{
			flag = true;
		}
		if (flag)
		{
			((Thing)base.parent).Destroy((DestroyMode)0);
		}
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<int>(ref finalTick, "finalTick", 0, false);
		Scribe_Values.Look<int>(ref damagePerTick, "damagePerTick", 0, false);
		Scribe_Values.Look<int>(ref lastDamageTick, "lastDamageTick", 0, false);
	}
}
