using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using VEF.CacheClearing;
using Verse;

namespace VEF.Graphics;

public class CustomOverlayDrawer : MapComponent
{
	private const OverlayTypes CustomOverlayType = 16384;

	private static CustomOverlayDrawer cachedOverlayDrawer;

	private readonly Dictionary<Thing, (OverlayHandle? handle, List<CustomOverlayDef> overlays)> activeOverlays = new Dictionary<Thing, (OverlayHandle?, List<CustomOverlayDef>)>();

	private static readonly FieldRef<OverlayDrawer, DrawBatch> DrawBatchField;

	private static readonly FieldRef<OverlayDrawer, Vector3> CurOffsetField;

	private static readonly FieldRef<OverlayDrawer, Dictionary<Thing, ThingOverlaysHandle>> OverlayHandles;

	private static readonly float BaseAlt;

	public CustomOverlayDrawer(Map map)
		: base(map)
	{
	}

	static CustomOverlayDrawer()
	{
		cachedOverlayDrawer = null;
		DrawBatchField = AccessTools.FieldRefAccess<OverlayDrawer, DrawBatch>(AccessToolsExtensions.DeclaredField(typeof(OverlayDrawer), "drawBatch"));
		CurOffsetField = AccessTools.FieldRefAccess<OverlayDrawer, Vector3>(AccessToolsExtensions.DeclaredField(typeof(OverlayDrawer), "curOffset"));
		OverlayHandles = AccessTools.FieldRefAccess<OverlayDrawer, Dictionary<Thing, ThingOverlaysHandle>>(AccessToolsExtensions.DeclaredField(typeof(OverlayDrawer), "overlayHandles"));
		BaseAlt = Altitudes.AltitudeFor((AltitudeLayer)39);
		ClearCaches.OnClearCache += delegate
		{
			cachedOverlayDrawer = null;
		};
	}

	public void Enable(Thing thing, CustomOverlayDef def)
	{
		//IL_0032: Unknown result type (might be due to invalid IL or missing references)
		if (thing != null && def != null && thing.Spawned)
		{
			if (!activeOverlays.TryGetValue(thing, out (OverlayHandle?, List<CustomOverlayDef>) value))
			{
				value = (base.map.overlayDrawer.Enable(thing, (OverlayTypes)16384), new List<CustomOverlayDef>());
				activeOverlays[thing] = value;
			}
			GenCollection.AddDistinct<CustomOverlayDef>(value.Item2, def);
		}
	}

	public void Disable(Thing thing, CustomOverlayDef def)
	{
		if (thing == null || def == null)
		{
			return;
		}
		(OverlayHandle?, List<CustomOverlayDef>) value;
		if (!thing.Spawned || !OverlayHandles.Invoke(base.map.overlayDrawer).ContainsKey(thing))
		{
			activeOverlays.Remove(thing);
		}
		else if (activeOverlays.TryGetValue(thing, out value))
		{
			value.Item2.Remove(def);
			if (value.Item2.Count <= 0)
			{
				base.map.overlayDrawer.Disable(thing, ref value.Item1);
				activeOverlays.Remove(thing);
			}
		}
	}

	internal static void PostDisposeHandle(OverlayDrawer _, Thing thing)
	{
		Map map = thing.Map;
		if (cachedOverlayDrawer == null || ((MapComponent)cachedOverlayDrawer).map != map)
		{
			cachedOverlayDrawer = map.GetComponent<CustomOverlayDrawer>();
		}
		cachedOverlayDrawer.activeOverlays.Remove(thing);
	}

