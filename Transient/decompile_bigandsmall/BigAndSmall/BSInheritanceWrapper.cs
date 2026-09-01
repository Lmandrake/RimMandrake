using System;
using System.Collections.Generic;
using HarmonyLib;
using Verse;

namespace BigAndSmall;

public static class BSInheritanceWrapper
{
	private static bool initialized;

	private static Traverse GetChildGenesMethod;

	private static Traverse tryXenoByParents;

	public static bool? ModActive { get; private set; }

	public static void TrySetup()
	{
		if (initialized)
		{
			return;
		}
		initialized = true;
		ModActive = ModsConfig.IsActive("RedMattis.BetterGeneInheritance");
		if (ModActive == false)
		{
			return;
		}
		try
		{
			Type type = Type.GetType("BGInheritance.External, BGInheritance") ?? throw new NullReferenceException("\"BGInheritance.External, BGInheritance\" could not be found");
			GetChildGenesMethod = Traverse.Create(type).Method("GetChildGenes", new Type[2]
			{
				typeof(Pawn),
				typeof(Pawn)
			}, (object[])null) ?? throw new MissingMethodException("Could not find GetChildGenes");
			tryXenoByParents = Traverse.Create(type).Method("TrySetXenotypeBasedOnParents", new Type[2]
			{
				typeof(Pawn),
				typeof(List<Pawn>)
			}, (object[])null) ?? throw new MissingMethodException("Could not find TrySetXenotypeBasedOnParents");
		}
		catch (Exception ex)
		{
			Log.Error("BSInheritanceWrapper failed " + ex.Message + "\n" + ex.StackTrace);
		}
	}

	public static List<GeneDef> GetChildGenes(Pawn parentA, Pawn parentB)
	{
		return GetChildGenesMethod.GetValue<List<GeneDef>>(new object[2] { parentA, parentB });
	}

	public static void TrySetXenotypeBasedOnParents(Pawn baby, List<Pawn> parents)
	{
		tryXenoByParents.GetValue(new object[2] { baby, parents });
	}
}
