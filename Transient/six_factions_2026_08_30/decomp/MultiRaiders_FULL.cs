using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.CompilerServices;
using System.Runtime.Versioning;
using HarmonyLib;
using Microsoft.CodeAnalysis;
using MultiRaiders.Debug;
using MultiRaiders.Graphics;
using MultiRaiders.Hediff;
using MultiRaiders.Helpers;
using MultiRaiders.Map;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.AI.Group;

[assembly: CompilationRelaxations(8)]
[assembly: RuntimeCompatibility(WrapNonExceptionThrows = true)]
[assembly: Debuggable(DebuggableAttribute.DebuggingModes.Default | DebuggableAttribute.DebuggingModes.DisableOptimizations | DebuggableAttribute.DebuggingModes.IgnoreSymbolStoreSequencePoints | DebuggableAttribute.DebuggingModes.EnableEditAndContinue)]
[assembly: TargetFramework(".NETFramework,Version=v4.8", FrameworkDisplayName = ".NET Framework 4.8")]
[assembly: AssemblyCompany("Dylan, Owlchemist, Ingendum")]
[assembly: AssemblyConfiguration("Debug")]
[assembly: AssemblyCopyright("2026")]
[assembly: AssemblyFileVersion("1.4.2")]
[assembly: AssemblyInformationalVersion("1.6+6150c80a2710d5128fbaa6ccec9f3a8e1b8346dd")]
[assembly: AssemblyProduct("Animal Gear")]
[assembly: AssemblyTitle("MultiRaiders")]
[assembly: AssemblyVersion("1.4.2.0")]
[module: RefSafetyRules(11)]
namespace Microsoft.CodeAnalysis
{
	[CompilerGenerated]
	[Embedded]
	internal sealed class EmbeddedAttribute : Attribute
	{
	}
}
namespace System.Runtime.CompilerServices
{
	[CompilerGenerated]
	[Embedded]
	[AttributeUsage(AttributeTargets.Module, AllowMultiple = false, Inherited = false)]
	internal sealed class RefSafetyRulesAttribute : Attribute
	{
		public readonly int Version;

		public RefSafetyRulesAttribute(int P_0)
		{
			Version = P_0;
		}
	}
}
namespace MultiRaiders
{
	public class RaiderSwarmCompressionMod : Mod
	{
		private RaiderSwarmCompressionSettings settings;

		private string MaxRealRaidersBuffer = "";

		public RaiderSwarmCompressionMod(ModContentPack content)
			: base(content)
		{
			//IL_003b: Unknown result type (might be due to invalid IL or missing references)
			settings = ((Mod)this).GetSettings<RaiderSwarmCompressionSettings>();
			MaxRealRaidersBuffer = settings.MaxRealRaiders.ToString();
			new Harmony("Ingendum.RaiderSwarmCompression").PatchAll();
		}

		public override void DoSettingsWindowContents(Rect inRect)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Expected O, but got Unknown
			//IL_0008: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			//IL_0044: Unknown result type (might be due to invalid IL or missing references)
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_005b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0066: Unknown result type (might be due to invalid IL or missing references)
			//IL_0086: Unknown result type (might be due to invalid IL or missing references)
			//IL_008b: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e2: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f9: Unknown result type (might be due to invalid IL or missing references)
			//IL_0104: Unknown result type (might be due to invalid IL or missing references)
			//IL_011d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0122: Unknown result type (might be due to invalid IL or missing references)
			//IL_0175: Unknown result type (might be due to invalid IL or missing references)
			//IL_01dd: Unknown result type (might be due to invalid IL or missing references)
			Listing_Standard val = new Listing_Standard();
			((Listing)val).Begin(inRect);
			((Listing)val).Gap(12f);
			((Listing)val).Gap(12f);
			val.Label(Translator.Translate("ReplaceAlwaysFractionDesc1"), -1f, (string)null);
			val.Label(Translator.Translate("ReplaceAlwaysFractionDesc2"), -1f, (string)null);
			val.Label(Translator.Translate("ReplaceAlwaysFractionRec"), -1f, (string)null);
			float replaceFractionWithFakes = settings.ReplaceFractionWithFakes;
			float replaceFractionWithFakes2 = val.SliderLabeled(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("ReplaceAlwaysFraction", NamedArgument.op_Implicit((int)(replaceFractionWithFakes * 100f)))), replaceFractionWithFakes, 0f, 0.9f, 0.6f, (string)null);
			settings.ReplaceFractionWithFakes = replaceFractionWithFakes2;
			((Listing)val).GapLine(12f);
			((Listing)val).Gap(12f);
			((Listing)val).Gap(12f);
			val.Label(Translator.Translate("MaxRealRaidersDesc1"), -1f, (string)null);
			val.Label(Translator.Translate("MaxRealRaidersRec"), -1f, (string)null);
			int maxRealRaiders = settings.MaxRealRaiders;
			int maxRealRaiders2 = Mathf.RoundToInt(val.SliderLabeled(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MaxRealRaiders", NamedArgument.op_Implicit(maxRealRaiders))), (float)maxRealRaiders, 1f, 500f, 0.6f, (string)null));
			settings.MaxRealRaiders = maxRealRaiders2;
			((Listing)val).GapLine(12f);
			((Listing)val).Gap(12f);
			val.CheckboxLabeled(TaggedString.op_Implicit(Translator.Translate("ExplosionDamagePropagates")), ref settings.PropagateExplosionDamage, (string)null, 0f, 1f);
			((Listing)val).Gap(12f);
			((Listing)val).Gap(12f);
			val.CheckboxLabeled("Debug", ref settings.Debug, (string)null, 0f, 1f);
			((Listing)val).End();
			((Mod)this).DoSettingsWindowContents(inRect);
		}

		public override string SettingsCategory()
		{
			return "Raider Swarm Compression";
		}
	}
	public class RaiderSwarmCompressionSettings : ModSettings
	{
		public float ReplaceFractionWithFakes = 0f;

		public int MaxRealRaiders = 120;

		public bool PropagateExplosionDamage = true;

		public bool Debug = false;

		public static RaiderSwarmCompressionSettings Settings => ((Mod)LoadedModManager.GetMod<RaiderSwarmCompressionMod>()).GetSettings<RaiderSwarmCompressionSettings>();

