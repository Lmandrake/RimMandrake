using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace Outposts;

public static class Utils
{
	[CompilerGenerated]
	private sealed class _003CMake_003Ed__7 : IEnumerable<Thing>, IEnumerable, IEnumerator<Thing>, IDisposable, IEnumerator
	{
		private int _003C_003E1__state;

		private Thing _003C_003E2__current;

		private int _003C_003El__initialThreadId;

		private ThingDef thingDef;

		public ThingDef _003C_003E3__thingDef;

		private ThingDef stuff;

		public ThingDef _003C_003E3__stuff;

		private int count;

		public int _003C_003E3__count;

		Thing IEnumerator<Thing>.Current
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
		public _003CMake_003Ed__7(int _003C_003E1__state)
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
			Thing val2;
			switch (_003C_003E1__state)
			{
			default:
				return false;
			case 0:
				_003C_003E1__state = -1;
				goto IL_0076;
			case 1:
				_003C_003E1__state = -1;
				count -= thingDef.stackLimit;
				goto IL_0076;
			case 2:
				{
					_003C_003E1__state = -1;
					return false;
				}
				IL_0076:
				if (count > thingDef.stackLimit)
				{
					Thing val = ThingMaker.MakeThing(thingDef, stuff);
					val.stackCount = thingDef.stackLimit;
					_003C_003E2__current = val;
					_003C_003E1__state = 1;
					return true;
				}
				val2 = ThingMaker.MakeThing(thingDef, stuff);
				val2.stackCount = count;
				_003C_003E2__current = val2;
				_003C_003E1__state = 2;
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
		IEnumerator<Thing> IEnumerable<Thing>.GetEnumerator()
		{
			_003CMake_003Ed__7 _003CMake_003Ed__;
			if (_003C_003E1__state == -2 && _003C_003El__initialThreadId == Environment.CurrentManagedThreadId)
			{
				_003C_003E1__state = 0;
				_003CMake_003Ed__ = this;
			}
			else
			{
				_003CMake_003Ed__ = new _003CMake_003Ed__7(0);
			}
			_003CMake_003Ed__.thingDef = _003C_003E3__thingDef;
			_003CMake_003Ed__.count = _003C_003E3__count;
			_003CMake_003Ed__.stuff = _003C_003E3__stuff;
			return _003CMake_003Ed__;
		}

		[DebuggerHidden]
		IEnumerator IEnumerable.GetEnumerator()
		{
			return ((IEnumerable<Thing>)this).GetEnumerator();
		}
	}

	public static bool SatisfiedBy(this List<AmountBySkill> minSkills, IEnumerable<Pawn> pawns)
	{
		return minSkills.All((AmountBySkill abs) => pawns.Sum((Pawn p) => p.skills.GetSkill(abs.Skill).Level) >= abs.Count);
	}

	public static List<Pawn> HumanColonists(this Caravan caravan)
	{
		return caravan.PawnsListForReading.Where((Pawn p) => p.IsFreeColonist).ToList();
	}

	public static IEnumerable<T> OrEmpty<T>(this IEnumerable<T> source)
	{
		return source ?? Enumerable.Empty<T>();
	}

	public static IEnumerable<TResult> SelectOrEmpty<TSource, TResult>(this IEnumerable<TSource> source, Func<TSource, TResult> selector)
	{
		if (source != null)
		{
			return source.Select(selector);
		}
		return Enumerable.Empty<TResult>();
	}

	public static IEnumerable<TResult> SelectManyOrEmpty<TSource, TResult>(this IEnumerable<TSource> source, Func<TSource, IEnumerable<TResult>> selector)
	{
		if (source != null)
		{
			return source.SelectMany(selector);
		}
		return Enumerable.Empty<TResult>();
	}

	public static string Line(this string input, bool show = true)
	{
		if (show && !GenText.NullOrEmpty(input))
		{
			return "\n" + input;
		}
		return "";
	}

	public static string Line(this TaggedString input, bool show = true)
	{
		if (show && !((TaggedString)(ref input)).NullOrEmpty())
		{
			return "\n" + ((TaggedString)(ref input)).RawText;
		}
		return "";
	}

	[IteratorStateMachine(typeof(_003CMake_003Ed__7))]
	public static IEnumerable<Thing> Make(this ThingDef thingDef, int count, ThingDef stuff = null)
	{
		//yield-return decompiler failed: Unexpected instruction in Iterator.Dispose()
		return new _003CMake_003Ed__7(-2)
		{
			_003C_003E3__thingDef = thingDef,
			_003C_003E3__count = count,
			_003C_003E3__stuff = stuff
		};
	}

	public static string Requirement(this string req, bool passed)
	{
		//IL_0024: Unknown result type (might be due to invalid IL or missing references)
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		return ColoredText.Colorize((passed ? "✓" : "✖") + " " + req, passed ? Color.green : Color.red);
	}

