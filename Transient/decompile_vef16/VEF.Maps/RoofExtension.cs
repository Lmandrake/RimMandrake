using UnityEngine;
using Verse;

namespace VEF.Maps;

public class RoofExtension : DefModExtension
{
	public class CustomRoofGraphic
	{
		public class RoofDrawData
		{
			public Vector2 drawSize;

			public Vector3 offset;

			public AltitudeLayer layer;

			public Material material;

			public virtual void Print(MapDrawLayer mapDrawLayer, IntVec3 cell)
			{
				//IL_0003: Unknown result type (might be due to invalid IL or missing references)
				//IL_0008: Unknown result type (might be due to invalid IL or missing references)
				//IL_000e: Unknown result type (might be due to invalid IL or missing references)
				//IL_0013: Unknown result type (might be due to invalid IL or missing references)
				//IL_0018: Unknown result type (might be due to invalid IL or missing references)
				//IL_002f: Unknown result type (might be due to invalid IL or missing references)
				//IL_0031: Unknown result type (might be due to invalid IL or missing references)
				//IL_0046: Unknown result type (might be due to invalid IL or missing references)
				//IL_0047: Unknown result type (might be due to invalid IL or missing references)
				//IL_004e: Unknown result type (might be due to invalid IL or missing references)
				//IL_004f: Unknown result type (might be due to invalid IL or missing references)
				//IL_0056: Unknown result type (might be due to invalid IL or missing references)
				//IL_0057: Unknown result type (might be due to invalid IL or missing references)
				//IL_005e: Unknown result type (might be due to invalid IL or missing references)
				//IL_005f: Unknown result type (might be due to invalid IL or missing references)
				Vector3 val = ((IntVec3)(ref cell)).ToVector3ShiftedWithAltitude(layer) + offset;
				Material val2 = default(Material);
				Vector2[] array = default(Vector2[]);
				Color32 val3 = default(Color32);
				Graphic.TryGetTextureAtlasReplacementInfo(material, (TextureAtlasGroup)0, false, true, ref val2, ref array, ref val3);
				Printer_Plane.PrintPlane(mapDrawLayer, val, drawSize, val2, 0f, false, array, (Color32[])(object)new Color32[4] { val3, val3, val3, val3 }, 0.01f, 0f);
			}
		}

		public Vector2 drawSize = Vector2.one;

		public Vector3 offset = Vector3.zero;

		public AltitudeLayer layer = (AltitudeLayer)30;

		public string customRoofGraphicPath;

		public ShaderTypeDef customRoofGraphicShader;

		public Color customRoofGraphicColor = Color.white;

		public int renderQueue;

		[Unsaved(false)]
		protected RoofDrawData drawData;

		public virtual RoofDrawData DrawDataAt(Map map, IntVec3 cell, RoofDef roof)
		{
			//IL_0010: Unknown result type (might be due to invalid IL or missing references)
			//IL_0015: Unknown result type (might be due to invalid IL or missing references)
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Unknown result type (might be due to invalid IL or missing references)
			//IL_0028: Unknown result type (might be due to invalid IL or missing references)
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0055: Unknown result type (might be due to invalid IL or missing references)
			if (drawData == null)
			{
				RoofDrawData obj = new RoofDrawData
				{
					drawSize = drawSize,
					offset = offset,
					layer = layer
				};
				string text = customRoofGraphicPath;
				ShaderTypeDef obj2 = customRoofGraphicShader;
				obj.material = MaterialPool.MatFrom(text, ((obj2 != null) ? obj2.Shader : null) ?? ShaderDatabase.Cutout, customRoofGraphicColor, renderQueue);
				drawData = obj;
			}
			return drawData;
		}
	}

	public bool drawRoofShadow = true;

	public bool dealDamageOnCollapsed = true;

	public Color? roofOverlayColor;

	public CustomRoofGraphic customRoofGraphic;

	protected internal virtual bool AlwaysDrawsShadow => drawRoofShadow;

	protected internal virtual bool AlwaysDealsDamageOnCollapsed => dealDamageOnCollapsed;

	protected internal virtual bool EverUsesCustomOverlayColor => roofOverlayColor.HasValue;

	protected internal virtual bool EverUsesCustomRoofGraphic => customRoofGraphic != null;

	public virtual bool ShouldDrawShadow(Map map, int cellIndex, RoofDef roof)
	{
		return drawRoofShadow;
	}

	public virtual bool DealDamageOnCollapsed(Map map, IntVec3 cell, RoofDef roof)
	{
		return dealDamageOnCollapsed;
	}

	public virtual Color? RoofOverlayColor(Map map, int cellIndex, RoofDef roof)
	{
		return roofOverlayColor;
	}
}
