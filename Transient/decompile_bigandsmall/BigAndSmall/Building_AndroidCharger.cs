using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;
using Verse.AI;

namespace BigAndSmall;

public class Building_AndroidCharger : Building, IRobotCharger
{
	[CompilerGenerated]
	private sealed class _003C_003Ec__DisplayClass27_0
	{
		public Building_AndroidCharger _003C_003E4__this;

		public Pawn selPawn;

		internal void _003CGetFloatMenuOptions_003Eb__0()
		{
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			Job val = JobMaker.MakeJob(BSDefs.BS_UseCharger, LocalTargetInfo.op_Implicit((Thing)(object)_003C_003E4__this));
			ReservationUtility.Reserve(selPawn, LocalTargetInfo.op_Implicit((Thing)(object)_003C_003E4__this), val, 1, -1, (ReservationLayerDef)null, true, true);
			selPawn.jobs.TryTakeOrderedJob(val, (JobTag?)(JobTag)0, false);
		}
	}

	[CompilerGenerated]
	private sealed class _003CGetFloatMenuOptions_003Ed__27 : IEnumerable<FloatMenuOption>, IEnumerable, IEnumerator<FloatMenuOption>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private FloatMenuOption _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		public Building_AndroidCharger _003C_003E4__this;

		private Pawn selPawn;

		public Pawn _003C_003E3__selPawn;

		private _003C_003Ec__DisplayClass27_0 _003C_003E8__1;

		private IEnumerator<FloatMenuOption> _003C_003E7__wrap1;

		FloatMenuOption IEnumerator<FloatMenuOption>.Current
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
		public _003CGetFloatMenuOptions_003Ed__27(int _003C_003E1__state)
		{
			this._003C_003E1__state = _003C_003E1__state;
			_003C_003El__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			int num = _003C_003E1__state;
			if (num == -3 || num == 1)
			{
				try
				{
				}
				finally
				{
					_003C_003Em__Finally1();
				}
			}
			_003C_003E8__1 = null;
			_003C_003E7__wrap1 = null;
			_003C_003E1__state = -2;
		}

