using System;
using System.Collections.Generic;
using System.Linq;
using System.Xml;
using FactionLoadout.Util;
using Verse;

namespace FactionLoadout;

public class ForcedHediff : IExposable, IDeepCopyable<ForcedHediff>
{
	private Lazy<HediffDef> resolvedHediffDef;

	public string hediffDef;

	public List<DefRef<BodyPartDef>> parts;

	public int maxParts = 1;

	public IntRange maxPartsRange = IntRange.One;

	public float chance = 1f;

	public HediffDef HediffDef
	{
		get
		{
			if (resolvedHediffDef == null)
			{
				resolvedHediffDef = new Lazy<HediffDef>(() => DefDatabase<HediffDef>.GetNamedSilentFail(hediffDef));
			}
			return resolvedHediffDef.Value;
		}
		set
		{
			hediffDef = ((Def)value).defName;
			resolvedHediffDef = new Lazy<HediffDef>(() => value);
		}
	}

	public int PartsToHit()
	{
		if (maxPartsRange.max <= 1)
		{
			return maxParts;
		}
		return ((IntRange)(ref maxPartsRange)).RandomInRange;
	}

	public ForcedHediff DeepClone()
	{
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		return new ForcedHediff
		{
			hediffDef = hediffDef,
			parts = parts?.Select((DefRef<BodyPartDef> p) => p?.DeepClone()).ToList(),
			maxParts = maxParts,
			maxPartsRange = maxPartsRange,
			chance = chance
		};
	}

	public void ExposeData()
	{
		//IL_0012: Unknown result type (might be due to invalid IL or missing references)
		//IL_0018: Invalid comparison between Unknown and I4
		//IL_00f7: Unknown result type (might be due to invalid IL or missing references)
		Scribe_Values.Look<string>(ref hediffDef, "hediffDef", (string)null, false);
		if ((int)Scribe.mode == 2)
		{
			XmlElement xmlElement = Scribe.loader.curXmlParent?["parts"];
			if (xmlElement != null && xmlElement.HasChildNodes && xmlElement.SelectSingleNode("li/defName") == null)
			{
				List<BodyPartDef> list = null;
				Scribe_Collections.Look<BodyPartDef>(ref list, "parts", (LookMode)4, Array.Empty<object>());
				parts = (from d in list?.Where((BodyPartDef d) => d != null)
					select new DefRef<BodyPartDef>(d)).ToList();
				goto IL_00da;
			}
		}
		Scribe_Collections.Look<DefRef<BodyPartDef>>(ref parts, "parts", (LookMode)2, Array.Empty<object>());
		goto IL_00da;
		IL_00da:
		Scribe_Values.Look<int>(ref maxParts, "maxParts", 1, false);
		Scribe_Values.Look<IntRange>(ref maxPartsRange, "maxPartsRange", IntRange.One, false);
		Scribe_Values.Look<float>(ref chance, "chance", 1f, false);
	}
}
