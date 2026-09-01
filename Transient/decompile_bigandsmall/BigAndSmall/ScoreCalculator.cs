using System.Collections.Generic;
using System.Linq;
using Verse;

namespace BigAndSmall;

public class ScoreCalculator(IScoreHolder scorableList)
{
	protected IScoreHolder parent = scorableList;

	/// <summary>
	/// This is the default implementation of the score calculator.
	/// </summary>
	/// <param name="obj">Object to calculate the score for.</param>
	/// <returns>Highest value, if any. Else null</returns>
	public virtual float? GetScoreFor(object obj)
	{
		if (GenCollection.EnumerableNullOrEmpty<IScoreProvider>(scorableList.Selectors))
		{
			return scorableList.GetDefaultValue;
		}
		IEnumerable<float?> source = from item in scorableList.Selectors
			select item.GetScore(obj) into filterScore
			where filterScore.HasValue
			select filterScore;
		if (!source.Any())
		{
			return null;
		}
		return source.Max();
	}

	public static IScoreHolder GetBestScored<T>(object obj, List<IScoreHolder> list) where T : IScoreHolder
	{
		return GetSortedScores(obj, list)?.FirstOrDefault();
	}

	public static List<IScoreHolder> GetSortedScores(object obj, IEnumerable<IScoreHolder> list)
	{
		List<(float, IScoreHolder)> list2 = new List<(float, IScoreHolder)>();
		foreach (IScoreHolder item in list)
		{
			float? scoreFor = item.Calculator.GetScoreFor(obj);
			if (scoreFor.HasValue)
			{
				list2.Add((scoreFor.Value, item));
			}
		}
		if (list2.Count != 0)
		{
			return (from element in list2
				orderby element.score descending
				select element.item).ToList();
		}
		return null;
	}
}
