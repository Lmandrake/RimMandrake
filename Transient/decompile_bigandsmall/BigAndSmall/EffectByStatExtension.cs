using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class EffectByStatExtension
{
	[SpecialName]
	public sealed class _003CG_003E_002496A1764D10F415D68D40791938EE4131
	{
		[SpecialName]
		public static class _003CM_003E_0024C269A50FBB6423BBA5A3C99A274B99CF
		{
		}

		[ExtensionMarker("<M>$C269A50FBB6423BBA5A3C99A274B99CF")]
		public float ApplyScaling(float offset, string tag, Pawn pawn)
		{
			throw new NotSupportedException();
		}
	}

	public static float ApplyScaling(this IEnumerable<StatScaling> scalings, float offset, string tag, Pawn pawn)
	{
		float num = 1f;
		foreach (StatScaling item in scalings.Where((StatScaling x) => x.isOffset && x.tag == tag))
		{
			offset += item.curve.Evaluate(StatExtension.GetStatValue((Thing)(object)pawn, item.stat, true, 100));
		}
		foreach (StatScaling item2 in scalings.Where((StatScaling x) => !x.isOffset && x.tag == tag))
		{
			num += item2.curve.Evaluate(StatExtension.GetStatValue((Thing)(object)pawn, item2.stat, true, 100));
		}
		return offset * num;
	}
}