		public override void ExposeData()
		{
			Scribe_Values.Look<float>(ref ReplaceFractionWithFakes, "ReplaceFractionWithFakes", 0f, false);
			Scribe_Values.Look<int>(ref MaxRealRaiders, "MaxRealRaiders", 0, false);
			Scribe_Values.Look<bool>(ref PropagateExplosionDamage, "propagateExplosionDamage", false, false);
			Scribe_Values.Look<bool>(ref Debug, "Debug", false, false);
			((ModSettings)this).ExposeData();
		}
	}
}
namespace MultiRaiders.Patches
{
	public class IncidentPatches
	{
		[HarmonyPatch(typeof(RaidStrategyWorker), "SpawnThreats")]
		public static class RaidStrategyWorker_SpawnThreats_Patch
		{
			public static bool Prefix(ref List<Pawn> __result, RaidStrategyWorker __instance, IncidentParms parms)
			{
				//IL_008c: Unknown result type (might be due to invalid IL or missing references)
				//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
				//IL_0147: Unknown result type (might be due to invalid IL or missing references)
				if (parms.pawnKind == null)
				{
					return true;
				}
				if (parms.pawnCount == 0)
				{
					return true;
				}
				int pawnCount = parms.pawnCount;
				int maxRealRaiders = RaiderSwarmCompressionSettings.Settings.MaxRealRaiders;
				int num = Math.Min(maxRealRaiders, (int)((float)parms.pawnCount * (1f - RaiderSwarmCompressionSettings.Settings.ReplaceFractionWithFakes)));
				int num2 = Math.Max(0, pawnCount - num);
				List<Pawn> list = new List<Pawn>();
				PawnGenerationRequest val2 = default(PawnGenerationRequest);
				for (int i = 0; i < pawnCount; i++)
				{
					PawnKindDef pawnKind = parms.pawnKind;
					Faction faction = parms.faction;
					PawnGenerationContext val = (PawnGenerationContext)2;
					float biocodeWeaponsChance = parms.biocodeWeaponsChance;
					float biocodeApparelChance = parms.biocodeApparelChance;
					bool pawnsCanBringFood = __instance.def.pawnsCanBringFood;
					((PawnGenerationRequest)(ref val2))..ctor(pawnKind, faction, val, (PlanetTile?)null, false, false, false, true, true, 1f, false, true, false, pawnsCanBringFood, true, false, false, false, false, biocodeWeaponsChance, biocodeApparelChance, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false);
					((PawnGenerationRequest)(ref val2)).BiocodeApparelChance = 1f;
					Pawn val3 = PawnGenerator.GeneratePawn(val2);
					if (val3 != null)
					{
						list.Add(val3);
					}
				}
				if (GenCollection.Any<Pawn>(list))
				{
					List<Pawn> list2 = GeneratorHelper.SwarmifySpawnedPawns(list);
					parms.raidArrivalMode.Worker.Arrive(list2, parms);
					__result = list2;
					return false;
				}
				__result = null;
				return false;
			}
		}

		[HarmonyPatch(typeof(PawnGroupKindWorker_Normal), "GeneratePawns")]
		public static class PawnGroupKindWorker_GeneratePawns_Patch
		{
			public static bool Prefix(PawnGroupKindWorker_Normal __instance, PawnGroupMakerParms parms, PawnGroupMaker groupMaker, List<Pawn> outPawns, bool errorOnZeroResults = true)
			{
				//IL_0147: Unknown result type (might be due to invalid IL or missing references)
				//IL_014c: Unknown result type (might be due to invalid IL or missing references)
				//IL_016b: Unknown result type (might be due to invalid IL or missing references)
				//IL_018b: Unknown result type (might be due to invalid IL or missing references)
				//IL_01a8: Unknown result type (might be due to invalid IL or missing references)
				//IL_029f: Unknown result type (might be due to invalid IL or missing references)
				//IL_02db: Unknown result type (might be due to invalid IL or missing references)
				//IL_032e: Unknown result type (might be due to invalid IL or missing references)
				//IL_0391: Unknown result type (might be due to invalid IL or missing references)
				//IL_03b2: Unknown result type (might be due to invalid IL or missing references)
				//IL_03a3: Unknown result type (might be due to invalid IL or missing references)
				if (!((PawnGroupKindWorker)__instance).CanGenerateFrom(parms, groupMaker))
				{
					if (errorOnZeroResults)
					{
						string[] array = new string[5] { "Cannot generate pawns for ", null, null, null, null };
						int num = 1;
						array[num] = ((object)parms.faction)?.ToString();
						array[2] = " with ";
						array[3] = parms.points.ToString();
						array[4] = ". Defaulting to a single random cheap group.";
						Log.Error(string.Concat(array));
					}
					return false;
				}
				bool flag = parms.raidStrategy == null || parms.raidStrategy.pawnsCanBringFood || (parms.faction != null && !FactionUtility.HostileTo(parms.faction, Faction.OfPlayer));
				bool flag2 = false;
				bool flag3 = false;
				bool flag4 = false;
				Predicate<Pawn> predicate = ((parms.raidStrategy != null) ? ((Predicate<Pawn>)((Pawn p) => parms.raidStrategy.Worker.CanUsePawn(parms.points, p, outPawns))) : null);
				Dictionary<PawnGenOptionWithXenotype, List<Pawn>> dictionary = new Dictionary<PawnGenOptionWithXenotype, List<Pawn>>();
				PawnGenerationRequest val3 = default(PawnGenerationRequest);
				foreach (PawnGenOptionWithXenotype item in PawnGroupMakerUtility.ChoosePawnGenOptionsByPoints(parms.points, groupMaker.options, parms))
				{
					PawnGenOptionWithXenotype current = item;
					PawnKindDef kind = ((PawnGenOptionWithXenotype)(ref current)).Option.kind;
					Faction faction = parms.faction;
					PawnGenerationContext val = (PawnGenerationContext)2;
					Ideo ideo = parms.ideo;
					XenotypeDef xenotype = ((PawnGenOptionWithXenotype)(ref current)).Xenotype;
					PlanetTile? val2 = parms.tile;
					bool inhabitants = parms.inhabitants;
					((PawnGenerationRequest)(ref val3))..ctor(kind, faction, val, val2, flag3, flag4, parms.faction.deactivated, true, true, 1f, false, true, true, flag, true, inhabitants, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, predicate, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, ideo, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, xenotype, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false);
					if (parms.raidAgeRestriction != null && parms.raidAgeRestriction.Worker.ShouldApplyToKind(((PawnGenOptionWithXenotype)(ref current)).Option.kind))
					{
						((PawnGenerationRequest)(ref val3)).BiologicalAgeRange = parms.raidAgeRestriction.ageRange;
						((PawnGenerationRequest)(ref val3)).AllowedDevelopmentalStages = parms.raidAgeRestriction.developmentStage;
					}
					if (((PawnGenOptionWithXenotype)(ref current)).Option.kind.pawnGroupDevelopmentStage.HasValue)
					{
						((PawnGenerationRequest)(ref val3)).AllowedDevelopmentalStages = ((PawnGenOptionWithXenotype)(ref current)).Option.kind.pawnGroupDevelopmentStage.Value;
					}
					if (!Find.Storyteller.difficulty.ChildRaidersAllowed && parms.faction != null && FactionUtility.HostileTo(parms.faction, Faction.OfPlayer))
					{
						((PawnGenerationRequest)(ref val3)).AllowedDevelopmentalStages = (DevelopmentalStage)8;
					}
					Pawn val4 = PawnGenerator.GeneratePawn(val3);
					if (parms.forceOneDowned && !flag2)
					{
						val4.health.forceDowned = true;
						if (val4.guest != null)
						{
							val4.guest.Recruitable = true;
						}
						val4.mindState.canFleeIndividual = false;
						flag2 = true;
					}
					if (!dictionary.ContainsKey(current))
					{
						dictionary.Add(current, new List<Pawn>());
					}
					dictionary[current].Add(val4);
				}
				outPawns.AddRange(GeneratorHelper.SwarmifySpawnedPawns(dictionary));
				return false;
			}
		}