		private bool MoveNext()
		{
			//IL_0100: Unknown result type (might be due to invalid IL or missing references)
			//IL_0124: Unknown result type (might be due to invalid IL or missing references)
			//IL_0129: Unknown result type (might be due to invalid IL or missing references)
			//IL_012d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0154: Unknown result type (might be due to invalid IL or missing references)
			//IL_015b: Expected O, but got Unknown
			//IL_0172: Unknown result type (might be due to invalid IL or missing references)
			//IL_0177: Unknown result type (might be due to invalid IL or missing references)
			//IL_017b: Unknown result type (might be due to invalid IL or missing references)
			try
			{
				int num = _003C_003E1__state;
				Building_AndroidCharger building_AndroidCharger = _003C_003E4__this;
				switch (num)
				{
				default:
					return false;
				case 0:
					_003C_003E1__state = -1;
					_003C_003E8__1 = new _003C_003Ec__DisplayClass27_0();
					_003C_003E8__1._003C_003E4__this = _003C_003E4__this;
					_003C_003E8__1.selPawn = selPawn;
					_003C_003E7__wrap1 = building_AndroidCharger._003C_003En__0(_003C_003E8__1.selPawn).GetEnumerator();
					_003C_003E1__state = -3;
					goto IL_00aa;
				case 1:
					_003C_003E1__state = -3;
					goto IL_00aa;
				case 2:
					{
						_003C_003E1__state = -1;
						break;
					}
					IL_00aa:
					if (_003C_003E7__wrap1.MoveNext())
					{
						FloatMenuOption current = _003C_003E7__wrap1.Current;
						_003C_003E2__current = current;
						_003C_003E1__state = 1;
						return true;
					}
					_003C_003Em__Finally1();
					_003C_003E7__wrap1 = null;
					if (((Thing)_003C_003E8__1.selPawn).Faction == Faction.OfPlayerSilentFail && building_AndroidCharger.CanUseChargers(_003C_003E8__1.selPawn) && ReachabilityUtility.CanReach(_003C_003E8__1.selPawn, LocalTargetInfo.op_Implicit((Thing)(object)building_AndroidCharger), (PathEndMode)2, (Danger)3, false, false, (TraverseMode)0) && building_AndroidCharger.user == null)
					{
						TaggedString val = Translator.Translate("BS_UseAndroidCharger");
						FloatMenuOption val3 = new FloatMenuOption(TaggedString.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst()), (Action)delegate
						{
							//IL_000b: Unknown result type (might be due to invalid IL or missing references)
							//IL_0022: Unknown result type (might be due to invalid IL or missing references)
							Job val2 = JobMaker.MakeJob(BSDefs.BS_UseCharger, LocalTargetInfo.op_Implicit((Thing)(object)_003C_003E8__1._003C_003E4__this));
							ReservationUtility.Reserve(_003C_003E8__1.selPawn, LocalTargetInfo.op_Implicit((Thing)(object)_003C_003E8__1._003C_003E4__this), val2, 1, -1, (ReservationLayerDef)null, true, true);
							_003C_003E8__1.selPawn.jobs.TryTakeOrderedJob(val2, (JobTag?)(JobTag)0, false);
						}, (MenuOptionPriority)4, (Action<Rect>)null, (Thing)null, 0f, (Func<Rect, bool>)null, (WorldObject)null, true, 0);
						if (!building_AndroidCharger.PowerGridSufficientPowerToStart)
						{
							val3.Disabled = true;
							val = Translator.Translate("BS_InsufficientBatteryPower");
							val3.Label = TaggedString.op_Implicit(((TaggedString)(ref val)).CapitalizeFirst());
						}
						_003C_003E2__current = val3;
						_003C_003E1__state = 2;
						return true;
					}
					break;
				}
				return false;
			}
			catch
			{
				//try-fault
				((IDisposable)this).Dispose();
				throw;
			}
		}

		bool IEnumerator.MoveNext()
		{
			//ILSpy generated this explicit interface implementation from .override directive in MoveNext
			return this.MoveNext();
		}

		private void _003C_003Em__Finally1()
		{
			_003C_003E1__state = -1;
			if (_003C_003E7__wrap1 != null)
			{
				_003C_003E7__wrap1.Dispose();
			}
		}

		[DebuggerHidden]
		void IEnumerator.Reset()
		{
			throw new NotSupportedException();
		}

		[DebuggerHidden]
		IEnumerator<FloatMenuOption> IEnumerable<FloatMenuOption>.GetEnumerator()
		{
			_003CGetFloatMenuOptions_003Ed__27 _003CGetFloatMenuOptions_003Ed__;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				_003CGetFloatMenuOptions_003Ed__ = this;
			}
			else
			{
				_003CGetFloatMenuOptions_003Ed__ = new _003CGetFloatMenuOptions_003Ed__27(0)
				{
					_003C_003E4__this = _003C_003E4__this
				};
			}
			_003CGetFloatMenuOptions_003Ed__.selPawn = _003C_003E3__selPawn;
			return _003CGetFloatMenuOptions_003Ed__;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<FloatMenuOption>)this).GetEnumerator();
		}
	}

	private const int StandardBatteryWd = 600;

	private const int BaseWdPer1Food = 400;

	private const int TicksPerHour = 2500;

	private const float MinimumBatteryChargeToUse = 294f;

	public const float BaseTransferSpeed = 4f;

	public const float BasePowerPerDay = 9600f;

	private Pawn user;

	private float userChargingEfficiency = 1f;

	private float extraSpeedFactor = 1f;

	private float pawnFoodFallRate;

	private int lastTick = -1;

	public CompPowerTrader Power => ThingCompUtility.TryGetComp<CompPowerTrader>((Thing)(object)this);

	public bool IsPowered => Power.PowerOn;

	protected bool PowerGridSufficientPowerToStart => ((CompPower)Power).PowerNet.CurrentStoredEnergy() >= 294f;

	protected bool PowerGridSufficientPowerToContinue => ((CompPower)Power).PowerNet.CurrentStoredEnergy() >= 10f;

	public float GetPowerPerDay(float factor)
	{
		return 9600f * factor / StatExtension.GetStatValue((Thing)(object)this, StatDefOf.WorkTableEfficiencyFactor, false, 1000) / userChargingEfficiency;
	}

	public float GetWorkSpeedFactor()
	{
		return 4f * userChargingEfficiency * extraSpeedFactor * StatExtension.GetStatValue((Thing)(object)this, StatDefOf.WorkTableWorkSpeedFactor, false, 1000);
	}

	public bool PawnCanUse(Pawn pawn, bool isNew)
	{
		CompPowerTrader power = Power;
		if (((power != null) ? ((CompPower)power).PowerNet : null) == null || !IsPowered)
		{
			return false;
		}
		if (user != pawn && !CanUseChargers(pawn))
		{
			return false;
		}
		if (user == null || user == pawn)
		{
			if (!isNew)
			{
				return PowerGridSufficientPowerToContinue;
			}
			return PowerGridSufficientPowerToStart;
		}
		return false;
	}

	public virtual bool CanUseChargers(Pawn pawn)
	{
		return pawn.GetCachePrepatched().canUseChargers;
	}

	protected override void TickInterval(int delta)
	{
		if (lastTick < 0)
		{
			lastTick = Find.TickManager.TicksGame;
		}
		Pawn val = user;
		if (val != null)
		{
			int ticksGame = Find.TickManager.TicksGame;
			if (val.CurJobDef == BSDefs.BS_UseCharger)
			{
				int ticksPassed = ticksGame - lastTick;
				DoCharge(val, ticksPassed);
			}
			else
			{
				user = null;
				Power.PowerOutput = 0f;
			}
			lastTick = ticksGame;
		}
	}

	public void StartCharging(Pawn pawn)
	{
		user = pawn;
		userChargingEfficiency = StatExtension.GetStatValue((Thing)(object)pawn, BSDefs.BS_BatteryCharging, true, 500);
		extraSpeedFactor = 1f;
		float bodySize = pawn.BodySize;
		if (bodySize > 1f)
		{
			extraSpeedFactor = bodySize;
		}
		try
		{
			pawnFoodFallRate = pawn.needs.food.FoodFallPerTickAssumingCategory((HungerCategory)1, true);
		}
		catch
		{
			Log.ErrorOnce($"Error getting food fall rate for {pawn}. Setting to 0.", 81410);
			pawnFoodFallRate = 0f;
		}
		lastTick = Find.TickManager.TicksGame;
	}

	public void StopCharging()
	{
		user = null;
		Power.PowerOutput = 0f;
	}

	protected virtual void DoCharge(Pawn pawn, int ticksPassed)
	{
		if (!IsPowered)
		{
			pawn.jobs.EndCurrentJob((JobCondition)4, true, true);
		}
		float workSpeedFactor = GetWorkSpeedFactor();
		Power.PowerOutput = 0f - GetPowerPerDay(workSpeedFactor);
		Need_Food food = pawn.needs.food;
		if (food != null && food != null && ((Need)food).CurLevelPercentage < 1f)
		{
			float num = (float)ticksPassed / 2500f;
			((Need)food).CurLevel = ((Need)food).CurLevel + workSpeedFactor * num;
			((Need)food).CurLevel = ((Need)food).CurLevel + pawnFoodFallRate * (float)ticksPassed;
			if (((Need)food).CurLevelPercentage >= 1f)
			{
				pawn.jobs.EndCurrentJob((JobCondition)2, true, true);
			}
		}
	}

	[IteratorStateMachine(typeof(_003CGetFloatMenuOptions_003Ed__27))]
	public override IEnumerable<FloatMenuOption> GetFloatMenuOptions(Pawn selPawn)
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CGetFloatMenuOptions_003Ed__27(-2)
		{
			_003C_003E4__this = this,
			_003C_003E3__selPawn = selPawn
		};
	}

	public override void ExposeData()
	{
		((Building)this).ExposeData();
		Scribe_References.Look<Pawn>(ref user, "userOfBuilding", false);
		Scribe_Values.Look<float>(ref userChargingEfficiency, "currentUserChargingEfficiency", 1f, false);
		Scribe_Values.Look<float>(ref extraSpeedFactor, "extraSpeedFactor", 1f, false);
		Scribe_Values.Look<float>(ref pawnFoodFallRate, "pawnFoodFallRate", 0f, false);
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<FloatMenuOption> _003C_003En__0(Pawn selPawn)
	{
		return ((ThingWithComps)this).GetFloatMenuOptions(selPawn);
	}
}
