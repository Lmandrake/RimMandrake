using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Buildings;

public class CompProperties_Refuelable_DualFuel : CompProperties_Refuelable
{
	public float secondaryFuelCapacity = 10f;

	public float initialSecondaryFuelPercent;

	public float autoRefuelSecondaryPercent = 0.3f;

	public ThingFilter secondaryFuelFilter;

	public bool initialAllowAutoRefuelSecondary = true;

	public bool showAllowAutoRefuelSecondaryToggle;

	public bool targetSecondaryFuelLevelConfigurable;

	public float initialConfigurableSecondaryTargetFuelLevel;

	public float minimumSecondaryFueledThreshold = 1f;

	private float secondaryFuelMultiplier = 1f;

	public bool factorSecondaryByDifficulty;

	[MustTranslate]
	public string secondaryFuelLabel;

	[MustTranslate]
	public string secondaryFuelGizmoLabel;

	[MustTranslate]
	public string outOfSecondaryFuelMessage;

	[NoTranslate]
	public string secondaryFuelIconPath;

	private Texture2D secondaryFuelIcon;

	public static HashSet<ThingDef> allSecondaryFuelDefs = new HashSet<ThingDef>();

	public string SecondaryFuelLabel
	{
		get
		{
			//IL_0012: Unknown result type (might be due to invalid IL or missing references)
			if (GenText.NullOrEmpty(secondaryFuelLabel))
			{
				return TaggedString.op_Implicit(Translator.Translate("VFES_SecondaryFuel"));
			}
			return secondaryFuelLabel;
		}
	}

	public string SecondaryFuelGizmoLabel
	{
		get
		{
			//IL_0012: Unknown result type (might be due to invalid IL or missing references)
			if (GenText.NullOrEmpty(secondaryFuelGizmoLabel))
			{
				return TaggedString.op_Implicit(Translator.Translate("VFES_SecondaryFuel"));
			}
			return secondaryFuelGizmoLabel;
		}
	}

	public Texture2D SecondaryFuelIcon
	{
		get
		{
			if ((Object)(object)secondaryFuelIcon == (Object)null)
			{
				if (!GenText.NullOrEmpty(secondaryFuelIconPath))
				{
					secondaryFuelIcon = ContentFinder<Texture2D>.Get(secondaryFuelIconPath, true);
				}
				else
				{
					ThingFilter obj = secondaryFuelFilter;
					ThingDef val = ((obj != null) ? obj.AnyAllowedDef : null) ?? ThingDefOf.Shell_HighExplosive;
					secondaryFuelIcon = ((BuildableDef)val).uiIcon;
				}
			}
			return secondaryFuelIcon;
		}
	}

	public float SecondaryFuelMultiplierCurrentDifficulty
	{
		get
		{
			if (factorSecondaryByDifficulty && Find.Storyteller?.difficulty != null)
			{
				return secondaryFuelMultiplier / Find.Storyteller.difficulty.maintenanceCostFactor;
			}
			return secondaryFuelMultiplier;
		}
	}

	public CompProperties_Refuelable_DualFuel()
	{
		((CompProperties)this).compClass = typeof(CompRefuelable_DualFuel);
	}

	public override void ResolveReferences(ThingDef parentDef)
	{
		((CompProperties_Refuelable)this).ResolveReferences(parentDef);
		ThingFilter obj = secondaryFuelFilter;
		if (obj != null)
		{
			obj.ResolveReferences();
		}
		allSecondaryFuelDefs.Add(parentDef);
	}
}
