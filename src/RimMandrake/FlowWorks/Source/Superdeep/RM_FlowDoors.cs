using System.Collections.Generic;
using System.Text;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// FLOWWORKS_DOOR_FAMILY_1 — the owner's two stuffable canal doors (2026-09-17: "I'd be happy if
	/// we just had Sluice and SecurityGrateDoor and allowed them to be stuffably made too"). Stuff
	/// decides armour, hit points and whether it burns; nothing here hardcodes a material ladder.
	///
	///   • FLOWWORKS_SLUICE_TWO_DOORS_1 (owner 2026-10-06, typed): "There are sealed sluice gates
	///     (standard) and the ones made of metal grates that always allow liquid (this is just a gate,
	///     not a sluice gate then)." A SHUT sluice seals its cell: the depth engine moves no liquid into
	///     or out of it (RM_FlowKernel.sealedCell, fed by SealsLiquid) and the legacy flood walk refuses
	///     it. Open (a pawn passing, or held open) it passes. The grate passes liquid shut or open.
	///   • Neither opens for a pawn held in a superdeep pit (setting flowDoorsSealedFromPitEnabled):
	///     the pit spec §4 door rule, a grid fact now that the holder Thing is retired.
	///   • The sluice holds small creatures only. A humanlike, or anything too big for a one-wide
	///     pit (owner Q4, 2026-10-02: W = max(1, round(sqrt(BodySize))) — the same "small" the pit
	///     uses), forces it (setting sluiceLetsBigThroughEnabled). The grate holds a real prisoner
	///     exactly like a vanilla door: that is why it exists.
	/// The verdict is RM_PitTrapMath.FlowDoorOpens (Verse-free, covered by the C# selftest).
	/// </summary>
	public class RM_FlowDoorExtension : DefModExtension
	{
		/// <summary>True for the sluice: humanlikes and big creatures force it.</summary>
		public bool holdsSmallCreaturesOnly;
	}

	public class Building_RM_FlowDoor : Building_Door
	{
		public override bool PawnCanOpen(Pawn p)
		{
			return RM_FlowDoorRules.CanOpen(this, p, base.PawnCanOpen(p));
		}
	}

	public static class RM_FlowDoorRules
	{
		public static bool IsFlowDoor(Thing t)
		{
			return t is Building_RM_FlowDoor;
		}

		public static bool IsSluice(ThingDef def)
		{
			RM_FlowDoorExtension ext = def?.GetModExtension<RM_FlowDoorExtension>();
			return ext != null && ext.holdsSmallCreaturesOnly;
		}

		/// <summary>FLOWWORKS_SLUICE_TWO_DOORS_1: the verdict for the edifice on a cell — only a shut sluice
		/// holds liquid back. Pure on its two inputs so the selftest covers it (RM_PitTrapMath.FlowDoorSeals).</summary>
		public static bool SealsLiquid(Building edifice)
		{
			Building_RM_FlowDoor door = edifice as Building_RM_FlowDoor;
			return door != null && RM_PitTrapMath.FlowDoorSeals(IsSluice(door.def), door.Open);
		}

		public static bool CanOpen(Building_Door door, Pawn p, bool vanillaOpens)
		{
			if (p == null || door == null)
			{
				return false;
			}
			return RM_PitTrapMath.FlowDoorOpens(vanillaOpens,
				RM_SuperdeepTrap.IsHeld(p), RimMandrakeFlowWorksSettings.flowDoorsSealedFromPitEnabled,
				IsSluice(door.def), RimMandrakeFlowWorksSettings.sluiceLetsBigThroughEnabled,
				p.Faction != null && p.Faction == Faction.OfPlayer,
				p.RaceProps != null && p.RaceProps.Humanlike,
				RM_SuperdeepTrap.RequiredWidth(p));
		}

		private static Building_RM_FlowDoor DoorAt(Map map, IntVec3 c)
		{
			return map == null || !c.InBounds(map) ? null : c.GetEdifice(map) as Building_RM_FlowDoor;
		}

		/// <summary>Bridge proof (jawa/static_call): every pawn within 3 cells of the flow door at
		/// <paramref name="cell"/>, and whether the door would open for it.
		/// "DOOR RM_Sluice stuff WoodLog | Human123 OPEN held=False w=1 | Muffalo9 OPEN ..." (ThingIDs, as jawa/spawn_pawn returns them).</summary>
		public static string ProofOpen(Map map, IntVec3 cell)
		{
			Building_RM_FlowDoor door = DoorAt(map, cell);
			if (door == null)
			{
				return "REFUSED: no flow door at " + cell;
			}
			StringBuilder sb = new StringBuilder();
			sb.Append("DOOR ").Append(door.def.defName).Append(" stuff ").Append(door.Stuff?.defName ?? "none");
			foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
			{
				if (p.Position.DistanceTo(cell) > 3.01f)
				{
					continue;
				}
				sb.Append(" | ").Append(p.ThingID)
					.Append(door.PawnCanOpen(p) ? " OPEN" : " SHUT")
					.Append(" held=").Append(RM_SuperdeepTrap.IsHeld(p))
					.Append(" w=").Append(RM_SuperdeepTrap.RequiredWidth(p));
			}
			return sb.ToString();
		}

		/// <summary>Bridge proof (jawa/static_call): the liquid under a flow door — dug depth and
		/// fill F at the door cell, so a chain can show the level passing a CLOSED grate and stopping at a
		/// CLOSED sluice. "DOOR RM_SecurityGrateDoor open=False seals=False | depth 2 fill 1".</summary>
		public static string ProofLiquid(Map map, IntVec3 cell)
		{
			Building_RM_FlowDoor door = DoorAt(map, cell);
			if (door == null)
			{
				return "REFUSED: no flow door at " + cell;
			}
			RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
			int depth = eng == null ? 0 : eng.DepthAt(cell);
			int fill = eng == null ? 0 : eng.FillAt(cell);
			return "DOOR " + door.def.defName + " open=" + door.Open + " seals=" + SealsLiquid(door) +
				" | depth " + depth + " fill " + fill;
		}
	}
}
