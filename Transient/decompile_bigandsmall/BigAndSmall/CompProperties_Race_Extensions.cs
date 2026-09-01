using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace BigAndSmall;

public static class CompProperties_Race_Extensions
{
	public static void EnsureValidBodyType(this List<CompProperties_Race> comps, BSCache cache)
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = cache.pawn;
		Gender gender = cache.GetApparentGender();
		List<BodyTypeDef> list = comps.SelectMany((CompProperties_Race x) => x.BodyTypeDefs(gender)).ToList();
		if (GenCollection.Any<BodyTypeDef>(list) && !list.Contains(pawn.story?.bodyType))
		{
			RandBlock val = default(RandBlock);
			((RandBlock)(ref val))._002Ector(pawn.GetPawnRNGSeed());
			try
			{
				pawn.story.bodyType = GenCollection.RandomElement<BodyTypeDef>((IEnumerable<BodyTypeDef>)list);
			}
			finally
			{
				((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
			}
		}
	}

	public static void EnsureValidHeadType(this List<CompProperties_Race> comps, BSCache cache)
	{
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		Pawn pawn = cache.pawn;
		Gender gender = cache.GetApparentGender();
		List<HeadTypeDef> list = comps.SelectMany((CompProperties_Race x) => x.HeadTypeDefs(gender)).ToList();
		if (GenCollection.Any<HeadTypeDef>(list) && !list.Contains(pawn.story?.headType))
		{
			RandBlock val = default(RandBlock);
			((RandBlock)(ref val))._002Ector(pawn.GetPawnRNGSeed());
			try
			{
				pawn.story.headType = GenCollection.RandomElement<HeadTypeDef>((IEnumerable<HeadTypeDef>)list);
			}
			finally
			{
				((IDisposable)(RandBlock)(ref val)/*cast due to .constrained prefix*/).Dispose();
			}
		}
	}
}
