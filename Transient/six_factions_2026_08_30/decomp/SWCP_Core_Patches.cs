using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using SWCP.Factions;
using UnityEngine;
using Verse;
using Verse.AI;

namespace SWCP.Core;

[StaticConstructorOnStartup]
public static class Patches
{
	static Patches()
	{
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Expected O, but got Unknown
		//IL_006b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Expected O, but got Unknown
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ac: Expected O, but got Unknown
		//IL_00d5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e1: Expected O, but got Unknown
		//IL_0109: Unknown result type (might be due to invalid IL or missing references)
		//IL_0116: Expected O, but got Unknown
		//IL_013f: Unknown result type (might be due to invalid IL or missing references)
		//IL_014b: Expected O, but got Unknown
		//IL_0173: Unknown result type (might be due to invalid IL or missing references)
		//IL_0180: Expected O, but got Unknown
		//IL_01a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b5: Expected O, but got Unknown
		//IL_01de: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ea: Expected O, but got Unknown
		//IL_0211: Unknown result type (might be due to invalid IL or missing references)
		//IL_021d: Expected O, but got Unknown
		//IL_0246: Unknown result type (might be due to invalid IL or missing references)
		//IL_0252: Expected O, but got Unknown
		//IL_027b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0287: Expected O, but got Unknown
		//IL_02af: Unknown result type (might be due to invalid IL or missing references)
		//IL_02bc: Expected O, but got Unknown
		//IL_02e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f1: Expected O, but got Unknown
		//IL_031a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0326: Expected O, but got Unknown
		//IL_0374: Unknown result type (might be due to invalid IL or missing references)
		//IL_037f: Expected O, but got Unknown
		//IL_03a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_03b4: Expected O, but got Unknown
		//IL_03de: Unknown result type (might be due to invalid IL or missing references)
		//IL_03e9: Expected O, but got Unknown
		//IL_0412: Unknown result type (might be due to invalid IL or missing references)
		//IL_041e: Expected O, but got Unknown
		//IL_0447: Unknown result type (might be due to invalid IL or missing references)
		//IL_0453: Expected O, but got Unknown
		//IL_047c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0488: Expected O, but got Unknown
		//IL_04e9: Unknown result type (might be due to invalid IL or missing references)
		//IL_04f6: Expected O, but got Unknown
		//IL_054a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0557: Expected O, but got Unknown
		//IL_05b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_05c5: Expected O, but got Unknown
		//IL_05ee: Unknown result type (might be due to invalid IL or missing references)
		//IL_05fa: Expected O, but got Unknown
		//IL_0623: Unknown result type (might be due to invalid IL or missing references)
		//IL_062f: Expected O, but got Unknown
		//IL_0658: Unknown result type (might be due to invalid IL or missing references)
		//IL_0664: Expected O, but got Unknown
		//IL_069a: Unknown result type (might be due to invalid IL or missing references)
		//IL_06a7: Expected O, but got Unknown
		//IL_06cf: Unknown result type (might be due to invalid IL or missing references)
		//IL_06dc: Expected O, but got Unknown
		//IL_0704: Unknown result type (might be due to invalid IL or missing references)
		//IL_0711: Expected O, but got Unknown
		//IL_073a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0746: Expected O, but got Unknown
		Harmony harmony = SWCPCoreMod.harmony;
		harmony.PatchAll();
		harmony.Patch((MethodBase)AccessTools.Method(typeof(WildAnimalSpawner), "CommonalityOfAnimalNow", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "WildAnimalSpawnerCommonalityOfAnimalNow_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(TraderCaravanUtility), "GetTraderCaravanRole", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "TraderCaravanUtilityGetTraderCaravanRole_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(Pawn_GuestTracker), "RandomizeJoinStatus", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "Pawn_GuestTrackerRandomizeJoinStatus_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(Pawn), "PreTraded", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "PawnPreTraded_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(DamageWorker_AddInjury), "ApplyDamageToPart", (Type[])null, (Type[])null), new HarmonyMethod(typeof(Patches), "DamageWorker_AddInjuryApplyDamageToPart_Prefix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(JobGiver_AIDefendPawn), "FindAttackTarget", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "JobGiver_AIDefendPawnFindAttackTarget_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(Pawn_JobTracker), "CleanupCurrentJob", (Type[])null, (Type[])null), new HarmonyMethod(typeof(Patches), "Pawn_JobTrackerCleanupCurrentJob_Prefix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(Verb_MeleeAttack), "GetDodgeChance", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "Verb_MeleeAttackGetDodgeChance_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(Pawn_JobTracker), "StartJob", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "Pawn_JobTrackerStartJob_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.PropertyGetter(typeof(ShotReport), "AimOnTargetChance_StandardTarget"), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "ShotReportAimOnTargetChance_StandardTarget_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(StatExtension), "GetStatValue", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "StatExtensionGetStatValue_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(IdeoGenerator), "MakeFixedIdeo", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "IdeoGeneratorMakeFixedIdeo_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(IdeoFoundation), "RandomizeIcon", (Type[])null, (Type[])null), new HarmonyMethod(typeof(Patches), "IdeoFoundationRandomizeIcon_Prefix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(IdeoFoundation), "InitPrecepts", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "IdeoFoundationInitPrecepts_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(PawnsArrivalModeWorker), "CanUseWith", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "PawnsArrivalModeWorkerCanUseWith_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)((IEnumerable<Type>)typeof(IncidentWorker_CaravanMeeting).GetNestedTypes(AccessTools.all)).SelectMany((Func<Type, IEnumerable<MethodInfo>>)AccessTools.GetDeclaredMethods).First((MethodInfo mi) => mi.ReturnType == typeof(bool) && GenCollection.ContainsAny<ParameterInfo>((IList<ParameterInfo>)mi.GetParameters(), (Func<ParameterInfo, bool>)((ParameterInfo pi) => pi.ParameterType == typeof(Faction)))), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "IncidentWorker_CaravanMeetingTryFindFaction_Linq_Transpiler", (Type[])null), (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(IncidentWorker_NeutralGroup), "FactionCanBeGroupSource", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "IncidentWorker_NeutralGroup_FactionCanBeGroupSource_Transpiler", (Type[])null), (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(PermitsCardUtility), "DoLeftRect", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "PermitsCardUtility_LeftRect_Transpiler", (Type[])null), (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(RoyalTitlePermitDef), "AvailableForPawn", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "RoyalTitlePermitDef_AvailableForPawn_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(RoyalTitleAwardWorker), "DoAward", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "RoyalTitleAwardWorker_DoAward_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(RoyalTitleAwardWorker_Instant), "DoAward", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "RoyalTitleAwardWorker_DoAward_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(PawnGroupKindWorker_Trader), "GeneratePawns", new Type[4]
		{
			typeof(PawnGroupMakerParms),
			typeof(PawnGroupMaker),
			typeof(List<Pawn>),
			typeof(bool)
		}, (Type[])null), new HarmonyMethod(typeof(Patches), "PawnGroupKindWorker_Trader_GeneratePawns_Prefix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(PawnGroupKindWorker_Trader), "GenerateTrader", new Type[3]
		{
			typeof(PawnGroupMakerParms),
			typeof(PawnGroupMaker),
			typeof(TraderKindDef)
		}, (Type[])null), new HarmonyMethod(typeof(Patches), "PawnGroupKindWorker_Trader_GenerateTrader_Prefix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(PawnGroupKindWorker_Normal), "GeneratePawns", new Type[4]
		{
			typeof(PawnGroupMakerParms),
			typeof(PawnGroupMaker),
			typeof(List<Pawn>),
			typeof(bool)
		}, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "PawnGroupKindWorker_Normal_GeneratePawns_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(GoodwillSituationWorker_PermanentEnemy), "ArePermanentEnemies", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "GoodwillSituationWorker_PermanentEnemy_ArePermanentEnemies_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(Faction), "CanChangeGoodwillFor", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "Faction_CanChangeGoodwillFor_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(FactionDef), "PermanentlyHostileTo", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "FactionDef_PermanentlyHostileTo_Postfix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessToolsExtensions.GetDeclaredMethods(typeof(Faction)).First((MethodInfo mi) => mi.Name.Contains("GetInitialGoodwill")), new HarmonyMethod(typeof(Patches), "Faction_TryMakeInitialRelationsWith_GetInitialGoodwill_Prefix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(Faction), "TryGenerateNewLeader", (Type[])null, (Type[])null), new HarmonyMethod(typeof(Patches), "Faction_TryGenerateNewLeader_Prefix", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(PawnRenderUtility), "DrawEquipmentAndApparelExtras", (Type[])null, (Type[])null), new HarmonyMethod(typeof(Patches), "WeaponDrawPosPatch", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		harmony.Patch((MethodBase)AccessTools.Method(typeof(InspectPaneUtility), "AdjustedLabelFor", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(Patches), "RarityLabelPatch", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
	}

	public static void WildAnimalSpawnerCommonalityOfAnimalNow_Postfix(PawnKindDef def, ref Map ___map, ref float __result)
	{
		//IL_002b: Unknown result type (might be due to invalid IL or missing references)
		//IL_004b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0074: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Invalid comparison between Unknown and I4
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_0098: Unknown result type (might be due to invalid IL or missing references)
		ModExtension_BiomeFeatureRequirements modExtension = ((Def)def.race).GetModExtension<ModExtension_BiomeFeatureRequirements>();
		if (modExtension != null)
		{
			bool flag = modExtension.requireCaves && !Find.World.HasCaves(___map.Tile);
			int num;
			if (modExtension.requireCoast)
			{
				Rot4 val = Find.World.CoastDirectionAt(___map.Tile);
				num = ((!((Rot4)(ref val)).IsValid) ? 1 : 0);
			}
			else
			{
				num = 0;
			}
			bool flag2 = (byte)num != 0;
			PlanetTile tile;
			int num2;
			if (modExtension.requireHills)
			{
				tile = ___map.Tile;
				num2 = (((int)((PlanetTile)(ref tile)).Tile.hilliness == 1) ? 1 : 0);
			}
			else
			{
				num2 = 0;
			}
			bool flag3 = (byte)num2 != 0;
			int num3;
			if (modExtension.requireRiver)
			{
				tile = ___map.Tile;
				Tile tile2 = ((PlanetTile)(ref tile)).Tile;
				Tile obj = ((tile2 is SurfaceTile) ? tile2 : null);
				num3 = ((((obj != null) ? ((SurfaceTile)obj).Rivers : null) == null) ? 1 : 0);
			}
			else
			{
				num3 = 0;
			}
			bool flag4 = (byte)num3 != 0;
			if (flag || flag2 || flag3 || flag4)
			{
				__result = 0f;
			}
		}
	}

	public static void TraderCaravanUtilityGetTraderCaravanRole_Postfix(Pawn p, ref TraderCaravanRole __result)
	{
		ModExtension_PawnKindProperties modExtension_PawnKindProperties = ModExtension_PawnKindProperties.Get((Def)(object)p.kindDef);
		if (modExtension_PawnKindProperties != null && modExtension_PawnKindProperties.purchasableFromTrader)
		{
			__result = (TraderCaravanRole)4;
		}
	}

	public static void Pawn_GuestTrackerRandomizeJoinStatus_Postfix(ref Pawn ___pawn, ref JoinStatus ___joinStatus)
	{
		if ((int)___joinStatus != 1 && PatchesUtility.CanRecruit(___pawn))
		{
			___joinStatus = (JoinStatus)1;
		}
	}

	public static void PawnPreTraded_Postfix(ref Pawn __instance)
	{
		if (PatchesUtility.CanRecruit(__instance))
		{
			Need_Mood mood = __instance.needs.mood;
			if (mood != null)
			{
				mood.thoughts.memories.RemoveMemoriesOfDef(ThoughtDefOf.FreedFromSlavery);
			}
		}
	}

	public static void DamageWorker_AddInjuryApplyDamageToPart_Prefix(ref DamageInfo dinfo, Pawn pawn, DamageResult result)
	{
		Thing instigator = ((DamageInfo)(ref dinfo)).Instigator;
		Pawn val = (Pawn)(object)((instigator is Pawn) ? instigator : null);
		if (val != null && val.IsFlyingPawn(out var comp))
		{
			AttackDamageFactor attackDamageFactor = comp.Props.attackDamageFactor;
			if (attackDamageFactor != null && pawn.BodySize <= attackDamageFactor.targetBodySize)
			{
				((DamageInfo)(ref dinfo)).SetAmount(((DamageInfo)(ref dinfo)).Amount * attackDamageFactor.damageMultiplier);
			}
		}
	}

	public static void JobGiver_AIDefendPawnFindAttackTarget_Postfix(JobGiver_AIDefendPawn __instance, ref Thing __result, Pawn pawn)
	{
		if (pawn != null && __instance is JobGiver_AIDefendMaster && pawn.IsFlyingPawn(out var comp) && comp.Props.attackEnemiesMasterAttacking)
		{
			Pawn master = pawn.playerSettings.Master;
			if (master.CurJobDef == JobDefOf.AttackStatic || master.CurJobDef == JobDefOf.AttackMelee)
			{
				__result = ((LocalTargetInfo)(ref master.CurJob.targetA)).Thing;
			}
		}
	}

	public static void Pawn_JobTrackerCleanupCurrentJob_Prefix(Pawn ___pawn)
	{
		if (___pawn.IsFlyingPawn(out var comp) && comp.isFlyingCurrently)
		{
			comp.isFlyingCurrently = false;
			comp.ChangeGraphic();
		}
	}

	public static void Verb_MeleeAttackGetDodgeChance_Postfix(ref float __result, LocalTargetInfo target)
	{
		Pawn pawn = ((LocalTargetInfo)(ref target)).Pawn;
		if (pawn.IsFlyingPawn(out var comp) && comp.isFlyingCurrently)
		{
			__result *= comp.Props.evadeChanceWhenFlying;
		}
	}

	public static void Pawn_JobTrackerStartJob_Postfix(Pawn ___pawn)
	{
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		if (___pawn.IsFlyingPawn(out var comp))
		{
			Job curJob = ___pawn.CurJob;
			if (curJob != null && ((comp.Props.flyWhenFleeing && (curJob.def == JobDefOf.Flee || curJob.def == JobDefOf.FleeAndCower)) || (curJob.def == JobDefOf.GotoWander && Rand.Chance(comp.Props.flyWhenWanderingChance)) || (curJob.def == JobDefOf.PredatorHunt && comp.Props.flyWhenHunting)))
			{
				comp.isFlyingCurrently = true;
				curJob.locomotionUrgency = (LocomotionUrgency)3;
				comp.ChangeGraphic(withSound: true);
			}
		}
	}

	public static void ShotReportAimOnTargetChance_StandardTarget_Postfix(ref float __result, TargetInfo ___target)
	{
		Thing thing = ((TargetInfo)(ref ___target)).Thing;
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val != null)
		{
			CompFlyingPawn compFlyingPawn = ThingCompUtility.TryGetComp<CompFlyingPawn>((Thing)(object)val);
			if (compFlyingPawn != null && compFlyingPawn.isFlyingCurrently)
			{
				__result *= 1f - compFlyingPawn.Props.evadeChanceWhenFlying;
			}
		}
	}

	private static void StatExtensionGetStatValue_Postfix(Thing thing, StatDef stat, ref float __result)
	{
		if (stat == StatDefOf.MoveSpeed)
		{
			Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
			if (val != null && val.IsFlyingPawn(out var comp) && comp.isFlyingCurrently)
			{
				__result *= comp.Props.flyingMoveSpeedMultiplier;
			}
		}
	}

	public static void IdeoGeneratorMakeFixedIdeo_Postfix(IdeoGenerationParms parms, Ideo __result)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		FactionDef forFaction = parms.forFaction;
		((forFaction != null) ? ((Def)forFaction).GetModExtension<ModExtension_FixedIdeo>() : null)?.CopyToIdeo(__result);
	}

	public static bool IdeoFoundationRandomizeIcon_Prefix(IdeoFoundation __instance)
	{
		Ideo ideo = __instance.ideo;
		return ideo.iconDef == null;
	}

	public static void IdeoFoundationInitPrecepts_Postfix(IdeoGenerationParms parms, IdeoFoundation __instance)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		FactionDef forFaction = parms.forFaction;
		ModExtension_FixedIdeo modExtension_FixedIdeo = ((forFaction != null) ? ((Def)forFaction).GetModExtension<ModExtension_FixedIdeo>() : null);
		if (modExtension_FixedIdeo == null)
		{
			return;
		}
		foreach (Precept item in __instance.ideo.PreceptsListForReading)
		{
			Precept_Role preceptRole = (Precept_Role)(object)((item is Precept_Role) ? item : null);
			if (preceptRole == null)
			{
				continue;
			}
			ModExtension_FixedIdeo.RoleOverride roleOverride = GenCollection.FirstOrDefault<ModExtension_FixedIdeo.RoleOverride>(modExtension_FixedIdeo.roleOverrides, (Predicate<ModExtension_FixedIdeo.RoleOverride>)((ModExtension_FixedIdeo.RoleOverride x) => x.preceptDef == ((Precept)preceptRole).def));
			if (roleOverride != null)
			{
				if (roleOverride.newName != null)
				{
					((Precept)preceptRole).SetName(roleOverride.newName);
				}
				if (roleOverride.disableApparelRequirements)
				{
					((Precept)preceptRole).ApparelRequirements.Clear();
				}
				else if (GenCollection.Any<PreceptApparelRequirement>(roleOverride.apparelRequirementsOverride))
				{
					((Precept)preceptRole).ApparelRequirements = roleOverride.apparelRequirementsOverride;
				}
			}
		}
	}

