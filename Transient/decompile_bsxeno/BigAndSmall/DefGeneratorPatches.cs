using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class DefGeneratorPatches
{
	[CompilerGenerated]
	private sealed class _003CGenerateCorpseDef_Transpiler_003Ed__1 : IEnumerable<CodeInstruction>, IEnumerable, IEnumerator<CodeInstruction>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private CodeInstruction _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		private IEnumerable<CodeInstruction> instructions;

		public IEnumerable<CodeInstruction> _003C_003E3__instructions;

		private List<CodeInstruction> _003Ccodes_003E5__2;

		private MethodInfo _003CtargetMethod_003E5__3;

		private int _003Ci_003E5__4;

		private CodeInstruction _003Ccode_003E5__5;

		CodeInstruction IEnumerator<CodeInstruction>.Current
		{
			[DebuggerHidden]
			get
			{
				return _003C_003E2__current;
			}
		}

		object IEnumerator.Current
		{
			[DebuggerHidden]
			get
			{
				return _003C_003E2__current;
			}
		}

		[DebuggerHidden]
		public _003CGenerateCorpseDef_Transpiler_003Ed__1(int _003C_003E1__state)
		{
			this._003C_003E1__state = _003C_003E1__state;
			_003C_003El__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			_003Ccodes_003E5__2 = null;
			_003CtargetMethod_003E5__3 = null;
			_003Ccode_003E5__5 = null;
			_003C_003E1__state = -2;
		}

		private bool MoveNext()
		{
			//IL_0107: Unknown result type (might be due to invalid IL or missing references)
			//IL_0111: Expected O, but got Unknown
			//IL_00e1: Unknown result type (might be due to invalid IL or missing references)
			//IL_00eb: Expected O, but got Unknown
			switch (_003C_003E1__state)
			{
			default:
				return false;
			case 0:
				_003C_003E1__state = -1;
				_003Ccodes_003E5__2 = new List<CodeInstruction>(instructions);
				_003CtargetMethod_003E5__3 = AccessTools.Method(typeof(DefGeneratorPatches), "TrySetToRobotCorpse", (Type[])null, (Type[])null);
				_003Ci_003E5__4 = 0;
				break;
			case 1:
				_003C_003E1__state = -1;
				if (_003Ccode_003E5__5.opcode == OpCodes.Ldsfld && _003Ccodes_003E5__2[_003Ci_003E5__4].operand is FieldInfo { Name: "CorpsesHumanlike" })
				{
					_003C_003E2__current = new CodeInstruction(OpCodes.Ldarg_0, (object)null);
					_003C_003E1__state = 2;
					return true;
				}
				goto IL_0121;
			case 2:
				_003C_003E1__state = -1;
				_003C_003E2__current = new CodeInstruction(OpCodes.Call, (object)_003CtargetMethod_003E5__3);
				_003C_003E1__state = 3;
				return true;
			case 3:
				{
					_003C_003E1__state = -1;
					goto IL_0121;
				}
				IL_0121:
				_003Ccode_003E5__5 = null;
				_003Ci_003E5__4++;
				break;
			}
			if (_003Ci_003E5__4 < _003Ccodes_003E5__2.Count)
			{
				_003Ccode_003E5__5 = _003Ccodes_003E5__2[_003Ci_003E5__4];
				_003C_003E2__current = _003Ccode_003E5__5;
				_003C_003E1__state = 1;
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
			_003CGenerateCorpseDef_Transpiler_003Ed__1 _003CGenerateCorpseDef_Transpiler_003Ed__;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				_003CGenerateCorpseDef_Transpiler_003Ed__ = this;
			}
			else
			{
				_003CGenerateCorpseDef_Transpiler_003Ed__ = new _003CGenerateCorpseDef_Transpiler_003Ed__1(0);
			}
			_003CGenerateCorpseDef_Transpiler_003Ed__.instructions = _003C_003E3__instructions;
			return _003CGenerateCorpseDef_Transpiler_003Ed__;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<CodeInstruction>)this).GetEnumerator();
		}
	}

	public static FieldInfo iconColor;

	public static ThingCategoryDef TrySetToRobotCorpse(ThingCategoryDef previousDef, ThingDef pawnDef)
	{
		if (pawnDef.IsMechanicalDef())
		{
			return BSEDefs.BS_RobotCorpses;
		}
		return previousDef;
	}

	[IteratorStateMachine(typeof(_003CGenerateCorpseDef_Transpiler_003Ed__1))]
	[HarmonyPatch(typeof(ThingDefGenerator_Corpses), "GenerateCorpseDef")]
	[HarmonyTranspiler]
	public static IEnumerable<CodeInstruction> GenerateCorpseDef_Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CGenerateCorpseDef_Transpiler_003Ed__1(-2)
		{
			_003C_003E3__instructions = instructions
		};
	}

	[HarmonyPatch(typeof(GeneDefGenerator), "ImpliedGeneDefs")]
	[HarmonyPriority(100)]
	[HarmonyPostfix]
	public static void ImpliedGeneDefs_Postfix(ref IEnumerable<GeneDef> __result)
	{
		List<GeneDef> list = __result.ToList();
		if (!BigSmall.BSTransformGenes || !BigSmallMod.settings.generateDefs)
		{
			return;
		}
		foreach (GeneDef item in GenerateXenotypeGenes())
		{
			list.Add(item);
		}
		__result = list;
	}

	public static List<GeneDef> GenerateXenotypeGenes()
	{
		List<GeneDef> list = new List<GeneDef>();
		List<XenotypeDef> allDefsListForReading = DefDatabase<XenotypeDef>.AllDefsListForReading;
		GeneTemplate named = DefDatabase<GeneTemplate>.GetNamed("BS_MetamorphTemplate", true);
		GeneTemplate named2 = DefDatabase<GeneTemplate>.GetNamed("BS_RetromorphDownTemplate", true);
		if (named == null)
		{
			Log.Warning("Big and Small DefGen: GenerateXenotypeGenes: Could not find the Metamorphosis Template. Metamorphosis genes will not be generated.\nIf using Big and Small Genes this likely means you need to resubscribe to the mod, or that you have a config that removes the required def.");
		}
		if (named2 == null)
		{
			Log.Warning("Big and Small DefGen: GenerateXenotypeGenes: Could not find the Metamorphosis Down Template. Retromorphosis genes will not be generated.\nIf using Big and Small Genes this likely means you need to resubscribe to the mod, or that you have a config that removes the required def.");
		}
		try
		{
			foreach (XenotypeDef item in allDefsListForReading)
			{
				if (named != null)
				{
					PawnExtension extension = new PawnExtension
					{
						morphTargets = new List<MorphTarget>(1)
						{
							new MorphTarget
							{
								xenotype = item
							}
						},
						hideInGenePicker = false
					};
					list.Add(GenerateXenoTypeGene(item, named, (DefModExtension)(object)extension, new List<string>(1) { ((Def)item).label }));
				}
				if (named2 != null)
				{
					PawnExtension extension2 = new PawnExtension
					{
						morphTargets = new List<MorphTarget>(1)
						{
							new MorphTarget
							{
								xenotype = item,
								isRetromorph = true
							}
						},
						hideInGenePicker = false
					};
					list.Add(GenerateXenoTypeGene(item, named2, (DefModExtension)(object)extension2, new List<string>(1) { ((Def)item).label }));
				}
			}
		}
		catch (Exception ex)
		{
			Log.Error("Exception duing Big and Small DefGen: GenerateXenotypeGenes.\nGenerating the genes has been aborted.\n" + ex.Message + "\n" + ex.StackTrace);
		}
		return list;
	}

	public static GeneDef GenerateXenoTypeGene(XenotypeDef xenoDef, GeneTemplate template, DefModExtension extension, List<string> descriptionKeys)
	{
		//IL_0054: Unknown result type (might be due to invalid IL or missing references)
		//IL_0059: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_007c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_0094: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ba: Unknown result type (might be due to invalid IL or missing references)
		//IL_00c6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Expected O, but got Unknown
		//IL_0185: Unknown result type (might be due to invalid IL or missing references)
		if (xenoDef == null || template == null || extension == null || descriptionKeys == null)
		{
			Log.Error("Big and Small DefGen: GenerateXenoTypeGene: One of the parameters was null." + $"\nXenoDef: {xenoDef}, template: {template}, extension: {extension}, descriptionKeys: {descriptionKeys}");
			return null;
		}
		string defName = ((Def)xenoDef).defName + "_" + template.keyTag;
		GeneDef val = new GeneDef
		{
			defName = defName,
			label = ((Def)xenoDef).label + " " + ((Def)template).label,
			description = ((Def)template).description,
			customEffectDescriptions = template.customEffectDescriptions,
			iconPath = xenoDef.iconPath,
			biostatCpx = 0,
			biostatMet = 0,
			displayCategory = template.displayCategory,
			canGenerateInGeneSet = template.canGenerateInGeneSet,
			selectionWeight = template.selectionWeight,
			modExtensions = new List<DefModExtension>(1) { extension }
		};
		for (int i = 0; i < descriptionKeys.Count; i++)
		{
			((Def)val).description = ((Def)val).description.Replace("{" + i + "}", descriptionKeys[i]);
		}
		if (iconColor == null)
		{
			iconColor = AccessTools.Field(typeof(GeneDef), "iconColor");
		}
		if (template.iconColor.HasValue)
		{
			iconColor.SetValue(val, template.iconColor);
		}
		else
		{
			iconColor.SetValue(val, (object)new Color(0.75f, 0.75f, 0.75f));
		}
		return val;
	}
}
