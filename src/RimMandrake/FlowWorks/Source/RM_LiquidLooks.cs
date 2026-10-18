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
	/// Depth reads: each look tier (very-shallow, flood and half 0, brim 1, superdeep 2; a liquid's own suite: shallow 0, chest-deep 1, deep 2) multiplies the tint by
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

		// LIQUID_LOOK_MATERIAL_OWNERSHIP_1: every material a look writes to is its OWN copy, tracked here and destroyed
		// on revert or re-apply. GraphicDatabase/MaterialPool cache by (texture, shader, colour, queue), so mutating the
		// cached MatSingle reached any other graphic sharing that key, and each re-apply leaked a waterDepth copy.
		private static readonly Dictionary<TerrainDef, List<Material>> ownedMats = new Dictionary<TerrainDef, List<Material>>();
		private static readonly FieldInfo SingleMatField = AccessTools.Field(typeof(Graphic_Single), "mat");
		private static readonly MethodInfo CloneMethod = typeof(object).GetMethod("MemberwiseClone", BindingFlags.Instance | BindingFlags.NonPublic); // BCL, not a game type: the patch-target lint indexes game assemblies only

		private static Material Own(TerrainDef t, Material source)
		{
			Material m = new Material(source);
			if (!ownedMats.TryGetValue(t, out List<Material> list))
			{
				list = new List<Material>();
				ownedMats[t] = list;
			}
			list.Add(m);
			return m;
		}

		private static void ReleaseOwned(TerrainDef t)
		{
			if (!ownedMats.TryGetValue(t, out List<Material> list))
			{
				return;
			}
			foreach (Material m in list)
			{
				if (m != null)
				{
					UnityEngine.Object.Destroy(m);
				}
			}
			ownedMats.Remove(t);
		}

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
			// LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD (unified depth spec §4.1): the fill looks are keyed to METRES OF WATER (0.5 / 1 /
			// 1.5 / 2 m+), so the surface tier follows the water: 0.5 m and 1 m shallow, 1.5 m chest-deep, 2 m and more deep.
			if (f.fillTerrainVeryShallow != null) yield return new Member { terrain = f.fillTerrainVeryShallow, tier = 0 };
			if (f.floodTerrain != null) yield return new Member { terrain = f.floodTerrain, tier = 0 };
			if (f.fillTerrainHalf != null) yield return new Member { terrain = f.fillTerrainHalf, tier = 0 };
			if (f.fillTerrainBrim != null) yield return new Member { terrain = f.fillTerrainBrim, tier = 1 };
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
		/// darkened per tier. Pure.</summary>
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
			Graphic shared = GraphicDatabase.Get<Graphic_Terrain>(tex, shader, Vector2.one, col, 2000 + t.renderPrecedence);
			// The previous apply's materials are replaced below; the terrain still points at them until then, and the
			// caller regenerates the map meshes after, so destroying them here is safe (Destroy is end-of-frame).
			ReleaseOwned(t);
			Graphic g = shared;
			Material m = shared.MatSingle;
			if (SingleMatField != null && CloneMethod != null && shared is Graphic_Single)
			{
				g = (Graphic)CloneMethod.Invoke(shared, null);
				m = Own(t, shared.MatSingle);
				SingleMatField.SetValue(g, m);
			}
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
			bool ripple = look.rippleDensity >= 0f || look.rippleIntensity >= 0f;
			// no water ripple pass under a thick liquid, except a Solid look that asks for one (rippleDensity or
			// rippleIntensity set): opaque colour with vanilla's ripple pass over it (TAR_LOOK_TUNE_THICK_AND_SLOW)
			if (flow || (solid && !ripple))
			{
				t.waterDepthMaterial = null;
			}
			else if (o.waterDepthMaterial != null && ripple)
			{
				Material wd = Own(t, o.waterDepthMaterial);
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
			ReleaseOwned(t);
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
		/// <summary>The look row of a FluidDef or LiquidDef by defName. C8b-F2: only a Tune (<paramref name="create"/>) gives a
		/// lookless def a new look; a read never writes one.</summary>
		private static RM_LiquidSurfaceLook Find(string defName, bool create)
		{
			defName = Resolve(defName) ?? defName;
			FluidDef f = DefDatabase<FluidDef>.GetNamedSilentFail(defName);
			if (f != null)
			{
				RM_LiquidSurfaceLook look = RM_LiquidLooks.LookOfFluid(f);
				if (look == null && create)
				{
					look = new RM_LiquidSurfaceLook();
					f.surfaceLook = look;
				}
				return look;
			}
			LiquidDef l = DefDatabase<LiquidDef>.GetNamedSilentFail(defName);
			if (l != null && l.terrainSuite != null)
			{
				if (l.surfaceLook == null && create)
				{
					l.surfaceLook = new RM_LiquidSurfaceLook();
				}
				return l.surfaceLook;
			}
			return null;
		}

		/// <summary>Tune one liquid's look live and re-apply it: Tune("RM_Fluid_Tar", "tint=(0.2,0.18,0.16);flowSpeed=0.05").</summary>
		public static string Tune(string defName, string spec)
		{
			RM_LiquidSurfaceLook look = Find(defName, true);
			if (look == null)
			{
				return "no FluidDef/LiquidDef " + defName;
			}
			string bad = RM_LiquidLooks.Set(look, spec);
			RM_LiquidSurface.ForgetLook(look);
			int n = 0;
			// C8b-F4/F5: every terrain wearing this look (an inherited look is shared by the liquid's suite and each canal fluid
			// that inherits it), through Members()' official-terrain protection, never just the named def's own members
			foreach (KeyValuePair<RM_LiquidSurfaceLook, RM_LiquidLooks.Member> kv in RM_LiquidLooks.Members())
			{
				if (kv.Key != look)
				{
					continue;
				}
				RM_LiquidLooks.Revert(kv.Value.terrain);
				if (RM_LiquidLooks.Apply(kv.Value.terrain, look, kv.Value.tier)) n++;
			}
			RM_LiquidLooks.RefreshMaps();
			return "applied " + n + (bad.Length > 0 ? " bad:" + bad : "") + " | " + RM_LiquidLooks.Describe(look);
		}

		/// <summary>TAR_LOOK_TUNE_THICK_AND_SLOW: a FluidDef/LiquidDef defName as given, else a short name ("tar", "Tar")
		/// matched against RM_Liquid_&lt;name&gt; / RM_Fluid_&lt;name&gt; or a LiquidDef label, case-insensitively. Null when
		/// nothing matches.</summary>
		public static string Resolve(string name)
		{
			if (name.NullOrEmpty()) return null;
			if (DefDatabase<FluidDef>.GetNamedSilentFail(name) != null || DefDatabase<LiquidDef>.GetNamedSilentFail(name) != null)
			{
				return name;
			}
			string key = name.Replace(" ", "");
			foreach (LiquidDef l in DefDatabase<LiquidDef>.AllDefsListForReading)
			{
				if (string.Equals(l.defName, "RM_Liquid_" + key, StringComparison.OrdinalIgnoreCase)
					|| string.Equals(l.label, name, StringComparison.OrdinalIgnoreCase))
				{
					return l.defName;
				}
			}
			foreach (FluidDef f in DefDatabase<FluidDef>.AllDefsListForReading)
			{
				if (string.Equals(f.defName, "RM_Fluid_" + key, StringComparison.OrdinalIgnoreCase))
				{
					return f.defName;
				}
			}
			return null;
		}

		/// <summary>Field order of a dumped &lt;surfaceLook&gt; block: generate_liquid_suite.py's _LOOK_FIELDS, so a dump is
		/// exactly what the generator emits for the same values (selftest_liquid_look_tune.py pins the two equal and
		/// covering every public field of RM_LiquidSurfaceLook).</summary>
		public static readonly string[] FieldOrder =
		{
			"shader", "texture", "mask", "tint", "depthDarken", "flowSpeed", "flowAmplitude", "flowFrequency",
			"brightness", "spotScale", "spotSpeed", "spotMin", "spotMax", "rippleDensity", "rippleIntensity",
			"fleck", "fleckChance", "splashes", "overlay", "highlight", "strength", "scale", "speed", "sharpness",
			"stretch", "sheen", "wake", "bubbles", "bubbleColor", "seeThrough", "seeThroughTint"
		};

		private static string Text(object v)
		{
			return v is float x ? x.ToString("0.0##", CultureInfo.InvariantCulture)
				: v is Color c ? string.Format(CultureInfo.InvariantCulture, "({0:0.0##},{1:0.0##},{2:0.0##})", c.r, c.g, c.b)
				: v is bool b ? (b ? "true" : "false")
				: v?.ToString();
		}

		/// <summary>Every field of one liquid's live look, field -&gt; text (null for an unset string), in
		/// <see cref="FieldOrder"/>. Null when the def has no look.</summary>
		public static Dictionary<string, string> Values(string defName)
		{
			RM_LiquidSurfaceLook look = Peek(defName);
			if (look == null) return null;
			Dictionary<string, string> d = new Dictionary<string, string>();
			foreach (string k in FieldOrder)
			{
				FieldInfo f = typeof(RM_LiquidSurfaceLook).GetField(k, BindingFlags.Public | BindingFlags.Instance);
				d[k] = f == null ? "?" : Text(f.GetValue(look));
			}
			return d;
		}

		/// <summary>The fields whose live value differs from RM_LiquidSurfaceLook's own default, in FieldOrder.</summary>
		private static List<KeyValuePair<string, string>> Changed(RM_LiquidSurfaceLook look)
		{
			RM_LiquidSurfaceLook def = new RM_LiquidSurfaceLook();
			List<KeyValuePair<string, string>> o = new List<KeyValuePair<string, string>>();
			foreach (string k in FieldOrder)
			{
				FieldInfo f = typeof(RM_LiquidSurfaceLook).GetField(k, BindingFlags.Public | BindingFlags.Instance);
				if (f == null) continue;
				string now = Text(f.GetValue(look)), was = Text(f.GetValue(def));
				if (now != was && now != null) o.Add(new KeyValuePair<string, string>(k, now));
			}
			return o;
		}

		/// <summary>One liquid's live look as the &lt;surfaceLook&gt; XML block (fields differing from the class
		/// defaults, generator order), ready to paste into RM_LiquidDefRegistry.xml.</summary>
		public static string Xml(string defName)
		{
			RM_LiquidSurfaceLook look = Peek(defName);
			if (look == null) return null;
			StringBuilder sb = new StringBuilder("<surfaceLook>\n");
			foreach (KeyValuePair<string, string> kv in Changed(look))
			{
				sb.Append("  <").Append(kv.Key).Append('>').Append(System.Security.SecurityElement.Escape(kv.Value))
					.Append("</").Append(kv.Key).Append(">\n");
			}
			return sb.Append("</surfaceLook>").ToString();
		}

		/// <summary>The same look as a SURFACE_LOOKS entry for Tools/generate_liquid_suite.py (the registry XML is
		/// generated from that table, so the table is where a tuned look must land to survive a regenerate).</summary>
		public static string GeneratorEntry(string defName)
		{
			RM_LiquidSurfaceLook look = Peek(defName);
			if (look == null) return null;
			List<string> parts = new List<string>();
			FieldInfo[] fs = typeof(RM_LiquidSurfaceLook).GetFields(BindingFlags.Public | BindingFlags.Instance);
			foreach (KeyValuePair<string, string> kv in Changed(look))
			{
				Type t = Array.Find(fs, f => f.Name == kv.Key).FieldType;
				string v = t == typeof(float) ? kv.Value : t == typeof(bool) ? (kv.Value == "true" ? "True" : "False")
					: "\"" + kv.Value.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
				parts.Add("\"" + kv.Key + "\": " + v);
			}
			return "{" + string.Join(", ", parts) + "}";
		}

		/// <summary>Each terrain wearing this liquid's look, with what it actually draws (see <see cref="Material"/>).</summary>
		public static List<string> Terrains(string defName)
		{
			RM_LiquidSurfaceLook look = Peek(defName);
			List<string> o = new List<string>();
			if (look == null) return o;
			foreach (KeyValuePair<RM_LiquidSurfaceLook, RM_LiquidLooks.Member> kv in RM_LiquidLooks.Members())
			{
				if (kv.Key == look)
				{
					o.Add(kv.Value.terrain.defName + " tier=" + kv.Value.tier + " | " + Material(kv.Value.terrain.defName));
				}
			}
			return o;
		}

		/// <summary>The current look of one liquid, as a spec string.</summary>
		public static string Show(string defName)
		{
			RM_LiquidSurfaceLook look = Find(defName, false);
			return look == null ? "no look for " + defName + " (no such FluidDef/LiquidDef, or it has none)" : RM_LiquidLooks.Describe(look);
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

		/// <summary>A read of a look that never creates one (C8b-F2). Kept below Show so the mutation selftest's first
		/// Find(defName, false) is still Show's own.</summary>
		private static RM_LiquidSurfaceLook Peek(string defName)
		{
			return Find(defName, false);
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
