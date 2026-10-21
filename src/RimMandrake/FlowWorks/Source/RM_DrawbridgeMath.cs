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
	/// A leaf's movement is a progress count in ticks, 0 = lowered, FullTicks = raised. A leaf is rigid: off its seat
	/// (any progress) none of its squares is ground (RaisedSquares); its riders tip to the hinge bank first. Raising is a reversible
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

		/// <summary>How many squares are no longer ground at this progress. A leaf is one rigid plank on its hinge: the moment
		/// it leaves its seat (any progress at all) it is a tilting slope that nobody stands on, so EVERY square of it stops being
		/// ground at once, and it is ground again only when fully lowered. (Phase 2: this replaces phase 1's tip-first count,
		/// which left the hinge squares walkable on a tilted leaf and could not honour "tips towards hinged side".)</summary>
		public static int RaisedSquares(int progress, int fullTicks, int length)
		{
			return progress <= 0 || length < 1 ? 0 : length;
		}

		/// <summary>Is this deck index raised (not ground) at this progress?</summary>
		public static bool IsRaised(LeafSpan leaf, int index, int progress, int fullTicks)
		{
			return leaf.Contains(index) && RaisedSquares(progress, fullTicks, leaf.Length) > 0;
		}

		// ── Phase 2: the tip rule (R3) ──────────────────────────────────────────────────────────────

		/// <summary>How far (cardinal steps from the hinge bank's anchor squares) a tipped rider can land (proposal). Beyond it
		/// there is no legal bank square and the rider falls.</summary>
		public const int TipReach = 3;

		/// <summary>One pawn riding the leaf: its distance from the hinge (squares) and its cell index (the tie-break).</summary>
		public struct Rider
		{
			public int Id;
			public int FromHinge;
			public int CellIndex;

			public Rider(int id, int fromHinge, int cellIndex)
			{
				Id = id;
				FromHinge = fromHinge;
				CellIndex = cellIndex;
			}
		}

		/// <summary>R3 order: nearest the hinge first, ties by cell index, then id (fully deterministic).</summary>
		public static List<Rider> TipOrder(IEnumerable<Rider> riders)
		{
			List<Rider> l = new List<Rider>(riders);
			l.Sort((a, b) => a.FromHinge != b.FromHinge ? a.FromHinge.CompareTo(b.FromHinge)
				: a.CellIndex != b.CellIndex ? a.CellIndex.CompareTo(b.CellIndex) : a.Id.CompareTo(b.Id));
			return l;
		}

		/// <summary>The legal landing squares on the hinge bank, nearest first: a breadth-first walk from the anchor squares
		/// through passable squares (never through a wall or a closed gate: `passable` says), at most `reach` steps, keeping the
		/// squares that are `free` (standable, no pawn). Ties within one step keep the walk's order (starts first, then the
		/// neighbour order given).</summary>
		public static List<int> BankLandings(IList<int> starts, System.Func<int, IEnumerable<int>> neighbours, System.Func<int, bool> passable,
			System.Func<int, bool> free, int reach)
		{
			List<int> landings = new List<int>();
			HashSet<int> seen = new HashSet<int>();
			List<int> frontier = new List<int>();
			foreach (int s in starts)
			{
				if (seen.Add(s) && passable(s))
				{
					frontier.Add(s);
				}
			}
			for (int step = 0; step <= reach && frontier.Count > 0; step++)
			{
				List<int> next = new List<int>();
				foreach (int c in frontier)
				{
					if (free(c))
					{
						landings.Add(c);
					}
					if (step == reach)
					{
						continue;
					}
					foreach (int n in neighbours(c))
					{
						if (seen.Add(n) && passable(n))
						{
							next.Add(n);
						}
					}
				}
				frontier = next;
			}
			return landings;
		}

		/// <summary>Assign landings to riders in tip order: the k-th rider takes the k-th landing; riders past the last landing
		/// are the overflow and fall (review answer 1). Returns rider id → landing cell, or -1 for a faller.</summary>
		public static Dictionary<int, int> AssignTips(IEnumerable<Rider> riders, IList<int> landings)
		{
			Dictionary<int, int> to = new Dictionary<int, int>();
			int k = 0;
			foreach (Rider r in TipOrder(riders))
			{
				to[r.Id] = k < landings.Count ? landings[k] : -1;
				k++;
			}
			return to;
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

		// ── Phase 3: control (R2, R4, owner follow-ups 2026-10-20) ─────────────────────────────────

		/// <summary>A player order waiting for a colonist to carry it out at the winch (or, for a raise, at the far anchor).</summary>
		public const int OrderNone = 0;
		public const int OrderRaise = 1;
		public const int OrderLower = 2;

		/// <summary>How often (ticks) the map's free-hostile count is re-read for peace/locked mode.</summary>
		public const int ModeCheckInterval = 60;

		/// <summary>A steel lever throw: the colonist sets the powered drive going and leaves (ticks).</summary>
		public const int LeverTicks = 60;

		/// <summary>The wall-ladder rule (answer 3): a leaf raises from either bank and lowers only from its winch (control) bank.</summary>
		public static bool MayWorkFrom(bool onControlBank, bool raise)
		{
			return raise || onControlBank;
		}

		/// <summary>Whether the drive can move the leaf now: steel needs power (and freezes without it, review answer 4); timber
		/// needs a colonist at the winch this step. No winch house: nothing moves it.</summary>
		public static bool DriveMoves(SuspensionTier t, bool hasWinch, bool powered, bool worked)
		{
			if (!hasWinch)
			{
				return false;
			}
			return IsPowered(t) ? powered : worked;
		}

		/// <summary>A steel leaf with a winch but no power is frozen where it is (it holds; no hand fallback, no drop).</summary>
		public static bool FrozenFor(SuspensionTier t, bool hasWinch, bool powered)
		{
			return IsPowered(t) && hasWinch && !powered;
		}

		/// <summary>R4 + review answer 3: only a FREE hostile locks a drawbridge: an active hostile threat that is neither held by
		/// the pit engine (trapped) nor a prisoner/captive.</summary>
		public static bool IsFreeHostile(bool hostileActiveThreat, bool trappedInPit, bool prisonerOrCaptive)
		{
			return hostileActiveThreat && !trappedInPit && !prisonerOrCaptive;
		}

		/// <summary>Peace mode (no free hostile): a leaf that is up (or going up) and not held raised lowers itself for the
		/// colony; locked mode never starts one.</summary>
		public static bool ShouldAutoLower(bool locked, bool holdRaised, int progress, bool targetRaised, bool autoLowering)
		{
			return !locked && !holdRaised && !autoLowering && (progress > 0 || targetRaised);
		}

		/// <summary>Locking cancels a pending automatic lower (R4: the switch is atomic); the leaf goes back to raised.</summary>
		public static bool ShouldCancelAutoLower(bool locked, bool autoLowering)
		{
			return locked && autoLowering;
		}

		/// <summary>A raise ordered in peace is a deliberate one and holds the leaf up; a raise ordered while locked comes down
		/// again (peace mode) once the threat is gone; a lower order always clears the hold.</summary>
		public static bool HoldAfterOrder(bool raise, bool locked, bool holdBefore)
		{
			return raise ? (!locked || holdBefore) : false;
		}

		/// <summary>Owner follow-up (2026-10-20): a destroyed winch house crashes its leaf down. True when the crash hits
		/// anything (the leaf was off its seat); a lowered leaf has nothing to crash.</summary>
		public static bool WinchLossCrashes(int progress)
		{
			return progress > 0;
		}

		/// <summary>R11 lock readout.</summary>
		public static string LockLine(bool locked, int freeHostiles, bool holdRaised)
		{
			if (locked)
			{
				return "Locked: " + freeHostiles + " free hostile" + (freeHostiles == 1 ? "" : "s") + " on the map; it moves only when ordered";
			}
			return holdRaised ? "Peace: held raised by order" : "Peace: lowers itself for your people";
		}


		// ── Phase 4: raiders (R5) ───────────────────────────────────────────────────────────────

		/// <summary>The longest gap a raid plank spans (squares of hole between the two banks): a timber leaf's default.</summary>
		public const int RaidPlankMaxSpan = 4;

		/// <summary>Ticks a raider spends laying a plank at the lip (proposal: 3 s).</summary>
		public const int RaidPlankLayTicks = 180;

		/// <summary>Does a raid plank fit this crossing line? depths[0] and depths[last] are the two banks, every square between
		/// is hole: both banks at the same height, at least one square of hole, no more than maxSpan.</summary>
		public static bool RaidPlankFits(int[] depths, int maxSpan)
		{
			if (depths == null || depths.Length < 3)
			{
				return false;
			}
			int last = depths.Length - 1;
			if (depths[0] != depths[last] || last - 1 > maxSpan)
			{
				return false;
			}
			for (int i = 1; i < last; i++)
			{
				if (depths[i] <= depths[0])
				{
					return false;   // not a hole below the banks: no gap for a plank to span here
				}
			}
			return true;
		}

		/// <summary>How many planks a raid of this size brings, when it brings any (one per four raiders, at least one).</summary>
		public static int RaidPlankCount(int raiders)
		{
			return raiders <= 0 ? 0 : (raiders + 3) / 4;
		}

		/// <summary>R5 / GPT #13: each plank is laid in ONE transaction, counted exactly once. A carrier interrupted before the
		/// commit lays nothing and keeps the plank; a second commit of the same plank, or a commit on a line already laid, is
		/// refused. Per map, never saved (a laid plank is a bridge record; an unlaid one is an item).</summary>
		public sealed class PlankLedger
		{
			private readonly HashSet<int> committed = new HashSet<int>();
			private readonly HashSet<long> laidLines = new HashSet<long>();

			public int Laid => committed.Count;

			public static long LineKey(int lipCell, int farCell)
			{
				int a = lipCell < farCell ? lipCell : farCell, b = lipCell < farCell ? farCell : lipCell;
				return ((long)a << 32) | (uint)b;
			}

			public bool CanCommit(int plankId, long line)
			{
				return !committed.Contains(plankId) && !laidLines.Contains(line);
			}

			public bool TryCommit(int plankId, long line)
			{
				if (!CanCommit(plankId, line))
				{
					return false;
				}
				committed.Add(plankId);
				laidLines.Add(line);
				return true;
			}

			/// <summary>A laid plank was destroyed: its line may be planked again.</summary>
			public void Release(long line)
			{
				laidLines.Remove(line);
			}
		}

		/// <summary>Phase 6 (R7): may the gate leaf open (for a pawn the door's own faction rules already let through)? Never
		/// while its leaf is off its seat; while locked only when the player holds it open; in peace, yes.</summary>
		public static bool GateOpensFor(bool locked, bool leafUp, bool holdOpen)
		{
			if (leafUp)
			{
				return false;
			}
			return !locked || holdOpen;
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
