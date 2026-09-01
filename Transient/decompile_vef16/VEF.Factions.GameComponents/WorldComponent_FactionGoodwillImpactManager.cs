using System;
using System.Collections.Generic;
using RimWorld.Planet;
using Verse;

namespace VEF.Factions.GameComponents;

public class WorldComponent_FactionGoodwillImpactManager : WorldComponent
{
	protected List<GoodwillImpactDelayed> goodwillImpacts = new List<GoodwillImpactDelayed>();

	public WorldComponent_FactionGoodwillImpactManager(World world)
		: base(world)
	{
	}

	public override void WorldComponentTick()
	{
		((WorldComponent)this).WorldComponentTick();
		for (int num = goodwillImpacts.Count - 1; num >= 0; num--)
		{
			GoodwillImpactDelayed goodwillImpactDelayed = goodwillImpacts[num];
			if (Find.TickManager.TicksGame >= goodwillImpactDelayed.impactInTicks)
			{
				goodwillImpactDelayed.DoImpact();
				if (goodwillImpactDelayed.RemoveAfterImpact)
				{
					goodwillImpacts.RemoveAt(num);
				}
			}
		}
	}

	public void ImpactFactionGoodwill(GoodwillImpactDelayed goodwillImpact)
	{
		goodwillImpacts.Add(goodwillImpact);
	}

	public override void ExposeData()
	{
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Invalid comparison between Unknown and I4
		((WorldComponent)this).ExposeData();
		Scribe_Collections.Look<GoodwillImpactDelayed>(ref goodwillImpacts, "goodwillImpacts", (LookMode)2, Array.Empty<object>());
		if ((int)Scribe.mode == 4 && goodwillImpacts == null)
		{
			goodwillImpacts = new List<GoodwillImpactDelayed>();
		}
	}
}