	public static string Requirement(this TaggedString req, bool passed)
	{
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		return ColoredText.Colorize((passed ? "✓" : "✖") + " " + ((TaggedString)(ref req)).RawText, passed ? Color.green : Color.red);
	}

	public static string RequirementsStringBase(this OutpostExtension ext, PlanetTile tileIdx, IEnumerable<Pawn> ps)
	{
		//IL_0018: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_008d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0194: Unknown result type (might be due to invalid IL or missing references)
		//IL_0199: Unknown result type (might be due to invalid IL or missing references)
		//IL_0110: Unknown result type (might be due to invalid IL or missing references)
		//IL_0296: Unknown result type (might be due to invalid IL or missing references)
		//IL_029b: Unknown result type (might be due to invalid IL or missing references)
		//IL_02e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0220: Unknown result type (might be due to invalid IL or missing references)
		//IL_0231: Unknown result type (might be due to invalid IL or missing references)
		//IL_0236: Unknown result type (might be due to invalid IL or missing references)
		//IL_0317: Unknown result type (might be due to invalid IL or missing references)
		//IL_031c: Unknown result type (might be due to invalid IL or missing references)
		StringBuilder stringBuilder = new StringBuilder();
		BiomeDef biome = Find.WorldGrid[tileIdx].biome;
		string reason = TaggedString.op_Implicit(Translator.Translate("Outposts.NoValidPawns"));
		List<Pawn> list = ps.Where((Pawn p) => ext.CanAddPawn(p, out reason)).ToList();
		if (list.Count == 0)
		{
			stringBuilder.AppendLine(reason.Requirement(passed: false));
		}
		List<BiomeDef> allowedBiomes = ext.AllowedBiomes;
		if (allowedBiomes != null && allowedBiomes.Count > 0)
		{
			stringBuilder.AppendLine(Translator.Translate("Outposts.AllowedBiomes").Requirement(ext.AllowedBiomes.Contains(biome)));
			stringBuilder.AppendLine(GenText.ToLineList(ext.AllowedBiomes.Select((BiomeDef b) => ((Def)b).label), "  ", true));
		}
		allowedBiomes = ext.DisallowedBiomes;
		if (allowedBiomes != null && allowedBiomes.Count > 0)
		{
			stringBuilder.AppendLine(Translator.Translate("Outposts.DisallowedBiomes").Requirement(!ext.DisallowedBiomes.Contains(biome)));
			stringBuilder.AppendLine(GenText.ToLineList(ext.DisallowedBiomes.Select((BiomeDef b) => ((Def)b).label), "  ", true));
		}
		if (ext.MinPawns > 0)
		{
			stringBuilder.AppendLine(TranslatorFormattedStringExtensions.Translate("Outposts.NumPawns", NamedArgument.op_Implicit(ext.MinPawns)).Requirement(list.Count >= ext.MinPawns));
		}
		List<AmountBySkill> requiredSkills = ext.RequiredSkills;
		if (requiredSkills != null && requiredSkills.Count > 0)
		{
			foreach (AmountBySkill requiredSkill in ext.RequiredSkills)
			{
				stringBuilder.AppendLine(TranslatorFormattedStringExtensions.Translate("Outposts.RequiredSkill", NamedArgument.op_Implicit(requiredSkill.Skill.skillLabel), NamedArgument.op_Implicit(requiredSkill.Count)).Requirement(list.Sum((Pawn p) => p.skills.GetSkill(requiredSkill.Skill).Level) >= requiredSkill.Count));
			}
		}
		if (ext.RequiresGrowing)
		{
			TaggedString req = Translator.Translate("Outposts.GrowingRequired");
			List<Twelfth> list2 = GenTemperature.TwelfthsInAverageTemperatureRange(tileIdx, 6f, 42f);
			stringBuilder.AppendLine(req.Requirement(list2 != null && GenCollection.Any<Twelfth>(list2)));
		}
		List<ThingDefCountClass> costToMake = ext.CostToMake;
		if (costToMake != null && costToMake.Count > 0)
		{
			Caravan val = Find.WorldObjects.PlayerControlledCaravanAt(tileIdx);
			foreach (ThingDefCountClass item in ext.CostToMake)
			{
				stringBuilder.AppendLine(TranslatorFormattedStringExtensions.Translate("Outposts.MustHaveInCaravan", NamedArgument.op_Implicit(item.Label)).Requirement(CaravanInventoryUtility.HasThings(val, item.thingDef, item.count, (Func<Thing, bool>)null)));
			}
		}
		return stringBuilder.ToString();
	}

	public static bool CanAddPawn(this OutpostExtension ext, Pawn pawn, out string reason)
	{
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		if (ext?.Event != null && !IdeoUtility.DoerWillingToDo(ext.Event, pawn))
		{
			reason = TaggedString.op_Implicit(Translator.Translate("IdeoligionForbids"));
			return false;
		}
		reason = null;
		return true;
	}

