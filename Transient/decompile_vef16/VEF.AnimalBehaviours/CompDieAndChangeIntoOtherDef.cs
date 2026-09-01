using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

public class CompDieAndChangeIntoOtherDef : ThingComp, PawnGizmoProvider
{
	public CompProperties_DieAndChangeIntoOtherDef Props => base.props as CompProperties_DieAndChangeIntoOtherDef;

	public IEnumerable<Gizmo> GetGizmos()
	{
		if (Props.mustBeTamed)
		{
			if (!Props.mustBeTamed)
			{
				yield break;
			}
			Faction faction = ((Thing)base.parent).Faction;
			if (faction == null || !faction.IsPlayer)
			{
				yield break;
			}
		}
		yield return (Gizmo)new Command_Action
		{
			defaultLabel = TaggedString.op_Implicit(Translator.Translate(Props.gizmoLabel)),
			defaultDesc = TaggedString.op_Implicit(Translator.Translate(Props.gizmoDesc)),
			icon = (Texture)(object)ContentFinder<Texture2D>.Get(Props.gizmoImage, true),
			action = delegate
			{
				DiggableTerrainSetup();
			}
		};
	}

	public void DiggableTerrainSetup()
	{
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0048: Unknown result type (might be due to invalid IL or missing references)
		//IL_004d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0067: Unknown result type (might be due to invalid IL or missing references)
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (Props.needsDiggableTerrain)
		{
			if (GridsUtility.GetTerrain(((Thing)val).Position, ((Thing)val).Map).affordances.Contains(VEFDefOf.Diggable))
			{
				ChangeDef(val);
				return;
			}
			TaggedString val2 = Translator.Translate("VEF_TerrainsNeedsDiggable");
			Messages.Message(TaggedString.op_Implicit(((TaggedString)(ref val2)).CapitalizeFirst()), LookTargets.op_Implicit(new TargetInfo(((Thing)val).Position, ((Thing)val).Map, false)), MessageTypeDefOf.NegativeEvent, true);
		}
		else
		{
			ChangeDef(val);
		}
	}

	public void ChangeDef(Pawn pawn)
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		GenSpawn.Spawn(Props.defToChangeTo, ((Thing)pawn).Position, ((Thing)pawn).Map, (WipeMode)0);
		((Entity)pawn).DeSpawn((DestroyMode)0);
		Find.WorldPawns.PassToWorld(pawn, (PawnDiscardDecideMode)2);
	}
}
