using System;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT (plan P5) and DIG_COST_TUNE_DEEP_IS_A_MEGAPROJECT (plan P6): how deep a colonist may
	/// dig and what each cut costs. Owner R5 (2026-10-17, by card): <i>a setting from 2 to 20 m; the 0.5 m dig step stays;
	/// lakes keep their own floors.</i> DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL (owner card 2026-10-21): colonists 2 m by
	/// default, machine labour (mechanoids, droids) deeper, to its own cap (default 20 m). V1 (default, veto-able): keep today's curve, 3,200 × the
	/// notch being cut.
	///
	/// Three numbers that used to be one (the old <c>MaxDepth = Superdeep = 4</c> of RM_ExcavationDepth) and are now separate:
	///   • <see cref="PitDepth"/> (4 notches = 2 m): the ABSOLUTE "pit" the T0 rules still read (rooms, spikes, shooting,
	///     exposure, the OFF-branch trap). P7 (PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE) makes those relative; nothing here may
	///     add a new reader of it.
	///   • the dig CAPS (Mod Settings, <see cref="MinMaxDigDepth"/>..<see cref="MaxDigCeiling"/>): the colonist cap
	///     (<see cref="DefaultMaxDigDepth"/> 4 = 2 m) and the machine cap (<see cref="DefaultMachineDigDepth"/> 40 = 20 m);
	///     <see cref="CapFor"/> picks one digger's, <see cref="DesignationCap"/> the deepest anyone may go. Lowering it never shallows a cell already dug.
	///   • <see cref="MaxDigCeiling"/> (40 = 20 m): the deepest any dug square can legitimately be; the load repair clamps
	///     to it, never to the setting.
	/// Lake floors are none of these (RM_BedMath, to 125 m).
	///
	/// ⛔ Verse-free: compiled into Source/SelfTest/ as the production file.
	/// </summary>
	public static class RM_DigDepthMath
	{
		/// <summary>The absolute pit (2 m). Equal to <c>RM_ExcavationDepth.Superdeep</c>; NOT the dig cap.</summary>
		public const int PitDepth = 4;

		/// <summary>The lowest the cap setting goes: 2 m (today's dig, T0).</summary>
		public const int MinMaxDigDepth = 4;

		/// <summary>DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL (owner card 2026-10-21, "Colonists 2 m, machines deeper"): the default
		/// COLONIST cap, 2 m (was R5's 8 m).</summary>
		public const int DefaultMaxDigDepth = 4;

		/// <summary>DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL: the default MACHINE cap (mechanoids, droids), 20 m (the ceiling).</summary>
		public const int DefaultMachineDigDepth = 40;

		/// <summary>Owner R5: the highest the cap setting goes, 20 m. Also the deepest a dug square may hold on load.</summary>
		public const int MaxDigCeiling = 40;

		/// <summary>Base work for one notch (0.5 m). Unchanged from the shipped single-level value.</summary>
		public const int WorkPerNotch = 3200;

		/// <summary>vanilla JobDriver_AffectFloor: work done per tick = 1.7 × the speed stat (RimSage,
		/// RimWorld/JobDriver_AffectFloor.cs). Used only to state digger-days.</summary>
		public const float WorkPerTickAtSpeedOne = 1.7f;

		public const int TicksPerDay = 60000;

		/// <summary>The cap setting (a float slider in notches) as notches, rounded, held to 4..40.</summary>
		public static int ClampCap(float notches)
		{
			if (float.IsNaN(notches))
			{
				return DefaultMaxDigDepth;
			}
			int n = (int)Math.Round(notches, MidpointRounding.AwayFromZero);
			return n < MinMaxDigDepth ? MinMaxDigDepth : (n > MaxDigCeiling ? MaxDigCeiling : n);
		}

		/// <summary>P6, V1: the work to cut notch <paramref name="notch"/> (1-based: the first 0.5 m is notch 1). With the
		/// curve on, 3,200 × the notch (each half-metre deeper is further to throw the spoil). Off (V1's other option, a
		/// setting): flat past 2 m, every notch below 2 m costs what the 2 m notch costs (12,800).</summary>
		public static int WorkToCut(int notch, bool costRisesWithDepth = true)
		{
			int n = notch < 1 ? 1 : (notch > MaxDigCeiling ? MaxDigCeiling : notch);
			if (!costRisesWithDepth && n > PitDepth)
			{
				n = PitDepth;
			}
			return WorkPerNotch * n;
		}

		/// <summary>Total work to take one square from <paramref name="fromDepth"/> to <paramref name="toDepth"/> notches.</summary>
		public static long WorkToDig(int fromDepth, int toDepth, bool costRisesWithDepth = true)
		{
			long w = 0;
			for (int n = Math.Max(0, fromDepth) + 1; n <= toDepth; n++)
			{
				w += WorkToCut(n, costRisesWithDepth);
			}
			return w;
		}

		/// <summary>Digger-days for an amount of work at a mining speed (vanilla's 1.7 work a tick at speed 1).</summary>
		public static double DiggerDays(long work, float miningSpeed = 1f)
		{
			float s = miningSpeed > 0f ? miningSpeed : 1f;
			return work / (WorkPerTickAtSpeedOne * s * TicksPerDay);
		}

		/// <summary>May a square now at <paramref name="depth"/> be cut one notch deeper under cap <paramref name="cap"/>?</summary>
		public static bool MayDeepen(int depth, int cap)
		{
			return depth < cap && depth < MaxDigCeiling;
		}

		/// <summary>DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL: one digger's cap. Machine labour (with machine digging on) digs to the
		/// machine cap but never shallower than a colonist; everyone else to the colonist cap.</summary>
		public static int CapFor(bool isMachine, int colonistCap, bool machineDigOn, int machineCap)
		{
			return isMachine && machineDigOn && machineCap > colonistCap ? machineCap : colonistCap;
		}

		/// <summary>The deepest ANYONE may dig now: what a designation, a dig-to target and the stale test are held to. A 2 m
		/// square ordered to 6 m is valid work, only not for a colonist.</summary>
		public static int DesignationCap(int colonistCap, bool machineDigOn, int machineCap)
		{
			return CapFor(true, colonistCap, machineDigOn, machineCap);
		}

		/// <summary>DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL (night fixer 2026-10-22: "an order should never vanish silently"): the
		/// deepest a standing ORDER may stay valid to: the machine cap whether or not machine digging is on now. With machines
		/// off an order past the colonist cap WAITS (alert, right-click reason) instead of being deleted by the work giver;
		/// a NEW order is still held to <see cref="DesignationCap"/> at placement.</summary>
		public static int OrderCap(int colonistCap, int machineCap)
		{
			return CapFor(true, colonistCap, true, machineCap);
		}

		/// <summary>"Dig to N m": the target held to 1..cap (a target past the cap digs to the cap).</summary>
		public static int ClampTarget(int target, int cap)
		{
			int c = cap < 1 ? 1 : (cap > MaxDigCeiling ? MaxDigCeiling : cap);
			return target < 1 ? 1 : (target > c ? c : target);
		}

		/// <summary>Is there work left on a square at <paramref name="depth"/> with a dig-to target (0 = none: one notch)?</summary>
		public static bool DigToOwesWork(int depth, int target, int cap)
		{
			return target > 0 && depth < ClampTarget(target, cap) && MayDeepen(depth, cap);
		}

		/// <summary>The load repair (EXCAVATION_LOAD_SANITY_REPAIR_1) clamps dug depth to this, never to the setting: lowering
		/// the cap never shallows a dug cell.</summary>
		public static byte RepairCeiling => (byte)MaxDigCeiling;
	}
}
