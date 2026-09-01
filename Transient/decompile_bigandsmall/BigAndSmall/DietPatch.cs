using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.CompilerServices;
using BigAndSmall.FilteredLists;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace BigAndSmall;

[HarmonyPatch]
public static class DietPatch
{
	[CompilerGenerated]
	private sealed class _003CPostIngested_Transpiler_003Ed__3 : IEnumerable<CodeInstruction>, IEnumerable, IEnumerator<CodeInstruction>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private CodeInstruction _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		private IEnumerable<CodeInstruction> instructions;

		public IEnumerable<CodeInstruction> _003C_003E3__instructions;

		private List<CodeInstruction> _003Ccodes_003E5__2;

		private int _003Ci_003E5__3;

		CodeInstruction IEnumerator<CodeInstruction>.Current
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
		public _003CPostIngested_Transpiler_003Ed__3(int _003C_003E1__state)
		{
			this._003C_003E1__state = _003C_003E1__state;
			_003C_003El__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			_003Ccodes_003E5__2 = null;
			_003C_003E1__state = -2;
		}

		private bool MoveNext()
		{
			//IL_00da: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e4: Expected O, but got Unknown
			//IL_012e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0138: Expected O, but got Unknown
			switch (_003C_003E1__state)
			{
			default:
				return false;
			case 0:
				_003C_003E1__state = -1;
				_003Ccodes_003E5__2 = instructions.ToList();
				_003Ci_003E5__3 = 0;
				break;
			case 1:
				_003C_003E1__state = -1;
				_003C_003E2__current = new CodeInstruction(OpCodes.Ldc_R4, (object)0.8f);
				_003C_003E1__state = 2;
				return true;
			case 2:
				_003C_003E1__state = -1;
				_003C_003E2__current = new CodeInstruction(OpCodes.Call, (object)typeof(Mathf).GetMethod("Max", new Type[2]
				{
					typeof(float),
					typeof(float)
				}));
				_003C_003E1__state = 3;
				return true;
			case 3:
				_003C_003E1__state = -1;
				goto IL_0171;
			case 4:
				{
					_003C_003E1__state = -1;
					goto IL_0171;
				}
				IL_0171:
				_003Ci_003E5__3++;
				break;
			}
			if (_003Ci_003E5__3 < _003Ccodes_003E5__2.Count)
			{
				if (_003Ccodes_003E5__2[_003Ci_003E5__3].opcode == OpCodes.Callvirt && _003Ccodes_003E5__2[_003Ci_003E5__3].operand is MethodInfo { Name: "get_BodySize" })
				{
					_003C_003E2__current = _003Ccodes_003E5__2[_003Ci_003E5__3];
					_003C_003E1__state = 1;
					return true;
				}
				_003C_003E2__current = _003Ccodes_003E5__2[_003Ci_003E5__3];
				_003C_003E1__state = 4;
				return true;
			}
			return false;
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
		IEnumerator<CodeInstruction> IEnumerable<CodeInstruction>.GetEnumerator()
		{
			_003CPostIngested_Transpiler_003Ed__3 _003CPostIngested_Transpiler_003Ed__;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				_003CPostIngested_Transpiler_003Ed__ = this;
			}
			else
			{
				_003CPostIngested_Transpiler_003Ed__ = new _003CPostIngested_Transpiler_003Ed__3(0);
			}
			_003CPostIngested_Transpiler_003Ed__.instructions = _003C_003E3__instructions;
			return _003CPostIngested_Transpiler_003Ed__;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<CodeInstruction>)this).GetEnumerator();
		}
	}

	public static bool ShouldSkipDietChecks(Pawn p)
	{
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Invalid comparison between Unknown and I4
		if (p == null)
		{
			return true;
		}
		if (WildManUtility.IsWildMan(p))
		{
			return true;
		}
		if (p.IsMutant)
		{
			return true;
		}
		if ((int)p.DevelopmentalStage == 2)
		{
			return true;
		}
		return false;
	}

	[HarmonyPatch(typeof(FoodUtility), "WillEat", new Type[]
	{
		typeof(Pawn),
		typeof(ThingDef),
		typeof(Pawn),
		typeof(bool),
		typeof(bool)
	})]
	[HarmonyPrefix]
	[HarmonyPriority(700)]
	public static bool WillEatDef_Prefix(ref bool __result, Pawn p, ThingDef food, Pawn getter, bool careIfNotAcceptableForTitle, bool allowVenerated)
	{
		if (food == null)
		{
			return true;
		}
		if (ShouldSkipDietChecks(p))
		{
			return true;
		}
		BSCache cache = p.GetCache();
		if (cache != null)
		{
			if (cache.isBloodFeeder)
			{
				return true;
			}
			if (cache.willEatDef.TryGetValue(food, out var value))
			{
				if (!value)
				{
					__result = false;
					return false;
				}
				return true;
			}
			if (food.GetFilterForFoodThingDef(cache).Denied())
			{
				cache.willEatDef[food] = false;
				__result = false;
				return false;
			}
			cache.willEatDef[food] = true;
			return true;
		}
		return true;
	}

	[HarmonyPatch(typeof(FoodUtility), "WillEat", new Type[]
	{
		typeof(Pawn),
		typeof(Thing),
		typeof(Pawn),
		typeof(bool),
		typeof(bool)
	})]
	[HarmonyPrefix]
	[HarmonyPriority(10000)]
	public static bool WillDietPermitEatingThing(ref bool __result, Pawn p, Thing food, Pawn getter, bool careIfNotAcceptableForTitle, bool allowVenerated)
	{
		if (food == null)
		{
			return true;
		}
		if (ShouldSkipDietChecks(p))
		{
			return true;
		}
		if (((Thing)p).Spawned)
		{
			BSCache cache = p.GetCache();
			if (cache != null && cache.isHumanlike)
			{
				if (cache.isBloodFeeder)
				{
					return true;
				}
				if (food.FilterForFoodThing(cache).Denied())
				{
					__result = false;
					return false;
				}
				if (cache.willEatDef.TryGetValue(food.def, out var value))
				{
					if (!value)
					{
						__result = false;
						return false;
					}
					return true;
				}
				ThingDef def = food.def;
				if (def.GetFilterForFoodThingDef(cache).Denied())
				{
					cache.willEatDef[def] = false;
					__result = false;
					return false;
				}
				cache.willEatDef[def] = true;
			}
		}
		return true;
	}

	/// <summary>
	/// This is a patch that fixes so small characters don't overdose so easily.
	///
	/// It will also make cats and whatever not overdose on beer all the time, but arguably that's a good thing, because it... was stupid.
	/// </summary>
	/// <returns></returns>
	[IteratorStateMachine(typeof(_003CPostIngested_Transpiler_003Ed__3))]
	[HarmonyPatch(typeof(CompDrug), "PostIngested")]
	[HarmonyTranspiler]
	public static IEnumerable<CodeInstruction> PostIngested_Transpiler(IEnumerable<CodeInstruction> instructions)
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CPostIngested_Transpiler_003Ed__3(-2)
		{
			_003C_003E3__instructions = instructions
		};
	}

	[HarmonyPatch(typeof(Thing), "Ingested", new Type[]
	{
		typeof(Pawn),
		typeof(float)
	})]
	[HarmonyPostfix]
	public static void Ingested_Postfix(Thing __instance, ref float __result, Pawn ingester, float nutritionWanted)
	{
		bool __result2 = true;
		WillDietPermitEatingThing(ref __result2, ingester, __instance, null, careIfNotAcceptableForTitle: false, allowVenerated: false);
		if (ingester == null || !((Thing)ingester).Spawned)
		{
			return;
		}
		BSCache cachePrepatched = ingester.GetCachePrepatched();
		if (cachePrepatched != null && cachePrepatched.isHumanlike && !__result2 && ((Thing)ingester).Faction == Faction.OfPlayerSilentFail)
		{
			__result = 0f;
			Log.Warning($"[BigAndSmall] {((ingester != null) ? ingester.Name : null)} ate {((Def)(__instance?.def?)).defName} which their gene-diet requirements does not permit" + "\nIf this was not due to the player forcing them to then something went wrong.");
			if (((Thing)ingester).Spawned)
			{
				ingester.jobs.StartJob(JobMaker.MakeJob(JobDefOf.Vomit), (JobCondition)16, (ThinkNode)null, false, true, (ThinkTreeDef)null, (JobTag?)null, false, false, (bool?)null, false, true, false);
			}
			else
			{
				((Need)ingester.needs.food).CurLevel = -0.25f;
			}
		}
	}
}
