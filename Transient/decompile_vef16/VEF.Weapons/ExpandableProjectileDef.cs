using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace VEF.Weapons;

public class ExpandableProjectileDef : ThingDef
{
	public int lifeTimeDuration = 100;

	public float widthScaleFactor = 1f;

	public float heightScaleFactor = 1f;

	public Vector3 startingPositionOffset = Vector3.zero;

	public float totalSizeScale = 1f;

	public ExpandableGraphicData graphicData;

	public int tickFrameRate = 1;

	public int finalTickFrameRate;

	public int tickDamageRate = 60;

	public float minDistanceToAffect;

	public bool disableVanillaDamageMethod;

	public bool dealsDamageOnce;

	public bool reachMaxRangeAlways;

	public float arcSize = 2.5f;

	public bool debugMode;

	public bool wideAtStart;

	public bool stopMotionOnFadeoutStarted;

	public FleckDef impactFleck;

	public bool triggerWaterSplashes;

	public SoundDef impactSound;

	public FloatRange impactFleckRotation = FloatRange.Zero;

	public FloatRange impactFleckRotationRate = FloatRange.Zero;

	public FloatRange impactFleckAngle = FloatRange.Zero;

	public FloatRange impactFleckSpeed = FloatRange.Zero;

	public bool impactFleckUsesProjectileAngle;

	public ThingDef filthOnUninterrupted;

	public float filthOnUninterruptedChance = 1f;

	public IntRange filthOnUninterruptedCount;

	public bool stopWhenHit = true;

	public float stopAtBuildingWithCover = 1f;

	public bool stopWhenNaturalRockHit;

	public bool stopWhenZeroDamageAfterHit;

	public List<string> stopWhenHitAt = new List<string>();

	public GaussProperties gauss;

	public bool IsGaussProjectile => GenTypes.SameOrSubclassOf<GaussProjectile>(base.thingClass);

	protected override void ResolveIcon()
	{
		((ThingDef)this).ResolveIcon();
		ref Texture2D uiIcon = ref ((BuildableDef)this).uiIcon;
		Texture mainTexture = graphicData.Materials[0].mainTexture;
		uiIcon = (Texture2D)(object)((mainTexture is Texture2D) ? mainTexture : null);
	}

	public override void PostLoad()
	{
		((ThingDef)this).PostLoad();
		LongEventHandler.ExecuteWhenFinished((Action)delegate
		{
			graphicData.InitMainTextures();
			graphicData.InitFadeOutTextures();
		});
	}

	public override void ResolveReferences()
	{
		((ThingDef)this).ResolveReferences();
		if (gauss == null)
		{
			gauss = GaussProperties.DefaultProperties;
		}
		gauss.ResolveReferences(this);
	}
}
