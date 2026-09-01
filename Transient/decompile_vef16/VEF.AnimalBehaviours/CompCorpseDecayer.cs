using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace VEF.AnimalBehaviours;

public class CompCorpseDecayer : ThingComp
{
	public bool flagOnce;

	public bool decayingOn = true;

	public CompProperties_CorpseDecayer Props => (CompProperties_CorpseDecayer)(object)base.props;

	public override void PostExposeData()
	{
		((ThingComp)this).PostExposeData();
		Scribe_Values.Look<bool>(ref decayingOn, "decayingOn", true, false);
	}

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
		if (training == null || !training.HasLearned(InternalDefOf.VEF_ControlledCorpseDecay))
		{
			yield break;
		}
		if (decayingOn)
		{
			yield return (Gizmo)new Command_Action
			{
				action = delegate
				{
					decayingOn = false;
				},
				hotKey = KeyBindingDefOf.Misc2,
				defaultDesc = TaggedString.op_Implicit(Translator.Translate("VEF_DisableCorpseDecayingDesc")),
				icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Abilities/VEF_CorpseDecay", true),
				defaultLabel = TaggedString.op_Implicit(Translator.Translate("VEF_DisableCorpseDecaying"))
			};
		}
		else
		{
			yield return (Gizmo)new Command_Action
			{
				action = delegate
				{
					decayingOn = true;
				},
				hotKey = KeyBindingDefOf.Misc2,
				defaultDesc = TaggedString.op_Implicit(Translator.Translate("VEF_EnableCorpseDecayingDesc")),
				icon = (Texture)(object)ContentFinder<Texture2D>.Get("UI/Abilities/VEF_CorpseDecay", true),
				defaultLabel = TaggedString.op_Implicit(Translator.Translate("VEF_EnableCorpseDecaying"))
			};
		}
	}

	public override void CompTickInterval(int delta)
	{
		//IL_0050: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Unknown result type (might be due to invalid IL or missing references)
		//IL_005b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_0078: Unknown result type (might be due to invalid IL or missing references)
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0091: Unknown result type (might be due to invalid IL or missing references)
		//IL_0092: Unknown result type (might be due to invalid IL or missing references)
		//IL_00a3: Unknown result type (might be due to invalid IL or missing references)
		//IL_0199: Unknown result type (might be due to invalid IL or missing references)
		//IL_024c: Unknown result type (might be due to invalid IL or missing references)
		//IL_01ce: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_01f9: Unknown result type (might be due to invalid IL or missing references)
		//IL_0225: Unknown result type (might be due to invalid IL or missing references)
		//IL_0231: Unknown result type (might be due to invalid IL or missing references)
		//IL_0236: Unknown result type (might be due to invalid IL or missing references)
		((ThingComp)this).CompTickInterval(delta);
		if (!AnimalBehaviours_Settings.flagCorpseDecayingEffect || !Gen.IsHashIntervalTick((Thing)(object)base.parent, Props.tickInterval, delta))
		{
			return;
		}
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (decayingOn)
		{
			if (((Thing)val).Map == null)
			{
				return;
			}
			CellRect val2 = GenAdj.OccupiedRect(((Thing)val).Position, ((Thing)val).Rotation, IntVec2.One);
			val2 = ((CellRect)(ref val2)).ExpandedBy(Props.radius);
			{
				IntVec3 val5 = default(IntVec3);
				foreach (IntVec3 cell in ((CellRect)(ref val2)).Cells)
				{
					if (GenGrid.InBounds(cell, ((Thing)val).Map))
					{
						foreach (Thing item in new HashSet<Thing>(GridsUtility.GetThingList(cell, ((Thing)val).Map)))
						{
							Corpse val3 = (Corpse)(object)((item is Corpse) ? item : null);
							if (val3 == null || !((Thing)val3.InnerPawn).def.race.IsFlesh)
							{
								continue;
							}
							((Thing)val3).HitPoints = ((Thing)val3).HitPoints - 5;
							if (val?.needs?.food != null)
							{
								Need_Food food = val.needs.food;
								((Need)food).CurLevel = ((Need)food).CurLevel + Props.nutritionGained;
							}
							if (ModLister.HasActiveModWithName("Alpha Animals") && ((Thing)val).Faction == Faction.OfPlayer && ((Thing)val3.InnerPawn).def.race.Humanlike)
							{
								val.health.AddHediff(HediffDef.Named("AA_CorpseFeast"), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
							}
							CompRottable val4 = ThingCompUtility.TryGetComp<CompRottable>((Thing)(object)val3);
							if ((int)val4.Stage == 0)
							{
								val4.RotProgress += 100000f;
							}
							if (((Thing)val3).HitPoints < 0)
							{
								((Thing)val3).Destroy((DestroyMode)0);
								for (int i = 0; i < 20; i++)
								{
									CellFinder.TryFindRandomReachableNearbyCell(((Thing)val).Position, ((Thing)val).Map, 2f, TraverseParms.For((TraverseMode)2, (Danger)3, false, false, false, true, false), (Predicate<IntVec3>)null, (Predicate<Region>)null, ref val5, 999999);
									FilthMaker.TryMakeFilth(val5, ((Thing)val).Map, ThingDefOf.Filth_CorpseBile, GenText.LabelIndefinite(val), 1, (FilthSourceFlags)0);
									SoundStarter.PlayOneShot(SoundDef.Named(Props.corpseSound), SoundInfo.op_Implicit(new TargetInfo(((Thing)val).Position, ((Thing)val).Map, false)));
								}
							}
							FilthMaker.TryMakeFilth(cell, ((Thing)val).Map, ThingDefOf.Filth_CorpseBile, GenText.LabelIndefinite(val), 1, (FilthSourceFlags)0);
							flagOnce = true;
						}
					}
					if (flagOnce)
					{
						flagOnce = false;
						break;
					}
				}
				return;
			}
		}
		if (!ModsConfig.OdysseyActive)
		{
			Pawn_TrainingTracker training = val.training;
			if (training == null || !training.HasLearned(InternalDefOf.VEF_ControlledCorpseDecay))
			{
				decayingOn = true;
			}
		}
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Gizmo> _003C_003En__0()
	{
		return ((ThingComp)this).CompGetGizmosExtra();
	}
}
