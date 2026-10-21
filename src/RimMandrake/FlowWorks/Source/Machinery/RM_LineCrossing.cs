using HarmonyLib;
using RimWorld;
using Verse;
using RimMandrake.FlowWorks.Pits;

namespace RimMandrake.FlowWorks.Machinery
{
	/// <summary>PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE P1: the def-level line tag. Put on a line's ThingDef (RM_UniversalPipe in
	/// Defs/Machinery/RM_LiquidLogistics.xml; vanilla PowerConduit by Patches/RM_LineKinds.xml, which HiddenConduit and
	/// WaterproofConduit inherit). Never on a ThingStyleDef: a look must not change where a line may go.</summary>
	public class RM_LineKindExtension : DefModExtension
	{
		public LineKind kind = LineKind.RigidPipe;
	}

	/// <summary>
	/// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 1 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P2):
	/// the one crossing policy (RM_LineCrossingMath.Verdict) read off the map. Three gates use it:
	///   * GenConstruct.CanBuildOnTerrain (RM_Patch_LineCrossingTerrain): the engine's terrain gate for blueprint placement,
	///     for auto-rebuild (ThingUtility.CheckAutoRebuildOnDestroyed goes through CanPlaceBlueprintAt), and for
	///     TerrainGrid.DoTerrainChangedEffects cancelling a blueprint or frame whose square was dug under it;
	///   * GenConstruct.CanPlaceBlueprintAt_NewTemp (RM_Patch_LineCrossingPlacement): the same verdict with its reason text;
	///   * Frame.CompleteConstruction (RM_Patch_LineCrossingFrame): a deck or cover can be built over a planned line without
	///     any terrain change, so the frame is checked again when it completes, and cancelled (refunded) if it may not stand.
	/// Setting RM_MachinerySettings.lineCrossingRulesEnabled; off, lines take the engine's affordance rules alone.
	/// Not here (later phases): digging under a BUILT line (P4), pipe poles (P3), the hose router's ramp/ladder rule (P5).
	/// </summary>
	public static class RM_LineCrossing
	{
		/// <summary>State reads for the functional script: placement checks refused (counted per CanPlaceBlueprintAt call, so a
		/// designator dragged over a deck counts every frame: compare before/after one call, never read it as a blueprint count),
		/// and frames cancelled at completion.</summary>
		public static int PlacementsRefused, FramesCancelled;

		/// <summary>The line kind of a buildable (a blueprint's or frame's own def answers through entityDefToBuild), or null for
		/// anything that is not a tagged line. Reads the def's tag only: never its style, never building.isPowerConduit.</summary>
		public static LineKind? KindOf(BuildableDef def)
		{
			if (def is ThingDef td && td.entityDefToBuild != null)
			{
				def = td.entityDefToBuild;
			}
			RM_LineKindExtension ext = def?.GetModExtension<RM_LineKindExtension>();
			return ext == null ? (LineKind?)null : ext.kind;
		}

		/// <summary>What the square is, as a line sees it: an intact cover or deck on it, else dug or solid ground.</summary>
		public static LineSurface SurfaceAt(Map map, IntVec3 c)
		{
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			return RM_LineCrossingMath.Classify(ex != null && ex.IsExcavated(c), DeckOn(map, c));
		}

		private static DeckOnSquare DeckOn(Map map, IntVec3 c)
		{
			Building_SpanDeck deck = RM_SpanUtility.DeckAt(map, c);   // intact and not raised
			if (deck == null)
			{
				return DeckOnSquare.None;
			}
			if (deck is Building_PitCover)
			{
				return DeckOnSquare.Cover;
			}
			if (deck is Building_SuspensionDeck s)
			{
				SuspensionBridgeRecord r = s.Record;
				if (r != null && r.IsDrawbridge && r.TryIndexOf(c, out _, out int i) && RM_Drawbridges.LeafOf(r, i) != null)
				{
					return DeckOnSquare.DrawbridgeLeaf;
				}
				return s.Tier == SuspensionTier.Rope ? DeckOnSquare.RopeDeck : DeckOnSquare.Deck;
			}
			return DeckOnSquare.Deck;
		}

		/// <summary>The first refused square of this line's footprint, with its reason; null = may stand (or not a line, or the
		/// rules are off).</summary>
		public static string Refusal(BuildableDef def, IntVec3 center, Rot4 rot, Map map)
		{
			if (!RM_MachinerySettings.lineCrossingRulesEnabled || map == null)
			{
				return null;
			}
			LineKind? kind = KindOf(def);
			if (kind == null)
			{
				return null;
			}
			foreach (IntVec3 c in GenAdj.OccupiedRect(center, rot, def.Size))
			{
				if (!c.InBounds(map))
				{
					continue;
				}
				string why = RM_LineCrossingMath.RefusalReason(kind.Value, SurfaceAt(map, c));
				if (why != null)
				{
					return why;
				}
			}
			return null;
		}

