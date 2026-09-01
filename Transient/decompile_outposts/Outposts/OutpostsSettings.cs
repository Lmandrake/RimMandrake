using System;
using System.Collections.Generic;
using Verse;

namespace Outposts;

public class OutpostsSettings : ModSettings
{
	public class OutpostSettings : IExposable
	{
		private Dictionary<string, string> dictionary = new Dictionary<string, string>();

		public void ExposeData()
		{
			Scribe_Collections.Look<string, string>(ref dictionary, "keysToValues", (LookMode)1, (LookMode)1);
		}

		public bool Has(string key)
		{
			return dictionary.ContainsKey(key);
		}

		public void Remove(string key)
		{
			dictionary.Remove(key);
		}

		public bool TryGet(string key, Type type, out object value)
		{
			if (dictionary == null)
			{
				dictionary = new Dictionary<string, string>();
			}
			if (Has(key))
			{
				value = ParseHelper.FromString(dictionary[key], type);
				return true;
			}
			value = null;
			return false;
		}

		public void Set(string key, object value)
		{
			GenCollection.SetOrAdd<string, string>(dictionary, key, value.ToString());
		}
	}

	public DeliveryMethod DeliveryMethod;

	public float ProductionMultiplier = 1f;

	public Dictionary<string, OutpostSettings> SettingsPerOutpost = new Dictionary<string, OutpostSettings>();

	public float TimeMultiplier = 1f;

	public OutpostSettings SettingsFor(string defName)
	{
		if (SettingsPerOutpost == null)
		{
			SettingsPerOutpost = new Dictionary<string, OutpostSettings>();
		}
		if (!SettingsPerOutpost.TryGetValue(defName, out var value) || value == null)
		{
			GenCollection.SetOrAdd<string, OutpostSettings>(SettingsPerOutpost, defName, value = new OutpostSettings());
		}
		return value;
	}

	public override void ExposeData()
	{
		((ModSettings)this).ExposeData();
		Scribe_Values.Look<float>(ref ProductionMultiplier, "productionMultiplier", 1f, false);
		Scribe_Values.Look<float>(ref TimeMultiplier, "timeMultiplier", 1f, false);
		Scribe_Values.Look<DeliveryMethod>(ref DeliveryMethod, "deliveryMethod", DeliveryMethod.Teleport, false);
		Scribe_Collections.Look<string, OutpostSettings>(ref SettingsPerOutpost, "settingsPerOutpost", (LookMode)1, (LookMode)2);
	}
}
