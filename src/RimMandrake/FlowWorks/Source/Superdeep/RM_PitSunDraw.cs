using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM, step 3: the pit relief's sun is the game's own. Vanilla
	/// sets one shadow vector a frame (SkyManager.SkyManagerUpdate -> _CastVect: the sun by day, the moon by night, strength 0 round dusk
	/// and dawn, a pinned sun's override on Utinni); every building shadow follows it. The walls layer bakes its cast shadow, so this
	/// reads that vector on the current map, snaps it (RM_PitReliefMath.SunKey), and re-meshes the relief when the snapped sun or the sky
	/// glow moves. A square's own share of the sun (roof, lamps) is read when the square is meshed; lamps and roofs already re-mesh it
	/// (GroundGlow, Roofs). No lamp casts a shadow here: that is a new feature for the owner.</summary>
	internal static class RM_PitSunDraw
	{
		private static MapMeshFlagDef flag;
		private static bool flagResolved;

		/// <summary>The relief's own mesh flag (only the walls layer listens); 0 if the def is missing (then the sun bakes once).</summary>
		public static ulong PitSunFlag
		{
			get
			{
				if (!flagResolved)
				{
					flag = DefDatabase<MapMeshFlagDef>.GetNamedSilentFail("RM_PitSun");
					flagResolved = true;
				}
				return flag;
			}
		}

		/// <summary>Every 20 frames on the current map: read the game's shadow vector and sky glow, and re-mesh the relief when the snapped
		/// sun or sky moved. The read is one shader global; a re-mesh happens a few dozen times a game day.</summary>
		public static void Update(Map map, RM_MapComponent_Excavation eng)
		{
			if (map == null || eng == null || map != Find.CurrentMap || !RM_UnderLiquid.Relief || Time.frameCount % 20 != 0
				|| eng.ExcavatedCellCount == 0)
			{
				return;
			}
			Vector4 v = Shader.GetGlobalVector(ShaderPropertyIDs.MapSunLightDirection);
			float sky = map.skyManager.CurSkyGlow;
			int key = RM_PitReliefMath.SunKey(v.x, v.z, v.w, sky);
			if (key == eng.pitSunKey)
			{
				return;
			}
			eng.pitSunKey = key;
			eng.pitSun = RM_PitReliefMath.QuantizedSun(v.x, v.z, v.w);
			eng.pitSky = Mathf.Round(Mathf.Clamp01(sky) / RM_PitReliefMath.SkyStep) * RM_PitReliefMath.SkyStep;
			if (PitSunFlag != 0)
			{
				map.mapDrawer.WholeMapChanged(PitSunFlag);
			}
		}

		/// <summary>The sun as it reaches square <paramref name="c"/>: the baked game sun times its share (none under a roof, none where
		/// lamp light outshines the sky).</summary>
		public static RM_PitReliefMath.PitSun SunAt(Map map, RM_MapComponent_Excavation eng, IntVec3 c)
		{
			RM_PitReliefMath.PitSun sun = eng != null ? eng.pitSun : RM_PitReliefMath.FixedSun;
			float sky = eng != null ? eng.pitSky : 1f;
			bool roofed = map.roofGrid.Roofed(c);
			float lamp = map.glowGrid.GroundGlowAt(c, false, true);
			return RM_PitReliefMath.Reached(sun, RM_PitReliefMath.SkyShare(roofed, sky, lamp));
		}
	}
}
