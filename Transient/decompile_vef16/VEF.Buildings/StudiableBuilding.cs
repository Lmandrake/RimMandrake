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

public class StudiableBuilding : Building
{
	private MapComponent_InteractableBuildingsInMap cachedMapComp;

	private StudiableBuildingDetails cachedExtension;

	public StudiableBuildingDetails StudiableExtension
	{
		get
		{
			if (cachedExtension == null)
			{
				cachedExtension = ((Def)((Thing)this).def).GetModExtension<StudiableBuildingDetails>();
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
		Command_Action val = new Command_Action();
		MapComponent_InteractableBuildingsInMap interactablesMapComp = InteractablesMapComp;
		if (interactablesMapComp != null && !interactablesMapComp.studiables_InMap.Contains((Thing)(object)this))
		{
			((Command)val).defaultDesc = TaggedString.op_Implicit(Translator.Translate(StudiableExtension.gizmoDesc));
			((Command)val).defaultLabel = TaggedString.op_Implicit(Translator.Translate(StudiableExtension.gizmoText));
			((Command)val).icon = (Texture)(object)ContentFinder<Texture2D>.Get(StudiableExtension.gizmoTexture, true);
			((Command)val).hotKey = KeyBindingDefOf.Misc1;
			val.action = delegate
			{
				InteractablesMapComp?.AddStudiablesToMap((Thing)(object)this);
			};
		}
		else
		{
			((Command)val).defaultDesc = TaggedString.op_Implicit(Translator.Translate(StudiableExtension.gizmoDesc));
			((Command)val).defaultLabel = TaggedString.op_Implicit(Translator.Translate(StudiableExtension.gizmoText));
			((Command)val).icon = (Texture)(object)ContentFinder<Texture2D>.Get(StudiableExtension.gizmoTexture, true);
			((Gizmo)val).Disabled = true;
		}
		yield return (Gizmo)(object)val;
	}

	public override void Destroy(DestroyMode mode = 0)
	{
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		InteractablesMapComp?.RemoveStudiablesFromMap((Thing)(object)this);
		((Building)this).Destroy(mode);
	}

	public override void Kill(DamageInfo? dinfo = null, Hediff exactCulprit = null)
	{
		InteractablesMapComp?.RemoveStudiablesFromMap((Thing)(object)this);
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
		if (interactablesMapComp != null && interactablesMapComp.studiables_InMap.Contains((Thing)(object)this) && StudiableExtension.overlayTexture != null)
		{
			Vector3 drawPos = ((Thing)this).DrawPos;
			drawPos.y = Altitudes.AltitudeFor((AltitudeLayer)39) + 0.18181819f;
			float num = ((float)Math.Sin((Time.realtimeSinceStartup + 397f * (float)(((Thing)this).thingIDNumber % 571)) * 4f) + 1f) * 0.5f;
			num = 0.3f + num * 0.7f;
			Material val = FadedMaterialPool.FadedVersionOf(MaterialPool.MatFrom(StudiableExtension.overlayTexture, ShaderDatabase.MetaOverlay), num);
			Graphics.DrawMesh(MeshPool.plane08, drawPos, Quaternion.identity, val, 0);
		}
	}

	public virtual void Study(Pawn pawn)
	{
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0036: Unknown result type (might be due to invalid IL or missing references)
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		if (StudiableExtension == null)
		{
			return;
		}
		if (StudiableExtension.buildingLeft != null)
		{
			Thing val = GenSpawn.Spawn(ThingMaker.MakeThing(StudiableExtension.buildingLeft, (ThingDef)null), ((Thing)this).Position, ((Thing)this).Map, ((Thing)this).Rotation, (WipeMode)0, false, false);
			if (val.def.CanHaveFaction)
			{
				val.SetFaction(((Thing)this).Faction, (Pawn)null);
			}
		}
		if (StudiableExtension.deconstructSound != null)
		{
			SoundStarter.PlayOneShot(StudiableExtension.deconstructSound, SoundInfo.op_Implicit((Thing)(object)this));
		}
		if (StudiableExtension.craftingInspiration)
		{
			pawn.mindState.inspirationHandler.TryStartInspiration(InspirationDefOf.Inspired_Creativity, (string)null, true);
		}
		if (((Thing)this).Spawned)
		{
			((Entity)this).DeSpawn((DestroyMode)0);
		}
	}

	public override IEnumerable<FloatMenuOption> GetFloatMenuOptions(Pawn selPawn)
	{
		foreach (FloatMenuOption item in _003C_003En__1(selPawn))
		{
			yield return item;
		}
		if (!ReservationUtility.CanReserve(selPawn, LocalTargetInfo.op_Implicit((Thing)(object)this), 1, -1, (ReservationLayerDef)null, false) || !selPawn.health.capacities.CapableOf(PawnCapacityDefOf.Manipulation) || selPawn.skills.GetSkill(SkillDefOf.Intellectual).TotallyDisabled)
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
		val = Translator.Translate(StudiableExtension.gizmoText);
		yield return FloatMenuUtility.DecoratePrioritizedTask(new FloatMenuOption(TaggedString.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst()), (Action)delegate
		{
			//IL_0016: Unknown result type (might be due to invalid IL or missing references)
			selPawn.jobs.TryTakeOrderedJob(JobMaker.MakeJob(InternalDefOf.VFE_StudyBuilding, LocalTargetInfo.op_Implicit((Thing)(object)this)), (JobTag?)(JobTag)0, false);
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
