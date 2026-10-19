using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>
	/// SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS (construction design §1.1-§1.3, ruled model C "drag like a wall"): the build
	/// button of one suspension bridge type. Vanilla's Designator_Build answers "may this one cell take a piece?"; only the
	/// whole drag can answer "does this reach ground at both ends?", so DesignateMultiCell sees the drag and refuses it with
	/// its reason, or places an anchor on each end of every lane and deck blueprints between, and records the bridge.
	/// Registered through DesignationCategoryDef Structure's specialDesignatorClasses (Patches/Pits/RM_SuspensionBridges.xml);
	/// the deck defs set canGenerateDefaultDesignator false so vanilla makes no plain button for them.
	/// </summary>
	public abstract class Designator_SuspensionBridge : Designator_Build
	{
		protected Designator_SuspensionBridge(ThingDef deck) : base(deck)
		{
		}

		public SuspensionTier Tier => ((ThingDef)PlacingDef).GetModExtension<RM_SuspensionExtension>()?.tier ?? SuspensionTier.Timber;

		/// <summary>SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP: this button places the grated deck of its type.</summary>
		public bool Grated => ((ThingDef)PlacingDef).GetModExtension<RM_SuspensionExtension>()?.grated ?? false;

		public override bool Visible => RM_SuspensionSettings.suspensionBridgesBuildable && base.Visible;

		public override string Desc => base.Desc + "\n\nDrag from solid ground, across a dug hole, to solid ground: 1 to 3 squares wide, at most "
			+ RM_SuspensionMath.MaxLength(Tier, RM_SuspensionSettings.suspensionLengthMultiplier)
			+ " squares between supports (plan a tower on the hole floor first to go further). Anchors go on both ends and are built first.";

		public override AcceptanceReport CanDesignateCell(IntVec3 c)
		{
			if (!c.InBounds(Map))
			{
				return false;
			}
			if (c.Fogged(Map))
			{
				return "CannotPlaceInUndiscovered".Translate();
			}
			return true;
		}

		public override void DesignateSingleCell(IntVec3 c)
		{
			Messages.Message("Drag a suspension bridge from solid ground, across a dug hole, to solid ground on the far side.",
				MessageTypeDefOf.RejectInput, false);
		}

		public override void DesignateMultiCell(IEnumerable<IntVec3> cells)
		{
			List<IntVec3> list = cells.ToList();
			string refusal = TryDesignate(list);
			if (refusal != null)
			{
				Messages.Message(refusal, MessageTypeDefOf.RejectInput, false);
				Finalize(false);
				return;
			}
			Finalize(true);
		}

		/// <summary>Validate the drag and place it. Null = placed; otherwise why not (nothing placed).</summary>
		public string TryDesignate(List<IntVec3> cells)
		{
			Map map = Map;
			if (cells == null || cells.Count == 0)
			{
				return RM_SuspensionMath.ValidateDrag(null, null, Tier, RM_SuspensionSettings.suspensionLengthMultiplier);
			}
			int minX = cells.Min(c => c.x), maxX = cells.Max(c => c.x), minZ = cells.Min(c => c.z), maxZ = cells.Max(c => c.z);
			int dx = maxX - minX + 1, dz = maxZ - minZ + 1;
			HashSet<IntVec3> dragged = new HashSet<IntVec3>(cells);
			List<Rot4> axes = new List<Rot4>();
			if (dz >= dx)
			{
				axes.Add(Rot4.North);
			}
			if (dx >= dz)
			{
				axes.Add(Rot4.East);
			}
			string first = null;
			foreach (Rot4 dir in axes)
			{
				SuspensionBridgeRecord r = new SuspensionBridgeRecord
				{
					tier = Tier,
					// Side is the clockwise turn of dir: North → East (+x) so lanes count from the south-west corner; East → South
					// (-z) so they count from the north-west corner.
					origin = dir == Rot4.North ? new IntVec3(minX, 0, minZ) : new IntVec3(minX, 0, maxZ),
					dir = dir,
					length = dir == Rot4.North ? dz : dx,
					width = dir == Rot4.North ? dx : dz,
					stuff = StuffDef,
					grated = Grated,
				};
				// SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD: the deck's height is the ends' (surface, or one dry ledge depth: a
				// sunken bridge, setting sunkenBridges)
				r.deckNotches = RM_SuspensionMath.DeckNotchesFor(EndDepth(map, r.Cell(0, 0)), EndDepth(map, r.Cell(0, r.length - 1)),
					RM_SuspensionSettings.sunkenBridges);
				if (r.deckNotches < 0)
				{
					first = first ?? "Both ends of a suspension bridge must stand at one height: solid surface ground, or (a sunken bridge) "
						+ "dry ledges at the same depth inside the hole.";
					continue;
				}
				string why = Plan(map, r, dragged);
				if (why == null)
				{
					Place(map, r);
					return null;
				}
				first = first ?? why;
			}
			return first;
		}

		/// <summary>Classify every square of the planned bridge and run the rules (RM_SuspensionMath.ValidateDrag), then the
		/// vanilla per-square placement check for each anchor and deck blueprint.</summary>
		private string Plan(Map map, SuspensionBridgeRecord r, HashSet<IntVec3> dragged)
		{
			List<IList<SpanGround>> lanes = new List<IList<SpanGround>>();
			List<ICollection<int>> towers = new List<ICollection<int>>();
			for (int lane = 0; lane < r.width; lane++)
			{
				List<SpanGround> g = new List<SpanGround>();
				HashSet<int> t = new HashSet<int>();
				for (int i = 0; i < r.length; i++)
				{
					IntVec3 c = r.Cell(lane, i);
					g.Add(dragged.Contains(c) ? Classify(map, c, r.deckNotches) : SpanGround.Blocked);
					if (i > 0 && i < r.length - 1 && c.InBounds(map) && RM_MapComponent_SuspensionBridges.TowerAt(map, c))
					{
						t.Add(i);
					}
				}
				lanes.Add(g);
				towers.Add(t);
			}
			string why = RM_SuspensionMath.ValidateDrag(lanes, towers, r.tier, RM_SuspensionSettings.suspensionLengthMultiplier);
			if (why != null)
			{
				return why;
			}
			// every lane shares the same tower squares (a tower holds the whole width): the record keeps lane 0's
			r.towers = towers[0].ToList();
			ThingDef anchor = RM_SuspensionDefOf.AnchorOf(r.tier);
			ThingDef deck = RM_SuspensionDefOf.DeckOf(r.tier, r.grated);
			for (int lane = 0; lane < r.width; lane++)
			{
				for (int i = 0; i < r.length; i++)
				{
					bool end = i == 0 || i == r.length - 1;
					ThingDef d = end ? anchor : deck;
					Rot4 rot = end ? (i == 0 ? r.dir : r.dir.Opposite) : r.dir;
					AcceptanceReport ok = GenConstruct.CanPlaceBlueprintAt(d, r.Cell(lane, i), rot, map, false, null, null,
						d.MadeFromStuff ? r.stuff : null);
					if (!ok.Accepted)
					{
						return (end ? "Anchor" : "Deck square " + i) + (r.width > 1 ? " of row " + (lane + 1) : "") + ": "
							+ (ok.Reason.NullOrEmpty() ? "cannot be placed there." : ok.Reason);
					}
				}
			}
			return null;
		}

		/// <summary>The walking depth (notches) an END of the drag stands at: 0 on undug ground, the dug depth of a dry ledge,
		/// -1 where no anchor can stand (wet, out of the map).</summary>
		public static int EndDepth(Map map, IntVec3 c)
		{
			if (!c.InBounds(map))
			{
				return -1;
			}
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null || ex.ExcavatedDepthAt(c) <= 0)
			{
				return 0;
			}
			return ex.FillAt(c) == 0 ? ex.ExcavatedDepthAt(c) : -1;
		}

		/// <summary>What one dragged square is for a surface bridge (the posts build's reading).</summary>
		public static SpanGround Classify(Map map, IntVec3 c)
		{
			return Classify(map, c, 0);
		}

		/// <summary>What one dragged square is for a deck at <paramref name="deckNotches"/>: ground an anchor stands on (the
		/// surface, or a dry ledge at exactly the deck's height), a hole a deck may cross (at least 0.5 m below the deck), or
		/// blocked.</summary>
		public static SpanGround Classify(Map map, IntVec3 c, int deckNotches)
		{
			if (!c.InBounds(map) || c.Fogged(map))
			{
				return SpanGround.Blocked;
			}
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			if (c.GetEdifice(map) != null || RM_SpanUtility.DeckedAt(map, c))
			{
				return SpanGround.Blocked;
			}
			foreach (Thing t in c.GetThingList(map))
			{
				if (RM_SuspensionDefOf.IsPartDef(t.def) && !RM_MapComponent_SuspensionBridges.TowerAt(map, c))
				{
					return SpanGround.Blocked;   // another bridge is planned here
				}
			}
			if (ex != null && ex.ExcavatedDepthAt(c) > 0)
			{
				bool dryClear = ex.FillAt(c) == 0 && c.Standable(map);
				return RM_SuspensionMath.GroundFor(ex.ExcavatedDepthAt(c), deckNotches, dryClear);
			}
			if (deckNotches > 0)
			{
				return SpanGround.Blocked;   // undug ground above a sunken deck
			}
			TerrainDef terrain = c.GetTerrain(map);
			// SUSPENSION_WATERS_BUILD_MAY_BACKTRACK (Q5): natural water (a river, a lake, the sea) is crossed like a hole; the
			// deck is a building on top and nothing converts the water
			if (terrain != null && terrain.IsWater)
			{
				return RM_SuspensionWaters.Spannable(terrain) ? SpanGround.Hole : SpanGround.Blocked;
			}
			if (terrain == null || !c.Standable(map) || (ex != null && ex.DepthAt(c) > 0))
			{
				return SpanGround.Blocked;
			}
			return SpanGround.Ground;
		}

		private void Place(Map map, SuspensionBridgeRecord r)
		{
			ThingDef anchor = RM_SuspensionDefOf.AnchorOf(r.tier);
			ThingDef deck = RM_SuspensionDefOf.DeckOf(r.tier, r.grated);
			map.GetComponent<RM_MapComponent_SuspensionBridges>().Register(r);
			// anchors first, then the deck from both ends inward, so the god-mode path (instant build) runs the same order
			List<(int lane, int i)> order = new List<(int, int)>();
			for (int lane = 0; lane < r.width; lane++)
			{
				order.Add((lane, 0));
				order.Add((lane, r.length - 1));
			}
			for (int step = 1; step <= (r.length - 1) / 2; step++)
			{
				for (int lane = 0; lane < r.width; lane++)
				{
					int a = step, b = r.length - 1 - step;
					if (a < b)
					{
						order.Add((lane, a));
						order.Add((lane, b));
					}
					else if (a == b)
					{
						order.Add((lane, a));
					}
				}
			}
			foreach ((int lane, int i) in order)
			{
				bool end = i == 0 || i == r.length - 1;
				ThingDef d = end ? anchor : deck;
				Rot4 rot = end ? (i == 0 ? r.dir : r.dir.Opposite) : r.dir;
				IntVec3 c = r.Cell(lane, i);
				ThingDef stuff = d.MadeFromStuff ? r.stuff : null;
				if (DebugSettings.godMode)
				{
					Thing t = ThingMaker.MakeThing(d, stuff);
					t.SetFactionDirect(Faction.OfPlayer);
					GenSpawn.Spawn(t, c, map, rot);
				}
				else
				{
					GenSpawn.WipeExistingThings(c, rot, d.blueprintDef, map, DestroyMode.Deconstruct);
					GenConstruct.PlaceBlueprintForBuild(d, c, map, rot, Faction.OfPlayer, stuff);
				}
				FleckMaker.ThrowMetaPuffs(GenAdj.OccupiedRect(c, rot, d.Size), map);
			}
		}
	}

	public class Designator_SuspensionBridge_Rope : Designator_SuspensionBridge
	{
		public Designator_SuspensionBridge_Rope() : base(DefDatabase<ThingDef>.GetNamed("RM_SuspensionDeck_Rope"))
		{
		}
	}

	public class Designator_SuspensionBridge_Timber : Designator_SuspensionBridge
	{
		public Designator_SuspensionBridge_Timber() : base(DefDatabase<ThingDef>.GetNamed("RM_SuspensionDeck_Timber"))
		{
		}
	}

	public class Designator_SuspensionBridge_Steel : Designator_SuspensionBridge
	{
		public Designator_SuspensionBridge_Steel() : base(DefDatabase<ThingDef>.GetNamed("RM_SuspensionDeck_Steel"))
		{
		}
	}

	public class Designator_SuspensionBridge_Heavy : Designator_SuspensionBridge
	{
		public Designator_SuspensionBridge_Heavy() : base(DefDatabase<ThingDef>.GetNamed("RM_SuspensionDeck_Heavy"))
		{
		}
	}

	public class Designator_SuspensionBridge_SteelGrated : Designator_SuspensionBridge
	{
		public Designator_SuspensionBridge_SteelGrated() : base(DefDatabase<ThingDef>.GetNamed("RM_SuspensionDeck_SteelGrated"))
		{
		}
	}

	public class Designator_SuspensionBridge_HeavyGrated : Designator_SuspensionBridge
	{
		public Designator_SuspensionBridge_HeavyGrated() : base(DefDatabase<ThingDef>.GetNamed("RM_SuspensionDeck_HeavyGrated"))
		{
		}
	}

	/// <summary>A deck square goes over a dug hole at least 0.5 m deep (the designator places them; this guards copy/paste).</summary>
	public class PlaceWorker_SuspensionOverHole : PlaceWorker
	{
		public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null,
			Thing thing = null)
		{
			RM_MapComponent_Excavation ex = map?.GetComponent<RM_MapComponent_Excavation>();
			bool water = map != null && loc.InBounds(map) && RM_SuspensionWaters.Spannable(loc.GetTerrain(map));
			if (!water && (ex == null || !RM_SpanMath.HasDrop(ex.ExcavatedDepthAt(loc), 0)))
			{
				return "Goes over a dug hole at least 0.5 m deep, or over a river, lake or the sea.";
			}
			if (checkingDef == RM_SuspensionDefOf.RM_SuspensionTower && RM_SpanUtility.DeckedAt(map, loc))
			{
				return "Build the tower first, then drag the suspension bridge over it.";
			}
			return true;
		}
	}
}
