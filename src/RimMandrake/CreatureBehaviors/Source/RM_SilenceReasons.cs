using System.Collections.Generic;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// MAP_SILENCE_SINGLE_OWNER_1 (FV-3). Pure bookkeeping for "who wants this map quiet": a set of named
	/// reasons, each either timed (an end tick) or open-ended (Indefinite, until removed). The map is hushed
	/// while ANY reason remains; ambient sound is restored only when the last one leaves. No Verse types, so
	/// it is unit-testable outside the game.
	/// </summary>
	public static class RM_SilenceReasons
	{
		public const int Indefinite = int.MaxValue;

		/// <summary>Adds or extends a reason (a later end never shortens an earlier one). True when this call started the hush (no reason before it).</summary>
		public static bool Add(Dictionary<string, int> reasons, string key, int endTick)
		{
			bool wasEmpty = reasons.Count == 0;
			if (reasons.TryGetValue(key, out int old))
			{
				if (endTick > old)
				{
					reasons[key] = endTick;
				}
			}
			else
			{
				reasons[key] = endTick;
			}
			return wasEmpty;
		}

		/// <summary>Removes a reason. True when that emptied the set (the caller restores sound).</summary>
		public static bool Remove(Dictionary<string, int> reasons, string key)
		{
			return reasons.Remove(key) && reasons.Count == 0;
		}

		/// <summary>Drops every timed reason whose end tick has passed. True when that emptied a non-empty set.</summary>
		public static bool Expire(Dictionary<string, int> reasons, int nowTick)
		{
			if (reasons.Count == 0)
			{
				return false;
			}
			List<string> gone = null;
			foreach (KeyValuePair<string, int> kv in reasons)
			{
				if (kv.Value != Indefinite && nowTick >= kv.Value)
				{
					(gone ?? (gone = new List<string>())).Add(kv.Key);
				}
			}
			if (gone == null)
			{
				return false;
			}
			for (int i = 0; i < gone.Count; i++)
			{
				reasons.Remove(gone[i]);
			}
			return reasons.Count == 0;
		}
	}
}
