using System.Collections.Generic;
using System.Linq;
using RimWorld;
using VEF.CacheClearing;
using Verse;

namespace VEF.AnimalBehaviours;

[StaticConstructorOnStartup]
public static class StaticCollectionsClass
{
	public static List<ThingDef> riverAnimals;

	public static HashSet<Thing> draftable_animals;

	public static HashSet<Thing> canEquipWeapon_animals;

	public static HashSet<Thing> floating_animals;

	public static HashSet<Thing> waterstriding_pawns;

	public static HashSet<Thing> nofleeing_animals;

	public static HashSet<Thing> abilityUsing_animals;

	public static HashSet<Thing> nofilth_animals;

	public static HashSet<Thing> nodisease_animals;

	public static HashSet<Thing> weirdEaters_animals;

	public static HashSet<ThingDef> notamingdecay_animals;

	public static IDictionary<Thing, float> lastStand_animals;

	[NoCacheClearing]
	public static HashSet<PawnKindDef> questDisabledAnimals;

	public static int numberOfAnimalControlHubsBuilt;

	public static bool IsDraftableAnimal(this Pawn pawn)
	{
		return draftable_animals.Contains((Thing)(object)pawn);
	}

	public static bool IsAbilityUserAnimal(this Pawn pawn)
	{
		if (abilityUsing_animals.Contains((Thing)(object)pawn))
		{
			Faction faction = ((Thing)pawn).Faction;
			if (faction != null && faction.IsPlayer)
			{
				return pawn.MentalState == null;
			}
		}
		return false;
	}

	public static bool IsLastStandAnimal(this Pawn pawn)
	{
		return lastStand_animals.ContainsKey((Thing)(object)pawn);
	}

	public static float LastStandAnimalRate(this Pawn pawn)
	{
		return lastStand_animals[(Thing)(object)pawn];
	}

	public static bool TryGetLastStandAnimalRate(this Pawn pawn, out float rate)
	{
		return lastStand_animals.TryGetValue((Thing)(object)pawn, out rate);
	}

	public static bool IsDraftableControllableAnimal(this Pawn pawn)
	{
		if (pawn.IsDraftableAnimal() && ((Thing)pawn).Faction != null && ((Thing)pawn).Faction.IsPlayer)
		{
			return pawn.MentalState == null;
		}
		return false;
	}

	public static void AddDraftableAnimalToList(Thing thing)
	{
		if (!draftable_animals.Contains(thing))
		{
			draftable_animals.Add(thing);
		}
	}

	public static void RemoveDraftableAnimalFromList(Thing thing)
	{
		if (draftable_animals.Contains(thing))
		{
			draftable_animals.Remove(thing);
		}
	}

	public static void AddCanEquipWeaponsAnimalToList(Thing thing)
	{
		if (!canEquipWeapon_animals.Contains(thing))
		{
			canEquipWeapon_animals.Add(thing);
		}
	}

	public static void RemoveCanEquipWeaponsAnimalFromList(Thing thing)
	{
		if (canEquipWeapon_animals.Contains(thing))
		{
			canEquipWeapon_animals.Remove(thing);
		}
	}

	public static void AddLastStandAnimalToList(Thing thing, float rate)
	{
		if (!lastStand_animals.ContainsKey(thing))
		{
			lastStand_animals.Add(thing, rate);
		}
	}

	public static void RemoveLastStandAnimalFromList(Thing thing)
	{
		if (lastStand_animals.ContainsKey(thing))
		{
			lastStand_animals.Remove(thing);
		}
	}

	public static void AddAbilityUsingAnimalToList(Thing thing)
	{
		if (!abilityUsing_animals.Contains(thing))
		{
			abilityUsing_animals.Add(thing);
		}
	}

	public static void RemoveAbilityUsingFromList(Thing thing)
	{
		if (abilityUsing_animals.Contains(thing))
		{
			abilityUsing_animals.Remove(thing);
		}
	}

	public static void AddNoDiseasesAnimalToList(Thing thing)
	{
		if (!nodisease_animals.Contains(thing))
		{
			nodisease_animals.Add(thing);
		}
	}

	public static void RemoveNoDiseasesAnimalFromList(Thing thing)
	{
		if (nodisease_animals.Contains(thing))
		{
			nodisease_animals.Remove(thing);
		}
	}

