using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using VEF.Things;
using Verse;

namespace VEF.Cooking;

[Obsolete("VEF.Cooking.Recipe_Extension is obsolete, use VEF.Things.RecipeExtension instead")]
public class Recipe_Extension : RecipeExtension
{
	private const string ObsoleteError = "VEF.Cooking.Recipe_Extension is obsolete, use VEF.Things.RecipeExtension instead";

	public override IEnumerable<string> ConfigErrors()
	{
		foreach (string item in _003C_003En__0())
		{
			yield return item;
		}
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<string> _003C_003En__0()
	{
		return ((DefModExtension)this).ConfigErrors();
	}
}
