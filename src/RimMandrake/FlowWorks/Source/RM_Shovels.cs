using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// SHOVELS_BUILD_NO_DIGGING_BARE_HANDED: marks a ThingDef as a digging tool (RM_Shovel carries it; another mod's spade may
	/// add it by a PatchOperationFindMod-guarded patch). Held in inventory, it lets a pawn dig and fill.
	/// </summary>
	public class RM_DiggingTool : DefModExtension
	{
	}

	/// <summary>
	/// SHOVELS_BUILD_NO_DIGGING_BARE_HANDED: a race or flesh type that digs with its own body (claws, a digging limb) and never
	/// needs a shovel. FlowWorks names no def itself; a creature mod adds this with a guarded patch, as with RM_MachineDigger.
	/// </summary>
	public class RM_DigsBareHanded : DefModExtension
	{
	}

	/// <summary>
	/// SHOVELS_BUILD_NO_DIGGING_BARE_HANDED (owner 2026-10-25: "You can't dig without them. Hands don't work"; "Shovels now
	/// v1."). Who needs a shovel (RM_ShovelMath.NeedsShovel), who has one (inventory only), and the nearest free one. Design:
	/// design/RimMandrake/shovels_v1_2026-10-25.md §2-§4. Colonists: WorkGiver_/JobDriver_DigCanal and _FillInCanal (JobOnCell
	/// hands out FetchJobFor first; the drivers fail when the shovel is gone). Raiders: RM_RaiderTrench.FillJob and its two
	/// drivers. Pyrelands sand and Moving Dunes drift read this class reflection-soft (_Shared/FlowWorksShovels).
	/// </summary>
	public static class RM_Shovels
	{
		/// <summary>Why a colonist with no shovel gets no dig or fill job (the work tab's float menu reads this).</summary>
		public const string NoShovelReason = "Needs a shovel (none free on the map).";

		private static List<ThingDef> toolDefs;

		/// <summary>Every ThingDef carrying RM_DiggingTool (RM_Shovel, plus any another mod marks). Built once, after defs load.</summary>
		public static List<ThingDef> ToolDefs
		{
			get
			{
				if (toolDefs == null)
				{
					toolDefs = new List<ThingDef>();
					foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
					{
						if (d.HasModExtension<RM_DiggingTool>())
						{
							toolDefs.Add(d);
						}
					}
				}
				return toolDefs;
			}
		}

		public static bool IsShovel(Thing t)
		{
			return t?.def != null && t.def.HasModExtension<RM_DiggingTool>();
		}

		/// <summary>The setting, and only while a shovel def exists at all (no def: nobody could ever comply, so nobody must).</summary>
		public static bool Required => RimMandrakeFlowWorksSettings.shovelRequired && ToolDefs.Count > 0;

		public static bool DigsBareHanded(Pawn pawn)
		{
			RaceProperties race = pawn?.RaceProps;
			return race != null && (pawn.def.HasModExtension<RM_DigsBareHanded>()
				|| (race.FleshType != null && race.FleshType.HasModExtension<RM_DigsBareHanded>()));
		}

		/// <summary>Whether <paramref name="pawn"/> must hold a shovel to dig or fill (setting on, not machine labour, not a
		/// bare-handed digger).</summary>
		public static bool Needs(Pawn pawn)
		{
			return pawn != null && RM_ShovelMath.NeedsShovel(Required, RM_DigLabor.IsMachineLabour(pawn), DigsBareHanded(pawn));
		}

		/// <summary>A shovel in <paramref name="pawn"/>'s inventory (never one carried in the hands while hauling).</summary>
		public static bool HasShovel(Pawn pawn)
		{
			ThingOwner<Thing> inv = pawn?.inventory?.innerContainer;
			if (inv == null)
			{
				return false;
			}
			for (int i = 0; i < inv.Count; i++)
			{
				if (IsShovel(inv[i]))
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>May dig or fill now: needs none, or has one.</summary>
		public static bool Ready(Pawn pawn)
		{
			return !Needs(pawn) || HasShovel(pawn);
		}

		/// <summary>Coarse: any shovel spawned on the map at all (reserved, forbidden or unreachable ones included).</summary>
		public static bool AnyOnMap(Map map)
		{
			if (map == null)
			{
				return false;
			}
			List<ThingDef> defs = ToolDefs;
			for (int i = 0; i < defs.Count; i++)
			{
				if (map.listerThings.ThingsOfDef(defs[i]).Count > 0)
				{
					return true;
				}
			}
			return false;
		}

		// one shovel search per pawn per tick, however many cells the scanner asks about (the HasMaterial pattern)
		private static int cachePawn = -1;
		private static int cacheTick = -1;
		private static bool cacheForced;
		private static bool cacheRaider;
		private static Thing cacheFound;

		/// <summary>The nearest shovel <paramref name="pawn"/> could take now, or null. A colonist honours forbidden; a raider
		/// (<paramref name="raider"/>) takes any loose one, the colony's included. Memoised per pawn per tick.</summary>
		public static Thing FindShovelFor(Pawn pawn, bool forced, float maxDistance = 9999f, bool raider = false)
		{
			if (pawn?.Map == null)
			{
				return null;
			}
			int tick = Find.TickManager.TicksGame;
			if (cachePawn == pawn.thingIDNumber && cacheTick == tick && cacheForced == forced && cacheRaider == raider
				&& (cacheFound == null || (cacheFound.Spawned && cacheFound.Map == pawn.Map)))
			{
				return cacheFound;
			}
			cachePawn = pawn.thingIDNumber;
			cacheTick = tick;
			cacheForced = forced;
			cacheRaider = raider;
			cacheFound = Search(pawn, forced, maxDistance, raider);
			return cacheFound;
		}

		private static Thing Search(Pawn pawn, bool forced, float maxDistance, bool raider)
		{
			if (!AnyOnMap(pawn.Map))
			{
				return null;
			}
			System.Predicate<Thing> ok = t => !t.IsBurning() && (raider || !t.IsForbidden(pawn)) && pawn.CanReserve(t, 1, -1, null, forced);
			Thing best = null;
			float bestD = float.MaxValue;
			List<ThingDef> defs = ToolDefs;
			for (int i = 0; i < defs.Count; i++)
			{
				Thing found = GenClosest.ClosestThingReachable(pawn.Position, pawn.Map, ThingRequest.ForDef(defs[i]),
					PathEndMode.ClosestTouch, TraverseParms.For(pawn), maxDistance, ok);
				if (found != null)
				{
					float d = found.Position.DistanceToSquared(pawn.Position);
					if (d < bestD)
					{
						best = found;
						bestD = d;
					}
				}
			}
			return best;
		}

		/// <summary>The job that puts the nearest free shovel in <paramref name="pawn"/>'s pack (null: none free). A WorkGiver
		/// returns it from JobOnCell instead of the dig or fill job when the pawn is not Ready; the next scan, shovel in pack,
		/// gives the dig. Public for the reflection-soft callers (Pyrelands sand, Moving Dunes drift: _Shared/FlowWorksShovels).</summary>
		public static Job FetchJobFor(Pawn pawn, bool forced)
		{
			Thing shovel = FindShovelFor(pawn, forced);
			return shovel == null ? null : TakeJob(shovel);
		}

		/// <summary>The scanner gate for a dig or fill cell: true when <paramref name="pawn"/> may be offered the cell (Ready, or
		/// a free shovel to fetch first). False sets the work tab's reason. Never touches the designation.</summary>
		public static bool CanWorkOrFetch(Pawn pawn, bool forced)
		{
			if (Ready(pawn))
			{
				return true;
			}
			if (FindShovelFor(pawn, forced) != null)
			{
				return true;
			}
			JobFailReason.Is(NoShovelReason);
			return false;
		}

		private static JobDef takeInventory;

		/// <summary>The job to put <paramref name="shovel"/> in the pack (vanilla TakeInventory, count 1): colonists and raiders.</summary>
		public static Job TakeJob(Thing shovel)
		{
			if (takeInventory == null)
			{
				takeInventory = DefDatabase<JobDef>.GetNamedSilentFail("TakeInventory");
			}
			if (takeInventory == null || shovel == null)
			{
				return null;
			}
			Job job = JobMaker.MakeJob(takeInventory, shovel);
			job.count = 1;
			return job;
		}
	}

	/// <summary>
	/// SHOVELS_BUILD_NO_DIGGING_BARE_HANDED: dig or fill orders on a home map that nobody there can work, because no colonist
	/// holds a shovel, none lies free on the map, and no machine (or bare-handed digger) is there. Re-measured every 250 ticks.
	/// </summary>
	public class Alert_RM_DigNeedsShovel : Alert
	{
		private const int RecheckTicks = 250;
		private const int MaxCulprits = 20;

		private readonly List<GlobalTargetInfo> culprits = new List<GlobalTargetInfo>();
		private int checkedAt = -RecheckTicks;

		public Alert_RM_DigNeedsShovel()
		{
			defaultLabel = "Digging needs a shovel";
			defaultPriority = AlertPriority.Medium;
		}

		private static bool SomeoneCanDig(Map map)
		{
			foreach (Pawn p in map.mapPawns.SpawnedPawnsInFaction(Faction.OfPlayer))
			{
				if (!p.Downed && !p.WorkTypeIsDisabled(WorkTypeDefOf.Mining) && RM_Shovels.Ready(p))
				{
					return true;
				}
			}
			return false;
		}

		private static bool FreeShovel(Map map)
		{
			foreach (ThingDef d in RM_Shovels.ToolDefs)
			{
				foreach (Thing t in map.listerThings.ThingsOfDef(d))
				{
					if (!t.IsForbidden(Faction.OfPlayer))
					{
						return true;
					}
				}
			}
			return false;
		}

		private List<GlobalTargetInfo> Culprits()
		{
			int now = Find.TickManager?.TicksGame ?? 0;
			if (now - checkedAt < RecheckTicks && now >= checkedAt)
			{
				return culprits;
			}
			checkedAt = now;
			culprits.Clear();
			if (Find.Maps == null || Faction.OfPlayerSilentFail == null || !RM_Shovels.Required)
			{
				return culprits;
			}
			foreach (Map m in Find.Maps)
			{
				if (!m.IsPlayerHome)
				{
					continue;
				}
				bool dig = m.designationManager.AnySpawnedDesignationOfDef(RimMandrakeFlowWorks_DefOf.RM_DigCanal);
				bool fill = m.designationManager.AnySpawnedDesignationOfDef(RimMandrakeFlowWorks_DefOf.RM_FillInCanal);
				if ((!dig && !fill) || FreeShovel(m) || SomeoneCanDig(m))
				{
					continue;
				}
				foreach (DesignationDef def in new[] { RimMandrakeFlowWorks_DefOf.RM_DigCanal, RimMandrakeFlowWorks_DefOf.RM_FillInCanal })
				{
					foreach (Designation d in m.designationManager.SpawnedDesignationsOfDef(def))
					{
						if (culprits.Count >= MaxCulprits)
						{
							break;
						}
						culprits.Add(new GlobalTargetInfo(d.target.Cell, m));
					}
				}
			}
			return culprits;
		}

		public override TaggedString GetExplanation()
		{
			return "Nobody digs or fills in with bare hands. No colonist here carries a shovel and none lies free on the map, so "
				+ "these dig and fill-in orders wait.\n\nMake a shovel (crafting spot or smithy, wood or metal), unforbid one, "
				+ "or take one from a raider. Machines dig without. \"Digging and filling need a shovel\" is in the Flow Works settings.";
		}

		public override AlertReport GetReport()
		{
			return AlertReport.CulpritsAre(Culprits());
		}
	}

	/// <summary>
	/// SHOVELS_BUILD_NO_DIGGING_BARE_HANDED design §4a: on a map with a dug trench (the jump-pack gate), a share of a
	/// neolithic-or-better raid's humanlike tool-users arrive with a shovel in their pack: wood below industrial, steel from
	/// industrial. Sappers bring more; a siege none (owner 2026-10-25, Q1: "Siege is mortar-based. Sappers however would bring
	/// shovels &amp; ladders."). Their shovels are loot when they fall.
	/// </summary>
	[HarmonyPatch(typeof(IncidentWorker_Raid), "PostProcessSpawnedPawns")]
	[RimMandrake.Shared.PatchFeature("Raiders bring shovels")]
	public static class RM_Patch_Raid_Shovels
	{
		[HarmonyPostfix]
		public static void Postfix(IncidentParms parms, List<Pawn> pawns)
		{
			ThingDef shovel = RimMandrakeFlowWorks_DefOf.RM_Shovel;
			if (shovel == null || !RM_Shovels.Required || !RM_RaiderTrench.On || pawns == null || !(parms?.target is Map map)
				|| parms.faction == null || parms.faction.def.techLevel < TechLevel.Neolithic)
			{
				return;
			}
			RaidStrategyWorker worker = parms.raidStrategy?.Worker;
			float share = RM_ShovelMath.ShareFor(worker is RaidStrategyWorker_Siege, worker is RaidStrategyWorker_ImmediateAttackSappers,
				RM_RaiderTrenchSettings.raiderShovelShare, RM_RaiderTrenchSettings.sapperShovelShare);
			if (share <= 0f)
			{
				return;
			}
			RM_MapComponent_Excavation eng = RM_SuperdeepTrap.EngineOf(map);
			if (eng == null || eng.ClimbCellCount < RM_RaiderTrench.MinClimbCellsForJumpPacks)
			{
				return;
			}
			ThingDef stuff = parms.faction.def.techLevel >= TechLevel.Industrial ? ThingDefOf.Steel : ThingDefOf.WoodLog;
			if (stuff == null)
			{
				stuff = GenStuff.DefaultStuffFor(shovel);
			}
			for (int i = 0; i < pawns.Count; i++)
			{
				Pawn p = pawns[i];
				if (p?.inventory == null || !RM_RaiderTrench.ToolUser(p) || !RM_Shovels.Needs(p) || RM_Shovels.HasShovel(p)
					|| !RM_ShovelMath.GetsShovel(p.thingIDNumber, share))
				{
					continue;
				}
				p.inventory.innerContainer.TryAdd(ThingMaker.MakeThing(shovel, stuff));
			}
		}
	}
}
