using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class BS_GeneSlimePower : Gene_Resource, IGeneResourceDrain
{
	[CompilerGenerated]
	private sealed class _003CGetGizmos_003Ed__38 : IEnumerable<Gizmo>, IEnumerable, IEnumerator<Gizmo>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private Gizmo _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		public BS_GeneSlimePower _003C_003E4__this;

		private IEnumerator<Gizmo> _003C_003E7__wrap1;

		Gizmo IEnumerator<Gizmo>.Current
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
		public _003CGetGizmos_003Ed__38(int _003C_003E1__state)
		{
			this._003C_003E1__state = _003C_003E1__state;
			_003C_003El__initialThreadId = Environment.CurrentManagedThreadId;
		}

		[DebuggerHidden]
		void IDisposable.Dispose()
		{
			switch (_003C_003E1__state)
			{
			case -3:
			case 1:
				try
				{
				}
				finally
				{
					_003C_003Em__Finally1();
				}
				break;
			case -4:
			case 2:
				try
				{
				}
				finally
				{
					_003C_003Em__Finally2();
				}
				break;
			}
			_003C_003E7__wrap1 = null;
			_003C_003E1__state = -2;
		}

		private bool MoveNext()
		{
			try
			{
				int num = _003C_003E1__state;
				BS_GeneSlimePower bS_GeneSlimePower = _003C_003E4__this;
				switch (num)
				{
				default:
					return false;
				case 0:
					_003C_003E1__state = -1;
					if (!((Gene)bS_GeneSlimePower).Active)
					{
						return false;
					}
					_003C_003E7__wrap1 = bS_GeneSlimePower._003C_003En__0().GetEnumerator();
					_003C_003E1__state = -3;
					goto IL_0081;
				case 1:
					_003C_003E1__state = -3;
					goto IL_0081;
				case 2:
					{
						_003C_003E1__state = -4;
						break;
					}
					IL_0081:
					if (_003C_003E7__wrap1.MoveNext())
					{
						Gizmo current = _003C_003E7__wrap1.Current;
						_003C_003E2__current = current;
						_003C_003E1__state = 1;
						return true;
					}
					_003C_003Em__Finally1();
					_003C_003E7__wrap1 = null;
					_003C_003E7__wrap1 = GeneResourceDrainUtility.GetResourceDrainGizmos((IGeneResourceDrain)(object)bS_GeneSlimePower).GetEnumerator();
					_003C_003E1__state = -4;
					break;
				}
				if (_003C_003E7__wrap1.MoveNext())
				{
					Gizmo current2 = _003C_003E7__wrap1.Current;
					_003C_003E2__current = current2;
					_003C_003E1__state = 2;
					return true;
				}
				_003C_003Em__Finally2();
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

		private void _003C_003Em__Finally2()
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
		IEnumerator<Gizmo> IEnumerable<Gizmo>.GetEnumerator()
		{
			_003CGetGizmos_003Ed__38 result;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				result = this;
			}
			else
			{
				result = new _003CGetGizmos_003Ed__38(0)
				{
					_003C_003E4__this = _003C_003E4__this
				};
			}
			return result;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<Gizmo>)this).GetEnumerator();
		}
	}

	public int offsetFromGenes;

	protected float cachedIncrease;

	private int tickDown = 100;

	private static HediffDef slimeHediffDef;

	public override float MinLevelForAlert => 0f;

	protected override Color BarColor
	{
		get
		{
			//IL_0006: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Unknown result type (might be due to invalid IL or missing references)
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			ColorInt val = new ColorInt(30, 60, 120);
			return ((ColorInt)(ref val)).ToColor;
		}
	}

	protected override Color BarHighlightColor
	{
		get
		{
			//IL_0009: Unknown result type (might be due to invalid IL or missing references)
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0011: Unknown result type (might be due to invalid IL or missing references)
			ColorInt val = new ColorInt(50, 100, 150);
			return ((ColorInt)(ref val)).ToColor;
		}
	}

	public override float InitialResourceMax => 1f;

	public override float MaxLevelOffset => 0f;

	public override float Max => ((Gene_Resource)this).InitialResourceMax + cachedIncrease;

	public Gene_Resource Resource => (Gene_Resource)(object)this;

	public Hediff SlimeHediff => GetSlimeHediff();

	public bool CanOffset => ((Gene)this).Active;

	public float ResourceLossPerDay => ((Gene)this).def.resourceLossPerDay;

	public Pawn Pawn => ((Gene)this).pawn;

	public string DisplayLabel => TaggedString.op_Implicit(((Gene)this).Label + " (" + Translator.Translate("Gene") + ")");

	public float DefaultTargetValue
	{
		get
		{
			if (!(((Gene_Resource)this).Max < 2f))
			{
				return 1.5f;
			}
			return 1f;
		}
	}

	public override void PostAdd()
	{
		((Gene)this).Reset();
	}

	public override void SetTargetValuePct(float val)
	{
		if (!float.IsNaN(val) && !float.IsNaN(base.max))
		{
			if (val > 1f)
			{
				val = 1f;
			}
			base.targetValue = val * ((Gene_Resource)this).Max;
		}
	}

	public override void Reset()
	{
		CalculateResourceMaxOffset();
		base.targetValue = DefaultTargetValue;
		base.cur = DefaultTargetValue;
		SlimeHediff.Severity = Mathf.Clamp(((Gene_Resource)this).Value, 0.05f, 9999f);
		RefreshCache();
	}

	public override void TickInterval(int delta)
	{
		((Gene)this).TickInterval(delta);
		tickDown -= delta;
		if (tickDown > 0)
		{
			return;
		}
		tickDown = 500;
		if (!((Gene)this).pawn.IsColonist && !((Gene)this).pawn.IsPrisonerOfColony)
		{
			base.targetValue = DefaultTargetValue;
		}
		RecalculateMax();
		float num = 0.125f;
		SlimeHediff.Severity = Mathf.Clamp(((Gene_Resource)this).Value, 0.05f, 9999f);
		bool flag = ((Gene)this).pawn?.needs?.food != null;
		float num2;
		if (!flag)
		{
			num2 = base.targetValue;
		}
		else
		{
			Pawn pawn = ((Gene)this).pawn;
			bool? obj;
			if (pawn == null)
			{
				obj = null;
			}
			else
			{
				Pawn_HealthTracker health = pawn.health;
				if (health == null)
				{
					obj = null;
				}
				else
				{
					HediffSet hediffSet = health.hediffSet;
					obj = ((hediffSet != null) ? new bool?(hediffSet.HasHediff(HediffDefOf.Malnutrition, false)) : ((bool?)null));
				}
			}
			bool? flag2 = obj;
			if (flag2 == true)
			{
				num2 = 0f;
			}
			else
			{
				Pawn pawn2 = ((Gene)this).pawn;
				if (pawn2 != null)
				{
					Pawn_NeedsTracker needs = pawn2.needs;
					float? obj2;
					if (needs == null)
					{
						obj2 = null;
					}
					else
					{
						Need_Food food = needs.food;
						obj2 = ((food != null) ? new float?(((Need)food).CurLevelPercentage) : ((float?)null));
					}
					if (obj2 > 0.29f)
					{
						num2 = base.targetValue;
						goto IL_0198;
					}
				}
				if (!(base.targetValue < base.cur))
				{
					return;
				}
				num2 = base.targetValue;
			}
		}
		goto IL_0198;
		IL_0198:
		num = Mathf.Min(num, Mathf.Abs(num2 - base.cur));
		float num3 = ((!(num2 > base.cur)) ? (0f - num) : num);
		float num4 = base.cur + num3;
		if (num2 > base.cur && base.cur + num3 > num2)
		{
			num4 = num2;
		}
		else if (num2 < base.cur && base.cur + num3 < num2)
		{
			num4 = num2;
		}
		if (Mathf.Abs(num4 - ((Gene_Resource)this).Value) < 0.01f)
		{
			((Gene_Resource)this).Value = num4;
			SlimeHediff.Severity = Mathf.Clamp(((Gene_Resource)this).Value, 0.05f, 9999f);
			return;
		}
		if (num4 < ((Gene_Resource)this).Value && flag)
		{
			Need_Food food2 = ((Gene)this).pawn.needs.food;
			((Need)food2).CurLevelPercentage = ((Need)food2).CurLevelPercentage + 0.2f;
		}
		else if (num4 > ((Gene_Resource)this).Value && flag)
		{
			((Need)((Gene)this).pawn.needs.food).CurLevelPercentage = Mathf.Max(0.1f, ((Need)((Gene)this).pawn.needs.food).CurLevelPercentage - 0.5f);
		}
		((Gene_Resource)this).Value = num4;
		SlimeHediff.Severity = Mathf.Clamp(((Gene_Resource)this).Value, 0.05f, 9999f);
		RefreshCache();
	}

	private void RefreshCache()
	{
		HumanoidPawnScaler.GetCache(((Gene)this).pawn, forceRefresh: true);
	}

	private void RecalculateMax()
	{
		float num = base.cur / base.max;
		CalculateResourceMaxOffset();
		if (!(Mathf.Abs(((Gene_Resource)this).Max - base.max) < 0.03f))
		{
			base.cur = Mathf.Clamp(base.cur, 0f, base.max);
			if (num > 0f)
			{
				((Gene_Resource)this).SetTargetValuePct(Mathf.Clamp(num, 0f, 1f));
			}
			SlimeHediff.Severity = Mathf.Clamp(((Gene_Resource)this).Value, 0.05f, 9999f);
		}
	}

	private float CalculateResourceMaxOffset()
	{
		float num = 0f;
		foreach (Gene allActiveGene in ((Gene)this).pawn.GetAllActiveGenes())
		{
			if (((Def)allActiveGene.def).HasModExtension<BS_GeneSlimeProps>())
			{
				num += ((Def)allActiveGene.def).GetModExtension<BS_GeneSlimeProps>().resourceMaxOffset;
			}
		}
		cachedIncrease = num;
		base.max = ((Gene_Resource)this).InitialResourceMax + num;
		return num;
	}

	public Hediff GetSlimeHediff()
	{
		if (slimeHediffDef == null)
		{
			IEnumerable<HediffDef> source = DefDatabase<HediffDef>.AllDefsListForReading.Where((HediffDef x) => ((Def)x).defName == "BS_SlimeMetabolism");
			if (source.Count() == 0)
			{
				Log.Error("BS_SlimeMetabolism hediff not found in the library.");
				return null;
			}
			slimeHediffDef = source.First();
		}
		if (!((Gene)this).pawn.health.hediffSet.HasHediff(slimeHediffDef, false))
		{
			((Gene)this).pawn.health.AddHediff(slimeHediffDef, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		}
		return ((Gene)this).pawn.health.hediffSet.GetFirstHediffOfDef(slimeHediffDef, false);
	}

	[IteratorStateMachine(typeof(_003CGetGizmos_003Ed__38))]
	public override IEnumerable<Gizmo> GetGizmos()
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CGetGizmos_003Ed__38(-2)
		{
			_003C_003E4__this = this
		};
	}

	public override void ExposeData()
	{
		((Gene_Resource)this).ExposeData();
		Scribe_Values.Look<float>(ref cachedIncrease, "cachedIncrease", 0f, false);
	}

	[CompilerGenerated]
	[DebuggerHidden]
	private IEnumerable<Gizmo> _003C_003En__0()
	{
		return ((Gene_Resource)this).GetGizmos();
	}
}
