using System;
using System.Collections.Generic;
using System.Linq;
using BigAndSmall.EventArgs;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public static class RaceMorpher
{
	public const int forcePriority = 9001;

	public const int irremovablePriority = 900;

	public const int withoutSourcePriority = 200;

	public const int hediffPriority = 100;

	public const int genePriority = 0;

	public const int racePriority = -100;

	public const int inactiveGenePriority = -200;

	public static Dictionary<Pawn, List<Hediff>> hediffsToReapply = new Dictionary<Pawn, List<Hediff>>();

	public static bool runningRaceSwap = false;

	public static event EventHandler<AnimalSwappedEventArgs> OnAnimalSwapped;

	public static event EventHandler<DefSwappedEventArgs> OnDefSwapped;

	public static Pawn SwapAnimalToSapientVersion(this Pawn aniPawn)
	{
		//IL_0606: Unknown result type (might be due to invalid IL or missing references)
		//IL_0109: Unknown result type (might be due to invalid IL or missing references)
		//IL_0640: Unknown result type (might be due to invalid IL or missing references)
		//IL_065e: Unknown result type (might be due to invalid IL or missing references)
		//IL_017f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0189: Expected O, but got Unknown
		//IL_018e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0198: Expected O, but got Unknown
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0314: Unknown result type (might be due to invalid IL or missing references)
		//IL_0320: Unknown result type (might be due to invalid IL or missing references)
		//IL_040b: Unknown result type (might be due to invalid IL or missing references)
		//IL_041c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0413: Unknown result type (might be due to invalid IL or missing references)
		//IL_0421: Unknown result type (might be due to invalid IL or missing references)
		//IL_0556: Unknown result type (might be due to invalid IL or missing references)
		//IL_055d: Expected O, but got Unknown
		bool flag = false;
		try
		{
			if (((Thing)aniPawn).def.IsHumanlikeAnimal())
			{
				return null;
			}
			ThingDef val = HumanlikeAnimals.HumanLikeAnimalFor(((Thing)aniPawn).def);
			if (val == null)
			{
				return null;
			}
			if (aniPawn.inventory != null && aniPawn.inventory?.innerContainer != null)
			{
				if (((Thing)aniPawn).Spawned)
				{
					aniPawn.inventory.DropAllNearPawn(((Thing)aniPawn).Position, false, false);
				}
				else
				{
					aniPawn.inventory.DestroyAll((DestroyMode)0);
				}
			}
			bool flag2 = false;
			Pawn val2 = PawnGenerator.GeneratePawn(new PawnGenerationRequest(PawnKindDefOf.Colonist, (Faction)null, (PawnGenerationContext)2, (PlanetTile?)null, true, false, false, false, false, 1f, false, true, false, true, false, false, false, false, false, 0f, 0f, (Pawn)null, 1f, (Predicate<Pawn>)null, (Predicate<Pawn>)null, (IEnumerable<TraitDef>)null, (IEnumerable<TraitDef>)null, (float?)null, (float?)null, (float?)null, (Gender?)null, (string)null, (string)null, (RoyalTitleDef)null, (Ideo)null, false, true, true, false, (List<GeneDef>)null, (List<GeneDef>)null, (XenotypeDef)null, (CustomXenotype)null, (List<XenotypeDef>)null, 2f, (DevelopmentalStage)8, (Func<XenotypeDef, PawnKindDef>)null, (FloatRange?)null, (FloatRange?)null, false, false, false, -1, 0, false));
			val2.inventory.DestroyAll((DestroyMode)0);
			val2.equipment.DestroyAllEquipment((DestroyMode)0);
			val2.apparel.DestroyAll((DestroyMode)0);
			Name name = aniPawn.Name;
			string text = ((name != null) ? name.ToStringShort : null);
			if (text == null)
			{
				val2.Name = PawnBioAndNameGenerator.GeneratePawnName(val2, (NameStyle)0, (string)null, true, (XenotypeDef)null);
			}
			else
			{
				aniPawn.Name = (Name)new NameSingle(aniPawn.Name.ToStringShort + "_Discard", false);
				val2.Name = (Name)new NameSingle(text, false);
			}
			val2.relations.ClearAllRelations();
			val2.story.Adulthood = DefDatabase<BackstoryDef>.GetNamed("Colonist97", true);
			val2.story.Childhood = DefDatabase<BackstoryDef>.GetNamed("TribeChild19", true);
			if (((Thing)aniPawn).Faction == null)
			{
				flag2 = true;
				Pawn_IdeoTracker ideo = val2.ideo;
				if (ideo != null)
				{
					Faction ofPlayerSilentFail = Faction.OfPlayerSilentFail;
					object ideo2;
					if (ofPlayerSilentFail == null)
					{
						ideo2 = null;
					}
					else
					{
						FactionIdeosTracker ideos = ofPlayerSilentFail.ideos;
						ideo2 = ((ideos != null) ? ideos.PrimaryIdeo : null);
					}
					ideo.SetIdeo((Ideo)ideo2);
				}
			}
			else
			{
				Pawn_IdeoTracker ideo3 = val2.ideo;
				if (ideo3 != null)
				{
					FactionIdeosTracker ideos2 = ((Thing)aniPawn).Faction.ideos;
					ideo3.SetIdeo((ideos2 != null) ? ideos2.PrimaryIdeo : null);
				}
				((Thing)val2).SetFaction(((Thing)aniPawn).Faction, (Pawn)null);
			}
			if (ModsConfig.BiotechActive && val2.genes.Xenotype != XenotypeDefOf.Baseliner)
			{
				Log.Message($"[Big and Small] {val2} had a xenotype {((Def)val2.genes.Xenotype).defName} but was supossed to generate as a baseliner." + "Removing xenotype and genes.");
				for (int num = val2.genes.GenesListForReading.Count - 1; num >= 0; num--)
				{
					Gene val3 = val2.genes.GenesListForReading[num];
					val2.genes.RemoveGene(val3);
				}
				val2.genes.SetXenotype(XenotypeDefOf.Baseliner);
				GeneHelpers.ClearCachedGenes(val2);
			}
			CacheAndRemoveHediffs(aniPawn);
			val2.health.hediffSet.hediffs.Clear();
			if (((Thing)aniPawn).Spawned)
			{
				GenSpawn.Spawn((Thing)(object)val2, ((Thing)aniPawn).Position, ((Thing)aniPawn).Map, ((Thing)aniPawn).Rotation, (WipeMode)2, false, false);
			}
			AlternateGraphic val4 = default(AlternateGraphic);
			int value = default(int);
			if (PawnGraphicUtils.TryGetAlternate(aniPawn, ref val4, ref value))
			{
				((Thing)val2).overrideGraphicIndex = value;
			}
			val2.SwapThingDef(val, state: true, 9001, force: true, null, permitFusion: false, clearHediffsToReapply: false);
			RestoreMatchingHediffs(val2, val, aniPawn, new List<string>(2) { "pregnancy", "pregnant" });
			bool isMechanoid = aniPawn.RaceProps.IsMechanoid;
			int ageBiologicalYears = aniPawn.ageTracker.AgeBiologicalYears;
			float num2 = (float)ageBiologicalYears / aniPawn.RaceProps.lifeExpectancy;
			_ = (float)ageBiologicalYears / val2.RaceProps.lifeExpectancy;
			int num3 = Mathf.RoundToInt(num2 * val2.RaceProps.lifeExpectancy);
			int num4 = Mathf.Max(ageBiologicalYears, num3);
			if (isMechanoid && (float)num4 < BS.Settings.minAgeSapientMechs)
			{
				num4 = Mathf.RoundToInt(BS.Settings.minAgeSapientMechs);
			}
			int num5 = Mathf.Max(3, Mathf.Min(13, num4));
			val2.gender = (((int)aniPawn.gender == 0) ? val2.gender : aniPawn.gender);
			val2.ageTracker.AgeChronologicalTicks = aniPawn.ageTracker.AgeChronologicalTicks;
			val2.ageTracker.AgeBiologicalTicks = (long)(val2.RaceProps.lifeExpectancy * num2) * 3600000;
			if (aniPawn.ageTracker.AgeBiologicalYears < num5)
			{
				val2.ageTracker.AgeBiologicalTicks = num5 * 3600000;
			}
			if (flag2)
			{
				if (((Thing)val2).Faction != null)
				{
					((Thing)val2).SetFaction((Faction)null, (Pawn)null);
				}
				val2.ChangeKind(PawnKindDefOf.WildMan);
				val2.jobs.StopAll(false, true);
			}
			if (isMechanoid)
			{
				PawnKindDef kindDef = aniPawn.kindDef;
				if (kindDef != null)
				{
					List<string> weaponTags = kindDef.weaponTags;
					if (((weaponTags != null) ? new bool?(GenCollection.Any<string>(weaponTags)) : ((bool?)null)) == true)
					{
						try
						{
							string weaponTag = aniPawn.kindDef.weaponTags.FirstOrDefault();
							ThingWithComps val5 = (ThingWithComps)ThingMaker.MakeThing((from x in DefDatabase<ThingDef>.AllDefsListForReading
								where x.IsWeapon && (x.weaponTags?.Contains(weaponTag) ?? false)
								orderby x.BaseMarketValue descending
								select x).FirstOrDefault(), (ThingDef)null);
							val2.equipment.AddEquipment(val5);
						}
						catch (Exception ex)
						{
							Log.Error($"[Big and Small] Error trying to equip {val2} with a weapon from {aniPawn.kindDef}:\n{ex.Message}\n{ex.StackTrace}");
						}
					}
				}
			}
			GeneDef hairDef = val2.genes.GetHairColorGene();
			Gene val6 = GenCollection.FirstOrDefault<Gene>(val2.genes.Endogenes, (Predicate<Gene>)((Gene x) => x.def == hairDef));
			if (val6 != null)
			{
				val2.genes.RemoveGene(val6);
			}
			val2.story.HairColor = new Color(0f, 0f, 0f, 0f);
			Color? val7 = aniPawn.ageTracker.CurKindLifeStage?.bodyGraphicData?.color;
			if (val7.HasValue)
			{
				val2.story.HairColor = val7.Value;
			}
			RaceMorpher.OnAnimalSwapped?.Invoke(null, new AnimalSwappedEventArgs(aniPawn, val2));
			((Thing)aniPawn).Destroy((DestroyMode)0);
			flag = true;
			return val2;
		}
		catch (Exception ex2)
		{
			Log.Error($"[Big and Small] Error trying to swap {aniPawn} to a sapient version: {ex2.Message}\n{ex2.StackTrace}");
			return flag ? null : aniPawn;
		}
	}

	/// <summary>
	///
	/// </summary>
	/// <param name="pawn"></param>
	/// <param name="swapTarget"></param>
	/// <param name="state"></param>
	/// <param name="targetPriority"></param>
	/// <param name="force"></param>
	/// <param name="source"></param>
	/// <param name="permitFusion"></param>
	/// <param name="clearHediffsToReapply"></param>
	public static void SwapThingDef(this Pawn pawn, ThingDef swapTarget, bool state, int targetPriority, bool force = false, object source = null, bool permitFusion = true, bool clearHediffsToReapply = true)
	{
		if (swapTarget == null)
		{
			Log.Error($"SwapThingDef called on {pawn} with null swapTarget.");
		}
		else if (pawn == null)
		{
			Log.Error($"SwapThingDef called on a null pawn with swapTarget {swapTarget}.");
		}
		else
		{
			if (runningRaceSwap || pawn?.genes == null || (((Thing)pawn).def == swapTarget && state))
			{
				return;
			}
			MergableBody mergableBody = BodyDefFusionsHelper.MergableBodies.Where((MergableBody x) => x.defaultMechanical).FirstOrDefault();
			if (((Thing)pawn).def == mergableBody.thingDef && swapTarget.IsMechanicalDef())
			{
				force = true;
				permitFusion = false;
				targetPriority = 9001;
			}
			if (clearHediffsToReapply)
			{
				hediffsToReapply.Clear();
			}
			try
			{
				runningRaceSwap = true;
				Pawn_HealthTracker health = pawn.health;
				bool flag = health != null && health.Dead;
				if (force)
				{
					targetPriority = 9001;
				}
				BSCache cache = HumanoidPawnScaler.GetCache(pawn, forceRefresh: false, canRegenerate: false);
				if (force)
				{
					List<HediffDef> list = ((Def)swapTarget).GetModExtension<RaceExtension>()?.RaceHediffs;
					if (list != null)
					{
						foreach (HediffDef item2 in list)
						{
							List<HediffDef> list2 = BodyDefFusionsHelper.GetSubstitutableTrackers(item2).SelectMany((HashSet<HediffDef> x) => x).ToList();
							cache.raceTrackerHistory.RemoveWhere(list2.Contains);
						}
					}
				}
				List<ThingDef> list3 = (from x in pawn.GetAllPawnExtensions(null, new List<Type>(1) { typeof(RaceTracker) })
					where x.thingDefSwap != null
					select x.thingDefSwap).ToList();
				List<ThingDef> list4 = (from x in pawn.GetAllPawnExtensions()
					where x.thingDefSwap != null
					select x.thingDefSwap).ToList();
				List<ThingDef> list5 = (from x in pawn.GetAllPawnExtensions(null, null, doSort: true, includeInactive: true)
					where x.thingDefSwap != null
					select x.thingDefSwap).ToList();
				bool flag2 = false;
				List<(int priority, ThingDef thing)> thingsToTryFusionWith = new List<(int, ThingDef)>();
				List<ThingDef> list6 = ((Thing)pawn).def.GetRaceExtensions()?.Where((RaceExtension x) => x.isFusionOf != null)?.SelectMany((RaceExtension x) => x.isFusionOf).ToList();
				list6 = (GenList.NullOrEmpty<ThingDef>((IList<ThingDef>)list6) ? new List<ThingDef>(1) { ((Thing)pawn).def } : list6);
				bool flag3 = !state && list6.Contains(swapTarget);
				ThingDef val = (state ? swapTarget : ThingDefOf.Human);
				if (!flag3)
				{
					list6.Remove(swapTarget);
					foreach (var (val2, source2) in list6.Select((ThingDef x) => (x: x, (from x in x.ExtensionsOnDef<RaceExtension, ThingDef>((List<Type>)null, (List<Type>)null, doSort: true)?.SelectMany((RaceExtension x) => x.RaceHediffs)
						where x != null
						select x).ToList())))
					{
						if (IsDiscardable(val2))
						{
							continue;
						}
						List<CompProperties_Race> list7 = source2.SelectMany((HediffDef x) => from x in x.comps
							select x as CompProperties_Race into x
							where x != null
							select x).ToList();
						int item = 200;
						if (GenCollection.Any<ThingDef>(list3, (Predicate<ThingDef>)((ThingDef x) => x == ((Thing)pawn).def)))
						{
							item = 100;
						}
						else if (GenCollection.Any<ThingDef>(list4, (Predicate<ThingDef>)((ThingDef x) => x == ((Thing)pawn).def)))
						{
							item = 0;
						}
						else if (!IsDiscardable(val2) && GenCollection.Any<CompProperties_Race>(list7, (Predicate<CompProperties_Race>)((CompProperties_Race x) => !x.canSwapAwayFrom)))
						{
							item = 900;
						}
						thingsToTryFusionWith.Add((item, val2));
					}
				}
				if (state)
				{
					thingsToTryFusionWith.Add((targetPriority, swapTarget));
				}
				if (!state && flag3)
				{
					bool flag4 = false;
					if (list3.Count > 0)
					{
						thingsToTryFusionWith.AddRange(list3.Select((ThingDef x) => (hediffPriority: 100, x: x)));
						flag4 = true;
					}
					if (list4.Count > 0)
					{
						thingsToTryFusionWith.AddRange(list4.Select((ThingDef x) => (genePriority: 0, x: x)));
						flag4 = true;
					}
					if (list5.Count > 0)
					{
						thingsToTryFusionWith.AddRange(list4.Select((ThingDef x) => (inactiveGenePriority: -200, x: x)));
						flag4 = true;
					}
					if (!flag4)
					{
						ThingDef val3 = ThingDefOf.Human;
						if (cache.isMechanical && mergableBody != null && mergableBody?.thingDef != swapTarget)
						{
							val3 = mergableBody.thingDef;
						}
						if (cache.originalThing != ((Thing)pawn).def && cache.originalThing != ThingDefOf.Human)
						{
							val3 = cache.originalThing;
						}
						if (val3 == null || val3 == swapTarget)
						{
							val3 = ThingDefOf.Human;
							cache.originalThing = ThingDefOf.Human;
						}
						if (val3 != ThingDefOf.Human)
						{
							thingsToTryFusionWith.Add((-100, val3));
						}
					}
				}
				if (permitFusion)
				{
					thingsToTryFusionWith.AddRange(list3.Select((ThingDef x) => (hediffPriority: 100, x: x)));
					thingsToTryFusionWith.AddRange(from x in list4
						where x != swapTarget
						select (genePriority: 0, x: x));
					thingsToTryFusionWith.AddRange(from x in list5
						where x != swapTarget
						select (inactiveGenePriority: -200, x: x));
					int idx;
					for (idx = thingsToTryFusionWith.Count - 1; idx >= 0; idx--)
					{
						if (GenCollection.Count<(int, ThingDef)>(thingsToTryFusionWith, (Predicate<(int, ThingDef)>)(((int priority, ThingDef thing) x) => x.thing == thingsToTryFusionWith[idx].thing)) > 1)
						{
							thingsToTryFusionWith.RemoveAt(idx);
						}
					}
					thingsToTryFusionWith = thingsToTryFusionWith.OrderByDescending(((int priority, ThingDef thing) x) => x.priority).ToList();
					List<BodyDef> list8 = thingsToTryFusionWith.Select(((int priority, ThingDef thing) x) => x.thing.race.body).ToList();
					if (!state)
					{
						thingsToTryFusionWith.RemoveAll(((int priority, ThingDef thing) x) => x.thing == swapTarget);
					}
					while (list8.Count > 0)
					{
						FusedBody fusedBody = FusedBody.TryGetBody(cache.isMechanical, list8.ToArray());
						if (fusedBody != null)
						{
							val = fusedBody.Thing;
							break;
						}
						BodyDef nonFusedBody = FusedBody.TryGetNonFused(list8.ToArray());
						if (nonFusedBody != null)
						{
							(int, ThingDef) tuple2 = GenCollection.FirstOrDefault<(int, ThingDef)>(thingsToTryFusionWith, (Predicate<(int, ThingDef)>)(((int priority, ThingDef thing) x) => x.thing.race.body == nonFusedBody));
							if (tuple2.Item2 != null)
							{
								val = tuple2.Item2;
								break;
							}
						}
						list8.RemoveAt(list8.Count - 1);
						if (list8.Count == 1)
						{
							val = thingsToTryFusionWith[0].thing;
						}
					}
				}
				if (((Def)((Thing)pawn).def).defName != ((Def)val).defName)
				{
					flag2 = ExecuteDefSwap(cache, val);
				}
				if (flag2)
				{
					((Thing)(object)pawn).RecacheStatsForThing();
					pawn.VerbTracker.InitVerbsFromZero();
					if (pawn.health.Dead && !flag)
					{
						Log.WarningOnce($"[DEBUG] {pawn} was dead after def swap to {val}. Attempting to resurrect.", 921378231);
						ResurrectionUtility.TryResurrect(pawn, (ResurrectionParams)null);
						pawn.VerbTracker.InitVerbsFromZero();
					}
					cache.RefreshOwnerId(pawn);
				}
			}
			catch (Exception ex)
			{
				Log.Message($"Error trying to in SwapThingDef of {pawn} to {swapTarget} (if this happend during world gen it is likely harmless):\n{ex.Message}\n{ex.StackTrace}");
			}
			finally
			{
				runningRaceSwap = false;
				HumanoidPawnScaler.GetCache(pawn, forceRefresh: true);
				foreach (StatModifier statBasis in ((BuildableDef)((Thing)pawn).def).statBases)
				{
					statBasis.stat.Worker.ClearCacheForThing((Thing)(object)pawn);
				}
			}
		}
		static bool IsDiscardable(ThingDef def)
		{
			if (def != ThingDefOf.Human)
			{
				return def == ThingDefOf.CreepJoiner;
			}
			return true;
		}
	}

	private static bool ExecuteDefSwap(BSCache cache, ThingDef swapTarget)
	{
		Pawn pawn = cache.pawn;
		if (((Thing)(pawn?)).def == null)
		{
			return false;
		}
		if (((Thing)pawn).def == swapTarget)
		{
			return false;
		}
		bool flag = false;
		Map map = ((Thing)pawn).Map;
		if (!hediffsToReapply.ContainsKey(pawn))
		{
			hediffsToReapply[pawn] = new List<Hediff>();
		}
		try
		{
			if (map != null)
			{
				RegionListersUpdater.DeregisterInRegions((Thing)(object)pawn, map);
			}
		}
		catch (Exception ex)
		{
			Log.Message("Error when deregistering in regions: " + ex.Message);
		}
		try
		{
			if (map != null && map.listerThings.Contains((Thing)(object)pawn))
			{
				map.listerThings.Remove((Thing)(object)pawn);
				flag = true;
			}
		}
		catch (Exception ex2)
		{
			Log.Message("Error when removing from listers: " + ex2.Message);
		}
		int ageBiologicalYears = pawn.ageTracker.AgeBiologicalYears;
		RaceExtension.RemoveOldRaceTrackers(pawn);
		CacheAndRemoveHediffs(pawn);
		Type type = ((object)((Thing)pawn).def).GetType();
		((Thing)pawn).def = swapTarget;
		((Thing)(object)pawn).RecacheStatsForThing();
		if (!((object)((Thing)pawn).def).GetType().Name.Contains("ThingDef_AlienRace"))
		{
			for (int num = ((ThingWithComps)pawn).AllComps.Count - 1; num >= 0; num--)
			{
				if (((object)((ThingWithComps)pawn).AllComps[num]).GetType().Name.Contains("AlienComp"))
				{
					Log.WarningOnce("[Big and Small] " + ((Def)((Thing)pawn).def).defName + " Swapped to an AlienRace with an AlienComp. This is somewhat untested.", 929972331);
				}
			}
		}
		else if (type != ((object)((Thing)pawn).def).GetType())
		{
			((object)((Thing)pawn).def).GetType().Name.Contains("ThingDef_AlienRace");
		}
		int num2 = -1;
		List<LifeStageAge> lifeStageAges = pawn.RaceProps.lifeStageAges;
		for (int num3 = lifeStageAges.Count - 1; num3 >= 0; num3--)
		{
			if (lifeStageAges[num3].minAge <= (float)ageBiologicalYears + 1E-06f)
			{
				num2 = num3;
				break;
			}
		}
		AccessTools.FieldRefAccess<Pawn_AgeTracker, int>("cachedLifeStageIndex").Invoke(pawn.ageTracker) = num2;
		try
		{
			if (map != null && (flag || ((Thing)pawn).Spawned) && !map.listerThings.Contains((Thing)(object)pawn))
			{
				map.listerThings.Add((Thing)(object)pawn);
			}
		}
		catch (Exception ex3)
		{
			Log.Message("Error when restoring to listers: " + ex3.Message);
		}
		try
		{
			if (map != null)
			{
				RegionListersUpdater.RegisterInRegions((Thing)(object)pawn, ((Thing)pawn).Map);
			}
		}
		catch (Exception ex4)
		{
			Log.Message("Error when registering in regions: " + ex4.Message);
		}
		RestoreMatchingHediffs(pawn, ((Thing)pawn).def);
		(((Thing)pawn).def.GetRaceExtensions()?.FirstOrDefault())?.ApplyTrackerIfMissing(pawn, cache);
		if (pawn?.needs != null)
		{
			pawn.needs.AddOrRemoveNeedsAsAppropriate();
		}
		try
		{
			AddMissingComps(pawn);
		}
		catch (Exception ex5)
		{
			Log.Error($"[Big and Small] Error trying to add missing comps to {pawn}: {ex5.Message}\n{ex5.StackTrace}");
		}
		return true;
	}

	public static void CacheAndRemoveHediffs(Pawn pawn)
	{
		List<Hediff> list = pawn.health.hediffSet.hediffs.ToList();
		hediffsToReapply[pawn] = list.ToList();
		foreach (Hediff item in list)
		{
			pawn.health.hediffSet.hediffs.Remove(item);
		}
	}

	public static void RestoreMatchingHediffs(Pawn pawn, ThingDef targetThingDef, Pawn source = null, List<string> blacklist = null)
	{
		List<BodyPartRecord> list = targetThingDef.race.body.AllParts.Select((BodyPartRecord x) => x).ToList();
		if (source == null)
		{
			source = pawn;
		}
		if (blacklist == null)
		{
			blacklist = new List<string>();
		}
		if (hediffsToReapply[source].Count <= 0)
		{
			return;
		}
		for (int num = hediffsToReapply[source].Count - 1; num >= 0; num--)
		{
			Hediff hediff = hediffsToReapply[source][num];
			if (!GenCollection.Any<string>(blacklist, (Predicate<string>)((string x) => x.Equals(((Def)hediff.def).defName, StringComparison.OrdinalIgnoreCase))))
			{
				_ = hediff.Severity;
				if (hediff.Part == null || GenCollection.Any<BodyPartRecord>(list, (Predicate<BodyPartRecord>)((BodyPartRecord x) => ((Def)x.def).defName == ((Def)hediff.Part.def).defName || x.customLabel == hediff.Part.customLabel)))
				{
					try
					{
						if (!(hediff is Hediff_ChemicalDependency))
						{
							if (hediff.Part == null)
							{
								hediff.pawn = pawn;
								pawn.health.hediffSet.hediffs.Add(hediff);
							}
							else
							{
								BodyPartRecord val = GenCollection.FirstOrDefault<BodyPartRecord>(list, (Predicate<BodyPartRecord>)((BodyPartRecord x) => ((Def)x.def).defName == ((Def)hediff.Part.def).defName && x.customLabel == hediff.Part.customLabel));
								BodyPartRecord val2 = GenCollection.FirstOrDefault<BodyPartRecord>(list, (Predicate<BodyPartRecord>)((BodyPartRecord x) => ((Def)x.def).defName == ((Def)hediff.Part.def).defName && x.Label == hediff.Part.Label));
								BodyPartRecord val3 = GenCollection.FirstOrDefault<BodyPartRecord>(list, (Predicate<BodyPartRecord>)((BodyPartRecord x) => ((Def)x.def).defName == ((Def)hediff.Part.def).defName));
								BodyPartRecord val4 = val ?? val2 ?? val3;
								if (val4 != null)
								{
									try
									{
										pawn.health.hediffSet.hediffs.Add(hediff);
										hediff.Part = val4;
										hediff.pawn = pawn;
									}
									catch (Exception ex)
									{
										Log.Warning($"Failed to add/transfer {((Def)hediff.def).defName} to {pawn.Name} on {((Def)val4.def).defName}.\n{ex.Message}");
									}
								}
							}
						}
					}
					catch
					{
					}
					finally
					{
						hediffsToReapply[source].RemoveAt(num);
					}
				}
			}
		}
		pawn.health.hediffSet.DirtyCache();
		for (int i = 0; i < pawn.health.hediffSet.hediffs.Count; i++)
		{
			if (pawn.health.hediffSet.hediffs.Count > i)
			{
				pawn.health.Notify_HediffChanged(pawn.health.hediffSet.hediffs[i]);
			}
		}
		foreach (Gene_ChemicalDependency item in (from x in GeneHelpers.GetAllActiveEndoGenes(pawn)
			where x is Gene_ChemicalDependency
			select x).Select((Func<Gene, Gene_ChemicalDependency>)((Gene x) => (Gene_ChemicalDependency)x)).ToList())
		{
			RestoreDependencies(pawn, item, xenoGene: false);
		}
		foreach (Gene_ChemicalDependency item2 in (from x in GeneHelpers.GetAllActiveXenoGenes(pawn)
			where x is Gene_ChemicalDependency
			select x).Select((Func<Gene, Gene_ChemicalDependency>)((Gene x) => (Gene_ChemicalDependency)x)).ToList())
		{
			RestoreDependencies(pawn, item2, xenoGene: true);
		}
	}

	private static void AddMissingComps(Pawn pawn)
	{
		//IL_00f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f8: Expected O, but got Unknown
		ThingDef def = ((Thing)pawn).def;
		if (!GenCollection.Any<CompProperties>(def.comps))
		{
			return;
		}
		List<ThingComp> list = ((ThingWithComps)pawn).AllComps.ToList();
		List<CompProperties> list2 = def.comps.ToList();
		for (int num = list.Count - 1; num >= 0; num--)
		{
			ThingComp comp = list[num];
			if (comp == null)
			{
				Log.Warning($"Found a null comp on {pawn} ({((Def)(((Thing)(pawn?)).def?)).defName})");
			}
			else if (comp.props != null)
			{
				CompProperties val = GenCollection.FirstOrDefault<CompProperties>(list2, (Predicate<CompProperties>)((CompProperties x) => x.compClass != null && x != null && ((object)comp.props).GetType() == ((object)x).GetType() && x.compClass == ((object)comp).GetType()));
				if (val != null)
				{
					list2.Remove(val);
				}
				else
				{
					((ThingWithComps)pawn).AllComps.Remove(comp);
				}
			}
		}
		for (int i = 0; i < list2.Count; i++)
		{
			CompProperties val2 = list2[i];
			ThingComp val3 = null;
			try
			{
				val3 = (ThingComp)Activator.CreateInstance(val2.compClass);
				val3.parent = (ThingWithComps)(object)pawn;
				((ThingWithComps)pawn).AllComps.Add(val3);
				val3.Initialize(val2);
			}
			catch (Exception arg)
			{
				Log.Error($"Could not instantiate or initialize a ThingComp: {arg}");
				if (val3 != null)
				{
					((ThingWithComps)pawn).AllComps.Remove(val3);
				}
			}
		}
	}

	private static void RestoreDependencies(Pawn pawn, Gene_ChemicalDependency chemGene, bool xenoGene)
	{
		int lastIngestedTick = chemGene.lastIngestedTick;
		GeneDef def = ((Gene)chemGene).def;
		pawn.genes.RemoveGene((Gene)(object)chemGene);
		if (def != null)
		{
			pawn.genes.AddGene(def, xenoGene);
		}
		chemGene.lastIngestedTick = lastIngestedTick;
	}
}
