// Gimme Some Slack 0.1.1 (RIMMANDRAKE_WIDEN_SLACK_STYLE_BUTTON_REACH_ITEM_RUN_OR_WHOLE_MAP; owner walk 2026-11-22, card
// "All three, now"): the style button's three reaches and the rule for mixed-look runs
// (design/RimMandrake/messyconduit_style_per_build_design.md section 2.5), plus the Gust sway default
// (RIMMANDRAKE_SHIP_SLACK_GUST_SWAY_AS_DEFAULT_HE_PICKED_OF_THREE). Pure rules in ../Aerial/ConduitStyles.cs; the gizmo and
// settings wiring by a read of the production source. Each property has a can-fail beside it.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using RimMandrake.GimmeSomeSlack.Aerial;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class StyleReachChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "reach: " + msg);
        private const string D = "Scrapper";

        public static void Run()
        {
            MixedRuns();
            Joins();
            NewPieceOnMixed();
            Lamps();
            Reaches();
            Wiring();
            GustDefault();
        }

        private static ConduitStyles.Run R(int area, int oldest, string look, string colour = null, bool mixed = false) =>
            new ConduitStyles.Run { Area = area, Oldest = oldest, Look = look, Colour = colour, Mixed = mixed };

        private static ConduitStyles.LookSet Set(params (string look, bool conduit, string colour)[] members)
        {
            var s = new ConduitStyles.LookSet(D);
            foreach (var m in members) s.Add(m.look, m.conduit, m.colour);
            return s;
        }

        private static void MixedRuns()
        {
            Check(!Set(("Industrial", true, null), ("Industrial", false, null), ("Industrial", true, null)).Mixed,
                  "a run whose members all store Industrial is uniform");
            Check(!Set((null, true, null), ("Scrapper", false, null), (null, false, null)).Mixed,
                  "legacy members draw the default look: legacy + stored default is uniform");
            Check(!Set(("Modern", true, "Blue"), ("Modern", false, null), ("Modern", true, "Blue")).Mixed,
                  "one colour per run (Modern multicolour painted Blue): conduit all Blue, the switch carries the look alone -> uniform");
            Check(!Set(("Modern", true, ConduitStyles.Mix), ("Modern", true, ConduitStyles.Mix)).Mixed,
                  "a random-mix run (every cell the mix marker) is uniform");
            Check(Set(("Industrial", true, null), ("Futuristic", true, null)).Mixed,
                  "can fail: one conduit cell restyled to Futuristic in an Industrial run makes it mixed");
            Check(Set((null, true, null), ("Industrial", false, null)).Mixed,
                  "can fail: one pole restyled to Industrial in a legacy (default Scrapper) run makes it mixed");
            Check(Set(("Modern", true, "Blue"), ("Modern", true, "Orange")).Mixed && Set(("Modern", true, "Blue"), ("Modern", true, null)).Mixed,
                  "can fail: two Modern colours, or a stored colour beside no stored colour, on the conduit of one run is mixed");
            var a = Set(("Industrial", true, null)); var b = Set(("Modern", true, "Blue"));
            a.AddSet(b);
            Check(a.Mixed && a.Looks.SetEquals(new[] { "Industrial", "Modern" }), "two uniform sets of different looks merged read mixed, with both drawn looks");
        }

        private static void Joins()
        {
            // rule 1: a join repaints a loser only when winner and loser are both uniform
            ConduitStyles.Plan uu = ConduitStyles.PlanPlacement("Futuristic", null, new[] { R(3, 1, "Modern", "Orange"), R(6, 50, "Industrial") }, D);
            Check(uu.Look == "Industrial" && uu.Repaint.SequenceEqual(new[] { 0 }), "uniform + uniform: the larger run wins and the smaller is repainted (unchanged)");
            ConduitStyles.Plan um = ConduitStyles.PlanPlacement(null, null, new[] { R(3, 1, "Futuristic", mixed: true), R(6, 50, "Industrial") }, D);
            Check(um.Look == "Industrial" && um.Repaint.Count == 0 && !um.StylesDiffered,
                  "a mixed loser is never repainted by a join; the new piece takes the uniform winner's look");
            var winM = R(6, 50, "Industrial", mixed: true); winM.Touch = R(1, 61, "Futuristic");
            ConduitStyles.Plan mu = ConduitStyles.PlanPlacement("Scrapper", null, new[] { R(3, 1, "Modern", "Orange"), winM }, D);
            Check(mu.Look == "Futuristic" && mu.Repaint.Count == 0 && mu.Winner == 1 && !mu.MaterialiseWinner,
                  "a uniform loser of a mixed winner keeps its look; the new piece takes the look it touches in the winner (Futuristic)");
            ConduitStyles.Plan link = ConduitStyles.PlanPlacement(null, null, new[] { R(3, 1, "Modern", "Orange"), winM }, D);
            Check(link.Repaint.Count == 0, "a span joining a uniform run to a larger mixed run repaints nothing");
            ConduitStyles.Plan old = ConduitStyles.PlanPlacement(null, null, new[] { R(3, 1, "Futuristic"), R(6, 50, "Industrial") }, D);
            Check(old.Repaint.Count == 1, "can fail: the same span between two uniform runs repaints the smaller (the pre-0.1.1 rule still holds)");
        }

        private static void NewPieceOnMixed()
        {
            // rule 2: onto a mixed run the new piece takes the touched member's look (conduit first for conduit, else oldest)
            var touched = new List<ConduitStyles.Run> { R(0, 5, "Industrial"), R(1, 9, "Modern", "Green"), R(1, 7, "Futuristic") };
            Check(ConduitStyles.LocalPick(touched, true) == 2, "a new conduit cell touching a pole and two conduit cells takes the OLDEST touching conduit cell");
            Check(ConduitStyles.LocalPick(touched, false) == 0, "a new pole takes the oldest touching member of any kind");
            Check(ConduitStyles.LocalPick(new List<ConduitStyles.Run>(), true) == -1, "nothing touched: no pick");
            var m = R(5, 3, "Industrial", mixed: true); m.Touch = R(1, 9, "Modern", "Green");
            ConduitStyles.Plan p = ConduitStyles.PlanPlacement("Futuristic", null, new[] { m }, D);
            Check(p.Look == "Modern" && p.Colour == "Green" && p.Repaint.Count == 0, "built onto a mixed run beside a Green Modern cell: Modern, Green, nothing repainted");
            var pole = R(5, 3, "Industrial", mixed: true); pole.Touch = R(0, 9, "Modern", null);
            ConduitStyles.Plan pp = ConduitStyles.PlanPlacement("Futuristic", null, new[] { pole }, D);
            Check(pp.Look == "Modern" && pp.Colour == null, "touching only a Modern pole: Modern with no stored colour (a pole carries no colour)");
            var leg = R(5, 3, "Industrial", mixed: true); leg.Touch = R(1, 9, null);
            ConduitStyles.Plan pl = ConduitStyles.PlanPlacement("Futuristic", null, new[] { leg }, D);
            Check(pl.MaterialiseWinner && pl.Look == D && pl.Repaint.Count == 0, "touching a member that stores no look: the new piece stores none either");
            var u = R(5, 3, "Industrial"); u.Touch = R(1, 9, "Modern", "Green");
            ConduitStyles.Plan pu = ConduitStyles.PlanPlacement("Futuristic", null, new[] { u }, D);
            Check(pu.Look == "Industrial", "can fail: on a UNIFORM run the touched member is ignored and the run's look is adopted (as before)");
        }

        private static void Lamps()
        {
            // rule 4: a lamp follows "all connected" when it wears a look some member drew before, or none
            var drew = new HashSet<string> { "Industrial", "Futuristic" };
            Check(ConduitStyles.LampFollowsRun("Futuristic", drew, true, false) && ConduitStyles.LampFollowsRun("Industrial", drew, true, false) &&
                  ConduitStyles.LampFollowsRun(null, drew, true, false),
                  "on a mixed run a lamp wearing either drawn look, or none, follows");
            Check(!ConduitStyles.LampFollowsRun("Modern", drew, true, false) && !ConduitStyles.LampFollowsRun("Industrial", drew, true, true),
                  "can fail: a lamp in a look no member drew, or in another mod's style, keeps it");
            bool same = true;
            foreach (string lamp in AerialStyles.Looks.Concat(new string[] { null }))
                foreach (string run in AerialStyles.Looks.Concat(new string[] { null }))
                    same &= ConduitStyles.LampFollowsRun(lamp, new HashSet<string> { run ?? D }, true, false) == ConduitStyles.LampFollowsRun(lamp, run, D, true, false);
            Check(same, "on a uniform run the new rule equals round 6's for every (lamp, run) look pair");
        }

        private static void Reaches()
        {
            var all = (ConduitStyles.Reach[])Enum.GetValues(typeof(ConduitStyles.Reach));
            Check(all.Length == 3 && all.Select(ConduitStyles.ReachLabel).Distinct().Count() == 3, "three reaches, three labels");
            // (isTarget, inTargetRun, playerOwned)
            Check(ConduitStyles.ReachTakes(ConduitStyles.Reach.Item, true, true, true, false) &&
                  !ConduitStyles.ReachTakes(ConduitStyles.Reach.Item, false, true, true, false),
                  "this item: the target only, never another member of its run");
            Check(ConduitStyles.ReachTakes(ConduitStyles.Reach.Connected, false, true, true, false) &&
                  ConduitStyles.ReachTakes(ConduitStyles.Reach.Connected, false, true, false, false) &&
                  !ConduitStyles.ReachTakes(ConduitStyles.Reach.Connected, false, false, true, false),
                  "all connected: every member of the run (whoever owns it), nothing outside it");
            Check(ConduitStyles.ReachTakes(ConduitStyles.Reach.Map, false, false, true, false) &&
                  !ConduitStyles.ReachTakes(ConduitStyles.Reach.Map, false, false, false, false) &&
                  ConduitStyles.ReachTakes(ConduitStyles.Reach.Map, false, false, false, true),
                  "all on map: the player's own things; in god mode every faction's too");
        }

        private static void Wiring()
        {
            string dir = SwitchFlipChecks.AerialSourceDir();
            Check(dir != null, "found Source/Aerial to read the gizmo");
            if (dir == null) return;
            string picker = File.ReadAllText(Path.Combine(dir, "ConduitStylePicker.cs"));
            string runs = File.ReadAllText(Path.Combine(dir, "RM_MapComponent_ConduitRuns.cs"));
            Check(picker.Contains("ReachMenu(") && Regex.Matches(picker, @"ConduitStyles\.Reach\.(Item|Connected|Map)").Cast<Match>().Select(m => m.Value).Distinct().Count() == 3,
                  "the Restyle gizmo opens the reach menu, which names all three reaches");
            Check(!picker.Contains("SwitchAllGizmo") && !picker.Contains("DEV: switch ALL"), "the separate god-mode 'DEV: switch ALL to...' button is gone (its job is the map reach)");
            Check(Regex.IsMatch(runs, @"public int RestyleOne\(") && Regex.IsMatch(runs, @"public int RestyleAll\(string key, bool message, bool everyFaction\)"),
                  "the run component has this-item and player-limited all-on-map calls");
            Check(Regex.IsMatch(runs, @"ReachTakes\(ConduitStyles\.Reach\.Map"), "all on map decides ownership through the tested ReachTakes rule");
        }

        private static void GustDefault()
        {
            string dir = SwitchFlipChecks.AerialSourceDir();
            if (dir == null) { Check(false, "gust: found Source/Aerial"); return; }
            string s = File.ReadAllText(Path.Combine(dir, "AerialSettings.cs"));
            bool field = Regex.IsMatch(s, @"public static WireSwayLook swayLook = WireSwayLook\.Gust;");
            bool scribe = Regex.IsMatch(s, @"Scribe_Values\.Look\(ref swayLook, ""swayLook"", WireSwayLook\.Gust\)");
            bool reset = Regex.IsMatch(s, @"swayLook = WireSwayLook\.Gust;\s*\n\s*explosionsCut");
            Check(field && scribe && reset, $"gust: the shipped overhead sway is Gust in the field, the saved default and Reset (field {field}, scribe {scribe}, reset {reset})");
            Check(Regex.IsMatch(s, @"Gust \(default") && !Regex.IsMatch(s, @"Rope \(default"), "gust: the settings radio button marks Gust as the default, not Rope");
            Check(s.Contains("WireSwayLook.Pendulum") && s.Contains("WireSwayLook.Rope"), "gust: Pendulum and Rope stay as choices");
        }
    }
}
