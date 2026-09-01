using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using Verse;
using Verse.AI;

namespace BigAndSmall;

public class JobDriver_UseCharger : JobDriver
{
	[CompilerGenerated]
	private sealed class _003CMakeNewToils_003Ed__3 : IEnumerable<Toil>, IEnumerable, IEnumerator<Toil>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private Toil _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		public JobDriver_UseCharger _003C_003E4__this;

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
		public _003CMakeNewToils_003Ed__3(int _003C_003E1__state)
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
			//IL_007b: Unknown result type (might be due to invalid IL or missing references)
			int num = _003C_003E1__state;
			JobDriver_UseCharger CS_0024_003C_003E8__locals11 = _003C_003E4__this;
			switch (num)
			{
			default:
				return false;
			case 0:
				_003C_003E1__state = -1;
				ToilFailConditions.FailOnDespawnedOrNull<JobDriver_UseCharger>(CS_0024_003C_003E8__locals11, (TargetIndex)1);
				ToilFailConditions.FailOn<JobDriver_UseCharger>(CS_0024_003C_003E8__locals11, (Func<bool>)(() => !CS_0024_003C_003E8__locals11.Charger.PawnCanUse(((JobDriver)CS_0024_003C_003E8__locals11).pawn, isNew: false)));
				_003C_003E2__current = ToilFailConditions.FailOnForbidden<Toil>(ToilFailConditions.FailOnDespawnedOrNull<Toil>(Toils_Goto.GotoThing((TargetIndex)1, (PathEndMode)2, false), (TargetIndex)1), (TargetIndex)1);
				_003C_003E1__state = 1;
				return true;
			case 1:
			{
				_003C_003E1__state = -1;
				Toil val = ToilMaker.MakeToil("MakeNewToils");
				val.defaultCompleteMode = (ToilCompleteMode)5;
				val.initAction = delegate
				{
					CS_0024_003C_003E8__locals11.Charger.StartCharging(((JobDriver)CS_0024_003C_003E8__locals11).pawn);
				};
				val.handlingFacing = true;
				val.tickIntervalAction = (Action<int>)Delegate.Combine(val.tickIntervalAction, (Action<int>)delegate
				{
					//IL_0011: Unknown result type (might be due to invalid IL or missing references)
					//IL_0016: Unknown result type (might be due to invalid IL or missing references)
					((JobDriver)CS_0024_003C_003E8__locals11).pawn.rotationTracker.FaceTarget(LocalTargetInfo.op_Implicit(((Thing)CS_0024_003C_003E8__locals11.Charger).Position));
					if ((double)((Need)((JobDriver)CS_0024_003C_003E8__locals11).pawn.needs.food).CurLevelPercentage >= 1.0)
					{
						CS_0024_003C_003E8__locals11.Charger.StopCharging();
						((JobDriver)CS_0024_003C_003E8__locals11).ReadyForNextToil();
					}
				});
				_003C_003E2__current = val;
				_003C_003E1__state = 2;
				return true;
			}
			case 2:
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
			_003CMakeNewToils_003Ed__3 result;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				result = this;
			}
			else
			{
				result = new _003CMakeNewToils_003Ed__3(0)
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

	public Building_AndroidCharger Charger => (Building_AndroidCharger)(object)((LocalTargetInfo)(ref base.job.targetA)).Thing;

	public override bool TryMakePreToilReservations(bool errorOnFailed)
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		return ReservationUtility.Reserve(base.pawn, LocalTargetInfo.op_Implicit((Thing)(object)Charger), base.job, 1, -1, (ReservationLayerDef)null, errorOnFailed, false);
	}

	[IteratorStateMachine(typeof(_003CMakeNewToils_003Ed__3))]
	protected override IEnumerable<Toil> MakeNewToils()
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CMakeNewToils_003Ed__3(-2)
		{
			_003C_003E4__this = this
		};
	}
}
