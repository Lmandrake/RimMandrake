using System.Collections.Generic;
using System;
using System.Linq;
using RimMandrake.KineticArms;

// Offline kernel tests KA-01..KA-12 for the production RM_KineticMath.cs.
internal static class Program
{
    private static int pass, fail;

    private static void Check(string id, bool ok, string detail = "")
    {
        if (ok) pass++;
        else
        {
            fail++;
            Console.WriteLine("FAIL " + id + " " + detail);
        }
    }

    private static int Main()
    {
        // KA-01 direction east, unit length
        Check("KA-01", RM_KineticMath.Dir(0, 0, 6, 0, out float dx, out float dz) && Math.Abs(dx - 1) < 1e-4 && Math.Abs(dz) < 1e-4);
        // KA-02 zero vector refuses
        Check("KA-02", !RM_KineticMath.Dir(3, 3, 3, 3, out _, out _));
        // KA-03 back-step east shot: centre one cell west of impact
        RM_KineticMath.BackStep(10, 10, 1, 0, out int bx, out int bz);
        Check("KA-03", bx == 9 && bz == 10, bx + "," + bz);
        // KA-04 diagonal shot steps back diagonally
        RM_KineticMath.Dir(0, 0, 5, 5, out dx, out dz);
        RM_KineticMath.BackStep(10, 10, dx, dz, out bx, out bz);
        Check("KA-04", bx == 9 && bz == 9, bx + "," + bz);
        // KA-05 shallow shot steps back along the major axis
        RM_KineticMath.Dir(0, 0, 10, 3, out dx, out dz);
        RM_KineticMath.BackStep(10, 10, dx, dz, out bx, out bz);
        Check("KA-05", bx == 9 && bz == 10, bx + "," + bz);
        // KA-06 cone: ahead in, behind out, centre out
        Check("KA-06", RM_KineticMath.InCone(0, 0, 1, 0, 1, 0, 90) && !RM_KineticMath.InCone(0, 0, -1, 0, 1, 0, 90) && !RM_KineticMath.InCone(0, 0, 0, 0, 1, 0, 90));
        // KA-07 wrap-around: a westward shot (180 degrees) keeps cells either side of the -x axis
        Check("KA-07", RM_KineticMath.InCone(0, 0, -2, 1, -1, 0, 90) && RM_KineticMath.InCone(0, 0, -2, -1, -1, 0, 90) && !RM_KineticMath.InCone(0, 0, 2, 0, -1, 0, 90));
        // KA-08 45-degree edge of a 90 cone is inside; 60 degrees is outside
        Check("KA-08", RM_KineticMath.InCone(0, 0, 1, 1, 1, 0, 90) && !RM_KineticMath.InCone(0, 0, 1, 2, 1, 0, 90));
        // KA-09 cone cells always include the impact; never the centre; nothing behind
        var cells = RM_KineticMath.ConeCells(9, 10, 10, 10, 1, 0, 1.9f, 90);
        Check("KA-09", cells.Contains((10, 10)) && !cells.Contains((9, 10)) && cells.All(c => c.x >= 10), string.Join(" ", cells));
        // KA-10 a 1.5 kicker cone north from the cell behind the plate covers the plate and its two forward diagonals only
        RM_KineticMath.Facing(0, out float fx, out float fz);
        var kick = RM_KineticMath.ConeCells(5, 4, 5, 5, fx, fz, 1.5f, 90);
        Check("KA-10", kick.Count == 3 && kick.Contains((5, 5)) && kick.Contains((4, 5)) && kick.Contains((6, 5)), string.Join(" ", kick));
        // KA-11 facings: 0 N, 1 E, 2 S, 3 W, and negatives wrap
        RM_KineticMath.Facing(1, out fx, out fz); bool e = fx == 1 && fz == 0;
        RM_KineticMath.Facing(2, out fx, out fz); bool sth = fx == 0 && fz == -1;
        RM_KineticMath.Facing(-1, out fx, out fz); bool w = fx == -1 && fz == 0;
        Check("KA-11", e && sth && w);
        // KA-12 pulse charge: unpowered no refill; powered refills one per rechargeTicks; capped; spend gates fire
        float c0 = RM_KineticMath.Recharge(0f, 4, 1200, 600, false);
        float c1 = RM_KineticMath.Recharge(0f, 4, 1200, 1200, true);
        float c2 = RM_KineticMath.Recharge(3.9f, 4, 1200, 99999, true);
        bool gate = !RM_KineticMath.CanFire(0.5f) && RM_KineticMath.CanFire(1f) && RM_KineticMath.Spend(0.4f) == 0f;
        Check("KA-12", c0 == 0f && Math.Abs(c1 - 1f) < 1e-4 && c2 == 4f && gate, c0 + " " + c1 + " " + c2 + " " + gate);
        // KA-13 strength scaling never negative
        Check("KA-13", RM_KineticMath.ScaledForce(2.5f, 0f) == 0f && RM_KineticMath.ScaledForce(2f, 1.5f) == 3f && RM_KineticMath.ScaledForce(2f, -1f) == 0f);

        // KA-14 looted weapons on pirate raiders (owner 2026-10-06): rare gate, grenadier gets grenades, money fits, toggles
        {
            var opts = new[]
            {
                new RM_KineticMath.LootOption { grenade = true, price = 110, enabled = true },   // thudder
                new RM_KineticMath.LootOption { grenade = false, price = 260, enabled = true },  // palm thumper
                new RM_KineticMath.LootOption { grenade = false, price = 420, enabled = true },  // slam launcher
                new RM_KineticMath.LootOption { grenade = false, price = 900, enabled = true },  // repulsor rifle
                new RM_KineticMath.LootOption { grenade = false, price = 2400, enabled = true }, // grav-ram
            };
            Check("KA-14 roll above chance keeps own gun", RM_KineticMath.PickLooted(opts, false, 345, 0.02f, 0.5f, 0f) == -1);
            Check("KA-14 chance 0 never", RM_KineticMath.PickLooted(opts, false, 9999, 0f, 0f, 0f) == -1);
            Check("KA-14 pirate (345) gets palm thumper", RM_KineticMath.PickLooted(opts, false, 345, 0.02f, 0.01f, 0.99f) == 1);
            Check("KA-14 grenadier gets thudder", RM_KineticMath.PickLooted(opts, true, 1000, 0.02f, 0.01f, 0.5f) == 0);
            Check("KA-14 boss (1400) never grav-ram", RM_KineticMath.PickLooted(opts, false, 1400, 0.02f, 0.01f, 0.999f) == 3);
            Check("KA-14 too poor for any", RM_KineticMath.PickLooted(opts, false, 200, 1f, 0f, 0f) == -1);
            opts[1].enabled = false;
            Check("KA-14 toggle off excluded", RM_KineticMath.PickLooted(opts, false, 345, 1f, 0f, 0f) == -1);
            Check("KA-15 ceiling keeps grav-ram off a rich kind", RM_KineticMath.LootMoney(26000f, 0f) == 1000f);
            Check("KA-15 floor lifts a poor kind", RM_KineticMath.LootMoney(168f, 300f) == 300f && RM_KineticMath.LootMoney(660f, 300f) == 660f);
            opts[1].enabled = true;
            Check("KA-15 junker (168 lifted to 300) gets palm thumper", RM_KineticMath.PickLooted(opts, false, RM_KineticMath.LootMoney(168f, 300f), 1f, 0f, 0f) == 1);
            Check("KA-15 hutt leader (15600) never grav-ram", RM_KineticMath.PickLooted(opts, false, RM_KineticMath.LootMoney(15600f, 0f), 1f, 0f, 0.999f) == 3);
            opts[1].enabled = false;
            int hits = 0;
            for (int i = 0; i < 1000; i++)
            {
                if (RM_KineticMath.PickLooted(opts, false, 1400, 0.02f, i / 1000f, 0.5f) >= 0) hits++;
            }
            Check("KA-14 2% of pawns", hits == 20, hits.ToString());
        }

        // KA-16 ruins loot pick (owner: found in Ancient Danger ruins)
        {
            var on = new List<bool> { true, true, true, true, true, true, true, true };
            Check("KA-16 roll above chance = nothing", RM_KineticMath.PickRuins(on, 0.35f, 0.35f, 0f) == -1);
            Check("KA-16 roll below chance picks", RM_KineticMath.PickRuins(on, 0.35f, 0.34f, 0f) == 0);
            Check("KA-16 last pick", RM_KineticMath.PickRuins(on, 0.35f, 0f, 0.9999f) == 7);
            on[7] = false;
            Check("KA-16 toggle off never picked", RM_KineticMath.PickRuins(on, 1f, 0f, 0.9999f) == 6);
            Check("KA-16 all off = nothing", RM_KineticMath.PickRuins(new List<bool> { false, false }, 1f, 0f, 0.5f) == -1);
            Check("KA-16 chance 0 = nothing", RM_KineticMath.PickRuins(on, 0f, 0f, 0.5f) == -1);
            var counts = new int[8];
            for (int i = 0; i < 700; i++)
            {
                counts[RM_KineticMath.PickRuins(on, 1f, 0f, i / 700f)]++;
            }
            Check("KA-16 uniform over enabled", counts[0] == 100 && counts[6] == 100 && counts[7] == 0, string.Join(",", counts));
            Check("KA-16 shells 5-12", RM_KineticMath.RuinsStack(true, 0f) == 5 && RM_KineticMath.RuinsStack(true, 0.9999f) == 12);
            Check("KA-16 weapons single", RM_KineticMath.RuinsStack(false, 0.7f) == 1);
        }

        Console.WriteLine((fail == 0 ? "KERNEL: PASS " : "KERNEL: FAIL ") + pass + "/" + (pass + fail));
        return fail == 0 ? 0 : 1;
    }
}
