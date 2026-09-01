using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class GeneTemplate : Def
{
	public GeneCategoryDef displayCategory;

	public float selectionWeight = 1f;

	public bool canGenerateInGeneSet = true;

	public string keyTag = "";

	public string backgroundPathEndogenes;

	public string backgroundPathXenogenes;

	public string backgroundPathArchite;

	public Color? iconColor;

	public List<string> customEffectDescriptions = new List<string>();
}
