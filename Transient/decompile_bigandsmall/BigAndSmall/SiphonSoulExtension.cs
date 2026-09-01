using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;

namespace BigAndSmall;

public static class SiphonSoulExtension
{
	[SpecialName]
	public sealed class _003CG_003E_00249549C7675D6837AAFE22E8DBED4E6DA8
	{
		[SpecialName]
		public static class _003CM_003E_00242EA270C49F7EE134990DBC59DCE342AA
		{
		}

		[ExtensionMarker("<M>$2EA270C49F7EE134990DBC59DCE342AA")]
		public SiphonSoul FuseAll(SiphonType type)
		{
			throw new NotSupportedException();
		}
	}

	public static SiphonSoul FuseAll(this IEnumerable<SiphonSoul> siphons, SiphonType type)
	{
		siphons = siphons.Where((SiphonSoul x) => x.type == type);
		if (!siphons.Any())
		{
			return null;
		}
		SiphonSoul siphonSoul = siphons.First()._003CClone_003E_0024();
		bool flag = true;
		foreach (SiphonSoul siphon in siphons)
		{
			if (flag)
			{
				flag = false;
			}
			else
			{
				siphonSoul = siphonSoul.FuseWith(siphon);
			}
		}
		return siphonSoul;
	}
}
