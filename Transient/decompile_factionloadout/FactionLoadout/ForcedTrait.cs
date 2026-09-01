using System;
using FactionLoadout.Util;
using RimWorld;
using Verse;

namespace FactionLoadout;

public class ForcedTrait : IExposable, IDeepCopyable<ForcedTrait>
{
	private Lazy<TraitDef> resolvedTraitDef;

	public string traitDef;

	public int degree;

	public float chance = 1f;

	public TraitDef TraitDef
	{
		get
		{
			if (resolvedTraitDef == null)
			{
				resolvedTraitDef = new Lazy<TraitDef>(() => DefDatabase<TraitDef>.GetNamedSilentFail(traitDef));
			}
			return resolvedTraitDef.Value;
		}
		set
		{
			traitDef = ((Def)value).defName;
			resolvedTraitDef = new Lazy<TraitDef>(() => value);
		}
	}

	public ForcedTrait DeepClone()
	{
		return new ForcedTrait
		{
			traitDef = traitDef,
			degree = degree,
			chance = chance
		};
	}

	public void ExposeData()
	{
		Scribe_Values.Look<string>(ref traitDef, "traitDef", (string)null, false);
		Scribe_Values.Look<int>(ref degree, "degree", 0, false);
		Scribe_Values.Look<float>(ref chance, "chance", 1f, false);
	}
}
