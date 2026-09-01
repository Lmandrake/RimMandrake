using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using Verse;

namespace VEF;

public static class GenRadialPatches
{
	private const int Range = 200;

	public static void IncreaseRadialPatternRadiiSize()
	{
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f7: Unknown result type (might be due to invalid IL or missing references)
		if (GenRadial.RadialPattern.Length >= 160000)
		{
			return;
		}
		List<(IntVec3, int)> list = new List<(IntVec3, int)>();
		IntVec3 item = default(IntVec3);
		for (int i = -200; i <= 200; i++)
		{
			for (int j = -200; j <= 200; j++)
			{
				((IntVec3)(ref item))._002Ector(i, 0, j);
				list.Add((item, ((IntVec3)(ref item)).LengthHorizontalSquared));
			}
		}
		IntVec3 val = new IntVec3(200, 0, 0);
		int maxLength = ((IntVec3)(ref val)).LengthHorizontalSquared;
		list.RemoveAll(((IntVec3 pos, int length) x) => x.length > maxLength);
		list.Sort(delegate((IntVec3 pos, int length) a, (IntVec3 pos, int length) b)
		{
			int item2 = a.length;
			int item3 = b.length;
			return (item2 < item3) ? (-1) : ((item2 != item3) ? 1 : 0);
		});
		IntVec3[] array = (IntVec3[])(object)new IntVec3[list.Count];
		float[] array2 = new float[list.Count];
		int[] array3 = new int[40001];
		for (int k = 0; k < list.Count; k++)
		{
			array[k] = list[k].Item1;
			int num = k;
			(IntVec3, int) tuple = list[k];
			array2[num] = ((IntVec3)(ref tuple.Item1)).LengthHorizontal;
		}
		for (int l = 0; l < array3.Length; l++)
		{
			array3[l] = -1;
		}
		for (int m = 0; m < array.Length; m++)
		{
			int lengthHorizontalSquared = ((IntVec3)(ref array[m])).LengthHorizontalSquared;
			if (array3[lengthHorizontalSquared] == -1)
			{
				array3[lengthHorizontalSquared] = m;
			}
		}
		int num2 = 0;
		for (int n = 0; n < array3.Length; n++)
		{
			if (array3[n] != -1)
			{
				num2 = array3[n];
			}
			else
			{
				array3[n] = num2;
			}
		}
		AccessToolsExtensions.Field(typeof(GenRadial), "RadialPattern").SetValue(null, array);
		AccessToolsExtensions.Field(typeof(GenRadial), "RadialPatternRadii").SetValue(null, array2);
		AccessToolsExtensions.Field(typeof(GenRadial), "LengthSquaredToIndexArray").SetValue(null, array3);
		LongEventHandler.ExecuteWhenFinished((Action)delegate
		{
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			//IL_0043: Expected O, but got Unknown
			VEF_Mod.harmonyInstance.Patch((MethodBase)AccessToolsExtensions.DeclaredMethod(typeof(GenRadial), "NumCellsInRadius", (Type[])null, (Type[])null), (HarmonyMethod)null, (HarmonyMethod)null, new HarmonyMethod((Delegate)new Func<IEnumerable<CodeInstruction>, IEnumerable<CodeInstruction>>(IncreaseNumCellsInRadiusCount)), (HarmonyMethod)null);
		});
	}

	private static IEnumerable<CodeInstruction> IncreaseNumCellsInRadiusCount(IEnumerable<CodeInstruction> instr)
	{
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004e: Expected O, but got Unknown
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Expected O, but got Unknown
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Expected O, but got Unknown
		//IL_00b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b7: Expected O, but got Unknown
		//IL_00c5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00cb: Expected O, but got Unknown
		int num = ((float[])AccessToolsExtensions.Field(typeof(GenRadial), "RadialPatternRadii").GetValue(null)).Length;
		int num2 = ((int[])AccessToolsExtensions.Field(typeof(GenRadial), "LengthSquaredToIndexArray").GetValue(null)).Length - 1;
		CodeMatcher val = new CodeMatcher(instr, (ILGenerator)null);
		val.MatchStartForward((CodeMatch[])(object)new CodeMatch[2]
		{
			new CodeMatch((OpCode?)OpCodes.Ldc_I4, (object)null, (string)null),
			new CodeMatch((OpCode?)OpCodes.Ret, (object)null, (string)null)
		});
		long num3 = Convert.ToInt64(val.Instruction.operand);
		val.Reset(true);
		val.MatchStartForward((CodeMatch[])(object)new CodeMatch[2]
		{
			new CodeMatch((OpCode?)OpCodes.Ldc_I4, (object)null, (string)null),
			new CodeMatch((OpCode?)OpCodes.Stloc_2, (object)null, (string)null)
		});
		long num4 = Convert.ToInt64(val.Instruction.operand);
		if (num3 < num)
		{
			val.Reset(true);
			for (int i = 0; i < 25; i++)
			{
				val.MatchStartForward((CodeMatch[])(object)new CodeMatch[1] { CodeMatch.LoadsConstant(num3) });
				if (val.IsInvalid)
				{
					break;
				}
				val.Operand = num;
			}
		}
		if (num4 < num2)
		{
			val.Reset(true);
			for (int j = 0; j < 25; j++)
			{
				val.MatchStartForward((CodeMatch[])(object)new CodeMatch[1] { CodeMatch.LoadsConstant(num4) });
				if (val.IsInvalid)
				{
					break;
				}
				val.Operand = num2;
			}
		}
		return val.Instructions();
	}
}
