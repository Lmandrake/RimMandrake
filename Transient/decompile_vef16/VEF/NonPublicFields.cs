using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF;

[StaticConstructorOnStartup]
public static class NonPublicFields
{
	public static readonly FieldRef<IntVec3> SiegeBlueprintPlacer_center = AccessTools.StaticFieldRefAccess<IntVec3>(AccessToolsExtensions.Field(typeof(SiegeBlueprintPlacer), "center"));

	public static readonly FieldRef<Faction> SiegeBlueprintPlacer_faction = AccessTools.StaticFieldRefAccess<Faction>(AccessToolsExtensions.Field(typeof(SiegeBlueprintPlacer), "faction"));

	public static readonly FieldRef<IntRange> SiegeBlueprintPlacer_NumCoverRange = AccessTools.StaticFieldRefAccess<IntRange>(AccessToolsExtensions.Field(typeof(SiegeBlueprintPlacer), "NumCoverRange"));

	public static readonly FieldRef<List<IntVec3>> SiegeBlueprintPlacer_placedCoverLocs = AccessTools.StaticFieldRefAccess<List<IntVec3>>(AccessToolsExtensions.Field(typeof(SiegeBlueprintPlacer), "placedCoverLocs"));

	public static readonly FieldRef<IntRange> SiegeBlueprintPlacer_CoverLengthRange = AccessTools.StaticFieldRefAccess<IntRange>(AccessToolsExtensions.Field(typeof(SiegeBlueprintPlacer), "CoverLengthRange"));

	public static readonly FieldRef<Projectile, int> Projectile_ticksToImpact = AccessTools.FieldRefAccess<Projectile, int>("ticksToImpact");

	public static readonly FieldRef<Projectile, Vector3> Projectile_origin = AccessTools.FieldRefAccess<Projectile, Vector3>("origin");

	public static readonly FieldRef<Projectile, Vector3> Projectile_destination = AccessTools.FieldRefAccess<Projectile, Vector3>("destination");

	public static readonly FieldRef<Projectile, LocalTargetInfo> Projectile_usedTarget = AccessTools.FieldRefAccess<Projectile, LocalTargetInfo>("usedTarget");

	public static readonly FieldRef<CompArt, TaggedString> CompArt_authorNameInt = AccessTools.FieldRefAccess<CompArt, TaggedString>("authorNameInt");

	public static readonly FieldRef<CompArt, TaggedString> CompArt_titleInt = AccessTools.FieldRefAccess<CompArt, TaggedString>("titleInt");

	public static readonly FieldRef<CompArt, TaleReference> CompArt_taleRef = AccessTools.FieldRefAccess<CompArt, TaleReference>("taleRef");
}
