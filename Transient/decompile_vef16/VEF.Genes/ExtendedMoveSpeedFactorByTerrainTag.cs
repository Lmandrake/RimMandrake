using System;
using System.Collections.Generic;
using Verse;

namespace VEF.Genes;

public class ExtendedMoveSpeedFactorByTerrainTag
{
	private readonly Dictionary<string, Dictionary<object, float>> moveSpeedFactorByTerrainTag = new Dictionary<string, Dictionary<object, float>>();

	private readonly Dictionary<string, Dictionary<string, (float speedFactor, HashSet<object> activeGenes)>> taggedMoveSpeedFactorByTerrainTag = new Dictionary<string, Dictionary<string, (float, HashSet<object>)>>();

	public bool Empty
	{
		get
		{
			if (moveSpeedFactorByTerrainTag.Count == 0)
			{
				return taggedMoveSpeedFactorByTerrainTag.Count == 0;
			}
			return false;
		}
	}

	public void Add(object effectHolder, Dictionary<string, List<MoveSpeedFactor>> speedFactors)
	{
		string text = default(string);
		List<MoveSpeedFactor> list = default(List<MoveSpeedFactor>);
		foreach (KeyValuePair<string, List<MoveSpeedFactor>> speedFactor in speedFactors)
		{
			GenCollection.Deconstruct<string, List<MoveSpeedFactor>>(speedFactor, ref text, ref list);
			string key = text;
			foreach (MoveSpeedFactor item in list)
			{
				if (item.tag == null)
				{
					if (!moveSpeedFactorByTerrainTag.TryGetValue(key, out var value))
					{
						value = (moveSpeedFactorByTerrainTag[key] = new Dictionary<object, float>());
					}
					value[effectHolder] = item.moveSpeedFactor;
					continue;
				}
				if (!taggedMoveSpeedFactorByTerrainTag.TryGetValue(key, out Dictionary<string, (float, HashSet<object>)> value2))
				{
					value2 = (taggedMoveSpeedFactorByTerrainTag[key] = new Dictionary<string, (float, HashSet<object>)>());
				}
				if (!value2.TryGetValue(item.tag, out var value3))
				{
					value3 = (value2[item.tag] = (item.moveSpeedFactor, new HashSet<object>()));
				}
				value3.Item2.Add(effectHolder);
			}
		}
	}

	public void Remove(object effectHolder)
	{
		GenCollection.RemoveAll<string, Dictionary<object, float>>(moveSpeedFactorByTerrainTag, (Predicate<KeyValuePair<string, Dictionary<object, float>>>)delegate(KeyValuePair<string, Dictionary<object, float>> x)
		{
			x.Value.Remove(effectHolder);
			return x.Value.Count == 0;
		});
		GenCollection.RemoveAll<string, Dictionary<string, (float, HashSet<object>)>>(taggedMoveSpeedFactorByTerrainTag, (Predicate<KeyValuePair<string, Dictionary<string, (float, HashSet<object>)>>>)delegate(KeyValuePair<string, Dictionary<string, (float speedFactor, HashSet<object> activeGenes)>> x)
		{
			GenCollection.RemoveAll<string, (float, HashSet<object>)>(x.Value, (Predicate<KeyValuePair<string, (float, HashSet<object>)>>)delegate(KeyValuePair<string, (float speedFactor, HashSet<object> activeGenes)> z)
			{
				z.Value.activeGenes.Remove(effectHolder);
				return z.Value.activeGenes.Count == 0;
			});
			return x.Value.Count == 0;
		});
	}

	public void ApplySpeed(List<string> terrainTags, ref float speed)
	{
		if (terrainTags == null)
		{
			return;
		}
		foreach (string terrainTag in terrainTags)
		{
			ApplySpeed(terrainTag, ref speed);
		}
	}

	public void ApplySpeed(string terrainTag, ref float speed)
	{
		if (terrainTag == null)
		{
			return;
		}
		if (moveSpeedFactorByTerrainTag.TryGetValue(terrainTag, out var value))
		{
			foreach (float value3 in value.Values)
			{
				speed /= value3;
			}
		}
		if (!taggedMoveSpeedFactorByTerrainTag.TryGetValue(terrainTag, out Dictionary<string, (float, HashSet<object>)> value2))
		{
			return;
		}
		foreach (var value4 in value2.Values)
		{
			float item = value4.Item1;
			speed /= item;
		}
	}
}
