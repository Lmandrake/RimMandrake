using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse.AI;
using Verse;

namespace RimMandrake.RustCathedral.Hum
{
	// RUSTCATHEDRAL_BASE_FINISH_BUILD_1 part 2 -- hum reading. Sheet §7: "learnable, tradeable knowledge: reading the
	// tones and the bolts' dances tells you what no instrument can". No stat buff anywhere: the whole payoff is one
	// plain-words line on an inspect pane.
	//
	// ⛔ Ban 1: the readout names a band and a figure, never what either means or who is behind them.
	public static class RM_HumReading
	{
		public const string TraitDefName = "RM_HumReader";

		public const string CathedralBiomeDefName = "RM_RustCathedral";

		/// <summary>Cells within which a hum reader standing near a bolt off the plateau can read it.</summary>
		public const float NearRadius = 10f;

		private static TraitDef traitDef;

		public static TraitDef Trait => traitDef ?? (traitDef = DefDatabase<TraitDef>.GetNamedSilentFail(TraitDefName));

		public static bool IsReader(Pawn p)
		{
			TraitDef t = Trait;
			return t != null && p?.story?.traits != null && p.story.traits.HasTrait(t);
		}

		/// <summary>Plain words for a band, calmest first. Band 4 is the silent worst band.</summary>
		public static string BandWord(int band)
		{
			switch (band)
			{
				case 0: return "calm";
				case 1: return "uneasy";
				case 2: return "sharp";
				case 3: return "alarmed";
				default: return band >= 4 ? "silent" : "";
			}
		}

		/// <summary>What the bolts are doing at a band, in what a watcher sees and nothing more.</summary>
		public static string FigureWords(int band)
		{
			switch (band)
			{
				case 0: return "dancing wide loops";
				case 1: return "dancing tight figures";
				case 2: return "walking stiff lines";
				case 3: return "barely stirring";
				default: return band >= 4 ? "standing frozen" : "";
			}
		}

		public static string Line(int band)
		{
			if (band < 0)
			{
				return "";
			}
			return "The hum: " + BandWord(band) + ". The bolts: " + FigureWords(band) + ".";
		}

		public static bool AnyReaderOn(Map map)
		{
			if (map == null)
			{
				return false;
			}
			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < pawns.Count; i++)
			{
				if (IsReader(pawns[i]) && !pawns[i].Dead)
				{
					return true;
				}
			}
			return false;
		}

		/// <summary>The attitude readout for a map: the plain-words band line while a hum reader is on it, else "".</summary>
		public static string Readout(Map map)
		{
			if (!RustCathedralHumSettings.humMechanicEnabled || !AnyReaderOn(map))
			{
				return "";
			}
			return Line(RM_MapComponent_BiomeAttitude.GetBand(map));
		}

		/// <summary>The line on a bolt's inspect pane. On the Cathedral it is the map's readout; anywhere else a reader
		/// within NearRadius of the bolt hears what the Cathedral is doing (the bolts carry it).</summary>
		public static string ReadoutFor(Thing bolt)
		{
			Map map = bolt?.MapHeld;
			if (map == null || !RustCathedralHumSettings.humMechanicEnabled)
			{
				return "";
			}
			if (map.Biome != null && map.Biome.defName == CathedralBiomeDefName)
			{
				return Readout(map);
			}
			bool near = false;
			IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
			for (int i = 0; i < pawns.Count && !near; i++)
			{
				near = IsReader(pawns[i]) && pawns[i].Position.InHorDistOf(bolt.PositionHeld, NearRadius);
			}
			if (!near)
			{
				return "";
			}
			foreach (Map other in Find.Maps)
			{
				if (other.Biome != null && other.Biome.defName == CathedralBiomeDefName)
				{
					return Line(RM_MapComponent_BiomeAttitude.GetBand(other));
				}
			}
			return "";
		}

