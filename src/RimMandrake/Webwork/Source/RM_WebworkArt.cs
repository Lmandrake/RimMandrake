using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.Webwork
{
	/// <summary>
	/// WEBWORK_TERRAIN_WEATHER_PASS_1: the art contract of the web network and webfall (the RM_DrawbridgeArt pattern). The
	/// commissioned pictures do not exist until they pass review and `art install`; every def names a stand-in that DOES
	/// exist, and at startup each contract path is looked up SILENTLY (ContentFinder, no error). When one is installed it
	/// replaces the stand-in with no def or code change. Nothing here generates or queues art.
	///
	///   RM_Webwork_Cable       stand-in Things/Building/Natural/RM_Webwork_Anchor -> contract ContractCable
	///   RM_Webwork_Strand      stand-in Things/Building/Natural/RM_Webwork_Web    -> contract ContractStrand
	///   RM_Webwork_SilkCarpet  stand-in Terrain/Surfaces/Carpet (tinted)          -> contract ContractCarpet
	///   webfall overlay        stand-in a copy of the vanilla gentle-snow material -> contract texture ContractWebfall
	/// </summary>
	[StaticConstructorOnStartup]
	public static class RM_WebworkArt
	{
		public const string ContractCable = "Things/Building/Natural/RM_Webwork_Cable";
		public const string ContractStrand = "Things/Building/Natural/RM_Webwork_Strand";
		public const string ContractCarpet = "Terrain/Surfaces/RM_Webwork_SilkCarpet";
		public const string ContractWebfall = "Weather/RM_WebfallOverlay";

		/// <summary>Which contract pictures were found installed at startup (the proof reports it).</summary>
		public static readonly List<string> Installed = new List<string>();

		public static readonly Material WebfallMat;

		static RM_WebworkArt()
		{
			BindThing(RM_GenStep_WebworkWeb.CableDefName, ContractCable);
			BindThing(RM_GenStep_WebworkWeb.StrandDefName, ContractStrand);
			BindTerrain(RM_GenStep_WebworkWeb.CarpetDefName, ContractCarpet);
			WebfallMat = MakeWebfallMat();
		}

		private static Texture2D Find(string path)
		{
			return ContentFinder<Texture2D>.Get(path, false);
		}

		private static void BindThing(string defName, string contract)
		{
			ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
			Texture2D tex = Find(contract);
			if (def?.graphicData == null || tex == null)
			{
				return;
			}
			var gd = new GraphicData();
			gd.CopyFrom(def.graphicData);
			gd.texPath = contract;
			def.graphicData = gd;
			def.graphic = gd.Graphic;
			def.uiIcon = tex;
			Installed.Add(contract);
		}

		private static void BindTerrain(string defName, string contract)
		{
			TerrainDef def = DefDatabase<TerrainDef>.GetNamedSilentFail(defName);
			Texture2D tex = Find(contract);
			if (def == null || tex == null)
			{
				return;
			}
			def.texturePath = contract;
			def.color = Color.white; // the installed picture carries its own colour; the tint was for the vanilla stand-in
			def.graphic = GraphicDatabase.Get<Graphic_Terrain>(contract, def.Shader, Vector2.one, def.DrawColor, 2000 + def.renderPrecedence);
			if (def.edgeType == TerrainDef.TerrainEdgeType.FadeRough)
			{
				def.graphic.MatSingle.SetTexture(ShaderPropertyIDs.AlphaAddTex, TexGame.AlphaAddTex);
			}
			def.uiIcon = tex;
			Installed.Add(contract);
		}

		private static Material MakeWebfallMat()
		{
			Material baseMat = MatLoader.LoadMat("Weather/SnowOverlayWorld");
			if (baseMat == null)
			{
				return null;
			}
			var mat = new Material(baseMat) { name = "RM_WebfallOverlay" };
			Texture2D tex = Find(ContractWebfall);
			if (tex != null)
			{
				mat.SetTexture("_MainTex", tex);
				if (mat.HasProperty("_MainTex2"))
				{
					mat.SetTexture("_MainTex2", tex);
				}
				Installed.Add(ContractWebfall);
			}
			return mat;
		}
	}

	/// <summary>
	/// WEBWORK_TERRAIN_WEATHER_PASS_1: webfall's overlay. A dual panner like vanilla gentle snow, slower and nearly straight
	/// down (shed silk drifting, not snow blowing), on its OWN material (RM_WebworkArt.WebfallMat, a copy) so the vanilla snow
	/// material is never touched. The weather manager sets the overlay's colour each frame from the sky, as for any weather.
	/// </summary>
	public class RM_WeatherOverlay_Webfall : WeatherOverlayDualPanner
	{
		public RM_WeatherOverlay_Webfall()
		{
			worldOverlayMat = RM_WebworkArt.WebfallMat;
			worldOverlayPanSpeed1 = 0.0009f;
			worldPanDir1 = new Vector2(0.12f, -1f);
			worldPanDir1.Normalize();
			worldOverlayPanSpeed2 = 0.0013f;
			worldPanDir2 = new Vector2(-0.08f, -1f);
			worldPanDir2.Normalize();
		}

		public override void TickOverlay(Map map, float lerpFactor)
		{
			if (worldOverlayMat == null)
			{
				worldOverlayMat = RM_WebworkArt.WebfallMat; // built before the startup class ran: pick it up late
			}
			base.TickOverlay(map, lerpFactor);
		}
	}
}
