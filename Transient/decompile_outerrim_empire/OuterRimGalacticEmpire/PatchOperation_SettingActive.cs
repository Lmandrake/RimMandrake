using System.Collections.Generic;
using System.Linq;
using System.Xml;
using Verse;

namespace OuterRimGalacticEmpire;

public class PatchOperation_SettingActive : PatchOperation
{
	public List<string> settings;

	public PatchOperation active;

	public PatchOperation inactive;

	public override bool ApplyWorker(XmlDocument xml)
	{
		bool flag = false;
		_ = ((Mod)OuterRimGalacticEmpireMod.mod).Content;
		for (int i = 0; i < settings.Count(); i++)
		{
			if (!OuterRimGalacticEmpireMod.settings.IsValidSetting(settings[i]))
			{
				Log.Error("Configuration error in patch, { settings[i]} is not an existing setting in this mod. This can only check existing boolean settings.");
			}
			if (OuterRimGalacticEmpireMod.settings.GetEnabledSettings.Contains(settings[i]))
			{
				flag = true;
				break;
			}
		}
		if (flag)
		{
			if (active != null)
			{
				return active.Apply(xml);
			}
		}
		else if (inactive != null)
		{
			return inactive.Apply(xml);
		}
		return true;
	}
}
