using UnityEngine;
using Verse;

namespace VEF.Weathers;

public class WeatherOverlay_Custom : WeatherOverlayDualPanner
{
	public WeatherDef weatherDef;

	public WeatherDef curWeather;

	public override void TickOverlay(Map map, float lerpFactor)
	{
		//IL_005d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0062: Unknown result type (might be due to invalid IL or missing references)
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Expected O, but got Unknown
		//IL_00b7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bd: Expected O, but got Unknown
		if (curWeather != map.weatherManager.curWeather && weatherDef == map.weatherManager.curWeather)
		{
			curWeather = map.weatherManager.curWeather;
			WeatherOverlayExtension modExtension = ((Def)curWeather).GetModExtension<WeatherOverlayExtension>();
			if (modExtension != null)
			{
				base.worldOverlayPanSpeed1 = modExtension.worldOverlayPanSpeed1;
				base.worldPanDir1 = modExtension.worldPanDir1;
				((Vector2)(ref base.worldPanDir1)).Normalize();
				base.worldOverlayPanSpeed2 = modExtension.worldOverlayPanSpeed2;
				base.worldPanDir2 = modExtension.worldPanDir2;
				((Vector2)(ref base.worldPanDir2)).Normalize();
				base.worldOverlayMat = new Material(MaterialPool.MatFrom(modExtension.overlayPath));
				Material val = new Material(MatLoader.LoadMat(modExtension.copyPropertiesFrom, -1));
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