	public static void AddFloatingAnimalToList(Thing thing)
	{
		if (!floating_animals.Contains(thing))
		{
			floating_animals.Add(thing);
		}
	}

	public static void RemoveFloatingAnimalFromList(Thing thing)
	{
		if (floating_animals.Contains(thing))
		{
			floating_animals.Remove(thing);
		}
	}

	public static void AddWaterstridingPawnToList(Thing thing)
	{
		if (!waterstriding_pawns.Contains(thing))
		{
			waterstriding_pawns.Add(thing);
		}
	}

	public static void RemoveWaterstridingPawnFromList(Thing thing)
	{
		if (waterstriding_pawns.Contains(thing))
		{
			waterstriding_pawns.Remove(thing);
		}
	}

	public static void AddNoTamingDecayAnimalToList(ThingDef thing)
	{
		if (!notamingdecay_animals.Contains(thing))
		{
			notamingdecay_animals.Add(thing);
		}
	}

	public static void RemoveNoTamingDecayAnimalFromList(ThingDef thing)
	{
		if (notamingdecay_animals.Contains(thing))
		{
			notamingdecay_animals.Remove(thing);
		}
	}

	public static bool IsNoTamingDecayAnimal(this ThingDef pawn)
	{
		return notamingdecay_animals.Contains(pawn);
	}

	public static void AddNoFilthAnimalToList(Thing thing)
	{
		if (!nofilth_animals.Contains(thing))
		{
			nofilth_animals.Add(thing);
		}
	}

	public static void RemoveNoFilthAnimalFromList(Thing thing)
	{
		if (nofilth_animals.Contains(thing))
		{
			nofilth_animals.Remove(thing);
		}
	}

	public static void AddNotFleeingAnimalToList(Thing thing)
	{
		if (!nofleeing_animals.Contains(thing))
		{
			nofleeing_animals.Add(thing);
		}
	}

	public static void RemoveNotFleeingAnimalFromList(Thing thing)
	{
		if (nofleeing_animals.Contains(thing))
		{
			nofleeing_animals.Remove(thing);
		}
	}

	public static void AddWeirdEaterAnimalToList(Thing thing)
	{
		if (!weirdEaters_animals.Contains(thing))
		{
			weirdEaters_animals.Add(thing);
		}
	}

	public static void RemoveWeirdEaterAnimalFromList(Thing thing)
	{
		if (weirdEaters_animals.Contains(thing))
		{
			weirdEaters_animals.Remove(thing);
		}
	}

	public static void AddControlHubBuilt()
	{
		numberOfAnimalControlHubsBuilt++;
	}

	public static void RemoveControlHubBuilt()
	{
		if (numberOfAnimalControlHubsBuilt > 0)
		{
			numberOfAnimalControlHubsBuilt--;
		}
	}

	static StaticCollectionsClass()
	{
		riverAnimals = new List<ThingDef>();
		draftable_animals = new HashSet<Thing>();
		canEquipWeapon_animals = new HashSet<Thing>();
		floating_animals = new HashSet<Thing>();
		waterstriding_pawns = new HashSet<Thing>();
		nofleeing_animals = new HashSet<Thing>();
		abilityUsing_animals = new HashSet<Thing>();
		nofilth_animals = new HashSet<Thing>();
		nodisease_animals = new HashSet<Thing>();
		weirdEaters_animals = new HashSet<Thing>();
		notamingdecay_animals = new HashSet<ThingDef>();
		lastStand_animals = new Dictionary<Thing, float>();
		questDisabledAnimals = new HashSet<PawnKindDef>();
		numberOfAnimalControlHubsBuilt = 0;
		ClearCaches.clearCacheTypes.Add(typeof(StaticCollectionsClass));
		foreach (AnimalsDisabledFromQuestsDef item in DefDatabase<AnimalsDisabledFromQuestsDef>.AllDefsListForReading.ToHashSet())
		{
			GenCollection.AddRange<PawnKindDef>(questDisabledAnimals, item.disabledFromQuestsPawns);
		}
		foreach (RiverNeedingAnimalDef item2 in DefDatabase<RiverNeedingAnimalDef>.AllDefsListForReading)
		{
			foreach (ThingDef riverNeedingAnimal in item2.riverNeedingAnimals)
			{
				riverAnimals.Add(riverNeedingAnimal);
			}
		}
	}
}
