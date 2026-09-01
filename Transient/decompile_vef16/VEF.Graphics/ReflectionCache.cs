using System;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class ReflectionCache
{
	public static readonly FieldRef<Thing, Graphic> itemGraphic = AccessTools.FieldRefAccess<Thing, Graphic>(AccessTools.Field(typeof(Thing), "graphicInt"));

	public static readonly Func<Pawn, bool> canOrderPlayerPawn = (Func<Pawn, bool>)Delegate.CreateDelegate(typeof(Func<Pawn, bool>), AccessTools.Method(typeof(PawnAttackGizmoUtility), "CanOrderPlayerPawn", (Type[])null, (Type[])null));

	public static readonly FieldRef<Graphic_Single, Material> graphicMat = AccessTools.FieldRefAccess<Graphic_Single, Material>(AccessTools.Field(typeof(Graphic_Single), "mat"));

	public static readonly FieldRef<CompGeneratedNames, string> compGeneratedNamesName = AccessTools.FieldRefAccess<CompGeneratedNames, string>(AccessTools.Field(typeof(CompGeneratedNames), "name"));
}