	public static void PawnsArrivalModeWorkerCanUseWith_Postfix(IncidentParms parms, ref bool __result, PawnsArrivalModeDef ___def)
	{
		if (__result)
		{
			Faction faction = parms.faction;
			ModExtension_FactionBannedArrivalModes modExtension_FactionBannedArrivalModes = ((faction != null) ? ((Def)faction.def).GetModExtension<ModExtension_FactionBannedArrivalModes>() : null);
			if (modExtension_FactionBannedArrivalModes != null && GenList.NotNullAndContains<PawnsArrivalModeDef>((IList<PawnsArrivalModeDef>)modExtension_FactionBannedArrivalModes.arrivalModes, ___def))
			{
				__result = false;
			}
		}
	}

	private static IEnumerable<CodeInstruction> IncidentWorker_CaravanMeetingTryFindFaction_Linq_Transpiler(IEnumerable<CodeInstruction> instructions, ILGenerator generator)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003c: Expected O, but got Unknown
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Expected O, but got Unknown
		//IL_00a6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ac: Expected O, but got Unknown
		MethodInfo methodInfo = AccessToolsExtensions.PropertyGetter(typeof(Faction), "Hidden");
		CodeMatcher val = new CodeMatcher(instructions, generator).End().MatchStartBackwards((CodeMatch[])(object)new CodeMatch[2]
		{
			new CodeMatch((OpCode?)OpCodes.Ldc_I4_0, (object)null, (string)null),
			new CodeMatch((OpCode?)OpCodes.Ret, (object)null, (string)null)
		}).MatchStartBackwards((CodeMatch[])(object)new CodeMatch[2]
		{
			CodeMatch.Calls(methodInfo),
			CodeMatch.Branches((string)null)
		})
			.Advance(1)
			.ThrowIfInvalid("SWCPTools Transpiler was unable to find the use of Faction.get_Hidden in the CaravanMeeting Nested Method");
		Label label = default(Label);
		val.CreateLabelAt(val.Pos + 1, ref label).InsertAndAdvance((CodeInstruction[])(object)new CodeInstruction[3]
		{
			new CodeInstruction(OpCodes.Brfalse, (object)label),
			CodeInstruction.LoadArgument(1, false),
			CodeInstruction.Call(typeof(ModExtension_HiddenFactionHasCaravans), "FactionHas", (Type[])null, (Type[])null)
		}).SetOpcodeAndAdvance(OpCodes.Brfalse);
		return val.Instructions();
	}

	private static IEnumerable<CodeInstruction> IncidentWorker_NeutralGroup_FactionCanBeGroupSource_Transpiler(IEnumerable<CodeInstruction> instructions, ILGenerator generator)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		//IL_009d: Expected O, but got Unknown
		MethodInfo methodInfo = AccessToolsExtensions.PropertyGetter(typeof(Faction), "Hidden");
		CodeMatcher val = new CodeMatcher(instructions, generator).MatchEndForward((CodeMatch[])(object)new CodeMatch[2]
		{
			CodeMatch.Calls(methodInfo),
			CodeMatch.Branches((string)null)
		}).ThrowIfInvalid("SWCPTools : FactionCanBeGroupSource_Transpiler couldn't find a valid insertion point");
		object operand = val.Operand;
		Label label = default(Label);
		val.CreateLabelWithOffsets(1, ref label).SetAndAdvance(OpCodes.Brfalse, (object)label).Insert((CodeInstruction[])(object)new CodeInstruction[3]
		{
			CodeInstruction.LoadArgument(1, false),
			CodeInstruction.Call(typeof(ModExtension_HiddenFactionHasCaravans), "FactionHas", (Type[])null, (Type[])null),
			new CodeInstruction(OpCodes.Brfalse, operand)
		});
		return val.Instructions();
	}

	private static IEnumerable<CodeInstruction> PermitsCardUtility_LeftRect_Transpiler(IEnumerable<CodeInstruction> instructions, ILGenerator generator)
	{
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		FieldInfo fieldInfo = AccessTools.Field(typeof(PermitsCardUtility), "selectedPermit");
		FieldInfo fieldInfo2 = AccessTools.Field(typeof(RoyalTitlePermitDef), "minTitle");
		FieldInfo fieldInfo3 = AccessTools.Field(typeof(RoyalTitlePermitDef), "prerequisite");
		CodeMatcher val = new CodeMatcher(instructions, generator).MatchEndForward((CodeMatch[])(object)new CodeMatch[2]
		{
			CodeMatch.LoadsField(fieldInfo2, false),
			CodeMatch.Branches((string)null)
		}).ThrowIfInvalid("PermitsCardUtility_LeftRect_Transpiler: SWCPTools couldn't find the correct branch (seq 1)").MatchStartForward((CodeMatch[])(object)new CodeMatch[2]
		{
			CodeMatch.LoadsField(fieldInfo, false),
			CodeMatch.LoadsField(fieldInfo3, false)
		})
			.ThrowIfInvalid("PermitsCardUtility_LeftRect_Transpiler: SWCPTools couldn't find the second branch (seq 2)")
			.Advance(-1)
			.ThrowIfNotMatch("PermitsCardUtility_LeftRect_Transpiler: instruction prior to end of second branch is not as expected (seq 4)", (CodeMatch[])(object)new CodeMatch[1] { CodeMatch.StoresLocal("storeText") });
		int localIndex = (val.NamedMatch("storeText").operand as LocalBuilder).LocalIndex;
		val.Advance(1).Insert((CodeInstruction[])(object)new CodeInstruction[4]
		{
			CodeInstruction.LoadLocal(localIndex, false),
			CodeInstruction.LoadArgument(1, false),
			CodeInstruction.Call(typeof(Patches), "PermitsCardUtility_Util_AppendMaxTitleStatus", (Type[])null, (Type[])null),
			CodeInstruction.StoreLocal(localIndex)
		});
		return val.Instructions();
	}

	private static string PermitsCardUtility_Util_AppendMaxTitleStatus(string text, Pawn pawn)
	{
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		MaxTitlePermitExtension modExtension = ((Def)PermitsCardUtility.selectedPermit).GetModExtension<MaxTitlePermitExtension>();
		if (modExtension?.maxTitle == null)
		{
			return text;
		}
		bool flag = pawn.royalty.GetCurrentTitle(PermitsCardUtility.selectedFaction).seniority <= modExtension.maxTitle.seniority;
		return text + "\nMaximum Title: " + ColoredText.Colorize(modExtension.maxTitle.GetLabelForBothGenders(), flag ? Color.white : ColorLibrary.RedReadable);
	}

	private static void RoyalTitlePermitDef_AvailableForPawn_Postfix(ref bool __result, RoyalTitlePermitDef __instance, Pawn pawn, Faction faction)
	{
		if (!__result)
		{
			return;
		}
		MaxTitlePermitExtension modExtension = ((Def)__instance).GetModExtension<MaxTitlePermitExtension>();
		if (modExtension != null)
		{
			RoyalTitleDef currentTitle = pawn.royalty.GetCurrentTitle(faction);
			if (currentTitle.seniority < __instance.minTitle.seniority || currentTitle.seniority > modExtension.maxTitle.seniority)
			{
				__result = false;
			}
		}
	}

	private static void RoyalTitleAwardWorker_DoAward_Postfix(Pawn pawn, Faction faction, RoyalTitleDef currentTitle, RoyalTitleDef newTitle)
	{
		//IL_0079: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		foreach (FactionPermit item in pawn.royalty.AllFactionPermits.ToList())
		{
			MaxTitlePermitExtension modExtension = ((Def)item.Permit).GetModExtension<MaxTitlePermitExtension>();
			if (!(newTitle.seniority <= modExtension?.maxTitle.seniority))
			{
				Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("SWCP_MessagePermitLostOnPromotion", NamedArgument.op_Implicit((Thing)(object)pawn), NamedArgument.op_Implicit(currentTitle.GetLabelFor(pawn)), NamedArgument.op_Implicit((Def)(object)item.Permit))), MessageTypeDefOf.NeutralEvent, true);
				pawn.royalty.AllFactionPermits.Remove(item);
			}
		}
	}

	public static void PawnGroupKindWorker_Trader_GeneratePawns_Prefix(PawnGroupMakerParms parms, PawnGroupMaker groupMaker)
	{
		if (groupMaker is GroupMakerWithTraderKind groupMakerWithTraderKind)
		{
			if (GenCollection.Empty<TraderKindDef>(groupMakerWithTraderKind.traderKinds))
			{
				SWCPLog.Warning("A GroupMakerWithTraderKind was defined without any traderKindDefs assigned");
			}
			else
			{
				parms.traderKind = GenCollection.RandomElement<TraderKindDef>((IEnumerable<TraderKindDef>)groupMakerWithTraderKind.traderKinds);
			}
		}
	}

	public static bool PawnGroupKindWorker_Trader_GenerateTrader_Prefix(ref Pawn __result, PawnGroupMakerParms parms, PawnGroupMaker groupMaker, TraderKindDef traderKind)
	{
		if (!(groupMaker is GroupMakerWithTraderKind groupMakerWithTraderKind) || GenCollection.Empty<CharacterDef>(groupMakerWithTraderKind.characterDefs))
		{
			return true;
		}
		if (!Rand.Chance(groupMakerWithTraderKind.characterChance))
		{
			return true;
		}
		List<CharacterDef> list = groupMakerWithTraderKind.characterDefs.ToList();
		UniqueCharactersTracker instance = UniqueCharactersTracker.Instance;
		Pawn val = null;
		Faction faction = parms.faction;
		while (list.Count > 0)
		{
			int index = Rand.Range(0, list.Count);
			CharacterDef charDef = list[index];
			if (!instance.CharacterPawnDead(charDef) && !instance.CharacterPawnSpawned(charDef))
			{
				val = instance.GetOrGenPawn(charDef, null, faction);
				break;
			}
			list.RemoveAt(index);
		}
		if (val == null)
		{
			return true;
		}
		val.mindState.wantsToTradeWithColony = true;
		PawnComponentsUtility.AddAndRemoveDynamicComponents(val, true);
		val.trader.traderKind = traderKind;
		parms.points -= val.kindDef.combatPower;
		__result = val;
		return false;
	}

	public static void PawnGroupKindWorker_Normal_GeneratePawns_Postfix(PawnGroupMakerParms parms, PawnGroupMaker groupMaker, ref List<Pawn> outPawns)
	{
		if (!(groupMaker is GroupMakerWithCustomChar groupMakerWithCustomChar))
		{
			return;
		}
		if (GenCollection.Empty<CharacterDef>(groupMakerWithCustomChar.characterDefs))
		{
			SWCPLog.Warning("A GroupMakerWithCustomChar was defined without any characterDefs assigned");
		}
		else
		{
			if (!Rand.Chance(groupMakerWithCustomChar.characterChance))
			{
				return;
			}
			List<CharacterDef> list = groupMakerWithCustomChar.characterDefs.ToList();
			UniqueCharactersTracker instance = UniqueCharactersTracker.Instance;
			Pawn val = null;
			Faction faction = parms.faction;
			while (list.Count > 0)
			{
				int index = Rand.Range(0, list.Count);
				CharacterDef charDef = list[index];
				if (!instance.CharacterPawnDead(charDef) && !instance.CharacterPawnSpawned(charDef))
				{
					val = instance.GetOrGenPawn(charDef, null, faction);
					break;
				}
				list.RemoveAt(index);
			}
			if (val != null)
			{
				outPawns.Add(val);
			}
		}
	}

	public static void GoodwillSituationWorker_PermanentEnemy_ArePermanentEnemies_Postfix(Faction a, Faction b, ref bool __result)
	{
		if (!__result)
		{
			ModExtension_FactionPermanentlyHostileTo modExtension = ((Def)a.def).GetModExtension<ModExtension_FactionPermanentlyHostileTo>();
			ModExtension_FactionPermanentlyHostileTo modExtension2 = ((Def)a.def).GetModExtension<ModExtension_FactionPermanentlyHostileTo>();
			__result = modExtension?.FactionIsHostileTo(b.def) ?? modExtension2?.FactionIsHostileTo(a.def) ?? __result;
		}
	}

	public static void Faction_CanChangeGoodwillFor_Postfix(Faction other, Faction __instance, ref bool __result)
	{
		if (__result)
		{
			ModExtension_FactionPermanentlyHostileTo modExtension = ((Def)__instance.def).GetModExtension<ModExtension_FactionPermanentlyHostileTo>();
			if (modExtension != null)
			{
				__result = !modExtension.FactionIsHostileTo(other.def);
			}
		}
	}

	public static void FactionDef_PermanentlyHostileTo_Postfix(FactionDef otherFactionDef, FactionDef __instance, ref bool __result)
	{
		if (!__result)
		{
			__result = ((Def)__instance).GetModExtension<ModExtension_FactionPermanentlyHostileTo>()?.FactionIsHostileTo(otherFactionDef) ?? false;
		}
	}

	public static bool Faction_TryMakeInitialRelationsWith_GetInitialGoodwill_Prefix(Faction a, Faction b, ref int __result)
	{
		ModExtension_FactionPermanentlyHostileTo modExtension = ((Def)a.def).GetModExtension<ModExtension_FactionPermanentlyHostileTo>();
		if (modExtension == null || !modExtension.hostileFactionDefs.Contains(b.def))
		{
			return true;
		}
		__result = -100;
		return false;
	}

	public static bool Faction_TryGenerateNewLeader_Prefix(Faction __instance, ref bool __result)
	{
		//IL_010e: Unknown result type (might be due to invalid IL or missing references)
		UniqueCharactersTracker instance = UniqueCharactersTracker.Instance;
		IOrderedEnumerable<CharacterDefWithRole<CharacterRole_FactionLeader>> orderedEnumerable = from charWithRole in CharacterRoleUtils.GetAllWithRole<CharacterRole_FactionLeader>()
			where charWithRole.characterDef.faction == __instance.def
			orderby charWithRole.role.seniority descending
			select charWithRole;
		PawnGenerationRequest value = default(PawnGenerationRequest);
		foreach (CharacterDefWithRole<CharacterRole_FactionLeader> item in orderedEnumerable)
		{
			((PawnGenerationRequest)(ref value))..ctor(item.characterDef.pawnKind, __instance, (PawnGenerationContext)2, (PlanetTile?)null, false, false, false, true, false, 1f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false);
			Pawn orGenPawn = instance.GetOrGenPawn(item.characterDef, value);
			if (((Thing)orGenPawn).Faction != __instance || !item.role.PawnIsValid(orGenPawn))
			{
				continue;
			}
			item.role.ApplyRole(orGenPawn);
			__result = true;
			return false;
		}
		return true;
	}

	private static void WeaponDrawPosPatch(Pawn pawn, ref Vector3 drawPos, Rot4 facing, PawnRenderFlags flags)
	{
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b4: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00dd: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
		//IL_010d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0117: Unknown result type (might be due to invalid IL or missing references)
		//IL_012f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0139: Unknown result type (might be due to invalid IL or missing references)
		//IL_0152: Unknown result type (might be due to invalid IL or missing references)
		//IL_0157: Unknown result type (might be due to invalid IL or missing references)
		//IL_0158: Unknown result type (might be due to invalid IL or missing references)
		//IL_015d: Unknown result type (might be due to invalid IL or missing references)
		//IL_015f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0164: Unknown result type (might be due to invalid IL or missing references)
		//IL_0169: Unknown result type (might be due to invalid IL or missing references)
		//IL_016e: Unknown result type (might be due to invalid IL or missing references)
		Pawn_EquipmentTracker equipment = pawn.equipment;
		if (((equipment != null) ? equipment.Primary : null) == null)
		{
			return;
		}
		Pawn_EquipmentTracker equipment2 = pawn.equipment;
		CompPositionAttributes compPositionAttributes = ((equipment2 != null) ? ThingCompUtility.TryGetComp<CompPositionAttributes>((Thing)(object)equipment2.Primary) : null);
		if (compPositionAttributes != null)
		{
			Vector2 val = Vector2.zero;
			Vector2 val2 = Vector2.zero;
			Stance obj = pawn.stances?.curStance;
			Stance_Busy val3 = (Stance_Busy)(object)((obj is Stance_Busy) ? obj : null);
			if (!((Enum)flags).HasFlag((Enum)(object)(PawnRenderFlags)128) && val3 != null && !val3.neverAimWeapon && ((LocalTargetInfo)(ref val3.focusTarg)).IsValid)
			{
				val = compPositionAttributes.Props.DraftedDrawOffset;
				val2 = compPositionAttributes.Props.DraftedDrawOffsetAbsolute;
			}
			else if (PawnRenderUtility.CarryWeaponOpenly(pawn))
			{
				val = compPositionAttributes.Props.HeldDrawOffset;
				val2 = compPositionAttributes.Props.HeldDrawOffsetAbsolute;
			}
			switch (((Rot4)(ref facing)).AsInt)
			{
			case 1:
			{
				float y2 = val.y;
				val.y = 0f - val.x;
				val.x = 0f - y2;
				break;
			}
			case 3:
			{
				float y = val.y;
				val.y = 0f - val.x;
				val.x = y;
				break;
			}
			}
			drawPos += Vector2Utility.ToVector3(val) + Vector2Utility.ToVector3(val2);
		}
	}

	private static void RarityLabelPatch(List<object> selected, ref string __result)
	{
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		Thing val = null;
		for (int i = 0; i < selected.Count; i++)
		{
			object obj = selected[i];
			Thing val2 = (Thing)((obj is Thing) ? obj : null);
			if (val2 != null)
			{
				val = MinifyUtility.GetInnerIfMinified(val2);
				break;
			}
		}
		CompLabelColored compLabelColored = default(CompLabelColored);
		if (val != null && ThingCompUtility.TryGetComp<CompLabelColored>(val, ref compLabelColored))
		{
			__result = ColoredText.Colorize(__result, compLabelColored.GetRarityColor());
		}
	}
}
You are not using the latest version of the tool, please update.
Latest version is '11.0.0.9375' (yours is '9.0.0.7889')