	public static string CanSpawnOnWithExt(this OutpostExtension ext, PlanetTile tileIdx, IEnumerable<Pawn> ps)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		//IL_001a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0060: Unknown result type (might be due to invalid IL or missing references)
		//IL_00f5: Unknown result type (might be due to invalid IL or missing references)
		//IL_0128: Unknown result type (might be due to invalid IL or missing references)
		//IL_00df: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e4: Unknown result type (might be due to invalid IL or missing references)
		//IL_0169: Unknown result type (might be due to invalid IL or missing references)
		//IL_016e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0219: Unknown result type (might be due to invalid IL or missing references)
		//IL_025b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0260: Unknown result type (might be due to invalid IL or missing references)
		//IL_01d9: Unknown result type (might be due to invalid IL or missing references)
		//IL_01df: Unknown result type (might be due to invalid IL or missing references)
		//IL_01e4: Unknown result type (might be due to invalid IL or missing references)
		string reason = TaggedString.op_Implicit(Translator.Translate("Outposts.NoValidPawns"));
		List<Pawn> pawns = ps.Where((Pawn p) => ext.CanAddPawn(p, out reason)).ToList();
		if (pawns.Count == 0)
		{
			return reason;
		}
		Tile val = Find.WorldGrid[tileIdx];
		if (val != null)
		{
			BiomeDef biome = val.biome;
			List<BiomeDef> disallowedBiomes = ext.DisallowedBiomes;
			if (disallowedBiomes == null || disallowedBiomes.Count <= 0 || !ext.DisallowedBiomes.Contains(biome))
			{
				disallowedBiomes = ext.AllowedBiomes;
				if (disallowedBiomes == null || disallowedBiomes.Count <= 0 || ext.AllowedBiomes.Contains(biome))
				{
					goto IL_00ef;
				}
			}
			return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.CannotBeMade", NamedArgument.op_Implicit(((Def)biome).label)));
		}
		goto IL_00ef;
		IL_00ef:
		if (Find.WorldObjects.AnySettlementBaseAtOrAdjacent(tileIdx) || Find.WorldObjects.AllWorldObjects.OfType<Outpost>().Any((Outpost outpost) => Find.WorldGrid.IsNeighborOrSame(tileIdx, ((WorldObject)outpost).Tile)))
		{
			return TaggedString.op_Implicit(Translator.Translate("Outposts.TooClose"));
		}
		if (ext.MinPawns > 0 && pawns.Count < ext.MinPawns)
		{
			return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.NotEnoughPawns", NamedArgument.op_Implicit(ext.MinPawns)));
		}
		List<AmountBySkill> requiredSkills = ext.RequiredSkills;
		if (requiredSkills != null && requiredSkills.Count > 0)
		{
			AmountBySkill amountBySkill = GenCollection.FirstOrDefault<AmountBySkill>(ext.RequiredSkills, (Predicate<AmountBySkill>)((AmountBySkill requiredSkill) => pawns.Sum((Pawn p) => p.skills.GetSkill(requiredSkill.Skill).Level) < requiredSkill.Count));
			if (amountBySkill != null)
			{
				SkillDef skill = amountBySkill.Skill;
				if (skill != null)
				{
					string skillLabel = skill.skillLabel;
					int count = amountBySkill.Count;
					return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.NotSkilledEnough", NamedArgument.op_Implicit(skillLabel), NamedArgument.op_Implicit(count)));
				}
			}
		}
		List<ThingDefCountClass> costToMake = ext.CostToMake;
		if (costToMake != null && costToMake.Count > 0)
		{
			Caravan caravan = Find.WorldObjects.PlayerControlledCaravanAt(tileIdx);
			ThingDefCountClass val2 = GenCollection.FirstOrDefault<ThingDefCountClass>(ext.CostToMake, (Predicate<ThingDefCountClass>)((ThingDefCountClass tdcc) => !CaravanInventoryUtility.HasThings(caravan, tdcc.thingDef, tdcc.count, (Func<Thing, bool>)null)));
			if (val2 != null)
			{
				string label = val2.Label;
				return TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("Outposts.MustHaveInCaravan", NamedArgument.op_Implicit(label)));
			}
		}
		return null;
	}

	public static string CheckSkill(this IEnumerable<Pawn> pawns, SkillDef skill, int minLevel)
	{
		//IL_003a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_0023: Unknown result type (might be due to invalid IL or missing references)
		return TaggedString.op_Implicit((pawns.Sum((Pawn p) => p.skills.GetSkill(skill).Level) < minLevel) ? TranslatorFormattedStringExtensions.Translate("Outposts.NotSkilledEnough", NamedArgument.op_Implicit(skill.skillLabel), NamedArgument.op_Implicit(minLevel)) : TaggedString.op_Implicit((string)null));
	}
}
