using System.Xml;
using Verse;

namespace RimMandrake.Greentide
{
	// A PatchOperation that respects a Greentide Mod Settings toggle. Same shape and reasoning as
	// src/RimUtinni/UtinniPatches/Source/PatchOperationSettingGate.cs: LoadedModManager constructs
	// RM_GreentideMod (GetSettings, so the statics hold the player's saved choices) BEFORE it
	// applies patches. A settings change therefore takes effect on the NEXT game start; every gated
	// option's tooltip says so.
	//
	// Named-switch rather than reflection on purpose: a typo in the XML is loud, never a silent "on".
	public class RM_PatchOperationGreentideSettingGate : PatchOperation
	{
		public string setting;
		public PatchOperation match;
		public PatchOperation nomatch;

		protected override bool ApplyWorker(XmlDocument xml)
		{
			bool on;
			switch (setting)
			{
				case "greatboleSeedPlantingEnabled":
					on = RM_GreentideSettings.greatboleSeedPlantingEnabled;
					break;
				case "greatboleServantsEnabled":
					on = RM_GreentideSettings.greatboleServantsEnabled;
					break;
				default:
					Log.Error("[Greentide] RM_PatchOperationGreentideSettingGate: unknown setting '" + setting + "'.");
					return false;
			}
			PatchOperation branch = on ? match : nomatch;
			return branch == null || branch.Apply(xml);
		}
	}
}
