using System.Collections.Generic;
using System.Linq;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.Abilities;

public class Ability_Skyfallers : Ability
{
	private static List<ThingDef> allNaturalRockDefs;

	public static List<ThingDef> AllNaturalRockDefs
	{
		get
		{
			if (allNaturalRockDefs == null)
			{
				allNaturalRockDefs = DefDatabase<ThingDef>.AllDefs.Where((ThingDef d) => d.IsNonResourceNaturalRock).ToList();
			}
			return allNaturalRockDefs;
		}
	}

	public override void Cast(params GlobalTargetInfo[] targets)
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Unknown result type (might be due to invalid IL or missing references)
		base.Cast(targets);
		for (int i = 0; i < targets.Length; i++)
		{
			GlobalTargetInfo val = targets[i];
			List<IntVec3> list = (from c in GenRadial.RadialCellsAround(((GlobalTargetInfo)(ref val)).Cell, GetRadiusForPawn(), true)
				where GenGrid.InBounds(c, ((Thing)pawn).Map) && !GridsUtility.Fogged(c, ((Thing)pawn).Map) && GridsUtility.GetEdifice(c, ((Thing)pawn).Map) == null
				select c).ToList();
			float powerForPawn = GetPowerForPawn();
			for (int j = 0; (float)j < powerForPawn; j++)
			{
				SpawnSkyfaller(GenCollection.RandomElement<IntVec3>((IEnumerable<IntVec3>)list));
			}
		}
	}

	protected virtual void SpawnSkyfaller(IntVec3 cell)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		SkyfallerMaker.SpawnSkyfaller(((Def)def).GetModExtension<AbilityExtension_Skyfaller>().skyfaller, GetContents(), cell, ((Thing)pawn).Map);
	}

	protected virtual IEnumerable<Thing> GetContents()
	{
		int rocks = ((Def)def).GetModExtension<AbilityExtension_Skyfaller>()?.rocks ?? 0;
		for (int i = 0; i < rocks; i++)
		{
			yield return ThingMaker.MakeThing(GenCollection.RandomElement<ThingDef>((IEnumerable<ThingDef>)AllNaturalRockDefs), (ThingDef)null);
		}
	}
}
