// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// RIMMANDRAKE_LIGHT_SLACK_SWITCH_GREEN_RED_DARK_WHEN_UNPOWERED (owner 2026-11-20: "the switch should have some illuminated indicator
// on it showing whether it is open or closed but always powered (green Vs red) vs unpowered (no glow)"; his card the same evening:
// "Green flows, red cut"). Bar switch_light_reads_state. This is the one decision of the lamp's state; SwitchLightDraw.cs feeds it
// from the live map and SelfTest/SwitchLightChecks.cs runs it.
//
// What "powered" reads. A closed switch is a transmitter of one power net, so it is powered when that net has an active power source
// (PowerNet.HasActivePowerSource: a charged battery or a producing generator; the same read CordWorldAdapter.IsLive gives the cords,
// so the lamp and the cords never disagree). An open switch is in no power net (Building_PowerSwitch.TransmitsPowerNow is false); its
// sides are the four cells cardinally beside it, the adjacency vanilla PowerNetMaker.ContiguousPowerBuildings joins nets on and the
// cells CordWorldAdapter.AddPower hooks the switch's cords to. It is powered when the net a transmitter on any of those cells belongs
// to has an active power source. The lamp reads both every frame, so a flick, a battery run dry or a generator switched off shows on
// the next frame; nothing is cached across frames.
namespace RimMandrake.GimmeSomeSlack.Core
{
    public enum SwitchLamp { Dark, Green, Red }

    public static class SwitchLight
    {
        /// <summary>Powered: the switch's own net is live (closed), or the net on any cardinal side cell is live (open or closed).</summary>
        public static bool AnySidePowered(bool ownNetLive, bool[] sideLive)
        {
            if (ownNetLive) return true;
            if (sideLive == null) return false;
            foreach (bool s in sideLive) if (s) return true;
            return false;
        }

        /// <summary>The lamp: dark when the setting is off or no side has power; else green when closed (power flows), red when open
        /// (power cut).</summary>
        public static SwitchLamp Of(bool settingOn, bool closed, bool powered)
        {
            if (!settingOn || !powered) return SwitchLamp.Dark;
            return closed ? SwitchLamp.Green : SwitchLamp.Red;
        }

        /// <summary>Does this switch draw its glow out? The Futuristic look's closed art carries its own cyan glow; with no power on
        /// any side that glow is put out (the unlit picture is drawn over it), whatever the lamp setting says.</summary>
        public static bool GlowOut(string look, bool closedArt, bool powered) => look == "Futuristic" && closedArt && !powered;

        /// <summary>The unlit picture's file name for a switch that draws the stubs in <paramref name="drawn"/> (SwitchStubs mask).</summary>
        public static string UnlitName(int drawn) => "PowerSwitch_Unlit" + SwitchStubs.Suffix(drawn);
    }
}
