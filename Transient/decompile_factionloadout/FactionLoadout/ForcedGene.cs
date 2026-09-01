using System;
using FactionLoadout.Util;
using Verse;

namespace FactionLoadout;

public class ForcedGene : IExposable, IDeepCopyable<ForcedGene>
{
	private Lazy<GeneDef> resolvedGeneDef;

	public string geneDef;

	public float chance = 1f;

	public bool xenogene;

	public bool forceActive;

	public GeneDef GeneDef
	{
		get
		{
			if (resolvedGeneDef == null)
			{
				resolvedGeneDef = new Lazy<GeneDef>(() => DefDatabase<GeneDef>.GetNamedSilentFail(geneDef));
			}
			return resolvedGeneDef.Value;
		}
		set
		{
			geneDef = ((Def)value).defName;
			resolvedGeneDef = new Lazy<GeneDef>(() => value);
		}
	}

	public ForcedGene DeepClone()
	{
		return new ForcedGene
		{
			geneDef = geneDef,
			chance = chance,
			xenogene = xenogene,
			forceActive = forceActive
		};
	}

	public void ExposeData()
	{
		Scribe_Values.Look<string>(ref geneDef, "geneDef", (string)null, false);
		Scribe_Values.Look<float>(ref chance, "chance", 1f, false);
		Scribe_Values.Look<bool>(ref xenogene, "xenogene", false, false);
		Scribe_Values.Look<bool>(ref forceActive, "forceActive", false, false);
	}
}
