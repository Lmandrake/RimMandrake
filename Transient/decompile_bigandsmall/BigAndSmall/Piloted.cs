using System;
using System.Collections.Generic;
using System.Linq;
using BigAndSmall.Utilities;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public class Piloted : HediffWithComps, IThingHolder
{
	private static bool forcePilotableUpdate = false;

	public bool removeIfNoPilot;

	public bool defaultEnterable = true;

	private CompProperties_Piloted props;

	protected ThingOwner innerContainer;

	private int startPilotTime;

	protected Ideo cachedIdeology;

	protected Faction cachedFaction;

	protected Name cachedName;

	protected XenotypeDef cachedXenotype;

	public static readonly List<string> PhysicalTraitList = new List<string>(8) { "speedoffset", "beauty", "gigantism", "large", "small", "dwarfism", "bs_giant", "tough" };

	/// <summary>
	/// To avoid recursion from setting it in a method that will trigger a refresh hitting that very same method.
	/// </summary>
	private float severity = 0.1f;

	public List<PawnCapacityModifier> cachedCapMods = new List<PawnCapacityModifier>();

	private int pilotEjectCountdown = -1;

	private static readonly int tickRate = 550;

	public CompProperties_Piloted Props => GetProperties();

	public float BaseCapacity => Props.baseCapacity;

	public IThingHolder ParentHolder => (IThingHolder)(object)((Hediff)this).pawn;

	public int PilotCapacity => Props.pilotCapacity;

	public int PilotCount => ((IEnumerable<Thing>)innerContainer).Where((Thing x) => x is Pawn).Count();

	public float TotalMass => ((IEnumerable<Thing>)innerContainer).Where((Thing x) => x is Pawn).Sum((Thing x) => ((Pawn)x).BodySize) + ((IEnumerable<Thing>)innerContainer).Where((Thing x) => x is Corpse).Sum((Thing x) => ((Corpse)x).InnerPawn.BodySize);

	public float Fullness => TotalMass / ((Hediff)this).pawn.BodySize;

	public float MaxCapacity => BaseCapacity * (((Hediff)this).pawn.BodySize + (GenCollection.Any<Trait>(((Hediff)this).pawn.story.traits.allTraits, (Predicate<Trait>)((Trait x) => ((Def)x.def).defName == "VFEP_WarcasketTrait_Mech")) ? 1.05f : 0f));

	public ThingOwner InnerContainer
	{
		get
		{
			if (innerContainer == null)
			{
				innerContainer = (ThingOwner)(object)new ThingOwner<Thing>((IThingHolder)(object)this, false, (LookMode)2, true);
			}
			return innerContainer;
		}
		set
		{
			innerContainer = value;
		}
	}

	public override string LabelInBrackets
	{
		get
		{
			//IL_0056: Unknown result type (might be due to invalid IL or missing references)
			//IL_0060: Unknown result type (might be due to invalid IL or missing references)
			//IL_0070: Unknown result type (might be due to invalid IL or missing references)
			//IL_0046: Unknown result type (might be due to invalid IL or missing references)
			Thing obj = ((IEnumerable<Thing>)InnerContainer).Where((Thing x) => x is Pawn).FirstOrDefault();
			Pawn val = (Pawn)(object)((obj is Pawn) ? obj : null);
			if (val != null)
			{
				if (pilotEjectCountdown != -1)
				{
					return TaggedString.op_Implicit(Translator.Translate("BS_PilotEjectCoutndown"));
				}
				return TaggedString.op_Implicit(Translator.Translate("BS_PilotedBy") + " " + val.Name.ToStringShort);
			}
			return ((HediffWithComps)this).LabelInBrackets;
		}
	}

	public CompProperties_Piloted GetProperties()
	{
		if (props != null)
		{
			return props;
		}
		if (!(base.comps.Where((HediffComp x) => x is PilotedCompProps).FirstOrDefault() is PilotedCompProps pilotedCompProps))
		{
			Log.Error("BS_Piloted: No PilotedCompProps found on hediff " + ((Def)((Hediff)this).def).defName);
			return null;
		}
		props = pilotedCompProps.Props;
		return props;
	}

	public void GetChildHolders(List<IThingHolder> outChildren)
	{
		ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, (IList<Thing>)GetDirectlyHeldThings());
	}

	public ThingOwner GetDirectlyHeldThings()
	{
		return InnerContainer;
	}

	public override void PostAdd(DamageInfo? dinfo)
	{
		((HediffWithComps)this).PostAdd(dinfo);
	}

	public void AddPilot(Thing thing)
	{
		try
		{
			if (((Hediff)this).pawn == null)
			{
				Log.Warning("BS_Piloted: Pilotable entity was null");
			}
			if (thing == null)
			{
				Log.Warning($"BS_Piloted: Tried to add null pilot to {((Hediff)this).pawn.Name}.");
			}
			if (InnerContainer == null)
			{
				Log.Warning($"BS_Piloted: InnerContainer was null for {((Hediff)this).pawn.Name}.");
			}
			thing.DeSpawnOrDeselect((DestroyMode)0);
			if (thing.holdingOwner != null)
			{
				if (thing.holdingOwner.TryTransferToContainer(thing, InnerContainer, thing.stackCount, true) == 0)
				{
					Log.Warning($"Failed to transfer pilot to piloted hediff of {((Hediff)this).pawn.Name}.");
				}
			}
			else if (!InnerContainer.TryAdd(thing, true))
			{
				Log.Warning($"Failed to add pilot to piloted hediff of {((Hediff)this).pawn.Name}.");
			}
		}
		catch (Exception ex)
		{
			Log.Warning("Failed to add pilot to piloted hediff." + ex.Message + "\n" + ex.StackTrace);
		}
		try
		{
			if (Props.removeIfNoPilot)
			{
				removeIfNoPilot = true;
			}
			if (((IEnumerable<Thing>)InnerContainer).Where((Thing x) => x is Pawn && x != thing).FirstOrDefault() == null)
			{
				Thing obj = thing;
				Pawn val = (Pawn)(object)((obj is Pawn) ? obj : null);
				if (val != null)
				{
					Pawn_GuestTracker guest = ((Hediff)this).pawn.guest;
					if (guest != null)
					{
						guest.SetGuestStatus((Faction)null, (GuestStatus)0);
					}
					if (ModsConfig.IdeologyActive && Props.temporarilySwapIdeology && val.Ideo != null)
					{
						cachedIdeology = ((Hediff)this).pawn.Ideo;
						((Hediff)this).pawn.ideo.SetIdeo(val.Ideo);
					}
					if (Props.temporarilySwapFaction && ((Thing)val).Faction != null)
					{
						((Hediff)this).pawn.health.overrideDeathOnDownedChance = ((((Hediff)this).pawn.health.overrideDeathOnDownedChance > 0f) ? (((Hediff)this).pawn.health.overrideDeathOnDownedChance / 2f) : (Find.Storyteller.difficulty.enemyDeathOnDownedChanceFactor / 2f));
						cachedFaction = ((Thing)((Hediff)this).pawn).Faction;
						((Thing)((Hediff)this).pawn).SetFaction(((Thing)val).Faction, (Pawn)null);
					}
					if (Props.temporarilySwapName)
					{
						cachedName = ((Hediff)this).pawn.Name;
						((Hediff)this).pawn.Name = val.Name;
					}
					cachedXenotype = ((Hediff)this).pawn.genes.Xenotype;
					try
					{
						InheritPilotSkills(val, ((Hediff)this).pawn);
					}
					catch (Exception ex2)
					{
						Log.Warning("Failed to transfer pilot skills:\n" + ex2.Message + "\n" + ex2.StackTrace);
					}
					try
					{
						InheritPilotTraits(val);
					}
					catch (Exception ex3)
					{
						Log.Warning("Failed to transfer pilot traits:\n" + ex3.Message + "\n" + ex3.StackTrace);
					}
					try
					{
						InheritRelationships(val, ((Hediff)this).pawn);
					}
					catch (Exception ex4)
					{
						Log.Warning("Failed to transfer pilot relationships:\n" + ex4.Message + "\n" + ex4.StackTrace);
					}
					try
					{
						ApplyXenotypeToTargetOnApply(((Hediff)this).pawn);
					}
					catch (Exception ex5)
					{
						Log.Warning("Failed to apply xenotype:\n" + ex5.Message + "\n" + ex5.StackTrace);
					}
					try
					{
						ApplyHediffs(((Hediff)this).pawn);
					}
					catch (Exception ex6)
					{
						Log.Warning("Failed to apply hediffs:\n" + ex6.Message + "\n" + ex6.StackTrace);
					}
					startPilotTime = Find.TickManager.TicksGame;
				}
			}
		}
		catch (Exception ex7)
		{
			Log.Warning("Failed to transfer all pilot properties to pilotable: " + ex7.Message + ex7.StackTrace);
		}
		forcePilotableUpdate = true;
		((Hediff)this).pawn.health.Notify_HediffChanged((Hediff)(object)this);
	}

	public void ApplyXenotypeToTargetOnApply(Pawn target)
	{
		if (Props.xenotypeToApplyOnApply != null)
		{
			target.genes.SetXenotype(Props.xenotypeToApplyOnApply);
		}
	}

	public void ApplyHediffs(Pawn target)
	{
		if (GenList.NullOrEmpty<HediffChance>((IList<HediffChance>)Props.hediffsToApplyOnEnter) || ((Hediff)this).pawn.Dead || GenList.NullOrEmpty<HediffChance>((IList<HediffChance>)Props.hediffsToApplyOnEnter))
		{
			return;
		}
		foreach (HediffChance item in Props.hediffsToApplyOnEnter)
		{
			if (Rand.Chance(item.chance))
			{
				((Hediff)this).pawn.health.AddHediff(item.hediff, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
		}
	}

	public void InheritRelationships(Pawn pilot, Pawn target)
	{
		//IL_0574: Unknown result type (might be due to invalid IL or missing references)
		//IL_057e: Expected O, but got Unknown
		if (pilot == null || target == null)
		{
			return;
		}
		if (((Thing)pilot).Faction != null && ((Thing)pilot).Faction != ((Thing)target).Faction)
		{
			((Thing)target).SetFaction(((Thing)pilot).Faction, (Pawn)null);
		}
		if (pilot.Ideo != null)
		{
			target.ideo.SetIdeo(pilot.Ideo);
		}
		if (!Props.inheritRelationShips)
		{
			return;
		}
		target.guest.resistance = pilot.guest.resistance;
		target.guest.will = pilot.guest.will;
		Pawn_RelationsTracker relations = pilot.relations;
		List<DirectPawnRelation> list = ((relations != null) ? relations.DirectRelations.ToList() : null);
		Pawn_NeedsTracker needs = pilot.needs;
		object obj;
		if (needs == null)
		{
			obj = null;
		}
		else
		{
			Need_Mood mood = needs.mood;
			if (mood == null)
			{
				obj = null;
			}
			else
			{
				ThoughtHandler thoughts = mood.thoughts;
				if (thoughts == null)
				{
					obj = null;
				}
				else
				{
					MemoryThoughtHandler memories = thoughts.memories;
					obj = ((memories == null) ? null : memories.Memories?.ToList());
				}
			}
		}
		List<Thought_Memory> list2 = (List<Thought_Memory>)obj;
		Pawn_RelationsTracker relations2 = target.relations;
		if (relations2 != null)
		{
			relations2.ClearAllRelations();
		}
		Pawn_NeedsTracker needs2 = target.needs;
		if (needs2 != null)
		{
			Need_Mood mood2 = needs2.mood;
			if (mood2 != null)
			{
				ThoughtHandler thoughts2 = mood2.thoughts;
				if (thoughts2 != null)
				{
					MemoryThoughtHandler memories2 = thoughts2.memories;
					if (memories2 != null)
					{
						memories2.Memories?.Clear();
					}
				}
			}
		}
		Pawn_NeedsTracker needs3 = target.needs;
		if (needs3 != null)
		{
			Need_Mood mood3 = needs3.mood;
			if (mood3 != null)
			{
				ThoughtHandler thoughts3 = mood3.thoughts;
				if (thoughts3 != null)
				{
					SituationalThoughtHandler situational = thoughts3.situational;
					if (situational != null)
					{
						situational.Notify_SituationalThoughtsDirty();
					}
				}
			}
		}
		List<Pawn> first = Find.WorldPawns.AllPawnsAliveOrDead.ToList();
		first = first.Concat(Find.Maps.SelectMany((Map x) => x.mapPawns.AllPawns)).Distinct().ToList();
		if (list2 != null)
		{
			foreach (Thought_Memory item in list2)
			{
				if (item.otherPawn != null)
				{
					first.Add(item.otherPawn);
				}
			}
		}
		Dictionary<DirectPawnRelation, Pawn> dictionary = new Dictionary<DirectPawnRelation, Pawn>();
		foreach (Pawn item2 in first)
		{
			if (item2 == pilot)
			{
				continue;
			}
			Pawn_RelationsTracker relations3 = item2.relations;
			List<DirectPawnRelation> list3 = ((relations3 == null) ? null : relations3.DirectRelations?.ToList());
			if (list3 == null)
			{
				continue;
			}
			try
			{
				foreach (DirectPawnRelation item3 in list3)
				{
					if (item3?.otherPawn != null && item3.otherPawn == pilot)
					{
						dictionary.Add(item3, item2);
					}
				}
			}
			catch (Exception ex)
			{
				Log.Error($"Failed to fetch relations to pilot {pilot.Name} from {item2.Name} with error: \n{ex.Message}\n{ex.StackTrace}");
			}
		}
		for (int num = list.Count - 1; num >= 0; num--)
		{
			DirectPawnRelation val = list[num];
			try
			{
				Pawn_RelationsTracker relations4 = target.relations;
				if (relations4 != null && !relations4.DirectRelationExists(val.def, val.otherPawn) && target != null)
				{
					Pawn_RelationsTracker relations5 = target.relations;
					if (relations5 != null)
					{
						relations5.AddDirectRelation(val.def, val.otherPawn);
					}
				}
			}
			catch (Exception ex2)
			{
				Log.Error($"Failed to add relation {((Def)val.def).defName} to {target.Name} from {pilot.Name} with error: \n{ex2.Message}\n{ex2.StackTrace}");
			}
		}
		foreach (KeyValuePair<DirectPawnRelation, Pawn> item4 in dictionary)
		{
			Pawn value = item4.Value;
			PawnRelationDef def = item4.Key.def;
			try
			{
				value.relations.AddDirectRelation(def, target);
			}
			catch (Exception ex3)
			{
				Log.Error($"Failed to add relation {((Def)def).defName} to {value.Name} from {target.Name} with error: \n{ex3.Message}\n{ex3.StackTrace}");
			}
		}
		for (int num2 = list2.Count - 1; num2 >= 0; num2--)
		{
			Thought_Memory val2 = list2[num2];
			try
			{
				Thought_Memory val3 = ThoughtMaker.MakeThought(((Thought)val2).def, ((Thought)val2).sourcePrecept);
				val3.CopyFrom(val2);
				((Thought)val2).pawn = target;
				target.needs.mood.thoughts.memories.TryGainMemory(val3, val2.otherPawn);
			}
			catch (Exception ex4)
			{
				Log.Error($"Failed to add thought {((Def)((Thought)val2).def).defName} to {target.Name} from {pilot.Name} with error: \n{ex4.Message}\n{ex4.StackTrace}");
			}
		}
		if (((Hediff)this).pawn.needs?.mood?.thoughts != null)
		{
			Pawn pawn = ((Hediff)this).pawn;
			if (pawn != null)
			{
				Pawn_NeedsTracker needs4 = pawn.needs;
				if (needs4 != null)
				{
					Need_Mood mood4 = needs4.mood;
					if (mood4 != null)
					{
						ThoughtHandler thoughts4 = mood4.thoughts;
						if (thoughts4 != null)
						{
							SituationalThoughtHandler situational2 = thoughts4.situational;
							if (situational2 != null)
							{
								situational2.Notify_SituationalThoughtsDirty();
							}
						}
					}
				}
			}
		}
		if (ModsConfig.RoyaltyActive)
		{
			target.royalty = new Pawn_RoyaltyTracker(((Hediff)this).pawn);
			Pawn_RoyaltyTracker royalty = pilot.royalty;
			List<RoyalTitle> list4 = ((royalty != null) ? royalty.AllTitlesForReading : null);
			if (list4 != null)
			{
				foreach (RoyalTitle item5 in list4)
				{
					Pawn_RoyaltyTracker royalty2 = target.royalty;
					if (royalty2 != null)
					{
						royalty2.SetTitle(item5.faction, item5.def, false, false, false);
					}
					Pawn pawn2 = ((Hediff)this).pawn;
					int? obj2;
					if (pawn2 == null)
					{
						obj2 = null;
					}
					else
					{
						Pawn_RoyaltyTracker royalty3 = pawn2.royalty;
						obj2 = ((royalty3 != null) ? new int?(royalty3.GetFavor(item5.faction)) : ((int?)null));
					}
					int? num3 = obj2;
					if (num3.HasValue)
					{
						int valueOrDefault = num3.GetValueOrDefault();
						target.royalty.SetFavor(item5.faction, valueOrDefault, true);
					}
				}
			}
		}
		Pawn_RelationsTracker relations6 = pilot.relations;
		if (relations6 != null)
		{
			relations6.ClearAllRelations();
		}
		Pawn_NeedsTracker needs5 = pilot.needs;
		if (needs5 != null)
		{
			Need_Mood mood5 = needs5.mood;
			if (mood5 != null)
			{
				ThoughtHandler thoughts5 = mood5.thoughts;
				if (thoughts5 != null)
				{
					MemoryThoughtHandler memories3 = thoughts5.memories;
					if (memories3 != null)
					{
						memories3.Memories?.Clear();
					}
				}
			}
		}
		Pawn_NeedsTracker needs6 = pilot.needs;
		if (needs6 != null)
		{
			Need_Mood mood6 = needs6.mood;
			if (mood6 != null)
			{
				ThoughtHandler thoughts6 = mood6.thoughts;
				if (thoughts6 != null)
				{
					SituationalThoughtHandler situational3 = thoughts6.situational;
					if (situational3 != null)
					{
						situational3.Notify_SituationalThoughtsDirty();
					}
				}
			}
		}
		Pawn_NeedsTracker needs7 = target.needs;
		if (needs7 == null)
		{
			return;
		}
		Need_Mood mood7 = needs7.mood;
		if (mood7 == null)
		{
			return;
		}
		ThoughtHandler thoughts7 = mood7.thoughts;
		if (thoughts7 != null)
		{
			SituationalThoughtHandler situational4 = thoughts7.situational;
			if (situational4 != null)
			{
				situational4.Notify_SituationalThoughtsDirty();
			}
		}
	}

	public void InheritPilotSkills(Pawn source, Pawn target)
	{
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		if (Props.inheritPilotSkills)
		{
			List<SkillRecord> skills = source.skills.skills;
			List<SkillRecord> skills2 = target.skills.skills;
			for (int i = 0; i < skills.Count; i++)
			{
				SkillRecord val = skills[i];
				SkillRecord obj = skills2[i];
				obj.levelInt = val.levelInt;
				obj.passion = val.passion;
				obj.xpSinceLastLevel = val.xpSinceLastLevel;
				obj.xpSinceMidnight = val.xpSinceMidnight;
			}
		}
	}

	public void InheritPilotTraits(Pawn pilot)
	{
		if (!Props.inheritPilotMentalTraits)
		{
			return;
		}
		foreach (Trait item in ((Hediff)this).pawn.story.traits.allTraits.Where((Trait x) => !GenCollection.Any<string>(PhysicalTraitList, (Predicate<string>)((string y) => ((Def)x.def).defName.ToLower().StartsWith(y)))).ToList())
		{
			((Hediff)this).pawn.story.traits.allTraits.Remove(item);
		}
		foreach (Trait item2 in pilot.story.traits.allTraits.Where((Trait x) => !GenCollection.Any<string>(PhysicalTraitList, (Predicate<string>)((string y) => ((Def)x.def).defName.ToLower().StartsWith(y)))).ToList())
		{
			((Hediff)this).pawn.story.traits.GainTrait(item2, false);
		}
	}

	public void InheritTargetTraits(Pawn pilot)
	{
		if (!Props.pilotInheritMentalTraitsOnRemove)
		{
			return;
		}
		foreach (Trait item in ((Hediff)this).pawn.story.traits.allTraits.Where((Trait x) => !GenCollection.Any<string>(PhysicalTraitList, (Predicate<string>)((string y) => ((Def)x.def).defName.ToLower().StartsWith(y)))).ToList())
		{
			pilot.story.traits.GainTrait(item, false);
		}
	}

	public static void TryEjectFromPawn(Thing thing, Pawn parentPawn)
	{
		//IL_000a: Unknown result type (might be due to invalid IL or missing references)
		if (((Thing)parentPawn).MapHeld != null)
		{
			GenPlace.TryPlaceThing(thing, ((Thing)parentPawn).Position, ((Thing)parentPawn).MapHeld, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
			return;
		}
		if (CaravanUtility.IsCaravanMember(parentPawn))
		{
			Caravan caravan = CaravanUtility.GetCaravan((Thing)(object)parentPawn);
			if (caravan != null)
			{
				caravan.AddPawnOrItem(thing, true);
				return;
			}
		}
		if (!thing.Spawned)
		{
			Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
			if (val != null)
			{
				Find.WorldPawns.PassToWorld(val, (PawnDiscardDecideMode)0);
			}
		}
	}

	public void RemovePilots(bool mayRemoveHediff = true)
	{
		//IL_02ad: Unknown result type (might be due to invalid IL or missing references)
		//IL_0448: Unknown result type (might be due to invalid IL or missing references)
		IList<Thing> list = (IList<Thing>)InnerContainer;
		if (list.Count == 0)
		{
			return;
		}
		using (IEnumerator<Thing> enumerator = list.Where((Thing x) => x is Pawn).GetEnumerator())
		{
			if (enumerator.MoveNext())
			{
				Thing current = enumerator.Current;
				try
				{
					InheritPilotSkills(((Hediff)this).pawn, (Pawn)(object)((current is Pawn) ? current : null));
				}
				catch (Exception ex)
				{
					Log.Error($"Failed to inherit skills from {((Hediff)this).pawn.Name} with error:\n{ex.Message}\n{ex.StackTrace}");
				}
				try
				{
					InheritRelationships(((Hediff)this).pawn, (Pawn)(object)((current is Pawn) ? current : null));
				}
				catch (Exception ex2)
				{
					Log.Error($"Failed to inherit relationships from {((Hediff)this).pawn.Name} with error:\n{ex2.Message}\n{ex2.StackTrace}");
				}
				try
				{
					InheritTargetTraits((Pawn)(object)((current is Pawn) ? current : null));
				}
				catch (Exception ex3)
				{
					Log.Error($"Failed to have pilot inherit traits from {((Hediff)this).pawn.Name} with error:\n{ex3.Message}\n{ex3.StackTrace}");
				}
			}
		}
		for (int num = list.Count - 1; num >= 0; num--)
		{
			Thing thing = list[num];
			TryLearnSkill(thing);
			TryEjectFromPawn(thing, ((Hediff)this).pawn);
		}
		if (!((Hediff)this).pawn.Dead && Props.temporarilySwapIdeology && cachedIdeology != null)
		{
			((Hediff)this).pawn.ideo.SetIdeo(cachedIdeology);
			cachedIdeology = null;
		}
		if (!ThingUtility.DestroyedOrNull((Thing)(object)((Hediff)this).pawn) && Props.temporarilySwapFaction && cachedFaction != null)
		{
			((Thing)((Hediff)this).pawn).SetFaction(cachedFaction, (Pawn)null);
			cachedFaction = null;
		}
		if (!ThingUtility.DestroyedOrNull((Thing)(object)((Hediff)this).pawn) && Props.restoreXenotypeOnRemove && cachedXenotype != null)
		{
			((Hediff)this).pawn.genes.SetXenotype(cachedXenotype);
		}
		cachedXenotype = null;
		if (!ThingUtility.DestroyedOrNull((Thing)(object)((Hediff)this).pawn) && Props.xenotypeToApplyOnRemove != null)
		{
			((Hediff)this).pawn.genes.SetXenotype(Props.xenotypeToApplyOnRemove);
		}
		if (Props.temporarilySwapName && cachedName != null)
		{
			((Hediff)this).pawn.Name = cachedName;
			cachedName = null;
		}
		if (!((Hediff)this).pawn.Dead && Props.killOnRemove)
		{
			DamageInfo value = default(DamageInfo);
			((DamageInfo)(ref value))._002Ector(DamageDefOf.ExecutionCut, 10000f, 300f, -1f, (Thing)null, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false);
			((Thing)((Hediff)this).pawn).Kill((DamageInfo?)value, (Hediff)(object)this);
		}
		if (!((Hediff)this).pawn.Dead && !GenList.NullOrEmpty<HediffChance>((IList<HediffChance>)Props.hediffsToApplyOnRemove))
		{
			foreach (HediffChance item in Props.hediffsToApplyOnRemove)
			{
				if (Rand.Chance(item.chance))
				{
					((Hediff)this).pawn.health.AddHediff(item.hediff, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				}
			}
		}
		pilotEjectCountdown = -1;
		((Hediff)this).pawn.health.Notify_HediffChanged((Hediff)(object)this);
		forcePilotableUpdate = true;
		if (!mayRemoveHediff || !removeIfNoPilot)
		{
			return;
		}
		Pawn pawn = ((Hediff)this).pawn;
		if (pawn == null)
		{
			return;
		}
		Pawn_HealthTracker health = pawn.health;
		bool? obj;
		if (health == null)
		{
			obj = null;
		}
		else
		{
			HediffSet hediffSet = health.hediffSet;
			obj = ((hediffSet != null) ? new bool?(hediffSet.HasHediff(((Hediff)this).def, false)) : ((bool?)null));
		}
		bool? flag = obj;
		if (flag != true)
		{
			return;
		}
		try
		{
			if (!((Hediff)this).pawn.Dead)
			{
				int? injuryOnRemoval = props.injuryOnRemoval;
				if (injuryOnRemoval.HasValue)
				{
					int valueOrDefault = injuryOnRemoval.GetValueOrDefault();
					if (valueOrDefault > 0)
					{
						BodyPartRecord corePart = ((Hediff)this).pawn.RaceProps.body.corePart;
						if (corePart != null)
						{
							DamageInfo val = default(DamageInfo);
							((DamageInfo)(ref val))._002Ector(DamageDefOf.Cut, (float)valueOrDefault * ((Hediff)this).pawn.BodySize, 300f, -1f, (Thing)null, corePart, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false);
							((Thing)((Hediff)this).pawn).TakeDamage(val);
						}
					}
				}
			}
		}
		catch (Exception ex4)
		{
			Log.Error($"Failed to apply removal injury to {((Hediff)this).pawn.Name} with error:\n{ex4.Message}\n{ex4.StackTrace}");
		}
		((Hediff)this).pawn.health.RemoveHediff((Hediff)(object)this);
	}

	private void TryLearnSkill(Thing thing)
	{
		//IL_019b: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d0: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ec: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f1: Unknown result type (might be due to invalid IL or missing references)
		Pawn val = (Pawn)(object)((thing is Pawn) ? thing : null);
		if (val == null)
		{
			return;
		}
		float? pilotLearnSkills = Props.pilotLearnSkills;
		if (!pilotLearnSkills.HasValue)
		{
			return;
		}
		float valueOrDefault = pilotLearnSkills.GetValueOrDefault();
		if (val?.skills?.skills == null || ((Hediff)this).pawn?.skills?.skills == null)
		{
			return;
		}
		try
		{
			float num = (float)(Find.TickManager.TicksGame - startPilotTime) / 60000f * valueOrDefault / 40f;
			float statValue = StatExtension.GetStatValue((Thing)(object)val, StatDefOf.GlobalLearningFactor, true, -1);
			foreach (SkillRecord skill in val.skills.skills)
			{
				foreach (SkillRecord skill2 in ((Hediff)this).pawn.skills.skills)
				{
					if (skill2.def != skill.def)
					{
						continue;
					}
					float num2 = skill2.XpTotalEarned - skill.XpTotalEarned;
					if (num2 > 0f)
					{
						float num3 = num2 * num;
						if (num2 < 4000f)
						{
							num3 *= 0.2f;
						}
						else if (num2 < 6000f)
						{
							num3 *= 0.35f;
						}
						else if (num2 < 8000f)
						{
							num3 *= 0.5f;
						}
						else if (num2 < 12000f)
						{
							num3 *= 0.75f;
						}
						num3 = Mathf.Min(num3, num2 / statValue);
						skill.Learn(num3, false, false);
						if (num3 > 4000f)
						{
							NamedArgument val2 = NamedArgument.op_Implicit(val.Name.ToStringShort);
							NamedArgument val3 = NamedArgument.op_Implicit($"{num3:f0}");
							NamedArgument val4 = NamedArgument.op_Implicit(((Def)(skill2?.def?)).label);
							Name name = ((Hediff)this).pawn.Name;
							Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_GainedSkillFromPawnAmount", val2, val3, val4, NamedArgument.op_Implicit((name != null) ? name.ToStringShort : null))), LookTargets.op_Implicit((Thing)(object)((Hediff)this).pawn), MessageTypeDefOf.PositiveEvent, true);
						}
					}
					break;
				}
			}
		}
		catch (Exception ex)
		{
			Log.Error($"Failed to transfer learned skills from {((Hediff)this).pawn.Name} to {val.Name} with error:\n{ex.Message}\n{ex.StackTrace}");
		}
	}

	public override void PostRemoved()
	{
		try
		{
			((HediffWithComps)this).PostRemoved();
			RemovePilots(mayRemoveHediff: false);
		}
		catch (Exception ex)
		{
			Log.Error($"Failed to remove pilot from {((Hediff)this).pawn.Name} with error:\n{ex.Message}\n{ex.StackTrace}");
		}
	}

	public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
	{
	}

	public float CalculateConsciousnessOffset()
	{
		Thing obj = ((IEnumerable<Thing>)InnerContainer).FirstOrDefault();
		Pawn val = (Pawn)(object)((obj is Pawn) ? obj : null);
		if (val != null)
		{
			return (val.health.capacities.GetLevel(PawnCapacityDefOf.Consciousness) - 1f) * Props.pilotConsciousnessOffset + Props.flatBonusIfPiloted;
		}
		return 0f;
	}

	public bool HasNoPilotAndRequiresPilot()
	{
		Thing val = ((IEnumerable<Thing>)InnerContainer).FirstOrDefault();
		if (val == null || !(val is Pawn))
		{
			severity = 0.1f;
			if (Props.pilotRequired)
			{
				return true;
			}
		}
		else
		{
			severity = 1f;
		}
		return false;
	}

	[HarmonyPatch(/*Could not decode attribute arguments.*/)]
	[HarmonyPostfix]
	public static void CapMods_Postfix(Hediff __instance, ref List<PawnCapacityModifier> __result)
	{
		//IL_0070: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_0081: Expected O, but got Unknown
		if (!(__instance is Piloted piloted))
		{
			return;
		}
		IEnumerable<PawnCapacityModifier> collection = __result.Where((PawnCapacityModifier x) => x.capacity != PawnCapacityDefOf.Consciousness);
		if (!forcePilotableUpdate)
		{
			if (Find.TickManager.TicksGame % tickRate != 0 && piloted.cachedCapMods.Count() > 0)
			{
				__result = piloted.cachedCapMods;
				forcePilotableUpdate = false;
				return;
			}
		}
		else
		{
			forcePilotableUpdate = false;
		}
		PawnCapacityModifier val = new PawnCapacityModifier
		{
			capacity = PawnCapacityDefOf.Consciousness
		};
		if (piloted.HasNoPilotAndRequiresPilot())
		{
			val.setMax = 0.01f;
		}
		val.offset = piloted.CalculateConsciousnessOffset();
		List<PawnCapacityModifier> list = new List<PawnCapacityModifier>();
		list.Add(val);
		list.AddRange(collection);
		__result = list;
		piloted.cachedCapMods = __result;
	}

	public override void Tick()
	{
		((Hediff)this).Tick();
		if (Find.TickManager.TicksGame % tickRate != 0 && !forcePilotableUpdate)
		{
			return;
		}
		if (((IEnumerable<Thing>)InnerContainer).Count() > 0)
		{
			Need_Food food = ((Hediff)this).pawn.needs.food;
			((Need)food).CurLevel = ((Need)food).CurLevel - ((Hediff)this).pawn.needs.food.FoodFallPerTick * (float)tickRate * 0.5f;
		}
		if (((Hediff)this).Severity != severity)
		{
			((Hediff)this).Severity = severity;
			((Hediff)this).pawn.health.Notify_HediffChanged((Hediff)(object)this);
		}
		if (PilotCount > 0 && ((Hediff)this).pawn.Downed && (Props.canAutoEjectIfColonist || !((Hediff)this).pawn.IsColonist))
		{
			if (pilotEjectCountdown == -1)
			{
				pilotEjectCountdown = 2;
				return;
			}
			pilotEjectCountdown--;
			if (pilotEjectCountdown == 0)
			{
				pilotEjectCountdown = -1;
				RemovePilots();
			}
		}
		else
		{
			pilotEjectCountdown = -1;
		}
	}

	public override void ExposeData()
	{
		((HediffWithComps)this).ExposeData();
		forcePilotableUpdate = true;
		Scribe_Deep.Look<ThingOwner>(ref innerContainer, "innerContainer", new object[1] { this });
		Scribe_Values.Look<bool>(ref removeIfNoPilot, "removeIfNoPilot", false, false);
		Scribe_Values.Look<bool>(ref defaultEnterable, "defaultEnterable", true, false);
		Scribe_References.Look<Faction>(ref cachedFaction, "cachedFaction", false);
		Scribe_References.Look<Ideo>(ref cachedIdeology, "cachedIdeology", false);
		Scribe_Defs.Look<XenotypeDef>(ref cachedXenotype, "cachedXenotype");
		Scribe_Values.Look<int>(ref startPilotTime, "timeSpentPiloting", 0, false);
	}
}