		[HarmonyPatch(typeof(PawnGroupKindWorker_Shamblers), "GeneratePawns")]
		public static class PawnGroupKindWorker_Shamblers_GeneratePawns_Patch
		{
			public static bool Prefix(PawnGroupKindWorker_Shamblers __instance, PawnGroupMakerParms parms, PawnGroupMaker groupMaker, List<Pawn> outPawns, bool errorOnZeroResults = true)
			{
				//IL_010d: Unknown result type (might be due to invalid IL or missing references)
				//IL_0152: Unknown result type (might be due to invalid IL or missing references)
				//IL_0154: Unknown result type (might be due to invalid IL or missing references)
				//IL_0156: Unknown result type (might be due to invalid IL or missing references)
				//IL_016d: Unknown result type (might be due to invalid IL or missing references)
				//IL_01da: Unknown result type (might be due to invalid IL or missing references)
				//IL_01dd: Unknown result type (might be due to invalid IL or missing references)
				//IL_01f4: Unknown result type (might be due to invalid IL or missing references)
				//IL_0139: Unknown result type (might be due to invalid IL or missing references)
				//IL_013c: Unknown result type (might be due to invalid IL or missing references)
				//IL_013d: Unknown result type (might be due to invalid IL or missing references)
				if (!((PawnGroupKindWorker)__instance).CanGenerateFrom(parms, groupMaker))
				{
					if (errorOnZeroResults)
					{
						string[] array = new string[5] { "Cannot generate pawns for ", null, null, null, null };
						int num = 1;
						array[num] = ((object)parms.faction)?.ToString();
						array[2] = " with ";
						array[3] = parms.points.ToString();
						array[4] = ". Defaulting to a single random cheap group.";
						Log.Error(string.Concat(array));
					}
					return false;
				}
				float num2 = parms.points;
				float num3 = groupMaker.options.Min((PawnGenOption opt) => opt.Cost);
				Dictionary<PawnGenOption, List<Pawn>> dictionary = new Dictionary<PawnGenOption, List<Pawn>>();
				PawnGenOption val = default(PawnGenOption);
				FloatRange value = default(FloatRange);
				while (num2 > num3)
				{
					GenCollection.TryRandomElementByWeight<PawnGenOption>((IEnumerable<PawnGenOption>)groupMaker.options, (Func<PawnGenOption, float>)((PawnGenOption gr) => gr.selectionWeight), ref val);
					if (val.Cost <= num2)
					{
						num2 -= val.Cost;
						DevelopmentalStage val2 = (DevelopmentalStage)8;
						if (Find.Storyteller.difficulty.ChildrenAllowed && Find.Storyteller.difficulty.childShamblersAllowed)
						{
							val2 = (DevelopmentalStage)(val2 | 4);
						}
						PawnKindDef kind = val.kind;
						Faction faction = parms.faction;
						PawnGenerationContext val3 = (PawnGenerationContext)2;
						DevelopmentalStage val4 = val2;
						((FloatRange)(ref value))..ctor(0f, 8f);
						Pawn item = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, faction, val3, (PlanetTile?)null, false, false, false, true, false, 1f, false, true, false, true, true, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, false, false, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 0f, val4, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)value, (FloatRange?)null, false, false, false, -1, 0, false));
						if (!dictionary.ContainsKey(val))
						{
							dictionary.Add(val, new List<Pawn>());
						}
						dictionary[val].Add(item);
					}
				}
				outPawns.AddRange(GeneratorHelper.SwarmifySpawnedPawns(dictionary));
				return false;
			}
		}

		[HarmonyPatch(typeof(AggressiveAnimalIncidentUtility), "GenerateAnimals", new Type[]
		{
			typeof(PawnKindDef),
			typeof(PlanetTile),
			typeof(float),
			typeof(int)
		})]
		public static class AggressiveAnimalIncidentUtility_GenerateAnimals_Patch
		{
			public static void Postfix(ref List<Pawn> __result, PawnKindDef animalKind, PlanetTile tile, float points, int animalCount = 0)
			{
				__result = GeneratorHelper.SwarmifySpawnedPawns(__result);
			}
		}

		[HarmonyPatch(typeof(AggressiveAnimalIncidentUtility), "GenerateAnimals", new Type[]
		{
			typeof(List<PawnKindDef>),
			typeof(PlanetTile)
		})]
		public static class AggressiveAnimalIncidentUtility_GenerateAnimals2_Patch
		{
			public static void Postfix(ref List<Pawn> __result, List<PawnKindDef> animalKinds, PlanetTile tile)
			{
				__result = GeneratorHelper.SwarmifySpawnedPawns(__result);
			}
		}

		[HarmonyPatch(typeof(IncidentWorker_AggressiveAnimals), "TryExecuteWorker")]
		public static class ThingDef_get_DescriptionDetailed_Patch
		{
			[CompilerGenerated]
			private sealed class <Transpiler>d__0 : IEnumerable<CodeInstruction>, IEnumerable, IEnumerator<CodeInstruction>, IDisposable, IEnumerator
			{
				private int <>1__state;

				private CodeInstruction <>2__current;

				private int <>l__initialThreadId;

				private IEnumerable<CodeInstruction> instructions;

				public IEnumerable<CodeInstruction> <>3__instructions;

				private List<CodeInstruction> <codes>5__1;

				private MethodInfo <addScariaMethod>5__2;

				private int <i>5__3;

				CodeInstruction IEnumerator<CodeInstruction>.Current
				{
					[DebuggerHidden]
					get
					{
						return <>2__current;
					}
				}

				object IEnumerator.Current
				{
					[DebuggerHidden]
					get
					{
						return <>2__current;
					}
				}

				[DebuggerHidden]
				public <Transpiler>d__0(int <>1__state)
				{
					this.<>1__state = <>1__state;
					<>l__initialThreadId = Environment.CurrentManagedThreadId;
				}

				[DebuggerHidden]
				void IDisposable.Dispose()
				{
					<codes>5__1 = null;
					<addScariaMethod>5__2 = null;
					<>1__state = -2;
				}

				private bool MoveNext()
				{
					//IL_02a9: Unknown result type (might be due to invalid IL or missing references)
					//IL_02b3: Expected O, but got Unknown
					//IL_02d1: Unknown result type (might be due to invalid IL or missing references)
					//IL_02db: Expected O, but got Unknown
					switch (<>1__state)
					{
					default:
						return false;
					case 0:
						<>1__state = -1;
						<codes>5__1 = new List<CodeInstruction>(instructions);
						<addScariaMethod>5__2 = AccessTools.Method(typeof(MirrorImageHelper), "AddScariaToMirrors", (Type[])null, (Type[])null);
						<i>5__3 = 0;
						break;
					case 1:
						<>1__state = -1;
						<>2__current = <codes>5__1[<i>5__3++];
						<>1__state = 2;
						return true;
					case 2:
						<>1__state = -1;
						<>2__current = <codes>5__1[<i>5__3++];
						<>1__state = 3;
						return true;
					case 3:
						<>1__state = -1;
						<>2__current = <codes>5__1[<i>5__3++];
						<>1__state = 4;
						return true;
					case 4:
						<>1__state = -1;
						<>2__current = <codes>5__1[<i>5__3++];
						<>1__state = 5;
						return true;
					case 5:
						<>1__state = -1;
						<>2__current = <codes>5__1[<i>5__3++];
						<>1__state = 6;
						return true;
					case 6:
						<>1__state = -1;
						<>2__current = <codes>5__1[<i>5__3++];
						<>1__state = 7;
						return true;
					case 7:
						<>1__state = -1;
						<>2__current = <codes>5__1[<i>5__3];
						<>1__state = 8;
						return true;
					case 8:
						<>1__state = -1;
						<>2__current = new CodeInstruction(OpCodes.Dup, (object)null);
						<>1__state = 9;
						return true;
					case 9:
						<>1__state = -1;
						<>2__current = new CodeInstruction(OpCodes.Callvirt, (object)<addScariaMethod>5__2);
						<>1__state = 10;
						return true;
					case 10:
						<>1__state = -1;
						goto IL_0319;
					case 11:
						{
							<>1__state = -1;
							goto IL_0319;
						}
						IL_0319:
						<i>5__3++;
						break;
					}
					if (<i>5__3 < <codes>5__1.Count)
					{
						if (<codes>5__1[<i>5__3].opcode == OpCodes.Ldsfld && <codes>5__1[<i>5__3].operand as FieldInfo == AccessTools.Field(typeof(HediffDefOf), "Scaria"))
						{
							<>2__current = <codes>5__1[<i>5__3++];
							<>1__state = 1;
							return true;
						}
						<>2__current = <codes>5__1[<i>5__3];
						<>1__state = 11;
						return true;
					}
					return false;
				}

				bool IEnumerator.MoveNext()
				{
					//ILSpy generated this explicit interface implementation from .override directive in MoveNext
					return this.MoveNext();
				}

				[DebuggerHidden]
				void IEnumerator.Reset()
				{
					throw new NotSupportedException();
				}

				[DebuggerHidden]
				IEnumerator<CodeInstruction> IEnumerable<CodeInstruction>.GetEnumerator()
				{
					<Transpiler>d__0 <Transpiler>d__;
					if (<>1__state == -2 && <>l__initialThreadId == Environment.CurrentManagedThreadId)
					{
						<>1__state = 0;
						<Transpiler>d__ = this;
					}
					else
					{
						<Transpiler>d__ = new <Transpiler>d__0(0);
					}
					<Transpiler>d__.instructions = <>3__instructions;
					return <Transpiler>d__;
				}

				[DebuggerHidden]
				IEnumerator IEnumerable.GetEnumerator()
				{
					return ((IEnumerable<CodeInstruction>)this).GetEnumerator();
				}
			}

			[IteratorStateMachine(typeof(<Transpiler>d__0))]
			public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
			{
				//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
				return new <Transpiler>d__0(-2)
				{
					<>3__instructions = instructions
				};
			}
		}

		[HarmonyPatch(typeof(Hediff_Scaria), "get_IsBerserk")]
		public static class Hediff_Scaria_get_IsBerserk_Patch
		{
			public static bool Prefix(Hediff_Scaria __instance, ref bool __result)
			{
				if (((Hediff)__instance).pawn?.mindState?.mentalStateHandler == null)
				{
					__result = false;
					return false;
				}
				return true;
			}
		}
	}
	public class PawnPatches
	{
		[HarmonyPatch(typeof(Pawn_HealthTracker), "MakeDowned")]
		public static class Pawn_HealthTracker_MakeDowned_Patch
		{
			private static Lazy<FieldInfo> _effectivePawn = new Lazy<FieldInfo>(() => AccessTools.Field(typeof(Pawn_HealthTracker), "pawn"));

			public static void Postfix(Pawn_HealthTracker __instance, DamageInfo? dinfo, Hediff hediff)
			{
				//IL_0011: Unknown result type (might be due to invalid IL or missing references)
				//IL_0017: Expected O, but got Unknown
				Pawn val = (Pawn)_effectivePawn.Value.GetValue(__instance);
				val.health.hediffSet.GetFirstHediff<HediffMirrorImage>()?.SpawnNextInLine();
			}
		}

		[HarmonyPatch(typeof(Pawn_HealthTracker), "SetDead")]
		public static class Pawn_HealthTracker_SetDead_Patch
		{
			private static Lazy<FieldInfo> _effectivePawn = new Lazy<FieldInfo>(() => AccessTools.Field(typeof(Pawn_HealthTracker), "pawn"));

			public static void Postfix(Pawn_HealthTracker __instance)
			{
				//IL_0011: Unknown result type (might be due to invalid IL or missing references)
				//IL_0017: Expected O, but got Unknown
				Pawn val = (Pawn)_effectivePawn.Value.GetValue(__instance);
				val.health.hediffSet.GetFirstHediff<HediffMirrorImage>()?.SpawnNextInLine();
			}
		}

		[HarmonyPatch(typeof(Pawn), "ExitMap")]
		public static class Pawn_ExitMap_Patch
		{
			public static bool Prefix(Pawn __instance, bool allowedToJoinOrCreateCaravan, Rot4 exitDir)
			{
				if (__instance == null || __instance.health == null)
				{
					return true;
				}
				HediffMirrorImage firstHediff;
				while ((firstHediff = __instance.health.hediffSet.GetFirstHediff<HediffMirrorImage>()) != null)
				{
					__instance.health.RemoveHediff((Hediff)(object)firstHediff);
				}
				return true;
			}
		}

		[HarmonyPatch(typeof(DistressCallUtility), "SpawnCorpses")]
		public static class DistressCallUtility_SpawnCorpses_Patch
		{
			public static bool Prefix(Pawn __instance, Map map, IEnumerable<Pawn> pawns, IEnumerable<Pawn> killers, IntVec3 root, int radius)
			{
				foreach (Pawn pawn in pawns)
				{
					if (pawn != null && pawn.health != null)
					{
						HediffMirrorImage firstHediff;
						while ((firstHediff = pawn.health.hediffSet.GetFirstHediff<HediffMirrorImage>()) != null)
						{
							pawn.health.RemoveHediff((Hediff)(object)firstHediff);
						}
					}
				}
				return true;
			}
		}

		[HarmonyPatch(typeof(DamageWorker), "ExplosionDamageThing")]
		public static class DamageWorker_ExplosionDamageThing_Patch
		{
			public static void Prefix(DamageWorker __instance, Explosion explosion, Thing t, List<Thing> damagedThings, List<Thing> ignoredThings, IntVec3 cell)
			{
				//IL_0118: Unknown result type (might be due to invalid IL or missing references)
				if (!RaiderSwarmCompressionSettings.Settings.PropagateExplosionDamage)
				{
					return;
				}
				Pawn val = (Pawn)(object)((t is Pawn) ? t : null);
				if (val == null)
				{
					return;
				}
				MultiRaidersDebug.LogMessage("ExplosionDamageThing postfix for " + (object)val);
				HediffMirrorImage firstHediff = val.health.hediffSet.GetFirstHediff<HediffMirrorImage>();
				if (firstHediff == null)
				{
					return;
				}
				MultiRaidersDebug.LogMessage("MirrorImages " + firstHediff.FakePawns.Count);
				foreach (Pawn item in new List<Pawn>(firstHediff.FakePawns))
				{
					MultiRaidersDebug.LogMessage("Mirror image " + (object)item);
					if (!item.Dead)
					{
						MultiRaidersDebug.LogMessage("Applying explosion damage to fake pawn " + (object)item);
						_ExplosionDamageThing.Value.Invoke(__instance, new object[5]
						{
							explosion,
							item,
							new List<Thing>(),
							ignoredThings,
							cell
						});
					}
				}
				firstHediff.MaybeEjectDeadOrDowned();
			}
		}

		private static Lazy<MethodInfo> _ExplosionDamageThing = new Lazy<MethodInfo>(() => AccessTools.Method(typeof(DamageWorker), "ExplosionDamageThing", (Type[])null, (Type[])null));
	}
	public class UIPatches
	{
		[HarmonyPatch(typeof(InspectPaneUtility), "AdjustedLabelFor")]
		public static class InspectPaneUtility_AdjustedLabelFor_Patch
		{
			public static void Postfix(ref string __result, List<object> selected, Rect rect)
			{
				//IL_00d7: Unknown result type (might be due to invalid IL or missing references)
				//IL_00dc: Unknown result type (might be due to invalid IL or missing references)
				if (selected[0] is IRenameable)
				{
					return;
				}
				List<Pawn> list = new List<Pawn>();
				for (int i = 0; i < selected.Count; i++)
				{
					object obj = selected[i];
					Pawn val = (Pawn)((obj is Pawn) ? obj : null);
					if (val != null)
					{
						list.Add(val);
					}
				}
				int num = 0;
				foreach (Pawn item in list)
				{
					HediffMirrorImage firstHediff = item.health.hediffSet.GetFirstHediff<HediffMirrorImage>();
					if (firstHediff != null)
					{
						num += firstHediff.FakePawns.Count;
					}
				}
				if (num > 0)
				{
					__result += string.Format(" {0}", TranslatorFormattedStringExtensions.Translate("Compressed", NamedArgument.op_Implicit(num)));
				}
			}
		}
	}
}
namespace MultiRaiders.Map
{
	public class MultiRaidersMapComponent : MapComponent
	{
		private Dictionary<Pawn, (HediffMirrorImage hediff, HediffComp_MirrorImage comp)> mirrorCache = new Dictionary<Pawn, (HediffMirrorImage, HediffComp_MirrorImage)>();

