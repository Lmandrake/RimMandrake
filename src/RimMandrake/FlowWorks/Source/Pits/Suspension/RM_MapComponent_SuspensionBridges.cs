using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>One dragged suspension bridge: lanes (1 to 3) of `length` squares from anchor A (index 0) to anchor B
	/// (index length-1) along `dir`, towers at indices in the middle. Cell(lane, i) = origin + side × lane + dir × i.</summary>
	public class SuspensionBridgeRecord : IExposable
	{
		public int id;
		public SuspensionTier tier;
		public IntVec3 origin;
		public Rot4 dir = Rot4.North;
		public int length;
		public int width = 1;
		public List<int> towers = new List<int>();
		public bool railings;
		public ThingDef stuff;
		/// <summary>SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP: the deck squares are the grated deck of this type.</summary>
		public bool grated;
		/// <summary>SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD: the deck's height in notches below ground (0 = surface; a sunken
		/// bridge stands on a ledge at this depth).</summary>
		public int deckNotches;

		public IntVec3 Side => dir.Rotated(RotationDirection.Clockwise).FacingCell;

		public IntVec3 Cell(int lane, int i)
		{
			return origin + Side * lane + dir.FacingCell * i;
		}

		/// <summary>SUSPENSION_JETTY_BUILD_WALK_THE_PLANK: a jetty: index 0 is its root (an anchor), 1..length-1 the overhang;
		/// no far end, one span, one person's weight.</summary>
		public bool jetty;

		/// <summary>SUSPENSION_ART_RESKIN_HE_SEES_FIRST: the look picked on the build button (Scrapper, Industrial, Modern,
		/// Futuristic; null = the default look). Its railings and its wreck are made in it.</summary>
		public string look;

		/// <summary>DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS (R9): the drawbridge leaves of this bridge, each with its own saved state;
		/// null on an ordinary suspension bridge (and on every bridge in a save from before drawbridges: all lowered).</summary>
		public List<DrawbridgeLeaf> leaves;

		public bool IsDrawbridge => leaves != null && leaves.Count > 0;

		/// <summary>DRAWBRIDGE phase 4 (R5): a raider's plank laid across a moat (no anchors; ordinary load, fire and breaking).</summary>
		public bool raidPlank;

		public List<int> Supports => RM_SuspensionMath.Supports(length, towers);

		public int SpanCount => jetty ? 1 : Supports.Count - 1;

		/// <summary>The last deck index (a bridge's far anchor is not deck; a jetty has no far anchor).</summary>
		public int LastDeck => jetty ? length - 1 : length - 2;

		/// <summary>The span a deck index belongs to.</summary>
		public int SpanOfIndex(int i)
		{
			if (jetty)
			{
				return 0;
			}
			return RM_SuspensionMath.SegmentOf(i <= 0 ? 1 : i >= length - 1 ? length - 2 : i, Supports);
		}

		/// <summary>The deck indices of span k.</summary>
		public List<int> SpanIndices(int span)
		{
			if (jetty)
			{
				List<int> all = new List<int>();
				for (int i = 1; i < length; i++)
				{
					all.Add(i);
				}
				return all;
			}
			return RM_SuspensionMath.SegmentCells(span, Supports, length);
		}

		public float RatingKg => jetty ? RM_SuspensionMath.JettyRatingKg(RM_SuspensionSettings.suspensionLoadMultiplier)
			: RM_SuspensionMath.RatingKg(tier, width, RM_SuspensionSettings.suspensionLoadMultiplier);

		public bool TryIndexOf(IntVec3 c, out int lane, out int i)
		{
			lane = -1;
			i = -1;
			IntVec3 d = c - origin;
			IntVec3 f = dir.FacingCell;
			IntVec3 s = Side;
			int along = d.x * f.x + d.z * f.z;
			int across = d.x * s.x + d.z * s.z;
			if (along < 0 || along >= length || across < 0 || across >= width || Cell(across, along) != c)
			{
				return false;
			}
			lane = across;
			i = along;
			return true;
		}

		public void ExposeData()
		{
			Scribe_Values.Look(ref id, "id", 0);
			Scribe_Values.Look(ref tier, "tier", SuspensionTier.Timber);
			Scribe_Values.Look(ref origin, "origin");
			Scribe_Values.Look(ref dir, "dir", Rot4.North);
			Scribe_Values.Look(ref length, "length", 0);
			Scribe_Values.Look(ref width, "width", 1);
			Scribe_Collections.Look(ref towers, "towers", LookMode.Value);
			Scribe_Values.Look(ref railings, "railings", false);
			Scribe_Defs.Look(ref stuff, "stuff");
			Scribe_Values.Look(ref grated, "grated", false);
			Scribe_Values.Look(ref deckNotches, "deckNotches", 0);
			Scribe_Values.Look(ref jetty, "jetty", false);
			Scribe_Values.Look(ref look, "look");
			Scribe_Collections.Look(ref leaves, "rmDrawbridgeLeaves", LookMode.Deep);
			Scribe_Values.Look(ref raidPlank, "rmRaidPlank", false);
			if (Scribe.mode == LoadSaveMode.PostLoadInit && towers == null)
			{
				towers = new List<int>();
			}
		}
	}

	/// <summary>
	/// SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS: the span record of every suspension bridge on a map (construction design
	/// §1.2 model C: "a map component records this span = these cells between these anchors"), its load check, collapse,
	/// swing-down from a lost support, railings switch and the shared reads the patches make.
	///
	/// Load (every 60 ticks): pawns (StatDefOf.Mass), items (mass × stack) and buildings (mass of their cost list) on each
	/// span's built deck squares, all lanes together, against the span's rating. At 90% it sags (inspect warning, a caution
	/// message as the creak); over it, the whole span gives way (setting suspensionWeightCollapse).
	/// </summary>
	public class RM_MapComponent_SuspensionBridges : MapComponent
	{
		private List<SuspensionBridgeRecord> bridges = new List<SuspensionBridgeRecord>();
		private int nextId = 1;
		private readonly Dictionary<IntVec3, SuspensionBridgeRecord> index = new Dictionary<IntVec3, SuspensionBridgeRecord>();
		private readonly HashSet<long> sagging = new HashSet<long>();

		/// <summary>SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD: pawns in the floor band (under a deck), decided per step by
		/// RM_SuspensionUnderpass.Entered. Saved, so a load keeps everyone on their own side of the deck.</summary>
		private HashSet<Pawn> floorBand = new HashSet<Pawn>();
		private List<Pawn> floorBandScribe;

		/// <summary>Items and corpses lying UNDER a deck (on the hole's floor, beneath it) that found no open floor to slide to:
		/// the square they lay on when marked. They are not the deck's load. Saved.</summary>
		private readonly Dictionary<Thing, IntVec3> underThings = new Dictionary<Thing, IntVec3>();
		private List<Thing> underScribe;
		private List<IntVec3> underCells;

		/// <summary>This thing lies under the deck on its square (RM_SuspensionUnderpass.SlideOut found nowhere to put it).</summary>
		public void MarkUnder(Thing t)
		{
			if (t != null && t.Spawned && t.Map == map)
			{
				underThings[t] = t.Position;
			}
		}

		/// <summary>Is this thing lying under the deck (marked, and still where it was marked)?</summary>
		public bool IsUnder(Thing t)
		{
			return underThings.Count > 0 && underThings.TryGetValue(t, out IntVec3 c) && t.Spawned && t.Position == c;
		}

		private void PruneUnder()
		{
			if (underThings.Count == 0)
			{
				return;
			}
			foreach (Thing t in underThings.Keys.ToList())
			{
				if (t == null || !t.Spawned || t.Map != map || t.Position != underThings[t] || RM_SuspensionUnderpass.PassingDeckAt(map, t.Position) == null)
				{
					underThings.Remove(t);
				}
			}
		}

		public static RM_MapComponent_SuspensionBridges Of(Map map)
		{
			return map?.GetComponent<RM_MapComponent_SuspensionBridges>();
		}

		public bool InBandSet(Pawn p)
		{
			return p != null && floorBand.Contains(p);
		}

		/// <summary>Pawns in any floor band on any map: 0 lets the hot reads (shots, draw, loads) skip the band at once. Static, so
		/// it is zeroed when a new game starts or loads (bandGame) and a removed map takes its band with it (MapRemoved).</summary>
		public static int BandTotal;

		private static Game bandGame;

		private static void BandForThisGame()
		{
			if (bandGame != Current.Game)
			{
				bandGame = Current.Game;
				BandTotal = 0;
			}
		}

		public override void MapRemoved()
		{
			base.MapRemoved();
			BandTotal = System.Math.Max(0, BandTotal - floorBand.Count);
			floorBand.Clear();
			underThings.Clear();
		}

		public void SetBand(Pawn p, bool under)
		{
			if (p == null)
			{
				return;
			}
			BandForThisGame();
			if (under)
			{
				if (floorBand.Add(p))
				{
					BandTotal++;
				}
			}
			else if (floorBand.Remove(p) && BandTotal > 0)
			{
				BandTotal--;
			}
		}

		/// <summary>The floor-band pawns standing on this square (read before a falling deck despawns).</summary>
		public List<Pawn> BandPawnsAt(IntVec3 c)
		{
			List<Pawn> ps = new List<Pawn>();
			foreach (Pawn p in floorBand)
			{
				if (p != null && p.Spawned && !p.Dead && p.Position == c)
				{
					ps.Add(p);
				}
			}
			return ps;
		}

		/// <summary>State reads for the functional script: pawns crushed under a falling deck, wreck things landed.</summary>
		public static int Crushed, Wrecks;

		/// <summary>Q6 (construction design §4, ruled by card): a deck square fell onto the floor at <paramref name="c"/>. Each pawn
		/// that was under it takes vanilla's thin-roof collapse crush (15-30, from above); a wreck lands on the floor and blocks
		/// it until someone clears it (deconstructs it). Where a pawn lies, only rubble lands (a wreck never spawns on anyone).</summary>
		public static void LandWreck(Map map, IntVec3 c, List<Pawn> under, string look = null)
		{
			RM_MapComponent_SuspensionBridges b = Of(map);
			if (under != null)
			{
				foreach (Pawn p in under)
				{
					b?.SetBand(p, false);
					if (p == null || !p.Spawned || p.Dead)
					{
						continue;
					}
					var dinfo = new DamageInfo(DamageDefOf.Crush, Rand.RangeInclusive(RM_SuspensionMath.CrushDamageMin, RM_SuspensionMath.CrushDamageMax),
						0f, -1f, null, null, null, DamageInfo.SourceCategory.Collapse);
					dinfo.SetBodyRegion(BodyPartHeight.Top, BodyPartDepth.Outside);
					p.TakeDamage(dinfo);
					Crushed++;
					Messages.Message(p.LabelShort + " was hit by a falling suspension bridge.", new LookTargets(p), MessageTypeDefOf.NegativeEvent);
				}
			}
			if (!c.InBounds(map) || RM_SuspensionDefOf.RM_SuspensionWreck == null)
			{
				return;
			}
			bool anyone = false;
			foreach (Thing t in c.GetThingList(map))
			{
				anyone |= t is Pawn || t.def.passability == Traversability.Impassable;
			}
			// FALLEN_CORD_BUILD_RUBBLE_IS_NO_SHIELD (owner card 2026-10-21: "A collapsed pole is not a solid barrier by any
			// means."): a square whose cord fell with it (ClearDeckTop recorded it before the deck went) gets walkable rubble,
			// never the impassable wreck, so the cord lies on top and a live one shocks whoever walks there at once.
			bool cordHere = map.GetComponent<RimMandrake.FlowWorks.Machinery.RM_MapComponent_FallenCords>()?.CordFellAt(c) ?? false;
			if (anyone || cordHere)
			{
				FilthMaker.TryMakeFilth(c, map, ThingDefOf.Filth_RubbleRock, 2);
				return;
			}
			Thing w = ThingMaker.MakeThing(RM_SuspensionDefOf.RM_SuspensionWreck);
			w.SetFactionDirect(Faction.OfPlayer);
			RM_SuspensionLooks.Apply(w, look);
			GenSpawn.Spawn(w, c, map, Rot4.Random);
			Wrecks++;
		}

		private struct PendingDrop
		{
			public int tick;
			public IntVec3 cell;
		}

		private readonly List<PendingDrop> swing = new List<PendingDrop>();

		/// <summary>Read by the functional script (northstar/suspension_bridge_proof.py) through the bridge: "x,z@tick" of every
		/// square that dropped in a swing-down, oldest first, max 64. Not saved.</summary>
		public readonly List<string> swingLog = new List<string>();

		public RM_MapComponent_SuspensionBridges(Map map) : base(map)
		{
		}

		public IReadOnlyList<SuspensionBridgeRecord> Bridges => bridges;

		public SuspensionBridgeRecord RecordAt(IntVec3 c)
		{
			return index.TryGetValue(c, out SuspensionBridgeRecord r) ? r : null;
		}

		public SuspensionBridgeRecord Register(SuspensionBridgeRecord r)
		{
			r.id = nextId++;
			bridges.Add(r);
			Reindex();
			return r;
		}

		private void Reindex()
		{
			index.Clear();
			foreach (SuspensionBridgeRecord r in bridges)
			{
				for (int lane = 0; lane < r.width; lane++)
				{
					for (int i = 0; i < r.length; i++)
					{
						// a jetty rooted on a bridge's anchor leaves that square to the bridge (RootedJetties finds it)
						if (r.jetty && i == 0 && index.ContainsKey(r.Cell(lane, i)))
						{
							continue;
						}
						index[r.Cell(lane, i)] = r;
					}
				}
			}
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Collections.Look(ref bridges, "rmSuspensionBridges", LookMode.Deep);
			Scribe_Values.Look(ref nextId, "rmSuspensionNextId", 1);
			if (Scribe.mode == LoadSaveMode.Saving)
			{
				floorBandScribe = new List<Pawn>(floorBand);
				floorBandScribe.RemoveAll(p => p == null || p.Destroyed);
			}
			Scribe_Collections.Look(ref floorBandScribe, "rmSuspensionFloorBand", LookMode.Reference);
			if (Scribe.mode == LoadSaveMode.Saving)
			{
				PruneUnder();
				underScribe = underThings.Keys.ToList();
				underCells = underScribe.Select(t => underThings[t]).ToList();
			}
			Scribe_Collections.Look(ref underScribe, "rmSuspensionUnderThings", LookMode.Reference);
			Scribe_Collections.Look(ref underCells, "rmSuspensionUnderCells", LookMode.Value);
			if (Scribe.mode == LoadSaveMode.Saving)
			{
				underScribe = null;
				underCells = null;
			}
			// a swing-down in flight survives a save (else the unfallen squares hang anchorless for good); old saves: keys absent = none
			List<int> swingTicks = null;
			List<IntVec3> swingCells = null;
			if (Scribe.mode == LoadSaveMode.Saving)
			{
				swingTicks = swing.Select(d => d.tick).ToList();
				swingCells = swing.Select(d => d.cell).ToList();
			}
			Scribe_Collections.Look(ref swingTicks, "rmSuspensionSwingTicks", LookMode.Value);
			Scribe_Collections.Look(ref swingCells, "rmSuspensionSwingCells", LookMode.Value);
			if (Scribe.mode == LoadSaveMode.LoadingVars && swingTicks != null && swingCells != null)
			{
				swing.Clear();
				for (int i = 0; i < System.Math.Min(swingTicks.Count, swingCells.Count); i++)
				{
					swing.Add(new PendingDrop { tick = swingTicks[i], cell = swingCells[i] });
				}
			}
			if (Scribe.mode == LoadSaveMode.PostLoadInit)
			{
				bridges = bridges ?? new List<SuspensionBridgeRecord>();
				Reindex();
				floorBand = new HashSet<Pawn>((floorBandScribe ?? new List<Pawn>()).Where(p => p != null));
				BandForThisGame();
				BandTotal += floorBand.Count;
				floorBandScribe = null;
				underThings.Clear();
				for (int i = 0; underScribe != null && underCells != null && i < System.Math.Min(underScribe.Count, underCells.Count); i++)
				{
					if (underScribe[i] != null)
					{
						underThings[underScribe[i]] = underCells[i];
					}
				}
				underScribe = null;
				underCells = null;
			}
		}

		// ── shared reads ─────────────────────────────────────────────────────────────

		/// <summary>Do these two squares hold deck of one span of one bridge?</summary>
		public bool SameSpan(IntVec3 a, IntVec3 b)
		{
			SuspensionBridgeRecord r = RecordAt(a);
			if (r == null || r != RecordAt(b) || !r.TryIndexOf(a, out _, out int ia) || !r.TryIndexOf(b, out _, out int ib))
			{
				return false;
			}
			return r.SpanOfIndex(ia) == r.SpanOfIndex(ib);
		}

		public List<IntVec3> SpanCellsOf(SuspensionBridgeRecord r, int span)
		{
			List<IntVec3> cells = new List<IntVec3>();
			List<int> idx = r.SpanIndices(span);
			for (int lane = 0; lane < r.width; lane++)
			{
				foreach (int i in idx)
				{
					cells.Add(r.Cell(lane, i));
				}
			}
			return cells;
		}

		/// <summary>Every intact deck of the span holding this square.</summary>
		public List<Building_SpanDeck> SpanDecks(IntVec3 c)
		{
			List<Building_SpanDeck> decks = new List<Building_SpanDeck>();
			SuspensionBridgeRecord r = RecordAt(c);
			if (r == null || !r.TryIndexOf(c, out _, out int i))
			{
				if (StructuralDeckAt(map, c) is Building_SuspensionDeck lone)
				{
					decks.Add(lone);
				}
				return decks;
			}
			foreach (IntVec3 cell in SpanCellsOf(r, r.SpanOfIndex(i)))
			{
				if (StructuralDeckAt(map, cell) is Building_SuspensionDeck d)
				{
					decks.Add(d);
				}
			}
			return decks;
		}

		public static Building_SuspensionDeck DeckAt(Map map, IntVec3 c)
		{
			return RM_SpanUtility.DeckAt(map, c) as Building_SuspensionDeck;
		}

		/// <summary>DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS (R6): the intact deck STRUCTURE on this square, raised or lowered. Structure
		/// reads (a span giving way, a swing-down) use this, so a raised leaf still falls with its span; walking reads use DeckAt.</summary>
		public static Building_SuspensionDeck StructuralDeckAt(Map map, IntVec3 c)
		{
			Building_SuspensionDeck d = BuiltAt<Building_SuspensionDeck>(map, c);
			return d != null && d.Spawned && !d.Collapsed ? d : null;
		}

		public static T BuiltAt<T>(Map map, IntVec3 c) where T : Thing
		{
			if (map == null || !c.InBounds(map))
			{
				return null;
			}
			List<Thing> things = map.thingGrid.ThingsListAtFast(c);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i] is T t)
				{
					return t;
				}
			}
			return null;
		}

		/// <summary>A built railing on this square.</summary>
		public static bool RailedAt(Map map, IntVec3 c)
		{
			return BuiltAt<Building_SuspensionRailing>(map, c) != null;
		}

		/// <summary>A railing draws no edge toward another deck square or an anchor (built or planned).</summary>
		public static bool HoldsBridgeEnd(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map))
			{
				return false;
			}
			List<Thing> things = map.thingGrid.ThingsListAtFast(c);
			for (int i = 0; i < things.Count; i++)
			{
				ThingDef d = things[i].def;
				BuildableDef b = d.IsBlueprint || d.IsFrame ? d.entityDefToBuild : d;
				if (RM_SuspensionDefOf.IsDeckDef(b) || RM_SuspensionDefOf.IsAnchorDef(b))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Is there a suspension bridge part (built, frame or blueprint) on this square? (dig and fill refuse it)</summary>
		public static bool AnyPartAt(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map))
			{
				return false;
			}
			List<Thing> things = map.thingGrid.ThingsListAtFast(c);
			for (int i = 0; i < things.Count; i++)
			{
				if (RM_SuspensionDefOf.IsPartDef(things[i].def))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>Is there a tower (built, frame or blueprint) on this square?</summary>
		public static bool TowerAt(Map map, IntVec3 c)
		{
			List<Thing> things = map.thingGrid.ThingsListAtFast(c);
			for (int i = 0; i < things.Count; i++)
			{
				ThingDef d = things[i].def;
				if (d == RM_SuspensionDefOf.RM_SuspensionTower || d.entityDefToBuild == RM_SuspensionDefOf.RM_SuspensionTower)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>An open hole beside a deck square (a cardinal neighbour that is dug and not decked), or Invalid.</summary>
		public static IntVec3 OpenEdgeBeside(Map map, IntVec3 c)
		{
			RM_MapComponent_Excavation ex = map?.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null)
			{
				return IntVec3.Invalid;
			}
			List<IntVec3> open = new List<IntVec3>();
			for (int i = 0; i < 4; i++)
			{
				IntVec3 n = c + GenAdj.CardinalDirections[i];
				// SUSPENSION_WATERS_BUILD_MAY_BACKTRACK: natural water beside a deck is an open edge too (a fall is a splash)
				if (n.InBounds(map) && !RM_SpanUtility.DeckedAt(map, n) && ((ex.ExcavatedDepthAt(n) > 0 && n.Standable(map))
					|| (n.GetTerrain(map)?.IsWater == true && (n.Standable(map) || Swimming.RM_SwimWater.IsDeepSwimCell(map, n)))))
				{
					open.Add(n);
				}
			}
			return open.Count == 0 ? IntVec3.Invalid : open.RandomElement();
		}

		public static void DirtyAround(Map map, IntVec3 c)
		{
			if (map == null)
			{
				return;
			}
			for (int i = 0; i < 4; i++)
			{
				IntVec3 n = c + GenAdj.CardinalDirections[i];
				if (n.InBounds(map))
				{
					map.mapDrawer.MapMeshDirty(n, MapMeshFlagDefOf.Buildings);
				}
			}
		}

		public static List<Pawn> PawnsOn(Map map, IntVec3 c)
		{
			List<Pawn> ps = new List<Pawn>();
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				// SUSPENSION_UNDERPASS: a pawn under the deck is not on it (it is hit, not dropped, when the deck falls)
				if (things[i] is Pawn p && !p.Dead && !p.Flying && !RM_SuspensionUnderpass.InFloorBand(p))
				{
					ps.Add(p);
				}
			}
			return ps;
		}

		/// <summary>Buildings standing on a falling deck square (railings included) are destroyed; items stay and fall with it.
		/// Every collapse path clears its squares here, so the deck (the support) owns the line teardown: first the cords on the
		/// square are recorded as a fallen wire and the hoses across it are reeled in (RM_DeckCollapseLines, PIPE_POLES phase 3),
		/// then everything is destroyed.</summary>
		public static void ClearDeckTop(Map map, IntVec3 c)
		{
			RimMandrake.FlowWorks.Machinery.RM_DeckCollapseLines.OnDeckCleared(map, c);
			List<Thing> things = new List<Thing>(c.GetThingList(map));
			foreach (Thing t in things)
			{
				if (t.Destroyed || t is Building_SpanDeck || t is Building_SuspensionTower)
				{
					continue;
				}
				if (t is Building || t.def.IsBlueprint || t.def.IsFrame)
				{
					t.Destroy(t is Building && !(t is Building_SuspensionRailing) ? DestroyMode.KillFinalize : DestroyMode.Vanish);
				}
			}
			// a player building killed above leaves its auto-rebuild blueprint (ThingUtility.CheckAutoRebuildOnDestroyed) on the
			// square that is about to be an open hole: nothing can be rebuilt there, so it goes too
			foreach (Thing t in new List<Thing>(c.GetThingList(map)))
			{
				if (!t.Destroyed && t.def.IsBlueprint)
				{
					t.Destroy(DestroyMode.Vanish);
				}
			}
		}

		/// <summary>Everyone on a deck that just went falls through the descent event; with suspensionOwnPeopleFall off, your
		/// own people are set down on the nearest standing anchor instead.</summary>
		public static void Drop(Map map, List<Pawn> fallers, SuspensionBridgeRecord r)
		{
			RM_SuperdeepTrapState state = RM_SuperdeepTrap.EngineOf(map)?.SuperdeepTrap;
			foreach (Pawn p in fallers)
			{
				if (p == null || !p.Spawned || p.Dead || p.Flying)
				{
					continue;
				}
				if (!RM_SuspensionSettings.suspensionOwnPeopleFall && p.Faction == Faction.OfPlayer)
				{
					IntVec3 safe = NearestAnchor(map, p.Position, r);
					if (safe.IsValid)
					{
						p.Position = safe;
						p.Notify_Teleported(true, true);
						continue;
					}
				}
				if (state != null)
				{
					// a sunken deck's riders fall from its height (SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD)
					int h = r?.deckNotches ?? 0;
					RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
					RM_SuperdeepTrap.OnForcedDescent(p, p.Position, state, h > 0 && eng != null ? System.Math.Max(0, eng.ClimbDepthAt(p.Position) - h) : -1);
				}
			}
		}

		private static IntVec3 NearestAnchor(Map map, IntVec3 from, SuspensionBridgeRecord r)
		{
			IntVec3 best = IntVec3.Invalid;
			float bestD = float.MaxValue;
			RM_MapComponent_SuspensionBridges b = map.GetComponent<RM_MapComponent_SuspensionBridges>();
			r = r ?? b?.RecordAt(from);
			if (r == null)
			{
				return best;
			}
			for (int lane = 0; lane < r.width; lane++)
			{
				foreach (int i in new[] { 0, r.length - 1 })
				{
					IntVec3 c = r.Cell(lane, i);
					if (BuiltAt<Building_SuspensionAnchor>(map, c) != null && c.Standable(map))
					{
						float d = c.DistanceToSquared(from);
						if (d < bestD)
						{
							bestD = d;
							best = c;
						}
					}
				}
			}
			return best;
		}

		// ── load ─────────────────────────────────────────────────────────────────────

		/// <summary>The weight on these deck squares: pawns, items, buildings (not the bridge's own parts).</summary>
		public float LoadOn(List<IntVec3> cells, List<Pawn> standing)
		{
			float sum = RM_SpanUtility.LoadOn(map, cells, null, true, standing);
			foreach (IntVec3 c in cells)
			{
				if (DeckAt(map, c) == null)
				{
					continue;
				}
				List<Thing> things = c.GetThingList(map);
				for (int i = 0; i < things.Count; i++)
				{
					Thing t = things[i];
					if (t.def.category == ThingCategory.Item && !IsUnder(t))
					{
						sum += t.GetStatValue(StatDefOf.Mass) * t.stackCount;
					}
					else if (t is Building bld && !RM_SuspensionDefOf.IsPartDef(bld.def) && !(bld is Building_SpanDeck))
					{
						sum += BuildingMass(bld);
					}
				}
			}
			return sum;
		}

		/// <summary>A building's weight on a deck: its own mass stat when set, else the mass of what it was built from.</summary>
		public static float BuildingMass(Building b)
		{
			float own = b.GetStatValue(StatDefOf.Mass);
			if (own > 0.01f)
			{
				return own;
			}
			float m = 0f;
			List<ThingDefCountClass> cost = b.def.CostListAdjusted(b.Stuff, false);
			if (cost != null)
			{
				foreach (ThingDefCountClass c in cost)
				{
					m += c.thingDef.BaseMass * c.count;
				}
			}
			return m;
		}

		/// <summary>Built deck squares of span k.</summary>
		private List<IntVec3> BuiltSpanCells(SuspensionBridgeRecord r, int span)
		{
			List<IntVec3> cells = new List<IntVec3>();
			foreach (IntVec3 c in SpanCellsOf(r, span))
			{
				if (DeckAt(map, c) != null)
				{
					cells.Add(c);
				}
			}
			return cells;
		}

		public float SpanLoad(SuspensionBridgeRecord r, int span, List<Pawn> standing = null)
		{
			return LoadOn(BuiltSpanCells(r, span), standing);
		}

		public override void MapComponentTick()
		{
			int now = Find.TickManager.TicksGame;
			RM_Drawbridges.Tick(this, now);   // DRAWBRIDGE_BUILD_MOAT_WITH_MANNERS: leaves move, toggles repath at once
			for (int k = swing.Count - 1; k >= 0; k--)
			{
				if (swing[k].tick <= now)
				{
					IntVec3 c = swing[k].cell;
					swing.RemoveAt(k);
					Building_SuspensionDeck d = StructuralDeckAt(map, c);
					if (d != null)
					{
						d.DropAlone();
						swingLog.Add(c.x + "," + c.z + "@" + now);
						if (swingLog.Count > 64)
						{
							swingLog.RemoveAt(0);
						}
					}
				}
			}
			if (now % 60 != 0 || bridges.Count == 0)
			{
				return;
			}
			if (now % 600 == 0)
			{
				PruneDead();
			}
			SweepUnder();
			PruneUnder();
			if (now % RM_SuspensionMath.TicksPerHour == 0)
			{
				RM_SuspensionWaters.FloodHour(map, bridges);
			}
			for (int b = 0; b < bridges.Count; b++)
			{
				SuspensionBridgeRecord r = bridges[b];
				for (int span = 0; span < r.SpanCount; span++)
				{
					List<Pawn> standing = new List<Pawn>();
					List<IntVec3> cells = BuiltSpanCells(r, span);
					if (cells.Count == 0)
					{
						continue;
					}
					float load = LoadOn(cells, standing);
					SpanLoadState st = RM_SuspensionMath.Classify(load, r.RatingKg);
					long key = ((long)r.id << 8) | (uint)span;
					if (st == SpanLoadState.Over && RM_SuspensionSettings.suspensionWeightCollapse)
					{
						sagging.Remove(key);
						Building_SuspensionDeck d = DeckAt(map, cells[0]);
						List<Pawn> fallers = PawnsOnCells(cells);
						foreach (IntVec3 c in cells)
						{
							ClearDeckTop(map, c);
						}
						if (d != null)
						{
							CollapseWithOwnFactionRule(d, fallers);
						}
						if (d != null && fallers.Count == 0)
						{
							Messages.Message("The " + RM_SuspensionMath.TierLabel(r.tier) + " suspension bridge gave way under its load ("
								+ RM_SuspensionMath.LoadLine(load, r.RatingKg) + ").", new TargetInfo(cells[0], map), MessageTypeDefOf.NegativeEvent);
						}
						break;   // the record's spans changed under us; next pass sees the rest
					}
					if (st != SpanLoadState.Ok)
					{
						if (sagging.Add(key))
						{
							Messages.Message("A " + RM_SuspensionMath.TierLabel(r.tier) + " suspension bridge creaks and sags: "
								+ RM_SuspensionMath.LoadLine(load, r.RatingKg) + ".", new TargetInfo(cells[0], map), MessageTypeDefOf.CautionInput);
						}
					}
					else
					{
						sagging.Remove(key);
					}
				}
			}
		}

		private List<Pawn> PawnsOnCells(List<IntVec3> cells)
		{
			List<Pawn> ps = new List<Pawn>();
			foreach (IntVec3 c in cells)
			{
				ps.AddRange(PawnsOn(map, c));
			}
			return ps;
		}

		/// <summary>SUSPENSION_UNDERPASS (construction design §1.4, the risk table's fallback, taken first): a pawn under a deck is
		/// drawn UNDER it. The deck square it stands under is drawn again over it, half see-through, so the pawn reads as beneath
		/// the deck and can still be found. (Re-layering every deck-band pawn above the deck is the alternative; it waits on a
		/// live look at 1.6's draw batching.)</summary>
		public override void MapComponentUpdate()
		{
			if (floorBand.Count == 0 || Find.CurrentMap != map)
			{
				return;
			}
			foreach (Pawn p in floorBand)
			{
				if (p == null || !p.Spawned || p.Map != map)
				{
					continue;
				}
				Building_SuspensionDeck d = RM_SuspensionUnderpass.PassingDeckAt(map, p.Position);
				float angle = 0f;
				Material mat = d == null ? null : RM_SuspensionDeckLink.TileFor(d, out angle);
				if (mat == null)
				{
					continue;
				}
				Vector3 at = p.Position.ToVector3Shifted();
				at.y = AltitudeLayer.PawnState.AltitudeFor();
				Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(at, Quaternion.AngleAxis(angle, Vector3.up), Vector3.one),
					FadedMaterialPool.FadedVersionOf(mat, UnderFade), 0);
			}
		}

		/// <summary>How opaque the deck drawn over a pawn under it is.</summary>
		public const float UnderFade = 0.6f;

		/// <summary>SUSPENSION_UNDERPASS: every 60 ticks the floor band drops anyone no longer under a deck, and a floor-band
		/// pawn that died there leaves its corpse on open floor (nothing rests under a deck).</summary>
		private void SweepUnder()
		{
			if (floorBand.Count == 0)
			{
				return;
			}
			List<Pawn> gone = null;
			foreach (Pawn p in floorBand)
			{
				if (p == null || p.Dead || !p.Spawned || p.Map != map || RM_SuspensionUnderpass.PassingDeckAt(map, p.Position) == null)
				{
					(gone = gone ?? new List<Pawn>()).Add(p);
				}
			}
			if (gone == null)
			{
				return;
			}
			foreach (Pawn p in gone)
			{
				if (floorBand.Remove(p) && BandTotal > 0)
				{
					BandTotal--;
				}
				if (p != null && p.Dead && p.Corpse != null && p.Corpse.Spawned && p.Corpse.Map == map)
				{
					RM_SuspensionUnderpass.SlideOut(p.Corpse);
				}
			}
		}

		/// <summary>A record with no part of its bridge left on any of its squares is forgotten.</summary>
		private void PruneDead()
		{
			bool changed = false;
			for (int b = bridges.Count - 1; b >= 0; b--)
			{
				SuspensionBridgeRecord r = bridges[b];
				bool any = false;
				for (int lane = 0; lane < r.width && !any; lane++)
				{
					for (int i = 0; i < r.length && !any; i++)
					{
						IntVec3 c = r.Cell(lane, i);
						if (c.InBounds(map) && AnyPartAt(map, c) && !TowerAt(map, c))
						{
							any = true;
						}
					}
				}
				if (!any)
				{
					bridges.RemoveAt(b);
					changed = true;
				}
			}
			if (changed)
			{
				Reindex();
			}
		}

		// ── collapse and swing-down ─────────────────────────────────────────────────

		/// <summary>The span holding this deck gives way whole (a square broke or was taken apart).</summary>
		public void CollapseSpan(Building_SuspensionDeck from, string how)
		{
			List<Building_SpanDeck> span = SpanDecks(from.Position);
			List<Pawn> fallers = new List<Pawn>();
			foreach (Building_SpanDeck d in span)
			{
				fallers.AddRange(PawnsOn(map, d.Position));
				ClearDeckTop(map, d.Position);
			}
			if (fallers.Count == 0)
			{
				Messages.Message("A square of a " + RM_SuspensionMath.TierLabel(from.Tier) + " suspension bridge " + how
					+ "; its whole span fell.", new TargetInfo(from.Position, map), MessageTypeDefOf.NegativeEvent);
			}
			CollapseWithOwnFactionRule(from, fallers);
		}

		/// <summary>Building_SpanDeck.Collapse with the own-faction rule: your own people are set down on an anchor first when
		/// suspensionOwnPeopleFall is off.</summary>
		private void CollapseWithOwnFactionRule(Building_SuspensionDeck d, List<Pawn> fallers)
		{
			if (!RM_SuspensionSettings.suspensionOwnPeopleFall)
			{
				SuspensionBridgeRecord r = RecordAt(d.Position);
				fallers.RemoveAll(p =>
				{
					if (p.Faction != Faction.OfPlayer)
					{
						return false;
					}
					IntVec3 safe = NearestAnchor(map, p.Position, r);
					if (!safe.IsValid)
					{
						return false;   // no anchor stands: they fall with the rest
					}
					p.Position = safe;
					p.Notify_Teleported(true, true);
					return true;
				});
			}
			d.Collapse(fallers);
		}

		/// <summary>An anchor or tower at this square went: the span(s) it held swing down from that end, square by square
		/// (setting suspensionAnchorLossFalls; off, a bridge with no anchor stays up).</summary>
		public void Notify_SupportLost(IntVec3 c)
		{
			// SUSPENSION_JETTY_BUILD_WALK_THE_PLANK: a jetty fails at the root: losing its anchor drops the whole overhang at once
			foreach (SuspensionBridgeRecord j in bridges.Where(b => b.jetty && b.Cell(0, 0) == c).ToList())
			{
				if (RM_SuspensionSettings.suspensionAnchorLossFalls && DeckAt(map, j.Cell(0, 1)) is Building_SuspensionDeck jd)
				{
					CollapseSpan(jd, "lost its anchor");
				}
			}
			SuspensionBridgeRecord r = RecordAt(c);
			if (r != null && r.jetty)
			{
				return;
			}
			if (r == null || !r.TryIndexOf(c, out int lane, out int i))
			{
				return;
			}
			bool isTower = i > 0 && i < r.length - 1;
			if (isTower)
			{
				if (BuiltAt<Building_SuspensionTower>(map, c) != null)
				{
					return;   // another built tower stands there (a rebuild blueprint or frame holds nothing up)
				}
				if (!r.towers.Remove(i))
				{
					return;   // never one of this bridge's supports (a tower refused on a drawbridge, Notify_TowerBuilt): nothing swings
				}
			}
			if (!RM_SuspensionSettings.suspensionAnchorLossFalls)
			{
				return;
			}
			List<int> sup = isTower ? RM_SuspensionMath.Supports(r.length, WithTower(r.towers, i)) : r.Supports;
			int now = Find.TickManager.TicksGame;
			int k = sup.IndexOf(i);
			// the span(s) that touched the lost support: before it (lost at its high end) and after it (lost at its low end)
			List<(List<int> cells, bool lowEnd)> lost = new List<(List<int>, bool)>();
			if (k > 0)
			{
				lost.Add((RM_SuspensionMath.SegmentCells(k - 1, sup, r.length), false));
			}
			if (k >= 0 && k < sup.Count - 1)
			{
				lost.Add((RM_SuspensionMath.SegmentCells(k, sup, r.length), true));
			}
			foreach ((List<int> cells, bool lowEnd) in lost)
			{
				List<int> order = RM_SuspensionMath.SwingOrder(cells, lowEnd);
				// an anchor carries its own lane; a tower carries every lane (it stands under the whole deck width)
				for (int l = 0; l < r.width; l++)
				{
					if (!isTower && l != lane)
					{
						continue;
					}
					for (int s = 0; s < order.Count; s++)
					{
						swing.Add(new PendingDrop { tick = now + 1 + s * RM_SuspensionMath.SwingTicksPerCell, cell = r.Cell(l, order[s]) });
					}
				}
			}
			if (lost.Count > 0)
			{
				Messages.Message("A suspension bridge lost its " + (isTower ? "tower" : "anchor") + " and is swinging down.",
					new TargetInfo(c, map), MessageTypeDefOf.NegativeEvent);
			}
		}

		private static List<int> WithTower(List<int> towers, int i)
		{
			List<int> t = new List<int>(towers);
			if (!t.Contains(i))
			{
				t.Add(i);
			}
			return t;
		}

		/// <summary>A tower was built (a rebuilt one included) in the middle of a bridge: it is one of that bridge's supports again.
		/// Never a drawbridge's (placement refuses it, PlaceWorker_SuspensionOverHole; a frame or rebuild blueprint laid before
		/// the bridge became a drawbridge is refused here, with the same reason).</summary>
		public void Notify_TowerBuilt(Building_SuspensionTower t)
		{
			SuspensionBridgeRecord r = RecordAt(t.Position);
			if (r != null && !RM_DrawbridgeMath.TowerMayJoin(r.IsDrawbridge))
			{
				Messages.Message(RM_DrawbridgeMath.TowerOnDrawbridgeRefused + " This tower holds nothing up.", new TargetInfo(t.Position, map),
					MessageTypeDefOf.RejectInput, false);
				return;
			}
			if (r != null && !r.jetty && r.TryIndexOf(t.Position, out _, out int i) && i > 0 && i < r.length - 1 && !r.towers.Contains(i))
			{
				r.towers.Add(i);
				r.towers.Sort();
			}
		}

		public void Notify_DeckBuilt(Building_SuspensionDeck d)
		{
			SuspensionBridgeRecord r = RecordAt(d.Position);
			if (r != null && r.railings)
			{
				PlaceRailing(d.Position);
			}
			// SUSPENSION_LIVE_DIAGNOSE_FIRST_REAL_RUN: a deck completed over the hole has whoever stands on its floor UNDER it
			// (the band was entered only by a walked step: live 2026-10-19 a timber span read 816 kg with one rider, 13 pawns in
			// the trench below counted on top) and what lies there slides out to open floor, or is marked under.
			if (!d.FloorBandPassesUnder)
			{
				return;
			}
			foreach (Thing t in d.Position.GetThingList(map).ToList())
			{
				if (t is Pawn p)
				{
					if (!p.Dead && !p.Flying)
					{
						SetBand(p, true);
					}
				}
				else if (t.def.category == ThingCategory.Item)
				{
					RM_SuspensionUnderpass.SlideOut(t);
				}
			}
		}

		// ── railings ────────────────────────────────────────────────────────────────

		public static Gizmo RailingGizmo(Map map, SuspensionBridgeRecord r)
		{
			if (map == null || r == null)
			{
				return null;
			}
			RM_MapComponent_SuspensionBridges b = map.GetComponent<RM_MapComponent_SuspensionBridges>();
			bool want = !r.railings;
			return new Command_Toggle
			{
				defaultLabel = "Railings: " + (r.railings ? "on" : "off"),
				defaultDesc = "Order railings built on every square of this suspension bridge (+50% of the deck's cost), or taken "
					+ "down. A railed edge never drops anyone; an open edge lets people fall off when staggered, blasted or slipping, "
					+ "and lets them jump down into the hole on purpose. Railings give no cover.",
				icon = TexCommand.ForbidOff,
				isActive = () => r.railings,
				toggleAction = () => b.SetRailings(r, want),
			};
		}

		/// <summary>Idempotent: the switch's wanted state is fixed when the gizmo is made, so a multi-selection toggling every
		/// selected square sets the one bridge once.</summary>
		public void SetRailings(SuspensionBridgeRecord r, bool on)
		{
			if (r.railings == on)
			{
				return;
			}
			r.railings = on;
			for (int lane = 0; lane < r.width; lane++)
			{
				for (int i = 1; i <= r.LastDeck; i++)
				{
					IntVec3 c = r.Cell(lane, i);
					if (on)
					{
						if (DeckAt(map, c) != null)
						{
							PlaceRailing(c);
						}
					}
					else
					{
						RemoveRailing(c);
					}
				}
			}
		}

		private void PlaceRailing(IntVec3 c)
		{
			ThingDef rail = RM_SuspensionDefOf.RM_SuspensionRailing;
			if (rail == null || RailedAt(map, c))
			{
				return;
			}
			foreach (Thing t in c.GetThingList(map))
			{
				if (t.def.entityDefToBuild == rail)
				{
					return;
				}
			}
			if (GenConstruct.CanPlaceBlueprintAt(rail, c, Rot4.North, map).Accepted)
			{
				string look = RecordAt(c)?.look;
				// RAILING_MATERIAL_FIX_MADE_OF_NOTHING: the railing is madeFromStuff, so both paths pass a material (the deck's when
				// it can make one, else the default) -- stuff null logged 'madeFromStuff but stuff=null' once per railing, live 2026-10-22.
				ThingDef stuff = RailingStuffFor(rail, StructuralDeckAt(map, c));
				if (DebugSettings.godMode)
				{
					Thing t = ThingMaker.MakeThing(rail, stuff);
					t.SetFactionDirect(Faction.OfPlayer);
					RM_SuspensionLooks.Apply(t, look);
					GenSpawn.Spawn(t, c, map, Rot4.North);
				}
				else
				{
					GenConstruct.PlaceBlueprintForBuild(rail, c, map, Rot4.North, Faction.OfPlayer, stuff, null, RM_SuspensionLooks.StyleFor(rail, look));
				}
			}
		}

		/// <summary>The railing's material: the deck's own stuff when it can make a railing, else the first cost-list material that
		/// can (a rope deck's wood, a heavy deck's steel), else the game's default for the railing. Null only for an unstuffed rail.</summary>
		public static ThingDef RailingStuffFor(ThingDef rail, Building_SuspensionDeck deck)
		{
			if (rail == null || !rail.MadeFromStuff)
			{
				return null;
			}
			if (deck != null)
			{
				if (deck.Stuff != null && deck.Stuff.stuffProps != null && deck.Stuff.stuffProps.CanMake(rail))
				{
					return deck.Stuff;
				}
				if (deck.def.costList != null)
				{
					foreach (ThingDefCountClass tc in deck.def.costList)
					{
						if (tc.thingDef != null && tc.thingDef.IsStuff && tc.thingDef.stuffProps.CanMake(rail))
						{
							return tc.thingDef;
						}
					}
				}
			}
			return GenStuff.DefaultStuffFor(rail);
		}

		private void RemoveRailing(IntVec3 c)
		{
			List<Thing> things = new List<Thing>(c.GetThingList(map));
			foreach (Thing t in things)
			{
				if (t.def.entityDefToBuild == RM_SuspensionDefOf.RM_SuspensionRailing && (t.def.IsBlueprint || t.def.IsFrame))
				{
					t.Destroy(DestroyMode.Cancel);
				}
				else if (t is Building_SuspensionRailing rail)
				{
					if (DebugSettings.godMode)
					{
						rail.Destroy(DestroyMode.Vanish);
					}
					else if (map.designationManager.DesignationOn(rail, DesignationDefOf.Deconstruct) == null)
					{
						map.designationManager.AddDesignation(new Designation(rail, DesignationDefOf.Deconstruct));
					}
				}
			}
		}

		// ── accidental falls off an open edge ─────────────────────────────────────────

		/// <summary>A stagger, blast or slime slip on a deck square with an open edge drops the pawn into the hole beside it
		/// with this chance (0 on a railed square): the existing descent event, fall damage by metres.</summary>
		public static bool TryKnockOff(Pawn p, float chance, string why)
		{
			if (p == null || !p.Spawned || p.Dead || p.Flying)
			{
				return false;
			}
			Map map = p.Map;
			IntVec3 c = p.Position;
			Building_SuspensionDeck deckHere = DeckAt(map, c);
			if (deckHere == null || RM_SuspensionUnderpass.InFloorBand(p))
			{
				return false;   // not on a deck (a pawn under it, in the floor band, is already down in the hole)
			}
			IntVec3 open = OpenEdgeBeside(map, c);
			float ch = RM_SuspensionMath.FallChance(chance, RailedAt(map, c), open.IsValid);
			if (ch <= 0f || !Rand.Chance(ch))
			{
				return false;
			}
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			RM_SuperdeepTrapState state = ex?.SuperdeepTrap;
			if (state == null)
			{
				return false;
			}
			p.jobs?.StopAll();
			p.pather?.StopDead();
			p.Position = open;
			p.Notify_Teleported(true, true);
			// a sunken deck's rider falls from the deck's height, as Drop and Collapse already count it
			RM_SuperdeepTrap.OnForcedDescent(p, open, state, System.Math.Max(0, ex.ClimbDepthAt(open) - deckHere.DeckNotches));
			Messages.Message(p.LabelShort + " was " + why + " off the edge of a suspension bridge.", new LookTargets(p),
				MessageTypeDefOf.NegativeEvent);
			return true;
		}

		// ── inspect ─────────────────────────────────────────────────────────────────

		public string InspectLines(SuspensionBridgeRecord r, IntVec3 at)
		{
			List<string> lines = new List<string>();
			int span = 0;
			if (r.TryIndexOf(at, out _, out int i))
			{
				span = r.SpanOfIndex(i);
			}
			float load = SpanLoad(r, span);
			Building_SuspensionDeck d0 = DeckAt(map, at) ?? (r.length > 1 ? DeckAt(map, r.Cell(0, 1)) : null);
			if (r.jetty)
			{
				lines.Add(RM_SuspensionMath.JettyReadoutLine(r.tier, load, r.RatingKg, r.deckNotches));
				lines.Add(RM_SuspensionMath.LoadLine(load, r.RatingKg) + " (one person's weight)");
				if (RM_SuspensionMath.Classify(load, r.RatingKg) != SpanLoadState.Ok)
				{
					lines.Add("Sagging: any more weight and the whole jetty drops at the root.");
				}
				lines.Add("Reaches " + (r.length - 1) + " / " + RM_SuspensionMath.JettyMaxCells + " squares out · railings " + (r.railings ? "on" : "off"));
				return string.Join("\n", lines);
			}
			lines.Add(RM_SuspensionMath.ReadoutLine(r.tier, load, r.RatingKg, r.deckNotches, d0 != null && d0.FloorBandPassesUnder));
			lines.Add(RM_SuspensionMath.LoadLine(load, r.RatingKg) + (r.SpanCount > 1 ? " (span " + (span + 1) + " of " + r.SpanCount + ")" : ""));
			if (RM_SuspensionMath.Classify(load, r.RatingKg) != SpanLoadState.Ok)
			{
				lines.Add(RM_SuspensionSettings.suspensionWeightCollapse
					? "Sagging: near its rating. Any more weight and the whole span gives way."
					: "Over its rating (weight collapse is off in Mod Settings).");
			}
			List<int> sup = r.Supports;
			int run = sup[span + 1] - sup[span] - 1;
			lines.Add("Span " + run + " / " + RM_SuspensionMath.MaxLength(r.tier, RM_SuspensionSettings.suspensionLengthMultiplier)
				+ " squares between supports · " + r.width + " wide · railings " + (r.railings ? "on" : "off"));
			return string.Join("\n", lines);
		}
	}
}