		public static bool GrantTrait(Pawn p, bool letter)
		{
			TraitDef t = Trait;
			if (t == null || p?.story?.traits == null || IsReader(p))
			{
				return false;
			}
			p.story.traits.GainTrait(new Trait(t, 0, forced: true));
			if (letter && PawnUtility.ShouldSendNotificationAbout(p))
			{
				Find.LetterStack.ReceiveLetter("Hears the plate: " + p.LabelShort,
					p.LabelShort + " has listened under the plate long enough to tell one tone from another.",
					LetterDefOf.PositiveEvent, p);
			}
			return true;
		}
	}

	/// <summary>Exposure tally: hours each colonist spends on Cathedral ground while the hum shows a calm band
	/// (0 or 1). Kept per game, not per map, so the total carries across visits.</summary>
	public class RM_GameComponent_HumExposure : GameComponent
	{
		public const int IntervalTicks = GenDate.TicksPerHour;

		public const int CalmBandCeiling = 1;

		private Dictionary<string, int> hours = new Dictionary<string, int>();

		public RM_GameComponent_HumExposure(Game game)
		{
		}

		public override void ExposeData()
		{
			base.ExposeData();
			Scribe_Collections.Look(ref hours, "hours", LookMode.Value, LookMode.Value);
			if (hours == null)
			{
				hours = new Dictionary<string, int>();
			}
		}

		public static int ThresholdHours => Mathf.Max(1, Mathf.RoundToInt(RustCathedralHumSettings.humReaderThresholdDays * 24f));

		public int HoursFor(Pawn p)
		{
			return p != null && hours.TryGetValue(p.GetUniqueLoadID(), out int h) ? h : 0;
		}

		public override void GameComponentTick()
		{
			if (Find.TickManager.TicksGame % IntervalTicks != 0)
			{
				return;
			}
			if (!RustCathedralHumSettings.humMechanicEnabled || !RustCathedralHumSettings.humReadingEnabled)
			{
				return;
			}
			foreach (Map map in Find.Maps)
			{
				TickMap(map, 1);
			}
		}

		/// <summary>Adds `add` hours to every eligible colonist on this map; grants the trait at the threshold.
		/// Returns the number of colonists credited. Public so a proof can drive it without waiting game hours.</summary>
		public int TickMap(Map map, int add)
		{
			if (map?.Biome == null || map.Biome.defName != RM_HumReading.CathedralBiomeDefName)
			{
				return 0;
			}
			int band = RM_MapComponent_BiomeAttitude.GetBand(map);
			if (band < 0 || band > CalmBandCeiling)
			{
				return 0;
			}
			int credited = 0;
			List<Pawn> colonists = map.mapPawns.FreeColonistsSpawned;
			for (int i = 0; i < colonists.Count; i++)
			{
				Pawn p = colonists[i];
				if (RM_HumReading.IsReader(p))
				{
					continue;
				}
				string key = p.GetUniqueLoadID();
				hours.TryGetValue(key, out int h);
				h += add;
				hours[key] = h;
				credited++;
				if (h >= ThresholdHours)
				{
					RM_HumReading.GrantTrait(p, letter: true);
				}
			}
			return credited;
		}

		public static RM_GameComponent_HumExposure Get()
		{
			return Current.Game?.GetComponent<RM_GameComponent_HumExposure>();
		}
	}

	public class CompProperties_HumReadout : CompProperties
	{
		public CompProperties_HumReadout()
		{
			compClass = typeof(RM_CompHumReadout);
		}
	}

	/// <summary>On the living bolts: the plain-words readout appears on the bolt's inspect pane for a hum reader.</summary>
	public class RM_CompHumReadout : ThingComp
	{
		public override string CompInspectStringExtra()
		{
			string s = RM_HumReading.ReadoutFor(parent);
			return s.NullOrEmpty() ? null : s;
		}
	}

	// ---- the primer: a vanilla 1.6 book that teaches the trait to whoever reads it through ----

	public class BookOutcomeProperties_HumPrimer : BookOutcomeProperties
	{
		/// <summary>Reading ticks a pawn needs on this book. PROVISIONAL: 15000 ticks, about six in-game hours.</summary>
		public int readingTicksToLearn = 15000;

		public override System.Type DoerClass => typeof(BookOutcomeDoer_HumPrimer);
	}

	public class BookOutcomeDoer_HumPrimer : BookOutcomeDoer
	{
		private Dictionary<string, float> progress = new Dictionary<string, float>();

		public new BookOutcomeProperties_HumPrimer Props => (BookOutcomeProperties_HumPrimer)props;

		public override bool DoesProvidesOutcome(Pawn reader)
		{
			return reader != null && RM_HumReading.Trait != null && !RM_HumReading.IsReader(reader);
		}

		public override string GetBenefitsString(Pawn reader = null)
		{
			return " - Teaches its reader to tell one tone under the plate from another.";
		}

		public override void OnReadingTick(Pawn reader, float factor)
		{
			if (!DoesProvidesOutcome(reader))
			{
				return;
			}
			string key = reader.GetUniqueLoadID();
			progress.TryGetValue(key, out float done);
			// factor = reading speed x room bonus x ticks since the last call (Book.OnBookReadTick)
			done += Mathf.Max(0f, factor);
			progress[key] = done;
			if (done >= Props.readingTicksToLearn)
			{
				RM_HumReading.GrantTrait(reader, letter: true);
			}
		}

		/// <summary>Proof hook: what a pawn has read of this copy, in ticks.</summary>
		public float ProgressFor(Pawn p)
		{
			return p != null && progress.TryGetValue(p.GetUniqueLoadID(), out float v) ? v : 0f;
		}

		public override void PostExposeData()
		{
			Scribe_Collections.Look(ref progress, "humPrimerProgress", LookMode.Value, LookMode.Value);
			if (progress == null)
			{
				progress = new Dictionary<string, float>();
			}
		}
	}

	/// <summary>On a RecipeDef: only a pawn carrying this trait may start the bill.</summary>
	public class RM_RecipeRequiresTraitExtension : DefModExtension
	{
		public TraitDef trait;
	}

	[HarmonyPatch(typeof(Bill), nameof(Bill.PawnAllowedToStartAnew))]
	public static class HarmonyPatch_HumPrimer_BillNeedsTrait
	{
		public static void Postfix(Bill __instance, Pawn p, ref bool __result)
		{
			if (!__result || __instance?.recipe == null)
			{
				return;
			}
			RM_RecipeRequiresTraitExtension ext = __instance.recipe.GetModExtension<RM_RecipeRequiresTraitExtension>();
			if (ext?.trait == null)
			{
				return;
			}
			if (p?.story?.traits == null || !p.story.traits.HasTrait(ext.trait))
			{
				JobFailReason.Is("Needs someone who can read the hum.");
				__result = false;
			}
		}
	}

	// ---- part 3's tie-in: butchering a living coolant eel is a catch, priced exactly as a fished one ----

	[HarmonyPatch(typeof(Corpse), nameof(Corpse.ButcherProducts))]
	public static class HarmonyPatch_CoolantEel_ButcherIsACatch
	{
		public const string EelRaceDefName = "RM_CoolantEel";

		public static void Prefix(Corpse __instance, Pawn butcher)
		{
			if (__instance?.InnerPawn?.def?.defName != EelRaceDefName)
			{
				return;
			}
			RM_CathedralFishing.NoteCatch(butcher?.MapHeld ?? __instance.MapHeld, 1f);
		}
	}
}
