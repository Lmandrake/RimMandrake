using System.Collections.Generic;

namespace BigAndSmall;

/// <summary>
/// This is a class which contains one or more IScoreThing objects which acts as components for a score.
///
/// By default the highest single score is returned.
///
/// If is basically a non-def version of ScorableDef.
/// </summary>
public abstract class Scoreable : IScoreHolder, IScoreProvider
{
	private ScoreCalculator _calculator;

	public abstract IEnumerable<IScoreProvider> Selectors { get; }

	public virtual ScoreCalculator Calculator => _calculator ?? (_calculator = new ScoreCalculator(this));

	public virtual float GetDefaultValue => float.MinValue;

	public virtual float? GetScore(object obj)
	{
		return Calculator.GetScoreFor(obj);
	}
}
