using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>One part the drawbridge drag places besides its deck and anchors: a winch house (one per leaf) or a gate (one
	/// per lane at each hinge bank).</summary>
	public struct DrawbridgePart
	{
		public ThingDef def;
		public IntVec3 cell;
		public Rot4 rot;
		public ThingDef stuff;
		/// <summary>The leaf (index into the record's leaves) a winch is planned for; -1 for a gate.</summary>
		public int leaf;
	}

	/// <summary>
	/// DRAWBRIDGE_BUILD_ONE_DRAG_DOES_IT_ALL (owner ruling 2026-10-25, "Drawbridges: A: one drag"): the parts of a drawbridge
	/// that used to be placed by hand and linked only by touching. The drag plans them with the deck (PlanParts), places their
	/// blueprints with it (PlaceParts), and records each winch's square on its leaf (DrawbridgeLeaf.plannedWinch), which is the
	/// link LinkWinch honours first. The winch house and gate have no Architect button of their own any more
	/// (canGenerateDefaultDesignator false); a leaf without its winch offers "Place winch house" (WinchGizmo). Geometry is
	/// RM_DrawbridgePackageMath's (pure, SelfTest DrawbridgeChecks).
	/// </summary>
	public static class RM_DrawbridgePackage
	{
		public static ThingDef WinchDef(SuspensionTier t)
		{
			return t == SuspensionTier.Steel ? RM_DrawbridgeDefOf.RM_DrawbridgeWinch_Steel : RM_DrawbridgeDefOf.RM_DrawbridgeWinch_Timber;
		}

		/// <summary>Winch and gate face across the moat from their hinge bank, as that bank's anchor does.</summary>
		public static Rot4 PartRot(SuspensionBridgeRecord r, DrawbridgeLeaf l)
		{
			return l.hingeAtFirst ? r.dir : r.dir.Opposite;
		}

		/// <summary>The gate's material: the bridge's own when a gate may be made of it, else wood (timber) or steel.</summary>
		public static ThingDef GateStuff(SuspensionBridgeRecord r)
		{
			ThingDef gate = RM_DrawbridgeDefOf.RM_DrawbridgeGate;
			if (r.stuff != null && GenStuff.AllowedStuffsFor(gate).Contains(r.stuff))
			{
				return r.stuff;
			}
			return r.tier == SuspensionTier.Steel ? ThingDefOf.Steel : ThingDefOf.WoodLog;
		}

		private static bool Placeable(Map map, ThingDef d, IntVec3 c, Rot4 rot, ThingDef stuff, out string why)
		{
			why = null;
			if (!c.InBounds(map))
			{
				why = "off the map";
				return false;
			}
			AcceptanceReport ok = GenConstruct.CanPlaceBlueprintAt(d, c, rot, map, false, null, null, d.MadeFromStuff ? stuff : null);
			if (!ok.Accepted)
			{
				why = ok.Reason.NullOrEmpty() ? "cannot be placed there" : ok.Reason;
			}
			return ok.Accepted;
		}

		/// <summary>The square this leaf's winch house goes on: the preferred side of its hinge anchor, else the other side;
		/// Invalid (with why) when neither takes a blueprint.</summary>
		public static IntVec3 WinchSpot(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l, bool otherSide, out string why)
		{
			why = null;
			ThingDef d = WinchDef(r.tier);
			int hinge = RM_DrawbridgePackageMath.HingeAnchorIndex(l.Span);
			IntVec3 c0 = r.Cell(0, hinge);
			foreach (bool side in new[] { otherSide, !otherSide })
			{
				IntVec3 c = r.Cell(RM_DrawbridgePackageMath.WinchLane(r.width, side), hinge);
				if (Placeable(map, d, c, PartRot(r, l), null, out string w))
				{
					return c;
				}
				why = why ?? w;
			}
			why = "no room for the winch house on either side of the hinge anchor at " + c0 + " (" + why + ")";
			return IntVec3.Invalid;
		}

		/// <summary>Plan every part of the leaves the drag just cut (the record is planned, not yet registered). A winch that
		/// fits on neither side refuses the drag; a gate square that will not take a gate is skipped (gates are optional; the
		/// count goes in skippedGates). Sets each leaf's plannedWinch. False with why when the drag must be refused.</summary>
		public static bool PlanParts(Map map, SuspensionBridgeRecord r, bool otherSide, bool gates, List<DrawbridgePart> parts,
			out int skippedGates, out string why)
		{
			why = null;
			skippedGates = 0;
			parts.Clear();
			if (map == null || r == null || !r.IsDrawbridge)
			{
				why = "not a drawbridge";
				return false;
			}
			ThingDef winch = WinchDef(r.tier);
			if (!winch.IsResearchFinished && !DebugSettings.godMode)  // god mode places the unresearched, as vanilla's does
			{
				why = "the " + winch.label + " needs research first ("
					+ string.Join(", ", winch.researchPrerequisites?.Select(x => x.LabelCap.ToString()) ?? Enumerable.Empty<string>()) + ")";
				return false;
			}
			ThingDef gate = RM_DrawbridgeDefOf.RM_DrawbridgeGate;
			ThingDef gateStuff = GateStuff(r);
			for (int k = 0; k < r.leaves.Count; k++)
			{
				DrawbridgeLeaf l = r.leaves[k];
				IntVec3 w = WinchSpot(map, r, l, otherSide, out string wwhy);
				if (!w.IsValid)
				{
					why = wwhy;
					return false;
				}
				l.plannedWinch = w;
				parts.Add(new DrawbridgePart { def = winch, cell = w, rot = PartRot(r, l), leaf = k });
				if (!gates)
				{
					continue;
				}
				int gi = RM_DrawbridgePackageMath.GateIndex(l.Span);
				for (int lane = 0; lane < r.width; lane++)
				{
					IntVec3 c = r.Cell(lane, gi);
					if (Placeable(map, gate, c, PartRot(r, l), gateStuff, out _))
					{
						parts.Add(new DrawbridgePart { def = gate, cell = c, rot = PartRot(r, l), stuff = gateStuff, leaf = -1 });
					}
					else
					{
						skippedGates++;
					}
				}
			}
			return true;
		}

		/// <summary>Place one part: a blueprint, or in god mode the finished building (as the deck's own Place does).</summary>
		public static void PlacePart(Map map, DrawbridgePart p, string look)
		{
			ThingDef stuff = p.def.MadeFromStuff ? p.stuff : null;
			if (DebugSettings.godMode)
			{
				Thing t = ThingMaker.MakeThing(p.def, stuff);
				t.SetFactionDirect(Faction.OfPlayer);
				GenSpawn.Spawn(t, p.cell, map, p.rot, WipeMode.VanishOrMoveAside);
			}
			else
			{
				GenSpawn.WipeExistingThings(p.cell, p.rot, p.def.blueprintDef, map, DestroyMode.Deconstruct);
				GenConstruct.PlaceBlueprintForBuild(p.def, p.cell, map, p.rot, Faction.OfPlayer, stuff, null, RM_SuspensionLooks.StyleFor(p.def, look));
			}
			FleckMaker.ThrowMetaPuffs(GenAdj.OccupiedRect(p.cell, p.rot, p.def.Size), map);
		}

		/// <summary>Is this def already built, framed or blueprinted on c (so "Place winch house" is not offered twice)?</summary>
		public static bool PlannedOrBuiltAt(Map map, IntVec3 c, ThingDef d)
		{
			if (map == null || !c.IsValid || !c.InBounds(map))
			{
				return false;
			}
			foreach (Thing t in c.GetThingList(map))
			{
				if (t.def == d || t.def.entityDefToBuild == d)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>"Place winch house": for a leaf with no winch (lost, never built, or a drawbridge from before the one drag),
		/// a blueprint on its planned square, else beside its hinge anchor. Null when the leaf has one, or one is planned.</summary>
		public static Command_Action WinchGizmo(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)
		{
			if (map == null || r == null || l == null || (l.winch != null && l.winch.Spawned))
			{
				return null;
			}
			ThingDef d = WinchDef(r.tier);
			if (PlannedOrBuiltAt(map, l.plannedWinch, d))
			{
				return null;
			}
			Command_Action cmd = new Command_Action
			{
				defaultLabel = "Place winch house",
				defaultDesc = "This leaf has no winch house. Plan one on its hinge bank, beside the anchor it swings on"
					+ (RM_DrawbridgeMath.IsPowered(r.tier) ? " (it needs power)." : "."),
				icon = d.uiIcon,
				action = () =>
				{
					IntVec3 c = l.plannedWinch;
					string why = null;
					if (!c.IsValid || !Placeable(map, d, c, PartRot(r, l), null, out why))
					{
						c = WinchSpot(map, r, l, false, out why);
					}
					if (!c.IsValid)
					{
						Messages.Message("Cannot place the winch house: " + why + ".", MessageTypeDefOf.RejectInput, false);
						return;
					}
					l.plannedWinch = c;
					PlacePart(map, new DrawbridgePart { def = d, cell = c, rot = PartRot(r, l), leaf = r.leaves.IndexOf(l) }, r.look);
				},
			};
			if (!d.IsResearchFinished)
			{
				cmd.Disable("Needs research first.");
			}
			return cmd;
		}
	}
}
