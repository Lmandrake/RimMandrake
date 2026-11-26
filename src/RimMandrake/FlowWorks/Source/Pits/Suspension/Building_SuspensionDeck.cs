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

		/// <summary>SUSPENSION_JETTY_BUILD_WALK_THE_PLANK: a jetty square (1 or 2 out from an anchor, no far end).</summary>
		public bool jetty;
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
		/// deck when its floor is at least 2 m below it and the setting is on (RM_SpanMath.PassesUnder, the rule a pit cover
		/// shares since 2026-11-22). No roof or dug passage ever grants a floor band ("NOT actual tunnels").</summary>
		public override bool FloorBandPassesUnder
		{
			get
			{
				if (!RM_SuspensionSettings.suspensionWalkUnder || !Spawned)
				{
					return false;
				}
				RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(Map);
				// Clearance is measured to the floor. The climb depth can rise with the water.
				return eng != null && RM_SpanMath.PassesUnder(RM_SpanMath.SpanKind.SuspensionDeck, RM_SuspensionSettings.suspensionWalkUnder,
					eng.HollowDepthAt(Position), DeckNotches);
			}
		}

		/// <summary>The picture the fade pass draws see-through over a pawn under it: what Print would draw, chosen in Print's
		/// order (a laid raid plank's piece, else the picked deck art's strip piece, else the linked tile), with its turn.</summary>
		public override Material FadeMaterial(out float angle)
		{
			SuspensionBridgeRecord r = Record;
			Material m = RM_DrawbridgeArt.RaidPlankMat(this, r, out angle);
			if (m == null)
			{
				m = RM_DrawbridgeArt.LeafDeckMat(this, r, out angle);
			}
			if (m == null)
			{
				m = RM_DeckArt.DeckMat(this, r, out angle);
			}
			return m ?? RM_SuspensionDeckLink.TileFor(this, out angle);
		}

		/// <summary>DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS: this square of a drawbridge leaf is up (derived from its leaf record by
		/// RM_Drawbridges.Apply and on spawn; never saved on the deck: the leaf record is the one saved state, R9).</summary>
		internal bool leafRaised;

		public override bool Raised => leafRaised;

		public RM_MapComponent_SuspensionBridges Bridges => Map?.GetComponent<RM_MapComponent_SuspensionBridges>();

		/// <summary>ISLAND_RAIDERS_NEVER_CROSS_LOWERED_LEAF: a raider sent at this bridge's winch does not wreck the crossing.</summary>
		public override void PreApplyDamage(ref DamageInfo dinfo, out bool absorbed)
		{
			absorbed = RM_DrawbridgeRaid.SparesBridge(this, dinfo);
			if (!absorbed)
			{
				base.PreApplyDamage(ref dinfo, out absorbed);
			}
		}

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
			leafRaised = RM_Drawbridges.RaisedAt(map, Position);   // DRAWBRIDGE: a reload (or a rebuilt square) reads its leaf
			RM_MapComponent_SuspensionBridges.DirtyAround(map, Position);
			RM_DeckArt.DirtyEnds(map, Record);   // the picked art's cables hang only from a whole deck
			RM_SuspensionWaters.Notify_DeckChanged(map, Position);
		}

		public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
		{
			Map map = Map;
			IntVec3 pos = Position;
			// SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD (Q6): a square that falls (a span giving way, a swing-down) lands on the
			// floor: whoever is under it is hit like a roof collapse, and the wreck blocks the floor until cleared
			bool falls = collapsed;
			List<Pawn> under = falls ? Bridges?.BandPawnsAt(pos) : null;
			SuspensionBridgeRecord rec = Bridges?.RecordAt(pos);
			string look = rec?.look;
			base.DeSpawn(mode);
			RM_MapComponent_SuspensionBridges.DirtyAround(map, pos);
			RM_DeckArt.DirtyEnds(map, rec);
			RM_SuspensionWaters.Notify_DeckChanged(map, pos);
			if (falls && map != null)
			{
				RM_MapComponent_SuspensionBridges.LandWreck(map, pos, under, look);
			}
		}

		/// <summary>A sunken deck draws a ledge shadow over itself so it reads as down in the hole, not on the surface.</summary>
		public override void Print(SectionLayer layer)
		{
			if (leafRaised)
			{
				return;   // DRAWBRIDGE (R12): a raised square draws empty; the winch house draws the leaf upright
			}
			Map map = Map;
			if (map != null && RM_MapComponent_SuspensionBridges.FadedAt(map, Position))
			{
				return;   // RIMMANDRAKE_FADE_EVERY_PIT_COVER_...: a pawn beneath; the fade pass draws this square see-through
			}
			if (RM_DrawbridgeArt.PrintRaidPlank(layer, this, Record))
			{
				// DRAWBRIDGE_LOOKS_WIRE_PICTURES_IN_WINGS: a laid raid plank draws its own mid and end pieces, turned to the span
			}
			else if (RM_DrawbridgeArt.PrintLeafDeck(layer, this, Record))
			{
				// his rulings of 2026-11-03: a drawbridge's lowered leaf is the picture it raises, so nothing changes at the first tick
			}
			else if (RM_DeckArt.PrintDeck(layer, this, Record))
			{
				// RIMMANDRAKE_INSTALL_JETTY_BRIDGE_PICKS: the owner's picked art, one strip cut into root/mid/tip/solo pieces
			}
			else if (Graphic is Graphic_Linked linked && linked.SubGraphic != null)
			{
				RM_SuspensionDeckLink.Print(layer, this);   // SUSPENSION_DECK_LINKED_NO_SEAMS
			}
			else
			{
				base.Print(layer);
			}
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
			Messages.Message("The " + RM_SuspensionMath.BridgeName(Tier) + " gave way under " + first.LabelShort
				+ (fallers.Count > 1 ? " and others." : "."), new LookTargets(fallers), MessageTypeDefOf.NegativeEvent);
		}

		public override string GetInspectString()
		{
			string s = base.GetInspectString();
			SuspensionBridgeRecord r = Record;
			string line = r == null ? RM_SuspensionMath.ReadoutName(Tier) : Bridges.InspectLines(r, Position);
			if (r != null && r.IsDrawbridge && r.TryIndexOf(Position, out _, out int li) && RM_Drawbridges.LeafOf(r, li) is DrawbridgeLeaf leaf)
			{
				line += "\n" + RM_Drawbridges.InspectLine(Map, r, leaf);   // DRAWBRIDGE (R11)
			}
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
			foreach (Gizmo g in RM_Drawbridges.DeckGizmos(Map, Record, Position))
			{
				yield return g;
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
		/// <summary>ISLAND_RAIDERS_NEVER_CROSS_LOWERED_LEAF: a raider sent at this bridge's winch does not wreck the crossing.</summary>
		public override void PreApplyDamage(ref DamageInfo dinfo, out bool absorbed)
		{
			absorbed = RM_DrawbridgeRaid.SparesBridge(this, dinfo);
			if (!absorbed)
			{
				base.PreApplyDamage(ref dinfo, out absorbed);
			}
		}

		public SuspensionTier Tier => def.GetModExtension<RM_SuspensionExtension>()?.tier ?? SuspensionTier.Timber;

		/// <summary>DRAWBRIDGE_CABLES_FIX_STOP_SHORT: facing a deck square, the ropes run on from where the picture stops to
		/// under the deck's end (they stopped short); facing a raised leaf, they lie slack on the bank, disconnected (owner
		/// 2026-10-23). The deck toggling a leaf re-prints its neighbours (RM_Drawbridges.NotifyToggled → DirtyAround).</summary>
		public override void Print(SectionLayer layer)
		{
			if (RM_DrawbridgeArt.PrintDrawbridgeEnd(layer, this))
			{
				foreach (ThingComp c in AllComps)
				{
					c.PostPrintOnto(layer);
				}
				return;   // the gate frame (hinge bank) or the mooring (far bank): no suspension tower, no painted ropes
			}
			if (RM_DeckArt.PrintAbutment(layer, this))
			{
				foreach (ThingComp c in AllComps)
				{
					c.PostPrintOnto(layer);
				}
				return;   // RIMMANDRAKE_REDRAW_TIMBER_BRIDGE_FROM_HIS_THREE_PHOTOS: a beam bridge's end is a sill, no bollards or ropes
			}
			RM_DrawbridgeArt.AnchorPrint p = RM_DrawbridgeArt.AnchorPrintFor(this);
			if (p == null)
			{
				base.Print(layer);
				RM_DeckArt.PrintEnd(layer, this);
				return;
			}
			if (p.slack)
			{
				RM_DrawbridgeArt.PrintBollards(layer, p);
				foreach (ThingComp c in AllComps)
				{
					c.PostPrintOnto(layer);
				}
			}
			else
			{
				base.Print(layer);
			}
			RM_DrawbridgeArt.PrintRopes(layer, p);
			RM_DeckArt.PrintEnd(layer, this);
		}

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
		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			if (!respawningAfterLoad)
			{
				map.GetComponent<RM_MapComponent_SuspensionBridges>()?.Notify_TowerBuilt(this);
			}
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
			if (map == null || mat == null || RM_Drawbridges.RaisedAt(map, Position))
			{
				return;   // a raised leaf's railing does not hang in the open gap
			}
			if (RM_DeckArt.PrintNetting(layer, this))
			{
				return;   // RIMMANDRAKE_REDRAW_ROPE_BRIDGE_AS_ROPES_AND_SPARSE_SLATS: a rope bridge's railing is rope netting
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
