using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

public class CompProperties_MultiVerbWeapon : CompProperties
{
	public enum SwitchMode
	{
		DoubleVerbToggle,
		DoubleVerbToggleMirrored,
		SingleSwitchGizmo,
		MultiSwitchGizmo,
		FloatMenuGizmo
	}

	public class VerbData
	{
		[NoTranslate]
		public string verbLabel;

		[MustTranslate]
		public string statExplanationLabelOverride;

		public List<StatModifier> statOffsets;

		public List<StatModifier> statFactors;

		[MustTranslate]
		public string gizmoLabelOverride;

		[MustTranslate]
		public string gizmoDescriptionOverride;

		[NoTranslate]
		public string gizmoIconPathOverride;

		[Unsaved(false)]
		public Texture2D gizmoIconOverride;

		public void LoadIcons()
		{
			if (!GenText.NullOrEmpty(gizmoIconPathOverride))
			{
				gizmoIconOverride = ContentFinder<Texture2D>.Get(gizmoIconPathOverride, true);
				if ((Object)(object)gizmoIconOverride == (Object)(object)BaseContent.BadTex)
				{
					gizmoIconOverride = null;
				}
			}
		}
	}

	[NoTranslate]
	public string defaultVerbLabel;

	[MustTranslate]
	public string statExplanationLabel;

	public SwitchMode switchMode = SwitchMode.SingleSwitchGizmo;

	public List<VerbData> verbs = new List<VerbData>();

	[MustTranslate]
	public string gizmoLabel;

	[MustTranslate]
	public string gizmoDescription;

	[NoTranslate]
	public string gizmoIconPath;

	[Unsaved(false)]
	public Texture2D gizmoIcon;

	public CompProperties_MultiVerbWeapon()
	{
		base.compClass = typeof(CompMultiVerbWeapon);
	}

	public override void PostLoadSpecial(ThingDef parent)
	{
		((CompProperties)this).PostLoadSpecial(parent);
		LongEventHandler.ExecuteWhenFinished((Action)delegate
		{
			gizmoIcon = ContentFinder<Texture2D>.Get(gizmoIconPath, true);
			foreach (VerbData verb in verbs)
			{
				verb.LoadIcons();
			}
		});
	}
}