		private int lastCacheUpdateTick = -1;

		private int numEntitiesSinceLastUpdate = -1;

		private const int CacheUpdateInterval = 60;

		public MultiRaidersMapComponent(Map map)
			: base(map)
		{
		}

		public override void MapComponentUpdate()
		{
			//IL_00c8: Unknown result type (might be due to invalid IL or missing references)
			if (Find.TickManager.TicksGame - lastCacheUpdateTick > 60 || numEntitiesSinceLastUpdate != base.map.mapPawns.AllPawnsSpawned.Count)
			{
				UpdateMirrorCache();
				lastCacheUpdateTick = Find.TickManager.TicksGame;
			}
			foreach (KeyValuePair<Pawn, (HediffMirrorImage, HediffComp_MirrorImage)> item in mirrorCache)
			{
				Pawn key = item.Key;
				var (hediffMirrorImage, hediffComp_MirrorImage) = item.Value;
				if (key != null && ((Thing)key).Spawned && hediffComp_MirrorImage != null && ((Thing)key).Map == Find.CurrentMap && !WorldRendererUtility.WorldRendered)
				{
					hediffComp_MirrorImage.DrawAt(GenThing.TrueCenter((Thing)(object)key));
				}
			}
		}

		private void UpdateMirrorCache()
		{
			mirrorCache.Clear();
			foreach (Pawn item in base.map.mapPawns.AllPawnsSpawned)
			{
				HediffMirrorImage firstHediff = item.health.hediffSet.GetFirstHediff<HediffMirrorImage>();
				if (firstHediff != null)
				{
					HediffComp_MirrorImage comp = ((HediffWithComps)firstHediff).GetComp<HediffComp_MirrorImage>();
					if (comp != null && !InvisibilityUtility.IsPsychologicallyInvisible(item))
					{
						mirrorCache[item] = (firstHediff, comp);
					}
				}
			}
			numEntitiesSinceLastUpdate = base.map.mapPawns.AllPawnsSpawned.Count;
		}

