using System;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace VEF.Graphics;

public class TaggedDefProperties : DefModExtension
{
	public enum RNGSource
	{
		Pawn,
		Faction,
		Ideo,
		PawnKind,
		FactionDef
	}

	public List<TaggedAdvancedColor> generateAdvancedColors = new List<TaggedAdvancedColor>();

	public List<List<TaggedText>> generateRandomStrings = new List<List<TaggedText>>();

	public List<TaggedColor> taggedColors = new List<TaggedColor>();

	public List<TaggedText> taggedStrings = new List<TaggedText>();

	public override IEnumerable<string> ConfigErrors()
	{
		if (GenCollection.Any<TaggedColor>(taggedColors, (Predicate<TaggedColor>)delegate(TaggedColor tc)
		{
			//IL_000e: Unknown result type (might be due to invalid IL or missing references)
			if (!GenText.NullOrEmpty(tc.tag))
			{
				_ = tc.value;
				return false;
			}
			return true;
		}))
		{
			yield return "TaggedColor has null or empty tag or value.";
		}
		if (GenCollection.Any<TaggedText>(taggedStrings, (Predicate<TaggedText>)((TaggedText tp) => GenText.NullOrEmpty(tp.tag) || GenText.NullOrEmpty(tp.value))))
		{
			yield return "TaggedPath has null or empty tag or value.";
		}
	}

	public List<T> GetTaggedItems<T>() where T : ITaggedItem
	{
		if (typeof(T) == typeof(TaggedColor))
		{
			return taggedColors as List<T>;
		}
		if (typeof(T) == typeof(TaggedText))
		{
			return taggedStrings as List<T>;
		}
		throw new NotImplementedException($"Attempted to fetch tagged item for unsuported type: {typeof(T)}");
	}

	public void GenerateTags(Faction faction)
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		foreach (TaggedAdvancedColor generateAdvancedColor in generateAdvancedColors)
		{
			Color color = generateAdvancedColor.value.GetColor(faction);
			((ILoadReferenceable)(object)faction).SetColorTag(generateAdvancedColor.tag, color);
		}
		foreach (List<TaggedText> generateRandomString in generateRandomStrings)
		{
			string value = GenCollection.RandomElement<TaggedText>((IEnumerable<TaggedText>)generateRandomString).value;
			((ILoadReferenceable)(object)faction).SetStringTag(generateRandomString.First().tag, value);
		}
	}

	public void GenerateTags(Pawn pawn)
	{
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_002c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		foreach (TaggedAdvancedColor generateAdvancedColor in generateAdvancedColors)
		{
			Color color = generateAdvancedColor.value.GetColor(pawn, null, null);
			((ILoadReferenceable)(object)pawn).SetColorTag(generateAdvancedColor.tag, color);
		}
		foreach (List<TaggedText> generateRandomString in generateRandomStrings)
		{
			string value = GenCollection.RandomElement<TaggedText>((IEnumerable<TaggedText>)generateRandomString).value;
			((ILoadReferenceable)(object)pawn).SetStringTag(generateRandomString.First().tag, value);
		}
	}
}
