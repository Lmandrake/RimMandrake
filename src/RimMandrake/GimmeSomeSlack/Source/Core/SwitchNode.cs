// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// RIMMANDRAKE_SEAT_SLACK_CORDS_IN_OFF_SWITCH_NOT_CUT (his walk of 2026-11-20, row 1): "Switching the switch to off shows the cables as
// suddenly completely disconnected from the switch, but they are not. They should read connected without power, not broken."
// Vanilla keeps an off power switch in no power net (Building_PowerSwitch.TransmitsPowerNow is false), so a graph that takes its
// transmitter buildings only from the nets lost the switch and drew the conduit beside it as cut ends. This is the one decision of
// which transmitter buildings become cord-graph nodes; CordWorldAdapter.AddPower asks it, and SelfTest/SwitchOffChecks.cs runs it.
namespace RimMandrake.GimmeSomeSlack.Core
{
    public static class SwitchNode
    {
        /// <summary>True when a spawned transmitter building is a node of the cord graph: every building in a power net, and a power
        /// switch whatever its state (off, it is in no net, but its cords still end on its stubs, drawn unpowered).</summary>
        public static bool JoinsGraph(bool inPowerNet, bool isPowerSwitch) => inPowerNet || isPowerSwitch;
    }
}