		public void AddToCache(Pawn pawn, HediffMirrorImage hediff, HediffComp_MirrorImage comp)
		{
			mirrorCache[pawn] = (hediff, comp);
		}
	}
}
namespace MultiRaiders.Helpers
{
	public class GeneratorHelper
	{
		public static List<List<T>> SplitListEvenly<T>(List<T> source, int n)
		{
			List<List<T>> list = new List<List<T>>(n);
			int count = source.Count;
			int num = count / n;
			int num2 = count % n;
			int num3 = 0;
			for (int i = 0; i < n; i++)
			{
				int num4 = num + ((i < num2) ? 1 : 0);
				list.Add(source.GetRange(num3, num4));
				num3 += num4;
			}
			return list;
		}

		public static List<Pawn> SwarmifySpawnedPawns(List<Pawn> unsortedPawns)
		{
			if (unsortedPawns.Count < RaiderSwarmCompressionSettings.Settings.MaxRealRaiders)
			{
				return unsortedPawns;
			}
			MultiRaidersDebug.LogMessage($"SwarmifySpawnedPawns start for {unsortedPawns.Count} pawns");
			Dictionary<int, List<Pawn>> dictionary = new Dictionary<int, List<Pawn>>();
			dictionary.Add(0, unsortedPawns);
			return SwarmifySpawnedPawns(dictionary);
		}

