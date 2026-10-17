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
		public static JobDef RM_AdministerWater;
		public static HediffDef RM_SaltPoisoning;

		static RM_ThirstDefOf()
		{
			DefOfHelper.EnsureInitializedInCtor(typeof(RM_ThirstDefOf));
		}
	}

	/// <summary>Design §1 step 1: which ONE thirst need runs, resolved once at startup and written to the log once:
	/// <c>[FlowWorks] thirst provider: Own|Dbh (reason)</c>. Dbh when DBH's NeedDef <c>DBHThirst</c> loaded AND the Thirst
	/// add-on (<c>Dubwise.DubsBadHygiene.Thirst</c>) or full DBH (<c>Dubwise.DubsBadHygiene</c>) is active (packageIds and the
	/// defName read from the workshop files 2570319432 / 2582878800 / 836308268, 2026-10-16). Corner case (design §1): DBH
	/// loaded with its own thirst switched off in DBH's settings may still leave DBHThirst loaded with no pawn holding it;
	/// then there is no thirst at all, which is DBH's choice. Whether DBH drops the def in that case is UNMEASURED (live T1).</summary>
	[StaticConstructorOnStartup]
	public static class RM_ThirstProvider
	{
		public const string DbhThirstNeed = "DBHThirst";
		public const string DbhThirstAddon = "Dubwise.DubsBadHygiene.Thirst";
		public const string DbhFull = "Dubwise.DubsBadHygiene";

		private static bool resolved;
		private static RM_ThirstProviderMode mode;
		private static string reason = "not resolved yet";

		static RM_ThirstProvider()
		{
			Resolve();
		}

		public static RM_ThirstProviderMode Mode
		{
			get
			{
				if (!resolved)
				{
					Resolve();
				}
				return mode;
			}
		}

		public static bool Own => Mode == RM_ThirstProviderMode.Own;

		/// <summary>True when our need is live: Own mode and the setting on.</summary>
		public static bool OursLive => Own && RM_ThirstSettings.thirstEnabled;

		public static string Reason => reason;

		public static string ModeLabel => (resolved ? mode.ToString() : "?") + " (" + reason + ")";

		private static void Resolve()
		{
			bool need = DefDatabase<NeedDef>.GetNamedSilentFail(DbhThirstNeed) != null;
			mode = RM_ThirstMath.ProviderMode(need, ModsConfig.IsActive(DbhThirstAddon), ModsConfig.IsActive(DbhFull), out reason);
			resolved = true;
			Log.Message("[FlowWorks] thirst provider: " + mode + " (" + reason + ")");
		}

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

	/// <summary>Design §1 step 2: RM_Thirst exists only where Eligible says so, so it steps aside in Dbh mode and with the
	/// setting off. Vanilla AddOrRemoveNeedsAsAppropriate then removes it from loaded pawns, so a save survives DBH being
	/// added or removed in either direction with no dangling def.
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
