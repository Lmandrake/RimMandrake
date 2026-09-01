using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class CompProperties_ColorAndFur : HediffCompProperties
{
	private List<Color> skinColorOverride;

	private List<Color> hairColorOverride;

	public FurDef furskinOverride;

	public bool skinIsHairColor;

	protected BodyTypeDef bodyDefOverride;

	protected BodyTypeDef bodyDefOverride_Female;

	protected List<BodyTypeDef> bodyDefOverrideList = new List<BodyTypeDef>();

	protected List<BodyTypeDef> bodyDefOverrideList_Female = new List<BodyTypeDef>();

	protected HeadTypeDef headDefOverride;

	protected HeadTypeDef headDefOverride_Female;

	protected List<HeadTypeDef> headDefOverrideList = new List<HeadTypeDef>();

	protected List<HeadTypeDef> headDefOverrideList_Female = new List<HeadTypeDef>();

	public bool disableFacialAnims;

	public bool disableBeards;

	public bool disableHair;

	public bool hideHead;

	public bool hideBody;

	private List<BodyTypeDef> BodyDefs
	{
		get
		{
			if (bodyDefOverride != null)
			{
				List<BodyTypeDef> list = bodyDefOverrideList;
				List<BodyTypeDef> list2 = new List<BodyTypeDef>(1 + list.Count);
				list2.AddRange(list);
				list2.Add(bodyDefOverride);
				return list2;
			}
			return bodyDefOverrideList;
		}
	}

	private List<BodyTypeDef> BodyDefsFemale
	{
		get
		{
			if (bodyDefOverride_Female != null)
			{
				List<BodyTypeDef> list = bodyDefOverrideList_Female;
				List<BodyTypeDef> list2 = new List<BodyTypeDef>(1 + list.Count);
				list2.AddRange(list);
				list2.Add(bodyDefOverride_Female);
				return list2;
			}
			return bodyDefOverrideList_Female;
		}
	}

	private List<HeadTypeDef> HeadDefs
	{
		get
		{
			if (headDefOverride != null)
			{
				List<HeadTypeDef> list = headDefOverrideList;
				List<HeadTypeDef> list2 = new List<HeadTypeDef>(1 + list.Count);
				list2.AddRange(list);
				list2.Add(headDefOverride);
				return list2;
			}
			return headDefOverrideList;
		}
	}

	private List<HeadTypeDef> HeadDefsFemale
	{
		get
		{
			if (headDefOverride_Female != null)
			{
				List<HeadTypeDef> list = headDefOverrideList_Female;
				List<HeadTypeDef> list2 = new List<HeadTypeDef>(1 + list.Count);
				list2.AddRange(list);
				list2.Add(headDefOverride_Female);
				return list2;
			}
			return headDefOverrideList_Female;
		}
	}

	public List<Color> SkinColorOverride => skinColorOverride;

	public List<Color> HairColorOverride => hairColorOverride;

	public List<BodyTypeDef> BodyTypeDefs(Gender targetGender)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Invalid comparison between Unknown and I4
		if ((int)targetGender != 2 || !GenCollection.Any<BodyTypeDef>(BodyDefsFemale))
		{
			return BodyDefs;
		}
		return BodyDefsFemale;
	}

	public List<HeadTypeDef> HeadTypeDefs(Gender targetGender)
	{
		//IL_0000: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Invalid comparison between Unknown and I4
		if ((int)targetGender != 2 || !GenCollection.Any<HeadTypeDef>(HeadDefsFemale))
		{
			return HeadDefs;
		}
		return HeadDefsFemale;
	}

	public CompProperties_ColorAndFur()
	{
		base.compClass = typeof(HediffComp_ColorAndFur);
	}
}
