using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Thirst
{
	[DefOf]
	public static class RM_ThirstDefOf
	{
		public static NeedDef RM_Thirst;
		public static HediffDef RM_Dehydration;
		public static ThoughtDef RM_Thought_DrankDistilled;
		public static JobDef RM_DrinkFromTerrain;
		public static JobDef RM_DrinkFromTank;
		public static JobDef RM_DrinkFromFaucet;
		public static JobDef RM_FillAtFaucet;
		public static JobDef RM_AdministerWater;
		public static HediffDef RM_SaltPoisoning;
		public static ThoughtDef RM_Thought_DrankRough;
		public static JobDef RM_DrinkFromContainer;
		public static JobDef RM_DrinkWaterItem;
		public static JobDef RM_GatherSnow;
		public static ThingDef RM_BucketSnow;

		static RM_ThirstDefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RM_ThirstDefOf));
		}
	}

	/// <summary>FlowWorks runs its own thirst only. Dubs Bad Hygiene thirst interop was cut by the owner 2026-10-31
	/// (THIRST_DUBS_EXCISE_WARN_NOT_BRIDGE): About.xml declares full DBH and its Thirst add-on incompatible instead. The
	/// startup log line <c>[FlowWorks] thirst provider: Own (...)</c> stays, so a load proves the thirst came up.</summary>
	[StaticConstructorOnStartup]
	public static class RM_ThirstProvider
	{
		public const string Reason = "FlowWorks' own thirst; Dubs Bad Hygiene thirst is not supported";

		static RM_ThirstProvider()
		{
			Log.Message("[FlowWorks] thirst provider: Own (" + Reason + ")");
		}

		/// <summary>True when our need is live: the setting on.</summary>
		public static bool OursLive => RM_ThirstSettings.thirstEnabled;

		/// <summary>After a settings change: every live pawn re-asks which needs it should have (vanilla adds or removes
		/// RM_Thirst through ShouldHaveNeed, below).</summary>
		public static void Reapply()
		{
			if (Current.Game == null)
			{
				return;
			}
			foreach (Pawn p in PawnsFinder.AllMapsWorldAndTemporary_Alive)
			{
				p.needs?.AddOrRemoveNeedsAsAppropriate();
			}
		}

		private static readonly Dictionary<ThingDef, bool> bodyDrinks = new Dictionary<ThingDef, bool>();

		/// <summary>Design §2 "who gets it": a body with Metabolism or BloodPumping that eats; never a mechanoid, a droid
		/// (they do not eat), an anomaly entity, or a race / active gene carrying RM_ThirstExemptExtension; animals only while
		/// animalsGetThirst is on (ruled ON, OQ-5).</summary>
		public static bool Eligible(Pawn pawn)
		{
			if (pawn?.RaceProps == null || !OursLive)
			{
				return false;
			}
			RaceProperties race = pawn.RaceProps;
			if (race.IsMechanoid || !race.EatsFood || race.IsAnomalyEntity)
			{
				return false;
			}
			if (!race.Humanlike && !RM_ThirstSettings.animalsGetThirst)
			{
				return false;
			}
			if (pawn.def.HasModExtension<RM_ThirstExemptExtension>())
			{
				return false;
			}
			if (pawn.genes != null)
			{
				List<Gene> genes = pawn.genes.GenesListForReading;
				for (int i = 0; i < genes.Count; i++)
				{
					if (genes[i].Active && genes[i].def.HasModExtension<RM_ThirstExemptExtension>())
					{
						return false;
					}
				}
			}
			if (!bodyDrinks.TryGetValue(pawn.def, out bool drinks))
			{
				drinks = race.body != null && (race.body.HasPartWithTag(BodyPartTagDefOf.BloodPumpingSource)
					|| race.body.HasPartWithTag(BodyPartTagDefOf.MetabolismSource));
				bodyDrinks[pawn.def] = drinks;
			}
			return drinks;
		}
	}

	/// <summary>Opt-out by data: put this on a race ThingDef or a GeneDef (by patch) and that pawn never gets RM_Thirst.</summary>
	public class RM_ThirstExemptExtension : DefModExtension
	{
	}

	/// <summary>Design §1 step 2: RM_Thirst exists only where Eligible says so, so it steps aside with the setting off.
	/// Vanilla AddOrRemoveNeedsAsAppropriate then removes it from loaded pawns, so a save survives the switch in either
	/// direction with no dangling def.
	/// Target VERIFIED 2026-10-16 against the decompiled 1.6.4871 Assembly-CSharp
	/// (D:\Luke\dev\reference\rimworld-decompiled\RimWorld\Pawn_NeedsTracker.cs:198):
	/// <c>private bool ShouldHaveNeed(NeedDef nd)</c>, called from <c>public void AddOrRemoveNeedsAsAppropriate()</c>.</summary>
	[HarmonyPatch(typeof(Pawn_NeedsTracker), "ShouldHaveNeed")]
	[RimMandrake.Shared.PatchFeature("Thirst", typeof(RM_ThirstSettings), "thirstEnabled")]
	public static class RM_Patch_ShouldHaveNeed
	{
		public static void Postfix(NeedDef nd, Pawn ___pawn, ref bool __result)
		{
			if (nd != RM_ThirstDefOf.RM_Thirst || !__result)
			{
				return;
			}
			__result = RM_ThirstProvider.Eligible(___pawn);
		}
	}
}
