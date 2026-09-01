using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompChangeDefIfNotUnique : ThingComp
{
	private bool flag;

	public CompProperties_ChangeDefIfNotUnique Props => (CompProperties_ChangeDefIfNotUnique)(object)base.props;

	public override void PostExposeData()
	{
		Scribe_Values.Look<bool>(ref flag, "flag", false, false);
	}

	public override void PostSpawnSetup(bool respawningAfterLoad)
	{
		((ThingComp)this).PostSpawnSetup(respawningAfterLoad);
		foreach (Pawn item in ((Thing)base.parent).Map.mapPawns.AllPawnsSpawned)
		{
			if (((Def)((Thing)item).def).defName == ((Def)((Thing)base.parent).def).defName)
			{
				flag = true;
			}
		}
	}

	public override void CompTick()
	{
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTick();
		if (flag)
		{
			GenSpawn.Spawn((Thing)(object)PawnGenerator.GeneratePawn(new PawnGenerationRequest(PawnKindDef.Named(Props.defToChangeTo), (Faction)null, (PawnGenerationContext)2, (PlanetTile?)null, false, false, false, true, false, 1f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false)), ((Thing)base.parent).Position, ((Thing)base.parent).Map, (WipeMode)0);
			((Thing)base.parent).Destroy((DestroyMode)0);
		}
	}
}
