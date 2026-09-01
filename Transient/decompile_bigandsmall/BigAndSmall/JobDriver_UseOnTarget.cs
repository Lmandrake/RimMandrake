using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace BigAndSmall;

internal class JobDriver_UseOnTarget : JobDriver_UseItem
{
	[CompilerGenerated]
	private sealed class _003CMakeNewToils_003Ed__4 : IEnumerable<Toil>, IEnumerable, IEnumerator<Toil>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private Toil _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		public JobDriver_UseOnTarget _003C_003E4__this;

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
		public _003CMakeNewToils_003Ed__4(int _003C_003E1__state)
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
			JobDriver_UseOnTarget CS_0024_003C_003E8__locals10 = _003C_003E4__this;
			switch (num)
			{
			default:
				return false;
			case 0:
				_003C_003E1__state = -1;
				ToilFailConditions.FailOnIncapable<JobDriver_UseOnTarget>(CS_0024_003C_003E8__locals10, PawnCapacityDefOf.Manipulation);
				ToilFailConditions.FailOn<JobDriver_UseOnTarget>(CS_0024_003C_003E8__locals10, (Func<bool>)(() => !AcceptanceReport.op_Implicit(ThingCompUtility.TryGetComp<CompUsable>(((JobDriver)CS_0024_003C_003E8__locals10).TargetThingA).CanBeUsedBy(((JobDriver)CS_0024_003C_003E8__locals10).pawn, false, false))));
				_003C_003E2__current = Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)(((JobDriver)CS_0024_003C_003E8__locals10).TargetThingA.def.hasInteractionCell ? 4 : 2), false);
				_003C_003E1__state = 1;
				return true;
			case 1:
				_003C_003E1__state = -1;
				if (((LocalTargetInfo)(ref ((JobDriver)CS_0024_003C_003E8__locals10).job.targetB)).IsValid)
				{
					_003C_003E2__current = Toils_Haul.StartCarryThing((TargetIndex)1, false, false, false, true, false);
					_003C_003E1__state = 2;
					return true;
				}
				goto IL_0116;
			case 2:
				_003C_003E1__state = -1;
				_003C_003E2__current = ToilFailConditions.FailOnDespawnedOrNull<Toil>(Toils_Goto.GotoThing((TargetIndex)2, (PathEndMode)2, false), (TargetIndex)2);
				_003C_003E1__state = 3;
				return true;
			case 3:
			{
				_003C_003E1__state = -1;
				Toil val = ToilMaker.MakeToil("SetTarget");
				val.initAction = delegate
				{
					ThingCompUtility.TryGetComp<CompTargetable>(((JobDriver)CS_0024_003C_003E8__locals10).pawn.carryTracker.CarriedThing).selectedTarget = ((JobDriver)CS_0024_003C_003E8__locals10).TargetThingB;
				};
				_003C_003E2__current = val;
				_003C_003E1__state = 4;
				return true;
			}
			case 4:
				_003C_003E1__state = -1;
				goto IL_0116;
			case 5:
				_003C_003E1__state = -1;
				_003C_003E2__current = ((JobDriver_UseItem)CS_0024_003C_003E8__locals10).Use();
				_003C_003E1__state = 6;
				return true;
			case 6:
				{
					_003C_003E1__state = -1;
					return false;
				}
				IL_0116:
				_003C_003E2__current = CS_0024_003C_003E8__locals10.WaitDuration();
				_003C_003E1__state = 5;
				return true;
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
			_003CMakeNewToils_003Ed__4 result;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				result = this;
			}
			else
			{
				result = new _003CMakeNewToils_003Ed__4(0)
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

	private int useDuration = -1;

	public override void ExposeData()
	{
		((JobDriver_UseItem)this).ExposeData();
		Scribe_Values.Look<int>(ref useDuration, "useDuration", 0, false);
	}

	public override void Notify_Starting()
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0013: Unknown result type (might be due to invalid IL or missing references)
		((JobDriver_UseItem)this).Notify_Starting();
		LocalTargetInfo target = ((JobDriver)this).job.GetTarget((TargetIndex)1);
		useDuration = ThingCompUtility.TryGetComp<CompUsable>(((LocalTargetInfo)(ref target)).Thing).Props.useDuration;
	}

	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		//IL_0072: Unknown result type (might be due to invalid IL or missing references)
		CompUseConditionQuantity compUseConditionQuantity = ThingCompUtility.TryGetComp<CompUseConditionQuantity>(((JobDriver)this).TargetThingA);
		if (compUseConditionQuantity != null)
		{
			((JobDriver)this).job.count = compUseConditionQuantity.Props.quantity;
		}
		if (!ReservationUtility.Reserve(((JobDriver)this).pawn, ((JobDriver)this).job.targetA, ((JobDriver)this).job, 1, ((JobDriver)this).job.count, (ReservationLayerDef)null, errorOnFailed, false))
		{
			return false;
		}
		if (((LocalTargetInfo)(ref ((JobDriver)this).job.targetB)).IsValid && !ReservationUtility.Reserve(((JobDriver)this).pawn, ((JobDriver)this).job.targetB, ((JobDriver)this).job, 1, -1, (ReservationLayerDef)null, errorOnFailed, false))
		{
			return false;
		}
		return true;
	}

	[IteratorStateMachine(typeof(_003CMakeNewToils_003Ed__4))]
	protected override IEnumerable<Toil> MakeNewToils()
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CMakeNewToils_003Ed__4(-2)
		{
			_003C_003E4__this = this
		};
	}

	private Toil WaitDuration()
	{
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		//IL_0019: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_0041: Unknown result type (might be due to invalid IL or missing references)
		//IL_0042: Unknown result type (might be due to invalid IL or missing references)
		//IL_0047: Unknown result type (might be due to invalid IL or missing references)
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_006d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0075: Unknown result type (might be due to invalid IL or missing references)
		//IL_016c: Unknown result type (might be due to invalid IL or missing references)
		LocalTargetInfo target = ((JobDriver)this).job.GetTarget((TargetIndex)1);
		Thing thing = ((LocalTargetInfo)(ref target)).Thing;
		TargetIndex val = (TargetIndex)((!((LocalTargetInfo)(ref ((JobDriver)this).job.targetB)).IsValid) ? 1 : 2);
		LocalTargetInfo target2 = ((JobDriver)this).job.GetTarget(val);
		Toil val2 = Toils_General.WaitWith(val, useDuration, false, false, false, (TargetIndex)0, (PathEndMode)2);
		ToilEffects.WithProgressBarToilDelay(val2, val, false, -0.5f);
		ToilFailConditions.FailOnDespawnedNullOrForbidden<Toil>(val2, val);
		ToilFailConditions.FailOnCannotTouch<Toil>(val2, val, (PathEndMode)(((LocalTargetInfo)(ref target2)).Thing.def.hasInteractionCell ? 4 : 2));
		val2.handlingFacing = true;
		Thing obj = ((thing is ThingWithComps) ? thing : null);
		List<CompUseEffect> useComps = ((obj == null) ? null : ((ThingWithComps)obj).GetComps<CompUseEffect>()?.ToList());
		CompUsable val3 = ThingCompUtility.TryGetComp<CompUsable>(thing);
		if (((LocalTargetInfo)(ref ((JobDriver)this).job.targetB)).IsValid)
		{
			ToilFailConditions.FailOnDespawnedOrNull<Toil>(val2, (TargetIndex)2);
			CompTargetable obj2 = ThingCompUtility.TryGetComp<CompTargetable>(thing);
			if (((obj2 == null) ? ((bool?)null) : obj2.Props?.nonDownedPawnOnly) == true)
			{
				ToilFailConditions.FailOnDestroyedOrNull<Toil>(val2, (TargetIndex)2);
				ToilFailConditions.FailOnDowned<Toil>(val2, (TargetIndex)2);
			}
		}
		Mote warmupMote = null;
		if (val3 != null && val3.Props?.warmupMote != null)
		{
			warmupMote = MoteMaker.MakeAttachedOverlay(((LocalTargetInfo)(ref target2)).Thing, val3.Props.warmupMote, Vector3.zero, 1f, -1f);
		}
		val2.tickAction = delegate
		{
			//IL_0053: Unknown result type (might be due to invalid IL or missing references)
			if (useComps != null)
			{
				for (int num = useComps.Count - 1; num >= 0; num--)
				{
					useComps[num].PrepareTick();
				}
			}
			Mote obj3 = warmupMote;
			if (obj3 != null)
			{
				obj3.Maintain();
			}
			((JobDriver)this).pawn.rotationTracker.FaceTarget(target2);
		};
		return val2;
	}
}
