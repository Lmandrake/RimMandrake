using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Weapons;

public static class OptionalFeatures_WeaponTraitDefFeatures
{
	public static void ApplyFeature(Harmony harm)
	{
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Expected O, but got Unknown
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Expected O, but got Unknown
		//IL_0095: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Expected O, but got Unknown
		//IL_00cb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d6: Expected O, but got Unknown
		//IL_0105: Unknown result type (might be due to invalid IL or missing references)
		//IL_0110: Expected O, but got Unknown
		//IL_0139: Unknown result type (might be due to invalid IL or missing references)
		//IL_0145: Expected O, but got Unknown
		//IL_016e: Unknown result type (might be due to invalid IL or missing references)
		//IL_017a: Expected O, but got Unknown
		//IL_01ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b8: Expected O, but got Unknown
		//IL_020d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0219: Expected O, but got Unknown
		//IL_0241: Unknown result type (might be due to invalid IL or missing references)
		//IL_024c: Expected O, but got Unknown
		//IL_0275: Unknown result type (might be due to invalid IL or missing references)
		//IL_0281: Expected O, but got Unknown
		//IL_02a9: Unknown result type (might be due to invalid IL or missing references)
		//IL_02b6: Expected O, but got Unknown
		//IL_02de: Unknown result type (might be due to invalid IL or missing references)
		//IL_02eb: Expected O, but got Unknown
		//IL_0316: Unknown result type (might be due to invalid IL or missing references)
		//IL_0320: Expected O, but got Unknown
		harm.Patch((MethodBase)AccessTools.Method(typeof(Pawn), "GetInspectString", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_Pawn_GetInspectString_Patch), "AddInspectString", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Property(typeof(Verb_LaunchProjectile), "Projectile").GetMethod, (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_Verb_LaunchProjectile_Projectile_Patch), "ChangeProjectile", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(Verb_MeleeAttack), "SoundHitPawn", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_Verb_MeleeAttack_SoundHitPawn_Patch), "ChangeMeleeSound", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(Verb), "TryCastNextBurstShot", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_Verb_TryCastNextBurstShot_Patch), "ChangeSoundProduced", (Type[])null), (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.EnumeratorMoveNext((MethodBase)AccessTools.Method(typeof(Verb_MeleeAttackDamage), "DamageInfosToApply", (Type[])null, (Type[])null)), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_Verb_MeleeAttackDamage_DamageInfosToApply_Patch), "ModifyMeleeDamage", (Type[])null), (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(CompUniqueWeapon), "AddTrait", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_CompUniqueWeapon_AddTrait_Patch), "HandleExtendedWorker", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(Pawn_EquipmentTracker), "Notify_AbilityUsed", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_Pawn_EquipmentTracker_Notify_AbilityUsed_Patch), "NotifyAbilityUses", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessToolsExtensions.PropertyGetter(typeof(CompEquippable), "VerbProperties"), new HarmonyMethod((Delegate)new _003C_003EF_007B00000008_007D<CompEquippable, List<VerbProperties>, bool>(VanillaExpandedFramework_CompEquippable_VerbProperties_Patch.UseVerbTraitsIfPresent)), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(VerbProperties), "AdjustedCooldown", new Type[3]
		{
			typeof(Tool),
			typeof(Pawn),
			typeof(Thing)
		}, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_VerbProperties_AdjustedCooldown_Patch), "RandomizeCooldown", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessToolsExtensions.PropertyGetter(typeof(Verb), "BurstShotCount"), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_Verb_BurstShotCount_Patch), "RandomizeBurstCount", (Type[])null), (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(IncidentWorker_TraderCaravanArrival), "TryExecuteWorker", (Type[])null, (Type[])null), (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_IncidentWorker_TraderCaravanArrival_TryExecuteWorker_Patch), "DetectEmpireContraband", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(PawnRenderUtility), "DrawEquipmentAndApparelExtras", (Type[])null, (Type[])null), new HarmonyMethod(typeof(VanillaExpandedFramework_PawnRenderUtility_DrawEquipmentAiming_Patch), "GrabPawn", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(PawnRenderUtility), "DrawEquipmentAiming", (Type[])null, (Type[])null), new HarmonyMethod(typeof(VanillaExpandedFramework_PawnRenderUtility_DrawEquipmentAiming_Patch), "DrawDuplicate", (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null);
		harm.Patch((MethodBase)AccessTools.Method(typeof(PawnRenderUtility), "DrawEquipmentAiming", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod(typeof(VanillaExpandedFramework_PawnRenderUtility_DrawEquipmentAiming_Patch), "DrawDuplicateCleanup", (Type[])null));
	}
}
