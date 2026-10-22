using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// Marks a cell of diggable soil to be carved into an empty channel.
	/// Pattern mirrors <see cref="Designator_SmoothFloors"/> exactly --
	/// vanilla's own cell-designation + labor-job shape, just targeting a
	/// different terrain and a different completion effect.
	/// </summary>
	public class Designator_DigCanal : Designator_Cells
	{
		public Designator_DigCanal()
		{
			defaultLabel = "Dig canal";
			defaultDesc = "Carve a channel half a metre deeper. Designating a channel that is "
				+ "already dug deepens it another half-metre, down to the deepest dig set in this mod's settings "
				+ "(as shipped, colonists 2 m; mechanoids and droids 20 m); from 2 m a cut is a pit. \"Dig to depth\" orders the whole depth at once. "
				+ "Liquid fills the deepest cells first and overflows into shallower ones. "
				+ "A channel dug into the strip along the map edge is a SINK: liquid reaching "
				+ "it leaves the map, which is how you empty a canal on purpose. Bare rock ground "
				+ "can be dug too, but is much slower work, and may turn up chunks of that rock.";
			icon = ContentFinder<Texture2D>.Get("UI/Designators/FlowWorks/RM_DigCanal", true);
			useMouseIcon = true;
			soundDragSustain = SoundDefOf.Designate_DragStandard;
			soundDragChanged = SoundDefOf.Designate_DragStandard_Changed;
			soundSucceeded = SoundDefOf.Designate_Mine;
			hotKey = KeyBindingDefOf.Misc6;
		}

		public override AcceptanceReport CanDesignateCell(IntVec3 c)
		{
			return CanDigCell(c, 0);
		}

		/// <summary>The shared gate. <paramref name="target"/>: a dig-to depth in notches (0 = one notch, this designator).</summary>
		protected AcceptanceReport CanDigCell(IntVec3 c, int target)
		{
			if (!c.InBounds(Map) || c.Fogged(Map))
			{
				return false;
			}
			if (c.InNoBuildEdgeArea(Map))
			{
				// PHASE 4, ruling 9 — SINKS. A sink is a map-edge drain, and the
				// edge band is precisely where vanilla refuses construction, so
				// with the edge refusal in place a sink could never be dug and
				// the mechanic could not exist. With sinks ON, the band opens to
				// the dig designator ONLY; nothing else about the no-build rule
				// changes, and an excavation in the band drains off-map by
				// definition. With sinks OFF, the old refusal stands unaltered.
				if (!RimMandrakeFlowWorksSettings.edgeSinksEnabled)
				{
					return "TooCloseToMapEdge".Translate();
				}
				if (c.OnEdge(Map))
				{
					return "TooCloseToMapEdge".Translate();
				}
			}
			if (target == 0 && Map.designationManager.DesignationAt(c, RimMandrakeFlowWorks_DefOf.RM_DigCanal) != null)
			{
				return "Already being dug as a canal.";
			}
			Building edifice = c.GetEdifice(Map);
			if (edifice != null)
			{
				// PIT_LEGACY_CODE_RETIRE_1: there are no pit buildings any more —
				// a pit is a canal cell dug to D=4, so digging deeper IS digging a pit.
				return "Must designate open ground.";
			}
			// Top layer (foundation first), not GetTerrain: GetTerrain returns the temp layer (ice, a flood).
			// NOT BaseTerrainAt here: that returns the soil UNDER a player floor, and would let a floored cell be
			// dug (floor destroyed). A wet channel's water is its top terrain since P14, so the water gate below
			// asks the depth grid whether the square is already ours.
			TerrainDef terrain = Map.terrainGrid.FoundationAt(c) ?? Map.terrainGrid.TopTerrainAt(c);
			// Digging an already-dug cell DEEPENS it (ruling 19), half a metre a cut, to the dig cap. Depth is set by digging
			// and by nothing else. PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT: the depth is the GRID's (terrain says only "2 m or
			// deeper"), so a 2 m pit is no longer refused as "as far down as digging goes".
			RM_MapComponent_Excavation eng = Map.GetComponent<RM_MapComponent_Excavation>();
			// P14: a wet DUG square carries its water on the base layer (the one ladder), so "is water" is asked of the
			// grid: only undug water (a lake, a river) is refused; a wet channel is deepened.
			if (terrain.IsWater && !(eng != null && eng.IsExcavated(c)))
			{
				return "Already water.";
			}
			int depth = eng != null ? eng.ExcavatedDepthAt(c) : RM_ExcavationDepth.DepthOfDryTerrain(terrain);
			// DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL: an order is held to the deepest ANYONE may dig (machine labour past the
			// colonist cap); the work giver holds each digger to its own.
			int cap = RM_DigLabor.DesignationCap;
			if (depth != RM_ExcavationDepth.Surface)
			{
				if (!RM_DigDepthMath.MayDeepen(depth, cap))
				{
					return "Already " + RM_Volume.FormatFloorMetres(depth) + " deep: the deepest digging goes (" + RM_Volume.FormatFloorMetres(cap)
						+ ", set in this mod's settings).";
				}
				if (target > 0 && depth >= RM_DigDepthMath.ClampTarget(target, cap))
				{
					return "Already " + RM_Volume.FormatFloorMetres(depth) + " deep.";
				}
				if (!RimMandrakeFlowWorksSettings.digToDepthEnabled)
				{
					return "Deepening is switched off in this mod's settings.";
				}
				return AcceptanceReport.WasAccepted;
			}
			if (!terrain.IsSoil && !(RimMandrakeFlowWorksSettings.digRockGroundEnabled && RM_DigDiscovery.RockOfTerrain(terrain) != null))
			{
				return "Must designate diggable soil or bare rock ground.";
			}
			// POND_BED (owner by card 2026-10-14): a dry pond bed is dug from its own depth, one deeper.
			if (eng != null && eng.NaturalBedDepthAt(c) > 0 && eng.FirstCutDepthAt(c) < 0)
			{
				return RimMandrakeFlowWorksSettings.digToDepthEnabled
					? "This dried pond bed is already as deep as digging goes (" + RM_Volume.FormatFloorMetres(cap) + ", set in this mod's settings)."
					: "Deepening is switched off in this mod's settings.";
			}
			if (target > 0 && eng != null && eng.FirstCutDepthAt(c) > RM_DigDepthMath.ClampTarget(target, cap))
			{
				return "This dried pond bed is already deeper than " + RM_Volume.FormatFloorMetres(RM_DigDepthMath.ClampTarget(target, cap)) + ".";
			}
			return AcceptanceReport.WasAccepted;
		}

		public override void DesignateSingleCell(IntVec3 c)
		{
			// The newer order wins, as vanilla's mine/deconstruct designators do: a cell marked both to dig and to
			// fill in would have pawns dig a level and fill it back for no net change.
			Map.designationManager.TryRemoveDesignation(c, RimMandrakeFlowWorks_DefOf.RM_FillInCanal);
			Map.designationManager.AddDesignation(new Designation(c, RimMandrakeFlowWorks_DefOf.RM_DigCanal));
			Map.GetComponent<RM_MapComponent_Excavation>()?.SetDigTarget(c, 0);   // a plain order is one notch
		}

		/// <summary>DIG_ROCK_TUNE_STONE_FIGHTS_BACK: say, beside the cursor, that the ground under it is rock and slow.</summary>
		public override void DrawMouseAttachments()
		{
			base.DrawMouseAttachments();
			Map map = Find.CurrentMap;
			IntVec3 c = UI.MouseCell();
			if (map == null || !RimMandrakeFlowWorksSettings.digRockGroundEnabled || !c.InBounds(map))
			{
				return;
			}
			if (RM_DigDiscovery.RockGroundAt(map, c) == null)
			{
				return;
			}
			string text = "Rock ground: slow to dig (x" + RimMandrakeFlowWorksSettings.digRockWorkMultiplier.ToString("0.#") + " work)";
			Vector2 m = UI.MousePositionOnUIInverted;
			Text.Font = GameFont.Small;
			Rect r = new Rect(m.x + 24f, m.y + 24f, 300f, 24f);
			Widgets.DrawBoxSolid(r, new Color(0f, 0f, 0f, 0.6f));
			Widgets.Label(r, " " + text);
		}

		public override void SelectedUpdate()
		{
			GenUI.RenderMouseoverBracket();
		}
	}

	/// <summary>
	/// PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT: "dig to N m". One order digs a square down to a chosen depth, half a metre a cut
	/// (one designation per notch was 14 clicks a square for 7 m). Pick the depth from the menu that opens when the tool is
	/// selected; drag over squares as with "Dig canal". A square already ordered is re-targeted. Each cut is the same job, cost
	/// and rules as "Dig canal" (RM_DigCanal designation; JobDriver_DigCanal puts it back after each cut until the target).
	/// The 4/7/7/4 square is 12 squares at 4 m and 4 at 7 m: two drags.
	/// </summary>
	public class Designator_DigCanalTo : Designator_DigCanal
	{
		/// <summary>The chosen depth in notches (default 4 m), held to the cap when used.</summary>
		public static int chosenTarget = 8;

		public Designator_DigCanalTo()
		{
			defaultLabel = "Dig to depth";
			defaultDesc = "Order squares dug down to a chosen depth in one go, half a metre a cut, as deep as this mod's settings "
				+ "allow (as shipped, colonists 2 m; mechanoids and droids 20 m: a deeper order waits for one). Pick the depth when you select this tool. Squares already ordered take the new depth. "
				+ "Each cut costs what \"Dig canal\" costs at that depth: deeper is slower. Get in and out with a ladder or ramps.";
			hotKey = null;
		}

		public static int Target => RM_DigDepthMath.ClampTarget(chosenTarget, RM_DigLabor.DesignationCap);

		public override string Label => "Dig to " + RM_Volume.FormatFloorMetres(Target);

		public override void ProcessInput(Event ev)
		{
			if (!CheckCanInteract())
			{
				return;
			}
			var options = new System.Collections.Generic.List<FloatMenuOption>();
			int cap = RM_DigLabor.DesignationCap;
			int colonistCap = RM_ExcavationDepth.MaxDigDepth;
			for (int n = 1; n <= cap; n++)
			{
				int pick = n;
				options.Add(new FloatMenuOption("Dig to " + RM_Volume.FormatFloorMetres(n)
					+ " (" + RM_DigDepthMath.DiggerDays(RM_DigDepthMath.WorkToDig(0, n, RimMandrakeFlowWorksSettings.digCostRisesWithDepth)).ToString("0.#")
					+ " digger-days a square of soil" + (n > colonistCap ? "; machines only past " + RM_Volume.FormatFloorMetres(colonistCap) : "") + ")", delegate
				{
					chosenTarget = pick;
					base.ProcessInput(ev);
				}));
			}
			Find.WindowStack.Add(new FloatMenu(options));
		}

		public override AcceptanceReport CanDesignateCell(IntVec3 c)
		{
			if (!RimMandrakeFlowWorksSettings.digToDepthEnabled)
			{
				return "Deepening is switched off in this mod's settings.";
			}
			return CanDigCell(c, Target);
		}

		public override void DesignateSingleCell(IntVec3 c)
		{
			Map.designationManager.TryRemoveDesignation(c, RimMandrakeFlowWorks_DefOf.RM_FillInCanal);
			if (Map.designationManager.DesignationAt(c, RimMandrakeFlowWorks_DefOf.RM_DigCanal) == null)
			{
				Map.designationManager.AddDesignation(new Designation(c, RimMandrakeFlowWorks_DefOf.RM_DigCanal));
			}
			Map.GetComponent<RM_MapComponent_Excavation>()?.SetDigTarget(c, Target);
		}
	}
}
