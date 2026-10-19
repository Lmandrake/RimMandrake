using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Pits
{
	/// <summary>
	/// SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT (stage S0, design/RimMandrake/flowworks_bridges_design_2026-10-17.md §1,
	/// §2, §6): the span base the whole suspension family builds on, lifted out of Building_PitCover with no behaviour
	/// change. A span deck is a 1×1 non-edifice building that turns the cell under it into walking ground at its deck
	/// height; neighbouring decks that join form one SPAN, whose mass is summed together and which gives way whole,
	/// dropping everyone on it through the pit's own descent event.
	///
	/// Extension points for the siblings (each defaults to the pit cover's behaviour):
	///   * DeckHeightM — metres below ground (0 = surface); a sunken deck overrides it (UNDERPASS item).
	///   * FloorBandPassesUnder — pawns in the hole walk under it (UNDERPASS item); never for a cover.
	///   * Grated — fire and spilled liquid pass (GRATE item); RM_SpanUtility reads it, nothing acts on it yet.
	///   * LoadRatingKg — the span's rating; RM_SpanUtility.LoadOn sums the mass (POSTS item shows it).
	///   * JoinsSpan / SpanCells — which decks form one span (covers: 4-way connected covers; bridges: cells between supports).
	///   * CollapseSaveKey, CollapseMessage — save key and the letter/message on giving way.
	/// </summary>
	public abstract class Building_SpanDeck : Building
	{
		protected bool collapsed;

		/// <summary>Intact and on the map: the cell is walking ground at DeckHeightM.</summary>
		public bool Decked => !collapsed && Spawned;

		public bool Collapsed => collapsed;

		public virtual float DeckHeightM => 0f;

		public virtual bool FloorBandPassesUnder => false;

		public virtual bool Grated => false;

		public virtual float LoadRatingKg => float.PositiveInfinity;

		public int DeckNotches => RM_SpanMath.Notches(DeckHeightM);

		public RM_SpanMath.DeckRead Read => Decked
			? new RM_SpanMath.DeckRead(true, DeckHeightM, FloorBandPassesUnder) : RM_SpanMath.DeckRead.None;

		/// <summary>The save key of the collapsed flag (a cover keeps its old "rmCoverSprung" so saves load unchanged).</summary>
		protected virtual string CollapseSaveKey => "rmSpanCollapsed";

		/// <summary>Whether a neighbouring deck belongs to this span. Default: the same kind of deck at the same height.</summary>
		public virtual bool JoinsSpan(Building_SpanDeck other)
		{
			return other != null && other.GetType() == GetType() && other.DeckNotches == DeckNotches;
		}

		/// <summary>Every intact deck of this span, this one included.</summary>
		public virtual List<Building_SpanDeck> SpanCells()
		{
			return RM_SpanUtility.ConnectedSpan(this);
		}

		// A deck is ground (at its height) in the pocket grid, so its coming and going moves the climb generation
		// (PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP, design §8.3, GPT #12).
		public override void SpawnSetup(Map map, bool respawningAfterLoad)
		{
			base.SpawnSetup(map, respawningAfterLoad);
			RM_SuperdeepTrap.EngineOf(map)?.BumpClimbGeneration();
		}

		public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
		{
			Map map = Map;
			base.DeSpawn(mode);
			RM_SuperdeepTrap.EngineOf(map)?.BumpClimbGeneration();
		}

		/// <summary>The whole span gives way at once: every deck is marked and destroyed (rubble left) BEFORE the pawns on it
		/// descend through the superdeep trap's own descent event (fall damage, then whatever hooks PitDescent).</summary>
		public void Collapse(List<Pawn> fallers)
		{
			if (collapsed || !Spawned)
			{
				return;
			}
			Map map = Map;
			List<Building_SpanDeck> span = SpanCells();
			int deck = DeckNotches; // read while still spawned: a suspension deck's height comes from Map's record
			foreach (Building_SpanDeck c in span)
			{
				c.collapsed = true;
			}
			foreach (Building_SpanDeck c in span)
			{
				if (c.Spawned)
				{
					FilthMaker.TryMakeFilth(c.Position, map, ThingDefOf.Filth_RubbleRock, 1);
					c.Destroy(DestroyMode.Vanish);
				}
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			RM_SuperdeepTrapState state = eng?.SuperdeepTrap;
			Pawn first = null;
			foreach (Pawn p in fallers)
			{
				if (p == null || !p.Spawned || p.Dead || p.Flying)
				{
					continue;
				}
				if (state != null)
				{
					// SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD: a sunken deck's riders fall from its height, not the surface
					RM_SuperdeepTrap.OnForcedDescent(p, p.Position, state, deck > 0 && eng != null ? System.Math.Max(0, eng.ClimbDepthAt(p.Position) - deck) : -1);
				}
				first = first ?? p;
			}
			if (first != null)
			{
				CollapseMessage(first, fallers);
			}
		}

		protected virtual void CollapseMessage(Pawn first, List<Pawn> fallers)
		{
			Messages.Message(LabelCap + " gave way under " + first.LabelShort + (fallers.Count > 1 ? " and others." : "."),
				new LookTargets(fallers), MessageTypeDefOf.NeutralEvent);
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Values.Look(ref collapsed, CollapseSaveKey, false);
		}
	}

	/// <summary>The one read every walking system makes of a deck (design §1: the seven "is it covered" call sites).</summary>
	public static class RM_SpanUtility
	{
		/// <summary>The intact deck on this cell, or null.</summary>
		public static Building_SpanDeck DeckAt(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map))
			{
				return null;
			}
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i] is Building_SpanDeck deck && deck.Decked)
				{
					return deck;
				}
			}
			return null;
		}

		public static RM_SpanMath.DeckRead ReadAt(Map map, IntVec3 c)
		{
			Building_SpanDeck deck = DeckAt(map, c);
			return deck == null ? RM_SpanMath.DeckRead.None : deck.Read;
		}

		/// <summary>Is this cell walking ground on a deck? deckHeightM is the walking height (metres below ground, 0 = surface);
		/// floorBandPassesUnder says pawns in the hole walk beneath it (always false for a pit cover).</summary>
		public static bool DeckedAt(Map map, IntVec3 c, out float deckHeightM, out bool floorBandPassesUnder)
		{
			RM_SpanMath.DeckRead r = ReadAt(map, c);
			deckHeightM = r.DeckHeightM;
			floorBandPassesUnder = r.FloorBandPassesUnder;
			return r.Decked;
		}

		public static bool DeckedAt(Map map, IntVec3 c, out float deckHeightM)
		{
			return DeckedAt(map, c, out deckHeightM, out _);
		}

		public static bool DeckedAt(Map map, IntVec3 c)
		{
			return DeckAt(map, c) != null;
		}

		/// <summary>The depth (notches) a walker reads on this cell: the deck's height when decked, the floor otherwise.</summary>
		public static int WalkingDepth(Map map, IntVec3 c, int floorNotches)
		{
			return floorNotches > 0 ? RM_SpanMath.WalkingDepth(floorNotches, ReadAt(map, c)) : floorNotches;
		}

		/// <summary>Every intact deck 4-way connected to start through decks that join its span (no size cap: the flood is
		/// bounded by the decks built, COVER_DECK_TUNE_QUADRATIC_CENSUS).</summary>
		public static List<Building_SpanDeck> ConnectedSpan(Building_SpanDeck start)
		{
			List<Building_SpanDeck> span = new List<Building_SpanDeck>();
			if (start == null || !start.Spawned)
			{
				return span;
			}
			Map map = start.Map;
			HashSet<IntVec3> seen = new HashSet<IntVec3> { start.Position };
			Queue<IntVec3> open = new Queue<IntVec3>();
			open.Enqueue(start.Position);
			while (open.Count > 0)
			{
				Building_SpanDeck d = DeckAt(map, open.Dequeue());
				if (d == null || (d != start && !start.JoinsSpan(d)))
				{
					continue;
				}
				span.Add(d);
				for (int i = 0; i < 4; i++)
				{
					IntVec3 n = d.Position + GenAdj.CardinalDirections[i];
					if (seen.Add(n) && start.JoinsSpan(DeckAt(map, n)))
					{
						open.Enqueue(n);
					}
				}
			}
			return span;
		}

		/// <summary>The mass on these deck cells (StatDefOf.Mass: body plus gear and inventory) of every living, walking pawn,
		/// each added to standing. The owner's own faction counts only when countOwnFaction is on (the
		/// superdeepCapturesOwnFaction carve-out). Items and buildings on a deck are the POSTS item's to add.</summary>
		public static float LoadOn(Map map, List<IntVec3> cells, Faction owner, bool countOwnFaction, List<Pawn> standing)
		{
			float sum = 0f;
			if (map == null || cells == null)
			{
				return sum;
			}
			foreach (IntVec3 cell in cells)
			{
				List<Thing> thingsHere = cell.GetThingList(map);
				for (int i = 0; i < thingsHere.Count; i++)
				{
					// SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD: a pawn under the deck (floor band) weighs nothing on it
				if (thingsHere[i] is Pawn p && !p.Dead && !p.Flying && (p.Faction != owner || countOwnFaction)
					&& !RM_SuspensionUnderpass.InFloorBand(p))
					{
						standing?.Add(p);
						sum += p.GetStatValue(StatDefOf.Mass);
					}
				}
			}
			return sum;
		}
	}
}
