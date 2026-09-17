using System.Collections.Generic;
using RimMandrake.FlowWorks.Pits;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RULING 26 — <i>"SUPERDEEP captures as if dry; shallower is wadeable."</i>
	/// Fill does not decide whether a pawn falls in; D does, and only D = 4 does.
	///
	/// 🔑 THIS CLASS WRITES NO CAPTURE AND NO ESCAPE SYSTEM, which is the whole
	/// point of doing it here rather than in the engine. Everything below the
	/// waterline is inherited from <see cref="Building_OpenPit"/>, merged in with
	/// Pits on 2026-09-16:
	///   • capture       — <c>Spring(List&lt;Pawn&gt;)</c>: fall damage, the
	///                     RM_PinnedInPit hediff, DeSpawn into innerContainer,
	///                     and the fitting's OnCapture.
	///   • holding       — innerContainer + <c>Tick</c>'s <c>DoTick</c>, so a held
	///                     pawn's needs and hediffs still advance.
	///   • escape        — <c>RunStruggleInterval</c> and PitEscapeUtility's
	///                     struggle clock, scored off bodysize / health /
	///                     manipulation.
	///   • release       — the Release gizmo and <c>EjectPawn</c>.
	///   • destruction   — <c>Destroy</c> drops occupants rather than voiding them.
	/// What is genuinely new here is a DETECTOR and a GATE, and nothing else.
	///
	/// THE DETECTOR is vanilla's own, copied in shape from
	/// RimWorld/Building_Trap.cs:77-100 (MEASURED 2026-09-16): keep a list of
	/// pawns currently touching the cell, act on the transition into it, and
	/// prune the list when they leave or stop being spawned. Per-tick, exactly as
	/// every vanilla trap is — pillar 2's "no per-tick simulation" is about the
	/// flow engine, and this is a trap, not a fluid.
	///
	/// 🔴 WHY THE OWN-FACTION CARVE-OUT EXISTS. It is not invented here: it is
	/// the rule CompPitCoverTrigger already ships, with its reason recorded in
	/// place — <i>"A trap that captures its own colony is not the intended raider
	/// trap use case."</i> Without it nobody could ever build the ladder that
	/// makes the hole exitable, because the builder would fall in on the way.
	/// It is a Mod Setting, so the harsher reading is one click away.
	/// </summary>
	public class Building_SuperdeepPit : Building_OpenPit
	{
		/// <summary>DERIVED, never scribed. On load a pawn standing in the cell is
		/// simply detected again on the next tick and captured, which is the right
		/// outcome; scribing this would instead resurrect a reference to a pawn
		/// that may no longer exist.</summary>
		private readonly List<Pawn> touchingPawns = new List<Pawn>();

		/// <summary>LADDERS — the jailer mechanic, and one boolean.
		///
		/// 🔑 UNIFIED WITH THE PRISONER PIT CELL, not duplicated. Building_PitCell
		/// already expresses "you are held because a thing above you is shut" by
		/// overriding <see cref="Building_OpenPit.EscapeBlocked"/> with its gate
		/// state. A missing ladder is the same sentence with a different subject,
		/// so it is the same override — remove the ladder and whatever is down
		/// there is stranded, exactly as a closed gate strands a captive.</summary>
		protected override bool EscapeBlocked
		{
			get
			{
				if (!RimMandrakeFlowWorksSettings.ladderRequiredToExitEnabled)
				{
					return false;
				}
				return !RM_LadderUtility.HasLadder(Map, Position);
			}
		}

		/// <summary>A ladder beats the liquid. Without this, a fitting that blocks
		/// escape (deep water, tar) would hold a pawn in a cell that visibly has a
		/// ladder in it — the mechanic would read as broken rather than as depth.
		/// Shipped behaviour for every other pit is unchanged: the base returns
		/// false and the fitting's own block stands.</summary>
		protected override bool EscapeAssisted =>
			RimMandrakeFlowWorksSettings.ladderRequiredToExitEnabled
			&& RM_LadderUtility.HasLadder(Map, Position);

		protected override void Tick()
		{
			base.Tick();
			if (!Spawned || !RimMandrakeFlowWorksSettings.superdeepCaptureEnabled)
			{
				return;
			}
			ScanForFallers();
		}

		/// <summary>Building_Trap.Tick's shape, with the roll replaced by ruling
		/// 26: there is no SpringChance here, because a four-level hole is not a
		/// concealed trap that might be spotted. Entering one takes you.</summary>
		private void ScanForFallers()
		{
			Map map = Map;
			if (map == null)
			{
				return;
			}
			List<Thing> thingList = Position.GetThingList(map);
			List<Pawn> fallers = null;
			for (int i = 0; i < thingList.Count; i++)
			{
				if (!(thingList[i] is Pawn pawn) || pawn.Dead || pawn.Flying)
				{
					continue;
				}
				if (touchingPawns.Contains(pawn))
				{
					continue;
				}
				touchingPawns.Add(pawn);
				if (!CapturesFaction(pawn))
				{
					continue;
				}
				if (fallers == null)
				{
					fallers = new List<Pawn>();
				}
				fallers.Add(pawn);
			}
			for (int i = touchingPawns.Count - 1; i >= 0; i--)
			{
				Pawn p = touchingPawns[i];
				if (p == null || !p.Spawned || p.Flying || p.Position != Position)
				{
					touchingPawns.RemoveAt(i);
				}
			}
			if (fallers != null)
			{
				Spring(fallers);
			}
		}

		private bool CapturesFaction(Pawn p)
		{
			if (RimMandrakeFlowWorksSettings.superdeepCapturesOwnFaction)
			{
				return true;
			}
			return p.Faction != Faction;
		}

		public override string GetInspectString()
		{
			string result = base.GetInspectString();
			if (RimMandrakeFlowWorksSettings.ladderRequiredToExitEnabled)
			{
				string ladder = RM_LadderUtility.HasLadder(Map, Position)
					? "RMFlow_SuperdeepLadderPresent".Translate()
					: "RMFlow_SuperdeepNoLadder".Translate();
				result = result.NullOrEmpty() ? ladder : result + "\n" + ladder;
			}
			return result;
		}
	}
}
