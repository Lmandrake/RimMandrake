using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// THEY_MOD_REPLICATION_1. Attach to a race ThingDef to make
	/// RM_JobGiver_DirectedAssault drive it: attack the nearest hostile if one
	/// is visible, otherwise march toward the colony instead of idling. This
	/// is the generic replacement for They! (Giant Ants)' custom
	/// MyAntMod.JobGiver_AntRaid — a hidden, permanentEnemy, animal-race
	/// faction that raids without any Lord/IncidentWorker managing it, so
	/// each pawn has to decide its own approach every tick.
	/// </summary>
	public class RM_DirectedAssaultExtension : DefModExtension
	{
		/// <summary>How far TryFindNewTarget/AttackTargetFinder looks for something to fight before falling back to marching.</summary>
		public float huntRadius = 60f;

		/// <summary>Once within this many cells of the march target, stop pushing toward it and let the rest of the think tree (idle/wander) take over.</summary>
		public float arrivalDistance = 5f;
	}
}