	internal static void RenderCustomOverlays(OverlayDrawer _, Thing thing, OverlayTypes overlayTypes)
	{
		//IL_0008: Unknown result type (might be due to invalid IL or missing references)
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		if ((overlayTypes & 0x4000) == 0)
		{
			return;
		}
		Map map = thing.Map;
		if (cachedOverlayDrawer == null || ((MapComponent)cachedOverlayDrawer).map != map)
		{
			cachedOverlayDrawer = map.GetComponent<CustomOverlayDrawer>();
		}
		if (!cachedOverlayDrawer.activeOverlays.TryGetValue(thing, out (OverlayHandle?, List<CustomOverlayDef>) value) || value.Item2.Count <= 0)
		{
			return;
		}
		DrawBatch drawBatch = DrawBatchField.Invoke(((MapComponent)cachedOverlayDrawer).map.overlayDrawer);
		ref Vector3 curOffset2 = ref CurOffsetField.Invoke(((MapComponent)cachedOverlayDrawer).map.overlayDrawer);
		foreach (CustomOverlayDef item in value.Item2)
		{
			CustomOverlayDef overlay = item;
			List<Material> list = overlay.Worker.ExtraMaterialsForThing(thing);
			if (list.Count == 0)
			{
				RenderOverlay(overlay.Worker.MaterialForThing(thing), 2, MeshPool.plane08, incrementOffset: true, ref curOffset2);
				continue;
			}
			RenderOverlay(overlay.Worker.MaterialForThing(thing), 2, MeshPool.plane08, incrementOffset: false, ref curOffset2);
			for (int i = 0; i < list.Count; i++)
			{
				RenderOverlay(list[i], i + 3, MeshPool.plane08, i == list.Count - 1, ref curOffset2);
			}
			void RenderOverlay(Material mat, int altInd, Mesh mesh, bool incrementOffset, ref Vector3 curOffset)
			{
				//IL_0007: Unknown result type (might be due to invalid IL or missing references)
				//IL_000c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0054: Unknown result type (might be due to invalid IL or missing references)
				//IL_0057: Unknown result type (might be due to invalid IL or missing references)
				//IL_005c: Unknown result type (might be due to invalid IL or missing references)
				//IL_0061: Unknown result type (might be due to invalid IL or missing references)
				//IL_001b: Unknown result type (might be due to invalid IL or missing references)
				//IL_002f: Unknown result type (might be due to invalid IL or missing references)
				//IL_0034: Unknown result type (might be due to invalid IL or missing references)
				//IL_0039: Unknown result type (might be due to invalid IL or missing references)
				//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
				//IL_00bb: Unknown result type (might be due to invalid IL or missing references)
				//IL_007f: Unknown result type (might be due to invalid IL or missing references)
				//IL_0087: Unknown result type (might be due to invalid IL or missing references)
				//IL_008c: Unknown result type (might be due to invalid IL or missing references)
				//IL_008f: Unknown result type (might be due to invalid IL or missing references)
				//IL_0099: Unknown result type (might be due to invalid IL or missing references)
				//IL_009e: Unknown result type (might be due to invalid IL or missing references)
				//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
				//IL_00a8: Unknown result type (might be due to invalid IL or missing references)
				//IL_0155: Unknown result type (might be due to invalid IL or missing references)
				//IL_0156: Unknown result type (might be due to invalid IL or missing references)
				//IL_015b: Unknown result type (might be due to invalid IL or missing references)
				//IL_0160: Unknown result type (might be due to invalid IL or missing references)
				Vector3 val = GenThing.TrueCenter(thing);
				if (overlay.useCustomOffset)
				{
					val += overlay.Worker.CustomOffsetForThing(thing);
				}
				else
				{
					val.y = BaseAlt + 0.03658537f * (float)altInd;
					val += curOffset;
					BuildingProperties building = thing.def.building;
					if (building != null && building.isAttachment)
					{
						Vector3 val2 = val;
						Rot4 rotation = thing.Rotation;
						val = val2 + Vector2Utility.ToVector3(((Rot4)(ref rotation)).AsVector2 * 0.5f);
					}
					val.y = Mathf.Min(val.y, ((Component)Find.Camera).transform.position.y - 0.1f);
					if (incrementOffset)
					{
						curOffset.x += StackOffsetFor(thing);
					}
				}
				if (overlay.pulsing)
				{
					float num = ((float)Math.Sin((Time.realtimeSinceStartup + 397f * (float)(thing.thingIDNumber % 571)) * 4f) + 1f) * 0.5f;
					num = 0.3f + num * 0.7f;
					mat = FadedMaterialPool.FadedVersionOf(mat, num);
				}
				drawBatch.DrawMesh(mesh, Matrix4x4.TRS(val, Quaternion.identity, Vector3.one), mat, 0, true);
			}
		}
	}

	private static float StackOffsetFor(Thing t)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		return (float)t.RotatedSize.x * 0.25f;
	}
}
