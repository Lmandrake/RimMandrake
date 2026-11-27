// Offline test of RIMMANDRAKE_ADD_LIGHT_ANYTHING_FLAMMABLE_ORDER_TO_ALL_COLONISTS: the REAL LightOrderRule.cs (the one decision
// the right-click order makes: is this thing lightable, by this colonist, and if not, is the line hidden or greyed with a reason).
// Verse-free: the facts are what Source/LightOrder/LightOrder.cs reads from the game (Thing.FlammableNow, FireUtility.
// ChanceToStartFireIn, Pawn.IsColonistPlayerControlled, CanReach, FlowWorks' own toss test) and hands over.
// Two halves: (1) the named scenes of the spec, (2) every combination of the 13 facts read against a rule table
// written from the spec, not from the code. Run: python3 src/RimMandrake/MandrakePatches/selftest_light_order.py
using System;
using System.Collections.Generic;
using RimMandrake.Patches;

internal static class Scenarios
{
    private static int fails;
    private static int read;

    private static void Expect(string name, LightFacts f, LightVerdict want, string reasonPart = null)
    {
        read++;
        LightVerdict got = LightOrderRule.Decide(f, out string reason);
        bool ok = got == want && (reasonPart == null || (reason ?? "").Contains(reasonPart));
        Console.WriteLine("{0}  {1}: {2} ({3})", ok ? "ok  " : "FAIL", name, got, reason ?? "-");
        if (!ok)
        {
            fails++;
            Console.WriteLine("      wanted {0}{1}", want, reasonPart == null ? "" : " with reason containing '" + reasonPart + "'");
        }
    }

    // A colonist who can light it, and a thing that lights: the base every scene changes one fact of.
    private static LightFacts Lightable() => new LightFacts
    {
        OrderOn = true, PlantsOn = false, PawnControllable = true, PawnDowned = false, PawnHasHands = true,
        TargetIsPawn = false, TargetIsPlant = false, TargetIsFire = false, FlammableNow = true, Burning = false,
        CellTakesFire = true, Reachable = true, OtherModCellLine = false,
    };

    private static int Main()
    {
        // ---- (1) the named scenes ----
        LightFacts f = Lightable();
        Expect("wooden wall, colonist with a path", f, LightVerdict.Offer);
        Expect("hay stack (Flammability 1.5)", f, LightVerdict.Offer);
        Expect("chemfuel puddle Filth_Fuel (Flammability 2.0)", f, LightVerdict.Offer);
        f = Lightable(); f.FlammableNow = false;
        Expect("steel wall (MetalNonFlammable: 0) is refused with no line", f, LightVerdict.None, "not flammable");
        f = Lightable(); f.TargetIsPawn = true;
        Expect("a living pawn: no line (that is an attack)", f, LightVerdict.None, "living");
        f = Lightable(); f.TargetIsFire = true;
        Expect("the fire itself: no line", f, LightVerdict.None);
        f = Lightable(); f.Burning = true;
        Expect("already burning: no line (vanilla's extinguish line is the one)", f, LightVerdict.None, "burning");
        f = Lightable(); f.TargetIsPlant = true;
        Expect("a tree, plants setting off: no line", f, LightVerdict.None, "plant");
        f.PlantsOn = true;
        Expect("a tree, plants setting on: offered", f, LightVerdict.Offer);
        f = Lightable(); f.OtherModCellLine = true;
        Expect("a corpse in a FlowWorks tar canal: FlowWorks' toss line only", f, LightVerdict.None, "FlowWorks");
        f = Lightable(); f.OrderOn = false;
        Expect("Mod Settings switch off: no line", f, LightVerdict.None, "off");
        f = Lightable(); f.PawnControllable = false;
        Expect("not a player-controlled colonist: no line", f, LightVerdict.None);
        f = Lightable(); f.PawnDowned = true;
        Expect("downed colonist: no line", f, LightVerdict.None);
        f = Lightable(); f.PawnHasHands = false;
        Expect("colonist with no Manipulation: greyed", f, LightVerdict.Disabled, "hands");
        f = Lightable(); f.Reachable = false;
        Expect("walled-off wall: greyed, no path", f, LightVerdict.Disabled, "path");
        f = Lightable(); f.CellTakesFire = false;
        Expect("fire foam on its square: greyed, nothing catches", f, LightVerdict.Disabled, "catch");
        // the labels the menu shows
        string on = LightOrderRule.Label("wood wall", LightVerdict.Offer, null);
        string off = LightOrderRule.Label("wood wall", LightVerdict.Disabled, "no path");
        read += 2;
        bool lab = on == "Set fire to wood wall" && off == "Cannot set fire to wood wall: no path" && LightOrderRule.Label("x", LightVerdict.None, "y") == null;
        Console.WriteLine("{0}  labels: '{1}' / '{2}'", lab ? "ok  " : "FAIL", on, off);
        if (!lab) fails++;

        // ---- (2) every combination, read against the rule table ----
        // Rule table (from the spec): HIDDEN when the switch is off, the colonist is not a controllable standing colonist,
        // the target is a living pawn / the fire itself / a plant with plants off / not flammable now / already burning,
        // or FlowWorks offers its toss line on the clicked square. Otherwise GREYED when the colonist has no hands, the
        // square will not take fire, or there is no path. Otherwise OFFERED.
        int combos = 0, wrong = 0;
        string firstWrong = null;
        for (int m = 0; m < 1 << 13; m++)
        {
            bool B(int i) => (m >> i & 1) == 1;
            var c = new LightFacts
            {
                OrderOn = B(0), PlantsOn = B(1), PawnControllable = B(2), PawnDowned = B(3), PawnHasHands = B(4),
                TargetIsPawn = B(5), TargetIsPlant = B(6), TargetIsFire = B(7), FlammableNow = B(8), Burning = B(9),
                CellTakesFire = B(10), Reachable = B(11), OtherModCellLine = B(12),
            };
            bool hidden = !c.OrderOn || !c.PawnControllable || c.PawnDowned || c.TargetIsPawn || c.TargetIsFire
                          || (c.TargetIsPlant && !c.PlantsOn) || !c.FlammableNow || c.Burning || c.OtherModCellLine;
            bool greyed = !hidden && (!c.PawnHasHands || !c.CellTakesFire || !c.Reachable);
            LightVerdict want = hidden ? LightVerdict.None : greyed ? LightVerdict.Disabled : LightVerdict.Offer;
            LightVerdict got = LightOrderRule.Decide(c, out string why);
            combos++;
            bool reasonOk = got == LightVerdict.Offer ? why == null : !string.IsNullOrEmpty(why);
            if (got != want || !reasonOk)
            {
                wrong++;
                if (firstWrong == null) firstWrong = "mask " + m + ": got " + got + " (" + why + "), wanted " + want;
            }
        }
        read += combos;
        Console.WriteLine("{0}  rule table: {1} combinations read, {2} wrong (limit 0){3}", wrong == 0 ? "ok  " : "FAIL",
            combos, wrong, firstWrong == null ? "" : "; first " + firstWrong);
        if (wrong != 0) fails++;
        if (combos != 8192) { Console.WriteLine("FAIL  the sweep read {0} combinations, not 2^13", combos); fails++; }

        Console.WriteLine();
        Console.WriteLine(fails == 0 ? "all light-order scenarios held ({0} cases read)" : "{1} light-order scenario(s) FAILED ({0} cases read)", read, fails);
        return fails == 0 ? 0 : 1;
    }
}
