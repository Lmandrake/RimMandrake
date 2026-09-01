using System;
using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

/// <summary>
/// This is a class which contains one or more IScoreThing objects which acts as components for a score.
///
/// By default the highest single score is returned.
///
/// If is basically a def version of Scorable.
/// </summary>
public abstract class ScorableDef : Def, IScoreHolder
{
	public Type scoreCalculatorType = typeof(ScoreCalculator);

	private ScoreCalculator _calculator;

	public abstract IEnumerable<IScoreProvider> Selectors { get; }

	public virtual ScoreCalculator Calculator => _calculator ?? (_calculator = (ScoreCalculator)Activator.CreateInstance(scoreCalculatorType, this));

	public virtual float GetDefaultValue => float.MinValue;

	public virtual float? GetScore(object obj)
	{
		return Calculator.GetScoreFor(obj);
	}

	public static ScorableDef GetBestScoredDef<T>(object obj) where T : ScorableDef
	{
		List<T> sortedScoredDefs = GetSortedScoredDefs<T>(obj);
		return (sortedScoredDefs != null) ? sortedScoredDefs.FirstOrDefault() : null;
	}

	public static List<T> GetSortedScoredDefs<T>(object obj) where T : ScorableDef
	{
		IEnumerable<IScoreHolder> enumerable = DefDatabase<T>.AllDefsListForReading.OfType<IScoreHolder>();
		if (enumerable.Any() && ScoreCalculator.GetSortedScores(obj, enumerable) != null)
		{
			return ScoreCalculator.GetSortedScores(obj, enumerable).OfType<T>().ToList();
		}
		return null;
	}
}