		/// <summary>The narrow exception (P2, answer 4): a flexible line lies on any intact deck, rope included, though rope lends
		/// no Light affordance to anything else.</summary>
		public static bool FlexOnDeck(BuildableDef def, IntVec3 center, Rot4 rot, Map map)
		{
			if (!RM_MachinerySettings.lineCrossingRulesEnabled || map == null)
			{
				return false;
			}
			LineKind? kind = KindOf(def);
			if (kind == null || !RM_LineCrossingMath.IsFlexible(kind.Value))
			{
				return false;
			}
			foreach (IntVec3 c in GenAdj.OccupiedRect(center, rot, def.Size))
			{
				if (!c.InBounds(map))
				{
					return false;
				}
				LineSurface s = SurfaceAt(map, c);
				if ((s != LineSurface.Deck && s != LineSurface.RopeDeck && s != LineSurface.DrawbridgeLeaf)
					|| !RM_LineCrossingMath.MayBuild(kind.Value, s))
				{
					return false;
				}
			}
			return true;
		}
	}

	/// <summary>The terrain gate. Last, so it overrules RM_Patch_SuspensionAffordance (a timber deck lends Light, which would
	/// otherwise admit a pipe) and grants the flexible-line deck exception after it.</summary>
	[HarmonyPatch(typeof(GenConstruct), nameof(GenConstruct.CanBuildOnTerrain))]
	[RimMandrake.Shared.PatchFeature("Rigid pipe and conduit need solid ground", typeof(RM_MachinerySettings), "lineCrossingRulesEnabled")]
	public static class RM_Patch_LineCrossingTerrain
	{
		[HarmonyPostfix]
		[HarmonyPriority(Priority.Last)]
		public static void Postfix(BuildableDef entDef, IntVec3 c, Map map, Rot4 rot, ref bool __result)
		{
			if (map == null || entDef == null || RM_LineCrossing.KindOf(entDef) == null)
			{
				return;   // the common case: not a tagged line
			}
			if (__result)
			{
				if (RM_LineCrossing.Refusal(entDef, c, rot, map) != null)
				{
					__result = false;
				}
			}
			else if (RM_LineCrossing.FlexOnDeck(entDef, c, rot, map))
			{
				__result = true;
			}
		}
	}

	/// <summary>Placement and auto-rebuild: the same verdict, with its reason on the blueprint.</summary>
	[HarmonyPatch(typeof(GenConstruct), nameof(GenConstruct.CanPlaceBlueprintAt_NewTemp))]
	[RimMandrake.Shared.PatchFeature("Line crossing reasons on placement", typeof(RM_MachinerySettings), "lineCrossingRulesEnabled")]
	public static class RM_Patch_LineCrossingPlacement
	{
		[HarmonyPostfix]
		[HarmonyPriority(Priority.Last)]
		public static void Postfix(BuildableDef entDef, IntVec3 center, Rot4 rot, Map map, ref AcceptanceReport __result)
		{
			if (map == null || entDef == null || RM_LineCrossing.KindOf(entDef) == null)
			{
				return;
			}
			string why = RM_LineCrossing.Refusal(entDef, center, rot, map);
			if (why != null)
			{
				RM_LineCrossing.PlacementsRefused++;
				__result = new AcceptanceReport(why);
			}
		}
	}

	/// <summary>Frame completion: a cover or deck built over a planned line since it was placed changes no terrain, so nothing
	/// cancelled the frame. Checked here; a refused frame is cancelled with its materials refunded.</summary>
	[HarmonyPatch(typeof(Frame), nameof(Frame.CompleteConstruction))]
	[RimMandrake.Shared.PatchFeature("Line crossing checked when a frame completes", typeof(RM_MachinerySettings), "lineCrossingRulesEnabled")]
	public static class RM_Patch_LineCrossingFrame
	{
		[HarmonyPrefix]
		public static bool Prefix(Frame __instance)
		{
			if (__instance == null || !__instance.Spawned || RM_LineCrossing.KindOf(__instance.def) == null)
			{
				return true;
			}
			string why = RM_LineCrossing.Refusal(__instance.def.entityDefToBuild, __instance.Position, __instance.Rotation, __instance.Map);
			if (why == null)
			{
				return true;
			}
			RM_LineCrossing.FramesCancelled++;
			Messages.Message(why + " The frame was cancelled.", new TargetInfo(__instance.Position, __instance.Map), MessageTypeDefOf.RejectInput, false);
			__instance.Destroy(DestroyMode.Cancel);
			return false;
		}
	}
}
