using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Verse;

namespace OuterRimGalacticEmpire;

public class OuterRimGalacticEmpireSettings : ModSettings
{
	public bool enableInquisitors = true;

	public bool enableWookieeSlaves = true;

	public bool enableOccupation = true;

	public bool occupationFlyovers = true;

	public bool occupationBroadcasts = true;

	public bool occupationInspections = true;

	public bool occupationTaxes = true;

	public bool darthDolores = true;

	public IEnumerable<string> GetEnabledSettings => from p in ((object)this).GetType().GetFields()
		where p.FieldType == typeof(bool) && (bool)p.GetValue(this)
		select p.Name;

	public override void ExposeData()
	{
		((ModSettings)this).ExposeData();
		Scribe_Values.Look<bool>(ref enableInquisitors, "enableInquisitors", true, false);
		Scribe_Values.Look<bool>(ref enableWookieeSlaves, "enableWookieeSlaves", true, false);
		Scribe_Values.Look<bool>(ref enableOccupation, "enableOccupation", true, false);
		Scribe_Values.Look<bool>(ref occupationFlyovers, "occupationFlyovers", true, false);
		Scribe_Values.Look<bool>(ref occupationBroadcasts, "occupationBroadcasts", true, false);
		Scribe_Values.Look<bool>(ref occupationInspections, "occupationInspections", true, false);
		Scribe_Values.Look<bool>(ref occupationTaxes, "occupationTaxes", true, false);
		Scribe_Values.Look<bool>(ref darthDolores, "darthDolores", true, false);
	}

	public bool IsValidSetting(string input)
	{
		if ((from p in ((object)this).GetType().GetFields()
			where p.FieldType == typeof(bool)
			select p).Any((FieldInfo i) => i.Name == input))
		{
			return true;
		}
		return false;
	}
}