		public static List<Pawn> SwarmifySpawnedPawns<T>(Dictionary<T, List<Pawn>> sortedPawns)
		{
			//IL_0209: Unknown result type (might be due to invalid IL or missing references)
			//IL_0214: Unknown result type (might be due to invalid IL or missing references)
			//IL_0219: Unknown result type (might be due to invalid IL or missing references)
			MultiRaidersDebug.LogMessage($"SwarmifySpawnedPawns start for {sortedPawns.Count} pawn groups");
			List<Pawn> list = new List<Pawn>();
			int num = sortedPawns.Values.Sum((List<Pawn> e) => e.Count);
			if (num < RaiderSwarmCompressionSettings.Settings.MaxRealRaiders && RaiderSwarmCompressionSettings.Settings.ReplaceFractionWithFakes <= 0f)
			{
				return sortedPawns.Values.SelectMany((List<Pawn> _) => _).ToList();
			}
			foreach (KeyValuePair<T, List<Pawn>> sortedPawn in sortedPawns)
			{
				List<Pawn> value = sortedPawn.Value;
				int count = sortedPawn.Value.Count;
				float num2 = (float)count / (float)num;
				int val = Math.Max(1, (int)((float)RaiderSwarmCompressionSettings.Settings.MaxRealRaiders * num2));
				int num3 = Math.Max(1, Math.Min(val, (int)((float)count * (1f - RaiderSwarmCompressionSettings.Settings.ReplaceFractionWithFakes))));
				int count2 = Math.Max(0, count - num3);
				List<Pawn> range = value.GetRange(0, num3);
				List<Pawn> range2 = value.GetRange(num3, count2);
				List<List<Pawn>> list2 = SplitListEvenly(range2, num3);
				for (int i = 0; i < num3; i++)
				{
					Pawn val2 = range[i];
					if (list2[i].Count > 0)
					{
						HediffMirrorImage hediffMirrorImage = (HediffMirrorImage)(object)val2.health.AddHediff(DefDatabase<HediffDef>.GetNamed("MirrorImage", true), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
						HediffComp_MirrorImage hediffComp_MirrorImage = HediffUtility.TryGetComp<HediffComp_MirrorImage>((Hediff)(object)hediffMirrorImage);
						hediffComp_MirrorImage.fakePawns = list2[i];
						hediffMirrorImage.UpdateSeverity();
					}
					list.Add(val2);
				}
			}
			Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("CompressedRaidersTo", NamedArgument.op_Implicit(num), NamedArgument.op_Implicit(list.Count))), MessageTypeDefOf.NeutralEvent, true);
			MultiRaidersDebug.LogMessage("SwarmifySpawnedPawns finished");
			return list;
		}
	}
	public static class MirrorImageHelper
	{
		public static float GetTickOffsetForPawn(Pawn pawn, int idx, bool asleep)
		{
			float num = (float)idx * 1234f + (float)(Gen.HashOffset((Thing)(object)pawn) % 1000);
			float num2 = (asleep ? 0f : ((float)GenTicks.TicksGame * 0.00015f * ((float)idx + 1f)));
			return num + num2;
		}

		public static Vector3 GetSwirlOffset(float time, float scale = 1f)
		{
			//IL_0054: Unknown result type (might be due to invalid IL or missing references)
			//IL_005a: Unknown result type (might be due to invalid IL or missing references)
			//IL_005f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0062: Unknown result type (might be due to invalid IL or missing references)
			float num = Mathf.Sin(time * 0.7f) + 0.5f * Mathf.Sin(time * 1.3f + 1.2f);
			float num2 = Mathf.Cos(time * 1.1f) + 0.5f * Mathf.Cos(time * 0.9f + 2.3f);
			return new Vector3(num, 0f, num2) * scale;
		}

		public static Vector3 GetSwirlDirection(float time, float scale = 1f)
		{
			//IL_0009: Unknown result type (might be due to invalid IL or missing references)
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0013: Unknown result type (might be due to invalid IL or missing references)
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_0019: Unknown result type (might be due to invalid IL or missing references)
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0020: Unknown result type (might be due to invalid IL or missing references)
			//IL_0024: Unknown result type (might be due to invalid IL or missing references)
			//IL_0029: Unknown result type (might be due to invalid IL or missing references)
			//IL_002a: Unknown result type (might be due to invalid IL or missing references)
			//IL_002b: Unknown result type (might be due to invalid IL or missing references)
			//IL_002f: Unknown result type (might be due to invalid IL or missing references)
			float num = 0.01f;
			Vector3 swirlOffset = GetSwirlOffset(time, scale);
			Vector3 swirlOffset2 = GetSwirlOffset(time + num, scale);
			Vector3 val = swirlOffset2 - swirlOffset;
			return ((Vector3)(ref val)).normalized;
		}

		public static Rot4 GetSwirlInfluencedRot4(Rot4 baseRot, Vector3 swirlDir, float influence = 0.5f)
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_005e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0063: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
			//IL_00af: Unknown result type (might be due to invalid IL or missing references)
			//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
			//IL_007f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0084: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ad: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
			float num = Mathf.Atan2(swirlDir.x, swirlDir.z) * 57.29578f;
			if (num < 0f)
			{
				num += 360f;
			}
			float asAngle = ((Rot4)(ref baseRot)).AsAngle;
			float num2 = influence * num + (1f - influence) * asAngle;
			if (num2 >= 315f || num2 < 45f)
			{
				return Rot4.North;
			}
			if (num2 >= 45f && num2 < 135f)
			{
				return Rot4.East;
			}
			if (num2 >= 135f && num2 < 225f)
			{
				return Rot4.South;
			}
			return Rot4.West;
		}

		public static void AddScariaToMirrors(Pawn pawn)
		{
			HediffMirrorImage firstHediff = pawn.health.hediffSet.GetFirstHediff<HediffMirrorImage>();
			if (firstHediff == null)
			{
				return;
			}
			HediffComp_MirrorImage hediffComp_MirrorImage = HediffUtility.TryGetComp<HediffComp_MirrorImage>((Hediff)(object)firstHediff);
			foreach (Pawn fakePawn in hediffComp_MirrorImage.fakePawns)
			{
				fakePawn.health.AddHediff(HediffDefOf.Scaria, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
		}
	}
}
namespace MultiRaiders.Hediff
{
	public class HediffCompProperties_MirrorImage : HediffCompProperties
	{
		public GraphicData graphicData;

		public HediffCompProperties_MirrorImage()
		{
			base.compClass = typeof(HediffComp_MirrorImage);
		}
	}
	public class HediffComp_MirrorImage : HediffComp
	{
		public List<Pawn> fakePawns = new List<Pawn>();

		private HediffCompProperties_MirrorImage Props => base.props as HediffCompProperties_MirrorImage;

		public override bool CompShouldRemove => ((HediffComp)this).CompShouldRemove || ((Thing)((HediffComp)this).Pawn).Faction == Faction.OfPlayer;

		public override string CompLabelInBracketsExtra => "Squad size : " + fakePawns.Count();

