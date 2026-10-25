using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>DIG_SPOIL_BUILD_GRAVEL_PAYS_ITS_WAY + PIT_DIG_FIX_SAND_SLIDES_BACK_IN (owner 2026-10-25): "you can't dig in sand
	/// or mud (just slides back in)"; rock ground "produces a chunk or gravel"; "it takes 1 gravel or 2 chunks to put it all
	/// back in again"; "Dirt makes no chunks". The Verse side of <see cref="RM_GroundClassMath"/>.</summary>
	public static class RM_DigSpoil
	{
		public const string SlidesBackReason = "Sand and mud slide back in: they cannot be dug.";

		public static RM_GroundClass ClassOf(TerrainDef t)
		{
			if (t == null)
			{
				return RM_GroundClass.NotDiggable;
			}
			return RM_GroundClassMath.Classify(t.defName, t.IsWater, t.layerable, RM_DigDiscovery.RockOfTerrain(t) != null,
				t.IsSoil, Diggable(t), t.categoryType.ToString());
		}

		private static bool Diggable(TerrainDef t)
		{
			if (t.affordances == null)
			{
				return false;
			}
			foreach (TerrainAffordanceDef a in t.affordances)
			{
				if (a.defName == "Diggable")
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>The ground a cut at <paramref name="c"/> goes through: the terrain FlowWorks saved before its first cut, else
		/// what is on top now (foundation first, as the dig gate reads it).</summary>
		public static TerrainDef GroundAt(Map map, IntVec3 c)
		{
			return map.GetComponent<RM_MapComponent_Excavation>()?.OriginalTerrainAt(c)
				?? (map.terrainGrid.FoundationAt(c) ?? map.terrainGrid.TopTerrainAt(c));
		}

		public static RM_GroundClass ClassAt(Map map, IntVec3 c)
		{
			return ClassOf(GroundAt(map, c));
		}

		/// <summary>Card ruling 2026-10-25: rubble digs at rock speed.</summary>
		public static bool IsRubbleAt(Map map, IntVec3 c)
		{
			return RimMandrakeFlowWorksSettings.digSpoilEnabled && ClassAt(map, c) == RM_GroundClass.Rubble;
		}

		/// <summary>ICE_DIG_BUILD_CRUSHED_ICE_MELTS_DOWN: ice and packed snow dig at rock speed.</summary>
		public static bool IsIceAt(Map map, IntVec3 c)
		{
			return RimMandrakeFlowWorksSettings.iceDigEnabled && ClassAt(map, c) == RM_GroundClass.Ice;
		}

		/// <summary>The one ground gate the designator and the work giver share. <paramref name="terrain"/> is the cell's top
		/// terrain as the caller read it; a dug cell is judged by the ground it was cut from. Null: may be dug.</summary>
		public static string DigRefusal(Map map, IntVec3 c, TerrainDef terrain, bool surface)
		{
			if (RimMandrakeFlowWorksSettings.sandMudSlidesBackEnabled)
			{
				TerrainDef ground = surface ? terrain : (map.GetComponent<RM_MapComponent_Excavation>()?.OriginalTerrainAt(c));
				if (ground != null && ClassOf(ground) == RM_GroundClass.Slumps)
				{
					return SlidesBackReason;
				}
			}
			if (!surface)
			{
				return null;
			}
			if (terrain.IsSoil || (RimMandrakeFlowWorksSettings.digRockGroundEnabled && RM_DigDiscovery.RockOfTerrain(terrain) != null))
			{
				return null;
			}
			if (RimMandrakeFlowWorksSettings.digSpoilEnabled && ClassOf(terrain) == RM_GroundClass.Rubble)
			{
				return null;
			}
			// ICE_DIG_BUILD_CRUSHED_ICE_MELTS_DOWN (owner card 2026-10-25): "Ice is definitely diggable."
			if (RimMandrakeFlowWorksSettings.iceDigEnabled && ClassOf(terrain) == RM_GroundClass.Ice)
			{
				return null;
			}
			return "Must designate diggable soil, rubble, ice or bare rock ground.";
		}

		/// <summary>One gravel on the lip of the cut (merges into a stack there when it can). True when placed.</summary>
		public static bool PlaceGravel(Map map, IntVec3 near, bool forbid)
		{
			return PlaceSpoil(map, RimMandrakeFlowWorks_DefOf.RM_Gravel, near, forbid);
		}

		/// <summary>One unit of <paramref name="def"/> (gravel, crushed ice) on the lip of the cut. True when placed.</summary>
		public static bool PlaceSpoil(Map map, ThingDef def, IntVec3 near, bool forbid)
		{
			if (def == null || map == null)
			{
				return false;
			}
			Thing made = ThingMaker.MakeThing(def);
			made.stackCount = 1;
			if (!GenPlace.TryPlaceThing(made, near, map, ThingPlaceMode.Near, out Thing placed))
			{
				if (!made.Destroyed)
				{
					made.Destroy();
				}
				return false;
			}
			if (forbid && placed != null && !placed.Destroyed)
			{
				placed.SetForbidden(true, false);
			}
			return true;
		}

		public static bool IsStoneChunk(ThingDef d)
		{
			return d != null && d.thingCategories != null && d.thingCategories.Contains(ThingCategoryDefOf.StoneChunks);
		}

		/// <summary>What a fill material is, for its credit (RM_GroundClassMath.CreditOf): gravel, crushed ice, a stone chunk, or
		/// none (not fill material).</summary>
		public static RM_CutSpoil FillKindOf(ThingDef d)
		{
			if (d == null)
			{
				return RM_CutSpoil.None;
			}
			if (d == RimMandrakeFlowWorks_DefOf.RM_Gravel)
			{
				return RM_CutSpoil.Gravel;
			}
			if (d == RimMandrakeFlowWorks_DefOf.RM_CrushedIce)
			{
				return RM_CutSpoil.CrushedIce;
			}
			return IsStoneChunk(d) ? RM_CutSpoil.Chunk : RM_CutSpoil.None;
		}

		/// <summary>The material a filler fetches: the nearest reachable, unforbidden gravel it can take one of, else crushed ice,
		/// else the nearest stone chunk, within <paramref name="maxDistance"/>. Null when there is none.</summary>
		public static Thing FindFillMaterial(Pawn pawn, bool forced, float maxDistance = 9999f)
		{
			System.Predicate<Thing> ok = t => !t.IsForbidden(pawn) && pawn.CanReserve(t, 10, 1, null, forced);
			// ICE_DIG_BUILD_CRUSHED_ICE_MELTS_DOWN: crushed ice is a full load as gravel is, after gravel (it keeps no better)
			foreach (ThingDef def in new[] { RimMandrakeFlowWorks_DefOf.RM_Gravel, RimMandrakeFlowWorks_DefOf.RM_CrushedIce })
			{
				Thing found = def == null ? null : GenClosest.ClosestThingReachable(pawn.Position, pawn.Map, ThingRequest.ForDef(def),
					PathEndMode.ClosestTouch, TraverseParms.For(pawn), maxDistance, ok);
				if (found != null)
				{
					return found;
				}
			}
			return GenClosest.ClosestThingReachable(pawn.Position, pawn.Map, ThingRequest.ForGroup(ThingRequestGroup.Chunk),
				PathEndMode.ClosestTouch, TraverseParms.For(pawn), maxDistance, t => IsStoneChunk(t.def) && ok(t));
		}
	}

	/// <summary>Fill credit per cell: material already tipped into a pit toward its next notch (gravel 2, chunk 1, a notch 2).
	/// A new cut clears it: re-digging throws the tipped material out with the rest.</summary>
	public class RM_MapComponent_FillCredit : MapComponent
	{
		private Dictionary<int, int> credit = new Dictionary<int, int>();

		public RM_MapComponent_FillCredit(Map map) : base(map)
		{
		}

		public int CreditAt(IntVec3 c)
		{
			return c.InBounds(map) && credit.TryGetValue(map.cellIndices.CellToIndex(c), out int v) ? v : 0;
		}

		public void SetCredit(IntVec3 c, int v)
		{
			if (!c.InBounds(map))
			{
				return;
			}
			int i = map.cellIndices.CellToIndex(c);
			if (v <= 0)
			{
				credit.Remove(i);
			}
			else
			{
				credit[i] = v;
			}
		}

		public void AddCredit(IntVec3 c, int v)
		{
			SetCredit(c, CreditAt(c) + v);
		}

		public void ClearCredit(IntVec3 c)
		{
			SetCredit(c, 0);
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Collections.Look(ref credit, "rmFillCredit", LookMode.Value, LookMode.Value);
			if (credit == null)
			{
				credit = new Dictionary<int, int>();
			}
		}
	}

	/// <summary>On RM_Gravel: the recipes (defNames) whose stone-chunk ingredient also takes gravel. Missing recipes (a mod not
	/// loaded) are skipped silently.</summary>
	public class RM_GravelRecipes : DefModExtension
	{
		public List<string> recipes = new List<string>();
	}

	/// <summary>Owner: gravel "should be able to satisfy some recipies for items that might otherwise consume blocks or chunks".
	/// At startup, each listed recipe's stone-chunk ingredient, its fixed filter and its default filter allow gravel. Bills
	/// already in a save keep their own filters (the player ticks gravel in).</summary>
	[StaticConstructorOnStartup]
	public static class RM_GravelRecipeApplier
	{
		public static int Applied;

		static RM_GravelRecipeApplier()
		{
			ThingDef gravel = RimMandrakeFlowWorks_DefOf.RM_Gravel;
			RM_GravelRecipes ext = gravel?.GetModExtension<RM_GravelRecipes>();
			if (!RimMandrakeFlowWorksSettings.gravelRecipesEnabled || ext == null)
			{
				return;
			}
			ThingDef anyChunk = null;
			foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
			{
				if (RM_DigSpoil.IsStoneChunk(d))
				{
					anyChunk = d;
					break;
				}
			}
			foreach (string name in ext.recipes)
			{
				RecipeDef r = DefDatabase<RecipeDef>.GetNamedSilentFail(name);
				if (r == null)
				{
					continue;
				}
				IngredientCount ing = null;
				if (anyChunk != null && r.ingredients != null)
				{
					foreach (IngredientCount i in r.ingredients)
					{
						if (i.filter != null && i.filter.Allows(anyChunk))
						{
							ing = i;
							break;
						}
					}
				}
				if (ing == null)
				{
					Log.Warning("[RimMandrake FlowWorks] gravel recipes: " + name + " has no stone-chunk ingredient; left as it is.");
					continue;
				}
				ing.filter.SetAllow(gravel, true);
				r.fixedIngredientFilter?.SetAllow(gravel, true);
				r.defaultIngredientFilter?.SetAllow(gravel, true);
				Applied++;
			}
		}
	}

	/// <summary>Owner: mining normal rock "should now also produce the same material as the ground digging when it fails to
	/// produce a chunk". A colonist (any pawn) mining a natural non-resource rock whose yield is a stone chunk, when the
	/// vanilla roll drops no chunk, leaves 1 gravel. Explosions (no pawn) leave nothing extra. Forbidden as vanilla forbids
	/// the chunk: when the miner is not of the player's faction. The (Map, bool, Pawn) overload by type: 1.6 also keeps an
	/// [Obsolete] (Map, float, bool, Pawn) one, and a name-only target is ambiguous.</summary>
	[HarmonyPatch(typeof(Mineable), "TrySpawnYield", new[] { typeof(Map), typeof(bool), typeof(Pawn) })]
	[RimMandrake.Shared.PatchFeature("Mining leaves gravel when no chunk drops", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "mineGravelEnabled")]
	public static class RM_Patch_MineGravel
	{
		/// <summary>Bridge/proof: gravel this patch has placed since load.</summary>
		public static int Placed;

		public static void Prefix(Mineable __instance, Map map, Pawn pawn, out int __state)
		{
			__state = -1;
			if (!RimMandrakeFlowWorksSettings.mineGravelEnabled || pawn == null || map == null || __instance?.def?.building == null)
			{
				return;
			}
			ThingDef chunk = __instance.def.building.mineableThing;
			if (!__instance.def.IsNonResourceNaturalRock || !RM_DigSpoil.IsStoneChunk(chunk))
			{
				return;
			}
			__state = CountOf(map, chunk);
		}

		public static void Postfix(Mineable __instance, Map map, Pawn pawn, int __state)
		{
			if (__state < 0)
			{
				return;
			}
			if (!RM_GroundClassMath.MiningGivesGravel(__state, CountOf(map, __instance.def.building.mineableThing)))
			{
				return;
			}
			if (RM_DigSpoil.PlaceGravel(map, __instance.Position, pawn.Faction != Faction.OfPlayer))
			{
				Placed++;
			}
		}

		private static int CountOf(Map map, ThingDef def)
		{
			int n = 0;
			foreach (Thing t in map.listerThings.ThingsOfDef(def))
			{
				n += t.stackCount;
			}
			return n;
		}
	}
}
