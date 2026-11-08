using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_STORY_FIX_MELEE_ACROSS_THE_LIP (Artisan pass 6, 2026-11-08, his covered-pit story on game A). Three runs showed a
	/// pawn at the foot of a sheer wall fighting things standing on top of it:
	/// - s5b and s6: a raider who fell into the 2 m story pit bashed the passage wall on the rim from the pit floor for 1,700+
	///   ticks (AttackMelee@Wall).
	/// - s7: a raider in the pit (118,120) took AttackMelee on an archer standing on the north lip (118,121), and the drafted
	///   archers above executed him point blank before any rescuer came. His story leaves "injured prisoners", not corpses.
	///
	/// WHY: melee needs only adjacency (Touch), and two squares either side of a pit's lip ARE adjacent. The shooting rule
	/// (RM_SuperdeepShooting.RuleAppliesTo) waves melee through on purpose; vanilla's auto-targeting treats a trapped raider as
	/// a live threat like any other.
	///
	/// THE RULE: no melee swing, trash job or blocker-bash between two squares a cliff apart (the shooting rule's cliff, 2 m
	/// shipped), either way. And a pawn HELD in a pit (RM_SuperdeepTrap.IsHeld: it cannot climb out) is no auto-target threat
	/// to a searcher a cliff above it unless it has engaged a target in the last 360 ticks (vanilla's own window for roamers,
	/// Pawn.ThreatDisabledBecauseNonAggressiveRoamer). So drafted defenders on the lip shoot the raiders still on their feet,
	/// a trapped archer who shoots up is shot back, and an explicit attack order on a captive still works.
	/// </summary>
	public static class RM_CliffMelee
	{
		/// <summary>Threat checks this rule turned off since load (ProofThink-style reads).</summary>
		public static int ThreatsDisabled;

		/// <summary>Melee, trash and bash jobs this rule refused since load.</summary>
		public static int Refused;

		/// <summary>Live read (jawa/static_call): the two counters.</summary>
		public static string ProofCliffMelee(string arg) => "CLIFFMELEE refused=" + Refused + " threatsDisabled=" + ThreatsDisabled;

		/// <summary>TRUE when squares a and b are a cliff apart on this map (one end at least a cliff deeper than the other).</summary>
		public static bool Across(Map map, IntVec3 a, IntVec3 b)
		{
			if (map == null || !RimMandrakeFlowWorksSettings.reachSeesWallsAndCliffs)
			{
				return false;
			}
			RM_MapComponent_Excavation engine = RM_SuperdeepShooting.EngineFor(map);
			if (engine == null || engine.ClimbCellCount == 0)
			{
				return false;
			}
			int da = RM_SuperdeepShooting.ShotDepthAt(map, engine, a.x, a.z);
			int db = RM_SuperdeepShooting.ShotDepthAt(map, engine, b.x, b.z);
			int d = da > db ? da - db : db - da;
			return d >= RM_SuperdeepShooting.CliffNotches;
		}

		/// <summary>TRUE when the pawn cannot swing at the thing: the nearest square of the thing is a cliff from the pawn's.</summary>
		public static bool Across(Pawn p, Thing t)
		{
			if (p == null || t == null || !p.Spawned || !t.Spawned || p.Map != t.Map)
			{
				return false;
			}
			IntVec3 c = t.def.size.x * t.def.size.z > 1 ? t.OccupiedRect().ClosestCellTo(p.Position) : t.Position;
			return Across(p.Map, p.Position, c);
		}
	}

	/// <summary>Also PIT_COVER_FIX_RAIDERS_TRASH_THE_HIDDEN_COVER: in s6 a tribal raid walked in from the map edge 55 squares off
	/// already set on bashing and torching the concealed cover (AttackMelee@ and Ignite@RM_PitCover_WovenScrap, t+600), because
	/// JobGiver_AITrashBuildingsDistant takes it for any building. A raider never trashes a cover that has not given way: to
	/// him it is ground. (Pass 5 tried isTrap on the defs; vanilla refuses that on a non-edifice: "isTrap but is not edifice.
	/// Code will break.")</summary>
	[HarmonyPatch(typeof(TrashUtility), nameof(TrashUtility.ShouldTrashBuilding), new[] { typeof(Pawn), typeof(Building), typeof(bool) })]
	[RimMandrake.Shared.PatchFeature("No melee across a pit's lip", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "reachSeesWallsAndCliffs")]
	public static class RM_Patch_TrashBuilding_CliffMelee
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn pawn, Building b, ref bool __result)
		{
			if (__result && ((b is Pits.Building_PitCover cover && !cover.Sprung) || RM_CliffMelee.Across(pawn, b)))
			{
				__result = false;
				RM_CliffMelee.Refused++;
			}
		}
	}

	[HarmonyPatch(typeof(TrashUtility), nameof(TrashUtility.ShouldTrashPlant), new[] { typeof(Pawn), typeof(Plant) })]
	[RimMandrake.Shared.PatchFeature("No melee across a pit's lip", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "reachSeesWallsAndCliffs")]
	public static class RM_Patch_TrashPlant_CliffMelee
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn pawn, Plant p, ref bool __result)
		{
			if (__result && RM_CliffMelee.Across(pawn, p))
			{
				__result = false;
				RM_CliffMelee.Refused++;
			}
		}
	}

	/// <summary>The sapper's, the exit's and the revenant's "bash what blocks my path": refused when the blocker stands a cliff
	/// from the square the pawn would swing from (the pather's route through a wall from a pit floor).</summary>
	[HarmonyPatch(typeof(DigUtility), nameof(DigUtility.PassBlockerJob))]
	[RimMandrake.Shared.PatchFeature("No melee across a pit's lip", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "reachSeesWallsAndCliffs")]
	public static class RM_Patch_PassBlockerJob_CliffMelee
	{
		[HarmonyPrefix]
		public static bool Prefix(Pawn pawn, Thing blocker, IntVec3 cellBeforeBlocker, ref Job __result)
		{
			if (pawn?.Map == null || blocker == null || !blocker.Spawned)
			{
				return true;
			}
			IntVec3 from = cellBeforeBlocker.IsValid ? cellBeforeBlocker : pawn.Position;
			IntVec3 to = blocker.def.size.x * blocker.def.size.z > 1 ? blocker.OccupiedRect().ClosestCellTo(from) : blocker.Position;
			if (!RM_CliffMelee.Across(pawn.Map, from, to))
			{
				return true;
			}
			__result = null;
			RM_CliffMelee.Refused++;
			return false;
		}
	}

	/// <summary>A trapped occupant is no auto-target threat to a searcher a cliff above it until it engages someone.</summary>
	[HarmonyPatch(typeof(Pawn), nameof(Pawn.ThreatDisabled))]
	[RimMandrake.Shared.PatchFeature("Trapped raiders are not auto-targets", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "reachSeesWallsAndCliffs")]
	public static class RM_Patch_ThreatDisabled_HeldInPit
	{
		/// <summary>Vanilla's window after an engagement in which a roamer stays a threat (Pawn.ThreatDisabledBecauseNonAggressiveRoamer).</summary>
		public const int EngageWindowTicks = 360;

		[HarmonyPostfix]
		public static void Postfix(Pawn __instance, IAttackTargetSearcher disabledFor, ref bool __result)
		{
			if (__result || !(disabledFor?.Thing is Pawn s) || s.Map != __instance.Map || !__instance.Spawned)
			{
				return;
			}
			if (__instance.mindState != null && Find.TickManager.TicksGame < __instance.mindState.lastEngageTargetTick + EngageWindowTicks)
			{
				return;
			}
			if (!RM_CliffMelee.Across(__instance.Map, __instance.Position, s.Position) || !RM_SuperdeepTrap.IsHeld(__instance))
			{
				return;
			}
			__result = true;
			RM_CliffMelee.ThreatsDisabled++;
		}
	}
}
