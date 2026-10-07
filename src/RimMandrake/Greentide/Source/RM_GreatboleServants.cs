using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Greentide
{
	// GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1, spec §8b-ii — the arboreal servant crossover, OPT-IN
	// (RM_GreentideSettings.greatboleServantsEnabled, default OFF; Utinni ships it off).
	// Owner ruling 2026-10-03 (question card): vanilla Gauranlen, nearby-building penalty OFF.
	//
	// Engine check (FOUNDRY 2026-10-04, re-read 2026-10-06, RimSage decompiled 1.6):
	// CompTreeConnection never casts its parent to Plant, and ThingRequestGroup.DryadSpawner is
	// "def has CompProperties_TreeConnection", so pruning, mode change and both alerts find a
	// Building host unchanged. Two places key on ThingDefOf.Plant_TreeGauranlen and would never see
	// RM_GreatboleCore; these two classes replace them, and are swapped in only by
	// Patches/RM_Greatbole_Crossovers.xml when the setting is on. Both enumerate the whole
	// DryadSpawner group, so vanilla Gauranlen trees keep working exactly as before.

	/// <summary>Gate 1: the connection ritual's target list. Vanilla lists only Plant_TreeGauranlen.</summary>
	public class RM_RitualObligationTargetWorker_UnconnectedDryadSpawner : RitualObligationTargetWorker_UnconnectedGauranlenTree
	{
		public RM_RitualObligationTargetWorker_UnconnectedDryadSpawner()
		{
		}

		public RM_RitualObligationTargetWorker_UnconnectedDryadSpawner(RitualObligationTargetFilterDef def)
			: base(def)
		{
		}

		public override IEnumerable<TargetInfo> GetTargets(RitualObligation obligation, Map map)
		{
			List<Thing> hosts = map.listerThings.ThingsInGroup(ThingRequestGroup.DryadSpawner);
			for (int i = 0; i < hosts.Count; i++)
			{
				CompTreeConnection comp = hosts[i].TryGetComp<CompTreeConnection>();
				if (comp != null && !comp.Connected && !comp.ConnectionTorn)
				{
					yield return hosts[i];
				}
			}
		}
	}

	/// <summary>Gate 2: where the connector stands. Vanilla searches only Plant_TreeGauranlen.
	/// The spot is the cell west of the host (vanilla's own offset), so at a greatbole core the
	/// player must have mined that cell open first.</summary>
	public class RM_RitualPosition_BesideDryadSpawner : RitualPosition_BesideTree
	{
		public override IEnumerable<Thing> CandidateThings(LordJob_Ritual ritual)
		{
			List<Thing> hosts = ritual.Map.listerThings.ThingsInGroup(ThingRequestGroup.DryadSpawner);
			for (int i = 0; i < hosts.Count; i++)
			{
				if (hosts[i].Position.InHorDistOf(ritual.selectedTarget.Cell, 50f))
				{
					yield return hosts[i];
				}
			}
		}
	}
}
