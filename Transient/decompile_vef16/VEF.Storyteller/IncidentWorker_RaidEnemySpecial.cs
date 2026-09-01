using RimWorld;
using Verse;

namespace VEF.Storyteller;

public class IncidentWorker_RaidEnemySpecial : IncidentWorker_RaidEnemy
{
	private IncidentDefExtension IncidentDefExtension => IncidentDefExtension.Get((Def)(object)((IncidentWorker)this).def);

	protected override bool TryResolveRaidFaction(IncidentParms parms)
	{
		if (IncidentDefExtension.forcedFaction == null)
		{
			return ((IncidentWorker_RaidEnemy)this).TryResolveRaidFaction(parms);
		}
		parms.faction = Find.FactionManager.FirstFactionOfDef(IncidentDefExtension.forcedFaction);
		return true;
	}

	protected override void ResolveRaidPoints(IncidentParms parms)
	{
		//IL_0006: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		if (IncidentDefExtension.forcedPointsRange == IntRange.One)
		{
			((IncidentWorker_RaidEnemy)this).ResolveRaidPoints(parms);
		}
		else
		{
			parms.points = (float)((IntRange)(ref IncidentDefExtension.forcedPointsRange)).RandomInRange * Find.Storyteller.difficulty.threatScale;
		}
	}

	public override void ResolveRaidStrategy(IncidentParms parms, PawnGroupKindDef groupKind)
	{
		if (IncidentDefExtension.forcedStrategy == null)
		{
			((IncidentWorker_RaidEnemy)this).ResolveRaidStrategy(parms, groupKind);
		}
		else
		{
			parms.raidStrategy = IncidentDefExtension.forcedStrategy;
		}
	}
}
