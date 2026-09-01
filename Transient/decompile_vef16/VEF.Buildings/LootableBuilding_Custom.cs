using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace VEF.Buildings;

public class LootableBuilding_Custom : Building
{
	private MapComponent_InteractableBuildingsInMap cachedMapComp;

	private LootableBuildingDetails cachedExtension;

	public LootableBuildingDetails LootableExtension
	{
		get
		{
			if (cachedExtension == null)
			{
				cachedExtension = ((Def)((Thing)this).def).GetModExtension<LootableBuildingDetails>();
			}
			return cachedExtension;
		}
	}

	public MapComponent_InteractableBuildingsInMap InteractablesMapComp
	{
		get
		{
			if (cachedMapComp == null)
			{
				cachedMapComp = ((Thing)this).Map.GetComponent<MapComponent_InteractableBuildingsInMap>();
			}
			return cachedMapComp;
		}
	}

	public override IEnumerable<Gizmo> GetGizmos()
	{
		foreach (Gizmo item in _003C_003En__0())
		{
			yield return item;
		}
		Command_Action command_Action = new Command_Action();
		Command_Action val = new Command_Action();
		MapComponent_InteractableBuildingsInMap interactablesMapComp = InteractablesMapComp;
		if (interactablesMapComp != null && !interactablesMapComp.lootables_InMap.Contains((Thing)(object)this))
		{
			((Command)command_Action).defaultDesc = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(LootableExtension.gizmoDesc, NamedArgument.op_Implicit(((Entity)this).LabelCap)));
			((Command)command_Action).defaultLabel = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(LootableExtension.gizmoText, NamedArgument.op_Implicit(((Entity)this).LabelCap)));
			((Command)command_Action).icon = (Texture)(object)ContentFinder<Texture2D>.Get(LootableExtension.gizmoTexture, true);
			((Command)command_Action).hotKey = KeyBindingDefOf.Misc1;
			command_Action.action = delegate
			{
				InteractablesMapComp?.AddLootableToMap((Thing)(object)this);
			};
		}
		else
		{
			((Command)command_Action).defaultDesc = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(LootableExtension.gizmoDesc, NamedArgument.op_Implicit(((Entity)this).LabelCap)));
			((Command)command_Action).defaultLabel = TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate(LootableExtension.gizmoText, NamedArgument.op_Implicit(((Entity)this).LabelCap)));
			((Command)command_Action).icon = (Texture)(object)ContentFinder<Texture2D>.Get(LootableExtension.gizmoTexture, true);
			((Gizmo)command_Action).Disabled = true;
			((Command)val).defaultDesc = TaggedString.op_Implicit(Translator.Translate(LootableExtension.cancelLootinggizmoDesc));
			((Command)val).defaultLabel = TaggedString.op_Implicit(Translator.Translate(LootableExtension.cancelLootinggizmoText));
			((Command)val).icon = (Texture)(object)ContentFinder<Texture2D>.Get(LootableExtension.cancelLootingGizmoTexture, true);
			((Command)val).hotKey = KeyBindingDefOf.Misc2;
			val.action = delegate
			{
				InteractablesMapComp?.RemoveLootableFromMap((Thing)(object)this);
			};
			yield return (Gizmo)(object)val;
		}
		yield return (Gizmo)(object)command_Action;
	}

	public override void Destroy(DestroyMode mode = 0)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		InteractablesMapComp?.RemoveLootableFromMap((Thing)(object)this);
		((Building)this).Destroy(mode);
	}

	public override void Kill(DamageInfo? dinfo = null, Hediff exactCulprit = null)
	{
		InteractablesMapComp?.RemoveLootableFromMap((Thing)(object)this);
		((ThingWithComps)this).Kill(dinfo, exactCulprit);
	}

	protected override void DrawAt(Vector3 drawLoc, bool flip = false)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_003b: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b2: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b3: Unknown result type (might be due to invalid IL or missing references)
		((ThingWithComps)this).DrawAt(drawLoc, flip);
		MapComponent_InteractableBuildingsInMap interactablesMapComp = InteractablesMapComp;
		if (interactablesMapComp != null && interactablesMapComp.lootables_InMap.Contains((Thing)(object)this) && LootableExtension.overlayTexture != null)
		{
			Vector3 drawPos = ((Thing)this).DrawPos;
			drawPos.y = Altitudes.AltitudeFor((AltitudeLayer)39) + 0.18181819f;
			float num = ((float)Math.Sin((Time.realtimeSinceStartup + 397f * (float)(((Thing)this).thingIDNumber % 571)) * 4f) + 1f) * 0.5f;
			num = 0.3f + num * 0.7f;
			Material val = FadedMaterialPool.FadedVersionOf(MaterialPool.MatFrom(LootableExtension.overlayTexture, ShaderDatabase.MetaOverlay), num);
			Graphics.DrawMesh(MeshPool.plane08, drawPos, Quaternion.identity, val, 0);
		}
	}

	public void Open()
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0030: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_028e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0293: Unknown result type (might be due to invalid IL or missing references)
		//IL_02a7: Unknown result type (might be due to invalid IL or missing references)
		//IL_02bc: Unknown result type (might be due to invalid IL or missing references)
		//IL_02f8: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_01eb: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_0161: Unknown result type (might be due to invalid IL or missing references)
		//IL_0172: Unknown result type (might be due to invalid IL or missing references)
		//IL_0232: Unknown result type (might be due to invalid IL or missing references)
		//IL_0245: Unknown result type (might be due to invalid IL or missing references)
		if (LootableExtension == null)
		{
			return;
		}
		if (LootableExtension.useThingSetMakerDef)
		{
			ThingSetMakerParams val = default(ThingSetMakerParams);
			val.totalMarketValueRange = LootableExtension.setMakerDetails.totalMarketValueRange;
			val.minSingleItemMarketValuePct = LootableExtension.setMakerDetails.minSingleItemMarketValuePct;
			val.allowNonStackableDuplicates = LootableExtension.setMakerDetails.allowNonStackableDuplicates;
			int randomInRange = ((IntRange)(ref LootableExtension.setMakerDetails.countRange)).RandomInRange;
			val.countRange = new IntRange(randomInRange, randomInRange);
			List<Thing> list = LootableExtension.setMakerDetails.thingSetMakerDef.root.Generate(val);
			if (list != null)
			{
				foreach (Thing item in list)
				{
					GenPlace.TryPlaceThing(item, ((Thing)this).Position, ((Thing)this).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
				}
			}
		}
		else if (LootableExtension.randomFromContents)
		{
			for (int i = 0; i < ((IntRange)(ref LootableExtension.totalRandomLoops)).RandomInRange; i++)
			{
				ThingAndCount thingAndCount = GenCollection.RandomElement<ThingAndCount>((IEnumerable<ThingAndCount>)LootableExtension.contents);
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
			foreach (ThingAndCount content in LootableExtension.contents)
			{
				Thing val2 = ThingMaker.MakeThing(content.thing, (ThingDef)null);
				if (content.randomCount != new IntRange(1, 1))
				{
					val2.stackCount = ((IntRange)(ref content.randomCount)).RandomInRange;
				}
				else
				{
					val2.stackCount = content.count;
				}
				Thing obj3 = ((val2 is ThingWithComps) ? val2 : null);
				if (obj3 != null)
				{
					CompQuality compQuality2 = ((ThingWithComps)obj3).compQuality;
					if (compQuality2 != null)
					{
						compQuality2.SetQuality(QualityUtility.GenerateQualityRandomEqualChance(), (ArtGenerationContext?)(ArtGenerationContext)1);
					}
				}
				GenPlace.TryPlaceThing(val2, ((Thing)this).Position, ((Thing)this).Map, (ThingPlaceMode)1, (Action<Thing, int>)null, (Predicate<IntVec3>)null, (Rot4?)null, 1);
			}
		}
		if (LootableExtension.buildingLeft != null)
		{
			Rot4 rotation = ((Thing)this).Rotation;
			Thing val3 = GenSpawn.Spawn(ThingMaker.MakeThing(LootableExtension.buildingLeft, (ThingDef)null), ((Thing)this).Position, ((Thing)this).Map, (WipeMode)0);
			val3.Rotation = rotation;
			if (val3.def.CanHaveFaction)
			{
				val3.SetFaction(((Thing)this).Faction, (Pawn)null);
			}
		}
		if (LootableExtension.deconstructSound != null)
		{
			SoundStarter.PlayOneShot(LootableExtension.deconstructSound, SoundInfo.op_Implicit((Thing)(object)this));
		}
		if (((Thing)this).Spawned)
		{
			((Thing)this).Destroy((DestroyMode)0);
		}
	}

	public override IEnumerable<FloatMenuOption> GetFloatMenuOptions(Pawn selPawn)
	{
		foreach (FloatMenuOption item in _003C_003En__1(selPawn))
		{
			yield return item;
		}
		if (!ReservationUtility.CanReserve(selPawn, LocalTargetInfo.op_Implicit((Thing)(object)this), 1, -1, (ReservationLayerDef)null, false) || !selPawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation) || (LootableExtension.useHackingSpeed && (!LootableExtension.useHackingSpeed || selPawn.skills.GetSkill(SkillDefOf.Intellectual).TotallyDisabled || StatDefOf.HackingSpeed.Worker.IsDisabledFor((Thing)(object)selPawn))))
		{
			yield break;
		}
		TaggedString val;
		if (!ReachabilityUtility.CanReach(selPawn, LocalTargetInfo.op_Implicit((Thing)(object)this), (PathEndMode)1, (Danger)3, false, false, (TraverseMode)0))
		{
			val = Translator.Translate("NoPath");
			yield return new FloatMenuOption(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("CannotUseReason", NamedArgument.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst()))), (Action)null, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
			yield break;
		}
		val = Translator.Translate(LootableExtension.gizmoText);
		yield return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(TaggedString.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst()), (Action)delegate
		{
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			selPawn.jobs.TryTakeOrderedJob(JobMaker.MakeJob(InternalDefOf.VFE_Loot, LocalTargetInfo.op_Implicit((Thing)(object)this)), (JobTag?)(JobTag)0, false);
		}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0), selPawn, LocalTargetInfo.op_Implicit((Thing)(object)this), "ReservedBy", (ReservationLayerDef)null);
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Gizmo> _003C_003En__0()
	{
		return ((Building)this).GetGizmos();
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<FloatMenuOption> _003C_003En__1(Pawn selPawn)
	{
		return ((ThingWithComps)this).GetFloatMenuOptions(selPawn);
	}
}
