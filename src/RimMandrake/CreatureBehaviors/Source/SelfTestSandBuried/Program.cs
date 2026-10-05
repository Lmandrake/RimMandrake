using System;
using RimMandrake.CreatureBehaviors;

// Offline selftest for RM_SandBuriedGraphic.ShouldDrawBuried (LONGSHADE_SHEET_STRUCTURAL_RULINGS_1).
// Compiles the REAL production decision file. Covered: every one of the 256 input combinations
// against the stated rule, plus the named cases the owner's rulings depend on. NOT covered (needs
// the game): that the Harmony postfix lands on Pawn.DrawNonHumanlikeSwimmingGraphic, the terrain
// read, and how the art looks — those are the live half.
public static class Program
{
    static int pass, fail;

    static void Check(string name, bool got, bool want)
    {
        if (got == want) { pass++; Console.WriteLine("PASS  " + name); }
        else { fail++; Console.WriteLine("FAIL  " + name + " (got " + got + ", want " + want + ")"); }
    }

    static bool D(bool enabled = true, bool vanilla = false, bool spawned = true, bool humanlike = false,
        bool swim = true, bool still = true, bool moving = false, bool sand = true)
        => RM_SandBuriedGraphic.ShouldDrawBuried(enabled, vanilla, spawned, humanlike, swim, still, moving, sand);

    public static int Main()
    {
        Check("drazzik waiting still on sand -> buried art", D(), true);
        Check("drazzik running across sand -> ordinary body (onlyWhenStill)", D(moving: true), false);
        Check("onlyWhenStill=false: moving on sand still buried", D(still: false, moving: true), true);
        Check("resting on rock -> ordinary body", D(sand: false), false);
        Check("setting off -> ordinary body", D(enabled: false), false);
        Check("setting off never hides vanilla water swimming", D(enabled: false, vanilla: true), true);
        Check("no swimmingGraphicData -> never (no magenta from an empty slot)", D(swim: false), false);
        Check("unspawned (corpse/carried) -> never", D(spawned: false), false);
        Check("humanlike -> never", D(humanlike: true), false);

        int bad = 0;
        for (int m = 0; m < 256; m++)
        {
            bool e = (m & 1) != 0, v = (m & 2) != 0, sp = (m & 4) != 0, h = (m & 8) != 0,
                 sw = (m & 16) != 0, st = (m & 32) != 0, mv = (m & 64) != 0, sa = (m & 128) != 0;
            bool want = v || (e && sp && !h && sw && !(st && mv) && sa);
            if (RM_SandBuriedGraphic.ShouldDrawBuried(e, v, sp, h, sw, st, mv, sa) != want) bad++;
        }
        Check("all 256 input combinations match the rule (vanilla TRUE is never turned FALSE)", bad == 0, true);

        Console.WriteLine((fail == 0 ? "OK " : "FAILED ") + pass + "/" + (pass + fail));
        return fail == 0 ? 0 : 1;
    }
}
