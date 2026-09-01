using System.Collections.Generic;
using UnityEngine;
using VEF.Pawns;
using Verse;

namespace VEF.Things;

public class ThingDefExtension : DefModExtension
{
	public bool? usableWithShields = false;

	public WeaponDrawOffsets weaponCarryDrawOffsets;

	public WeaponDrawOffsets weaponDraftedDrawOffsets;

	public List<PawnKindDef> useFactionColourForPawnKinds;

	public float siegeBlueprintPoints = 60f;

	public Color deepColor = Color.white;

	public float transparencyMultiplier = 0.5f;

	public bool allowDeepDrill = true;

	public bool deepResourcesOnGUI;

	public bool deepResourcesOnGUIRequireScanner = true;

	public int shieldDamageIntercepted = -1;

	public bool destroyCorpse;

	public ConstructionSkillRequirement constructionSkillRequirement;

	public List<ThingStyleChance> playerCraftedStyles;

	public bool playerCraftedStylesOverrideOtherStyles;

	public float playerCraftedStyleChance = 1f;
}
