using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using Verse;

namespace FactionLoadout.Util;

public static class ReflectionHelper
{
	public static Lazy<Type> DefDatabaseGenericType = new Lazy<Type>(() => typeof(DefDatabase<>));

	public static Lazy<Type> ListGenericType = new Lazy<Type>(() => typeof(List<>));

	public static Lazy<MethodInfo> GetCompGenericMethod = new Lazy<MethodInfo>(() => AccessTools.Method(typeof(Pawn), "GetComp", (Type[])null, (Type[])null));
}
