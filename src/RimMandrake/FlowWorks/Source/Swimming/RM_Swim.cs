using System.Collections.Generic;
using HarmonyLib;
using RimMandrake.FlowWorks.LiquidTypes;
using RimMandrake.FlowWorks.ManyWaters;
using RimWorld;
using Unity.Collections;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks.Swimming
{
	// ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
	// DEEP_WATER_BUILD_SWIM_OR_SINK (plan P12 of FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG). Owner R12, 2026-10-17 by card:
	// "pawns may swim in water 2 m or deeper", in lakes, canals and pits alike; non-water fluids keep the no-swim refusal; deep
	// water stops being a barrier for pits and trenches.
	//
	// PASSABLE DEEP BAND, by the PATH GRID, not the def (item step 1, "pick one and record why"): vanilla WaterDeep keeps its
	// identity AND its <passability>Impassable</passability>. Every def-level reader of "deep water" (roads
	// RoadDefGenStep_DryWithFallback, GenStep_RemoveTinyIslands, stockpile and fishing zone designators, the deep scanner, the
	// terraformer, the gravship area, BaseGen floors, RM_Volume.BedLevels) keeps vanilla's answer. Only PathGrid.CalculatedCostAt
	// (the one source of Walkable, Standable and the region types) answers a swim cost instead of 10000 on a swim square, so
	// regions, reachability and the pathfinder see open water. Items never land on a swim square (GenSpawn.CanSpawnAt) and drop
	// pods never aim at one (DropCellFinder.IsGoodDropSpot).
	//
	// WHO and HOW FAST: RM_SwimMath (Verse-free, SelfTest). Drowning stays ONE rule (P7 V2, RM_Drowning.PerCheck): this file
	// plugs the swim rule into RM_Drowning.keepsHeadUp and runs PerCheck on natural deep water too.
	// ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

	/// <summary>Mod Settings for swimming (superb-settings rule: on/off per feature, a number where the number is the
	/// experience; defaults = the shipped behaviour). Scribed into the FlowWorks settings file.</summary>
	public static class RM_SwimSettings
	{
		/// <summary>Master (R12): deep water is swimmable. Off: vanilla, deep water blocks walking; pits keep the old rule (a
		/// creature with a swimming graphic keeps its head up).</summary>
		public static bool deepSwimEnabled = true;
		/// <summary>Also the ocean and deep moving water (R12 names lakes, canals and pits; the open sea is the map edge). Off.</summary>
		public static bool swimOpenWaterEnabled = false;
		public static bool humanlikesSwim = true;
		public static bool mechanoidsSink = true;
		public static int swimPathCost = RM_SwimMath.DefaultSwimPathCost;
		public static float swimEnduranceHours = RM_SwimMath.DefaultEnduranceHours;
		public static float swimRecoveryHours = RM_SwimMath.DefaultRecoveryHours;
		public static float swimWeightEndurancePenalty = RM_SwimMath.DefaultWeightEndurancePenalty;
		public static float swimWeightSlowdown = RM_SwimMath.DefaultWeightSlowdown;
		public static bool animalsAvoidDeepWater = true;
		public static int animalAvoidCost = RM_SwimMath.DefaultAnimalAvoidCost;
		public static float swimWarnAt = RM_SwimMath.DefaultWarnAt;
		public static bool tiredSwimmersHeadForShore = true;
		public static bool deepSwimJoyEnabled = true;

		public static void ExposeData()
		{
			Scribe_Values.Look(ref deepSwimEnabled, "deepSwimEnabled", true);
			Scribe_Values.Look(ref swimOpenWaterEnabled, "swimOpenWaterEnabled", false);
			Scribe_Values.Look(ref humanlikesSwim, "humanlikesSwim", true);
			Scribe_Values.Look(ref mechanoidsSink, "mechanoidsSink", true);
			Scribe_Values.Look(ref swimPathCost, "swimPathCost", RM_SwimMath.DefaultSwimPathCost);
			Scribe_Values.Look(ref swimEnduranceHours, "swimEnduranceHours", RM_SwimMath.DefaultEnduranceHours);
			Scribe_Values.Look(ref swimRecoveryHours, "swimRecoveryHours", RM_SwimMath.DefaultRecoveryHours);
			Scribe_Values.Look(ref swimWeightEndurancePenalty, "swimWeightEndurancePenalty", RM_SwimMath.DefaultWeightEndurancePenalty);
			Scribe_Values.Look(ref swimWeightSlowdown, "swimWeightSlowdown", RM_SwimMath.DefaultWeightSlowdown);
			Scribe_Values.Look(ref animalsAvoidDeepWater, "animalsAvoidDeepWater", true);
			Scribe_Values.Look(ref animalAvoidCost, "animalAvoidCost", RM_SwimMath.DefaultAnimalAvoidCost);
			Scribe_Values.Look(ref swimWarnAt, "swimWarnAt", RM_SwimMath.DefaultWarnAt);
			Scribe_Values.Look(ref tiredSwimmersHeadForShore, "tiredSwimmersHeadForShore", true);
			Scribe_Values.Look(ref deepSwimJoyEnabled, "deepSwimJoyEnabled", true);
		}

		public static void DoSettingsSection(Listing_Standard list)
		{
			list.GapLine();
			list.Label("Swimming in deep water");
			list.CheckboxLabeled("People and animals can swim in water 2 m and deeper", ref deepSwimEnabled,
				"Deep lake water, and deep water in dug canals and pits, can be swum. Swimmers are slower than waders, tire, are "
				+ "warned when tiring, and drown if they cannot reach footing before they are exhausted. Mechanoids and anyone too "
				+ "heavily loaded sink and are never routed into deep water. Oil, slime, tar, propane, boiling water and brine are "
				+ "never swum. Off: deep water blocks walking, as in the base game. Changing this re-reads every map's paths.");
			GUI.enabled = deepSwimEnabled;
			list.CheckboxLabeled("  Also the ocean and deep river water (not supported)", ref swimOpenWaterEnabled,
				"The ruling covers lakes, canals and pits. On: deep ocean and deep river squares are swimmable too, which opens "
				+ "map edges to swimmers. Off (shipped): those stay impassable.");
			list.CheckboxLabeled("  People can swim", ref humanlikesSwim,
				"On: every person swims (and tires). Off: people sink like mechanoids and never enter deep water; creatures that "
				+ "swim by race or gene still do.");
			list.CheckboxLabeled("  Mechanoids sink", ref mechanoidsSink,
				"On: mechanoids never enter deep water and drown if forced into it. Off: they swim like animals.");
			list.Label("  Swim cost per square: " + swimPathCost + "  (walking adds 0, wading chest-deep 42; shipped 60)");
			swimPathCost = Mathf.RoundToInt(list.Slider(swimPathCost, 30f, 300f) / 5f) * 5;
			list.Label("  Endurance: " + swimEnduranceHours.ToString("0.0#") + " h for an unloaded healthy person (shipped 2)");
			swimEnduranceHours = Mathf.Round(list.Slider(swimEnduranceHours, 0.25f, 12f) * 4f) / 4f;
			list.Label("  Recovery on footing: " + swimRecoveryHours.ToString("0.0#") + " h from exhausted (shipped 1)");
			swimRecoveryHours = Mathf.Round(list.Slider(swimRecoveryHours, 0.25f, 6f) * 4f) / 4f;
			list.Label("  Weight shortens endurance: x(1 - " + swimWeightEndurancePenalty.ToString("0.00") + " x load)  (load = gear, "
				+ "inventory and carried mass over carrying capacity; shipped 1.25: sinks past 72% load)");
			swimWeightEndurancePenalty = Mathf.Round(list.Slider(swimWeightEndurancePenalty, 0f, 3f) * 20f) / 20f;
			list.Label("  Weight slows swimming: x(1 + " + swimWeightSlowdown.ToString("0.00") + " x load)  (shipped 1.5)");
			swimWeightSlowdown = Mathf.Round(list.Slider(swimWeightSlowdown, 0f, 4f) * 20f) / 20f;
			list.Label("  Warn when exhaustion reaches " + swimWarnAt.ToStringPercent() + "  (shipped 70%)");
			swimWarnAt = Mathf.Round(list.Slider(swimWarnAt, 0.3f, 0.95f) * 20f) / 20f;
			list.CheckboxLabeled("  Tired swimmers head for the nearest footing", ref tiredSwimmersHeadForShore,
				"On: at the warning, a swimmer who is not drafted (and any creature not under your command) drops what it is "
				+ "doing and swims to the nearest square where it can stand. Drafted colonists obey you. Off: only the warning.");
			list.CheckboxLabeled("  Land animals walk around deep water", ref animalsAvoidDeepWater,
				"On: animals that do not swim by nature (no water cost in their race) route around deep water unless there is no "
				+ "other way. Off: they swim it like people.");
			if (animalsAvoidDeepWater)
			{
				list.Label("  Animal detour cost per deep square: " + animalAvoidCost + "  (shipped 3000)");
				animalAvoidCost = Mathf.RoundToInt(list.Slider(animalAvoidCost, 100f, 9000f) / 100f) * 100;
			}
			list.CheckboxLabeled("  Swimming for fun in deep water", ref deepSwimJoyEnabled,
				"On: the Odyssey 'go swimming' pastime may use deep water, for rested swimmers only. Off: shallows only.");
			GUI.enabled = true;
		}
	}

	/// <summary>Which squares are swum, how deep the water is, and whether the liquid there may be swum.</summary>
	[StaticConstructorOnStartup]
	public static class RM_SwimWater
	{
		private static bool[] swimTerrain;
		private static bool[] swimmableLiquid;
		private static Dictionary<TerrainDef, LiquidDef> liquidByTerrain;
		// Ints, not strings: EnsureTables runs on every IsSwimTerrain call (Reachability.CanReach, the path grid), so the
		// fingerprint must not allocate. tableFingerprint = what the tables were built for; appliedFingerprint = what the maps'
		// path grids were last computed under (Reapply's own, so a table rebuild between a settings change and Reapply cannot
		// hide the change from it). The swim cost is in it: CalculatedCostAt bakes it into every map's path grid.
		private static int tableFingerprint = -1;
		private static int appliedFingerprint = -1;

		/// <summary>Liquids a creature may swim in (the liquid matrix): fresh, salt and icy water. Everything else (oil, slime,
		/// tar, propane, boiling, poisoned, acid, brine, lava) refuses.</summary>
		public static readonly HashSet<string> SwimLiquids = new HashSet<string> { "RM_Liquid_FreshWater", "RM_Liquid_SaltWater", "RM_Liquid_IcyWater" };

		/// <summary>Dug-pit fluids a creature may swim in.</summary>
		public static readonly HashSet<string> SwimFluids = new HashSet<string> { "RM_Fluid_Water", "RM_Fluid_IcyWater" };

		static RM_SwimWater()
		{
			// The P12 hook (P7 left it in RM_Drowning): from here on the swim rule answers "keeps its head up".
			RM_Drowning.keepsHeadUp = RM_Swim.KeepsHeadUp;
		}

		public static bool On => RM_SwimSettings.deepSwimEnabled;

		private static int Fingerprint()
		{
			return (RM_SwimSettings.deepSwimEnabled ? 1 : 0) | (RM_SwimSettings.swimOpenWaterEnabled ? 2 : 0)
				| (Mathf.Clamp(RM_SwimSettings.swimPathCost, 0, 0xFFFF) << 2);
		}

		private static void EnsureTables()
		{
			int fp = Fingerprint();
			if (swimTerrain != null && swimTerrain.Length == DefDatabase<TerrainDef>.DefCount && fp == tableFingerprint)
			{
				return;
			}
			tableFingerprint = fp;
			if (appliedFingerprint < 0)
			{
				appliedFingerprint = fp;
			}
			if (liquidByTerrain == null)
			{
				liquidByTerrain = new Dictionary<TerrainDef, LiquidDef>();
				foreach (LiquidDef liquid in DefDatabase<LiquidDef>.AllDefsListForReading)
				{
					if (liquid?.terrainSuite == null)
					{
						continue;
					}
					foreach (TerrainDef t in new[] { liquid.terrainSuite.shallow, liquid.terrainSuite.deep, liquid.terrainSuite.chestDeep })
					{
						if (t != null && !liquidByTerrain.ContainsKey(t))
						{
							liquidByTerrain[t] = liquid;
						}
					}
				}
			}
			int n = DefDatabase<TerrainDef>.DefCount;
			var swim = new bool[n];
			var liq = new bool[n];
			foreach (TerrainDef t in DefDatabase<TerrainDef>.AllDefsListForReading)
			{
				if (t.index >= n)
				{
					continue;
				}
				liq[t.index] = LiquidAllowsSwimming(t);
				swim[t.index] = RM_SwimSettings.deepSwimEnabled && liq[t.index] && t.IsWater && t.passability == Traversability.Impassable
					&& (RM_SwimSettings.swimOpenWaterEnabled || (!t.IsOcean && !t.IsRiver));
			}
			swimmableLiquid = liq;
			swimTerrain = swim;
		}

		/// <summary>The liquid this terrain is may be swum: water of a swimmable LiquidDef, or any water no LiquidDef claims with
		/// no toxic buildup (vanilla's swim rule); never a terrain carrying the no-swim marker.</summary>
		private static bool LiquidAllowsSwimming(TerrainDef t)
		{
			if (t == null || !t.IsWater || t.HasModExtension<RM_NoRecreationalSwimExtension>() || t.toxicBuildupFactor > 0f)
			{
				return false;
			}
			if (liquidByTerrain.TryGetValue(t, out LiquidDef liquid))
			{
				return SwimLiquids.Contains(liquid.defName);
			}
			return true;   // unclaimed water (marsh, hot spring, another mod's): vanilla's own rule (no toxic buildup) decides
		}

		/// <summary>A deep (vanilla-impassable) water terrain that is swum while swimming is on.</summary>
		public static bool IsSwimTerrain(TerrainDef t)
		{
			if (t == null)
			{
				return false;
			}
			EnsureTables();
			return t.index < swimTerrain.Length && swimTerrain[t.index];
		}

		public static bool IsDeepSwimCell(Map map, IntVec3 c)
		{
			return On && c.InBounds(map) && IsSwimTerrain(map.terrainGrid.TerrainAt(c));
		}

		/// <summary>May a creature swim in the liquid on this square (dug: the cell's fluid; natural: the terrain)?</summary>
		public static bool LiquidSwimmableAt(Map map, RM_MapComponent_Excavation ex, IntVec3 c)
		{
			if (map == null || !c.InBounds(map))
			{
				return false;
			}
			if (ex != null && ex.IsExcavated(c))
			{
				FluidDef f = ex.FluidAt(c) ?? ex.ActiveFluid;
				return f == null || SwimFluids.Contains(f.defName);
			}
			TerrainDef t = map.terrainGrid.TerrainAt(c);
			if (t == null)
			{
				return false;
			}
			EnsureTables();
			return t.index < swimmableLiquid.Length && swimmableLiquid[t.index];
		}

		/// <summary>The liquid refuses swimming here (a non-water liquid in a pit or a natural sea of one).</summary>
		public static bool LiquidRefusesAt(Map map, IntVec3 c)
		{
			if (map == null || !c.InBounds(map))
			{
				return false;
			}
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			if (ex != null && ex.IsExcavated(c))
			{
				FluidDef f = ex.FluidAt(c) ?? ex.ActiveFluid;
				return f != null && !SwimFluids.Contains(f.defName);
			}
			TerrainDef t = map.terrainGrid.TerrainAt(c);
			return t != null && t.IsWater && !LiquidSwimmableAt(map, ex, c);
		}

		/// <summary>Metres of water standing on a square: a dug cell's own water; a natural square's water from the solver (its
		/// pond's surface over its floor), else its band (deep 2 m, chest 1.5 m, shallow 0.5 m). 0 on dry ground or ice.</summary>
		public static float WaterMetresAt(Map map, RM_MapComponent_Excavation ex, IntVec3 c)
		{
			if (map == null || !c.InBounds(map))
			{
				return 0f;
			}
			if (ex != null && ex.IsExcavated(c))
			{
				return ex.WaterMetresAt(c);
			}
			TerrainDef t = map.terrainGrid.TerrainAt(c);
			if (t == null || !t.IsWater)
			{
				return 0f;
			}
			if (ex != null)
			{
				double dl = ex.NaturalWaterDlAt(c, out _, out _);
				if (dl > 0.0)
				{
					return (float)RM_LevelSolve.Metres((long)dl);
				}
			}
			if (t.passability == Traversability.Impassable)
			{
				return 2f;
			}
			return t.pathCost >= 40 ? 1.5f : 0.5f;
		}

		/// <summary>Settings changed (Mod.WriteSettings): rebuild the tables and re-read every map's path costs, so the deep band
		/// opens or closes without a restart (regions follow the path grid's walkability notifications).</summary>
		public static void Reapply()
		{
			int fp = Fingerprint();
			if (swimTerrain == null || fp == appliedFingerprint)
			{
				RM_SwimPathing.BumpAll();
				return;
			}
			appliedFingerprint = fp;
			EnsureTables();
			if (Current.ProgramState != ProgramState.Playing || Find.Maps == null)
			{
				return;
			}
			foreach (Map m in Find.Maps)
			{
				m.pathing.RecalculateAllPerceivedPathCosts();
				m.reachability.ClearCache();
			}
			RM_SwimPathing.BumpAll();
		}
	}

	/// <summary>One creature's swimming, cached for a quarter of a second of game time.</summary>
	public struct RM_SwimProfile
	{
		public RM_SwimMath.SwimClass cls;
		public RM_SwimMath.SwimClass natural;
		public float endurance;
		public float costFactor;
		public float load;
		public int tick;
	}

	public static class RM_Swim
	{
		public const int CheckTicks = 250;

		private static readonly Dictionary<int, RM_SwimProfile> profiles = new Dictionary<int, RM_SwimProfile>();
		private static readonly Dictionary<int, int> lastWarn = new Dictionary<int, int>();
		private static readonly Dictionary<int, int> lastDrownMsg = new Dictionary<int, int>();
		private static readonly Dictionary<int, int> shoreJob = new Dictionary<int, int>();

		public static HediffDef ExhaustionDef => RimMandrakeFlowWorks_DefOf.RM_SwimExhaustion;

		public static RM_SwimProfile ProfileOf(Pawn p)
		{
			int now = Find.TickManager?.TicksGame ?? 0;
			if (profiles.TryGetValue(p.thingIDNumber, out RM_SwimProfile pr) && now - pr.tick < 60 && now >= pr.tick)
			{
				return pr;
			}
			if (profiles.Count > 4096)
			{
				profiles.Clear();
			}
			int? wcc = null;
			if (ModsConfig.BiotechActive && p.genes != null)
			{
				wcc = p.genes.WaterCellCost;
			}
			if (!wcc.HasValue)
			{
				wcc = p.def.race?.waterCellCost;
			}
			RaceProperties rp = p.RaceProps;
			bool graphic = p.ageTracker?.CurKindLifeStage?.swimmingGraphicData != null;
			RM_SwimMath.SwimClass natural = RM_SwimMath.Classify(rp.IsMechanoid && RM_SwimSettings.mechanoidsSink, wcc, graphic,
				rp.waterSeeker, rp.Humanlike, RM_SwimSettings.humanlikesSwim);
			float moving = p.health?.capacities != null ? p.health.capacities.GetLevel(PawnCapacityDefOf.Moving) : 1f;
			float cap = 0f, gear = 0f, carriedKg = 0f;
			bool carryingPawn = false;
			try
			{
				cap = MassUtility.Capacity(p);
				gear = MassUtility.GearAndInventoryMass(p);
				Thing carried = p.carryTracker?.CarriedThing;
				if (carried is Pawn)
				{
					carryingPawn = true;
				}
				else if (carried != null)
				{
					carriedKg = carried.GetStatValue(StatDefOf.Mass) * carried.stackCount;
				}
			}
			catch (System.Exception e)
			{
				Log.ErrorOnce("[FlowWorks] swim load read threw: " + e.Message, 0x5D7A21);
			}
			float load = RM_SwimMath.Load(gear, carriedKg, carryingPawn, cap);
			float ef = RM_SwimMath.EnduranceFactor(natural, moving, p.BodySize, load, RM_SwimSettings.swimWeightEndurancePenalty);
			RM_SwimMath.SwimClass cls = RM_SwimMath.Effective(natural, ef);
			pr = new RM_SwimProfile
			{
				cls = cls,
				natural = natural,
				endurance = cls == RM_SwimMath.SwimClass.None ? 0f : ef,
				costFactor = RM_SwimMath.CostFactor(cls, moving, load, RM_SwimSettings.swimWeightSlowdown),
				load = load,
				tick = now,
			};
			profiles[p.thingIDNumber] = pr;
			return pr;
		}

		public static float ExhaustionOf(Pawn p)
		{
			HediffDef d = ExhaustionDef;
			if (d == null || p?.health == null)
			{
				return 0f;
			}
			Hediff h = p.health.hediffSet.GetFirstHediffOfDef(d);
			return h?.Severity ?? 0f;
		}

		/// <summary>RM_Drowning.keepsHeadUp (the P12 hook). Off: the old rule (a swimming graphic). On: the swim rule: a creature
		/// that swims, in a liquid that may be swum, keeps its head up until exhausted; a downed creature does not (aquatic
		/// excepted); a non-swimmer never.</summary>
		public static bool KeepsHeadUp(Pawn p, IntVec3 c, float waterMetres)
		{
			if (!RM_SwimWater.On)
			{
				return RM_PitFillEffects.IsSwimmer(p);
			}
			if (p == null || p.Map == null)
			{
				return false;
			}
			RM_SwimProfile pr = ProfileOf(p);
			if (p.Downed && pr.cls != RM_SwimMath.SwimClass.Aquatic)
			{
				return false;
			}
			bool liquid = RM_SwimWater.LiquidSwimmableAt(p.Map, RM_SuperdeepTrap.EngineOf(p.Map), c);
			return RM_SwimMath.KeepsHeadUp(pr.cls, ExhaustionOf(p), liquid);
		}

		/// <summary>Every 250 ticks: exhaustion for everyone swimming (dug or natural water over the head, standing), recovery for
		/// everyone on footing, the warning and the turn for the shore, and the ONE drowning rule on natural water (dug cells
		/// are RM_PitFillEffects' pass).</summary>
		public static void Tick(Map map, RM_MapComponent_Excavation ex)
		{
			if (Find.TickManager.TicksGame % CheckTicks != 0)
			{
				return;
			}
			HediffDef exhDef = ExhaustionDef;
			HediffDef drowning = RimMandrakeFlowWorks_DefOf.RM_PitDrowning;
			bool on = RM_SwimWater.On;
			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn p = pawns[i];
				if (p.health == null || p.Dead)
				{
					continue;
				}
				IntVec3 c = p.Position;
				Hediff exh = exhDef != null ? p.health.hediffSet.GetFirstHediffOfDef(exhDef) : null;
				TerrainDef t = map.terrainGrid.TerrainAt(c);
				bool dug = ex != null && ex.IsExcavated(c);
				if (exh == null && !dug && (t == null || !t.IsWater))
				{
					continue;   // the common case: dry ground, never swam
				}
				if (!on || p.Flying || (dug && Pits.RM_PitCoverUtility.IsCovered(map, c)))
				{
					Recover(p, exh);
					continue;
				}
				float w = RM_SwimWater.WaterMetresAt(map, ex, c);
				bool lying = RM_Drowning.Lying(p);
				bool swimming = w > 0f && RM_SwimMath.IsSwimming(w, RM_Drowning.HeightOf(p), lying,
					RimMandrakeFlowWorksSettings.pitDrowningHeadFraction);
				RM_SwimProfile pr = ProfileOf(p);
				bool liquid = RM_SwimWater.LiquidSwimmableAt(map, ex, c);
				if (swimming && liquid && pr.cls != RM_SwimMath.SwimClass.Aquatic && pr.cls != RM_SwimMath.SwimClass.None && exhDef != null)
				{
					float before = exh?.Severity ?? 0f;
					float add = RM_SwimMath.ExhaustionPerCheck(pr.endurance, RM_SwimSettings.swimEnduranceHours, CheckTicks);
					if (exh == null)
					{
						exh = HediffMaker.MakeHediff(exhDef, p);
						exh.Severity = 0.001f;
						p.health.AddHediff(exh);
					}
					exh.Severity = Mathf.Min(RM_SwimMath.Exhausted, before + add);
					Warn(p, before, exh.Severity, pr);
					if (exh.Severity >= RM_SwimSettings.swimWarnAt)
					{
						HeadForShore(p, map, ex);
					}
				}
				else if (!swimming)
				{
					Recover(p, exh);
				}
				// The one drowning rule: natural water here; dug cells get their severity from RM_PitFillEffects (same PerCheck),
				// and the message from here for both.
				if (w > 0f && drowning != null && RimMandrakeFlowWorksSettings.pitDrowningEnabled)
				{
					float d = RM_Drowning.PerCheck(map, ex, p, c, w);
					if (d > 0f)
					{
						if (!dug)
						{
							HealthUtility.AdjustSeverity(p, drowning, d);
						}
						DrownMessage(p);
					}
				}
			}
		}

		private static void Recover(Pawn p, Hediff exh)
		{
			if (exh == null)
			{
				return;
			}
			exh.Severity -= RM_SwimMath.RecoveryPerCheck(RM_SwimSettings.swimRecoveryHours, CheckTicks);
			if (exh.Severity <= 0.001f)
			{
				p.health.RemoveHediff(exh);
			}
		}

		private static bool Ours(Pawn p)
		{
			return p.Faction == Faction.OfPlayer || p.HostFaction == Faction.OfPlayer;
		}

		/// <summary>No-vanishing rule (2026-09-29/30): a readable sign before anyone drowns. Our own creatures get a message at
		/// the warning and at exhaustion; everyone shows the exhaustion hediff.</summary>
		private static void Warn(Pawn p, float before, float now, RM_SwimProfile pr)
		{
			if (!Ours(p))
			{
				return;
			}
			int tick = Find.TickManager.TicksGame;
			if (before < RM_SwimSettings.swimWarnAt && now >= RM_SwimSettings.swimWarnAt)
			{
				float hoursLeft = (RM_SwimMath.Exhausted - now) * RM_SwimMath.EnduranceHours(pr.endurance, RM_SwimSettings.swimEnduranceHours);
				Messages.Message(p.LabelShort + " is tiring in deep water: about " + Mathf.Max(1, Mathf.RoundToInt(hoursLeft * 60f))
					+ " minutes of swimming left before going under.", p, MessageTypeDefOf.NegativeEvent);
				lastWarn[p.thingIDNumber] = tick;
			}
			else if (before < RM_SwimMath.Exhausted && now >= RM_SwimMath.Exhausted)
			{
				Messages.Message(p.LabelShort + " is exhausted and going under. Get them to footing or rescue them.", p,
					MessageTypeDefOf.ThreatBig);
				lastWarn[p.thingIDNumber] = tick;
			}
		}

		private static void DrownMessage(Pawn p)
		{
			if (!Ours(p))
			{
				return;
			}
			int tick = Find.TickManager.TicksGame;
			if (lastDrownMsg.TryGetValue(p.thingIDNumber, out int last) && tick - last < 2500)
			{
				return;
			}
			if (lastDrownMsg.Count > 1024)
			{
				lastDrownMsg.Clear();
			}
			lastDrownMsg[p.thingIDNumber] = tick;
			Messages.Message(p.LabelShort + " is drowning.", p, MessageTypeDefOf.ThreatBig);
		}

		/// <summary>The rescue behaviour: at the warning a swimmer not under the player's direct command (undrafted, or any
		/// creature not ours) drops its job and swims to the nearest square where its head is clear. Drafted colonists obey.</summary>
		private static void HeadForShore(Pawn p, Map map, RM_MapComponent_Excavation ex)
		{
			if (!RM_SwimSettings.tiredSwimmersHeadForShore || p.Downed || p.Drafted || p.InMentalState || p.jobs == null)
			{
				return;
			}
			if (shoreJob.TryGetValue(p.thingIDNumber, out int jobId) && p.CurJob != null && p.CurJob.loadID == jobId)
			{
				return;
			}
			IntVec3 dest = NearestFooting(p, map, ex);
			if (!dest.IsValid)
			{
				return;
			}
			Job job = JobMaker.MakeJob(JobDefOf.Goto, dest);
			job.locomotionUrgency = LocomotionUrgency.Sprint;
			if (shoreJob.Count > 1024)
			{
				shoreJob.Clear();
			}
			shoreJob[p.thingIDNumber] = job.loadID;
			p.jobs.StartJob(job, JobCondition.InterruptForced, null, resumeCurJobAfterwards: false);
		}

		/// <summary>Nearest square (4-way flood over walkable squares, up to 3000) where this creature stands with its head clear.</summary>
		public static IntVec3 NearestFooting(Pawn p, Map map, RM_MapComponent_Excavation ex)
		{
			float h = RM_Drowning.HeightOf(p);
			float frac = RimMandrakeFlowWorksSettings.pitDrowningHeadFraction;
			var seen = new HashSet<IntVec3> { p.Position };
			var q = new Queue<IntVec3>();
			q.Enqueue(p.Position);
			int budget = 3000;
			while (q.Count > 0 && budget-- > 0)
			{
				IntVec3 c = q.Dequeue();
				for (int i = 0; i < 4; i++)
				{
					IntVec3 n = c + GenAdj.CardinalDirections[i];
					if (!n.InBounds(map) || seen.Contains(n) || !n.Walkable(map))
					{
						continue;
					}
					seen.Add(n);
					float w = RM_SwimWater.WaterMetresAt(map, ex, n);
					if (!RM_RelativeRulesMath.HeadUnder(w, h, false, frac) && n.Standable(map))
					{
						return n;
					}
					q.Enqueue(n);
				}
			}
			return IntVec3.Invalid;
		}

		/// <summary>Swimming for fun in deep water: the setting, a creature that swims (not sinking), at least an hour of
		/// endurance, and rested (exhaustion under 0.2).</summary>
		public static bool JoySwimAllowed(Pawn p)
		{
			if (!RM_SwimSettings.deepSwimJoyEnabled || p == null)
			{
				return false;
			}
			RM_SwimProfile pr = ProfileOf(p);
			if (pr.cls == RM_SwimMath.SwimClass.None)
			{
				return false;
			}
			return RM_SwimMath.EnduranceHours(pr.endurance, RM_SwimSettings.swimEnduranceHours) >= 1f && ExhaustionOf(p) < 0.2f;
		}

		/// <summary>static_call surface: "x,z" -&gt; the swim verdict for the first pawn there.</summary>
		public static string ProofSwim(string arg)
		{
			Map map = Find.CurrentMap;
			string[] a = (arg ?? "").Split(',');
			if (map == null || a.Length != 2 || !int.TryParse(a[0], out int x) || !int.TryParse(a[1], out int z))
			{
				return "REFUSED: arg must be x,z on a current map";
			}
			IntVec3 c = new IntVec3(x, 0, z);
			if (!c.InBounds(map))
			{
				return "REFUSED: out of bounds";
			}
			RM_MapComponent_Excavation ex = RM_SuperdeepTrap.EngineOf(map);
			foreach (Thing t in c.GetThingList(map))
			{
				if (t is Pawn p)
				{
					RM_SwimProfile pr = ProfileOf(p);
					float w = RM_SwimWater.WaterMetresAt(map, ex, c);
					return "SWIM " + p.ThingID + " class=" + pr.cls + " natural=" + pr.natural + " load=" + pr.load.ToString("0.00")
						+ " enduranceH=" + RM_SwimMath.EnduranceHours(pr.endurance, RM_SwimSettings.swimEnduranceHours).ToString("0.00")
						+ " costX=" + pr.costFactor.ToString("0.00") + " water=" + w.ToString("0.00") + " deepCell=" + RM_SwimWater.IsDeepSwimCell(map, c)
						+ " pathCost=" + map.pathing.For(p).pathGrid.Cost(c) + " liquidOk=" + RM_SwimWater.LiquidSwimmableAt(map, ex, c)
						+ " exhaustion=" + ExhaustionOf(p).ToString("0.000") + " headUp=" + RM_Drowning.KeepsHeadUp(p, c, w);
				}
			}
			return "REFUSED: no pawn at " + c;
		}
	}

	/// <summary>Per-creature path planning through deep water (item step 6): a non-swimmer's request carries an offset grid that
	/// closes every swim square; a land animal's adds a detour cost; people pay only the grid's swim cost. Grids are immutable
	/// per (map, terrain version), like RM_PitPathing's (the pathfinder caches jobs by customizer object), retired after 2500
	/// ticks, and composed with a pit grid when both apply.</summary>
	public static class RM_SwimPathing
	{
		private const int RetireAfterTicks = 2500;

		public sealed class Grid : PathRequest.IPathGridCustomizer
		{
			public NativeArray<ushort> cells;

			public NativeArray<ushort> GetOffsetGrid()
			{
				return cells;
			}
		}

		private sealed class MapGrids
		{
			public int version = -1;
			public int builtVersion = -2;
			public int deepCount;
			public Grid block;
			public Grid avoid;
			public readonly Dictionary<(object, object), Grid> combined = new Dictionary<(object, object), Grid>();
			public readonly List<(Grid grid, int tick)> retired = new List<(Grid, int)>();
		}

		private static readonly Dictionary<Map, MapGrids> grids = new Dictionary<Map, MapGrids>();

		public static void Bump(Map map)
		{
			if (map != null && grids.TryGetValue(map, out MapGrids g))
			{
				g.version++;
			}
		}

		public static void BumpAll()
		{
			foreach (MapGrids g in grids.Values)
			{
				g.version++;
			}
		}

		private static void Retire(MapGrids g, Grid grid, int now)
		{
			if (grid != null)
			{
				g.retired.Add((grid, now));
			}
		}

		private static MapGrids For(Map map)
		{
			if (!grids.TryGetValue(map, out MapGrids g))
			{
				PruneDeadMaps();
				g = new MapGrids { version = 0 };
				grids[map] = g;
			}
			int now = Find.TickManager?.TicksGame ?? 0;
			if (g.builtVersion != g.version)
			{
				g.builtVersion = g.version;
				Retire(g, g.block, now);
				Retire(g, g.avoid, now);
				foreach (Grid cg in g.combined.Values)
				{
					Retire(g, cg, now);
				}
				g.combined.Clear();
				g.block = null;
				g.avoid = null;
				int n = map.cellIndices.NumGridCells;
				var deep = new List<int>();
				for (int i = 0; i < n; i++)
				{
					if (RM_SwimWater.IsSwimTerrain(map.terrainGrid.TerrainAt(map.cellIndices.IndexToCell(i))))
					{
						deep.Add(i);
					}
				}
				g.deepCount = deep.Count;
				if (deep.Count > 0)
				{
					var b = new NativeArray<ushort>(n, Allocator.Persistent, NativeArrayOptions.ClearMemory);
					var a = new NativeArray<ushort>(n, Allocator.Persistent, NativeArrayOptions.ClearMemory);
					ushort avoidCost = (ushort)Mathf.Clamp(RM_SwimSettings.animalAvoidCost, 0, RM_SwimMath.Blocked - 1);
					foreach (int i in deep)
					{
						b[i] = RM_SwimMath.Blocked;
						a[i] = avoidCost;
					}
					g.block = new Grid { cells = b };
					g.avoid = new Grid { cells = a };
				}
			}
			for (int i = g.retired.Count - 1; i >= 0; i--)
			{
				if (now - g.retired[i].tick >= RetireAfterTicks || now < g.retired[i].tick)
				{
					g.retired[i].grid.cells.Dispose();
					g.retired.RemoveAt(i);
				}
			}
			return g;
		}

		/// <summary>The offset grid for this pawn's next request, or null (vanilla costs do).</summary>
		public static PathRequest.IPathGridCustomizer CustomizerFor(Pawn pawn)
		{
			if (!RM_SwimWater.On || pawn == null || !pawn.Spawned || pawn.Flying)
			{
				return null;
			}
			RM_SwimProfile pr = RM_Swim.ProfileOf(pawn);
			int offset = RM_SwimMath.PlanOffset(pr.cls, pawn.RaceProps.Animal, RM_SwimSettings.animalsAvoidDeepWater, RM_SwimSettings.animalAvoidCost);
			if (offset == 0)
			{
				return null;
			}
			MapGrids g = For(pawn.Map);
			if (g.deepCount == 0)
			{
				return null;
			}
			return offset >= RM_SwimMath.Blocked ? g.block : g.avoid;
		}

		/// <summary>A pit grid and a swim grid on one request: summed per cell, saturating at blocked.</summary>
		public static PathRequest.IPathGridCustomizer Combine(Map map, PathRequest.IPathGridCustomizer a, PathRequest.IPathGridCustomizer b)
		{
			if (a == null)
			{
				return b;
			}
			if (b == null)
			{
				return a;
			}
			MapGrids g = For(map);
			if (g.combined.TryGetValue((a, b), out Grid done))
			{
				return done;
			}
			NativeArray<ushort> x = a.GetOffsetGrid(), y = b.GetOffsetGrid();
			int n = map.cellIndices.NumGridCells;
			var c = new NativeArray<ushort>(n, Allocator.Persistent, NativeArrayOptions.ClearMemory);
			for (int i = 0; i < n; i++)
			{
				int s = (x.IsCreated && i < x.Length ? x[i] : 0) + (y.IsCreated && i < y.Length ? y[i] : 0);
				c[i] = (ushort)(s >= RM_SwimMath.Blocked ? RM_SwimMath.Blocked : s);
			}
			var grid = new Grid { cells = c };
			if (g.combined.Count > 8)
			{
				int now = Find.TickManager?.TicksGame ?? 0;
				foreach (Grid old in g.combined.Values)
				{
					Retire(g, old, now);
				}
				g.combined.Clear();
			}
			g.combined[(a, b)] = grid;
			return grid;
		}

		public static void PruneDeadMaps()
		{
			List<Map> dead = null;
			foreach (Map m in grids.Keys)
			{
				if (Find.Maps == null || !Find.Maps.Contains(m))
				{
					(dead ?? (dead = new List<Map>())).Add(m);
				}
			}
			if (dead == null)
			{
				return;
			}
			foreach (Map m in dead)
			{
				MapGrids g = grids[m];
				g.block?.cells.Dispose();
				g.avoid?.cells.Dispose();
				foreach (Grid cg in g.combined.Values)
				{
					cg.cells.Dispose();
				}
				foreach ((Grid grid, int _) in g.retired)
				{
					grid.cells.Dispose();
				}
				grids.Remove(m);
			}
		}
	}

	/// <summary>The passable deep band: a swim square answers the swim cost (or the creature's own waterCellCost override)
	/// instead of 10000, still closed by an impassable thing or (for the fence-blocked grid) a fence on it.</summary>
	[HarmonyPatch(typeof(PathGrid), nameof(PathGrid.CalculatedCostAt))]
	[RimMandrake.Shared.PatchFeature("Swimming in deep water", typeof(RM_SwimSettings), "deepSwimEnabled")]
	public static class RM_Patch_PathGrid_SwimCost
	{
		[HarmonyPostfix]
		public static void Postfix(PathGrid __instance, IntVec3 c, int? baseCostOverride, ref int __result)
		{
			if (__result < RM_SwimMath.Blocked || !RM_SwimWater.On)
			{
				return;
			}
			Map map = __instance.map;
			if (map == null || !RM_SwimWater.IsSwimTerrain(map.terrainGrid.TerrainAt(c)))
			{
				return;
			}
			int cost = baseCostOverride ?? RM_SwimSettings.swimPathCost;
			List<Thing> list = map.thingGrid.ThingsListAt(c);
			for (int i = 0; i < list.Count; i++)
			{
				ThingDef d = list[i].def;
				if (d.passability == Traversability.Impassable)
				{
					return;
				}
				if (!__instance.def.fencePassable && d.building != null && d.building.isFence)
				{
					return;
				}
				if (d.pathCost > cost)
				{
					cost = d.pathCost;
				}
			}
			__result = cost;
		}
	}

	/// <summary>Swim speed: the creature's own factor (Moving, load) on a swim square.</summary>
	[HarmonyPatch(typeof(Pawn_PathFollower), "CostToMoveIntoCell", new[] { typeof(Pawn), typeof(IntVec3) })]
	[RimMandrake.Shared.PatchFeature("Swimming in deep water", typeof(RM_SwimSettings), "deepSwimEnabled")]
	public static class RM_Patch_PathFollower_SwimSpeed
	{
		[HarmonyPostfix]
		public static void Postfix(Pawn pawn, IntVec3 c, ref float __result)
		{
			if (!RM_SwimWater.On || pawn == null || pawn.Flying || pawn.Map == null || !RM_SwimWater.IsDeepSwimCell(pawn.Map, c))
			{
				return;
			}
			float f = RM_Swim.ProfileOf(pawn).costFactor;
			if (f > 0f && f != 1f)
			{
				__result = Mathf.Clamp(__result * f, 1f, 1200f);
			}
		}
	}

	/// <summary>A terrain change that opens or closes a swim square re-cuts the swim offset grids.</summary>
	[HarmonyPatch(typeof(TerrainGrid), "DoTerrainChangedEffects")]
	[RimMandrake.Shared.PatchFeature("Swimming in deep water", typeof(RM_SwimSettings), "deepSwimEnabled")]
	public static class RM_Patch_TerrainGrid_SwimVersion
	{
		[HarmonyPostfix]
		public static void Postfix(TerrainDef oldTerr, TerrainDef newTerr, Map ___map)
		{
			if (RM_SwimWater.IsSwimTerrain(oldTerr) != RM_SwimWater.IsSwimTerrain(newTerr))
			{
				RM_SwimPathing.Bump(___map);
			}
		}
	}

	/// <summary>A non-swimmer cannot reach a destination that needs standing in deep water (a square with no dry square beside
	/// it for a touch). Crossing is closed by its offset grid; this keeps work givers from offering it a lake square.</summary>
	[HarmonyPatch(typeof(Reachability), nameof(Reachability.CanReach),
		new[] { typeof(IntVec3), typeof(LocalTargetInfo), typeof(PathEndMode), typeof(TraverseParms) })]
	[RimMandrake.Shared.PatchFeature("Swimming in deep water", typeof(RM_SwimSettings), "deepSwimEnabled")]
	public static class RM_Patch_Reachability_NonSwimmer
	{
		[HarmonyPostfix]
		public static void Postfix(LocalTargetInfo dest, PathEndMode peMode, TraverseParms traverseParams, ref bool __result, Map ___map)
		{
			if (!__result || !RM_SwimWater.On)
			{
				return;
			}
			Pawn p = traverseParams.pawn;
			if (p == null || p.Flying || !dest.IsValid || !RM_SwimWater.IsDeepSwimCell(___map, dest.Cell))
			{
				return;
			}
			if (peMode != PathEndMode.OnCell && peMode != PathEndMode.None)
			{
				foreach (IntVec3 n in GenAdj.CellsAdjacent8Way(dest.Cell, Rot4.North, IntVec2.One))
				{
					if (n.InBounds(___map) && n.Standable(___map) && !RM_SwimWater.IsDeepSwimCell(___map, n))
					{
						return;
					}
				}
			}
			if (RM_Swim.ProfileOf(p).cls == RM_SwimMath.SwimClass.None)
			{
				__result = false;
			}
		}
	}

	/// <summary>Things sink: no item is placed on a swim square.</summary>
	[HarmonyPatch(typeof(GenSpawn), nameof(GenSpawn.CanSpawnAt))]
	[RimMandrake.Shared.PatchFeature("Swimming in deep water", typeof(RM_SwimSettings), "deepSwimEnabled")]
	public static class RM_Patch_GenSpawn_NoItemsInDeepWater
	{
		[HarmonyPostfix]
		public static void Postfix(ThingDef thingDef, IntVec3 c, Map map, ref bool __result)
		{
			if (__result && thingDef != null && thingDef.category == ThingCategory.Item && RM_SwimWater.IsDeepSwimCell(map, c))
			{
				__result = false;
			}
		}
	}

	/// <summary>Drop pods never aim at a swim square.</summary>
	[HarmonyPatch(typeof(DropCellFinder), nameof(DropCellFinder.IsGoodDropSpot))]
	[RimMandrake.Shared.PatchFeature("Swimming in deep water", typeof(RM_SwimSettings), "deepSwimEnabled")]
	public static class RM_Patch_DropCellFinder_NotInDeepWater
	{
		[HarmonyPostfix]
		public static void Postfix(IntVec3 c, Map map, ref bool __result)
		{
			if (__result && RM_SwimWater.IsDeepSwimCell(map, c))
			{
				__result = false;
			}
		}
	}
}
