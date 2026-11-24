using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>RIMMANDRAKE_ENACT_PIT_MELEE_REACH_EQUALS_CLIMB_SIZE_DECIDES (owner 2026-11-23): melee across a pit's edge works
	/// exactly when the attacker's body could take that step by the climb criterion
	/// (RM_PitTrapMath.BodyTakesStep, which the walked step asks too). Each body is read at the depth it
	/// stands at: on the floor under a deck or a lid, at the surface of water it swims in, on the ground over a trench a titan
	/// strides. Reach is the body's own (NaturalClimbLimitOf, a creature that flies, jumps or floats over walls, a ramp as
	/// sloping ground); a ladder and climbing gear change climbing and not reach (relative_depth_climb_design_2026-10-12.md
	/// §8.1 "Ladders and ramps are steps", §8.2 the climb limit is the body's height).</summary>
	public static class RM_PitReach
	{
		private static bool On(Pawn attacker, Thing target, out RM_MapComponent_Excavation eng)
		{
			eng = null;
			if (!RimMandrakeFlowWorksSettings.pitLipMeleeDeniedEnabled || !RM_SuperdeepTrap.RuleOn || attacker == null || target == null
				|| !attacker.Spawned || !target.Spawned || attacker.Map != target.Map)
			{
				return false;
			}
			eng = RM_SuperdeepTrap.EngineOf(attacker.Map);
			return RM_SuperdeepTrap.AnyHole(eng);
		}

		/// <summary>The depth (notches) a pawn's feet are at.</summary>
		public static int BodyDepth(Pawn p, RM_MapComponent_Excavation eng)
		{
			if (Pits.RM_PitCoverBeneath.IsBeneath(p))
			{
				return eng.ClimbDepthAt(p.Position);
			}
			return Pits.RM_SuspensionUnderpass.InFloorBand(p)
				? Pits.RM_SuspensionUnderpass.FloorViewDepthAt(p.Map, eng, p.Position)
				: RM_TrenchStride.StepDepthFor(p, p.Map, eng, p.Position);
		}

		/// <summary>The square of the target nearest the attacker: a pawn's own, a building's closest.</summary>
		private static IntVec3 CellOf(Pawn attacker, Thing target)
		{
			return target is Pawn || target.def.size == IntVec2.One ? target.Position
				: target.OccupiedRect().ClosestCellTo(attacker.Position);
		}

		private static int DepthOf(Thing target, IntVec3 at, RM_MapComponent_Excavation eng)
		{
			return target is Pawn p ? BodyDepth(p, eng) : RM_SuperdeepTrap.StepDepthAt(target.Map, eng, at);
		}

		/// <summary>Can this attacker's body reach the target from where it stands, as far as depth decides? Adjacency is vanilla's.
		/// A building standing down in a pit is not a question of reach (it stands up out of it): allowed, as before.</summary>
		public static bool Strikes(Pawn attacker, Thing target)
		{
			if (!On(attacker, target, out RM_MapComponent_Excavation eng))
			{
				return true;
			}
			Map map = attacker.Map;
			IntVec3 from = attacker.Position, to = CellOf(attacker, target);
			int a = BodyDepth(attacker, eng), t = DepthOf(target, to, eng);
			if (a == t || (t > a && !(target is Pawn)))
			{
				return true;
			}
			if (!RM_PocketGrid.Relative)
			{
				// the absolute rule: whoever the deeper square holds does not step out of it, so it neither strikes out nor in
				return !RM_PitTrapMath.StepBlocked(RM_SuperdeepTrap.IsHeldAt(attacker, a > t ? from : to), System.Math.Min(a, t));
			}
			if (!RM_CliffMask.On && !RM_SuperdeepTrap.Captures(attacker))
			{
				return true;    // the step rule does not hold this pawn (RelativeVeto's own gate): it climbs, so it reaches
			}
			bool diagonal = from.x != to.x && from.z != to.z;
			int ca = 0, cb = 0;
			if (diagonal)
			{
				ca = RM_TrenchStride.StepDepthFor(attacker, map, eng, new IntVec3(to.x, 0, from.z));
				cb = RM_TrenchStride.StepDepthFor(attacker, map, eng, new IntVec3(from.x, 0, to.z));
			}
			return RM_PitRoomMath.MeleeReaches(true, a, t, RM_PocketGrid.NaturalClimbLimitOf(attacker), diagonal, ca, cb,
				!diagonal && RM_ClimbJoins.RampJoins(map, eng, from, to, a, t),
				RM_PocketGrid.FreePitTraveller(attacker) || RM_SuperdeepTrap.InOwnPocketTooNarrow(attacker));
		}

		/// <summary>May a melee searcher pick this target (RM_PitRoomMath.MeleeTargetWorth)? A held raider does not walk the pit
		/// floor to stand under a colonist it can never hit, and nobody is sent to a rim to swing at air.</summary>
		public static bool WorthAttacking(Pawn attacker, Thing target)
		{
			if (!On(attacker, target, out RM_MapComponent_Excavation eng))
			{
				return true;
			}
			IntVec3 to = CellOf(attacker, target);
			int a = BodyDepth(attacker, eng), t = DepthOf(target, to, eng);
			if (a == t || (t > a && !(target is Pawn)))
			{
				return true;
			}
			if (!RM_PocketGrid.Relative)
			{
				return Strikes(attacker, target);
			}
			return RM_PitRoomMath.MeleeTargetWorth(attacker.Position.AdjacentTo8WayOrInside(to), Strikes(attacker, target),
				!RM_SuperdeepTrap.RelativeVeto(attacker.Map, attacker.Position, to, PathEndMode.OnCell, attacker));
		}

		public static bool CanWalkIn(Pawn attacker, Thing target)
		{
			// Check the floor itself because Touch accepts the rim the pawn is already standing on.
			return !RM_SuperdeepTrap.RelativeVeto(attacker.Map, attacker.Position, target.Position, PathEndMode.OnCell, attacker)
				&& attacker.CanReach(target, PathEndMode.OnCell, Danger.Deadly)
				&& RM_Patch_PathFollower_ReachWalker.As(attacker, () => attacker.Map.reachability.CanReach(attacker.Position,
					target, PathEndMode.OnCell, TraverseParms.For(TraverseMode.PassDoors)));
		}

		/// <summary>A pawn chasing this target stopped at a rim it cannot strike across, and a ramp, a ladder or an easier step
		/// leads to the target's floor: walk on, onto the target's own square (vanilla's chase stops at the first touch).</summary>
		public static void WalkIn(Pawn attacker, Thing target)
		{
			Job job = attacker?.CurJob;
			if (job == null || job.targetA.Thing != target || job.targetB.IsValid || attacker.pather == null || attacker.pather.Moving
				|| (job.def != JobDefOf.AttackMelee && job.def != JobDefOf.PredatorHunt) || !(target is Pawn))
			{
				return;
			}
			if (!CanWalkIn(attacker, target))
			{
				if (job.def == JobDefOf.AttackMelee)
				{
					if (job.playerForced && attacker.Faction == Faction.OfPlayer)
					{
						Messages.Message("NoPath".Translate(), attacker, MessageTypeDefOf.RejectInput, false);
					}
					attacker.jobs.EndCurrentJob(JobCondition.Incompletable);
				}
				return;
			}
			attacker.pather.StartPath(target, PathEndMode.OnCell);
		}

		/// <summary>Bridge/proof read: "MELEE strikes=b worth=b aDepth=n tDepth=n k=n size=f adjacent=b".</summary>
		public static string Proof(Pawn attacker, Pawn target)
		{
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(attacker.Map);
			return "MELEE strikes=" + Strikes(attacker, target) + " worth=" + WorthAttacking(attacker, target)
				+ " aDepth=" + (eng == null ? 0 : BodyDepth(attacker, eng)) + " tDepth=" + (eng == null ? 0 : BodyDepth(target, eng))
				+ " k=" + RM_PocketGrid.NaturalClimbLimitOf(attacker)
				+ " size=" + attacker.BodySize.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture)
				+ " adjacent=" + attacker.Position.AdjacentTo8WayOrInside(target.Position);
		}
	}

	[HarmonyPatch(typeof(FloatMenuUtility), nameof(FloatMenuUtility.GetMeleeAttackAction))]
	[RimMandrake.Shared.PatchFeature("Melee across a pit's edge needs reach", typeof(RimMandrakeFlowWorksSettings), "pitLipMeleeDeniedEnabled")]
	public static class RM_Patch_OrderedMelee_PitLip
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn pawn, LocalTargetInfo target, ref string failStr, ref System.Action __result)
		{
			if (__result != null && target.Thing is Pawn && pawn.Position.AdjacentTo8WayOrInside(target.Cell)
				&& !RM_PitReach.Strikes(pawn, target.Thing) && !RM_PitReach.CanWalkIn(pawn, target.Thing))
			{
				failStr = "NoPath".Translate();
				__result = null;
			}
		}
	}

	/// <summary>Pawn_MeleeVerbs.TryMeleeAttack is the one door every hand attack goes through: the AttackMelee job, a predator's
	/// hunt, vanilla Wait's auto-attack on the 8 squares around a pawn, and a drafted colonist's order.</summary>
	[HarmonyPatch(typeof(Pawn_MeleeVerbs), nameof(Pawn_MeleeVerbs.TryMeleeAttack))]
	[RimMandrake.Shared.PatchFeature("Melee across a pit's edge needs reach", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitLipMeleeDeniedEnabled")]
	public static class RM_Patch_MeleeVerbs_PitLip
	{
		[HarmonyPrefix]
		public static bool Prefix(Pawn_MeleeVerbs __instance, Thing target, ref bool __result)
		{
			if (!RimMandrakeFlowWorksSettings.pitLipMeleeDeniedEnabled || target == null || RM_PitReach.Strikes(__instance.Pawn, target))
			{
				return true;
			}
			RM_PitReach.WalkIn(__instance.Pawn, target);
			__result = false;
			return false;
		}
	}

	/// <summary>The AI half: a melee searcher picks no target it can neither strike nor walk to (RM_PitReach.WorthAttacking).</summary>
	[HarmonyPatch(typeof(AttackTargetFinder), nameof(AttackTargetFinder.BestAttackTarget))]
	[RimMandrake.Shared.PatchFeature("Melee across a pit's edge needs reach", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "pitLipMeleeDeniedEnabled")]
	public static class RM_Patch_AttackTargetFinder_PitLipMelee
	{
		[HarmonyPrefix]
		public static void Prefix(IAttackTargetSearcher searcher, ref System.Predicate<Thing> validator)
		{
			if (!RimMandrakeFlowWorksSettings.pitLipMeleeDeniedEnabled || searcher == null)
			{
				return;
			}
			Pawn p = searcher.Thing as Pawn;
			Verb verb = searcher.CurrentEffectiveVerb;
			if (p == null || !p.Spawned || verb == null || !verb.IsMeleeAttack)
			{
				return;
			}
			Wrap(p, ref validator);
		}

		// a separate method, so the closure is built only for a melee searcher
		private static void Wrap(Pawn p, ref System.Predicate<Thing> validator)
		{
			System.Predicate<Thing> inner = validator;
			validator = t => (inner == null || inner(t)) && (t == null || RM_PitReach.WorthAttacking(p, t));
		}
	}
}
