using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.Sound;

namespace VEF.Buildings;

public class LootableBuilding : Building, IOpenable
{
	private LootableBuildingDetails contentDetails;

	public int OpenTicks => 300;

	public bool CanOpen
	{
		get
		{
			GetDetails();
			if (contentDetails?.requiredMod != "")
			{
				return ModLister.HasActiveModWithName(contentDetails?.requiredMod);
			}
			return true;
		}
	}

	public LootableBuildingDetails GetDetails()
	{
		if (contentDetails == null)
		{
			contentDetails = ((Def)((Thing)this).def).GetModExtension<LootableBuildingDetails>();
		}
		return contentDetails;
	}

	public void Open()
	{
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0055: Unknown result type (might be due to invalid IL or missing references)
		//IL_006c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f1: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d7: Unknown result type (might be due to invalid IL or missing references)
		//IL_01dc: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f0: Unknown result type (might be due to invalid IL or missing references)
		//IL_0205: Unknown result type (might be due to invalid IL or missing references)
		//IL_0180: Unknown result type (might be due to invalid IL or missing references)
		//IL_0191: Unknown result type (might be due to invalid IL or missing references)
		//IL_0241: Unknown result type (might be due to invalid IL or missing references)
		CompBouncingArrow comp = ((ThingWithComps)this).GetComp<CompBouncingArrow>();
		if (comp != null)
		{
			comp.doBouncingArrow = false;
		}
		MapParent parent = ((Thing)this).Map.Parent;
		PocketMapParent val = (PocketMapParent)(object)((parent is PocketMapParent) ? parent : null);
		MapParent val2 = ((val != null) ? val.sourceMap.Parent : ((Thing)this).Map.Parent);
		string text = "LootableBuildingOpened";
		Find.SignalManager.SendSignal(new Signal(text, NamedArgumentUtility.Named((object)val2, "SUBJECT")));
		QuestUtility.SendQuestTargetSignals(((WorldObject)val2).questTags, text, NamedArgumentUtility.Named((object)val2, "SUBJECT"));
		GetDetails();
		if (contentDetails == null)
		{
			return;
		}
		if (contentDetails.randomFromContents)
		{
			for (int i = 0; i < ((IntRange)(ref contentDetails.totalRandomLoops)).RandomInRange; i++)
			{
				ThingAndCount thingAndCount = GenCollection.RandomElement<ThingAndCount>((IEnumerable<ThingAndCount>)contentDetails.contents);
				Thing obj = ThingMaker.MakeThing(thingAndCount.thing, (ThingDef)null);
				obj.stackCount = thingAndCount.count;
				Thing obj2 = ((obj is ThingWithComps) ? obj : null);
				if (obj2 != null)
				{
					CompQuality compQuality = ((ThingWithComps)obj2).compQuality;
					if (compQuality != null)
					{
						compQuality.SetQuality(QualityUtility.GenerateQualityRandomEqualChance(), (ArtGenerationContext?)(ArtGenerationContext)1);
					}
				}
				GenPlace.TryPlaceThing(obj, ((Thing)this).Position, ((Thing)this).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
			}
		}
		else
		{
			foreach (ThingAndCount content in contentDetails.contents)
			{
				Thing obj3 = ThingMaker.MakeThing(content.thing, (ThingDef)null);
				obj3.stackCount = content.count;
				Thing obj4 = ((obj3 is ThingWithComps) ? obj3 : null);
				if (obj4 != null)
				{
					CompQuality compQuality2 = ((ThingWithComps)obj4).compQuality;
					if (compQuality2 != null)
					{
						compQuality2.SetQuality(QualityUtility.GenerateQualityRandomEqualChance(), (ArtGenerationContext?)(ArtGenerationContext)1);
					}
				}
				GenPlace.TryPlaceThing(obj3, ((Thing)this).Position, ((Thing)this).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
			}
		}
		if (contentDetails.buildingLeft != null)
		{
			Rot4 rotation = ((Thing)this).Rotation;
			Thing val3 = GenSpawn.Spawn(ThingMaker.MakeThing(contentDetails.buildingLeft, (ThingDef)null), ((Thing)this).Position, ((Thing)this).Map, (WipeMode)0);
			val3.Rotation = rotation;
			if (val3.def.CanHaveFaction)
			{
				val3.SetFaction(((Thing)this).Faction, (Pawn)null);
			}
		}
		if (contentDetails.deconstructSound != null)
		{
			SoundStarter.PlayOneShot(contentDetails.deconstructSound, SoundInfo.op_Implicit((Thing)(object)this));
		}
		if (((Thing)this).Spawned)
		{
			((Thing)this).Destroy((DestroyMode)0);
		}
	}
}
