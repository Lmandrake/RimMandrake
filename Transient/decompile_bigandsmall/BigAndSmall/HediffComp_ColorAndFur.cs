using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class HediffComp_ColorAndFur : HediffComp
{
	public CompProperties_ColorAndFur CRProps => (CompProperties_ColorAndFur)(object)base.props;

	public override void CompPostMake()
	{
		//IL_0179: Unknown result type (might be due to invalid IL or missing references)
		//IL_017e: Unknown result type (might be due to invalid IL or missing references)
		//IL_003d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_023c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0063: Unknown result type (might be due to invalid IL or missing references)
		//IL_005c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0365: Unknown result type (might be due to invalid IL or missing references)
		//IL_0277: Unknown result type (might be due to invalid IL or missing references)
		//IL_027c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0297: Unknown result type (might be due to invalid IL or missing references)
		//IL_0267: Unknown result type (might be due to invalid IL or missing references)
		//IL_0210: Unknown result type (might be due to invalid IL or missing references)
		//IL_0215: Unknown result type (might be due to invalid IL or missing references)
		//IL_0216: Unknown result type (might be due to invalid IL or missing references)
		//IL_021d: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_03ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_0346: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostMake();
		Pawn val = ((Hediff)(base.parent?)).pawn;
		BSCache cache = FastAcccess.GetCache(val);
		if (cache == null)
		{
			return;
		}
		if (val.story != null)
		{
			BSCache bSCache = cache;
			Color valueOrDefault = bSCache.savedSkinColor.GetValueOrDefault();
			if (!bSCache.savedSkinColor.HasValue)
			{
				Pawn_StoryTracker story = val.story;
				valueOrDefault = ((story != null) ? story.SkinColor : Color.white);
				bSCache.savedSkinColor = valueOrDefault;
			}
			bSCache = cache;
			Color? savedHairColor = bSCache.savedHairColor;
			if (!savedHairColor.HasValue)
			{
				BSCache bSCache2 = bSCache;
				Pawn_StoryTracker story2 = val.story;
				bSCache2.savedHairColor = ((story2 != null) ? new Color?(story2.HairColor) : ((Color?)null));
			}
			bSCache = cache;
			if (bSCache.savedFurSkin == null)
			{
				bSCache.savedFurSkin = ((Def)(val.story?.furDef?)).defName;
			}
			bSCache = cache;
			if (bSCache.savedBodyDef == null)
			{
				bSCache.savedBodyDef = ((Def)(val.story?.bodyType?)).defName;
			}
			bSCache = cache;
			if (bSCache.savedHeadDef == null)
			{
				bSCache.savedHeadDef = ((Def)(val.story?.headType?)).defName;
			}
			bSCache = cache;
			if (bSCache.savedBeardDef == null)
			{
				bSCache.savedBeardDef = ((Def)(val.style?.beardDef?)).defName;
			}
		}
		Gender apparentGender = cache.GetApparentGender();
		if (CRProps.HairColorOverride != null)
		{
			if (!cache.randomPickHairColor.HasValue || cache.randomPickHairColor >= CRProps.HairColorOverride.Count - 1)
			{
				cache.randomPickHairColor = Rand.Range(0, CRProps.HairColorOverride.Count - 1);
			}
			Color valueOrDefault = (val.story.HairColor = CRProps.HairColorOverride[cache.randomPickHairColor.Value]);
			cache.overridenHairColor = valueOrDefault;
		}
		if (CRProps.skinIsHairColor)
		{
			if (val.story.HairColor.a < 0.05f)
			{
				val.story.HairColor = new Color(0.3f, 0.2f, 0.1f, 1f);
			}
			Color hairColor = val.story.HairColor;
			hairColor.a = 1f;
			val.story.skinColorOverride = (cache.overridenSkinColor = val.story.HairColor);
		}
		else if (CRProps.SkinColorOverride != null)
		{
			if (!cache.randomPickSkinColor.HasValue || cache.randomPickSkinColor >= CRProps.SkinColorOverride.Count - 1)
			{
				cache.randomPickSkinColor = Rand.Range(0, CRProps.SkinColorOverride.Count - 1);
			}
			val.story.skinColorOverride = (cache.overridenSkinColor = CRProps.SkinColorOverride[cache.randomPickSkinColor.Value]);
		}
		List<BodyTypeDef> list = CRProps.BodyTypeDefs(apparentGender);
		RandBlock val3 = default(RandBlock);
		if (val.story != null && GenCollection.Any<BodyTypeDef>(list) && !list.Contains(val.story.bodyType))
		{
			((RandBlock)(ref val3))._002Ector(((Thing)val).thingIDNumber);
			try
			{
				val.story.bodyType = (cache.overridenBodyDef = GenCollection.RandomElement<BodyTypeDef>((IEnumerable<BodyTypeDef>)list));
			}
			finally
			{
				((IDisposable)(RandBlock)(ref val3)/*cast due to .constrained prefix*/).Dispose();
			}
		}
		List<HeadTypeDef> list2 = CRProps.HeadTypeDefs(apparentGender);
		if (val.story != null && GenCollection.Any<HeadTypeDef>(list2) && !list2.Contains(val.story.headType))
		{
			((RandBlock)(ref val3))._002Ector(((Thing)val).thingIDNumber);
			try
			{
				val.story.headType = (cache.overridenHeadDef = GenCollection.RandomElement<HeadTypeDef>((IEnumerable<HeadTypeDef>)list2));
			}
			finally
			{
				((IDisposable)(RandBlock)(ref val3)/*cast due to .constrained prefix*/).Dispose();
			}
		}
		if (CRProps.furskinOverride != null)
		{
			val.story.furDef = (cache.overridenFurSkin = CRProps.furskinOverride);
		}
		if (CRProps.disableFacialAnims)
		{
			cache.facialAnimationDisabled_Transform = true;
		}
		if (CRProps.disableBeards)
		{
			val.style.beardDef = (cache.overridenBeardDef = null);
		}
		if (CRProps.disableHair)
		{
			val.story.hairDef = (cache.overridenHairDef = HairDefOf.Bald);
		}
	}

	public override void CompPostPostRemoved()
	{
		//IL_0046: Unknown result type (might be due to invalid IL or missing references)
		//IL_0096: Unknown result type (might be due to invalid IL or missing references)
		//IL_0068: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b8: Unknown result type (might be due to invalid IL or missing references)
		//IL_0165: Unknown result type (might be due to invalid IL or missing references)
		//IL_016a: Unknown result type (might be due to invalid IL or missing references)
		//IL_01a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ac: Unknown result type (might be due to invalid IL or missing references)
		//IL_017f: Unknown result type (might be due to invalid IL or missing references)
		//IL_01c1: Unknown result type (might be due to invalid IL or missing references)
		//IL_0224: Unknown result type (might be due to invalid IL or missing references)
		//IL_0259: Unknown result type (might be due to invalid IL or missing references)
		((HediffComp)this).CompPostPostRemoved();
		Pawn val = ((Hediff)(base.parent?)).pawn;
		BSCache cache = FastAcccess.GetCache(val);
		if (cache == null || val.story == null)
		{
			return;
		}
		if (cache.savedSkinColor.HasValue && (double)cache.savedSkinColor.Value.a > 0.05)
		{
			val.story.skinColorOverride = cache.savedSkinColor.Value;
			cache.savedSkinColor = null;
		}
		if (cache.savedHairColor.HasValue && (double)cache.savedHairColor.Value.a > 0.05)
		{
			val.story.HairColor = cache.savedHairColor.Value;
			cache.savedHairColor = null;
		}
		if (cache.savedFurSkin != null)
		{
			FurDef named = DefDatabase<FurDef>.GetNamed(cache.savedFurSkin, true);
			if (named != null)
			{
				val.story.furDef = named;
				cache.savedFurSkin = null;
			}
		}
		if (cache.savedBodyDef != null)
		{
			BodyTypeDef named2 = DefDatabase<BodyTypeDef>.GetNamed(cache.savedBodyDef, true);
			if (named2 != null)
			{
				val.story.bodyType = named2;
				cache.savedBodyDef = null;
			}
		}
		if (cache.savedHeadDef != null)
		{
			HeadTypeDef named3 = DefDatabase<HeadTypeDef>.GetNamed(cache.savedHeadDef, true);
			if (named3 != null)
			{
				val.story.headType = named3;
				cache.savedHeadDef = null;
			}
		}
		Color? overridenSkinColor = cache.overridenSkinColor;
		if (overridenSkinColor.HasValue)
		{
			Color valueOrDefault = overridenSkinColor.GetValueOrDefault();
			List<Color> skinColorOverride = CRProps.SkinColorOverride;
			if (skinColorOverride != null && skinColorOverride.Contains(valueOrDefault))
			{
				cache.overridenHairColor = null;
			}
		}
		overridenSkinColor = cache.overridenHairColor;
		if (overridenSkinColor.HasValue)
		{
			Color valueOrDefault2 = overridenSkinColor.GetValueOrDefault();
			List<Color> hairColorOverride = CRProps.HairColorOverride;
			if (hairColorOverride != null && hairColorOverride.Contains(valueOrDefault2))
			{
				cache.overridenHairColor = null;
			}
		}
		if (CRProps.skinIsHairColor)
		{
			cache.overridenSkinColor = null;
		}
		FurDef overridenFurSkin = cache.overridenFurSkin;
		if (overridenFurSkin != null && overridenFurSkin == CRProps.furskinOverride)
		{
			cache.overridenFurSkin = null;
		}
		BodyTypeDef overridenBodyDef = cache.overridenBodyDef;
		if (overridenBodyDef != null)
		{
			List<BodyTypeDef> list = CRProps.BodyTypeDefs(val.gender);
			if (list != null && list.Contains(overridenBodyDef))
			{
				cache.overridenBodyDef = null;
			}
		}
		HeadTypeDef overridenHeadDef = cache.overridenHeadDef;
		if (overridenHeadDef != null)
		{
			List<HeadTypeDef> list2 = CRProps.HeadTypeDefs(val.gender);
			if (list2 != null && list2.Contains(overridenHeadDef))
			{
				cache.overridenHeadDef = null;
			}
		}
		if (CRProps.disableFacialAnims)
		{
			cache.facialAnimationDisabled_Transform = false;
		}
		if (CRProps.disableBeards)
		{
			if (cache.savedBeardDef != null)
			{
				BeardDef named4 = DefDatabase<BeardDef>.GetNamed(cache.savedBeardDef, true);
				if (named4 != null)
				{
					val.style.beardDef = named4;
					goto IL_02d1;
				}
			}
			val.style.beardDef = null;
			goto IL_02d1;
		}
		goto IL_02d8;
		IL_02d8:
		if (!CRProps.disableHair)
		{
			return;
		}
		if (cache.savedHairDef != null)
		{
			HairDef named5 = DefDatabase<HairDef>.GetNamed(cache.savedHairDef, true);
			if (named5 != null)
			{
				val.story.hairDef = named5;
				goto IL_0323;
			}
		}
		val.story.hairDef = GenCollection.RandomElement<HairDef>(DefDatabase<HairDef>.AllDefs);
		goto IL_0323;
		IL_0323:
		cache.savedHairDef = null;
		return;
		IL_02d1:
		cache.savedBeardDef = null;
		goto IL_02d8;
	}
}
