using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>
	/// PIT_COVER_FIX_OCCUPANT_STAYS_BELOW (owner card 2026-10-21 "Stays below, hidden"). A concealed pit's lid is ground to
	/// everyone who walks onto it, so a pawn already down in the pit when the lid was laid used to read as standing on it:
	/// not held (IsHeldAt false on a covered square), its square in the surface component (StepDepthAt 0), its mass on the
	/// lid, and drawn over the lid's ground print. It popped up through the cover.
	///
	/// Now the lid takes such a pawn BENEATH (RM_SuperdeepTrapState's saved set): held where it stands; it may leave only
	/// along the floor into an open pit square (RM_PitCoverBeneathMath, conservative: never under the next lid); not on the
	/// lid's load, and not dropped again when the lid breaks (it is already on the floor). The lid's inspect line names who is
	/// under it. The flag counts only while an intact lid stands on the pawn's square.
	///
	/// RIMMANDRAKE_LET_PAWN_WALK_UNDER_PLANK_COVER_BRIDGES_ALREADY_ALLOW_IT (owner 2026-11-22 "She should be able to walk
	/// beneath it"): a lid the floor band passes under (Building_PitCover.FloorBandPassesUnder) takes such a pawn into its
	/// FLOOR BAND instead, as a bridge does, and it walks on under the lids along the floor. The held beneath set remains for a
	/// lid the band does not pass under (walk-under setting off, or a floor under 2 m).
	/// RIMMANDRAKE_FADE_EVERY_PIT_COVER_TRANSPARENT_OVER_A_PAWN_LIGHTEN_PLEASED_HIM: a pawn beneath a lid is drawn, the lid
	/// faded over it (RM_CoverFadeMath), no longer hidden.
	/// </summary>
	public static class RM_PitCoverBeneath
	{
		private static RM_SuperdeepTrapState StateOf(Map map)
		{
			return RM_SuperdeepTrap.EngineOf(map)?.SuperdeepTrap;
		}

		/// <summary>Is this pawn down in the pit under an intact lid on its own square?</summary>
		public static bool IsBeneath(Pawn p)
		{
			if (RM_SuperdeepTrapState.BeneathTotal <= 0 || p == null || !p.Spawned)
			{
				return false;
			}
			RM_SuperdeepTrapState st = StateOf(p.Map);
			return st != null && st.InBeneathSet(p) && RM_PitCoverUtility.CoverAt(p.Map, p.Position) != null;
		}

		/// <summary>The lid has just been laid (not loaded): every living walker down in the pit on its square goes beneath it
		/// and stops where it is.</summary>
		public static void TakeUnder(Building_PitCover cover, bool respawningAfterLoad)
		{
			Map map = cover?.Map;
			if (map == null || respawningAfterLoad)
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			RM_SuperdeepTrapState st = eng?.SuperdeepTrap;
			if (st == null)
			{
				return;
			}
			IntVec3 c = cover.Position;
			bool dug = eng.IsExcavated(c) && eng.ClimbDepthAt(c) > 0;
			List<Thing> things = c.GetThingList(map);
			List<Pawn> under = null;
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i] is Pawn p && RM_PitCoverBeneathMath.TakesBeneath(dug, p.Dead, p.Flying, false))
				{
					(under ?? (under = new List<Pawn>())).Add(p);
				}
			}
			if (under == null)
			{
				return;
			}
			RM_MapComponent_SuspensionBridges band = cover.FloorBandPassesUnder ? RM_MapComponent_SuspensionBridges.Of(map) : null;
			foreach (Pawn p in under)
			{
				if (band != null)
				{
					band.SetBand(p, true);   // down on the floor under the lid: the floor band, free to walk on beneath
					continue;
				}
				st.SetBeneath(p, true);
				p.pather?.StopDead();
				if (p.jobs?.curJob != null)
				{
					p.jobs.EndCurrentJob(JobCondition.InterruptForced);
				}
			}
		}

		/// <summary>May this beneath pawn take the step to <paramref name="next"/> (a cardinal step into an open pit square
		/// it can climb to)?</summary>
		public static bool StepAllowed(Pawn p, RM_MapComponent_Excavation eng, IntVec3 next)
		{
			Map map = p?.Map;
			if (map == null || eng == null || !next.InBounds(map))
			{
				return false;
			}
			IntVec3 from = p.Position;
			if (next == from)
			{
				return true;
			}
			bool diagonal = from.x != next.x && from.z != next.z;
			bool toDug = eng.IsExcavated(next);
			return RM_PitCoverBeneathMath.StepAllowed(diagonal, toDug, RM_PitCoverUtility.IsCovered(map, next),
				eng.ClimbDepthAt(from), toDug ? eng.ClimbDepthAt(next) : 0, RM_PocketGrid.ClimbLimitOf(p));
		}

		/// <summary>No open pit square beside it that it could step to.</summary>
		public static bool Trapped(Pawn p)
		{
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(p?.Map);
			if (eng == null)
			{
				return true;
			}
			IntVec3 c = p.Position;
			return RM_PitCoverBeneathMath.Trapped(StepAllowed(p, eng, c + IntVec3.North), StepAllowed(p, eng, c + IntVec3.East),
				StepAllowed(p, eng, c + IntVec3.South), StepAllowed(p, eng, c + IntVec3.West));
		}

		/// <summary>Who is beneath these lid squares (the inspect line): held beneath, or walking under them in the floor band.</summary>
		public static List<Pawn> BeneathOn(Map map, IEnumerable<Building_PitCover> deck)
		{
			List<Pawn> list = new List<Pawn>();
			if (map == null || (RM_SuperdeepTrapState.BeneathTotal <= 0 && RM_MapComponent_SuspensionBridges.BandTotal <= 0))
			{
				return list;
			}
			foreach (Building_PitCover d in deck)
			{
				if (d == null || !d.Spawned || d.Map != map)
				{
					continue;
				}
				List<Thing> things = d.Position.GetThingList(map);
				for (int i = 0; i < things.Count; i++)
				{
					if (things[i] is Pawn p && !p.Dead && !list.Contains(p) && (IsBeneath(p) || RM_SuspensionUnderpass.InFloorBand(p)))
					{
						list.Add(p);
					}
				}
			}
			return list;
		}
	}
}
