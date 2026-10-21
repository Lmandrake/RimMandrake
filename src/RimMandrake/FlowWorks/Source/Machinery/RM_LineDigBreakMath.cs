using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.Machinery
{
	// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 2 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P4):
	// which lines a committed dig breaks. Pure: no Verse, no UnityEngine, so the offline SelfTest compiles this file itself
	// (LineDigBreakChecks.cs). The map side (called from RM_MapComponent_Excavation.Deepen) is RM_LineDigBreak.cs.

	public static class RM_LineDigBreakMath
	{
		/// <summary>P4: rigid pipe, rigid conduit and cords on a dug square are destroyed. A hose is not: it re-plans or is cut
		/// by its own router once that router reads depth (P5, the item's phase 6), so a dig never destroys a hose.</summary>
		public static bool BreaksOnDig(LineKind k) => k != LineKind.Hose;

		/// <summary>A dig COMMITS only when the depth grid actually went down (Deepen returned a deeper D). A designation, a
		/// cancelled job or a cut the cap refused never reaches this, so it breaks nothing.</summary>
		public static bool IsCommit(int depthBefore, int depthAfter) => depthAfter > depthBefore;

		/// <summary>The lines one committed cut on one square breaks: every tagged line of a breaking kind that is still standing.
		/// Rules off, no commit, untagged things (kindOf null) and things already gone (destroyed by an earlier commit or anything
		/// else) give nothing, so calling this again for the same square is a no-op: the teardown is idempotent.</summary>
		public static List<T> ToBreak<T>(bool rulesOn, int depthBefore, int depthAfter, IEnumerable<T> onSquare,
			Func<T, LineKind?> kindOf, Func<T, bool> gone)
		{
			var hit = new List<T>();
			if (!rulesOn || !IsCommit(depthBefore, depthAfter) || onSquare == null)
			{
				return hit;
			}
			foreach (T t in onSquare)
			{
				if (t == null || gone(t))
				{
					continue;
				}
				LineKind? k = kindOf(t);
				if (k != null && BreaksOnDig(k.Value) && !hit.Contains(t))
				{
					hit.Add(t);
				}
			}
			return hit;
		}

		/// <summary>The one message a commit that broke something shows (null when it broke nothing).</summary>
		public static string Message(int broken)
		{
			if (broken <= 0)
			{
				return null;
			}
			return broken == 1
				? "Digging broke the line on this square. Cross a pit, trench or canal on poles."
				: "Digging broke " + broken + " lines on this square. Cross a pit, trench or canal on poles.";
		}
	}
}
