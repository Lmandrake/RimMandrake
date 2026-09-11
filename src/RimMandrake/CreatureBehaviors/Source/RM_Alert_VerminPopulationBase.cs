using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// SHIP_VERMIN_MOD_1. Abstract population-count alert. A concrete mod
	/// subclasses this (e.g. ShipVermin's RM_Alert_ShipVermin) naming the
	/// group tag it watches (RM_VerminPressureExtension.populationGroupTag)
	/// and its label/description translation keys; everything else — summing
	/// live population across every map, firing once any is present — lives
	/// here so a second vermin family (Greentide, Shokk) does not need to
	/// re-derive it. Alert subclasses are auto-discovered by the vanilla
	/// AlertsReadout, so this class itself stays abstract (never instantiated)
	/// and only concrete subclasses show up in play.
	/// </summary>
	public abstract class RM_Alert_VerminPopulationBase : Alert
	{
		protected abstract string GroupTag { get; }

		protected virtual int CurrentPopulation()
		{
			int total = 0;
			foreach (Map map in Find.Maps)
			{
				RM_MapComponent_VerminPopulation comp = map.GetComponent<RM_MapComponent_VerminPopulation>();
				if (comp != null)
				{
					total += comp.GetPopulation(GroupTag);
				}
			}
			return total;
		}

		public override string GetLabel()
		{
			return string.Format(defaultLabel, CurrentPopulation());
		}

		public override TaggedString GetExplanation()
		{
			return string.Format(defaultExplanation, CurrentPopulation());
		}

		public override AlertReport GetReport()
		{
			return CurrentPopulation() > 0 ? AlertReport.Active : AlertReport.Inactive;
		}
	}
}
