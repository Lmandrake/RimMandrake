// BESKAR_ARMORER_QUEST_1 L3: offline proof of the kernel rules. Run: python3 src/RimMandrake/Utils/selftest_beskar_armorer.py
using System;
using System.Collections.Generic;

namespace RimMandrake.Utinni.BeskarArmorer.SelfTest
{
    internal static class Program
    {
        private static int fails, checks;
        private static void Eq(object want, object got, string what)
        {
            checks++;
            if (!Equals(want, got)) { fails++; Console.WriteLine("FAIL " + what + ": want " + want + " got " + got); }
        }
        private static KeyValuePair<bool, int> C(bool b, int n) { return new KeyValuePair<bool, int>(b, n); }

        private static int Main()
        {
            // beskar mass
            Eq(7, ArmorerKernel.BeskarMass(true, 7, null, false, 0), "a stack of beskar is its count");
            Eq(30, ArmorerKernel.BeskarMass(false, 1, new[] { C(true, 30), C(false, 50) }, false, 0), "only beskar cost lines count");
            Eq(60, ArmorerKernel.BeskarMass(false, 1, null, true, 60), "made of beskar: its stuff count");
            Eq(0, ArmorerKernel.BeskarMass(false, 1, new[] { C(false, 50) }, false, 60), "no beskar, stuff count ignored");
            // melt
            int r = 0;
            Eq(40, ArmorerKernel.MeltIngots(50, 5, ref r), "melt 50 keeps 1 in 5"); Eq(0, r, "melt 50 leaves no remainder");
            for (int mass = 1; mass <= 400; mass++)
            {
                r = 0;
                Eq(mass * 4 / 5, ArmorerKernel.MeltIngots(mass, 5, ref r), "melt x0.8 floor at " + mass);
                Eq(mass * 4 % 5, r, "melt remainder at " + mass);
            }
            r = 0; int got = 0;
            for (int i = 0; i < 5; i++) got += ArmorerKernel.MeltIngots(1, 5, ref r);
            Eq(4, got, "five single units give exactly four ingots"); Eq(0, r, "and nothing owed");
            r = 0; Eq(0, ArmorerKernel.MeltIngots(0, 5, ref r), "no mass no ingots");
            // smelt
            float third = 1f / 3f;
            for (int n = 1; n <= 300; n++)
            {
                Eq((n + 2) / 3, ArmorerKernel.SmeltSteel(n, third), "steel ceil(n/3) at " + n);
                Eq(1, ArmorerKernel.SmeltSlag(n), "one slag at " + n);
            }
            Eq(0, ArmorerKernel.SmeltSteel(0, third), "no beskar no steel"); Eq(0, ArmorerKernel.SmeltSlag(0), "no beskar no slag");
            // bill gate: every combination against an independent statement of the rule
            foreach (bool on in new[] { false, true }) foreach (bool bes in new[] { false, true })
            foreach (bool forge in new[] { false, true }) foreach (bool smelt in new[] { false, true })
                Eq(!(on && bes && !forge && !smelt), ArmorerKernel.BillMayConsume(on, bes, forge, smelt), "gate " + on + bes + forge + smelt);
            Eq(false, ArmorerKernel.MayWorkForge(true, true, false), "colonist refused at forge");
            Eq(true, ArmorerKernel.MayWorkForge(true, true, true), "she works it");
            Eq(true, ArmorerKernel.MayWorkForge(true, false, false), "other benches are not her business");
            Eq(true, ArmorerKernel.RouteOneFires(true, true, true, true, false, false, false), "route 1 fires");
            foreach (int i in new[] { 0, 1, 2, 3, 4, 5, 6 })
            {
                bool[] a = { true, true, true, true, false, false, false }; a[i] = !a[i];
                Eq(false, ArmorerKernel.RouteOneFires(a[0], a[1], a[2], a[3], a[4], a[5], a[6]), "route 1 refuses with flag " + i + " wrong");
            }
            Eq(false, ArmorerKernel.RouteTwoOffers(true, 29.9f, 30f, false, false, false), "route 2 not before day 30");
            Eq(true, ArmorerKernel.RouteTwoOffers(true, 30f, 30f, false, false, false), "route 2 from day 30");
            Eq(false, ArmorerKernel.RouteTwoOffers(true, 40f, 30f, true, false, false), "route 2 never while revealed");
            Eq(false, ArmorerKernel.RouteTwoOffers(true, 40f, 30f, false, true, false), "route 2 never while lost");
            Console.WriteLine(fails == 0 ? "PASS " + checks + " checks" : "FAIL " + fails + " of " + checks);
            return fails == 0 ? 0 : 1;
        }
    }
}
