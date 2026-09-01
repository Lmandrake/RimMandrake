using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace BigAndSmall;

[HarmonyPatch]
public static class LovinPatches
{
	[CompilerGenerated]
	private sealed class _003CJobDriver_Lovin_003Ed__1 : IEnumerable<Toil>, IEnumerable, IEnumerator<Toil>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private Toil _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		private JobDriver_Lovin __instance;

		public JobDriver_Lovin _003C_003E3____instance;

		private TargetIndex ___PartnerInd;

		public TargetIndex _003C_003E3_____PartnerInd;

		private IEnumerable<Toil> __result;

		public IEnumerable<Toil> _003C_003E3____result;

		private IEnumerator<Toil> _003C_003E7__wrap1;

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
		public _003CJobDriver_Lovin_003Ed__1(int _003C_003E1__state)
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
			_003C_003E7__wrap1 = null;
			_003C_003E1__state = -2;
		}

		private bool MoveNext()
		{
			//IL_0037: Unknown result type (might be due to invalid IL or missing references)
			//IL_003c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0046: Unknown result type (might be due to invalid IL or missing references)
			//IL_004c: Expected O, but got Unknown
			try
			{
				switch (_003C_003E1__state)
				{
				default:
					return false;
				case 0:
					_003C_003E1__state = -1;
					try
					{
						Pawn pawn = ((JobDriver)__instance).pawn;
						Pawn val = (Pawn)(Thing)((JobDriver)__instance).job.GetTarget(___PartnerInd);
						if (pawn != null && val != null)
						{
							__result = LovinSoulfeed(__result, pawn, val);
							if (!GeneUtility.IsBloodfeeder(val))
							{
								__result = LovinBloodFeed(__result, pawn, val);
							}
						}
					}
					catch (Exception ex)
					{
						Log.Warning(ex.Message + "\n" + ex.StackTrace);
					}
					_003C_003E7__wrap1 = __result.GetEnumerator();
					_003C_003E1__state = -3;
					break;
				case 1:
					_003C_003E1__state = -3;
					break;
				}
				if (_003C_003E7__wrap1.MoveNext())
				{
					Toil current = _003C_003E7__wrap1.Current;
					_003C_003E2__current = current;
					_003C_003E1__state = 1;
					return true;
				}
				_003C_003Em__Finally1();
				_003C_003E7__wrap1 = null;
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
		IEnumerator<Toil> IEnumerable<Toil>.GetEnumerator()
		{
			//IL_0043: Unknown result type (might be due to invalid IL or missing references)
			//IL_0048: Unknown result type (might be due to invalid IL or missing references)
			_003CJobDriver_Lovin_003Ed__1 _003CJobDriver_Lovin_003Ed__;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				_003CJobDriver_Lovin_003Ed__ = this;
			}
			else
			{
				_003CJobDriver_Lovin_003Ed__ = new _003CJobDriver_Lovin_003Ed__1(0);
			}
			_003CJobDriver_Lovin_003Ed__.__result = _003C_003E3____result;
			_003CJobDriver_Lovin_003Ed__.__instance = _003C_003E3____instance;
			_003CJobDriver_Lovin_003Ed__.___PartnerInd = _003C_003E3_____PartnerInd;
			return _003CJobDriver_Lovin_003Ed__;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<Toil>)this).GetEnumerator();
		}
	}

	[CompilerGenerated]
	private sealed class _003CVEHighmates_Lovin_003Ed__0 : IEnumerable<Toil>, IEnumerable, IEnumerator<Toil>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private Toil _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		private JobDriver __instance;

		public JobDriver _003C_003E3____instance;

		private IEnumerable<Toil> __result;

		public IEnumerable<Toil> _003C_003E3____result;

		private IEnumerator<Toil> _003C_003E7__wrap1;

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
		public _003CVEHighmates_Lovin_003Ed__0(int _003C_003E1__state)
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
			_003C_003E7__wrap1 = null;
			_003C_003E1__state = -2;
		}

		private bool MoveNext()
		{
			//IL_0037: Unknown result type (might be due to invalid IL or missing references)
			//IL_0041: Unknown result type (might be due to invalid IL or missing references)
			//IL_0047: Expected O, but got Unknown
			try
			{
				switch (_003C_003E1__state)
				{
				default:
					return false;
				case 0:
					_003C_003E1__state = -1;
					try
					{
						Pawn pawn = __instance.pawn;
						Pawn val = (Pawn)(Thing)__instance.job.GetTarget((TargetIndex)1);
						if (pawn != null && val != null)
						{
							__result = LovinSoulfeed(__result, pawn, val);
							if (!GeneUtility.IsBloodfeeder(val))
							{
								__result = LovinBloodFeed(__result, pawn, val);
							}
						}
					}
					catch (Exception ex)
					{
						Log.Warning(ex.Message + "\n" + ex.StackTrace);
					}
					_003C_003E7__wrap1 = __result.GetEnumerator();
					_003C_003E1__state = -3;
					break;
				case 1:
					_003C_003E1__state = -3;
					break;
				}
				if (_003C_003E7__wrap1.MoveNext())
				{
					Toil current = _003C_003E7__wrap1.Current;
					_003C_003E2__current = current;
					_003C_003E1__state = 1;
					return true;
				}
				_003C_003Em__Finally1();
				_003C_003E7__wrap1 = null;
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
		IEnumerator<Toil> IEnumerable<Toil>.GetEnumerator()
		{
			_003CVEHighmates_Lovin_003Ed__0 _003CVEHighmates_Lovin_003Ed__;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				_003CVEHighmates_Lovin_003Ed__ = this;
			}
			else
			{
				_003CVEHighmates_Lovin_003Ed__ = new _003CVEHighmates_Lovin_003Ed__0(0);
			}
			_003CVEHighmates_Lovin_003Ed__.__result = _003C_003E3____result;
			_003CVEHighmates_Lovin_003Ed__.__instance = _003C_003E3____instance;
			return _003CVEHighmates_Lovin_003Ed__;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<Toil>)this).GetEnumerator();
		}
	}

	[IteratorStateMachine(typeof(_003CVEHighmates_Lovin_003Ed__0))]
	public static IEnumerable<Toil> VEHighmates_Lovin(IEnumerable<Toil> __result, JobDriver __instance)
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CVEHighmates_Lovin_003Ed__0(-2)
		{
			_003C_003E3____result = __result,
			_003C_003E3____instance = __instance
		};
	}

	[IteratorStateMachine(typeof(_003CJobDriver_Lovin_003Ed__1))]
	[HarmonyPatch(typeof(JobDriver_Lovin), "MakeNewToils")]
	[HarmonyPostfix]
	public static IEnumerable<Toil> JobDriver_Lovin(IEnumerable<Toil> __result, JobDriver_Lovin __instance, TargetIndex ___PartnerInd)
	{
		//IL_0016: Unknown result type (might be due to invalid IL or missing references)
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CJobDriver_Lovin_003Ed__1(-2)
		{
			_003C_003E3____result = __result,
			_003C_003E3____instance = __instance,
			_003C_003E3_____PartnerInd = ___PartnerInd
		};
	}

	public static void SiphonAction(Pawn initiator, Pawn target)
	{
		//IL_0080: Unknown result type (might be due to invalid IL or missing references)
		//IL_0085: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ab: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b0: Unknown result type (might be due to invalid IL or missing references)
		//IL_00bf: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ca: Expected O, but got Unknown
		if (target != null && initiator != null)
		{
			IEnumerable<SiphonSoul> enumerable = from x in initiator.GetAllPawnExtensions()
				select x.siphonSoul into x
				where x != null && x.type == SiphonType.Lovin
				select x;
			if (enumerable.Any())
			{
				SiphonSoul parms = enumerable.FuseAll(SiphonType.Lovin);
				float num = Soul.GetOrAddSoulCollector(initiator).AddPawnSoul(target, parms);
				Messages.Message(new Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_LovinSoulFeed", NamedArgument.op_Implicit(initiator.NameShortColored), NamedArgument.op_Implicit(target.NameShortColored), NamedArgument.op_Implicit($"{num * 100f:f1}%"))), MessageTypeDefOf.NeutralEvent), true);
			}
		}
	}

	public static IEnumerable<Toil> LovinSoulfeed(IEnumerable<Toil> __result, Pawn initiator, Pawn target)
	{
		if ((from x in initiator.GetAllPawnExtensions()
			select x.siphonSoul into x
			where x != null && x.type == SiphonType.Lovin
			select x).Any())
		{
			__result.Last();
			Toil val = ToilMaker.MakeToil("Post-lovin' soul suckin'");
			val.AddFinishAction((Action)delegate
			{
				SiphonAction(initiator, target);
			});
			__result = CollectionExtensions.AddItem<Toil>(__result, val);
		}
		return __result;
	}

	public unsafe static IEnumerable<Toil> LovinBloodFeed(IEnumerable<Toil> __result, Pawn pawn, Pawn partner)
	{
		if (GeneHelpers.GetActiveGenesByNames(pawn, new List<string>(1) { "VU_VampireLover" }).Count > 0)
		{
			IEnumerable<Ability> source = pawn.abilities.AllAbilitiesForReading.Where((Ability x) => x.comps != null && x.comps.Where((AbilityComp y) => y is CompAbilityEffect_BloodfeederBite).Count() > 0);
			List<Gene> activeGenesByName = GeneHelpers.GetActiveGenesByName(pawn, "VU_LethalLover");
			float hemogenTriggerLevel2 = 0.55f;
			if (activeGenesByName.Count > 0)
			{
				hemogenTriggerLevel2 = 0.75f;
			}
			if (source.Count() > 0)
			{
				__result.Last();
				Ability bite2 = source.Last();
				Toil val = ToilMaker.MakeToil("Post-lovin' feedin'");
				ToilFailConditions.FailOn<Toil>(val, new Func<bool>(partner, (nint)(delegate*<Pawn, bool>)(&GeneUtility.IsBloodfeeder)));
				val.AddFinishAction((Action)delegate
				{
					Feedin(pawn, partner, hemogenTriggerLevel2, bite2);
				});
				__result = CollectionExtensions.AddItem<Toil>(__result, val);
			}
		}
		return __result;
		static void Feedin(Pawn pawn, Pawn partner, float hemogenTriggerLevel, Ability bite)
		{
			//IL_0037: Unknown result type (might be due to invalid IL or missing references)
			//IL_003d: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0052: Unknown result type (might be due to invalid IL or missing references)
			//IL_0058: Unknown result type (might be due to invalid IL or missing references)
			//IL_005d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0062: Unknown result type (might be due to invalid IL or missing references)
			//IL_0071: Unknown result type (might be due to invalid IL or missing references)
			//IL_007c: Expected O, but got Unknown
			if (pawn != null && partner != null)
			{
				Pawn_GeneTracker genes = pawn.genes;
				if (((Gene_Resource)((genes != null) ? genes.GetFirstGeneOfType<Gene_Hemogen>() : null)).Value < hemogenTriggerLevel)
				{
					foreach (CompAbilityEffect effectComp in bite.EffectComps)
					{
						effectComp.Apply(LocalTargetInfo.op_Implicit((Thing)(object)partner), LocalTargetInfo.op_Implicit((Thing)(object)pawn));
						Messages.Message(new Message(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("BS_LovinnBloodfeed", NamedArgument.op_Implicit(pawn.NameShortColored), NamedArgument.op_Implicit(partner.NameShortColored))), MessageTypeDefOf.NegativeHealthEvent), true);
					}
				}
			}
		}
	}
}
