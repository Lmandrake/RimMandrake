using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// THEY_MOD_REPLICATION_1. Generic "hunt or march on the colony" JobGiver.
	/// Built from vanilla patterns (AttackTargetFinder.BestAttackTarget, the
	/// same call JobGiver_AIFightEnemy makes) rather than decompiling They!
	/// (Giant Ants)' MyAntMod.JobGiver_AntRaid — replicates the shape of that
	/// behavior (a hidden, permanentEnemy, animal-race faction whose pawns
	/// carry no Lord/duty and must each decide their own approach) without
	/// reading its bytecode.
	///
	/// Gated on RM_DirectedAssaultExtension, so it is a no-op for every other
	/// animal in the game — this assembly names no race of its own.
	/// </summary>
	public class RM_JobGiver_DirectedAssault : ThinkNode_JobGiver
	{
		protected override Job TryGiveJob(Pawn pawn)
		{
			if (!RM_CreatureBehaviorsSettings.directedAssaultBehaviorEnabled)
			{
				return null; // mod option: directed-assault behavior disabled
			}
			RM_DirectedAssaultExtension ext = pawn.def?.GetModExtension<RM_DirectedAssaultExtension>();
			if (ext == null || pawn.Map == null || !pawn.Spawned)
			{
				return null;
			}

			// Something to fight already? Close and attack it — same call
			// vanilla's own JobGiver_AIFightEnemy makes.
			IAttackTarget target = AttackTargetFinder.BestAttackTarget(
				pawn,
				TargetScanFlags.NeedThreat | TargetScanFlags.NeedAutoTargetable,
				null, 0f, ext.huntRadius);
			if (target?.Thing != null)
			{
				return JobMaker.MakeJob(JobDefOf.AttackMelee, target.Thing);
			}

			// Nothing visible yet — this is the "off-map directed assault"
			// half: march toward the colony instead of idling at the map edge.
			Map map = pawn.Map;
			IntVec3 marchTarget = FindMarchTarget(map);
			if (!marchTarget.IsValid)
			{
				return null;
			}
			if (pawn.Position.InHorDistOf(marchTarget, ext.arrivalDistance))
			{
				return null; // close enough — let idle/wander handle the rest
			}
			if (!map.reachability.CanReach(pawn.Position, marchTarget, PathEndMode.OnCell, TraverseParms.For(pawn)))
			{
				return null;
			}
			return JobMaker.MakeJob(JobDefOf.Goto, marchTarget);
		}

		private static IntVec3 FindMarchTarget(Map map)
		{
			var colonists = map.mapPawns.FreeColonistsSpawned;
			if (colonists != null && colonists.Count > 0)
			{
				return colonists[0].Position;
			}
			if (map.IsPlayerHome)
			{
				return map.Center;
			}
			return IntVec3.Invalid;
		}
	}
}
