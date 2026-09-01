using System;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class CustomOverlayDef : Def
{
	public Type workerClass = typeof(CustomOverlayWorker);

	public bool pulsing = true;

	public bool useCustomOffset;

	public Vector3 customOffset = Vector3.zero;

	[NoTranslate]
	public string overlayPath;

	public ShaderTypeDef shaderType;

	public Material CachedMaterial { get; protected set; }

	public CustomOverlayWorker Worker { get; protected set; }

	public override void PostLoad()
	{
		((Editable)this).PostLoad();
		LongEventHandler.ExecuteWhenFinished((Action)delegate
		{
			Worker = (CustomOverlayWorker)Activator.CreateInstance(workerClass, this);
			if (shaderType == null)
			{
				shaderType = ShaderTypeDefOf.MetaOverlay;
			}
			if (!GenText.NullOrEmpty(overlayPath))
			{
				CachedMaterial = MaterialPool.MatFrom(overlayPath, shaderType.Shader);
			}
		});
	}
}
