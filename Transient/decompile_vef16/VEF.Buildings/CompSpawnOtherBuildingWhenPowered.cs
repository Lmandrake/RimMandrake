using System.Collections.Generic;
using RimWorld;
using Verse;

namespace VEF.Buildings;

public class CompSpawnOtherBuildingWhenPowered : ThingComp
{
	protected CompPowerTrader compPower;

	protected CompFlickable compFlickable;

	public Building newHologram;

	public int tickCounter;

	public CompProperties_SpawnOtherBuildingWhenPowered Props => (CompProperties_SpawnOtherBuildingWhenPowered)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_References.Look<Building>(ref newHologram, "newHologram", false);
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
		compPower = base.parent.GetComp<CompPowerTrader>();
		compFlickable = base.parent.GetComp<CompFlickable>();
		if (newHologram != null && ((Thing)base.parent).Map != null && !((Thing)newHologram).Destroyed)
		{
			((Thing)newHologram).Destroy((DestroyMode)0);
		}
	}

	public override void PostDeSpawn(Map map, DestroyMode mode = 0)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).PostDeSpawn(map, mode);
		if (newHologram != null && map != null && !((Thing)newHologram).Destroyed)
		{
			((Thing)newHologram).Destroy((DestroyMode)0);
		}
	}

	public override void PostDestroy(DestroyMode mode, Map previousMap)
	{
		if (newHologram != null && previousMap != null && !((Thing)newHologram).Destroyed)
		{
			((Thing)newHologram).Destroy((DestroyMode)0);
		}
	}

	public override void CompTickRare()
	{
		//IL_015f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Expected O, but got Unknown
		//IL_012a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0113: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickRare();
		tickCounter++;
		if (tickCounter < Props.tickRaresToCheck)
		{
			return;
		}
		tickCounter = 0;
		if (((Thing)base.parent).Map == null)
		{
			return;
		}
		if (compPower != null && compPower.PowerOn)
		{
			bool flag = true;
			List<Thing> list = ((Thing)base.parent).Map.thingGrid.ThingsListAt(((Thing)base.parent).Position);
			for (int i = 0; i < list.Count; i++)
			{
				if (list[i] is Building && ((Def)list[i].def).defName == Props.defOfBuildingToSpawn)
				{
					flag = false;
				}
			}
			if (!flag)
			{
				return;
			}
			Building val = (Building)ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed(Props.defOfBuildingToSpawn, true), (ThingDef)null);
			((Thing)val).SetFaction(Faction.OfPlayer, (Pawn)null);
			CompQuality compQuality = ((ThingWithComps)val).compQuality;
			if (compQuality != null)
			{
				CompQuality compQuality2 = base.parent.compQuality;
				if (compQuality2 != null)
				{
					compQuality.SetQuality(compQuality2.Quality, (ArtGenerationContext?)(ArtGenerationContext)1);
				}
			}
			GenSpawn.Spawn((Thing)(object)val, ((Thing)base.parent).Position, ((Thing)base.parent).Map, (WipeMode)0);
			newHologram = val;
			return;
		}
		List<Thing> list2 = ((Thing)base.parent).Map.thingGrid.ThingsListAt(((Thing)base.parent).Position);
		for (int j = 0; j < list2.Count; j++)
		{
			if (list2[j] is Building && ((Def)list2[j].def).defName == Props.defOfBuildingToSpawn)
			{
				list2[j].Destroy((DestroyMode)0);
			}
		}
	}
}
