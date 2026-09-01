using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

[HarmonyPatch(typeof(CompEggLayer), "ProduceEgg")]
public class VanillaExpandedFramework_CompEggLayer_ProduceEgg
{
	[HarmonyTranspiler]
	public static IEnumerable<CodeInstruction> ModifyCrossbreedEggThingDef(IEnumerable<CodeInstruction> codeInstructions)
	{
		List<CodeInstruction> codes = codeInstructions.ToList();
		FieldInfo field = AccessTools.DeclaredField(typeof(CompProperties_EggLayer), "eggFertilizedDef");
		MethodInfo method = AccessTools.DeclaredPropertyGetter(typeof(CompEggLayer), "Props");
		FieldInfo extraField = AccessTools.DeclaredField(typeof(CompEggLayer), "fertilizedBy");
		MethodInfo extraMethod = AccessTools.DeclaredMethod(typeof(VanillaExpandedFramework_CompEggLayer_ProduceEgg), "ModifyCrossbreedEgg", (Type[])null, (Type[])null);
		for (int i = 0; i < codes.Count; i++)
		{
			CodeInstruction val = codes[i];
			if (i + 1 < codes.Count && CodeInstructionExtensions.Calls(val, method) && CodeInstructionExtensions.LoadsField(codes[i + 1], field, false))
			{
				yield return CodeInstruction.LoadArgument(0, false);
				yield return new CodeInstruction(OpCodes.Ldfld, (object)extraField);
				yield return new CodeInstruction(OpCodes.Call, (object)extraMethod);
				i++;
			}
			else
			{
				yield return val;
			}
		}
	}

	public static ThingDef ModifyCrossbreedEgg(CompEggLayer comp, Pawn father)
	{
		AnimalCrossbreedExtension animalCrossbreedExtension = ((Def)((Thing)((ThingComp)comp).parent).def).GetModExtension<AnimalCrossbreedExtension>();
		if (animalCrossbreedExtension == null)
		{
			animalCrossbreedExtension = ((father != null) ? ((Def)((Thing)father).def).GetModExtension<AnimalCrossbreedExtension>() : null);
		}
		if (animalCrossbreedExtension == null)
		{
			return comp.Props.eggFertilizedDef;
		}
		switch (animalCrossbreedExtension.crossBreedKindDef)
		{
		case FatherOrMother.AlwaysFather:
		{
			CompEggLayer comp2 = ((ThingWithComps)father).GetComp<CompEggLayer>();
			return ((comp2 != null) ? comp2.Props.eggFertilizedDef : null) ?? comp.Props.eggFertilizedDef;
		}
		case FatherOrMother.Random:
		{
			object obj;
			if (!Rand.Bool)
			{
				CompEggLayer comp3 = ((ThingWithComps)father).GetComp<CompEggLayer>();
				obj = ((comp3 != null) ? comp3.Props.eggFertilizedDef : null);
				if (obj == null)
				{
					return comp.Props.eggFertilizedDef;
				}
			}
			else
			{
				obj = comp.Props.eggFertilizedDef;
			}
			return (ThingDef)obj;
		}
		case FatherOrMother.OtherPawnKind:
		{
			PawnKindDef kindDef2 = null;
			PawnKindDefWeight val = default(PawnKindDefWeight);
			if (animalCrossbreedExtension.otherPawnKindsByWeight != null && GenCollection.TryRandomElementByWeight<PawnKindDefWeight>((IEnumerable<PawnKindDefWeight>)animalCrossbreedExtension.otherPawnKindsByWeight, (Func<PawnKindDefWeight, float>)((PawnKindDefWeight x) => x.weight), ref val))
			{
				kindDef2 = val.kindDef;
			}
			return GetEggForPawnKind(kindDef2) ?? GetEggForPawnKind(animalCrossbreedExtension.otherPawnKind) ?? comp.Props.eggFertilizedDef;
		}
		default:
			return comp.Props.eggFertilizedDef;
		}
		static ThingDef GetEggForPawnKind(PawnKindDef kindDef)
		{
			ThingDef race = kindDef.race;
			if (race == null)
			{
				return null;
			}
			return race.GetCompProperties<CompProperties_EggLayer>()?.eggFertilizedDef;
		}
	}
}
