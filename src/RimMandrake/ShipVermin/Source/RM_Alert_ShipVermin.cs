using RimMandrake.CreatureBehaviors;
using Verse;

namespace RimMandrake.ShipVermin
{
	/// <summary>
	/// SHIP_VERMIN_MOD_1. The one concrete alert this mod ships — everything
	/// else lives in mandrake.rm.creaturebehaviors' abstract base so a future
	/// vermin family (Greentide, Shokk) need only repeat this much.
	/// </summary>
	public class RM_Alert_ShipVermin : RM_Alert_VerminPopulationBase
	{
		protected override string GroupTag => "ShipVermin";

		public RM_Alert_ShipVermin()
		{
			defaultLabel = "Mynocks aboard: {0}";
			defaultExplanation = "Mynocks have taken hold somewhere in your ships or base ({0} counted). Alone they are barely a nuisance, but left unchecked they breed fast, and a real swarm will gnaw conduits and lights dead compartment by compartment. Hunt them down before the population climbs.";
		}
	}
}