		public virtual void DrawAt(Vector3 drawPos)
		{
			//IL_0047: Unknown result type (might be due to invalid IL or missing references)
			//IL_004c: Unknown result type (might be due to invalid IL or missing references)
			//IL_004f: Unknown result type (might be due to invalid IL or missing references)
			//IL_005b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0065: Unknown result type (might be due to invalid IL or missing references)
			//IL_006a: Unknown result type (might be due to invalid IL or missing references)
			//IL_009a: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
			//IL_00c7: Unknown result type (might be due to invalid IL or missing references)
			//IL_00cd: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d4: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d9: Unknown result type (might be due to invalid IL or missing references)
			int num = 0;
			Pawn pawn = ((Hediff)base.parent).pawn;
			bool asleep = !RestUtility.Awake(pawn);
			foreach (Pawn fakePawn in fakePawns)
			{
				float tickOffsetForPawn = MirrorImageHelper.GetTickOffsetForPawn(fakePawn, num, asleep);
				Vector3 swirlOffset = MirrorImageHelper.GetSwirlOffset(tickOffsetForPawn);
				Rot4 swirlInfluencedRot = MirrorImageHelper.GetSwirlInfluencedRot4(((Thing)pawn).Rotation, MirrorImageHelper.GetSwirlDirection(tickOffsetForPawn), 0.15f);
				GraphicData graphicData = Props.graphicData;
				if (((graphicData != null) ? graphicData.Graphic : null) is MirrorImageGraphic mirrorImageGraphic)
				{
					mirrorImageGraphic.SetMaterial(fakePawn, swirlInfluencedRot, asleep);
				}
				GraphicData graphicData2 = Props.graphicData;
				if (graphicData2 != null)
				{
					graphicData2.Graphic.Draw(new Vector3(drawPos.x, Altitudes.AltitudeFor((AltitudeLayer)23), drawPos.z) + swirlOffset, swirlInfluencedRot, (Thing)(object)fakePawn, 0f);
				}
				num++;
			}
		}

		public override void CompExposeData()
		{
			((HediffComp)this).CompExposeData();
			Scribe_Collections.Look<Pawn>(ref fakePawns, "FakePawns", (LookMode)2, Array.Empty<object>());
		}
	}
	public class HediffMirrorImage : HediffWithComps
	{
		public bool wasDowned;

		public bool lordInformed = false;

		public List<Pawn> FakePawns => ((HediffWithComps)this).GetComp<HediffComp_MirrorImage>().fakePawns;

		public void UpdateSeverity()
		{
			((Hediff)this).Severity = Math.Min(1f, (float)FakePawns.Count * 0.25f);
		}

		public override void PostTick()
		{
			if (!lordInformed)
			{
				Lord val = default(Lord);
				if (LordUtility.TryGetLord(((Hediff)this).pawn, ref val))
				{
					Lord obj = val;
					obj.numPawnsEverGained += FakePawns.Count;
				}
				lordInformed = true;
			}
		}

		public void MaybeEjectDeadOrDowned()
		{
			//IL_00df: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
			//IL_0158: Unknown result type (might be due to invalid IL or missing references)
			//IL_0168: Unknown result type (might be due to invalid IL or missing references)
			//IL_0077: Unknown result type (might be due to invalid IL or missing references)
			//IL_0082: Unknown result type (might be due to invalid IL or missing references)
			//IL_0098: Expected O, but got Unknown
			foreach (Pawn item in new List<Pawn>(FakePawns))
			{
				if (item.Dead)
				{
					MultiRaidersDebug.LogMessage("Ejecting dead fake pawn " + ((object)item)?.ToString() + " for " + (object)((Hediff)this).pawn);
					FakePawns.Remove(item);
					try
					{
						GenSpawn.Spawn((Thing)(Corpse)((Thing)item).ParentHolder, ((Thing)((Hediff)this).pawn).Position, ((Thing)((Hediff)this).pawn).Map, (WipeMode)0);
					}
					catch (Exception ex)
					{
						MultiRaidersDebug.LogMessage("Error spawning corpse for fake pawn " + ((object)item)?.ToString() + ": " + ex);
						MultiRaidersDebug.LogMessage("Defaulting to normal spawn");
						GenSpawn.Spawn((Thing)(object)item, ((Thing)((Hediff)this).pawn).Position, ((Thing)((Hediff)this).pawn).Map, Rot4.South, (WipeMode)0, false, false);
					}
				}
				else if (item.Downed)
				{
					MultiRaidersDebug.LogMessage("Ejecting downed fake pawn " + ((object)item)?.ToString() + " for " + (object)((Hediff)this).pawn);
					FakePawns.Remove(item);
					GenSpawn.Spawn((Thing)(object)item, ((Thing)((Hediff)this).pawn).Position, ((Thing)((Hediff)this).pawn).Map, Rot4.South, (WipeMode)0, false, false);
				}
			}
			UpdateSeverity();
		}

		public void SpawnNextInLine()
		{
			//IL_007a: Unknown result type (might be due to invalid IL or missing references)
			//IL_007f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0081: Unknown result type (might be due to invalid IL or missing references)
			//IL_008d: Unknown result type (might be due to invalid IL or missing references)
			//IL_00f3: Unknown result type (might be due to invalid IL or missing references)
			//IL_00fd: Expected O, but got Unknown
			if (FakePawns.Count == 0)
			{
				return;
			}
			Pawn val = GenCollection.Pop<Pawn>(FakePawns);
			HediffMirrorImage hediffMirrorImage = (HediffMirrorImage)(object)val.health.AddHediff(DefDatabase<HediffDef>.GetNamed("MirrorImage", true), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			HediffComp_MirrorImage hediffComp_MirrorImage = HediffUtility.TryGetComp<HediffComp_MirrorImage>((Hediff)(object)hediffMirrorImage);
			hediffComp_MirrorImage.fakePawns = FakePawns.ToList();
			hediffMirrorImage.UpdateSeverity();
			hediffMirrorImage.lordInformed = true;
			IntVec3 position = ((Thing)((Hediff)this).pawn).Position;
			GenSpawn.Spawn((Thing)(object)val, position, ((Thing)((Hediff)this).pawn).Map, Rot4.South, (WipeMode)0, false, false);
			Lord val2 = default(Lord);
			if (LordUtility.TryGetLord(((Hediff)this).pawn, ref val2))
			{
				if (((Hediff)this).pawn.mindState.duty != null)
				{
					val.mindState.duty = ((Hediff)this).pawn.mindState.duty;
				}
				else
				{
					val.mindState.duty = new PawnDuty(DutyDefOf.AssaultColony);
				}
				val2.AddPawns((IEnumerable<Pawn>)new <>z__ReadOnlySingleElementList<Pawn>(val), false);
			}
			((Thing)((Hediff)this).pawn).Map.GetComponent<MultiRaidersMapComponent>().AddToCache(val, hediffMirrorImage, hediffComp_MirrorImage);
			FakePawns.Clear();
			UpdateSeverity();
		}
	}
}
namespace MultiRaiders.Graphics
{
	public class MirrorImageGraphic : Graphic_Multi
	{
		public static Lazy<FieldInfo> matsInfo = new Lazy<FieldInfo>(() => AccessTools.Field(typeof(MirrorImageGraphic), "mats"));

		public Material[] _mats;

		protected Shader _shader;

		protected int _renderQueue;

		protected List<ShaderParameter> _shaderParameters;

		protected Pawn _pawn;

		public override bool ShouldDrawRotated => false;

