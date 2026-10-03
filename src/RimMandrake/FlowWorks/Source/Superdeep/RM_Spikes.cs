using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// CANAL_BOTTOM_SPIKES_1 — spikes are per-cell hardware on a superdeep canal bottom, the same
	/// shape as the ladder (a Thing in the cell, a placeworker, a one-line cell query). Owner Q2,
	/// 2026-10-02 (by card): spikes only in the deepest pits; shallower canals are just slow ground.
	///
	/// They fire on DESCENT into the cell only (RM_SuperdeepTrap.PitDescent, raised after the
	/// fall): never on walking up to the lip, never on moving between two D = 4 cells. Spikes key
	/// on the descent, not on being held, so a creature too wide for its pit still takes them on
	/// the way in (owner Q4 interplay). A flying pawn does not land on them.
	/// </summary>
	public static class RM_SpikeUtility
	{
		public static bool HasSpikes(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map))
			{
				return false;
			}
			ThingDef spikes = RimMandrakeFlowWorks_DefOf.RM_Spikes;
			if (spikes == null)
			{
				return false;
			}
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i].def == spikes)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>The placement rule as a pure function of the cell's dug depth: D = 4 only.
		/// Null = accepted, otherwise the refusal reason.</summary>
		public static string PlacementRefusal(RM_MapComponent_Excavation engine, IntVec3 c)
		{
			if (engine == null || !engine.IsExcavated(c))
			{
				return "RMFlow_SpikesNeedSuperdeep".Translate(0);
			}
			int depth = engine.ExcavatedDepthAt(c);
			return depth >= 4 ? null : (string)"RMFlow_SpikesNeedSuperdeep".Translate(depth);
		}

		/// <summary>Lands the spike hits on a pawn that just dropped into <paramref name="cell"/>.
		/// Returns the number of hits landed (0 when the cell is unspiked, the setting is off, or
		/// the pawn is flying).</summary>
		public static int ApplyDescent(Pawn p, IntVec3 cell)
		{
			if (p == null || p.Dead || !p.Spawned || !RimMandrakeFlowWorksSettings.spikesEnabled
				|| p.Flying || !HasSpikes(p.Map, cell))
			{
				return 0;
			}
			float perHit = RM_PitTrapMath.SpikeDamagePerHit(p.BodySize, RimMandrakeFlowWorksSettings.spikeDamageMultiplier);
			int landed = 0;
			for (int i = 0; i < RM_PitTrapMath.SpikeHits; i++)
			{
				if (p.Dead || p.Destroyed)
				{
					break;
				}
				p.TakeDamage(new DamageInfo(DamageDefOf.Stab, perHit));
				landed++;
			}
			return landed;
		}

		/// <summary>Bridge proof (jawa/static_call): would RM_Spikes be accepted on this cell?
		/// "ACCEPT depth N" or "REFUSE depth N: reason".</summary>
		public static string ProofPlacement(Map map, IntVec3 cell)
		{
			RM_MapComponent_Excavation engine = map?.GetComponent<RM_MapComponent_Excavation>();
			int depth = engine != null && engine.IsExcavated(cell) ? engine.ExcavatedDepthAt(cell) : 0;
			string why = PlacementRefusal(engine, cell);
			return why == null ? "ACCEPT depth " + depth : "REFUSE depth " + depth + ": " + why;
		}

		/// <summary>Bridge proof (jawa/static_call): the descent hook, fired directly on the pawn
		/// standing on <paramref name="cell"/> (the pit's descent detector is the live route; this
		/// isolates the spike half). Returns "HITS n | INJURIES Stab k" for the first pawn there.</summary>
		public static string ProofDescent(Map map, IntVec3 cell)
		{
			if (map == null)
			{
				return "REFUSED: no map";
			}
			foreach (Thing t in cell.GetThingList(map))
			{
				if (t is Pawn p)
				{
					int hits = ApplyDescent(p, cell);
					int stabs = 0;
					foreach (Hediff h in p.health.hediffSet.hediffs)
					{
						if (h is Hediff_Injury && h.def == DamageDefOf.Stab.hediff)
						{
							stabs++;
						}
					}
					return "HITS " + hits + " | INJURIES Stab " + stabs + " | bodySize " + p.BodySize.ToString("0.##");
				}
			}
			return "REFUSED: no pawn at " + cell;
		}
	}

	[StaticConstructorOnStartup]
	public static class RM_SpikesHook
	{
		static RM_SpikesHook()
		{
			RM_SuperdeepTrap.PitDescent += (p, cell) => RM_SpikeUtility.ApplyDescent(p, cell);
		}
	}

	/// <summary>Spikes belong on a pit floor, and only the deepest (owner Q2): refused on open
	/// ground and on depths 1-3, with the depth in the reason.</summary>
	public class PlaceWorker_SpikesOnSuperdeep : PlaceWorker
	{
		public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot,
			Map map, Thing thingToIgnore = null, Thing thing = null)
		{
			if (map == null)
			{
				return false;
			}
			string why = RM_SpikeUtility.PlacementRefusal(map.GetComponent<RM_MapComponent_Excavation>(), loc);
			return why == null ? AcceptanceReport.WasAccepted : new AcceptanceReport(why);
		}
	}
}
