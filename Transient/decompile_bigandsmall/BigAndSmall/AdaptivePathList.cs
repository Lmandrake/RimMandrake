using System;
using System.Collections.Generic;
using System.Linq;
using System.Xml;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class AdaptivePathList : List<AdaptivePawnPath>
{
	public bool ValidFor(BSCache cache, Gender? forceGender)
	{
		return GetPaths(cache, forceGender) != null;
	}

	public bool TryGetPath(BSCache cache, ref string path)
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		int pawnRNGSeed = cache.pawn.GetPawnRNGSeed();
		Gender? forceGender = cache.GetApparentGender();
		List<string> paths = GetPaths(cache, forceGender);
		if (!GenList.NullOrEmpty<string>((IList<string>)paths))
		{
			RandBlock val = default(RandBlock);
			((RandBlock)(ref val))._002Ector(pawnRNGSeed);
			try
			{
				path = ((paths != null) ? GenCollection.RandomElement<string>((IEnumerable<string>)paths) : null);
				return true;
			}
			finally
			{
				((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
			}
		}
		return false;
	}

	public List<string> GetPaths(BSCache cache, Gender? forceGender = null)
	{
		//IL_0035: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_009e: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		if (base.Count == 0)
		{
			return null;
		}
		Pawn pawn = cache.pawn;
		Gender targetGender = ((!forceGender.HasValue) ? pawn.gender : forceGender.Value);
		if (forceGender.HasValue)
		{
			BodyTypeDef bodyType = pawn.story.bodyType;
			if (forceGender == (Gender?)2 && bodyType == BodyTypeDefOf.Male)
			{
				pawn.story.bodyType = BodyTypeDefOf.Female;
			}
			else if (forceGender == (Gender?)1 && bodyType == BodyTypeDefOf.Female)
			{
				pawn.story.bodyType = BodyTypeDefOf.Male;
			}
		}
		IEnumerable<AdaptivePawnPath> source = this.Where((AdaptivePawnPath x) => (x.GetBodyType() == null || x.GetBodyType() == pawn.story?.bodyType) && (!x.GetGender().HasValue || x.GetGender() == (Gender?)targetGender));
		if (!source.Any())
		{
			return null;
		}
		int bestPriority = source.Select((AdaptivePawnPath x) => x.GetPriority()).DefaultIfEmpty(-99).Max();
		List<string> list = (from x in source
			where x.GetPriority() == bestPriority
			select x.texturePath).ToList();
		if (!GenCollection.Any<string>(list))
		{
			return null;
		}
		return list;
	}

	public void LoadDataFromXmlCustom(XmlNode xmlRoot)
	{
		foreach (XmlNode childNode in xmlRoot.ChildNodes)
		{
			AdaptivePawnPath adaptivePawnPath = new AdaptivePawnPath();
			adaptivePawnPath.LoadDataFromXmlCustom(childNode);
			Add(adaptivePawnPath);
		}
	}
}
