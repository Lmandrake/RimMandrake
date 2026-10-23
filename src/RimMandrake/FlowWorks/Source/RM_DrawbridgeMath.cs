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

		/// <summary>A winch house left the map any way at all (destroyed, deconstructed, flown off on a gravship, despawned by anything else) while
		/// its leaf stayed: that is a lost winch, and the leaf crashes per WinchLossCrashes. The one exception is a winch whose
		/// bridge was itself torn loose at that same launch (RM_Patch_GravshipLaunch_Bridges): its span already fell, so there
		/// is no leaf left to crash; the link is only cleared. Deconstructing counts as losing it (the ruled general rule; a
		/// lower-then-release on deconstruct is unruled, put to the owner).</summary>
		public static bool WinchDepartureCrashes(int progress, bool bridgeTornLooseAtLaunch)
		{
			return !bridgeTornLooseAtLaunch && WinchLossCrashes(progress);
		}

		/// <summary>A tower may join a bridge's supports only when the bridge is not a drawbridge (a leaf swings from a bank,
		/// never from a tower: CanBeDrawbridge). Read at placement, at frame completion and at a rebuild.</summary>
		public static bool TowerMayJoin(bool isDrawbridge)
		{
			return !isDrawbridge;
		}

		public const string TowerOnDrawbridgeRefused = "A drawbridge cannot stand on towers: its leaves swing from the banks.";

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

	/// <summary>
	/// DRAWBRIDGE_LOOKS_WIRE_PICTURES_IN_WINGS: the texPath candidates of every drawbridge picture, best first, for a material
	/// (Timber/Steel) and a look (Scrapper/Industrial/Modern/Futuristic; null = no looks loaded). DRAWBRIDGE_LOOKS_FIX_HIS_PICKS_OUTRANK
	/// (owner by card 2026-10-22, "Material picks win": a Timber drawbridge always shows your Timber picture; looks only restyle
	/// pipes and machinery): the MATERIAL's picture wins; a part the material has no picture for falls back to the look's
	/// picture (today only the timber gate shut). Names follow the installed art (bridge_art_redraw, 2026-10-21): material files are &lt;part&gt;_&lt;M&gt;[_&lt;view&gt;], look
	/// files &lt;part&gt;_&lt;view|state&gt;_&lt;Look&gt; (the winch keeps its material in the look name, as its drive differs). Pure:
	/// the game reads the first candidate that exists (RM_DrawbridgeArt); selftest_flowworks_drawbridge_art.py checks them on disk.
	/// </summary>
	public static class DrawbridgeArtPaths
	{
		public const string Dir = "Things/Building/FlowWorks/Drawbridge/";
		public static readonly string[] Looks = { "Scrapper", "Industrial", "Modern", "Futuristic" };
		public static readonly string[] LeafViews = { "Face", "Underside", "Edge" };
		public const string RaidPlankLaid = Dir + "RM_RaidPlank_Laid";
		public const string RaidPlankLaidEnd = Dir + "RM_RaidPlank_LaidEnd";

		public static string Material(SuspensionTier t)
		{
			return t == SuspensionTier.Steel ? "Steel" : "Timber";
		}

		private static string[] LookThenMaterial(string look, string lookPath, string materialPath)
		{
			return look == null ? new[] { materialPath } : new[] { materialPath, lookPath };
		}

		/// <summary>The raised leaf, one view (Face, Underside, Edge); a single picture.</summary>
		public static string[] LeafUp(SuspensionTier t, string look, string view)
		{
			return LookThenMaterial(look, Dir + "RM_DrawbridgeLeafUp_" + view + "_" + look, Dir + "RM_DrawbridgeLeafUp_" + Material(t) + "_" + view);
		}

		/// <summary>The art planks beside the hinge; a single picture.</summary>
		public static string[] Planks(SuspensionTier t, string look)
		{
			return LookThenMaterial(look, Dir + "RM_DrawbridgePlanks_" + look, Dir + "RM_DrawbridgePlanks_" + Material(t));
		}

		/// <summary>The winch house; a Graphic_Multi base path (_south/_east/_north).</summary>
		public static string[] Winch(SuspensionTier t, string look)
		{
			return LookThenMaterial(look, Dir + "RM_DrawbridgeWinch_" + Material(t) + "_" + look, Dir + "RM_DrawbridgeWinch_" + Material(t));
		}

		/// <summary>The gate leaf shut or open; a base path with _south (face-on; north reuses it) and _east (edge-on).</summary>
		public static string[] Gate(SuspensionTier t, string look, bool open)
		{
			string state = open ? "Open" : "Closed";
			return LookThenMaterial(look, Dir + "RM_DrawbridgeGate_" + state + "_" + look, Dir + "RM_DrawbridgeGate_" + Material(t) + "_" + state);
		}

		/// <summary>The gate's facing file for a door rotation: a door in an east-west wall turns North and shows its face
		/// (_south); in a north-south wall it turns East and shows its edge (_east).</summary>
		public static string GateFacing(bool rotationHorizontal)
		{
			return rotationHorizontal ? "_east" : "_south";
		}

		public enum RaidPlankPiece
		{
			None,
			Mid,
			EndNear,
			EndFar,
		}

		/// <summary>Which picture a laid raid plank square draws: its record runs lip (index 0) to far bank (length-1), planks
		/// lie on 1..length-2. The two end squares draw the end piece (hooks biting the bank), the rest the mid piece; a
		/// one-square plank draws the end hooked to the lip.</summary>
		public static RaidPlankPiece PieceAt(int index, int length)
		{
			int last = length - 2;
			if (index < 1 || index > last)
			{
				return RaidPlankPiece.None;
			}
			if (index == 1)
			{
				return RaidPlankPiece.EndNear;
			}
			return index == last ? RaidPlankPiece.EndFar : RaidPlankPiece.Mid;
		}

		/// <summary>The art's top edge (the end piece's hooks) points back toward the lip (index 0) for the near end, else along
		/// the record toward the far bank.</summary>
		public static bool TopTowardLip(RaidPlankPiece p)
		{
			return p == RaidPlankPiece.EndNear;
		}
	}

	/// <summary>
	/// DRAWBRIDGE_CABLES_FIX_STOP_SHORT: where a suspension / drawbridge anchor's two ropes run, read from the art (measured from
	/// the PNGs' alpha by art_source/Drawbridge/measure_cable_art.py into anchor_cable_art.json; the SelfTest grades this table
	/// against that fixture). Owner 2026-10-23: lowered, the ropes stopped short of the deck ("bridges have gaps in their support
	/// cables"); raised: "Ropes should now be slack and disconnected" (no rope across the pit, no stiff rope at the raised leaf's top).
	/// Rope frame: along 0 = the anchor square's back edge, 1 = the edge facing the deck; lateral 0 = the square's centre line,
	/// + = left of the rope's direction; both in cells. Pure: no Verse, no UnityEngine.
	/// </summary>
	public static class RM_DrawbridgeCableMath
	{
		public struct RopeArt
		{
			public double Lateral, Thick, Attach, End;

			public RopeArt(double lateral, double thick, double attach, double end)
			{
				Lateral = lateral;
				Thick = thick;
				Attach = attach;
				End = end;
			}
		}

		/// <summary>A straight rope piece in the rope frame. Painted: already in the anchor picture; else drawn by code.</summary>
		public struct Piece
		{
			public double A0, L0, A1, L1;
			public bool Painted;
		}

		/// <summary>How far a taut rope runs past the deck-facing edge, under the deck's end (no hairline seam).</summary>
		public const double DeckOverlap = 0.04;

		/// <summary>A slack rope never reaches past this along the anchor square: it lies on the bank, never over the pit.</summary>
		public const double SlackReach = 0.9;

		/// <summary>Measured by art_source/Drawbridge/measure_cable_art.py (anchor_cable_art.json). Key "look/material/facing"
		/// for the styled Timber/Steel pictures, upright bollards since ANCHOR_BOLLARD_REDRAW_LIES_DOWN_ON_DUTY: the post occludes the
		/// rope that runs away from the camera, so the attachment point differs per facing. "look/material" for the styled Heavy
		/// pictures (all facings the same picture turned), "base/material" for the unstyled single picture. Look up with
		/// <see cref="RopesFor"/>.</summary>
		public static readonly Dictionary<string, RopeArt[]> Art = new Dictionary<string, RopeArt[]>
		{
			{ "Futuristic/Heavy", new[] { new RopeArt(0.21289, 0.05078, 0.62500, 0.94922), new RopeArt(-0.21289, 0.05078, 0.62500, 0.94922) } },
			{ "Futuristic/Steel/east", new[] { new RopeArt(0.20312, 0.03906, 0.41406, 0.94922), new RopeArt(-0.20312, 0.03906, 0.41406, 0.94922) } },
			{ "Futuristic/Steel/north", new[] { new RopeArt(0.20312, 0.03906, 0.56250, 0.94922), new RopeArt(-0.20312, 0.03906, 0.56250, 0.94922) } },
			{ "Futuristic/Steel/south", new[] { new RopeArt(0.20312, 0.03906, 0.37500, 0.94922), new RopeArt(-0.20312, 0.03906, 0.37500, 0.94922) } },
			{ "Futuristic/Timber/east", new[] { new RopeArt(0.21484, 0.03906, 0.41797, 0.94922), new RopeArt(-0.21875, 0.03906, 0.41797, 0.94922) } },
			{ "Futuristic/Timber/north", new[] { new RopeArt(0.21484, 0.03906, 0.57812, 0.94922), new RopeArt(-0.21875, 0.03906, 0.57812, 0.94922) } },
			{ "Futuristic/Timber/south", new[] { new RopeArt(0.21484, 0.03906, 0.37500, 0.94922), new RopeArt(-0.21875, 0.03906, 0.37500, 0.94922) } },
			{ "Industrial/Heavy", new[] { new RopeArt(0.21680, 0.05078, 0.52344, 0.94922), new RopeArt(-0.21875, 0.04688, 0.52344, 0.94922) } },
			{ "Industrial/Steel/east", new[] { new RopeArt(0.22852, 0.03516, 0.41406, 0.94922), new RopeArt(-0.23438, 0.03125, 0.41797, 0.94922) } },
			{ "Industrial/Steel/north", new[] { new RopeArt(0.22852, 0.03516, 0.56250, 0.94922), new RopeArt(-0.23438, 0.03125, 0.56250, 0.94922) } },
			{ "Industrial/Steel/south", new[] { new RopeArt(0.22852, 0.03516, 0.37500, 0.94922), new RopeArt(-0.23438, 0.03125, 0.37500, 0.94922) } },
			{ "Industrial/Timber/east", new[] { new RopeArt(0.23047, 0.04688, 0.41406, 0.94922), new RopeArt(-0.23242, 0.04297, 0.41406, 0.94922) } },
			{ "Industrial/Timber/north", new[] { new RopeArt(0.23047, 0.04688, 0.57422, 0.94922), new RopeArt(-0.23242, 0.04297, 0.57422, 0.94922) } },
			{ "Industrial/Timber/south", new[] { new RopeArt(0.23047, 0.04688, 0.37109, 0.94922), new RopeArt(-0.23242, 0.04297, 0.37500, 0.94922) } },
			{ "Modern/Heavy", new[] { new RopeArt(0.20508, 0.04297, 0.72656, 0.94922), new RopeArt(-0.20898, 0.04297, 0.72656, 0.94922) } },
			{ "Modern/Steel/east", new[] { new RopeArt(0.21484, 0.03125, 0.42578, 0.94922), new RopeArt(-0.21875, 0.03125, 0.42188, 0.94922) } },
			{ "Modern/Steel/north", new[] { new RopeArt(0.21484, 0.03125, 0.56250, 0.94922), new RopeArt(-0.21875, 0.03125, 0.56250, 0.94922) } },
			{ "Modern/Steel/south", new[] { new RopeArt(0.21484, 0.03125, 0.37500, 0.94922), new RopeArt(-0.21875, 0.03125, 0.37500, 0.94922) } },
			{ "Modern/Timber/east", new[] { new RopeArt(0.20117, 0.04297, 0.41406, 0.94922), new RopeArt(-0.20508, 0.04297, 0.41406, 0.94922) } },
			{ "Modern/Timber/north", new[] { new RopeArt(0.20117, 0.04297, 0.57812, 0.94922), new RopeArt(-0.20508, 0.04297, 0.57812, 0.94922) } },
			{ "Modern/Timber/south", new[] { new RopeArt(0.20117, 0.04297, 0.37500, 0.94922), new RopeArt(-0.20508, 0.04297, 0.37500, 0.94922) } },
			{ "Scrapper/Heavy", new[] { new RopeArt(0.21094, 0.04688, 0.48438, 0.94922), new RopeArt(-0.21484, 0.04688, 0.48438, 0.94922) } },
			{ "Scrapper/Steel/east", new[] { new RopeArt(0.21484, 0.03125, 0.42188, 0.94922), new RopeArt(-0.21875, 0.03125, 0.42188, 0.94922) } },
			{ "Scrapper/Steel/north", new[] { new RopeArt(0.21484, 0.03125, 0.57031, 0.94922), new RopeArt(-0.21875, 0.03125, 0.57031, 0.94922) } },
			{ "Scrapper/Steel/south", new[] { new RopeArt(0.21484, 0.03125, 0.37500, 0.94922), new RopeArt(-0.21875, 0.03125, 0.37500, 0.94922) } },
			{ "Scrapper/Timber/east", new[] { new RopeArt(0.21289, 0.05078, 0.41016, 0.94922), new RopeArt(-0.21289, 0.05078, 0.41016, 0.94922) } },
			{ "Scrapper/Timber/north", new[] { new RopeArt(0.21289, 0.05078, 0.57422, 0.94922), new RopeArt(-0.21289, 0.05078, 0.57422, 0.94922) } },
			{ "Scrapper/Timber/south", new[] { new RopeArt(0.21289, 0.05078, 0.37109, 0.94922), new RopeArt(-0.21289, 0.05078, 0.37109, 0.94922) } },
			{ "base/Heavy/east", new[] { new RopeArt(0.19336, 0.05078, 0.44141, 1.00000), new RopeArt(-0.19531, 0.04688, 0.44141, 1.00000) } },
			{ "base/Heavy/north", new[] { new RopeArt(0.19336, 0.05078, 0.51953, 1.00000), new RopeArt(-0.19531, 0.04688, 0.51953, 1.00000) } },
			{ "base/Heavy/south", new[] { new RopeArt(0.19336, 0.05078, 0.36328, 1.00000), new RopeArt(-0.19531, 0.04688, 0.36719, 1.00000) } },
			{ "base/Rope/east", new[] { new RopeArt(0.12109, 0.03906, 0.40625, 1.00000), new RopeArt(-0.12109, 0.03906, 0.40625, 1.00000) } },
			{ "base/Rope/north", new[] { new RopeArt(0.12109, 0.03906, 0.51953, 1.00000), new RopeArt(-0.12109, 0.03906, 0.51953, 1.00000) } },
			{ "base/Rope/south", new[] { new RopeArt(0.12109, 0.03906, 0.36719, 1.00000), new RopeArt(-0.12109, 0.03906, 0.36719, 1.00000) } },
			{ "base/Steel/east", new[] { new RopeArt(0.22461, 0.02734, 0.42578, 1.00000), new RopeArt(-0.22852, 0.02734, 0.42578, 1.00000) } },
			{ "base/Steel/north", new[] { new RopeArt(0.22461, 0.02734, 0.55859, 1.00000), new RopeArt(-0.22852, 0.02734, 0.55859, 1.00000) } },
			{ "base/Steel/south", new[] { new RopeArt(0.22461, 0.02734, 0.37500, 1.00000), new RopeArt(-0.22852, 0.02734, 0.37500, 1.00000) } },
			{ "base/Timber/east", new[] { new RopeArt(0.18945, 0.04297, 0.41797, 1.00000), new RopeArt(-0.18945, 0.04297, 0.42188, 1.00000) } },
			{ "base/Timber/north", new[] { new RopeArt(0.18945, 0.04297, 0.55469, 1.00000), new RopeArt(-0.18945, 0.04297, 0.55469, 1.00000) } },
			{ "base/Timber/south", new[] { new RopeArt(0.18945, 0.04297, 0.37500, 1.00000), new RopeArt(-0.18945, 0.04297, 0.37500, 1.00000) } },
		};

		/// <summary>The raised leaf's edge pictures paint a stiff rope stub off the top of the hook; only the leaf body's columns
		/// (u0, u1) below the top of the hook's eye (a fraction of the picture's height from its top) are drawn. Key: the
		/// picture's name after "RM_DrawbridgeLeafUp_".</summary>
		public static readonly Dictionary<string, double[]> LeafEdgeBody = new Dictionary<string, double[]>
		{
			{ "Edge_Futuristic", new[] { 0.44922, 0.60547, 0.01562 } },
			{ "Edge_Industrial", new[] { 0.40625, 0.50781, 0.06348 } },
			{ "Edge_Modern", new[] { 0.46484, 0.58203, 0.05371 } },
			{ "Edge_Scrapper", new[] { 0.60156, 0.76562, 0.01465 } },
			{ "Steel_Edge", new[] { 0.42578, 0.54297, 0.04102 } },
			{ "Timber_Edge", new[] { 0.42578, 0.53125, 0.06250 } },
		};

		/// <summary>The art key of an anchor texture path: "&lt;look&gt;/&lt;material&gt;" for a styled picture
		/// (…/SuspensionBridge/&lt;Look&gt;/RM_SuspensionAnchor_&lt;Material&gt;), "base/&lt;material&gt;" for the unstyled one; null otherwise.</summary>
		public static string KeyOf(string texPath, bool styled)
		{
			if (string.IsNullOrEmpty(texPath))
			{
				return null;
			}
			string[] parts = texPath.Replace('\\', '/').Split('/');
			string file = parts[parts.Length - 1];
			const string pre = "RM_SuspensionAnchor_";
			if (!file.StartsWith(pre, System.StringComparison.Ordinal))
			{
				return null;
			}
			string mat = file.Substring(pre.Length);
			// the unstyled pictures live straight in SuspensionBridge/: upright per-facing bollards (Graphic_Multi) since
			// ANCHOR_BASE_REDRAW_STILL_LYING_FLAT, no longer the one rotated single
			string look = parts.Length >= 2 ? parts[parts.Length - 2] : "";
			string key = styled && look != "SuspensionBridge" ? look + "/" + mat : "base/" + mat;
			return Art.ContainsKey(key) || Art.ContainsKey(key + "/east") ? key : null;
		}

		/// <summary>The rope table of one picture: the per-facing entry ("look/material/facing") where the art differs by facing,
		/// else the shared one.</summary>
		public static RopeArt[] RopesFor(string key, string facing)
		{
			return Art.TryGetValue(key + "/" + facing, out RopeArt[] r) ? r : Art[key];
		}

		/// <summary>Lowered: each rope is the painted run (attach → painted end) plus, where the picture stops short of the
		/// deck-facing edge, a drawn run from just inside the painted end to past the edge under the deck.</summary>
		public static List<Piece> Taut(RopeArt r)
		{
			var list = new List<Piece> { new Piece { A0 = r.Attach, L0 = r.Lateral, A1 = r.End, L1 = r.Lateral, Painted = true } };
			if (r.End < 1.0 + DeckOverlap)
			{
				double from = System.Math.Max(r.Attach, r.End - r.Thick);
				list.Add(new Piece { A0 = from, L0 = r.Lateral, A1 = 1.0 + DeckOverlap, L1 = r.Lateral, Painted = false });
			}
			return list;
		}

		/// <summary>How flat a ground coil reads on screen: its screen-vertical extent over its screen-horizontal one. A rope lying
		/// on the ground is seen as a squashed ring; a loop taller than this reads as a hook standing up (SLACK_LOOP_REDRAW_STANDS_UP_IN_PROFILE,
		/// art brief C6: the true perspective plane).</summary>
		public const double CoilAspect = 0.55;

		/// <summary>The smallest along semi-axis of an E/W coil: below it the squashed ring is too thin to read as slack.</summary>
		public const double MinCoilAlong = 0.15;

		/// <summary>A slack coil keeps this far from the square's centre line (the two ropes never cross) and from its edge.</summary>
		public const double CoilMargin = 0.05;

		/// <summary>A slack coil's semi-axis across the screen, the same in every rotation.</summary>
		public const double CoilWide = 0.15;

		/// <summary>How uneven a slack coil's turns are (radius ± this fraction).</summary>
		public const double CoilWobble = 0.10;

		/// <summary>The foot of an upright bollard in its _north picture (rope frame along): every styled Timber/Steel _north
		/// picture's lowest opaque row is along 0.270 (measured 2026-10-23, 8 pictures). The deck is up the screen there, so the
		/// post's head (the attachment point) is drawn above its foot and a coil placed ahead of the head floats at head height
		/// like a halo; the rope must drop to the ground at the foot instead (art-eval run slack_coil_20261023, GPT K1/K2).</summary>
		public const double UprightFootNorth = 0.27;

		/// <summary>Where a slack coil must lie for this print: the upright post's foot when the deck is up the screen (a styled
		/// per-facing _north print), else -1 (the coil lies ahead of the attachment point).</summary>
		public static double SlackFoot(string key, string facing)
		{
			return facing == "north" && key != null && Art.ContainsKey(key + "/north") ? UprightFootNorth : -1;
		}

		/// <summary>Raised (slack, disconnected): the rope drops from its attachment point into a coil lying flat on the bank, a
		/// ring squashed in the screen's vertical (<see cref="CoilAspect"/>) in EVERY rotation, so it lies on the ground plane and
		/// never stands up as a hook. alongScreenVertical: the rope runs up/down the screen (rotations N/S), so the coil's
		/// short axis is along the rope; else (E/W) its short axis is lateral. The coil stays on its own side of the centre line,
		/// inside the square, and never past <see cref="SlackReach"/>; it winds a little over one turn, closing inward (a loose
		/// end, not a hoop). foot >= 0 (<see cref="SlackFoot"/>): the coil lies on the ground just in front of the post, its far
		/// edge at the foot, so the rope drops down the post's front from its head into it and never crosses the post behind it
		/// (a ring round the foot drew its far arc over the post base: art-eval slack_coil_20261023_r2, LAYER_ORDER).</summary>
		public static List<(double A, double L)> Slack(RopeArt r, bool alongScreenVertical, double foot = -1, int n = 44)
		{
			double s = r.Lateral >= 0 ? 1.0 : -1.0;
			double lat = System.Math.Abs(r.Lateral);
			double alongRoom = System.Math.Max(0.06, (SlackReach - r.Attach) / 2);   // semi-axis room ahead of the bollard
			double latRoom = (0.5 - 2 * CoilMargin) / 2;                                // semi-axis room on its own side
			double ra, rl;
			if (alongScreenVertical)
			{
				rl = System.Math.Min(CoilWide, latRoom);                     // CoilWide across the screen in every rotation (_r5: E/W coils
				ra = System.Math.Min(CoilAspect * rl, alongRoom);            // were 1.4x the N/S ones)
			}
			else
			{
				ra = System.Math.Max(System.Math.Min(CoilWide, alongRoom), MinCoilAlong);
				rl = System.Math.Min(CoilAspect * ra, latRoom);
			}
			double cA = foot >= 0
				? System.Math.Max(foot - ra, ra + CoilMargin)                // on the ground in front of the upright post, touching its foot
				: System.Math.Min(r.Attach + ra, SlackReach - ra);           // a far-forward attachment (Heavy): the coil reaches back beside it
			// N/S: drawn a little inboard of the rope, so a coil behind a raised leaf (half-width ~0.40) stays hidden (run _r2: "stray ears")
			double want = alongScreenVertical ? lat - 0.04 : lat;
			double cL = s * System.Math.Min(System.Math.Max(want, CoilMargin + rl), 0.5 - CoilMargin - rl);
			// start on the coil at the point facing the attachment point and wind inward (closing to 55 %, uneven: a loose coil of
			// rope, not a turned ring) between one and two turns, so the coil ends on its outer-back side; the loose end runs from
			// there straight out across the turns, away from the centre line and the deck (_r3 "no loose end", _r5 "end points at
			// the leaf": a rope still tied on)
			double t0 = System.Math.Atan2((r.Lateral - cL) / rl, (r.Attach - cA) / ra);
			double dir = s;   // +lateral rope winds clockwise in (along, lateral): away from the centre line first
			double tail = s * (System.Math.PI / 2 + (alongScreenVertical ? 0.6 : 0.0));   // E/W: straight out sideways, clear of the post
			double sweep = 2.0 * System.Math.PI + Mod(dir * (t0 - tail), 2.0 * System.Math.PI);
			var pts = new List<(double, double)> { (r.Attach, r.Lateral) };
			for (int i = 0; i <= n; i++)
			{
				double t = (double)i / n;
				double th = t0 - dir * t * sweep;
				double k = (1.0 - 0.45 * t) * (1.0 + CoilWobble * System.Math.Sin(5.0 * System.Math.PI * t));
				pts.Add((cA + k * ra * System.Math.Cos(th), cL + k * rl * System.Math.Sin(th)));
			}
			foreach (double k in new[] { 0.95, 1.3 })
			{
				double a = System.Math.Min(System.Math.Max(cA + k * ra * System.Math.Cos(tail), 0.02), System.Math.Min(SlackReach, cA + ra));
				double l = cL + k * rl * System.Math.Sin(tail);
				l = s * System.Math.Min(System.Math.Max(s * l, CoilMargin), 0.5 - CoilMargin);
				pts.Add((a, l));
			}
			return pts;
		}

		private static double Mod(double x, double m) => ((x % m) + m) % m;

		/// <summary>The rope's direction in the picture's UV space (v up): a styled north picture and the unstyled single
		/// picture point up, south down, east right.</summary>
		public static (double U, double V) TexDir(string facing)
		{
			switch (facing)
			{
				case "east": return (1, 0);
				case "south": return (0, -1);
				default: return (0, 1);   // north, single
			}
		}

		/// <summary>Rope frame → the picture's UV.</summary>
		public static (double U, double V) ToUV(string facing, double a, double l)
		{
			(double du, double dv) = TexDir(facing);
			double lu = -dv, lv = du;   // left of the rope direction
			return (0.5 + du * (a - 0.5) + lu * l, 0.5 + dv * (a - 0.5) + lv * l);
		}

		/// <summary>UV → world offset from the printed quad's centre (a 1×1 quad, as Graphic.Print prints it): mirrored when the
		/// print flips the UVs, then turned clockwise by the print angle (Printer_Plane.PrintPlane's own turn).</summary>
		public static (double X, double Z) UVToWorld(double u, double v, bool flip, double angleDeg)
		{
			double qx = flip ? 0.5 - u : u - 0.5, qz = v - 0.5;
			double r = angleDeg * System.Math.PI / 180.0, c = System.Math.Cos(r), s = System.Math.Sin(r);
			return (qx * c + qz * s, -qx * s + qz * c);
		}

		public static (double X, double Z) ToWorld(string facing, bool flip, double angleDeg, double a, double l)
		{
			(double u, double v) = ToUV(facing, a, l);
			return UVToWorld(u, v, flip, angleDeg);
		}

		/// <summary>The rotation angle (degrees, 0 = north, 90 = east) of a world direction.</summary>
		public static double AngleOf(double dx, double dz)
		{
			return System.Math.Atan2(dx, dz) * 180.0 / System.Math.PI;
		}
	}
}
