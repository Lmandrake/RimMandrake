using System.Collections.Generic;

namespace BigAndSmall;

public interface IScoreHolder
{
	IEnumerable<IScoreProvider> Selectors { get; }

	ScoreCalculator Calculator { get; }

	float GetDefaultValue { get; }

	float? GetScore(object obj);
}