		public override void Init(GraphicRequest req)
		{
			//IL_0002: Unknown result type (might be due to invalid IL or missing references)
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_001a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0026: Unknown result type (might be due to invalid IL or missing references)
			//IL_0027: Unknown result type (might be due to invalid IL or missing references)
			//IL_002c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0032: Unknown result type (might be due to invalid IL or missing references)
			//IL_0033: Unknown result type (might be due to invalid IL or missing references)
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			//IL_003e: Unknown result type (might be due to invalid IL or missing references)
			//IL_003f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0044: Unknown result type (might be due to invalid IL or missing references)
			//IL_004a: Unknown result type (might be due to invalid IL or missing references)
			//IL_0056: Unknown result type (might be due to invalid IL or missing references)
			//IL_0062: Unknown result type (might be due to invalid IL or missing references)
			((Graphic)this).data = req.graphicData;
			((Graphic)this).path = req.path;
			((Graphic)this).maskPath = req.maskPath;
			((Graphic)this).color = req.color;
			((Graphic)this).colorTwo = req.colorTwo;
			((Graphic)this).drawSize = req.drawSize;
			_shader = req.shader;
			_renderQueue = req.renderQueue;
			_shaderParameters = req.shaderParameters;
			_mats = matsInfo.Value.GetValue(this) as Material[];
		}

		public void SetMaterial(Pawn pawn, Rot4 rot, bool asleep)
		{
			//IL_0003: Unknown result type (might be due to invalid IL or missing references)
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			//IL_001b: Unknown result type (might be due to invalid IL or missing references)
			//IL_002c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0032: Unknown result type (might be due to invalid IL or missing references)
			//IL_0063: Unknown result type (might be due to invalid IL or missing references)
			//IL_0068: Unknown result type (might be due to invalid IL or missing references)
			//IL_0070: Unknown result type (might be due to invalid IL or missing references)
			//IL_0075: Unknown result type (might be due to invalid IL or missing references)
			//IL_0094: Unknown result type (might be due to invalid IL or missing references)
			//IL_0095: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
			MaterialRequest val = default(MaterialRequest);
			Vector2 val2 = new Vector2(600f, 600f);
			Rot4 val3 = rot;
			PawnHealthState? val4 = (PawnHealthState)(asleep ? 1 : 2);
			val.mainTex = (Texture)(object)PortraitsCache.Get(pawn, val2, val3, default(Vector3), 0.5f, false, false, true, true, (IReadOnlyDictionary<Apparel, Color>)null, (Color?)null, false, val4);
			val.shader = _shader;
			val.color = ((Graphic)this).color;
			val.colorTwo = ((Graphic)this).colorTwo;
			val.renderQueue = _renderQueue;
			val.shaderParameters = _shaderParameters;
			MaterialRequest val5 = val;
			_mats[((Rot4)(ref rot)).AsInt] = MaterialPool.MatFrom(val5);
			_pawn = pawn;
		}
	}
}
namespace MultiRaiders.Debug
{
	public static class MultiRaidersDebug
	{
		public static void LogMessage(string msg)
		{
			if (RaiderSwarmCompressionSettings.Settings.Debug)
			{
				Log.Message("[MultiRaiders] " + msg);
			}
		}
	}
}
[CompilerGenerated]
internal sealed class <>z__ReadOnlySingleElementList<T> : IEnumerable, ICollection, IList, IEnumerable<T>, IReadOnlyCollection<T>, IReadOnlyList<T>, ICollection<T>, IList<T>
{
	private sealed class Enumerator : IDisposable, IEnumerator, IEnumerator<T>
	{
		object IEnumerator.Current => _item;

		T IEnumerator<T>.Current => _item;

		public Enumerator(T item)
		{
			_item = item;
		}

		bool IEnumerator.MoveNext()
		{
			return !_moveNextCalled && (_moveNextCalled = true);
		}

		void IEnumerator.Reset()
		{
			_moveNextCalled = false;
		}

		void IDisposable.Dispose()
		{
		}
	}

	int ICollection.Count => 1;

	bool ICollection.IsSynchronized => false;

	object ICollection.SyncRoot => this;

	object IList.this[int index]
	{
		get
		{
			if (index != 0)
			{
				throw new IndexOutOfRangeException();
			}
			return _item;
		}
		set
		{
			throw new NotSupportedException();
		}
	}

	bool IList.IsFixedSize => true;

	bool IList.IsReadOnly => true;

	int IReadOnlyCollection<T>.Count => 1;

	T IReadOnlyList<T>.this[int index]
	{
		get
		{
			if (index != 0)
			{
				throw new IndexOutOfRangeException();
			}
			return _item;
		}
	}

	int ICollection<T>.Count => 1;

	bool ICollection<T>.IsReadOnly => true;

	T IList<T>.this[int index]
	{
		get
		{
			if (index != 0)
			{
				throw new IndexOutOfRangeException();
			}
			return _item;
		}
		set
		{
			throw new NotSupportedException();
		}
	}

	public <>z__ReadOnlySingleElementList(T item)
	{
		_item = item;
	}

	IEnumerator IEnumerable.GetEnumerator()
	{
		return new Enumerator(_item);
	}

	void ICollection.CopyTo(Array array, int index)
	{
		array.SetValue(_item, index);
	}

	int IList.Add(object value)
	{
		throw new NotSupportedException();
	}

	void IList.Clear()
	{
		throw new NotSupportedException();
	}

	bool IList.Contains(object value)
	{
		return EqualityComparer<T>.Default.Equals(_item, (T)value);
	}

	int IList.IndexOf(object value)
	{
		return (!EqualityComparer<T>.Default.Equals(_item, (T)value)) ? (-1) : 0;
	}

	void IList.Insert(int index, object value)
	{
		throw new NotSupportedException();
	}

	void IList.Remove(object value)
	{
		throw new NotSupportedException();
	}

	void IList.RemoveAt(int index)
	{
		throw new NotSupportedException();
	}

	IEnumerator<T> IEnumerable<T>.GetEnumerator()
	{
		return new Enumerator(_item);
	}

	void ICollection<T>.Add(T item)
	{
		throw new NotSupportedException();
	}

	void ICollection<T>.Clear()
	{
		throw new NotSupportedException();
	}

	bool ICollection<T>.Contains(T item)
	{
		return EqualityComparer<T>.Default.Equals(_item, item);
	}

	void ICollection<T>.CopyTo(T[] array, int arrayIndex)
	{
		array[arrayIndex] = _item;
	}

	bool ICollection<T>.Remove(T item)
	{
		throw new NotSupportedException();
	}

	int IList<T>.IndexOf(T item)
	{
		return (!EqualityComparer<T>.Default.Equals(_item, item)) ? (-1) : 0;
	}

	void IList<T>.Insert(int index, T item)
	{
		throw new NotSupportedException();
	}

	void IList<T>.RemoveAt(int index)
	{
		throw new NotSupportedException();
	}
}
You are not using the latest version of the tool, please update.
Latest version is '11.0.0.9375' (yours is '9.0.0.7889')
