using System.Collections.Generic;
using System.Text;
using HarmonyLib;
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
	///   • Ruling #18 (owner card, 2026-10-11): both may be PLACED on a wet canal cell (RM_Patch_FlowDoorOnWetCanal).
	///     A blueprint or frame on a dry cut also survives the cut flooding (the same terrain verdict). The half-built
	///     frame is not a door: it seals nothing (SealsLiquid reads only a finished Building_RM_FlowDoor), so liquid runs
	///     through the frame cell until the door is finished; then a shut sluice seals it.
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

	/// <summary>Ruling #18: GenConstruct.CanBuildOnTerrain is the one terrain gate for placing a blueprint, for
	/// TerrainGrid.DoTerrainChangedEffects cancelling a blueprint or frame whose cell changed, and for spawning a building.
	/// A flow door on a dug cell holding liquid passes it (RM_PitTrapMath.FlowDoorStandsOn). Early-outs on every
	/// already-allowed call and every non-door def, so map generation pays one bool test.</summary>
	[HarmonyPatch(typeof(GenConstruct), nameof(GenConstruct.CanBuildOnTerrain))]
	[RimMandrake.Shared.PatchFeature("Sluices and grates stand on wet canal cells")]
	public static class RM_Patch_FlowDoorOnWetCanal
	{
		public static void Postfix(ref bool __result, BuildableDef entDef, IntVec3 c, Map map, Rot4 rot, Thing thingToIgnore)
		{
			if (__result || map == null || !(entDef is ThingDef td) || !RM_FlowDoorRules.IsFlowDoorDef(td))
			{
				return;
			}
			RM_MapComponent_Excavation eng = map.GetComponent<RM_MapComponent_Excavation>();
			if (eng == null)
			{
				return;
			}
			CellRect rect = GenAdj.OccupiedRect(c, rot, td.Size);
			foreach (IntVec3 cell in rect)
			{
				if (!cell.InBounds(map) || !RM_PitTrapMath.FlowDoorStandsOn(false, true, eng.ExcavatedDepthAt(cell), eng.FillAt(cell))
					|| HasTerrainOrder(cell, map, thingToIgnore))
				{
					return;
				}
			}
			__result = true;
		}

		/// <summary>Vanilla's other refusal on a cell: a floor blueprint or frame under the door. Left standing (only the
		/// missing Light on a wet cell is overridden).</summary>
		private static bool HasTerrainOrder(IntVec3 cell, Map map, Thing thingToIgnore)
		{
			List<Thing> things = cell.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i] != thingToIgnore && things[i].def.entityDefToBuild is TerrainDef)
				{
					return true;
				}
			}
			return false;
		}
	}

	public static class RM_FlowDoorRules
	{
		/// <summary>True for the sluice and the grate defs (their thingClass), blueprint and frame excluded.</summary>
		public static bool IsFlowDoorDef(ThingDef def)
		{
			return def?.thingClass != null && typeof(Building_RM_FlowDoor).IsAssignableFrom(def.thingClass);
		}

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

		/// <summary>The legacy flood walk's edifice verdict: a flow door that is not sealing, or a flow door's frame (ruling
		/// #18: the half-built frame seals nothing). Every other edifice holds liquid back.</summary>
		public static bool LetsLiquidThrough(Building edifice)
		{
			if (edifice is Frame frame)
			{
				return IsFlowDoorDef(frame.def.entityDefToBuild as ThingDef);
			}
			return IsFlowDoor(edifice) && !SealsLiquid(edifice);
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
