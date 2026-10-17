using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimMandrake.FlowWorks.Machinery;
using RimMandrake.Shared;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Sprinklers
{
	/// <summary>
	/// The soft link to Vanilla Furniture Expanded - Farming (design §3.4): resolved by name, never a reference to VFEF.dll.
	/// MEASURED 2026-10-16 by ilspycmd on workshop 1957158779/1.6/Assemblies/VFEF.dll:
	///   internal class VFEF.VFEF_SprinklersManager : MapComponent { private void BoostPlantAt(IntVec3 cell) { plant.Growth += 0.04f } }
	///   public class VFEF.CompSprinkler : ThingComp { public List&lt;IntVec3&gt; affectCells; public CompPowerTrader compPowerTrader; ... }
	/// A mismatch logs one warning and the adapter's patch is skipped (VFE then runs as shipped).
	/// </summary>
	public static class RM_SprinklerVFE
	{
		private static bool resolved;
		private static MethodInfo boostTarget;
		private static Type compType;
		private static FieldInfo affectCellsField;
		private static MethodInfo egBiomeInScope;

		/// <summary>State read: VFE boosts skipped inside our biomes this session.</summary>
		public static int BoostsSkipped, BoostsPassed;
		public static string SignatureProblem;

		private static void Resolve()
		{
			if (resolved) return;
			resolved = true;
			try
			{
				Type mgr = AccessTools.TypeByName("VFEF.VFEF_SprinklersManager");
				compType = AccessTools.TypeByName("VFEF.CompSprinkler");
				if (mgr == null && compType == null) return;   // VFE Farming absent: silent
				MethodInfo m = mgr == null ? null : AccessTools.Method(mgr, "BoostPlantAt", new[] { typeof(IntVec3) });
				if (m == null || m.ReturnType != typeof(void) || m.IsStatic || !typeof(MapComponent).IsAssignableFrom(mgr))
				{
					SignatureProblem = "VFEF.VFEF_SprinklersManager.BoostPlantAt(IntVec3) not found as an instance void method";
				}
				else
				{
					boostTarget = m;
				}
				affectCellsField = compType == null ? null : AccessTools.Field(compType, "affectCells");
				if (affectCellsField == null || !typeof(IList).IsAssignableFrom(affectCellsField.FieldType))
				{
					affectCellsField = null;
					SignatureProblem = (SignatureProblem == null ? "" : SignatureProblem + "; ") + "VFEF.CompSprinkler.affectCells not found";
				}
				if (SignatureProblem != null)
				{
					Log.Warning("[FlowWorks] Vanilla Furniture Expanded - Farming sprinkler adapter: " + SignatureProblem
						+ ". A VFE update changed it; the parts that need it are off and VFE runs as shipped there.");
				}
			}
			catch (Exception e)
			{
				SignatureProblem = e.Message;
				Log.Warning("[FlowWorks] VFE sprinkler adapter failed to resolve: " + e.Message);
			}
		}

		public static bool VfeLoaded
		{
			get { Resolve(); return compType != null; }
		}

		public static MethodInfo BoostTarget
		{
			get { Resolve(); return boostTarget; }
		}

		/// <summary>VFE's own covered cells (radius 5.8, MEASURED), or null.</summary>
		public static List<IntVec3> AffectCells(ThingWithComps t)
		{
			Resolve();
			if (affectCellsField == null || t == null) return null;
			foreach (ThingComp c in t.AllComps)
			{
				if (compType.IsInstanceOfType(c) && affectCellsField.GetValue(c) is List<IntVec3> l) return l;
			}
			return null;
		}

		/// <summary>The water rule's scope (our biomes, OQ-S3): ExplosiveGrowth's own BiomeInScope when it is loaded (read
		/// reflection-soft: no dependency), else a biome this project ships (packageId mandrake.*, or an RM_/RUT_/RSW_ def).</summary>
		public static bool InOurBiomes(Map map)
		{
			BiomeDef b = map?.Biome;
			if (b == null) return false;
			if (egBiomeInScope == null && !egTried)
			{
				egTried = true;
				Type reg = AccessTools.TypeByName("RimMandrake.ExplosiveGrowth.RM_ExplosiveGrowthRegistry");
				egBiomeInScope = reg == null ? null : AccessTools.Method(reg, "BiomeInScope", new[] { typeof(BiomeDef) });
			}
			if (egBiomeInScope != null)
			{
				try
				{
					return (bool)egBiomeInScope.Invoke(null, new object[] { b });
				}
				catch (Exception)
				{
					egBiomeInScope = null;
				}
			}
			string pid = b.modContentPack?.PackageId ?? "";
			return pid.StartsWith("mandrake.") || b.defName.StartsWith("RM_") || b.defName.StartsWith("RUT_") || b.defName.StartsWith("RSW_");
		}

		private static bool egTried;
	}

	/// <summary>OQ-S3 RULED: VFE's waterless +0.04 a day is removed only inside our biomes, while the adapter is on.</summary>
	[PatchFeature("Sprinklers: VFE waterless boost removed in our biomes", typeof(RM_SprinklerSettings), "vfeSprinklerAdapterEnabled")]
	[HarmonyPatch]
	internal static class Patch_VFEF_BoostPlantAt_OurBiomes
	{
		private static bool Prepare() => RM_SprinklerVFE.BoostTarget != null;

		private static MethodBase TargetMethod() => RM_SprinklerVFE.BoostTarget;

		private static bool Prefix(MapComponent __instance)
		{
			if (!RM_SprinklerSettings.vfeSprinklerAdapterEnabled || !RM_SprinklerVFE.InOurBiomes(__instance?.map))
			{
				RM_SprinklerVFE.BoostsPassed++;
				return true;
			}
			RM_SprinklerVFE.BoostsSkipped++;
			return false;
		}
	}

	public class CompProperties_RM_SmartSprinkler : CompProperties
	{
		/// <summary>Used only if VFE's own cells cannot be read (MEASURED VFE effectRadius 5.8).</summary>
		public float fallbackRadius = 5.8f;

		public CompProperties_RM_SmartSprinkler()
		{
			compClass = typeof(CompRM_SmartSprinkler);
		}
	}

	/// <summary>
	/// The adapted VFE_Sprinkler (design §3, added by Patches/Compat/RM_VFEFarming_Sprinkler.xml): a pipe consumer under §1 that
	/// needs a pump (ruled by card 2026-10-16), and while powered the THIRST VALVE (OQ-S4, bold #1): it charges only cells where
	/// water changes growth, nearest first, inside a daily budget and above a reserve floor. Unpowered it is a dumb head. VFE's
	/// own mote animation is left alone.
	/// </summary>
	public class CompRM_SmartSprinkler : CompRM_SprinklerBase
	{
		public CompProperties_RM_SmartSprinkler Props => (CompProperties_RM_SmartSprinkler)props;

		public int budgetLitresPerDay;     // 0 = no budget
		public int reserveLitres;          // 0 = no floor
		public int spentTodayUnits, savedTodayUnits, day = -1, coveredCells, valveCells;
		public bool valveTrimmed;

		public override bool FeatureEnabled => RM_SprinklerSettings.vfeSprinklerAdapterEnabled;

		/// <summary>Our own spray mote is not drawn: VFE's rotating spray is the visible sign.</summary>
		protected override bool ShowsOwnSpray => false;

		private bool Powered => parent.GetComp<CompPowerTrader>()?.PowerOn ?? false;

		public bool ValveActive => RM_SprinklerSettings.vfeThirstValve && Powered;

		public override void PostSpawnSetup(bool respawningAfterLoad)
		{
			base.PostSpawnSetup(respawningAfterLoad);
			CoverRadius = Props.fallbackRadius;
		}

		private List<IntVec3> Covered()
		{
			List<IntVec3> vfe = RM_SprinklerVFE.AffectCells(parent);
			if (vfe == null) return RM_Sprinkle.Covered(parent, Props.fallbackRadius);
			// VFE's cells are a plain radius; walls still stop our spray (OQ-S7)
			var list = new List<IntVec3>(vfe.Count);
			Map map = parent.Map;
			foreach (IntVec3 c in vfe)
			{
				if (!c.InBounds(map) || c.Impassable(map)) continue;
				if (c != parent.Position && !GenSight.LineOfSight(parent.Position, c, map, true)) continue;
				list.Add(c);
			}
			return list;
		}

		protected override List<IntVec3> CellsForPulse()
		{
			int today = GenDate.DaysPassed;
			if (today != day)
			{
				day = today;
				spentTodayUnits = 0;
				savedTodayUnits = 0;
			}
			List<IntVec3> covered = Covered();
			coveredCells = covered.Count;
			Map map = parent.Map;
			var weigh = new List<RM_ValveCell>(covered.Count);
			RM_MapComponent_Sprinklers sp = RM_MapComponent_Sprinklers.Of(map);
			int now = Find.TickManager.TicksGame;
			for (int i = 0; i < covered.Count; i++)
			{
				IntVec3 c = covered[i];
				Plant plant = c.GetPlant(map);
				bool lit = plant != null && map.glowGrid.GroundGlowAt(c) >= plant.def.plant.growMinGlow;
				weigh.Add(new RM_ValveCell(i, c.DistanceTo(parent.Position), plant != null, RM_Sprinkle.Sealed(c, map),
					AlreadyWet(c, map, sp, now), lit, plant != null && plant.def.plant.IsTree));
			}
			List<int> pick;
			valveTrimmed = false;
			if (ValveActive)
			{
				int budgetLeft = RM_SprinklerKernel.BudgetLeft(budgetLitresPerDay, spentTodayUnits, RM_Volume.UnitsPerLitre);
				int net = 0;
				if (reserveLitres > 0) RM_Sprinkle.MostHeld(parent, out net);
				pick = RM_SprinklerKernel.Valve(weigh, RM_SprinklerSettings.sprinklerLitresPerCellHour, RM_Volume.UnitsPerLitre,
					budgetLeft, net, reserveLitres * RM_Volume.UnitsPerLitre, out valveTrimmed);
			}
			else
			{
				pick = RM_SprinklerKernel.NativeCharge(weigh);
			}
			valveCells = pick.Count;
			int unsealed = RM_SprinklerKernel.NativeCharge(weigh).Count;
			if (ValveActive) savedTodayUnits += RM_SprinklerKernel.Saved(unsealed, pick.Count, RM_SprinklerSettings.sprinklerLitresPerCellHour, RM_Volume.UnitsPerLitre);
			var cells = new List<IntVec3>(pick.Count);
			foreach (int i in pick) cells.Add(covered[i]);
			return cells;
		}

		/// <summary>Wet by a source the valve can see from FlowWorks: natural water ground, rain on open ground, a liquid
		/// spill, or another head's spray. (A dug channel's soak is ExplosiveGrowth's read; not consulted here.)</summary>
		private bool AlreadyWet(IntVec3 c, Map map, RM_MapComponent_Sprinklers sp, int now)
		{
			TerrainDef t = c.GetTerrain(map);
			if (t != null && (t.IsWater || t.defName.IndexOf("Marsh", StringComparison.OrdinalIgnoreCase) >= 0 || t.defName.IndexOf("Mud", StringComparison.OrdinalIgnoreCase) >= 0)) return true;
			if (map.weatherManager.RainRate > 0.1f && !c.Roofed(map)) return true;
			if (sp != null && sp.WetByOther(c, parent.thingIDNumber, now)) return true;
			List<Thing> things = c.GetThingList(map);
			for (int i = 0; i < things.Count; i++)
			{
				if (things[i] is Filth && SpillFilths.Contains(things[i].def)) return true;
			}
			return false;
		}

		private static HashSet<ThingDef> spillFilths;

		private static HashSet<ThingDef> SpillFilths
		{
			get
			{
				if (spillFilths != null) return spillFilths;
				spillFilths = new HashSet<ThingDef>();
				if (RimMandrakeFlowWorks_DefOf.RM_Filth_LiquidSpill != null) spillFilths.Add(RimMandrakeFlowWorks_DefOf.RM_Filth_LiquidSpill);
				foreach (LiquidTypes.LiquidDef l in DefDatabase<LiquidTypes.LiquidDef>.AllDefsListForReading)
				{
					if (l.spillFilth != null && !l.flammable) spillFilths.Add(l.spillFilth);
				}
				return spillFilths;
			}
		}

		protected override void Record(RM_Sprinkle.Result r)
		{
			if (ValveActive && valveTrimmed && r.cells == 0) r.state = RM_SprinklerState.Budget;
			base.Record(r);
			spentTodayUnits += r.units;
		}

		public override string CompInspectStringExtra()
		{
			if (!FeatureEnabled) return null;   // adapter off: VFE exactly as shipped
			string s = base.CompInspectStringExtra();
			if (state == RM_SprinklerState.Spraying && ValveActive)
			{
				s += "\nThirst valve: watering " + valveCells + " of " + coveredCells + " cells, " + L(lastUnits) + "/h, saved " + L(savedTodayUnits) + " today";
			}
			if (budgetLitresPerDay > 0) s += "\nDaily budget: " + L(spentTodayUnits) + " of " + budgetLitresPerDay + " L";
			if (reserveLitres > 0) s += "\nReserve floor: " + reserveLitres + " L";
			return s;
		}

		private static readonly int[] BudgetChoices = { 0, 100, 250, 500, 1000, 2000 };
		private static readonly int[] ReserveChoices = { 0, 500, 1000, 2000, 5000 };

		public override IEnumerable<Gizmo> CompGetGizmosExtra()
		{
			foreach (Gizmo g in base.CompGetGizmosExtra()) yield return g;
			if (!FeatureEnabled || !RM_SprinklerSettings.vfeThirstValve || parent.Faction != Faction.OfPlayer) yield break;
			yield return new Command_Action
			{
				defaultLabel = "Daily budget: " + (budgetLitresPerDay > 0 ? budgetLitresPerDay + " L" : "none"),
				defaultDesc = "The most water this sprinkler may spray in a day. When the day's budget runs short the moisture valve " +
				              "drops the farthest cells first. Needs power (the valve's brains).",
				icon = TexCommand.ForbidOff,
				action = () => Menu(BudgetChoices, v => budgetLitresPerDay = v, v => v > 0 ? v + " L a day" : "No budget"),
			};
			yield return new Command_Action
			{
				defaultLabel = "Reserve floor: " + (reserveLitres > 0 ? reserveLitres + " L" : "none"),
				defaultDesc = "Stop watering while the network holds less than this much water, so the farm never drinks the colony's " +
				              "drinking supply. Needs power.",
				icon = TexCommand.ForbidOff,
				action = () => Menu(ReserveChoices, v => reserveLitres = v, v => v > 0 ? v + " L kept back" : "No reserve"),
			};
		}

		private static void Menu(int[] choices, Action<int> set, Func<int, string> label)
		{
			var opts = new List<FloatMenuOption>();
			foreach (int v in choices)
			{
				int x = v;
				opts.Add(new FloatMenuOption(label(x), () => set(x)));
			}
			Find.WindowStack.Add(new FloatMenu(opts));
		}

		public override void PostExposeData()
		{
			base.PostExposeData();
			Scribe_Values.Look(ref budgetLitresPerDay, "rmBudgetLitresPerDay");
			Scribe_Values.Look(ref reserveLitres, "rmReserveLitres");
			Scribe_Values.Look(ref spentTodayUnits, "rmSpentTodayUnits");
			Scribe_Values.Look(ref savedTodayUnits, "rmSavedTodayUnits");
			Scribe_Values.Look(ref day, "rmValveDay", -1);
		}
	}
}
