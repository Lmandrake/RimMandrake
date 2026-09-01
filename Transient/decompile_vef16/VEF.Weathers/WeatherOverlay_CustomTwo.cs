using UnityEngine;
using Verse;

namespace VEF.Weathers;

public class WeatherOverlay_CustomTwo : WeatherOverlayDualPanner
{
	public WeatherDef curWeather;

	public override void TickOverlay(Map map, float lerpFactor)
	{
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_006a: Unknown result type (might be due to invalid IL or missing references)
		//IL_006f: Unknown result type (might be due to invalid IL or missing references)
		if (curWeather != map.weatherManager.curWeather)
		{
			curWeather = map.weatherManager.curWeather;
			WeatherOverlayExtensionTwo modExtension = ((Def)curWeather).GetModExtension<WeatherOverlayExtensionTwo>();
			if (modExtension != null)
			{
				base.worldOverlayPanSpeed1 = modExtension.worldOverlayPanSpeed1;
				base.worldPanDir1 = modExtension.worldPanDir1;
				((Vector2)(ref base.worldPanDir1)).Normalize();
				base.worldOverlayPanSpeed2 = modExtension.worldOverlayPanSpeed2;
				base.worldPanDir2 = modExtension.worldPanDir2;
				((Vector2)(ref base.worldPanDir2)).Normalize();
				base.worldOverlayMat = MaterialPool.MatFrom(modExtension.overlayPath);
				Material val = MatLoader.LoadMat(modExtension.copyPropertiesFrom, -1);
				base.worldOverlayMat.CopyPropertiesFromMaterial(val);
				base.worldOverlayMat.shader = val.shader;
				Texture2D val2 = ContentFinder<Texture2D>.Get(modExtension.overlayPath, true);
				base.worldOverlayMat.SetTexture("_MainTex", (Texture)(object)val2);
				base.worldOverlayMat.SetTexture("_MainTex2", (Texture)(object)val2);
			}
		}
		((WeatherOverlayDualPanner)this).TickOverlay(map, lerpFactor);
	}
}
