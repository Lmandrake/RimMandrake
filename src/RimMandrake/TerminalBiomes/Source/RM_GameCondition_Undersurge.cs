using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_CHANNEL_CURRENT_1 §2. "Not a separate system — a parameter
    // storm on §1.3" (spec, verbatim): this class is deliberately thin.
    // Strength-up and width-out are read directly off RM_MapComponent_
    // ChannelCurrent.SurgeActive by that component's own CadenceFor/
    // HasCurrent/LaneAt — nothing here duplicates that logic. This class's
    // whole job is telling every affected map's component when the storm
    // starts and stops, plus the one-off violent grab at start (also on the
    // component, so a map that gains the condition mid-way through a load —
    // Scribed vanilla-style via GameCondition's own base ExposeData — grabs
    // correctly either way).
    public class RM_GameCondition_Undersurge : GameCondition
    {
        public override void Init()
        {
            base.Init();
            SingleMap?.GetComponent<RM_MapComponent_ChannelCurrent>()?.BeginSurge();
        }

        public override void End()
        {
            SingleMap?.GetComponent<RM_MapComponent_ChannelCurrent>()?.EndSurge();
            base.End();
        }
    }
}
