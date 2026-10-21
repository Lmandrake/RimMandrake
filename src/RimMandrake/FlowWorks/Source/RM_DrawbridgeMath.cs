using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>One leaf of a drawbridge: deck indices first..last (inclusive) along its bridge record, hinged at one end.
	/// HingeAtFirst: the hinge (and the winch house) is on the bank beside `first`; otherwise beside `last`.</summary>
	public struct LeafSpan
	{
		public int First;
		public int Last;
		public bool HingeAtFirst;

		public LeafSpan(int first, int last, bool hingeAtFirst)
		{
			First = first;
			Last = last;
			HingeAtFirst = hingeAtFirst;
		}

		public int Length => Last - First + 1;

		/// <summary>Squares from the hinge: 0 is the square beside the hinge bank, Length-1 the leaf's tip.</summary>
		public int FromHinge(int index)
		{
			return HingeAtFirst ? index - First : Last - index;
		}

		public bool Contains(int index)
		{
			return index >= First && index <= Last;
		}
	}

	/// <summary>
	/// DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS (design/RimMandrake/flowworks_drawbridge_design_2026-10-20.md §Ruled design, phase 1
	/// "core"): the Verse-free rules of a drawbridge leaf. A drawbridge is a timber or steel suspension bridge whose deck is cut
	/// into one or two LEAVES (R1): a leaf no longer than its material allows (Mod Settings, defaults timber 4, steel 8); a
	/// longer deck is two leaves, one hinged on each bank, each tipping toward its own hinge.
	///
	/// A leaf's movement is a progress count in ticks, 0 = lowered, FullTicks = raised. Raising lifts the TIP first: the
	/// squares that stop being ground are counted from the tip back to the hinge (RaisedSquares). Raising is a reversible
	/// state change and never a collapse (R3). Numbers are the design's proposals, never measurements.
	/// Compiled into the FlowWorks SelfTest (DrawbridgeChecks).
	/// </summary>
	public static class RM_DrawbridgeMath
	{
		/// <summary>The save record's format version (R9: versioned).</summary>
		public const int LeafRecordVersion = 1;

		/// <summary>Hand winch (timber): about 4 s per square (R2 proposal).</summary>
		public const int HandTicksPerSquare = 240;

		/// <summary>Powered (steel): about 2 s for the whole leaf (R2 proposal).</summary>
		public const int PoweredTicksPerLeaf = 120;

		/// <summary>Only timber and steel are drawbridges (owner answer 8).</summary>
		public static bool IsDrawbridgeTier(SuspensionTier t)
		{
			return t == SuspensionTier.Timber || t == SuspensionTier.Steel;
		}

		/// <summary>Timber is hand-winched, steel is powered (owner answer 4).</summary>
		public static bool IsPowered(SuspensionTier t)
		{
			return t == SuspensionTier.Steel;
		}

		/// <summary>Default longest leaf, by material (answer 7, proposal: timber 4, steel 8); 0 = not a drawbridge material.</summary>
		public static int DefaultMaxLeaf(SuspensionTier t)
		{
			switch (t)
			{
				case SuspensionTier.Timber: return 4;
				case SuspensionTier.Steel: return 8;
				default: return 0;
			}
		}

		/// <summary>Cut the deck squares first..last into leaves: one leaf hinged on `colonyBankAtFirst`'s bank when it fits,
		/// else two leaves (the larger half on the colony bank), each hinged on its own bank; null when even two leaves are too
		/// short to close the gap, or the material is not a drawbridge material.</summary>
		public static List<LeafSpan> SplitLeaves(int first, int last, int maxLeaf, bool colonyBankAtFirst)
		{
			int n = last - first + 1;
			if (n < 1 || maxLeaf < 1)
			{
				return null;
			}
			if (n <= maxLeaf)
			{
				return new List<LeafSpan> { new LeafSpan(first, last, colonyBankAtFirst) };
			}
			if (n > 2 * maxLeaf)
			{
				return null;
			}
			int near = (n + 1) / 2; // the colony-bank leaf takes the odd square
			if (colonyBankAtFirst)
			{
				return new List<LeafSpan> { new LeafSpan(first, first + near - 1, true), new LeafSpan(first + near, last, false) };
			}
			return new List<LeafSpan> { new LeafSpan(last - near + 1, last, false), new LeafSpan(first, last - near, true) };
		}

		/// <summary>Ticks from lowered to raised for a leaf of this length.</summary>
		public static int FullTicks(SuspensionTier t, int length, float speedMultiplier)
		{
			if (length < 1)
			{
				length = 1;
			}
			float m = speedMultiplier <= 0.01f ? 0.01f : speedMultiplier;
			int raw = IsPowered(t) ? PoweredTicksPerLeaf : HandTicksPerSquare * length;
			int ticks = (int)(raw / m + 0.5f);
			return ticks < length ? length : ticks;
		}

		/// <summary>How many squares (counted from the tip) are no longer ground at this progress: any progress at all lifts the
		/// tip off its bank, so 1 tick in is one square raised; full progress is every square.</summary>
		public static int RaisedSquares(int progress, int fullTicks, int length)
		{
			if (progress <= 0 || length < 1)
			{
				return 0;
			}
			if (fullTicks < 1 || progress >= fullTicks)
			{
				return length;
			}
			int sq = (int)(((long)progress * length + fullTicks - 1) / fullTicks); // ceil
			return sq < 1 ? 1 : sq > length ? length : sq;
		}

		/// <summary>Is this deck index raised (not ground) at this progress?</summary>
		public static bool IsRaised(LeafSpan leaf, int index, int progress, int fullTicks)
		{
			if (!leaf.Contains(index))
			{
				return false;
			}
			int raised = RaisedSquares(progress, fullTicks, leaf.Length);
			return leaf.FromHinge(index) >= leaf.Length - raised;
		}

		/// <summary>One drive step toward the target. Returns the new progress (clamped to 0..fullTicks).</summary>
		public static int Step(int progress, bool targetRaised, int fullTicks, int ticks)
		{
			int p = progress + (targetRaised ? ticks : -ticks);
			return p < 0 ? 0 : p > fullTicks ? fullTicks : p;
		}

		public static bool AtTarget(int progress, bool targetRaised, int fullTicks)
		{
			return targetRaised ? progress >= fullTicks : progress <= 0;
		}

		/// <summary>R11 readout: "lowered", "raised", "raising 40%", "lowering 60%".</summary>
		public static string StateLine(int progress, bool targetRaised, int fullTicks, bool frozen)
		{
			string s;
			if (progress <= 0 && !targetRaised)
			{
				s = "lowered";
			}
			else if (progress >= fullTicks && targetRaised)
			{
				s = "raised";
			}
			else
			{
				int pct = fullTicks < 1 ? 0 : (int)(100L * progress / fullTicks);
				s = (targetRaised ? "raising " : "lowering ") + pct + "%";
			}
			return frozen ? s + " (stopped)" : s;
		}
	}
}
