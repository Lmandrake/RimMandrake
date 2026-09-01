using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace BigAndSmall;

public class JobDriver_Reanimate : JobDriver
{
	[CompilerGenerated]
	private sealed class _003CMakeNewToils_003Ed__9 : IEnumerable<Toil>, IEnumerable, IEnumerator<Toil>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private Toil _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		public JobDriver_Reanimate _003C_003E4__this;

		Toil IEnumerator<Toil>.Current
		{
			[DebuggerHidden]
			get
			{
				return _003C_003E2__current;
			}
		}

		object IEnumerator.Current
		{
			[DebuggerHidden]
			get
			{
				return _003C_003E2__current;
			}
		}

		[DebuggerHidden]
		public _003CMakeNewToils_003Ed__9(int _003C_003E1__state)
		{
			this._003C_003E1__state = _003C_003E1__state;
			_003C_003El__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			_003C_003E1__state = -2;
		}

		private bool MoveNext()
		{
			int num = _003C_003E1__state;
			JobDriver_Reanimate CS_0024_003C_003E8__locals6 = _003C_003E4__this;
			switch (num)
			{
			default:
				return false;
			case 0:
				_003C_003E1__state = -1;
				_003C_003E2__current = ToilFailConditions.FailOnDespawnedOrNull<Toil>(ToilFailConditions.FailOnDespawnedOrNull<Toil>(Toils_Goto.GotoThing((TargetIndex)2, (PathEndMode)2, false), (TargetIndex)2), (TargetIndex)1);
				_003C_003E1__state = 1;
				return true;
			case 1:
				_003C_003E1__state = -1;
				_003C_003E2__current = Toils_Haul.StartCarryThing((TargetIndex)2, false, false, false, true, false);
				_003C_003E1__state = 2;
				return true;
			case 2:
				_003C_003E1__state = -1;
				_003C_003E2__current = ToilFailConditions.FailOnDespawnedOrNull<Toil>(Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)2, false), (TargetIndex)1);
				_003C_003E1__state = 3;
				return true;
			case 3:
			{
				_003C_003E1__state = -1;
				Toil val = Toils_General.Wait(600, (TargetIndex)0);
				ToilEffects.WithProgressBarToilDelay(val, (TargetIndex)1, false, -0.5f);
				ToilFailConditions.FailOnDespawnedOrNull<Toil>(val, (TargetIndex)1);
				ToilFailConditions.FailOnCannotTouch<Toil>(val, (TargetIndex)1, (PathEndMode)2);
				val.tickAction = delegate
				{
					//IL_0036: Unknown result type (might be due to invalid IL or missing references)
					CompUsable val2 = ThingCompUtility.TryGetComp<CompUsable>(CS_0024_003C_003E8__locals6.Item);
					if (val2 != null && CS_0024_003C_003E8__locals6.warmupMote == null && val2.Props.warmupMote != null)
					{
						CS_0024_003C_003E8__locals6.warmupMote = MoteMaker.MakeAttachedOverlay((Thing)(object)CS_0024_003C_003E8__locals6.Corpse, val2.Props.warmupMote, Vector3.zero, 1f, -1f);
					}
					Mote warmupMote = CS_0024_003C_003E8__locals6.warmupMote;
					if (warmupMote != null)
					{
						warmupMote.Maintain();
					}
				};
				_003C_003E2__current = val;
				_003C_003E1__state = 4;
				return true;
			}
			case 4:
				_003C_003E1__state = -1;
				_003C_003E2__current = Toils_General.Do((Action)CS_0024_003C_003E8__locals6.ReanimateToil);
				_003C_003E1__state = 5;
				return true;
			case 5:
				_003C_003E1__state = -1;
				return false;
			}
		}

		bool IEnumerator.MoveNext()
		{
			//ILSpy generated this explicit interface implementation from .override directive in MoveNext
			return this.MoveNext();
		}

		[DebuggerHidden]
		void IEnumerator.Reset()
		{
			throw new NotSupportedException();
		}

		[DebuggerHidden]
		IEnumerator<Toil> IEnumerable<Toil>.GetEnumerator()
		{
			_003CMakeNewToils_003Ed__9 result;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				result = this;
			}
			else
			{
				result = new _003CMakeNewToils_003Ed__9(0)
				{
					_003C_003E4__this = _003C_003E4__this
				};
			}
			return result;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<Toil>)this).GetEnumerator();
		}
	}

	private const TargetIndex CorpseInd = 1;

	private const TargetIndex ItemInd = 2;

	private const int DurationTicks = 600;

	private Mote warmupMote;

	private Corpse Corpse
	{
		get
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0014: Unknown result type (might be due to invalid IL or missing references)
			//IL_001a: Expected O, but got Unknown
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)1);
			return (Corpse)((LocalTargetInfo)(ref target)).Thing;
		}
	}

	private Thing Item
	{
		get
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			LocalTargetInfo target = base.job.GetTarget((TargetIndex)2);
			return ((LocalTargetInfo)(ref target)).Thing;
		}
	}

	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		if (ReservationUtility.Reserve(base.pawn, LocalTargetInfo.op_Implicit((Thing)(object)Corpse), base.job, 1, -1, (ReservationLayerDef)null, errorOnFailed, false))
		{
			return ReservationUtility.Reserve(base.pawn, LocalTargetInfo.op_Implicit(Item), base.job, 1, -1, (ReservationLayerDef)null, errorOnFailed, false);
		}
		return false;
	}

	[IteratorStateMachine(typeof(_003CMakeNewToils_003Ed__9))]
	protected override IEnumerable<Toil> MakeNewToils()
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CMakeNewToils_003Ed__9(-2)
		{
			_003C_003E4__this = this
		};
	}

	private void ReanimateToil()
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		CompProperties_TargetEffectReanimate currentProps = CompTargetEffect_Reanimate.currentProps;
		Pawn innerPawn = Corpse.InnerPawn;
		ReanimatePawn(innerPawn, currentProps.xenoTypeDef);
		SoundStarter.PlayOneShot(SoundDefOf.MechSerumUsed, SoundInfo.InMap(TargetInfo.op_Implicit((Thing)(object)innerPawn), (MaintenanceType)0));
		Messages.Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MessagePawnResurrected", NamedArgument.op_Implicit((Thing)(object)innerPawn))), LookTargets.op_Implicit((Thing)(object)innerPawn), MessageTypeDefOf.PositiveEvent, true);
		Thing item = Item;
		object obj;
		if (item == null)
		{
			obj = null;
		}
		else
		{
			CompTargetEffect_Resurrect obj2 = ThingCompUtility.TryGetComp<CompTargetEffect_Resurrect>(item);
			obj = ((obj2 != null) ? obj2.Props.moteDef : null);
		}
		ThingDef val = (ThingDef)obj;
		if (val != null)
		{
			MoteMaker.MakeAttachedOverlay((Thing)(object)innerPawn, val, Vector3.zero, 1f, -1f);
		}
		Item.SplitOff(1).Destroy((DestroyMode)0);
	}

	public static void ReanimatePawn(Pawn innerPawn, XenotypeDef xenotype)
	{
		if (xenotype == BSDefs.VU_Returned)
		{
			VUReturning.ModifyReturnedByRotStage(innerPawn, ref xenotype);
		}
		if (innerPawn != null)
		{
			RaceProperties raceProps = innerPawn.RaceProps;
			if (((raceProps != null) ? new bool?(raceProps.Animal) : ((bool?)null)) == true)
			{
				innerPawn.health.AddHediff(VUReturning.GetAnimalReturnedHediff(innerPawn), (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				goto IL_0080;
			}
		}
		if (innerPawn.genes != null)
		{
			GeneHelpers.AddAllXenotypeGenes(innerPawn, xenotype, "Returned " + innerPawn.genes.XenotypeLabel);
		}
		goto IL_0080;
		IL_0080:
		GameUtils.UnhealingRessurection(innerPawn);
	}
}
