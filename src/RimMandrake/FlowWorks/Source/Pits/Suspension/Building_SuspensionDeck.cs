using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS: which suspension bridge part a def is, and its type.</summary>
	public class RM_SuspensionExtension : DefModExtension
	{
		public SuspensionTier tier = SuspensionTier.Timber;

		/// <summary>SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP: an open grating (steel and heavy only): fire, spilled liquid and splash
		/// pass; shots between the deck and the floor band are not blocked.</summary>
		public bool grated;
	}

	[DefOf]
	public static class RM_SuspensionDefOf
	{
		public static ThingDef RM_SuspensionDeck_Rope;
		public static ThingDef RM_SuspensionDeck_Timber;
		public static ThingDef RM_SuspensionDeck_Steel;
		public static ThingDef RM_SuspensionDeck_Heavy;
		public static ThingDef RM_SuspensionDeck_SteelGrated;
		public static ThingDef RM_SuspensionDeck_HeavyGrated;
		public static ThingDef RM_SuspensionAnchor_Rope;
		public static ThingDef RM_SuspensionAnchor_Timber;
		public static ThingDef RM_SuspensionAnchor_Steel;
		public static ThingDef RM_SuspensionAnchor_Heavy;
		public static ThingDef RM_SuspensionTower;
		public static ThingDef RM_SuspensionRailing;
		public static ThingDef RM_SuspensionWreck;

		static RM_SuspensionDefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RM_SuspensionDefOf));
		}

		/// <summary>The deck def of this type, grated (steel and heavy only; any other type has no grated deck).</summary>
		public static ThingDef DeckOf(SuspensionTier t, bool grated)
		{
			if (grated && RM_SuspensionMath.MayBeGrated(t))
			{
				return t == SuspensionTier.Steel ? RM_SuspensionDeck_SteelGrated : RM_SuspensionDeck_HeavyGrated;
			}
			return DeckOf(t);
		}

		public static ThingDef DeckOf(SuspensionTier t)
		{
			switch (t)
			{
				case SuspensionTier.Rope: return RM_SuspensionDeck_Rope;
				case SuspensionTier.Timber: return RM_SuspensionDeck_Timber;
				case SuspensionTier.Steel: return RM_SuspensionDeck_Steel;
				default: return RM_SuspensionDeck_Heavy;
			}
		}

		public static ThingDef AnchorOf(SuspensionTier t)
		{
			switch (t)
			{
				case SuspensionTier.Rope: return RM_SuspensionAnchor_Rope;
				case SuspensionTier.Timber: return RM_SuspensionAnchor_Timber;
				case SuspensionTier.Steel: return RM_SuspensionAnchor_Steel;
				default: return RM_SuspensionAnchor_Heavy;
			}
		}

		public static bool IsDeckDef(BuildableDef d)
		{
			return d is ThingDef td && td.thingClass != null && typeof(Building_SuspensionDeck).IsAssignableFrom(td.thingClass);
		}

		public static bool IsAnchorDef(BuildableDef d)
		{
			return d is ThingDef td && td.thingClass != null && typeof(Building_SuspensionAnchor).IsAssignableFrom(td.thingClass);
		}

		/// <summary>Any part of a suspension bridge (deck, anchor, tower, railing), built or planned.</summary>
		public static bool IsPartDef(BuildableDef d)
		{
			if (d is ThingDef td && (td.IsBlueprint || td.IsFrame))
			{
				d = td.entityDefToBuild;
			}
			return d is ThingDef t && t.GetModExtension<RM_SuspensionExtension>() != null;
		}
	}

	/// <summary>
	/// SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS (design/RimMandrake/suspension_bridge_construction_design_2026-10-18.md §1-§4;
	/// parent design §6): one deck square of a player-facing "Suspension bridge" at the surface, over dug ground. A span deck
	/// (Building_SpanDeck): walking ground at height 0; for now a wall from below (the floor band is
	/// SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD's). Its span is the deck squares of its bridge between two supports (the
	/// RM_MapComponent_SuspensionBridges record), all lanes together; that span is summed and gives way whole. Losing any
	/// square (hit points to 0, or deconstructed) drops the whole span.
	/// </summary>
	public class Building_SuspensionDeck : Building_SpanDeck
	{
		public SuspensionTier Tier => def.GetModExtension<RM_SuspensionExtension>()?.tier ?? SuspensionTier.Timber;

		/// <summary>SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP: read by RM_GrateEffects (fire, spills, splash) and the shots between
		/// bands (SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD).</summary>
		public override bool Grated => def.GetModExtension<RM_SuspensionExtension>()?.grated ?? false;

		/// <summary>SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD: a sunken bridge's deck height (its record's, set by the drag from
		/// the ledge its anchors stand on); 0 at the surface.</summary>
		public override float DeckHeightM => (Record?.deckNotches ?? 0) * RM_SpanMath.NotchM;

		/// <summary>SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD (Q2, ruled 2 m clearance): pawns down in the hole walk under this
		/// deck when its floor is at least 2 m below it and the setting is on. Keyed to this class only: no roof, cover or
		/// passage ever grants a floor band ("NOT actual tunnels").</summary>
		public override bool FloorBandPassesUnder
		{
			get
			{
				if (!RM_SuspensionSettings.suspensionWalkUnder || !Spawned)
				{
					return false;
				}
				RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(Map);
				return eng != null && RM_SpanMath.ClearsUnderpass(eng.ClimbDepthAt(Position), DeckNotches);
			}
		}

		public RM_MapComponent_SuspensionBridges Bridges => Map?.GetComponent<RM_MapComponent_SuspensionBridges>();

		public SuspensionBridgeRecord Record => Bridges?.RecordAt(Position);

		public override float LoadRatingKg
		{
			get
			{
				SuspensionBridgeRecord r = Record;
				return r == null ? RM_SuspensionMath.RatingKg(Tier, 1, RM_SuspensionSettings.suspensionLoadMultiplier) : r.RatingKg;
			}
		}

		public override bool JoinsSpan(Building_SpanDeck other)
		{
			if (!(other is Building_SuspensionDeck d))
			{
				return false;
			}
			RM_MapComponent_SuspensionBridges b = Bridges;
			return b != null && b.SameSpan(Position, d.Position);
		}

		public override List<Building_SpanDeck> SpanCells()
		{
			RM_MapComponent_SuspensionBridges b = Bridges;
			return b == null ? new List<Building_SpanDeck> { this } : b.SpanDecks(Position);
		}

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			if (!respawningAfterLoad)
			{
				map.GetComponent<RM_MapComponent_SuspensionBridges>()?.Notify_DeckBuilt(this);
			}
			RM_MapComponent_SuspensionBridges.DirtyAround(map, Position);
		}

		public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
		{
			Map map = Map;
			IntVec3 pos = Position;
			// SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD (Q6): a square that falls (a span giving way, a swing-down) lands on the
			// floor: whoever is under it is hit like a roof collapse, and the wreck blocks the floor until cleared
			bool falls = collapsed;
			List<Pawn> under = falls ? Bridges?.BandPawnsAt(pos) : null;
			base.DeSpawn(mode);
			RM_MapComponent_SuspensionBridges.DirtyAround(map, pos);
			if (falls && map != null)
			{
				RM_MapComponent_SuspensionBridges.LandWreck(map, pos, under);
			}
		}

		/// <summary>A sunken deck draws a ledge shadow over itself so it reads as down in the hole, not on the surface.</summary>
		public override void Print(SectionLayer layer)
		{
			base.Print(layer);
			if (DeckNotches > 0 && RM_SuspensionMats.LedgeShadow != null)
			{
				Vector3 c = Position.ToVector3Shifted();
				c.y = def.Altitude + Altitudes.AltInc;
				Printer_Plane.PrintPlane(layer, c, Vector2.one, RM_SuspensionMats.LedgeShadow);
			}
		}

		/// <summary>A square lost by damage or by deconstruction drops its whole span: a suspension bridge does not unzip.</summary>
		public override void Destroy(DestroyMode mode = DestroyMode.Vanish)
		{
			if (!collapsed && Spawned && (mode == DestroyMode.KillFinalize || mode == DestroyMode.Deconstruct))
			{
				RM_MapComponent_SuspensionBridges b = Bridges;
				if (b != null)
				{
					b.CollapseSpan(this, mode == DestroyMode.KillFinalize ? "broke" : "was taken apart");
					if (Destroyed)
					{
						return;
					}
				}
			}
			base.Destroy(mode);
		}

		/// <summary>One square dropping alone (the swing-down from a lost anchor): pawns on it fall, the square is gone.</summary>
		public void DropAlone()
		{
			if (collapsed || !Spawned)
			{
				return;
			}
			Map map = Map;
			IntVec3 pos = Position;
			List<Pawn> fallers = RM_MapComponent_SuspensionBridges.PawnsOn(map, pos);
			SuspensionBridgeRecord rec = Record;
			RM_MapComponent_SuspensionBridges.ClearDeckTop(map, pos);
			collapsed = true;
			FilthMaker.TryMakeFilth(pos, map, ThingDefOf.Filth_RubbleRock, 1);
			Destroy(DestroyMode.Vanish);
			RM_MapComponent_SuspensionBridges.Drop(map, fallers, rec);
		}

		/// <summary>Marked collapsed by the bridge so its own Destroy does not re-enter the span collapse.</summary>
		internal void MarkCollapsed()
		{
			collapsed = true;
		}

		protected override void CollapseMessage(Pawn first, List<Pawn> fallers)
		{
			Messages.Message("The " + RM_SuspensionMath.TierLabel(Tier) + " suspension bridge gave way under " + first.LabelShort
				+ (fallers.Count > 1 ? " and others." : "."), new LookTargets(fallers), MessageTypeDefOf.NegativeEvent);
		}

		public override string GetInspectString()
		{
			string s = base.GetInspectString();
			SuspensionBridgeRecord r = Record;
			string line = r == null ? "Suspension bridge (" + RM_SuspensionMath.TierLabel(Tier) + ")" : Bridges.InspectLines(r, Position);
			return s.NullOrEmpty() ? line : s + "\n" + line;
		}

		public override IEnumerable<Gizmo> GetGizmos()
		{
			foreach (Gizmo g in base.GetGizmos())
			{
				yield return g;
			}
			Gizmo rail = RM_MapComponent_SuspensionBridges.RailingGizmo(Map, Record);
			if (rail != null)
			{
				yield return rail;
			}
		}
	}

	/// <summary>Materials the suspension decks print besides their own graphic.</summary>
	[StaticConstructorOnStartup]
	public static class RM_SuspensionMats
	{
		public static readonly Material LedgeShadow = MaterialPool.MatFrom("Things/Building/FlowWorks/SuspensionBridge/RM_SuspensionLedgeShadow",
			ShaderDatabase.Transparent);
	}

	/// <summary>The posts at one end of a suspension bridge (1×1, on solid ground, facing the span). Built first; losing one
	/// swings the span it held down from that end.</summary>
	public class Building_SuspensionAnchor : Building
	{
		public SuspensionTier Tier => def.GetModExtension<RM_SuspensionExtension>()?.tier ?? SuspensionTier.Timber;

		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			RM_MapComponent_SuspensionBridges.DirtyAround(map, Position);
		}

		public override void Destroy(DestroyMode mode = DestroyMode.Vanish)
		{
			Map map = Map;
			IntVec3 pos = Position;
			bool wasSpawned = Spawned;
			base.Destroy(mode);
			if (wasSpawned && map != null)
			{
				map.GetComponent<RM_MapComponent_SuspensionBridges>()?.Notify_SupportLost(pos);
				RM_MapComponent_SuspensionBridges.DirtyAround(map, pos);
			}
		}

		public override string GetInspectString()
		{
			string s = base.GetInspectString();
			RM_MapComponent_SuspensionBridges b = Map?.GetComponent<RM_MapComponent_SuspensionBridges>();
			SuspensionBridgeRecord r = b?.RecordAt(Position);
			if (r == null)
			{
				return s;
			}
			string line = b.InspectLines(r, Position);
			return s.NullOrEmpty() ? line : s + "\n" + line;
		}

		public override IEnumerable<Gizmo> GetGizmos()
		{
			foreach (Gizmo g in base.GetGizmos())
			{
				yield return g;
			}
			RM_MapComponent_SuspensionBridges b = Map?.GetComponent<RM_MapComponent_SuspensionBridges>();
			Gizmo rail = RM_MapComponent_SuspensionBridges.RailingGizmo(Map, b?.RecordAt(Position));
			if (rail != null)
			{
				yield return rail;
			}
		}
	}

	/// <summary>A tower: a column built on the hole's floor (by a pawn down there) that holds a suspension bridge in the
	/// middle, splitting it into two spans. Plan it before dragging the bridge over it. Losing it swings both spans down.</summary>
	public class Building_SuspensionTower : Building
	{
		public override void Destroy(DestroyMode mode = DestroyMode.Vanish)
		{
			Map map = Map;
			IntVec3 pos = Position;
			bool wasSpawned = Spawned;
			base.Destroy(mode);
			if (wasSpawned && map != null)
			{
				map.GetComponent<RM_MapComponent_SuspensionBridges>()?.Notify_SupportLost(pos);
			}
		}
	}

	/// <summary>Railings on one deck square, ordered per bridge by the "Railings" switch (+50% of the deck's cost). Drawn on
	/// the square's edges that touch neither another deck square nor an anchor. A railed square never drops anyone and is a
	/// rail for RM_FallRails (blast throws stop at it, walked steps over its edge are refused). No cover (ruled).</summary>
	public class Building_SuspensionRailing : Building
	{
		public override void Print(SectionLayer layer)
		{
			Map map = Map;
			Material mat = Graphic?.MatSingle;
			if (map == null || mat == null)
			{
				return;
			}
			Vector3 center = Position.ToVector3Shifted();
			center.y = def.Altitude;
			for (int i = 0; i < 4; i++)
			{
				Rot4 edge = new Rot4(i);
				IntVec3 n = Position + edge.FacingCell;
				if (RM_MapComponent_SuspensionBridges.HoldsBridgeEnd(map, n))
				{
					continue;
				}
				Printer_Plane.PrintPlane(layer, center, Vector2.one, mat, edge.AsAngle);
			}
		}
	}
}
