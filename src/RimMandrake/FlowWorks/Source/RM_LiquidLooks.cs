using System;
using System.Collections.Generic;
using System.Globalization;
using System.Reflection;
using System.Text;
using HarmonyLib;
using RimMandrake.FlowWorks.LiquidTypes;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// FLOWWORKS_LIQUID_LOOKS_1 (owner, 2026-10-05: <i>"All of the liquid appearances need serious work."</i> ·
	/// <i>"Can't we make the water just look like Shallow water?"</i> · tar <i>"should look like black liquid"</i>).
	///
	/// Every liquid's SURFACE is drawn by an engine shader, chosen and tuned by DATA on its look row
	/// (<see cref="RM_LiquidSurfaceLook"/>: LiquidDef.surfaceLook from Tools/generate_liquid_suite.py, or
	/// FluidDef.surfaceLook for a fluid with no row). Two carriers, both the base game's own:
	/// <list type="bullet">
	/// <item><b>Water</b> — the terrain's own vanilla water shader (Custom/Terrain water + the WaterDepth ripple pass):
	/// the exact shallow-water look and motion, tinted by <c>tint</c>, ripple pass tuned by
	/// <c>rippleDensity</c>/<c>rippleIntensity</c>. Fresh water, brine, toxic, acid, boiling, icy …</item>
	/// <item><b>Flow</b> — the base game's slow distorting lava-flow shader (Map/TerrainLavaShallow, in Core's
	/// resources; only Odyssey's ShaderTypeDef names it) over a noise texture, tinted dark: a thick liquid that
	/// visibly creeps and catches broad highlights. Tar, oil, slime.</item>
	/// </list>
	/// Depth reads: each fill tier (trace 0, half 1, brim/superdeep/deep 2) multiplies the tint by
	/// (1 - depthDarken)^tier, and water keeps vanilla's Shallow/ChestDeep/Deep ramps underneath.
	/// Terrain flecks (<c>fleck</c>, e.g. AirPuff steam off boiling water) use vanilla's per-terrain emitter.
	///
	/// Mod Setting <c>liquidLooksEnabled</c> off: nothing is applied and every fill keeps its plain XML look.
	/// Live tuning for review: <see cref="RM_LiquidLookProof"/> (jawa/static_call).
	/// </summary>
	[StaticConstructorOnStartup]
	public static class RM_LiquidLooks
	{
		public const string FlowShaderPath = "Map/TerrainLavaShallow";

		/// <summary>A look's <c>texture</c> value meaning "plain white" (no asset; BaseContent.WhiteTex).</summary>
		public const string WhiteTexture = "White";

		/// <summary>What a terrain looked like before any look was applied, so a look can be undone live.</summary>
		private class Original
		{
			public Graphic graphic;
			public Material waterDepthMaterial;
			public float throwFleckChance;
			public TerrainFleckData fleckData;
			public bool takeSplashes;
		}

		private static readonly Dictionary<TerrainDef, Original> originals = new Dictionary<TerrainDef, Original>();

		static RM_LiquidLooks()
		{
			try
			{
				if (RimMandrakeFlowWorksSettings.liquidLooksEnabled)
				{
					ApplyAll();
				}
			}
			catch (Exception e)
			{
				Log.Error("[FlowWorks] liquid looks not applied: " + e);
			}
		}

		// ── which terrains belong to which look, at which depth tier ──────────

		public struct Member
		{
			public TerrainDef terrain;
			public int tier;
		}

		/// <summary>Every (look, terrain, tier) the defs declare. A FluidDef's own look wins over its LiquidDef row's.
		/// Base-game terrains are never touched (a row may ADOPT vanilla water; vanilla stays vanilla).</summary>
		public static IEnumerable<KeyValuePair<RM_LiquidSurfaceLook, Member>> Members()
		{
			HashSet<TerrainDef> seen = new HashSet<TerrainDef>();
			foreach (FluidDef f in DefDatabase<FluidDef>.AllDefsListForReading)
			{
				RM_LiquidSurfaceLook look = LookOfFluid(f);
				if (look == null)
				{
					continue;
				}
				foreach (Member m in FluidMembers(f))
				{
					if (Owned(m.terrain) && seen.Add(m.terrain))
					{
						yield return new KeyValuePair<RM_LiquidSurfaceLook, Member>(look, m);
					}
				}
			}
			foreach (LiquidDef l in DefDatabase<LiquidDef>.AllDefsListForReading)
			{
				if (l.surfaceLook == null || l.terrainSuite == null)
				{
					continue;
				}
				foreach (Member m in SuiteMembers(l))
				{
					if (Owned(m.terrain) && seen.Add(m.terrain))
					{
						yield return new KeyValuePair<RM_LiquidSurfaceLook, Member>(l.surfaceLook, m);
					}
				}
			}
		}

		public static RM_LiquidSurfaceLook LookOfFluid(FluidDef f)
		{
			if (f.surfaceLook != null)
			{
				return f.surfaceLook;
			}
			foreach (LiquidDef l in DefDatabase<LiquidDef>.AllDefsListForReading)
			{
				if (l.canalFluid == f && l.surfaceLook != null)
				{
					return l.surfaceLook;
				}
			}
			return null;
		}

		public static IEnumerable<Member> FluidMembers(FluidDef f)
		{
			if (f.floodTerrain != null) yield return new Member { terrain = f.floodTerrain, tier = 0 };
			if (f.fillTerrainHalf != null) yield return new Member { terrain = f.fillTerrainHalf, tier = 1 };
			if (f.fillTerrainBrim != null) yield return new Member { terrain = f.fillTerrainBrim, tier = 2 };
			if (f.fillTerrainSuperdeep != null) yield return new Member { terrain = f.fillTerrainSuperdeep, tier = 2 };
		}

		public static IEnumerable<Member> SuiteMembers(LiquidDef l)
		{
			if (l.terrainSuite.shallow != null) yield return new Member { terrain = l.terrainSuite.shallow, tier = 0 };
			if (l.terrainSuite.chestDeep != null) yield return new Member { terrain = l.terrainSuite.chestDeep, tier = 1 };
			if (l.terrainSuite.deep != null) yield return new Member { terrain = l.terrainSuite.deep, tier = 2 };
		}

		private static bool Owned(TerrainDef t)
		{
			return t != null && (t.modContentPack == null || !t.modContentPack.IsOfficialMod);
		}

		// ── applying ───────────────────────────────────────────────────────────

		public static int ApplyAll()
		{
			int n = 0;
			foreach (KeyValuePair<RM_LiquidSurfaceLook, Member> kv in Members())
			{
				if (Apply(kv.Value.terrain, kv.Key, kv.Value.tier))
				{
					n++;
				}
			}
			RefreshMaps();
			return n;
		}

		public static void RevertAll()
		{
			foreach (TerrainDef t in new List<TerrainDef>(originals.Keys))
			{
				Revert(t);
			}
			RefreshMaps();
		}

		/// <summary>The colour a look paints a terrain at a tier: its tint (white = keep the def's own colour),
		/// darkened per tier. Pure; pinned by the selftest.</summary>
		public static Color TierColor(Color defColor, Color tint, float depthDarken, int tier)
		{
			Color c = IsWhite(tint) ? defColor : tint;
			float k = Mathf.Pow(Mathf.Clamp01(1f - depthDarken), Mathf.Max(0, tier));
			return new Color(c.r * k, c.g * k, c.b * k, c.a);
		}

		/// <summary>"{depth}" in a look's texture becomes vanilla's ramp word for the tier (Shallow / ChestDeep /
		/// Deep), so a tinted water keeps vanilla's three depth ramps: Terrain/Surfaces/ToxicWater{depth}Ramp.</summary>
		public static string TierTexture(string tex, int tier)
		{
			return tex.Replace("{depth}", tier <= 0 ? "Shallow" : tier == 1 ? "ChestDeep" : "Deep");
		}

		private static bool IsWhite(Color c)
		{
			return c.r >= 0.999f && c.g >= 0.999f && c.b >= 0.999f;
		}

		public static bool Apply(TerrainDef t, RM_LiquidSurfaceLook look, int tier)
		{
			if (t == null || look == null || t.graphic == null || t.graphic == BaseContent.BadGraphic)
			{
				return false;
			}
			if (!originals.TryGetValue(t, out Original o))
			{
				o = new Original
				{
					graphic = t.graphic,
					waterDepthMaterial = t.waterDepthMaterial,
					throwFleckChance = t.throwFleckChance,
					fleckData = t.fleckData,
					takeSplashes = t.takeSplashes
				};
				originals[t] = o;
			}
			bool flow = string.Equals(look.shader, "Flow", StringComparison.OrdinalIgnoreCase);
			// "Solid": the base game's plain opaque terrain shader (floors, carpets) — the colour is exactly texture x tint,
			// nothing added. Tar (live 2026-10-06: on the lava-flow shader a neutral grey tint came out OLIVE, because that
			// shader paints its own hot colours under the tint; owner: dark grey, no hue).
			bool solid = string.Equals(look.shader, "Solid", StringComparison.OrdinalIgnoreCase);
			Shader shader = solid ? ShaderDatabase.TerrainHard : flow ? ShaderDatabase.LoadShader(FlowShaderPath) : o.graphic.Shader;
			if (shader == null)
			{
				Log.WarningOnce("[FlowWorks] liquid look: shader " + FlowShaderPath + " not found; " + t.defName + " keeps its own look", 0x51A7E1);
				return false;
			}
			// "White": plain white under the shader, so the tint IS the colour (a tint on vanilla's blue water ramp always
			// stays blue — tar and propane, owner 2026-10-06). The graphic is keyed by this look's own colour, so the
			// texture swap below touches no other terrain's material.
			bool white = string.Equals(look.texture, WhiteTexture, StringComparison.OrdinalIgnoreCase);
			string tex = white ? t.texturePath : !look.texture.NullOrEmpty() ? TierTexture(look.texture, tier) : t.texturePath;
			if (ContentFinder<Texture2D>.Get(tex, false) == null)
			{
				Log.WarningOnce("[FlowWorks] liquid look: texture " + tex + " not found; " + t.defName + " keeps its own", tex.GetHashCode());
				tex = t.texturePath;
			}
			Color col = TierColor(o.graphic.Color, look.tint, look.depthDarken, tier);
			Graphic g = GraphicDatabase.Get<Graphic_Terrain>(tex, shader, Vector2.one, col, 2000 + t.renderPrecedence);
			Material m = g.MatSingle;
			m.SetTexture(ShaderPropertyIDs.AlphaAddTex, TexGame.AlphaAddTex);
			if (white)
			{
				m.mainTexture = BaseContent.WhiteTex;
			}
			if (flow)
			{
				Texture2D noise = ContentFinder<Texture2D>.Get("Other/Perlin", false);
				if (noise != null) m.SetTexture("_NoiseTex", noise);
				Texture2D mask = ContentFinder<Texture2D>.Get(look.mask.NullOrEmpty() ? "Other/White" : look.mask, false);
				m.SetTexture("_MaskTex", mask != null ? mask : Texture2D.whiteTexture);
				SetIf(m, "_DistortionSpeed", look.flowSpeed);
				SetIf(m, "_DistortionAmplitude", look.flowAmplitude);
				SetIf(m, "_DistortionFrequency", look.flowFrequency);
				SetIf(m, "_LavaBrightness", look.brightness);
				SetIf(m, "_BrightSpotScale", look.spotScale);
				SetIf(m, "_BrightSpotSpeed", look.spotSpeed);
				SetIf(m, "_BrightSpotThresholdMin", look.spotMin);
				SetIf(m, "_BrightSpotThresholdMax", look.spotMax);
			}
			t.graphic = g;
			if (flow || solid)
			{
				t.waterDepthMaterial = null;     // no water ripple pass under a thick liquid
			}
			else if (o.waterDepthMaterial != null && (look.rippleDensity >= 0f || look.rippleIntensity >= 0f))
			{
				Material wd = new Material(o.waterDepthMaterial);
				SetIf(wd, "_WaterRippleDensity", look.rippleDensity);
				SetIf(wd, "_WaterDepthIntensity", look.rippleIntensity);
				t.waterDepthMaterial = wd;
			}
			else
			{
				t.waterDepthMaterial = o.waterDepthMaterial;
			}
			FleckDef fleck = look.fleck.NullOrEmpty() ? null : DefDatabase<FleckDef>.GetNamedSilentFail(look.fleck);
			if (fleck != null && look.fleckChance > 0f)
			{
				t.throwFleckChance = look.fleckChance;
				t.fleckData = new TerrainFleckData
				{
					fleck = fleck,
					velocitySpeedRange = new FloatRange(0.01f, 0.5f),
					velocityAngleRange = new FloatRange(-90f, 90f),
					rotationSpeedRange = new FloatRange(-50f, 50f),
					solidTicksRange = new FloatRange(1f, 3f),
					scaleRange = new FloatRange(1.5f, 3f)
				};
			}
			else
			{
				t.throwFleckChance = o.throwFleckChance;
				t.fleckData = o.fleckData;
			}
			t.takeSplashes = look.splashes;
			return true;
		}

		public static void Revert(TerrainDef t)
		{
			if (t == null || !originals.TryGetValue(t, out Original o))
			{
				return;
			}
			t.graphic = o.graphic;
			t.waterDepthMaterial = o.waterDepthMaterial;
			t.throwFleckChance = o.throwFleckChance;
			t.fleckData = o.fleckData;
			t.takeSplashes = o.takeSplashes;
			originals.Remove(t);
		}

		private static void SetIf(Material m, string prop, float v)
		{
			if (v >= 0f && m.HasProperty(prop))
			{
				m.SetFloat(prop, v);
			}
		}

		private static readonly FieldInfo matCache = AccessTools.Field(typeof(TerrainGrid), "terrainMatCache");

		/// <summary>Drop every map's cached terrain materials and rebuild its terrain meshes.</summary>
		public static void RefreshMaps()
		{
			if (Current.Game == null)
			{
				return;
			}
			foreach (Map map in Find.Maps)
			{
				if (matCache?.GetValue(map.terrainGrid) is System.Collections.IDictionary d)
				{
					d.Clear();
				}
				map.mapDrawer.WholeMapChanged(MapMeshFlagDefOf.Terrain);
			}
		}

		// ── live tuning (read back into the generator table once it looks right) ──

		public static string Describe(RM_LiquidSurfaceLook look)
		{
			StringBuilder sb = new StringBuilder();
			foreach (FieldInfo f in typeof(RM_LiquidSurfaceLook).GetFields(BindingFlags.Public | BindingFlags.Instance))
			{
				object v = f.GetValue(look);
				string s = v is float x ? x.ToString("0.###", CultureInfo.InvariantCulture)
					: v is Color c ? string.Format(CultureInfo.InvariantCulture, "({0:0.###},{1:0.###},{2:0.###})", c.r, c.g, c.b)
					: v?.ToString() ?? "";
				sb.Append(f.Name).Append('=').Append(s).Append(';');
			}
			return sb.ToString();
		}

		/// <summary>Set fields of a look from "name=value;name=value" (floats, bools, strings, "(r,g,b)").</summary>
		public static string Set(RM_LiquidSurfaceLook look, string spec)
		{
			StringBuilder bad = new StringBuilder();
			foreach (string part in (spec ?? "").Split(';'))
			{
				int eq = part.IndexOf('=');
				if (eq <= 0)
				{
					continue;
				}
				string k = part.Substring(0, eq).Trim(), v = part.Substring(eq + 1).Trim();
				FieldInfo f = typeof(RM_LiquidSurfaceLook).GetField(k, BindingFlags.Public | BindingFlags.Instance);
				if (f == null)
				{
					bad.Append(k).Append('?');
					continue;
				}
				try
				{
					object val = f.FieldType == typeof(string) ? (v.Length == 0 ? null : v)
						: f.FieldType == typeof(float) ? (object)float.Parse(v, CultureInfo.InvariantCulture)
						: f.FieldType == typeof(bool) ? (object)bool.Parse(v)
						: ParseHelper.FromString(v, f.FieldType);
					f.SetValue(look, val);
				}
				catch (Exception e)
				{
					bad.Append(k).Append('!').Append(e.Message);
				}
			}
			return bad.ToString();
		}
	}

	/// <summary>Bridge hooks (jawa/static_call) for judging and tuning liquid looks live on the review map.</summary>
	public static class RM_LiquidLookProof
	{
		/// <summary>The look row of a FluidDef or LiquidDef by defName.</summary>
		private static RM_LiquidSurfaceLook Find(string defName, out IEnumerable<RM_LiquidLooks.Member> members)
		{
			FluidDef f = DefDatabase<FluidDef>.GetNamedSilentFail(defName);
			if (f != null)
			{
				members = RM_LiquidLooks.FluidMembers(f);
				RM_LiquidSurfaceLook look = RM_LiquidLooks.LookOfFluid(f);
				if (look == null)
				{
					look = new RM_LiquidSurfaceLook();
					f.surfaceLook = look;
				}
				return look;
			}
			LiquidDef l = DefDatabase<LiquidDef>.GetNamedSilentFail(defName);
			if (l != null && l.terrainSuite != null)
			{
				members = RM_LiquidLooks.SuiteMembers(l);
				if (l.surfaceLook == null)
				{
					l.surfaceLook = new RM_LiquidSurfaceLook();
				}
				return l.surfaceLook;
			}
			members = null;
			return null;
		}

		/// <summary>Tune one liquid's look live and re-apply it: Tune("RM_Fluid_Tar", "tint=(0.2,0.18,0.16);flowSpeed=0.05").</summary>
		public static string Tune(string defName, string spec)
		{
			RM_LiquidSurfaceLook look = Find(defName, out IEnumerable<RM_LiquidLooks.Member> members);
			if (look == null)
			{
				return "no FluidDef/LiquidDef " + defName;
			}
			string bad = RM_LiquidLooks.Set(look, spec);
			RM_LiquidSurface.ForgetLook(look);
			int n = 0;
			foreach (RM_LiquidLooks.Member m in members)
			{
				RM_LiquidLooks.Revert(m.terrain);
				if (RM_LiquidLooks.Apply(m.terrain, look, m.tier)) n++;
			}
			RM_LiquidLooks.RefreshMaps();
			return "applied " + n + (bad.Length > 0 ? " bad:" + bad : "") + " | " + RM_LiquidLooks.Describe(look);
		}

		/// <summary>The current look of one liquid, as a spec string.</summary>
		public static string Show(string defName)
		{
			RM_LiquidSurfaceLook look = Find(defName, out _);
			return look == null ? "no FluidDef/LiquidDef " + defName : RM_LiquidLooks.Describe(look);
		}

		/// <summary>What a terrain actually draws with: shader, colour, texture, queue of its graphic and of its water-depth
		/// overlay. For finding why a look change shows nothing (tar rendering flat black, 2026-10-06).</summary>
		public static string Material(string terrainDefName)
		{
			TerrainDef t = DefDatabase<TerrainDef>.GetNamedSilentFail(terrainDefName);
			if (t == null) return "no TerrainDef " + terrainDefName;
			StringBuilder sb = new StringBuilder();
			Material m = t.graphic?.MatSingle;
			sb.Append("def.color=").Append(t.color).Append(" edge=").Append(t.edgeType).Append(" prec=").Append(t.renderPrecedence);
			sb.Append(" | graphic=").Append(m == null ? "null" : m.shader.name + " color=" + m.color + " tex=" + (m.mainTexture != null ? m.mainTexture.name : "null") + " queue=" + m.renderQueue);
			Material wd = t.waterDepthMaterial;
			sb.Append(" | depth=").Append(wd == null ? "null" : wd.shader.name + " color=" + (wd.HasProperty("_Color") ? wd.color.ToString() : "n/a") + " queue=" + wd.renderQueue);
			sb.Append(" | edgeMat=").Append(t.edgeType);
			return sb.ToString();
		}

		/// <summary>"on" re-applies every look; "off" restores every fill's plain XML look (the Mod Setting's fallback).</summary>
		public static string All(string onOff)
		{
			if (onOff == "off")
			{
				RM_LiquidLooks.RevertAll();
				return "reverted";
			}
			RM_LiquidLooks.RevertAll();
			return "applied " + RM_LiquidLooks.ApplyAll();
		}
	}
}
