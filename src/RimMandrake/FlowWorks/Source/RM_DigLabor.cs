using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL (owner card 2026-10-21, "Colonists 2 m, machines deeper"): opt a race or a flesh
	/// type into machine labour. FlowWorks names no franchise def: a droid mod adds this to its own FleshTypeDef (or race
	/// ThingDef) with a patch guarded by PatchOperationFindMod on FlowWorks (an unguarded extension whose type is missing
	/// discards the whole def). Design: design/RimMandrake/machine_dig_2026-10-21.md §2.
	/// </summary>
	public class RM_MachineDigger : DefModExtension
	{
	}

	/// <summary>
	/// Who digs how deep. Machine labour = a mechanoid (RaceProps.IsMechanoid: every colony mech) or a race / flesh type
	/// carrying <see cref="RM_MachineDigger"/>; which defs that is today: design/RimMandrake/machine_dig_2026-10-21.md §2.
	/// Ownership is not asked here: only colony pawns scan work. The ridable digging rig (owed, design §7) will add a
	/// cell-aware overload.
	/// </summary>
	public static class RM_DigLabor
	{
		public static bool IsMachineLabour(Pawn pawn)
		{
			RaceProperties race = pawn?.RaceProps;
			if (race == null)
			{
				return false;
			}
			if (race.IsMechanoid)
			{
				return true;
			}
			return pawn.def.HasModExtension<RM_MachineDigger>()
				|| (race.FleshType != null && race.FleshType.HasModExtension<RM_MachineDigger>());
		}

		/// <summary>How deep this pawn may cut, in notches (colonist cap, or the machine cap for machine labour).</summary>
		public static int CapFor(Pawn pawn)
		{
			return RM_DigDepthMath.CapFor(IsMachineLabour(pawn), RimMandrakeFlowWorksSettings.MaxDigDepth,
				RimMandrakeFlowWorksSettings.machineDigEnabled, RimMandrakeFlowWorksSettings.MaxMachineDigDepth);
		}

		/// <summary>The deepest anyone may dig now: designations, dig-to targets and the stale test are held to this.</summary>
		public static int DesignationCap => RM_DigDepthMath.DesignationCap(RimMandrakeFlowWorksSettings.MaxDigDepth,
			RimMandrakeFlowWorksSettings.machineDigEnabled, RimMandrakeFlowWorksSettings.MaxMachineDigDepth);

		/// <summary>Why <paramref name="pawn"/> may not cut below <paramref name="depth"/> notches when someone else could, or
		/// null. Text from the effective limits (never "2 m" when the colonist cap is set elsewhere).</summary>
		public static string RefusalFor(Pawn pawn, int depth)
		{
			int mine = CapFor(pawn);
			if (RM_DigDepthMath.MayDeepen(depth, mine))
			{
				return null;
			}
			return "Colonists dig to " + RM_Volume.FormatFloorMetres(mine) + "; deeper needs machine labour (a mechanoid or a droid).";
		}
	}
}
