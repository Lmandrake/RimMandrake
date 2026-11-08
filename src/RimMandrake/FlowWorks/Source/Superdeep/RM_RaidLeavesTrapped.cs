using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_STORY_BUILD_LEFT_IN_THE_PIT (Artisan pass 6): his covered-pit story ends "The raiders are driven off, leaving some
	/// injured prisoners already in a tidy prison". The capture from the lip exists (RMFlow_CaptureDown, a right-click), but
	/// nothing told a player that the raiders standing in his pit as the raid withdrew were his to take. When a hostile raid's
	/// lord turns to leaving (flight, exit, kidnap or steal cover) with members still held in a pit, one message names them and
	/// points at the capture; it looks at them. Once per lord.
	/// </summary>
	[HarmonyPatch(typeof(Lord), nameof(Lord.GotoToil))]
	[RimMandrake.Shared.PatchFeature("A withdrawing raid's trapped are pointed out", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "superdeepCaptureEnabled")]
	public static class RM_Patch_RaidLeavesTrapped
	{
		private static readonly HashSet<int> told = new HashSet<int>();

		/// <summary>Messages sent since load (ProofThink-style reads).</summary>
		public static int Sent;

		public static bool Leaving(LordToil t)
		{
			return t is LordToil_PanicFlee || t is LordToil_ExitMap || t is LordToil_KidnapCover || t is LordToil_StealCover;
		}

		[HarmonyPostfix]
		public static void Postfix(Lord __instance, LordToil newLordToil)
		{
			if (!RimMandrakeFlowWorksSettings.superdeepCaptureEnabled || __instance?.Map == null || !Leaving(newLordToil)
				|| __instance.faction == null || !__instance.faction.HostileTo(Faction.OfPlayer) || told.Contains(__instance.loadID))
			{
				return;
			}
			List<Pawn> held = __instance.ownedPawns.Where(p => p != null && p.Spawned && !p.Dead && RM_SuperdeepTrap.IsHeld(p)).ToList();
			if (held.Count == 0)
			{
				return;
			}
			told.Add(__instance.loadID);
			Sent++;
			string names = held.Select(p => p.LabelShort).ToCommaList(useAnd: true);
			Messages.Message("RMFlow_RaidLeftTrapped".Translate(names), new LookTargets(held), MessageTypeDefOf.PositiveEvent);
		}
	}
}
