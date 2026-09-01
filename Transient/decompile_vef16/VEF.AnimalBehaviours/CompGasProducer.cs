using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.AnimalBehaviours;

internal class CompGasProducer : ThingComp
{
	private int gasTickMax = 65;

	public bool productionOn = true;

	public CompProperties_GasProducer Props => (CompProperties_GasProducer)(object)base.props;

	public override IEnumerable<Gizmo> CompGetGizmosExtra()
	{
		foreach (Gizmo item in _003C_003En__0())
		{
			yield return item;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (!ModsConfig.OdysseyActive)
		{
			yield break;
		}
		Pawn_TrainingTracker training = val.training;
		if (training == null || !training.HasLearned(InternalDefOf.VEF_FumeRegulation))
		{
			yield break;
		}
		if (productionOn)
		{
			yield return (Gizmo)new Command_Action
			{
				action = delegate
				{
					productionOn = false;
				},
				hotKey = KeyBindingDefOf.Misc2,
				defaultDesc = TaggedString.op_Implicit(Translator.Translate("VEF_DisableGasDesc")),
				icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Abilities/VEF_FumeRegulation", true),
				defaultLabel = TaggedString.op_Implicit(Translator.Translate("VEF_DisableGas"))
			};
		}
		else
		{
			yield return (Gizmo)new Command_Action
			{
				action = delegate
				{
					productionOn = true;
				},
				hotKey = KeyBindingDefOf.Misc2,
				defaultDesc = TaggedString.op_Implicit(Translator.Translate("VEF_EnableGasDesc")),
				icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Abilities/VEF_FumeRegulation", true),
				defaultLabel = TaggedString.op_Implicit(Translator.Translate("VEF_EnableGas"))
			};
		}
	}

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<bool>(ref productionOn, "productionOn", true, false);
	}

	public override void CompTickInterval(int delta)
	{
		//IL_0077: Unknown result type (might be due to invalid IL or missing references)
		//IL_007d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0082: Unknown result type (might be due to invalid IL or missing references)
		//IL_0087: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_009a: Unknown result type (might be due to invalid IL or missing references)
		//IL_009f: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b6: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ed: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f8: Unknown result type (might be due to invalid IL or missing references)
		if (!AnimalBehaviours_Settings.flagAnimalParticles || !Gen.IsHashIntervalTick((Thing)(object)base.parent, gasTickMax, delta))
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (productionOn)
		{
			if (((Thing)val).Map == null || (Props.generateIfDowned && (!Props.generateIfDowned || val.Downed || val.Dead)))
			{
				return;
			}
			CellRect val2 = GenAdj.OccupiedRect(((Thing)val).Position, ((Thing)val).Rotation, IntVec2.One);
			val2 = ((CellRect)(ref val2)).ExpandedBy(Props.radius);
			{
				foreach (IntVec3 cell in ((CellRect)(ref val2)).Cells)
				{
					if (GenGrid.InBounds(cell, ((Thing)val).Map) && Rand.Chance(Props.rate))
					{
						Thing obj = ThingMaker.MakeThing(ThingDef.Named(Props.gasType), (ThingDef)null);
						obj.Rotation = Rot4.North;
						obj.Position = cell;
						((Entity)obj).SpawnSetup(((Thing)val).Map, false);
					}
				}
				return;
			}
		}
		if (ModsConfig.OdysseyActive)
		{
			Pawn_TrainingTracker training = val.training;
			if (training != null && training.HasLearned(InternalDefOf.VEF_FumeRegulation))
			{
				return;
			}
		}
		productionOn = true;
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Gizmo> _003C_003En__0()
	{
		return ((ThingComp)this).CompGetGizmosExtra();
	}
}
