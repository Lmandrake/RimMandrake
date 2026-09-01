using HarmonyLib;
using RimWorld.QuestGen;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(QuestGen))]
[HarmonyPatch("AddSlateQuestTags")]
public static class VanillaExpandedFramework_QuestGen_AddSlateQuestTags_Patch
{
	public static Slate slate;

	public static void Postfix()
	{
		slate = QuestGen.slate.DeepCopy();
	}
}
