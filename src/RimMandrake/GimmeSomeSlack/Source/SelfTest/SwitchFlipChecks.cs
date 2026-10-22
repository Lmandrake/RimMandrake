// GSS_SWITCHES_PROVE_TWENTY_UNFLIPPED, aerial half: flip each aerial Mod Settings value whose effect is decided by a pure
// AerialMath function and require the outcome to change, then require the production call site to feed that function the
// setting (so the flip proven here is the flip the game makes). Hose keys are not here: the hose and its switches live in
// FlowWorks. fallenWireShock/Ignites/Knockback and keepWiresOnGravship are Verse-bound
// gates with no pure half; they still owe live rows.
using System;
using System.IO;
using System.Text.RegularExpressions;
using RimMandrake.GimmeSomeSlack.Aerial;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class SwitchFlipChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "switchflip: " + msg);

        public static void Run()
        {
            // maxStrands: three insulators each side carry min(3, maxStrands) wires
            Check(AerialMath.StrandCount(3, 3, 3) == 3 && AerialMath.StrandCount(3, 3, 1) == 1, "maxStrands 3 -> 3 wires, 1 -> 1 wire");
            var a = new P2(0, 0); var b = new P2(10, 0); var ins = new[] { new P2(0, 0.1), new P2(0, 0.2), new P2(0, 0.3) };
            var ib = new[] { new P2(10, 0.1), new P2(10, 0.2), new P2(10, 0.3) };
            Check(AerialMath.SpanStrands(a, ins, b, ib, 7, 3).Count == 3 && AerialMath.SpanStrands(a, ins, b, ib, 7, 1).Count == 1,
                  "maxStrands flips the strands a span lays");

            // explosionsCut / kineticSway
            Check(AerialMath.BlastKindFor(true, false, 10, true, true) == AerialMath.BlastKind.Cut
                  && AerialMath.BlastKindFor(true, false, 10, false, true) == AerialMath.BlastKind.None, "explosionsCut on cuts, off spares");
            Check(AerialMath.BlastKindFor(true, true, 10, true, true) == AerialMath.BlastKind.Sway
                  && AerialMath.BlastKindFor(true, true, 10, true, false) == AerialMath.BlastKind.None, "kineticSway on sways, off does nothing");
            Check(AerialMath.BlastKindFor(true, true, 10, false, true) == AerialMath.BlastKind.Sway, "explosionsCut off never stops a kinetic sway");

            // tapRate / tapsEnabled (k = CompPower.WattsToWattDaysPerTick = 1/60000 per watt-tick)
            const double k = 1.0 / 60000.0;
            double s500 = AerialMath.TapStolenPerTick(500, 1, 0, k, false, true, 0, true);
            double s100 = AerialMath.TapStolenPerTick(100, 1, 0, k, false, true, 0, true);
            Check(Math.Abs(s500 - 500 * k) < 1e-12 && Math.Abs(s100 - 100 * k) < 1e-12, "tapRate is the watts taken when the victim has surplus");
            Check(AerialMath.TapStolenPerTick(0, 1, 0, k, false, true, 0, true) == 0, "tapRate 0 takes nothing");
            Check(AerialMath.TapStolenPerTick(500, 1, 0, k, false, false, 0, true) == 0, "tapsEnabled off takes nothing");

            // swayStrength scales the CPU sway amplitude; 0 is still
            double peak1 = 0, peak2 = 0, peak0 = 0;
            for (int i = 0; i < 200; i++)
            {
                double t = i * 0.05;
                peak1 = Math.Max(peak1, Math.Abs(AerialMath.Sway(0.5, t, 1, 0.12 * 1, 3)));
                peak2 = Math.Max(peak2, Math.Abs(AerialMath.Sway(0.5, t, 1, 0.12 * 2, 3)));
                peak0 = Math.Max(peak0, Math.Abs(AerialMath.Sway(0.5, t, 1, 0.12 * 0, 3)));
            }
            Check(peak1 > 0 && Math.Abs(peak2 - 2 * peak1) < 1e-9 && peak0 == 0, "swayStrength 2 doubles the sway, 0 stills it");

            // the production call sites feed these functions the setting
            string dir = AerialSourceDir();
            Check(dir != null, "found Source/Aerial to read the call sites");
            if (dir == null) return;
            string comp = File.ReadAllText(Path.Combine(dir, "RM_MapComponent_Aerial.cs"));
            string anchor = File.ReadAllText(Path.Combine(dir, "CompAerialAnchor.cs"));
            string tap = File.ReadAllText(Path.Combine(dir, "CompPowerTap.cs"));
            Check(Regex.IsMatch(comp, @"SpanStrands\([^;]*AerialSettings\.maxStrands\)") && anchor.Contains("AerialSettings.maxStrands)"),
                  "maxStrands reaches SpanStrands and StrandCount");
            Check(Regex.Matches(comp, @"BlastKindFor\([^;]*AerialSettings\.explosionsCut, AerialSettings\.kineticSway\)").Count >= 2,
                  "both blast paths pass explosionsCut and kineticSway");
            Check(Regex.IsMatch(tap, @"TapStolenPerTick\(AerialSettings\.tapRate,[^;]*AerialSettings\.tapsEnabled"), "the tap passes tapRate and tapsEnabled");
            Check(Regex.IsMatch(comp, @"AerialMath\.Sway\([^;]*AerialSettings\.swayStrength"), "the span sway passes swayStrength");

            // PIPE_POLE_SWITCH_DECIDE_HOSTAGE_TO_WIRES (owner by card 2026-10-21: "Their own switch."): a pipe pole obeys FlowWorks'
            // pipe-pole switch, a power anchor GSS's power master, and neither the other's
            foreach (bool power in new[] { false, true })
                foreach (bool pipe in new[] { false, true })
                    foreach (bool sub in new[] { false, true })
                    {
                        Check(AerialKinds.KindOn(AerialLineKind.Power, power, pipe) == power, $"power anchor on = the power master ({power},{pipe})");
                        Check(AerialKinds.KindOn(AerialLineKind.Pipe, power, pipe) == pipe, $"pipe pole on = its own switch, never the power master ({power},{pipe})");
                        Check(AerialKinds.KindBehaviour(AerialLineKind.Power, power, pipe, sub) == (power && sub), "a power behaviour needs the master and its setting");
                        Check(AerialKinds.KindBehaviour(AerialLineKind.Pipe, power, pipe, sub) == pipe, "a pipe behaviour reads only the pipe switch (the power settings are greyed with the master)");
                    }
            // every gate the item listed reads the anchor's own kind, not the bare power master
            string Src(string f) => File.ReadAllText(Path.Combine(dir, f));
            string place = Src("PlaceWorkers_Aerial.cs"), ground = Src("SectionLayer_RM_AerialGround.cs"), restring = Src("RestringJob.cs"),
                   alert = Src("Alert_WireDown.cs");
            Check(place.Contains("IsBuildDesignatorVisible(BuildableDef def) => AerialLineProfiles.KindOn(AerialLineProfiles.KindOf(def as ThingDef))"),
                  "anchor build button: each kind's own switch");
            Check(place.Contains("AerialLineProfiles.KindBehaviour(kind, AerialSettings.autoLink)"), "the ghost's preview line follows the real auto-link rule");
            Check(Regex.IsMatch(comp, @"void MapComponentUpdate\(\)[\s\S]{0,400}!AerialLineProfiles\.AnyKindOn")
                  && Regex.IsMatch(comp, @"foreach \(CompAerialAnchor a in Anchors\)\s*\{\s*if \(!AerialLineProfiles\.KindOn\(a\.Kind\)\) continue;"),
                  "span draw: runs while any kind is on, skips an anchor whose kind is off");
            Check(Regex.IsMatch(comp, @"if \(!AerialSettings\.enabled\) return;[^\n]*\n\s*DrawLocalDrops\(view\);\s*DrawTaps\(view\);\s*DrawFallenGlow\(\);"),
                  "drops, clamps and live-end glow stay behind the power master");
            Check(comp.Contains("if (!AerialLineProfiles.KindBehaviour(a.Kind, AerialSettings.autoLink)) continue;")
                  && anchor.Contains("AerialLineProfiles.KindBehaviour(Kind, AerialSettings.autoLink)) comp?.QueueAutoLink(this);"),
                  "auto-link (queue and process) per kind");
            Check(comp.Contains("if (!AerialLineProfiles.KindBehaviour(a.Kind, AerialSettings.cutWiresOnOwnerChange)) continue;"), "owner-change cut per kind");
            Check(ground.Contains("public override bool Visible => AerialLineProfiles.AnyKindOn;")
                  && ground.Contains("!AerialLineProfiles.KindOn(a.Kind)) continue;"), "ground layer: visible for any kind, prints only kinds that are on");
            Check(restring.Contains("!AerialLineProfiles.AnyKindOn || !pawn.Map.designationManager")
                  && restring.Contains("a == null || !AerialLineProfiles.KindOn(a.Kind)")
                  && restring.Contains("AerialLineProfiles.KindOn(ta.Kind)) || !Restringing.Designated(TargetThingA)"), "re-string per kind");
            Check(alert.Contains("AerialLineProfiles.KindBehaviour(a.Kind, AerialSettings.wireDownAlert)")
                  && alert.Contains("GetReport() => AerialLineProfiles.AnyKindOn"), "wire-down alert per kind");
            Check(!Regex.IsMatch(place + ground + restring + alert, @"AerialSettings\.enabled(?! && AerialSettings\.tapsEnabled)"),
                  "no bare power-master read left in the placeworkers, ground layer, re-string or alert (the clamp keeps its own)");
        }

        private static string AerialSourceDir()
        {
            for (DirectoryInfo d = new DirectoryInfo(AppContext.BaseDirectory); d != null; d = d.Parent)
            {
                string p = Path.Combine(d.FullName, "src", "RimMandrake", "GimmeSomeSlack", "Source", "Aerial");
                if (Directory.Exists(p)) return p;
                p = Path.Combine(d.FullName, "Source", "Aerial");
                if (File.Exists(Path.Combine(p, "CompPowerTap.cs"))) return p;
            }
            return null;
        }
    }
}
